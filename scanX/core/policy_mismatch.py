# core/policy_mismatch.py

def detect_policy_mismatch(policy_quality: dict, experience_data: dict) -> dict:
    """
    Detect mismatch between stated policies and user complaints.
    """

    mismatches = {}

    # -----------------------------
    # Refund vs Refund Complaints
    # -----------------------------
    refund_policy = policy_quality.get("refund", {})
    refund_complaints = experience_data.get("payment_issues", {}).get("count", 0)

    if refund_policy.get("exists"):
        if refund_policy.get("quality") in ["Vague", "Partial"] and refund_complaints >= 3:
            mismatches["refund"] = {
                "severity": "High",
                "summary": (
                    "A refund policy exists but lacks clarity, while users "
                    "frequently report refund-related issues."
                )
            }
        elif refund_policy.get("quality") == "Clear" and refund_complaints >= 5:
            mismatches["refund"] = {
                "severity": "Medium",
                "summary": (
                    "Despite a clear refund policy, users report delays or "
                    "issues with refund enforcement."
                )
            }

    # -----------------------------
    # Support vs Support Complaints
    # -----------------------------
    support_complaints = experience_data.get("customer_support_issues", {}).get("count", 0)

    if support_complaints >= 4:
        mismatches["support"] = {
            "severity": "Medium",
            "summary": (
                "Customer support channels exist, but repeated complaints "
                "suggest slow or ineffective responses."
            )
        }

    # -----------------------------
    # Account / Security vs Policy
    # -----------------------------
    security_complaints = experience_data.get("security_concerns", {}).get("count", 0)

    if security_complaints >= 2:
        mismatches["security"] = {
            "severity": "Medium",
            "summary": (
                "Users report security-related concerns despite the presence "
                "of standard privacy or security statements."
            )
        }

    return mismatches
