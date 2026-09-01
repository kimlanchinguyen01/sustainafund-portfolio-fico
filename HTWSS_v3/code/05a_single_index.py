"""
05a — Single-index (Sharpe diagonal) covariance, all stocks retained
===================================================================
Priority 1. Replaces the complete-case sample covariance with Sharpe's (1963)
single-index model:

    r_i(t) = alpha_i + beta_i * r_M(t) + eps_i(t)
    Sigma  = beta beta' * var(r_M) + diag(var(eps_i))

Why this keeps every stock: beta_i is fitted on whatever days stock i actually
has. No pair of stocks ever needs a common history, so a 2022 listing costs
nothing to the other 1092. PSD holds by construction - beta beta' * var(r_M) is
rank-1 PSD and the residual block is a non-negative diagonal.

Market proxy: equal-weighted mean return of the 997 complete-history stocks.
Constant composition over the whole window and gap-free, so the factor series
has no survivorship drift inside the window.

Two mu variants are reported, because the covariance is not the only thing that
decides whether a newly-included stock gets bought:
    RAW    - each stock's own annualised sample mean. Isolates the covariance
             change (only Sigma differs from the previous model), but hands the
             optimiser 40-88% "expected returns" for the 2023-25 listings.
    SHRUNK - James-Stein by sample size (from 04a).
The comparison is the honest answer to "do the newcomers look financially
sensible": under RAW they are bought for a reason that will not repeat.
"""

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

TRADING_DAYS = 252
WINDOW_YEARS = 10
MIN_OBS = 252
SHARES = "shares_imputed.csv"


prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
px = prices.loc[:, end - pd.DateOffset(years=WINDOW_YEARS):end]
rets = np.log(px).diff(axis=1).iloc[:, 1:]

n_obs = rets.notna().sum(axis=1)
long_hist = rets.index[rets.notna().all(axis=1)].tolist()
short_hist = [s for s in rets.index if s not in long_hist]
print(f"Window {px.columns.min().date()} -> {px.columns.max().date()}, "
      f"{rets.shape[1]} return days, {rets.shape[0]} stocks")
print(f"Complete history: {len(long_hist)} | partial: {len(short_hist)}")

# ------------------------------------------------ market factor
r_M = rets.loc[long_hist].mean(axis=0)
var_M = float(r_M.var() * TRADING_DAYS)
print(f"\nMarket proxy: equal-weighted, {len(long_hist)} constituents, "
      f"annualised vol {np.sqrt(var_M)*100:.2f}%, "
      f"annualised mean {r_M.mean()*TRADING_DAYS*100:.2f}%")

# ------------------------------------------------ per-stock regression
eligible = [s for s in rets.index if n_obs[s] >= MIN_OBS]
excluded = sorted(set(rets.index) - set(eligible))
rows = {}
rM = r_M.values
for s in eligible:
    y = rets.loc[s]
    m = y.notna().values
    X = np.column_stack([np.ones(int(m.sum())), rM[m]])
    coef, *_ = np.linalg.lstsq(X, y.values[m], rcond=None)
    resid = y.values[m] - X @ coef
    ss = float(((y.values[m] - y.values[m].mean()) ** 2).sum())
    rows[s] = {
        "n_obs": int(m.sum()),
        "beta": float(coef[1]),
        "resid_var": float(resid.var(ddof=2) * TRADING_DAYS),
        "r2": 1.0 - float((resid ** 2).sum()) / ss if ss > 0 else np.nan,
        "mu_raw": float(y.values[m].mean() * TRADING_DAYS),
        "sd_sample": float(y.values[m].std(ddof=1) * np.sqrt(TRADING_DAYS)),
    }
P = pd.DataFrame(rows).T
P["sd_model"] = np.sqrt(P.beta ** 2 * var_M + P.resid_var)

print(f"\nQ1. STOCKS KEPT: {len(eligible)} of {len(rets)}  "
      f"(previous complete-case model: {len(long_hist)})")
print(f"    newly reachable: {len(set(eligible) & set(short_hist))}")
if excluded:
    print(f"    still excluded (<{MIN_OBS} obs): {len(excluded)} -> {excluded}")
else:
    print(f"    still excluded: none - every stock has >= {MIN_OBS} observations")

print(f"\nBeta: min {P.beta.min():.2f} | median {P.beta.median():.2f} | "
      f"max {P.beta.max():.2f}")
print(f"R^2 : median {P.r2.median():.3f} | long-history {P.r2.loc[long_hist].median():.3f} "
      f"| short-history {P.r2.loc[[s for s in eligible if s in short_hist]].median():.3f}")

# ------------------------------------------------ Sigma
beta = P.beta.values.astype(float)
Sig = np.outer(beta, beta) * var_M
Sig[np.diag_indices_from(Sig)] += P.resid_var.values.astype(float)
Sig = (Sig + Sig.T) / 2
Sigma = pd.DataFrame(Sig, index=eligible, columns=eligible)

eig = np.linalg.eigvalsh(Sig)
print(f"\nQ2. PSD CHECK on {Sigma.shape[0]}x{Sigma.shape[1]}")
print(f"    smallest eigenvalue : {eig.min():.6e}   (>= 0 required)")
print(f"    largest eigenvalue  : {eig.max():.4f}")
print(f"    negative eigenvalues: {int((eig < 0).sum())}")
print(f"    PSD                 : {eig.min() >= 0}")
print(f"    condition number    : {eig.max()/eig.min():.1f}")
print(f"    for reference, complete-case Ledoit-Wolf (997) was cond 13244.6")

# ------------------------------------------------ Q4 risk sanity, universe-wide
print("\nQ4a. IS THE MODEL RISK ARTIFICIALLY LOW? (model sigma vs own sample sigma)")
P["ratio"] = P.sd_model / P.sd_sample
for grp, idx in [("long-history", long_hist),
                 ("short-history", [s for s in eligible if s in short_hist])]:
    g = P.loc[idx]
    print(f"    {grp:14s} n={len(g):4d} | model sigma median {g.sd_model.median()*100:5.1f}% "
          f"| sample sigma median {g.sd_sample.median()*100:5.1f}% "
          f"| ratio median {g.ratio.median():.3f} min {g.ratio.min():.3f}")
print("    ratio ~1 means the single-index model reproduces the stock's own")
print("    realised volatility; ratio << 1 would mean risk is being invented away.")

# ------------------------------------------------ solve
sh = pd.read_csv(SHARES).set_index("Stock")
mu_shrunk_all = pd.read_csv("expected_return_shrunk_usd.csv").set_index("Stock")["expected_return"]


def attach(mu):
    common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
    return (mu.loc[common], Sigma.loc[common, common],
            sh.loc[common, "Region"], sh.loc[common, "ESG score"])


def run(mu, label):
    args = attach(mu)
    lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=180)
    hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=180)
    assert lo["feasible"] and hi["feasible"], f"{label} infeasible"
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 15)
    out = [Model2.solve_model2(*args, mode="min_risk", target_return=b, time_limit=180)
           for b in grid]
    out = [r for r in out if r["feasible"]]
    print(f"\n  {label}: {len(out)}/15 solved | universe {len(args[0])} | "
          f"return {out[0]['portfolio_return']*100:.2f}%..{out[-1]['portfolio_return']*100:.2f}% "
          f"| risk {out[0]['portfolio_risk']*100:.2f}%..{out[-1]['portfolio_risk']*100:.2f}%")
    return out


print("\n" + "=" * 92)
print("Q3. DOES THE OPTIMISER ACTUALLY BUY THE PREVIOUSLY-EXCLUDED STOCKS?")
print("=" * 92)
newcomers = sorted(set(eligible) & set(short_hist))
P_raw = P.mu_raw.astype(float)

for label, mu in [("RAW mu", P_raw), ("SHRUNK mu", mu_shrunk_all)]:
    front = run(mu, label)
    held = {}
    for i, r in enumerate(front):
        w = r["weights"]
        for s in w[w > 1e-9].index:
            held.setdefault(s, []).append((i, float(w[s])))
    got = sorted(set(held) & set(newcomers))
    print(f"  newcomers held somewhere on the frontier: {len(got)} of {len(newcomers)}")
    lo_w = float(front[0]["weights"].reindex(newcomers).fillna(0).sum()) * 100
    hi_w = float(front[-1]["weights"].reindex(newcomers).fillna(0).sum()) * 100
    print(f"  combined newcomer weight: {lo_w:.2f}% at min-risk end, "
          f"{hi_w:.2f}% at max-return end")
    if got:
        det = pd.DataFrame({
            "n_obs": P.n_obs[got].astype(int),
            "beta": P.beta[got].astype(float).round(2),
            "R2": P.r2[got].astype(float).round(2),
            "mu_used_%": (mu.reindex(got).astype(float) * 100).round(1),
            "mu_raw_%": (P.mu_raw[got].astype(float) * 100).round(1),
            "sd_model_%": (P.sd_model[got].astype(float) * 100).round(1),
            "sd_sample_%": (P.sd_sample[got].astype(float) * 100).round(1),
            "ratio": P.ratio[got].astype(float).round(3),
            "max_w_%": [round(max(x[1] for x in held[s]) * 100, 2) for s in got],
        }).sort_values("max_w_%", ascending=False)
        print("\n  Q4b. Selected newcomers - are their numbers financially sensible?")
        print(det.to_string())
        bad = det[det.ratio < 0.9]
        print(f"\n  newcomers whose model sigma is >10% below their realised sigma: "
              f"{len(bad)}" + (f" -> {list(bad.index)}" if len(bad) else " (none)"))
    if label == "SHRUNK mu":
        pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in front]).to_csv(
            "efficient_frontier_singleindex.csv", index=False)
        pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(front)}).to_csv(
            "efficient_frontier_weights_singleindex.csv")

Sigma.to_csv("covariance_matrix_singleindex.csv")
P.to_csv("single_index_params.csv")
print("\nSaved covariance_matrix_singleindex.csv, single_index_params.csv, "
      "efficient_frontier_singleindex.csv, efficient_frontier_weights_singleindex.csv")
