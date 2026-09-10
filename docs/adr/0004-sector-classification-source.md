# 4. Use a dedicated GICS reference table, not yfinance's per-ticker sector field

## Status

Accepted

## Context

The entire Screen feature depends on grouping stocks into the correct sector cohort — the z-score in `architecture.md` §2.1 is computed *relative to sector peers*, so getting the sector wrong for a stock silently puts it in the wrong comparison group and produces a confidently wrong score, with no error to catch it.

The original plan (charter Section 7, before this check) was to pull `sector` straight from `yfinance`'s per-ticker `.info` field alongside the other fundamentals — one API, one call, simplest possible design.

Phase 0 validation (`architecture.md` §2.6) tested this against 19 real S&P 500 tickers, comparing `yfinance`'s `sector` field to the official GICS Sector name from Wikipedia's S&P 500 constituent list:

| | yfinance `sector` | Official GICS Sector |
|---|---|---|
| AAPL, MSFT, NVDA, etc. | `Technology` | `Information Technology` |
| JNJ, PFE, UNH, etc. | `Healthcare` | `Health Care` |
| NEE, DUK, SO, etc. | `Utilities` | `Utilities` (matched) |

Match rate: 6/19 (32%). `yfinance` uses its own coarser, differently-named taxonomy — it's not simply GICS with different capitalization, and there's no reliable string-mapping shortcut that wouldn't need to be verified against all 11 GICS sectors and their edge cases anyway.

## Decision

Sector (and industry) classification for the fixed ~500-stock universe this project covers comes from a dedicated reference table — sourced from the Wikipedia S&P 500 constituent list (or an equivalent authoritative GICS source if that proves unreliable long-term) — ingested and refreshed periodically (index reconstitution happens a few times a year, not daily), not pulled from `yfinance`'s per-ticker `sector` field.

`yfinance` remains the source for everything it's actually good at: price data, P/E, P/B, EV/EBITDA, P/S, EPS, dividend yield. Only sector/industry classification moves to the dedicated reference.

## Consequences

- Ingestion (Phase 2) gains a second data source with a different refresh cadence than daily prices — needs its own scheduling, separate from `src/ingestion/prices.py` and `fundamentals.py`.
- The reference table becomes a small dependency the whole Screen feature relies on being correct — worth a dbt test asserting every ticker in the fundamentals table has a non-null sector from this reference, so a gap fails loudly instead of silently dropping a stock from its cohort.
- Scraping Wikipedia is fragile in the abstract (page structure could change), but the constituent list changes rarely and the ingestion script can validate row count (~500 ± a few) and fail loudly rather than silently ingesting garbage if the page structure ever breaks.
- This is a concrete example of why Phase 0's validation step existed — the original single-source design would have shipped a confidently wrong Screen feature with no visible symptom until someone happened to notice Apple wasn't grouped with Microsoft.
