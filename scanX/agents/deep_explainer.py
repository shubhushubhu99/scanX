# agents/deep_explainer.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


SYSTEM_PROMPT = """
You are a cybersecurity and trust analyst.

You are given VERIFIED evidence collected from:
- Google-indexed public discussions
- Live website inspection
- Extracted customer experience patterns
- Rule-based baseline risk assessment

Rules you MUST follow:
- Do NOT invent facts
- Do NOT accuse the website
- Do NOT exaggerate
- If evidence is weak or normal, clearly say so
- Explain issues only if evidence supports them
- Be specific and practical
- Adapt your explanation to the user's selected purpose

Your tone must be neutral, investigative, and professional.
"""


def explain_trust(
    domain: str,
    category: str,
    osint_data: dict,
    experience_data: dict,
    live_inspection: dict,
    risk_result: dict
) -> dict:
    print("[AI] explain_trust() CALLED")
    """
    Produce a deep, dynamic explanation based on real signals.
    """

    prompt = f"""
Website: {domain}
Intended purpose: {category}

=== BASELINE ASSESSMENT ===
Risk level: {risk_result['baseline_risk']['risk_level']}
Reason: {risk_result['baseline_risk']['reason']}
Confidence: {risk_result['baseline_risk']['confidence']}

=== LIVE SITE INSPECTION ===
Homepage reachable: {live_inspection['homepage']}
Support signals: {live_inspection['signals']}
Support emails found: {live_inspection['support_emails']}

=== PUBLIC EXPERIENCE PATTERNS ===
{experience_data if experience_data else "No dominant complaint patterns found."}

=== GOOGLE-INDEXED PRESENCE ===
Evidence strength: {osint_data['evidence_strength']}
Platforms with mentions: {osint_data['platforms_with_mentions']}

TASKS:
1. Explain what is working well on this website (if any).
2. Explain what problems or weaknesses are visible from evidence.
3. Explain how these issues affect the intended purpose.
4. Give a clear, practical recommendation to the user.
5. If this is a well-established site, clearly say that complaints are normal.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[SYSTEM_PROMPT, prompt]
    )

    return {
        "analysis": response.text.strip(),
        "risk_level": risk_result["baseline_risk"]["risk_level"],
        "confidence": risk_result["baseline_risk"]["confidence"]
    }
