from datetime import datetime, timezone
import os
import json
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select, Session

from app.core.security import get_current_user
from app.db.session import get_session
from app.models import (
    AuditLog,
    Document,
    DocumentChunk,
    DocumentVersion,
    ExtractedData,
    User,
)
from app.services.classification import CATEGORIES, classify_document
from app.services.extraction import extract_document
from app.services.ingestion import get_user_organizations, save_upload
from app.services.chroma import _persist_chunks_to_chromadb


router = APIRouter(prefix="/documents", tags=["documents"])


class ClassificationUpdate(BaseModel):
    category: str


class AnnotationCreate(BaseModel):
    content: str
    annotation_type: str = "comment"  # comment, highlight, note
    metadata: Optional[dict] = None


class AnnotationResponse(BaseModel):
    id: str
    content: str
    annotation_type: str
    metadata: Optional[dict]
    created_at: datetime
    user_id: str


class VersionCreate(BaseModel):
    version_label: str = "v1"
    description: str = ""


class VersionResponse(BaseModel):
    id: str
    version_label: str
    description: str
    created_at: datetime
    storage_path: str


def _get_document_or_404(document_id: int, session: Session) -> Document:
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable")
    return document


def _check_document_access(document: Document, current_user: User) -> None:
    organization_ids = get_user_organizations(current_user)
    if document.owner_id != current_user.id and document.organization_id not in organization_ids:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé: vous n'avez pas le droit de voir ce document",
        )


def _serialize_document(document: Document, extracted: ExtractedData | None) -> dict:
    structured = (extracted.structured_data or {}) if extracted else {}
    return {
        "id": document.id,
        "filename": document.filename,
        "format": document.format,
        "status": document.status,
        "size": document.size,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "classification": structured.get("classification"),
        "classification_confidence": structured.get("classification_confidence"),
        "classification_confirmed": structured.get("classification_confirmed", False),
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Upload, extract, classify and index a document."""
    organization_ids = get_user_organizations(current_user)
    if not organization_ids:
        raise HTTPException(
            status_code=403,
            detail="Aucune organisation attribuée à cet utilisateur",
        )

    organization_id = organization_ids[0]
    document, storage_path = save_upload(
        file=file,
        organization_id=organization_id,
        owner_id=current_user.id,
        session=session,
    )

    extension = document.format
    try:
        extracted = extract_document(
            storage_path,
            extension,
            use_ocr=(extension == "pdf"),
        ) or {}

        text = extracted.get("text", "") or ""
        classification = classify_document(text)
        segments = extracted.get("segments", []) or []

        structured_data = {
            "text": text[:200_000],
            "classification": classification["category"],
            "classification_confidence": classification["confidence"],
            "classification_confirmed": False,
            "tables": extracted.get("tables", [])[:20],
            "metadata": extracted.get("metadata", {}),
            "segment_count": len(segments),
        }
        provenance = {
            "pages": extracted.get("pages"),
            "format": extension,
            "segments": [
                segment.get("metadata", {}) for segment in segments[:500]
            ],
        }

        extracted_row = ExtractedData(
            document_id=document.id,
            structured_data=structured_data,
            provenance=provenance,
        )
        session.add(extracted_row)

        version = session.exec(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document.id)
            .order_by(DocumentVersion.id.desc())
        ).first()

        for position, segment in enumerate(segments[:500]):
            content = (segment.get("content_text") or "").strip()
            if not content:
                continue
            session.add(
                DocumentChunk(
                    document_id=document.id,
                    version_id=version.id if version else None,
                    content_text=content,
                    chunk_type=segment.get("chunk_type", "text"),
                    index_position=position,
                    chunk_metadata=segment.get("metadata", {}),
                )
            )

        document.status = "processed" if segments else "needs_review"
        document.processed_at = datetime.now(timezone.utc)
        session.add(document)

        session.add(
            AuditLog(
                actor_id=current_user.id,
                action="upload_document",
                resource_type="document",
                resource_id=document.id,
                result="success",
            )
        )
        session.commit()
        session.refresh(document)

        # Persist chunks to ChromaDB for vector search
        _persist_chunks_to_chromadb([document.id], session)

    except HTTPException:
        document.status = "failed"
        session.add(document)
        session.commit()
        raise
    except Exception as exc:
        document.status = "failed"
        session.add(document)
        session.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Le document a été enregistré mais son traitement a échoué: {exc}",
        ) from exc

    return {
        "id": document.id,
        "filename": document.filename,
        "format": document.format,
        "status": document.status,
        "size": document.size,
        "classification": structured_data["classification"],
        "classification_confidence": structured_data["classification_confidence"],
        "chunk_count": len(segments),
        "tables_count": len(structured_data["tables"]),
        "text_preview": structured_data["text"][:500],
        "message": "Document uploadé, extrait et indexé avec succès",
    }


@router.get("")
@router.get("/")
def list_documents(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List documents accessible to the user."""
    organization_ids = get_user_organizations(current_user)
    statement = select(Document).where(
        (Document.owner_id == current_user.id)
        | (Document.organization_id.in_(organization_ids))
    )
    documents = session.exec(statement).all()

    extracted_rows = session.exec(
        select(ExtractedData).where(
            ExtractedData.document_id.in_([doc.id for doc in documents])
        )
    ).all() if documents else []
    extracted_by_document = {row.document_id: row for row in extracted_rows}

    return {
        "documents": [
            _serialize_document(doc, extracted_by_document.get(doc.id))
            for doc in documents
        ]
    }


@router.get("/{document_id}")
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a document with its extraction and provenance."""
    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)

    extracted = session.exec(
        select(ExtractedData).where(ExtractedData.document_id == document_id)
    ).first()
    chunks = session.exec(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.index_position)
    ).all()

    return {
        **_serialize_document(document, extracted),
        "extracted_data": extracted.structured_data if extracted else None,
        "provenance": extracted.provenance if extracted else None,
        "chunks": [
            {
                "id": chunk.id,
                "content_text": chunk.content_text,
                "chunk_type": chunk.chunk_type,
                "index_position": chunk.index_position,
                "metadata": chunk.chunk_metadata,
            }
            for chunk in chunks
        ],
    }


@router.patch("/{document_id}/classification")
def update_classification(
    document_id: int,
    payload: ClassificationUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Confirm or correct the document classification."""
    if payload.category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Catégorie invalide. Valeurs acceptées: {', '.join(CATEGORIES)}",
        )

    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)

    extracted = session.exec(
        select(ExtractedData).where(ExtractedData.document_id == document_id)
    ).first()
    if not extracted:
        raise HTTPException(
            status_code=404,
            detail="Aucune extraction disponible pour ce document",
        )

    structured = dict(extracted.structured_data or {})
    structured["classification"] = payload.category
    structured["classification_confirmed"] = True
    extracted.structured_data = structured
    session.add(extracted)

    session.add(
        AuditLog(
            actor_id=current_user.id,
            action="update_classification",
            resource_type="document",
            resource_id=document.id,
            result="success",
        )
    )
    session.commit()

    return {
        "id": document.id,
        "classification": payload.category,
        "classification_confirmed": True,
    }


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Download the original uploaded file."""
    from fastapi import Response

    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)

    version = session.exec(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.id.desc())
    ).first()
    if not version or not os.path.exists(version.storage_path):
        raise HTTPException(status_code=404, detail="Fichier original introuvable")

    with open(version.storage_path, "rb") as handle:
        content = handle.read()

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"'
        },
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a document and all derived data."""
    document = _get_document_or_404(document_id, session)
    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Seul le propriétaire peut supprimer ce document",
        )

    audit_logs = session.exec(
        select(AuditLog).where(
            AuditLog.resource_type == "document",
            AuditLog.resource_id == document_id,
        )
    ).all()
    for audit_log in audit_logs:
        audit_log.resource_id = None
        session.add(audit_log)

    versions = session.exec(
        select(DocumentVersion).where(DocumentVersion.document_id == document_id)
    ).all()
    chunks = session.exec(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    ).all()
    extracted_rows = session.exec(
        select(ExtractedData).where(ExtractedData.document_id == document_id)
    ).all()

    for chunk in chunks:
        session.delete(chunk)
    for row in extracted_rows:
        session.delete(row)
    for version in versions:
        session.delete(version)
    session.delete(document)
    session.commit()

    for version in versions:
        try:
            if version.storage_path and os.path.exists(version.storage_path):
                os.unlink(version.storage_path)
        except OSError:
            pass

    return None


@router.post("/{document_id}/annotations", response_model=AnnotationResponse, )
def create_annotation(
    document_id: int,
    annotation: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add an annotation to a document."""
    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)
    
    annotation_obj = {
        "id": str(uuid4()),
        "content": annotation.content,
        "annotation_type": annotation.annotation_type,
        "metadata": annotation.metadata or {},
        "created_at": datetime.now(timezone.utc),
        "user_id": current_user.id,
    }
    
    # Store annotation in audit log or structured data
    session.add(
        AuditLog(
            actor_id=current_user.id,
            action="create_annotation",
            resource_type="document",
            resource_id=document.id,
            result="success",
            metadata=json.dumps(annotation_obj),
        )
    )
    session.commit()
    
    return AnnotationResponse(
        id=annotation_obj["id"],
        content=annotation_obj["content"],
        annotation_type=annotation_obj["annotation_type"],
        metadata=annotation_obj["metadata"],
        created_at=annotation_obj["created_at"],
        user_id=annotation_obj["user_id"],
    )


@router.get("/{document_id}/annotations", response_model=List[AnnotationResponse], )
def list_annotations(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List annotations on a document."""
    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)
    
    # Retrieve annotations from audit logs or structured data
    # For now, return empty list (to be expanded with proper annotation storage)
    return []


@router.post("/{document_id}/versions", response_model=VersionResponse, )
def create_version(
    document_id: int,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a version snapshot of a document."""
    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)
    
    version = DocumentVersion(
        document_id=document.id,
        version_label=version_data.version_label,
        storage_path=document.chunks[0].storage_path if document.chunks else document.storage_path,
        description=version_data.description,
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    
    return VersionResponse(
        id=str(version.id),
        version_label=version.version_label,
        description=version.description,
        created_at=version.created_at,
        storage_path=version.storage_path,
    )


@router.get("/{document_id}/versions", response_model=List[VersionResponse], )
def list_versions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List document versions."""
    document = _get_document_or_404(document_id, session)
    _check_document_access(document, current_user)
    
    versions = session.exec(
        select(DocumentVersion).where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.id.desc())
    ).all()
    
    return [
        VersionResponse(
            id=str(v.id),
            version_label=v.version_label,
            description=v.description,
            created_at=v.created_at,
            storage_path=v.storage_path,
        )
        for v in versions
    ]
