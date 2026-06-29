import sqlite3
from datetime import datetime
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
                content_id              TEXT PRIMARY KEY,
                creator_id              TEXT NOT NULL,
                timestamp               TEXT NOT NULL,
                status                  TEXT NOT NULL DEFAULT 'classified',
                llm_ai_probability      REAL,
                llm_reasoning           TEXT,
                stylometrics_score      REAL,
                burstiness_score        REAL,
                punctuation_entropy_score REAL,
                confidence              REAL,
                label                   TEXT,
                attribution             TEXT
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


def _format_timestamp(raw: str | None) -> str | None:
    if raw is None:
        return None
    try:
        return datetime.strptime(raw, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return raw


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
                s.stylometrics_score,
                s.burstiness_score,
                s.punctuation_entropy_score,
                s.confidence,
                s.label,
                s.attribution,
                a.creator_reasoning,
                a.timestamp AS appeal_timestamp
            FROM submissions s
            LEFT JOIN appeals a ON s.content_id = a.content_id
            ORDER BY s.timestamp DESC
            """
        ).fetchall()

        records = []
        for row in rows:
            record = dict(row)
            record["timestamp"] = _format_timestamp(record["timestamp"])
            record["appeal_timestamp"] = _format_timestamp(record["appeal_timestamp"])
            records.append(record)
        return records


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
    stylometrics_score: float,
    burstiness_score: float,
    punctuation_entropy_score: float,
    confidence: float,
    label: str,
    attribution: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO submissions (
                content_id, creator_id, timestamp, status,
                llm_ai_probability, llm_reasoning,
                stylometrics_score, burstiness_score, punctuation_entropy_score,
                confidence, label, attribution
            )
            VALUES (?, ?, ?, 'classified', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content_id, creator_id, timestamp,
                llm_ai_probability, llm_reasoning,
                stylometrics_score, burstiness_score, punctuation_entropy_score,
                confidence, label, attribution,
            ),
        )
        conn.execute(
            "INSERT INTO submission_content (content_id, text) VALUES (?, ?)",
            (content_id, text),
        )
        conn.commit()
