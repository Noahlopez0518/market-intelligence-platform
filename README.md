# Market Intelligence Platform

End-to-end data engineering and analytics platform that ingests daily U.S. equity market data, transforms it through a medallion architecture, and flags S&P 500 stocks that are statistically mispriced relative to their GICS sector peers.

**Status:** early build — see [project-charter.md](project-charter.md) for scope, timeline, and success criteria.

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
- [Setup guide](docs/setup.md) — accounts and env vars needed to run this locally / in CI
- [ADRs](docs/adr/) — architecture decisions as they're made
