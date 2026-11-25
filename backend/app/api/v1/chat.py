from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models import AuditLog, Conversation, User
from app.services.rag.rag_pipeline import process_question


router = APIRouter(prefix="/chat", tags=["chat"])

MAX_STORED_MESSAGES = 10


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ReportRequest(BaseModel):
    conversation_id: int
    question: str
    incorrect_answer: str
    correct_answer: str = ""


def _conversation_for_user(
    conversation_id: int, user: User, session: Session
) -> Conversation:
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    if conversation.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé: cette conversation ne vous appartient pas",
        )
    return conversation


@router.post("/send", status_code=status.HTTP_200_OK)
async def send_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Ask a question over the documents the user is allowed to access."""
    question = (payload.message or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="La question est vide")

    conversation = None
    if payload.conversation_id:
        conversation = _conversation_for_user(
            payload.conversation_id, current_user, session
        )

    result = await process_question(question, current_user, session)

    if conversation is None:
        conversation = Conversation(
            user_id=current_user.id,
            organization_id=current_user.organization_id or 0,
            title=question[:80],
            context_summary={},
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    messages = list((conversation.context_summary or {}).get("messages", []))
    messages.append(
        {
            "role": "user",
            "content": question,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    messages.append(
        {
            "role": "assistant",
            "content": result.get("answer", ""),
            "citations": result.get("citations", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    conversation.context_summary = {
        **(conversation.context_summary or {}),
        "messages": messages[-MAX_STORED_MESSAGES:],
        "last_question": question[:200],
        "last_answer_summary": result.get("answer", "")[:200],
    }
    conversation.last_activity_at = datetime.now(timezone.utc)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return {
        "conversation_id": conversation.id,
        "question": question,
        "answer": result["answer"],
        "citations": result.get("citations", []),
        "source_count": result.get("source_count", 0),
        "fallback": result.get("fallback", True),
        "used_llm": result.get("used_llm", False),
        "injection_detected": result.get("injection_detected", False),
        "response_time": result.get("response_time", 0),
    }


@router.get("/history", status_code=status.HTTP_200_OK)
def get_chat_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List the current user's conversations."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.last_activity_at.desc())
    )
    conversations = session.exec(statement).all()

    return {
        "conversations": [
            {
                "id": conversation.id,
                "title": conversation.title,
                "last_activity_at": (
                    conversation.last_activity_at.isoformat()
                    if conversation.last_activity_at
                    else None
                ),
                "context_summary": conversation.context_summary or {},
            }
            for conversation in conversations
        ]
    }


@router.post("/report", status_code=status.HTTP_200_OK)
def report_incorrect_answer(
    payload: ReportRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Flag an incorrect answer for quality review."""
    _conversation_for_user(payload.conversation_id, current_user, session)

    session.add(
        AuditLog(
            actor_id=current_user.id,
            action="report_incorrect_answer",
            resource_type="conversation",
            resource_id=None,
            result="reported",
        )
    )
    session.commit()

    return {
        "message": "Signalement enregistré avec succès",
        "conversation_id": payload.conversation_id,
        "reported_by": current_user.email,
    }


@router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a conversation with its short-term memory."""
    conversation = _conversation_for_user(conversation_id, current_user, session)
    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": (conversation.context_summary or {}).get("messages", []),
        "context_summary": conversation.context_summary or {},
        "last_activity_at": (
            conversation.last_activity_at.isoformat()
            if conversation.last_activity_at
            else None
        ),
    }
