"""
Job scraper agent — fetches jobs from Upwork RSS, OnlineJobs.ph, JobStreet.
Returns normalized list of job dicts.
"""

import certifi
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

INTRO_VIDEO_PHRASES = [
    "intro video", "introduction video", "loom video", "video introduction",
    "record a video", "video application", "video cover letter", "selfie video",
    "send a video", "submit a video", "1-2 minute video", "1 minute video",
    "2 minute video", "short video",
]

ONLINEJOBS_TERMS = [
    "gohighlevel",
    "n8n",
    "automation specialist",
    "voice ai",
    "ghl admin",
]

GREEN_FLAGS = [
    "gohighlevel", "ghl", "n8n", "make", "zapier", "voice ai", "vapi",
    "retell", "elevenlabs", "crm automation", "workflow automation",
    "ai automation", "automation specialist",
]

def scrape_all() -> list[dict]:
    jobs = []
    jobs.extend(scrape_onlinejobs())

    # Pre-filter: only keep jobs with at least one green flag keyword
    before = len(jobs)
    jobs = [j for j in jobs if _has_green_flag(j)]
    print(f"[scraper] Pre-filter: {before} -> {len(jobs)} relevant jobs")
    return jobs

def _has_green_flag(job: dict) -> bool:
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    return any(flag in text for flag in GREEN_FLAGS)

def scrape_onlinejobs() -> list[dict]:
    jobs = []
    seen_urls = set()

    for term in ONLINEJOBS_TERMS:
        query = term.replace(" ", "+")
        url = f"https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword={query}&jobtype=1"
        try:
            response = requests.get(url, headers=HEADERS, verify=certifi.where(), timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for card in soup.select(".jobpost-cat-box"):
                title_el = card.select_one("h4")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                # Remove badge text (Full Time / Part Time) from title
                for badge in title_el.select(".badge"):
                    badge.decompose()
                title = title_el.get_text(strip=True)

                link_el = card.select_one("a[href*='/jobseekers/job/']")
                if not link_el:
                    continue
                job_url = f"https://www.onlinejobs.ph{link_el['href']}"

                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                desc_el = card.select_one(".desc")
                description = desc_el.get_text(separator=" ", strip=True) if desc_el else ""

                salary_el = card.select_one("dd")
                budget = salary_el.get_text(strip=True) if salary_el else "Not specified"

                posted_el = card.select_one("p[data-temp]")
                posted_at = posted_el.get("data-temp", str(datetime.now())) if posted_el else str(datetime.now())

                # Filter: posted within last 2 days
                if not _is_recent(posted_at, days=2):
                    continue

                # Filter: skip long job posts (over 700 chars)
                if len(description) > 700:
                    continue

                # Filter: skip jobs requiring intro video
                full_text = (title + " " + description).lower()
                if any(phrase in full_text for phrase in INTRO_VIDEO_PHRASES):
                    print(f"[scraper] Skipped (intro video required): {title}")
                    continue

                jobs.append({
                    "title": title,
                    "description": description[:1000],
                    "url": job_url,
                    "company": "OnlineJobs.ph Employer",
                    "platform": "OnlineJobs.ph",
                    "budget": budget,
                    "posted_at": posted_at,
                })
        except Exception as e:
            print(f"[scraper] OnlineJobs error for '{term}': {e}")

    print(f"[scraper] OnlineJobs.ph: {len(jobs)} jobs")
    return jobs

def _is_recent(posted_at: str, days: int = 2) -> bool:
    try:
        posted = datetime.strptime(posted_at[:19], "%Y-%m-%d %H:%M:%S")
        cutoff = datetime.now() - timedelta(days=days)
        return posted >= cutoff
    except Exception:
        return True


if __name__ == "__main__":
    jobs = scrape_all()
    for j in jobs[:3]:
        print(f"\n{j['platform']} | {j['title']}")
        print(f"  URL: {j['url']}")
        print(f"  Budget: {j['budget']}")
