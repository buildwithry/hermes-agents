# Hermes Agent v2 — Design Spec
**Date:** 2026-06-11
**Status:** Approved

---

## Overview

Hermes is an autonomous job-hunt agent for Adrian Agdan — a GHL Certified Admin and AI Automation Specialist based in the Philippines. It scrapes job boards twice daily, scores matches against his profile using Claude Haiku, deduplicates using SQLite so Claude tokens are never wasted on repeat jobs, and delivers the top 10 matches to Telegram — one message per job.

**Target audience:** AI automation agencies using GHL, n8n, Make, Zapier, and Voice AI.

---

## Architecture

```
n8n (6PM PH / 1AM PH daily)
  → POST http://localhost:8000/run
    → scraper.py orchestrates all 4 sources
    → db.py filters already-seen jobs (SQLite)
    → scorer.py sends only NEW jobs to Claude Haiku
    → db.py saves scored jobs with URL as primary key
    → notifier.py sends top 10 matches, 1 message per job → Telegram
    → notifier.py sends 1 run summary message
```

---

## File Structure

```
hermes-agents/
├── agents/
│   ├── scraper.py          ← thin orchestrator, calls all sources
│   ├── scorer.py           ← Claude Haiku scoring
│   └── notifier.py         ← 1 message per job + run summary
├── sources/                ← one file per job platform
│   ├── __init__.py
│   ├── onlinejobs.py       ← OnlineJobs.ph HTML scraping
│   ├── linkedin.py         ← LinkedIn Jobs RSS feed
│   ├── make_jobs.py        ← Make.com jobs board scraping
│   └── zapier_jobs.py      ← Zapier jobs board scraping
├── db.py                   ← SQLite — deduplication + job history
├── main.py                 ← FastAPI server (/run, /score-jobs)
├── profile.yaml            ← Adrian's skills, rates, deal-breakers
├── .env                    ← API keys (never committed)
├── .env.example            ← Template
├── .gitignore              ← excludes .env, venv/, data/
├── requirements.txt
├── n8n/
│   └── hermes_workflow.json ← 6PM + 1AM PH schedule
└── docs/
    └── superpowers/specs/
        └── 2026-06-11-hermes-v2-design.md
```

---

## Job Sources

Each source implements a single `scrape() -> list[dict]` function.

| Source | File | Method | Key Search Terms |
|--------|------|--------|-----------------|
| OnlineJobs.ph | `sources/onlinejobs.py` | HTML scraping | gohighlevel, ghl, n8n, vapi, automation |
| LinkedIn Jobs | `sources/linkedin.py` | RSS feed | GHL, GoHighLevel, n8n automation, voice AI |
| Make.com Jobs | `sources/make_jobs.py` | HTML scraping | automation specialist, make.com, n8n, GHL |
| Zapier Jobs | `sources/zapier_jobs.py` | HTML scraping | automation, zapier, workflow, GHL |

**Universal filters applied in every source:**
- Posted within last 2 days
- Description under 700 characters
- No intro video required
- Must contain at least 1 green flag keyword

**Green flag keywords:**
`gohighlevel, ghl, n8n, make, zapier, voice ai, vapi, retell, elevenlabs, crm automation, workflow automation, ai automation, automation specialist`

**Deal-breakers (auto score 0):**
- Time tracker required (Hubstaff, TimeDoctor, Clockify)
- Intro video required
- Micromanagement / screenshots required

---

## Database Schema (SQLite)

**File:** `db.py` | **Database:** `data/hermes.db`

```sql
CREATE TABLE seen_jobs (
    url        TEXT PRIMARY KEY,
    title      TEXT,
    platform   TEXT,
    score      INTEGER,
    first_seen TEXT,
    run_count  INTEGER DEFAULT 1
);
```

**Rules:**
- Before scoring: check URL against `seen_jobs` — if found, skip Claude entirely
- After scoring: insert new jobs into `seen_jobs`
- Auto-delete jobs older than 30 days to keep DB lean

---

## Scoring

- **Model:** `claude-haiku-4-5-20251001` (cheapest, fast)
- **Only new jobs** (not in SQLite) are sent to Claude
- **Max tokens:** 150 per job
- **Output:** JSON with score (1-10), match_reason, apply_angle, red_flags, deal_breaker

**Estimated cost per run:** ~$0.01-0.03 (only new jobs scored)

---

## Notifications

**Per job message (top 10, ordered by score):**
```
🔥 GHL Automation Specialist
📍 LinkedIn | 💰 $2,500/month
⭐ Score: 9/10
💡 Perfect match — GHL + n8n + webhook integrations
🎯 Angle: Lead with GHL Certified Admin + Romea.AI experience
🔗 Apply → https://linkedin.com/jobs/...
```

Rate display rules:
- Show monthly rate if available
- Show hourly rate if available
- Show both if both are listed
- Show "Not specified" only if neither is found

**Run summary message (sent last):**
```
🤖 Hermes Run Complete
📊 Scraped: 89 jobs | 🆕 New: 23 | ✅ Matches (6+): 10
💰 Claude cost: ~$0.02 | 🕐 Next run: 1AM
```

---

## Schedule

| Run | PH Time | Why |
|-----|---------|-----|
| Evening | 6:00 PM | Start of your evening, catch same-day PH posts |
| Early morning | 1:00 AM | US agencies post during their workday (US Eastern 1PM = PH 1AM) |

---

## Git Setup

- Initialize git repo in `d:/Projects/Hermes Agents`
- `.gitignore` excludes: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `data/`, `test_claude.py`
- Initial commit includes all source files, profile.yaml, .env.example, docs/
- Push to GitHub for portfolio visibility

---

## Portfolio README Goals

- **Headline:** "AI agent that hunts jobs for me while I sleep"
- **Target reader:** Hiring manager at GHL/n8n AI automation agency
- **Must include:** Architecture diagram, Telegram screenshot, cost breakdown ($0.19 → $0.03)
- **Tech stack badge:** Python · FastAPI · Claude API · n8n · SQLite · Telegram

---

## Success Criteria

- [ ] 4 job sources scraping daily
- [ ] Zero duplicate Claude calls across runs
- [ ] Top 10 jobs delivered as individual Telegram messages
- [ ] Run summary sent after each digest
- [ ] Git repo initialized and pushed to GitHub
- [ ] n8n workflow running on 6PM + 1AM PH schedule
- [ ] README with architecture and demo screenshot
