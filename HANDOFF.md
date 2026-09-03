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

---

## Open

1. **Country cap.** Switzerland reaches 47% of the risk-averse book. Nothing
   restrains it — a sector cap cannot see it because it spans two sectors, and
   the region cap only limits Europe as a whole. A 25% country cap costs 0.156pp.
   `archive/our_model_frozen/Model3.py` already implements it. **Most obvious
   next addition.**
2. **Dashboard.** Not started. A separate requirement in the brief and the
   largest remaining piece of work. Streamlit was the intended choice; port 8501
   is already forwarded in the devcontainer.
3. **Six missing price series** in Chloe's total-return export — `URW.PA`,
   `AVB.N`, `EQR.N` (REITs), `HOLN.S`, `EA.OQ`, `HWM.N`. 2870 of 2870 values
   absent where the previous file had a full history. Dropped rather than
   back-filled (an unadjusted series would cost them ~3pp). Worth re-extracting.
4. Not done and worth saying so: factor-level return attribution, transaction
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
  (`getVersion` not `getversion`). Installed version 9.9.1, optimizer 47.01.02.
- Do not commit `xpauth.xpr`. `.gitignore` covers `*.xpr`; `/data/` is anchored
  with a leading slash because a bare `data/` also matched
  `FINAL_data_cleaning/data/` and silently excluded it.
