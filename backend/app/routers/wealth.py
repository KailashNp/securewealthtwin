"""Wealth intelligence endpoints – insights, simulation, portfolio suggestions."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Transaction, Asset, Goal
from ..schemas import (
    SpendingSummary, PortfolioSuggestion,
    SimulationRequest, SimulationResponse, DashboardSummary, UserOut,
)
from ..services.wealth_intel import (
    compute_spending_summary,
    suggest_portfolio,
    get_tax_saving_tips,
    get_overspending_alerts,
)
from ..services.scenario_engine import run_simulation

router = APIRouter(prefix="/wealth", tags=["wealth"])


@router.get("/insights", response_model=SpendingSummary)
def get_insights(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Spending analysis, income tracking, category breakdown."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return compute_spending_summary(txns)


@router.get("/portfolio-suggestion", response_model=PortfolioSuggestion)
def get_portfolio(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return suggest_portfolio(user)


@router.post("/simulation", response_model=SimulationResponse)
def simulate(payload: SimulationRequest, db: Session = Depends(get_db)):
    return run_simulation(
        monthly_savings=payload.monthly_savings,
        years=payload.years,
        expected_return_pct=payload.expected_return_pct,
    )


@router.get("/tax-tips")
def tax_tips(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    return get_tax_saving_tips(user, assets)


@router.get("/alerts")
def alerts(user_id: int = Query(...), db: Session = Depends(get_db)):
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return get_overspending_alerts(txns)


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Full dashboard data in a single call."""
    user = db.query(User).filter(User.id == user_id).first()
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()

    total_assets = sum(a.current_value for a in assets)
    spending = compute_spending_summary(txns)
    net_worth = total_assets + spending.savings

    from ..schemas import GoalOut
    from ..models import WealthAction

    recent_actions = (
        db.query(WealthAction)
        .filter(WealthAction.user_id == user_id)
        .order_by(WealthAction.created_at.desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        user=UserOut.model_validate(user),
        net_worth=net_worth,
        total_assets=total_assets,
        spending_summary=spending,
        goals=[GoalOut.model_validate(g) for g in goals],
        recent_actions=[
            {
                "id": a.id, "type": a.action_type.value,
                "amount": a.amount, "decision": a.decision.value if a.decision else None,
                "risk_score": a.risk_score,
            }
            for a in recent_actions
        ],
    )
