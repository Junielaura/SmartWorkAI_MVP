"""Marketplace service for SmartWork AI - model catalog and publishing."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.core.config import settings
from app.models import Document, GeneratedFile, Report, ReportSchedule

logger = logging.getLogger(__name__)

MODEL_CATEGORIES = {
    "report": "Rapports administratifs et professionnels",
    "financial": "Rapports financiers",
    "meeting": "Comptes rendus de réunion",
    "analysis": "Analyses et études",
    "summary": "Synthèses documentaires",
    "template": "Modèles de document",
}

# In-memory marketplace storage (to be persisted DB later)
marketplace_db: Dict[str, dict] = {}


class MarketplaceModel(BaseModel):
    """Model definition for the marketplace."""
    id: str
    name: str
    description: str
    category: str
    version: str
    template_type: str  # docx, pdf, xlsx, pptx
    template_params: dict  # Default parameters
    is_public: bool
    owner_id: Optional[str] = None
    usage_count: int = 0
    created_at: datetime


def get_marketplace() -> Dict[str, dict]:
    """Get the marketplace database."""
    return marketplace_db


def get_model(model_id: str) -> Optional[dict]:
    """Get a model by ID."""
    return marketplace_db.get(model_id)


def list_models(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> List[dict]:
    """List models, optionally filtered by category and visibility."""
    models = list(marketplace_db.values())
    
    if category:
        models = [m for m in models if m.get("category") == category]
    
    if is_public is not None:
        models = [m for m in models if m.get("is_public") == is_public]
    
    return models


def create_model(
    name: str,
    description: str,
    category: str,
    template_type: str,
    template_params: dict,
    is_public: bool,
    owner_id: Optional[str] = None,
) -> dict:
    """Create a new marketplace model."""
    model_id = str(uuid4())
    model = {
        "id": model_id,
        "name": name,
        "description": description,
        "category": category,
        "version": "1.0.0",
        "template_type": template_type,
        "template_params": template_params,
        "is_public": is_public,
        "owner_id": owner_id,
        "usage_count": 0,
        "created_at": datetime.utcnow(),
    }
    marketplace_db[model_id] = model
    return model


def increment_usage(model_id: str) -> None:
    """Increment the usage count for a model."""
    if model_id in marketplace_db:
        marketplace_db[model_id]["usage_count"] += 1


def search_models(
    query: str,
    category: Optional[str] = None,
) -> List[dict]:
    """Search models by name/description and optionally by category."""
    models = marketplace_db.values()
    if category:
        models = [m for m in models if m.get("category") == category]
    
    query_lower = query.lower()
    results = []
    for m in models:
        if query_lower in m.get("name", "").lower() or query_lower in m.get("description", "").lower():
            results.append(m)
    
    return results
