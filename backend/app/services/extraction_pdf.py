"""PDF extraction service using PyMuPDF with optional OCR support."""

from __future__ import annotations

from typing import Any, Dict, List

import fitz  # PyMuPDF
from fastapi import HTTPException


class ExtractionResult:
    """Result of document extraction."""

    def __init__(
        self,
        text: str = "",
        tables: List[Dict[str, Any]] | None = None,
        metadata: Dict[str, Any] | None = None,
        pages: int = 0,
        pages_data: List[Dict[str, Any]] | None = None,
    ):
        self.text = text
        self.tables = tables or []
        self.metadata = metadata or {}
        self.pages = pages
        self.pages_data = pages_data or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "tables": self.tables,
            "metadata": self.metadata,
            "pages": self.pages,
            "pages_data": self.pages_data,
        }


def extract_pdf(file_path: str) -> ExtractionResult:
    """Extract text, tables and metadata from a PDF file."""
    doc = fitz.open(file_path)
    result = ExtractionResult()
    result.pages = len(doc)

    if doc.metadata:
        result.metadata = {
            "title": doc.metadata.get("title"),
            "author": doc.metadata.get("author"),
            "subject": doc.metadata.get("subject"),
            "creator": doc.metadata.get("creator"),
            "producer": doc.metadata.get("producer"),
            "creation_date": doc.metadata.get("creation_date"),
            "modification_date": doc.metadata.get("modification_date"),
        }

    full_text_parts: List[str] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1
        page_text = page.get_text("text") or ""
        full_text_parts.append(page_text)

        result.pages_data.append(
            {
                "page": page_number,
                "text": page_text,
                "tables": _detect_tables(page),
            }
        )
        result.tables.extend(
            {**table, "page": page_number} for table in result.pages_data[-1]["tables"]
        )

    result.text = "\n".join(full_text_parts)
    doc.close()
    return result


def _detect_tables(page) -> List[Dict[str, Any]]:
    """Best-effort table detection using PyMuPDF text blocks."""
    tables: List[Dict[str, Any]] = []
    try:
        blocks = page.get_text("blocks") or []
    except Exception:
        return tables

    for block in blocks:
        if len(block) < 5:
            continue
        bbox, block_type, text = block[0], block[1], block[4]
        if block_type != 0 or not text or not text.strip():
            continue
        lines = [line for line in text.strip().split("\n") if line.strip()]
        if len(lines) >= 2 and any("|" in line or "\t" in line for line in lines):
            tables.append(
                {
                    "bbox": list(bbox),
                    "text": "\n".join(lines),
                    "type": "detected",
                }
            )
    return tables


def extract_pdf_with_ocr(file_path: str) -> ExtractionResult:
    """Extract from a PDF using OCR for scanned documents."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise HTTPException(
            status_code=501,
            detail="OCR non disponible: installez pytesseract et tesseract-ocr",
        ) from exc

    doc = fitz.open(file_path)
    result = ExtractionResult(pages=len(doc))

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_text = pytesseract.image_to_string(image, lang="fra+eng")
        result.pages_data.append(
            {"page": page_index + 1, "text": ocr_text, "tables": []}
        )
        result.text += f"\n--- Page {page_index + 1} ---\n{ocr_text}"

    doc.close()
    return result
