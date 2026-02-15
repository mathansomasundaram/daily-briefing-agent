Daily Personalized News Briefing System – Reframed Plan
Overview

You are building a daily automated news briefing application that generates personalized email reports based on each user’s configuration.

Each user can specify:

Topics of interest (e.g., Geopolitics, Sports, Tech, Stocks, etc.)

Sub-focus areas (e.g., AI, data breaches)

Email address (stored in Google Sheets)

The system runs every 24 hours, fetches relevant news from the last 24 hours, processes and ranks it, formats it using an LLM, and sends a structured email to the user.

Phase 1 (MVP Scope)

Focus on:

Single user

Topics:

Tech (AI developments + recent data breaches)

Geopolitics

Indian stock market

User email stored in Google Sheets (Service Account access provided)

Limit:

5–10 top news items per category

Ranked by importance

Each item must include source attribution

End-to-End Workflow
1. Scheduler (Runs Every 24 Hours)

Use:

Cron (local/server)

Cloud Scheduler (GCP)

AWS EventBridge (if applicable)

Trigger the pipeline once daily.

2. User Configuration Loader

Fetch user configuration

Load:

Topics selected

Sub-categories

Email address (from Google Sheet)

Last run timestamp

This ensures:

Personalized news per user

Only new articles since last run are fetched

3. News Aggregation Layer

For each selected category:

Pull articles from multiple sources

Use source adapters or API clients (e.g., News APIs, RSS feeds, financial APIs)

Fetch articles within:

last_run_timestamp → current_time

4. Normalization Layer

Convert all incoming articles into a unified schema:

{
  "title": "",
  "summary": "",
  "source": "",
  "published_at": "",
  "category": "",
  "url": "",
  "importance_score": 0
}


This ensures consistency across multiple news providers.

5. Deduplication + Freshness Strategy

To prevent duplicates and old content:

Store previously sent article URLs in:

A JSON file (Phase 1)

Database (future scaling)

Maintain:

last_run_timestamp

sent_article_urls

Rules:

Only fetch articles newer than last_run_timestamp

Do not send URLs already present in sent_article_urls

6. Ranking Engine

For each category, rank articles based on:

Importance (manual weight rules)

Popularity (engagement metrics, mentions, trending signals)

Trusted source priority (assign weight to premium sources)

Select:

Top 5–10 per category

7. Pre-LLM Filtering / Trimming

Before sending to the LLM:

Remove low-quality articles

Trim long summaries

Limit total tokens

Keep only high-ranking items

This reduces:

LLM cost

Noise

Hallucination risk

8. LLM Formatting Layer

Pass cleaned, ranked articles to LLM to:

Refine summaries

Improve readability

Create structured email format

Add headings per category

Keep professional tone

The LLM should:

Not invent facts

Preserve original sources

Maintain factual accuracy

9. Email Rendering Layer

Generate a clean HTML email template:

Structure example:

Good Morning,

Here is your personalized news briefing:

🔹 Tech (AI & Data Breaches)
- Headline
- 2–3 line summary
- Source | Date

🔹 Geopolitics
...

🔹 Indian Stock Market
...

Best,
Daily Briefing

10. Email Delivery

Read user email from Google Sheets

Send via:

Gmail API

SendGrid

SES

SMTP

Data Freshness Strategy

To avoid duplicates and stale news:

Store last_run_timestamp

Fetch articles only between:

last_run_timestamp → now


Update timestamp after successful send

Maintain a persistent list of previously sent URLs

System Architecture Overview
Scheduler (Cron / Cloud Scheduler)
        |
        v
User Config Loader
        |
        v
News Aggregation Layer
   - Source adapters
   - API clients
        |
        v
Normalization Layer
   - Convert to common schema
        |
        v
Deduplication + Ranking Engine
   - Store sent URLs (JSON file for Phase 1)
        |
        v
Pre-Summarization (optional small model)
        |
        v
LLM Formatter
        |
        v
Email Renderer (HTML template)
        |
        v
Email Sender

Key Design Principles

Personalized per user

Only last 24-hour news

No duplicate sends

Ranked by importance

Trusted source prioritization

Controlled LLM cost

Structured output

Scalable to multi-user in Phase 2