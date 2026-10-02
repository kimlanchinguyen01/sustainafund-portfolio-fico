# Results — country cap, and profiles as mandates

Output of `2_optimisation_model/code/24_country_cap_and_mandate.py` and nothing else. Run time ~6 min.
Both additions come from FICO's own
[python-notebooks/xpress-api/modeling_examples](https://github.com/fico-xpress/python-notebooks/tree/main/xpress-api/modeling_examples).

The model is `2_optimisation_model/code/Main_model.py`. `ENABLE_COUNTRY_CAP` ships **OFF**, so nothing
here changes the existing results until it is switched on deliberately.

---

## Verification first

The group caps were rewritten from three `np.unique` loops to three
`groupby(...)["w"].sum()` constraints, the idiom in FICO's
`portfolio_pandas.ipynb`. That rewrite was **verified, not assumed**, twice:

- both forms write a **byte-identical LP file** (13 rows, 1077 cols, 2154
  elements) — `diff` returns nothing;
- all 15 frontier points re-solved with the pre-edit code and the edited code:
  **max |Δ weight| = 0.000e+00** at every point, Δn = 0, Δreturn = Δrisk = 0.

Separately, and unrelated to this work: the stored
`2_optimisation_model/results/efficient_frontier_*.csv` is **not** exactly reproducible on this
machine at the min-risk end — points 0–6 differ by up to 7.7e-05 in return and
±1 holding. The pre-edit code reproduces that same deviation exactly, so it is
an artefact of `MIP_GAP = 0.001` admitting alternative optima on the flat part
of the frontier, not of any code change. Points 8–14, including Neutral, match
to the last digit.

---

## Part A — the country cap

Model 2 capped **region** and **sector**. Switzerland fell between the two: it
is not a region, and it spans two sectors (cantonal banks, real estate), so
neither cap could see it.

Uncapped, Switzerland is the largest country at **14 of the 15** frontier
points — every one but the max-return corner, where Belgium leads at 21.0%.

| Profile (uncapped) | Switzerland | United States | two countries |
|---|---|---|---|
| Risk averse | **46.98%** | 45.26% | **92.24%** |
| Neutral | 36.74% | 48.29% | 85.03% |
| Risk prone | 4.24% | 60.00% | 64.24% |

The risk-averse book holds 92% of $100M in two countries while passing every
Model 2 constraint. That is the hole.

### What a cap costs

Two framings, because they differ by an order of magnitude and only one of them
is intuitive. The frontier is roughly 10x steeper at the min-risk end, so a
small risk penalty there equals a large return penalty.

| Cap | binds at | risk cost at matched return | return cost at matched risk |
|---|---|---|---|
| | | min-risk end / Neutral | min-risk end / Neutral |
| 20% | 12/15 pts | +0.228pp / +0.161pp | −1.84pp / −0.159pp |
| **25%** | **10/15 pts** | **+0.146pp / +0.112pp** | **−1.39pp / −0.067pp** |
| 30% | 10/15 pts | +0.084pp / +0.069pp | −1.01pp / −0.013pp |
| 40% | 3/15 pts | +0.014pp / +0.024pp | −0.35pp / ~0 (+0.006) |

No cap level made any frontier point infeasible.

### The recommended book barely moves

25% cap, Neutral profile:

| | uncapped | 25% cap |
|---|---|---|
| Return | 14.300% | 14.358% |
| Risk | 10.622% | 10.733% |
| Return / risk | 1.346 | **1.338** |
| Holdings | 30 | 30 |
| Weighted ESG | 70.000 | 70.000 |
| Switzerland | **36.74%** | **25.00%** |

11.7pp of Swiss concentration removed for 0.008 of the return/risk ratio. The
return actually rises slightly, because the capped frontier's corners move and
the 15-point grid shifts with them — which is itself an argument for Part B.

### The US exemption is forced, not chosen

`COUNTRY_CAP_EXEMPT = {"United States"}` is not a policy preference.
`REGION_CAP = 0.60` over two regions implies US >= 0.40, so any cap below 40%
applied to the US is infeasible on its own. Removing the exemption at 25% and
letting the new IIS diagnosis name the conflict:

```
1 independent IIS
--- IIS 1: 3 constraints, 0 bounds (total infeasibility 0.15) ---
  constraint budget_sum_w_eq_1            (relax the 'G' side)
  constraint region_cap=Europe            (relax the 'L' side)
  constraint country_cap=United States    (relax the 'L' side)
```

Total infeasibility **0.15 = 1 − 0.60 − 0.25** exactly: 15% of the budget has
nowhere to go. Mechanical, not argued.

---

## Part B — profiles as mandates instead of grid picks

`analyze_risk.py` chooses the three profiles post hoc from 15 sampled frontier
points with `idxmin` / `idxmax(sharpe)` / `idxmax`. Each is therefore the best
of 15, not an optimum. A mandate states the same intent directly: *maximise
return, then minimise risk while giving up at most X of the maximum*.

| Give up at most | Return | Risk | Ret/Risk | Held |
|---|---|---|---|---|
| 0% | 17.631% | 22.625% | 0.779 | 30 |
| 5% | 16.750% | 15.361% | 1.090 | 30 |
| **10%** | **15.868%** | **12.575%** | **1.262** | 30 |
| 15% | 14.986% | 11.254% | 1.332 | 30 |
| **20%** | **14.105%** | **10.484%** | **1.345** | 30 |
| 30% | 12.342% | 9.643% | 1.280 | 39 |
| 40% | 10.579% | 9.290% | 1.139 | 44 |

Two results worth the slide:

1. **0% reproduces the current Risk Prone exactly** (17.631% / 22.625% /
   0.779), which validates the construction.
2. **The current Risk Prone is dominated.** Giving up 10% of the maximum return
   — 1.76pp — removes **10.05pp** of volatility. "Maximise return" buys 1.76pp
   of return for 10pp of risk, and a mandate holder would not sign that.
3. 20% lands at ratio 1.345 against the grid-picked Neutral's 1.346, i.e. the
   mandate finds the same trade-off without needing a grid at all.

Each mandate is two ordinary MIQP solves and takes ~0.4s.

### Why not Xpress' native multi-objective

`markowitz_multiobj.ipynb` does this with `setObjective(priority=..., reltol=...)`.
Every objective must be **linear**, so the variance has to move into a transfer
variable, `Dot(w,Sigma,w) - variance <= 0`. Measured on this problem:

| form | quadratic elements | quadratic constraints |
|---|---|---|
| quadratic in objective | 1,159,929 in objective | 0 |
| quadratic in constraint | 580,503 in constraint | 1 |

That turns a convex MIQP into a quadratically **constrained** MIP. It did not
finish one solve in over two minutes, against ~0.8s for the MIQP. The
notebook's example has 5 assets, where the distinction never shows up.
Two explicit solves give identical semantics and keep the quadratic where
Xpress wants it.

---

## Files

| File | Contents |
|---|---|
| `cap_frontier.csv` | every frontier point at cap off / 20 / 25 / 30 / 40% |
| `cap_cost.csv` | per-point cost of each cap, both framings |
| `cap_profiles.csv` | the three profiles at every cap level |
| `mandate.csv` | the mandate sweep, cap off and cap 25% |
| `top_countries.csv` | six largest countries in each uncapped profile |

## Reproduce

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 24_country_cap_and_mandate.py
```
