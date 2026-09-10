"""
Phase 0 validation script (see docs/architecture.md Section 2.6). Exploratory,
not application code -- the real scoring engine lands in src/domain in Phase 5.

Pulls real fundamentals for a sample of S&P 500 stocks across sectors,
computes the robust z-score from architecture.md Section 2.1 by hand, and
checks:
  1. Does the math produce numbers that match intuition for well-known stocks?
  2. How often are P/E, P/B, EV/EBITDA, P/S actually available/meaningful?
  3. Does yfinance's `sector` field match Wikipedia's official GICS Sector?

This run found two real issues, both now reflected in docs/architecture.md:
  - AAPL's inflated P/B alone skewed its composite score -> added a +/-4 clip
    before averaging (Section 2.1).
  - yfinance's `sector` field only matched official GICS names 32% of the
    time -> sector now comes from a dedicated reference table instead
    (ADR 0004: docs/adr/0004-sector-classification-source.md).

Re-run at full sector size in Phase 5 before pinning results as permanent
unit tests -- this sample (6-7 tickers/sector) is too small to trust as final.

Outputs (checked into docs/validation/ alongside this script):
  - sp500-constituents-<date>.csv  Wikipedia S&P 500 list snapshot used
  - phase0-raw-sample.csv          raw yfinance pull for the 19 sampled tickers
  - phase0-zscores.csv             computed z-scores / composite per stock
"""
import time
import numpy as np
import pandas as pd
import yfinance as yf

SAMPLE = {
    "Information Technology": ["AAPL", "MSFT", "NVDA", "ORCL", "CSCO", "ADBE", "INTC"],
    "Health Care": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY"],
    "Utilities": ["NEE", "DUK", "SO", "AEP", "ED", "EXC"],
}

sp500 = pd.read_csv("../docs/validation/sp500-constituents-2026-09-09.csv")
wiki_sector = dict(zip(sp500["Symbol"].str.replace(".", "-", regex=False), sp500["GICS Sector"]))

rows = []
for sector, tickers in SAMPLE.items():
    for t in tickers:
        try:
            info = yf.Ticker(t).info
        except Exception as e:
            print(f"{t}: FAILED {e}")
            continue
        rows.append({
            "ticker": t,
            "expected_sector": sector,
            "yf_sector": info.get("sector"),
            "yf_industry": info.get("industry"),
            "wiki_sector": wiki_sector.get(t),
            "trailingPE": info.get("trailingPE"),
            "priceToBook": info.get("priceToBook"),
            "evToEbitda": info.get("enterpriseToEbitda"),
            "priceToSales": info.get("priceToSalesTrailing12Months"),
        })
        time.sleep(0.3)

df = pd.DataFrame(rows)
df.to_csv("../docs/validation/phase0-raw-sample.csv", index=False)
print("=== RAW DATA ===")
print(df.to_string())

# --- Check 1: sector label agreement ---
print("\n=== SECTOR LABEL CHECK (yfinance vs Wikipedia GICS) ===")
df["sector_match"] = df["yf_sector"] == df["wiki_sector"]
print(df[["ticker", "yf_sector", "wiki_sector", "sector_match"]].to_string())
print(f"\nMatch rate: {df['sector_match'].mean():.0%}")

# --- Check 2: metric coverage ---
print("\n=== METRIC COVERAGE (non-null, positive) ===")
for m in ["trailingPE", "priceToBook", "evToEbitda", "priceToSales"]:
    valid = df[m].notna() & (df[m] > 0)
    print(f"{m}: {valid.sum()}/{len(df)} usable ({valid.mean():.0%})")

# --- Check 3: robust z-score by hand, per sector ---
print("\n=== ROBUST Z-SCORES (median/MAD) ===")


def robust_z(series):
    med = series.median()
    mad = (series - med).abs().median()
    scaled_mad = 1.4826 * mad
    if scaled_mad == 0:
        return pd.Series(np.nan, index=series.index)
    return (series - med) / scaled_mad


results = []
for sector, group in df.groupby("expected_sector"):
    metrics_z = {}
    for m in ["trailingPE", "priceToBook", "evToEbitda", "priceToSales"]:
        vals = group[m].where(group[m] > 0)  # exclude negative/meaningless
        z = robust_z(vals)
        metrics_z[f"z_{m}"] = z
    zdf = pd.DataFrame(metrics_z, index=group.index)
    zdf["composite"] = zdf.mean(axis=1, skipna=True)
    combined = pd.concat([group[["ticker", "expected_sector"] + ["trailingPE", "priceToBook", "evToEbitda", "priceToSales"]], zdf], axis=1)
    results.append(combined)

result_df = pd.concat(results)
print(result_df.sort_values("composite", ascending=False).to_string())
result_df.to_csv("../docs/validation/phase0-zscores.csv", index=False)
