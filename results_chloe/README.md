# Results — corrected Model2_ori.py

Everything here is the output of running `../Model2_ori.py` and nothing else.
Two invocations, differing only in `ENABLE_TIER2_EXCLUSION`.

## What was corrected in the model first

Defects only; the design and the defaults are unchanged. `git log -p Model2_ori.py`
shows every line.

| # | Defect | Effect before the fix |
|---|---|---|
| 1 | four Tier-2 tickers absent from this dataset | the screen excluded **6 of 10**, silently. `BA.L`→`BAES.L`, `HO.PA`→`TCFP.PA`, `LDO.MI`→`LDOF.MI`, `SAAB-B.ST`→`SAABb.ST`. `BA.L` was the dangerous one — `BA.N` exists here and is **Boeing** |
| 2 | `SCENARIO_TAG` hand-edited, its comment self-referential | the second run **overwrote** the first run's CSVs. Now derived by `scenario_tag()` from the active toggles, so it cannot go stale |
| 3 | `MIP_GAP = 0.01` | the cost of a cheap constraint read roughly **double** its true value (0.078pp at 1% vs 0.042pp at 0.1%). Tightening costs no measurable time |
| 4 | inputs pointed at the 31 Aug files | new constraints would have been evaluated on local-currency prices over a 997-stock complete-case universe. Now `expected_return_v4.csv` / `covariance_matrix_v4.csv` — USD, **dividend-adjusted**, 20-factor, 1087 stocks |
| 5 | `mode="max_return"` compared a variance against `risk_cap` unsquared | the cap was 2.89x looser than intended and on this data never bound at all: asking for 12% risk returned a **22.29%** portfolio. Now `risk_cap ** 2`, verified at 12.08%. The mode is unused by the script but the case study proposes it explicitly |

## Input change: dividend-adjusted prices

These results are built on `prices_lseg_dividend_adjusted.csv`, not on closing
prices. A plain close omits dividends and therefore understates exactly the
high-yield, low-volatility names a minimum-variance book is made of. The file
checks out on three independent signs:

- back-adjusted, anchored at the end: `adj/raw` runs 0.68 → 0.81 → **1.00** for
  Unilever, and 0.959 → 0.999 for NVDA, which pays almost nothing
- volatility is unchanged, 31.08% → 31.05% — dividends add drift, not noise
- the increase is ordered by dividend yield across sectors: Energy +3.89pp,
  Utilities +3.66, Financial Services +3.36, Real Estate +3.31, Consumer
  Defensive +2.76, against Technology +1.18 and Healthcare +1.23

Effect on the estimates: median expected return **7.80% → 10.39%**, stocks with
a negative expected return **3 → 0**, correlation with the previous estimate
0.972 — the level moved, the ranking largely did not.

Effect on the frontier: it shifts up by roughly 2.8pp. The minimum-variance book
now returns **9.92%** at 9.26% risk, against 7.07% at 9.24% before. The gain
lands hardest exactly at the risk-averse end, which is where the high-dividend
names sit.

> **Six stocks are empty in the source file** — 2870 of 2870 values missing,
> where the previous file had a full history: `HOLN.S`, `URW.PA`, `EA.OQ`,
> `AVB.N`, `EQR.N`, `HWM.N`. Three of the six are REITs, whose adjustment
> factors are the largest, so the extraction most likely failed on them. They
> are **dropped** (1093 → 1087) rather than back-filled from the unadjusted
> file: an unadjusted series carries a ~3pp lower return, and the optimiser
> would then penalise them for a data defect rather than for their quality.
> `EA.OQ` was held at ~1% in the previous risk-averse book. **Worth
> re-extracting these six.**

## The two runs

| tag | configuration |
|---|---|
| `sec30_tier1_tier2off` | sector cap 30%, ESG ≥ 70, Tier 1 excluded — **the shipped default** |
| `sec30_tier1_tier2on` | the same plus Tier 2 excluded |

Both completed 15/15 frontier points, ESG binding at exactly 70.00 throughout.

## The answer the two-run design was built to get

**Excluding Tier 2 costs nothing: −0.019 pp of annual return on average.**

| risk | tier2off | tier2on | cost |
|---|---|---|---|
| 9.26% | 9.980% | 9.840% | **−0.139 pp** |
| 11.17% | 14.900% | 14.897% | −0.003 pp |
| 14.99% | 16.644% | 16.641% | −0.003 pp |
| 22.62% | 17.631% | 17.631% | 0.000 pp |

The whole cost sits at the minimum-variance corner and vanishes along the rest of
the frontier. Reason: Tier 1 is already on in both runs, so Rheinmetall is out
either way, and the ten Tier-2 names only reach **2.08%** of the book anywhere —
in the risk-averse portfolio of `tier2off`. The conclusion is unchanged from the
closing-price run (−0.016 pp there), which is itself reassuring: the answer does
not depend on the dividend treatment.

So the contested policy can be decided on principle. The data does not charge for
it. Differences under ~0.03 pp are at the level of the MIP gap and the frontier
interpolation grid, so read the +0.002 entries as zero, not as a gain.

## Two things worth looking at

**The ESG score does not screen weapons.** Rheinmetall's ESG is **87.3**,
Leonardo's 89.2, Lockheed's 85.6 — all comfortably above the 70 threshold. Run
with `ENABLE_TIER1_EXCLUSION = False` and Rheinmetall takes up to **10.2%** of
the book. The controversial-industry screen does work the ESG constraint does not,
and that is the strongest argument for keeping it.

**Country concentration is unconstrained.** The sector cap holds Consumer
Defensive to exactly 30.00%, but Switzerland reaches **46.8%** (tier2off) and
**47.1%** (tier2on) of the risk-averse book — Swiss cantonal banks and real
estate. The sector cap cannot see this because it is not one sector. A 25%
country cap held it to 25.0% at a cost of 0.156 pp; that cap is currently not in
this model. This is the most obvious next thing to add.

## Files

```
efficient_frontier_model2_<tag>.csv    frontier: return, risk, ESG, n, sector and
                                       region exposures, tier weights per point
efficient_frontier_weights_<tag>.csv   full weight vector per frontier point
portfolio_<run>_<profile>.csv          holdings of the three profiles: weight,
                                       USD amount, sector, country, ESG, mu
portfolio_summary.csv                  the six portfolios on one page
comparison_tier2.csv                   return at matched risk, both runs
```

Profiles are picked by rule, not by hand: minimum risk; maximum return/risk
ratio; and the highest-return point that is not a degenerate corner (top-3 weight
≤ 40% and at most 15 positions on the 1% floor).

## Reproducing

```bash
export XPAUTH_PATH=/path/to/xpauth.xpr
python3 Model2_ori.py                      # -> tier2off
# set ENABLE_TIER2_EXCLUSION = True
python3 Model2_ori.py                      # -> tier2on, no longer overwrites
```

Needs `covariance_matrix_v4.csv` (23 MB, gitignored). Regenerate with a single
script: `pipeline/20_dividend_adjusted_pipeline.py`, about 3 minutes. It takes
`prices_lseg_dividend_adjusted.csv` through cleaning, USD conversion at daily ECB
rates, truncation at trading discontinuities, and the estimator.
