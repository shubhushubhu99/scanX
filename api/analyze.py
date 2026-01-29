from utils.validators import validate_target
from core.domain_intel import domain_intelligence
from core.content_scanner import content_scan


def analyze_target(target: str) -> dict:
    """
    Main analysis entry point for scanX.
    Returns a structured scan report.
    """

    try:
        domain = validate_target(target)
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }

    try:
        domain_info = domain_intelligence(domain)
        content_info = content_scan(domain)

        return {
            "success": True,
            "target": domain,
            "domain_intel": domain_info,
            "content_scan": content_info
        }

    except Exception as e:
        return {
            "success": False,
            "error": "Analysis failed",
            "details": str(e)
        }
