from fastapi import APIRouter
from app.models.schemas import UserProfile, SimulationInput
from app.services.recommendation import generate_recommendation
from app.services.explainer import generate_explanation
from app.services.simulator import simulate_growth
from app.services.market import get_market_context

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Wealth Engine Running"}


@router.post("/recommend")
def recommend(profile: UserProfile):
    return generate_recommendation(profile)


@router.post("/recommend/explain")
def explain(profile: UserProfile):
    result = generate_recommendation(profile)
    return generate_explanation(profile, result["reasons"])


@router.post("/simulate")
def simulate(data: SimulationInput):
    return simulate_growth(data)


@router.get("/market-context")
def market():
    return get_market_context()