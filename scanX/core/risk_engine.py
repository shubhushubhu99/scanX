# core/risk_engine.py

def classify_legitimacy(evidence: dict) -> str:
    """
    Determine whether a website is well-established or unknown
    based on strong legitimacy signals.
    """
    legitimacy_keywords = [
        "customer service",
        "help & contact",
        "official",
        "support",
        "threat intelligence",
        "security issue",
        "privacy policy",
        "terms of service",
    ]

    score = 0

    for platform, items in evidence.items():
        for item in items:
            title = item.get("title", "").lower()
            if any(keyword in title for keyword in legitimacy_keywords):
                score += 1

    if score >= 3:
        return "Established"

    return "Unknown"


def classify_complaint_intensity(evidence: dict) -> str:
    """
    Measure how complaint-heavy the discussion is.
    This does NOT decide legitimacy.
    """
    complaint_keywords = [
        "scam",
        "fraud",
        "refund issue",
        "payment issue",
        "fake",
        "complaint",
        "not legit",
    ]

    hits = 0

    for platform, items in evidence.items():
        for item in items:
            text = (
                item.get("title", "") + " " +
                item.get("snippet", "")
            ).lower()

            if any(keyword in text for keyword in complaint_keywords):
                hits += 1

    if hits >= 8:
        return "High"
    if hits >= 3:
        return "Medium"
    if hits > 0:
        return "Low"

    return "None"


def baseline_risk_assessment(
    evidence_strength: str,
    legitimacy: str,
    complaint_intensity: str
) -> dict:
    """
    Final baseline risk decision (AI cannot override this).
    """

    # 🟢 Rule 1: Well-established platforms are low risk by default
    if legitimacy == "Established":
        return {
            "risk_level": "Low Risk (Well-established)",
            "confidence": "High",
            "reason": (
                "The website shows strong legitimacy signals such as official "
                "support, security pages, and extensive public presence. "
                "User complaints appear to be typical for a large platform."
            )
        }

    # 🔴 Rule 2: Unknown site + high complaints = high risk
    if legitimacy == "Unknown" and complaint_intensity == "High":
        return {
            "risk_level": "High Risk",
            "confidence": "High",
            "reason": (
                "The website lacks strong legitimacy signals and is associated "
                "with multiple complaint-related discussions."
            )
        }

    # 🟡 Rule 3: Unknown site + some complaints
    if legitimacy == "Unknown" and complaint_intensity in ["Medium", "Low"]:
        return {
            "risk_level": "Moderate Risk",
            "confidence": "Medium",
            "reason": (
                "Some public discussions raise concerns, but evidence is not "
                "strong enough to confirm severe risk."
            )
        }

    # ⚪ Rule 4: No evidence available
    if evidence_strength == "None":
        return {
            "risk_level": "Insufficient Data",
            "confidence": "Low",
            "reason": (
                "There is insufficient publicly indexed information available "
                "to assess the trustworthiness of this website."
            )
        }

    # 🟡 Default fallback
    return {
        "risk_level": "Moderate Risk",
        "confidence": "Low",
        "reason": (
            "Public information is mixed and does not clearly indicate "
            "whether the website is safe or unsafe."
        )
    }


def evaluate_risk(osint_data: dict) -> dict:
    """
    Main entry point used by the API.
    """
    evidence = osint_data.get("evidence", {})
    evidence_strength = osint_data.get("evidence_strength", "None")

    legitimacy = classify_legitimacy(evidence)
    complaint_intensity = classify_complaint_intensity(evidence)

    baseline = baseline_risk_assessment(
        evidence_strength,
        legitimacy,
        complaint_intensity
    )

    return {
        "baseline_risk": baseline,
        "legitimacy": legitimacy,
        "complaint_intensity": complaint_intensity,
        "evidence_strength": evidence_strength
    }
