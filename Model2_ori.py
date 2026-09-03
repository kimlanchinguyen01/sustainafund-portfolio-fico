"""
SustainaFund — Model 2 (Markowitz / MIQP) — FICO Xpress Python
================================================================
Formulation:
    minimize    w^T Sigma w
    subject to  w^T mu >= beta
                sum(w) = 1
                0.01*y_i <= w_i <= 0.20*y_i,  y_i in {0,1}
                sum(y_i) >= 30
                sum(w_i) per region <= 0.60
                sum(ESG_i * w_i) >= 70
                sum(w_i) per sector <= SECTOR_CAP        (NEW)
                sum(w_i) for controversial tickers <= CONTROVERSIAL_CAP  (NEW)

--------------------------------------------------------------------------
CORRECTIONS (1 Sep 2026) — defects only, the design and the defaults are
unchanged. `git diff` against the previous commit shows every line.

1. FOUR OF TEN Tier-2 tickers do not exist in this dataset, so the screen
   silently excluded 6 of 10. Corrected against shares_full.csv:
       BA.L      -> BAES.L    BAE Systems
       HO.PA     -> TCFP.PA   Thales
       LDO.MI    -> LDOF.MI   Leonardo
       SAAB-B.ST -> SAABb.ST  Saab
   BA.L was the dangerous one: BA.N exists in this dataset and is BOEING,
   so a plausible "fix" would have excluded the wrong company.

2. SCENARIO_TAG is now DERIVED from the active configuration by
   scenario_tag() instead of being a hand-edited string. Before, the tag had
   to be changed by hand together with ENABLE_TIER2_EXCLUSION, and the tag's
   own comment said to set it to the value it already held - so a second run
   silently overwrote the first run's CSVs. Two runs now cannot collide, and
   a single invocation can sweep both.

3. MIP_GAP 0.01 -> 0.001. At a 1% gap the measured cost of a cheap
   constraint is roughly double its true value (verified on an identical
   solve: 0.078pp at 1%, 0.042pp at 0.1% and at 0.01%). Tightening costs no
   measurable time - 0.4s either way on this problem.

4. Input files now point at the current estimates rather than the 31 Aug
   ones. The previous files were local-currency prices over a complete-case
   universe of 997 stocks; the new constraints would have been evaluated on
   superseded numbers. See INPUT NOTE below.
--------------------------------------------------------------------------
"""

import os
import time
import numpy as np
import pandas as pd
import xpress as xp


# ============================================================
# CONFIG
# ============================================================
# INPUT NOTE
#   expected_return_v4.csv     James-Stein shrunk mu, USD, 10-year window
#   covariance_matrix_v4.csv   20-factor PCA covariance, 1087 stocks, PSD
#   Both are built from DIVIDEND-ADJUSTED (total-return) prices. A plain closing
#   price omits dividends and so understates exactly the high-yield, low-volatility
#   names a minimum-variance book is made of: switching lifts the median expected
#   return from 7.80% to 10.39% and the increase follows dividend yield by sector
#   (Energy +3.89pp, Utilities +3.66, Financials +3.36 ... Technology +1.18).
#   Volatility is unchanged, as it should be - dividends add drift, not noise.
#   Six stocks are empty in the source file and are dropped: HOLN.S, URW.PA,
#   EA.OQ, AVB.N, EQR.N, HWM.N (three are REITs, whose adjustment factors are the
#   largest). Hence 1087 rather than 1093. Worth a re-extraction.
#   Both are built from USD-converted prices (ECB reference rates). Prices are
#   quoted in 8 currencies across 19 exchanges; a local-currency return is what
#   a domestic investor earns, not what a USD fund earns. Because
#   ln(P_usd) = ln(P_local) + ln(fx), the FX term is additive and survives the
#   move to returns: it barely moves mu (< 0.3pp) but it puts a shared factor
#   into the covariance, and a local-currency Sigma understated the risk of the
#   min-variance book by 19.7% (8.46% believed vs 10.13% actual).
#   The previous files (expected_return_final.csv / covariance_matrix_shrunk.csv)
#   are local-currency and cover only the 997 stocks with a complete 10-year
#   history; they are kept in the repository for comparison.
FILE_EXPECTED_RETURN = "expected_return_v4.csv"
FILE_COVARIANCE = "covariance_matrix_v4.csv"
FILE_SHARES = "shares_imputed.csv"
FILE_SECTORS = "sectors.xlsx"

COL_STOCK = "Stock"
COL_REGION = "Region"
COL_ESG = "ESG score"
COL_RETURN = "expected_return"
COL_SECTOR = "Sector"

BUDGET = 100_000_000
W_MIN = 0.01
W_MAX = 0.20
REGION_CAP = 0.60
MIN_STOCKS = 30
ESG_MIN = 70.0
ENABLE_ESG_CONSTRAINT = True  # False when test "impact of ESG constraint on returns"
SECTOR_CAP = 0.30            # guard-rail cap per sector — see reasoning above, adjust if it binds oddly
ENABLE_SECTOR_CAP = True
ESG_FLOOR = 30.0
ENABLE_ESG_FLOOR = True

# Manually-flagged controversial-industry tickers (weapons/defense).
# NOT derived from the sector file - "Industrials" is too broad to isolate
# defense companies (Rheinmetall shares that bucket with unrelated firms).
# --- Controversial-industry screening (two-tier policy) ---
# Tier 1 = "controversial weapons" in the narrow sense: company where
# weapons/ammunition is the overwhelming core business, not a side
# segment of a diversified conglomerate. Near-consensus exclusion in
# ESG practice (Norway GPFG-style precedent). Kept ON always.
TIER1_CONTROVERSIAL_TICKERS = ["RHMG.DE"]
ENABLE_TIER1_EXCLUSION = True

# Tier 2 = diversified defense/aerospace conglomerates (defense is a
# major but not sole segment -- e.g. RTX also makes civilian jet
# engines, Kongsberg also has maritime/digital divisions). This is the
# CONTESTED category post-2022 (industry debate on whether conventional
# national defense belongs in an ESG exclusion list). Treated as an
# independent sensitivity toggle so the report can show the exact
# return cost of this policy choice, not bake it in silently.
TIER2_CONTROVERSIAL_TICKERS = [
    "LMT.N", "RTX.N", "NOC.N", "GD.N", "LHX.N",              # US primes
    "KOG.OL", "BAES.L", "TCFP.PA", "LDOF.MI", "SAABb.ST",    # European primes
]   # four of these were corrected - see CORRECTIONS note 1
ENABLE_TIER2_EXCLUSION = False   # set False for the "keep conventional defense" run

CONTROVERSIAL_CAP = 0.0   # applies to whichever tier(s) are enabled: full exclusion

# Tag appended to every output filename so a Tier-2-on run and a Tier-2-off run
# never overwrite each other's CSVs. DERIVED, not hand-edited: it cannot fall out
# of sync with the toggles above. See CORRECTIONS note 2.
def scenario_tag():
    parts = ["sec%d" % int(SECTOR_CAP * 100) if ENABLE_SECTOR_CAP else "nosec"]
    if ENABLE_TIER1_EXCLUSION:
        parts.append("tier1")
    parts.append("tier2on" if ENABLE_TIER2_EXCLUSION else "tier2off")
    if not ENABLE_ESG_CONSTRAINT:
        parts.append("noesg")
    if ENABLE_ESG_FLOOR:
        parts.append("esgfloor%d" % int(ESG_FLOOR))
    return "_".join(parts)

TIME_LIMIT_SEC = 300
MIP_GAP = 0.001   # see CORRECTIONS note 3

RUN_FULL_SWEEP = True
N_FRONTIER_POINTS = 15

os.environ.setdefault("XPAUTH_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "xpauth.xpr"))

# %%
# ============================================================
# 1. LOAD & MERGE DATA
# ============================================================
def load_data():
    ret = pd.read_csv(FILE_EXPECTED_RETURN)
    cov = pd.read_csv(FILE_COVARIANCE, index_col=0)
    shares = pd.read_csv(FILE_SHARES)
    sectors = pd.read_excel(FILE_SECTORS)   # needs openpyxl: pip install openpyxl if missing

    print("expected_return columns:", ret.columns.tolist())
    print("covariance matrix shape:", cov.shape, "| first cols:", cov.columns[:3].tolist())
    print("shares columns:", shares.columns.tolist())
    print("sectors columns:", sectors.columns.tolist())

    ret = ret.set_index(COL_STOCK)[COL_RETURN]
    shares = shares.set_index(COL_STOCK)
    sectors = sectors.set_index(COL_STOCK)[COL_SECTOR]

    common = sorted(set(ret.index) & set(cov.index) & set(cov.columns) & set(shares.index))
    print(f"Stocks common to all required sources: {len(common)}")
    dropped = (set(ret.index) | set(shares.index)) - set(common)
    if dropped:
        print(f"WARNING: {len(dropped)} stocks dropped due to missing data "
              f"(e.g. {list(dropped)[:5]})")

    mu = ret.loc[common]
    Sigma = cov.loc[common, common]
    region = shares.loc[common, COL_REGION]
    esg = shares.loc[common, COL_ESG]

#%%
    # sector is optional/supplementary: don't shrink the universe over it,
    # just bucket anything missing as "Unknown" (which then also falls under the cap)
    sector = sectors.reindex(common)
    n_missing_sector = int(sector.isna().sum())
    if n_missing_sector > 0:
        print(f"WARNING: {n_missing_sector} stocks missing sector -> assigned 'Unknown'")
    sector = sector.fillna("Unknown")

    assert not mu.isna().any(), "NaN found in expected return!"
    assert not esg.isna().any(), "NaN found in ESG - check you're using the imputed file!"
    assert not Sigma.isna().any().any(), "NaN found in covariance matrix!"

    if ENABLE_ESG_FLOOR:
        low_esg_mask = esg < ESG_FLOOR
        n_low_esg = int(low_esg_mask.sum())
        if n_low_esg > 0:
            print(f"ESG FLOOR: excluding {n_low_esg} stocks with individual ESG < {ESG_FLOOR} "
                  f"(e.g. {list(esg[low_esg_mask].index[:5])})")
            keep = ~low_esg_mask
            mu = mu[keep]
            Sigma = Sigma.loc[keep, keep]
            region = region[keep]
            sector = sector[keep]
            esg = esg[keep]

        # Check which controversial/defense candidate tickers are actually
    # present in the cleaned universe (informational only -- the real
    # exclusion happens in solve_model2 via TIER1/TIER2 lists above).
    t1_present = [t for t in TIER1_CONTROVERSIAL_TICKERS if t in common]
    t2_present = [t for t in TIER2_CONTROVERSIAL_TICKERS if t in common]
    print(f"Tier 1 (controversial weapons) present in universe: {t1_present}")
    print(f"Tier 2 (diversified defense conglomerates) present in universe: {t2_present}")
    t2_missing = [t for t in TIER2_CONTROVERSIAL_TICKERS if t not in common]
    if t2_missing:
        print(f"  (not found / not in universe: {t2_missing} -- check ticker spelling "
              f"against your data if you expected these to be present)")
        
    return mu, Sigma, region, esg, sector

# %%
# ============================================================
# 2. BUILD & SOLVE MODEL 2
# ============================================================
def solve_model2(mu, Sigma, region, esg, sector,
                  mode="min_risk",
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
    sector_arr = sector.values
    stocks_arr = np.array(stocks)

    p = xp.problem("SustainaFund_Model2")
    p.controls.miprelstop = mip_gap
    p.controls.timelimit = time_limit
    p.controls.outputlog = 1 if verbose else 0

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

    if ENABLE_SECTOR_CAP:
        for s in np.unique(sector_arr):
            mask = (sector_arr == s)
            p.addConstraint(xp.Sum(w[mask]) <= SECTOR_CAP)

    if ENABLE_TIER1_EXCLUSION:
        t1_mask = np.isin(stocks_arr, TIER1_CONTROVERSIAL_TICKERS)
        if t1_mask.any():
            p.addConstraint(xp.Sum(w[t1_mask]) <= CONTROVERSIAL_CAP)
    if ENABLE_TIER2_EXCLUSION:
        t2_mask = np.isin(stocks_arr, TIER2_CONTROVERSIAL_TICKERS)
        if t2_mask.any():
            p.addConstraint(xp.Sum(w[t2_mask]) <= CONTROVERSIAL_CAP)

    portfolio_return_expr = xp.Dot(mu_arr, w)
    portfolio_var_expr = xp.Dot(w, Sigma_arr, w)

    if mode == "min_risk":
        assert target_return is not None
        p.addConstraint(portfolio_return_expr >= target_return)
        p.setObjective(portfolio_var_expr, sense=xp.minimize)
    elif mode == "max_return":
        # risk_cap is an annualised STANDARD DEVIATION, so it must be squared
        # before being compared with a variance. Without the square the cap sits
        # at variance = risk_cap, i.e. a risk of sqrt(risk_cap): passing 0.12
        # permits 34.64% risk, 2.89x looser than intended, and on this data the
        # constraint does not bind at all - you silently get the unconstrained
        # max-return corner (22.29% risk instead of 12%).
        assert risk_cap is not None, \
            "risk_cap is an annualised STANDARD DEVIATION, e.g. 0.12 for 12%"
        p.addConstraint(portfolio_var_expr <= risk_cap ** 2)
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

    result = {
        "mode": mode,
        "solvestatus": solvestatus.name,
        "solstatus": solstatus.name,
        "feasible": solstatus in (xp.SolStatus.OPTIMAL, xp.SolStatus.FEASIBLE),
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
        for s in np.unique(sector_arr):
            mask = (sector_arr == s)
            result[f"weight_sector_{s}"] = float(w_sol[mask].sum())
        result["weight_tier1_controversial"] = float(w_sol[np.isin(stocks_arr, TIER1_CONTROVERSIAL_TICKERS)].sum())
        result["weight_tier2_defense"] = float(w_sol[np.isin(stocks_arr, TIER2_CONTROVERSIAL_TICKERS)].sum())

    return result


# ============================================================
# 3. FEASIBILITY + SCALE CHECK
# ============================================================
def check_feasibility_and_scale(mu, Sigma, region, esg, sector):
    print("\n=== STEP 1: FEASIBILITY + SCALE CHECK (full universe) ===\n")

    print("--- (a) Global min-variance (no return constraint) ---")
    r_min = solve_model2(mu, Sigma, region, esg, sector, mode="min_risk_only", time_limit=180)
    print(f"  status={r_min['solstatus']}  time={r_min['elapsed_sec']:.1f}s")
    if r_min["feasible"]:
        print(f"  return={r_min['portfolio_return']:.4f}  risk={r_min['portfolio_risk']:.4f}  "
              f"n_selected={r_min['n_selected']}  esg={r_min['esg_weighted']:.2f}")
    else:
        raise RuntimeError("INFEASIBLE even for pure min-variance! Check constraints/data.")

    print("\n--- (b) Pure max return (no risk constraint) ---")
    r_max = solve_model2(mu, Sigma, region, esg, sector, mode="max_return_only", time_limit=180)
    print(f"  status={r_max['solstatus']}  time={r_max['elapsed_sec']:.1f}s")
    if r_max["feasible"]:
        print(f"  return={r_max['portfolio_return']:.4f}  risk={r_max['portfolio_risk']:.4f}  "
              f"n_selected={r_max['n_selected']}  esg={r_max['esg_weighted']:.2f}")

    print(f"\n=> Feasible beta range: [{r_min['portfolio_return']:.4f}, {r_max['portfolio_return']:.4f}]")
    return r_min, r_max


# ============================================================
# 4. EFFICIENT FRONTIER
# ============================================================
def efficient_frontier(mu, Sigma, region, esg, sector, r_min, r_max,
                        n_points=N_FRONTIER_POINTS,
                        time_limit=TIME_LIMIT_SEC, mip_gap=MIP_GAP):

    beta_lo = r_min["portfolio_return"]
    beta_hi = r_max["portfolio_return"]
    betas = np.linspace(beta_lo, beta_hi, n_points)

    frontier = []
    for i, beta in enumerate(betas):
        print(f"\n[{i + 1}/{n_points}] target return beta = {beta:.4f}")
        res = solve_model2(mu, Sigma, region, esg, sector, mode="min_risk", target_return=beta,
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
    mu, Sigma, region, esg, sector = load_data()
    r_min, r_max = check_feasibility_and_scale(mu, Sigma, region, esg, sector)

    print("\nTop 10 holdings - min-variance portfolio:")
    print(r_min["weights"].sort_values(ascending=False).head(10))

    print("\nTop 10 holdings - max-return portfolio:")
    print(r_max["weights"].sort_values(ascending=False).head(10))

    if RUN_FULL_SWEEP:
        frontier = efficient_frontier(mu, Sigma, region, esg, sector, r_min, r_max)
        rows = [{k: v for k, v in r.items() if k != "weights"} for r in frontier]
        tag = scenario_tag()
        pd.DataFrame(rows).to_csv(f"efficient_frontier_model2_{tag}.csv", index=False)
        print(f"\nSaved efficient_frontier_model2_{tag}.csv")

        weights_df = pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(frontier) if r["feasible"]})
        weights_df.to_csv(f"efficient_frontier_weights_{tag}.csv")
        print(f"Saved efficient_frontier_weights_{tag}.csv")
    else:
        print("\nRUN_FULL_SWEEP=False -> only the feasibility+scale check ran.")