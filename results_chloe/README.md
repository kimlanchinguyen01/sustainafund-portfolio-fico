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
| 4 | inputs pointed at the 31 Aug files | new constraints would have been evaluated on local-currency prices over a 997-stock complete-case universe. Now `expected_return_v3.csv` / `covariance_matrix_v3.csv` — USD, 20-factor, 1093 stocks |

## The two runs

| tag | configuration |
|---|---|
| `sec30_tier1_tier2off` | sector cap 30%, ESG ≥ 70, Tier 1 excluded — **the shipped default** |
| `sec30_tier1_tier2on` | the same plus Tier 2 excluded |

Both completed 15/15 frontier points, ESG binding at exactly 70.00 throughout.

## The answer the two-run design was built to get

**Excluding Tier 2 costs nothing: −0.016 pp of annual return on average.**

| risk | tier2off | tier2on | cost |
|---|---|---|---|
| 9.25% | 7.135% | 7.007% | **−0.127 pp** |
| 11.11% | 12.766% | 12.768% | +0.002 pp |
| 14.84% | 14.912% | 14.912% | −0.001 pp |
| 22.29% | 16.201% | 16.201% | 0.000 pp |

The whole cost sits at the minimum-variance corner and vanishes along the rest of
the frontier. Reason: Tier 1 is already on in both runs, so Rheinmetall is out
either way, and the ten Tier-2 names only reach **2.08%** of the book anywhere —
in the risk-averse portfolio of `tier2off`.

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
Defensive to exactly 30.00%, but Switzerland reaches **46.2%** (tier2off) and
**47.2%** (tier2on) of the risk-averse book — Swiss cantonal banks and real
estate. The sector cap cannot see this because it is not one sector. A 25%
country cap held it to 25.0% at a cost of 0.156 pp; that cap is currently not in
this model.

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

Needs `covariance_matrix_v3.csv` (23 MB, gitignored). Regenerate:
`pipeline/02a` → `pipeline/03a` → `pipeline/13` → `pipeline/14`, about 5 minutes
total; see the root README.
