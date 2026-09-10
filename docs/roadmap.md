# Roadmap

Granular milestones and to-dos underneath the phase table in [project-charter.md](../project-charter.md). Check items off as they land; this file is expected to change as work reveals what the phase table couldn't predict — update it, don't let it go stale.

---

## Phase 0 — Planning (Sep 9 – Sep 16)

**Milestone: nothing gets built until the design holds together on paper.**

- [x] Rebase charter timeline after the unstarted-since-May gap
- [x] Pivot charter to the personal decision-support use case (Screen / Monitor / Compare)
- [x] Write `docs/architecture.md` — flowchart, math methodology, security design
- [x] Write ADR 0002 — public/private repo split
- [x] Write this roadmap
- [x] Decide layered architecture (`domain` / `repositories` / `services` / `api`) + FastAPI backend — `docs/architecture.md` §3, [ADR 0003](adr/0003-layered-architecture-and-api.md) — so the project demonstrates software engineering, not just data engineering
- [x] Sanity-check the math methodology against real S&P 500 stocks (19 tickers, 3 sectors, live `yfinance` data — see `docs/architecture.md` §2.6) — found and fixed a real issue: added a ±4 clip to the composite score after AAPL's inflated P/B alone skewed it. These values become the basis for pinned tests in `tests/unit/domain/` once re-verified at full sector size in Phase 5.
- [x] Decide final list of valuation metrics for v1 — **keep all four (P/E, P/B, EV/EBITDA, P/S)**; sample coverage was 95–100% usable, no metric thin enough to cut
- [x] Confirm GICS sector classification source — **do not use `yfinance`'s `sector` field**, it only matched official GICS sector names 32% of the time in testing. Use a dedicated reference table instead — see [ADR 0004](adr/0004-sector-classification-source.md)

---

## Phase 1 — Infrastructure (Sep 17 – Sep 23)

**Milestone: an empty pipeline can run end-to-end against real infrastructure.**

- [ ] Create Supabase project (account already exists)
- [ ] Design schema split: public schema (bronze/silver/gold, all portfolio-safe) vs. a separate schema or database reserved for the future private watchlist table (built Phase 6, but reserve the design now so it's not bolted on later)
- [ ] Add Supabase connection secrets to local `.env` (from `env.example`) and to GitHub Actions repo secrets
- [ ] Verify `src/utils/db.py` connects successfully to both local and CI environments
- [ ] Request FRED API key, add to `.env` and Actions secrets
- [ ] Confirm `requirements.txt` installs cleanly in the CI runner (already true as of the CI workflow, re-verify after any dependency additions)
- [ ] `dbt debug` succeeds against the Supabase connection
- [ ] Restructure `src/` into the layered skeleton (`domain/`, `repositories/`, `services/`, `api/`), add `tests/unit/` and `tests/integration/` — empty modules with the boundaries in place, no logic yet (architecture.md §3.1)
- [ ] Add `fastapi`, `uvicorn`, `pydantic`, `httpx`, `mypy`, `pytest-cov` to `requirements.txt`
- [ ] Add `mypy` check step to `.github/workflows/ci.yml`, alongside the existing `ruff` step

---

## Phase 2 — Ingestion / Bronze (Sep 24 – Oct 7)

**Milestone: five years of real S&P 500 data sitting in bronze tables, refreshed daily.**

- [ ] `src/ingestion/prices.py` — daily OHLCV for all ~500 tickers via `yfinance`, idempotent upsert (re-running a day must not duplicate rows)
- [ ] `src/ingestion/fundamentals.py` — market cap, P/E, P/B, EV/EBITDA, P/S, EPS, dividend yield (no sector — see next item)
- [ ] `src/ingestion/sector_reference.py` — pulls the S&P 500 constituent + GICS sector list (Wikipedia or equivalent), refreshed periodically rather than daily, per [ADR 0004](../docs/adr/0004-sector-classification-source.md). Validates row count is ~500 ± a few and fails loudly if not, rather than silently ingesting a broken scrape.
- [ ] dbt test: every ticker in the fundamentals table has a non-null sector from the reference table — a gap here breaks Screen's entire cohort grouping silently if untested
- [ ] `src/ingestion/macro.py` — 10Y Treasury, Fed Funds rate, CPI via `fredapi`
- [ ] Backfill ~5 years of historical price data (one-time bulk load, separate from the daily incremental script)
- [ ] Retry/backoff logic for `yfinance` rate limits (charter risk #1)
- [ ] Bronze schema for the future private watchlist table — table definition only, no real tickers in this repo (per ADR 0002); actual private table created later in the private repo's own Supabase schema
- [ ] Wire `.github/workflows/daily-ingestion.yml`'s ingestion step to actually call these scripts (currently a placeholder echo)
- [ ] Unit tests for each ingestion script (replace `tests/test_placeholder.py` coverage) — mock the external API calls, don't hit real APIs in CI

---

## Phase 3 — Modeling / Silver + Gold (Oct 8 – Oct 21)

**Milestone: dbt turns raw bronze rows into the marts Screen/Compare/Monitor all read from.**

- [ ] Staging models: one per bronze source, light cleaning/typing only
- [ ] Intermediate models: sector cohort aggregation (median/MAD per metric per sector per day)
- [ ] Gold mart: `fct_valuation_gap` — per stock, per day: raw metrics, robust z-scores per metric, composite score
- [ ] dbt tests on every model per the pattern in `dbt/models/staging/schema.yml` — not_null/unique at minimum, `accepted_values` on sector
- [ ] Confirm dbt test failures actually fail the CI/ingestion pipeline (charter Success Criterion #2)
- [ ] `dbt docs generate` produces a browsable lineage graph, linked from the README
- [ ] Build `src/repositories/` — `MarketDataRepository` interface + Supabase implementation reading the gold marts; add an in-memory fake implementation for unit tests
- [ ] Integration tests (`tests/integration/`) for the repository against a real test schema — confirms the SQL side actually works before any business logic depends on it

---

## Phase 4 — Orchestration (Oct 22 – Oct 28)

**Milestone: the whole bronze→silver→gold chain runs on a schedule without anyone watching it.**

- [ ] Chain ingestion → dbt run → dbt test into one scheduled workflow (or sequenced dependent jobs)
- [ ] Confirm the failure-alert step (`daily-ingestion.yml`) fires correctly on a deliberately broken run
- [ ] Run for 7 consecutive days without manual intervention (charter Success Criterion #1) — track pass/fail per day somewhere visible (even a simple log table)
- [ ] Design (not yet build) the private watchlist-monitor job's scheduling — depends on the Phase 5 API being live, not just the gold marts existing

---

## Phase 5 — Data Science + API (Oct 29 – Nov 11)

**Milestone: Screen produces a ranked, explainable shortlist; the math has been checked against reality; it's reachable over HTTP.**

- [ ] Build `src/domain/` — `Stock`, `SectorCohort`, `ValuationScore`, `AnomalyResult` models + `ScoringEngine` implementing composite z-score **with the ±4 clip** (architecture.md §2.1, added after Phase 0 validation). Zero I/O.
- [ ] Re-run the Phase 0 validation script at full sector size (all ~73 Information Technology stocks, not 7) to confirm the clip threshold and math still hold up outside a small sample; pin the results as permanent test cases in `tests/unit/domain/`
- [ ] Implement per-sector Isolation Forest (architecture.md §2.2) inside `ScoringEngine`, `scikit-learn`, `contamination=0.1` starting point
- [ ] Shortlist rule (architecture.md §2.3) — confirm every flagged stock carries its driving metric(s) in the output row
- [ ] **Validation pass:** hand-pick 5–10 S&P 500 stocks Noah already has a strong opinion on (clearly overvalued, clearly cheap, clearly unremarkable) and confirm the model's output roughly agrees — this is the check against charter risk "composite score doesn't feel actionable"
- [ ] Build `src/services/` — `ScreenService`, `CompareService` wiring the Phase 3 repository + this phase's domain engine
- [ ] Build `src/api/` — FastAPI app: `/screen`, `/compare`, `/score/{ticker}` per the contract in architecture.md §3.4, Pydantic schemas, dependency injection
- [ ] Integration tests (`tests/integration/api/`) via FastAPI's `TestClient`
- [ ] Investigate earnings-estimate data source for Monitor's earnings-surprise trigger (architecture.md §2.4 — currently an open question, not yet resolved)
- [ ] Tune shortlist thresholds (`|composite| > 2.0`, top-decile anomaly) based on how many stocks actually surface — too many or too few both indicate a miscalibrated threshold

---

## Phase 6 — Visualization + Monitor (Nov 12 – Nov 22)

**Milestone: Screen and Compare are live and public; Monitor is live and private.**

- [ ] Choose free API hosting (Render or Fly.io — architecture.md §3.4) and deploy the FastAPI backend
- [ ] Tableau Public account created, dashboard built against gold marts, published
- [ ] Streamlit Community Cloud account created
- [ ] `streamlit_app/` — Screen tab: ranked shortlist, filterable by sector, each row shows driving metric(s) — calls the deployed API, no direct DB access
- [ ] `streamlit_app/` — Compare tab: ticker multi-select (2–5), side-by-side table + chart, calls the deployed API, no persistence
- [ ] Deploy public Streamlit app, confirm no personal data path exists in the deployed code (spot-check: grep the deployed repo for any hardcoded ticker list — there should be none)
- [ ] Create the private companion repo (name TBD, not `market-intelligence-platform`)
- [ ] Private repo: a small watchlist table (ticker + last-seen composite score) — this is the *only* private data store needed now that Monitor reads market data via the public API (ADR 0003), not Supabase directly
- [ ] Private repo: Monitor job — calls `GET /score/{ticker}` on the public API for each watched ticker, compares to last-seen value, applies the change-detection rules (architecture.md §2.4)
- [ ] Private repo: email alerting wired up (SMTP secret or a transactional email service), tested with a deliberate trigger
- [ ] Confirm private repo's Actions logs are actually private (repo visibility setting, not just an assumption)

---

## Phase 7 — Showcase (Nov 23 – Nov 27)

**Milestone: the public repo reads like a finished, professional project to someone who's never seen it.**

- [ ] README polish — 60-second explanation, links to live Tableau + Streamlit, architecture diagram embedded or linked
- [ ] Confirm all ADRs are current (0001, 0002, 0003, 0004, plus any written along the way — Phase 5's threshold-tuning decisions probably deserve one)
- [ ] Clean commit history check — no secrets in any past commit (`git log -p` spot check or a secret-scanning tool), no "wip" commits left unsquashed if that matters to the final presentation
- [ ] Short write-up / blog post: what the project does, why the public/private split exists, what the math methodology is — this doubles as proof of the "why," not just the "what" (charter Definition of Done)
- [ ] Final pass: does every claim in the README actually work if a stranger clicks it right now?
