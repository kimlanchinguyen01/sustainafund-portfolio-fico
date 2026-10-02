"""
03d — Does the complete-history requirement cost us anything?
============================================================
Raised by Chi Chloe (2026-09-01): the 10-year complete-history rule used for the
covariance excludes every stock listed after 2015-12-31, so those stocks can
never be selected. 96 of 1093 stocks are affected.

The critique is correct as a statement of fact. This script measures whether it
is also material, and separates two effects that a naive 10y-vs-5y comparison
confounds:

    window effect  : mu and Sigma change when the estimation window changes
    universe effect: more stocks become eligible on a shorter window

To isolate the universe effect, the 5-year window is solved TWICE:
    (A) full 5y universe          (1055 stocks)
    (B) 5y estimates, restricted to the 997 stocks that also clear 10y
The difference between A and B is attributable to the universe alone, because
mu and Sigma are identical in both.

All runs use USD inputs and the unmodified Model2 formulation.
"""

from paths import P   # where each data file lives (see paths.py)

import os

import numpy as np
import pandas as pd

LICENSE = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
os.environ["XPAUTH_PATH"] = LICENSE

import Model2

SHARES = P("shares_imputed.csv")


def load(mu_file, cov_file, restrict_to=None):
    mu = pd.read_csv(mu_file).set_index("Stock")["expected_return"]
    cov = pd.read_csv(cov_file, index_col=0)
    sh = pd.read_csv(SHARES).set_index("Stock")

    common = sorted(set(mu.index) & set(cov.index) & set(sh.index))
    if restrict_to is not None:
        common = sorted(set(common) & set(restrict_to))
    return (mu.loc[common], cov.loc[common, common],
            sh.loc[common, "Region"], sh.loc[common, "ESG score"])


def frontier(mu, Sigma, region, esg, n_points=15, label=""):
    r_lo = Model2.solve_model2(mu, Sigma, region, esg, mode="min_risk_only", time_limit=120)
    r_hi = Model2.solve_model2(mu, Sigma, region, esg, mode="max_return_only", time_limit=120)
    assert r_lo["feasible"] and r_hi["feasible"], f"{label}: infeasible endpoints"
    betas = np.linspace(r_lo["portfolio_return"], r_hi["portfolio_return"], n_points)
    out = []
    for b in betas:
        r = Model2.solve_model2(mu, Sigma, region, esg, mode="min_risk",
                                target_return=b, time_limit=120)
        if r["feasible"]:
            out.append(r)
    print(f"  {label}: {len(out)}/{n_points} solved | "
          f"return {out[0]['portfolio_return']*100:.2f}% .. {out[-1]['portfolio_return']*100:.2f}%")
    return out


def curve(front):
    x = np.array([r["portfolio_risk"] for r in front]) * 100
    y = np.array([r["portfolio_return"] for r in front]) * 100
    o = np.argsort(x)
    return x[o], y[o]


# ---------------------------------------------------------------- universes
u10 = pd.read_csv(P("expected_return_final_usd.csv")).set_index("Stock").index
u5 = pd.read_csv(P("expected_return_final_usd_5y.csv")).set_index("Stock").index
u3 = pd.read_csv(P("expected_return_final_usd_3y.csv")).set_index("Stock").index
sh_all = pd.read_csv(SHARES).set_index("Stock")

excl10 = sorted(set(sh_all.index) - set(u10))
print("=" * 88)
print("PROFILE OF THE STOCKS THE 10-YEAR RULE EXCLUDES")
print("=" * 88)
print(f"Excluded by the 10y rule: {len(excl10)} of {len(sh_all)}")
print(f"  of those, eligible on 5y: {len(set(excl10) & set(u5))}"
      f" | on 3y: {len(set(excl10) & set(u3))}")

mu5 = pd.read_csv(P("expected_return_final_usd_5y.csv")).set_index("Stock")["expected_return"]
sd5 = pd.read_csv(P("per_stock_risk_final_usd_5y.csv")).set_index("Stock")["risk_std"]
newcomers = sorted(set(excl10) & set(u5))
prof = pd.DataFrame({
    "mu": mu5.loc[newcomers] * 100, "sd": sd5.loc[newcomers] * 100,
    "ESG": sh_all.loc[newcomers, "ESG score"], "Region": sh_all.loc[newcomers, "Region"]})
incumbent = sorted(set(u5) & set(u10))
base = pd.DataFrame({
    "mu": mu5.loc[incumbent] * 100, "sd": sd5.loc[incumbent] * 100,
    "ESG": sh_all.loc[incumbent, "ESG score"]})
print("\nOn the 5y window - newcomers vs incumbents (means):")
print(f"  expected return : newcomers {prof.mu.mean():6.2f}%   incumbents {base.mu.mean():6.2f}%")
print(f"  risk (sigma)    : newcomers {prof.sd.mean():6.2f}%   incumbents {base.sd.mean():6.2f}%")
print(f"  ESG             : newcomers {prof.ESG.mean():6.2f}    incumbents {base.ESG.mean():6.2f}")
print(f"  ESG >= 70       : newcomers {(prof.ESG>=70).mean()*100:5.1f}%   "
      f"incumbents {(base.ESG>=70).mean()*100:5.1f}%")
print(f"  region split    : {prof.Region.value_counts().to_dict()}")
print("\nTop 8 newcomers by expected return:")
print(prof.sort_values("mu", ascending=False).head(8).round(2).to_string())

# ---------------------------------------------------------------- experiment
print("\n" + "=" * 88)
print("EXPERIMENT: universe effect, isolated (5y window, identical mu and Sigma)")
print("=" * 88)
A = frontier(*load(P("expected_return_final_usd_5y.csv"),
                   P("covariance_matrix_shrunk_usd_5y.csv")), label="A: 5y, full 1055")
B = frontier(*load(P("expected_return_final_usd_5y.csv"),
                   P("covariance_matrix_shrunk_usd_5y.csv"), restrict_to=u10),
             label="B: 5y, restricted to the 997")

xa, ya = curve(A)
xb, yb = curve(B)
print("\nAt matched risk, return of the WIDER universe minus the RESTRICTED one:")
print(f"{'risk %':>8} {'A full %':>10} {'B restr %':>11} {'gain pp':>9}")
gains = []
for r in np.linspace(max(xa.min(), xb.min()), min(xa.max(), xb.max()), 9):
    a, b = float(np.interp(r, xa, ya)), float(np.interp(r, xb, yb))
    gains.append(a - b)
    print(f"{r:8.2f} {a:10.2f} {b:11.2f} {a-b:+9.2f}")
print(f"\nUniverse effect: mean {np.mean(gains):+.2f} pp | max {np.max(gains):+.2f} pp")

# do the newcomers actually get bought?
print("\nAre newly-eligible stocks actually selected in A?")
picked = set()
for r in A:
    w = r["weights"]
    picked |= set(w[w > 1e-9].index)
newpicked = sorted(picked & set(newcomers))
print(f"  newcomers held somewhere on frontier A: {len(newpicked)} of {len(newcomers)}")
if newpicked:
    print(f"  {newpicked[:12]}")
    wmax = pd.Series({s: max(float(r['weights'].get(s, 0)) for r in A) for s in newpicked})
    print(f"  largest weight any newcomer reaches: {wmax.max()*100:.2f}% "
          f"({wmax.idxmax()})")
    print(f"  combined newcomer weight, min-risk end: "
          f"{float(A[0]['weights'].reindex(newcomers).fillna(0).sum())*100:.2f}%")
    print(f"  combined newcomer weight, max-ret end: "
          f"{float(A[-1]['weights'].reindex(newcomers).fillna(0).sum())*100:.2f}%")

# ---------------------------------------------------------------- window effect
print("\n" + "=" * 88)
print("FOR CONTEXT: window effect (10y vs 5y vs 3y, each on its own full universe)")
print("=" * 88)
T = frontier(*load(P("expected_return_final_usd.csv"),
                   P("covariance_matrix_shrunk_usd.csv")), label="10y, 997")
C = frontier(*load(P("expected_return_final_usd_3y.csv"),
                   P("covariance_matrix_shrunk_usd_3y.csv")), label="3y, 1076")
for name, f in [("10y", T), ("5y", A), ("3y", C)]:
    x, y = curve(f)
    print(f"  {name}: min-risk {x.min():5.2f}% @ {y[np.argmin(x)]:6.2f}%  |  "
          f"max-ret {y.max():6.2f}% @ {x[np.argmax(y)]:5.2f}%")
