"""Report scheduling and generation API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import (
    User,
    Organization,
    Report,
    ReportSchedule,
    GeneratedFile,
)
from app.schemas.report_schedule import (
    ReportScheduleCreate,
    ReportScheduleUpdate,
    ReportScheduleInDB,
    ReportGenerationRequest,
    ReportNotificationRequest,
)
from app.reporting.tasks import (
    generate_daily_reports,
    generate_weekly_reports,
    generate_monthly_reports,
    _generate_organization_reports,
    _generate_reports_for_schedule,
    _create_report_draft,
)


router = APIRouter(prefix="/reporting", tags=["reporting"])


@router.post("/schedules", status_code=status.HTTP_201_CREATED)
def create_report_schedule(
    schedule_in: ReportScheduleCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new report schedule."""
    # Verify organization access - user must belong to the organization
    org_id = current_user.organization_ids[0] if current_user.organization_ids else None
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune organisation attribuée à cet utilisateur",
        )
    
    # Create the schedule
    schedule = ReportSchedule(
        report_id=None,  # Will be linked later
        frequency=schedule_in.frequency,
        timezone=schedule_in.timezone or "UTC",
        next_execution=datetime.now(timezone.utc),
        parameters=schedule_in.parameters or {},
        is_active=schedule_in.is_active,
        organization_id=org_id,
        owner_id=current_user.id,
    )
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    return {
        "id": schedule.id,
        "frequency": schedule.frequency,
        "timezone": schedule.timezone,
        "next_execution": schedule.next_execution.isoformat() if schedule.next_execution else None,
        "parameters": schedule.parameters,
        "is_active": schedule.is_active,
        "organization_id": schedule.organization_id,
    }


@router.get("/schedules")
def list_report_schedules(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all report schedules for the user's organizations."""
    # Get user's organizations
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    
    if not org_ids:
        return {"schedules": []}
    
    # Get all schedules for user's organizations
    statement = select(ReportSchedule).where(
        ReportSchedule.organization_id.in_(org_ids)
    )
    schedules = session.exec(statement).all()
    
    return {
        "schedules": [
            {
                "id": s.id,
                "frequency": s.frequency,
                "timezone": s.timezone,
                "next_execution": s.next_execution.isoformat() if s.next_execution else None,
                "parameters": s.parameters,
                "is_active": s.is_active,
                "organization_id": s.organization_id,
            }
            for s in schedules
        ]
    }


@router.put("/schedules/{schedule_id}")
def update_report_schedule(
    schedule_id: int,
    schedule_in: ReportScheduleUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a report schedule."""
    # Get the schedule
    schedule = session.get(ReportSchedule, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planification de rapport introuvable",
        )
    
    # Check ownership - user must belong to the organization
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if schedule.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: vous ne pouvez pas modifier ce planning",
        )
    
    # Update fields
    if schedule_in.frequency is not None:
        schedule.frequency = schedule_in.frequency
    if schedule_in.timezone is not None:
        schedule.timezone = schedule_in.timezone
    if schedule_in.parameters is not None:
        schedule.parameters = schedule_in.parameters
    if schedule_in.is_active is not None:
        schedule.is_active = schedule_in.is_active
    
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    return {
        "id": schedule.id,
        "frequency": schedule.frequency,
        "timezone": schedule.timezone,
        "next_execution": schedule.next_execution.isoformat() if schedule.next_execution else None,
        "parameters": schedule.parameters,
        "is_active": schedule.is_active,
    }


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a report schedule."""
    schedule = session.get(ReportSchedule, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planification de rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if schedule.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    session.delete(schedule)
    session.commit()
    return None


@router.post("/schedules/{schedule_id}/generate", status_code=status.HTTP_202_ACCEPTED)
def trigger_report_generation(
    schedule_id: int,
    force: bool = False,
    include_notifications: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Trigger report generation for a schedule immediately."""
    schedule = session.get(ReportSchedule, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planification de rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if schedule.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Generate the draft synchronously so the user gets immediate feedback
    from app.reporting.tasks import generate_schedule_draft

    outcome = generate_schedule_draft(schedule, session, owner_id=current_user.id)
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Impossible de générer le rapport : associez un document source "
                "à cette planification."
            ),
        )

    report, generated_file = outcome
    return {
        "schedule_id": schedule_id,
        "report_id": report.id,
        "file_id": generated_file.id,
        "filename": generated_file.filename,
        "status": generated_file.status,
        "download_url": f"/api/v1/generation/file/{generated_file.id}",
        "message": "Rapport généré en brouillon",
    }


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_report_now(
    request: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a report immediately for a specific report ID."""
    report = session.get(Report, request.report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if report.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Check if draft already exists (unless force)
    if not request.force:
        from app.models import GeneratedFile
        stmt = select(GeneratedFile).where(
            GeneratedFile.report_id == request.report_id,
            GeneratedFile.status == "draft",
        )
        existing = session.exec(stmt).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un brouillon existe déjà pour ce rapport. Utilisez force=true pour overwrite.",
            )
    
    # Trigger generation task
    from app.reporting.tasks import _create_report_draft
    
    task = _create_report_draft.apply_async(
        args=[request.report_id],
    )
    
    return {
        "task_id": task.id,
        "report_id": request.report_id,
        "message": "Génération de rapport déclenchée",
    }


@router.get("/history", status_code=status.HTTP_200_OK)
def report_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get report generation history."""
    from app.models import Report, GeneratedFile
    
    # Get user's organizations
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    
    # Get reports and their generated files
    statement = select(Report).where(
        Report.organization_id.in_(org_ids) if org_ids else Report.organization_id == 0
    )
    reports = session.exec(statement).all()
    
    history = []
    for report in reports:
        # Get generated files for this report
        stmt2 = select(GeneratedFile).where(GeneratedFile.report_id == report.id)
        generated_files = session.exec(stmt2).all()
        
        for gf in generated_files:
            history.append({
                "id": gf.id,
                "report_id": report.id,
                "report_title": report.title,
                "period": report.period,
                "filename": gf.filename,
                "format": gf.format,
                "status": gf.status,
                "model_version": gf.model_version,
                "created_at": gf.created_at.isoformat() if gf.created_at else None,
                "validated_at": gf.validated_at.isoformat() if gf.validated_at else None,
                "generation_params": gf.generation_params,
            })
    
    # Sort by creation date, newest first
    history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {"history": history}


@router.get("/{report_id}/status", status_code=status.HTTP_200_OK)
def report_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get the status of a report and its generated files."""
    from app.models import Report, GeneratedFile
    
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if report.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Get generated files
    stmt = select(GeneratedFile).where(GeneratedFile.report_id == report_id)
    generated_files = session.exec(stmt).all()
    
    return {
        "report": {
            "id": report.id,
            "title": report.title,
            "period": report.period,
            "status": report.status,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "published_at": report.published_at.isoformat() if report.published_at else None,
        },
        "generated_files": [
            {
                "id": gf.id,
                "filename": gf.filename,
                "format": gf.format,
                "status": gf.status,
                "model_version": gf.model_version,
                "created_at": gf.created_at.isoformat() if gf.created_at else None,
                "validated_at": gf.validated_at.isoformat() if gf.validated_at else None,
            }
            for gf in generated_files
        ],
    }


@router.post("/{report_id}/validate", status_code=status.HTTP_200_OK)
def validate_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Validate a report draft for external diffusion."""
    from app.models import Report, GeneratedFile
    
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if report.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Get generated files with draft status
    stmt = select(GeneratedFile).where(
        GeneratedFile.report_id == report_id,
        GeneratedFile.status == "draft",
    )
    draft_files = session.exec(stmt).all()
    
    if not draft_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun brouillon à valider pour ce rapport",
        )
    
    # Validate each draft file
    for draft in draft_files:
        draft.status = "validated"
        draft.validated_at = datetime.now(timezone.utc)
        session.add(draft)
    
    # Update report status
    report.status = "approved"
    report.published_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    
    # Trigger notifications if configured
    _send_validation_notifications(report, draft_files, session)
    
    return {
        "message": "Rapport validé avec succès",
        "report_id": report_id,
        "validated_files": len(draft_files),
    }


def _send_validation_notifications(
    report: Report, draft_files: list, session: Session
) -> None:
    """Send notifications when a report is validated."""
    from app.models import Notification
    from datetime import datetime, timezone
    
    # Get recipients from report parameters
    recipients = report.parameters.get("recipients", []) if report.parameters else []
    
    for draft in draft_files:
        notification = Notification(
            recipient_type="email" if recipients else "in_app",
            recipient_email=recipients[0] if recipients else None,
            recipient_user_id=draft.owner_id,
            title="Rapport validé",
            message=f"Le rapport '{report.title}' a été validé et est prêt pour diffusion.",
            related_report_id=report.id,
            related_generated_file_id=draft.id,
            status="sent",
            created_at=datetime.now(timezone.utc),
        )
        session.add(notification)


@router.post("/{report_id}/publish", status_code=status.HTTP_200_OK)
def publish_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Publish a report for external diffusion."""
    from app.models import Report, GeneratedFile
    
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if report.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Verify report has been validated
    if report.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le rapport doit être approuvé avant publication",
        )
    
    # Get validated generated files
    stmt = select(GeneratedFile).where(
        GeneratedFile.report_id == report_id,
        GeneratedFile.status.in_(["validated", "approved"]),
    )
    generated_files = session.exec(stmt).all()
    
    if not generated_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun fichier validé disponible pour la publication",
        )
    
    # Update report status to published
    report.status = "published"
    report.published_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    
    # Send publication notifications
    _send_publication_notifications(report, generated_files, session)
    
    return {
        "message": "Rapport publié avec succès",
        "report_id": report_id,
        "published_at": report.published_at.isoformat(),
    }


def _send_publication_notifications(
    report: Report, generated_files: list, session: Session
) -> None:
    """Send notifications when a report is published."""
    from app.models import Notification
    from datetime import datetime, timezone
    
    # Get recipients from report parameters
    recipients = report.parameters.get("recipients", []) if report.parameters else []
    
    for gf in generated_files:
        notification = Notification(
            recipient_type="email" if recipients else "in_app",
            recipient_email=recipients[0] if recipients else None,
            recipient_user_id=gf.owner_id,
            title="Rapport publié",
            message=f"Le rapport '{report.title}' a été publié et est maintenant disponible.",
            related_report_id=report.id,
            related_generated_file_id=gf.id,
            status="sent",
            created_at=datetime.now(timezone.utc),
        )
        session.add(notification)


@router.post("/{report_id}/email-notify", status_code=status.HTTP_200_OK)
def send_email_notification(
    report_id: int,
    notification_request: ReportNotificationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Send email notification for a report (if email service configured)."""
    from app.models import Report, GeneratedFile, Notification
    from datetime import datetime, timezone
    
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport introuvable",
        )
    
    # Check ownership
    org_ids = current_user.organization_ids if hasattr(current_user, 'organization_ids') else []
    if report.organization_id not in org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé",
        )
    
    # Get generated files
    stmt = select(GeneratedFile).where(GeneratedFile.report_id == report_id)
    generated_files = session.exec(stmt).all()
    
    if not generated_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun fichier généré pour ce rapport",
        )
    
    # In production, would integrate with actual email service (SendGrid, SES, etc.)
    # For MVP, we log and create notification records
    sent_recipients = notification_request.recipients or []
    
    for gf in generated_files:
        notification = Notification(
            recipient_type="email",
            recipient_email=sent_recipients[0] if sent_recipients else None,
            recipient_user_id=gf.owner_id,
            title=f"Rapport : {report.title}",
            message=notification_request.message or f"Le rapport '{report.title}' est prêt.",
            related_report_id=report.id,
            related_generated_file_id=gf.id,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        session.add(notification)
    
    session.commit()
    
    return {
        "message": "Notification email enregistrée",
        "report_id": report_id,
        "recipients": sent_recipients,
        "files_count": len(generated_files),
    }