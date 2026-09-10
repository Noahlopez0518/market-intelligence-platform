# 2. Split personal watchlist data into a private companion repo

## Status

Accepted

## Context

The project pivoted from a pure portfolio piece to a personal decision-support tool (charter Section 2). That added a **Monitor** feature: a private watchlist of tickers Noah is actually researching, with alerts when something changes.

The existing repo is public — that's a deliberate portfolio-visibility choice (charter Section 7, "Public repo for portfolio visibility"). GitHub Actions logs on a public repo are visible to anyone, and the pipeline-failure alerting already built (`daily-ingestion.yml`) posts to public GitHub Issues. Reusing that same mechanism for watchlist alerts would mean Noah's actual stock research — which tickers, when, why — becomes public by accident, not by choice.

Three options considered:
1. **Make the whole repo private.** Defeats the portfolio purpose entirely (charter Definition of Done requires a public repo link a hiring manager can click).
2. **One repo, careful discipline** (never log the ticker, never name it in an issue). Rejected — this is a "don't mess up" solution, not a "can't mess up" solution. One forgotten `print(ticker)` in a debug session leaks it.
3. **Two repos: public generic code, private personal data + alerting.** The public repo stays fully portfolio-safe by construction — it never contains a real ticker list, only code that accepts one as a parameter. The private repo holds the actual watchlist and runs its own scheduled Action with its own (private) logs and its own secrets.

## Decision

Go with option 3. The public repo (`market-intelligence-platform`) contains all code: ingestion, dbt, ML scoring, Streamlit (Screen + Compare tabs only), Tableau queries. A second, private repo holds the watchlist table reference, the Monitor scheduling, and private email-alert wiring — built in Phase 6 once the public gold-layer marts it depends on exist.

## Consequences

- The public repo can be shown to anyone at any point without a review pass to scrub personal data — there's structurally nothing to scrub.
- Two repos to maintain instead of one; the private repo needs its own minimal CI (or none — it's low-stakes, personal-use code).
- The private repo depends on the public repo's gold-layer schema staying stable, or it breaks silently. Acceptable for a personal tool; would need a versioned contract if this ever had other users.
- Monitor's actual build is deferred to Phase 6, after Screen and Compare (and the marts they depend on) are working — see [roadmap.md](../roadmap.md).
