"""
06a — Bootstrap-resampled ("robust") portfolio construction
==========================================================
03e/04b measured the problem: changing only the estimation window (10y -> 5y)
reshuffles ~two thirds of the capital (Jaccard 0.27). The Markowitz objective is
flat near the optimum, so the MIQP is choosing between hundreds of near-equal
candidates on the strength of estimation noise.

Michaud's resampled efficiency: instead of solving once on point estimates,
resample the return history B times, re-estimate mu and Sigma on each resample,
solve each, and use the ENSEMBLE rather than any single solution.

Why the ensemble is not simply averaged
---------------------------------------
Averaging weights breaks this problem's constraints. A stock selected in 5 of
100 resamples averages to 0.05%, which violates "either zero or at least 1%",
and the averaged vector has hundreds of tiny positions instead of 30-50. So the
bootstrap is used as a SELECTION signal:

    1. record how often each stock is selected across resamples
    2. keep the stocks selected in at least FREQ_MIN of them
    3. re-solve the original, unmodified MIQP restricted to that shortlist

The result is feasible by construction (Model2 is untouched) and holds only names
that survive resampling rather than names that won once.

The whole procedure is run on BOTH the 10y and the 5y window, so the stability
gain is measured with exactly the test that exposed the problem.

Estimation per resample mirrors 05d at k=20 (PCA factor Sigma, all stocks
retained, PSD by construction) and 04a (James-Stein mu).
"""

import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.linalg import eigh

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

TD = 252
K_FACTORS = 20
MIN_OBS = 252
B_RESAMPLES = 100
N_POINTS = 8
FREQ_MIN = 0.20          # keep stocks selected in >= 20% of resamples
SEED = 20260901
SHARES = "shares_imputed.csv"

sh = pd.read_csv(SHARES).set_index("Stock")
prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)


def window_returns(years):
    end = prices.columns.max()
    px = prices.loc[:, end - pd.DateOffset(years=years):end]
    return np.log(px).diff(axis=1).iloc[:, 1:]


def estimate(Rv, stocks, long_mask, k=K_FACTORS):
    """mu (James-Stein) and factor Sigma from a returns array (stocks x days)."""
    valid = ~np.isnan(Rv)
    n_obs = valid.sum(axis=1)

    # factors: top-k PCs of the complete-history block
    L = Rv[long_mask]
    Lc = (L - L.mean(axis=1, keepdims=True)).T           # days x n_long
    C = Lc.T @ Lc
    n = C.shape[0]
    _, V = eigh(C, subset_by_index=[n - k, n - 1])
    F = Lc @ V                                            # days x k
    F = F / np.sqrt(len(F))
    Fcov = np.cov(F, rowvar=False) * TD

    T = Rv.shape[1]
    X = np.column_stack([np.ones(T), F])

    Bm = np.zeros((len(stocks), k))
    dv = np.zeros(len(stocks))
    # complete-history stocks share one design matrix -> one solve
    li = np.where(long_mask)[0]
    coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
    resid = Rv[li].T - X @ coef
    Bm[li] = coef[1:].T
    dv[li] = resid.var(axis=0, ddof=k + 1) * TD
    # partial-history stocks: own mask each
    for i in np.where(~long_mask)[0]:
        m = valid[i]
        if m.sum() < MIN_OBS:
            dv[i] = np.nan
            continue
        Xi = X[m]
        c, *_ = np.linalg.lstsq(Xi, Rv[i][m], rcond=None)
        r = Rv[i][m] - Xi @ c
        Bm[i] = c[1:]
        dv[i] = r.var(ddof=k + 1) * TD

    keep = ~np.isnan(dv)
    Bk, dvk = Bm[keep], dv[keep]
    Sig = Bk @ Fcov @ Bk.T
    Sig[np.diag_indices_from(Sig)] += dvk
    Sig = (Sig + Sig.T) / 2
    names = [stocks[i] for i in np.where(keep)[0]]

    mu_hat = np.nanmean(Rv, axis=1) * TD
    sd_hat = np.nanstd(Rv, axis=1, ddof=1) * np.sqrt(TD)
    lm = long_mask
    target = float(np.mean(mu_hat[lm]))
    tau2 = float(np.var(mu_hat[lm]))
    se2 = (sd_hat ** 2) / np.maximum(n_obs, 1) * TD
    w = tau2 / (tau2 + se2)
    mu = w * mu_hat + (1 - w) * target

    return (pd.Series(mu[keep], index=names),
            pd.DataFrame(Sig, index=names, columns=names))


def attach(mu, Sigma):
    c = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
    return (mu.loc[c], Sigma.loc[c, c], sh.loc[c, "Region"], sh.loc[c, "ESG score"])


def solve_frontier(args, n_points=N_POINTS, tl=60):
    lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=tl)
    hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=tl)
    if not (lo["feasible"] and hi["feasible"]):
        return []
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n_points)
    return [r for r in (Model2.solve_model2(*args, mode="min_risk", target_return=b,
                                            time_limit=tl) for b in grid) if r["feasible"]]


def run_window(years, label):
    print(f"\n{'='*84}\n{label}: {years}-year window\n{'='*84}", flush=True)
    R = window_returns(years)
    stocks = list(R.index)
    Rv = R.values
    long_mask = ~np.isnan(Rv).any(axis=1)
    print(f"stocks {len(stocks)} | days {Rv.shape[1]} | complete-history {long_mask.sum()}",
          flush=True)

    mu0, S0 = estimate(Rv, stocks, long_mask)
    base = solve_frontier(attach(mu0, S0))
    print(f"point-estimate frontier: {len(base)} points | universe {len(mu0)} | "
          f"return {base[0]['portfolio_return']*100:.2f}%..{base[-1]['portfolio_return']*100:.2f}%",
          flush=True)

    rng = np.random.default_rng(SEED + years)
    T = Rv.shape[1]
    freq = {p: pd.Series(0.0, index=stocks) for p in range(N_POINTS)}
    wsum = {p: pd.Series(0.0, index=stocks) for p in range(N_POINTS)}
    counts = {p: 0 for p in range(N_POINTS)}

    t0 = time.time()
    for b in range(B_RESAMPLES):
        idx = rng.integers(0, T, T)
        mu_b, S_b = estimate(Rv[:, idx], stocks, long_mask)
        front = solve_frontier(attach(mu_b, S_b))
        for p, r in enumerate(front):
            if p >= N_POINTS:
                break
            w = r["weights"]
            hit = w[w > 1e-9]
            freq[p].loc[hit.index] += 1
            wsum[p].loc[hit.index] += hit.values
            counts[p] += 1
        if (b + 1) % 10 == 0:
            el = time.time() - t0
            print(f"  resample {b+1}/{B_RESAMPLES} | {el:.0f}s elapsed | "
                  f"eta {el/(b+1)*(B_RESAMPLES-b-1):.0f}s", flush=True)

    robust = []
    print(f"\n  {'pt':>3} {'shortlist':>10} {'n':>4} {'ret%':>7} {'risk%':>7} "
          f"{'ESG':>6} {'wEU%':>6}", flush=True)
    for p in range(N_POINTS):
        if counts[p] == 0:
            robust.append(None)
            continue
        f = freq[p] / counts[p]
        shortlist = sorted(f[f >= FREQ_MIN].index)
        if len(shortlist) < 40:                     # need slack over the 30-stock floor
            shortlist = sorted(f.sort_values(ascending=False).head(60).index)
        args = attach(mu0.reindex([s for s in shortlist if s in mu0.index]).dropna(),
                      S0)
        target = base[p]["portfolio_return"] if p < len(base) else None
        r = Model2.solve_model2(*args, mode="min_risk", target_return=target,
                                time_limit=120) if target is not None else None
        if r is None or not r["feasible"]:
            r = Model2.solve_model2(*args, mode="min_risk_only", time_limit=120)
        robust.append(r)
        print(f"  {p:3d} {len(shortlist):10d} {r['n_selected']:4d} "
              f"{r['portfolio_return']*100:6.2f}% {r['portfolio_risk']*100:6.2f}% "
              f"{r['esg_weighted']:6.1f} {r['weight_region_Europe']*100:5.1f}%", flush=True)

    sel = pd.DataFrame({f"pt{p}": freq[p] / max(counts[p], 1) for p in range(N_POINTS)})
    sel.to_csv(f"bootstrap_selection_freq_{years}y.csv")
    return base, robust, sel


def jaccard(ra, rb):
    a = ra["weights"][ra["weights"] > 1e-9]
    b = rb["weights"][rb["weights"] > 1e-9]
    sa, sb = set(a.index), set(b.index)
    idx = sorted(sa | sb)
    wa, wb = a.reindex(idx).fillna(0.0), b.reindex(idx).fillna(0.0)
    return len(sa & sb) / len(sa | sb), 0.5 * float((wa - wb).abs().sum())


base10, rob10, sel10 = run_window(10, "PRIMARY")
base5, rob5, sel5 = run_window(5, "STABILITY CHECK")

print("\n" + "=" * 84)
print("DID IT WORK? composition churn between the 10y and 5y windows")
print("=" * 84)
print(f"{'pt':>3} {'point-est Jac':>14} {'point-est act':>14} "
      f"{'robust Jac':>11} {'robust act':>11}")
pj, pa, rj, ra_ = [], [], [], []
for p in range(min(len(base10), len(base5), N_POINTS)):
    j1, a1 = jaccard(base10[p], base5[p])
    pj.append(j1); pa.append(a1)
    line = f"{p:3d} {j1:13.2f} {a1*100:13.1f}%"
    if rob10[p] and rob5[p]:
        j2, a2 = jaccard(rob10[p], rob5[p])
        rj.append(j2); ra_.append(a2)
        line += f" {j2:10.2f} {a2*100:10.1f}%"
    print(line)
print(f"\npoint estimates : Jaccard {np.mean(pj):.2f} | active share {np.mean(pa)*100:.1f}%")
print(f"bootstrap robust: Jaccard {np.mean(rj):.2f} | active share {np.mean(ra_)*100:.1f}%")
print(f"(03e/04b measured Jaccard 0.27-0.28 on the point estimates)")

pd.DataFrame([{k: v for k, v in r.items() if k != "weights"}
              for r in rob10 if r]).to_csv("efficient_frontier_robust.csv", index=False)
pd.DataFrame({f"pt{p}": r["weights"] for p, r in enumerate(rob10) if r}).to_csv(
    "efficient_frontier_weights_robust.csv")
print("\nSaved efficient_frontier_robust.csv, efficient_frontier_weights_robust.csv, "
      "bootstrap_selection_freq_{10,5}y.csv")
