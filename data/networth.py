from fastapi import FastAPI, HTTPException
import json
import os

app = FastAPI()

def load_persona(user_id: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "personas", f"{user_id}.json")
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    
    with open(path) as f:
        return json.load(f)

@app.post("/api/networth/compute")
def compute_networth(body: dict):
    user_id = body.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    user = load_persona(user_id)
    
    bank_balance = sum(
        a["balance"] for a in user.get("accounts", [])
        if a["balance"] > 0
    )
    
    portfolio_value = sum(
        h["current_value"] for h in user.get("portfolio", {}).get("holdings", [])
    )
    
    asset_value = sum(
        a["value"] for a in user.get("assets", [])
    )
    
    liabilities = user.get("liabilities", 0)
    
    total = bank_balance + portfolio_value + asset_value - liabilities
    
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "breakdown": {
            "bank_balances": bank_balance,
            "portfolio_value": portfolio_value,
            "physical_assets": asset_value,
            "liabilities": liabilities
        },
        "net_worth": total
    }

@app.get("/api/user/{user_id}/assets")
def get_assets(user_id: str):
    user = load_persona(user_id)
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "assets": user.get("assets", []),
        "accounts": user.get("accounts", []),
        "portfolio": user.get("portfolio", {})
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)