# Market Intelligence Platform
### Project Charter

**Author:** Noah Lopez
**Start Date:** September 9, 2026
**Target Completion:** November 27, 2026
**Status:** Active

*(Originally chartered May 17, 2026 as a pure portfolio piece; timeline rebased September 9, 2026 after the project sat unstarted for several months; scope re-pivoted September 9, 2026 to a personal decision-support tool — see Section 2. Full architecture, math methodology, and security design live in [docs/architecture.md](docs/architecture.md); granular milestones and to-dos live in [docs/roadmap.md](docs/roadmap.md).)*

---

## 1. Project Summary

The Market Intelligence Platform is an end-to-end data engineering and analytics system that ingests daily U.S. equity market data, transforms it through a modern medallion architecture, applies statistical models to detect mispriced stocks within their sectors, and surfaces insights through interactive dashboards.

The project demonstrates the complete data lifecycle — ingestion, modeling, orchestration, testing, machine learning, and visualization — built to professional standards on a fully free and publicly accessible technology stack.

---

## 2. Business Problem

**This is a personal tool, built for Noah, to support his own stock-buying decisions.** It has one real user.

Today, deciding whether to buy or add to a position is ad hoc — checking a handful of metrics one at a time across different sites, with no systematic way to see how a stock actually compares to its real peers, and no way to be told when something on a watchlist changes enough to be worth a second look. This platform replaces that manual process with three concrete capabilities:

1. **Screen** — rank the S&P 500 by how statistically out of line each stock is with its own GICS sector, so there's a shortlist worth researching instead of 500 names to eyeball.
2. **Monitor** — track a private watchlist and get alerted, privately, when something on it moves enough to matter.
3. **Compare** — pick a small set of candidates and see them side by side on the same sector-relative terms.

**Guardrail:** the tool stays descriptive, never prescriptive. It answers "how does this compare, and what changed" — it never outputs "buy" or "sell." Noah makes every decision; the tool just makes the inputs to that decision faster and more consistent than doing it by hand. (This also keeps the project on the right side of the "no personalized financial advice" line — a tool that surfaces data for its owner to interpret is meaningfully different from a system that issues recommendations.)

---

## 3. Primary Objectives

1. **Screen** — Identify S&P 500 stocks that are statistically mispriced relative to their GICS sector peers using a robust z-score plus isolation forest, ranked and with each flag traceable to the metric(s) that drove it.
2. **Monitor** — Track a private watchlist; detect and privately alert on meaningful changes (valuation gap shift, sector rotation, earnings surprise) without that data or those alerts ever touching the public repo.
3. **Compare** — Given 2–5 user-selected tickers, produce an ad hoc, sector-normalized side-by-side comparison — no persistence needed, safe to expose publicly.
4. **Provide context** — Layer in sector rotation analysis to explain *why* a stock may be moving against its peers.
5. **Deliver reliability** — Build the platform with idempotent pipelines, automated testing, and scheduled refreshes so insights are current and trustworthy.
6. **Showcase craft** — A layered, tested, typed codebase with a real API behind it (not just pipelines feeding a dashboard) — document every architectural decision, publish the generic code openly, and produce a portfolio piece that shows software engineering as well as data engineering. Secondary to objectives 1–3, but free as a byproduct of building this properly.

---

## 4. Headline Questions

The platform exists to answer three questions on demand:

> **Screen:** "Which S&P 500 stocks are trading at the largest valuation gap from their sector peers right now, and why?"
>
> **Monitor:** "Has anything on my watchlist changed enough today that I should look at it?"
>
> **Compare:** "Of these specific stocks I'm considering, which is priced better relative to its own peers?"

Screen and Compare are answered by the public Streamlit app and Tableau dashboard. Monitor is answered privately — see [Section 5](#5-scope) and [docs/architecture.md](docs/architecture.md#security--the-publicprivate-split).

---

## 5. Scope

### In Scope
- All ~500 constituents of the S&P 500 index
- Daily price data (open, high, low, close, volume, adjusted close)
- Company fundamentals (sector, industry, market cap, P/E, EPS, dividend yield)
- Quarterly earnings history
- Macro indicators (10Y Treasury yield, Fed Funds rate, CPI) for context
- ~5 years of historical data at launch, with daily incremental refresh
- Anomaly detection at the stock-vs-sector level (Screen)
- Sector rotation analysis at the index level
- Ad hoc side-by-side comparison of 2–5 user-selected tickers (Compare) — no persistence, public-safe
- A private watchlist of tickers Noah is tracking (Monitor) — private data, never committed to the repo
- Private change-detection alerting on the watchlist (email, not a public channel)

### Out of Scope
- International equities
- Options, futures, crypto, fixed income
- Intraday or real-time data
- Predictive forecasting (we describe what *is* unusual, not what *will* happen)
- Trading recommendations or financial advice — the tool never outputs "buy" or "sell"
- Sentiment analysis from news or social media (potential v2)
- Brokerage integration or automated trade execution
- Storing real position size, cost basis, or brokerage account data
- Any public exposure of the private watchlist, its contents, or its alert history

---

## 6. Success Criteria

The project is considered complete and successful when **all** of the following are true:

| # | Criterion | Measurable Outcome |
|---|---|---|
| 1 | Pipeline runs end-to-end without manual intervention | Daily scheduled GitHub Actions run completes successfully for 7 consecutive days |
| 2 | Data quality is enforced | 100% of dbt tests pass on every run; failures trigger alerts |
| 3 | Anomaly model produces interpretable results | Each flagged stock includes the metric, z-score, and sector benchmark |
| 4 | Public-safe features are publicly accessible | Tableau dashboard and Streamlit app (Screen + Compare only) live with public URLs |
| 5 | Repository is portfolio-ready | Public GitHub repo with README, architecture diagram, ADRs, and demo links |
| 6 | Documentation is complete | Every component has a written explanation of *what* it does and *why* it was chosen |
| 7 | Monitor works for its one real user | Noah can add a ticker to his private watchlist and receive a private email alert when it changes meaningfully |
| 8 | Public/private boundary holds | Zero watchlist tickers, alert content, or personal holdings ever appear in the public repo, its commit history, or public Action logs |

---

## 7. Technology Stack

| Layer | Tool | Rationale |
|---|---|---|
| Language | Python 3.11+ | Industry standard for data engineering |
| Ingestion | `yfinance`, `fredapi` | Free, reliable, well-maintained libraries |
| Storage | Supabase (PostgreSQL) | Free tier, permanent, cloud-hosted, SQL standard |
| Transformation | dbt Core | Industry standard for SQL-based modeling |
| Application architecture | Layered: `domain` / `repositories` / `services` / `api` | Separates business logic from data access from HTTP — testable in isolation; see [docs/architecture.md](docs/architecture.md) §3 and [ADR 0003](docs/adr/0003-layered-architecture-and-api.md) |
| Backend API | FastAPI + Pydantic | Real HTTP service (not just scripts), typed request/response schemas, free interactive docs at `/docs` |
| Type checking | `mypy` | Catches a class of bugs before runtime, standard on production Python services |
| Testing | `pytest` + `pytest-cov` + dbt tests | Unit (domain/services, no I/O) + integration (API, repositories) + data-quality layers |
| Orchestration | GitHub Actions | Free for public repos, scheduled cron, built into version control |
| Machine Learning | scikit-learn | Mature, well-documented, sufficient for our methods |
| Notebooks | Jupyter | Standard for exploratory work, versioned in repo |
| BI Dashboard | Tableau Public | New skill, free, public URL for portfolio |
| Interactive App | Streamlit + Streamlit Community Cloud | Thin API client, free hosting — no direct DB access, no business logic |
| API hosting | Render or Fly.io (free tier) — decided in Phase 6 | Needs to be reachable over HTTPS by the private Monitor job, not just co-located with Streamlit |
| Version Control | Git + GitHub | Public repo for portfolio visibility |
| Documentation | Markdown + dbt docs | Lives alongside code, version-controlled |

---

## 8. Architecture Overview

Quick-reference diagram below; the full flowchart (with the public/private split), the math methodology behind Screen/Monitor/Compare, and the security design live in **[docs/architecture.md](docs/architecture.md)**.

```
┌─────────────────────┐
│  External Sources   │
│  • Yahoo Finance    │
│  • FRED (macro)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Python Ingestion  │  ← GitHub Actions (scheduled daily)
│   (extract + load)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Bronze (raw)       │
│  Supabase Postgres  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Silver (cleaned)   │  ← dbt staging + intermediate models
│  Supabase Postgres  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Gold (analytics)   │  ← dbt marts + ML predictions
│  Supabase Postgres  │
└──────────┬──────────┘
           │
           ├──────────────┬─────────────────┐
           ▼              ▼                 ▼
   ┌──────────────┐  ┌──────────┐   ┌─────────────┐
   │   Tableau    │  │ Streamlit│   │  Jupyter    │
   │   Public     │  │   App    │   │  Notebooks  │
   └──────────────┘  └──────────┘   └─────────────┘
```

---

## 9. Project Phases & Timeline

See [docs/roadmap.md](docs/roadmap.md) for the granular milestone- and task-level breakdown. Phase-level summary:

| Phase | Dates | Deliverable |
|---|---|---|
| **0. Planning** | Sep 9 – Sep 16 | Charter, architecture doc, math methodology, roadmap, flowchart, ADRs |
| **1. Infrastructure** | Sep 17 – Sep 23 | Supabase (public schema + private schema) + GitHub + Python env operational |
| **2. Ingestion (Bronze)** | Sep 24 – Oct 7 | Python ingestion scripts, raw data flowing, watchlist table created |
| **3. Modeling (Silver/Gold)** | Oct 8 – Oct 21 | dbt project with full test coverage, composite valuation-gap marts |
| **4. Orchestration** | Oct 22 – Oct 28 | Scheduled GitHub Actions, pipeline monitoring, private watchlist-monitor job |
| **5. Data Science** | Oct 29 – Nov 11 | z-score + isolation forest models, validated against hand-picked known examples |
| **6. Visualization** | Nov 12 – Nov 22 | Tableau + public Streamlit (Screen, Compare) live; private companion repo for Monitor alerts |
| **7. Showcase** | Nov 23 – Nov 27 | README polish, architecture diagram, blog post |

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `yfinance` API changes or rate limits | Medium | Medium | Build retry logic; have FRED as backup macro source |
| Supabase free tier limits (500MB) hit | Low | High | Aggressively partition historical data; archive >5yr to Parquet |
| Scope creep extends timeline past Nov 27 | High | Medium | Strict phase gates; defer v2 features to backlog |
| Tableau learning curve slows Phase 6 | Medium | Low | Allocate buffer week; YouTube tutorials in advance |
| ML model produces noisy or unconvincing results | Medium | High | Use multiple methods (z-score + isolation forest); validate against known historical anomalies |
| Composite score doesn't feel actionable for a real personal buy decision | Medium | High | Validate against a small hand-picked set of stocks Noah already has a strong opinion on before trusting the output; treat as directional, not authoritative |
| Personal watchlist/alert data leaks into the public repo (commits, Action logs, public issues) | Medium | High | Hard split: private data lives only in Noah's own Supabase schema + a private companion repo for alerting; public repo never references specific tickers Noah is tracking — see [ADR 0002](docs/adr/0002-public-demo-vs-private-personal-data.md) |
| Scope grew (Monitor + Compare added) without extending the timeline | High | Medium | Target completion moved from Nov 23 to Nov 27; phase gates still strict, v2 backlog absorbs anything further |

---

## 11. Out-of-Scope (Backlog for v2)

- News sentiment integration (NewsAPI + transformer model)
- Real-time / intraday data via Alpaca or Polygon
- International market coverage (FTSE, Nikkei)
- Backtesting framework for anomaly-based strategies
- LLM-generated written commentary on flagged stocks
- Mobile-responsive dashboard

---

## 12. Definition of Done

The project is **done** when both of these are true:

**For its real user (primary):**
1. Noah can add a ticker to his private watchlist and, without touching code, get told privately when it's worth a look
2. Noah can pull up 2–5 tickers he's actually considering and see a side-by-side comparison that's faster than doing it by hand
3. The Screen shortlist has been checked against a handful of stocks Noah already has a strong opinion on, and it agrees often enough to be trusted directionally

**For the portfolio (secondary, free byproduct):**
4. A hiring manager can click the GitHub repo link, read a README that explains the project in 60 seconds, view the live Tableau dashboard and Streamlit app (Screen + Compare), and read an architecture diagram and ADRs explaining every design choice — including *why* the personal watchlist data never appears in any of it

---

*This charter is a living document. Any material change to scope, timeline, or stack will be reflected here and committed to version control.*
