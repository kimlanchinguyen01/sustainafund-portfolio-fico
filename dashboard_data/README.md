# dashboard_data — everything a dashboard needs, in one place

465 KB, 31 CSVs, no solver required to read any of them. Rebuilt by
`build_dashboard_data.py` (~5 s) from result files elsewhere in the repo, so
this folder can always be regenerated and can never disagree with the model.

```bash
python3 dashboard_data/build_dashboard_data.py
```

Every file except `universe/stocks.csv` is a straight copy under a stable name;
the source of each is listed below. `universe/stocks.csv` is the one table built
here, because a joined per-stock view did not exist anywhere.

**All numbers are `tier2off`** (conventional defense kept) unless the filename
says `tier2on`. That is the delivered configuration.

---

## Start here

| File | Rows | What it drives |
|---|---|---|
| `universe/stocks.csv` | 1093 | every filter, scatter and colour dimension |
| `frontier/frontier_points.csv` | 15 | the efficient-frontier chart |
| `portfolios/summary.csv` | 6 | the three-profile comparison cards |
| `portfolios/neutral.csv` | 30 | the recommended book's composition |
| `backtest/equity_curves.csv` | 2023 | the out-of-sample equity chart |
| `stress/panelB_windows.csv` | 20 | the crisis-window table |

---

## universe/

### `stocks.csv` — one row per stock, 1093 rows

| Column | Type | Notes |
|---|---|---|
| `stock` | str | ticker, the join key everywhere else |
| `region` | str | `Europe` / `United States` |
| `country` | str | 17 distinct values |
| `sector` | str | 11 sectors, missing filled as `Unknown` |
| `esg` | float | 0–100, 49 values imputed |
| `expected_return` | float | annual **decimal** (0.1488 = 14.88%), James-Stein shrunk |
| `risk_std` | float | annual **decimal** standard deviation |
| `has_price_data` | bool | 1087 true — survived the price pipeline |
| `passes_esg_floor` | bool | 1083 true — individual ESG >= 30 |
| `in_model_universe` | bool | **1077 true — what Model 2 actually optimised over** |
| `weight_risk_averse_%` | float | percent, 0 if not held |
| `weight_neutral_%` | float | percent, 0 if not held |
| `weight_risk_prone_%` | float | percent, 0 if not held |

Three flags rather than one because **1093 stocks entered and 1077 reached the
model**, and a dashboard that shows either number as the other is wrong. 6 lost
price series (`URW.PA`, `AVB.N`, `EQR.N`, `HOLN.S`, `EA.OQ`, `HWM.N`) and 10
fell below the ESG floor.

Note the unit split, it is the easiest mistake to make here: `expected_return`
and `risk_std` are **decimals**, every `*_%` column is already **percent**.

Sources: `shares_imputed.csv`, `sectors.xlsx`, `expected_return_v4.csv`,
`per_stock_risk_v4.csv`, `covariance_matrix_v4.csv` (header only),
`results_chloe/portfolio_tier2off_*.csv`.

---

## frontier/

| File | Rows | Source |
|---|---|---|
| `frontier_points.csv` | 15 | `results_chloe/efficient_frontier_model2_sec30_tier1_tier2off_esgfloor30.csv` |
| `frontier_weights.csv` | 1077 | `..._weights_sec30_tier1_tier2off_esgfloor30.csv` |
| `frontier_points_tier2on.csv` | 15 | the tier2-on variant |
| `frontier_weights_tier2on.csv` | 1077 | the tier2-on variant |

`frontier_points.csv`: one row per frontier point, in increasing return order.
Plot `portfolio_risk` against `portfolio_return` — both **decimals**.
`target_beta` is the return floor the point was solved at.
`n_selected` is the holding count. `esg_weighted` is the weighted ESG, which
sits at exactly 70.00 at every point (the constraint always binds).
Also carries `weight_region_*` and `weight_sector_*` columns for a
composition-versus-risk chart.

`frontier_weights.csv`: stocks as rows, `beta_0` … `beta_14` as columns, values
are **decimal** weights. Column `beta_N` corresponds to row N of
`frontier_points.csv`. **`beta_8` is the recommended neutral book**, `beta_0`
the minimum-risk corner, `beta_14` the maximum-return corner.

---

## portfolios/

| File | Rows | Contents |
|---|---|---|
| `summary.csv` | 6 | the three profiles × tier2 off/on, one row each |
| `risk_averse.csv` | 42 | holdings |
| `neutral.csv` | 30 | holdings — **the recommendation** |
| `risk_prone.csv` | 30 | holdings |
| `*_tier2on.csv` | 41/30/30 | the same three with defense excluded |
| `profile_definitions.csv` | 3 | how each profile was selected, with `target_beta` |

Holdings files: index is the ticker, then `weight_%`, `amount_USD` (of $100M),
`Sector`, `Country`, `Region`, `ESG`, `exp_return_%`. Weights sum to 99.999 —
rounding in the source file, not a bug; renormalise if the dashboard needs
exactly 100.

`summary.csv` gives `ret_%`, `risk_%`, `ratio`, `n`, `ESG`, `min_ESG_held`,
`top_sector` / `top_sector_%`, `top_country` / `top_country_%`, `wEurope_%`,
`max_pos_%` and `RHMG_%` (Rheinmetall, 0 everywhere — the Tier 1 screen).

⚠ **`summary.csv` and `profile_definitions.csv` disagree about risk-prone.**
`summary.csv` uses frontier point **11** (15.97% at 12.77%, ratio 1.250);
`profile_definitions.csv`, the deck, and every other artefact use point **14**
(17.63% at 22.62%, ratio 0.779), which is what "maximum return" means. This is
open item 6 in `HANDOFF.md`. **Use `profile_definitions.csv` for risk-prone**
until it is resolved; risk-averse and neutral agree in both files.

---

## sensitivity/

| File | Rows | What it shows |
|---|---|---|
| `scenario_matrix.csv` | 24 | 8 constraint configurations × 3 profiles — the ESG/sector/Tier-2 cost table |
| `tier2_comparison.csv` | 8 | cost of excluding conventional defense, along the frontier |
| `country_cap_frontier.csv` | 75 | every frontier point at cap off / 20 / 25 / 30 / 40% |
| `country_cap_cost.csv` | 60 | per-point cost of each cap, in risk **and** in return |
| `country_cap_profiles.csv` | 15 | the three profiles at each cap level |
| `mandate_sweep.csv` | 14 | profiles stated as mandates ("give up at most X% of max return") |
| `top_countries.csv` | 18 | six largest countries in each profile |

`country_cap_cost.csv` carries both framings and they differ by an order of
magnitude: `d_risk_pp` is the risk cost at matched return,
`d_ret_pp_at_matched_risk` the return cost at matched risk. The frontier is
~10x steeper at the min-risk end, so quote the one that fits the question.

`mandate_sweep.csv`: `reltol` is the fraction of maximum return given up.
`reltol = 0` reproduces the max-return corner exactly.

The country cap is **off** in the delivered model. These files describe what
turning it on would cost — see `results_country_cap/README.md`.

---

## backtest/  (walk-forward, out-of-sample)

Source: `results_chloe/backtest/`. Produced by
`pipeline/21_backtest_walkforward.py`. **Tests the minimum-variance book, not
the neutral recommendation** — rolling 3-year window, quarterly rebalance,
2018-04 to 2025-12.

| File | Rows | Contents |
|---|---|---|
| `equity_curves.csv` | 2023 | daily `optimised` and `equal_weight`, both indexed to 1.0 |
| `summary.csv` | 3 | CAGR, vol, Sharpe, maxDD, final multiple |
| `subperiods.csv` | 7 | six regimes plus FULL, optimiser vs 1/N |
| `rebalances.csv` | 31 | per rebalance: eligible, held, predicted risk, ESG, turnover |
| `diagnostics.csv` | 13 | metric/value pairs, including predicted vs realised risk |

The headline is honest and negative: Sharpe 0.835 against 1/N's 0.866. The real
edge is volatility, −22% overall.

---

## stress/  (crisis windows)

Source: `stress_test/results/`. Produced by
`stress_test/25_crisis_stress_test.py`. Full write-up in
`stress_test/README.md` — **read it before putting these on a slide**, because
the two panels disagree by design.

| File | Rows | Contents |
|---|---|---|
| `panelA_windows.csv` | 28 | delivered books × 7 windows — **IN-SAMPLE** |
| `panelB_windows.csv` | 20 | point-in-time books × 4 testable windows — the real test |
| `panelB_portfolios.csv` | 16 | what each point-in-time solve held, plus `solstatus` |
| `panelB_not_testable.csv` | 2 | the two windows with no usable history, and why |
| `covid_attribution.csv` | 30 | per-stock contribution to the COVID drawdown |
| `worst_windows.csv` | 5 | worst 60-day stretches, found from the data |

**Do not show Panel A as a stress test.** Mu and Sigma were estimated on
2015–2025, which contains every one of those crises. Panel A describes the
delivered book; Panel B is the test. If the dashboard shows both, label them.

`panelB_windows.csv` has `pred_risk_%` next to realised `vol_%`. The ratio is
the most useful single number in this folder: **1.83× in 2018 Q4, 1.44× in 2022,
6.71× in the COVID crash.**

Two rows in `panelB_portfolios.csv` have `solstatus = FEASIBLE` rather than
`OPTIMAL` — the `risk_averse` solves at 2020-02-19 hit the 120 s limit. Flag
them if the dashboard surfaces that book.

---

## Not here, deliberately

| Wanted? | Where it is | Why not copied |
|---|---|---|
| covariance matrix | `covariance_matrix_v4.csv`, `FINAL_data_cleaning/data/` | 24 MB; only the shipped copy is in git |
| daily price history | `pipeline/prices_div_usd.csv` | 52 MB, gitignored, LSEG-derived |
| raw prices | `data/data_full/stockprices_full.csv` | 22 MB, gitignored |
| the PDF deck | `SustainaFund_interim_review.pdf` | not data |

If the dashboard needs per-stock price charts it needs `prices_div_usd.csv`,
which is not in git. Rebuild with `pipeline/20_dividend_adjusted_pipeline.py`
or ask Chloe. Everything else here is self-contained.

## Provenance

| Concept | Value |
|---|---|
| Universe | 1093 stocks in, 1077 optimised |
| Prices | USD, dividend-adjusted (total return), 2015-01-01 to 2025-12-31 |
| Expected return | James-Stein shrunk, annualised |
| Covariance | 20-factor PCA, PSD by construction |
| Model | MIQP in FICO Xpress 9.9.1 / optimizer 47.01.02 |
| Budget | $100,000,000 |
| Constraints | 1–20% per holding, >= 30 holdings, region <= 60%, sector <= 30%, weighted ESG >= 70, per-stock ESG >= 30, Tier 1 weapons excluded |
