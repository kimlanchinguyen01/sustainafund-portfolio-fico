"""
16 — Run Chi Chloe's Main_model.py against the current (v3) inputs
==================================================================
Her model adds two constraint families to Model 2:
    sector cap                  sum of weights in any one sector <= 30%
    controversial-industry cap  two tiers, Tier 2 toggleable

Her file is imported unmodified; only the configuration is overridden, the same
way 03c did with Model2. Three things had to be handled first:

1. FOUR OF TEN Tier-2 tickers do not exist in this universe, so the exclusion
   silently missed them. Corrected here (the originals are kept in the printout
   so the diff is visible):
        BA.L      -> BAES.L    BAE Systems
        HO.PA     -> TCFP.PA   Thales
        LDO.MI    -> LDOF.MI   Leonardo
        SAAB-B.ST -> SAABb.ST  Saab
   BA.L is the dangerous one: BA.N exists in this universe and is BOEING, so a
   plausible "fix" would have excluded the wrong company.

2. Her config reads expected_return_final.csv and covariance_matrix_shrunk.csv,
   which are the v2 inputs - local currency, complete-case, 997 stocks. Pointed
   at the v3 estimates instead (USD, 20-factor, 1093 stocks), otherwise the new
   constraints would be evaluated on superseded numbers.

3. sectors.xlsx is not in the repository, so the SECTOR CAP CANNOT BE TESTED and
   is disabled below. Partial sector data would be worse than none: her code
   buckets missing sectors as "Unknown" and caps that bucket too, so covering
   only the 500 US names would put 593 European stocks in one capped bucket.

Scenarios, so the cost of each policy is priced rather than assumed:
    S0  no controversial exclusion at all      (baseline)
    S1  Tier 1 only            - her default   (Rheinmetall out)
    S2  Tier 1 + Tier 2        - the contested policy (all 10 defence names out)
"""

from paths import P   # where each data file lives (see paths.py)

import os
import sys

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "2_optimisation_model", "code"))
import Main_model as CM

T2_FIXED = ["LMT.N", "RTX.N", "NOC.N", "GD.N", "LHX.N", "KOG.OL",
            "BAES.L", "TCFP.PA", "LDOF.MI", "SAABb.ST"]

sh = pd.read_csv(P("shares_imputed.csv")).set_index("Stock")
mu = pd.read_csv(P("expected_return_v3.csv"), index_col=0)["expected_return"]
Sg = pd.read_csv(P("covariance_matrix_v3.csv"), index_col=0)
common = sorted(set(mu.index) & set(Sg.index) & set(sh.index))
MU, SG = mu.loc[common], Sg.loc[common, common]
REG, ESG = sh.loc[common, "Region"], sh.loc[common, "ESG score"]
SEC = pd.Series("Unknown", index=common)          # placeholder; cap disabled

CM.ENABLE_SECTOR_CAP = False
CM.ENABLE_ESG_CONSTRAINT = True
CM.TIER2_CONTROVERSIAL_TICKERS = T2_FIXED
CM.CONTROVERSIAL_CAP = 0.0

print(f"universe {len(common)} | inputs: expected_return_v3.csv, covariance_matrix_v3.csv")
print(f"sector cap: DISABLED (sectors.xlsx absent)")
print("\nTier 2 after ticker correction:")
for t in T2_FIXED:
    print(f"  {t:10s} {sh.loc[t,'Country']:15s} ESG {sh.loc[t,'ESG score']:5.1f}")
print(f"  RHMG.DE (Tier 1) {sh.loc['RHMG.DE','Country']:9s} ESG {sh.loc['RHMG.DE','ESG score']:5.1f}")
print("\nNote: every one of these clears ESG 59-89, so the ESG constraint does not")
print("exclude weapons manufacturers. Chloe's screen does work the ESG score does not.")


def frontier(t1, t2, label, n=12):
    CM.ENABLE_TIER1_EXCLUSION = t1
    CM.ENABLE_TIER2_EXCLUSION = t2
    lo = CM.solve_model2(MU, SG, REG, ESG, SEC, mode="min_risk_only",
                         time_limit=180, verbose=False)
    hi = CM.solve_model2(MU, SG, REG, ESG, SEC, mode="max_return_only",
                         time_limit=180, verbose=False)
    assert lo["feasible"] and hi["feasible"], f"{label} infeasible"
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n)
    out = [r for r in (CM.solve_model2(MU, SG, REG, ESG, SEC, mode="min_risk",
                                       target_return=b, time_limit=180, verbose=False)
                       for b in grid) if r["feasible"]]
    x = np.array([r["portfolio_risk"] for r in out]) * 100
    y = np.array([r["portfolio_return"] for r in out]) * 100
    o = np.argsort(x)
    dw = sum(float(r["weights"].reindex(T2_FIXED + ["RHMG.DE"]).fillna(0).sum())
             for r in out) / len(out) * 100
    print(f"  {label:26s} {len(out):2d}/{n} pts | risk {x.min():5.2f}..{x.max():5.2f}% | "
          f"return {y.min():5.2f}..{y.max():5.2f}% | avg defence weight {dw:5.2f}%")
    return x[o], y[o], out


print("\n" + "=" * 92)
print("SCENARIOS")
print("=" * 92)
S = {}
S["S0 no exclusion"] = frontier(False, False, "S0 no exclusion")
S["S1 Tier 1 only"] = frontier(True, False, "S1 Tier 1 (her default)")
S["S2 Tier 1 + Tier 2"] = frontier(True, True, "S2 Tier 1 + Tier 2")

print("\n" + "=" * 92)
print("RETURN AT MATCHED RISK (% p.a.) — the cost of each exclusion policy")
print("=" * 92)
lo_r = max(v[0].min() for v in S.values())
hi_r = min(v[0].max() for v in S.values())
risks = np.linspace(lo_r, hi_r, 7)
tab = pd.DataFrame({k: [float(np.interp(r, v[0], v[1])) for r in risks]
                    for k, v in S.items()}, index=[f"{r:.2f}%" for r in risks])
tab.index.name = "risk"
print(tab.round(2).to_string())
cost = tab.drop(columns=["S0 no exclusion"]).sub(tab["S0 no exclusion"], axis=0)
print("\ncost vs no exclusion (pp of annual return):")
print(cost.round(3).to_string())
print("\nmean cost:")
for c in cost.columns:
    print(f"  {c:22s} {cost[c].mean():+7.3f} pp")

print("\n" + "=" * 92)
print("WHICH DEFENCE NAMES WERE ACTUALLY HELD WITHOUT THE SCREEN (S0)")
print("=" * 92)
held = {}
for r in S["S0 no exclusion"][2]:
    w = r["weights"]
    for t in T2_FIXED + ["RHMG.DE"]:
        v = float(w.get(t, 0))
        if v > 1e-9:
            held.setdefault(t, []).append(v)
if held:
    D = pd.DataFrame([{"Stock": t, "held_in_pts": len(v), "max_weight_%": max(v) * 100,
                       "mean_weight_%": np.mean(v) * 100,
                       "Country": sh.loc[t, "Country"], "ESG": sh.loc[t, "ESG score"]}
                      for t, v in held.items()]).sort_values("max_weight_%", ascending=False)
    print(D.round(2).to_string(index=False))
else:
    print("  none held anywhere on the unscreened frontier")
tab.to_csv(P("chloe_exclusion_scenarios.csv"))
print("\nSaved chloe_exclusion_scenarios.csv")
