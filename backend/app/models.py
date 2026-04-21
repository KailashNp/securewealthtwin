"""SQLAlchemy ORM models for SecureWealth Twin."""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    ForeignKey, Text, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
import enum

from .database import Base


# ── Enums ────────────────────────────────────────────────────────────

class RiskAppetite(str, enum.Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"


class ActionType(str, enum.Enum):
    START_SIP = "start_sip"
    MODIFY_SIP = "modify_sip"
    STOP_SIP = "stop_sip"
    INVEST_LUMPSUM = "invest_lumpsum"
    REBALANCE = "rebalance"
    LARGE_TRANSFER = "large_transfer"
    REDEEM = "redeem"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Decision(str, enum.Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class AssetType(str, enum.Enum):
    PROPERTY = "property"
    GOLD = "gold"
    VEHICLE = "vehicle"
    FD = "fd"
    MUTUAL_FUND = "mutual_fund"
    STOCKS = "stocks"
    PPF = "ppf"
    NPS = "nps"
    CASH = "cash"
    OTHER = "other"


class TransactionCategory(str, enum.Enum):
    SALARY = "salary"
    FREELANCE = "freelance"
    RENT = "rent"
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    DINING = "dining"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    TRAVEL = "travel"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    EMI = "emi"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    TRANSFER = "transfer"
    OTHER = "other"


# ── Models ───────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=True)  # nullable for legacy seed users
    age = Column(Integer, default=30)
    occupation = Column(String(120), default="Salaried")
    monthly_income = Column(Float, default=0.0)
    risk_appetite = Column(SAEnum(RiskAppetite), default=RiskAppetite.MODERATE)
    kyc_verified = Column(Boolean, default=False)
    trusted_devices = Column(Text, default="[]")  # JSON list of device IDs
    consent_given = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    wealth_actions = relationship("WealthAction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(SAEnum(TransactionCategory), nullable=False)
    description = Column(String(300), default="")
    is_credit = Column(Boolean, default=False)  # True = income, False = expense

    user = relationship("User", back_populates="transactions")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_type = Column(SAEnum(AssetType), nullable=False)
    name = Column(String(200), nullable=False)
    current_value = Column(Float, nullable=False)
    purchase_value = Column(Float, default=0.0)
    purchase_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="assets")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date, nullable=False)
    priority = Column(Integer, default=1)  # 1 = highest
    status = Column(SAEnum(GoalStatus), default=GoalStatus.ACTIVE)

    user = relationship("User", back_populates="goals")


class WealthAction(Base):
    __tablename__ = "wealth_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(SAEnum(ActionType), nullable=False)
    amount = Column(Float, nullable=False)
    fund_or_product = Column(String(200), default="")
    description = Column(String(500), default="")

    # Protection layer results
    risk_score = Column(Integer, default=0)
    risk_level = Column(SAEnum(RiskLevel), nullable=True)
    decision = Column(SAEnum(Decision), nullable=True)
    signal_details = Column(Text, default="{}")  # JSON
    decision_reason = Column(Text, default="")

    # Execution
    confirmed = Column(Boolean, default=False)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wealth_actions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_id = Column(Integer, ForeignKey("wealth_actions.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # e.g. "protection_check"
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="")
    decision = Column(String(20), default="")
    signal_breakdown = Column(Text, default="{}")  # JSON
    message = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)
