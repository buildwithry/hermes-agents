import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "data" / "hermes.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_jobs (
                url        TEXT PRIMARY KEY,
                title      TEXT,
                platform   TEXT,
                score      INTEGER DEFAULT 0,
                first_seen TEXT,
                run_count  INTEGER DEFAULT 1
            )
        """)
        conn.commit()


def is_seen(url: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM seen_jobs WHERE url = ?", (url,)).fetchone()
        return row is not None


def mark_seen(job: dict, score: int = 0):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO seen_jobs (url, title, platform, score, first_seen, run_count)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(url) DO UPDATE SET run_count = run_count + 1
        """, (job["url"], job.get("title", ""), job.get("platform", ""), score, datetime.now().isoformat()))
        conn.commit()


def filter_new(jobs: list[dict]) -> list[dict]:
    return [j for j in jobs if not is_seen(j["url"])]


def save_scored_jobs(scored_jobs: list[dict]):
    for job in scored_jobs:
        mark_seen(job, score=job.get("score", 0))


def cleanup_old(days: int = 30):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        conn.execute("DELETE FROM seen_jobs WHERE first_seen < ?", (cutoff,))
        conn.commit()
