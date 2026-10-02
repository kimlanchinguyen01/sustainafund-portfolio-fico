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
                sum(w_i) per country <= COUNTRY_CAP, US exempt          (NEW)

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
ADDITIONS (3 Sep 2026) — three additions, no change to the existing model.
Ideas 1-3 come from FICO's own python-notebooks/xpress-api/modeling_examples.

1. COUNTRY CAP. sum of w over any one country <= COUNTRY_CAP, US exempt.
   Model 2 capped REGION and SECTOR, and Switzerland slipped between them:
   it is not a region, and it spans two sectors (cantonal banks and real
   estate), so neither cap could see it. Measured uncapped, Switzerland is
   the largest country at every frontier point but the last, peaking at
   46.81% at the min-risk end.
   Default OFF. When OFF, or when country= is not passed, the model is the
   model that produced the current results.

2. GROUP CAPS VIA PANDAS groupby. Region, sector and country caps are now
   one addConstraint each, the idiom used in FICO's portfolio_pandas.ipynb,
   instead of three np.unique loops. Verified equivalent rather than assumed:
   both forms write a byte-identical LP file. A separate check re-solved all
   15 frontier points with the pre-edit code and this code and got identical
   numbers at every point.
   The rewrite also buys the constraint labels for free - addConstraint on a
   grouped Series returns a Series indexed by the group key, so an IIS can
   name "country_cap=Switzerland" rather than "R412".

3. IIS INFEASIBILITY DIAGNOSIS. See diagnose_infeasible(); called
   automatically whenever a solve comes back INFEASIBLE. Pattern from
   diagnose_infeasible.ipynb, corrected against the API docs on two points
   the notebook's helper does differently - see that function's docstring.

NOT adopted, and why - so nobody re-derives these:
  * Blended multi-objective weights (markowitz_multiobj.ipynb) to trace the
    frontier. A weighted sum only reaches points on the CONVEX HULL of the
    Pareto frontier. With binary y the frontier is not convex, so some
    Pareto-optimal portfolios are unreachable by any weight. The
    epsilon-constraint sweep used here (min risk s.t. return >= beta) reaches
    all of them. The notebook's example has no binaries, hence no problem.
  * Build once and chgRHS between frontier points instead of rebuilding.
    Measured, not assumed: the build is 0.09s of a 0.8s solve (linear 0.01,
    Dot(w,Sigma,w) 0.05, setObjective 0.03), so about 1.4s over a 15-point
    sweep. Warm-started re-solves do run ~40% faster, but the saving is
    seconds and it would cost solve_model2 its statelessness.
  * addIndicator for the w/y linking. W_MAX = 0.20 is already a tight
    coefficient, so w <= W_MAX*y is not a loose big-M. Indicators are
    enforced by branching and give a weaker LP relaxation, i.e. slower.
    Semi-continuous variables were tested earlier and rejected: 26 real
    positions while reporting 30.
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
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(CODE_DIR), "data")        # model inputs
RESULTS_DIR = os.path.join(os.path.dirname(CODE_DIR), "results")  # model outputs

FILE_EXPECTED_RETURN = os.path.join(DATA_DIR, "expected_return_v4.csv")
FILE_COVARIANCE = os.path.join(DATA_DIR, "covariance_matrix_v4.csv")
FILE_SHARES = os.path.join(DATA_DIR, "shares_imputed.csv")
FILE_SECTORS = os.path.join(DATA_DIR, "sectors.xlsx")

COL_STOCK = "Stock"
COL_REGION = "Region"
COL_ESG = "ESG score"
COL_RETURN = "expected_return"
COL_SECTOR = "Sector"
COL_COUNTRY = "Country"

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

# --- Country concentration cap (see ADDITIONS note 1) ---
# The region cap cannot see a country, and the sector cap cannot see a country
# that spans two sectors. Switzerland exploited both gaps at once and reached
# 47% of the risk-averse book through cantonal banks and real estate.
COUNTRY_CAP = 0.25
ENABLE_COUNTRY_CAP = False        # True enables the cap; the tag then records it
# The US exemption is FORCED, not a policy choice: REGION_CAP = 0.60 spread over
# two regions implies US >= 0.40, so any cap below 40% applied to the US makes
# the problem infeasible on its own. The US is also the one country here that is
# itself a diversified market (500 constituents, every sector), whereas the
# European countries in this universe are not.
COUNTRY_CAP_EXEMPT = {"United States"}

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
    # Appended only when the cap is on, so a capped run cannot overwrite the
    # uncapped CSVs and an uncapped run keeps the filenames it has always had.
    if ENABLE_COUNTRY_CAP:
        parts.append("cty%d" % int(COUNTRY_CAP * 100))
    return "_".join(parts)

TIME_LIMIT_SEC = 300
MIP_GAP = 0.001   # see CORRECTIONS note 3

RUN_FULL_SWEEP = True
N_FRONTIER_POINTS = 15

os.environ.setdefault("XPAUTH_PATH", os.path.join(os.path.dirname(os.path.dirname(CODE_DIR)), "xpauth.xpr"))

# %%
# ============================================================
# 1. LOAD & MERGE DATA
# ============================================================
def load_data(return_country=False):
    """Load and align the four inputs.

    Returns (mu, Sigma, region, esg, sector) by default. `return_country=True`
    appends the country Series. The default keeps the five-tuple contract that
    23_scenario_matrix.py, 17_chloe_full.py and 05c_multifactor.py unpack
    positionally, so enabling the country cap does not break them.
    """
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
    country = shares.loc[common, COL_COUNTRY]

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
            country = country[keep]

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
        
    if return_country:
        assert not country.isna().any(), "NaN found in Country - check the imputed file!"
        n_capped = int((~country.isin(COUNTRY_CAP_EXEMPT)).sum())
        print(f"Countries: {country.nunique()} distinct, {n_capped} stocks subject to "
              f"a country cap ({len(country) - n_capped} exempt)")
        return mu, Sigma, region, esg, sector, country
    return mu, Sigma, region, esg, sector

# %%
# ============================================================
# 2a. INFEASIBILITY DIAGNOSIS (IIS)
# ============================================================
def diagnose_infeasible(p, labels=None, find_all=False, max_report=12):
    """Name the constraints that conflict, instead of reporting "INFEASIBLE".

    An Irreducible Infeasible Set is a minimal subset of constraints and bounds
    that is infeasible on its own and becomes feasible if any one member is
    removed. Repairing one IIS need not make the model feasible - there may be
    other independent ones, which is what find_all=True enumerates.

    Pattern from FICO's diagnose_infeasible.ipynb, with two corrections made
    against docs/solver/python-interface.md rather than from memory:

      * getIISData returns INDICES, not objects, and returns eight values:
        rowind, colind, contype, bndtype, duals, djs, isolrows, isolcols.
        The isolation fields are 0/1/-1 flags, not names. Indices are mapped
        to names through problem.getConstraint / problem.getVariable.
      * IISIsolations applies to LINEAR problems only. Model 2 is a MIQP, so
        isolations are not available here and are not requested. The IIS
        itself is, because firstIIS "applies to all problem types".

    firstIIS/IISAll signal success through the iissolstatus attribute;
    IISAll returns None, so its return value must not be tested.

    Returns a dict; 'report' is a printable string.
    """
    out = {"is_infeasible": False, "iis_found": False, "num_iis": 0,
           "iis_list": [], "report": ""}

    if p.attributes.solstatus != xp.SolStatus.INFEASIBLE:
        out["report"] = f"not infeasible (solstatus {p.attributes.solstatus.name})"
        return out
    out["is_infeasible"] = True

    if find_all:
        p.IISAll()
    else:
        p.firstIIS(1)          # mode 1 = emphasise a simple IIS

    status = p.attributes.iissolstatus
    if status == xp.IISSolStatus.UNSTARTED:
        out["report"] = "IIS computation did not start (licence or input error)"
        return out
    if status == xp.IISSolStatus.FEASIBLE:
        out["report"] = "no IIS found - the problem may in fact be feasible"
        return out

    out["iis_found"] = True
    # IISStatus returns PER-IIS LISTS, not scalars: rowsizes/colsizes are indexed
    # 0..numiis, where entry 0 describes the IIS APPROXIMATION and 1..numiis the
    # real IIS. Printing them raw reads as "rows [3, 3]", which is meaningless.
    numiis, rowsizes, colsizes, suminf, numinf = p.IISStatus()
    out["num_iis"] = numiis
    out["approx_size"] = {"rows": rowsizes[0], "bounds": colsizes[0]} if len(rowsizes) else {}

    lines = ["INFEASIBLE - IIS diagnosis", "=" * 46,
             f"{numiis} independent IIS "
             f"(initial infeasible subproblem: {rowsizes[0]} rows, {colsizes[0]} bounds)"]
    if status == xp.IISSolStatus.UNFINISHED:
        lines.append("WARNING: interrupted - the subsystem may be larger than a true IIS")

    for k in range(1, numiis + 1):
        rowind, colind, contype, bndtype = p.getIISData(k)[:4]
        # The index list MUST be passed positionally. p.getConstraint(index=[...])
        # returns an EMPTY LIST instead of raising - a silent wrong answer, which
        # is how this reported "3 constraints" and then named none of them.
        ctr_names = [(labels or {}).get(int(i), c.name)
                     for i, c in zip(rowind, p.getConstraint(list(rowind)))] \
                    if len(rowind) else []
        var_names = [v.name for v in p.getVariable(list(colind))] if len(colind) else []
        out["iis_list"].append({"iis_number": k,
                                "constraints": ctr_names, "constraint_types": list(contype),
                                "bounds": var_names, "bound_types": list(bndtype)})

        lines.append(f"\n--- IIS {k}: {len(rowind)} constraints, {len(colind)} bounds "
                     f"(total infeasibility {suminf[k]:.4g}) ---")
        for name, t in list(zip(ctr_names, contype))[:max_report]:
            lines.append(f"  constraint {name}  (relax the '{t}' side)")
        if len(ctr_names) > max_report:
            lines.append(f"  ... and {len(ctr_names) - max_report} more constraints")
        for name, t in list(zip(var_names, bndtype))[:max_report]:
            lines.append(f"  bound on {name}  (relax '{t}')")
        if len(var_names) > max_report:
            lines.append(f"  ... and {len(var_names) - max_report} more bounds")

    out["report"] = "\n".join(lines)
    return out


# %%
# ============================================================
# 2. BUILD & SOLVE MODEL 2
# ============================================================
def solve_model2(mu, Sigma, region, esg, sector,
                  country=None,
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
    country_arr = country.values if country is not None else None

    p = xp.problem("SustainaFund_Model2")
    p.controls.miprelstop = mip_gap
    p.controls.timelimit = time_limit
    p.controls.outputlog = 1 if verbose else 0

    w = p.addVariables(n, lb=0, ub=W_MAX, name="w")
    y = p.addVariables(n, vartype=xp.binary, name="y")

    # Human labels for the IIS report, keyed by row index. Group caps get theirs
    # from the group key (see below); the scalar constraints are labelled here,
    # because an IIS naming "R2155" instead of "budget" is not a diagnosis.
    ctr_labels = {}

    def label(added, kind):
        """`added` is a scalar constraint or a Series indexed by group key."""
        if hasattr(added, "items"):
            for key, ctr in added.items():
                ctr_labels[ctr.index] = f"{kind}={key}"
        else:
            ctr_labels[added.index] = kind

    p.addConstraint(w <= W_MAX * y)
    p.addConstraint(w >= W_MIN * y)
    label(p.addConstraint(xp.Sum(w) == 1), "budget_sum_w_eq_1")
    label(p.addConstraint(xp.Sum(y) >= MIN_STOCKS), f"min_stocks_ge_{MIN_STOCKS}")

    # --- group caps ---------------------------------------------------------
    # One addConstraint per grouping, using the Pandas idiom from FICO's own
    # portfolio_pandas.ipynb: groupby(key)["w"].sum() builds one constraint per
    # group. This replaces two hand-written np.unique loops and is a PROVABLY
    # identical rewrite, not a judgement call - both forms were written to LP
    # with problem.write() and the files are byte-identical (13 rows, 1077 cols,
    # 2154 elements). The variables have to sit in a Series of dtype "xpressobj"
    # for Pandas to aggregate them; that dtype needs Xpress >= 9.8.
    groups = pd.DataFrame({COL_REGION: region_arr, COL_SECTOR: sector_arr}, index=stocks)
    groups["w"] = pd.Series(w, index=stocks, dtype="xpressobj")

    # addConstraint returns a Series indexed by the group key, so the group
    # labels survive into the row indices. That is what makes an IIS report
    # readable ("country_cap=Switzerland") instead of "R412" - group caps built
    # by hand would need a name= on every constraint to get the same thing.
    label(p.addConstraint(groups.groupby(COL_REGION)["w"].sum() <= REGION_CAP), "region_cap")

    if ENABLE_ESG_CONSTRAINT:
        label(p.addConstraint(xp.Dot(esg_arr, w) >= ESG_MIN), f"esg_avg_ge_{ESG_MIN:g}")

    if ENABLE_SECTOR_CAP:
        label(p.addConstraint(groups.groupby(COL_SECTOR)["w"].sum() <= SECTOR_CAP), "sector_cap")

    # Country cap. Requires country= to be passed; when it is None the model is
    # exactly the model that produced the current results, whatever the flag says.
    if ENABLE_COUNTRY_CAP and country_arr is not None:
        capped = groups.assign(**{COL_COUNTRY: country_arr})
        capped = capped.loc[~capped[COL_COUNTRY].isin(COUNTRY_CAP_EXEMPT)]
        label(p.addConstraint(capped.groupby(COL_COUNTRY)["w"].sum() <= COUNTRY_CAP),
              "country_cap")

    if ENABLE_TIER1_EXCLUSION:
        t1_mask = np.isin(stocks_arr, TIER1_CONTROVERSIAL_TICKERS)
        if t1_mask.any():
            label(p.addConstraint(xp.Sum(w[t1_mask]) <= CONTROVERSIAL_CAP), "tier1_exclusion")
    if ENABLE_TIER2_EXCLUSION:
        t2_mask = np.isin(stocks_arr, TIER2_CONTROVERSIAL_TICKERS)
        if t2_mask.any():
            label(p.addConstraint(xp.Sum(w[t2_mask]) <= CONTROVERSIAL_CAP), "tier2_exclusion")

    portfolio_return_expr = xp.Dot(mu_arr, w)
    portfolio_var_expr = xp.Dot(w, Sigma_arr, w)

    if mode == "min_risk":
        assert target_return is not None
        label(p.addConstraint(portfolio_return_expr >= target_return),
                     f"return_floor_ge_{target_return:.4f}")
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
        label(p.addConstraint(portfolio_var_expr <= risk_cap ** 2),
                     f"risk_cap_le_{risk_cap:.4f}")
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

    if not result["feasible"] and solstatus == xp.SolStatus.INFEASIBLE:
        diag = diagnose_infeasible(p, labels=ctr_labels)
        result["iis"] = diag
        if verbose:
            print(diag["report"])

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
        if country_arr is not None:
            by_country = pd.Series(w_sol, index=country_arr).groupby(level=0).sum()
            for c, v in by_country.items():
                result[f"weight_country_{c}"] = float(v)
            non_exempt = by_country.drop(labels=[c for c in COUNTRY_CAP_EXEMPT
                                                 if c in by_country.index], errors="ignore")
            if len(non_exempt):
                result["max_country_weight"] = float(non_exempt.max())
                result["max_country"] = str(non_exempt.idxmax())
        result["weight_tier1_controversial"] = float(w_sol[np.isin(stocks_arr, TIER1_CONTROVERSIAL_TICKERS)].sum())
        result["weight_tier2_defense"] = float(w_sol[np.isin(stocks_arr, TIER2_CONTROVERSIAL_TICKERS)].sum())

    return result


# ============================================================
# 3. FEASIBILITY + SCALE CHECK
# ============================================================
def check_feasibility_and_scale(mu, Sigma, region, esg, sector, country=None):
    print("\n=== STEP 1: FEASIBILITY + SCALE CHECK (full universe) ===\n")

    print("--- (a) Global min-variance (no return constraint) ---")
    r_min = solve_model2(mu, Sigma, region, esg, sector, country=country,
                         mode="min_risk_only", time_limit=180)
    print(f"  status={r_min['solstatus']}  time={r_min['elapsed_sec']:.1f}s")
    if r_min["feasible"]:
        print(f"  return={r_min['portfolio_return']:.4f}  risk={r_min['portfolio_risk']:.4f}  "
              f"n_selected={r_min['n_selected']}  esg={r_min['esg_weighted']:.2f}")
    else:
        raise RuntimeError("INFEASIBLE even for pure min-variance! Check constraints/data.")

    print("\n--- (b) Pure max return (no risk constraint) ---")
    r_max = solve_model2(mu, Sigma, region, esg, sector, country=country,
                         mode="max_return_only", time_limit=180)
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
                        country=None,
                        n_points=N_FRONTIER_POINTS,
                        time_limit=TIME_LIMIT_SEC, mip_gap=MIP_GAP):

    beta_lo = r_min["portfolio_return"]
    beta_hi = r_max["portfolio_return"]
    betas = np.linspace(beta_lo, beta_hi, n_points)

    frontier = []
    for i, beta in enumerate(betas):
        print(f"\n[{i + 1}/{n_points}] target return beta = {beta:.4f}")
        res = solve_model2(mu, Sigma, region, esg, sector, country=country,
                            mode="min_risk", target_return=beta,
                            time_limit=time_limit, mip_gap=mip_gap, verbose=False)
        res["target_beta"] = beta
        frontier.append(res)
        status = "OK" if res["feasible"] else "INFEASIBLE"
        print(f"  -> {status}  ({res['elapsed_sec']:.1f}s)"
              + (f"  risk={res['portfolio_risk']:.4f}" if res["feasible"] else ""))

    return frontier


# ============================================================
# 5. RISK PROFILE AS A MANDATE (lexicographic, without multi-objective)
# ============================================================
def solve_mandate(mu, Sigma, region, esg, sector, country=None,
                  reltol=0.10, time_limit=TIME_LIMIT_SEC, mip_gap=MIP_GAP,
                  verbose=False):
    """A risk profile stated as a mandate instead of picked off a grid.

    "Maximise return, then minimise risk while giving up at most `reltol` of
    the maximum attainable return." That is the lexicographic idea from FICO's
    markowitz_multiobj.ipynb, and it is how an investment mandate is actually
    written - whereas the three profiles in analyze_risk.py are chosen post hoc
    with idxmin/idxmax/idxmax(sharpe) over 15 sampled frontier points, so each
    one is the best of 15 rather than the true optimum.

    Xpress' NATIVE multi-objective machinery is not used here, and the reason
    is measured rather than assumed. addObjective/setObjective(priority=...)
    require every objective to be LINEAR, so the variance has to move into a
    transfer variable:  Dot(w,Sigma,w) - variance <= 0. On this problem that
    turns a convex MIQP into a quadratically CONSTRAINED MIP:

        quadratic in objective:   qelems 1,159,929 | qconstraints 0
        quadratic in constraint:  qcelems  580,503 | qconstraints 1

    The second form did not finish a single solve in over two minutes, against
    roughly 1s for the first. The notebook's example has 5 assets, where the
    distinction does not show up.

    Two ordinary MIQP solves give identical semantics and keep the quadratic in
    the objective, where Xpress wants it:
        1. max return, unconstrained     -> R*
        2. min risk s.t. return >= (1 - reltol) * R*

    reltol=0 reproduces the max-return corner; reltol=1 the global min-variance
    portfolio. Returns a dict shaped like solve_model2's, plus the mandate terms.
    """
    kw = dict(country=country, time_limit=time_limit, mip_gap=mip_gap, verbose=verbose)

    stage1 = solve_model2(mu, Sigma, region, esg, sector, mode="max_return_only", **kw)
    if not stage1["feasible"]:
        return {"feasible": False, "stage": 1, "reltol": reltol,
                "solstatus": stage1["solstatus"], "iis": stage1.get("iis")}

    r_star = stage1["portfolio_return"]
    floor = (1.0 - reltol) * r_star

    stage2 = solve_model2(mu, Sigma, region, esg, sector, mode="min_risk",
                          target_return=floor, **kw)
    if not stage2["feasible"]:
        return {"feasible": False, "stage": 2, "reltol": reltol,
                "return_floor": floor, "max_return": r_star,
                "solstatus": stage2["solstatus"], "iis": stage2.get("iis")}

    out = dict(stage2)
    out.update({"mode": "mandate", "reltol": reltol,
                "max_return": r_star, "return_floor": floor,
                "return_given_up_pp": (r_star - stage2["portfolio_return"]) * 100,
                "elapsed_sec": stage1["elapsed_sec"] + stage2["elapsed_sec"]})
    return out


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    mu, Sigma, region, esg, sector, country = load_data(return_country=True)
    r_min, r_max = check_feasibility_and_scale(mu, Sigma, region, esg, sector, country=country)

    print("\nTop 10 holdings - min-variance portfolio:")
    print(r_min["weights"].sort_values(ascending=False).head(10))

    print("\nTop 10 holdings - max-return portfolio:")
    print(r_max["weights"].sort_values(ascending=False).head(10))

    if RUN_FULL_SWEEP:
        frontier = efficient_frontier(mu, Sigma, region, esg, sector, r_min, r_max,
                                      country=country)
        rows = [{k: v for k, v in r.items() if k != "weights"} for r in frontier]
        tag = scenario_tag()
        os.makedirs(RESULTS_DIR, exist_ok=True)
        pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, f"efficient_frontier_model2_{tag}.csv"), index=False)
        print(f"\nSaved efficient_frontier_model2_{tag}.csv")

        weights_df = pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(frontier) if r["feasible"]})
        weights_df.to_csv(os.path.join(RESULTS_DIR, f"efficient_frontier_weights_{tag}.csv"))
        print(f"Saved efficient_frontier_weights_{tag}.csv")
    else:
        print("\nRUN_FULL_SWEEP=False -> only the feasibility+scale check ran.")