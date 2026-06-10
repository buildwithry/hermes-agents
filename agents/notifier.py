import os
import time
import certifi
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_digest(scored_jobs: list[dict], run_stats: dict = None) -> bool:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    top_jobs = [
        j for j in scored_jobs
        if not j.get("deal_breaker", False) and j.get("score", 0) >= 6
    ][:10]

    all_success = True

    if not top_jobs:
        _send_message(token, chat_id, "🤖 <b>Hermes Run Complete</b>\n\nNo strong matches this run. Check back next time.")
    else:
        for i, job in enumerate(top_jobs):
            success = _send_message(token, chat_id, _format_job(job))
            if not success:
                all_success = False
            if i < len(top_jobs) - 1:
                time.sleep(0.5)

    if run_stats:
        _send_message(token, chat_id, _format_summary(run_stats))

    return all_success


def _format_job(job: dict) -> str:
    score = job.get("score", 0)
    emoji = "🔥" if score >= 8 else "✅"
    rate = job.get("budget", "Not specified")
    red_flags = job.get("red_flags", "")
    flags_line = f"⚠️ {red_flags}\n" if red_flags and red_flags.lower() not in ("none", "") else ""

    return (
        f"{emoji} <b>{job['title']}</b>\n"
        f"📍 {job['platform']} | 💰 {rate}\n"
        f"⭐ Score: {score}/10\n"
        f"💡 {job.get('match_reason', '')}\n"
        f"🎯 {job.get('apply_angle', '')}\n"
        f"{flags_line}"
        f"🔗 <a href=\"{job.get('url', '')}\">Apply</a>"
    )


def _format_summary(stats: dict) -> str:
    return (
        f"🤖 <b>Hermes Run Complete</b>\n"
        f"📊 Scraped: {stats.get('total_scraped', 0)} | "
        f"🆕 New: {stats.get('new_jobs', 0)} | "
        f"✅ Matches (6+): {stats.get('matches', 0)}\n"
        f"💰 Est. cost: ~${stats.get('cost_usd', 0.0):.3f} | "
        f"🕐 Next run: {stats.get('next_run', '?')}"
    )


def _send_message(token: str, chat_id: str, text: str) -> bool:
    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        response = requests.post(url, json=payload, verify=certifi.where(), timeout=10)
        success = response.status_code == 200
        if not success:
            print(f"[notifier] Telegram error: {response.text}")
        return success
    except Exception as e:
        print(f"[notifier] Request failed: {e}")
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sample_jobs = [
        {
            "title": "GHL Automation Specialist",
            "platform": "OnlineJobs.ph",
            "budget": "$2,500/month",
            "score": 9,
            "match_reason": "Exact match — GHL + n8n + webhook integrations.",
            "apply_angle": "Lead with GHL Certified Admin + Romea.AI experience.",
            "red_flags": "none",
            "url": "https://www.onlinejobs.ph/jobseekers/job/example",
            "deal_breaker": False,
        },
        {
            "title": "n8n Workflow Developer",
            "platform": "LinkedIn",
            "budget": "$15/hour",
            "score": 7,
            "match_reason": "Strong n8n match, remote async work.",
            "apply_angle": "Highlight n8n workflows built for Romea.AI clients.",
            "red_flags": "none",
            "url": "https://linkedin.com/jobs/view/example",
            "deal_breaker": False,
        },
    ]
    sample_stats = {
        "total_scraped": 89,
        "new_jobs": 23,
        "matches": 2,
        "cost_usd": 0.019,
        "next_run": "1AM",
    }
    send_digest(sample_jobs, run_stats=sample_stats)
    print("[notifier] Test messages sent — check your Telegram!")
