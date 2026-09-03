"""
Build the Power BI facing layer of dashboard_data/.

The raw per-study mirrors built by build_dashboard_data.py stay exactly where
they are, for audit. This adds the clean, normalised, consistently-typed tables
a BI tool should actually load, and then VALIDATES them.

CONVENTIONS, applied everywhere in this layer
---------------------------------------------
* every percentage-like value is a DECIMAL: 0.142995 means 14.2995%. Column
  names carry no `_%` suffix. No percentage strings anywhere.
* ESG stays on its own 0-100 scale, because it is not a percentage.
* `profile` is exactly one of: Risk Averse | Neutral | Risk Prone.
  `profile_rule` says how it was selected. `frontier_point` traces it back.
* `strategy` names a backtested strategy, e.g. "Optimised Minimum Variance",
  "1/N Equal Weight".
* long format over wide: one row per (key..., value), never one column per date
  or per frontier point.
* no `Unnamed: 0`. Every index column is named for what it holds.
* every table carries the identifiers needed to read a row on its own. No
  filename context required.

CANONICAL PROFILE RULE
----------------------
Resolved from the frozen archive/our_model_frozen/19_freeze_v4.py, not invented:
Risk Averse = min variance, Neutral = max return/risk, Risk Prone = max return
among NON-DEGENERATE points, where degenerate means top-3 weight > 40% or more
than 15 positions on the 1% floor. On the delivered frontier: points 0, 8, 11.
`31_scenario_grid.py` derives this per scenario; this script only consumes it.

Run:  python3 dashboard_data/build_powerbi_layer.py       # ~10 s, no solver
      (run 31_scenario_grid.py first if scenarios/ is missing)
"""

import os
import shutil
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BUDGET = 100_000_000
PCT_TOL = 1e-6

# folders this script owns and therefore clears before rebuilding, so a source
# that disappears cannot leave a stale destination behind (issue 17)
OWNED = ["universe", "backtest_standard", "stress_standard", "benchmark_standard"]

STRATEGY_NAMES = {
    "minvar": "Optimised Minimum Variance",
    "optimised": "Optimised Minimum Variance",
    "mandate20": "Optimised Mandate (give up <=20% of max return)",
    "mandate10": "Optimised Mandate (give up <=10% of max return)",
    "equal_weight": "1/N Equal Weight",
    # script 21 labels its own summary rows in prose; map them too (issue 13)
    "Model 2 (min-variance)": "Optimised Minimum Variance",
    "Model 2": "Optimised Minimum Variance",
    "1/N benchmark": "1/N Equal Weight",
    "1N_all_monthly": "1/N Equal Weight (all stocks, monthly)",
    "1N_model_monthly": "1/N Equal Weight (model universe, monthly)",
    "1N_esg70_monthly": "1/N Equal Weight (ESG>=70, monthly)",
    "1N_all_daily": "1/N Equal Weight (all stocks, daily)",
    "1N_model_buyhold": "1/N Equal Weight (model universe, buy and hold)",
}
PROFILE_NAMES = {
    "risk_averse": "Risk Averse", "risk-averse": "Risk Averse",
    "Risk Averse": "Risk Averse", "Risk Averse (min risk)": "Risk Averse",
    "neutral": "Neutral", "Neutral": "Neutral",
    "Neutral (max Sharpe = return/risk)": "Neutral",
    "risk_prone": "Risk Prone", "risk-prone": "Risk Prone",
    "Risk Prone": "Risk Prone", "Risk Prone (max return)": "Risk Prone",
}
PROFILE_RULES = {
    "Risk Averse": "Minimum variance",
    "Neutral": "Maximum return/risk ratio",
    "Risk Prone": "Highest non-degenerate return",
}


def to_decimal(df, cols):
    """Divide the named columns by 100 and drop the _% / _pp suffix."""
    out = df.copy()
    ren = {}
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce") / 100.0
            ren[c] = c.replace("_%", "").replace("_pp", "")
    return out.rename(columns=ren)


def pct_cols(df):
    return [c for c in df.columns if c.endswith("_%") or c.endswith("_pp")]


def read(rel, **kw):
    return pd.read_csv(os.path.join(ROOT, rel), **kw)


# ===========================================================================
# 1. the stock dimension
# ===========================================================================
def build_universe():
    """One row per stock: every dimension a slicer might need.

    INDUSTRY: taken from the LSEG export (TR.GICSIndustryGroup, 25 groups, all
    1093 tickers, no gaps), parsed by 27_lseg_esg_sector_update.py. It is a
    DISPLAY dimension only - the model still optimises on the current sector
    taxonomy, and adding industry here changes no optimisation. Both the
    current sector and the LSEG GICS sector are exposed so a slicer can use
    either without implying the model switched.
    """
    shares = read("shares_imputed.csv").set_index("Stock")
    sector = read("sectors.xlsx".replace(".xlsx", ".xlsx")) if False else \
        pd.read_excel(os.path.join(ROOT, "sectors.xlsx")).set_index("Stock")["Sector"]
    mu = read("expected_return_v4.csv").set_index("Stock")["expected_return"]
    sd = read("per_stock_risk_v4.csv").set_index("Stock")["risk_std"]
    cov_cols = read("covariance_matrix_v4.csv", nrows=0).columns.tolist()[1:]

    gics_path = os.path.join(ROOT, "data_lseg_update", "sectors_gics.xlsx")
    have_industry = os.path.exists(gics_path)
    if have_industry:
        g = pd.read_excel(gics_path).set_index("Stock")
    else:
        g = None

    u = pd.DataFrame(index=shares.index)
    u.index.name = "stock"
    u["region"] = shares["Region"]
    u["country"] = shares["Country"]
    u["sector"] = sector.reindex(u.index).fillna("Unknown")
    if have_industry:
        u["industry"] = g["IndustryGroup"].reindex(u.index)
        u["sector_gics"] = g["Sector"].reindex(u.index)
    u["esg"] = shares["ESG score"]                        # 0-100, not a percentage
    u["esg_band"] = pd.cut(u["esg"], [0, 30, 50, 60, 70, 80, 100],
                           labels=["<30", "30-50", "50-60", "60-70", "70-80", "80+"],
                           right=False).astype(str)
    u["expected_return"] = mu.reindex(u.index)            # decimal already
    u["risk_std"] = sd.reindex(u.index)                   # decimal already
    u["has_price_data"] = u.index.isin(cov_cols)
    u["passes_esg_floor_30"] = u["esg"] >= 30.0
    u["in_model_universe"] = u["has_price_data"] & u["passes_esg_floor_30"]
    u["esg_ge_70"] = u["esg"] >= 70.0
    return u.sort_index(), have_industry


# ===========================================================================
# 2. backtests, standardised
# ===========================================================================
def build_backtests(out):
    rows_sum, rows_curve, rows_sub, rows_diag = [], [], [], []

    SOURCES = [
        # (label of the run, folder, book->column mapping present in that run)
        ("walk-forward min-variance (script 21)", "results_chloe/backtest",
         {"optimised": "optimised", "equal_weight": "equal_weight"},
         "backtest_summary.csv", "backtest_equity_curves.csv",
         "backtest_subperiods.csv", "backtest_diagnostics.csv"),
        ("walk-forward profiles (script 26)", "backtest_profiles/results",
         {"minvar": "minvar", "mandate20": "mandate20",
          "mandate10": "mandate10", "equal_weight": "equal_weight"},
         "summary.csv", "equity_curves.csv", "subperiods.csv", "diagnostics.csv"),
    ]

    for run, folder, books, fsum, fcurve, fsub, fdiag in SOURCES:
        p = os.path.join(ROOT, folder)
        if not os.path.exists(os.path.join(p, fsum)):
            continue
        S = pd.read_csv(os.path.join(p, fsum), index_col=0)
        S.index.name = "book"
        for book, r in S.iterrows():
            # "Model 2 after 10bp costs" / "minvar after 10bp" -> the book itself
            base = str(book).split(" after ")[0].strip()
            strat = STRATEGY_NAMES.get(base)
            if strat is None:
                raise SystemExit(f"unmapped strategy label {base!r} in {folder}/{fsum} - "
                                 "add it to STRATEGY_NAMES rather than letting a raw "
                                 "label reach the dashboard (issue 13)")
            rows_sum.append({
                "run": run, "book": base, "strategy": strat,
                "cost_adjusted": " after " in str(book),
                "cagr": float(r["CAGR_%"]) / 100, "volatility": float(r["vol_%"]) / 100,
                "sharpe": float(r["Sharpe"]),
                "max_drawdown": float(r["maxDD_%"]) / 100,
                "final_multiple": float(r["final_x"]),
            })

        C = pd.read_csv(os.path.join(p, fcurve), index_col=0, parse_dates=True)
        C.index.name = "date"
        for book in C.columns:
            if book not in STRATEGY_NAMES:
                raise SystemExit(f"unmapped strategy column {book!r} in {folder}/{fcurve}")
            for d, v in C[book].items():
                rows_curve.append({"run": run, "book": book,
                                   "strategy": STRATEGY_NAMES[book],
                                   "date": d.date(), "indexed_wealth": float(v)})

        if os.path.exists(os.path.join(p, fsub)):
            B = pd.read_csv(os.path.join(p, fsub))
            for _, r in B.iterrows():
                for book in books:
                    got = {}
                    for metric, suffix in (("cagr", "CAGR_%"), ("volatility", "vol_%"),
                                           ("max_drawdown", "maxDD_%")):
                        for cand in (f"{book}_{suffix}",
                                     f"opt_{suffix}" if book in ("optimised", "minvar") else None,
                                     f"eq_{suffix}" if book == "equal_weight" else None):
                            if cand and cand in B.columns:
                                got[metric] = float(r[cand]) / 100
                                break
                    if got:
                        rows_sub.append({"run": run, "book": book,
                                         "strategy": STRATEGY_NAMES.get(book, book),
                                         "period": r["period"], "regime": r["regime"],
                                         **got})

        if os.path.exists(os.path.join(p, fdiag)):
            D = pd.read_csv(os.path.join(p, fdiag))
            for _, r in D.iterrows():
                m = str(r["metric"])
                is_pct = "_%" in m or m.endswith("%")
                rows_diag.append({"run": run, "metric": m.replace("_%", ""),
                                  "value": float(r["value"]) / 100 if is_pct else float(r["value"]),
                                  "is_decimal_fraction": bool(is_pct)})

    pd.DataFrame(rows_sum).to_csv(f"{out}/summary.csv", index=False)
    pd.DataFrame(rows_curve).to_csv(f"{out}/equity_curves.csv", index=False)
    pd.DataFrame(rows_sub).to_csv(f"{out}/subperiods.csv", index=False)
    pd.DataFrame(rows_diag).to_csv(f"{out}/diagnostics.csv", index=False)
    return len(rows_sum), len(rows_curve)


# ===========================================================================
# 3. stress test, standardised, with explicit identifiers
# ===========================================================================
def build_stress(out):
    src = os.path.join(ROOT, "stress_test", "results")
    if not os.path.exists(src):
        return 0

    A = pd.read_csv(os.path.join(src, "panelA_windows.csv"))
    A["panel"] = "A (in-sample, descriptive)"
    A["profile"] = A["book"].map(lambda b: PROFILE_NAMES.get(b, STRATEGY_NAMES.get(b, b)))
    A["profile_rule"] = A["profile"].map(PROFILE_RULES).fillna("benchmark")
    A = to_decimal(A, pct_cols(A))
    A.to_csv(f"{out}/panelA_windows.csv", index=False)

    B = pd.read_csv(os.path.join(src, "panelB_windows.csv"))
    B["panel"] = "B (point-in-time, the actual test)"
    B["profile"] = B["book"].map(lambda b: PROFILE_NAMES.get(b, STRATEGY_NAMES.get(b, b)))
    B["profile_rule"] = B["profile"].map(PROFILE_RULES).fillna("benchmark")
    B = to_decimal(B, pct_cols(B))
    B.to_csv(f"{out}/panelB_windows.csv", index=False)

    # panelB holdings: the source file stores the top names as a pipe-joined
    # STRING, which cannot drive an allocation visual. Exploded to long here;
    # full weights need 25b (see README).
    P = pd.read_csv(os.path.join(src, "panelB_portfolios.csv"))
    rows = []
    for _, r in P.iterrows():
        names = str(r.get("holdings", "")).split("|") if pd.notna(r.get("holdings")) else []
        for rank, s in enumerate([x for x in names if x], start=1):
            rows.append({"window": r["window"],
                         "profile": PROFILE_NAMES.get(r["book"], r["book"]),
                         "cap": r["cap"], "stock": s, "rank": rank,
                         "solstatus": r.get("solstatus"),
                         "weight": np.nan,
                         "note": "top-8 names only; weights not in the source file"})
    pd.DataFrame(rows).to_csv(f"{out}/panelB_top_names.csv", index=False)
    Pd_ = to_decimal(P, pct_cols(P))
    Pd_["profile"] = Pd_["book"].map(lambda b: PROFILE_NAMES.get(b, b))
    Pd_.to_csv(f"{out}/panelB_portfolios.csv", index=False)

    # issue 15: these two carried no portfolio identifier at all
    C = pd.read_csv(os.path.join(src, "drawdown_attribution.csv"))
    C = C.rename(columns={C.columns[0]: "stock"})
    C.insert(1, "profile", "Neutral")
    C.insert(2, "profile_rule", PROFILE_RULES["Neutral"])
    C.insert(3, "window", "2020 COVID crash")
    C = to_decimal(C, pct_cols(C))
    C.to_csv(f"{out}/covid_attribution.csv", index=False)

    W = pd.read_csv(os.path.join(src, "worst_windows.csv"))
    W.insert(0, "profile", "Neutral")
    W.insert(1, "profile_rule", PROFILE_RULES["Neutral"])
    W.insert(2, "lookback_trading_days", 60)
    W = to_decimal(W, pct_cols(W))
    W.to_csv(f"{out}/worst_windows.csv", index=False)
    return 5


# ===========================================================================
# 4. the 1/N benchmark, standardised
# ===========================================================================
def build_benchmark(out):
    src = os.path.join(ROOT, "benchmark_1n", "results")
    if not os.path.exists(src):
        return 0

    S = pd.read_csv(os.path.join(src, "summary.csv"), index_col=0)
    S.index.name = "series_id"
    S = S.reset_index()
    S.insert(1, "strategy", S["series_id"].map(lambda k: STRATEGY_NAMES.get(k, k)))
    S = to_decimal(S, pct_cols(S))
    S.to_csv(f"{out}/summary.csv", index=False)

    C = pd.read_csv(os.path.join(src, "curves.csv"), index_col=0, parse_dates=True)
    C.index.name = "date"
    rows = []
    for k in C.columns:
        for d, v in C[k].items():
            rows.append({"series_id": k, "strategy": STRATEGY_NAMES.get(k, k),
                         "date": d.date(), "indexed_wealth": float(v)})
    pd.DataFrame(rows).to_csv(f"{out}/curves.csv", index=False)

    A = pd.read_csv(os.path.join(src, "annual.csv"))
    A = A.melt(id_vars="year", var_name="series_id", value_name="calendar_return")
    A["calendar_return"] = A["calendar_return"] / 100.0
    A.insert(1, "strategy", A["series_id"].map(lambda k: STRATEGY_NAMES.get(k, k)))
    A.to_csv(f"{out}/annual.csv", index=False)

    W = pd.read_csv(os.path.join(src, "windows.csv"))
    W.insert(1, "strategy", W["series"].map(lambda k: STRATEGY_NAMES.get(k, k)))
    W = to_decimal(W, pct_cols(W))
    W.to_csv(f"{out}/windows.csv", index=False)

    F = pd.read_csv(os.path.join(src, "feasibility.csv"))
    F.insert(1, "strategy", F["series"].map(lambda k: STRATEGY_NAMES.get(k, k)))
    F = to_decimal(F, [c for c in pct_cols(F) if c != "weighted_esg"])
    F.to_csv(f"{out}/feasibility.csv", index=False)
    return 5


# ===========================================================================
# 5. validation (issue 17)
# ===========================================================================
def validate(u, have_industry):
    fails, warns = [], []

    def check(cond, msg):
        (fails if not cond else warns).append(msg) if not cond else None

    # the stock dimension
    if len(u) != 1093:
        fails.append(f"universe has {len(u)} rows, expected 1093")
    if int(u["in_model_universe"].sum()) != 1077:
        fails.append(f"model universe is {int(u['in_model_universe'].sum())}, expected 1077")
    if u.index.duplicated().any():
        fails.append("duplicate stock keys in universe")
    if have_industry and u["industry"].isna().any():
        fails.append(f"{int(u['industry'].isna().sum())} stocks with no industry")

    # the scenario layer
    sc = os.path.join(HERE, "scenarios")
    if os.path.exists(os.path.join(sc, "portfolio_holdings.csv")):
        H = pd.read_csv(os.path.join(sc, "portfolio_holdings.csv"))
        P = pd.read_csv(os.path.join(sc, "portfolio_summary.csv"))
        FP = pd.read_csv(os.path.join(sc, "frontier_points.csv"))
        FW = pd.read_csv(os.path.join(sc, "frontier_weights.csv"))

        bad = set(H["profile"]) - set(PROFILE_RULES)
        if bad:
            fails.append(f"non-canonical profile names in holdings: {bad}")
        sums = H.groupby(["scenario_id", "profile"])["weight"].sum()
        off = sums[(sums - 1.0).abs() > 1e-3]
        if len(off):
            fails.append(f"{len(off)} portfolio(s) whose weights do not sum to 1: "
                         f"{off.round(4).to_dict()}")
        fws = FW.groupby(["scenario_id", "frontier_point"])["weight"].sum()
        offf = fws[(fws - 1.0).abs() > 1e-3]
        if len(offf):
            fails.append(f"{len(offf)} frontier point(s) whose weights do not sum to 1")
        if H.duplicated(["scenario_id", "profile", "stock"]).any():
            fails.append("duplicate (scenario, profile, stock) keys in holdings")
        if FW.duplicated(["scenario_id", "frontier_point", "stock"]).any():
            fails.append("duplicate (scenario, point, stock) keys in frontier weights")
        n_pts = FP.groupby("scenario_id")["frontier_point"].nunique()
        if (n_pts != 15).any():
            warns.append(f"scenarios without 15 frontier points: "
                         f"{n_pts[n_pts != 15].to_dict()}")
        unknown = set(H["stock"]) - set(u.index)
        if unknown:
            fails.append(f"{len(unknown)} held stocks missing from the universe table")
        # every profile must trace to a real frontier point of its own scenario
        key = set(zip(FP.scenario_id, FP.frontier_point))
        orphan = [(r.scenario_id, r.frontier_point) for r in P.itertuples()
                  if (r.scenario_id, r.frontier_point) not in key]
        if orphan:
            fails.append(f"{len(orphan)} summary rows point at a nonexistent frontier point")
    else:
        warns.append("scenarios/ not built yet - run 31_scenario_grid.py")

    # units: nothing in this layer may be a percentage string or a _% column
    for dp, _, fs in os.walk(HERE):
        if os.path.basename(dp) in ("scenarios", *OWNED):
            for f in fs:
                if not f.endswith(".csv"):
                    continue
                head = pd.read_csv(os.path.join(dp, f), nrows=3)
                bad_cols = [c for c in head.columns if c.endswith("_%") or c.endswith("_pp")]
                if bad_cols:
                    fails.append(f"{os.path.relpath(os.path.join(dp, f), HERE)}: "
                                 f"percentage-suffixed columns {bad_cols}")
                for c in head.columns:
                    if head[c].dtype == object and \
                       head[c].astype(str).str.contains("%", na=False).any():
                        fails.append(f"{os.path.relpath(os.path.join(dp, f), HERE)}: "
                                     f"column {c} contains percentage strings")
                if head.columns[0].startswith("Unnamed"):
                    fails.append(f"{os.path.relpath(os.path.join(dp, f), HERE)}: "
                                 "unnamed index column")
    return fails, warns


def main():
    for d in OWNED:
        p = os.path.join(HERE, d)
        if os.path.exists(p):
            shutil.rmtree(p)          # issue 17: no stale destinations
        os.makedirs(p, exist_ok=True)

    u, have_industry = build_universe()
    u.to_csv(os.path.join(HERE, "universe", "stocks.csv"))
    print(f"universe/stocks.csv   {len(u)} stocks | "
          f"{int(u['in_model_universe'].sum())} in the model universe | "
          f"industry: {'LSEG GICS Industry Group, ' + str(u['industry'].nunique()) + ' groups' if have_industry else 'NOT AVAILABLE'}")

    n_sum, n_curve = build_backtests(os.path.join(HERE, "backtest_standard"))
    print(f"backtest_standard/    {n_sum} summary rows | {n_curve} curve rows")
    print(f"stress_standard/      {build_stress(os.path.join(HERE, 'stress_standard'))} tables")
    print(f"benchmark_standard/   {build_benchmark(os.path.join(HERE, 'benchmark_standard'))} tables")

    fails, warns = validate(u, have_industry)
    print("\n--- validation ---")
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    if not fails:
        print("  all checks passed")
    else:
        raise SystemExit(f"\n{len(fails)} validation failure(s) - the layer is not clean")


if __name__ == "__main__":
    main()
