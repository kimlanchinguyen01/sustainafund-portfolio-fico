"""
06b — What does the ESG constraint cost?
========================================
Required explicitly by the case study description: "They would also like to
evaluate the impact of the ESG constraint on the potential returns."

The constraint has been binding at exactly 70.00 in every single solve across
every model variant built so far, so it is certainly costing something. This
sweeps the threshold and prices it.

Base model: the k=20 PCA factor covariance and James-Stein mu from 05d - all
1093 stocks, PSD, and the only variant that does not understate portfolio risk.
Model2 is imported unmodified; only ESG_MIN is overridden per run.

Reported per threshold:
    the whole frontier (return at matched risk levels)
    the cost in return of each 5-point step of ESG
    whether the constraint is still binding
    what happens to the number of holdings and the region split
"""

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

ESG_GRID = [0.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0]
N_POINTS = 10
SHARES = "shares_imputed.csv"

sh = pd.read_csv(SHARES).set_index("Stock")
mu = pd.read_csv("expected_return_shrunk_usd.csv").set_index("Stock")["expected_return"]
Sigma = pd.read_csv("covariance_matrix_factor_final.csv", index_col=0)
common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
args = (mu.loc[common], Sigma.loc[common, common],
        sh.loc[common, "Region"], sh.loc[common, "ESG score"])
esg_vec = sh.loc[common, "ESG score"]
print(f"Universe {len(common)} stocks | ESG: min {esg_vec.min():.1f} "
      f"median {esg_vec.median():.1f} max {esg_vec.max():.1f} | "
      f"share >= 70: {(esg_vec >= 70).mean()*100:.1f}%")

# a common risk grid, so thresholds are compared at equal risk rather than at
# equal position along their own frontiers
ref_esg = Model2.ESG_MIN
curves = {}
for thr in ESG_GRID:
    Model2.ESG_MIN = thr
    lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=180)
    hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=180)
    if not (lo["feasible"] and hi["feasible"]):
        print(f"ESG >= {thr:.0f}: INFEASIBLE")
        continue
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], N_POINTS)
    front = [r for r in (Model2.solve_model2(*args, mode="min_risk", target_return=b,
                                             time_limit=180) for b in grid) if r["feasible"]]
    x = np.array([r["portfolio_risk"] for r in front]) * 100
    y = np.array([r["portfolio_return"] for r in front]) * 100
    o = np.argsort(x)
    curves[thr] = (x[o], y[o], front)
    slack = np.mean([r["esg_weighted"] - thr for r in front])
    print(f"ESG >= {thr:5.1f} | risk {x.min():5.2f}%..{x.max():5.2f}% | "
          f"return {y.min():5.2f}%..{y.max():5.2f}% | "
          f"achieved ESG mean {np.mean([r['esg_weighted'] for r in front]):5.2f} "
          f"(slack {slack:+.2f}) | binding: {abs(slack) < 0.01}")
Model2.ESG_MIN = ref_esg

print("\n" + "=" * 88)
print("RETURN AT MATCHED RISK, BY ESG THRESHOLD (% p.a.)")
print("=" * 88)
lo_r = max(c[0].min() for c in curves.values())
hi_r = min(c[0].max() for c in curves.values())
risks = np.linspace(lo_r, hi_r, 8)
tab = pd.DataFrame({f"ESG>={int(t)}": [float(np.interp(r, c[0], c[1])) for r in risks]
                    for t, c in curves.items()}, index=[f"{r:.2f}%" for r in risks])
tab.index.name = "risk"
print(tab.round(2).to_string())

print("\n" + "=" * 88)
print("COST OF ESG (return given up vs the unconstrained ESG>=0 case, pp)")
print("=" * 88)
base = tab[f"ESG>=0"]
cost = tab.drop(columns=[f"ESG>=0"]).sub(base, axis=0)
print(cost.round(2).to_string())
print(f"\nmean cost per threshold (pp of annual return):")
for c in cost.columns:
    print(f"  {c:10s}: {cost[c].mean():+6.2f} pp")

print("\nmarginal cost of tightening ESG by 5 points, at the risk-averse end:")
ks = sorted(curves)
for a, b in zip(ks, ks[1:]):
    ra = float(np.interp(risks[0], curves[a][0], curves[a][1]))
    rb = float(np.interp(risks[0], curves[b][0], curves[b][1]))
    print(f"  {a:5.0f} -> {b:5.0f}: {rb-ra:+6.2f} pp")

print("\n" + "=" * 88)
print("STRUCTURE OF THE MIN-RISK PORTFOLIO BY THRESHOLD")
print("=" * 88)
rows = []
for t, (x, y, front) in sorted(curves.items()):
    r = front[int(np.argmin([f["portfolio_risk"] for f in front]))]
    w = r["weights"]
    w = w[w > 1e-9]
    rows.append({"ESG_min": t, "n": r["n_selected"], "ret_%": r["portfolio_return"] * 100,
                 "risk_%": r["portfolio_risk"] * 100, "ESG_achieved": r["esg_weighted"],
                 "wEU_%": r["weight_region_Europe"] * 100,
                 "max_w_%": float(w.max()) * 100})
print(pd.DataFrame(rows).round(2).to_string(index=False))

pd.DataFrame(rows).to_csv("esg_sensitivity_summary.csv", index=False)
tab.to_csv("esg_sensitivity_frontiers.csv")
print("\nSaved esg_sensitivity_summary.csv, esg_sensitivity_frontiers.csv")
