"""
Hermes Agent — FastAPI webhook server.
n8n calls POST /score-jobs with a list of jobs.
Returns scored jobs. Can also trigger the full pipeline via POST /run.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.scorer import score_jobs
from agents.scraper import scrape_all
from agents.notifier import send_digest

app = FastAPI(title="Hermes Agent", version="1.0.0")


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
    return {"status": "Hermes is running", "version": "1.0.0"}


@app.post("/score-jobs")
def score_jobs_endpoint(request: ScoringRequest):
    """n8n sends jobs here → Claude scores them → returns ranked list."""
    jobs_data = [job.model_dump() for job in request.jobs]
    try:
        scored = score_jobs(jobs_data)
        return {"scored_jobs": scored, "total": len(scored)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
def run_full_pipeline():
    """Trigger the full pipeline: scrape → score → send Telegram digest."""
    try:
        print("[hermes] Scraping jobs...")
        jobs = scrape_all()

        print(f"[hermes] Scoring {len(jobs)} jobs...")
        scored = score_jobs(jobs)

        top = [j for j in scored if j.get("score", 0) >= 6]
        print(f"[hermes] {len(top)} strong matches found. Sending digest...")

        send_digest(scored)
        return {
            "status": "done",
            "total_scraped": len(jobs),
            "strong_matches": len(top),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
