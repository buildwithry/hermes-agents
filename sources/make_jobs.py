import re
import certifi
import requests
import feedparser
from datetime import datetime
from .filters import apply_universal_filters

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FEED_URLS = [
    "https://jobicy.com/?feed=job_feed&search_keywords=make+automation+n8n",
    "https://jobicy.com/?feed=job_feed&search_keywords=ghl+automation",
    "https://jobicy.com/?feed=job_feed&search_keywords=workflow+automation+specialist",
]


def scrape() -> list[dict]:
    jobs = []
    seen_urls = set()

    for url in FEED_URLS:
        try:
            response = requests.get(url, headers=HEADERS, verify=certifi.where(), timeout=10)
            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                job_url = entry.get("link", "")
                if not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                try:
                    posted_at = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    posted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                description = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()

                jobs.append({
                    "title": entry.get("title", ""),
                    "description": description[:1000],
                    "url": job_url,
                    "company": entry.get("author", "Unknown"),
                    "platform": "Jobicy",
                    "budget": "Not specified",
                    "posted_at": posted_at,
                })
        except Exception as e:
            print(f"[make_jobs] Error for '{url}': {e}")

    filtered = apply_universal_filters(jobs)
    print(f"[make_jobs] {len(filtered)} jobs (from {len(jobs)} scraped)")
    return filtered


if __name__ == "__main__":
    results = scrape()
    for j in results[:3]:
        print(f"\n{j['title']}")
        print(f"  URL: {j['url']}")
