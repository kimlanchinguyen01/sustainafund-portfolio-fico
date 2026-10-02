"""
SustainaFund — 31: the scenario grid, in long format
=====================================================
Solves every scenario the dashboard needs and writes ONE set of normalised,
long-format tables keyed by (scenario_id, profile, frontier_point, stock).
Replaces the piecemeal per-study CSVs for dashboard purposes; the original
per-study outputs stay where they are for audit.

THE CANONICAL PROFILE RULE, resolved rather than invented
---------------------------------------------------------
The repo disagreed with itself about Risk Prone: portfolio holdings said
frontier point 11, while profile_definitions.csv, 23_scenario_matrix.py,
analyze_risk.py and the deck said point 14. Two different portfolios were
labelled "Risk Prone".

The rule that settles it already exists, in the FROZEN
archive/our_model_frozen/19_freeze_v4.py lines 101-107:

    deg  = (top3 > 0.40) | (n_at_floor > 15)
    ok   = frontier[~deg]
    Risk Averse = argmin risk
    Neutral     = argmax return/risk
    Risk Prone  = argmax return  AMONG NON-DEGENERATE POINTS

On the delivered frontier that gives 0 / 8 / 11, which is what the holdings
files contain. Points 12, 13 and 14 are degenerate: 16, 21 and 23 positions
sitting on the 1% floor and a top-3 concentration of 34%, 40% and 60%. Point 14
is the unconstrained max-return corner - three positions at the 20% cap and 60%
of the budget in three stocks - which is a corner of the feasible set, not a
portfolio anyone would run.

So `analyze_risk.py`'s plain argmax(return) is the outlier, not the holdings.
This script derives all three from the rule; nothing is hard-coded.

UNITS
-----
Every percentage-like value is a DECIMAL: 0.142995 means 14.2995%. ESG stays on
its own 0-100 scale. No percentage strings anywhere.

Outputs (dashboard_data/scenarios/):
    scenario_catalog.csv   one row per solved scenario, with its parameters
    portfolio_summary.csv  scenario x profile, with all the headline metrics
    portfolio_holdings.csv scenario x profile x stock x weight
    frontier_points.csv    scenario x frontier_point
    frontier_weights.csv   scenario x frontier_point x stock x weight

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 31_scenario_grid.py          # ~25 min
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

import Model2_ori as m2

OUTDIR = os.path.join(PART, "results", "scenario_grid")
BUDGET = 100_000_000
N_POINTS = 15

# The rule lives in profile_rule.py and nowhere else - it used to exist in three
# places with two different answers. Verified: the module reproduces all 45
# committed picks in this script's own output without re-solving.
from profile_rule import (DEG_TOP3, DEG_FLOOR_N, FLOOR_TOL, PROFILE_RULES,
                          pick_profiles)

# ---------------------------------------------------------------------------
# The grid. Every entry is (scenario_id, overrides on Model2_ori's constants).
# Only combinations we actually solve appear in the catalog.
# ---------------------------------------------------------------------------
BASE = dict(ENABLE_SECTOR_CAP=True, SECTOR_CAP=0.30, ESG_MIN=70.0,
            ENABLE_ESG_CONSTRAINT=True, ENABLE_TIER1_EXCLUSION=True,
            ENABLE_TIER2_EXCLUSION=False, ENABLE_COUNTRY_CAP=False,
            COUNTRY_CAP=1.0, ESG_FLOOR=30.0, ENABLE_ESG_FLOOR=True)

SCENARIOS = [("base", {})]
SCENARIOS += [("tier2_on", dict(ENABLE_TIER2_EXCLUSION=True))]
# sector cap: the study asked for 30 (base) vs 25, 20 and none
SCENARIOS += [("sector_cap_none", dict(ENABLE_SECTOR_CAP=False)),
              ("sector_cap_20", dict(SECTOR_CAP=0.20)),
              ("sector_cap_25", dict(SECTOR_CAP=0.25))]
# ESG threshold sweep; 0 means the constraint is switched off entirely
SCENARIOS += [("esg_unconstrained", dict(ENABLE_ESG_CONSTRAINT=False, ESG_MIN=0.0))]
SCENARIOS += [(f"esg_min_{int(v)}", dict(ESG_MIN=float(v))) for v in (50, 60, 65, 75, 80)]
# country cap
SCENARIOS += [(f"country_cap_{int(v*100)}",
               dict(ENABLE_COUNTRY_CAP=True, COUNTRY_CAP=v)) for v in (0.20, 0.25, 0.30, 0.40)]

os.makedirs(OUTDIR, exist_ok=True)


def params_of(overrides):
    """Flatten a scenario's effective parameters for the catalog. Decimals."""
    p = {**BASE, **overrides}
    return {
        "sector_cap": p["SECTOR_CAP"] if p["ENABLE_SECTOR_CAP"] else np.nan,
        "sector_cap_active": bool(p["ENABLE_SECTOR_CAP"]),
        "esg_min": p["ESG_MIN"] if p["ENABLE_ESG_CONSTRAINT"] else np.nan,
        "esg_constraint_active": bool(p["ENABLE_ESG_CONSTRAINT"]),
        "esg_floor": p["ESG_FLOOR"] if p["ENABLE_ESG_FLOOR"] else np.nan,
        "country_cap": p["COUNTRY_CAP"] if p["ENABLE_COUNTRY_CAP"] else np.nan,
        "country_cap_active": bool(p["ENABLE_COUNTRY_CAP"]),
        "region_cap": m2.REGION_CAP,
        "min_holdings": m2.MIN_STOCKS,
        "weight_min": m2.W_MIN,
        "weight_max": m2.W_MAX,
        "tier1_excluded": bool(p["ENABLE_TIER1_EXCLUSION"]),
        "tier2_excluded": bool(p["ENABLE_TIER2_EXCLUSION"]),
        "window_years": 10,
    }


def degeneracy(w):
    h = w[w > 1e-9].sort_values(ascending=False)
    return {"top3": float(h.head(3).sum()),
            "n_at_floor": int((h < m2.W_MIN + FLOOR_TOL).sum())}


def solve_scenario(sid, overrides, shares, sectors):
    for k, v in {**BASE, **overrides}.items():
        setattr(m2, k, v)
    mu, Sigma, region, esg, sector = m2.load_data()
    country = pd.read_csv(m2.FILE_SHARES).set_index("Stock")["Country"].reindex(mu.index)
    kw = dict(country=country, time_limit=300, verbose=False)

    lo = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk_only", **kw)
    hi = m2.solve_model2(mu, Sigma, region, esg, sector, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        print(f"  {sid}: corners infeasible - SKIPPED")
        return None, None, None

    pts, wrows = [], []
    for i, b in enumerate(np.linspace(lo["portfolio_return"], hi["portfolio_return"], N_POINTS)):
        r = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk",
                            target_return=b, **kw)
        if not r["feasible"]:
            continue
        w = r["weights"]
        held = w[w > 1e-9]
        d = degeneracy(w)
        pts.append({"scenario_id": sid, "frontier_point": i, "target_return": float(b),
                    "expected_return": float(r["portfolio_return"]),
                    "risk": float(r["portfolio_risk"]),
                    "return_risk_ratio": float(r["portfolio_return"] / r["portfolio_risk"]),
                    "n_holdings": int(r["n_selected"]), "weighted_esg": float(r["esg_weighted"]),
                    "top3_weight": d["top3"], "n_at_floor": d["n_at_floor"],
                    "degenerate": bool(d["top3"] > DEG_TOP3 or d["n_at_floor"] > DEG_FLOOR_N)})
        for s, v in held.items():
            wrows.append({"scenario_id": sid, "frontier_point": i,
                          "stock": s, "weight": float(v)})

    picks = pick_profiles(pts)

    summary, holdings = [], []
    W = pd.DataFrame(wrows)
    for prof, pt in picks.items():
        row = next(p for p in pts if p["frontier_point"] == pt)
        hw = W[(W.frontier_point == pt)].set_index("stock")["weight"]
        by_c = hw.groupby(country.reindex(hw.index)).sum()
        by_s = hw.groupby(sector.reindex(hw.index)).sum()
        by_r = hw.groupby(region.reindex(hw.index)).sum()
        summary.append({
            "scenario_id": sid, "profile": prof, "profile_rule": PROFILE_RULES[prof],
            "frontier_point": pt,
            "expected_return": row["expected_return"], "risk": row["risk"],
            "return_risk_ratio": row["return_risk_ratio"],
            "n_holdings": row["n_holdings"], "weighted_esg": row["weighted_esg"],
            "min_esg_held": float(esg.reindex(hw.index).min()),
            "max_position": float(hw.max()), "min_position": float(hw.min()),
            "top3_weight": row["top3_weight"], "n_at_floor": row["n_at_floor"],
            "europe_weight": float(by_r.get("Europe", 0.0)),
            "us_weight": float(by_r.get("United States", 0.0)),
            "top_sector": str(by_s.idxmax()), "top_sector_weight": float(by_s.max()),
            "top_country": str(by_c.idxmax()), "top_country_weight": float(by_c.max()),
        })
        for s, v in hw.items():
            holdings.append({"scenario_id": sid, "profile": prof,
                             "profile_rule": PROFILE_RULES[prof], "frontier_point": pt,
                             "stock": s, "weight": float(v),
                             "amount_usd": float(v) * BUDGET})

    neu = next(r for r in summary if r["profile"] == "Neutral")
    print(f"  {sid:22s} pts {len(pts):2d} | profiles "
          + " ".join(f"{k.split()[-1]}={v}" for k, v in picks.items())
          + f" | Neutral ret {neu['expected_return']*100:6.3f}% "
            f"risk {neu['risk']*100:6.3f}%", flush=True)
    return pts, wrows, (summary, holdings)


def main():
    shares = pd.read_csv(m2.FILE_SHARES).set_index("Stock")
    sectors = pd.read_excel(m2.FILE_SECTORS).set_index("Stock")["Sector"]

    catalog, all_pts, all_w, all_sum, all_hold = [], [], [], [], []
    print(f"solving {len(SCENARIOS)} scenarios\n")
    for sid, ov in SCENARIOS:
        pts, wrows, res = solve_scenario(sid, ov, shares, sectors)
        cat = {"scenario_id": sid, "solved": res is not None, **params_of(ov)}
        catalog.append(cat)
        if res is None:
            continue
        all_pts += pts
        all_w += wrows
        all_sum += res[0]
        all_hold += res[1]

    pd.DataFrame(catalog).to_csv(f"{OUTDIR}/scenario_catalog.csv", index=False)
    pd.DataFrame(all_pts).to_csv(f"{OUTDIR}/frontier_points.csv", index=False)
    pd.DataFrame(all_w).to_csv(f"{OUTDIR}/frontier_weights.csv", index=False)
    S = pd.DataFrame(all_sum)
    S.to_csv(f"{OUTDIR}/portfolio_summary.csv", index=False)
    H = pd.DataFrame(all_hold)
    H.to_csv(f"{OUTDIR}/portfolio_holdings.csv", index=False)

    print("\n" + "=" * 104)
    print("PORTFOLIO SUMMARY, all scenarios (decimals)")
    print("=" * 104)
    show = ["scenario_id", "profile", "frontier_point", "expected_return", "risk",
            "return_risk_ratio", "n_holdings", "weighted_esg", "top_sector_weight"]
    print(S[show].to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    print(f"\ncatalog {len(catalog)} | frontier points {len(all_pts)} | "
          f"frontier weights {len(all_w)} | summary rows {len(S)} | holdings {len(H)}")
    print(f"Wrote 5 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
