import sqlite3
from pathlib import Path

_DB_PATH = Path("provenance_guard.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                content_id          TEXT PRIMARY KEY,
                creator_id          TEXT NOT NULL,
                text                TEXT NOT NULL,
                timestamp           TEXT NOT NULL,
                status              TEXT NOT NULL DEFAULT 'classified',
                llm_ai_probability  REAL,
                llm_reasoning       TEXT
            )
        """)
        # Migrate existing databases that predate these columns
        for column, definition in [
            ("llm_ai_probability", "REAL"),
            ("llm_reasoning", "TEXT"),
        ]:
            try:
                conn.execute(f"ALTER TABLE submissions ADD COLUMN {column} {definition}")
            except sqlite3.OperationalError:
                pass  # Column already exists
        conn.commit()


def insert_submission(
    content_id: str,
    creator_id: str,
    text: str,
    timestamp: str,
    llm_ai_probability: float,
    llm_reasoning: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO submissions
                (content_id, creator_id, text, timestamp, status, llm_ai_probability, llm_reasoning)
            VALUES (?, ?, ?, ?, 'classified', ?, ?)
            """,
            (content_id, creator_id, text, timestamp, llm_ai_probability, llm_reasoning),
        )
        conn.commit()
