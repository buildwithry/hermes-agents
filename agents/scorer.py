"""
Job scoring agent — takes a list of jobs, scores each against profile.yaml using Claude.
Called by n8n via POST /score-jobs
"""

import os
import yaml
import anthropic
from pathlib import Path

PROFILE_PATH = Path(__file__).parent.parent / "profile.yaml"

def load_profile() -> dict:
    with open(PROFILE_PATH, "r") as f:
        return yaml.safe_load(f)

def score_jobs(jobs: list[dict]) -> list[dict]:
    """Score a list of jobs against the user profile. Returns jobs with scores added."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    profile = load_profile()

    scored = []
    for job in jobs:
        result = _score_single_job(client, profile, job)
        scored.append(result)

    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored

def _score_single_job(client: anthropic.Anthropic, profile: dict, job: dict) -> dict:
    scoring_instructions = profile.get("scoring_instructions", "")
    skills_expert = ", ".join(profile["skills"]["expert"])
    skills_intermediate = ", ".join(profile["skills"]["intermediate"])
    green_flags = ", ".join(profile["preferences"]["green_flags"])
    deal_breakers = ", ".join(profile["preferences"]["deal_breakers"])
    min_rate = profile["preferences"]["minimum_rate"]

    prompt = f"""Score this job for {profile['name']} (GHL/n8n/Vapi/AI automation expert, min ${min_rate['monthly_usd']}/mo or ${min_rate['hourly_usd']}/hr).
Deal-breakers (score 0): {deal_breakers}

JOB: {job.get('title')} | {job.get('budget', 'N/A')}
{job.get('description', '')[:600]}

Reply raw JSON only:
{{"score":<1-10>,"match_reason":"<1 sentence>","apply_angle":"<1 sentence>","red_flags":"<1 sentence or none>","deal_breaker":<true/false>}}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        raw = message.content[0].text.strip()
        clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        scoring = json.loads(clean)
    except Exception:
        scoring = {
            "score": 0,
            "match_reason": "Could not parse score",
            "apply_angle": "",
            "red_flags": "parsing error",
            "deal_breaker": False
        }

    return {**job, **scoring}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sample_jobs = [
        {
            "title": "GoHighLevel Automation Specialist",
            "company": "Digital Marketing Agency",
            "platform": "Upwork",
            "description": "We need a GHL expert to build workflows, automations, and integrate n8n. Must know webhooks and API integrations. Remote, async work. No time tracker required.",
            "budget": "$1500-2500/month",
            "url": "https://upwork.com/jobs/example1"
        },
        {
            "title": "Virtual Assistant for Data Entry",
            "company": "Small Business",
            "platform": "OnlineJobs.ph",
            "description": "Looking for a VA for data entry tasks. Must use Hubstaff time tracker. $4/hour.",
            "budget": "$4/hour",
            "url": "https://onlinejobs.ph/example2"
        }
    ]

    results = score_jobs(sample_jobs)
    for job in results:
        print(f"\n{'='*50}")
        print(f"Score: {job['score']}/10 — {job['title']}")
        print(f"Match: {job['match_reason']}")
        print(f"Angle: {job['apply_angle']}")
        print(f"Flags: {job['red_flags']}")
