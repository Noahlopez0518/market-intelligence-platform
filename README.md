# Market Intelligence Platform

A personal decision-support tool: ingests daily U.S. equity market data, transforms it through a medallion architecture, and answers three questions — **Screen** (which S&P 500 stocks are statistically mispriced vs. their GICS sector peers), **Compare** (how do 2–5 stocks I'm considering stack up side by side), and **Monitor** (has anything on my private watchlist changed enough to look at). It never tells you what to buy — it makes the inputs to that decision faster and more consistent than doing it by hand.

**Status:** planning complete, build starting — see [project-charter.md](project-charter.md) for scope, timeline, and success criteria.

## Stack

Python (`yfinance`, `fredapi`) → Supabase (Postgres) → dbt Core → GitHub Actions → scikit-learn → Tableau Public / Streamlit

## Repo layout

```
src/ingestion/     Python extract + load scripts (Bronze)
dbt/               staging / intermediate / marts models (Silver/Gold)
notebooks/         exploratory analysis, versioned
streamlit_app/     interactive exploration app
docs/              setup guide, ADRs
.github/workflows/ scheduled ingestion + CI
```

## Docs

- [Project charter](project-charter.md) — problem, scope, success criteria, phased timeline
- [Architecture](docs/architecture.md) — system flowchart, math methodology, security design
- [Roadmap](docs/roadmap.md) — granular milestones and to-dos per phase
- [Setup guide](docs/setup.md) — accounts and env vars needed to run this locally / in CI
- [ADRs](docs/adr/) — architecture decisions as they're made

## A note on the personal watchlist

The public code here is deliberately generic — it never contains a real ticker list. The private "Monitor" feature (a personal watchlist + private alerting) lives in a separate, private repo by design, not by omission. See [ADR 0002](docs/adr/0002-public-demo-vs-private-personal-data.md) for why.
