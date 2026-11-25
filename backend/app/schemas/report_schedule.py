"""Pydantic schemas for report scheduling."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.models import ReportSchedule as ReportScheduleModel


class ReportScheduleCreate(BaseModel):
    """Schema for creating a new report schedule."""
    
    frequency: str = Field(
        description="Report frequency: daily, weekly, or monthly",
        example="daily",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for report scheduling",
        example="UTC",
    )
    parameters: Dict[str, Any] = Field(
        default=dict,
        description="Report parameters: sources, filters, recipients",
        example={"sources": ["doc1", "doc2"], "recipients": ["user@example.com"]},
    )
    is_active: bool = Field(default=True, description="Whether the schedule is active")


class ReportScheduleUpdate(BaseModel):
    """Schema for updating a report schedule."""
    
    frequency: Optional[str] = Field(
        default=None,
        description="Report frequency: daily, weekly, or monthly",
        example="weekly",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="Timezone for report scheduling",
        example="Europe/Paris",
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Report parameters: sources, filters, recipients",
        example={"sources": ["doc1"], "recipients": ["user@example.com"]},
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the schedule is active",
    )
    
    @validator("frequency")
    def validate_frequency(cls, v):
        if v and v not in ["daily", "weekly", "monthly"]:
            raise ValueError("Frequency must be one of: daily, weekly, monthly")
        return v


class ReportScheduleInDB(BaseModel):
    """Schema for report schedule as returned from DB."""
    
    id: int
    report_id: Optional[int] = None
    frequency: str
    timezone: str
    next_execution: datetime
    parameters: Dict[str, Any]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportGenerationRequest(BaseModel):
    """Schema for triggering a report generation."""
    
    report_id: int = Field(description="ID of the report to generate")
    force: bool = Field(
        default=False,
        description="Force generation even if recent draft exists",
        example=False,
    )
    include_notifications: bool = Field(
        default=True,
        description="Whether to send notifications",
    )


class ReportNotificationRequest(BaseModel):
    """Schema for report notification configuration."""
    
    recipients: List[str] = Field(
        default=[],
        description="Email recipients for report notifications",
        example=["user@example.com"],
    )
    notification_type: str = Field(
        default="in_app",
        description="Type of notification: in_app, email, both",
        example="both",
    )
    send_on_draft: bool = Field(
        default=False,
        description="Send notification on draft generation",
    )
    send_on_approved: bool = Field(
        default=True,
        description="Send notification on approval",
    )