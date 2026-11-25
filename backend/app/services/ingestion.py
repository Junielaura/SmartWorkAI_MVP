"""Document ingestion and validation service for SmartWork AI MVP."""

from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import List, Tuple

import magic
from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.core.config import ensure_directories, settings
from app.models import Document, DocumentVersion

logger = logging.getLogger(__name__)

ALLOWED_FORMATS = {"pdf", "docx", "xlsx", "csv"}

MIME_BY_EXTENSION = {
    "pdf": {"application/pdf"},
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    },
    "xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
    },
    "csv": {"text/csv", "text/plain", "application/csv", "text/x-csv"},
}


def _max_file_size() -> int:
    return settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_file(file: UploadFile) -> bytes:
    """Validate an uploaded file and return its raw content.

    Checks size, emptiness, extension, MIME type and dangerous filenames.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")

    filename = Path(file.filename).name
    if filename != file.filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Fichier vide")
    if file_size > _max_file_size():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Fichier trop volumineux: {file_size / 1024 / 1024:.1f} Mo "
                f"(limite: {settings.MAX_UPLOAD_SIZE_MB} Mo)"
            ),
        )

    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Format non supporté: .{extension}. "
                f"Formats acceptés: {', '.join(sorted(ALLOWED_FORMATS))}"
            ),
        )

    content = file.file.read()
    file.file.seek(0)

    try:
        mime_type = magic.from_buffer(content[:2048], mime=True)
    except Exception:  # libmagic missing or unreadable buffer
        mime_type = "application/octet-stream"

    expected = MIME_BY_EXTENSION.get(extension, set())
    if expected and mime_type not in expected:
        logger.warning(
            "MIME mismatch for %s: extension=%s detected=%s",
            filename,
            extension,
            mime_type,
        )

    return content


def _safe_filename(filename: str) -> str:
    base = Path(filename).name
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return base or "document"


def save_upload(
    file: UploadFile,
    organization_id: int,
    owner_id: int,
    session: Session,
) -> Tuple[Document, str]:
    """Validate, store on disk and register an uploaded document.

    Returns the persisted document and its storage path.
    """
    content = validate_file(file)
    ensure_directories()

    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    stored_name = f"{uuid.uuid4().hex}_{_safe_filename(file.filename or 'document')}"

    storage_dir = Path(settings.STORAGE_DIR) / str(organization_id) / "documents"
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / stored_name

    with open(storage_path, "wb") as handle:
        handle.write(content)

    document = Document(
        filename=Path(file.filename or "document").name,
        format=extension or "unknown",
        status="processing",
        size=len(content),
        owner_id=owner_id,
        organization_id=organization_id,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    version = DocumentVersion(
        document_id=document.id,
        version_label="v1",
        storage_path=str(storage_path),
    )
    session.add(version)
    session.commit()

    return document, str(storage_path)


def get_user_organizations(user) -> List[int]:
    """Return the organization IDs a user can access."""
    organization_ids = list(getattr(user, "organization_ids", None) or [])
    if not organization_ids and getattr(user, "organization_id", None):
        organization_ids = [user.organization_id]
    return organization_ids
