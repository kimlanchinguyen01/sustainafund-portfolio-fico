"""
08 — Country cap: choose the level, then rebuild the final portfolios
=====================================================================
Model 2's min-variance solution held 45.4% in Switzerland while passing every
constraint, because diversification was enforced on REGION only. Model 3 adds a
per-country cap (US exempt - the region cap forces US >= 40%, so a lower country
cap on the US is infeasible).

This script:
  1. asserts Model 3 with the cap disabled reproduces Model 2 exactly
  2. sweeps the cap level and prices it in return at matched risk
  3. rebuilds the three risk profiles at the chosen level, fully audited
"""

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2
import Model3

BUDGET = 100_000_000
TD = 252
CAP_GRID = [1.00, 0.30, 0.25, 0.20, 0.15]
N_POINTS = 15

sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
mu = pd.read_csv("expected_return_shrunk_usd.csv").set_index("Stock")["expected_return"]
Sigma = pd.read_csv("covariance_matrix_factor_final.csv", index_col=0)
common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
MU, SG = mu.loc[common], Sigma.loc[common, common]
REG, ESG = sh.loc[common, "Region"], sh.loc[common, "ESG score"]
CTRY = sh.loc[common, "Country"]

prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
rets = np.log(prices.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]

print(f"Universe {len(common)} | countries {CTRY.nunique()}")
print("stocks per country (top 8):", CTRY.value_counts().head(8).to_dict())

# ---------------------------------------------------------------- 1. control
print("\n" + "=" * 88)
print("CONTROL: Model 3 with the cap disabled must equal Model 2")
print("=" * 88)
Model3.COUNTRY_CAP = 1.00
for mode in ["min_risk_only", "max_return_only"]:
    a = Model2.solve_model2(MU, SG, REG, ESG, mode=mode, time_limit=180)
    b = Model3.solve_model2(MU, SG, REG, ESG, country=CTRY, mode=mode, time_limit=180)
    dret = abs(a["portfolio_return"] - b["portfolio_return"])
    drisk = abs(a["portfolio_risk"] - b["portfolio_risk"])
    dw = float((a["weights"] - b["weights"]).abs().max())
    print(f"  {mode:16s} dret {dret:.2e} drisk {drisk:.2e} max|dw| {dw:.2e}")
    assert dret < 1e-9 and drisk < 1e-9 and dw < 1e-8, "Model 3 diverges from Model 2!"
print("  PASS - the only behavioural change is the cap itself")


def frontier(cap, n=N_POINTS):
    Model3.COUNTRY_CAP = cap
    lo = Model3.solve_model2(MU, SG, REG, ESG, country=CTRY, mode="min_risk_only", time_limit=180)
    hi = Model3.solve_model2(MU, SG, REG, ESG, country=CTRY, mode="max_return_only", time_limit=180)
    if not (lo["feasible"] and hi["feasible"]):
        return None
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n)
    return [r for r in (Model3.solve_model2(MU, SG, REG, ESG, country=CTRY, mode="min_risk",
                                            target_return=b, time_limit=180)
                        for b in grid) if r["feasible"]]


# ---------------------------------------------------------------- 2. sweep
print("\n" + "=" * 88)
print("CAP SWEEP")
print("=" * 88)
curves = {}
print(f"{'cap':>6} {'pts':>4} {'risk range %':>16} {'ret range %':>16} "
      f"{'max country (min-risk pt)':>34}")
for cap in CAP_GRID:
    f = frontier(cap)
    if f is None:
        print(f"{cap*100:5.0f}% INFEASIBLE")
        continue
    x = np.array([r["portfolio_risk"] for r in f]) * 100
    y = np.array([r["portfolio_return"] for r in f]) * 100
    o = np.argsort(x)
    curves[cap] = (x[o], y[o], f)
    r0 = f[int(np.argmin([r["portfolio_risk"] for r in f]))]
    print(f"{cap*100:5.0f}% {len(f):4d} {x.min():7.2f}..{x.max():7.2f} "
          f"{y.min():7.2f}..{y.max():7.2f} "
          f"{r0['max_country']} {r0['max_country_weight']*100:5.1f}%".rjust(0))

print("\nRETURN AT MATCHED RISK, BY CAP (% p.a.)")
lo_r = max(c[0].min() for c in curves.values())
hi_r = min(c[0].max() for c in curves.values())
risks = np.linspace(lo_r, hi_r, 7)
tab = pd.DataFrame({f"cap{int(c*100)}": [float(np.interp(r, v[0], v[1])) for r in risks]
                    for c, v in curves.items()}, index=[f"{r:.2f}%" for r in risks])
print(tab.round(2).to_string())
print("\nCOST vs no cap (pp of annual return):")
cost = tab.drop(columns=["cap100"]).sub(tab["cap100"], axis=0)
print(cost.round(2).to_string())
print("\nmean cost:", {c: round(cost[c].mean(), 3) for c in cost.columns})

# ---------------------------------------------------------------- 3. finalise
CHOSEN = 0.25
print("\n" + "=" * 88)
print(f"FINAL PORTFOLIOS AT COUNTRY CAP = {CHOSEN*100:.0f}%")
print("=" * 88)
f = curves[CHOSEN][2]
EF = pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in f])
ratio = EF.portfolio_return / EF.portfolio_risk
PROFILES = {"risk-averse": int(EF.portfolio_risk.idxmin()),
            "neutral": int(ratio.idxmax()),
            "risk-prone": int(EF.portfolio_return.idxmax())}
show = EF[["n_selected", "portfolio_return", "portfolio_risk", "esg_weighted",
           "weight_region_Europe", "max_country", "max_country_weight"]].copy()
show.columns = ["n", "ret", "risk", "ESG", "wEU", "top_ctry", "top_ctry_w"]
show[["ret", "risk", "wEU", "top_ctry_w"]] *= 100
show["ret/risk"] = ratio.round(3)
show["profile"] = [next((k for k, v in PROFILES.items() if v == i), "") for i in show.index]
print(show.round(2).to_string())

summary = []
for label, pt in PROFILES.items():
    w = f[pt]["weights"]
    w = w[w > 1e-9].sort_values(ascending=False)
    cw = w.groupby(sh.loc[w.index, "Country"]).sum().sort_values(ascending=False)
    rw = w.groupby(sh.loc[w.index, "Region"]).sum()
    esgw = float(sh.loc[w.index, "ESG score"] @ w)
    checks = [
        ("sum(w) == 1", abs(w.sum() - 1) < 1e-6, f"{w.sum():.10f}"),
        ("w >= 1%", w.min() >= 0.01 - 1e-9, f"min {w.min()*100:.4f}%"),
        ("w <= 20%", w.max() <= 0.20 + 1e-9, f"max {w.max()*100:.4f}%"),
        ("n >= 30", len(w) >= 30, f"n = {len(w)}"),
        ("region <= 60%", rw.max() <= 0.60 + 1e-6,
         " | ".join(f"{k} {v*100:.2f}%" for k, v in rw.items())),
        ("ESG >= 70", esgw >= 70 - 1e-6, f"{esgw:.4f}"),
        (f"country <= {CHOSEN*100:.0f}% (ex-US)",
         cw.drop("United States", errors="ignore").max() <= CHOSEN + 1e-6,
         f"largest ex-US: {cw.drop('United States', errors='ignore').index[0]} "
         f"{cw.drop('United States', errors='ignore').iloc[0]*100:.2f}%"),
    ]
    R = rets.loc[list(w.index)]
    ok = R.notna().all(axis=0)
    real = float((R.loc[:, ok].T * w.values).sum(axis=1).std(ddof=1) * np.sqrt(TD))

    print(f"\n{'-'*88}\n{label.upper()} (point {pt})")
    for n_, o_, v_ in checks:
        print(f"  [{'PASS' if o_ else 'FAIL'}] {n_:28s} {v_}")
    assert all(c[1] for c in checks), f"{label} violates a constraint"
    print(f"  return {f[pt]['portfolio_return']*100:.2f}% | risk predicted "
          f"{f[pt]['portfolio_risk']*100:.2f}% realised {real*100:.2f}% "
          f"({int(ok.sum())} days) | holdings {len(w)}")
    print(f"  countries: " + ", ".join(f"{k} {v*100:.1f}%" for k, v in cw.head(6).items()))
    hold = pd.DataFrame({"weight_%": (w * 100).round(3),
                         "amount_USD": (w * BUDGET).round(0),
                         "Region": sh.loc[w.index, "Region"],
                         "Country": sh.loc[w.index, "Country"],
                         "ESG": sh.loc[w.index, "ESG score"].round(1),
                         "exp_return_%": (mu.reindex(w.index) * 100).round(2)})
    hold.to_csv(f"FINAL_v2_portfolio_{label.replace('-','_')}.csv")
    print(f"  top 8:")
    print(hold.head(8).to_string().replace("\n", "\n  "))
    summary.append({"profile": label, "pt": pt, "n": len(w),
                    "ret_%": f[pt]["portfolio_return"] * 100,
                    "risk_pred_%": f[pt]["portfolio_risk"] * 100,
                    "risk_real_%": real * 100,
                    "ret_risk": f[pt]["portfolio_return"] / f[pt]["portfolio_risk"],
                    "ESG": esgw, "wEU_%": float(rw.get("Europe", 0)) * 100,
                    "max_pos_%": float(w.max()) * 100,
                    "top_ctry": cw.index[0], "top_ctry_%": float(cw.iloc[0]) * 100,
                    "top_exUS_ctry": cw.drop("United States", errors="ignore").index[0],
                    "top_exUS_%": float(cw.drop("United States", errors="ignore").iloc[0]) * 100})

S = pd.DataFrame(summary)
S.to_csv("FINAL_v2_portfolio_summary.csv", index=False)
EF.to_csv("efficient_frontier_final_capped.csv", index=False)
pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(f)}).to_csv(
    "efficient_frontier_weights_final_capped.csv")
print("\n" + "=" * 88)
print("SUMMARY")
print("=" * 88)
print(S.round(2).to_string(index=False))
print("\nSaved FINAL_v2_portfolio_*.csv, FINAL_v2_portfolio_summary.csv, "
      "efficient_frontier_final_capped.csv, efficient_frontier_weights_final_capped.csv")
