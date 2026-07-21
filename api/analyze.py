from flask import Blueprint, request, jsonify
from urllib.parse import urlparse

from utils.validators import validate_domain
from tasks.analyze_tasks import analyze_domain_task
from celery_app import celery

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
    domain = validate_domain(domain)

    if not domain:
        return jsonify({"error": "Invalid or disallowed domain"}), 400

    try:
        # Enqueue the background task
        task = analyze_domain_task.delay(domain, category)
        return jsonify({"task_id": task.id, "status": "processing"}), 202
    except Exception as e:
        return jsonify({
            "error": "Failed to start scan task",
            "details": str(e)
        }), 500

@analyze_api.route("/analyze/status/<task_id>", methods=["GET"])
def analyze_status(task_id):
    task = analyze_domain_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'processing'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.info
        }
        # If there's an error dict returned by the task itself (handled exception)
        if isinstance(task.info, dict) and "error" in task.info:
            response['state'] = 'FAILURE'
    else:
        # Something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info)  # this is the exception raised
        }
    return jsonify(response)
