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
                timestamp           TEXT NOT NULL,
                status              TEXT NOT NULL DEFAULT 'classified',
                llm_ai_probability  REAL,
                llm_reasoning       TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submission_content (
                content_id  TEXT PRIMARY KEY,
                text        TEXT NOT NULL,
                FOREIGN KEY (content_id) REFERENCES submissions (content_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appeals (
                content_id          TEXT PRIMARY KEY,
                creator_reasoning   TEXT NOT NULL,
                timestamp           TEXT NOT NULL,
                FOREIGN KEY (content_id) REFERENCES submissions (content_id)
            )
        """)
        conn.commit()


def insert_appeal(content_id: str, creator_reasoning: str, timestamp: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO appeals (content_id, creator_reasoning, timestamp)
            VALUES (?, ?, ?)
            """,
            (content_id, creator_reasoning, timestamp),
        )
        conn.execute(
            "UPDATE submissions SET status = 'under_review' WHERE content_id = ?",
            (content_id,),
        )
        conn.commit()


def fetch_log() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.content_id,
                s.creator_id,
                s.timestamp,
                s.status,
                s.llm_ai_probability,
                s.llm_reasoning,
                a.creator_reasoning
            FROM submissions s
            LEFT JOIN appeals a ON s.content_id = a.content_id
            ORDER BY s.timestamp DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_submission(content_id: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM submissions WHERE content_id = ?",
            (content_id,),
        ).fetchone()


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
                (content_id, creator_id, timestamp, status, llm_ai_probability, llm_reasoning)
            VALUES (?, ?, ?, 'classified', ?, ?)
            """,
            (content_id, creator_id, timestamp, llm_ai_probability, llm_reasoning),
        )
        conn.execute(
            "INSERT INTO submission_content (content_id, text) VALUES (?, ?)",
            (content_id, text),
        )
        conn.commit()
