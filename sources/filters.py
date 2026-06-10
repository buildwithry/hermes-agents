from datetime import datetime, timedelta

INTRO_VIDEO_PHRASES = [
    "intro video", "introduction video", "loom video", "video introduction",
    "record a video", "video application", "video cover letter", "selfie video",
    "send a video", "submit a video", "1-2 minute video", "1 minute video",
    "2 minute video", "short video",
]

GREEN_FLAGS = [
    "gohighlevel", "ghl", "n8n", "make", "zapier", "voice ai", "vapi",
    "retell", "elevenlabs", "crm automation", "workflow automation",
    "ai automation", "automation specialist",
]


def has_green_flag(job: dict) -> bool:
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    return any(flag in text for flag in GREEN_FLAGS)


def is_recent(posted_at: str, days: int = 2) -> bool:
    if not posted_at:
        return True
    try:
        posted = datetime.strptime(posted_at[:19], "%Y-%m-%d %H:%M:%S")
        return posted >= datetime.now() - timedelta(days=days)
    except Exception:
        return True


def requires_intro_video(job: dict) -> bool:
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    return any(phrase in text for phrase in INTRO_VIDEO_PHRASES)


def is_short_enough(job: dict, max_chars: int = 700) -> bool:
    return len(job.get("description", "")) <= max_chars


def apply_universal_filters(jobs: list[dict]) -> list[dict]:
    result = []
    for job in jobs:
        if not is_recent(job.get("posted_at", "")):
            continue
        if not is_short_enough(job):
            continue
        if requires_intro_video(job):
            continue
        if not has_green_flag(job):
            continue
        result.append(job)
    return result
