# 1_data_preparation/ — input preparation and the analysis behind it

These scripts build the inputs that `2_optimisation_model/code/Main_model.py` consumes, and they are the
record of how each choice was established. Numbering follows the order findings
were made, not a required run order.

To reproduce the model inputs, only four steps are needed:

| step | script | produces | time |
|---|---|---|---|
| 1 | `02a_esg_and_price_eda_cleaning.py` | `prices_clean.csv`, imputed / excluded shares | ~1 min |
| 2 | `03a_fx_convert.py` | `prices_clean_usd.csv` + cached ECB rates | ~1 min |
| 3 | `13_truncate_discontinuities.py` | `prices_clean_usd_v3.csv` | <1 min |
| 4 | `14_refreeze_v3.py` | `expected_return_v3.csv`, `covariance_matrix_v3.csv` | ~2 min |

`Model2.py` is the audit baseline, unchanged since 31 August. Every later model
asserts that it reproduces `Model2.py` exactly when its own additions are
disabled.

Everything else below is why the inputs look the way they do.

## Script map — what each one answers

Numbering is the order things were established, not a required run order.

### 03 — currency
| script | question | answer |
|---|---|---|
| `03a_fx_convert.py` | convert prices to USD | 8 currencies across 19 exchanges; `.L` is quoted in pence (cosmetic, cancels in log-returns) |
| `03b_usd_return_risk.py` | mu / sigma / Sigma in USD | control: reproduces v2's `01c` output to `9.7e-17`, so any later difference is the currency alone |
| `03c_frontier_usd.py` | does the frontier move? | min-var risk was understated 20% (8.46% believed vs 10.13% actual); the 60% region cap stopped binding; **+5.71pp of return available at matched risk** |
| `03d_universe_effect.py` | cost of the complete-case exclusion | +0.28pp mean at matched risk (measured on the 5y window as a proxy) |
| `03e_composition_stability.py` | does it change the *portfolio*? | yes — Jaccard 0.86, active share 7.6%; but an ordinary 5y↔10y window change gives Jaccard **0.28** |

### 04-05 — the risk model
| script | question | answer |
|---|---|---|
| `04a_factor_model.py` | keep all stocks via a factor model | 1093 of 1093; Sigma reproduces the v2 shrunk matrix where they overlap (off-diag corr **0.982**, per-stock sigma corr **1.000**) |
| `04b_frontier_factor.py` | does shrinkage fix the instability? | **no** — Jaccard 0.27 vs 0.28 |
| `05a_single_index.py` | Sharpe single-index model (team P1) | 1093 stocks, PSD, cond 1880 — but understates portfolio risk 13.6% mean, **39.9%** at the min-risk end |
| `05b_risk_validation.py` | why | the per-stock check is an OLS identity and cannot fail; residual correlations are +0.11 within region, -0.11 across, and the model sets all of them to zero |
| `05c_multifactor.py` | + region factor (team P2) | absorbs the region structure completely (spread +0.2237 → **-0.0010**) and leaves the risk error at **-13.1%** |
| `05d_factor_count.py` | how many factors, then | sharp cliff between k=2 (-17.6%) and k=5 (+3.9%); **k=20** is the smallest with no understatement anywhere |

### 06 — stability and ESG
| script | question | answer |
|---|---|---|
| `06a_bootstrap_robust.py` | resampled ("robust") weights | within a window the bootstrap is stable (top selection frequency **1.00**); across windows even the >=90% core disagrees (Jaccard **0.28**) → regime change, not sampling noise |
| `06b_esg_sensitivity.py` | what does ESG cost | ESG>=70 costs **0.07pp**; marginal cost per 5 points: 0.09 → 0.75 → 2.38pp, so 70 sits at the knee of the curve |

### 07-12 — finalising and challenges
| script | question | answer |
|---|---|---|
| `07_final_portfolio.py` | pick three profiles | exposed two problems: 45.4% in Switzerland, and a degenerate corner solution at the frontier endpoint |
| `08_country_cap.py` | add a country cap | 25% costs 0.06pp mean; Switzerland 45.4% → 25.0% |
| `09_lw_on_factor.py` | Ledoit-Wolf on the factor Sigma (team P3) | delta chosen **out of sample**; all delta within 0.56pp, no improvement over the frozen delta=1.0 |
| `10_outlier_relative.py` | relative vs fixed outlier threshold | relative rule strictly dominates, but 5 sigma fires on 0.31% of all observations — too loose to be a data-error detector; found **ZEG.L** and BMPS.MI |
| `11_refreeze_clean.py` | first attempt: drop ZEG.L entirely | superseded by `13`-`14`, which truncate instead of dropping |
| `12_fx_model_free.py` | is the currency conversion needed at all | model-free: same holdings realised **8.04% local vs 8.99% USD**; var(fx) is **17.6%** of total USD variance |
| `13_truncate_discontinuities.py` | find and cut trading discontinuities | exactly 2 of 1093: ZEG.L (38 identical closes, then +352% — reverse takeover) and BMPS.MI (**219** identical closes, then -69.8% — the 2016-17 recapitalisation). History starts after the break; neither stock is dropped |
| `14_refreeze_v3.py` | re-estimate; produces the current model inputs | Jaccard 0.94-0.97 vs v2, active share 2.7-2.9%; ZEG.L re-enters as a 557-day listing |
| `15_model1_linear.py` | **Model 1**, the linear risk measure | control: identical constraint set (`max\|dw\| = 0.00e+00`), only the objective differs. Model 1 carries **+19.2% more true risk** at matched return, and always sits at the 30-stock floor because diversification is invisible to its objective |

---

## Model 1 vs Model 3 — linear versus quadratic risk

Both routes to portfolio risk are now built, with an identical constraint set
(asserted: `max|dw| = 0.00e+00` when the same builder is given the quadratic
objective).

| | Model 1 (MILP) | Model 3, archived (MIQP) |
|---|---|---|
| objective | `min sum_i w_i * sigma_i` | `min w' Sigma w` |
| sees correlation | no | yes |
| true risk at matched return | **+19.2% higher** (range +9.7% .. +23.1%) | baseline |
| holdings chosen | always 30-31, i.e. the floor | 30-47 |

Two things are worth saying explicitly to anyone comparing the reported numbers:

- **The two risk figures are not on the same scale.** `sum w_i sigma_i` is the
  risk you would bear if every pair moved together, so it is an upper bound. For
  Model 1's own portfolio at a 13% return target its objective reads 21.95%
  while the portfolio's actual standard deviation is 13.42% — a ratio of 1.64x.
  That gap *is* the diversification the linear model cannot see.
- **Model 1 always holds the minimum 30 stocks.** Adding a 31st cannot lower
  `sum w_i sigma_i`, so it never has a reason to diversify beyond the constraint.
  Model 3 voluntarily holds up to 47.

Model 1 is not useless — it is a MILP, solves faster, and needs only per-stock
volatilities rather than a full covariance matrix. It is the right tool when a
covariance estimate is not trustworthy. Here it is, and the 19.2% is what
choosing it would have cost.

## Three limitations that belong on the slides

These are properties of the data and the estimator, so they carry over to any
model built on these inputs, including `Main_model.py`.

**1. The estimation window is a judgement, and it matters.** Bootstrap
resampling of a given window converges reliably (top selection frequency 1.00),
but the 10-year and 5-year cores overlap at Jaccard 0.28. The clearest single
example: LMT.N and NOC.N are selected in 100% and 92% of 5-year resamples and in
50% and 55% of 10-year ones — defence became a low-volatility holding only after
2022. This is regime change, so no amount of resampling resolves it. We chose 10
years because the mandate is mid-term and the estimate should span a full cycle
including the 2018 and 2020 drawdowns, and we report the cost rather than hide it.

**2. Risk validation in sample is not risk validation.** On the estimation window
the 20-factor model is conservative (+7.7% mean). Out of sample — fit on
2016-2020, scored on 2021-2025 — a structurally identical estimator **understates**
risk by **13.2% on average and 23.9% at the min-risk end**, and no shrinkage
intensity changes this. The frozen model itself cannot be tested out of sample:
it uses ten years and the dataset is ten years long. Say "consistent with the
estimation period", not "conservative".

**3. The 30-stock floor pads the portfolio.** 11 of 33 positions in the neutral
book sit exactly on the 1% minimum. They exist to satisfy the constraint, not
because they earn their place. A lower stock floor or a higher minimum weight
(3-5%) would produce a cleaner book — worth raising with the client.

On discontinuities specifically: the detector that found these is not the one we
started with. A fixed 50% move threshold and a 5-sigma relative threshold both
flag mostly genuine market events — the 2020 oil crash, Abivax's Phase 3 result,
Globe Life's short-seller report. The signature that actually separates a
corporate action from a market move is a **run of identical closing prices**
(trading suspended) followed by a large jump. That fires on exactly 2 of 1093
stocks. Note it must be run on local-currency prices: in USD the daily FX rate
un-freezes a frozen local price and the detector misses it.

---


---

## What in here is current, and what is not

Every script below has working imports and finds its inputs — audited, not
assumed. But only four are live.

### Live — these produce what the model actually uses

| Script | Produces |
|---|---|
| `02a_esg_and_price_eda_cleaning.py` | `shares_imputed.csv` — the ESG imputation. Its price-cleaning half is superseded, its ESG half is not |
| `20_dividend_adjusted_pipeline.py` | `expected_return_v4.csv`, `covariance_matrix_v4.csv`, `per_stock_risk_v4.csv` — the whole cleaning chain in one pass |
| `21_backtest_walkforward.py` | the walk-forward backtest |
| `Model2.py` | audit baseline, unchanged since 31 August |

### Superseded — rewritten into `20`, kept for what each established

| Script | Superseded because | What it established |
|---|---|---|
| `01c_test_return_risk.py` | complete-case rule, local currency | the original estimator. Its complete-case filter is what excluded 96 late listings — the defect Chloe flagged |
| `03a_fx_convert.py` | `20` does the FX conversion inline | the suffix→currency map and the pence handling |
| `03b_usd_return_risk.py` | `20` estimates directly | reproduced `01c` to 9.7e-17, which is what made every later attribution possible |
| `04a_factor_model.py` | `20` embeds the factor model | the factor model that retains every stock, PSD by construction |
| `05d_factor_count.py` | `20` fixes k=20 | **why 20 factors**: 1–2 understate portfolio risk ~18%, 5 understate none, 20 is the smallest with none anywhere |
| `13_truncate_discontinuities.py` | `20` truncates inline | the suspension-plus-jump rule that finds ZEG.L and BMPS.MI |

### Diagnostics — ran once to answer a question, produce no model inputs

| Script | Question |
|---|---|
| `02b_price_eda_cleaning.py` | how long are internal price gaps? (all exactly 1 day) |
| `03c_frontier_usd.py` | what did the currency error cost? (+5.71pp at matched risk) |
| `03d_universe_effect.py` | what does excluding late listings cost? (+0.28pp) |
| `03e_composition_stability.py` | does it change the portfolio, not just the objective? (Jaccard 0.86 vs 0.28 for an ordinary window change) |
| `04b_frontier_factor.py` | does shrinkage fix the instability? (no) |
| `05a_single_index.py` | single-index covariance (Chloe's P1) — understates portfolio risk 39.9% at the min-risk end |
| `05b_risk_validation.py` | why: residual correlations +0.11 within region, −0.11 across, all set to zero |
| `05c_multifactor.py` | market + region factor (P2) — absorbs the structure, does not fix the risk |
| `06a_bootstrap_robust.py` | resampled weights — within a window stable, across windows Jaccard 0.28 |
| `06b_esg_sensitivity.py` | what does ESG ≥ 70 cost? **Numbers computed on the older inputs** |
| `07_final_portfolio.py` | first attempt at picking three profiles; belongs to the archived model track |
| `10_outlier_relative.py` | fixed 50% threshold vs a per-stock 5σ rule |
| `12_fx_model_free.py` | is the USD conversion necessary at all? (model-free: 8.04% local vs 8.99% USD) |
| `16_run_chloe_model.py`, `17_chloe_full.py` | Chloe's model on the **older** inputs; superseded by running `2_optimisation_model/code/Main_model.py` directly |

### Moved out

Eight scripts belonging to the country-cap model track now live in
`../archive/our_model_frozen/` alongside `Model3.py` and `Model4.py`:
`08_country_cap`, `09_lw_on_factor`, `11_refreeze_clean`, `14_refreeze_v3`,
`15_model1_linear`, `18_combined_model`, `19_freeze_v4`.

They import `Model3`, so they only run next to it — which is why they were moved
rather than left behind. `14_refreeze_v3.py` also produced the previous
generation of model inputs (`*_v3.csv`), now superseded by `20`.

### Result files computed on older inputs

Named `*_v3inputs.csv` so they cannot be picked up by mistake, plus
`esg_sensitivity_*.csv` and `efficient_frontier_v3.csv`. Current results are only
in `2_optimisation_model/results/`.

---

The country-cap model track these notes were written around is frozen in
`../archive/our_model_frozen/`. The current model is `2_optimisation_model/code/Main_model.py`; its
results are in `2_optimisation_model/results/`.
