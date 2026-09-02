# Walk-forward backtest of Model 2

Option A of the two you proposed, tightly scoped. `pipeline/21_backtest_walkforward.py`.

## Why A rather than B

The argument for B was the deadline, and it does not apply here. Taking **one**
portfolio per rebalance instead of a whole frontier makes a rebalance cost one
Ledoit-Wolf fit plus one solve — 31 rebalances ran in minutes, not hours.

B's real weakness is not standardisation, it is sample size: two rebalance
points give two out-of-sample observations, on which skill and luck cannot be
separated. 31 gives a distribution.

## Protocol

Rolling **3-year** estimation window, **quarterly** rebalance, buy-and-hold in
between so weights drift with prices as a real book does. At each date `t`:

1. estimate on the trailing 3 years using **only** data strictly before `t`
2. eligible universe = complete price history inside that window. Here that is
   realism, not the complete-case defect we fixed for the static model — you
   cannot buy a stock that has no history yet
3. `mu` = annualised mean log-return, `Sigma` = **Ledoit-Wolf**, as you asked,
   deliberately not the James-Stein / 20-factor pipeline
4. solve Model 2's constraint set for **minimum variance**
5. hold to the next rebalance

Minimum variance rather than a target-return point: a target `beta` is arbitrary
and not comparable across regimes — the same `beta` is easy in 2021 and
infeasible in 2018. Min-variance has no free parameter.

Benchmark: **1/N over the same eligible universe** at each date, so the
comparison isolates the optimiser rather than the universe. Prices are
dividend-adjusted, which for a backtest is not optional.

## Headline

**2018-04-02 to 2025-12-31, 7.7 years, 31 rebalances**

| | CAGR | Volatility | Sharpe | Max DD | Final |
|---|---|---|---|---|---|
| Model 2 (min-variance) | 10.93% | **13.15%** | 0.831 | **−33.9%** | 2.23× |
| 1/N benchmark | **14.77%** | 16.92% | **0.873** | −37.6% | 2.91× |
| Model 2 after 10bp costs | 10.75% | 13.15% | 0.817 | −33.9% | 2.21× |

Risk-adjusted the two are **statistically indistinguishable**: the Sharpe gap is
0.042 and the t-statistic on the daily return difference is **−0.90**, far short
of significance. The correct claim is "indistinguishable, 1/N nominally ahead",
not "1/N wins".

The volatility gap is not noise: **−22.3%** overall, and lower in five of six
sub-periods.

This reproduces a well-known result rather than revealing a bug — DeMiguel,
Garlappi & Uppal (2009), *Optimal Versus Naive Diversification*, found the same
across many datasets. The cause is estimation error, and this project has three
independent measurements of it: composition Jaccard 0.27 between estimation
windows, out-of-sample risk understatement, and 84% annualised turnover.

## Where the model earns its keep

| Period | Regime | Model | 1/N | Δ | Model vol | 1/N vol |
|---|---|---|---|---|---|---|
| 2018-04…2019-12 | calm | **24.08%** | 12.99% | **+11.1** | 13.88% | 11.87% |
| 2020-02…03 | the crash | DD **−33.9%** | −37.6% | **+3.7pp** | 60.98% | 64.77% |
| 2021 | boom | 11.17% | 24.43% | −13.3 | **8.03%** | 11.47% |
| 2022 | inflation shock | **−12.24%** | −12.85% | **+0.6** | **13.63%** | 21.28% |
| 2023-2025 | AI rally | 14.67% | 21.90% | −7.2 | **8.23%** | 12.22% |

It wins in the drawdowns and loses in the rallies. That is the signature of a
low-volatility strategy and precisely the trade a risk-averse mandate buys. In
2022 it fell less while running **36% less volatility**.

One exception worth stating rather than glossing: in the calm 2018-19 window the
optimised book ran **higher** volatility than 1/N (13.88% vs 11.87%) and earned
+11pp for it. Volatility is lower in five of six sub-periods, not all six.

## The number to put on the limitations slide

Mean predicted risk at the rebalance dates was **8.78%**. Realised volatility was
**13.15%** — the model understated its own risk by **49.7%** out of sample.

An earlier single train/test split measured −13.2%. The walk-forward is worse
because the window is 3 years rather than 5 (noisier), because the estimator here
is Ledoit-Wolf rather than the 20-factor model, and because COVID sits inside the
test period as a genuine regime break. Indirectly this **justifies the 20-factor
choice** in the static model: the more conservative estimator was not caution for
its own sake.

## Turnover

Mean **20.9%** per rebalance, median 16.2%, max 73.5% — roughly **84% annualised**.
At 10bp one-way that costs **0.18pp** of CAGR, so costs are not what holds the
strategy back.

## Three limitations, none fixable with this dataset

1. **ESG and sector data are a present-day snapshot.** Applying ESG ≥ 70 at a
   2018 rebalance uses 2025 information. This is look-ahead and cannot be removed
   without a historical ESG panel.
2. **The universe is survivorship-biased by construction** — today's STOXX 600
   and S&P 500 constituents, so failed and delisted companies are absent.
   Realised returns are optimistic for **every** strategy here, benchmark
   included.
3. **Transaction costs are not in the optimisation**, only applied afterwards on
   measured turnover.

## Files

```
backtest_summary.csv        the headline table
backtest_subperiods.csv     regime-by-regime breakdown
backtest_diagnostics.csv    Sharpe test, risk understatement, turnover
backtest_rebalances.csv     per-rebalance: eligible, held, predicted risk, ESG, turnover
backtest_equity_curves.csv  daily value of both strategies
```
