# FINAL — data cleaning, inputs and results

Everything needed to reproduce the cleaned data and the model results from the
raw price file. Self-contained: replace what you have with this.

## Run order

| # | Script | Reads | Writes | Time |
|---|---|---|---|---|
| 1 | `code/02a_esg_and_price_eda_cleaning.py` | `shares_full.csv`, `stockprices_full.csv` | `shares_imputed.csv`, `shares_excluded.csv`, `prices_clean.csv` | ~1 min |
| 2 | `code/20_dividend_adjusted_pipeline.py` | `prices_lseg_dividend_adjusted.csv`, `shares_full.csv`, `fx_rates_ecb.csv` | `expected_return_v4.csv`, `covariance_matrix_v4.csv`, `per_stock_risk_v4.csv` | ~3 min |
| 3 | `code/Model2_ori.py` | the three files above + `sectors.xlsx`, `shares_imputed.csv` | `efficient_frontier_model2_<tag>.csv` + weights | ~15 s |

Step 2 is the whole cleaning chain in one script — gap handling, USD conversion,
discontinuity truncation and the estimator. Step 1 is still needed because it
produces the ESG imputation, which step 2 does not touch.

`data/covariance_matrix_v4.csv` is included (23 MB), so **step 3 runs as shipped**
— you only need steps 1 and 2 if you want to rebuild the inputs from scratch.

Two raw price files are **not** included (LSEG-derived, 21 and 49 MB): the
original `stockprices_full.csv` from `data_full`, and
`prices_lseg_dividend_adjusted.csv` — the one you produced. You need them only
for steps 1 and 2; put them next to the scripts.

Diagnostics, optional, none of them write model inputs:

| Script | Question it answers |
|---|---|
| `code/02b_price_eda_cleaning.py` | how long are the internal price gaps? (all exactly 1 day) |
| `code/10_outlier_relative.py` | fixed 50% threshold vs a per-stock 5-sigma rule |
| `code/12_fx_model_free.py` | is the USD conversion necessary at all? (model-free test) |
| `code/03a_fx_convert.py` | the standalone USD conversion, superseded by step 2 |

You need an Xpress licence only for step 3. Set `XPAUTH_PATH` to it.

## Excel files

**`data/FINAL_stock_data.xlsx`**

`data/` also holds the three model inputs as CSV — `expected_return_v4.csv`,
`per_stock_risk_v4.csv`, `covariance_matrix_v4.csv` — plus `shares_imputed.csv`,
`shares_excluded.csv`, `shares_full.csv`, `sectors.xlsx` and the cached ECB rates.

| sheet | contents |
|---|---|
| `stock_data` | one row per stock, all 1093: region, country, sector, exchange suffix, **listing currency**, ESG raw and imputed, whether it was imputed, observation count, expected return, risk, whether it survived into the final universe, and **why if it did not** |
| `cleaning_log` | eleven decisions: what was done, why, and which script does it |
| `fx_rates_last_year` | the last 260 days of ECB rates, as a sanity check on the conversion |

**`results/FINAL_portfolios.xlsx`** — 10 sheets: `summary`, `tier2_comparison`,
the two frontiers, and the six portfolios (three risk profiles × two runs) with
weight, USD amount, sector, country, ESG and expected return per holding.

## What the cleaning actually does

1. **ESG** — 49 of 1093 missing, imputed with the **25th percentile within the
   region**, not the mean, so a missing score is not rewarded with an optimistic
   one. `shares_excluded.csv` drops them instead, for sensitivity.
2. **Price gaps** — forward-filled, but never before a stock's first trading day
   (that would be backfilling a pre-IPO price). All internal gaps are exactly one
   trading day, verified on consecutive runs rather than on per-stock totals.
3. **Dividends** — the source is now total-return, not closing prices. Median
   expected return rises **7.80% → 10.39%**, and the increase is ordered by
   dividend yield across sectors (Energy +3.89pp … Technology +1.18pp), which is
   the check that the file is genuine. Volatility is unchanged.
4. **Currencies** — converted to USD at **daily** ECB rates. Not one rate:
   converting at a single rate would multiply each series by a constant, the
   constant cancels in a ratio, and you would get the local returns straight back.
   Because `ln(P_usd) = ln(P_local) + ln(fx)` the FX term is additive, barely
   moves μ (<0.3pp, currencies offset) but puts a shared factor into the
   covariance — a local-currency Σ understated the min-variance book's risk by
   19.7%.
5. **Discontinuities** — `ZEG.L` and `BMPS.MI` have a run of identical closes
   (trading suspended) followed by a large jump. That is a corporate action, so a
   return computed across it is not a return: a ZEG.L holder did not gain 352%,
   the share count changed. History starts after the break; neither stock is
   dropped.
6. **Outliers** — flagged, not removed. A 5σ per-stock rule fires on 0.31% of all
   observations and catches mostly genuine events, so it is a reporting tool, not
   an error detector. Only the two above are actual data defects.
7. **Estimation** — James-Stein shrinkage on μ with intensity set by sample size,
   and a 20-factor PCA covariance that keeps every stock and is PSD by
   construction.

## Six stocks are missing from the source file

`HOLN.S`, `URW.PA`, `EA.OQ`, `AVB.N`, `EQR.N`, `HWM.N` — 2870 of 2870 values
absent in `prices_lseg_dividend_adjusted.csv`, where the previous file had a full
history. Three of the six are REITs, whose adjustment factors are the largest, so
the extraction most likely failed on them.

They are **dropped** (1093 → 1087), not back-filled from the unadjusted file: an
unadjusted series carries a ~3pp lower return, so the optimiser would penalise
them for a data defect rather than for their quality. `EA.OQ` was held at ~1% in
the previous risk-averse book. **Worth re-extracting.**

## Fixes applied to Model2_ori.py

Defects only; the design and defaults are unchanged.

| # | Defect | Effect before |
|---|---|---|
| 1 | four Tier-2 tickers absent from the dataset | the screen excluded **6 of 10**. `BA.L`→`BAES.L`, `HO.PA`→`TCFP.PA`, `LDO.MI`→`LDOF.MI`, `SAAB-B.ST`→`SAABb.ST`. `BA.L` was the risky one — `BA.N` here is **Boeing** |
| 2 | `SCENARIO_TAG` hand-edited | the second run **overwrote** the first. Now derived by `scenario_tag()` from the active toggles |
| 3 | `MIP_GAP = 0.01` | a cheap constraint's cost read ~**2×** its true value |
| 4 | `mode="max_return"` compared a variance against `risk_cap` unsquared | asking for 12% risk returned a **22.29%** portfolio; the cap never bound. Now `risk_cap ** 2` |
| 5 | inputs pointed at the 31 Aug files | local currency, 997-stock complete-case universe |

## Current results

| | risk-averse | neutral | risk-prone |
|---|---|---|---|
| expected return | 9.92% | **14.32%** | 16.53% |
| risk | 9.26% | 10.64% | 14.41% |
| return / risk | 1.07 | **1.35** | 1.15 |
| holdings | 43 | 30 | 30 |
| top sector | Consumer Defensive 30.0% | 27.1% | Healthcare 23.9% |

Excluding Tier 2 costs **−0.019 pp** of annual return on average, and the whole
of it sits at the minimum-variance corner. The same conclusion held on closing
prices (−0.016 pp), so it does not depend on the dividend treatment — the
contested policy can be decided on principle.

**Still open:** the sector cap holds Consumer Defensive to exactly 30.00%, but
**Switzerland reaches 46.8%** of the risk-averse book — Swiss cantonal banks and
real estate. A sector cap cannot see that, because it is not one sector. A 25%
country cap held it to 25.0% at a cost of 0.156 pp. That is the most obvious next
addition.
