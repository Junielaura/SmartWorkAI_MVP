"""Workflow/automation service for SmartWork AI Studio visual builder."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.core.config import settings
from app.models import Document, DocumentVersion, Workflow, WorkflowRun

logger = logging.getLogger(__name__)

TRIGGER_TYPES = {"import", "schedule", "manual", "document_change"}
ACTION_TYPES = {
    "classify",
    "extract",
    "generate",
    "notify",
    "task_create",
    "report_generate",
    "storage_move",
}

MAX_WORKFLOW_DEPTH = 5


class WorkflowDefinition(BaseModel):
    """Pydantic model for workflow definition validation."""

    name: str
    description: str
    trigger: str
    trigger_params: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    organization_id: Optional[int] = None


def validate_trigger(trigger: str, trigger_params: Dict[str, Any]) -> bool:
    """Validate that a trigger type and its params are supported."""
    if trigger not in TRIGGER_TYPES:
        logger.warning("Unsupported trigger type: %s", trigger)
        return False
    return True


def validate_action(action: Dict[str, Any]) -> bool:
    """Validate that an action type and its params are supported."""
    action_type = action.get("action")
    if action_type not in ACTION_TYPES:
        logger.warning("Unsupported action type: %s", action_type)
        return False
    return True


def build_workflow_run(
    workflow: Workflow,
    initiating_document: Optional[Document] = None,
) -> WorkflowRun:
    """Execute a workflow against a document and return the run record."""
    run_id = str(uuid.uuid4())
    executed_actions: List[Dict[str, Any]] = []
    errors: List[str] = []

    for action_def in workflow.actions:
        if not validate_action(action_def):
            errors.append(f"Invalid action definition: {action_def.get('action')}")
            continue

        action_type = action_def["action"]
        action_params = action_def.get("params", {})

        try:
            result = execute_action(
                action_type,
                action_params,
                initiating_document,
            )
            executed_actions.append(
                {"action": action_type, "status": "success", "result": result}
            )
        except Exception as exc:
            executed_actions.append(
                {"action": action_type, "status": "error", "error": str(exc)}
            )
            errors.append(f"Action {action_type} failed: {exc}")

    run = WorkflowRun(
        id=run_id,
        workflow_id=workflow.id,
        document_id=initiating_document.id if initiating_document else None,
        status="completed" if not errors else "completed_with_errors",
        executed_actions=json.dumps(executed_actions),
        errors=json.dumps(errors) if errors else None,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def execute_action(
    action_type: str,
    params: Dict[str, Any],
    document: Optional[Document] = None,
) -> Any:
    """Execute a single action and return the result."""
    if action_type == "classify":
        from app.services.classification import classify_document
        return classify_document(document)

    if action_type == "extract":
        from app.services.extraction import extract_document
        return extract_document(document.storage_path, document.format)

    if action_type == "generate":
        from app.services.generation import generate_report
        return generate_report(
            document_id=document.id if document else None,
            template_id=params.get("template_id"),
            format_type=params.get("format_type", "docx"),
        )

    if action_type == "notify":
        from app.services.notifications import send_notification
        return send_notification(
            recipient=params.get("recipient"),
            message=params.get("message"),
            notification_type=params.get("type", "info"),
        )

    if action_type == "task_create":
        from app.services.tasks import create_task
        return create_task(
            title=params.get("title", "Workflow task"),
            description=params.get("description"),
            owner_id=params.get("owner_id"),
            due_date=params.get("due_date"),
            organization_id=params.get("organization_id"),
        )

    if action_type == "report_generate":
        from app.services.reporting import generate_report_immediate
        return generate_report_immediate(
            report_id=params.get("report_id"),
            organization_id=params.get("organization_id"),
        )

    if action_type == "storage_move":
        from app.services.ingestion import move_to_generated
        return move_to_generated(document.storage_path)

    raise HTTPException(
        status_code=400,
        detail=f"Action type not supported: {action_type}",
    )


def list_user_workflows(
    user, session, organization_id: Optional[int] = None
) -> List[Workflow]:
    """List workflows accessible to a user."""
    from app.models import Workflow

    statement = select(Workflow).where(Workflow.is_active == True)
    if organization_id:
        statement = statement.where(Workflow.organization_id == organization_id)
    elif getattr(user, "organization_id", None):
        statement = statement.where(Workflow.organization_id == user.organization_id)

    return session.exec(statement).all()


def create_workflow(
    name: str,
    description: str,
    trigger: str,
    trigger_params: Dict[str, Any],
    actions: List[Dict[str, Any]],
    owner_id: int,
    organization_id: Optional[int] = None,
) -> Workflow:
    """Create a new workflow definition."""
    from app.models import Workflow

    if not validate_trigger(trigger, trigger_params):
        raise HTTPException(status_code=400, detail="Invalid trigger configuration")

    for action_def in actions:
        if not validate_action(action_def):
            raise HTTPException(
                status_code=400, detail=f"Invalid action: {action_def.get('action')}"
            )

    workflow = Workflow(
        name=name,
        description=description,
        trigger=trigger,
        trigger_params=json.dumps(trigger_params),
        actions=json.dumps(actions),
        is_active=True,
        owner_id=owner_id,
        organization_id=organization_id,
    )
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


def execute_workflow(
    workflow_id: int, document_id: int, session
) -> WorkflowRun:
    """Execute a stored workflow against a document."""
    from app.models import Workflow, WorkflowRun

    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return build_workflow_run(workflow, document)