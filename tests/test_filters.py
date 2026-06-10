from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sources.filters import (
    has_green_flag, is_recent, requires_intro_video,
    is_short_enough, apply_universal_filters,
)


def _job(title="", description="", posted_at=None):
    if posted_at is None:
        posted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"title": title, "description": description, "posted_at": posted_at, "url": "https://example.com"}


# --- has_green_flag ---

def test_has_green_flag_ghl_in_title():
    assert has_green_flag(_job(title="GHL Automation Specialist")) is True

def test_has_green_flag_gohighlevel_in_description():
    assert has_green_flag(_job(description="Need someone with gohighlevel experience")) is True

def test_has_green_flag_n8n():
    assert has_green_flag(_job(title="n8n Workflow Developer")) is True

def test_has_green_flag_false():
    assert has_green_flag(_job(title="Data Entry Clerk", description="Spreadsheet work only")) is False


# --- is_recent ---

def test_is_recent_now():
    posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    assert is_recent(posted) is True

def test_is_recent_1_day_ago():
    posted = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert is_recent(posted) is True

def test_is_recent_3_days_ago():
    posted = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    assert is_recent(posted) is False

def test_is_recent_empty_defaults_true():
    assert is_recent("") is True


# --- requires_intro_video ---

def test_requires_intro_video_loom():
    assert requires_intro_video(_job(description="Please send a loom video with your application")) is True

def test_requires_intro_video_intro_video():
    assert requires_intro_video(_job(description="Send an intro video")) is True

def test_requires_intro_video_false():
    assert requires_intro_video(_job(description="Send your resume and portfolio link")) is False


# --- is_short_enough ---

def test_is_short_enough_under():
    assert is_short_enough(_job(description="x" * 699)) is True

def test_is_short_enough_exactly_700():
    assert is_short_enough(_job(description="x" * 700)) is True

def test_is_short_enough_over():
    assert is_short_enough(_job(description="x" * 701)) is False


# --- apply_universal_filters ---

def test_filters_out_old_job():
    old = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    jobs = [_job(title="GHL Specialist", posted_at=old)]
    assert apply_universal_filters(jobs) == []

def test_filters_out_intro_video():
    jobs = [_job(title="GHL Specialist", description="Please send a short video introduction")]
    assert apply_universal_filters(jobs) == []

def test_filters_out_long_post():
    jobs = [_job(title="GHL Specialist", description="x" * 701)]
    assert apply_universal_filters(jobs) == []

def test_filters_out_no_green_flag():
    jobs = [_job(title="Data Entry Clerk", description="Spreadsheet work")]
    assert apply_universal_filters(jobs) == []

def test_keeps_valid_job():
    jobs = [_job(title="GHL Automation Specialist", description="Need GHL expert for CRM workflows")]
    result = apply_universal_filters(jobs)
    assert len(result) == 1
    assert result[0]["title"] == "GHL Automation Specialist"
