# SustainaFund: ESG-constrained portfolio selection with FICO Xpress

Code and results for the individual report of the FICO / HTW Berlin Summer School 2026.
SustainaFund invests $100 million in equities from the S&P 500 and the STOXX Europe 600
(1,077 stocks in the final universe). A mixed integer quadratic program (MIQP) in FICO
Xpress 9.9 traces the efficient frontier under the rules of the brief, and fixed rules
select three risk profiles.

Educational exercise. Not investment advice.

## Results at a glance

| Profile | Frontier point | Expected return | Risk | Return / risk | Stocks |
|---|---|---|---|---|---|
| Risk Averse | 0 | 9.87% | 9.26% | 1.067 | 42 |
| Neutral | 8 | 14.30% | 10.62% | 1.346 | 30 |
| Risk Prone | 11 | 15.97% | 12.77% | 1.250 | 30 |

The ESG rule (weighted score of at least 70) costs 0.18 percentage points of expected
return at Neutral. Out of sample, no portfolio has a significantly higher Sharpe ratio than
an equal-weight portfolio, and the model understates risk. The report recommends Risk
Averse and treats its risk figures as a lower bound.
The numbers above come from `results_chloe/` (Tier 2 switch off, country cap off).

## The model

`Model2_ori.py` solves, for a grid of target returns β:

```
minimise   wᵀΣw
subject to wᵀμ ≥ β,  Σ wᵢ = 1
           0.01·yᵢ ≤ wᵢ ≤ 0.20·yᵢ,  yᵢ ∈ {0,1},  Σ yᵢ ≥ 30        (brief)
           each region ≤ 60%                                      (brief)
           Σ ESGᵢ·wᵢ ≥ 70                                         (brief)
           each sector ≤ 30%                                      (added)
           ESGᵢ ≥ 30 for every held stock                         (added)
           Tier 1 weapons exclusion                               (added, always on)
           Tier 2 defence exclusion, country cap ≤ 25%            (added, switches, off)
```

Inputs: `expected_return_v4.csv` (James-Stein shrunk, USD, total return),
`covariance_matrix_v4.csv` (20-factor PCA, positive semidefinite), `shares_imputed.csv`
(region, country, ESG) and `sectors.xlsx`. `profile_rule.py` selects the three profiles.

## How to run

```bash
pip install -r requirements.txt
export XPAUTH_PATH=/path/to/xpauth.xpr     # Xpress licence, never committed
python Model2_ori.py                        # the frontier, about 15 seconds
```

Scripts in the repository root must be started from the root. The scripts in `pipeline/` run
from inside `pipeline/`.
Everything except solving works without the licence. `python src/check_license.py` solves a
toy problem to check the licence.

## Where each part of the report comes from

| Report section | Script | Output |
|---|---|---|
| 3.1 Data and preprocessing | `pipeline/02a_esg_and_price_eda_cleaning.py`, `pipeline/20_dividend_adjusted_pipeline.py` | `shares_imputed.csv`, `expected_return_v4.csv`, `covariance_matrix_v4.csv` |
| 3.2.2 and Table A2: factor count | `29_factor_count_v4.py` (about 9 min) | `results_factor_count/` |
| 3.3.1 Frontier and three portfolios | `Model2_ori.py`, `analyze_risk.py`, `profile_rule.py` | `results_chloe/` |
| 3.3.2 Cost of the constraints | `23_scenario_matrix.py`, `24_country_cap_and_mandate.py` (about 6 min) | `results_chloe/scenario_matrix.csv`, `results_country_cap/` |
| 3.3.3 Stability across windows | `32_robustness_windows.py`, `pipeline/03e_composition_stability.py`, `pipeline/06a_bootstrap_robust.py` | `dashboard_data/robustness/` |
| 3.3.4 Out-of-sample backtest | `backtest_profiles/26_backtest_profiles.py` (about 13 min), `benchmark_1n/30_benchmark_1n.py`, `backtest_profiles/26c_forecast_vs_realised.py` (expected vs realised return, no solver) | `backtest_profiles/results/`, `benchmark_1n/results/` |
| 3.3.5 Crisis stress test | `stress_test/25_crisis_stress_test.py` (about 7 min) | `stress_test/results/` |
| Second LSEG ESG and sector export (measured, not adopted) | `27_lseg_esg_sector_update.py` | `results_lseg_update/`, `data_lseg_update/` |

The factor count, robustness, backtest, benchmark and stress-test scripts read
`pipeline/prices_div_usd.csv`, which is not in the repository (see "Data and licences"). The
model itself needs only the four input files listed above. Scripts in the root start from the root; the scripts in
`backtest_profiles/`, `stress_test/` and `benchmark_1n/` find the root on their own.

Each results folder has its own `README.md` that states the script, the run time and the
caveats. `pipeline/README.md` is the provenance map of the input analysis.

## Layout

```
Model2_ori.py                  the model
profile_rule.py                selection rule for the three profiles
analyze_risk.py                profile analysis of a saved frontier
23_ ... 33_*.py                scenario, robustness and backtest scripts (see table above)
expected_return_v4.csv, covariance_matrix_v4.csv, shares_imputed.csv, sectors.xlsx
                               the four model inputs
results_*/, backtest_profiles/, stress_test/, benchmark_1n/    results of each study
pipeline/                      input preparation and the analysis behind it
dashboard_data/                generated long-format tables for the Power BI deck
report_figures/                scripts and images of the figures in the report
deck/, build_deck.py           presentation tooling, not needed for the report
archive/                       superseded material, kept for the record
docs/                          Xpress 9.9 documentation in markdown
```

## Data and licences

The repository contains the course data (`pipeline/stockprices_full.csv`, `shares_full.csv`),
the cached ECB exchange rates and the four model inputs. It does **not** contain the
dividend-adjusted LSEG price file `pipeline/prices_lseg_dividend_adjusted.csv` (about 49 MB)
or the USD price file `pipeline/prices_div_usd.csv` that `pipeline/20_dividend_adjusted_pipeline.py`
builds from it.

- Without them, `Model2_ori.py` and the scripts that need only the four model inputs
  (`23`, `24`, `27`, `31`, `analyze_risk.py`) run as shipped.
- The backtest, stress test, factor count and robustness scripts (`21`, `25`, `26`, `29`,
  `30`, `32`, `33`) read `prices_div_usd.csv`. To re-run them, place the LSEG file in
  `pipeline/` and run `python 20_dividend_adjusted_pipeline.py` from inside `pipeline/`
  (about 3 minutes). The results of these runs are stored in the results folders.

The Xpress licence file `xpauth.xpr` is excluded by `.gitignore` and must never be committed.
Large intermediate files (`prices_clean*.csv`, covariance files other than
`covariance_matrix_v4.csv`) are not committed and can be regenerated with the scripts above.

## Use of AI tools

Parts of the code were written and reviewed with the help of Claude (Anthropic). Appendix B
of the report lists the tools and the prompts.
