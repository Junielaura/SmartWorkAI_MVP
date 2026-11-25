from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models import Task, User, Organization, AuditLog
from app.services.notifications import notify_task_assigned, notify_task_status_changed


router = APIRouter(prefix="/tasks", tags=["tasks"])


def check_task_permission(
    task_id: int,
    current_user: User,
    session: Session,
) -> Task:
    """Verify that the current user has permission to access the task."""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    
    # Users can access tasks assigned to them, or tasks from their organizations,
    # or if they are organization members/admins
    if task.assigned_to_id == current_user.id:
        return task
    if task.organization_id in current_user.organization_ids:
        return task
    if task.created_by_id == current_user.id:
        return task
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accès refusé: vous n'avez pas le droit d'accéder à cette tâche",
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    title: str,
    assigned_to_id: Optional[int] = None,
    status: str = "to_do",
    due_date: Optional[str] = None,
    organization_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task and assign it to a user."""
    title = (title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Le titre de la tâche est requis")

    # Default the assignee to the current user
    assigned_to_id = assigned_to_id or current_user.id

    # Verify the assignee user exists
    assignee = session.get(User, assigned_to_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="Utilisateur assigné introuvable")

    # Verify organization if provided
    if organization_id:
        org = session.get(Organization, organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organisation introuvable")
    else:
        # Use the assignee's organization or the current user's organization
        org = assignee.organization or current_user.organization
        organization_id = organization_id or (org.id if org else None)

    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Format de date d'échéance invalide"
            )

    task = Task(
        title=title,
        status=status,
        assigned_to_id=assigned_to_id,
        organization_id=organization_id,
        created_by_id=current_user.id,
        due_date=parsed_due_date,
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Audit log
    audit_log = AuditLog(
        actor_id=current_user.id,
        action="create_task",
        resource_type="task",
        resource_id=task.id,
        result="success",
    )
    session.add(audit_log)
    
    # Notification
    notify_task_assigned(task_id=task.id, assignee_id=assigned_to_id)
    
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "assigned_to_id": task.assigned_to_id,
        "organization_id": task.organization_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "comments": task.comments,
        "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') else None,
    }


@router.get("/", status_code=status.HTTP_200_OK)
def list_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_filter: Optional[str] = None,
):
    """List tasks accessible to the user."""
    statement = select(Task).where(
        (Task.assigned_to_id == current_user.id)
        | (Task.organization_id.in_(current_user.organization_ids))
        | (Task.created_by_id == current_user.id)
    )
    
    if status_filter:
        statement = statement.where(Task.status == status_filter)
    
    result = session.exec(statement)
    tasks = result.all()
    
    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "assigned_to_id": t.assigned_to_id,
                "organization_id": t.organization_id,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "comments": t.comments,
            }
            for t in tasks
        ]
    }


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific task by ID."""
    task = check_task_permission(task_id, current_user, session)
    
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "assigned_to_id": task.assigned_to_id,
        "organization_id": task.organization_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "comments": task.comments,
    }


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update task status."""
    task = check_task_permission(task_id, current_user, session)
    
    valid_statuses = ["to_do", "in_progress", "validated", "approved", "rejected", "error", "completed"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status invalide. Doit être l'un de: {', '.join(valid_statuses)}",
        )
    
    old_status = task.status
    task.status = new_status
    
    # Track timestamps
    from datetime import datetime, timezone
    if new_status == "in_progress" and not task.started_at:
        task.started_at = datetime.now(timezone.utc)
    elif new_status in ["validated", "approved", "rejected", "error", "completed"]:
        task.completed_at = datetime.now(timezone.utc)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Audit log
    audit_log = AuditLog(
        actor_id=current_user.id,
        action="update_task_status",
        resource_type="task",
        resource_id=task.id,
        result="success",
    )
    session.add(audit_log)
    
    # Notification
    notify_task_status_changed(
        task_id=task.id,
        assignee_id=task.assigned_to_id,
        new_status=new_status,
        old_status=old_status,
    )
    
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "message": f"Status mis à jour de '{old_status}' à '{new_status}'",
    }


@router.patch("/{task_id}/comments")
def add_task_comments(
    task_id: int,
    comment: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a comment to a task."""
    task = check_task_permission(task_id, current_user, session)
    
    from datetime import datetime, timezone
    existing_comments = task.comments if task.comments else {}
    existing_comments[str(datetime.now(timezone.utc))] = {
        "author_id": current_user.id,
        "text": comment,
    }
    
    task.comments = existing_comments
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Audit log
    audit_log = AuditLog(
        actor_id=current_user.id,
        action="add_task_comment",
        resource_type="task",
        resource_id=task.id,
        result="success",
    )
    session.add(audit_log)
    
    return {
        "id": task.id,
        "title": task.title,
        "comments": task.comments,
    }


@router.get("/dashboard/overview", status_code=status.HTTP_200_OK)
def task_dashboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Dashboard overview of tasks and documents for the user."""
    # Count tasks by status
    statement = select(Task).where(
        (Task.assigned_to_id == current_user.id)
        | (Task.organization_id.in_(current_user.organization_ids))
        | (Task.created_by_id == current_user.id)
    )
    all_tasks = session.exec(statement).all()
    
    # Status counts
    status_counts = {}
    for status_val in ["to_do", "in_progress", "validated", "approved", "rejected", "error", "completed"]:
        status_counts[status_val] = sum(1 for t in all_tasks if t.status == status_val)
    
    # Tasks by organization
    org_task_counts = {}
    for org in current_user.organizations:
        org_stmt = select(Task).where(Task.organization_id == org.id)
        org_tasks = session.exec(org_stmt).all()
        org_task_counts[org.id] = len(org_tasks)
    
    # Recent tasks (last 5)
    recent_tasks = sorted(all_tasks, key=lambda t: t.id or 0, reverse=True)[:5]
    
    # Count documents
    from app.models import Document
    doc_statement = select(Document).where(
        (Document.owner_id == current_user.id)
        | (Document.organization_id.in_(current_user.organization_ids))
    )
    documents = session.exec(doc_statement).all()
    
    return {
        "task_statistics": {
            "total": len(all_tasks),
            "by_status": status_counts,
            "recent": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                }
                for t in recent_tasks
            ],
        },
        "document_statistics": {
            "total": len(documents),
            "by_status": {
                status_val: sum(1 for d in documents if d.status == status_val)
                for status_val in ["uploaded", "queued", "processing", "processed", "failed", "needs_review"]
            },
        },
        "organization_task_counts": org_task_counts,
    }