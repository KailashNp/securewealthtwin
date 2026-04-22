from pydantic import BaseModel

class UserProfile(BaseModel):
    income: float
    savings_rate: float
    expenses_pattern: str
    tax_usage: float


class SimulationInput(BaseModel):
    current_savings: float
    monthly_contribution: float
    goal_amount: float
    annual_return: float