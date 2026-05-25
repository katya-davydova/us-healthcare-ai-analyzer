"""
US Healthcare AI Analyzer — Web Server
========================================
Запускает локальный сервер, который соединяет index.html с Claude API.

Как запустить:
1. pip install flask anthropic
2. python server.py
3. Открой браузер: http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os

app = Flask(__name__)

# ─── API-КЛЮЧ ─────────────────────────────────────────────────────────────────
API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"  # Get your key at console.anthropic.com
# ─────────────────────────────────────────────────────────────────────────────

# Папка где лежит index.html (рабочий стол)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    company_text = data.get("company", "").strip()

    if not company_text:
        return jsonify({"error": "No company data provided"}), 400

    prompt = f"""You are a senior healthcare industry analyst with deep expertise in the US healthcare market.

Industry context (use this data to inform your Five Forces analysis):
- Competitive rivalry is HIGH: EBITDA fell from 11.2% (2019) to 8.9% (2024), expected 8.7% by 2027. Segment profitability below 1%. UnitedHealthcare controls 90,000+ physicians. Amazon, CVS invested $20B+ acquiring One Medical, Oak Street Health, Signify Health. CMS price transparency rules intensify competition.
- Threat of new entrants is LOW but rising: AI removes barriers; 85% of market leaders already exploring or adopting AI tools (McKinsey 2025).
- Supplier power is HIGH: workforce shortages give staffing agencies pricing power; drug prices growing 8% annually, expected to reach $990B by 2029; tech/SaaS providers gaining influence.
- Buyer power shifting from MODERATE to HIGH: 94% of patients willing to use telehealth again (vs 80% in 2020); millennials (43%) and Gen Z (33%) are less loyal to providers (Deloitte 2024).
- Threat of substitutes is MODERATE to LOW: shift to outpatient/home-based care could redistribute up to $250B; US wellness market reached $480B; preventive care reducing dependency on traditional providers.

A user has provided the following information about a healthcare company:

---
{company_text}
---

Analyze this company and provide a structured report. Format your response EXACTLY like this:

## RISKS
- [Risk title] — [2-3 sentence explanation specific to this company]
- [Risk title] — [explanation]
- [Risk title] — [explanation]
- [Risk title] — [explanation]
- [Risk title] — [explanation]

## OPPORTUNITIES
- [Opportunity title] — [2-3 sentence explanation specific to this company]
- [Opportunity title] — [explanation]
- [Opportunity title] — [explanation]
- [Opportunity title] — [explanation]
- [Opportunity title] — [explanation]

## TRENDS
- [Trend title] — [2-3 sentence explanation relevant to this type of company]
- [Trend title] — [explanation]
- [Trend title] — [explanation]

## FIVE FORCES
- Competitive Rivalry — [How intense is rivalry for THIS specific company and why]
- Threat of New Entrants — [How this force affects THIS company specifically]
- Supplier Power — [Key supplier dependencies and risks for THIS company]
- Buyer Power — [How patient/payer power affects THIS company]
- Threat of Substitutes — [What substitutes threaten THIS company's services]

## SUMMARY
[Write 3-4 sentences summarizing the company's strategic position, main challenge, and biggest opportunity. Be specific to this company.]

Rules: be specific to this company, use real US healthcare market context (CMS, HIPAA, ACA, payers), write in professional English, no extra sections."""

    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        parsed = parse_response(raw)
        return jsonify(parsed)

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_response(text: str) -> dict:
    sections = {"risks": [], "opportunities": [], "trends": [], "five_forces": [], "summary": ""}
    current = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "## RISKS" in line:
            current = "risks"
        elif "## OPPORTUNITIES" in line:
            current = "opportunities"
        elif "## TRENDS" in line:
            current = "trends"
        elif "## FIVE FORCES" in line:
            current = "five_forces"
        elif "## SUMMARY" in line:
            current = "summary"
            # Summary might be on the same line after the header
            after = line.split("## SUMMARY", 1)[-1].strip("# ").strip()
            if after:
                sections["summary"] += after + " "
        elif line.startswith("- ") and current in ("risks", "opportunities", "trends", "five_forces"):
            sections[current].append(line[2:].replace("**", ""))
        elif current == "summary" and not line.startswith("#"):
            sections["summary"] += line.replace("**", "") + " "

    sections["summary"] = sections["summary"].strip()
    return sections


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  🏥 US Healthcare AI Analyzer — Web Server")
    print("=" * 55)
    print("  ✅ Сервер запущен!")
    print("  🌐 Открой браузер и перейди по адресу:")
    print("     http://localhost:5000")
    print("  🛑 Чтобы остановить: нажми Ctrl+C")
    print("=" * 55 + "\n")
    app.run(debug=False, port=5000)
