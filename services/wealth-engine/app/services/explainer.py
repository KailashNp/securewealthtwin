def generate_explanation(profile, reasons):
    drivers = []

    if profile.savings_rate < 0.2:
        drivers.append("Low savings rate")
    if profile.tax_usage < 0.5:
        drivers.append("Low tax utilization")
    if profile.expenses_pattern == "unstable":
        drivers.append("Unstable spending pattern")

    explanation = "This recommendation is based on key financial indicators: "
    explanation += ", ".join(drivers) if drivers else "your financial profile is stable"
    explanation += "."

    return {
        "explanation_text": explanation,
        "top_drivers": drivers
    }