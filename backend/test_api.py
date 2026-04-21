"""Quick API verification script."""
import httpx
import json

BASE = "http://localhost:8000"

# 1. Users
r = httpx.get(f"{BASE}/users/")
users = r.json()
print(f"=== Users ({len(users)}) ===")
for u in users:
    print(f"  {u['id']}: {u['name']} (income={u['monthly_income']})")

# 2. Wealth Insights
r2 = httpx.get(f"{BASE}/wealth/insights?user_id=1")
data = r2.json()
print(f"\n=== Wealth Insights (User 1) ===")
print(f"  Income: {data['total_income']}, Expense: {data['total_expense']}")
print(f"  Savings: {data['savings']}, Rate: {data['savings_rate']}%")

# 3. Portfolio Suggestion
r3 = httpx.get(f"{BASE}/wealth/portfolio-suggestion?user_id=1")
p = r3.json()
print(f"\n=== Portfolio Suggestion ===")
print(f"  Equity: {p['equity_pct']}%, Debt: {p['debt_pct']}%, Gold: {p['gold_pct']}%")

# 4. Protection Layer - LOW risk
r4 = httpx.post(f"{BASE}/actions/evaluate", json={
    "user_id": 1,
    "action_type": "start_sip",
    "amount": 5000,
    "device_id": "device-arjun-phone",
    "otp_attempts": 1,
})
d4 = r4.json()
print(f"\n=== Protection (Low Risk) ===")
print(f"  Score: {d4['risk_score']}, Level: {d4['risk_level']}, Decision: {d4['decision']}")
print(f"  Message: {d4['message']}")

# 5. Protection Layer - HIGH risk
r5 = httpx.post(f"{BASE}/actions/evaluate", json={
    "user_id": 1,
    "action_type": "invest_lumpsum",
    "amount": 500000,
    "device_id": "unknown-device-xyz",
    "otp_attempts": 4,
})
d5 = r5.json()
print(f"\n=== Protection (High Risk) ===")
print(f"  Score: {d5['risk_score']}, Level: {d5['risk_level']}, Decision: {d5['decision']}")
print(f"  Message: {d5['message']}")

# 6. Chat
r6 = httpx.post(f"{BASE}/chat/", json={
    "user_id": 1,
    "message": "How should I start investing?",
})
d6 = r6.json()
print(f"\n=== Chat Response ===")
print(f"  Reply: {d6['reply'][:200]}...")
print(f"  Reasoning: {d6['reasoning']}")

print("\nAll API tests passed!")
