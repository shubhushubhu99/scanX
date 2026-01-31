from flask import Blueprint, request, jsonify
from agents.dimension_explainer import explain_dimension

dimension_api = Blueprint("dimension_api", __name__)

@dimension_api.route("/explain-dimension", methods=["POST"])
def explain_trust_dimension():
    data = request.get_json() or {}

    dimension = data.get("dimension")
    status = data.get("status")
    signals = data.get("signals")

    if not dimension or not status:
        return jsonify({"error": "Invalid request"}), 400

    explanation = explain_dimension(
        dimension=dimension,
        status=status,
        signals=signals
    )

    return jsonify({
        "dimension": dimension,
        "status": status,
        "explanation": explanation
    })
