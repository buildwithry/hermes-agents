import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.scorer import score_jobs
from agents.scraper import scrape_all
from agents.notifier import send_digest
from db import init_db, filter_new, save_scored_jobs, cleanup_old

app = FastAPI(title="Hermes Agent", version="2.0.0")


class Job(BaseModel):
    title: str
    description: str = ""
    url: str = ""
    company: str = ""
    platform: str = ""
    budget: str = "Not specified"
    posted_at: str = ""

class ScoringRequest(BaseModel):
    jobs: list[Job]


@app.get("/")
def health():
    return {"status": "Hermes is running", "version": "2.0.0"}


@app.post("/score-jobs")
def score_jobs_endpoint(request: ScoringRequest):
    jobs_data = [job.model_dump() for job in request.jobs]
    try:
        scored = score_jobs(jobs_data)
        return {"scored_jobs": scored, "total": len(scored)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
def run_full_pipeline():
    try:
        init_db()
        cleanup_old(days=30)

        print("[hermes] Scraping all sources...")
        all_jobs = scrape_all()

        print("[hermes] Filtering to new jobs only...")
        new_jobs = filter_new(all_jobs)
        skipped = len(all_jobs) - len(new_jobs)
        print(f"[hermes] {len(new_jobs)} new jobs, {skipped} already seen (skipping Claude)")

        if new_jobs:
            print(f"[hermes] Scoring {len(new_jobs)} new jobs with Claude Haiku...")
            scored = score_jobs(new_jobs)
            save_scored_jobs(scored)
        else:
            scored = []

        matches = [j for j in scored if j.get("score", 0) >= 6 and not j.get("deal_breaker")]
        cost_usd = len(new_jobs) * 0.00084  # ~$0.00084 per job (haiku pricing)

        hour = datetime.now().hour
        next_run = "6PM" if hour < 13 else "1AM"

        run_stats = {
            "total_scraped": len(all_jobs),
            "new_jobs": len(new_jobs),
            "matches": len(matches),
            "cost_usd": round(cost_usd, 4),
            "next_run": next_run,
        }

        print(f"[hermes] {len(matches)} matches. Sending Telegram digest...")
        try:
            send_digest(scored, run_stats=run_stats)
        except Exception as e:
            print(f"[hermes] Telegram notification failed: {e}")

        return {"status": "done", **run_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
