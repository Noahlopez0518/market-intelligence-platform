# 3. Layered architecture with a FastAPI backend

## Status

Accepted. Amends the data-access design in [ADR 0002](0002-public-demo-vs-private-personal-data.md) — see Consequences.

## Context

The original architecture (Section 1 of `architecture.md`, first draft) had Streamlit and Tableau reading dbt's gold-layer marts directly, and had the private Monitor job reading those same marts directly too. That's a data-engineering shape: pipelines feeding BI tools. It has no service boundary, no business logic that exists independently of a database connection, and nothing that can be unit tested without spinning up Postgres.

This project is meant to demonstrate software engineering as well as data engineering — not a dashboard bolted onto a pipeline, but a system with a real application layer someone else could read, test, and extend. That requires an actual architecture decision, not just "add more dbt models."

## Decision

Introduce a layered application inside `src/`:

- `domain/` — pure business logic and the scoring engine (the math in `architecture.md` Section 2), zero I/O
- `repositories/` — data access, isolates SQL from everything else
- `services/` — orchestration, combines repositories + domain into what the API returns
- `api/` — a FastAPI app exposing `/screen`, `/compare`, `/score/{ticker}`

Streamlit becomes a thin HTTP client of this API — no direct database access, no duplicated business logic. Tableau continues to read the gold marts directly, since Tableau has no code layer to put behind an API; that's an acceptable, narrower exception (BI tools are expected to query data directly, that's what they're for).

The private Monitor job (ADR 0002) also becomes an API client: instead of reading Supabase gold marts directly, it calls the public `/score/{ticker}` endpoint — which only ever returns public data, so there's nothing sensitive in the response.

## Consequences

- The scoring math exists in exactly one place (`src/domain`), fully unit-testable without a database — directly addresses the charter risk that the composite score might not feel actionable, since it can now be pinned with real test cases.
- **Amends ADR 0002:** that decision assumed Monitor would need Supabase credentials for the public schema. It no longer does — Monitor's private secret surface shrinks to its own tiny watchlist table and email-sending credentials only. Smaller attack surface, less private infrastructure overall. ADR 0002's core decision (a separate private repo, private alerting via email) still holds; only *how Monitor reaches market data* changed.
- Adds a new free-tier hosting dependency: the FastAPI backend needs to run somewhere reachable over HTTPS by the private repo's scheduled job, not just be co-located with Streamlit. Deferred as an open decision to Phase 6 (`architecture.md` Section 3.4) — doesn't block any earlier work.
- Adds `mypy` and `pytest-cov` to CI, alongside the existing `ruff` lint step.
- More upfront structure than "a few scripts" — justified here because the math is genuinely the risky part of this project (user's own framing: "very math intensive and a tough project"), and that's exactly the part this layering makes safe to change and cheap to verify.
