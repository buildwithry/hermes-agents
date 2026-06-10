from sources.onlinejobs import scrape as scrape_onlinejobs
from sources.linkedin import scrape as scrape_linkedin
from sources.make_jobs import scrape as scrape_make
from sources.zapier_jobs import scrape as scrape_zapier


def scrape_all() -> list[dict]:
    all_jobs = []
    seen_urls = set()

    for scrape_fn in [scrape_onlinejobs, scrape_linkedin, scrape_make, scrape_zapier]:
        try:
            jobs = scrape_fn()
            for job in jobs:
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)
        except Exception as e:
            print(f"[scraper] Source error: {e}")

    print(f"[scraper] Total: {len(all_jobs)} unique jobs across all platforms")
    return all_jobs


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    jobs = scrape_all()
    for j in jobs[:5]:
        print(f"\n{j['platform']} | {j['title']}")
        print(f"  Budget: {j['budget']}")
        print(f"  URL: {j['url']}")
