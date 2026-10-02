"""
17 — Chi Chloe's model in full: sector cap + controversial-industry screen
=========================================================================
sectors.xlsx is now present: 1093 of 1093 stocks, no missing values, 11 sectors
(Morningstar-style naming, not GICS). Her "Unknown" fallback therefore never
fires and the sector cap can be tested for real.

Her file is imported unmodified; only configuration is overridden. Two fixes are
applied to the configuration, both reported so the diff is visible:

  * four Tier-2 tickers do not exist in this universe and were silently missed:
        BA.L -> BAES.L, HO.PA -> TCFP.PA, LDO.MI -> LDOF.MI, SAAB-B.ST -> SAABb.ST
    BA.L is the dangerous one: BA.N exists here and is BOEING.
  * MIP_GAP 0.01 -> 0.001. At 1% the reported cost of a cheap constraint is
    roughly double the true value (verified: 0.078pp vs 0.042pp on the same
    solve) and tightening costs no time at all - 0.4s either way.

Inputs are the v3 estimates (USD, 20-factor, 1093 stocks), not the v2 files her
config points at.

All four scenarios run in ONE pass, each writing its own tagged output. Running
them as separate manual runs is where SCENARIO_TAG has to be edited by hand, and
that is easy to forget - see the note at the end.
"""

from paths import P   # where each data file lives (see paths.py)

import os
import sys

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "2_optimisation_model", "code"))
import Model2_ori as CM

T2 = ["LMT.N", "RTX.N", "NOC.N", "GD.N", "LHX.N", "KOG.OL",
      "BAES.L", "TCFP.PA", "LDOF.MI", "SAABb.ST"]
N_PTS = 12

sh = pd.read_csv(P("shares_imputed.csv")).set_index("Stock")
mu = pd.read_csv(P("expected_return_v3.csv"), index_col=0)["expected_return"]
Sg = pd.read_csv(P("covariance_matrix_v3.csv"), index_col=0)
sec_raw = pd.read_excel(P("sectors.xlsx")).set_index("Stock")["Sector"]

common = sorted(set(mu.index) & set(Sg.index) & set(sh.index) & set(sec_raw.index))
MU, SG = mu.loc[common], Sg.loc[common, common]
REG, ESG = sh.loc[common, "Region"], sh.loc[common, "ESG score"]
SEC = sec_raw.loc[common]
CM.TIER2_CONTROVERSIAL_TICKERS = T2
CM.CONTROVERSIAL_CAP = 0.0
CM.ENABLE_ESG_CONSTRAINT = True
CM.MIP_GAP = 0.001
print(f"universe {len(common)} | sectors {SEC.nunique()} | sector cap {CM.SECTOR_CAP*100:.0f}%")


def run(sector_cap, t1, t2, label):
    CM.ENABLE_SECTOR_CAP = sector_cap
    CM.ENABLE_TIER1_EXCLUSION = t1
    CM.ENABLE_TIER2_EXCLUSION = t2
    kw = dict(time_limit=300, mip_gap=0.001, verbose=False)
    lo = CM.solve_model2(MU, SG, REG, ESG, SEC, mode="min_risk_only", **kw)
    hi = CM.solve_model2(MU, SG, REG, ESG, SEC, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        print(f"  {label:34s} INFEASIBLE")
        return None
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], N_PTS)
    out = [r for r in (CM.solve_model2(MU, SG, REG, ESG, SEC, mode="min_risk",
                                       target_return=b, **kw) for b in grid) if r["feasible"]]
    x = np.array([r["portfolio_risk"] for r in out]) * 100
    y = np.array([r["portfolio_return"] for r in out]) * 100
    o = np.argsort(x)
    # does the sector cap bind anywhere?
    maxsec = 0.0
    binder = ""
    for r in out:
        w = r["weights"]
        sw = w.groupby(SEC).sum()
        if sw.max() > maxsec:
            maxsec, binder = float(sw.max()), str(sw.idxmax())
    dw = np.mean([float(r["weights"].reindex(T2 + ["RHMG.DE"]).fillna(0).sum()) for r in out]) * 100
    print(f"  {label:34s} {len(out):2d}/{N_PTS} | risk {x.min():5.2f}..{x.max():5.2f}% | "
          f"ret {y.min():5.2f}..{y.max():5.2f}% | top sector {maxsec*100:5.2f}% ({binder[:18]}) | "
          f"defence {dw:5.2f}%")
    return x[o], y[o], out


print("\n" + "=" * 108)
print("SCENARIOS  (all in one pass, MIP gap 0.001)")
print("=" * 108)
S = {}
S["A no sector cap, no screen"] = run(False, False, False, "A  no sector cap, no screen")
S["B sector cap only"] = run(True, False, False, "B  sector cap 30% only")
S["C sector + Tier1"] = run(True, True, False, "C  sector + Tier 1  (her default)")
S["D sector + Tier1 + Tier2"] = run(True, True, True, "D  sector + Tier 1 + Tier 2")
S = {k: v for k, v in S.items() if v}

print("\n" + "=" * 108)
print("RETURN AT MATCHED RISK (% p.a.)")
print("=" * 108)
lo_r = max(v[0].min() for v in S.values())
hi_r = min(v[0].max() for v in S.values())
risks = np.linspace(lo_r, hi_r, 7)
tab = pd.DataFrame({k: [float(np.interp(r, v[0], v[1])) for r in risks]
                    for k, v in S.items()}, index=[f"{r:.2f}%" for r in risks])
tab.index.name = "risk"
print(tab.round(3).to_string())
base = list(S)[0]
cost = tab.drop(columns=[base]).sub(tab[base], axis=0)
print(f"\ncost vs '{base}' (pp of annual return):")
print(cost.round(3).to_string())
print("\nmean cost:")
for c in cost.columns:
    print(f"  {c:28s} {cost[c].mean():+7.3f} pp")

print("\n" + "=" * 108)
print("SECTOR EXPOSURE of the min-risk book, with and without the cap")
print("=" * 108)
for k in ["A no sector cap, no screen", "C sector + Tier1"]:
    if k not in S:
        continue
    r = S[k][2][int(np.argmin([x["portfolio_risk"] for x in S[k][2]]))]
    w = r["weights"]
    w = w[w > 1e-9]
    sw = (w.groupby(SEC).sum() * 100).sort_values(ascending=False)
    print(f"\n{k}  (risk {r['portfolio_risk']*100:.2f}%, {r['n_selected']} holdings)")
    for s, v in sw.head(6).items():
        print(f"    {s:26s} {v:6.2f}%{'  <-- at cap' if v > 29.9 else ''}")

for tag, k in [("A_base", "A no sector cap, no screen"), ("B_sector", "B sector cap only"),
               ("C_tier1", "C sector + Tier1"), ("D_tier2", "D sector + Tier1 + Tier2")]:
    if k not in S:
        continue
    pd.DataFrame([{a: b for a, b in r.items() if a != "weights"} for r in S[k][2]]).to_csv(
        P(f"chloe_frontier_{tag}.csv"), index=False)
tab.to_csv(P("chloe_full_scenarios.csv"))
print("\nSaved chloe_frontier_{A_base,B_sector,C_tier1,D_tier2}.csv, chloe_full_scenarios.csv")
