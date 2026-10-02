# Figures of the report

The scripts read only saved result files, so they need neither the Xpress licence nor the
price files. They find the repository by their own location and can be started from any
directory. Images are written to `results/` in this folder.

```bash
python 7_report_figures/code/make_figs_main.py     # Figure 1 and Figure 2
python 7_report_figures/code/make_figs_extra.py    # Figure 3, A1, A2 and A3
```

| Report figure | File | Data |
|---|---|---|
| Figure 1: efficient frontier and the three portfolios | `results/fig1_frontier.png` | `2_optimisation_model/results/efficient_frontier_model2_sec30_tier1_tier2off_esgfloor30.csv` |
| Figure 2: value of 1 USD, walk-forward backtest | `results/fig2_backtest.png` | `4_backtest/results/profiles/equity_curves.csv` |
| Figure 3: expected vs realised return at the 31 rebalances | `results/fig_forecast_scatter.png` | `4_backtest/results/profiles/rebalances.csv`, `equity_curves.csv` (statistics: `4_backtest/code/26c_forecast_vs_realised.py`) |
| Figure A1: risk error by number of factors | `results/fig_factor_count.png` | `3_sensitivity_studies/results/factor_count/sweep.csv` |
| Figure A2: return given up by each constraint at Neutral | `results/fig_cost_constraints.png` | `2_optimisation_model/results/scenario_matrix.csv`, `country_cap/cap_cost.csv` |
| Figure A3: point-in-time crisis test (Panel B) | `results/fig_stress_panelB.png` | `6_stress_test/results/panelB_windows.csv` |

The font is Carlito; if it is not installed matplotlib falls back to its default font.
