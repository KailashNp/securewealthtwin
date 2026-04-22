from app.services.market import get_market_context

def generate_recommendation(profile):
    reasons = []
    score = 0

    # Savings check
    if profile.savings_rate < 0.2:
        reasons.append("your savings rate is below the recommended 20%")
        score += 1

    # Tax optimization
    if profile.tax_usage < 0.5:
        reasons.append("you are not fully utilizing tax-saving options (Section 80C)")
        score += 1

    # Expense behavior
    if profile.expenses_pattern == "unstable":
        reasons.append("your expenses are inconsistent month-to-month")
        score += 1

    market = get_market_context()

    # Decision logic
    if score == 0:
        recommendation = "Your financial health is stable. Continue your current investment strategy."
    elif score == 1:
        recommendation = "Consider optimizing your savings and monitoring your expenses."
    elif score == 2:
        recommendation = "Start a SIP of ₹5000 in a diversified mutual fund to improve long-term growth."
    else:
        recommendation = "Urgently improve savings discipline and start a SIP to stabilize your financial future."

    # Add market context
    if market["inflation_alert"]:
        recommendation += " Also, due to high inflation, consider allocating some funds to fixed deposits or gold."

    return {
        "recommendation": recommendation,
        "confidence": round(score / 3, 2),
        "reasons": reasons
    }