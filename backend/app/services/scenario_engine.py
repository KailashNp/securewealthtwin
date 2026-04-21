"""Scenario simulation engine – Monte-Carlo-lite wealth projections."""

from ..schemas import SimulationResponse


def run_simulation(
    monthly_savings: float,
    years: int = 10,
    expected_return_pct: float = 12.0,
) -> SimulationResponse:
    """
    Project future wealth using compound interest formula.

    Uses monthly compounding:
        FV = P × [((1+r)^n - 1) / r] × (1+r)
    where P = monthly investment, r = monthly rate, n = total months.
    """

    monthly_rate = expected_return_pct / 100 / 12
    projections = []
    total_invested = 0.0

    for year in range(1, years + 1):
        months = year * 12
        total_invested = monthly_savings * months

        if monthly_rate > 0:
            fv = monthly_savings * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            fv = total_invested

        projections.append({
            "year": year,
            "invested": round(total_invested, 2),
            "projected_value": round(fv, 2),
            "gains": round(fv - total_invested, 2),
        })

    final = projections[-1] if projections else {"projected_value": 0, "invested": 0}

    return SimulationResponse(
        projections=projections,
        final_value=final["projected_value"],
        total_invested=final["invested"],
    )
