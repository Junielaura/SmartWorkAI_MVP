from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.marketplace import (
    get_marketplace,
    get_model,
    list_models,
    create_model,
    increment_usage,
    search_models,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class ModelCreate(BaseModel):
    name: str
    description: str
    category: str
    template_type: str
    template_params: dict
    is_public: bool


class ModelResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str
    template_type: str
    template_params: dict
    is_public: bool
    owner_id: Optional[str]
    usage_count: int
    created_at: datetime


@router.post("/", response_model=ModelResponse, status_code=201)
def create_model(
    model_data: ModelCreate,
    current_user: any = Depends(get_current_user),
):
    """Create a new marketplace model."""
    model = create_model(
        name=model_data.name,
        description=model_data.description,
        category=model_data.category,
        template_type=model_data.template_type,
        template_params=model_data.template_params,
        is_public=model_data.is_public,
        owner_id=current_user.id if hasattr(current_user, 'id') else None,
    )
    return ModelResponse(**model)


@router.get("/", response_model=List[ModelResponse], status_code=200)
def list_marketplace_models(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: any = Depends(get_current_user),
):
    """List marketplace models."""
    models = list_models(category=category, is_public=is_public)
    return [ModelResponse(**m) for m in models]


@router.get("/{model_id}", response_model=ModelResponse, status_code=200)
def get_model(
    model_id: str,
    current_user: any = Depends(get_current_user),
):
    """Get a marketplace model by ID."""
    model = get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Modèle introuvable")
    increment_usage(model_id)
    return ModelResponse(**model)


@router.get("/search/{query}", response_model=List[ModelResponse], status_code=200)
def search_models(
    query: str,
    category: Optional[str] = None,
    current_user: any = Depends(get_current_user),
):
    """Search marketplace models."""
    models = search_models(query, category)
    return [ModelResponse(**m) for m in models]
