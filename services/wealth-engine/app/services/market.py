import json

def get_market_context():
    try:
        with open("data/market_snapshot.json") as f:
            data = json.load(f)

        return {
            "market_signal": "negative" if data["nifty_ytd"] < 0 else "positive",
            "inflation_alert": data["inflation_rate"] > 0.06,
            "advice": "High inflation detected. Consider FDs or gold."
        }
    except:
        return {
            "market_signal": "neutral",
            "inflation_alert": False,
            "advice": "Market stable."
        }