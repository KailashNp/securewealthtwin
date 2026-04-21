"""Generate demo financial data for newly registered users."""

import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..models import (
    Transaction, Asset, Goal,
    TransactionCategory, AssetType, GoalStatus,
)


def seed_new_user(db: Session, user_id: int, monthly_income: float) -> None:
    """
    Populate a newly registered user's account with realistic
    transactions, assets, and goals so their dashboard isn't empty.
    """
    today = date.today()

    # ── Transactions (6 months of history) ───────────────────────────
    expense_ratio = random.uniform(0.50, 0.70)
    monthly_expense = monthly_income * expense_ratio

    expense_categories = [
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

    for m in range(6):
        month_start = today.replace(day=1) - timedelta(days=30 * m)

        # Salary credit
        db.add(Transaction(
            user_id=user_id,
            date=month_start,
            amount=monthly_income + random.uniform(-1000, 1000),
            category=TransactionCategory.SALARY,
            description="Monthly Salary",
            is_credit=True,
        ))

        # Expenses
        for cat, share in expense_categories:
            amt = monthly_expense * share * random.uniform(0.7, 1.4)
            day_offset = random.randint(1, 28)
            db.add(Transaction(
                user_id=user_id,
                date=month_start + timedelta(days=day_offset),
                amount=round(amt, 2),
                category=cat,
                description=f"{cat.value.title()} expense",
                is_credit=False,
            ))

        # Occasional investment
        if random.random() > 0.4:
            db.add(Transaction(
                user_id=user_id,
                date=month_start + timedelta(days=random.randint(5, 25)),
                amount=round(random.uniform(2000, 10000), 2),
                category=TransactionCategory.INVESTMENT,
                description="SIP / Investment",
                is_credit=False,
            ))

    # ── Assets (scaled to income) ────────────────────────────────────
    base = monthly_income * 2
    assets_data = [
        (AssetType.MUTUAL_FUND, "Index Fund SIP", base * 1.2, base, 200),
        (AssetType.FD, "Fixed Deposit", base * 2, base * 2, 365),
        (AssetType.CASH, "Savings Account", base * 0.8, base * 0.8, 30),
    ]
    # Higher income → more diverse portfolio
    if monthly_income >= 80000:
        assets_data.append(
            (AssetType.STOCKS, "Equity Portfolio", base * 1.5, base * 1.2, 300)
        )
    if monthly_income >= 100000:
        assets_data.append(
            (AssetType.GOLD, "Gold ETF", base * 0.6, base * 0.5, 400)
        )

    for atype, name, current, purchase, days_ago in assets_data:
        db.add(Asset(
            user_id=user_id,
            asset_type=atype,
            name=name,
            current_value=round(current + random.uniform(-1000, 3000), 2),
            purchase_value=round(purchase, 2),
            purchase_date=today - timedelta(days=days_ago),
        ))

    # ── Goals ────────────────────────────────────────────────────────
    db.add(Goal(
        user_id=user_id,
        name="Emergency Fund",
        target_amount=monthly_income * 6,
        current_amount=round(monthly_income * random.uniform(1, 3), 2),
        deadline=today + timedelta(days=365),
        priority=1,
        status=GoalStatus.ACTIVE,
    ))
    db.add(Goal(
        user_id=user_id,
        name="Retirement Corpus",
        target_amount=monthly_income * 200,
        current_amount=round(monthly_income * random.uniform(5, 20), 2),
        deadline=today + timedelta(days=365 * 25),
        priority=2,
        status=GoalStatus.ACTIVE,
    ))

    db.commit()
