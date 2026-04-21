"""Pydantic schemas for API request / response validation."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


# ── Enums (mirror ORM enums for API layer) ───────────────────────────

class RiskAppetiteEnum(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class GoalStatusEnum(str, Enum):
    active = "active"
    achieved = "achieved"
    paused = "paused"


class ActionTypeEnum(str, Enum):
    start_sip = "start_sip"
    modify_sip = "modify_sip"
    stop_sip = "stop_sip"
    invest_lumpsum = "invest_lumpsum"
    rebalance = "rebalance"
    large_transfer = "large_transfer"
    redeem = "redeem"


class RiskLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DecisionEnum(str, Enum):
    allow = "allow"
    warn = "warn"
    block = "block"


class AssetTypeEnum(str, Enum):
    property = "property"
    gold = "gold"
    vehicle = "vehicle"
    fd = "fd"
    mutual_fund = "mutual_fund"
    stocks = "stocks"
    ppf = "ppf"
    nps = "nps"
    cash = "cash"
    other = "other"


class TransactionCategoryEnum(str, Enum):
    salary = "salary"
    freelance = "freelance"
    rent = "rent"
    groceries = "groceries"
    utilities = "utilities"
    dining = "dining"
    entertainment = "entertainment"
    shopping = "shopping"
    travel = "travel"
    healthcare = "healthcare"
    education = "education"
    emi = "emi"
    investment = "investment"
    insurance = "insurance"
    transfer = "transfer"
    other = "other"


# ── User ─────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name: str
    email: str
    age: int = 30
    occupation: str = "Salaried"
    monthly_income: float = 0.0
    risk_appetite: RiskAppetiteEnum = RiskAppetiteEnum.moderate
    kyc_verified: bool = False
    consent_given: bool = True


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Auth ─────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int = 25
    occupation: str = "Salaried"
    monthly_income: float = 50000.0
    risk_appetite: RiskAppetiteEnum = RiskAppetiteEnum.moderate
    device_id: str = ""


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str


# ── Transaction ──────────────────────────────────────────────────────

class TransactionBase(BaseModel):
    date: date
    amount: float
    category: TransactionCategoryEnum
    description: str = ""
    is_credit: bool = False


class TransactionCreate(TransactionBase):
    user_id: int


class TransactionOut(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ── Asset ────────────────────────────────────────────────────────────

class AssetBase(BaseModel):
    asset_type: AssetTypeEnum
    name: str
    current_value: float
    purchase_value: float = 0.0
    purchase_date: Optional[date] = None


class AssetCreate(AssetBase):
    user_id: int


class AssetOut(AssetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ── Goal ─────────────────────────────────────────────────────────────

class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: date
    priority: int = 1
    status: GoalStatusEnum = GoalStatusEnum.active


class GoalCreate(GoalBase):
    user_id: int


class GoalOut(GoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ── Wealth Action ────────────────────────────────────────────────────

class ActionEvaluateRequest(BaseModel):
    user_id: int
    action_type: ActionTypeEnum
    amount: float
    fund_or_product: str = ""
    description: str = ""
    # Session metadata for protection layer
    device_id: str = "default-device"
    login_timestamp: Optional[datetime] = None
    otp_attempts: int = 1


class ActionEvaluateResponse(BaseModel):
    action_id: int
    risk_score: int
    risk_level: RiskLevelEnum
    decision: DecisionEnum
    signals: dict
    message: str


class ActionConfirmRequest(BaseModel):
    action_id: int


# ── Wealth Insights ──────────────────────────────────────────────────

class SpendingSummary(BaseModel):
    total_income: float
    total_expense: float
    savings: float
    savings_rate: float
    category_breakdown: dict
    monthly_trend: list


class PortfolioSuggestion(BaseModel):
    equity_pct: float
    debt_pct: float
    gold_pct: float
    rationale: str


class SimulationRequest(BaseModel):
    user_id: int
    monthly_savings: float
    years: int = 10
    expected_return_pct: float = 12.0


class SimulationResponse(BaseModel):
    projections: list  # [{year, value}]
    final_value: float
    total_invested: float


# ── Chat ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    reasoning: str = ""


# ── Audit ────────────────────────────────────────────────────────────

class AuditLogOut(BaseModel):
    id: int
    user_id: int
    action_id: Optional[int]
    event_type: str
    risk_score: int
    risk_level: str
    decision: str
    signal_breakdown: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ── Dashboard Summary ────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    user: UserOut
    net_worth: float
    total_assets: float
    spending_summary: SpendingSummary
    goals: list
    recent_actions: list
