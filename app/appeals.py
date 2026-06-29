from datetime import datetime, UTC

from app.storage import get_submission, insert_appeal


class AppealError(Exception):
    pass


def process_appeal(content_id: str, creator_reasoning: str) -> None:
    """
    Validates and processes an appeal for a submission.
    Raises AppealError with a descriptive message if the appeal cannot be processed.
    """
    submission = get_submission(content_id)

    if submission is None:
        raise AppealError(f"no submission found with id '{content_id}'.")

    if submission["status"] == "under_review":
        raise AppealError(f"an appeal for '{content_id}' is already under review.")

    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    insert_appeal(content_id, creator_reasoning, timestamp)
