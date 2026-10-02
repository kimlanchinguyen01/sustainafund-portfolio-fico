# Is 20 factors still the right number on the current data?

Output of `3_sensitivity_studies/code/29_factor_count_v4.py`, ~9 min. Re-validates a choice that was
made on superseded inputs.

## Why this needed checking

The 20-factor choice comes from `1_data_preparation/code/05d_factor_count.py`, and that script
reads `prices_clean_usd.csv` and `expected_return_shrunk_usd.csv` — USD prices
that are **not dividend-adjusted**, with the pre-v4 expected returns, solved
against the old `Model2` (no sector cap, no per-stock ESG floor, no Tier-1
screen).

The data then changed. `20_dividend_adjusted_pipeline.py` rebuilt everything
from total-return prices and carries the number forward as a constant:

```python
TD, K, MIN_OBS = 252, 20, 252
```

So **K = 20 was inherited, not re-derived**. Nobody had checked it on the
inputs we actually ship.

## The gate

At k = 20 the rebuilt covariance must reproduce `covariance_matrix_v4.csv`, or
the sweep is measuring something other than our model:

| | |
|---|---|
| Stocks rebuilt / shipped / common | 1087 / 1087 / 1087 |
| Max absolute difference | **1.8 × 10⁻¹⁵** |

Floating-point exact. The construction mirrors the pipeline line for line.

---

## What the 20 factors actually are

They are **not** named factors chosen in advance. They are the leading principal
components of the daily log-return matrix — the eigenvectors of the return
covariance of the 991 stocks with a complete 10-year history, used as regressors
for all 1087. Nothing about them is specified by us except how many to keep.

Variance explained, individually:

| Factor | 1 | 2 | 3 | 4 | 5 | 6–10 | 11–20 |
|---|---|---|---|---|---|---|---|
| % of total | **27.8** | **7.5** | 3.4 | 2.4 | 1.6 | 0.7–1.3 each | 0.4–0.7 each |

Cumulative: 1 factor 27.8%, 5 factors 42.8%, 20 factors 52.9%, 50 factors 61.4%.

They are unnamed, but the leading ones are interpretable after the fact:

| Factor | What it turns out to be | Evidence |
|---|---|---|
| 1 | **the market** | correlation **0.996** with an equal-weight index of the same stocks |
| 2 | **Europe vs the United States** | mean beta **+1.43** for European stocks, **−1.73** for US |
| 3 | **Energy vs Technology** | mean beta −2.76 Energy … +1.75 Technology |
| 4 | **Technology vs Utilities** | mean beta −1.47 Technology … +2.94 Utilities |
| 5–20 | no single clean reading | 0.4–1.6% of variance each — the tail that carries the residual block structure |

Factor 2 is worth noticing: the team tested an **explicit** region factor in
`05c_multifactor.py` and it did not fix the risk understatement. PCA finds the
region split on its own, as the second component, without being told about it.

## Why a factor model at all

From `04a_factor_model.py`: a complete-history sample covariance needs a common
history for every *pair*, which excluded **96 of 1093** stocks — they could never
be bought. A factor model fits each stock's betas on whatever days that stock
has, so a 2022 listing costs the other 1092 nothing, and `B F B' + diag(D)` is
positive semi-definite by construction.

## Why not 1 or 2 factors

`05a`/`05b`/`05c` established the mechanism, and it is not about naming: the
single-index model sets **every** off-diagonal residual covariance to zero, and
with a median R² of 0.28 that throws away 72% of each stock's variance from the
covariance structure. Residual correlations are +0.11 within a region and −0.11
across regions — a spread of 0.22 the diagonal model declares to be zero. The
average residual correlation is ~0 by construction, so the failure is invisible
in the mean and lives entirely in the block structure, where a minimum-variance
optimiser will go looking for it.

---

## The result on the current data

Error = predicted risk / realised risk − 1, in %. **Negative means the model
understates risk**, which is the failure mode a risk-averse mandate cannot
tolerate. Realised is the volatility those exact weights had over the estimation
window.

| k | Var expl | R² med | PSD | Condition | Err mean | Err at min-risk | Worst | Understates? |
|---|---|---|---|---|---|---|---|---|
| 1 | 27.8% | 0.273 | yes | 1946 | −17.38% | **−38.34%** | −38.34% | **yes** |
| 2 | 35.4% | 0.355 | yes | 2842 | −16.62% | −37.55% | −37.55% | **yes** |
| 5 | 42.8% | 0.436 | yes | 2957 | +4.27% | +0.31% | **+0.31%** | no |
| 10 | 47.5% | 0.469 | yes | 3186 | +3.93% | −1.56% | −1.56% | **yes** |
| **20** | **52.9%** | **0.518** | yes | 3672 | **+6.61%** | **+1.86%** | **+1.54%** | **no** |
| 30 | 56.4% | 0.547 | yes | 3845 | +8.99% | +3.06% | +2.74% | no |
| 50 | 61.4% | 0.586 | yes | 4389 | +11.79% | +5.90% | +4.33% | no |

### The core finding survives the data change

One or two factors understate portfolio risk by **38%** at the min-risk end on
the current data, against the ~40% `05d` measured on the non-dividend-adjusted
data. The cliff between 2 and 5 factors is real and it is not an artefact of the
old inputs. The slide "a cliff, not a gradient" still holds.

### But the *boundary* moved, and the criterion is fragile there

On the old data 20 was the smallest k with no understatement anywhere. On the
current data the smallest is **5** — and **10 fails** at −1.56%.

That non-monotonicity is not a bug, it is the metric working as designed: each k
produces a *different* portfolio, so what is being measured is whether the
optimiser can find a blind spot in that particular covariance. Near zero the
answer is noisy. k = 5 passes by **+0.31%**, which is a third of a percentage
point of margin, and k = 10 then dips negative. Picking the literal minimum on
that basis would be reading a razor-thin margin as a decision.

**k = 20 is the smallest k with a margin that is not marginal** — +1.54% worst
case, +1.86% at the min-risk end — and every k above it stays positive too.

### More is not better either

Error is monotone in k above 5, and it goes the *other* way: mean overstatement
+4.3% at k=5 → +6.6% at 20 → +9.0% at 30 → +11.8% at 50. Median R² climbs 0.436
→ 0.586, which past some point is fitting noise into the common structure rather
than removing it from the residual. Condition number rises 2957 → 4389.
Overstating risk is the safe direction, but 50 factors buys nothing and costs
conditioning.

## Verdict

**Keep 20.** It is not the minimum on the current data, and the honest statement
is not "20 is confirmed" but:

> One or two factors understate risk by ~38% at the min-risk end, on old and new
> data alike. Above five factors the model no longer understates, but the
> boundary is unstable — five clears it by 0.3 pp and ten falls back below zero.
> Twenty is the smallest count with a margin wide enough not to depend on which
> portfolio the optimiser happens to pick, and more than twenty only inflates
> the overstatement and the condition number.

That is a stronger answer at a viva than the original, because it survives the
question "did you re-check it after the data changed?" — and it names the
weakness of the minimum-k rule rather than hiding behind it.

## Files

| File | Contents |
|---|---|
| `sweep.csv` | per k: variance explained, median R², PSD, condition, all three error measures |
| `frontier.csv` | every frontier point at every k: predicted vs realised risk |
| `gate.csv` | the k=20 reproduction check against `covariance_matrix_v4.csv` |

## Reproduce

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 29_factor_count_v4.py
```

Needs `1_data_preparation/results/prices_div_usd.csv` (52 MB, gitignored). Rebuild with
`1_data_preparation/code/20_dividend_adjusted_pipeline.py` or ask Chloe.
