"""Unified document extraction service with provenance-aware segments."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)

MAX_SEGMENT_CHARS = 1200


def _split_text(text: str, max_chars: int = MAX_SEGMENT_CHARS) -> List[str]:
    """Split text into chunks of at most ``max_chars`` characters."""
    if not text or not text.strip():
        return []

    chunks: List[str] = []
    current = ""

    for line in text.splitlines():
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current.strip())
        while len(line) > max_chars:
            chunks.append(line[:max_chars].strip())
            line = line[max_chars:]
        current = line

    if current.strip():
        chunks.append(current.strip())

    return [chunk for chunk in chunks if chunk]


def _pdf_segments(result: Any) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    pages_data = getattr(result, "pages_data", None) or []

    if pages_data:
        for page in pages_data:
            for piece in _split_text(page.get("text", "")):
                segments.append(
                    {
                        "content_text": piece,
                        "chunk_type": "text",
                        "metadata": {"page": page.get("page")},
                    }
                )
    else:
        for piece in _split_text(getattr(result, "text", "")):
            segments.append(
                {"content_text": piece, "chunk_type": "text", "metadata": {}}
            )

    for table in getattr(result, "tables", []) or []:
        text = table.get("text") if isinstance(table, dict) else str(table)
        if not text:
            continue
        segments.append(
            {
                "content_text": text[:MAX_SEGMENT_CHARS],
                "chunk_type": "table",
                "metadata": {
                    "page": table.get("page") if isinstance(table, dict) else None
                },
            }
        )

    return segments


def _docx_segments(result: Any) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    paragraphs = getattr(result, "paragraphs", []) or []

    current = ""
    start_index: Optional[int] = None
    for paragraph in paragraphs:
        text = paragraph.get("text", "")
        if not text:
            continue
        if start_index is None:
            start_index = paragraph.get("index")
        candidate = f"{current}\n{text}" if current else text
        if len(candidate) > MAX_SEGMENT_CHARS and current:
            segments.append(
                {
                    "content_text": current,
                    "chunk_type": "text",
                    "metadata": {"paragraph": start_index},
                }
            )
            current = text
            start_index = paragraph.get("index")
        else:
            current = candidate

    if current:
        segments.append(
            {
                "content_text": current,
                "chunk_type": "text",
                "metadata": {"paragraph": start_index},
            }
        )

    if not segments and getattr(result, "text", ""):
        for piece in _split_text(result.text):
            segments.append(
                {"content_text": piece, "chunk_type": "text", "metadata": {}}
            )

    for table in getattr(result, "tables", []) or []:
        text = table.get("text") if isinstance(table, dict) else str(table)
        if not text:
            continue
        segments.append(
            {
                "content_text": text[:MAX_SEGMENT_CHARS],
                "chunk_type": "table",
                "metadata": {
                    "table": table.get("index") if isinstance(table, dict) else None
                },
            }
        )

    return segments


def _spreadsheet_segments(result: Any) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []

    for sheet in getattr(result, "sheets", []) or []:
        sheet_name = sheet.get("name")
        for piece in _split_text(sheet.get("text", "")):
            segments.append(
                {
                    "content_text": piece,
                    "chunk_type": "table",
                    "metadata": {"sheet": sheet_name},
                }
            )

    return segments


def _normalize_tables(result: Any, format_type: str) -> List[Dict[str, Any]]:
    tables: List[Dict[str, Any]] = []

    if format_type in {"xlsx", "csv"}:
        for sheet in getattr(result, "sheets", []) or []:
            tables.append(
                {
                    "sheet": sheet.get("name"),
                    "headers": sheet.get("headers", []),
                    "rows": (sheet.get("rows") or [])[:50],
                    "row_count": sheet.get("row_count", 0),
                    "text": sheet.get("text", ""),
                }
            )
        return tables

    for table in getattr(result, "tables", []) or []:
        if isinstance(table, dict):
            tables.append(table)
        else:
            tables.append({"text": str(table)})
    return tables


def extract_document(
    file_path: str, format_type: str, use_ocr: bool = False
) -> Optional[Dict[str, Any]]:
    """Extract content from a document based on its format.

    Returns a normalized dictionary with text, tables, metadata and segments
    carrying provenance (page, sheet, paragraph, table index).

    For PDFs, if the extracted text is very short (likely a scanned document),
    OCR is automatically triggered via Tesseract.
    """
    format_type = (format_type or "").lower().strip()

    try:
        if format_type == "docx":
            from app.services.extraction_docx import extract_docx

            result = extract_docx(file_path)
            data = result.to_dict()
            data["segments"] = _docx_segments(result)

        elif format_type == "xlsx":
            from app.services.extraction_xlsx import extract_xlsx

            result = extract_xlsx(file_path)
            data = result.to_dict()
            data["segments"] = _spreadsheet_segments(result)

        elif format_type == "csv":
            from app.services.extraction_xlsx import extract_csv

            result = extract_csv(file_path)
            data = result.to_dict()
            data["segments"] = _spreadsheet_segments(result)

        elif format_type == "pdf":
            from app.services.extraction_pdf import extract_pdf, extract_pdf_with_ocr

            result = extract_pdf(file_path)
            total_text = (getattr(result, "text", "") or "").strip()
            # If the PDF has very little text, it's likely scanned → use OCR
            if not total_text or len(total_text) < 100:
                logger.info("PDF %s has insufficient text (len=%s), triggering OCR", file_path, len(total_text))
                try:
                    result = extract_pdf_with_ocr(file_path)
                except Exception as exc:  # OCR is optional
                    logger.warning("OCR failed for %s: %s", file_path, exc)
            # Otherwise, the normal text extraction is kept (result already has it)
            data = result.to_dict()
            data["segments"] = _pdf_segments(result)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format d'extraction non supporté: {format_type}",
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Extraction failed for %s (%s)", file_path, format_type)
        raise HTTPException(
            status_code=422,
            detail=f"Échec de l'extraction du document: {exc}",
        ) from exc

    data["format"] = format_type
    data["tables"] = _normalize_tables(result, format_type)
    data.setdefault("text", "")
    data.setdefault("metadata", {})
    data.setdefault("segments", [])
    return data
