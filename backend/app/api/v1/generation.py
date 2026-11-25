import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import Document, DocumentChunk, ExtractedData, GeneratedFile, User
from app.services.generation import (
    generate_docx_from_data,
    generate_pdf_from_docx,
    generate_xlsx_from_data,
    generate_summary_report,
)


router = APIRouter(prefix="/generation", tags=["generation"])


def _get_accessible_document(
    document_id: int,
    current_user: User,
    session: Session,
) -> Document:
    """Return the document if the current user is allowed to use it."""
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")
    if (
        doc.owner_id != current_user.id
        and doc.organization_id not in current_user.organization_ids
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé à ce document",
        )
    return doc


@router.post("/docx", status_code=status.HTTP_201_CREATED)
def generate_docx(
    document_id: int,
    model_version: str = "default",
    tone: str = "professional",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a DOCX report from a document."""
    doc = _get_accessible_document(document_id, current_user, session)

    # Generate the document
    result = generate_summary_report(
        document_id=document_id,
        model_version=model_version,
        tone=tone,
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message,
        )
    
    # Save to database
    generated_file = GeneratedFile(
        document_id=document_id,
        filename=result.filename,
        format="docx",
        model_version=model_version,
        generation_params={
            "tone": tone,
            "source_document": document_id,
        },
        status="draft",
        owner_id=current_user.id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    # Update document status
    doc.status = "processed"
    session.add(doc)
    session.commit()
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }


@router.post("/xlsx", status_code=status.HTTP_201_CREATED)
def generate_xlsx(
    document_id: int,
    model_version: str = "default",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate an XLSX spreadsheet from a document's extracted data."""
    doc = _get_accessible_document(document_id, current_user, session)

    # Extract data from the document
    extracted_row = session.exec(
        select(ExtractedData).where(ExtractedData.document_id == document_id)
    ).first()
    extracted_data = extracted_row.structured_data if extracted_row else {}

    # Prepare content for XLSX generation
    content = []

    # Add extracted structured data if available
    if extracted_data.get("structured_data"):
        structured = extracted_data["structured_data"]
        if isinstance(structured, list):
            # Use as rows
            for item in structured[:10]:  # Limit to 10 rows
                row = [str(v) if v is not None else "" for v in item.values()] if isinstance(item, dict) else [str(v) for v in item]
                content.append(row)
        elif isinstance(structured, dict):
            # Use as single row with headers
            headers = list(structured.keys())
            row = [str(v) if v is not None else "" for v in structured.values()]
            content.append(headers)
            content.append(row)

    # If we have extracted text tables, use those
    if not content:
        chunks = session.exec(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .where(DocumentChunk.chunk_type == "table")
        ).all()
        for chunk in chunks[:5]:
            if chunk.content_text:
                # Try to parse as simple table
                lines = chunk.content_text.split("\n")
                if len(lines) > 1:
                    # First line as header
                    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
                    row = [h.strip() for h in lines[1].split("|") if h.strip()] if len(lines) > 1 else []
                    if headers:
                        content.append(headers)
                    if row:
                        content.append(row)
    
    # Generate XLSX
    result = generate_xlsx_from_data({"title": f"Données : {doc.filename}", "content": content}, model_version=model_version)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message,
        )
    
    # Save to database
    generated_file = GeneratedFile(
        document_id=document_id,
        filename=result.filename,
        format="xlsx",
        model_version=model_version,
        generation_params={
            "source_document": document_id,
            "extracted_rows": len(content) if content else 0,
        },
        status="draft",
        owner_id=current_user.id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    # Update document status
    doc.status = "processed"
    session.add(doc)
    session.commit()
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }


@router.post("/summary/{document_id}", status_code=status.HTTP_201_CREATED)
def create_summary(
    document_id: int,
    tone: str = "professional",
    model_version: str = "default",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a summary report for a document."""
    _get_accessible_document(document_id, current_user, session)

    # Generate the summary report
    result = generate_summary_report(
        document_id=document_id,
        model_version=model_version,
        tone=tone,
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message,
        )
    
    # Save to database
    generated_file = GeneratedFile(
        document_id=document_id,
        filename=result.filename,
        format="docx",
        model_version=model_version,
        generation_params={
            "tone": tone,
            "source_document": document_id,
            "generation_type": "summary",
        },
        status="draft",
        owner_id=current_user.id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }

    session.add(generated_file)
    session.refresh(generated_file)
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }


@router.post("/pdf", status_code=status.HTTP_201_CREATED)
def generate_pdf(
    document_id: int,
    tone: str = "professional",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a PDF report from a document."""
    doc = _get_accessible_document(document_id, current_user, session)
    
    from app.services.generation import generate_pdf_from_docx
    
    result = generate_pdf_from_docx(
        {"title": doc.filename, "content": [], "meta": {}},
        model_version=tone,
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message,
        )
    
    generated_file = GeneratedFile(
        document_id=document_id,
        filename=result.filename,
        format="pdf",
        model_version=tone,
        generation_params={"tone": tone, "source_document": document_id},
        status="draft",
        owner_id=current_user.id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }


@router.post("/pptx", status_code=status.HTTP_201_CREATED)
def generate_pptx(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a PPTX presentation from a document."""
    doc = _get_accessible_document(document_id, current_user, session)
    
    from app.services.generation import generate_pptx_from_data
    
    result = generate_pptx_from_data({"title": doc.filename}, model_version="default")
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.message,
        )
    
    generated_file = GeneratedFile(
        document_id=document_id,
        filename=result.filename,
        format="pptx",
        model_version="default",
        generation_params={"source_document": document_id},
        status="draft",
        owner_id=current_user.id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    return {
        "id": generated_file.id,
        "filename": generated_file.filename,
        "format": generated_file.format,
        "model_version": generated_file.model_version,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": result.message,
        "generated_at": generated_file.created_at.isoformat(),
    }


@router.get("/file/{file_id}")
def download_generated_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Download a generated file."""
    from fastapi import Response

    generated_file = session.get(GeneratedFile, file_id)
    if not generated_file:
        raise HTTPException(status_code=404, detail="Fichier généré introuvable")

    allowed = generated_file.owner_id == current_user.id
    if not allowed and generated_file.document_id:
        doc = session.get(Document, generated_file.document_id)
        allowed = bool(
            doc and doc.organization_id in current_user.organization_ids
        )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: vous n'avez pas le droit de télécharger ce fichier",
        )

    candidates = [
        generated_file.filename,
        os.path.join(settings.GENERATED_DIR, os.path.basename(generated_file.filename)),
    ]
    file_path = next((path for path in candidates if os.path.isfile(path)), None)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier introuvable",
        )

    with open(file_path, "rb") as handle:
        file_content = handle.read()

    # Mark the generated file as validated once it has been retrieved
    generated_file.status = "validated"
    generated_file.validated_at = datetime.now(timezone.utc)
    session.add(generated_file)
    session.commit()

    download_name = os.path.basename(generated_file.filename)
    return Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )


@router.get("/history", status_code=status.HTTP_200_OK)
def generation_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get generation history for the user."""
    document_ids = session.exec(
        select(Document.id).where(
            (Document.owner_id == current_user.id)
            | (Document.organization_id.in_(current_user.organization_ids))
        )
    ).all()

    stmt = select(GeneratedFile).where(
        (GeneratedFile.owner_id == current_user.id)
        | (GeneratedFile.document_id.in_(document_ids))
    )
    files = session.exec(stmt).all()
    
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "format": f.format,
                "model_version": f.model_version,
                "status": f.status,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "validated_at": f.validated_at.isoformat() if f.validated_at else None,
                "document_id": f.document_id,
            }
            for f in files
        ]
    }