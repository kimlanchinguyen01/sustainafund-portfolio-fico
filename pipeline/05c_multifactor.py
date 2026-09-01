"""
05c — Priority 2: market + region factor model
==============================================
05b showed the single-index model understates portfolio risk by 13.6% on average
and 33.6% at the min-risk end, and identified the cause: after removing the
market factor, residual correlations are +0.11 within a region and -0.11 across
regions, a spread of +0.22 that the diagonal model sets to zero. The overall mean
residual correlation is ~0 (residuals are market-orthogonal by construction), so
the failure is invisible in the average and lives entirely in the block
structure.

Model:
    r_i(t) = a_i + b_iM * r_M(t) + b_iR * r_R(t) + eps_i(t)
    r_M = equal-weighted mean of all complete-history stocks
    r_R = r_Europe - r_US, an explicit region spread
    Sigma = B F B' + diag(var eps),  F = 2x2 annualised factor covariance

PSD by construction (F PSD, D >= 0), and betas are fitted per stock on its own
available days, so all 1093 stocks are retained.

Region is the right second factor to add here on two counts: it is what the
residuals actually show, and it is already a binding constraint of the business
problem, so the risk model and the constraint set speak about the same thing.

Validation repeats 05b's portfolio-level test and re-measures the residual
region spread - if the factor works, that spread must collapse.
"""

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

TD = 252
MIN_OBS = 252

prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
px = prices.loc[:, end - pd.DateOffset(years=10):end]
rets = np.log(px).diff(axis=1).iloc[:, 1:]
sh = pd.read_csv("shares_imputed.csv").set_index("Stock")

n_obs = rets.notna().sum(axis=1)
long_hist = rets.index[rets.notna().all(axis=1)].tolist()
short_hist = [s for s in rets.index if s not in long_hist]
eligible = [s for s in rets.index if n_obs[s] >= MIN_OBS]

reg_all = sh.loc[long_hist, "Region"].astype(str)
eu = [s for s in long_hist if reg_all[s] == "Europe"]
us = [s for s in long_hist if reg_all[s] == "United States"]
r_M = rets.loc[long_hist].mean(axis=0)
r_R = rets.loc[eu].mean(axis=0) - rets.loc[us].mean(axis=0)
F = pd.DataFrame({"MKT": r_M, "REG": r_R})
Fcov = F.cov() * TD
print(f"Factors: MKT vol {np.sqrt(Fcov.iloc[0,0])*100:.2f}% | "
      f"REG vol {np.sqrt(Fcov.iloc[1,1])*100:.2f}% | "
      f"corr {F.corr().iloc[0,1]:+.3f}")
print(f"  (REG = {len(eu)} European minus {len(us)} US stocks, equal-weighted)")

Fv = F.values
rows, resid_store = {}, {}
for s in eligible:
    y = rets.loc[s]
    m = y.notna().values
    X = np.column_stack([np.ones(int(m.sum())), Fv[m]])
    coef, *_ = np.linalg.lstsq(X, y.values[m], rcond=None)
    e = y.values[m] - X @ coef
    ss = float(((y.values[m] - y.values[m].mean()) ** 2).sum())
    rows[s] = {"n_obs": int(m.sum()), "b_mkt": float(coef[1]), "b_reg": float(coef[2]),
               "resid_var": float(e.var(ddof=3) * TD),
               "r2": 1.0 - float((e ** 2).sum()) / ss if ss > 0 else np.nan,
               "sd_sample": float(y.values[m].std(ddof=1) * np.sqrt(TD))}
    if s in long_hist:
        resid_store[s] = e
P = pd.DataFrame(rows).T

reg_e = sh.loc[eligible, "Region"].astype(str)
print(f"\nRegion beta by region (should split by sign):")
for r in ["Europe", "United States"]:
    idx = [s for s in eligible if reg_e[s] == r]
    print(f"  {r:14s}: b_reg median {P.b_reg[idx].astype(float).median():+.3f} | "
          f"b_mkt median {P.b_mkt[idx].astype(float).median():.3f}")
print(f"R^2: median {P.r2.astype(float).median():.3f} "
      f"(single-index was 0.276, 10-factor PCA 0.47)")

B = P[["b_mkt", "b_reg"]].astype(float)
Sig = B.values @ Fcov.values @ B.values.T
Sig[np.diag_indices_from(Sig)] += P.resid_var.values.astype(float)
Sig = (Sig + Sig.T) / 2
Sigma = pd.DataFrame(Sig, index=eligible, columns=eligible)
eig = np.linalg.eigvalsh(Sig)
print(f"\nSigma {Sigma.shape}: PSD={eig.min() >= 0} | min eig {eig.min():.4e} | "
      f"cond {eig.max()/eig.min():.1f} | stocks kept {len(eligible)} of {len(rets)}")

# ---- did the region structure actually get absorbed? ----
sub = list(pd.Series([s for s in long_hist if s in resid_store]).sample(600, random_state=20260901))
E = np.vstack([resid_store[s] for s in sub])
C = np.corrcoef(E)
iu = np.triu_indices(len(sub), k=1)
off = C[iu]
key = np.asarray(sh.loc[sub, "Region"].astype(str))
same = (key[:, None] == key[None, :])[iu]
print(f"\nResidual correlation AFTER adding the region factor:")
print(f"  same region {off[same].mean():+.4f} | different {off[~same].mean():+.4f} | "
      f"spread {off[same].mean()-off[~same].mean():+.4f}")
print(f"  (single-index model: +0.1106 / -0.1131, spread +0.2237)")

# ---- frontier ----
mu = pd.read_csv("expected_return_shrunk_usd.csv").set_index("Stock")["expected_return"]
common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
args = (mu.loc[common], Sigma.loc[common, common],
        sh.loc[common, "Region"], sh.loc[common, "ESG score"])
lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=180)
hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=180)
grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 15)
front = [Model2.solve_model2(*args, mode="min_risk", target_return=b, time_limit=180)
         for b in grid]
front = [r for r in front if r["feasible"]]
print(f"\nFrontier: {len(front)}/15 solved | universe {len(common)}")

newcomers = sorted(set(eligible) & set(short_hist))
picked = set()
for r in front:
    w = r["weights"]
    picked |= set(w[w > 1e-9].index)
got = sorted(picked & set(newcomers))
print(f"Newcomers held: {len(got)} of {len(newcomers)} -> {got[:12]}")
print(f"Combined newcomer weight: "
      f"{float(front[0]['weights'].reindex(newcomers).fillna(0).sum())*100:.2f}% min-risk end, "
      f"{float(front[-1]['weights'].reindex(newcomers).fillna(0).sum())*100:.2f}% max-return end")

# ---- portfolio-level risk validation, same test as 05b ----
def realised(w):
    R = rets.loc[list(w.index)]
    ok = R.notna().all(axis=0)
    return float((R.loc[:, ok].T * w.values).sum(axis=1).std(ddof=1) * np.sqrt(TD))


print("\n" + "=" * 78)
print("PORTFOLIO RISK: predicted vs realised (market+region model)")
print("=" * 78)
print(f"{'pt':>3} {'n':>4} {'pred%':>8} {'real%':>8} {'err%':>8}")
errs = []
for i, r in enumerate(front):
    w = r["weights"]
    w = w[w > 1e-9]
    w = w / w.sum()
    rl = realised(w)
    e = (r["portfolio_risk"] / rl - 1) * 100
    errs.append(e)
    print(f"{i:3d} {len(w):4d} {r['portfolio_risk']*100:7.2f}% {rl*100:7.2f}% {e:+7.1f}%")
print(f"\nmean signed error {np.mean(errs):+.2f}%  (range {min(errs):+.1f}% .. {max(errs):+.1f}%)")
print("  single-index    : -13.57%  (min-risk end -33.6%)")
print("  10-factor PCA   :  +3.27%")
print("  complete-case LW:  -0.64%  (but only 997 stocks)")

Sigma.to_csv("covariance_matrix_mktregion.csv")
P.to_csv("mktregion_params.csv")
pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in front]).to_csv(
    "efficient_frontier_mktregion.csv", index=False)
pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(front)}).to_csv(
    "efficient_frontier_weights_mktregion.csv")
print("\nSaved covariance_matrix_mktregion.csv, mktregion_params.csv, "
      "efficient_frontier_mktregion.csv, efficient_frontier_weights_mktregion.csv")
