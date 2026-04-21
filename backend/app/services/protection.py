"""7-signal cyber-protection risk scoring engine."""

import json
from datetime import datetime, timedelta

from ..models import User, WealthAction


def evaluate_risk(
    user,
    action,
    transactions: list,
    past_actions: list,
) -> dict:
    """
    Evaluate a proposed wealth action against 7 cyber-risk signals.

    Returns: {score, level, decision, signals, message}
    """

    signals = {}
    score = 0

    # ── Signal 1: Device Trust Check (+20) ───────────────────────────
    trusted_devices = json.loads(user.trusted_devices) if user.trusted_devices else []
    device_trusted = action.device_id in trusted_devices
    if not device_trusted:
        score += 20
        signals["device_trust"] = {
            "points": 20,
            "detail": f"New/untrusted device: {action.device_id}",
            "triggered": True,
        }
    else:
        signals["device_trust"] = {
            "points": 0,
            "detail": "Trusted device",
            "triggered": False,
        }

    # ── Signal 2: Login-to-Action Speed (+15) ────────────────────────
    if action.login_timestamp:
        elapsed = (datetime.utcnow() - action.login_timestamp).total_seconds()
        if elapsed < 10:
            score += 15
            signals["login_speed"] = {
                "points": 15,
                "detail": f"Action taken {elapsed:.1f}s after login (< 10s threshold)",
                "triggered": True,
            }
        else:
            signals["login_speed"] = {
                "points": 0,
                "detail": f"Normal speed: {elapsed:.1f}s after login",
                "triggered": False,
            }
    else:
        signals["login_speed"] = {"points": 0, "detail": "Login time not provided", "triggered": False}

    # ── Signal 3: Amount vs History (+20) ────────────────────────────
    expense_amounts = [t.amount for t in transactions if not t.is_credit and t.amount > 0]
    if expense_amounts:
        avg_amount = sum(expense_amounts) / len(expense_amounts)
        ratio = action.amount / avg_amount if avg_amount > 0 else 0
        if ratio > 2.5:
            score += 20
            signals["amount_history"] = {
                "points": 20,
                "detail": f"Amount ₹{action.amount:,.0f} is {ratio:.1f}× your average (₹{avg_amount:,.0f})",
                "triggered": True,
            }
        else:
            signals["amount_history"] = {
                "points": 0,
                "detail": f"Amount within normal range ({ratio:.1f}× average)",
                "triggered": False,
            }
    else:
        signals["amount_history"] = {"points": 0, "detail": "No history to compare", "triggered": False}

    # ── Signal 4: OTP Usage Pattern (+15) ────────────────────────────
    if action.otp_attempts > 2:
        score += 15
        signals["otp_pattern"] = {
            "points": 15,
            "detail": f"Multiple OTP attempts ({action.otp_attempts})",
            "triggered": True,
        }
    elif action.otp_attempts > 1 and action.amount > 50000:
        score += 10
        signals["otp_pattern"] = {
            "points": 10,
            "detail": f"OTP retry on high-value action (₹{action.amount:,.0f})",
            "triggered": True,
        }
    else:
        signals["otp_pattern"] = {
            "points": 0,
            "detail": "Normal OTP usage",
            "triggered": False,
        }

    # ── Signal 5: New Action / Investment Type (+10) ─────────────────
    past_types = {a.action_type.value if hasattr(a.action_type, 'value') else a.action_type for a in past_actions}
    action_type_val = action.action_type.value if hasattr(action.action_type, 'value') else action.action_type
    if action_type_val not in past_types:
        score += 10
        signals["new_action_type"] = {
            "points": 10,
            "detail": f"First-time action type: {action_type_val}",
            "triggered": True,
        }
    else:
        signals["new_action_type"] = {
            "points": 0,
            "detail": "Familiar action type",
            "triggered": False,
        }

    # ── Signal 6: Behaviour Consistency (+10) ────────────────────────
    # Simulate: check if user had multiple actions in last 5 minutes
    recent_count = sum(
        1 for a in past_actions
        if a.created_at and (datetime.utcnow() - a.created_at).total_seconds() < 300
    )
    if recent_count >= 3:
        score += 10
        signals["behaviour_consistency"] = {
            "points": 10,
            "detail": f"{recent_count} actions in last 5 minutes – unusual pattern",
            "triggered": True,
        }
    else:
        signals["behaviour_consistency"] = {
            "points": 0,
            "detail": "Normal behaviour pattern",
            "triggered": False,
        }

    # ── Signal 7: Aggregate Score → Decision ─────────────────────────
    if score <= 25:
        level = "low"
        decision = "allow"
        message = "✔ Action approved. No significant risks detected."
    elif score <= 55:
        level = "medium"
        decision = "warn"
        triggered = [k for k, v in signals.items() if v["triggered"]]
        message = (
            f"⚠ Moderate risk detected (score: {score}). "
            f"Flagged signals: {', '.join(triggered)}. "
            "A 30-second cooling-off period is recommended before proceeding."
        )
    else:
        level = "high"
        decision = "block"
        triggered = [k for k, v in signals.items() if v["triggered"]]
        message = (
            f"✖ High risk detected (score: {score}). "
            f"Flagged signals: {', '.join(triggered)}. "
            "This action has been temporarily blocked for your safety. "
            "Please contact your bank or retry from a trusted device."
        )

    return {
        "score": score,
        "level": level,
        "decision": decision,
        "signals": signals,
        "message": message,
    }
