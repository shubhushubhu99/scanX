# # core/trust_dimensions.py

# def evaluate_trust_dimensions(
#     osint: dict,
#     experience: dict,
#     live: dict,
#     policy_quality: dict,
#     policy_mismatches: dict
# ) -> dict:
#     """
#     Evaluate independent trust dimensions using heterogeneous signals.
#     """

#     dimensions = {}

#     # -----------------------------
#     # 1. Operational Reliability
#     # -----------------------------
#     support_issues = experience.get("customer_support_issues", {}).get("count", 0)
#     has_help = live["signals"].get("has_help_center", False)

#     if has_help and support_issues < 3:
#         status = "Strong"
#         reason = "Customer support infrastructure exists with limited public complaints."
#     elif has_help:
#         status = "Moderate"
#         reason = "Support channels exist, but recurring complaints suggest response delays."
#     else:
#         status = "Weak"
#         reason = "Lack of visible support channels combined with user complaints."

#     dimensions["operational_reliability"] = {
#         "status": status,
#         "reason": reason
#     }

#     # -----------------------------
#     # 2. Policy Enforcement
#     # -----------------------------
#     if "refund" in policy_mismatches:
#         status = "Weak"
#         reason = policy_mismatches["refund"]["summary"]
#     else:
#         refund_quality = policy_quality.get("refund", {}).get("quality", "Missing")
#         if refund_quality == "Clear":
#             status = "Strong"
#             reason = "Refund policy is clearly defined with no dominant enforcement complaints."
#         elif refund_quality == "Partial":
#             status = "Moderate"
#             reason = "Refund policy exists but lacks full clarity."
#         else:
#             status = "Weak"
#             reason = "Refund policy is missing or too vague to assess enforcement."

#     dimensions["policy_enforcement"] = {
#         "status": status,
#         "reason": reason
#     }

#     # -----------------------------
#     # 3. User Harm Exposure
#     # -----------------------------
#     total_complaints = sum(v.get("count", 0) for v in experience.values())

#     if total_complaints >= 10:
#         status = "Elevated"
#         reason = "Multiple recurring user complaints indicate repeated negative user experiences."
#     elif total_complaints >= 4:
#         status = "Moderate"
#         reason = "Some user complaints exist but do not dominate public discussion."
#     else:
#         status = "Low"
#         reason = "Limited evidence of repeated user harm in public discussions."

#     dimensions["user_harm_exposure"] = {
#         "status": status,
#         "reason": reason
#     }

#     # -----------------------------
#     # 4. Security Posture
#     # -----------------------------
#     security_issues = experience.get("security_concerns", {}).get("count", 0)

#     if security_issues >= 2:
#         status = "Concerning"
#         reason = "Multiple public mentions of security or account safety issues."
#     elif security_issues == 1:
#         status = "Monitor"
#         reason = "Isolated security-related mention detected."
#     else:
#         status = "Normal"
#         reason = "No dominant public indicators of security risk."

#     dimensions["security_posture"] = {
#         "status": status,
#         "reason": reason
#     }

#     # -----------------------------
#     # 5. Transparency & Accountability
#     # -----------------------------
#     policies_present = sum(
#         1 for p in policy_quality.values() if p.get("exists")
#     )

#     public_presence = osint.get("evidence_strength", "Low")

#     if policies_present >= 3 and public_presence == "High":
#         status = "Strong"
#         reason = "Clear policies combined with extensive public presence."
#     elif policies_present >= 2:
#         status = "Moderate"
#         reason = "Some transparency mechanisms exist, but coverage is incomplete."
#     else:
#         status = "Weak"
#         reason = "Limited policy transparency or public accountability signals."

#     dimensions["transparency_accountability"] = {
#         "status": status,
#         "reason": reason
#     }

#     return dimensions

def evaluate_trust_dimensions(
    osint: dict,
    experience: dict,
    live: dict,
    policy_quality: dict,
    policy_mismatches: dict,
    infra: dict = None,
    security: dict = None,
    content: dict = None
) -> dict:

    dimensions = {}

    # 1️⃣ Operational Reliability
    support_issues = experience.get("customer_support_issues", {}).get("count", 0)
    delivery_issues = experience.get("delivery_issues", {}).get("count", 0)

    if support_issues >= 5 or delivery_issues >= 5:
        dimensions["operational_reliability"] = {
            "status": "Moderate",
            "reason": "Recurring delivery or support-related complaints reported."
        }
    else:
        dimensions["operational_reliability"] = {
            "status": "Strong",
            "reason": "Operational complaints appear limited or isolated."
        }

    # 2️⃣ Security Posture
    security_mentions = experience.get("security_concerns", {}).get("count", 0)
    security_risk = security.get("risk_signal") if security else "Unknown"

    if security_mentions >= 3 or security_risk == "High":
        dimensions["security_posture"] = {
            "status": "Concerning",
            "reason": "Security-related complaints or weak security enforcement detected."
        }
    elif security_risk == "Moderate":
        dimensions["security_posture"] = {
            "status": "Moderate",
            "reason": "Basic security controls exist but gaps are present."
        }
    else:
        dimensions["security_posture"] = {
            "status": "Strong",
            "reason": "Security configuration and public perception appear strong."
        }

    # 3️⃣ Infrastructure Stability
    infra_risk = infra.get("risk_signal") if infra else "Unknown"

    if infra_risk == "High":
        dimensions["infrastructure_stability"] = {
            "status": "Weak",
            "reason": "Domain is very new or infrastructure appears unstable."
        }
    elif infra_risk == "Moderate":
        dimensions["infrastructure_stability"] = {
            "status": "Moderate",
            "reason": "Infrastructure maturity is limited."
        }
    else:
        dimensions["infrastructure_stability"] = {
            "status": "Strong",
            "reason": "Domain age and DNS infrastructure indicate stability."
        }

    # 4️⃣ Content & Transparency
    content_risk = content.get("risk_signal") if content else "Unknown"
    privacy_quality = policy_quality.get("privacy", {}).get("quality")

    if content_risk == "High" or privacy_quality == "Vague":
        dimensions["content_transparency"] = {
            "status": "Weak",
            "reason": "Content quality or policy clarity is insufficient."
        }
    elif content_risk == "Moderate":
        dimensions["content_transparency"] = {
            "status": "Moderate",
            "reason": "Content structure exists but lacks depth or clarity."
        }
    else:
        dimensions["content_transparency"] = {
            "status": "Strong",
            "reason": "Content metadata and policy clarity appear professional."
        }

    # 5️⃣ User Harm Exposure
    total_complaints = sum(v.get("count", 0) for v in experience.values())
    mismatch_count = len(policy_mismatches)

    if total_complaints >= 10 or mismatch_count >= 2:
        dimensions["user_harm_exposure"] = {
            "status": "Elevated",
            "reason": "Multiple recurring complaints and policy mismatches detected."
        }
    elif total_complaints >= 5:
        dimensions["user_harm_exposure"] = {
            "status": "Moderate",
            "reason": "Some recurring negative user experiences observed."
        }
    else:
        dimensions["user_harm_exposure"] = {
            "status": "Low",
            "reason": "Limited evidence of repeated user harm."
        }

    return dimensions
