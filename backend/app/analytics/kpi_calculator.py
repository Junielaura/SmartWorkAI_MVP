"""Analytics service for SmartWork AI MVP - KPI calculation and data visualization."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from pandas import DataFrame
import numpy as np

from app.core.config import settings


class KPIResult:
    """Result of KPI calculation."""
    
    def __init__(
        self,
        name: str,
        value: Any,
        unit: str = "",
        definition: str = "",
        formula: str = "",
        confidence: float = 1.0,
        warnings: List[str] = None,
    ):
        self.name = name
        self.value = value
        self.unit = unit
        self.definition = definition
        self.formula = formula
        self.confidence = confidence
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "definition": self.definition,
            "formula": self.formula,
            "confidence": self.confidence,
            "warnings": self.warnings,
        }


class DataProfiling:
    """Profiling analysis of a pandas DataFrame."""
    
    def __init__(self, df: DataFrame, name: str = "dataset"):
        self.df = df.copy()
        self.name = name
        self.columns_info: Dict[str, Dict] = {}
        self.total_rows = len(df)
    
    def profile(self) -> Dict[str, Any]:
        """Generate complete profiling report."""
        self._analyze_columns()
        return {
            "name": self.name,
            "rows": self.total_rows,
            "columns": len(self.df.columns),
            "column_types": {c: str(self.df[c].dtype) for c in self.df.columns},
            "columns": self.columns_info,
            "memory_usage": self.df.memory_usage(deep=True).to_dict(),
            "duplicates": int(self.df.duplicated().sum()),
            "missing_values": {
                col: {
                    "count": int(self.df[col].isna().sum()),
                    "percentage": round(self.df[col].isna().mean() * 100, 2),
                }
                for col in self.df.columns
            },
        }
    
    def _analyze_columns(self) -> None:
        """Analyze each column and store information."""
        for col in self.df.columns:
            series = self.df[col]
            info: Dict[str, Any] = {
                "dtype": str(series.dtype),
                "nullable": int(series.isna().sum()),
                "nullable_pct": round(series.isna().mean() * 100, 2),
                "unique": int(series.nunique()),
                "unique_pct": round(series.nunique() / self.total_rows * 100, 2) if self.total_rows > 0 else 0,
            }
            
            # Type-specific analysis
            if series.dtype in ["int64", "float64", "float32"]:
                info.update({
                    "min": float(series.min()) if not series.empty else None,
                    "max": float(series.max()) if not series.empty else None,
                    "mean": round(float(series.mean()), 4) if not series.empty else None,
                    "median": float(series.median()) if not series.empty else None,
                    "std": round(float(series.std()), 4) if not series.empty else None,
                })
                # Detect if it might be a date
                if "date" in str(series.dtype).lower() or self._looks_like_date(series.head(10)):
                    info["type_hint"] = "date"
                else:
                    info["type_hint"] = "numeric"
            
            elif series.dtype == "object":
                # String column - check if it looks like categorical
                n_unique_ratio = series.nunique() / self.total_rows if self.total_rows > 0 else 0
                if n_unique_ratio < 0.5 and series.str.len().median() < 50:
                    info["type_hint"] = "categorical"
                    info["top_values"] = series.value_counts().head(5).to_dict()
                else:
                    info["type_hint"] = "text"
                    # Check for date patterns
                    if self._looks_like_date(series.head(10)):
                        info["type_hint"] = "date"
                    # Check for URL/email patterns
                    elif series.str.contains(r"https?://", na=True).any():
                        info["contains"] = "urls"
                    elif series.str.contains(r"\S+@\S+", na=True).any():
                        info["contains"] = "emails"
            
            else:
                info["type_hint"] = "other"
            
            self.columns_info[col] = info
    
    def _looks_like_date(self, series) -> bool:
        """Check if series values look like dates."""
        import re
        date_pattern = re.compile(r"^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}")
        valid_dates = 0
        for val in series.dropna().head(20):
            if val and isinstance(val, str) and date_pattern.match(val):
                valid_dates += 1
        return valid_dates / max(len(series.dropna().head(20)), 1) > 0.6


class KPICalculator:
    """Calculator for common business KPIs using Pandas/SQL."""
    
    @staticmethod
    def sum_kpi(
        df: DataFrame,
        column: str,
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KPIResult]:
        """Calculate sum KPI, optionally grouped."""
        if filters:
            df = KPICalculator._apply_filters(df, filters)
        
        if group_by:
            grouped = df.groupby(group_by)[column].sum().reset_index()
            return [
                KPIResult(
                    name=f"{column}_sum_{'_'.join(str(row[g]) for g in group_by)}",
                    value=row[column],
                    unit=str(df[column].dtype) if column in df.columns else "",
                    formula=f"SUM({column})",
                    definition=f"Somme de {column}",
                    confidence=1.0,
                )
                for _, row in grouped.iterrows()
            ]
        else:
            total = df[column].sum() if column in df.columns else 0
            return [KPIResult(
                name=f"{column}_sum",
                value=total,
                unit=str(df[column].dtype) if column in df.columns else "",
                formula=f"SUM({column})",
                definition=f"Somme totale de {column}",
                confidence=1.0,
            )]
    
    @staticmethod
    def avg_kpi(
        df: DataFrame,
        column: str,
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KPIResult]:
        """Calculate average KPI."""
        if filters:
            df = KPICalculator._apply_filters(df, filters)
        
        if group_by:
            grouped = df.groupby(group_by)[column].mean().reset_index()
            return [
                KPIResult(
                    name=f"{column}_avg_{'_'.join(str(row[g]) for g in group_by)}",
                    value=row[column],
                    unit=str(df[column].dtype) if column in df.columns else "",
                    formula=f"AVG({column})",
                    definition=f"Moyenne de {column}",
                    confidence=1.0,
                )
                for _, row in grouped.iterrows()
            ]
        else:
            avg = df[column].mean() if column in df.columns else 0
            return [KPIResult(
                name=f"{column}_avg",
                value=round(avg, 4),
                unit=str(df[column].dtype) if column in df.columns else "",
                formula=f"AVG({column})",
                definition=f"Moyenne de {column}",
                confidence=1.0,
            )]
    
    @staticmethod
    def count_kpi(
        df: DataFrame,
        column: str,
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KPIResult]:
        """Calculate count KPI."""
        if filters:
            df = KPICalculator._apply_filters(df, filters)
        
        if group_by:
            grouped = df.groupby(group_by)[column].count().reset_index()
            return [
                KPIResult(
                    name=f"{column}_count_{'_'.join(str(row[g]) for g in group_by)}",
                    value=row[column],
                    unit="",
                    formula=f"COUNT({column})",
                    definition=f"Nombre d'entrées de {column}",
                    confidence=1.0,
                )
                for _, row in grouped.iterrows()
            ]
        else:
            count = df[column].count() if column in df.columns else 0
            return [KPIResult(
                name=f"{column}_count",
                value=count,
                unit="",
                formula=f"COUNT({column})",
                definition=f"Nombre total d'entrées de {column}",
                confidence=1.0,
            )]
    
    @staticmethod
    def _apply_filters(df: DataFrame, filters: Dict[str, Any]) -> DataFrame:
        """Apply filters to DataFrame."""
        result = df.copy()
        for col, value in filters.items():
            if col in result.columns:
                if isinstance(value, list):
                    result = result[result[col].isin(value)]
                else:
                    result = result[result[col] == value]
        return result
    
    @staticmethod
    def growth_rate_kpi(
        df: DataFrame,
        value_column: str,
        date_column: str,
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KPIResult]:
        """Calculate growth rate compared to previous period."""
        if filters:
            df = KPICalculator._apply_filters(df, filters)
        
        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.sort_values(date_column)
        
        # Calculate period-over-period
        if group_by:
            grouped = df.groupby(group_by + [date_column])[value_column].sum().reset_index()
        else:
            grouped = df.groupby([date_column])[value_column].sum().reset_index()
        
        # Calculate growth
        results = []
        for col in grouped.columns:
            if col == date_column:
                continue
            
        # Simplified: return last period vs previous period
        if len(grouped) < 2:
            return []
        
        # Get last two periods
        sorted_df = grouped.sort_values(date_column)
        last = sorted_df.iloc[-1][value_column]
        prev = sorted_df.iloc[-2][value_column] if len(sorted_df) >= 2 else 0
        
        change = last - prev
        pct_change = (change / prev * 100) if prev != 0 else 0
        
        return [KPIResult(
            name=f"{value_column}_growth",
            value=round(pct_change, 2),
            unit="%",
            formula=f"(({value_column}_last - {value_column}_prev) / {value_column}_prev) * 100",
            definition=f"Taux de croissance par rapport à la période précédente",
            confidence=1.0,
            warnings=["Calcul basé sur les 2 dernières périodes disponibles"] if len(sorted_df) >= 2 else ["Période insuffisante pour calcul de croissance"],
        )]
    
    @staticmethod
    def conversion_rate_kpi(
        df: DataFrame,
        success_column: str,
        total_column: str,
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KPIResult]:
        """Calculate conversion rate."""
        if filters:
            df = KPICalculator._apply_filters(df, filters)
        
        if group_by:
            grouped = df.groupby(group_by).apply(
                lambda x: pd.Series({
                    "rate": (x[success_column].sum() / x[total_column].sum() * 100) if x[total_column].sum() > 0 else 0,
                    "success": int(x[success_column].sum()),
                    "total": int(x[total_column].sum()),
                })
            ).reset_index()
            grouped.columns = [col for col in grouped.columns if col != '__index_level_0__']
            
            results = []
            for _, row in grouped.iterrows():
                group_vals = [str(row[g]) for g in group_by] if group_by else ["overall"]
                group_key = "_".join(group_vals)
                results.append(KPIResult(
                    name=f"conversion_rate_{group_key}",
                    value=round(row["rate"], 2),
                    unit="%",
                    formula=f"{success_column} / {total_column} * 100",
                    definition=f"Taux de conversion : {success_column} sur {total_column}",
                    confidence=1.0,
                ))
            return results
        else:
            total_success = df[success_column].sum() if success_column in df.columns else 0
            total = df[total_column].sum() if total_column in df.columns else 0
            rate = (total_success / total * 100) if total > 0 else 0
            
            return [KPIResult(
                name="conversion_rate",
                value=round(rate, 2),
                unit="%",
                formula=f"{success_column} / {total_column} * 100",
                definition=f"Taux de conversion : réussis sur total",
                confidence=1.0,
                warnings=["Division par zéro si total est 0"] if total == 0 else [],
            )]


def generate_chart(
    df: DataFrame,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    color_column: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    title: str = "",
) -> Dict[str, Any]:
    """Generate a Plotly chart figure dictionary."""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Apply filters
    if filters:
        result_df = df.copy()
        for col, value in filters.items():
            if col in result_df.columns:
                if isinstance(value, list):
                    result_df = result_df[result_df[col].isin(value)]
                else:
                    result_df = result_df[result_df[col] == value]
    else:
        result_df = df
    
    # Determine chart type
    chart_type = chart_type.lower()
    
    if chart_type == "bar":
        if y_column:
            fig = px.bar(
                result_df,
                x=x_column,
                y=y_column,
                color=color_column,
                title=title or f"Bar chart: {y_column} by {x_column}",
            )
        else:
            # Count bar chart
            fig = px.bar(
                result_df[x_column].value_counts().reset_index(),
                x=x_column,
                y="count",
                title=title or f"Count by {x_column}",
            )
    
    elif chart_type == "line":
        if y_column:
            fig = px.line(
                result_df,
                x=x_column,
                y=y_column,
                color=color_column,
                title=title or f"Line chart: {y_column} over {x_column}",
            )
    
    elif chart_type == "pie":
        if y_column:
            fig = px.pie(
                result_df,
                names=x_column,
                values=y_column,
                title=title or f"Pie chart: {title}",
            )
        else:
            fig = px.pie(
                result_df[x_column].value_counts().reset_index(),
                names=x_column,
                values="count",
                title=title or f"Distribution of {x_column}",
            )
    
    elif chart_type == "histogram":
        if y_column:
            fig = px.histogram(
                result_df,
                x=x_column,
                y=y_column,
                title=title or f"Histogram: {y_column}",
            )
        else:
            fig = px.histogram(
                result_df[x_column],
                title=title or f"Distribution of {x_column}",
            )
    
    elif chart_type == "scatter":
        if y_column:
            fig = px.scatter(
                result_df,
                x=x_column,
                y=y_column,
                color=color_column,
                title=title or f"Scatter: {y_column} vs {x_column}",
            )
    
    else:
        # Default to bar chart
        fig = px.bar(result_df, title=title or "Chart")
    
    # Update layout
    fig.update_layout(
        title={
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16},
        },
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode="closest",
    )
    
    # Convert to dict for JSON serialization
    return fig.to_dict()

def _detect_anomalies_series(series: pd.Series, z_threshold: float, method: str) -> List[float]:
    """Detect anomalies in a pandas Series using the specified method."""
    if method == "zscore":
        mean = series.mean()
        std = series.std()
        if std == 0:
            return []
        z_scores = np.abs((series - mean) / std)
        return series[z_scores > z_threshold].tolist()
    elif method == "iqr":
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return []
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return series[(series < lower) | (series > upper)].tolist()
    else:
        return []


@staticmethod
def detect_anomalies(
    df: DataFrame,
    value_column: str,
    group_by: Optional[List[str]] = None,
    z_threshold: float = 3.0,
    method: str = "zscore",
) -> List[KPIResult]:
    """Detect anomalies in a numeric column using z-score or IQR method."""
    if group_by:
        df = df.copy()
        for col in df.columns:
            if col not in group_by + [value_column]:
                df[col] = df[col].astype(str)
        
        grouped = df.groupby(group_by)[value_column].apply(
            lambda x: _detect_anomalies_series(x, z_threshold, method)
        ).reset_index()
        
        results = []
        for _, row in grouped.iterrows():
            group_vals = [str(row[g]) for g in group_by] if group_by else ["overall"]
            group_key = "_".join(group_vals)
            anomaly_count = row[value_column] if isinstance(row.get(value_column), (int, float)) else 0
            results.append(KPIResult(
                name=f"anomalies_{group_key}",
                value=anomaly_count,
                unit="anomalies",
                formula=f"Détection d'anomalies ({method}) sur {value_column}",
                definition=f"Nombre de valeurs aberrantes détectées using {method} (seuil z={z_threshold})",
                confidence=0.9,
                warnings=[f"Méthode: {method}, seuil: {z_threshold}"],
            ))
        return results
    else:
        values = df[value_column].dropna() if value_column in df.columns else pd.Series()
        if len(values) < 3:
            return []
        
        anomalies = _detect_anomalies_series(values, z_threshold, method)
        return [KPIResult(
            name="anomalies_total",
            value=len(anomalies),
            unit="anomalies",
            formula=f"Détection d'anomalies ({method}) sur {value_column}",
            definition=f"Valeurs identifiées comme aberrantes using {method} (seuil z={z_threshold})",
            confidence=0.9,
            warnings=[f"Méthode: {method}, seuil: {z_threshold}, total valeurs: {len(values)}"],
        )]
