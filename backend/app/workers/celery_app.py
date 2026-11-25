"""Celery configuration for SmartWork AI MVP reporting."""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
app = Celery(
    "smartwork",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
app.conf.update(
    # Task serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # UTC timezone
    timezone="UTC",
    enable_utc=True,

    # Celery Beat schedule for recurring reports
    beat_schedule={
        "daily-reports": {
            "task": "app.reporting.tasks.generate_daily_reports",
            "schedule": crontab(hour=6, minute=0),  # 6 AM daily
        },
        "weekly-reports": {
            "task": "app.reporting.tasks.generate_weekly_reports",
            "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 6 AM
        },
        "monthly-reports": {
            "task": "app.reporting.tasks.generate_monthly_reports",
            "schedule": crontab(hour=6, minute=0, day_of_month=1),  # 1st of month 6 AM
        },
    },

    # Task tracking
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Auto-discover tasks from reporting module
app.autodiscover_tasks(["app.reporting"])


# Helper function to get organization reports
def get_organization_reports(org_id: int, session) -> list:
    """Get all reports for an organization."""
    from app.models import Report
    from sqlmodel import select
    
    statement = select(Report).where(Report.organization_id == org_id)
    results = session.exec(statement)
    return results.all()


def check_report_freshness(report_id: int, session) -> bool:
    """Check if report data is fresh enough for generation."""
    from app.models import Report
    from datetime import datetime, timedelta
    
    report = session.get(Report, report_id)
    if not report:
        return False
    
    # Check if report has recent data (within last 24 hours)
    # This is a simplified check - in practice would check source documents
    if report.created_at:
        age = datetime.now(timezone.utc) - report.created_at
        return age < timedelta(hours=24)
    
    return False