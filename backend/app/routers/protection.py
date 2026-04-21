"""Protection layer endpoints – evaluate and confirm wealth actions."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Transaction, WealthAction, AuditLog, RiskLevel, Decision
from ..schemas import ActionEvaluateRequest, ActionEvaluateResponse, ActionConfirmRequest
from ..services.protection import evaluate_risk

router = APIRouter(prefix="/actions", tags=["protection"])


@router.post("/evaluate", response_model=ActionEvaluateResponse)
def evaluate_action(payload: ActionEvaluateRequest, db: Session = Depends(get_db)):
    """Run the 7-signal cyber-protection check on a proposed wealth action."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    txns = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    past_actions = db.query(WealthAction).filter(WealthAction.user_id == user.id).all()

    result = evaluate_risk(
        user=user,
        action=payload,
        transactions=txns,
        past_actions=past_actions,
    )

    # Persist the action
    action = WealthAction(
        user_id=user.id,
        action_type=payload.action_type.value,
        amount=payload.amount,
        fund_or_product=payload.fund_or_product,
        description=payload.description,
        risk_score=result["score"],
        risk_level=result["level"],
        decision=result["decision"],
        signal_details=json.dumps(result["signals"]),
        decision_reason=result["message"],
    )
    db.add(action)
    db.flush()

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action_id=action.id,
        event_type="protection_check",
        risk_score=result["score"],
        risk_level=result["level"],
        decision=result["decision"],
        signal_breakdown=json.dumps(result["signals"]),
        message=result["message"],
    )
    db.add(audit)
    db.commit()

    return ActionEvaluateResponse(
        action_id=action.id,
        risk_score=result["score"],
        risk_level=result["level"],
        decision=result["decision"],
        signals=result["signals"],
        message=result["message"],
    )


@router.post("/confirm")
def confirm_action(payload: ActionConfirmRequest, db: Session = Depends(get_db)):
    """Confirm a warned action after the cooling-off period."""
    action = db.query(WealthAction).filter(WealthAction.id == payload.action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action.decision == Decision.BLOCK:
        raise HTTPException(status_code=403, detail="This action was blocked and cannot be confirmed")
    action.confirmed = True
    action.executed = True

    audit = AuditLog(
        user_id=action.user_id,
        action_id=action.id,
        event_type="action_confirmed",
        risk_score=action.risk_score,
        risk_level=action.risk_level.value if action.risk_level else "",
        decision="confirmed",
        message="User confirmed the action after review.",
    )
    db.add(audit)
    db.commit()
    return {"status": "confirmed", "action_id": action.id}
