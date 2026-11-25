from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.session import get_session


router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory storage for workflow definitions (to be persisted DB later)
workflows_db: Dict[str, dict] = {}
workflow_runs_db: Dict[str, dict] = {}


class WorkflowCreate(BaseModel):
    name: str
    description: str
    trigger: str
    trigger_params: dict
    actions: list


class WorkflowRunCreate(BaseModel):
    document_id: int


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    document_id: int
    status: str = "pending"
    executed_actions: list = []
    errors: Optional[list] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


@router.post("/", response_model=dict, status_code=status.HTTP_201_OK)
def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: any = Depends(get_current_user),
):
    """Create a new workflow definition."""
    workflow_id = str(uuid4())
    workflows_db[workflow_id] = {
        "id": workflow_id,
        "name": workflow_data.name,
        "description": workflow_data.description,
        "trigger": workflow_data.trigger,
        "trigger_params": workflow_data.trigger_params,
        "actions": workflow_data.actions,
        "is_active": True,
        "owner_id": current_user.id if hasattr(current_user, 'id') else 1,
        "created_at": datetime.utcnow(),
    }
    return {
        "id": workflow_id,
        "name": workflow_data.name,
        "description": workflow_data.description,
        "trigger": workflow_data.trigger,
        "is_active": True,
    }


@router.get("/", response_model=list, status_code=status.HTTP_200_OK)
def list_workflows(
    current_user: any = Depends(get_current_user),
):
    """List workflows accessible to the current user."""
    user_id = current_user.id if hasattr(current_user, 'id') else 1
    user_workflows = [
        w for w in workflows_db.values() 
        if w.get("owner_id") == user_id or w.get("is_active", False)
    ]
    return user_workflows


@router.post("/{workflow_id}/execute", response_model=dict, status_code=status.HTTP_202_OK)
def execute_workflow(
    workflow_id: str,
    payload: WorkflowRunCreate,
    current_user: any = Depends(get_current_user),
):
    """Execute a workflow against a document."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows_db[workflow_id]
    run_id = str(uuid4())
    
    # Execute actions
    executed_actions = []
    errors = []
    
    for action_def in workflow.get("actions", []):
        action_type = action_def.get("action")
        action_params = action_def.get("params", {})
        
        try:
            # Simulate action execution
            executed_actions.append({
                "action": action_type,
                "status": "success",
                "action_type": action_type,
            })
        except Exception as exc:
            executed_actions.append({
                "action": action_type,
                "status": "error",
                "error": str(exc),
            })
            errors.append(f"Action {action_type} failed: {exc}")
    
    completed_at = datetime.utcnow().isoformat() if not errors else None
    status = "completed" if not errors else "completed_with_errors"
    
    run = WorkflowRun(
        id=run_id,
        workflow_id=workflow_id,
        document_id=payload.document_id,
        status=status,
        executed_actions=executed_actions,
        errors=errors if errors else None,
        completed_at=completed_at,
    )
    
    workflow_runs_db[run_id] = run.dict()
    return {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "document_id": payload.document_id,
        "status": status,
        "executed_actions": executed_actions,
        "errors": errors if errors else None,
        "completed_at": completed_at,
    }


@router.get("/{run_id}/status", response_model=dict, status_code=status.HTTP_200_OK)
def get_run_status(
    run_id: str,
    current_user: any = Depends(get_current_user),
):
    """Get the status of a workflow run."""
    if run_id not in workflow_runs_db:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    
    run = workflow_runs_db[run_id]
    return {
        "run_id": run_id,
        "workflow_id": run.get("workflow_id"),
        "document_id": run.get("document_id"),
        "status": run.get("status"),
        "executed_actions": run.get("executed_actions", []),
        "errors": run.get("errors"),
        "completed_at": run.get("completed_at"),
        "duration_seconds": run.get("duration_seconds"),
    }