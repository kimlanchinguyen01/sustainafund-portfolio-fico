"""
11 — Re-freeze with the ZEG.L data error removed
================================================
ZEG.L (Zegona Communications) shows a 4.538x single-day price jump on
2023-11-14 (27.59 -> 124.67 pence) preceded by four identical stale prices and
followed by no reversal - the signature of an unadjusted share consolidation
around the Vodafone Spain recapitalisation, not a market move. It contributed
+14.61pp to its own raw annualised mu and it was held at the 1% floor in two of
the three frozen portfolios.

BMPS.MI shows the same signature (ratio 0.302, 2017 recapitalisation) but is not
held in any portfolio, so it is reported as a limitation rather than acted on.

This rebuilds mu and Sigma from scratch without ZEG.L - not merely dropping it
from the solve - because its corrupted return also enters the PCA factor
extraction if it sits in the complete-history block.

Profile selection is by rule, not by hardcoded index, so it is reproducible:
    risk-averse  minimum predicted risk
    neutral      maximum return/risk ratio
    risk-prone   highest return among points that are NOT degenerate
                 (top-3 weight <= 40% and at most 15 positions on the 1% floor)
"""

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model3

TD, K, MIN_OBS, BUDGET = 252, 20, 252, 100_000_000
DROP = ["ZEG.L"]
Model3.COUNTRY_CAP = 0.25

sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
print(f"universe before: {len(prices)}")
prices = prices.drop(index=DROP)
print(f"dropping {DROP} -> {len(prices)}")

end = prices.columns.max()
rets = np.log(prices.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]
Rv = rets.values
valid = ~np.isnan(Rv)
n_obs = valid.sum(axis=1)
long_mask = valid.all(axis=1)
stocks = list(rets.index)
print(f"complete-history {long_mask.sum()} | partial {(~long_mask).sum()}")

L = Rv[long_mask]
Lc = (L - L.mean(axis=1, keepdims=True)).T
U, S_, _ = np.linalg.svd(Lc, full_matrices=False)
F = (U[:, :K] * S_[:K]) / np.sqrt(len(Lc))
Fcov = np.cov(F, rowvar=False) * TD
X = np.column_stack([np.ones(len(F)), F])

B = np.zeros((len(stocks), K)); dv = np.full(len(stocks), np.nan)
li = np.where(long_mask)[0]
coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
B[li] = coef[1:].T
dv[li] = (Rv[li].T - X @ coef).var(axis=0, ddof=K + 1) * TD
for i in np.where(~long_mask)[0]:
    m = valid[i]
    if m.sum() < MIN_OBS:
        continue
    c, *_ = np.linalg.lstsq(X[m], Rv[i][m], rcond=None)
    B[i] = c[1:]
    dv[i] = (Rv[i][m] - X[m] @ c).var(ddof=K + 1) * TD

keep = ~np.isnan(dv)
names = [stocks[i] for i in np.where(keep)[0]]
Sig = B[keep] @ Fcov @ B[keep].T
Sig[np.diag_indices_from(Sig)] += dv[keep]
Sig = (Sig + Sig.T) / 2
Sigma = pd.DataFrame(Sig, index=names, columns=names)
eig = np.linalg.eigvalsh(Sig)
print(f"Sigma {Sigma.shape} | PSD {eig.min() >= 0} | cond {eig.max()/eig.min():.1f}")

mu_hat = np.nanmean(Rv, axis=1) * TD
sd_hat = np.nanstd(Rv, axis=1, ddof=1) * np.sqrt(TD)
tgt = float(np.mean(mu_hat[long_mask])); tau2 = float(np.var(mu_hat[long_mask]))
se2 = (sd_hat ** 2) / np.maximum(n_obs, 1) * TD
wgt = tau2 / (tau2 + se2)
mu = pd.Series((wgt * mu_hat + (1 - wgt) * tgt)[keep], index=names)
print(f"mu range {mu.min()*100:.1f}%..{mu.max()*100:.1f}% | stocks {len(mu)}")

common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
args = (mu.loc[common], Sigma.loc[common, common],
        sh.loc[common, "Region"], sh.loc[common, "ESG score"])
CT = sh.loc[common, "Country"]
lo = Model3.solve_model2(*args, country=CT, mode="min_risk_only", time_limit=180)
hi = Model3.solve_model2(*args, country=CT, mode="max_return_only", time_limit=180)
grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 15)
front = [r for r in (Model3.solve_model2(*args, country=CT, mode="min_risk",
                                         target_return=b, time_limit=180)
                     for b in grid) if r["feasible"]]
print(f"frontier {len(front)}/15 | return {front[0]['portfolio_return']*100:.2f}%.."
      f"{front[-1]['portfolio_return']*100:.2f}%")

def hold(r):
    w = r["weights"]; return w[w > 1e-9].sort_values(ascending=False)

rows = []
for i, r in enumerate(front):
    w = hold(r)
    rows.append({"pt": i, "ret": r["portfolio_return"] * 100, "risk": r["portfolio_risk"] * 100,
                 "ratio": r["portfolio_return"] / r["portfolio_risk"], "n": len(w),
                 "top3": w.head(3).sum() * 100, "floor": int((w <= 0.01001).sum()),
                 "degenerate": (w.head(3).sum() > 0.40) or ((w <= 0.01001).sum() > 15)})
T = pd.DataFrame(rows)
print("\n" + T.round(2).to_string(index=False))

ok = T[~T.degenerate]
PROF = {"risk-averse": int(T.risk.idxmin()),
        "neutral": int(T.ratio.idxmax()),
        "risk-prone": int(ok.loc[ok.ret.idxmax(), "pt"])}
print(f"\nselected by rule: {PROF}")

old = {p: pd.read_csv(f"FROZEN_portfolio_{p.replace('-','_')}.csv", index_col=0)
       for p in PROF}
summary = []
for label, pt in PROF.items():
    r = front[pt]; w = hold(r)
    cw = w.groupby(sh.loc[w.index, "Country"]).sum().sort_values(ascending=False)
    rw = w.groupby(sh.loc[w.index, "Region"]).sum()
    esgw = float(sh.loc[w.index, "ESG score"] @ w)
    exus = cw.drop("United States", errors="ignore")
    checks = [("sum(w)=1", abs(w.sum() - 1) < 1e-6), ("w>=1%", w.min() >= 0.01 - 1e-9),
              ("w<=20%", w.max() <= 0.20 + 1e-9), ("n>=30", len(w) >= 30),
              ("region<=60%", rw.max() <= 0.60 + 1e-6), ("ESG>=70", esgw >= 70 - 1e-6),
              ("country<=25% exUS", exus.max() <= 0.25 + 1e-6),
              ("ZEG.L absent", "ZEG.L" not in w.index)]
    assert all(c[1] for c in checks), (label, [c for c in checks if not c[1]])
    ow = old[label]["weight_%"] / 100
    sa, sb = set(w.index), set(ow.index)
    idx = sorted(sa | sb)
    jac = len(sa & sb) / len(sa | sb)
    act = 0.5 * float((w.reindex(idx).fillna(0) - ow.reindex(idx).fillna(0)).abs().sum())
    print(f"\n{label}: pt{pt} | PASS all {len(checks)} checks | {len(w)} holdings | "
          f"{r['portfolio_return']*100:.2f}% / {r['portfolio_risk']*100:.2f}%")
    print(f"  vs previous freeze: Jaccard {jac:.3f} | active share {act*100:.2f}% | "
          f"held ZEG.L before: {'yes' if 'ZEG.L' in ow.index else 'no'}")
    pd.DataFrame({"weight_%": (w * 100).round(3), "amount_USD": (w * BUDGET).round(0),
                  "Region": sh.loc[w.index, "Region"], "Country": sh.loc[w.index, "Country"],
                  "ESG": sh.loc[w.index, "ESG score"].round(1),
                  "exp_return_%": (mu.reindex(w.index) * 100).round(2)}).to_csv(
        f"FROZEN_v2_portfolio_{label.replace('-','_')}.csv")
    summary.append({"profile": label, "pt": pt, "n": len(w),
                    "ret_%": r["portfolio_return"] * 100, "risk_%": r["portfolio_risk"] * 100,
                    "ratio": r["portfolio_return"] / r["portfolio_risk"], "ESG": esgw,
                    "wEU_%": float(rw.get("Europe", 0)) * 100, "max_pos_%": float(w.max()) * 100,
                    "jaccard_vs_v1": jac, "active_vs_v1_%": act * 100})

S = pd.DataFrame(summary)
S.to_csv("FROZEN_v2_portfolio_summary.csv", index=False)
pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in front]).to_csv(
    "efficient_frontier_v2.csv", index=False)
Sigma.to_csv("covariance_matrix_v2.csv")
mu.to_csv("expected_return_v2.csv", header=["expected_return"])
print("\n" + "=" * 92)
print("FROZEN v2 (ZEG.L removed)")
print("=" * 92)
print(S.round(3).to_string(index=False))
print("\nSaved FROZEN_v2_portfolio_*.csv, efficient_frontier_v2.csv, "
      "covariance_matrix_v2.csv, expected_return_v2.csv")
