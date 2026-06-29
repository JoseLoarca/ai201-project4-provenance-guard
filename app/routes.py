from flask import Blueprint, jsonify, request

from app.appeals import AppealError, process_appeal
from app.pipeline import process_submission
from app.storage import fetch_log

submit_bp = Blueprint("submit", __name__)


@submit_bp.route("/submit", methods=["POST"])
def submit():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Request body must be a JSON object."}), 422

    text = body.get("text")
    creator_id = body.get("creator_id")

    if not text or not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Missing or invalid field: 'text' must be a non-empty string."}), 422

    if not creator_id or not isinstance(creator_id, str) or not creator_id.strip():
        return jsonify({"error": "Missing or invalid field: 'creator_id' must be a non-empty string."}), 422

    try:
        result = process_submission(text, creator_id)
    except Exception:
        return jsonify({"error": "The evaluation could not be completed because an error occurred."}), 422

    return jsonify(result), 200


@submit_bp.route("/appeal", methods=["POST"])
def appeal():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "The appeal could not be processed because of: request body must be a JSON object."}), 422

    content_id = body.get("content_id")
    creator_reasoning = body.get("creator_reasoning")

    if not content_id or not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "The appeal could not be processed because of: missing or invalid field 'content_id'."}), 422

    if not creator_reasoning or not isinstance(creator_reasoning, str) or not creator_reasoning.strip():
        return jsonify({"error": "The appeal could not be processed because of: missing or invalid field 'creator_reasoning'."}), 422

    try:
        process_appeal(content_id, creator_reasoning)
    except AppealError as e:
        return jsonify({"error": f"The appeal could not be processed because of: {e}"}), 422

    return jsonify({
        "content_id": content_id,
        "status": f"The appeal for the submission {content_id} was received, it is now under review.",
    }), 200


@submit_bp.route("/log", methods=["GET"])
def log():
    return jsonify(fetch_log()), 200
