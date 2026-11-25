"""XLSX/CSV extraction service using openpyxl and the csv module."""

from __future__ import annotations

import csv
from typing import Any, Dict, List

from openpyxl import load_workbook

MAX_ROWS_PER_SHEET = 5000


class ExtractionResult:
    """Result of spreadsheet extraction."""

    def __init__(
        self,
        text: str = "",
        sheets: List[Dict[str, Any]] | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        self.text = text
        self.sheets = sheets or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "sheets": self.sheets,
            "metadata": self.metadata,
        }


def _stringify(value: Any) -> str:
    return "" if value is None else str(value)


def _build_sheet(name: str, raw_rows: List[List[Any]]) -> Dict[str, Any]:
    rows = [row for row in raw_rows if any(cell not in (None, "") for cell in row)]
    headers: List[str] = []
    data_rows: List[List[str]] = []

    if rows:
        header_row = rows[0]
        headers = [
            _stringify(cell) if _stringify(cell).strip() else f"col_{i + 1}"
            for i, cell in enumerate(header_row)
        ]
        data_rows = [
            [_stringify(cell) for cell in row]
            for row in rows[1 : MAX_ROWS_PER_SHEET + 1]
        ]

    text_lines = []
    if headers:
        text_lines.append("En-têtes: " + " | ".join(headers))
    for index, row in enumerate(data_rows, start=1):
        text_lines.append(f"Ligne {index}: " + " | ".join(row))

    return {
        "name": name,
        "headers": headers,
        "rows": data_rows,
        "row_count": len(data_rows),
        "column_count": len(headers),
        "has_header": bool(headers),
        "text": "\n".join(text_lines),
    }


def extract_xlsx(file_path: str) -> ExtractionResult:
    """Extract text, sheets and metadata from an XLSX file."""
    workbook = load_workbook(file_path, data_only=True, read_only=True)
    result = ExtractionResult()
    result.metadata = {
        "sheet_names": list(workbook.sheetnames),
        "total_sheets": len(workbook.sheetnames),
    }

    for worksheet in workbook.worksheets:
        raw_rows = [
            list(row)
            for row in worksheet.iter_rows(values_only=True)
        ]
        sheet = _build_sheet(worksheet.title, raw_rows)
        result.sheets.append(sheet)
        result.text += f"\n--- Feuille: {worksheet.title} ---\n{sheet['text']}\n"

    workbook.close()
    return result


def extract_csv(file_path: str) -> ExtractionResult:
    """Extract text and metadata from a CSV file."""
    result = ExtractionResult()

    content = None
    used_encoding = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252", "iso-8859-1"):
        try:
            with open(file_path, "r", encoding=encoding, newline="") as handle:
                content = handle.read()
            used_encoding = encoding
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise ValueError("Impossible de lire le fichier CSV - encodage non supporté")

    sample = content[:4096]
    delimiter = ","
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        first_line = sample.splitlines()[0] if sample.splitlines() else ""
        for candidate in (",", ";", "\t", "|"):
            if candidate in first_line:
                delimiter = candidate
                break

    rows = list(csv.reader(content.splitlines(), delimiter=delimiter))
    sheet = _build_sheet("csv", rows)

    result.metadata = {
        "rows": sheet["row_count"],
        "columns": sheet["column_count"],
        "delimiter": delimiter,
        "encoding": used_encoding,
        "content_length": len(content),
    }
    result.sheets = [sheet]
    result.text = f"--- Feuille: csv ---\n{sheet['text']}\n"

    return result
