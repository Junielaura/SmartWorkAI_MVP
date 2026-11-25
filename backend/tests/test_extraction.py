from pathlib import Path

from app.services.classification import classify_document
from app.services.extraction import extract_document


def test_csv_extraction_has_sheet_provenance(tmp_path: Path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("date,montant,client\n2026-01-01,100,A\n2026-01-02,200,B\n", encoding="utf-8")

    result = extract_document(str(csv_path), "csv")

    assert result["format"] == "csv"
    assert "montant" in result["text"]
    assert result["segments"], "CSV extraction must produce segments"
    assert all(
        segment["metadata"].get("sheet") == "csv" for segment in result["segments"]
    )
    assert result["tables"][0]["headers"] == ["date", "montant", "client"]


def test_docx_extraction_keeps_paragraph_and_table(tmp_path: Path):
    from docx import Document as DocxDocument

    doc = DocxDocument()
    doc.add_heading("Rapport mensuel", level=1)
    doc.add_paragraph("Le chiffre d'affaires progresse de 12 pourcent.")
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "KPI"
    table.rows[0].cells[1].text = "Valeur"
    table.rows[1].cells[0].text = "Chiffre d'affaires"
    table.rows[1].cells[1].text = "1200"
    docx_path = tmp_path / "report.docx"
    doc.save(docx_path)

    result = extract_document(str(docx_path), "docx")

    assert "Rapport mensuel" in result["text"]
    assert result["segments"]
    assert any(segment["chunk_type"] == "table" for segment in result["segments"])
    assert any(
        segment["metadata"].get("paragraph") is not None
        for segment in result["segments"]
        if segment["chunk_type"] == "text"
    )


def test_xlsx_extraction_lists_sheets(tmp_path: Path):
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Budget"
    sheet.append(["poste", "montant"])
    sheet.append(["loyer", 800])
    sheet.append(["salaires", 5000])
    xlsx_path = tmp_path / "budget.xlsx"
    workbook.save(xlsx_path)

    result = extract_document(str(xlsx_path), "xlsx")

    assert result["metadata"]["sheet_names"] == ["Budget"]
    assert result["segments"]
    assert all(
        segment["metadata"].get("sheet") == "Budget" for segment in result["segments"]
    )
    assert result["tables"][0]["row_count"] == 2


def test_pdf_extraction_keeps_page_provenance(tmp_path: Path):
    import fitz

    pdf_path = tmp_path / "note.pdf"
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Facture fournisseur montant total 450 euros")
    pdf.save(pdf_path)
    pdf.close()

    result = extract_document(str(pdf_path), "pdf")

    assert "Facture" in result["text"]
    assert result["segments"]
    assert result["segments"][0]["metadata"]["page"] == 1


def test_classification_detects_invoice():
    result = classify_document("Facture numéro 42, total HT 100 euros, TVA 20%")
    assert result["category"] == "facture"
