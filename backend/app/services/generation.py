"""Document generation service for SmartWork AI MVP."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import HTTPException

from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import pandas as pd

from app.services.extraction import extract_document
from app.core.config import settings


class GenerationResult:
    """Result of document generation."""
    
    def __init__(
        self,
        success: bool = False,
        file_path: str = "",
        filename: str = "",
        message: str = "",
    ):
        self.success = success
        self.file_path = file_path
        self.filename = filename
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "file_path": self.file_path,
            "filename": self.filename,
            "message": self.message,
        }


# --- Report templates ---


PROFESSIONAL_REPORT_TEMPLATE = {
    "title": "Rapport de synthèse",
    "meta_info": {
        "generated_by": "SmartWork AI",
        "generation_date": None,
        "model_version": None,
        "document_sources": [],
    },
    "sections": [
        {"type": "title", "content": ""},
        {"type": "introduction", "content": ""},
        {"type": "body", "content": ""},
        {"type": "conclusion", "content": ""},
        {"type": "appendices", "content": ""},
    ],
}


def generate_docx_from_data(
    data: Dict[str, Any],
    template: Dict[str, Any] = PROFESSIONAL_REPORT_TEMPLATE,
    model_version: str = "default",
    tone: str = "professional",
) -> GenerationResult:
    """Generate a DOCX document from data and template.
    
    Args:
        data: Dictionary containing generation data (title, content, metadata, etc.)
        template: DOCX template structure
        model_version: Version of the generation model
        tone: Tone of the document (professional, academic, administrative, synthetic)
    
    Returns:
        GenerationResult with file path and status
    """
    try:
        doc = DocxDocument()
        
        # Set default style
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        # Apply tone-specific styling
        if tone == "academic":
            style = doc.styles['Heading 1']
            style.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        elif tone == "admin":
            style = doc.styles['Heading 1']
            style.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)
        elif tone == "synthetic":
            style = doc.styles['Heading 1']
            style.font.color.rgb = RGBColor(0x5D, 0x1E, 0x1E)
        
        # Title
        title = data.get("title", template["title"])
        doc.add_heading(title, level=0)
        
        # Meta information
        meta = data.get("meta", {})
        if meta:
            doc.add_paragraph("")
            meta_text = f"Généré par : {meta.get('generated_by', 'SmartWork AI')}\n"
            meta_text += f"Date : {meta.get('generation_date', datetime.now().strftime('%Y-%m-%d'))}\n"
            meta_text += f"Modèle : {meta.get('model_version', model_version)}\n"
            if meta.get("document_sources"):
                meta_text += f"Sources : {', '.join(str(s) for s in meta['document_sources'][:3])}"
            p = doc.add_paragraph(meta_text)
            p.style = doc.styles['Normal']
            p.style.font.size = Pt(10)
            p.style.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
        
        # Add sections
        for section in template.get("sections", []):
            section_type = section.get("type", "")
            section_content = section.get("content", "")
            
            if section_type == "title":
                doc.add_heading(section_content, level=1)
            elif section_type == "introduction":
                doc.add_heading("Introduction", level=1)
                doc.add_paragraph(section_content or "")
            elif section_type == "body":
                doc.add_heading("Corps du document", level=1)
                if section_content:
                    # Handle different content types
                    if isinstance(section_content, list):
                        for item in section_content:
                            if isinstance(item, dict):
                                doc.add_paragraph(item.get("text", str(item)), style='List Bullet')
                            else:
                                doc.add_paragraph(str(item), style='List Bullet')
                    else:
                        doc.add_paragraph(str(section_content))
                else:
                    doc.add_paragraph("Contenu extrait du document source.")
            elif section_type == "conclusion":
                doc.add_heading("Conclusion", level=1)
                doc.add_paragraph(section_content or "Aucune conclusion extraite.")
            elif section_type == "appendices":
                doc.add_heading("Annexes", level=1)
                doc.add_paragraph(section_content or "Documents annexes.")
        
        # Add tables if data contains tables
        tables_data = data.get("tables", [])
        if tables_data:
            doc.add_heading("Tableaux", level=1)
            for i, table_info in enumerate(tables_data[:5]):  # Limit to 5 tables
                doc.add_heading(f"Tableau {i+1}", level=2)
                if isinstance(table_info, dict) and "rows" in table_info:
                    df = pd.DataFrame(table_info["rows"])
                    if "headers" in table_info:
                        df.columns = table_info["headers"]
                    if not df.empty:
                        # Truncate if too large
                        if len(df) > 20:
                            df = df.head(20)
                            doc.add_paragraph("(affichage limité à 20 lignes)")
                        table = doc.add_table(rows=len(df), cols=len(df.columns))
                        table.style = 'Light Grid Accent 1'
                        table.alignment = WD_TABLE_ALIGNMENT.CENTER
                        for j, row_df in df.iterrows():
                            for k, cell in enumerate(row_df):
                                table.rows[j].cells[k].text = str(cell) if cell is not None else ""
                        # Set column widths approximately
                        for row in table.rows:
                            for idx, cell in enumerate(row.cells):
                                width = Inches(1.5 if idx < 3 else 2.0)
                                cell.width = width
        
        # Save to temporary file
        os.makedirs(settings.GENERATED_DIR, exist_ok=True)
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        file_path = os.path.join(settings.GENERATED_DIR, filename)
        doc.save(file_path)
        
        return GenerationResult(
            success=True,
            file_path=file_path,
            filename=filename,
            message="Document DOCX généré avec succès",
        )
    
    except Exception as e:
        logger.error(f"DOCX generation error: {e}", exc_info=True)
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message=f"Erreur lors de la génération DOCX: {str(e)}",
        )


# Logger
import logging
logger = logging.getLogger(__name__)


def generate_pdf_from_docx(docx_path: str) -> GenerationResult:
    """Convert a DOCX file to PDF.
    
    Note: In MVP, we document the choice and rely on available converters.
    """
    try:
        # Check if we have a PDF converter available
        import subprocess
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", docx_path],
            capture_output=True,
            timeout=30,
        )
        
        if result.returncode == 0:
            # LibreOffice creates the PDF alongside the DOCX
            pdf_path = docx_path.replace(".docx", ".pdf")
            if os.path.exists(pdf_path):
                return GenerationResult(
                    success=True,
                    file_path=pdf_path,
                    filename=os.path.basename(pdf_path),
                    message="PDF généré à partir du DOCX",
                )
        
        # Fallback: document the limitation
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message="Conversion PDF non disponible - DOCX généré (validation humaine recommandée)",
        )
    
    except Exception as e:
        logger.error(f"PDF conversion error: {e}")
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message=f"Erreur conversion PDF: {str(e)}",
        )


def generate_xlsx_from_data(
    data: Dict[str, Any],
    model_version: str = "default",
) -> GenerationResult:
    """Generate an XLSX spreadsheet from data."""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.utils import get_column_letter
        
        wb = openpyxl.Workbook()
        ws = wb.active
        sheet_title = str(data.get("title") or "Données")
        for invalid_char in ("\\", "/", "*", "?", ":", "[", "]"):
            sheet_title = sheet_title.replace(invalid_char, " ")
        ws.title = sheet_title.strip()[:31] or "Données"
        
        # Style definitions
        header_font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font_white = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        
        content = data.get("content", [])
        
        # Write headers
        if content and isinstance(content, list) and content:
            headers = content[0] if content else []
            for k, header in enumerate(headers):
                cell = ws.cell(row=1, column=k+1, value=str(header) if header else "")
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Write data rows
            for i, row in enumerate(content[1:], start=2):
                for k, value in enumerate(row):
                    cell = ws.cell(row=i, column=k+1, value=str(value) if value is not None else "")
                    cell.alignment = Alignment(horizontal='center')
        
        # Adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save
        os.makedirs(settings.GENERATED_DIR, exist_ok=True)
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(settings.GENERATED_DIR, filename)
        wb.save(file_path)
        
        return GenerationResult(
            success=True,
            file_path=file_path,
            filename=filename,
            message="Fichier XLSX généré avec succès",
        )
    
    except Exception as e:
        logger.error(f"XLSX generation error: {e}", exc_info=True)
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message=f"Erreur génération XLSX: {str(e)}",
        )


def generate_summary_report(
    document_id: int,
    model_version: str = "default",
    tone: str = "professional",
) -> GenerationResult:
    """Generate a summary report for a document.
    
    This extracts the document and creates a professional summary.
    """
    from app.db.session import engine
    from app.models import Document, ExtractedData, GeneratedFile
    from sqlmodel import Session, select

    # Get document info and extracted text inside the session scope
    with Session(engine) as session:
        doc = session.get(Document, document_id)
        if not doc:
            return GenerationResult(
                success=False, message="Document introuvable"
            )
        filename = doc.filename
        doc_id = doc.id
        extracted_row = session.exec(
            select(ExtractedData).where(ExtractedData.document_id == document_id)
        ).first()
        extracted = None
        if extracted_row and isinstance(extracted_row.structured_data, dict):
            extracted = extracted_row.structured_data.get("text")

    # Prepare data for generation
    content_text = extracted or "Aucun contenu extrait n'est disponible pour ce document."

    # Determine tone-specific content
    if tone == "academic":
        sections = [
            {"type": "title", "content": filename},
            {"type": "introduction", "content": f"Résumé du document : {filename}"},
            {"type": "body", "content": content_text[:2000] if content_text else ""},
            {"type": "conclusion", "content": "Conclusion extraite du contenu principal."},
        ]
    elif tone == "admin":
        sections = [
            {"type": "title", "content": filename},
            {"type": "introduction", "content": "Document analysé"},
            {"type": "body", "content": content_text[:2000] if content_text else ""},
            {"type": "conclusion", "content": "Points clés identifiés."},
        ]
    elif tone == "synthetic":
        sections = [
            {"type": "title", "content": filename},
            {"type": "introduction", "content": "Synthèse rapide"},
            {"type": "body", "content": content_text[:1500] if content_text else ""},
        ]
    else:  # professional (default)
        sections = [
            {"type": "title", "content": filename},
            {"type": "introduction", "content": "Synthèse du document"},
            {"type": "body", "content": content_text[:2500] if content_text else ""},
            {"type": "conclusion", "content": "Points clés et recommandations."},
        ]

    # Generate DOCX
    data = {
        "title": f"Rapport : {filename}",
        "meta": {
            "generated_by": "SmartWork AI",
            "generation_date": datetime.now().strftime('%Y-%m-%d'),
            "model_version": model_version,
            "document_sources": [{"id": doc_id, "filename": filename}],
        },
        "tables": [],
        "content": sections,
    }

    return generate_docx_from_data(data, model_version=model_version, tone=tone)
def generate_pdf_from_docx(data: Dict[str, Any], model_version: str = "default", tone: str = "professional") -> GenerationResult:
    """Generate a PDF document from data.
    
    Uses weasyprint to convert HTML to PDF.
    """
    try:
        import weasyprint
        from io import BytesIO
        
        # Build HTML content similar to the DOCX template
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Calibri, sans-serif; margin: 40px; }}
                h1 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 10px; }}
                p {{ margin: 0 0 1em 0; }}
                .meta {{ color: #666; font-size: 0.9em; margin-bottom: 2em; }}
                .section {{ margin-top: 2em; }}
            </style>
        </head>
        <body>
            <h1>{data.get('title', 'Rapport')}</h1>
            <div class="meta">
                <p>Généré par : SmartWork AI</p>
                <p>Modèle : {model_version}</p>
                <p>Date : {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        """
        # Add sections if present
        sections = data.get("content", [])
        for section in sections:
            if section.get("type") == "title":
                html += f"<h1>{section.get('content', '')}</h1>"
            elif section.get("type") == "introduction":
                html += "<h2>Introduction</h2>"
                html += f"<p>{section.get('content', '')}</p>"
            elif section.get("type") == "body":
                html += "<h2>Corps du document</h2>"
                html += f"<p>{section.get('content', '')}</p>"
            elif section.get("type") == "conclusion":
                html += "<h2>Conclusion</h2>"
                html += f"<p>{section.get('content', '')}</p>"
        
        html += "</body></html>"
        
        html_bytes = html.encode("UTF-8")
        pdf_bytes = weasyprint.HTML(string=html_bytes).write_pdf()
        
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(settings.GENERATED_DIR, filename)
        os.makedirs(settings.GENERATED_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        
        return GenerationResult(
            success=True,
            file_path=file_path,
            filename=filename,
            message="PDF généré avec succès",
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message=f"Erreur génération PDF: {str(e)}",
        )


def generate_pptx_from_data(data: Dict[str, Any], model_version: str = "default") -> GenerationResult:
    """Generate a PPTX presentation from data.
    
    Creates a simple presentation with title slides and content slides.
    """
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # Title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = data.get("title", "Rapport")
        subtitle.text = f"Généré par SmartWork AI le {datetime.now().strftime('%Y-%m-%d')}"
        
        # Add content slides based on sections
        sections = data.get("content", [])
        for section in sections:
            section_type = section.get("type", "")
            section_content = section.get("content", "")
            
            if section_type == "title":
                slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and content
                slide.shapes.title.text = section.get("content", "")
                slide.placeholders[1].text = ""
            elif section_type == "introduction":
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = "Introduction"
                slide.placeholders[1].text = section_content or ""
            elif section_type == "body":
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = "Corps du document"
                slide.placeholders[1].text = section_content or ""
            elif section_type == "conclusion":
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = "Conclusion"
                slide.placeholders[1].text = section_content or ""
        
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        file_path = os.path.join(settings.GENERATED_DIR, filename)
        os.makedirs(settings.GENERATED_DIR, exist_ok=True)
        prs.save(file_path)
        
        return GenerationResult(
            success=True,
            file_path=file_path,
            filename=filename,
            message="Presentation PPTX générée avec succès",
        )
    except Exception as e:
        logger.error(f"PPTX generation error: {e}", exc_info=True)
        return GenerationResult(
            success=False,
            file_path="",
            filename="",
            message=f"Erreur génération PPTX: {str(e)}",
        )


# Logger (déjà défini plus haut dans le fichier)
