# Handoff — read this first

FICO case study "Portfolio Selection", HTW Berlin summer school 2026. Pick stocks
and weights for a $100M mid-term mandate under concentration, region, sector and
ESG constraints, trading expected return against risk.

- **Project root:** `~/Documents/FICO-case-study`
- **GitHub:** https://github.com/tamarapodpala-beep/fico-sustainafund (private)
- **Licence:** `xpauth.xpr` in the project root, gitignored. Set `XPAUTH_PATH` to
  it before any Xpress call.
- **Team:** Tamara (owner), Chi Chloe (`kimlanchinguyen01`), `NBK-emi`. Both
  collaborators with push access.

---

## The current model

**`Model2_ori.py`** in the repo root — Chloe's model, with defects fixed. This is
the model. It opens exactly four files:

```
expected_return_v4.csv      James-Stein shrunk mu, USD, dividend-adjusted
covariance_matrix_v4.csv    20-factor PCA, 1,087 stocks, PSD by construction
shares_imputed.csv          region, country, ESG (49 values imputed)
sectors.xlsx                sector per stock, 1093/1093, no gaps
```

Formulation: MIQP. `min w'Sw` subject to `w'mu >= beta`, `sum w = 1`,
`0.01 y_i <= w_i <= 0.20 y_i`, `y_i` binary, `sum y_i >= 30`, region <= 60%,
sector <= 30%, weighted ESG >= 70, per-stock ESG >= 30. Solves in 0.3–1.1 s.
A per-country cap now exists too but ships **OFF** (`ENABLE_COUNTRY_CAP = False`);
see "Country cap" below for what it costs and what is left to decide.

`pipeline/Model2.py` is the untouched audit baseline. Every later model asserts
it reproduces `Model2.py` exactly when its own additions are disabled.

**Current portfolios** (`results_chloe/portfolio_summary.csv`):

| | Return | Risk | Ret/Risk | Holdings |
|---|---|---|---|---|
| Risk Averse | 9.87% | 9.26% | 1.067 | 42 |
| **Neutral (recommended)** | **14.30%** | **10.62%** | **1.346** | 30 |
| Risk Prone | 17.63% | 22.62% | 0.779 | 30 |

Scenario definitions follow Chloe's `analyze_risk.py`: min risk, max return/risk,
max return.

---

## How to rebuild everything

```bash
export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
cd pipeline
python3 02a_esg_and_price_eda_cleaning.py     # ESG imputation      ~1 min
python3 20_dividend_adjusted_pipeline.py      # the whole chain     ~3 min
cd .. && python3 Model2_ori.py                # the frontier        ~15 s
python3 23_scenario_matrix.py                 # 24 scenarios        ~2 min
cd pipeline && python3 21_backtest_walkforward.py   # backtest      ~10 min
cd .. && python3 28_scenarios_for_deck.py     # the deck's scenarios ~2 s
python3 build_deck.py                         # the PDF deck        ~20 s
```

`20_dividend_adjusted_pipeline.py` does cleaning, USD conversion, discontinuity
truncation and estimation in one pass. Raw price files are **not** in git (49 MB
and 21 MB, LSEG-derived): `prices_lseg_dividend_adjusted.csv` is Chloe's export.

---

## Findings already measured — do not redo these

Each is reproducible from the script named. Re-deriving them wastes a session.

| Finding | Number | Script |
|---|---|---|
| Local-currency Sigma understated risk | min-var book 8.46% believed vs 10.13% actual; +5.71pp available at matched risk | `03c`, `12` |
| FX is a real covariance factor | same holdings realised 8.04% local vs 8.99% USD; `var(fx)` = 17.6% of total | `12_fx_model_free.py` |
| Dividends matter | median mu 7.80% -> 10.39%; rise ordered by dividend yield by sector | `20` |
| Complete-case rule excluded 96 stocks | factor model retains all; recovered names take 11.2% of capital at min-risk | `04a`, `20` |
| 20 factors, not 1–2 | 1 factor understates risk 39.9% at min-risk end; 20 is the smallest with none anywhere | `05d_factor_count.py` (OLD data) |
| That was measured on SUPERSEDED inputs | `05d` reads non-dividend-adjusted prices and the pre-v4 mu, against the old `Model2`; `20`'s `K = 20` is inherited, not re-derived | `05d` vs `20` |
| Re-validated on v4: the cliff survives | 1–2 factors still understate ~38% at min-risk (was ~40%) | `29` |
| But the minimum k moved and the criterion is fragile | smallest sufficient k is now 5 (+0.31% margin) while k=10 FAILS at -1.56%; 20 is the smallest with a non-marginal margin (+1.54% worst) | `29` |
| More factors is not better | mean overstatement +4.3% at k=5 -> +11.8% at k=50, R2 median 0.436 -> 0.586, condition 2957 -> 4389 | `29` |
| The factors are PCA components, and interpretable after the fact | f1 = market (corr 0.996 with an equal-weight index, 27.8% of variance), f2 = Europe vs US (beta +1.43 vs -1.73, 7.5%), f3 = Energy vs Tech, f4 = Tech vs Utilities | `29` |
| Quadratic beats linear | linear carries +19.2% more true risk; its objective/actual gap is 1.64x | `15_model1_linear.py` (archive) |
| Binaries required | semi-continuous alone returns 26 positions while reporting 30 | tested inline |
| ESG cost decomposition | average >=70 costs -0.151pp at Neutral; the per-stock floor costs +0.008pp, i.e. zero | `23_scenario_matrix.py` |
| ESG does not screen weapons | Rheinmetall ESG 87.3, takes 10.2% without the Tier 1 screen | `23` |
| ESG floor is not fragile | floor 20/30/40 -> 14.299 / 14.300 / 14.305% at Neutral | `23` |
| Tier 2 exclusion is free | -0.004pp at Neutral | `23` |
| Sector cap lowers risk where it binds | off raises Risk Prone volatility 22.63% -> 23.14% | `23` |
| Country and sector caps do not substitute | country cap only -> sector hits 39.8%; sector cap only -> Switzerland hits 46.8% | `18` (archive) |
| Portfolio is unstable across windows | Jaccard 0.27, 64% of capital placed differently, 5y vs 10y | `03e` |
| That instability is regime change, not noise | bootstrap converges within a window (top frequency 1.00) but cores disagree across windows | `06a` |
| Bootstrap resampling does not fix it | Jaccard 0.29 -> 0.31 | `06a` |
| Backtest: no Sharpe edge over 1/N | 0.835 vs 0.866, t = -0.85, not significant | `21` |
| Backtest: real volatility edge | -22% overall, lower in 5 of 6 sub-periods; wins the 2020 crash and 2022 | `21` |
| Risk understated out of sample | predicted 8.78% vs 13.21% realised, 50.4% | `21` |
| Turnover | 20.8% per rebalance, ~83% a year, 0.18pp of CAGR at 10bp | `21` |
| Two data defects found | ZEG.L (reverse takeover) and BMPS.MI (recapitalisation) truncated, not dropped | `10`, `13` |
| A position "at a bound" needs a 1e-5 tolerance, not 1e-6 | MIP_GAP 0.001 leaves the smallest min-risk holding at 0.010005, five parts per million above the 1% floor | `28` |
| Country concentration is real | Switzerland 46.98% of the risk-averse book, largest country at 14 of 15 frontier points; Switzerland + US = 92.2% of that book | `24` |
| A 25% country cap is cheap | +0.112pp risk at Neutral at matched return, or -0.067pp return at matched risk; Neutral ratio 1.346 -> 1.338, still 30 holdings, ESG still 70.00 | `24` |
| The cap is expensive only at the left end | +0.146pp risk at min-risk = -1.39pp return at matched risk, because the frontier is ~10x steeper there | `24` |
| No cap level is infeasible | 20/25/30/40% all solve at all 15 points; binds at 12/10/10/3 points | `24` |
| The US exemption is forced, not chosen | IIS = {budget, region_cap=Europe, country_cap=US}, total infeasibility exactly 0.15 = 1 - 0.60 - 0.25 | `24` |
| "Max return" is a dominated profile | giving up 10% of max return (1.76pp) removes 10.05pp of risk: 15.87%/12.58% ratio 1.262 vs 17.63%/22.62% ratio 0.779 | `24` |
| A mandate finds Neutral without a grid | "give up <= 20% of max return" -> ratio 1.345 against the grid-picked 1.346 | `24` |
| groupby caps == loop caps | byte-identical LP file; all 15 points re-solved, max abs weight difference 0.000e+00 | `24` |
| Native multi-objective is unusable here | linear-objective rule forces variance into a constraint: MIQP (1,159,929 obj q-elements) -> quadratically constrained MIP (580,503 q-elements, 1 q-constraint), no solve in >2 min vs ~0.8s | `24` |
| Delivered book halves crisis drawdowns (in sample) | COVID -15.86% vs 1/N -36.17%; 2022 -8.38% vs -25.26%; recovers in 99 days vs 175 | `25` |
| But out of sample Neutral does not protect | beats 1/N in 1 of 3 crises: COVID +6.1pp, 2018 Q4 -0.8pp, 2022 -6.8pp | `25` |
| The protection lives at the min-variance end | risk-averse beats 1/N in all 3 crises (+7.6 / +4.4 / +2.1pp) while Neutral loses two | `25` |
| Predicted risk fails hardest exactly when it matters | realised/predicted 1.83x in 2018 Q4, 1.44x in 2022, **6.71x** in the COVID crash | `25` |
| Swiss concentration did not earn its size | COVID: -0.157pp per 1% held vs -0.143pp for the US, at 36.7% vs 48.3% weight | `25` |
| Country cap is free in a crisis too | Neutral cap off vs 25%: -0.12 / +0.16 / -0.28pp across the three windows | `25` |
| The 36.7% Swiss position is an estimator artefact | point-in-time Ledoit-Wolf books hold at most 9.7-19.9% per country, so a 25% cap barely binds | `25` |
| 2015 and 2016 crises cannot be tested point-in-time | 156 and 384 trading days of history exist before them; 500 needed | `25` |
| Harness gate: min-variance reproduces script 21 | Sharpe 0.829 vs 0.835, vol 13.197 vs 13.210, maxDD -33.81 vs -33.89 | `26` |
| **No book beats 1/N significantly, in either direction** | t = -0.87 (minvar), +0.60 (mandate20), +1.12 (mandate10); the whole Sharpe spread 0.829-0.914 is noise | `26` |
| Return-seeking profiles turn over twice as much | 170% p.a. (mandate20) vs 83% (minvar); at 10bp mandate20's Sharpe falls to 0.857, BELOW 1/N's 0.866 | `26` |
| Risk is the robust, monotone result | realised vol 13.20 / 16.91 / 20.08 / 23.30% and maxDD -33.8 / -37.7 / -42.3 / -46.0% for minvar / 1/N / mandate20 / mandate10 | `26` |
| Mandates are a bull-market bet | win 2020 rebound (+56% vs +18%) and the AI rally (+33% vs +21%), lose 2022 by 22pp (-34.3% vs -12.6%) | `26` |
| Mandate anchors on the noisiest estimate available | out of sample the max-return corner comes from an unshrunk 3y sample mean: 45.85% predicted return at the first rebalance | `26` |
| Option B (2-3 rebalance points) contradicts itself here | mandate20 "beats 1/N" (+0.087) on one split and "loses" (-0.244) on another; spread 0.331 vs the 31-rebalance +0.010 | `26b` |
| B also overstates the min-variance loss 4-8x | -0.173 / -0.319 / -0.201 by split, against -0.038 over 31 rebalances | `26b` |
| The LSEG ESG/sector update barely moves the book | Neutral 14.300/10.622/1.346 -> 14.230/10.585/1.344 with both changes; -0.069pp return | `27` |
| GICS sectors are worth exactly nothing here | +0.005pp at Neutral, 0.000 at Risk Prone: the 71 reclassified stocks are not where the 30% cap binds | `27` |
| Our ESG imputation was individually wrong by 14 points | sector medians vs LSEG actuals: mean abs 14.07, max 45.92 (BFT.WA 62.03 -> 31.46) - and the portfolio did not notice | `27` |
| The new ESG column mixes fiscal years | FY2024 556, FY2025 529, plus FY2026 4 / FY2023 1 / FY2022 1 / missing 2 | `27` |
| It also revises the 1044 scores we already had | mean abs 1.86, max 17.31, only 17 of 1044 unchanged - a new vintage, not a gap-fill | `27` |

---

## Open

1. **Country cap — BUILT AND MEASURED, one decision left.** In `Model2_ori.py`,
   default OFF. Numbers in `results_country_cap/README.md`. The 0.156pp figure
   previously quoted here came from the frozen v3 track and is superseded: on v4
   data a 25% cap costs +0.112pp of risk at Neutral, or -0.067pp of return at
   matched risk, and removes 11.7pp of Swiss concentration.
   **What is left:** decide whether to switch it on for the final book, and if so
   at which level (25% is the recommendation — 40% barely binds, 20% costs 44%
   more for 5pp less concentration), then re-run `23_scenario_matrix.py` and the
   deck. Nothing else depends on it.
2. **The recommendation itself is now open, and script 26 sharpens the choice.**
   Two independent tests point the same way. `stress_test/` (crisis windows):
   out of sample Neutral beats 1/N in one crisis of three and loses 2022 by
   6.8pp, while min-variance beats it in all three. `backtest_profiles/` (31
   rebalances, 7.7 years): **no book beats 1/N significantly** — every t is
   inside ±1.96 — so no Sharpe claim is available to anyone, in either
   direction. What is robust is risk: min-variance is the only book materially
   below the benchmark on both volatility and drawdown, and the return-seeking
   mandates turn over twice as much, which at 10bp puts mandate20 under the
   benchmark.
   **The defensible position is therefore risk, not return:** recommend on
   measured volatility and drawdown reduction and say plainly that no
   risk-adjusted edge is statistically demonstrable over 7.7 years. Decide
   before the final deck; `QA_prep.md` needs a Q on it either way.
   Cheap next run that would sharpen it further: shrink mu at each rebalance
   before solving the mandate, which separates "the profile fails out of sample"
   from "an unshrunk 3-year sample mean fails out of sample". No extra solve
   cost. See the last section of `backtest_profiles/README.md`.
3. **Dashboard.** Not started. A separate requirement in the brief and the
   largest remaining piece of work. Streamlit was the intended choice; port 8501
   is already forwarded in the devcontainer.
4. **Adopt the LSEG ESG/sector update, or not.** Parsed and measured in
   `results_lseg_update/`; the delivered inputs are untouched and ready-to-use
   inputs sit in `data_lseg_update/`. Recommendation in that README: adopt the
   GICS sectors unconditionally (zero measurable effect, standard taxonomy, and
   it brings 25 industry groups), and adopt the ESG column WHOLE rather than
   blending our vintage with their gap-fills. The trade is
   consistent-but-partly-invented against real-but-mixed-vintage.
   If ESG is adopted, re-run `23`, `24`, `stress_test/`, `backtest_profiles/`
   and `dashboard_data/build_dashboard_data.py` - about 30 min of compute, and
   the published numbers shift by under 0.1pp. It is a provenance decision, not
   a results decision.

5. **Six missing price series** in Chloe's total-return export — `URW.PA`,
   `AVB.N`, `EQR.N` (REITs), `HOLN.S`, `EA.OQ`, `HWM.N`. 2870 of 2870 values
   absent where the previous file had a full history. Dropped rather than
   back-filled (an unadjusted series would cost them ~3pp). Worth re-extracting.
6. **`build_deck.py` — FIXED, and the deck is now reproducible from a clean
   clone.** It read `/tmp/scen.json`, which nothing in the repo wrote, so the
   documented `python3 build_deck.py` crashed anywhere /tmp had been cleared.
   `28_scenarios_for_deck.py` regenerates that file into
   `results_chloe/scenarios_for_deck.json` from committed artefacts only, and
   verifies itself field-by-field against the original (ALL FIELDS MATCH).
   Rebuilt with /tmp/scen.json deleted, the PDF is text-identical to the one
   that shipped. Every other input build_deck.py reads is in git. The only
   remaining /tmp use is the debug PNG *write*, which is intentional.
   Also removed there: a dead `portfolio_summary.csv` load, see item 7.
   **Still not regenerable, though committed and therefore working:**
   `results_chloe/backtest/backtest_subperiods.csv` and
   `backtest_diagnostics.csv`. `backtest_profiles/results/` now produces
   equivalents in the same regime windows, but wiring them in would change the
   slides from the min-variance book to a four-book comparison, so that is a
   deliberate decision rather than a fix.

7. **`results_chloe/portfolio_summary.csv` disagrees with every other artefact
   about Risk Prone.** Its risk-prone row is frontier point **11** (15.97% /
   12.77% / ratio 1.250); the deck, `risk_profile_scenarios_summary.csv`,
   `23_scenario_matrix.py` and this document all use point **14** (17.63% /
   22.62% / 0.779), which is what `idxmax(return)` gives. The table at the top of
   this file cites `portfolio_summary.csv` as its source but quotes point 14.
   The deck is unaffected (it never reads `S`). Decide which one is intended and
   regenerate the odd one out.

8. Not done and worth saying so: factor-level return attribution, transaction
   costs inside the optimiser.

---

## Deliverables that exist

| File | What |
|---|---|
| `SustainaFund_interim_review.pdf` | 14-slide deck, 16:9, built by `build_deck.py` |
| `QA_prep.md` | 22 likely questions with answers, all figures verified |
| `FINAL_data_cleaning/` | self-contained package for Chloe: code, data, Excel, results |
| `results_chloe/` | current model output — the two frontier runs and three profiles |
| `pipeline/README.md` | classifies all 25 scripts: 4 live, 6 superseded, 15 diagnostic |
| `archive/our_model_frozen/` | the country-cap track, frozen, recoverable at tag `freeze-candidate-v3` |
| `24_country_cap_and_mandate.py` | produces every number in the two additions below, ~6 min |
| `results_country_cap/` | its output: 5 CSVs + a README with the tables ready for slides |
| `25_crisis_stress_test.py` | crisis-window stress test of the DELIVERED books, ~7 min |
| `stress_test/` | crisis-window stress test: code, 6 CSVs, README. Panel A in-sample, Panel B point-in-time |
| `backtest_profiles/` | walk-forward of the RECOMMENDED profile, 4 books, code + 6 CSVs + README |
| `dashboard_data/` | 38 CSVs, 662 KB, one place with stable names; rebuilt by its own script |
| `27_lseg_esg_sector_update.py` | parses and measures the LSEG ESG/GICS export, ~5 min |
| `28_scenarios_for_deck.py` | regenerates the deck's scenario JSON; run before `build_deck.py` |
| `29_factor_count_v4.py` | re-validates the 20-factor choice on the current data, ~9 min |
| `results_factor_count/` | its output: 3 CSVs + a README with the verdict and what the factors are |
| `results_lseg_update/` | its output: 5 CSVs + a README with the adopt/don't recommendation |
| `data_lseg_update/` | the parsed inputs, unused until the update is adopted |

The backtest slide was **deliberately removed** from the deck at Tamara's
request. The overall Sharpe result now appears only in the scenario-coverage
table. `QA_prep.md` Q13/Q14 carry the verbal answer if asked.

---

## Environment gotchas, learned the hard way

- **`soffice`, `pandoc`, `pdftoppm`, `reportlab` are all absent.** The deck is
  built with matplotlib's `PdfPages`; PNG renders go to `/tmp/slideNN.png` for
  visual checking. Verify layout by looking at those, not by assuming.
- **pandas 3.0.2:** `stack()` retains NaN, and `.values` / `.to_numpy()` are
  read-only. Use `to_numpy(copy=True)` before mutating.
- **`urllib` has no root certificates** in this python.org build. `curl` works;
  `03a_fx_convert.py` falls back to it.
- **There is a git repo rooted at `$HOME`** with old commits. `FICO-case-study`
  has its own repo, so commands run inside it are safe, but never `git add .`
  in the home directory.
- **Verify GitHub state by reading the API**, not by `git status` or
  `git check-ignore` — several greps over staged filenames gave false results
  during this project, including a false pass on the licence file.
- **Xpress API:** consult `docs/solver/python-interface.md` (1.3 MB) rather than
  recalling. FICO warned that LLMs emit deprecated calls; confirmed in practice
  (`getVersion` not `getversion`, and `chgrhs` now warns in favour of `chgRHS`).
  Installed version 9.9.1, optimizer 47.01.02.
- **`p.getConstraint(index=[...])` returns an EMPTY LIST rather than raising.**
  The index list must be passed **positionally**: `p.getConstraint([1, 3])`. The
  keyword form is a silent wrong answer — it made the first IIS report announce
  "3 constraints" and then name none of them. `getVariable` behaves the same.
  `first=`/`last=` do work as keywords.
- **`p.IISStatus()` returns per-IIS LISTS, not scalars:** `numiis, rowsizes,
  colsizes, suminfeas, numinfeas`, where index 0 describes the initial
  infeasible subproblem and 1..numiis the real IIS. Printing them raw gives
  "rows [3, 3]".
- **`p.getIISData(iis)` returns INDICES and eight values**, not objects and not
  five: `rowind, colind, contype, bndtype, duals, djs, isolrows, isolcols`. The
  isolation entries are 0/1/-1 flags, not names.
- **`p.IISIsolations()` is for LINEAR problems only.** Model 2 is a MIQP, so
  isolations are unavailable; `firstIIS` itself does apply to all problem types.
- **Putting the variance in a constraint changes the problem class.** Xpress'
  multi-objective API requires linear objectives, and the transfer-variable
  workaround turns this MIQP into a quadratically constrained MIP that does not
  solve in minutes. Keep `Dot(w, Sigma, w)` in the objective.
- Do not commit `xpauth.xpr`. `.gitignore` covers `*.xpr`; `/data/` is anchored
  with a leading slash because a bare `data/` also matched
  `FINAL_data_cleaning/data/` and silently excluded it.
