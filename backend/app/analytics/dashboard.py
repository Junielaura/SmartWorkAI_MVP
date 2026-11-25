from typing import Optional
from typing import Any, Dict, Optional
from fastapi import APIRouter as APIRouterFastAPI, Depends, HTTPException
from sqlmodel import Session, select, func

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import Document, User
from app.analytics.kpi_calculator import (
    KPICalculator,
    DataProfiling,
    generate_chart,
)
import pandas as pd
import io
import base64


api_v1_router = APIRouterFastAPI(prefix="/analytics", tags=["analytics"])


@api_v1_router.post("/profile/{document_id}", )
def profile_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Profile a document's extracted data for dashboard insights."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    # Get extracted data
    extracted = doc.extracted_data or {}
    text = extracted.get("text", "") if extracted else ""
    
    # If we have chunks with table data, try to build a DataFrame
    chunks = doc.chunks or []
    tables_data = [c.get("content_text", "") for c in chunks if c.get("chunk_type") == "table"]
    
    profiling = {"type": "text_only", "data_points": 0}
    
    if tables_data:
        # Try to build a simple DataFrame from table texts
        rows = []
        for table_text in tables_data[:5]:  # Limit to 5 tables
            # Simple parsing: try to split by lines and then by |
            lines = table_text.strip().split("\n")
            if lines:
                # First line might be header
                header = [h.strip() for h in lines[0].split("|") if h.strip()]
                for line in lines[1:]:
                    values = [v.strip() for v in line.split("|") if v.strip()]
                    if len(values) >= len(header) if header else True:
                        row_dict = {}
                        for i, h in enumerate(header if header else [f"col_{i}" for i in range(len(values))]):
                            row_dict[h] = values[i] if i < len(values) else ""
                        rows.append(row_dict)
        
        if rows:
            try:
                df = pd.DataFrame(rows)
                profiling = DataProfiling(df, name=f"doc_{document_id}").profile()
                profiling["type"] = "tables_extracted"
            except Exception:
                profiling = DataProfiling(pd.DataFrame(), name=f"doc_{document_id}").profile()
    elif text:
        # Text-only: basic profiling
        profiling = DataProfiling(pd.DataFrame(), name=f"doc_{document_id}").profile()
        profiling["type"] = "text_only"
        profiling["data_points"] = len(text.split()) if text else 0
    
    return {
        "document_id": document_id,
        "profiling": profiling,
        "filename": doc.filename,
        "format": doc.format,
    }


@api_v1_router.post("/kpi/sum", )
def calculate_sum_kpi(
    document_id: int,
    column: str,
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Calculate sum KPI for a document's extracted data."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    # Build DataFrame from extracted data
    extracted = doc.extracted_data or {}
    
    # Try to extract structured data
    structured = extracted.get("structured_data", {}) if extracted else {}
    
    rows = []
    if isinstance(structured, list):
        for item in structured[:50]:  # Limit
            if isinstance(item, dict):
                rows.append(item)
    elif isinstance(structured, dict):
        # Convert dict to list of single-row dicts
        rows.append(structured)
    
    if rows:
        try:
            df = pd.DataFrame(rows)
            results = KPICalculator.sum_kpi(df, column, filters=filters)
            return {
                "document_id": document_id,
                "kpi": "sum",
                "column": column,
                "value": results[0].value if results else 0,
                "results": [r.to_dict() for r in results],
                "filename": doc.filename,
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de calculer le SUM: {str(e)}",
            )
    else:
        # No structured data, try to parse from text
        text = extracted.get("text", "") if extracted else ""
        return {
            "document_id": document_id,
            "kpi": "sum",
            "column": column,
            "value": 0,
            "results": [],
            "note": "Aucune donnée structurée disponible, extraction textuelle uniquement",
            "filename": doc.filename,
        }


@api_v1_router.post("/kpi/avg", )
def calculate_avg_kpi(
    document_id: int,
    column: str,
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Calculate average KPI for a document's extracted data."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    structured = doc.extracted_data.get("structured_data", {}) if doc.extracted_data else {}
    
    rows = []
    if isinstance(structured, list):
        for item in structured[:50]:
            if isinstance(item, dict):
                rows.append(item)
    elif isinstance(structured, dict):
        rows.append(structured)
    
    if rows:
        try:
            df = pd.DataFrame(rows)
            results = KPICalculator.avg_kpi(df, column, filters=filters)
            return {
                "document_id": document_id,
                "kpi": "avg",
                "column": column,
                "value": results[0].value if results else 0,
                "results": [r.to_dict() for r in results],
                "filename": doc.filename,
            }
        except Exception as e:
            raise HTTPException(400, detail=f"Impossible de calculer la Moyenne: {str(e)}")
    else:
        return {
            "document_id": document_id,
            "kpi": "avg",
            "column": column,
            "value": 0,
            "results": [],
            "note": "Aucune donnée structurée disponible",
            "filename": doc.filename,
        }


@api_v1_router.post("/kpi/conversion", )
def calculate_conversion_kpi(
    document_id: int,
    success_column: str,
    total_column: str,
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Calculate conversion rate KPI for a document's extracted data."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
            detail="Accès refusé",
        )
    
    extracted = doc.extracted_data or {}
    structured = extracted.get("structured_data", {}) if extracted else {}
    
    rows = []
    if isinstance(structured, list):
        for item in structured[:100]:
            if isinstance(item, dict):
                rows.append(item)
    elif isinstance(structured, dict):
        rows.append(structured)
    
    if rows:
        try:
            df = pd.DataFrame(rows)
            results = KPICalculator.conversion_rate_kpi(df, success_column, total_column)
            return {
                "document_id": document_id,
                "kpi": "conversion_rate",
                "success_column": success_column,
                "total_column": total_column,
                "value": results[0].value if results else 0,
                "results": [r.to_dict() for r in results],
                "filename": doc.filename,
            }
        except Exception as e:
            raise HTTPException(400, detail=f"Erreur taux de conversion: {str(e)}")
    
    return {
        "document_id": document_id,
        "kpi": "conversion_rate",
        "success_column": success_column,
        "total_column": total_column,
        "value": 0,
        "results": [],
        "note": "Données insuffisantes pour calculer le taux de conversion",
        "filename": doc.filename,
    }


@api_v1_router.post("/kpi/growth", )
def calculate_growth_kpi(
    document_id: int,
    value_column: str,
    date_column: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Calculate growth rate KPI."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    extracted = doc.extracted_data or {}
    structured = extracted.get("structured_data", {}) if extracted else {}
    
    rows = []
    if isinstance(structured, list):
        for item in structured[:100]:
            if isinstance(item, dict):
                rows.append(item)
    elif isinstance(structured, dict):
        rows.append(structured)
    
    if rows and len(rows) >= 2:
        try:
            df = pd.DataFrame(rows)
            # Ensure date column is datetime
            if date_column in df.columns:
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                results = KPICalculator.growth_rate_kpi(df, value_column, date_column)
                return {
                    "document_id": document_id,
                    "kpi": "growth_rate",
                    "value_column": value_column,
                    "date_column": date_column,
                    "growth_pct": results[0].value if results else 0,
                    "results": [r.to_dict() for r in results],
                    "filename": doc.filename,
                    "note": results[0].warnings[0] if results and results[0].warnings else None,
                }
        except Exception as e:
            raise HTTPException(400, detail=f"Erreur calcul croissance: {str(e)}")
    
    return {
        "document_id": document_id,
        "kpi": "growth_rate",
        "value_column": value_column,
        "date_column": date_column,
        "growth_pct": 0,
        "results": [],
        "note": "Données insuffisantes pour calcul de croissance",
        "filename": doc.filename,
    }


@api_v1_router.post("/chart/generate", )
def generate_chart_endpoint(
    document_id: int,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    color_column: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    title: str = "",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a Plotly chart for a document."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    # Build DataFrame from extracted data
    extracted = doc.extracted_data or {}
    structured = extracted.get("structured_data", {}) if extracted else {}
    
    rows = []
    if isinstance(structured, list):
        for item in structured[:200]:
            if isinstance(item, dict):
                rows.append(item)
    elif isinstance(structured, dict):
        rows.append(structured)
    
    chart_info = {"type": "none", "image": None, "figure": None}
    
    if rows:
        try:
            df = pd.DataFrame(rows)
            
            # Ensure columns exist
            if x_column and x_column in df.columns:
                # Generate the chart
                figure = generate_chart(
                    df,
                    chart_type,
                    x_column=x_column,
                    y_column=y_column,
                    color_column=color_column,
                    filters=filters,
                    title=title or f"Chart: {doc.filename}",
                )
                
                # Convert to image (base64 string for embedding)
                try:
                    import plotly.io as pio
                    img_bytes = pio.to_image(figure, format="png")
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    chart_info = {
                        "type": "png",
                        "image": f"data:image/png;base64,{img_base64}",
                        "figure": figure,
                    }
                except Exception:
                    chart_info = {
                        "type": "figure_dict",
                        "figure": figure,
                        "note": "Image non disponible, figure Plotly générée",
                    }
                
                chart_info["data_points"] = len(df)
                chart_info["columns_available"] = list(df.columns)
            else:
                chart_info = {
                    "type": "error",
                    "note": f"Colonne x '{x_column}' introuvable",
                }
        except Exception as e:
            chart_info = {
                "type": "error",
                "note": f"Erreur génération chart: {str(e)}",
            }
    else:
        chart_info = {
            "type": "no_data",
            "note": "Aucune donnée structurée disponible pour le graphique",
        }
    
    return {
        "document_id": document_id,
        "chart": chart_info,
        "filename": doc.filename,
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
    }


@api_v1_router.post("/dashboard/{document_id}", )
def dashboard_overview(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Complete dashboard overview for a document."""
    # Verify permissions
    stmt = select(Document).where(Document.id == document_id)
    doc = session.exec(stmt).one()
    
    if doc.owner_id != current_user.id and doc.organization_id not in current_user.organization_ids:
        raise HTTPException(
    
            detail="Accès refusé",
        )
    
    # Profile the data
    profiling_result = None
    chunks = doc.chunks or []
    tables_text = [c.get("content_text", "") for c in chunks if c.get("chunk_type") == "table"]
    
    if tables_text or doc.extracted_data:
        profiling_result = session.send(func.null)  # placeholder
        # Basic profiling
        structured = doc.extracted_data.get("structured_data", {}) if doc.extracted_data else {}
        rows = []
        if isinstance(structured, list):
            for item in structured[:100]:
                if isinstance(item, dict):
                    rows.append(item)
        elif isinstance(structured, dict):
            rows.append(structured)
        
        if rows:
            try:
                import pandas as pd
                df = pd.DataFrame(rows)
                profiling = DataProfiling(df, name=f"doc_{document_id}").profile()
                profiling_result = profiling
            except Exception:
                profiling_result = {"error": "profiling failed"}
    
    # Get some KPIs
    kpi_results = {}
    if rows := ([] if not doc.extracted_data else 
                ([item for item in doc.extracted_data.get("structured_data", {}).get("structured_data", [])[:50]] 
                 if isinstance(doc.extracted_data.get("structured_data"), list) else 
                 [doc.extracted_data.get("structured_data", {})] if isinstance(doc.extracted_data.get("structured_data"), dict) else [])):
        try:
            import pandas as pd
            df = pd.DataFrame(rows)
            if df.shape[1] > 0:
                # Try sum of first numeric column
                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                if numeric_cols:
                    kpi_results["sum_first_numeric"] = int(df[numeric_cols[0]].sum())
        except Exception:
            pass
    
    return {
        "document_id": document_id,
        "filename": doc.filename,
        "format": doc.format,
        "status": doc.status,
        "profiling": profiling_result,
        "kpi_summary": kpi_results,
        "tables_detected": len(tables_text),
        "has_extracted_data": doc.extracted_data is not None,
    }