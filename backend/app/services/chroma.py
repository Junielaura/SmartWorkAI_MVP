"""ChromaDB service layer for vector storage and retrieval.

Manages ChromaDB collections per organization with fallback to lexical
retrieval when ChromaDB is unavailable.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import chromadb

logger = logging.getLogger(__name__)


def _get_chroma_client() -> Any:
    """Get or create a ChromaDB client instance.

    Returns None if chromaDB is not available (e.g., not running).
    """
    try:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))

        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        # Test connection
        client.get_collections()
        logger.info("ChromaDB client connected at %s:%s", chroma_host, chroma_port)
        return client
    except Exception as exc:
        logger.warning("ChromaDB unavailable: %s", exc)
        return None


_chroma_client: Optional[Any] = None
_chroma_collections: Dict[str, Any] = {}


def get_chroma_client() -> Optional[Any]:
    """Get the global ChromaDB client instance."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = _get_chroma_client()
    return _chroma_client


def get_or_create_collection(organization_id: int) -> Any:
    """Get or create a ChromaDB collection for the given organization."""
    client = get_chroma_client()
    if client is None:
        return None

    collection_name = f"org_{organization_id}"

    if collection_name in _chroma_collections:
        return _chroma_collections[collection_name]

    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"organization_id": organization_id},
        )
        _chroma_collections[collection_name] = collection
        logger.info("Created/get ChromaDB collection: %s", collection_name)
        return collection
    except Exception as exc:
        logger.error("Failed to create/get ChromaDB collection %s: %s", collection_name, exc)
        return None


def add_chunks(
    collection: Any,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    ids: List[str],
    metadatas: List[Dict[str, Any]],
) -> bool:
    """Add chunks with embeddings to a ChromaDB collection.

    Returns True if successful, False otherwise.
    """
    if collection is None or not chunks:
        return False

    try:
        # Validate inputs
        if not embeddings or len(embeddings) != len(chunks):
            logger.error("Embeddings/chunks mismatch: %d embeddings vs %d chunks", len(embeddings), len(chunks))
            return False

        # Prepare data for ChromaDB
        chunk_ids = ids or [f"chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = metadatas or [{}] * len(chunks)
        chunk_embeddings = embeddings

        # Add to collection
        collection.add(
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            metadatas=chunk_metadatas,
        )
        logger.info("Added %d chunks to ChromaDB collection", len(chunks))
        return True
    except Exception as exc:
        logger.error("Failed to add chunks to ChromaDB: %s", exc)
        return False


def search_vector(
    collection: Any,
    query_embedding: List[float],
    top_k: int = 10,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Search for similar vectors in a ChromaDB collection.

    Returns list of result dicts with chunk data and similarity scores.
    """
    if collection is None:
        return []

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        chunk_results: List[Dict[str, Any]] = []
        ids = results.get("ids", [[]])[0] or []
        distances = results.get("distances", [[]])[0] or []
        metadatas = results.get("metadatas", [[]])[0] or []
        documents = results.get("documents", [[]])[0] or []

        for i in range(len(ids)):
            # Convert distance to similarity (Chroma uses Euclidean distance)
            # Convert to cosine similarity-like score: 1 - (distance / max_distance)
            distance = distances[i] if i < len(distances) else 1.0
            similarity = max(0.0, 1.0 - distance)

            chunk_result: Dict[str, Any] = {
                "id": ids[i] if i < len(ids) else None,
                "similarity_score": similarity,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "document": documents[i] if i < len(documents) else {},
            }
            chunk_results.append(chunk_result)

        return chunk_results
    except Exception as exc:
        logger.error("ChromaDB vector search failed: %s", exc)
        return []


def reset_collections() -> None:
    """Reset all ChromaDB collections (useful for testing)."""
    global _chroma_collections
    _chroma_collections = {}
    logger.info("ChromaDB collections reset")


def _persist_chunks_to_chromadb(
    document_ids: List[int],
    session,
) -> bool:
    """Persist DocumentChunk entries to ChromaDB with embeddings.

    Returns True if successful, False if ChromaDB is unavailable or on error.
    """
    from app.models import DocumentChunk

    client = get_chroma_client()
    if client is None:
        logger.info("ChromaDB unavailable, skipping vector persistence")
        return False

    for document_id in document_ids:
        # Get chunks for this document from DB
        chunks = session.exec(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        ).all()

        if not chunks:
            continue

        # Get embedding for each chunk's content_text
        embeddings: List[Optional[List[float]]] = []
        ids: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            chunk_id = f"doc_{document_id}_chunk_{chunk.id}"
            ids.append(chunk_id)

            # Use chunk content for embedding
            text = chunk.content_text or ""
            if not text.strip():
                # Skip empty chunks
                embeddings.append(None)  # type: ignore
                metadatas.append(chunk.chunk_metadata or {})
                continue

            embedding = embed_query(text)
            if embedding:
                embeddings.append(embedding)
            else:
                embeddings.append(None)  # type: ignore

            # Prepare metadata from chunk and document
            metadata: Dict[str, Any] = {
                "document_id": chunk.document_id,
                "chunk_type": chunk.chunk_type,
                "page": chunk.chunk_metadata.get("page") if chunk.chunk_metadata else None,
                "sheet": chunk.chunk_metadata.get("sheet") if chunk.chunk_metadata else None,
                "paragraph": chunk.chunk_metadata.get("paragraph") if chunk.chunk_metadata else None,
                "table": chunk.chunk_metadata.get("table") if chunk.chunk_metadata else None,
                "row_range": chunk.chunk_metadata.get("row_range") if chunk.chunk_metadata else None,
            }
            metadatas.append(metadata)

        # Filter out None embeddings
        valid_indices = [
            i for i, emb in enumerate(embeddings) if emb is not None
        ]
        if not valid_indices:
            logger.warning("No valid embeddings for document %s", document_id)
            continue

        valid_ids = [ids[i] for i in valid_indices]
        valid_embeddings = [embeddings[i] for i in valid_indices]
        valid_metadatas = [metadatas[i] for i in valid_indices]

        # Get or create collection for the document's organization
        from app.models import Document
        document = session.get(Document, document_id)
        if document is None:
            continue

        collection = get_or_create_collection(document.organization_id)
        if collection is None:
            continue

        success = add_chunks(
            collection=collection,
            chunks=[chunks[i] for i in valid_indices],
            embeddings=valid_embeddings,
            ids=valid_ids,
            metadatas=valid_metadatas,
        )

        if success:
            logger.info(
                "Persisted %d/%d chunks to ChromaDB for document %s",
                len(valid_indices),
                len(chunks),
                document_id,
            )

    return True