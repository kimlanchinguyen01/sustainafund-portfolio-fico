"""
SustainaFund — Model 3 = Model 2 + country concentration cap
=============================================================
Model 2 left a real hole: its diversification constraint is on REGION only, and
the region "United States" is coextensive with the country "United States". So
Model 2's min-variance solution put 45.4% of the budget into Switzerland (Swiss
cantonal banks and real estate - MOBN.S, ALLN.S, BCVN.S, VATN.S, PSPN.S), which
passes every Model 2 constraint while being badly concentrated in one small
market and two correlated sectors.

Added:  sum of weights in any one country <= COUNTRY_CAP

The United States is exempt, and this is forced rather than chosen: the region
cap of 60% over two regions implies US >= 40%, so any country cap below 40%
would make the problem infeasible if applied to the US. The US is also the one
country that is itself a diversified market (500 constituents, all sectors),
whereas the European countries are not.

Setting COUNTRY_CAP = 1.0 disables the constraint and must reproduce Model 2
exactly - 08_country_cap.py asserts this before trusting any capped run.

Everything else is Model 2 unchanged.


SustainaFund — Model 2 (Markowitz / MIQP) — FICO Xpress Python
================================================================
Formulation (expected-return-constrained scalarization):
    minimize    w^T Sigma w
    subject to  w^T mu >= beta          (target return, swept to build the efficient frontier)
                sum(w) = 1              (full investment)
                0.01*y_i <= w_i <= 0.20*y_i,  y_i in {0,1}   (1-20% if selected, 0 otherwise)
                sum(y_i) >= 30          (minimum 30 stocks)
                sum(w_i) per region <= 0.60
                sum(ESG_i * w_i) >= 70  (weighted-average ESG)
"""

import os
import time
import numpy as np
import pandas as pd
import xpress as xp


# ============================================================
# CONFIG — adjust if file/column names don't match reality
# ============================================================
FILE_EXPECTED_RETURN = "expected_return_final.csv"
FILE_COVARIANCE = "covariance_matrix_shrunk.csv"
FILE_SHARES = "shares_imputed.csv"          # switch to shares_excluded.csv for the sensitivity check later

COL_STOCK = "Stock"
COL_REGION = "Region"
COL_ESG = "ESG score"
COL_RETURN = "expected_return"              # verified against 01c output header

BUDGET = 100_000_000
W_MIN = 0.01
W_MAX = 0.20
REGION_CAP = 0.60
MIN_STOCKS = 30
ESG_MIN = 70.0
COUNTRY_CAP = 0.25            # max share of the budget in any single country
COUNTRY_CAP_EXEMPT = {"United States"}   # governed by the region cap; see docstring

TIME_LIMIT_SEC = 300     # per-solve time limit (seconds)
MIP_GAP = 0.01           # stop within 1% of optimal

RUN_FULL_SWEEP = True    # feasibility+scale check now passes; full sweep enabled
N_FRONTIER_POINTS = 15

os.environ.setdefault("XPAUTH_PATH", os.path.abspath("xpauth.xpr"))


# ============================================================
# 1. LOAD & MERGE DATA
# ============================================================
def load_data():
    ret = pd.read_csv(FILE_EXPECTED_RETURN)
    cov = pd.read_csv(FILE_COVARIANCE, index_col=0)
    shares = pd.read_csv(FILE_SHARES)

    print("expected_return columns:", ret.columns.tolist())
    print("covariance matrix shape:", cov.shape, "| first cols:", cov.columns[:3].tolist())
    print("shares columns:", shares.columns.tolist())

    ret = ret.set_index(COL_STOCK)[COL_RETURN]
    shares = shares.set_index(COL_STOCK)

    common = sorted(set(ret.index) & set(cov.index) & set(cov.columns) & set(shares.index))
    print(f"Stocks common to all 3 data sources: {len(common)}")
    dropped = (set(ret.index) | set(shares.index)) - set(common)
    if dropped:
        print(f"WARNING: {len(dropped)} stocks dropped due to missing data in one of the "
              f"3 sources (e.g. {list(dropped)[:5]})")

    mu = ret.loc[common]
    Sigma = cov.loc[common, common]
    region = shares.loc[common, COL_REGION]
    esg = shares.loc[common, COL_ESG]

    assert not mu.isna().any(), "NaN found in expected return!"
    assert not esg.isna().any(), "NaN found in ESG - make sure you're using the imputed file!"
    assert not Sigma.isna().any().any(), "NaN found in covariance matrix!"

    return mu, Sigma, region, esg


# ============================================================
# 2. BUILD & SOLVE MODEL 2
# ============================================================
def solve_model2(mu, Sigma, region, esg, country=None,
                  mode="min_risk",
                  # "min_risk"        : minimize risk, s.t. return >= target_return
                  # "max_return"      : maximize return, s.t. risk <= risk_cap
                  # "min_risk_only"   : global min-variance, no return constraint (beta_lo)
                  # "max_return_only" : pure max return, no risk constraint (beta_hi)
                  target_return=None,
                  risk_cap=None,
                  time_limit=TIME_LIMIT_SEC,
                  mip_gap=MIP_GAP,
                  verbose=True):

    stocks = list(mu.index)
    n = len(stocks)
    mu_arr = mu.values.astype(float)
    Sigma_arr = Sigma.values.astype(float)
    region_arr = region.values
    esg_arr = esg.values.astype(float)
    country_arr = None if country is None else country.loc[stocks].values

    p = xp.problem("SustainaFund_Model3")
    p.controls.miprelstop = mip_gap
    p.controls.timelimit = time_limit
    p.controls.outputlog = 0

    w = p.addVariables(n, lb=0, ub=W_MAX, name="w")
    y = p.addVariables(n, vartype=xp.binary, name="y")

    p.addConstraint(w <= W_MAX * y)
    p.addConstraint(w >= W_MIN * y)
    p.addConstraint(xp.Sum(w) == 1)
    p.addConstraint(xp.Sum(y) >= MIN_STOCKS)

    for r in np.unique(region_arr):
        mask = (region_arr == r)
        p.addConstraint(xp.Sum(w[mask]) <= REGION_CAP)

    p.addConstraint(xp.Dot(esg_arr, w) >= ESG_MIN)

    if country_arr is not None and COUNTRY_CAP < 1.0:
        for c in np.unique(country_arr):
            if c in COUNTRY_CAP_EXEMPT:
                continue
            mask = (country_arr == c)
            if mask.sum() == 0:
                continue
            p.addConstraint(xp.Sum(w[mask]) <= COUNTRY_CAP)

    portfolio_return_expr = xp.Dot(mu_arr, w)
    portfolio_var_expr = xp.Dot(w, Sigma_arr, w)

    if mode == "min_risk":
        assert target_return is not None
        p.addConstraint(portfolio_return_expr >= target_return)
        p.setObjective(portfolio_var_expr, sense=xp.minimize)
    elif mode == "max_return":
        assert risk_cap is not None
        p.addConstraint(portfolio_var_expr <= risk_cap)
        p.setObjective(portfolio_return_expr, sense=xp.maximize)
    elif mode == "min_risk_only":
        p.setObjective(portfolio_var_expr, sense=xp.minimize)
    elif mode == "max_return_only":
        p.setObjective(portfolio_return_expr, sense=xp.maximize)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    t0 = time.time()
    solvestatus, solstatus = p.optimize()
    elapsed = time.time() - t0

    # [FIX 2026-08-31] Xpress 9.9 returns UPPERCASE enum names:
    #   SolStatus  -> NOTFOUND | OPTIMAL | FEASIBLE | INFEASIBLE | UNBOUNDED
    # The original compared against ("Optimal", "Feasible"), which never
    # matches - so every successful solve was recorded as infeasible and
    # check_feasibility_and_scale() raised "INFEASIBLE even for pure
    # min-variance" on a run the solver had just returned OPTIMAL for.
    # The model itself was correct all along.
    result = {
        "mode": mode,
        "solvestatus": solvestatus.name,
        "solstatus": solstatus.name,
        "feasible": solstatus.name in ("OPTIMAL", "FEASIBLE"),
        "elapsed_sec": elapsed,
    }

    if result["feasible"]:
        w_sol = np.array(p.getSolution(w))
        y_sol = np.array(p.getSolution(y))
        result["weights"] = pd.Series(w_sol, index=stocks)
        result["n_selected"] = int(round(y_sol.sum()))
        result["portfolio_return"] = float(mu_arr @ w_sol)
        result["portfolio_variance"] = float(w_sol @ Sigma_arr @ w_sol)
        result["portfolio_risk"] = float(np.sqrt(max(result["portfolio_variance"], 0)))
        result["esg_weighted"] = float(esg_arr @ w_sol)
        for r in np.unique(region_arr):
            mask = (region_arr == r)
            result[f"weight_region_{r}"] = float(w_sol[mask].sum())
        if country_arr is not None:
            cw = pd.Series(w_sol).groupby(pd.Series(country_arr)).sum()
            result["max_country"] = str(cw.idxmax())
            result["max_country_weight"] = float(cw.max())

    return result


# ============================================================
# 3. FEASIBILITY + SCALE CHECK (do this FIRST, before sweeping)
# ============================================================
def check_feasibility_and_scale(mu, Sigma, region, esg):
    print("\n=== STEP 1: FEASIBILITY + SCALE CHECK (full universe) ===\n")

    print("--- (a) Global min-variance (no return constraint) ---")
    r_min = solve_model2(mu, Sigma, region, esg, mode="min_risk_only", time_limit=180)
    print(f"  status={r_min['solstatus']}  time={r_min['elapsed_sec']:.1f}s")
    if r_min["feasible"]:
        print(f"  return={r_min['portfolio_return']:.4f}  risk={r_min['portfolio_risk']:.4f}  "
              f"n_selected={r_min['n_selected']}  esg={r_min['esg_weighted']:.2f}")
    else:
        raise RuntimeError(
            "INFEASIBLE even for pure min-variance! Check the constraints or the data."
        )

    print("\n--- (b) Pure max return (no risk constraint) ---")
    r_max = solve_model2(mu, Sigma, region, esg, mode="max_return_only", time_limit=180)
    print(f"  status={r_max['solstatus']}  time={r_max['elapsed_sec']:.1f}s")
    if r_max["feasible"]:
        print(f"  return={r_max['portfolio_return']:.4f}  risk={r_max['portfolio_risk']:.4f}  "
              f"n_selected={r_max['n_selected']}  esg={r_max['esg_weighted']:.2f}")

    print(f"\n=> Feasible beta range for the frontier: [{r_min['portfolio_return']:.4f}, "
          f"{r_max['portfolio_return']:.4f}]")
    print(f"=> Single MIQP solve time on the full universe: ~{r_min['elapsed_sec']:.0f}-"
          f"{r_max['elapsed_sec']:.0f}s. Multiply by the number of sweeps needed "
          f"(frontier + sensitivity + robustness + backtest) to estimate total runtime.")

    return r_min, r_max


# ============================================================
# 4. EFFICIENT FRONTIER (only run after step 1 looks OK)
# ============================================================
def efficient_frontier(mu, Sigma, region, esg, r_min, r_max,
                        n_points=N_FRONTIER_POINTS,
                        time_limit=TIME_LIMIT_SEC, mip_gap=MIP_GAP):

    beta_lo = r_min["portfolio_return"]
    beta_hi = r_max["portfolio_return"]
    betas = np.linspace(beta_lo, beta_hi, n_points)

    frontier = []
    for i, beta in enumerate(betas):
        print(f"\n[{i + 1}/{n_points}] target return beta = {beta:.4f}")
        res = solve_model2(mu, Sigma, region, esg, mode="min_risk", target_return=beta,
                            time_limit=time_limit, mip_gap=mip_gap, verbose=False)
        res["target_beta"] = beta
        frontier.append(res)
        status = "OK" if res["feasible"] else "INFEASIBLE"
        print(f"  -> {status}  ({res['elapsed_sec']:.1f}s)"
              + (f"  risk={res['portfolio_risk']:.4f}" if res["feasible"] else ""))

    return frontier


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    mu, Sigma, region, esg = load_data()
    r_min, r_max = check_feasibility_and_scale(mu, Sigma, region, esg)

    if RUN_FULL_SWEEP:
        frontier = efficient_frontier(mu, Sigma, region, esg, r_min, r_max)
        rows = [{k: v for k, v in r.items() if k != "weights"} for r in frontier]
        pd.DataFrame(rows).to_csv("efficient_frontier_model2.csv", index=False)
        print("\nSaved efficient_frontier_model2.csv")

        weights_df = pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(frontier) if r["feasible"]})
        weights_df.to_csv("efficient_frontier_weights.csv")
        print("Saved efficient_frontier_weights.csv")
    else:
        print("\nRUN_FULL_SWEEP=False -> only the feasibility+scale check ran. "
              "If the timing looks acceptable, set RUN_FULL_SWEEP=True and rerun.")