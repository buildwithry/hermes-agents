import certifi
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .filters import apply_universal_filters

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SEARCH_TERMS = [
    "gohighlevel",
    "n8n",
    "automation specialist",
    "voice ai",
    "ghl admin",
]


def scrape() -> list[dict]:
    jobs = []
    seen_urls = set()

    for term in SEARCH_TERMS:
        query = term.replace(" ", "+")
        url = f"https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword={query}&jobtype=1"
        try:
            response = requests.get(url, headers=HEADERS, verify=certifi.where(), timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for card in soup.select(".jobpost-cat-box"):
                title_el = card.select_one("h4")
                if not title_el:
                    continue

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
                posted_at = posted_el.get("data-temp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if posted_el else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            print(f"[onlinejobs] Error for '{term}': {e}")

    filtered = apply_universal_filters(jobs)
    print(f"[onlinejobs] {len(filtered)} jobs (from {len(jobs)} scraped)")
    return filtered


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    results = scrape()
    for j in results[:3]:
        print(f"\n{j['title']}")
        print(f"  Budget: {j['budget']}")
        print(f"  URL: {j['url']}")
