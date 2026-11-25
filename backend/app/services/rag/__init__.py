"""RAG (Retrieval-Augmented Generation) pipeline for SmartWork AI MVP.

Explicit pipeline (no LangChain):
  question → scope identification → authorized retrieval → ranking/truncation → 
  generation with citations → answer
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional, Dict, Any, List

from fastapi import HTTPException

from app.services.extraction import extract_document
from app.services.classification import classify_document
from app.core.security import get_current_user

logger = logging.getLogger(__name__)


def format_citation(document: dict, chunk: dict) -> str:
    """Format a source citation from a document and chunk.
    
    Returns format: "Document filename, page X, paragraph Y" or 
                   "Document filename, sheet X, cell Y" etc.
    """
    filename = document.get("filename", "Document inconnu")
    provenance = document.get("provenance", {})
    
    # Try to extract page, paragraph, sheet, cell info
    page = provenance.get("page") or chunk.get("chunk_metadata", {}).get("page")
    sheet = provenance.get("sheet") or chunk.get("chunk_metadata", {}).get("sheet")
    paragraph = provenance.get("paragraph") or chunk.get("chunk_metadata", {}).get("paragraph")
    cell = provenance.get("cell") or chunk.get("chunk_metadata", {}).get("cell")
    
    parts = [filename]
    
    if page:
        parts.append(f"page {page}")
    if sheet:
        parts.append(f"feuille {sheet}")
    if paragraph is not None:
        parts.append(f"paragraphe {paragraph}")
    if cell:
        parts.append(f"cellule {cell}")
    
    return ", ".join(parts)


def format_citations(citations: List[dict]) -> str:
    """Format a list of citations into a formatted string for the answer."""
    if not citations:
        return ""
    
    formatted = []
    for i, citation in enumerate(citations, 1):
        doc = citation.get("document", {})
        chunk = citation.get("chunk", {})
        citation_text = format_citation(doc, chunk)
        formatted.append(f"[{i}] {citation_text}")
    
    return "\n".join(formatted)


async def identify_scope(
    user: dict, 
    question: str, 
    session
) -> List[int]:
    """Identify which documents/orgs the user can access related to the question.
    
    Returns list of document IDs that the user is authorized to search.
    """
    # Get user's organization IDs
    org_ids = user.get("organization_ids", [])
    
    # Build query to find accessible documents
    from app.models import Document
    from sqlmodel import select
    
    # Users can access their own documents + documents from their organizations
    statement = select(Document).where(
        (Document.owner_id == user["id"]) |
        (Document.organization_id.in_(org_ids))
    )
    result = session.exec(statement)
    documents = result.all()
    
    return [doc.id for doc in documents]


async def retrieve_authorized(
    document_ids: List[int],
    question: str,
    session,
    top_k: int = 10
) -> List[dict]:
    """Retrieve relevant chunks from authorized documents using simple keyword matching.
    
    Returns list of dicts with 'document', 'chunk', 'relevance_score' keys.
    """
    if not document_ids:
        return []
    
    from app.models import Document, DocumentChunk, ExtractedData
    from sqlmodel import select
    
    results = []
    
    # Get all chunks from authorized documents
    for doc_id in document_ids:
        # Get extracted data
        stmt = select(ExtractedData).where(ExtractedData.document_id == doc_id)
        extracted = session.exec(stmt).one_or_none()
        
        text = extracted.structured_data.get("text", "") if extracted and extracted.structured_data else ""
        
        # Simple keyword-based ranking
        question_lower = question.lower()
        words = [w for w in question_lower.split() if len(w) > 2]
        
        # Count word occurrences
        score = sum(1 for w in words if w in text.lower())
        
        if score > 0:
            # Get chunks for this document
            chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc_id)
            chunks = session.exec(chunk_stmt).all()
            
            for chunk in chunks:
                chunk_text = chunk.content_text.lower()
                chunk_score = sum(1 for w in words if w in chunk_text)
                
                if chunk_score > 0:
                    results.append({
                        "document_id": doc_id,
                        "chunk_id": chunk.id,
                        "document": {
                            "id": doc_id,
                            "filename": doc.filename if hasattr(doc, 'filename') else f"doc_{doc_id}",
                            "format": doc.format,
                        },
                        "chunk": {
                            "id": chunk.id,
                            "content_text": chunk.content_text,
                            "chunk_type": chunk.chunk_type,
                            "index_position": chunk.index_position,
                            "chunk_metadata": chunk.chunk_metadata or {},
                        },
                        "relevance_score": chunk_score,
                    })
    
    # Sort by relevance score (descending) and take top_k
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:top_k]


def truncate_context(
    chunks: List[dict], 
    max_chars: int = 8000
) -> List[dict]:
    """Truncate context chunks to fit within character limit.
    
    Priority: keep higher-relevance chunks, truncate lower-relevance ones.
    """
    total_chars = sum(len(chunk["chunk"]["content_text"]) for chunk in chunks)
    
    if total_chars <= max_chars:
        return chunks
    
    # Sort by relevance score (already sorted from retrieve_authorized)
    truncated = []
    current_chars = 0
    
    for chunk_info in chunks:
        chunk_text = chunk_info["chunk"]["content_text"]
        chunk_len = len(chunk_text)
        
        if current_chars + chunk_len <= max_chars:
            truncated.append(chunk_info)
            current_chars += chunk_len
        else:
            # Truncate this chunk to fit remaining space
            remaining = max_chars - current_chars
            if remaining > 200:  # Only include if enough space
                truncated.append({
                    **chunk_info,
                    "chunk": {
                        **chunk_info["chunk"],
                        "content_text": chunk_text[:remaining] + "...",
                    }
                })
            current_chars = max_chars
            break
    
    return truncated


def detect_prompt_injection(question: str) -> Optional[str]:
    """Detect potential prompt injection in the user question.
    
    Returns a warning message if injection is detected, None otherwise.
    """
    # Check for common prompt injection patterns
    injection_patterns = [
        r"(?i)ignore\s+(previous|all|prior)\s+instructions",
        r"(?i)system\s*[:=]\s*",
        r"(?i)you\s+are\s+(now|henceforth)\s+",
        r"(?i)disregard\s+(the\s+)?previous",
        r"(?i)<\s*system\s*>",
        r"(?i)prompt\s+injection",
        r"(?i)jailbreak",
        r"(?i)act\s+as\s+",
        r"(?i)override",
        r"(?i)forget\s+(the\s+)?previous",
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, question):
            return f"Potential prompt injection detected: pattern matching '{pattern}'"
    
    return None


async def answer_question(
    question: str,
    user: dict,
    session
) -> dict:
    """Execute the RAG pipeline to answer a user question.
    
    Returns dict with:
    - answer: the generated answer
    - citations: formatted citations
    - source_count: number of source documents
    - fallback: whether fallback was used
    """
    # Step 1: Detect prompt injection
    injection_warning = detect_prompt_injection(question)
    if injection_warning:
        return {
            "answer": f"⚠️ Détection de contenu suspect dans votre question. {injection_warning}",
            "citations": [],
            "source_count": 0,
            "fallback": True,
            "injection_detected": True,
        }
    
    # Step 2: Identify scope (which documents user can access)
    document_ids = await identify_scope(user, question, session)
    
    if not document_ids:
        return {
            "answer": "⚠️ Aucun document accessible n'est associé à votre compte. Veuillez d'abord importer des documents.",
            "citations": [],
            "source_count": 0,
            "fallback": True,
        }
    
    # Step 3: Retrieve authorized chunks
    retrieved = await retrieve_authorized(document_ids, question, session, top_k=10)
    
    if not retrieved:
        return {
            "answer": "⚠️ Information non trouvée dans vos documents autorisés. Le contenu demandé ne semble pas présent dans vos documents accessibles.",
            "citations": [],
            "source_count": 0,
            "fallback": True,
        }
    
    # Step 4: Truncate context
    truncated = truncate_context(retrieved, max_chars=6000)
    
    # Step 5: Generate answer with citations using simple extraction
    # In MVP, we extract key passages and format citations
    citations = []
    answer_parts = []
    
    for chunk_info in truncated[:5]:  # Use top 5 chunks
        chunk = chunk_info["chunk"]
        doc = chunk_info["document"]
        content = chunk["content_text"]
        
        # Format citation
        citation_str = format_citation(doc, chunk)
        citations.append({
            "document": doc,
            "chunk": chunk,
        })
        
        # Add to answer with source reference
        answer_parts.append(f"• {content[:500]}...")
    
    # Step 6: Build final answer
    answer = " ".join(answer_parts)
    
    if not answer.strip():
        return {
            "answer": "⚠️ Information non trouvée dans vos documents autorisés.",
            "citations": [],
            "source_count": 0,
            "fallback": True,
        }
    
    # Format citations string
    citations_formatted = format_citations(citations)
    
    citations_suffix = f"\n{citations_formatted}" if citations_formatted else ""
    full_answer = f"{answer}\n\n---\nSources:{citations_suffix}"
    
    return {
        "answer": full_answer,
        "citations": citations,
        "source_count": len(set(c["document"]["id"] for c in citations)),
        "fallback": False,
        "injection_detected": False,
    }


class QueryLog:
    """Simple query logging for audit and reporting."""
    
    @staticmethod
    def log_query(
        user_id: int,
        organization_id: int,
        question: str,
        answer: str,
        source_documents: List[int],
        success: bool,
        response_time: float = 0.0,
    ) -> None:
        """Log a query for audit purposes."""
        import os
        from datetime import datetime, timezone
        
        log_path = os.path.join(os.getenv("LOG_DIR", "/tmp"), "query_logs")
        os.makedirs(log_path, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "organization_id": organization_id,
            "question": question[:500] if question else "",
            "answer_summary": answer[:200] if answer else "",
            "source_documents": source_documents,
            "success": success,
            "response_time_ms": int(response_time * 1000),
        }
        
        log_file = os.path.join(log_path, "queries.log")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")