# core/policy_analyzer.py

import re
import requests
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "scanX Trust Analyzer"
}

TIMEOUT = 10


POLICY_KEYWORDS = {
    "refund": [
        "refund", "return", "cancellation", "money back"
    ],
    "privacy": [
        "privacy", "personal data", "information collected"
    ],
    "terms": [
        "terms", "conditions", "agreement"
    ]
}

QUALITY_SIGNALS = {
    "timeframe": [
        r"\b\d+\s?(day|days|week|weeks|business days)\b"
    ],
    "process": [
        "how to", "process", "steps", "request", "contact"
    ],
    "vague_language": [
        "at our discretion",
        "may change without notice",
        "not guaranteed",
        "sole discretion"
    ]
}


def fetch_policy_text(base_url: str, path: str) -> str:
    try:
        r = requests.get(urljoin(base_url, path), headers=HEADERS, timeout=TIMEOUT)
        if r.status_code < 400:
            return r.text.lower()
    except requests.RequestException:
        pass
    return ""


def analyze_policy_text(text: str) -> dict:
    analysis = {
        "has_timeframe": False,
        "has_process": False,
        "vague_language": False
    }

    for pattern in QUALITY_SIGNALS["timeframe"]:
        if re.search(pattern, text):
            analysis["has_timeframe"] = True

    for kw in QUALITY_SIGNALS["process"]:
        if kw in text:
            analysis["has_process"] = True

    for kw in QUALITY_SIGNALS["vague_language"]:
        if kw in text:
            analysis["vague_language"] = True

    return analysis


def analyze_policies(domain: str, live_inspection: dict) -> dict:
    """
    Analyze quality of refund, privacy and terms policies.
    """
    base_url = f"https://{domain}"
    results = {}

    policy_paths = {
        "refund": live_inspection["pages"].get("refund_policy", []),
        "privacy": live_inspection["pages"].get("privacy_policy", []),
        "terms": live_inspection["pages"].get("terms", [])
    }

    for policy_type, pages in policy_paths.items():
        if not pages:
            results[policy_type] = {
                "exists": False,
                "quality": "Missing"
            }
            continue

        text = fetch_policy_text(base_url, pages[0]["url"].replace(base_url, ""))
        analysis = analyze_policy_text(text)

        # Quality scoring (rule-based)
        if analysis["has_timeframe"] and analysis["has_process"] and not analysis["vague_language"]:
            quality = "Clear"
        elif analysis["has_process"]:
            quality = "Partial"
        else:
            quality = "Vague"

        results[policy_type] = {
            "exists": True,
            "quality": quality,
            "signals": analysis
        }

    return results
