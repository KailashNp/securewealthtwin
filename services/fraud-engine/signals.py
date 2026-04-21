"""
signals.py
----------
Each function here is one fraud signal.
Each function takes the request payload and user's history,
and returns a dict: { triggered: bool, score: int, reason: str }

YOU own this file. Add / tune signals here.
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# SIGNAL 1 — New / Untrusted Device
# Score: +20
# Logic: If the device_id in this request is not in the user's
#        list of trusted devices, it is flagged.
# ─────────────────────────────────────────────────────────────────
def signal_new_device(payload: dict, history: dict) -> dict:
    device_id       = payload.get("device_id", "")
    trusted_devices = history.get("trusted_devices", [])

    triggered = device_id not in trusted_devices

    return {
        "signal":    "new_device",
        "triggered": triggered,
        "score":     20 if triggered else 0,
        "reason":    "Action from an unrecognised device" if triggered
                     else "Device is trusted",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 2 — Action Taken Too Fast After Login
# Score: +15
# Logic: If fewer than 10 seconds passed between login_timestamp
#        and action_timestamp, the session seems rushed / coerced.
# ─────────────────────────────────────────────────────────────────
def signal_fast_action(payload: dict, history: dict) -> dict:
    login_ts  = payload.get("login_timestamp")   # ISO string or None
    action_ts = payload.get("action_timestamp")  # ISO string or None

    triggered = False
    if login_ts and action_ts:
        try:
            login_dt  = datetime.fromisoformat(login_ts)
            action_dt = datetime.fromisoformat(action_ts)
            elapsed   = (action_dt - login_dt).total_seconds()
            triggered = elapsed < 10
        except ValueError:
            triggered = False

    return {
        "signal":    "fast_action",
        "triggered": triggered,
        "score":     15 if triggered else 0,
        "reason":    "Critical action taken less than 10 seconds after login"
                     if triggered else "Session timing is normal",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 3 — Amount Anomaly
# Score: +25
# Logic: If this transaction amount is more than 2.5× the user's
#        90-day average transaction amount, it is unusual.
# ─────────────────────────────────────────────────────────────────
def signal_amount_anomaly(payload: dict, history: dict) -> dict:
    amount      = float(payload.get("amount", 0))
    avg_amount  = float(history.get("avg_transaction_amount", 0))

    triggered = (avg_amount > 0) and (amount > 2.5 * avg_amount)

    return {
        "signal":    "amount_anomaly",
        "triggered": triggered,
        "score":     25 if triggered else 0,
        "reason":    f"Amount ₹{amount:,.0f} is {amount/avg_amount:.1f}× your usual average"
                     if triggered else "Amount is within normal range",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 4 — OTP Retry Pattern
# Score: +20
# Logic: If the user has attempted OTP more than 2 times in this
#        session, it could mean coercion or OTP fishing.
# ─────────────────────────────────────────────────────────────────
def signal_otp_retry(payload: dict, history: dict) -> dict:
    otp_attempts = int(payload.get("otp_attempts", 1))
    triggered    = otp_attempts > 2

    return {
        "signal":    "otp_retry",
        "triggered": triggered,
        "score":     20 if triggered else 0,
        "reason":    f"OTP entered {otp_attempts} times in this session"
                     if triggered else "OTP usage is normal",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 5 — First-Time Investment Type
# Score: +15
# Logic: If the user has never done this type of investment before
#        (e.g. starting a new SIP category, a new fund house),
#        apply moderate extra scrutiny.
# ─────────────────────────────────────────────────────────────────
def signal_first_investment(payload: dict, history: dict) -> dict:
    action_type      = payload.get("action_type", "")
    past_actions     = history.get("past_action_types", [])
    triggered        = bool(action_type) and (action_type not in past_actions)

    return {
        "signal":    "first_investment",
        "triggered": triggered,
        "score":     15 if triggered else 0,
        "reason":    f"First time performing action type: {action_type}"
                     if triggered else "Action type is familiar",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 6 — Cancel-Retry Loop
# Score: +10
# Logic: If the user cancelled and re-attempted the same action
#        3 or more times, it signals confusion or external pressure.
# ─────────────────────────────────────────────────────────────────
def signal_retry_loop(payload: dict, history: dict) -> dict:
    retry_count = int(payload.get("retry_count", 0))
    triggered   = retry_count >= 3

    return {
        "signal":    "retry_loop",
        "triggered": triggered,
        "score":     10 if triggered else 0,
        "reason":    f"Action was cancelled and retried {retry_count} times"
                     if triggered else "No unusual retry pattern",
    }


# ─────────────────────────────────────────────────────────────────
# SIGNAL 7 — Large Transaction at Night
# Score: +10
# Logic: A transaction above ₹50,000 between 11pm and 5am is
#        statistically unusual and worth flagging.
# ─────────────────────────────────────────────────────────────────
def signal_night_large_txn(payload: dict, history: dict) -> dict:
    amount     = float(payload.get("amount", 0))
    action_ts  = payload.get("action_timestamp")

    triggered = False
    if action_ts and amount > 50_000:
        try:
            hour      = datetime.fromisoformat(action_ts).hour
            triggered = hour >= 23 or hour < 5
        except ValueError:
            triggered = False

    return {
        "signal":    "night_large_txn",
        "triggered": triggered,
        "score":     10 if triggered else 0,
        "reason":    f"Large amount ₹{amount:,.0f} transacted between 11pm–5am"
                     if triggered else "Transaction time is normal",
    }


# ─────────────────────────────────────────────────────────────────
# MASTER LIST — every signal the engine evaluates
# To add a new signal: write the function above, add it here.
# ─────────────────────────────────────────────────────────────────
ALL_SIGNALS = [
    signal_new_device,
    signal_fast_action,
    signal_amount_anomaly,
    signal_otp_retry,
    signal_first_investment,
    signal_retry_loop,
    signal_night_large_txn,
]
