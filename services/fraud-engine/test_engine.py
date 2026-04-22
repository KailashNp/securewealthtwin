"""
test_engine.py
--------------
Run this before pushing to GitHub to confirm everything works.
It tests every signal individually and then runs 4 full scenarios.

Usage:
  python test_engine.py

Expected: all tests print PASS. No errors.
"""

from signals     import (signal_new_device, signal_fast_action,
                          signal_amount_anomaly, signal_otp_retry,
                          signal_first_investment, signal_retry_loop,
                          signal_night_large_txn)
from risk_scorer import compute_risk_score
from user_store  import get_user_history


PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(label: str, condition: bool):
    status = PASS if condition else FAIL
    print(f"  [{status}]  {label}")
    if not condition:
        raise SystemExit(f"\n  Test failed: {label}")


print("\n══════════════════════════════════════════")
print("  SecureWealth Twin — Fraud Engine Tests  ")
print("══════════════════════════════════════════\n")


# ── Individual Signal Tests ────────────────────────────────────────

print("── Signal 1: New Device ──")
r = signal_new_device(
    {"device_id": "unknown_device"},
    {"trusted_devices": ["known_device"]}
)
check("fires on unknown device",   r["triggered"] is True)
check("score is 20",               r["score"] == 20)

r = signal_new_device(
    {"device_id": "known_device"},
    {"trusted_devices": ["known_device"]}
)
check("does NOT fire on known device", r["triggered"] is False)
check("score is 0",                    r["score"] == 0)

print()
print("── Signal 2: Fast Action ──")
r = signal_fast_action(
    {"login_timestamp":  "2026-04-20T22:55:00",
     "action_timestamp": "2026-04-20T22:55:05"},   # 5 seconds
    {}
)
check("fires when < 10 seconds",  r["triggered"] is True)
check("score is 15",              r["score"] == 15)

r = signal_fast_action(
    {"login_timestamp":  "2026-04-20T22:55:00",
     "action_timestamp": "2026-04-20T22:56:30"},   # 90 seconds
    {}
)
check("does NOT fire when > 10 seconds", r["triggered"] is False)

print()
print("── Signal 3: Amount Anomaly ──")
r = signal_amount_anomaly(
    {"amount": 90_000},
    {"avg_transaction_amount": 12_000}   # 7.5× average
)
check("fires when amount > 2.5× average", r["triggered"] is True)
check("score is 25",                      r["score"] == 25)

r = signal_amount_anomaly(
    {"amount": 15_000},
    {"avg_transaction_amount": 12_000}   # 1.25× average
)
check("does NOT fire when amount is normal", r["triggered"] is False)

print()
print("── Signal 4: OTP Retry ──")
r = signal_otp_retry({"otp_attempts": 3}, {})
check("fires when otp_attempts > 2", r["triggered"] is True)

r = signal_otp_retry({"otp_attempts": 1}, {})
check("does NOT fire on single OTP", r["triggered"] is False)

print()
print("── Signal 5: First Investment ──")
r = signal_first_investment(
    {"action_type": "start_sip"},
    {"past_action_types": ["view_portfolio"]}
)
check("fires on new action type", r["triggered"] is True)

r = signal_first_investment(
    {"action_type": "start_sip"},
    {"past_action_types": ["start_sip", "renew_fd"]}
)
check("does NOT fire on familiar action type", r["triggered"] is False)

print()
print("── Signal 6: Retry Loop ──")
r = signal_retry_loop({"retry_count": 3}, {})
check("fires when retry_count >= 3", r["triggered"] is True)

r = signal_retry_loop({"retry_count": 1}, {})
check("does NOT fire when retry_count < 3", r["triggered"] is False)

print()
print("── Signal 7: Night Large Transaction ──")
r = signal_night_large_txn(
    {"amount": 75_000, "action_timestamp": "2026-04-20T23:30:00"},
    {}
)
check("fires on large amount at 11:30pm", r["triggered"] is True)

r = signal_night_large_txn(
    {"amount": 75_000, "action_timestamp": "2026-04-20T14:00:00"},
    {}
)
check("does NOT fire at 2pm",             r["triggered"] is False)

r = signal_night_large_txn(
    {"amount": 10_000, "action_timestamp": "2026-04-20T23:30:00"},
    {}
)
check("does NOT fire for small night amount", r["triggered"] is False)


# ── Full Scenario Tests ───────────────────────────────────────────

print()
print("══════════════════════════════════════════")
print("  Full Scenario Tests                     ")
print("══════════════════════════════════════════\n")


print("── Scenario 1: Normal Priya action → should ALLOW ──")
history = get_user_history("priya_27")
payload = {
    "user_id":          "priya_27",
    "action_type":      "view_portfolio",   # familiar action
    "amount":           5_000,              # normal amount
    "device_id":        "device_priya_phone",  # trusted
    "login_timestamp":  "2026-04-20T10:00:00",
    "action_timestamp": "2026-04-20T10:05:00",  # 5 minutes later
    "otp_attempts":     1,
    "retry_count":      0,
}
result = compute_risk_score(payload, history)
print(f"  Score: {result['risk_score']}  |  Decision: {result['decision']}")
check("Priya normal action → ALLOW", result["decision"] == "ALLOW")

print()
print("── Scenario 2: Priya on new device + first SIP → should WARN ──")
payload = {
    "user_id":          "priya_27",
    "action_type":      "start_sip",        # first time
    "amount":           8_000,              # normal amount
    "device_id":        "device_priya_new_tablet",  # NOT in trusted list
    "login_timestamp":  "2026-04-20T10:00:00",
    "action_timestamp": "2026-04-20T10:05:00",
    "otp_attempts":     1,
    "retry_count":      0,
}
result = compute_risk_score(payload, history)
print(f"  Score: {result['risk_score']}  |  Decision: {result['decision']}")
print(f"  Triggered: {[s['signal'] for s in result['triggered_signals']]}")
check("Priya new device + first SIP → WARN or BLOCK",
      result["decision"] in ("WARN", "BLOCK"))

print()
print("── Scenario 3: Suspicious actor → should BLOCK ──")
suspicious_history = get_user_history("suspicious_actor")
payload = {
    "user_id":          "suspicious_actor",
    "action_type":      "large_transfer",
    "amount":           200_000,            # 40× their average (5000)
    "device_id":        "device_unknown",   # NOT in trusted list
    "login_timestamp":  "2026-04-20T23:55:00",
    "action_timestamp": "2026-04-20T23:55:06",  # 6 seconds — rushed
    "otp_attempts":     4,                  # multiple OTP retries
    "retry_count":      0,
}
result = compute_risk_score(payload, suspicious_history)
print(f"  Score: {result['risk_score']}  |  Decision: {result['decision']}")
print(f"  Triggered: {[s['signal'] for s in result['triggered_signals']]}")
check("Suspicious actor → BLOCK", result["decision"] == "BLOCK")

print()
print("── Scenario 4: Arjun rebalancing (known, normal) → should ALLOW ──")
arjun_history = get_user_history("arjun_38")
payload = {
    "user_id":          "arjun_38",
    "action_type":      "rebalance_portfolio",  # familiar
    "amount":           40_000,                 # within avg range (50k avg)
    "device_id":        "device_arjun_phone",   # trusted
    "login_timestamp":  "2026-04-20T11:00:00",
    "action_timestamp": "2026-04-20T11:08:00",
    "otp_attempts":     1,
    "retry_count":      0,
}
result = compute_risk_score(payload, arjun_history)
print(f"  Score: {result['risk_score']}  |  Decision: {result['decision']}")
check("Arjun normal rebalance → ALLOW", result["decision"] == "ALLOW")


print()
print("══════════════════════════════════════════")
print("  All tests passed. Safe to push.         ")
print("══════════════════════════════════════════\n")
