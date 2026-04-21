"""
user_store.py
-------------
Simulates a database of user behavioural baselines.
In a real bank this would be a proper database.
For the hackathon this is an in-memory dict that also
updates in real-time as actions are performed.

YOU own this file.
The 5 personas here match Member 5's JSON files exactly.
"""

from typing import Optional
from copy import deepcopy

# ─────────────────────────────────────────────────────────────────
# Default user history profiles
# These mirror the personas in data/personas/
# ─────────────────────────────────────────────────────────────────
_DEFAULT_USERS: dict = {

    "priya_27": {
        "user_id":                "priya_27",
        "name":                   "Priya Sharma",
        "trusted_devices":        ["device_priya_phone", "device_priya_laptop"],
        "avg_transaction_amount": 12_000,
        "past_action_types":      ["view_portfolio", "view_goals"],
        # starts with no SIPs — so first_investment will fire
    },

    "ramesh_45": {
        "user_id":                "ramesh_45",
        "name":                   "Ramesh Iyer",
        "trusted_devices":        ["device_ramesh_desktop"],
        "avg_transaction_amount": 35_000,
        "past_action_types":      ["start_sip", "renew_fd", "view_portfolio"],
    },

    "neha_33": {
        "user_id":                "neha_33",
        "name":                   "Neha Kapoor",
        "trusted_devices":        ["device_neha_phone"],
        "avg_transaction_amount": 18_000,
        "past_action_types":      ["view_portfolio", "buy_gold"],
    },

    "arjun_38": {
        "user_id":                "arjun_38",
        "name":                   "Arjun Mehta",
        "trusted_devices":        ["device_arjun_phone", "device_arjun_tablet"],
        "avg_transaction_amount": 50_000,
        "past_action_types":      ["start_sip", "rebalance_portfolio",
                                   "buy_equity", "book_gold_profits"],
    },

    "kiran_sme": {
        "user_id":                "kiran_sme",
        "name":                   "Kiran Enterprises",
        "trusted_devices":        ["device_kiran_office"],
        "avg_transaction_amount": 80_000,
        "past_action_types":      ["surplus_fd", "view_cashflow"],
    },

    # ── Special demo persona: designed to BLOCK ───────────────────
    # Use this for the fraud demo during the presentation.
    # New device + huge amount + first investment type.
    "suspicious_actor": {
        "user_id":                "suspicious_actor",
        "name":                   "Demo Fraud Scenario",
        "trusted_devices":        ["device_known"],   # new_device will NOT be known
        "avg_transaction_amount": 5_000,              # amount_anomaly fires hard
        "past_action_types":      [],                  # first_investment fires
    },
}

# Live in-memory store (starts as a deep copy of defaults)
_STORE: dict = deepcopy(_DEFAULT_USERS)


def get_user_history(user_id: str) -> Optional[dict]:
    """Return the behavioural baseline for a user, or None if not found."""
    return _STORE.get(user_id)


def update_trusted_device(user_id: str, device_id: str) -> None:
    """
    Add a device to a user's trusted list after a successful,
    manually verified action. Call this after a WARN action is
    confirmed by the user (post cooling-off).
    """
    user = _STORE.get(user_id)
    if user and device_id not in user["trusted_devices"]:
        user["trusted_devices"].append(device_id)


def record_action_type(user_id: str, action_type: str) -> None:
    """
    Record that a user has performed a given action type.
    This prevents first_investment from firing again for the same type.
    """
    user = _STORE.get(user_id)
    if user and action_type not in user["past_action_types"]:
        user["past_action_types"].append(action_type)


def update_avg_amount(user_id: str, new_amount: float) -> None:
    """
    Recalculate the user's rolling average after a successful transaction.
    Simple exponential moving average with alpha=0.2.
    """
    user = _STORE.get(user_id)
    if user:
        old_avg = user["avg_transaction_amount"]
        user["avg_transaction_amount"] = round(0.8 * old_avg + 0.2 * new_amount)


def list_users() -> list:
    """Return a list of all known user IDs."""
    return list(_STORE.keys())
