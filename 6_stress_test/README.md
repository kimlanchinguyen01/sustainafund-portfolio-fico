# Results — crisis-window stress test

Output of `6_stress_test/code/25_crisis_stress_test.py` and nothing else. ~7 min, of which
251 s is solver time.

The existing walk-forward backtest (`4_backtest/code/21_backtest_walkforward.py`)
tests the **minimum-variance** book. The book we recommend is **neutral**, and
until now it had never been put through a crisis.

---

## Read this before the tables

There are two panels and they disagree. That is the point, not a defect.

- **Panel A** holds the three *delivered* portfolios through each crisis. It is
  **in-sample**: mu and Sigma were estimated on 2015–2025, which contains every
  one of these crises. The optimiser had already seen them. Panel A describes
  the book we are handing over; it is **not** evidence that the method protects
  anyone.
- **Panel B** is the actual stress test. For each window it estimates on the
  three years strictly before, re-solves, and holds through. Nothing after the
  window start is used.

Panel A flatters the model. Panel B does not.

---

## Panel A — the delivered books through each crisis (in-sample)

Returns and drawdowns in %, `recovery` in calendar days from the window start
back to the window-start level.

| Window | neutral | 1/N | neutral maxDD | 1/N maxDD | neutral recovery | 1/N recovery |
|---|---|---|---|---|---|---|
| 2015 China devaluation | −3.56 | −8.97 | −4.99 | −8.97 | 59 | 247 |
| 2016 Brexit vote | +2.31 | −1.59 | −2.51 | −9.91 | 7 | 43 |
| 2018 Q4 selloff | −9.51 | −16.63 | −9.52 | −16.70 | 175 | 197 |
| **2020 COVID crash** | **−15.86** | **−36.17** | −16.05 | −36.17 | 99 | 175 |
| 2020 crash + recovery | +10.73 | −1.74 | −16.05 | −36.17 | 100 | 236 |
| 2022 inflation shock | −8.38 | −25.26 | −15.18 | −25.92 | 316 | 529 |
| FULL 2015–2025 | +801.35 | +366.71 | −20.06 | −35.37 | never under water | never |

The delivered book halves the COVID drawdown and never fell below its 2015
starting value. Realised volatility over the crash window was **41.60%**
against the **10.62%** the model predicted — the book protected capital while
breaking its own risk estimate by a factor of four.

### Who caused the COVID drawdown (neutral book, by country)

| Country | Weight % | Contribution to the −15.86% |
|---|---|---|
| United States | 48.29 | −6.91 pp |
| Switzerland | 36.74 | −5.78 pp |
| Norway | 2.78 | −1.30 pp |
| Belgium | 4.37 | −0.77 pp |
| United Kingdom | 3.95 | −0.51 pp |

Per unit of weight Switzerland was the **worse** of the two large exposures:
−0.157 pp per 1% held against −0.143 pp for the US. The Swiss concentration did
not earn its size in the crash — which is an argument for the country cap that
the static risk numbers cannot make.

### Worst 60-day stretches, found from the data rather than chosen

Greedy non-overlapping minima of the neutral book's rolling 60-day return, so
these are not cherry-picked windows.

| Start | End | 60-day return |
|---|---|---|
| 2019-12-30 | 2020-03-23 | **−13.66%** |
| 2022-03-24 | 2022-06-16 | −10.24% |
| 2021-11-04 | 2022-01-27 | −8.67% |
| 2018-10-01 | 2018-12-24 | −8.15% |
| 2022-07-22 | 2022-10-14 | −5.08% |

Four of the five worst stretches are COVID and 2022. The named windows above
are the right ones to have picked.

---

## Panel B — point-in-time (the real stress test)

Estimated on the 3 years before each window with a trailing mean log-return and
a Ledoit-Wolf shrunk sample covariance, following script 21 rather than the
20-factor James-Stein pipeline: re-running the factor pipeline per window would
change the estimator and the window at once and the comparison would mean
nothing.

**2015 and 2016 are not testable.** Both crises fall inside the first three
years of the dataset (which starts 2015-01-02), leaving 156 and 384 trading days
of history — below the 500-day minimum. That is missing data, not an infeasible
model, and `panelB_not_testable.csv` records it as such. Script 21 hits the same
wall and starts its walk-forward in 2018-04.

| Window | risk_averse | **neutral** | risk_prone | 1/N |
|---|---|---|---|---|
| 2018 Q4 selloff | **−9.97** | −18.38 | −18.63 | −17.54 |
| 2020 COVID crash | −33.52 | **−31.83** | −29.56 | −37.92 |
| 2022 inflation shock | **−23.53** | −32.46 | −44.95 | −25.64 |

### Three results that matter, and two of them are negative

**1. Out of sample the neutral book does not protect.** It beat 1/N in one of
three crises (COVID, by 6.1 pp) and lost the other two — 2018 Q4 by 0.8 pp and
2022 by **6.8 pp**. Panel A's 20 pp COVID advantage shrinks to 6 pp once the
optimiser is denied hindsight. This is consistent with the existing backtest
finding of no Sharpe edge over 1/N, and it is the honest answer to "does the
recommendation survive a crisis".

**2. The minimum-variance end is where the protection actually lives.** It beat
1/N in **all three** crises — by 7.6 pp in 2018, 4.4 pp in COVID and 2.1 pp in
2022 — while neutral lost two of three. The existing walk-forward backtest
measured a −22% volatility edge, and it tested min-variance. That was not a
coincidence of scope: the edge belongs to that end of the frontier, not to the
book we are recommending.

**3. Predicted risk is not a crisis number.** Realised over predicted:

| Window | predicted | realised | ratio |
|---|---|---|---|
| 2018 Q4 selloff | 9.93% | 18.15% | **1.83×** |
| 2020 COVID crash | 8.38% | 56.22% | **6.71×** |
| 2022 inflation shock | 15.19% | 21.80% | **1.44×** |

The static model quotes 10.62% for the neutral book. In a crash the same
construction realised nearly seven times its own forecast. The existing finding
of a 50.4% understatement out of sample is the *average* case; this is the tail.

### The country cap costs nothing in a crisis either

Neutral, cap off vs cap 25%:

| Window | cap off | cap 25% | difference |
|---|---|---|---|
| 2018 Q4 selloff | −18.38 | −18.50 | −0.12 pp |
| 2020 COVID crash | −31.83 | −31.67 | +0.16 pp |
| 2022 inflation shock | −32.46 | −32.74 | −0.28 pp |

Immaterial in both directions, and the reason is visible in
`panelB_portfolios.csv`: the point-in-time neutral books hold at most
**9.7–19.9%** in any one country, so the 25% cap barely binds. The 36.7% Swiss
position is an artefact of the **full-sample 20-factor** estimate, not something
the trailing 3-year Ledoit-Wolf estimate produces. Worth saying out loud if the
cap is questioned: it constrains a concentration that only the delivered
estimator creates.

---

## Caveats

- **Two solves did not prove optimality.** The point-in-time `risk_averse`
  solves at 2020-02-19 hit the 120 s limit and returned FEASIBLE (see
  `solstatus` in `panelB_portfolios.csv`). The min-variance end on a dense
  Ledoit-Wolf covariance over 994 stocks is a much harder MIQP than the same
  problem on the 20-factor PCA covariance. Every other solve is OPTIMAL, most
  in under 3 s.
- **`recovery_days` looks past the window end.** It is the only
  forward-looking quantity here and is labelled as such.
- Inherited from script 21 and not fixable with this dataset: ESG scores and
  sectors are a present-day snapshot, so applying ESG >= 70 at a 2018 rebalance
  is look-ahead; the universe is today's index constituents, so it is
  survivorship-biased for every strategy including the benchmark; no
  transaction costs.

## Files

| File | Contents |
|---|---|
| `panelA_windows.csv` | delivered books × every window, all metrics |
| `panelB_windows.csv` | point-in-time books × every testable window |
| `panelB_portfolios.csv` | what each point-in-time solve held, plus solstatus and solve time |
| `panelB_not_testable.csv` | the two windows with no usable estimation history, and why |
| `drawdown_attribution.csv` | per-stock COVID contribution for the neutral book |
| `worst_windows.csv` | the five worst 60-day stretches, found empirically |

## Reproduce

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 6_stress_test/code/25_crisis_stress_test.py
```
