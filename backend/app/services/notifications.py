"""Notification service for SmartWork AI MVP."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import redis

from app.core.config import settings


def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def notify_task_assigned(task_id: int, assignee_id: int) -> None:
    """Send notification when a task is assigned."""
    try:
        r = get_redis()
        notification = {
            "type": "task_assigned",
            "task_id": task_id,
            "assignee_id": assignee_id,
            "timestamp": __import__("datetime").datetime.now(timezone.utc).isoformat(),
        }
        key = f"notifications:user:{assignee_id}"
        r.rpush(key, json.dumps(notification))
    except Exception:
        # Redis might not be available in all environments
        pass


def notify_task_status_changed(
    task_id: int,
    assignee_id: int,
    new_status: str,
    old_status: str,
) -> None:
    """Send notification when task status changes."""
    try:
        r = get_redis()
        notification = {
            "type": "task_status_changed",
            "task_id": task_id,
            "assignee_id": assignee_id,
            "new_status": new_status,
            "old_status": old_status,
            "timestamp": __import__("datetime").datetime.now(timezone.utc).isoformat(),
        }
        key = f"notifications:user:{assignee_id}"
        r.rpush(key, json.dumps(notification))
    except Exception:
        pass


def notify_task_comment_added(
    task_id: int,
    commenter_id: int,
    assignee_id: int,
) -> None:
    """Send notification when a comment is added to a task."""
    try:
        r = get_redis()
        notification = {
            "type": "task_comment_added",
            "task_id": task_id,
            "commenter_id": commenter_id,
            "assignee_id": assignee_id,
            "timestamp": __import__("datetime").datetime.now(timezone.utc).isoformat(),
        }
        key = f"notifications:user:{assignee_id}"
        r.rpush(key, json.dumps(notification))
    except Exception:
        pass