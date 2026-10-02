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
The numbers above come from `2_optimisation_model/results/` (Tier 2 switch off, country cap off).

## Layout: one folder per part, each with `code/`, `data/` and `results/`

```
1_data_preparation/     from raw prices and ESG scores to the model inputs
    code/                 cleaning, FX conversion, return and risk estimation, factor model
    data/                 raw inputs (course data, ECB rates, case study PDF)
    results/              intermediate and exploratory outputs
2_optimisation_model/   the MIQP, the profile rule and the frontier
    code/                 Main_model.py, profile_rule.py, analyze_risk.py, 23_, 24_, check_license.py
    data/                 the six model inputs (returns, covariance, shares, sectors)
    results/              frontier, three portfolios, scenario matrix, country_cap/
3_sensitivity_studies/  how much the answer depends on the inputs and the rules
    code/                 27 (LSEG ESG and sectors), 29 (factor count), 31 (scenario grid), 32 (windows)
    results/              lseg_update/, factor_count/, scenario_grid/, robustness_windows/
4_backtest/             out-of-sample tests
    code/                 21 (min variance), 26 and 26b (profiles), 26c (forecast vs realised), 33 (walk-forward)
    results/              min_variance/, profiles/, walkforward/
5_benchmark_1n/         equal-weight benchmark over the full period
6_stress_test/          crisis windows (2018 Q4, 2020, 2022)
7_report_figures/       scripts and images of the figures in the report
dashboard_data/         derived tables for the Power BI deck (built from the folders above)
```

Every script finds its own files from its location, so it can be started from any directory.
Each part has a `README.md` with the method, the run time and the caveats.

## The model

`2_optimisation_model/code/Main_model.py` solves, for a grid of target returns β:

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

Inputs, all in `2_optimisation_model/data/`: `expected_return_v4.csv` (James-Stein shrunk,
USD, total return), `covariance_matrix_v4.csv` (20-factor PCA, positive semidefinite),
`shares_imputed.csv` (region, country, ESG) and `sectors.xlsx`. `profile_rule.py` selects
the three profiles.

## How to run

```bash
pip install -r requirements.txt
export XPAUTH_PATH=/path/to/xpauth.xpr     # Xpress licence, never committed
python 2_optimisation_model/code/Main_model.py     # the frontier, about 15 seconds
python 2_optimisation_model/code/analyze_risk.py   # the three profiles from the saved frontier
```

Everything except solving works without the licence.
`python 2_optimisation_model/code/check_license.py` solves a toy problem to check it.

## Where each part of the report comes from

| Report section | Script | Output |
|---|---|---|
| 3.1 Data and preprocessing | `1_data_preparation/code/02a_esg_and_price_eda_cleaning.py`, `20_dividend_adjusted_pipeline.py` | `2_optimisation_model/data/` |
| 3.2.2 and Table A2: factor count | `3_sensitivity_studies/code/29_factor_count_v4.py` (about 9 min) | `3_sensitivity_studies/results/factor_count/` |
| 3.3.1 Frontier and three portfolios | `Main_model.py`, `analyze_risk.py`, `profile_rule.py` | `2_optimisation_model/results/` |
| 3.3.2 Cost of the constraints | `23_scenario_matrix.py`, `24_country_cap_and_mandate.py` (about 6 min) | `2_optimisation_model/results/scenario_matrix.csv`, `country_cap/` |
| 3.3.3 Stability across windows | `3_sensitivity_studies/code/32_robustness_windows.py`, `1_data_preparation/code/03e_composition_stability.py`, `06a_bootstrap_robust.py` | `3_sensitivity_studies/results/robustness_windows/` |
| 3.3.4 Out-of-sample backtest | `4_backtest/code/26_backtest_profiles.py` (about 13 min), `5_benchmark_1n/code/30_benchmark_1n.py`, `4_backtest/code/26c_forecast_vs_realised.py` (no solver) | `4_backtest/results/profiles/`, `5_benchmark_1n/results/` |
| 3.3.5 Crisis stress test | `6_stress_test/code/25_crisis_stress_test.py` (about 7 min) | `6_stress_test/results/` |
| Figures 1 to 3, A1 to A3 | `7_report_figures/code/make_figs_main.py`, `make_figs_extra.py` | `7_report_figures/results/` |
| Second LSEG ESG and sector export (measured, not adopted) | `3_sensitivity_studies/code/27_lseg_esg_sector_update.py` | `3_sensitivity_studies/results/lseg_update/` |

## What runs with what

| You have | You can run |
|---|---|
| nothing extra | the figure scripts, `26c`, `analyze_risk.py`, the cleaning step `02a`, the `dashboard_data` builders; every stored result can be read as is |
| the Xpress licence | the model (`Main_model.py`), `23`, `24`, `31` |
| the licence and the price file | `21`, `25`, `26`, `29`, `30`, `32`, `33` |

The price file is `1_data_preparation/results/prices_div_usd.csv` (about 52 MB), built by
`1_data_preparation/code/20_dividend_adjusted_pipeline.py` from the dividend-adjusted LSEG
download `1_data_preparation/data/prices_lseg_dividend_adjusted.csv` (about 49 MB). Neither
file is in the repository. Running script 20 also rewrites the model inputs in
`2_optimisation_model/data/`. The results of all these runs are stored in the results folders.
`27` needs the LSEG ESG and sector workbook
`3_sensitivity_studies/data/lseg_update/ESG_and_sector_lseg.xlsx`, which is not included either;
its results are stored.

## Data and licences

The repository contains the course data (`1_data_preparation/data/stockprices_full.csv`,
`2_optimisation_model/data/shares_full.csv`), the cached ECB exchange rates, the case study PDF
and the model inputs. The Xpress licence file `xpauth.xpr` is excluded by `.gitignore` and must
never be committed. Large intermediate files (`prices_clean*.csv`, covariance files other than
`covariance_matrix_v4.csv`) are not committed and can be regenerated with the scripts above.

## Use of AI tools

Parts of the code were written and reviewed with the help of Claude (Anthropic). Appendix B
of the report lists the tools and the prompts.
