"""Report generation tasks for SmartWork AI MVP."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from celery import shared_task
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import Report, ReportSchedule, GeneratedFile, User, Organization
from sqlmodel import Session, select, func
from app.services.generation import generate_summary_report, generate_docx_from_data

logger = logging.getLogger(__name__)


# --- Idempotency helpers ---

def _task_key(report_schedule_id: int, **kwargs) -> str:
    """Generate a unique task key for idempotency."""
    return f"report:{report_schedule_id}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"


def _check_idempotence(task_key: str, session) -> bool:
    """Check if a task with this key already ran recently (within 24h).
    Returns True if already ran, False if should proceed.
    """
    # Use Redis SET with EXpiry for idempotency
    # We check if this exact task key was used in the last 24 hours
    from redis import Redis
    redis_client = Redis.from_url(settings.REDIS_URL)
    
    # Check if task already executed today
    key = f"task_key:{task_key}"
    existing = redis_client.get(key)
    
    if existing:
        logger.info(f"Task {task_key} already executed, skipping (idempotence)")
        return True
    
    # Mark this task key as executed with 24h expiry
    redis_client.setex(key, 86400, "1")  # 86400 seconds = 24 hours
    return False


def _next_execution(frequency: str) -> datetime:
    """Compute the next execution datetime for a frequency."""
    now = datetime.now(timezone.utc)
    if frequency == "daily":
        return now + timedelta(days=1)
    if frequency == "weekly":
        return now + timedelta(days=7)
    if frequency == "monthly":
        return now + timedelta(days=30)
    return now + timedelta(days=1)


def generate_schedule_draft(
    schedule: ReportSchedule,
    session: Session,
    owner_id: Optional[int] = None,
):
    """Generate a report draft for a schedule from its source document.

    Returns a ``(report, generated_file)`` tuple, or ``None`` when the
    schedule has no usable source document.
    """
    from app.models import Document

    params = schedule.parameters or {}
    document_id = params.get("document_id")
    if not document_id:
        logger.warning("Schedule %s has no document_id in parameters", schedule.id)
        return None

    try:
        document_id = int(document_id)
    except (TypeError, ValueError):
        logger.warning("Schedule %s has an invalid document_id", schedule.id)
        return None

    document = session.get(Document, document_id)
    if not document:
        logger.warning("Document %s for schedule %s not found", document_id, schedule.id)
        return None

    result = generate_summary_report(
        document_id=document_id,
        model_version="default",
        tone=params.get("tone", "professional"),
    )
    if not result.success:
        logger.error(
            "Report generation failed for schedule %s: %s",
            schedule.id,
            result.message,
        )
        return None

    resolved_owner = owner_id or schedule.owner_id or document.owner_id
    report = Report(
        title=f"Rapport {schedule.frequency} — {document.filename}",
        period=schedule.frequency,
        status="pending_review",
        organization_id=schedule.organization_id,
        owner_id=resolved_owner,
        created_at=datetime.now(timezone.utc),
    )
    session.add(report)
    session.commit()
    session.refresh(report)

    generated_file = GeneratedFile(
        document_id=document_id,
        report_id=report.id,
        filename=result.filename,
        format="docx",
        model_version="default",
        generation_params={
            "report_id": report.id,
            "title": report.title,
            "period": report.period,
            "document_id": document_id,
            "generation_type": "scheduled",
        },
        status="draft",
        owner_id=resolved_owner,
    )
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)

    schedule.next_execution = _next_execution(schedule.frequency)
    session.add(schedule)
    session.commit()

    return report, generated_file


def _run_frequency(frequency: str) -> Dict[str, Any]:
    """Generate scheduled reports for every active organization."""
    from app.db.session import engine
    from app.models import Organization

    results = {"total": 0, "success": 0, "failed": 0, "errors": []}

    with Session(engine) as session:
        organizations = session.exec(
            select(Organization).where(Organization.is_active == True)
        ).all()

        for organization in organizations:
            try:
                outcome = _generate_organization_reports(
                    organization.id, frequency, session
                )
                results["total"] += 1
                results["success"] += outcome["count"]
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "%s report failed for org %s: %s",
                    frequency,
                    organization.id,
                    exc,
                    exc_info=True,
                )
                results["total"] += 1
                results["failed"] += 1
                results["errors"].append(
                    f"Organization {organization.id}: {exc}"
                )

    logger.info("%s report generation complete: %s", frequency, results)
    return results


# --- Report Generation Tasks ---

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    soft_time_limit=30 * 60,
    time_limit=60 * 60,
)
def generate_daily_reports(self) -> Dict[str, Any]:
    """Generate daily reports for all active organizations."""
    return _run_frequency("daily")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    soft_time_limit=30 * 60,
    time_limit=60 * 60,
)
def generate_weekly_reports(self) -> Dict[str, Any]:
    """Generate weekly reports for all active organizations."""
    return _run_frequency("weekly")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    soft_time_limit=30 * 60,
    time_limit=60 * 60,
)
def generate_monthly_reports(self) -> Dict[str, Any]:
    """Generate monthly reports for all active organizations."""
    return _run_frequency("monthly")

def _generate_organization_reports(
    org_id: int, frequency: str, session: Session
) -> Dict[str, Any]:
    """Generate reports for every active schedule of an organization."""
    schedules = session.exec(
        select(ReportSchedule).where(
            ReportSchedule.organization_id == org_id,
            ReportSchedule.frequency == frequency,
            ReportSchedule.is_active == True,
        )
    ).all()

    total_generated = 0
    for schedule in schedules:
        try:
            outcome = generate_schedule_draft(schedule, session)
            if outcome:
                total_generated += 1
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to generate %s report for schedule %s: %s",
                frequency,
                schedule.id,
                exc,
                exc_info=True,
            )

    return {"success": True, "count": total_generated}


def _generate_reports_for_schedule(
    schedule_id: int, frequency: str, session: Session
) -> int:
    """Generate a report draft for a specific schedule."""
    schedule = session.get(ReportSchedule, schedule_id)
    if not schedule:
        return 0
    outcome = generate_schedule_draft(schedule, session)
    return 1 if outcome else 0


def _check_report_freshness(report_id: int, session: Session) -> bool:
    """Check if report source data is fresh enough."""
    from app.models import Report
    from datetime import datetime, timedelta
    
    report = session.get(Report, report_id)
    if not report:
        return False
    
    # Report data must be from within last 24 hours for daily,
    # 7 days for weekly, 30 days for monthly
    now = datetime.now(timezone.utc)
    max_age_map = {"daily": timedelta(hours=24), "weekly": timedelta(days=7), "monthly": timedelta(days=30)}
    max_age = max_age_map.get(report.period, timedelta(hours=24))
    
    # Check the most recent generated file associated with this report
    if report.generated_files:
        latest_file = max(report.generated_files, key=lambda f: f.created_at)
        age = now - latest_file.created_at
        if age > max_age:
            return False
    
    # Also check the report creation date
    if report.created_at:
        age = now - report.created_at
        if age > max_age:
            return False
    
    return True


def _create_report_draft(report: Report, session: Session) -> None:
    """Create a draft report generation from an existing report."""
    from app.models import GeneratedFile
    
    # Check if a draft already exists for today
    stmt = select(GeneratedFile).where(
        GeneratedFile.report_id == report.id,
        GeneratedFile.status == "draft",
    )
    existing = session.exec(stmt).first()
    
    if existing:
        logger.info(f"Draft already exists for report {report.id}, skipping")
        return
    
    # Generate summary report using the generation service
    from app.services.generation import generate_summary_report
    
    result = generate_summary_report(
        document_id=report.id,  # Using report ID as document context
        model_version="default",
        tone="professional",
    )
    
    if not result.success:
        logger.error(f"Report generation failed for {report.id}: {result.message}")
        report.status = "failed"
        session.add(report)
        session.commit()
        return
    
    # Save generated file as draft
    generated_file = GeneratedFile(
        document_id=report.id,
        filename=result.filename,
        format="docx",
        model_version="default",
        generation_params={
            "report_id": report.id,
            "title": report.title,
            "period": report.period,
            "generation_type": "scheduled",
        },
        status="draft",
        owner_id=report.owner_id,
    )
    
    session.add(generated_file)
    session.commit()
    session.refresh(generated_file)
    
    # Update report status to pending_review
    report.status = "pending_review"
    report.published_at = None
    session.add(report)
    session.commit()
    
    logger.info(f"Created draft report {generated_file.id} for report {report.id}")


def _create_new_reports_from_schedule(
    schedule: ReportSchedule, session: Session
) -> None:
    """Create new report drafts based on schedule parameters."""
    from app.models import Report, GeneratedFile
    from datetime import datetime
    
    # Check if we need to create a new report for this scheduling period
    # Look at the last report of this period for this organization
    stmt = select(Report).where(
        Report.organization_id == schedule.organization_id,
        Report.period == schedule.frequency,
    ).order_by(Report.created_at.desc())
    last_reports = session.exec(statement).all()
    
    if not last_reports:
        # No reports exist yet, create first one
        from app.models import User
        user_stmt = select(User).where(User.id == schedule.owner_id)
        user = session.exec(user_stmt).one()
        
        new_report = Report(
            title=f"Rapport {schedule.frequency} - {schedule.organization_id}",
            period=schedule.frequency,
            status="draft",
            organization_id=schedule.organization_id,
            owner_id=schedule.owner_id,
            created_at=datetime.now(timezone.utc),
        )
        
        session.add(new_report)
        session.commit()
        session.refresh(new_report)
        
        # Create draft generated file
        generated_file = GeneratedFile(
            document_id=new_report.id,
            filename=f"rapport_{schedule.frequency}_{datetime.now().strftime('%Y%m%d')}.docx",
            format="docx",
            model_version="default",
            generation_params={
                "report_id": new_report.id,
                "title": new_report.title,
                "period": new_report.period,
                "generation_type": "scheduled",
            },
            status="draft",
            owner_id=schedule.owner_id,
        )
        
        session.add(generated_file)
        session.commit()
        session.refresh(generated_file)
        
        # Update report status
        new_report.status = "pending_review"
        session.add(new_report)
        session.commit()
    
    elif last_reports:
        # Check if we should create a new report based on frequency
        last_report = last_reports[0]
        now = datetime.now(timezone.utc)
        
        # Calculate if enough time has passed based on frequency
        last_created = last_report.created_at
        
        days_since_last = (now - last_created).days
        
        should_create = False
        if schedule.frequency == "daily" and days_since_last >= 1:
            should_create = True
        elif schedule.frequency == "weekly" and days_since_last >= 7:
            should_create = True
        elif schedule.frequency == "monthly" and days_since_last >= 30:
            should_create = True
        
        if should_create:
            new_report = Report(
                title=f"Rapport {schedule.frequency} - {schedule.organization_id} ({now.strftime('%Y-%m')})",
                period=schedule.frequency,
                status="draft",
                organization_id=schedule.organization_id,
                owner_id=schedule.owner_id,
                created_at=now,
            )
            
            session.add(new_report)
            session.commit()
            session.refresh(new_report)
            
            # Create draft generated file
            generated_file = GeneratedFile(
                document_id=new_report.id,
                filename=f"rapport_{schedule.frequency}_{now.strftime('%Y%m%d')}.docx",
                format="docx",
                model_version="default",
                generation_params={
                    "report_id": new_report.id,
                    "title": new_report.title,
                    "period": new_report.period,
                    "generation_type": "scheduled",
                },
                status="draft",
                owner_id=schedule.owner_id,
            )
            
            session.add(generated_file)
            session.commit()
            
            # Update report status
            new_report.status = "pending_review"
            session.add(new_report)
            session.commit()