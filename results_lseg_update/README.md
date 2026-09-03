# The LSEG "ESG and sector" update — parsed, measured, not adopted

Output of `../27_lseg_esg_sector_update.py`, ~5 min. **The delivered inputs were
not modified.** Parsed inputs sit in `../data_lseg_update/`, ready if we adopt.

Source: `ESG and sector.xlsx`, an LSEG export covering all 1093 tickers with
`TR.TRESGScore`, `TR.GICSSector` and `TR.GICSIndustryGroup`. Ticker set matches
`shares_imputed.csv` exactly — 1093 in, 1093 matched, none missing either way.

---

## Bottom line

The recommendation is **robust to this update**. Neutral moves from
14.300% / 10.622% / ratio 1.346 to **14.230% / 10.585% / ratio 1.344** with both
changes applied — a return change of **−0.069 pp** and a ratio change of
−0.002. Holdings stay at 30, weighted ESG stays pinned at exactly 70.00.

That is worth having as a result in its own right: an independent, newer ESG
vintage and a different sector taxonomy move the recommended book by less than
a tenth of a percentage point.

---

## Three separate things are in that file

They have to be judged separately, because they are not equally good.

### 1. It fills 47 of the 49 ESG values we imputed — a real improvement

Our imputation used **sector medians**, visible in the data as the repeated
values 56.8608 and 62.0263. Against LSEG's actual scores those medians were off
by a mean of **14.07 points**, max **45.92**:

| Stock | Imputed | LSEG | Difference |
|---|---|---|---|
| BFT.WA | 62.03 | 31.46 | **−30.56** |
| AIG.N | 56.86 | 68.71 | +11.85 |
| ALB.N | 56.86 | 67.31 | +10.45 |
| CCI.N | 56.86 | 57.01 | +0.15 |

So the imputation was substantially wrong per stock, and it did not matter,
because the optimiser was not leaning on those 49 names. Robust here — but that
was luck rather than design, and it is a good argument for adopting real values
instead of relying on it holding next time.

Two tickers have no LSEG score (`ABVX.PA`, `TPRO.MI`); they keep their current
value so a blank cell cannot shrink the universe.

### 2. It also revises the 1044 scores we already had — a different vintage, not an addition

| | |
|---|---|
| Comparable values | 1044 |
| Mean absolute change | **1.86 points** |
| Largest change | **17.31** (BWY.L 49.48 → 66.79) |
| Unchanged to 0.01 | **17 of 1044** |
| Changed by more than 1 point | 444 |

This is not a gap-fill. It is a fresh pull of the whole ESG column.

### 3. It is a different sector taxonomy, not a refinement of ours

GICS, 11 buckets, same count as the current file. Most of the apparent change is
renaming: Financial Services → Financials, Healthcare → Health Care, Consumer
Cyclical → Consumer Discretionary, Technology → Information Technology, Consumer
Defensive → Consumer Staples, Basic Materials → Materials.

After accounting for that, **71 of 1093 stocks (6.5%) genuinely change bucket**
— the ones the 30% sector cap can see. Examples: ADP.OQ Technology →
Industrials, AMCR.N / AVY.N / BALL.N Consumer Cyclical → Materials, ANA.MC
Industrials → Utilities, ADYEN.AS Technology → Financials.

`TR.GICSIndustryGroup` is genuinely new: **25 groups**, a level finer than
anything we had.

---

## What it does to the model

Four runs, isolating each change. Full frontier each time, same 15 points.

| Config | Profile | Return | Risk | Ratio | Held | ESG |
|---|---|---|---|---|---|---|
| baseline | risk_averse | 9.871% | 9.255% | 1.067 | 42 | 70.00 |
| baseline | **neutral** | **14.300%** | **10.622%** | **1.346** | 30 | 70.00 |
| baseline | risk_prone | 17.631% | 22.625% | 0.779 | 30 | 70.00 |
| new ESG | neutral | 14.257% | 10.605% | 1.344 | 30 | 70.00 |
| new sectors | neutral | 14.305% | 10.625% | 1.346 | 30 | 70.00 |
| **both** | **neutral** | **14.230%** | **10.585%** | **1.344** | 30 | 70.00 |

Change from baseline, in percentage points:

| Config | Profile | Δ return | Δ risk | Δ ratio |
|---|---|---|---|---|
| new ESG | risk_averse | −0.004 | +0.000 | −0.0004 |
| new ESG | neutral | −0.043 | −0.016 | −0.0020 |
| new ESG | risk_prone | −0.082 | **−0.394** | **+0.0101** |
| new sectors | risk_averse | +0.001 | +0.000 | +0.0000 |
| new sectors | neutral | **+0.005** | +0.004 | +0.0000 |
| new sectors | risk_prone | +0.000 | +0.000 | +0.0000 |
| both | risk_averse | −0.038 | +0.002 | −0.0043 |
| both | neutral | −0.069 | −0.036 | −0.0019 |
| both | risk_prone | −0.082 | −0.394 | +0.0101 |

**The sector change is worth nothing at all** — +0.005 pp at neutral, exactly
0.000 at risk-prone. The 71 reclassified stocks are not in the buckets where the
30% cap binds, so GICS and the current taxonomy give the optimiser the same
problem.

**The ESG change is worth −0.043 pp at neutral.** The only visible effect is at
the risk-prone corner, where risk falls 0.394 pp and the ratio actually
*improves* by 0.010, because three more stocks drop below the ESG floor and the
corner loses some of its most volatile names.

Universe: 1077 → **1074** with the new ESG, because stocks below the floor of 30
go from 10 to 13 (`APP.OQ`, `ATO.N` join, and `BMEB.L` leaves the list as its
score rises from 22.90 to 38.18).

---

## The caveat that decides whether to adopt

**The ESG column is not one cross-section.** The per-cell formulas on the second
sheet show the fiscal period varies by row:

| Fiscal period | Tickers |
|---|---|
| FY2024 | 556 |
| FY2025 | 529 |
| FY2026 | 4 |
| FY2023 | 1 |
| FY2022 | 1 |
| missing | 2 |

An `ESG >= 70` constraint on this column compares one company's FY2024 score
against another's FY2025 score. Roughly half and half, so this is not a handful
of stragglers — it is the shape of the column.

Our current file is a single earlier vintage, which is internally consistent but
contains 49 sector-median guesses. Neither column is clean. The choice is
between **consistent-but-partly-invented** and **real-but-mixed-vintage**.

---

## Recommendation

**Adopt the sectors, decide on ESG deliberately.**

- **GICS sectors: adopt.** Zero measurable effect on any result, a standard
  taxonomy that is easier to defend than Morningstar-style labels, and it brings
  25 industry groups we did not have. There is no cost.
- **ESG: adopt the whole LSEG column rather than blending.** Taking LSEG's 47
  gap-fills while keeping our vintage for the other 1044 would produce a column
  from two different pulls — a third kind of inconsistency, and the hardest to
  explain. One sourced export with a stated fiscal-period spread is more
  defensible at a viva than a blend, and it removes the imputation entirely.
  State the FY2024/FY2025 split as a known limitation.
- If ESG is adopted, these need re-running before the deck:
  `23_scenario_matrix.py` (the ESG cost decomposition and floor sensitivity are
  all ESG-dependent), `24_country_cap_and_mandate.py`, `stress_test/`,
  `backtest_profiles/`, then `dashboard_data/build_dashboard_data.py`. About 30
  minutes of compute. The published numbers would shift by under 0.1 pp, so this
  is a provenance decision, not a results decision.

### What does NOT change either way

The industry groups confirm the country-cap argument rather than replacing it.
The Swiss names that drove the 47% concentration are `MOBN.S` / `ALLN.S` /
`PSPN.S` in **Real Estate Management & Development** and `BCVN.S` / `VATN.S` in
**Banks** — two distinct industry groups, so even a cap at the finer level would
not have caught them. Only a country cap does.

---

## Files

| File | Contents |
|---|---|
| `esg_comparison.csv` | per stock: current, LSEG, difference, fiscal period, was-imputed flag |
| `sector_crosswalk.csv` | per stock: current sector, GICS sector, GICS industry group, moved flag |
| `sector_moves.csv` | only the 71 that genuinely change bucket |
| `profiles.csv` | the three profiles under all four configurations |
| `frontier.csv` | every frontier point under all four configurations |

Parsed model inputs, not yet used by anything:

| File | Contents |
|---|---|
| `../data_lseg_update/shares_esg_lseg.csv` | `shares_imputed.csv` with the LSEG ESG column |
| `../data_lseg_update/sectors_gics.xlsx` | Stock, Sector (GICS), IndustryGroup |

## Reproduce

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
python3 27_lseg_esg_sector_update.py
```

The source workbook is kept in the repo as
`data_lseg_update/ESG_and_sector_lseg.xlsx` (86 KB), so this does not depend on
a WhatsApp temp directory. Override with `LSEG_XLSX=/path/to/file.xlsx`.
