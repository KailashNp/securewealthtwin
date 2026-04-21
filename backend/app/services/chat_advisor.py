"""Chat advisor – GenAI (OpenAI/Gemini) with rule-based fallback."""

from ..config import get_settings
from ..schemas import ChatResponse


def get_chat_response(message: str, context: dict) -> ChatResponse:
    """
    Generate a personalised financial advice response.

    Tries OpenAI/Gemini if API key is available, otherwise falls back to
    rule-based responses.
    """
    settings = get_settings()

    if settings.OPENAI_API_KEY:
        return _openai_response(message, context, settings.OPENAI_API_KEY)
    elif settings.GEMINI_API_KEY:
        return _gemini_response(message, context, settings.GEMINI_API_KEY)
    else:
        return _rule_based_response(message, context)


def _build_system_prompt(context: dict) -> str:
    return f"""You are SecureWealth Twin, a friendly and knowledgeable AI financial advisor for an Indian bank customer.

CUSTOMER PROFILE:
- Name: {context['name']}
- Age: {context['age']}
- Occupation: {context['occupation']}
- Monthly Income: ₹{context['monthly_income']:,.0f}
- Risk Appetite: {context['risk_appetite']}
- Total Assets: ₹{context['total_assets']:,.0f}
- Savings Rate: {context['savings_rate']}%
- Goals: {context.get('goals', [])}

RULES:
1. Give personalised, actionable advice based on the customer's profile.
2. Always explain WHY you recommend something.
3. Suggest specific amounts and timelines when possible.
4. Never promise guaranteed returns — use phrases like "historically" or "projected".
5. Mention relevant Indian tax-saving sections (80C, 80D, etc.) when applicable.
6. Keep responses concise but helpful (2-4 paragraphs max).
7. Add a "DISCLAIMER" at the end: "This is for informational purposes only, not financial advice."
"""


def _openai_response(message: str, context: dict, api_key: str) -> ChatResponse:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _build_system_prompt(context)},
                {"role": "user", "content": message},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        return ChatResponse(
            reply=reply,
            reasoning="Response generated using AI with your financial context for personalised advice.",
        )
    except Exception as e:
        return _rule_based_response(message, context)


def _gemini_response(message: str, context: dict, api_key: str) -> ChatResponse:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = _build_system_prompt(context) + f"\n\nUser question: {message}"
        response = model.generate_content(prompt)
        return ChatResponse(
            reply=response.text,
            reasoning="Response generated using Gemini AI with your financial context.",
        )
    except Exception:
        return _rule_based_response(message, context)


def _rule_based_response(message: str, context: dict) -> ChatResponse:
    """Keyword-based fallback when no API key is available."""
    msg_lower = message.lower()
    name = context.get("name", "there")
    income = context.get("monthly_income", 0)
    savings_rate = context.get("savings_rate", 0)
    risk = context.get("risk_appetite", "moderate")

    if any(kw in msg_lower for kw in ["save", "saving", "savings"]):
        ideal_savings = income * 0.3
        reply = (
            f"Hi {name}! Based on your income of ₹{income:,.0f}/month, I'd recommend saving "
            f"at least ₹{ideal_savings:,.0f}/month (30% of income). "
            f"Your current savings rate is {savings_rate}%. "
            f"\n\nTip: Set up an automatic SIP to build discipline. "
            f"Even ₹{income * 0.1:,.0f}/month in a Nifty 50 index fund can grow significantly over 10 years."
            f"\n\n*DISCLAIMER: This is for informational purposes only, not financial advice.*"
        )
        reasoning = "Rule-based: detected savings-related keywords, computed ideal savings at 30% of income."

    elif any(kw in msg_lower for kw in ["invest", "sip", "mutual fund", "stock"]):
        if risk == "aggressive":
            suggestion = "70-80% equity (index funds, mid-cap MFs) and 20-30% debt"
        elif risk == "conservative":
            suggestion = "30% equity, 50% debt (FDs, PPF), and 20% gold"
        else:
            suggestion = "50-60% equity, 30% debt, and 10-20% gold"
        reply = (
            f"Hi {name}! Given your {risk} risk profile, I'd suggest allocating: {suggestion}. "
            f"\n\nA good starting point is a monthly SIP of ₹{income * 0.15:,.0f} in a diversified index fund. "
            f"Historically, Nifty 50 has returned ~12% annually over 10+ year periods."
            f"\n\n*DISCLAIMER: Past performance doesn't guarantee future returns.*"
        )
        reasoning = f"Rule-based: investment query matched, profile is {risk} risk appetite."

    elif any(kw in msg_lower for kw in ["tax", "80c", "80d", "deduction"]):
        reply = (
            f"Hi {name}! Here are your key tax-saving options:\n"
            f"• **Section 80C** (up to ₹1.5L): ELSS MF, PPF, EPF, NSC, 5-yr FD\n"
            f"• **Section 80CCD(1B)** (extra ₹50K): NPS contribution\n"
            f"• **Section 80D**: Health insurance premiums (₹25K-₹50K)\n"
            f"\nBased on your income, you could save ~₹{min(income * 12 * 0.3, 250000) * 0.3:,.0f} in taxes annually."
            f"\n\n*DISCLAIMER: Consult a tax professional for personalised advice.*"
        )
        reasoning = "Rule-based: tax-related query, listing common deduction sections."

    elif any(kw in msg_lower for kw in ["goal", "plan", "house", "home", "retire", "education"]):
        goals = context.get("goals", [])
        if goals:
            goal_text = "\n".join(
                f"  • {g['name']}: ₹{g['current']:,.0f} / ₹{g['target']:,.0f}"
                for g in goals
            )
            reply = (
                f"Hi {name}! Here's your current goal progress:\n{goal_text}\n\n"
                f"To reach your goals faster, consider increasing your monthly savings by ₹{income * 0.05:,.0f}. "
                f"The power of compounding means even small increases make a big difference over time."
                f"\n\n*DISCLAIMER: This is for informational purposes only.*"
            )
        else:
            reply = (
                f"Hi {name}! I'd recommend setting at least 2-3 financial goals: "
                f"an emergency fund (6 months expenses), a medium-term goal, and a retirement corpus. "
                f"Would you like me to help you set up a goal?"
                f"\n\n*DISCLAIMER: This is for informational purposes only.*"
            )
        reasoning = "Rule-based: goal/planning query, showing current progress and suggestions."

    else:
        reply = (
            f"Hi {name}! I'm your SecureWealth Twin advisor. I can help you with:\n"
            f"• 💰 **Savings** – How much to save and where\n"
            f"• 📈 **Investments** – SIPs, mutual funds, portfolio allocation\n"
            f"• 🎯 **Goals** – Planning for house, retirement, education\n"
            f"• 🧾 **Tax Saving** – 80C, 80D, NPS deductions\n"
            f"\nJust ask me anything about your finances!"
            f"\n\n*DISCLAIMER: This is for informational purposes only, not financial advice.*"
        )
        reasoning = "Rule-based: general query, showing available topics."

    return ChatResponse(reply=reply, reasoning=reasoning)
