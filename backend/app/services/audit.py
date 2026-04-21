"""Audit service – helper utilities (most logic is inline in routers)."""

from datetime import datetime
from sqlalchemy.orm import Session

from ..models import AuditLog


def log_event(
    db: Session,
    user_id: int,
    event_type: str,
    message: str,
    action_id: int = None,
    risk_score: int = 0,
    risk_level: str = "",
    decision: str = "",
    signal_breakdown: str = "{}",
) -> AuditLog:
    """Create an audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action_id=action_id,
        event_type=event_type,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        signal_breakdown=signal_breakdown,
        message=message,
    )
    db.add(entry)
    db.commit()
    return entry
