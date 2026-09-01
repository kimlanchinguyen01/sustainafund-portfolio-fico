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

## The deliverable

`pipeline/FROZEN_v3_portfolio_{risk_averse,neutral,risk_prone}.csv` — three
portfolios with weights, dollar amounts, country and ESG per holding.
`pipeline/FROZEN_v3_portfolio_summary.csv` for the one-page view.

| | risk-averse | neutral | risk-prone |
|---|---|---|---|
| expected return | 7.17% | **13.02%** | 14.32% |
| predicted risk | 9.36% | 11.32% | 13.02% |
| return / risk | 0.77 | **1.15** | 1.10 |
| holdings | 46 | 33 | 31 |

The neutral book is the recommendation. `HTWSS_v3/README.md` is the full
provenance map — which script answers which question — and
`HTWSS_summary_v3.docx` is the write-up for the team.

---

## Model

`pipeline/Model3.py`, a MIQP:

```
minimise   wᵀΣw
s.t.       wᵀμ ≥ β                        target return, swept to build the frontier
           Σwᵢ = 1
           0.01·yᵢ ≤ wᵢ ≤ 0.20·yᵢ,  yᵢ ∈ {0,1}
           Σyᵢ ≥ 30
           Σ_{region} wᵢ ≤ 0.60
           Σ ESGᵢ·wᵢ ≥ 70
           Σ_{country} wᵢ ≤ 0.25         except the US, see below
```

`Model2.py` is the pre-country-cap version and is kept unchanged as the audit
baseline; `08_country_cap.py` asserts the two agree when the cap is disabled.

Two notes for anyone reviewing the formulation:

- **The US is exempt from the country cap, and that is forced, not chosen.** The
  60% region cap over two regions implies US ≥ 40%, so any country cap below 40%
  applied to the US makes the problem infeasible.
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
| 4 | `14_refreeze_v3.py` | μ, Σ, the frontier and the three frozen portfolios | ~2 min |

`03a` fetches ECB reference rates once (Frankfurter API) and caches them, so
later runs are offline. Scripts `03b`–`12` and `15` are the analysis and
validation steps; they are not needed to reproduce the deliverable but they are
what justifies it.

---

## Layout

```
pipeline/            all scripts and results; scripts are numbered in the order
                     findings were established, not a required run order
pipeline/Model2.py   audit baseline (unchanged since 31 Aug)
pipeline/Model3.py   the frozen model = Model2 + country cap
.devcontainer/       Codespace definition and setup check
docs/                Xpress 9.9 documentation, in markdown
HTWSS_v3/            the package sent to the team, with its own README
HTWSS_summary_v3.docx  changelog and insights write-up
```

---

Educational exercise. Not investment advice.
