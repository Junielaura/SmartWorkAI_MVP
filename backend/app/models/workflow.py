"""Database models for SmartWork AI Studio workflow definitions and runs."""

from __future__ import annotations

from sqlmodel import Field, SQLModel, Relationship


class Workflow(SQLModel, table=True):
    """A reusable automation workflow definition (no-code studio)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: str = Field(default="", sa_type="TEXT")
    trigger: str = Field(index=True, max_length=50)
    trigger_params: str = Field(default="{}", sa_type="JSONB")
    actions: str = Field(default="[]", sa_type="JSONB")
    is_active: bool = Field(default=True, index=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    organization_id: Optional[int] = Field(
        default=None, foreign_key="organization.id"
    )
    created_at: Optional[datetime] = Field(default=None, sa_type="TIMESTAMP")
    updated_at: Optional[datetime] = Field(default=None, sa_type="TIMESTAMP")


class WorkflowRun(SQLModel, table=True):
    """A single execution of a workflow against a document."""

    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: Optional[int] = Field(
        default=None, foreign_key="workflow.id"
    )
    document_id: Optional[int] = Field(
        default=None, foreign_key="document.id"
    )
    status: str = Field(default="pending", max_length=50)
    executed_actions: str = Field(default="[]", sa_type="JSONB")
    errors: Optional[str] = Field(default=None, sa_type="TEXT")
    completed_at: Optional[datetime] = Field(default=None, sa_type="TIMESTAMP")
    duration_seconds: Optional[float] = Field(default=None)


# Update Document model to add relationship
from sqlmodel import SQLModel


class Document(SQLModel, table=True):
    """Document model with workflow relationship added."""

    # existing fields...

    # Add relationship to workflows
    workflows: List[Workflow] = Relationship(
        back_populates="documents",  # type: ignore[attr-defined]
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )