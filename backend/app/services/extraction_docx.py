"""DOCX extraction service using python-docx."""

from __future__ import annotations

from typing import Any, Dict, List

from docx import Document as DocxDocument


class ExtractionResult:
    """Result of DOCX extraction."""

    def __init__(
        self,
        text: str = "",
        tables: List[Dict[str, Any]] | None = None,
        paragraphs: List[Dict[str, Any]] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        self.text = text
        self.tables = tables or []
        self.paragraphs = paragraphs or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "tables": self.tables,
            "paragraphs": self.paragraphs,
            "metadata": self.metadata,
        }


def extract_docx(file_path: str) -> ExtractionResult:
    """Extract text, tables and metadata from a DOCX file."""
    doc = DocxDocument(file_path)
    result = ExtractionResult()

    core_props = doc.core_properties
    result.metadata = {
        "title": core_props.title,
        "author": core_props.author,
        "subject": core_props.subject,
        "created": str(core_props.created) if core_props.created else None,
        "modified": str(core_props.modified) if core_props.modified else None,
        "paragraphs": len(doc.paragraphs),
        "words": getattr(core_props, "word_count", None),
    }

    for index, paragraph in enumerate(doc.paragraphs):
        if not paragraph.text.strip():
            continue
        style_name = paragraph.style.name if paragraph.style else ""
        result.text += paragraph.text + "\n"
        result.paragraphs.append(
            {
                "index": index,
                "style": style_name,
                "text": paragraph.text,
            }
        )

    for table_index, table in enumerate(doc.tables):
        rows = [[cell.text for cell in row.cells] for row in table.rows]
        result.tables.append(
            {
                "index": table_index,
                "rows": rows,
                "row_count": len(rows),
                "column_count": len(table.columns) if table.columns else 0,
                "text": "\n".join(" | ".join(row) for row in rows),
            }
        )

    return result


def extract_docx_metadata(file_path: str) -> Dict[str, Any]:
    """Extract only metadata from a DOCX file."""
    doc = DocxDocument(file_path)
    core_props = doc.core_properties
    return {
        "title": core_props.title,
        "author": core_props.author,
        "subject": core_props.subject,
        "created": str(core_props.created) if core_props.created else None,
        "modified": str(core_props.modified) if core_props.modified else None,
        "paragraphs": len(doc.paragraphs),
    }
