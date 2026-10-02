"""
SustainaFund — 27: the LSEG "ESG and sector" update, parsed and measured
=========================================================================
A second LSEG export arrived (`ESG and sector.xlsx`) carrying, for all 1093
tickers: TR.TRESGScore, TR.GICSSector and TR.GICSIndustryGroup.

It is NOT only a gap-fill. Three separate things are in that file, and they
have to be judged separately:

1. It supplies a REAL ESG score for 47 of the 49 values we imputed. That is a
   clear improvement - it removes almost all of the imputation.

2. It also REVISES the 1044 scores we already had. Mean absolute change 1.86
   points, max 17.31, and only 17 of 1044 are unchanged to 0.01. So this is a
   different VINTAGE of the whole ESG column, not an addition to ours.

3. It is a DIFFERENT sector taxonomy (GICS), not a refinement of the current
   one. Most of it is renaming - Financial Services -> Financials, Healthcare
   -> Health Care, Consumer Cyclical -> Consumer Discretionary, Technology ->
   Information Technology, Consumer Defensive -> Consumer Staples, Basic
   Materials -> Materials - but 71 of 1093 stocks (6.5%) genuinely change
   bucket, which the 30% sector cap will see.

   GICSIndustryGroup is new information at a finer level: 25 groups.

THE CAVEAT THAT DECIDES WHETHER TO ADOPT IT
-------------------------------------------
The ESG scores in that file are NOT one cross-section. The per-cell formulas in
the second sheet show the fiscal period varies by row:

    FY2024  556      FY2025  529      FY2026  4
    FY2023    1      FY2022    1      missing 2

So an ESG >= 70 constraint evaluated on this column compares a company's FY2024
score against another's FY2025 score. That is a real inconsistency, and it is
the reason this script MEASURES the update rather than adopting it.

The two tickers with no score keep their current (imputed) value, so the
universe is not shrunk by a blank cell. Recorded rather than silent.

WHAT THIS SCRIPT DOES
---------------------
Parses the workbook into clean inputs, then runs the model four ways to isolate
which change moves the answer:

    baseline      current shares_imputed.csv + sectors.xlsx
    new ESG       LSEG ESG, current sectors
    new sectors   current ESG, GICS sectors
    both          LSEG ESG + GICS sectors

Nothing is overwritten. The parsed inputs go to 3_sensitivity_studies/data/lseg_update/ and the
delivered inputs are untouched.

Outputs (3_sensitivity_studies/results/lseg_update/):
    esg_comparison.csv      per stock: old, new, difference, fiscal period
    sector_crosswalk.csv    per stock: current sector, GICS sector, industry group
    sector_moves.csv        only the stocks that genuinely change bucket
    profiles.csv            the three profiles under all four configurations
    frontier.csv            all frontier points under all four configurations

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 27_lseg_esg_sector_update.py         # ~5 min
"""

# --- repository layout (added when the repo was grouped by part) -------------
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))     # <repo>/<part>/code
PART = os.path.dirname(_HERE)                          # <repo>/<part>
_REPO = os.path.dirname(PART)                          # <repo>
MODEL_CODE = os.path.join(_REPO, "2_optimisation_model", "code")
MODEL_DATA = os.path.join(_REPO, "2_optimisation_model", "data")
MODEL_RESULTS = os.path.join(_REPO, "2_optimisation_model", "results")
PREP_RESULTS = os.path.join(_REPO, "1_data_preparation", "results")
sys.path.insert(0, MODEL_CODE)
# -----------------------------------------------------------------------------


import os
import numpy as np
import pandas as pd

import Main_model as m2

# The workbook is kept in the repo so this does not depend on a WhatsApp temp
# directory that gets cleared. LSEG_XLSX overrides it.
XLSX = os.environ.get("LSEG_XLSX", os.path.join(PART, "data", "lseg_update", "ESG_and_sector_lseg.xlsx"))

INDIR = os.path.join(PART, "data", "lseg_update")
OUTDIR = os.path.join(PART, "results", "lseg_update")

SHEET_DATA = "Tabelle3"          # ticker, ESG, GICS sector, GICS industry group
SHEET_FORMULAS = "ZGIzZDc2NjktNjYyNy00MT"   # per-cell formulas, carries fperiod

# Current-taxonomy label -> GICS label for the same bucket. Used ONLY to tell a
# rename apart from a real reclassification; the model always uses one taxonomy
# or the other, never a blend.
RENAME = {
    "Financial Services": "Financials",
    "Healthcare": "Health Care",
    "Consumer Cyclical": "Consumer Discretionary",
    "Technology": "Information Technology",
    "Consumer Defensive": "Consumer Staples",
    "Basic Materials": "Materials",
}

os.makedirs(INDIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)


def parse_workbook():
    if not os.path.exists(XLSX):
        raise SystemExit(f"cannot find the workbook:\n  {XLSX}\n"
                         "Set LSEG_XLSX to its path.")
    d = pd.read_excel(XLSX, sheet_name=SHEET_DATA, header=None).iloc[6:, [1, 2, 3, 4]]
    d.columns = ["Stock", "esg_new", "gics_sector", "gics_industry_group"]
    d = d.dropna(subset=["Stock"]).reset_index(drop=True)
    d["esg_new"] = pd.to_numeric(d["esg_new"], errors="coerce")

    # The fiscal period is only visible in the formula sheet, which is
    # ROW-ALIGNED with the data sheet (both start at row 6, both 1093 rows).
    fml = pd.read_excel(XLSX, sheet_name=SHEET_FORMULAS, header=None).iloc[6:, 5]
    fp = fml.astype(str).str.extract(r"fperiod=(FY\d{4})")[0].reset_index(drop=True)
    assert len(fp) >= len(d), "formula sheet is shorter than the data sheet"
    d["fperiod"] = fp.values[:len(d)]
    return d.set_index("Stock")


def main():
    new = parse_workbook()
    cur = pd.read_csv(m2.FILE_SHARES).set_index("Stock")
    raw = pd.read_csv(os.path.join(MODEL_DATA, "shares_full.csv")).set_index("Stock")
    sec_cur = pd.read_excel(m2.FILE_SECTORS).set_index("Stock")["Sector"]

    assert set(new.index) == set(cur.index), "ticker sets differ"
    print(f"workbook: {len(new)} tickers, all present in {m2.FILE_SHARES}")

    # ---------- 1. ESG ----------
    esg_raw_col = [c for c in raw.columns if "ESG" in c][0]
    was_imputed = pd.to_numeric(raw[esg_raw_col], errors="coerce").isna()

    cmp_esg = pd.DataFrame({
        "esg_current": cur["ESG score"],
        "esg_lseg": new["esg_new"],
        "fperiod": new["fperiod"],
        "was_imputed": was_imputed.reindex(cur.index).fillna(False),
    })
    cmp_esg["diff"] = cmp_esg.esg_lseg - cmp_esg.esg_current
    cmp_esg.to_csv(f"{OUTDIR}/esg_comparison.csv")

    filled = int(cmp_esg[cmp_esg.was_imputed].esg_lseg.notna().sum())
    known = cmp_esg[~cmp_esg.was_imputed].dropna(subset=["esg_lseg"])
    print(f"\nESG: real value supplied for {filled} of "
          f"{int(cmp_esg.was_imputed.sum())} previously imputed")
    print(f"     the {len(known)} already-known values also move: "
          f"mean |diff| {known['diff'].abs().mean():.2f}, max {known['diff'].abs().max():.2f}, "
          f"unchanged to 0.01: {(known['diff'].abs() < 0.01).sum()}")
    print(f"     fiscal period is NOT uniform: "
          + ", ".join(f"{k} {v}" for k, v in new.fperiod.value_counts(dropna=False).items()))
    print(f"     below the {m2.ESG_FLOOR:g} floor: current "
          f"{int((cmp_esg.esg_current < m2.ESG_FLOOR).sum())} -> LSEG "
          f"{int((cmp_esg.esg_lseg < m2.ESG_FLOOR).sum())}")

    # the two blanks keep their current value, so a blank cell cannot shrink the universe
    esg_final = cmp_esg.esg_lseg.fillna(cmp_esg.esg_current)
    gaps = cmp_esg.index[cmp_esg.esg_lseg.isna()].tolist()
    if gaps:
        print(f"     {len(gaps)} ticker(s) with no LSEG score keep the current value: {gaps}")

    shares_new = cur.copy()
    shares_new["ESG score"] = esg_final
    shares_new.reset_index().to_csv(f"{INDIR}/shares_esg_lseg.csv", index=False)

    # ---------- 2. sectors ----------
    cross = pd.DataFrame({
        "sector_current": sec_cur.reindex(new.index),
        "sector_gics": new.gics_sector,
        "industry_group_gics": new.gics_industry_group,
    })
    cross["current_mapped"] = cross.sector_current.replace(RENAME)
    cross["moved"] = cross.current_mapped != cross.sector_gics
    cross.to_csv(f"{OUTDIR}/sector_crosswalk.csv")
    cross[cross.moved].to_csv(f"{OUTDIR}/sector_moves.csv")
    print(f"\nSectors: {int(cross.moved.sum())} of {len(cross)} genuinely change bucket "
          f"({cross.moved.mean()*100:.1f}%), the rest is renaming")
    print(f"         GICS industry groups available: {cross.industry_group_gics.nunique()}")

    sec_out = pd.DataFrame({"Stock": cross.index, "Sector": cross.sector_gics.values,
                            "IndustryGroup": cross.industry_group_gics.values})
    sec_out.to_excel(f"{INDIR}/sectors_gics.xlsx", index=False)

    # ---------- 3. four runs ----------
    CONFIGS = [
        ("baseline",    m2.FILE_SHARES,                 m2.FILE_SECTORS),
        ("new ESG",     f"{INDIR}/shares_esg_lseg.csv", m2.FILE_SECTORS),
        ("new sectors", m2.FILE_SHARES,                 f"{INDIR}/sectors_gics.xlsx"),
        ("both",        f"{INDIR}/shares_esg_lseg.csv", f"{INDIR}/sectors_gics.xlsx"),
    ]
    orig = (m2.FILE_SHARES, m2.FILE_SECTORS)
    front_rows, prof_rows = [], []

    for label, fshares, fsectors in CONFIGS:
        print(f"\n=== {label} ===", flush=True)
        m2.FILE_SHARES, m2.FILE_SECTORS = fshares, fsectors
        mu, Sigma, region, esg, sector = m2.load_data()
        kw = dict(time_limit=300, verbose=False)

        lo = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk_only", **kw)
        hi = m2.solve_model2(mu, Sigma, region, esg, sector, mode="max_return_only", **kw)
        if not (lo["feasible"] and hi["feasible"]):
            print("  corners infeasible - skipped")
            continue

        rows = []
        for i, b in enumerate(np.linspace(lo["portfolio_return"], hi["portfolio_return"],
                                          m2.N_FRONTIER_POINTS)):
            r = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk",
                                target_return=b, **kw)
            if not r["feasible"]:
                continue
            rows.append(r)
            front_rows.append({"config": label, "pt": i, "universe": len(mu),
                               "ret_%": r["portfolio_return"] * 100,
                               "risk_%": r["portfolio_risk"] * 100,
                               "ratio": r["portfolio_return"] / r["portfolio_risk"],
                               "n": r["n_selected"], "esg": r["esg_weighted"]})
        ratio = [r["portfolio_return"] / r["portfolio_risk"] for r in rows]
        picks = {"risk_averse": int(np.argmin([r["portfolio_risk"] for r in rows])),
                 "neutral": int(np.argmax(ratio)),
                 "risk_prone": int(np.argmax([r["portfolio_return"] for r in rows]))}
        for pname, idx in picks.items():
            r = rows[idx]
            w = r["weights"]
            prof_rows.append({"config": label, "profile": pname, "pt": idx,
                              "universe": len(mu),
                              "ret_%": r["portfolio_return"] * 100,
                              "risk_%": r["portfolio_risk"] * 100,
                              "ratio": r["portfolio_return"] / r["portfolio_risk"],
                              "n": r["n_selected"], "esg": r["esg_weighted"],
                              "max_pos_%": float(w.max()) * 100})
            print(f"  {pname:12s} ret {r['portfolio_return']*100:6.3f}%  "
                  f"risk {r['portfolio_risk']*100:6.3f}%  ratio {ratio[idx]:.3f}  "
                  f"n={r['n_selected']}  ESG {r['esg_weighted']:.2f}")

    m2.FILE_SHARES, m2.FILE_SECTORS = orig
    P = pd.DataFrame(prof_rows)
    P.to_csv(f"{OUTDIR}/profiles.csv", index=False)
    pd.DataFrame(front_rows).to_csv(f"{OUTDIR}/frontier.csv", index=False)

    print("\n" + "=" * 88)
    print("THE THREE PROFILES UNDER ALL FOUR CONFIGURATIONS")
    print("=" * 88)
    print(P.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    base = P[P.config == "baseline"].set_index("profile")
    print("\n--- change from baseline, in percentage points ---")
    for cfg in ("new ESG", "new sectors", "both"):
        d = P[P.config == cfg].set_index("profile")
        for pname in ("risk_averse", "neutral", "risk_prone"):
            if pname in d.index and pname in base.index:
                print(f"  {cfg:12s} {pname:12s} "
                      f"ret {d.loc[pname,'ret_%'] - base.loc[pname,'ret_%']:+.3f}pp  "
                      f"risk {d.loc[pname,'risk_%'] - base.loc[pname,'risk_%']:+.3f}pp  "
                      f"ratio {d.loc[pname,'ratio'] - base.loc[pname,'ratio']:+.4f}")

    print(f"\nParsed inputs -> {INDIR}/   results -> {OUTDIR}/")
    print("The delivered inputs were NOT modified.")


if __name__ == "__main__":
    main()
