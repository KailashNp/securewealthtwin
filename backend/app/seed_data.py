"""Synthetic seed data generator – creates realistic demo personas."""

import json
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session

from .models import (
    User, Transaction, Asset, Goal,
    RiskAppetite, GoalStatus, TransactionCategory, AssetType,
)
from .services.auth import hash_password

# All demo users share this password for easy hackathon testing
_DEMO_PASSWORD = hash_password("demo1234")


def seed_database(db: Session) -> None:
    """Populate the database with demo personas and their financial data."""

    # Skip if data already exists
    if db.query(User).count() > 0:
        return

    personas = _build_personas()
    for persona in personas:
        user = User(**persona["user"])
        db.add(user)
        db.flush()  # get user.id

        for txn_data in persona["transactions"]:
            txn_data["user_id"] = user.id
            db.add(Transaction(**txn_data))

        for asset_data in persona["assets"]:
            asset_data["user_id"] = user.id
            db.add(Asset(**asset_data))

        for goal_data in persona["goals"]:
            goal_data["user_id"] = user.id
            db.add(Goal(**goal_data))

    db.commit()


def _build_personas() -> list[dict]:
    """Return a list of 4 demo personas with transactions, assets, and goals."""
    today = date.today()

    return [
        # ── Persona 1: Young Professional ────────────────────────────
        {
            "user": {
                "name": "Arjun Mehta",
                "email": "arjun.mehta@demo.com",
                "hashed_password": _DEMO_PASSWORD,
                "age": 26,
                "occupation": "Software Engineer",
                "monthly_income": 85000.0,
                "risk_appetite": RiskAppetite.AGGRESSIVE,
                "kyc_verified": True,
                "trusted_devices": json.dumps(["device-arjun-phone"]),
                "consent_given": True,
            },
            "transactions": _generate_transactions(
                months=10,
                monthly_income=85000,
                expense_ratio=0.55,
                today=today,
            ),
            "assets": [
                {"asset_type": AssetType.MUTUAL_FUND, "name": "Nifty 50 Index Fund",
                 "current_value": 180000, "purchase_value": 150000,
                 "purchase_date": today - timedelta(days=365)},
                {"asset_type": AssetType.STOCKS, "name": "Infosys + TCS",
                 "current_value": 95000, "purchase_value": 80000,
                 "purchase_date": today - timedelta(days=200)},
                {"asset_type": AssetType.PPF, "name": "PPF Account",
                 "current_value": 60000, "purchase_value": 60000,
                 "purchase_date": today - timedelta(days=300)},
            ],
            "goals": [
                {"name": "Emergency Fund", "target_amount": 500000,
                 "current_amount": 180000,
                 "deadline": today + timedelta(days=365), "priority": 1,
                 "status": GoalStatus.ACTIVE},
                {"name": "Europe Trip", "target_amount": 300000,
                 "current_amount": 45000,
                 "deadline": today + timedelta(days=540), "priority": 2,
                 "status": GoalStatus.ACTIVE},
            ],
        },

        # ── Persona 2: Mid-Career Family Person ─────────────────────
        {
            "user": {
                "name": "Priya Sharma",
                "email": "priya.sharma@demo.com",
                "hashed_password": _DEMO_PASSWORD,
                "age": 35,
                "occupation": "Marketing Manager",
                "monthly_income": 120000.0,
                "risk_appetite": RiskAppetite.MODERATE,
                "kyc_verified": True,
                "trusted_devices": json.dumps(["device-priya-phone", "device-priya-laptop"]),
                "consent_given": True,
            },
            "transactions": _generate_transactions(
                months=12,
                monthly_income=120000,
                expense_ratio=0.65,
                today=today,
            ),
            "assets": [
                {"asset_type": AssetType.PROPERTY, "name": "2BHK Apartment (EMI running)",
                 "current_value": 4500000, "purchase_value": 3800000,
                 "purchase_date": today - timedelta(days=1095)},
                {"asset_type": AssetType.MUTUAL_FUND, "name": "HDFC Balanced Advantage",
                 "current_value": 350000, "purchase_value": 300000,
                 "purchase_date": today - timedelta(days=730)},
                {"asset_type": AssetType.GOLD, "name": "Gold ETF",
                 "current_value": 200000, "purchase_value": 160000,
                 "purchase_date": today - timedelta(days=500)},
                {"asset_type": AssetType.FD, "name": "SBI FD",
                 "current_value": 500000, "purchase_value": 500000,
                 "purchase_date": today - timedelta(days=180)},
                {"asset_type": AssetType.NPS, "name": "NPS Tier 1",
                 "current_value": 280000, "purchase_value": 250000,
                 "purchase_date": today - timedelta(days=900)},
            ],
            "goals": [
                {"name": "Child Education Fund", "target_amount": 2500000,
                 "current_amount": 350000,
                 "deadline": today + timedelta(days=3650), "priority": 1,
                 "status": GoalStatus.ACTIVE},
                {"name": "Home Loan Prepayment", "target_amount": 1000000,
                 "current_amount": 200000,
                 "deadline": today + timedelta(days=1095), "priority": 2,
                 "status": GoalStatus.ACTIVE},
                {"name": "Retirement Corpus", "target_amount": 20000000,
                 "current_amount": 830000,
                 "deadline": today + timedelta(days=9125), "priority": 3,
                 "status": GoalStatus.ACTIVE},
            ],
        },

        # ── Persona 3: Conservative Senior ──────────────────────────
        {
            "user": {
                "name": "Ramesh Gupta",
                "email": "ramesh.gupta@demo.com",
                "hashed_password": _DEMO_PASSWORD,
                "age": 55,
                "occupation": "Government Employee",
                "monthly_income": 95000.0,
                "risk_appetite": RiskAppetite.CONSERVATIVE,
                "kyc_verified": True,
                "trusted_devices": json.dumps(["device-ramesh-phone"]),
                "consent_given": True,
            },
            "transactions": _generate_transactions(
                months=12,
                monthly_income=95000,
                expense_ratio=0.50,
                today=today,
            ),
            "assets": [
                {"asset_type": AssetType.PROPERTY, "name": "House (Owned)",
                 "current_value": 7500000, "purchase_value": 3500000,
                 "purchase_date": today - timedelta(days=7300)},
                {"asset_type": AssetType.FD, "name": "Multiple FDs",
                 "current_value": 1800000, "purchase_value": 1500000,
                 "purchase_date": today - timedelta(days=1825)},
                {"asset_type": AssetType.GOLD, "name": "Physical Gold",
                 "current_value": 800000, "purchase_value": 400000,
                 "purchase_date": today - timedelta(days=3650)},
                {"asset_type": AssetType.PPF, "name": "PPF (Mature)",
                 "current_value": 2200000, "purchase_value": 1500000,
                 "purchase_date": today - timedelta(days=5475)},
            ],
            "goals": [
                {"name": "Retirement Corpus", "target_amount": 15000000,
                 "current_amount": 12300000,
                 "deadline": today + timedelta(days=1825), "priority": 1,
                 "status": GoalStatus.ACTIVE},
                {"name": "Daughter's Wedding", "target_amount": 2000000,
                 "current_amount": 800000,
                 "deadline": today + timedelta(days=730), "priority": 2,
                 "status": GoalStatus.ACTIVE},
            ],
        },

        # ── Persona 4: First-time Investor (Student / Early Career) ─
        {
            "user": {
                "name": "Sneha Patel",
                "email": "sneha.patel@demo.com",
                "hashed_password": _DEMO_PASSWORD,
                "age": 22,
                "occupation": "Junior Analyst",
                "monthly_income": 40000.0,
                "risk_appetite": RiskAppetite.MODERATE,
                "kyc_verified": False,
                "trusted_devices": json.dumps(["device-sneha-phone"]),
                "consent_given": True,
            },
            "transactions": _generate_transactions(
                months=6,
                monthly_income=40000,
                expense_ratio=0.70,
                today=today,
            ),
            "assets": [
                {"asset_type": AssetType.CASH, "name": "Savings Account",
                 "current_value": 65000, "purchase_value": 65000,
                 "purchase_date": today - timedelta(days=90)},
            ],
            "goals": [
                {"name": "Emergency Fund", "target_amount": 200000,
                 "current_amount": 30000,
                 "deadline": today + timedelta(days=365), "priority": 1,
                 "status": GoalStatus.ACTIVE},
                {"name": "Laptop Upgrade", "target_amount": 80000,
                 "current_amount": 15000,
                 "deadline": today + timedelta(days=180), "priority": 2,
                 "status": GoalStatus.ACTIVE},
            ],
        },
    ]


# ── Helpers ──────────────────────────────────────────────────────────

_EXPENSE_CATEGORIES = [
    (TransactionCategory.RENT, 0.25),
    (TransactionCategory.GROCERIES, 0.12),
    (TransactionCategory.UTILITIES, 0.05),
    (TransactionCategory.DINING, 0.08),
    (TransactionCategory.ENTERTAINMENT, 0.06),
    (TransactionCategory.SHOPPING, 0.10),
    (TransactionCategory.TRAVEL, 0.05),
    (TransactionCategory.HEALTHCARE, 0.04),
    (TransactionCategory.EMI, 0.15),
    (TransactionCategory.INSURANCE, 0.03),
    (TransactionCategory.OTHER, 0.07),
]


def _generate_transactions(
    months: int,
    monthly_income: float,
    expense_ratio: float,
    today: date,
) -> list[dict]:
    """Generate realistic monthly transactions for a persona."""
    txns: list[dict] = []
    monthly_expense = monthly_income * expense_ratio

    for m in range(months):
        month_start = today.replace(day=1) - timedelta(days=30 * m)

        # Salary credit on 1st of each month
        txns.append({
            "date": month_start,
            "amount": monthly_income + random.uniform(-2000, 2000),
            "category": TransactionCategory.SALARY,
            "description": "Monthly Salary",
            "is_credit": True,
        })

        # Expenses spread across the month
        for cat, share in _EXPENSE_CATEGORIES:
            amt = monthly_expense * share * random.uniform(0.7, 1.4)
            day_offset = random.randint(1, 28)
            txns.append({
                "date": month_start + timedelta(days=day_offset),
                "amount": round(amt, 2),
                "category": cat,
                "description": f"{cat.value.title()} expense",
                "is_credit": False,
            })

        # Occasional investment debit
        if random.random() > 0.4:
            txns.append({
                "date": month_start + timedelta(days=random.randint(5, 25)),
                "amount": round(random.uniform(3000, 15000), 2),
                "category": TransactionCategory.INVESTMENT,
                "description": "SIP / Investment",
                "is_credit": False,
            })

    return txns
