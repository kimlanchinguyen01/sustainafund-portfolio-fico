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

Formulation: MIQP. `min w'Sw` subject to `w'mu >= beta`, `sum w = 1`. Solves in
0.3–1.1 s. **Keep the two columns apart when presenting** — credit is for the
right-hand one, and claiming the left-hand one invites a correction:

| Constraint | Source |
|---|---|
| `0.01 y_i <= w_i <= 0.20 y_i`, `y_i` binary | **the brief** |
| `sum y_i >= 30` | **the brief** |
| region <= 60% (so >= 40% in the other region) | **the brief** |
| weighted ESG >= 70 | **the brief** |
| sector <= 30% | ours |
| per-stock ESG floor >= 30 | ours (Chloe) |
| Tier 1 / Tier 2 controversial-weapons screens | ours |
| country <= 25%, US exempt | ours, ships **OFF** (`ENABLE_COUNTRY_CAP = False`) |

The brief's exact wording for the region condition: "The total investment in any
single region should not exceed 60% of the available budget (so at least 40% is
invested in the other region)." `Model2_ori.py`'s docstring already marks our
additions `(NEW)` and leaves the region line unmarked; this table says the same
thing in one place.

"Region" means three unrelated things in this project and they get confused:
1. the **region cap** of 60% above — an optimiser constraint, from the brief;
2. an explicit **region factor** in the covariance — `05c_multifactor.py` added
   one to try to fix the risk understatement. It absorbed the structure
   (residual-correlation spread +0.2237 -> -0.0010) and did **not** fix the
   understatement, 13.6% -> 13.1%. Tested and rejected as a remedy;
3. **PCA factor 2 turns out to be Europe vs the US** by itself, unprompted —
   mean beta +1.43 European against -1.73 US, 7.5% of variance (`29`). Which is
   why naming a region factor added nothing: the eigenvectors already contain it.
   The failure was never which factor is named, it is how much variance is left
   inside a residual block the model declares diagonal.

See "Country cap" below for what the country cap costs and what is left to
decide.

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
| 1/N over ALL 11 years, the reference series | 2015-01-02..2025-12-31: CAGR 14.80%, vol 15.96%, Sharpe 0.928, maxDD -38.05%, 4.56x (`1N_model_monthly`, the default comparator) | `30` |
| **No 1/N variant is admissible under the brief** | equal weight over 1077 names is 0.093% each against the 1% floor; unscreened variants miss ESG >= 70; the ESG-screened one breaks the 60% region cap at 63.2% Europe | `30` |
| "The 1/N benchmark" is not one number | rebalancing frequency moves it 0.9pp of CAGR: daily 15.67%, buy-and-hold 15.35%, monthly 14.80%. Always name which one | `30` |
| ESG as a constraint beats ESG as a screen, but modestly ex ante | naive ESG>=70 screen costs -0.263pp of expected return vs the constraint's -0.151pp (1.7x). The realised 11y gap is -1.471pp, i.e. 5.6x the ex-ante gap - mostly the screen's imposed exposures (63% Europe), not lower-mu stocks | `30`, `23` |
| Benchmark gate | this 1/N and script 21's independent one agree to 0.001 of Sharpe on script 21's window (0.867 vs 0.866) | `30` |
| Sector cap costs nothing at Neutral because it does not bind there | no cap -> Neutral top sector 27.10%, under the 30% limit; return +0.020pp, ratio +0.0001 | `31` |
| Where the sector cap DOES bind is the min-risk end | uncapped Risk Averse puts 33.95% in Consumer Defensive; the cap pulls it to 30.00% for -0.016pp of return | `31` |
| A 20% sector cap starts to cost | Neutral -0.160pp of return, ratio -0.0058; it binds at every profile | `31` |
| The sector cap also moves WHICH point is Risk Prone | uncapped and at 20% the non-degenerate boundary shifts to point 12, at 25/30% it is point 11 | `31` |
| ESG threshold sweep, Neutral return | unconstrained 14.48%, 50 -> 14.47%, 60 -> 14.45%, 65 -> 14.43%, 70 -> 14.30%, 75 -> 14.07%, 80 -> 13.11% | `31` |
| Walk-forward gate is exact | the 1/N benchmark in `33` reproduces script 21 to 0.000 on CAGR, volatility and Sharpe | `33` |
| **Canonical Neutral tested out of sample at last** | max return/risk picked from a 7-point frontier at each of 31 rebalances: CAGR 15.38%, vol 16.93%, Sharpe 0.909, maxDD -34.41% | `33` |
| And it still has no significant edge - weaker than the proxy | Neutral t = **0.139** vs the mandate proxy's +0.60; Risk Prone t = 0.472; Risk Averse t = -0.847. Script 26's proxy was slightly GENEROUS, not conservative | `33`, `26` |
| Two more independent harness cross-checks | Risk Averse t = -0.847 matches script 21's -0.85, and its risk understatement 50.35% matches script 21's 50.4% | `33`, `21` |
| Return costs turnover roughly proportionally | 21.2% per rebalance at Risk Averse, 43.2% at Neutral, 45.5% at Risk Prone, against 1/N's 0.3% | `33` |
| Window gate | re-estimating on 10y reproduces the shipped v4 files to 1.7e-16 (mu) and 1.8e-15 (Sigma) | `32` |
| Short windows look better and are worse | Neutral 14.30%/10.63% ratio 1.35 on 10y -> 17.47%/9.32% ratio 1.87 on 5y -> 25.73%/7.93% ratio **3.24** on 3y, while mu's range widens 2.7-19.1% -> -9.8-46.1% | `32` |
| The recommended book barely survives a window change | 5y Neutral shares 15 of 38 names with the 10y one, 3y shares 11 of 38 with weight correlation -0.019 | `32` |
| Risk Prone is the least stable profile | 3y: 7 of 30 names shared, active share 0.910, weight correlation -0.225 | `32` |
| Risk Averse is the most stable at every window | Jaccard 0.476 (5y) and 0.278 (3y) against Neutral's 0.283 / 0.193 - the THIRD independent analysis pointing at the min-variance end | `32`, `25`, `26` |
| 03e's instability figure cross-checks | its "Jaccard 0.27, 64% of capital placed differently" matches 3y-vs-10y Risk Averse: 0.278 and 0.643 | `32`, `03e` |
| ESG 80 is where it starts to hurt | Neutral ratio 1.346 -> 1.216 and the Risk Averse book shrinks to 31 holdings | `31` |
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
| `n/a` in a CSV is a pandas MISSING VALUE, and a null group key makes `groupby` drop rows silently | 3,979 benchmark positions were invisible to the weights-sum check that was meant to cover them - it passed by not looking. Any label written to CSV must survive a `read_csv` round trip | `25`, `build_powerbi_layer` |
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
6. **Risk Prone — FULLY RESOLVED AND PROPAGATED. The canonical rule is the frozen one, and the
   holdings files were right.** `archive/our_model_frozen/19_freeze_v4.py:101`
   defines it: degenerate = top-3 weight > 40% OR more than 15 positions on the
   1% floor; Risk Prone = max return among NON-degenerate points. On the
   delivered frontier that gives 0 / 8 / **11**, which is what
   `portfolio_summary.csv` and the holdings CSVs contain. Points 12/13/14 are
   degenerate (16/21/23 positions on the floor; top-3 34%/40%/60%).
   So `analyze_risk.py`'s plain `idxmax(return)` is the outlier, not the
   holdings. `31_scenario_grid.py` derives all three per scenario; nothing is
   hard-coded, and the rule re-selects when a constraint changes.
   The rule now lives in **`profile_rule.py` and nowhere else**. It used to
   exist in three places with two different answers. `analyze_risk.py`,
   `23_scenario_matrix.py` and `31_scenario_grid.py` all import it. Gated: the
   module reproduces all 45 committed picks in `31`'s output without re-solving.
   `risk_profile_scenarios_summary.csv` and `scenario_matrix.csv` were
   regenerated, and their `results_chloe/` copies refreshed - the builder reads
   those, so updating only the root files silently changed nothing.
   Every dashboard file now agrees: Risk Prone is point 11, 15.97% / 12.77% /
   ratio 1.250.
   The presentation is **retired** at Tamara's instruction, so the deck's own
   point-14 slide is no longer an open item. `build_deck.py` and
   `28_scenarios_for_deck.py` are left in place but superseded; if the deck is
   ever revived, `28` still reproduces the legacy pick and would need
   `profile_rule` wired in.

7. **Old note, kept for the record: `results_chloe/portfolio_summary.csv`
   disagrees with every other artefact about Risk Prone.** Its risk-prone row is frontier point **11** (15.97% /
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
| `dashboard_data/` | 45 CSVs, 1.0 MB, one place with stable names; rebuilt by its own script |
| `27_lseg_esg_sector_update.py` | parses and measures the LSEG ESG/GICS export, ~5 min |
| `28_scenarios_for_deck.py` | regenerates the deck's scenario JSON; run before `build_deck.py` |
| `29_factor_count_v4.py` | re-validates the 20-factor choice on the current data, ~9 min |
| `benchmark_1n/` | the 1/N reference series over all 11 years: code + 7 CSVs + README, no solver |
| `31_scenario_grid.py` | solves 15 scenarios into long-format normalised tables, ~20 min |
| `dashboard_data/build_powerbi_layer.py` | the clean Power BI layer + validation, ~10 s |
| `dashboard_data/POWERBI.md` | its contract: conventions, schemas, what is still to do |
| `32_robustness_windows.py` | 10Y/5Y/3Y with mu and Sigma re-estimated per window, ~12 min |
| `33_walkforward_profiles.py` | walk-forward with the CANONICAL profiles, ~280 solves, ~19 min |
| `profile_rule.py` | the canonical profile-selection rule; the only definition in the repo |
| `results_factor_count/` | its output: 3 CSVs + a README with the verdict and what the factors are |
| `results_lseg_update/` | its output: 5 CSVs + a README with the adopt/don't recommendation |
| `data_lseg_update/` | the parsed inputs, unused until the update is adopted |
| `deck/` | **the final presentation**: 29 slides as PPTX and PDF, 16 chart PNGs, code + README |
| `deck/36_slides.py` | the single slide spec both renderers read, so PPTX and PDF cannot drift |
| `deck/38_checklist.py` | the brief's 10 quality checks; all 10 pass |
| `SustainaFund_Method_Record.pdf` | the long-form method write-up: every data and modelling decision, justified |

The backtest slide was **deliberately removed** from the *interim* deck
(`SustainaFund_interim_review.pdf`) at Tamara's request; there the overall Sharpe
result appears only in the scenario-coverage table, and `QA_prep.md` Q13/Q14
carry the verbal answer if asked.

The **final** deck (`deck/`) restores it and goes further: S15-S17 are the
out-of-sample record, the Jobson-Korkie significance test, and the finding that
the expected-return model forecasts backwards. That is not a reversal - the
interim deck had no room for a result that needs three slides to state honestly,
and `presentation_structure_EN.md.docx` asks for all three. Where that docx and
`deck/BRIEF_build_deck.md` disagree, the docx wins by decision; the differences
are tabulated in `deck/README.md`.

One figure the docx asks for is **not** in the deck: its recovery-day statistics
do not reproduce under any definition tried, so they are flagged
`_UNREPRODUCIBLE_DO_NOT_PRINT` in `deck/data/derived_metrics.json` and appear on
no slide. `recovery_alternatives` in that file holds figures that do trace, if a
recovery statistic is ever wanted there.

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
