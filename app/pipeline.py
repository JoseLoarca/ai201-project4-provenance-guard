import uuid
from datetime import UTC, datetime

from app.llm_classifier import classify_text
from app.logger import get_session_logger
from app.storage import insert_submission
from app.stylometrics import analyze

logger = get_session_logger()


def compute_final_score(llm_score: float, stylometrics_score: float) -> float:
    """
    Computes the final confidence score from the two signal scores.

    Weighted average: 65% LLM, 35% stylometrics.
    Divergence check: if abs(llm_score - stylometrics_score) > 0.4, the signals
    contradict each other and the final score is forced to 0.5 (uncertain).
    """
    logger.debug("Computing final score.")
    divergence = abs(llm_score - stylometrics_score)
    if divergence > 0.4:
        logger.debug(f"Final score forced to 0.5, divergence: {divergence}.")
        return 0.5
    return round(0.65 * llm_score + 0.35 * stylometrics_score, 4)


def get_label(final_score: float) -> str:
    """
    Maps the final confidence score to a label. Symmetric around 0.5.

      >= 0.90  →  clearly AI
      >= 0.70  →  likely AI
      >= 0.30  →  uncertain
      >= 0.10  →  likely human
      <  0.10  →  clearly human
    """
    if final_score >= 0.90:
        return "clearly AI"
    if final_score >= 0.70:
        return "likely AI"
    if final_score >= 0.30:
        return "uncertain"
    if final_score >= 0.10:
        return "likely human"
    return "clearly human"


def get_attribution(label: str, final_score: float) -> str:
    """
    Produces the human-readable attribution string shown to the user.
    Confidence percentage reflects certainty in the label, not the raw AI score:
      - AI labels: confidence = final_score * 100
      - Human labels: confidence = (1 - final_score) * 100
    """
    confidence_pct = round(final_score * 100) if final_score > 0.5 else round((1 - final_score) * 100)

    if label == "clearly AI":
        return f"This content was assessed as AI-generated ({confidence_pct}% confidence)."
    if label == "likely AI":
        return f"This content was likely AI-generated ({confidence_pct}% confidence)."
    if label == "likely human":
        return f"This content was likely human-written ({confidence_pct}% confidence)."
    if label == "clearly human":
        return f"This content was assessed as human-written ({confidence_pct}% confidence)."
    return f"This content could not be confidently attributed. Attribution is uncertain."


def process_submission(text: str, creator_id: str) -> dict:
    """
    Runs the detection pipeline, persists the submission, and returns
    the fields the route needs to build the API response.
    """
    result = run(text)
    content_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

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

    return {
        "content_id": content_id,
        "attribution": result["attribution"],
        "confidence": result["confidence"],
        "label": result["label"],
    }


def run(text: str) -> dict:
    """
    Orchestrates the full multi-signal detection pipeline.
    Returns all fields needed for the API response and audit log.
    """
    logger.debug("Running pipeline on new submission.")
    llm_result = classify_text(text)
    stylometrics_result = analyze(text)

    llm_score = llm_result["ai_probability"]
    stylometrics_score = stylometrics_result["stylometrics_score"]

    final_score = compute_final_score(llm_score, stylometrics_score)
    label = get_label(final_score)
    attribution = get_attribution(label, final_score)
    logger.debug("Pipeline execution completed.")

    return {
        "llm_ai_probability": llm_score,
        "llm_reasoning": llm_result["reasoning"],
        "stylometrics_score": stylometrics_score,
        "burstiness_score": stylometrics_result["burstiness_score"],
        "punctuation_entropy_score": stylometrics_result["punctuation_entropy_score"],
        "confidence": final_score,
        "label": label,
        "attribution": attribution,
    }
