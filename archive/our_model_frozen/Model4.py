"""
SustainaFund — Model 4 = Model 2 + Chi Chloe's sector cap
==========================================================
Model 2's diversification constraint is on REGION only. Chloe's Model2_ori.py
added a per-sector cap, which catches a concentration the region cap cannot:
without it a single sector reaches 36% of the budget (Industrials) and the
min-variance book puts 35% into Consumer Defensive. Her 30% cap costs +0.001pp
of return on average - it is free.

This model takes that cap and drops the 25% country cap that Model3 used, per
the team decision to keep one concentration constraint rather than two.

    KNOWN CONSEQUENCE, measured not assumed: the sector cap does not restrain
    country concentration. With it alone, Switzerland reaches 46.8% of the
    budget (Swiss cantonal banks and real estate). Model3's country cap held
    that to 25.0% at a cost of 0.156pp. Dropping it is a deliberate choice and
    belongs on the limitations slide.

Also carried over from Chloe's file, with fixes:

  * her two-tier controversial-industry screen, off by default here
  * FOUR of her ten Tier-2 tickers do not exist in this universe and were
    silently skipped: BA.L -> BAES.L, HO.PA -> TCFP.PA, LDO.MI -> LDOF.MI,
    SAAB-B.ST -> SAABb.ST. BA.L is the dangerous one - BA.N exists here and is
    BOEING, so a plausible "fix" would have excluded the wrong company.
  * SCENARIO_TAG is now DERIVED from the active constraints instead of being a
    manually edited string. In her file the tag and the toggle had to be changed
    together by hand, and the tag's own comment told you to set it to the value
    it already had - so a second run silently overwrote the first run's CSVs.
    scenario_tag() below cannot get out of sync with the configuration.
  * MIP_GAP 0.01 -> 0.001. At 1% the measured cost of a cheap constraint is
    roughly double its true value (verified: 0.078pp vs 0.042pp on the same
    solve) and tightening costs no measurable time.


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

# --- Chloe's sector cap ---
SECTOR_CAP = 0.30
ENABLE_SECTOR_CAP = True

# --- Chloe's two-tier controversial-industry screen (both off by default) ---
# Tier 1: weapons/ammunition is the core business. Near-consensus ESG exclusion.
TIER1_TICKERS = ["RHMG.DE"]
ENABLE_TIER1 = False
# Tier 2: diversified defence/aerospace, where defence is a major but not sole
# segment. Contested post-2022; kept as an independent toggle so its cost can be
# priced rather than baked in. Tickers corrected against this universe.
TIER2_TICKERS = ["LMT.N", "RTX.N", "NOC.N", "GD.N", "LHX.N", "KOG.OL",
                 "BAES.L", "TCFP.PA", "LDOF.MI", "SAABb.ST"]
ENABLE_TIER2 = False
CONTROVERSIAL_CAP = 0.0

ENABLE_ESG_CONSTRAINT = True   # False to price the ESG constraint


def scenario_tag():
    """Output filename tag, derived from the configuration so it cannot go stale."""
    parts = []
    parts.append(f"sec{int(SECTOR_CAP*100)}" if ENABLE_SECTOR_CAP else "nosec")
    if ENABLE_TIER1:
        parts.append("t1")
    if ENABLE_TIER2:
        parts.append("t2")
    if not ENABLE_ESG_CONSTRAINT:
        parts.append("noesg")
    return "_".join(parts)

TIME_LIMIT_SEC = 300     # per-solve time limit (seconds)
MIP_GAP = 0.001          # 1% overstates cheap constraints ~2x; tightening is free

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
def solve_model2(mu, Sigma, region, esg, sector=None,
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
    sector_arr = None if sector is None else sector.loc[stocks].values
    tick_arr = np.array(stocks)

    p = xp.problem("SustainaFund_Model4")
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

    if ENABLE_ESG_CONSTRAINT:
        p.addConstraint(xp.Dot(esg_arr, w) >= ESG_MIN)

    if ENABLE_SECTOR_CAP and sector_arr is not None:
        for s_ in np.unique(sector_arr):
            p.addConstraint(xp.Sum(w[sector_arr == s_]) <= SECTOR_CAP)

    for enabled, tickers in ((ENABLE_TIER1, TIER1_TICKERS), (ENABLE_TIER2, TIER2_TICKERS)):
        if not enabled:
            continue
        mask = np.isin(tick_arr, tickers)
        if mask.any():
            p.addConstraint(xp.Sum(w[mask]) <= CONTROVERSIAL_CAP)

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
        if sector_arr is not None:
            sw = pd.Series(w_sol).groupby(pd.Series(sector_arr)).sum()
            result["max_sector"] = str(sw.idxmax())
            result["max_sector_weight"] = float(sw.max())
        result["weight_tier1"] = float(w_sol[np.isin(tick_arr, TIER1_TICKERS)].sum())
        result["weight_tier2"] = float(w_sol[np.isin(tick_arr, TIER2_TICKERS)].sum())

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