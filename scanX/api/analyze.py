# api/analyze.py

from flask import Blueprint, request, jsonify

from core.reputation import collect_public_signals
from core.live_inspector import inspect_site
from core.experience_miner import mine_experiences
from core.risk_engine import evaluate_risk
from agents.deep_explainer import explain_trust
from core.policy_analyzer import analyze_policies


analyze_api = Blueprint("analyze_api", __name__)


@analyze_api.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    domain = data.get("url", "").strip()
    category = data.get("category", "general")

    if not domain:
        return jsonify({"error": "Invalid domain"}), 400

    try:
        # 1️⃣ Google indexed OSINT
        osint = collect_public_signals(domain)

        # 2️⃣ Live site inspection
        live = inspect_site(domain)

        #policy quality checker
        policy_quality = analyze_policies(domain, live)


        # 3️⃣ Customer experience mining
        experience = mine_experiences(osint["evidence"])

        # 4️⃣ Rule-based risk evaluation
        risk = evaluate_risk(osint)

        # 5️⃣ Gemini deep explanation
        ai_result = explain_trust(
            domain=domain,
            category=category,
            osint_data=osint,
            experience_data=experience,
            live_inspection=live,
            risk_result=risk
        )

        return jsonify({
            "domain": domain,
            "category": category,
            "osint": osint,
            "live": live,
            "experience": experience,
            "risk": risk,
            "analysis": ai_result["analysis"],
            "confidence": ai_result["confidence"],
            "risk_level": ai_result["risk_level"],
            "policy_quality": policy_quality

        })

    except Exception as e:
        return jsonify({
            "error": "Scan failed",
            "details": str(e)
        }), 500
