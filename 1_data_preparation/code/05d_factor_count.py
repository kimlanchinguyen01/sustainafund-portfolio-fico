"""
05d — How many factors does the risk model actually need?
=========================================================
05a/05c produced a clean negative result: the single-index model understates
portfolio risk by 13.6% (33.6% at the min-risk end), and adding an explicit
region factor - which fully absorbs the region structure in the residuals,
spread +0.2237 -> -0.0010 - leaves the understatement at 13.1%.

So the problem is not which factor is named. It is how much of each stock's
variance is left inside a residual block the model declares diagonal, and how
much room that leaves a minimum-variance optimiser to hunt for the blind spot.

This sweeps the number of PCA factors and, for each, measures the same thing
that matters: predicted portfolio risk vs the risk those portfolios realised.
The right k is the smallest one where the error is no longer negative, because a
model that understates risk is the one failure mode a risk-averse mandate cannot
tolerate.

Every variant keeps all 1093 stocks and is PSD by construction.
"""

from paths import P   # where each data file lives (see paths.py)

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

TD = 252
MIN_OBS = 252
K_GRID = [1, 2, 5, 10, 20, 30, 50]

prices = pd.read_csv(P("prices_clean_usd.csv"), index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
px = prices.loc[:, end - pd.DateOffset(years=10):end]
rets = np.log(px).diff(axis=1).iloc[:, 1:]
sh = pd.read_csv(P("shares_imputed.csv")).set_index("Stock")
mu_all = pd.read_csv(P("expected_return_shrunk_usd.csv")).set_index("Stock")["expected_return"]

n_obs = rets.notna().sum(axis=1)
long_hist = rets.index[rets.notna().all(axis=1)].tolist()
short_hist = [s for s in rets.index if s not in long_hist]
eligible = [s for s in rets.index if n_obs[s] >= MIN_OBS]

R = rets.loc[long_hist].T
Rc = R - R.mean()
U, S, _ = np.linalg.svd(Rc.values, full_matrices=False)
evr = (S ** 2) / (S ** 2).sum()
Fall = pd.DataFrame(U * S, index=R.index) / np.sqrt(len(R))
print(f"PCA on {len(long_hist)} complete-history stocks, {len(R)} days\n")


def build(k):
    F = Fall.iloc[:, :k]
    Fcov = F.cov() * TD
    Fv = F.values
    betas, dvar, r2 = {}, {}, {}
    for s in eligible:
        y = rets.loc[s]
        m = y.notna().values
        X = np.column_stack([np.ones(int(m.sum())), Fv[m]])
        coef, *_ = np.linalg.lstsq(X, y.values[m], rcond=None)
        e = y.values[m] - X @ coef
        betas[s] = coef[1:]
        dvar[s] = float(e.var(ddof=k + 1) * TD)
        ss = float(((y.values[m] - y.values[m].mean()) ** 2).sum())
        r2[s] = 1.0 - float((e ** 2).sum()) / ss if ss > 0 else np.nan
    B = pd.DataFrame(betas, index=F.columns).T.loc[eligible]
    D = pd.Series(dvar).loc[eligible]
    Sig = B.values @ Fcov.values @ B.values.T
    Sig[np.diag_indices_from(Sig)] += D.values
    Sig = (Sig + Sig.T) / 2
    return pd.DataFrame(Sig, index=eligible, columns=Sigma_cols(eligible)), pd.Series(r2)


def Sigma_cols(x):
    return x


def realised(w):
    Rw = rets.loc[list(w.index)]
    ok = Rw.notna().all(axis=0)
    return float((Rw.loc[:, ok].T * w.values).sum(axis=1).std(ddof=1) * np.sqrt(TD))


print(f"{'k':>4} {'var expl':>9} {'R2 med':>7} {'PSD':>5} {'cond':>8} "
      f"{'err mean':>9} {'err minrisk':>12} {'newcomer w%':>12}")
out = []
for k in K_GRID:
    Sigma, r2 = build(k)
    eig = np.linalg.eigvalsh(Sigma.values)
    common = sorted(set(mu_all.index) & set(Sigma.index) & set(sh.index))
    args = (mu_all.loc[common], Sigma.loc[common, common],
            sh.loc[common, "Region"], sh.loc[common, "ESG score"])
    lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=180)
    hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=180)
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 15)
    front = [r for r in (Model2.solve_model2(*args, mode="min_risk", target_return=b,
                                             time_limit=180) for b in grid) if r["feasible"]]
    errs = []
    for r in front:
        w = r["weights"]
        w = w[w > 1e-9]
        w = w / w.sum()
        errs.append((r["portfolio_risk"] / realised(w) - 1) * 100)
    nc = [s for s in eligible if s in short_hist]
    ncw = float(front[0]["weights"].reindex(nc).fillna(0).sum()) * 100
    out.append({"k": k, "err_mean": np.mean(errs), "err_min": errs[0],
                "cond": eig.max() / eig.min(), "psd": eig.min() >= 0,
                "r2": r2.median(), "evr": evr[:k].sum() * 100, "ncw": ncw,
                "front": front, "Sigma": Sigma})
    print(f"{k:4d} {evr[:k].sum()*100:8.1f}% {r2.median():7.3f} "
          f"{str(eig.min() >= 0):>5} {eig.max()/eig.min():8.1f} "
          f"{np.mean(errs):+8.2f}% {errs[0]:+11.1f}% {ncw:11.2f}%")

print("\nReference points from 05a-05c (same test):")
print("  market only (05a)        : mean -13.57%  min-risk -33.6%")
print("  market + region (05c)    : mean -13.09%  min-risk -32.6%")
print("  complete-case LW, 997    : mean  -0.64%  (excludes 96 stocks)")

ok = [o for o in out if o["err_mean"] >= 0 and o["err_min"] >= 0]
if ok:
    best = min(ok, key=lambda o: o["k"])
    print(f"\nSmallest k with no understatement anywhere: k={best['k']} "
          f"(mean {best['err_mean']:+.2f}%, min-risk {best['err_min']:+.1f}%)")
    Sg = best["Sigma"]
    Sg.to_csv(P("covariance_matrix_factor_final.csv"))
    pd.DataFrame([{kk: v for kk, v in r.items() if kk != "weights"}
                  for r in best["front"]]).to_csv(P("efficient_frontier_final.csv"), index=False)
    pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(best["front"])}).to_csv(
        P("efficient_frontier_weights_final.csv"))
    print("Saved covariance_matrix_factor_final.csv, efficient_frontier_final.csv, "
          "efficient_frontier_weights_final.csv")
    print(f"\nFrontier at k={best['k']}:")
    fr = pd.DataFrame([{"n": r["n_selected"], "ret_%": r["portfolio_return"] * 100,
                        "risk_%": r["portfolio_risk"] * 100, "ESG": r["esg_weighted"],
                        "w_EU_%": r["weight_region_Europe"] * 100}
                       for r in best["front"]])
    print(fr.round(2).to_string())
else:
    print("\nNo k in the grid eliminates understatement everywhere.")
