"""
04b — Frontier on the factor model, and does it fix the instability?
====================================================================
Runs the unmodified Model2 on (factor Sigma, James-Stein mu) over all 1093
stocks, then answers three questions:

  1. Are the previously-excluded stocks actually eligible and selected now?
  2. How does this frontier compare with the 997-stock USD frontier?
  3. Does it fix the instability measured in 03e? That test rebuilds the whole
     model on a 5-year window and measures how much the portfolio composition
     churns - the same experiment as 03e, so the numbers are comparable.

build_model() reproduces 04a's logic parameterised by window length, and asserts
it reproduces 04a's saved 10-year output before being trusted on 5 years.
"""

from paths import P   # where each data file lives (see paths.py)

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

TRADING_DAYS = 252
N_FACTORS = 10
MIN_OBS = 252
SHARES = P("shares_imputed.csv")


def build_model(prices, years):
    """Factor Sigma + James-Stein mu on a given window. Mirrors 04a."""
    end = prices.columns.max()
    px = prices.loc[:, end - pd.DateOffset(years=years):end]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]

    n_obs = rets.notna().sum(axis=1)
    long_hist = rets.index[rets.notna().all(axis=1)].tolist()
    eligible = [s for s in rets.index if n_obs[s] >= MIN_OBS]

    R = rets.loc[long_hist].T
    Rc = R - R.mean()
    U, S, _ = np.linalg.svd(Rc.values, full_matrices=False)
    F = pd.DataFrame(U[:, :N_FACTORS] * S[:N_FACTORS], index=R.index,
                     columns=[f"F{i+1}" for i in range(N_FACTORS)]) / np.sqrt(len(R))
    Fcov = F.cov() * TRADING_DAYS
    Fv = F.values

    betas, resid_var = {}, {}
    for s in eligible:
        y = rets.loc[s]
        m = y.notna().values
        X1 = np.column_stack([np.ones(m.sum()), Fv[m]])
        coef, *_ = np.linalg.lstsq(X1, y.values[m], rcond=None)
        resid = y.values[m] - X1 @ coef
        betas[s] = coef[1:]
        resid_var[s] = float(resid.var(ddof=len(coef)) * TRADING_DAYS)

    B = pd.DataFrame(betas, index=F.columns).T.loc[eligible]
    D = pd.Series(resid_var).loc[eligible]
    Sig = B.values @ Fcov.values @ B.values.T
    Sig[np.diag_indices_from(Sig)] += D.values
    Sig = (Sig + Sig.T) / 2
    Sigma = pd.DataFrame(Sig, index=eligible, columns=eligible)

    mu_hat = rets.loc[eligible].mean(axis=1) * TRADING_DAYS
    sd_hat = rets.loc[eligible].std(axis=1) * np.sqrt(TRADING_DAYS)
    target = float(mu_hat.loc[long_hist].mean())
    tau2 = float(mu_hat.loc[long_hist].var())
    se2 = (sd_hat ** 2) / n_obs.loc[eligible] * TRADING_DAYS
    w = tau2 / (tau2 + se2)
    mu = w * mu_hat + (1.0 - w) * target
    return mu, Sigma


def attach(mu, Sigma):
    sh = pd.read_csv(SHARES).set_index("Stock")
    common = sorted(set(mu.index) & set(Sigma.index) & set(sh.index))
    return (mu.loc[common], Sigma.loc[common, common],
            sh.loc[common, "Region"], sh.loc[common, "ESG score"])


def frontier(args, n=15, label="", betas=None):
    lo = Model2.solve_model2(*args, mode="min_risk_only", time_limit=120)
    hi = Model2.solve_model2(*args, mode="max_return_only", time_limit=120)
    assert lo["feasible"] and hi["feasible"], f"{label}: infeasible"
    grid = betas if betas is not None else np.linspace(
        lo["portfolio_return"], hi["portfolio_return"], n)
    out = [Model2.solve_model2(*args, mode="min_risk", target_return=b, time_limit=120)
           for b in grid]
    out = [r for r in out if r["feasible"]]
    print(f"  {label}: {len(out)}/{len(grid)} solved | "
          f"return {out[0]['portfolio_return']*100:.2f}%..{out[-1]['portfolio_return']*100:.2f}% | "
          f"risk {out[0]['portfolio_risk']*100:.2f}%..{out[-1]['portfolio_risk']*100:.2f}%")
    return out


def compare(pa, pb):
    a = pa["weights"][pa["weights"] > 1e-9]
    b = pb["weights"][pb["weights"] > 1e-9]
    sa, sb = set(a.index), set(b.index)
    idx = sorted(sa | sb)
    wa, wb = a.reindex(idx).fillna(0.0), b.reindex(idx).fillna(0.0)
    return len(sa & sb) / len(sa | sb), 0.5 * float((wa - wb).abs().sum())


prices = pd.read_csv(P("prices_clean_usd.csv"), index_col=0)
prices.columns = pd.to_datetime(prices.columns)

# ---- control: build_model must reproduce 04a's saved 10y output -------------
mu10, S10 = build_model(prices, 10)
ref_mu = pd.read_csv(P("expected_return_shrunk_usd.csv")).set_index("Stock")["expected_return"]
ref_S = pd.read_csv(P("covariance_matrix_factor_usd.csv"), index_col=0, nrows=200)
assert sorted(mu10.index) == sorted(ref_mu.index), "universe mismatch vs 04a"
assert float((mu10.loc[ref_mu.index] - ref_mu).abs().max()) < 1e-12, "mu mismatch vs 04a"
cols = ref_S.columns[:200]
assert float((S10.loc[ref_S.index, cols] - ref_S[cols]).abs().to_numpy().max()) < 1e-12, \
    "Sigma mismatch vs 04a"
print(f"CONTROL: build_model reproduces 04a exactly ({len(mu10)} stocks)\n")

u997 = pd.read_csv(P("expected_return_final_usd.csv")).set_index("Stock").index
newcomers = sorted(set(mu10.index) - set(u997))
print("=" * 90)
print(f"1. ELIGIBILITY - the point Chloe raised")
print("=" * 90)
print(f"Stocks in the optimisation: {len(mu10)} of 1093  "
      f"(previous model: {len(u997)}, i.e. 96 unreachable)")
print(f"Newly reachable: {len(newcomers)}")

A = frontier(attach(mu10, S10), label="factor model, 1093 stocks")

picked = set()
for r in A:
    w = r["weights"]
    picked |= set(w[w > 1e-9].index)
got = sorted(picked & set(newcomers))
print(f"\nNewcomers actually held somewhere on the frontier: {len(got)} of {len(newcomers)}")
print(f"  {got[:14]}")
tot_lo = float(A[0]["weights"].reindex(newcomers).fillna(0).sum()) * 100
tot_hi = float(A[-1]["weights"].reindex(newcomers).fillna(0).sum()) * 100
print(f"  combined newcomer weight: {tot_lo:.2f}% at the min-risk end, "
      f"{tot_hi:.2f}% at the max-return end")

print("\n" + "=" * 90)
print("2. THE FRONTIER")
print("=" * 90)
rows = [{"n": r["n_selected"], "ret_%": r["portfolio_return"] * 100,
         "risk_%": r["portfolio_risk"] * 100, "ESG": r["esg_weighted"],
         "w_EU_%": r["weight_region_Europe"] * 100,
         "w_US_%": r["weight_region_United States"] * 100} for r in A]
print(pd.DataFrame(rows).round(2).to_string())

print("\n" + "=" * 90)
print("3. STABILITY - the same test as 03e, on the new model")
print("=" * 90)
mu5, S5 = build_model(prices, 5)
print(f"5y model: {len(mu5)} stocks eligible")
a10 = attach(mu10, S10)
a5 = attach(mu5, S5)
lo = Model2.solve_model2(*a10, mode="min_risk_only", time_limit=120)
hi = Model2.solve_model2(*a10, mode="max_return_only", time_limit=120)
grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 8)
print("Composition churn when only the estimation window changes (10y -> 5y):")
print(f"{'ret %':>7} {'Jaccard':>8} {'active':>8}")
res = []
for b in grid:
    r10 = Model2.solve_model2(*a10, mode="min_risk", target_return=b, time_limit=120)
    r5 = Model2.solve_model2(*a5, mode="min_risk", target_return=b, time_limit=120)
    if not (r10["feasible"] and r5["feasible"]):
        continue
    j, act = compare(r10, r5)
    res.append({"jac": j, "act": act})
    print(f"{b*100:7.2f} {j:8.2f} {act*100:7.1f}%")
Rs = pd.DataFrame(res)
print(f"\nNEW model : Jaccard {Rs.jac.mean():.2f} | active share {Rs.act.mean()*100:.1f}%")
print(f"OLD model : Jaccard 0.28 | active share 64.2%   (from 03e)")

pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in A]).to_csv(
    P("efficient_frontier_factor.csv"), index=False)
pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(A)}).to_csv(
    P("efficient_frontier_weights_factor.csv"))
print("\nSaved efficient_frontier_factor.csv, efficient_frontier_weights_factor.csv")
