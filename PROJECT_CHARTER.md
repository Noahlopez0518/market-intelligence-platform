# Market Intelligence Platform
### Project Charter

**Author:** Noah Lopez
**Start Date:** May 17, 2026
**Target Completion:** July 31, 2026
**Status:** Active

---

## 1. Project Summary

The Market Intelligence Platform is an end-to-end data engineering and analytics system that ingests daily U.S. equity market data, transforms it through a modern medallion architecture, applies statistical models to detect mispriced stocks within their sectors, and surfaces insights through interactive dashboards.

The project demonstrates the complete data lifecycle — ingestion, modeling, orchestration, testing, machine learning, and visualization — built to professional standards on a fully free and publicly accessible technology stack.

---

## 2. Business Problem

Investors and analysts face a recurring question: **"Is this stock fairly priced relative to its peers?"**

Traditional stock screeners compare absolute metrics (P/E ratio, market cap) without accounting for sector context. A P/E of 30 is expensive for a utility company but cheap for a high-growth tech firm. This platform answers the question correctly by evaluating each stock against its own sector cohort and flagging statistical outliers.

---

## 3. Primary Objectives

1. **Detect anomalies** — Identify S&P 500 stocks that are statistically mispriced relative to their GICS sector peers using z-score and isolation forest methods.
2. **Provide context** — Layer in sector rotation analysis to explain *why* a stock may be moving against its peers.
3. **Deliver reliability** — Build the platform with idempotent pipelines, automated testing, and scheduled refreshes so insights are current and trustworthy.
4. **Showcase craft** — Document every architectural decision, publish all code openly, and produce a portfolio piece that demonstrates senior-level data engineering thinking.

---

## 4. Headline Insight

> **"Which S&P 500 stocks are currently trading at the largest valuation gap from their sector peers, and which sectors are driving the divergence?"**

This question is answered daily by the platform and presented as the lead metric on the public Tableau dashboard.

---

## 5. Scope

### In Scope
- All ~500 constituents of the S&P 500 index
- Daily price data (open, high, low, close, volume, adjusted close)
- Company fundamentals (sector, industry, market cap, P/E, EPS, dividend yield)
- Quarterly earnings history
- Macro indicators (10Y Treasury yield, Fed Funds rate, CPI) for context
- ~5 years of historical data at launch, with daily incremental refresh
- Anomaly detection at the stock-vs-sector level
- Sector rotation analysis at the index level

### Out of Scope
- International equities
- Options, futures, crypto, fixed income
- Intraday or real-time data
- Predictive forecasting (we describe what *is* unusual, not what *will* happen)
- Trading recommendations or financial advice
- Sentiment analysis from news or social media (potential v2)

---

## 6. Success Criteria

The project is considered complete and successful when **all** of the following are true:

| # | Criterion | Measurable Outcome |
|---|---|---|
| 1 | Pipeline runs end-to-end without manual intervention | Daily scheduled GitHub Actions run completes successfully for 7 consecutive days |
| 2 | Data quality is enforced | 100% of dbt tests pass on every run; failures trigger alerts |
| 3 | Anomaly model produces interpretable results | Each flagged stock includes the metric, z-score, and sector benchmark |
| 4 | Dashboards are publicly accessible | Tableau Public dashboard and Streamlit app both live with public URLs |
| 5 | Repository is portfolio-ready | Public GitHub repo with README, architecture diagram, ADRs, and demo links |
| 6 | Documentation is complete | Every component has a written explanation of *what* it does and *why* it was chosen |

---

## 7. Technology Stack

| Layer | Tool | Rationale |
|---|---|---|
| Language | Python 3.11+ | Industry standard for data engineering |
| Ingestion | `yfinance`, `fredapi` | Free, reliable, well-maintained libraries |
| Storage | Supabase (PostgreSQL) | Free tier, permanent, cloud-hosted, SQL standard |
| Transformation | dbt Core | Industry standard for SQL-based modeling |
| Testing | dbt tests + `pytest` | Coverage at both data and code layers |
| Orchestration | GitHub Actions | Free for public repos, scheduled cron, built into version control |
| Machine Learning | scikit-learn | Mature, well-documented, sufficient for our methods |
| Notebooks | Jupyter | Standard for exploratory work, versioned in repo |
| BI Dashboard | Tableau Public | New skill, free, public URL for portfolio |
| Interactive App | Streamlit + Streamlit Community Cloud | Live Python-driven app, free hosting |
| Version Control | Git + GitHub | Public repo for portfolio visibility |
| Documentation | Markdown + dbt docs | Lives alongside code, version-controlled |

---

## 8. Architecture Overview

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

| Phase | Dates | Deliverable |
|---|---|---|
| **0. Planning** | May 17 – May 24 | Charter, architecture diagram, repo skeleton, ADRs |
| **1. Infrastructure** | May 25 – May 31 | Supabase + GitHub + Python env operational |
| **2. Ingestion (Bronze)** | Jun 1 – Jun 14 | Python ingestion scripts, raw data flowing |
| **3. Modeling (Silver/Gold)** | Jun 15 – Jun 28 | dbt project with full test coverage |
| **4. Orchestration** | Jun 29 – Jul 5 | Scheduled GitHub Actions, monitoring |
| **5. Data Science** | Jul 6 – Jul 19 | Anomaly detection models, predictions table |
| **6. Visualization** | Jul 20 – Jul 26 | Tableau dashboard + Streamlit app live |
| **7. Showcase** | Jul 27 – Jul 31 | README polish, architecture diagram, blog post |

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `yfinance` API changes or rate limits | Medium | Medium | Build retry logic; have FRED as backup macro source |
| Supabase free tier limits (500MB) hit | Low | High | Aggressively partition historical data; archive >5yr to Parquet |
| Scope creep extends timeline past July | High | Medium | Strict phase gates; defer v2 features to backlog |
| Tableau learning curve slows Phase 6 | Medium | Low | Allocate buffer week; YouTube tutorials in advance |
| ML model produces noisy or unconvincing results | Medium | High | Use multiple methods (z-score + isolation forest); validate against known historical anomalies |

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

The project is **done** when a hiring manager can:
1. Click the GitHub repo link
2. Read a README that explains the project in 60 seconds
3. View a live Tableau dashboard with current data
4. View a live Streamlit app with interactive exploration
5. Read an architecture diagram and ADRs explaining every design choice
6. See a clean commit history showing the project evolved professionally

---

*This charter is a living document. Any material change to scope, timeline, or stack will be reflected here and committed to version control.*
