# SustainaFund — Portfolio Selection (FICO case study)

HTW Berlin summer school 2026. Select stocks and weights for a $100M mid-term
mandate, subject to concentration, region, diversification and ESG constraints,
trading expected return against risk.

> **This repository must stay private.** It contains the licensed course dataset
> (LSEG-sourced prices). The Xpress licence itself is deliberately *not* in the
> repository — see below.

---

## Running it in a Codespace

1. **Code → Codespaces → Create codespace.** The devcontainer installs
   everything from `requirements.txt` and runs a setup check.
2. **Add the licence.** Drag `xpauth.xpr` into the workspace root in the VS Code
   file explorer. `.gitignore` excludes `*.xpr`, so it cannot be committed by
   accident. `XPAUTH_PATH` is already set for you by the devcontainer.
3. **Verify:**
   ```bash
   python .devcontainer/check_setup.py
   ```
   It prints the optimizer version and solves a toy problem. It never prints the
   licence contents.

Everything except solving works without the licence.

---

## The current model

**`Model2_ori.py`** — Chi Chloe's model, corrected. This is the model we are
working on. It adds a per-sector cap and a two-tier controversial-industry screen
to Model 2. Four defects were fixed (tickers, output tag, MIP gap, input files);
see `results_chloe/README.md` for the table and `git log -p Model2_ori.py` for the
lines.

Results of running exactly this model are in **`results_chloe/`**, two
invocations differing only in `ENABLE_TIER2_EXCLUSION`:

| | risk-averse | neutral | risk-prone |
|---|---|---|---|
| expected return | 7.07% | **12.93%** | 14.89% |
| predicted risk | 9.24% | 11.24% | 14.75% |
| return / risk | 0.77 | **1.15** | 1.01 |
| holdings | 46 | 30 | 30 |
| top sector | Consumer Defensive 30.0% | 28.7% | Healthcare 27.1% |

Headline from the two runs: **excluding Tier 2 costs −0.016 pp on average**, so
the contested policy can be decided on principle rather than on cost.

The parallel model track (a country cap instead of a sector cap) is frozen in
`archive/our_model_frozen/`, recoverable at tag `freeze-candidate-v3`.
`pipeline/README.md` is the provenance map for the input pipeline — which script
established which finding.

---

## Model

`Model2_ori.py`, a MIQP:

```
minimise   wᵀΣw
s.t.       wᵀμ ≥ β                        target return, swept to build the frontier
           Σwᵢ = 1
           0.01·yᵢ ≤ wᵢ ≤ 0.20·yᵢ,  yᵢ ∈ {0,1}
           Σyᵢ ≥ 30
           Σ_{region} wᵢ ≤ 0.60
           Σ ESGᵢ·wᵢ ≥ 70
           Σ_{sector} wᵢ ≤ 0.30
           Σ_{Tier 1} wᵢ ≤ 0            Rheinmetall; always on
           Σ_{Tier 2} wᵢ ≤ 0            defence conglomerates; toggle
```

`pipeline/Model2.py` is the pre-addition version, kept unchanged as the audit
baseline.

Two notes for anyone reviewing the formulation:

- **The ESG constraint does not screen weapons.** Rheinmetall's ESG is 87.3,
  Leonardo's 89.2, Lockheed's 85.6 — all above the 70 threshold. Without the
  Tier 1 screen, Rheinmetall reaches 10.2% of the book. The screen does work the
  ESG score does not.
- **The binary variables are required, not a workaround.** Xpress semi-continuous
  variables express "0 or in [1%, 20%]" natively, but they cannot be counted, so
  `Σyᵢ ≥ 30` still needs binaries. Dropping the `wᵢ ≥ 0.01·yᵢ` link and relying
  on semi-continuous alone silently breaks the cardinality constraint — it
  returns 26 positions while reporting 30. Tested; see the note in
  `HTWSS_summary_v3.docx`.

---

## Regenerating

Large artifacts are not committed. Run in this order from `pipeline/`; each
script validates itself and prints the check.

| step | script | produces | time |
|---|---|---|---|
| 1 | `02a_esg_and_price_eda_cleaning.py` | `prices_clean.csv`, imputed/excluded shares | ~1 min |
| 2 | `03a_fx_convert.py` | `prices_clean_usd.csv` + cached ECB rates | ~1 min |
| 3 | `13_truncate_discontinuities.py` | `prices_clean_usd_v3.csv` | <1 min |
| 4 | `14_refreeze_v3.py` | `expected_return_v3.csv`, `covariance_matrix_v3.csv` | ~2 min |
| 5 | `../Model2_ori.py` | the frontier, from the repository root | ~10 s |

`03a` fetches ECB reference rates once (Frankfurter API) and caches them, so
later runs are offline. Scripts `03b`–`12` and `15` are the analysis and
validation steps; they are not needed to reproduce the deliverable but they are
what justifies it.

---

## Layout

```
Model2_ori.py             THE model — Chloe's, corrected
sectors.xlsx              sector classification, 1093/1093, no gaps
expected_return_v3.csv    inputs the model reads
shares_imputed.csv
results_chloe/            output of running exactly Model2_ori.py, with a README
archive/our_model_frozen/ the parallel country-cap track, frozen
pipeline/                 input preparation and the analysis behind it; scripts
                          are numbered in the order findings were established
pipeline/Model2.py        audit baseline (unchanged since 31 Aug)
.devcontainer/            Codespace definition and setup check
docs/                     Xpress 9.9 documentation, in markdown
pipeline/README.md        provenance map: script -> question -> answer
```

The write-ups that were sent to the team (`HTWSS_v3.zip`, `HTWSS_summary_v3.docx`)
are deliberately **not** in git: they present the archived country-cap model as
the deliverable, which is no longer true. They remain on the author's disk and in
git history at tag `freeze-candidate-v3`.

---

Educational exercise. Not investment advice.
