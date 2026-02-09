from flask import Blueprint, request, jsonify
from urllib.parse import urlparse

from core.reputation import collect_public_signals
from core.live_inspector import inspect_site
from core.experience_miner import mine_experiences
from core.risk_engine import evaluate_risk
from core.policy_analyzer import analyze_policies
from core.policy_mismatch import detect_policy_mismatch
from core.trust_dimensions import evaluate_trust_dimensions
from agents.deep_explainer import explain_trust
from core.infra_intel import inspect_infrastructure
from core.security_posture import analyze_security_posture
from core.content_fingerprint import fingerprint_content


analyze_api = Blueprint("analyze_api", __name__)


def normalize_domain(url: str) -> str:
    if url.startswith("http"):
        return urlparse(url).netloc
    return url


@analyze_api.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    raw_domain = data.get("url", "").strip()
    category = data.get("category", "general")

    if not raw_domain:
        return jsonify({"error": "Invalid domain"}), 400

    domain = normalize_domain(raw_domain)

    try:
        # 1️⃣ OSINT collection
        osint = collect_public_signals(domain)

        # 2️⃣ Live site inspection
        live = inspect_site(domain)

        # 3️⃣ Policy quality analysis
        policy_quality = analyze_policies(domain, live)

        # 4️⃣ Experience mining
        experience = mine_experiences(osint.get("evidence", {}))

        # 5️⃣ Policy vs complaint mismatch
        policy_mismatches = detect_policy_mismatch(
            policy_quality,
            experience
        )

        # 6️⃣ Baseline risk evaluation
        risk = evaluate_risk(osint)

        # 7️⃣ AI explanation (graceful fallback)
        try:
            ai_result = explain_trust(
                domain=domain,
                category=category,
                osint_data=osint,
                experience_data=experience,
                live_inspection=live,
                risk_result=risk
            )
        except Exception as ai_error:
            ai_result = {
                "analysis": (
                    "AI-based explanation is temporarily unavailable due to API limits. "
                    "The assessment is derived from OSINT, live inspection, "
                    "policy analysis, and experience patterns."
                ),
                "risk_level": risk["baseline_risk"]["risk_level"],
                "confidence": risk["baseline_risk"]["confidence"],
                "ai_error": str(ai_error)
            }

                # 9 Domain age checker
        infra = inspect_infrastructure(domain)

        # 10 ANALYZE SECURITY POSTURE
        security = analyze_security_posture(domain)

        # 10 CONTENT FINGERPRINTING
        content_meta = fingerprint_content(domain)

        # 8️⃣ Trust Dimension Engine
        trust_dimensions = evaluate_trust_dimensions(
            osint=osint,
            experience=experience,
            live=live,
            policy_quality=policy_quality,
            policy_mismatches=policy_mismatches,
            infra=infra,
            security=security,
            content=content_meta
        )








        return jsonify({
            "domain": domain,
            "category": category,

            "risk_level": ai_result["risk_level"],
            "confidence": ai_result["confidence"],
            "analysis": ai_result["analysis"],

            "osint": osint,
            "live": live,
            "experience": experience,
            "policy_quality": policy_quality,
            "policy_mismatches": policy_mismatches,
            "risk": risk,
            "trust_dimensions": trust_dimensions,
            "infra": infra,
            "security_posture": security,
            "content_fingerprint": content_meta



        })

    except Exception as e:
        return jsonify({
            "error": "Scan failed",
            "details": str(e)
        }), 500
