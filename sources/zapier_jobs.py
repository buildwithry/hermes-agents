import re
import certifi
import requests
import feedparser
from datetime import datetime
from .filters import apply_universal_filters

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FEED_URL = "https://remoteok.com/remote-jobs.rss"

ZAPIER_KEYWORDS = ["zapier", "automation", "workflow", "ghl", "n8n", "make.com", "integromat"]


def scrape() -> list[dict]:
    jobs = []

    try:
        response = requests.get(FEED_URL, headers=HEADERS, verify=certifi.where(), timeout=10)
        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            title = entry.get("title", "")
            description = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()

            full_text = (title + " " + description).lower()
            if not any(kw in full_text for kw in ZAPIER_KEYWORDS):
                continue

            job_url = entry.get("link", "")
            if not job_url:
                continue

            try:
                posted_at = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                posted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            jobs.append({
                "title": title,
                "description": description[:1000],
                "url": job_url,
                "company": entry.get("author", "Unknown"),
                "platform": "RemoteOK",
                "budget": "Not specified",
                "posted_at": posted_at,
            })
    except Exception as e:
        print(f"[zapier_jobs] Error: {e}")

    filtered = apply_universal_filters(jobs)
    print(f"[zapier_jobs] {len(filtered)} jobs (from {len(jobs)} pre-filtered)")
    return filtered


if __name__ == "__main__":
    results = scrape()
    for j in results[:3]:
        print(f"\n{j['title']}")
        print(f"  URL: {j['url']}")
