# The Power BI layer of `dashboard_data/`

Built by `build_powerbi_layer.py` (~10 s, no solver) on top of
`31_scenario_grid.py` (~20 min, solver). The raw per-study mirrors built by
`build_dashboard_data.py` stay exactly where they are, for audit — this is an
additional clean layer, nothing was removed.

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 31_scenario_grid.py                      # solves the grid
python3 dashboard_data/build_dashboard_data.py   # the raw mirrors
python3 dashboard_data/build_powerbi_layer.py    # this layer + validation
```

---

## Conventions, applied everywhere in this layer

- **Every percentage-like value is a DECIMAL.** `0.142995` means 14.2995%. No
  `_%` column suffixes, no `_pp`, and **no percentage strings anywhere.** Power
  BI applies the display format.
- **ESG stays on its 0–100 scale**, because it is not a percentage.
- `profile` is exactly one of **`Risk Averse`**, **`Neutral`**, **`Risk Prone`**.
- `profile_rule` says how that profile was selected; `frontier_point` traces it
  back to the frontier.
- `strategy` names a backtested strategy: `Optimised Minimum Variance`,
  `1/N Equal Weight`, `Optimised Mandate (give up <=20% of max return)`, …
- **Long format, never wide.** No column-per-date, no column-per-frontier-point.
- **No `Unnamed: 0`.** Every index column is named for what it holds.
- Every row is readable on its own. No filename context needed.

The build **fails loudly** rather than shipping a violation: an unmapped
strategy label, a `_%` column, a percentage string or an unnamed index column
raises and stops the build.

---

## The canonical profile rule — resolved, not invented

The repo genuinely disagreed with itself. Holdings said Risk Prone was frontier
point 11; `profile_definitions.csv`, `23_scenario_matrix.py`, `analyze_risk.py`
and the deck said point 14. Two different portfolios wore the same label.

The rule that settles it already existed, in the **frozen**
`archive/our_model_frozen/19_freeze_v4.py` lines 101–107:

```python
deg = (top3 > 0.40) | (n_at_floor > 15)
ok  = frontier[~deg]
Risk Averse = argmin risk
Neutral     = argmax return/risk
Risk Prone  = argmax return AMONG NON-DEGENERATE POINTS
```

| Profile | Rule | Delivered frontier |
|---|---|---|
| Risk Averse | Minimum variance | point **0** |
| Neutral | Maximum return/risk ratio | point **8** |
| Risk Prone | Highest non-degenerate return | point **11** |

Why 12–14 are excluded:

| Point | Return | Risk | Top-3 weight | On the 1% floor | Degenerate |
|---|---|---|---|---|---|
| 11 | 15.97% | 12.77% | 33.8% | 10 | no |
| 12 | 16.52% | 14.38% | 34.0% | **16** | yes |
| 13 | 17.08% | 17.15% | **40.5%** | **21** | yes |
| 14 | 17.63% | 22.62% | **60.0%** | **23** | yes |

Point 14 is the unconstrained max-return corner: three positions pinned at the
20% cap and 60% of the budget in three stocks. A corner of the feasible set, not
a portfolio anyone would run.

**So `analyze_risk.py`'s plain `argmax(return)` was the outlier, and the
holdings files were right.** `31_scenario_grid.py` derives all three per
scenario; nothing is hard-coded, and the rule re-selects correctly when a
constraint changes (under no sector cap Risk Prone moves to point 12, because
which points are degenerate moves with the constraint set).

⚠ **This changes the deck.** `SustainaFund_interim_review.pdf` currently shows
point 14 as Risk Prone (17.63% / 22.62% / ratio 0.779) with a caveat box. Under
the canonical rule it should show point 11 (15.97% / 12.77% / ratio 1.250) and
the caveat box becomes unnecessary. Not changed here — see `HANDOFF.md`.

---

## Tables

### `scenarios/` — the model outputs, normalised

Relate these through `scenario_id`, `profile`, `frontier_point` and `stock`.

| Table | Rows | Grain |
|---|---|---|
| `scenario_catalog.csv` | 15 | one row per solved scenario, with its parameters |
| `portfolio_summary.csv` | 45 | scenario × profile |
| `portfolio_holdings.csv` | 1499 | scenario × profile × stock |
| `frontier_points.csv` | 225 | scenario × frontier_point |
| `frontier_weights.csv` | 7641 | scenario × frontier_point × stock |

`scenario_catalog.csv` carries every parameter as its own field:
`sector_cap`, `sector_cap_active`, `esg_min`, `esg_constraint_active`,
`esg_floor`, `country_cap`, `country_cap_active`, `region_cap`,
`min_holdings`, `weight_min`, `weight_max`, `tier1_excluded`,
`tier2_excluded`, `window_years`. An inactive cap is `NaN` with its
`*_active` flag `False`, so "no cap" and "a cap of 1.0" cannot be confused.

`portfolio_summary.csv` fields: `expected_return`, `risk`,
`return_risk_ratio`, `n_holdings`, `weighted_esg`, `min_esg_held`,
`max_position`, `min_position`, `top3_weight`, `n_at_floor`,
`europe_weight`, `us_weight`, `top_sector`, `top_sector_weight`,
`top_country`, `top_country_weight`.

`portfolio_holdings.csv` deliberately carries only `weight` and `amount_usd` —
country, sector, industry, region, ESG and expected return come from
`universe/stocks.csv` on `stock`, rather than being duplicated 1499 times.

`frontier_points.csv` includes `degenerate`, `top3_weight` and `n_at_floor`, so
a chart can show *why* the high-return end is excluded rather than just hiding
it.

**The 15 scenarios**

| Group | `scenario_id` |
|---|---|
| delivered | `base` |
| Tier 2 | `tier2_on` |
| **sector cap** | `sector_cap_none`, `sector_cap_20`, `sector_cap_25` (30% is `base`) |
| ESG threshold | `esg_unconstrained`, `esg_min_50`, `esg_min_60`, `esg_min_65`, `esg_min_75`, `esg_min_80` (70 is `base`) |
| country cap | `country_cap_20`, `country_cap_25`, `country_cap_30`, `country_cap_40` |

`esg_unconstrained` is the constraint switched off entirely, not `ESG_MIN = 0`:
`esg_constraint_active` is `False` and `esg_min` is `NaN`.

### `universe/stocks.csv` — the stock dimension, 1093 rows

`stock` (key), `region`, `country`, `sector`, **`industry`**, `sector_gics`,
`esg`, `esg_band`, `expected_return`, `risk_std`, `has_price_data`,
`passes_esg_floor_30`, `in_model_universe`, `esg_ge_70`.

**Industry: yes, we have it.** `TR.GICSIndustryGroup` from the LSEG export —
**25 groups, all 1093 tickers, no gaps** — parsed by
`27_lseg_esg_sector_update.py`. It is a **display dimension only**: the model
still optimises on the current sector taxonomy, and nothing about adding
industry here changes an optimisation. `sector_gics` is exposed alongside
`sector` so a slicer can use either without implying the model switched
taxonomy. Nothing is inferred from sector.

Three membership flags rather than one, because **1093 stocks entered and 1077
reached the model** — 6 lost price series, 10 below the ESG floor.

`esg_band` is a pre-cut label (`<30`, `30-50`, `50-60`, `60-70`, `70-80`, `80+`)
so ESG banding does not have to be re-derived in DAX.

### `robustness/` — 10Y / 5Y / 3Y, with holdings and stability

Built by `32_robustness_windows.py`. **μ and Σ are RE-ESTIMATED per window**,
not just re-solved — the window is the input being varied, so shortening it
changes both the expected returns and the covariance. Estimation mirrors
`20_dividend_adjusted_pipeline.py` exactly (20-factor PCA Σ, James-Stein μ),
and the gate proves it: at 10 years the rebuild reproduces the shipped
`expected_return_v4.csv` and `covariance_matrix_v4.csv` to **1.7e-16** and
**1.8e-15**. The shorter windows therefore measure the window, not the rebuild.

| Table | Rows | Grain |
|---|---|---|
| `window_summary.csv` | 9 | window × profile |
| `window_holdings.csv` | 338 | window × profile × stock |
| `window_frontiers.csv` | 45 | window × frontier_point |
| `stability.csv` | 9 | window × profile, against the 10-year book |
| `estimation.csv` | 3 | what each window's estimation actually saw |
| `gate.csv` | 1 | the 10-year reproduction check |

Profiles are re-selected per window with the canonical rule, not carried over —
which matters: on 3 years Neutral moves to frontier point 6 and Risk Prone to
point 12, because the degenerate set moves with the estimate.

| Window | Profile | Return | Risk | Ratio | Held |
|---|---|---|---|---|---|
| 10 | Risk Averse | 9.92% | 9.26% | 1.072 | 43 |
| 10 | **Neutral** | **14.30%** | **10.63%** | **1.346** | 30 |
| 10 | Risk Prone | 15.97% | 12.78% | 1.249 | 30 |
| 5 | Neutral | 17.47% | 9.32% | 1.874 | 38 |
| 3 | Neutral | **25.73%** | **7.93%** | **3.244** | 38 |
| 3 | Risk Prone | **35.93%** | 13.66% | 2.630 | 30 |

⚠ **Shorter windows look better and are worse.** A 3-year estimate claims
Neutral earns 25.73% at 7.93% risk, a return/risk ratio of 3.24 against the
10-year 1.35. Nothing improved: μ's range widens from 2.7%–19.1% on 10 years to
**−9.8%–46.1%** on 3, and the optimiser buys whatever that noise flattered.
`04a` recorded the same mechanism (max return 38.8% on 10y → 85.6% on 3y). If a
dashboard shows these side by side, the short windows must be labelled as
estimation error, not as an alternative recommendation.

`stability.csv` is the point of the exercise:

| Window | Profile | Names shared with 10Y | Jaccard | Active share | Weight corr |
|---|---|---|---|---|---|
| 5 | Risk Averse | 30 of 50 | 0.476 | 0.466 | 0.425 |
| 5 | Neutral | **15 of 38** | 0.283 | 0.645 | 0.164 |
| 5 | Risk Prone | 9 of 30 | 0.176 | 0.723 | 0.055 |
| 3 | Risk Averse | 20 of 49 | 0.278 | 0.643 | 0.084 |
| 3 | Neutral | **11 of 38** | 0.193 | 0.755 | **−0.019** |
| 3 | Risk Prone | **7 of 30** | 0.132 | **0.910** | **−0.225** |

`active_share` is half the sum of absolute weight differences: the fraction of
capital placed differently. So the 3-year Risk Prone book puts **91% of the
budget somewhere else** than the 10-year one, and its weights correlate
**−0.225** with it — no relationship at all.

Two things worth carrying to the defence. The 3-year Risk Averse row (Jaccard
0.278, active share 0.643) reproduces `03e`'s previously reported "Jaccard 0.27,
64% of capital placed differently" almost exactly, which cross-checks both.
And **Risk Averse is the most stable profile at every window while Risk Prone
is the least** — the third independent analysis to land on the min-variance end
being the robust one, after `stress_test/` and `backtest_profiles/`.

### `backtest_standard/` — walk-forward, standardised

Both runs in one set of tables, distinguished by `run`:
`walk-forward min-variance (script 21)` and
`walk-forward profiles (script 26)`.

| Table | Grain |
|---|---|
| `summary.csv` | run × strategy × `cost_adjusted` |
| `equity_curves.csv` | run × strategy × date × `indexed_wealth` |
| `subperiods.csv` | run × strategy × period |
| `diagnostics.csv` | run × metric, with `is_decimal_fraction` |

`indexed_wealth` stays as indexed wealth from 1.0, as asked. `cagr`,
`volatility`, `max_drawdown` are decimals; `sharpe` and `final_multiple` are
plain ratios.

⚠ **The script-21 backtest tests minimum variance, not Neutral.** It is
labelled `Optimised Minimum Variance` and must not be presented as validation
of the recommended book. The nearest out-of-sample test of a return-seeking
profile is `Optimised Mandate (give up <=20% of max return)` in the script-26
run — see `backtest_profiles/README.md`, whose headline is that **no book beats
1/N significantly** (t = −0.87, +0.60, +1.12).

### `stress_standard/` — crisis windows

`panelA_windows.csv` carries `panel = "A (in-sample, descriptive)"` and
`panelB_windows.csv` `panel = "B (point-in-time, the actual test)"`, so the two
cannot be mixed in a visual by accident. **Panel B is the test; Panel A
describes the delivered book and had hindsight.**

`covid_attribution.csv` and `worst_windows.csv` now carry explicit `profile`,
`profile_rule` and `window` / `lookback_trading_days` columns — previously you
had to know the filename to know what a row meant.

`panelB_top_names.csv` explodes the pipe-joined holdings string into rows, but
**`weight` is `NaN`**: the source file only stored the top-8 *names*. Real
point-in-time weights need the stress test re-run with a weight dump — see
"Still to do".

### `benchmark_standard/` — the 1/N benchmark, 2015–2025

`summary.csv`, `curves.csv` (long), `annual.csv` (long), `windows.csv`,
`feasibility.csv`, all with a `strategy` label.

Two things to carry onto any chart. **Rebalancing frequency moves the benchmark
by 0.9 pp of CAGR** (daily 15.67%, buy-and-hold 15.35%, monthly 14.80%), so
label which 1/N is plotted; `1/N Equal Weight (model universe, monthly)` is the
default comparator. And **no 1/N variant is admissible under the brief** —
`feasibility.csv` records which condition each one breaks. It is a reference,
not an alternative portfolio.

---

## Validation

`build_powerbi_layer.py` clears the folders it owns before rebuilding, so a
vanished source cannot leave a stale destination, and then checks:

- universe is 1093 rows with 1077 in the model universe, no duplicate keys, no
  missing industry
- every `profile` value is one of the three canonical names
- weights sum to 1 within 1e-3, per (scenario, profile) **and** per (scenario,
  frontier point)
- no duplicate (scenario, profile, stock) or (scenario, point, stock) keys
- every held stock exists in the universe table
- every summary row points at a frontier point that exists in its own scenario
- every scenario has 15 frontier points (warns if not)
- no `_%`/`_pp` columns, no percentage strings, no unnamed index columns

Current state: **all checks passed.**

---

## What Power BI should and should not do

Country / sector / industry / region / ESG-band slicers **filter the
visualised holdings**. They do not re-optimise, and they must not be presented
as constraints.

A selection only represents an actual optimisation **constraint** if it has been
solved in Python/Xpress and appears as a `scenario_id`. That is what the ESG
threshold, sector cap, country cap and Tier 2 scenarios are for. Everything
requiring the covariance, the frontier or the solver is precomputed here.

---

## Still to do

Honestly listed rather than implied as done:

1. **`stress/panelB_holdings.csv` with real weights.** Needs
   `stress_test/25_crisis_stress_test.py` re-run with a weight dump (~7 min).
2. **A Neutral walk-forward backtest.** Partly answered already:
   `backtest_profiles/` runs a return-seeking mandate out of sample over 31
   rebalances. A literal max-return/risk-per-rebalance version would need a
   frontier at each of the 31 rebalances rather than two solves.
3. **`sensitivity/tier2_comparison.csv`** in the raw mirror still contains
   percentage strings. It is outside this layer (the scenario tables supersede
   it) and the validator only guards this layer, but it should be regenerated.
