def simulate_growth(data):
    months = []
    values = []

    total = data.current_savings
    monthly_rate = data.annual_return / 12

    for m in range(1, 61):
        total += data.monthly_contribution
        total *= (1 + monthly_rate)

        months.append(m)
        values.append(round(total, 2))

    goal_month = next((i + 1 for i, v in enumerate(values) if v >= data.goal_amount), None)

    return {
        "months": months,
        "projected_values": values,
        "goal_reached_month": goal_month
    }