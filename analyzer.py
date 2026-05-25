"""
US Healthcare AI Analyzer — Real AI Agent
==========================================
Enter any US healthcare company data and get a real AI analysis from Claude.

How to run:
1. Install the library: pip install anthropic
2. Run: python analyzer.py
"""

import anthropic

# ─── API-КЛЮЧ ─────────────────────────────────────────────────────────────────
API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"  # Get your key at console.anthropic.com
# ─────────────────────────────────────────────────────────────────────────────


def analyze_healthcare_company(company_data: str) -> dict:
    client = anthropic.Anthropic(api_key=API_KEY)

    prompt = f"""You are a senior healthcare industry analyst with deep expertise in the US healthcare market.

A user has provided the following information about a healthcare company:

---
{company_data}
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

## SUMMARY
[Write 3-4 sentences summarizing the company's strategic position, main challenge, and biggest opportunity. Be specific to this company.]

Rules: be specific to this company, use real US healthcare market context (CMS, HIPAA, ACA, payers), write in professional English, no extra sections."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_response(message.content[0].text)


def parse_response(text: str) -> dict:
    sections = {"risks": [], "opportunities": [], "trends": [], "summary": ""}
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
        elif "## SUMMARY" in line:
            current = "summary"
        elif line.startswith("- ") and current in ("risks", "opportunities", "trends"):
            sections[current].append(line[2:].replace("**", ""))
        elif current == "summary" and not line.startswith("#"):
            sections["summary"] += line.replace("**", "") + " "

    sections["summary"] = sections["summary"].strip()
    return sections


def print_analysis(company_name: str, analysis: dict):
    width = 70
    print("\n" + "=" * width)
    print(f"  🏥 US HEALTHCARE AI ANALYZER")
    print(f"  Company: {company_name}")
    print("=" * width)

    print("\n⚠️  RISKS")
    print("-" * width)
    for i, risk in enumerate(analysis["risks"], 1):
        print(f"  {i}. {risk}")

    print("\n🚀 OPPORTUNITIES")
    print("-" * width)
    for i, opp in enumerate(analysis["opportunities"], 1):
        print(f"  {i}. {opp}")

    print("\n📈 TRENDS")
    print("-" * width)
    for i, trend in enumerate(analysis["trends"], 1):
        print(f"  {i}. {trend}")

    print("\n📋 SUMMARY")
    print("-" * width)
    print(f"  {analysis['summary']}")
    print("\n" + "=" * width)


def get_company_data() -> tuple[str, str]:
    print("\nEnter company data. The more details — the more accurate the analysis.\n")
    company_name = input("Company name: ").strip()
    if not company_name:
        company_name = "Healthcare Company"

    print("\nDescribe the company (type, size, location, specialization, patients, etc.):")
    print("(Press Enter twice when done)\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    description = "\n".join(lines).strip()
    return company_name, f"Company name: {company_name}\n\n{description}"


# ─── EXAMPLES ────────────────────────────────────────────────────────────────

EXAMPLE_CLINIC = """
Company name: Hillcrest Internal Medicine
Type: Independent, physician-owned primary care / internal medicine clinic
Location: 12720 Hillcrest Rd, Dallas, TX 75230
Providers: 2 board-certified physicians (Dr. Renée Stock D.O., Dr. Shalaun Hawkins M.D.) + 2 physician assistants
Services: Annual physicals, preventive medicine, chronic disease management, acute care, women's health, telehealth, lab services
Notable: Minority-owned business, 30+ years combined experience, awarded Best in DFW 2022 and 2025
Payers: Accepts multiple insurance plans
Challenge: Small independent practice competing with large health systems like Baylor Scott & White and UT Southwestern in Dallas market
"""

EXAMPLE_TELEHEALTH = """
Company name: MindBridge Health
Type: Mental health telehealth startup
Founded: 2022, San Francisco CA (operates in 22 states)
Size: 35 employees, 180 contracted therapists and psychiatrists
Patients: ~12,000 active patients
Revenue: Subscription ($89/month) + insurance billing (Aetna, BCBS in-network)
Services: Individual therapy, psychiatry, couples counseling via video
"""

EXAMPLE_INSURANCE = """
Company name: BlueStar Health Plans
Type: Regional health insurance provider
Location: Southeastern US (Georgia, Alabama, South Carolina, Tennessee)
Size: 2.3 million members, 1,800 employees
Products: Individual marketplace plans, employer-sponsored plans, Medicare Advantage
Financials: $4.2B annual premium revenue, 87% medical loss ratio
"""

# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("\n" + "=" * 70)
    print("  🏥 US HEALTHCARE AI ANALYZER — Real AI Edition")
    print("  Powered by Claude (Anthropic)")
    print("=" * 70)

    print("\nSelect mode:")
    print("  1 — Enter your own company data")
    print("  2 — Example: Clinic (Hillcrest Internal Medicine, Dallas TX)")
    print("  3 — Example: Telehealth Startup (MindBridge Health)")
    print("  4 — Example: Insurance Provider (BlueStar Health Plans)")

    choice = input("\nYour choice (1/2/3/4): ").strip()

    if choice == "2":
        company_name, company_data = "Hillcrest Internal Medicine", EXAMPLE_CLINIC
    elif choice == "3":
        company_name, company_data = "MindBridge Health", EXAMPLE_TELEHEALTH
    elif choice == "4":
        company_name, company_data = "BlueStar Health Plans", EXAMPLE_INSURANCE
    else:
        company_name, company_data = get_company_data()

    print(f"\n⏳ Analyzing {company_name}...\n")

    try:
        analysis = analyze_healthcare_company(company_data)
        print_analysis(company_name, analysis)
    except anthropic.AuthenticationError:
        print("\n❌ Invalid API key. Check your key at console.anthropic.com")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
