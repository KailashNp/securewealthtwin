"""
risk_scorer.py
--------------
Runs every signal against the incoming request and produces:
  - A numeric risk score  (0 – 100)
  - A risk level          (LOW / MEDIUM / HIGH)
  - A decision            (ALLOW / WARN / BLOCK)
  - The list of triggered signals with reasons

YOU own this file.
Tune THRESHOLDS here if the judges think the engine is too strict
or too lenient during the demo.
"""

from signals import ALL_SIGNALS


# ─────────────────────────────────────────────────────────────────
# Decision thresholds  ← tune these before the demo
# ─────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "LOW":    (0,  30),   # score 0–30   → ALLOW
    "MEDIUM": (31, 55),   # score 31–55  → WARN  (30-second cooling-off)
    "HIGH":   (56, 100),  # score 56–100 → BLOCK
}

DECISION_MAP = {
    "LOW":    "ALLOW",
    "MEDIUM": "WARN",
    "HIGH":   "BLOCK",
}

USER_MESSAGES = {
    "ALLOW":  "Your action has been approved. Proceeding safely.",
    "WARN":   "We noticed some unusual patterns with this action. "
              "Please review the details below and confirm after the "
              "30-second security pause.",
    "BLOCK":  "This action has been blocked for your protection. "
              "If this was you, please call our helpline: 1800-XXX-XXXX "
              "or visit your nearest branch with a valid ID.",
}


def compute_risk_score(payload: dict, history: dict) -> dict:
    """
    Run every signal function and aggregate the results.

    Parameters
    ----------
    payload : dict
        The incoming action request from the API.
        Contains fields like amount, device_id, timestamps, etc.

    history : dict
        The user's stored behavioural baseline.
        Contains fields like avg_transaction_amount, trusted_devices, etc.

    Returns
    -------
    dict with keys:
        risk_score        : int  (0-100, capped)
        risk_level        : str  (LOW / MEDIUM / HIGH)
        decision          : str  (ALLOW / WARN / BLOCK)
        triggered_signals : list of dicts (only the signals that fired)
        all_signals       : list of dicts (all signals evaluated)
        message           : str  (user-facing explanation)
    """
    all_results      = []
    triggered        = []
    total_score      = 0

    for signal_fn in ALL_SIGNALS:
        result = signal_fn(payload, history)
        all_results.append(result)
        if result["triggered"]:
            triggered.append(result)
            total_score += result["score"]

    # Cap at 100
    total_score = min(total_score, 100)

    # Determine risk level
    if total_score <= THRESHOLDS["LOW"][1]:
        risk_level = "LOW"
    elif total_score <= THRESHOLDS["MEDIUM"][1]:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    decision = DECISION_MAP[risk_level]
    message  = USER_MESSAGES[decision]

    return {
        "risk_score":        total_score,
        "risk_level":        risk_level,
        "decision":          decision,
        "triggered_signals": triggered,
        "all_signals":       all_results,
        "message":           message,
    }
