"""Chat advisor endpoint – GenAI or rule-based fallback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Transaction, Asset, Goal
from ..schemas import ChatRequest, ChatResponse
from ..services.chat_advisor import get_chat_response
from ..services.wealth_intel import compute_spending_summary

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    txns = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    assets = db.query(Asset).filter(Asset.user_id == user.id).all()
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()

    spending = compute_spending_summary(txns)

    context = {
        "name": user.name,
        "age": user.age,
        "occupation": user.occupation,
        "monthly_income": user.monthly_income,
        "risk_appetite": user.risk_appetite.value,
        "total_assets": sum(a.current_value for a in assets),
        "savings_rate": spending.savings_rate,
        "total_savings": spending.savings,
        "goals": [{"name": g.name, "target": g.target_amount, "current": g.current_amount} for g in goals],
    }

    return get_chat_response(payload.message, context)
