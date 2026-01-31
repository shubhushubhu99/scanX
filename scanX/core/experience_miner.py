# core/experience_miner.py

EXPERIENCE_PATTERNS = {
    "payment_issues": [
        "payment", "refund", "charged", "money", "billing", "price"
    ],
    "delivery_issues": [
        "delivery", "delivered", "shipping", "package", "late", "missing"
    ],
    "customer_support_issues": [
        "support", "customer service", "no response", "unresponsive", "help"
    ],
    "account_issues": [
        "account", "login", "locked", "suspended", "verification"
    ],
    "security_concerns": [
        "hacked", "breach", "security", "phishing", "fraud"
    ]
}


def mine_experiences(evidence: dict) -> dict:
    """
    Extract user experience patterns from indexed public discussions.
    """
    findings = {}

    for category, keywords in EXPERIENCE_PATTERNS.items():
        count = 0
        examples = set()

        for platform, items in evidence.items():
            for item in items:
                text = (
                    (item.get("title") or "") + " " +
                    (item.get("snippet") or "")
                ).lower()

                for kw in keywords:
                    if kw in text:
                        count += 1
                        examples.add(kw)

        if count > 0:
            findings[category] = {
                "count": count,
                "examples": list(examples)[:3]
            }

    return findings
