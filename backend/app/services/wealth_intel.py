"""Wealth intelligence service – spending analysis, portfolio, tax tips, alerts."""

from collections import defaultdict
from datetime import date, timedelta

from ..models import Transaction, User, Asset, AssetType, RiskAppetite
from ..schemas import SpendingSummary, PortfolioSuggestion


def compute_spending_summary(transactions: list) -> SpendingSummary:
    """Analyse a user's transactions and return an insight summary."""

    total_income = sum(t.amount for t in transactions if t.is_credit)
    total_expense = sum(t.amount for t in transactions if not t.is_credit)
    savings = total_income - total_expense
    savings_rate = round((savings / total_income * 100) if total_income else 0, 1)

    # Category breakdown (expenses only)
    cat_map: dict[str, float] = defaultdict(float)
    for t in transactions:
        if not t.is_credit:
            cat_map[t.category.value] += t.amount

    # Monthly trend
    monthly: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        key = t.date.strftime("%Y-%m")
        if t.is_credit:
            monthly[key]["income"] += t.amount
        else:
            monthly[key]["expense"] += t.amount

    monthly_trend = [
        {"month": k, "income": round(v["income"], 2), "expense": round(v["expense"], 2)}
        for k, v in sorted(monthly.items())
    ]

    return SpendingSummary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        savings=round(savings, 2),
        savings_rate=savings_rate,
        category_breakdown={k: round(v, 2) for k, v in cat_map.items()},
        monthly_trend=monthly_trend,
    )


def suggest_portfolio(user) -> PortfolioSuggestion:
    """Rule-based asset allocation by risk appetite and age."""

    age = user.age if user else 30
    appetite = user.risk_appetite if user else RiskAppetite.MODERATE

    if appetite == RiskAppetite.AGGRESSIVE:
        equity = min(80, 100 - age)
        debt = max(10, age - 10)
        gold = 100 - equity - debt
    elif appetite == RiskAppetite.CONSERVATIVE:
        equity = max(20, 50 - age // 2)
        debt = min(60, 40 + age // 2)
        gold = 100 - equity - debt
    else:  # moderate
        equity = max(30, 70 - age // 2)
        debt = min(50, 20 + age // 2)
        gold = 100 - equity - debt

    rationale_parts = [
        f"Based on your age ({age}) and {appetite.value} risk appetite:",
        f"  • {equity}% in Equity (index funds, diversified MFs)",
        f"  • {debt}% in Debt (FDs, debt funds, PPF)",
        f"  • {gold}% in Gold (Sovereign Gold Bonds, Gold ETF)",
    ]

    return PortfolioSuggestion(
        equity_pct=equity,
        debt_pct=debt,
        gold_pct=gold,
        rationale="\n".join(rationale_parts),
    )


def get_tax_saving_tips(user, assets: list) -> dict:
    """Suggest tax-saving instruments based on existing assets."""
    existing_types = {a.asset_type for a in assets}
    tips = []

    if AssetType.PPF not in existing_types:
        tips.append({
            "instrument": "PPF",
            "section": "80C",
            "limit": "₹1,50,000/year",
            "tip": "Open a PPF account for safe, tax-free returns over 15 years.",
        })
    if AssetType.NPS not in existing_types:
        tips.append({
            "instrument": "NPS",
            "section": "80CCD(1B)",
            "limit": "₹50,000 additional",
            "tip": "NPS gives you an extra ₹50,000 deduction beyond 80C.",
        })
    if AssetType.MUTUAL_FUND not in existing_types:
        tips.append({
            "instrument": "ELSS Mutual Fund",
            "section": "80C",
            "limit": "₹1,50,000/year",
            "tip": "ELSS has the shortest lock-in (3 years) among 80C options.",
        })

    tips.append({
        "instrument": "Health Insurance",
        "section": "80D",
        "limit": "₹25,000-₹50,000",
        "tip": "Premiums for self and family are deductible under 80D.",
    })

    return {"user_id": user.id, "tips": tips}


def get_overspending_alerts(transactions: list) -> dict:
    """Flag months where spending exceeds 1.5× average."""
    monthly_expense: dict[str, float] = defaultdict(float)
    for t in transactions:
        if not t.is_credit:
            key = t.date.strftime("%Y-%m")
            monthly_expense[key] += t.amount

    if not monthly_expense:
        return {"alerts": []}

    avg = sum(monthly_expense.values()) / len(monthly_expense)
    threshold = avg * 1.5

    alerts = []
    for month, total in sorted(monthly_expense.items()):
        if total > threshold:
            alerts.append({
                "month": month,
                "spent": round(total, 2),
                "average": round(avg, 2),
                "overspend_pct": round((total - avg) / avg * 100, 1),
                "message": f"You spent ₹{total:,.0f} in {month}, which is {((total-avg)/avg)*100:.0f}% above your average.",
            })

    return {"alerts": alerts}
