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
cd .. && python3 build_deck.py                # the PDF deck        ~20 s
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
| 20 factors, not 1–2 | 1 factor understates risk 39.9% at min-risk end; 20 is the smallest with none anywhere | `05d_factor_count.py` |
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
2. **The recommendation itself is now open.** `results_stress/` shows that out
   of sample the Neutral book beats 1/N in only one of three crises and loses
   2022 by 6.8pp, while the minimum-variance book beats 1/N in all three. The
   existing backtest's -22% volatility edge was measured on min-variance, and
   that now looks like the reason it exists. Neutral is still the best
   risk-adjusted profile on the *estimated* frontier — the question is whether
   to recommend a book whose advantage does not survive out of sample, or to
   move the recommendation toward the risk-averse end and say why. Decide before
   the final deck; `QA_prep.md` will need a Q on it either way.
3. **Dashboard.** Not started. A separate requirement in the brief and the
   largest remaining piece of work. Streamlit was the intended choice; port 8501
   is already forwarded in the devcontainer.
4. **Six missing price series** in Chloe's total-return export — `URW.PA`,
   `AVB.N`, `EQR.N` (REITs), `HOLN.S`, `EA.OQ`, `HWM.N`. 2870 of 2870 values
   absent where the previous file had a full history. Dropped rather than
   back-filled (an unadjusted series would cost them ~3pp). Worth re-extracting.
5. **`build_deck.py` is not reproducible as documented.** Line 85 reads
   `/tmp/scen.json`, and **nothing in the repository writes that file** — it was
   produced by an ad-hoc snippet in an earlier session. It happens to exist on
   this machine (3 Sep 09:50), but macOS clears `/tmp` on reboot, so the rebuild
   recipe above would crash on a clean checkout. Either emit it from
   `analyze_risk.py` or inline the three scenario dicts. Note `S` (loaded from
   `portfolio_summary.csv` at line 74) is dead — every scenario number on the
   slides comes from `SC`, i.e. from that /tmp file.

6. **`results_chloe/portfolio_summary.csv` disagrees with every other artefact
   about Risk Prone.** Its risk-prone row is frontier point **11** (15.97% /
   12.77% / ratio 1.250); the deck, `risk_profile_scenarios_summary.csv`,
   `23_scenario_matrix.py` and this document all use point **14** (17.63% /
   22.62% / 0.779), which is what `idxmax(return)` gives. The table at the top of
   this file cites `portfolio_summary.csv` as its source but quotes point 14.
   The deck is unaffected (it never reads `S`). Decide which one is intended and
   regenerate the odd one out.

7. Not done and worth saying so: factor-level return attribution, transaction
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
| `results_stress/` | its output: 6 CSVs + a README. Panel A in-sample, Panel B point-in-time |

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
