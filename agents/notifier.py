"""
Telegram notifier — sends scored job digest to your Telegram bot.
"""

import os
import certifi
import requests

def send_digest(scored_jobs: list[dict], top_n: int = 5) -> bool:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    top_jobs = [j for j in scored_jobs if not j.get("deal_breaker", False)][:top_n]

    if not top_jobs:
        message = "🤖 *Hermes Daily Digest*\n\nNo strong matches found today. Check back tomorrow."
    else:
        lines = ["🤖 *Hermes Daily Job Digest*\n"]
        for i, job in enumerate(top_jobs, 1):
            score = job.get("score", 0)
            emoji = "🔥" if score >= 8 else "✅" if score >= 6 else "📋"
            lines.append(
                f"{emoji} *{i}. {job['title']}*\n"
                f"📍 {job['platform']} | 💰 {job.get('budget', 'N/A')}\n"
                f"⭐ Score: {score}/10\n"
                f"💡 {job.get('match_reason', '')}\n"
                f"🎯 Angle: {job.get('apply_angle', '')}\n"
                f"🔗 [Apply Here]({job.get('url', '')})\n"
            )
        message = "\n".join(lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    response = requests.post(url, json=payload, verify=certifi.where())
    success = response.status_code == 200
    if not success:
        print(f"[notifier] Telegram error: {response.text}")
    return success


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sample = [
        {
            "title": "GHL Automation Specialist",
            "platform": "Upwork",
            "budget": "$2000/month",
            "score": 9,
            "match_reason": "Exact match — needs GHL, n8n, and webhook integrations.",
            "apply_angle": "Highlight your GHL Certified Admin credential and Romea.AI experience.",
            "url": "https://upwork.com/jobs/example",
            "deal_breaker": False,
        }
    ]
    send_digest(sample)
    print("[notifier] Test message sent — check your Telegram!")
