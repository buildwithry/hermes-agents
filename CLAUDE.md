# Hermes Agent — Project Guide

## What This Is

Hermes is an autonomous AI job-hunt agent. It monitors job boards, scores opportunities against your profile, drafts personalized cover letters, tracks your pipeline, and delivers daily digests — so you can focus on interviews, not searching.

**Portfolio goal:** Demonstrate real-world autonomous agent architecture for AI/software engineering roles.

## Core Capabilities (Roadmap)

| # | Feature | Status |
|---|---------|--------|
| 1 | Job board scraper (LinkedIn, Indeed, Greenhouse, Lever) | 🔲 planned |
| 2 | Job ↔ resume scoring (LLM-based relevance scoring) | 🔲 planned |
| 3 | Cover letter generator (personalized per company) | 🔲 planned |
| 4 | Application pipeline tracker (applied → interview → offer) | 🔲 planned |
| 5 | Company/interviewer researcher | 🔲 planned |
| 6 | Daily digest notifications | 🔲 planned |

## Tech Stack

- **Language:** Python 3.11+
- **LLM:** Anthropic Claude (`claude-haiku-4-5-20251001` for job scoring — fast + cheap)
- **API Server:** FastAPI + Uvicorn (webhook server n8n calls)
- **Orchestration:** n8n (local Docker → Hostinger VPS for production)
- **Notifications:** Telegram Bot API
- **Scraping:** feedparser (Upwork RSS) + BeautifulSoup (OnlineJobs.ph, JobStreet)
- **Storage:** profile.yaml for user profile, data/ for job history

## Architecture Principles

1. **Modular agents** — each capability is its own agent/tool, composable
2. **Observable** — every agent action is logged with reasoning
3. **Resumable** — state persists between runs; picks up where it left off
4. **Portfolio-ready** — clean README, demo video, clear architecture diagram

## Project Owner

- **Name:** Adrian (adrian@romea.ai)
- **Goal:** Land a job in AI/software engineering
- **Timeline:** Active job search — ship fast, iterate

## Development Rules

- Default model: `claude-sonnet-4-6` for complex reasoning, `claude-haiku-4-5-20251001` for high-volume tasks
- All secrets in `.env` — never committed
- Every agent module has a standalone `__main__` so it can be demoed independently
- Keep a `demo/` folder with sample outputs for portfolio showcasing
- Write a proper `README.md` — this is a portfolio project; it must be impressive

## File Structure (Target)

```
hermes-agents/
├── CLAUDE.md              # This file
├── README.md              # Portfolio-facing readme
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
├── agents/
│   ├── scraper.py         # Job board scraping agent
│   ├── scorer.py          # Job relevance scoring agent
│   ├── writer.py          # Cover letter generation agent
│   ├── tracker.py         # Pipeline tracking agent
│   ├── researcher.py      # Company research agent
│   └── digest.py          # Daily digest agent
├── tools/                 # Reusable tool functions for agents
├── data/                  # Local data storage
├── demo/                  # Sample outputs for portfolio
└── tests/                 # Unit + integration tests
```

## Key Decisions Still Open

- [ ] Agent framework: raw Anthropic SDK vs LangChain vs CrewAI vs LlamaIndex
- [ ] Storage: SQLite vs PostgreSQL vs JSON files
- [ ] Notification delivery: email vs Slack vs CLI
- [ ] Scraping approach: Playwright/Selenium vs APIs vs job board RSS feeds

## Running the Project

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env

# Run individual agents
python -m agents.scraper
python -m agents.scorer
```
