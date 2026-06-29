import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.pipeline import run
from app.storage import fetch_log, insert_submission

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
        result = run(text)
    except Exception:
        return jsonify({"error": "The evaluation could not be completed because an error occurred."}), 422

    content_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    insert_submission(
        content_id=content_id,
        creator_id=creator_id,
        text=text,
        timestamp=timestamp,
        llm_ai_probability=result["llm_ai_probability"],
        llm_reasoning=result["llm_reasoning"],
        stylometrics_score=result["stylometrics_score"],
        burstiness_score=result["burstiness_score"],
        punctuation_entropy_score=result["punctuation_entropy_score"],
        confidence=result["confidence"],
        label=result["label"],
        attribution=result["attribution"],
    )

    return jsonify({
        "content_id": content_id,
        "attribution": result["attribution"],
        "confidence": result["confidence"],
        "label": result["label"],
    }), 200


@submit_bp.route("/log", methods=["GET"])
def log():
    return jsonify(fetch_log()), 200
