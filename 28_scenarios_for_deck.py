"""
SustainaFund — 28: regenerate the deck's scenario file
=======================================================
FIXES A REPRODUCIBILITY DEFECT. `build_deck.py` line 85 read

    SC = json.load(open("/tmp/scen.json"))

and NOTHING in the repository wrote that file. It was produced by an ad-hoc
snippet in an earlier session. It happened to exist on one machine, but macOS
clears /tmp on reboot, so the documented rebuild recipe

    python3 build_deck.py            # the PDF deck   ~20 s

crashed on a clean checkout. Every scenario number on the slides came from that
file, so the deck was effectively unrebuildable by anyone else on the team.

This script regenerates it from committed artefacts only, into the repository:

    results_chloe/scenarios_for_deck.json

Sources, all in git:
    results_chloe/efficient_frontier_model2_<tag>.csv     the 15 frontier points
    results_chloe/efficient_frontier_weights_<tag>.csv    weights per point
    shares_imputed.csv                                    country
    sectors.xlsx                                          sector
    shares_full.csv                                       raw ESG, for the distribution

The three profiles are selected exactly as `analyze_risk.py` does - minimum
risk, maximum return/risk, maximum return - so the point indices come out of the
data rather than being hard-coded.

The ESG distribution block reproduces `02c_esg_explore.py`, including its
hand-picked candidate floors [10, 20, 30, 40, 49.3, 58.6]. Those numbers are
printed on a slide, so they have to match rather than be recomputed by some
tidier rule.

VERIFICATION: if /tmp/scen.json still exists, the regenerated file is compared
against it field by field and any mismatch is reported. That is how this was
checked in the first place.

Run:  python3 28_scenarios_for_deck.py       # ~2 s, no solver
"""

import json
import os
import numpy as np
import pandas as pd

TAG = "sec30_tier1_tier2off_esgfloor30"
FRONTIER = f"results_chloe/efficient_frontier_model2_{TAG}.csv"
WEIGHTS = f"results_chloe/efficient_frontier_weights_{TAG}.csv"
SHARES = "shares_imputed.csv"
SHARES_RAW = "shares_full.csv"
SECTORS = "sectors.xlsx"
OUT = "results_chloe/scenarios_for_deck.json"

W_MAX, W_MIN = 0.20, 0.01
TOP_N = 6          # the deck slices to [:5]; 6 is what the legacy file held
# A position counts as sitting ON a bound if it is within this of it. NOT 1e-6:
# with MIP_GAP = 0.001 the solver leaves positions microscopically clear of the
# bound - the smallest holding in the min-risk book is 0.010005, five parts in a
# million above the 1% floor - and a 1e-6 tolerance reports 0 positions at the
# floor where there is plainly 1.
BOUND_TOL = 1e-5
ESG_FLOOR_CANDIDATES = [10, 20, 30, 40, 49.3, 58.6]   # from 02c_esg_explore.py
LEGACY = "/tmp/scen.json"


def scenario_block(i, row, w, country, sector, esg):
    """Everything the deck reads for one profile, from that profile's weights."""
    held = w[w > 1e-9]
    return {
        "i": int(i),
        "ret": float(row["portfolio_return"]) * 100,
        "risk": float(row["portfolio_risk"]) * 100,
        "sharpe": float(row["portfolio_return"] / row["portfolio_risk"]),
        "n": int(row["n_selected"]),
        # positions pinned at the bounds: how cornered the solution is
        "at20": int((held > W_MAX - BOUND_TOL).sum()),
        "at1": int((held < W_MIN + BOUND_TOL).sum()),
        "top3": float(held.nlargest(3).sum()) * 100,
        "sector": str(held.groupby(sector.reindex(held.index)).sum().idxmax()),
        "sector_w": float(held.groupby(sector.reindex(held.index)).sum().max()) * 100,
        "country": str(held.groupby(country.reindex(held.index)).sum().idxmax()),
        "country_w": float(held.groupby(country.reindex(held.index)).sum().max()) * 100,
        "top": [[str(k), round(float(v) * 100, 2)] for k, v in held.nlargest(TOP_N).items()],
        "esg": float(row["esg_weighted"]),
        "minesg": float(esg.reindex(held.index).min()),
    }


def esg_block():
    """Reproduces 02c_esg_explore.py. `below` counts over ALL 1093 rows, where a
    NaN compares False - which is what 02c did and what the slide shows."""
    e = pd.read_csv(SHARES_RAW).set_index("Stock")["ESG score"]
    en = e.dropna()
    return {
        "vals": [float(v) for v in en.values],
        "stats": {"min": round(float(en.min()), 1),
                  "p10": round(float(en.quantile(0.10)), 1),
                  "p25": round(float(en.quantile(0.25)), 1),
                  "median": round(float(en.median()), 1),
                  "p75": round(float(en.quantile(0.75)), 1),
                  "max": round(float(en.max()), 1)},
        "below": {str(f): int((e < f).sum()) for f in ESG_FLOOR_CANDIDATES},
        "worst": [[str(k), round(float(v), 1)] for k, v in en.nsmallest(8).items()],
    }


def build():
    fr = pd.read_csv(FRONTIER)
    wts = pd.read_csv(WEIGHTS, index_col=0)
    shares = pd.read_csv(SHARES).set_index("Stock")
    sector = pd.read_excel(SECTORS).set_index("Stock")["Sector"]
    country = shares["Country"]
    esg = shares["ESG score"]

    fr = fr[fr["feasible"]].reset_index(drop=True)
    sharpe = fr["portfolio_return"] / fr["portfolio_risk"]

    # analyze_risk.py's three definitions, recomputed rather than hard-coded
    picks = {"Risk Averse": int(fr["portfolio_risk"].idxmin()),
             "Neutral": int(sharpe.idxmax()),
             "Risk Prone": int(fr["portfolio_return"].idxmax())}

    out = {}
    for label, i in picks.items():
        col = f"beta_{i}"
        assert col in wts.columns, f"{WEIGHTS} has no column {col}"
        out[label] = scenario_block(i, fr.loc[i], wts[col], country, sector, esg)
    out["esg"] = esg_block()
    return out


def verify(new):
    """Compare against the legacy /tmp file, if it is still around."""
    if not os.path.exists(LEGACY):
        print(f"\n{LEGACY} is gone - nothing to verify against "
              "(which is exactly the problem this script fixes).")
        return
    old = json.load(open(LEGACY))
    print(f"\n--- verification against {LEGACY} ---")
    bad = 0
    for label in ("Risk Averse", "Neutral", "Risk Prone"):
        for k, v in new[label].items():
            o = old[label].get(k, "<missing>")
            if k == "top":
                same = [t[0] for t in v] == [t[0] for t in o] and \
                       all(abs(a[1] - b[1]) < 0.011 for a, b in zip(v, o))
            elif isinstance(v, float):
                same = abs(v - float(o)) < 1e-6
            else:
                same = v == o
            if not same:
                bad += 1
                print(f"  MISMATCH {label}.{k}: new={v!r} old={o!r}")
    e_new, e_old = new["esg"], old["esg"]
    for k in ("stats", "below", "worst"):
        if e_new[k] != e_old[k]:
            bad += 1
            print(f"  MISMATCH esg.{k}:\n    new={e_new[k]}\n    old={e_old[k]}")
    dv = np.abs(np.sort(np.asarray(e_new["vals"], float))
                - np.sort(np.asarray(e_old["vals"], float))).max()
    print(f"  esg.vals: {len(e_new['vals'])} values, max abs difference {dv:.4g} "
          "(the legacy file stored them rounded; histogram only)")
    print("  ALL FIELDS MATCH" if bad == 0 else f"  {bad} field(s) differ")


if __name__ == "__main__":
    data = build()
    for label in ("Risk Averse", "Neutral", "Risk Prone"):
        d = data[label]
        print(f"{label:12s} pt {d['i']:2d}  ret {d['ret']:6.3f}%  risk {d['risk']:6.3f}%  "
              f"ratio {d['sharpe']:.3f}  n={d['n']:2d}  "
              f"at20={d['at20']} at1={d['at1']}  top3={d['top3']:.1f}%  "
              f"{d['country']} {d['country_w']:.1f}%")
    verify(data)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1)
    print(f"\nWrote {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")
