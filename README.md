# Hermes Agent

> An AI agent that hunts jobs for me while I sleep.

Hermes runs twice daily, scrapes 4 job boards for AI automation roles (GHL, n8n, Make, Zapier, Voice AI), scores each match against my profile using Claude Haiku, and delivers the top 10 to Telegram — one message per job.

Built as a portfolio project to demonstrate real-world autonomous agent architecture.

---

## What It Does

1. **Scrapes** OnlineJobs.ph, LinkedIn Jobs RSS, Jobicy, and RemoteOK for AI automation roles
2. **Deduplicates** using SQLite — Claude tokens are never spent on the same job twice
3. **Scores** new jobs against my skills profile (GHL, n8n, Vapi, Make, Zapier) using Claude Haiku
4. **Delivers** top 10 matches as individual Telegram messages with score, match reason, apply angle, and direct link

---

## Architecture

```
n8n (6PM PH + 1AM PH)
  → POST /run (FastAPI)
    → scraper.py orchestrates 4 sources
    → db.py filters already-seen jobs (SQLite)
    → scorer.py sends only NEW jobs to Claude Haiku
    → db.py saves scored jobs
    → notifier.py → Telegram (1 message per job + run summary)
```

**Sources:**

| Platform | Method | Search Terms |
|----------|--------|--------------|
| OnlineJobs.ph | HTML scraping | GHL, n8n, automation specialist, voice AI |
| LinkedIn Jobs | RSS feed | GoHighLevel automation, n8n specialist, Voice AI |
| Jobicy | RSS feed | make automation, GHL, workflow specialist |
| RemoteOK | RSS feed | zapier, automation, workflow, GHL |

---

## Tech Stack

- **Python** 3.11+
- **FastAPI** — webhook server n8n calls
- **Claude Haiku** — job relevance scoring (cheapest + fast)
- **SQLite** — deduplication (zero repeat Claude calls)
- **n8n** — daily scheduler (6PM + 1AM PH time)
- **Telegram Bot API** — job notifications

---

## Cost Optimization

| Version | Jobs Sent to Claude | Cost Per Run |
|---------|--------------------|----|
| v1 | All scraped jobs (126) | ~$0.19 |
| v2 | Only NEW jobs (SQLite dedup) | ~$0.01–0.03 |

Two-stage filter: green flag keyword pre-check → SQLite dedup → Claude only sees jobs it has never scored before.

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/hermes-agents.git
cd hermes-agents
python -m venv venv
venv/Scripts/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### Run

```bash
# Start the API server
python main.py

# Trigger a full run manually
curl -X POST http://localhost:8000/run

# Run a single agent for testing
python -m agents.scraper
python -m agents.scorer
python -m agents.notifier
```

### Schedule with n8n

Import `n8n/hermes_workflow.json` into your n8n instance. It triggers at 6PM and 1AM Philippines time.

---

## Profile Configuration

Edit `profile.yaml` to customize scoring for your own skills and rate requirements. Hermes reads this file on every run — no code changes needed.

---

## About

Built by **Adrian Agdan** — GHL Certified Admin & AI Automation Specialist based in the Philippines.

- Portfolio: [buildwithry.github.io/portfolio](https://buildwithry.github.io/portfolio/)
- Email: adrian@romea.ai
