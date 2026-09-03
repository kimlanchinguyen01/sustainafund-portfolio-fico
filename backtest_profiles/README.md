# Walk-forward backtest of the recommended profile

`26_backtest_profiles.py`, ~13 min. Results in `results/`.

## Why this is neither option A nor option B

**Option A already exists.** `pipeline/21_backtest_walkforward.py` is a full
walk-forward: rolling 3-year window, 31 quarterly rebalances, 7.7 test years,
mean log-return + Ledoit-Wolf, against 1/N, reporting Sharpe, max drawdown and
turnover. Rebuilding it would spend the day reproducing a result we have.

What it does not do is test the book we recommend. It optimises for **minimum
variance** at every rebalance. The recommendation is **neutral**, and the crisis
stress test showed that distinction decides the answer: min-variance beat 1/N in
all three testable crises while the neutral book lost two of three. So "no
Sharpe edge over 1/N" was a statement about min-variance, and the recommended
portfolio had never been walk-forward tested at all.

This closes that gap on the identical protocol, so the numbers are comparable.

### The obstacle, and the fix

Script 21 chose min-variance for a stated and correct reason: an absolute return
target `beta` is not comparable across regimes — the same beta is easy in 2021
and infeasible in 2018 — so picking one per rebalance smuggles in a free
parameter.

A **mandate** removes that objection. "Maximise return, then minimise risk while
giving up at most X of the *achievable* maximum" is defined relative to whatever
is achievable in that regime. No absolute target, comparable across regimes, and
two solves rather than a whole frontier. In the static model reltol = 20% lands
at return/risk 1.345 against the grid-picked Neutral's 1.346.

Four books per rebalance: `minvar`, `mandate20`, `mandate10`, `equal_weight`.
Estimation, eligibility, ESG floor, rebalance dates, buy-and-hold convention and
cost treatment are identical to script 21. Only the objective differs. All
solving goes through `Model2_ori.solve_model2`, so the constraint set cannot
drift from the model. Country cap off, as delivered.

### And B is not just smaller, it is unstable — measured, not asserted

`26b_why_not_option_b.py` runs B properly, twice with different split dates,
both defensible a priori and neither cherry-picked, plus a variant with three
rebalance points. Everything else identical.

| Scheme | Book | Sharpe | 1/N | Δ Sharpe | t | Verdict |
|---|---|---|---|---|---|---|
| split 2019-12 / 2022-12 | `minvar` | 0.656 | 0.829 | −0.173 | −1.42 | loses |
| split 2019-12 / 2022-12 | `mandate20` | 0.915 | 0.829 | **+0.087** | +0.70 | **beats** |
| split 2020-06 / 2023-06 | `minvar` | 0.940 | 1.258 | −0.319 | −1.87 | loses |
| split 2020-06 / 2023-06 | `mandate20` | 1.014 | 1.258 | **−0.244** | +0.10 | **loses** |
| 3 points, yearly-ish | `minvar` | 0.645 | 0.846 | −0.201 | −1.48 | loses |
| 3 points, yearly-ish | `mandate20` | 0.716 | 0.846 | −0.130 | +0.28 | loses |

**For the recommended profile B contradicts itself.** `mandate20` "beats 1/N"
on one split and "loses to 1/N" on another — a Δ Sharpe spread of **0.331**
decided by nothing but where the boundary falls. The 31-rebalance answer is
+0.010 with t = +0.60, i.e. indistinguishable. B would have handed us a
confident-looking result, in either direction, from the same data and the same
code.

For `minvar` B agrees on direction but not on size: −0.173 to −0.319 against
the 31-rebalance −0.038, overstating the loss four- to eightfold.

One honest qualification: with two rebalance points the test WINDOW also moves
with the split — the 2020-06 scheme begins after the COVID crash, which is why
its 1/N Sharpe is 1.258 rather than 0.829. So the spread is sample size and
window choice together, not sample size alone. That does not rescue B; it is a
second reason the protocol is fragile here, because with so few points the
window and the sample are not separable.

---

## The gate

`minvar` here must reproduce script 21, or nothing else is trustworthy:

| Metric | Script 21 | Here | Difference |
|---|---|---|---|
| CAGR % | 11.030 | 10.939 | −0.091 |
| Volatility % | 13.210 | 13.197 | −0.013 |
| Sharpe | 0.835 | 0.829 | −0.006 |
| Max DD % | −33.890 | −33.806 | +0.084 |

Reproduces. The residual is MIP-gap tie-breaking on alternative optima, the same
effect documented in `results_country_cap/README.md`.

---

## Headline — 2018-04-02 to 2025-12-31, 7.7 years, 31 rebalances

| Book | CAGR | Volatility | Sharpe | Max DD | Final | Turnover p.a. |
|---|---|---|---|---|---|---|
| `minvar` | 10.94% | **13.20%** | 0.829 | **−33.81%** | 2.24× | 83% |
| `mandate20` | 17.60% | 20.08% | 0.876 | −42.31% | 3.51× | **170%** |
| `mandate10` | 21.29% | 23.30% | **0.914** | −46.00% | **4.46×** | 159% |
| **1/N benchmark** | 14.65% | 16.91% | 0.866 | −37.68% | 2.89× | — |

After 10bp one-way on measured turnover: `minvar` 0.815, `mandate20` **0.857**,
`mandate10` 0.898.

## What this actually supports, and what it does not

**1. No book beats 1/N with statistical significance. None.** The t on the daily
return difference:

| Book | Sharpe − 1/N | t | Significant at 5%? |
|---|---|---|---|
| `minvar` | −0.038 | −0.87 | no |
| `mandate20` | +0.010 | +0.60 | no |
| `mandate10` | +0.047 | +1.12 | no |

Every one sits inside ±1.96. The Sharpe ordering 0.829 → 0.866 → 0.876 → 0.914
is noise. It cannot be used to claim the optimiser adds risk-adjusted return —
and equally, script 21's negative result cannot be used to claim it destroys
any. Over 7.7 years and 31 rebalances the honest answer is *not distinguishable
from the benchmark*. This is the single most important sentence in this folder.

**2. The apparent Sharpe edge does not survive trading costs.** `mandate20`
turns over **170% a year** against min-variance's 83%. At 10bp its Sharpe falls
to 0.857, **below** the 1/N benchmark's 0.866. `mandate10` stays above at 0.898,
but on a t of 1.12 that is not a finding.

**3. What IS robust is risk, and it is monotone.** Realised volatility and
drawdown rise in lockstep as the mandate loosens:

| Book | Realised vol | Max DD |
|---|---|---|
| `minvar` | 13.20% | −33.81% |
| 1/N | 16.91% | −37.68% |
| `mandate20` | 20.08% | −42.31% |
| `mandate10` | 23.30% | −46.00% |

**Min-variance is the only book that is materially below the benchmark on both.**
That is the same conclusion the crisis stress test reached from the other
direction, and it is where the −22% volatility edge in script 21 comes from.

**4. By regime, the mandates are a bull-market bet.**

| Period | Regime | `minvar` | `mandate20` | 1/N |
|---|---|---|---|---|
| 2018-04..2019-12 | calm | 24.72% | 13.47% | 13.04% |
| 2020 full year | crash and rebound | 3.82% | **56.03%** | 18.09% |
| 2020-02..2020-03 | the crash itself | −87.48% | −86.03% | −94.20% |
| 2021 | boom | 11.25% | 15.80% | 24.50% |
| 2022 | inflation shock | −12.06% | **−34.32%** | −12.60% |
| 2023-2025 | AI rally | 14.30% | 33.31% | 21.48% |

Annualised, so the short crash window reads extreme. The mandates win the 2020
rebound and the AI rally and lose 2022 by 22 pp against the benchmark. That is
the shape of chasing high sample means, not of a diversified mandate.

**5. Risk understatement, for the record.** Mean predicted risk against realised
volatility: `minvar` 8.78% → 13.20% (**+50.3%**, matching script 21's 50.4%),
`mandate20` 16.76% → 20.08% (+19.8%), `mandate10` 20.29% → 23.30% (+14.8%). The
optimiser understates its own risk everywhere, worst at the min-variance end.

## The honest weakness of the mandate construction

A mandate anchors on the **max-return corner**, and out of sample that corner is
estimated from an unshrunk trailing 3-year sample mean. At the first rebalance
`mandate20` was solved against a predicted maximum of ~57% p.a. and itself
predicted **45.85%** return. `pipeline/04a_factor_model.py` recorded the same
pathology in the static work — sample means reaching 88% p.a. purely from the
2023-25 regime — which is exactly why the delivered model uses James-Stein
shrinkage.

So `mandate20`'s realised behaviour conflates two things: the profile, and the
noisiest possible anchor for it. This does not affect the min-variance gate or
conclusion 1 and 3, which are the load-bearing results. It does mean the
mandates here are a **lower bound** on what a return-seeking profile can do
out of sample. Shrinking mu at each rebalance before solving the mandate would
separate the two, costs no extra solve time, and is the obvious next run — see
`HANDOFF.md`.

## Files

| File | Contents |
|---|---|
| `summary.csv` | CAGR / vol / Sharpe / maxDD / final per book, with cost rows |
| `equity_curves.csv` | daily curves, all four books, indexed to 1.0 |
| `subperiods.csv` | six regimes plus FULL, per book |
| `rebalances.csv` | per rebalance per book: held, predicted risk, ESG, turnover, `solstatus` |
| `diagnostics.csv` | Sharpe vs 1/N with t-tests, risk understatement, turnover |
| `gate.csv` | the reproduction check against script 21 |
| `option_b_comparison.csv` | what option B concludes under three different splits |

`subperiods.csv` and `diagnostics.csv` also close a reproducibility hole:
`build_deck.py` reads `results_chloe/backtest/backtest_subperiods.csv` and
`backtest_diagnostics.csv`, and **nothing in the repo writes either file** —
they were produced ad hoc. These are generated, in the same regime windows, so
they can replace them.

## Limitations

Inherited from script 21 and not fixable with this dataset:

1. ESG scores and sectors are a present-day snapshot, so applying ESG >= 70 at a
   2018 rebalance uses 2025 information. Look-ahead, reported not hidden.
2. The universe is today's index constituents: survivorship-biased for every
   strategy here, benchmark included.
3. No transaction costs inside the optimiser. Turnover is measured and a 10bp
   sensitivity applied afterwards — which, for the mandates, is the difference
   between beating and not beating 1/N.

Plus one of this script's own: `results_chloe/backtest/README.md` quotes CAGR
10.93 / vol 13.15 / Sharpe 0.831 while `backtest_summary.csv` in the same folder
says 11.03 / 13.21 / 0.835. The gate uses the CSV. Minor, but the README there
was written from an earlier run.

## Reproduce

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 backtest_profiles/26_backtest_profiles.py      # ~13 min, the deliverable
python3 backtest_profiles/26b_why_not_option_b.py      # ~3 min, the option-B check
```

Needs `pipeline/prices_div_usd.csv` (52 MB, gitignored). Rebuild with
`pipeline/20_dividend_adjusted_pipeline.py` or ask Chloe.
