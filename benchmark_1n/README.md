# The 1/N benchmark over the full study period

`30_benchmark_1n.py`, ~20 s, **no solver**. Results in `results/`.

## Why

1/N already existed in the repo twice, and both times narrower than we need:

- `pipeline/21_backtest_walkforward.py` and `backtest_profiles/` build it over
  the eligible universe at each rebalance, but only from **2018-04** — a
  walk-forward cannot start earlier because it needs three years of history
  first. That is 7.7 of the 11 years.
- `stress_test/` holds a fixed 1/N from 2015 but reports it only inside the
  crisis windows.

This gives a reference series for the **whole** period the brief defines, so any
result — the static frontier, a crisis window, a calendar year — can be quoted
against a consistently built naive benchmark.

## The gate

The construction has to agree with the 1/N script 21 built independently, on
script 21's own window, or one of the two is wrong. Script 21 rebalances
**quarterly** over the complete-3-year-history eligible set; this rebalances
**monthly** over the whole universe, so close-not-identical is the right result:

| Series (2018-04 → 2025-12) | CAGR | vol | Sharpe |
|---|---|---|---|
| `1N_all_monthly` here | 14.77% | 17.03% | **0.867** |
| script 21's 1/N | 14.65% | 16.91% | **0.866** |

Sharpe agrees to 0.001. `gate_vs_script21.csv`.

---

## The benchmark: 2015-01-02 → 2025-12-31, 11.0 years

| Series | CAGR | Volatility | Sharpe | Max DD | Final | Worst day |
|---|---|---|---|---|---|---|
| `1N_all_monthly` | 14.96% | 15.97% | 0.937 | −38.03% | 4.63× | −11.48% |
| **`1N_model_monthly`** | **14.80%** | **15.96%** | **0.928** | **−38.05%** | **4.56×** | −11.48% |
| `1N_esg70_monthly` | 13.33% | 16.35% | 0.815 | −37.95% | 3.96× | −11.91% |
| `1N_all_daily` | 15.67% | 16.11% | 0.973 | −37.94% | 4.96× | −11.70% |
| `1N_model_buyhold` | 15.35% | 16.30% | 0.941 | −36.64% | 4.81× | −11.16% |

**Use `1N_model_monthly` as the default comparator.** It is equal weight over
the same 1077-stock universe the model optimises, so a comparison isolates the
optimiser rather than the choice of universe — the principle script 21 already
adopted.

### Calendar years, %

| Year | `1N_model_monthly` | `1N_all_monthly` | `1N_esg70_monthly` |
|---|---|---|---|
| 2015 | +7.09 | +7.07 | +4.96 |
| 2016 | +12.23 | +12.22 | +11.04 |
| 2017 | +32.24 | +32.43 | +31.15 |
| 2018 | −7.08 | −6.93 | −9.90 |
| 2019 | +33.43 | +33.54 | +32.34 |
| 2020 | +17.83 | +18.36 | +14.52 |
| 2021 | +24.59 | +24.50 | +22.11 |
| 2022 | −13.11 | −13.46 | −12.36 |
| 2023 | +23.63 | +24.28 | +21.19 |
| 2024 | +11.94 | +12.44 | +9.45 |
| 2025 | +29.62 | +29.86 | +31.56 |

### Crisis windows, `1N_model_monthly`

Same windows as `stress_test/`, so the two are quotable side by side.

| Window | Return | Max DD | Volatility |
|---|---|---|---|
| 2015 China devaluation | −10.00% | −10.00% | 20.22% |
| 2016 Brexit vote | −1.57% | −10.70% | 38.80% |
| 2018 Q4 selloff | −17.64% | −17.71% | 15.18% |
| **2020 COVID crash** | **−38.05%** | −38.05% | 59.32% |
| 2020 crash + recovery | −2.09% | −38.05% | 39.51% |
| 2022 inflation shock | −26.94% | −27.41% | 21.86% |

---

## Three things this benchmark reveals

### 1. 1/N is not a portfolio we could have proposed

Worth saying before anyone compares them as alternatives. Against the brief's
own four conditions:

| Series | Names | Weight each | 1% floor | Weighted ESG | ESG ≥ 70 | Largest region | Admissible? |
|---|---|---|---|---|---|---|---|
| `1N_all_monthly` | 1087 | 0.092% | ✗ | 67.01 | ✗ | 54.4% ✓ | **no** |
| `1N_model_monthly` | 1077 | 0.093% | ✗ | 67.47 | ✗ | 54.6% ✓ | **no** |
| `1N_esg70_monthly` | 506 | 0.198% | ✗ | 78.07 | ✓ | **63.2% ✗** | **no** |

Every variant breaks the 1% per-stock floor by an order of magnitude, and no
equal-weight portfolio over more than **100** names can satisfy it at all. The
two unscreened variants also fail weighted ESG ≥ 70; the ESG-screened one
clears ESG but then breaks the 60% region cap, because the high-ESG half of the
universe is 63% European.

So 1/N is a **benchmark** — a reference for what no skill would have earned — and
not a competing proposal. That is the right way to present it: "we did not beat
the naive benchmark on risk-adjusted return, and the naive benchmark could not
have been bought under this mandate."

### 2. The ESG requirement is much cheaper as a constraint than as a screen — but not as much as the realised numbers suggest

A naive ESG screen throws away every name below 70. The optimiser's
weighted-average constraint can hold a low-ESG name as long as a high-ESG name
offsets it. The mechanism clearly favours the constraint; the size of the
advantage depends on which measure you use, and the two disagree:

| Measure | Naive ESG ≥ 70 screen | The model's weighted ESG ≥ 70 |
|---|---|---|
| Expected return on v4 μ, equal weight | 10.104% vs 10.367% → **−0.263 pp** | **−0.151 pp** at Neutral (script 23) |
| Realised CAGR, 2015–2025 | 13.331% vs 14.802% → **−1.471 pp** | not comparable (static book) |

On the strictly comparable measure — expected return under the same μ — the
screen costs **1.7×** what the constraint costs. Not ten times. The realised
11-year gap is **5.6× larger than the ex-ante expected gap**, which means most
of the screen's realised damage was not visible in μ at all: it came from the
exposures the screen happens to impose (63% Europe, a different sector mix), not
from picking lower-return stocks. Quote the −0.263 pp when comparing mechanisms
and the −1.471 pp only as what happened, with that caveat attached.

### 3. Rebalancing 1/N monthly was the worst of the three choices

| Rebalance | CAGR | Volatility | Max DD |
|---|---|---|---|
| daily | 15.67% | 16.11% | −37.94% |
| never (buy and hold) | 15.35% | 16.30% | −36.64% |
| monthly | 14.80% | 15.96% | −38.05% |

Non-monotone, and both effects are real: daily re-setting harvests
mean-reversion, never re-setting lets winners run, and monthly catches neither
cleanly. It matters because "the 1/N benchmark" is quoted as though it were one
number — the choice of rebalancing frequency moves it by **0.9 pp of CAGR**,
which is far more than most of the differences we report against it. Any
comparison has to name which 1/N it means.

One caveat on `1N_all_daily`: its first day is built from only 59 names, because
a return needs prices on two consecutive days and 2015-01-01 was a holiday on
which almost nothing traded. One day of 2869, so it does not move the
11-year figures, but `universe.csv` shows it.

---

## How entries are handled

"Complete history" is not a usable filter over this period. Across the whole
file only **59** stocks have no missing value at all — 2015-01-01 is a holiday
and a forward-fill only fills *after* a stock's first price. Over the model's
10-year window (from 2015-12-31) the same test gives **991**. Requiring
completeness would either discard 95% of the universe or silently shorten the
period.

Instead a stock is included on any day it has a return, i.e. a price that day
and on the previous observation. 118 stocks list after January 2015 and enter
when they appear, which is what an equal-weight index does and needs no
arbitrary cutoff.

## Files

| File | Contents |
|---|---|
| `curves.csv` | daily levels of all five series, indexed to 1.0, 2869 rows |
| `summary.csv` | full-period CAGR, vol, Sharpe, maxDD, final, best/worst day |
| `annual.csv` | calendar-year returns per series |
| `windows.csv` | the six crisis windows × all five series |
| `feasibility.csv` | which of the brief's conditions each series violates |
| `universe.csv` | names held per day, per series |
| `gate_vs_script21.csv` | agreement with script 21's independent 1/N |

## Reproduce

```bash
python3 benchmark_1n/30_benchmark_1n.py
```

Needs `pipeline/prices_div_usd.csv` (52 MB, gitignored) — the same USD,
dividend-adjusted prices μ and Σ are built from. Rebuild with
`pipeline/20_dividend_adjusted_pipeline.py` or ask Chloe.
