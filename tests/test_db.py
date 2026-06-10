import pytest
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import db


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test_hermes.db")
    db.init_db()
    yield


def test_init_creates_seen_jobs_table():
    conn = db.get_conn()
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='seen_jobs'"
    ).fetchone()
    conn.close()
    assert row is not None


def test_is_seen_false_for_new_url():
    assert db.is_seen("https://example.com/job/1") is False


def test_is_seen_true_after_mark_seen():
    job = {"url": "https://example.com/job/1", "title": "GHL Job", "platform": "Test"}
    db.mark_seen(job, score=7)
    assert db.is_seen("https://example.com/job/1") is True


def test_filter_new_removes_seen_jobs():
    seen = {"url": "https://example.com/job/1", "title": "Old", "platform": "Test"}
    new = {"url": "https://example.com/job/2", "title": "New", "platform": "Test"}
    db.mark_seen(seen)
    result = db.filter_new([seen, new])
    assert len(result) == 1
    assert result[0]["url"] == "https://example.com/job/2"


def test_save_scored_jobs_marks_all_seen():
    jobs = [
        {"url": "https://example.com/job/3", "title": "GHL", "platform": "Test", "score": 8},
        {"url": "https://example.com/job/4", "title": "n8n", "platform": "Test", "score": 6},
    ]
    db.save_scored_jobs(jobs)
    assert db.is_seen("https://example.com/job/3") is True
    assert db.is_seen("https://example.com/job/4") is True


def test_mark_seen_increments_run_count_on_duplicate():
    job = {"url": "https://example.com/job/5", "title": "Test", "platform": "Test"}
    db.mark_seen(job)
    db.mark_seen(job)
    conn = db.get_conn()
    row = conn.execute("SELECT run_count FROM seen_jobs WHERE url = ?", (job["url"],)).fetchone()
    conn.close()
    assert row["run_count"] == 2


def test_cleanup_old_removes_expired_jobs():
    conn = db.get_conn()
    old_date = (datetime.now() - timedelta(days=35)).isoformat()
    conn.execute(
        "INSERT INTO seen_jobs (url, title, platform, score, first_seen) VALUES (?,?,?,?,?)",
        ("https://example.com/old/1", "Old Job", "Test", 0, old_date),
    )
    conn.commit()
    conn.close()
    db.cleanup_old(days=30)
    assert db.is_seen("https://example.com/old/1") is False


def test_cleanup_old_keeps_recent_jobs():
    conn = db.get_conn()
    recent_date = (datetime.now() - timedelta(days=10)).isoformat()
    conn.execute(
        "INSERT INTO seen_jobs (url, title, platform, score, first_seen) VALUES (?,?,?,?,?)",
        ("https://example.com/recent/1", "Recent Job", "Test", 5, recent_date),
    )
    conn.commit()
    conn.close()
    db.cleanup_old(days=30)
    assert db.is_seen("https://example.com/recent/1") is True
