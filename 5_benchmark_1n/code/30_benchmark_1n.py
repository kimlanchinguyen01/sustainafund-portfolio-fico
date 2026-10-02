"""
SustainaFund — 30: the 1/N benchmark over the FULL study period
================================================================
WHY THIS EXISTS
1/N already appears twice in the repo, and both times it is narrower than we
need:

  * `4_backtest/code/21_backtest_walkforward.py` and `4_backtest/` compute it
    over the eligible universe at each rebalance, but only from 2018-04 - the
    walk-forward cannot start earlier because it needs three years of history
    first. That is 7.7 of the 11 years.
  * `6_stress_test/` holds a fixed 1/N from 2015 but reports it only for the
    crisis windows.

Neither gives a reference series for the whole study period the brief defines
("ten years of daily prices (2015-2025)"). This builds one, so any result -
static frontier, crisis window, calendar year - can be quoted against a
consistently-constructed naive benchmark.

No solver. Pure arithmetic on prices, ~20 s.

FIVE SERIES, because "1/N" is not one thing
-------------------------------------------
    1N_all_monthly      every stock with a price, rebalanced to equal weight
                        monthly, drifting in between
    1N_model_monthly    restricted to the 1077-stock MODEL universe (the ESG
                        floor of 30 applied), monthly  <-- PRIMARY COMPARATOR,
                        because it isolates the optimiser rather than the
                        universe, which is the comparison we actually make
    1N_esg70_monthly    only the 506 stocks with individual ESG >= 70, monthly -
                        the naive portfolio an ESG mandate could defend
    1N_all_daily        equal weight re-set every day: an equal-weight INDEX
    1N_model_buyhold    equal weight set once at the start and never touched,
                        so the value of rebalancing is visible as the gap to
                        1N_model_monthly

HANDLING ENTRIES, which matters more than it looks
--------------------------------------------------
"Complete history" is not a usable filter here. Over the full file only 59
stocks have no missing value at all, because 2015-01-01 is a holiday on which
almost nothing traded and a forward-fill only fills AFTER a stock's first
price. Over the model's 10-year window (from 2015-12-31) the same test gives
991. Requiring completeness would therefore either throw away 95% of the
universe or silently change the period.

Instead: on each day a stock is included if it has a return that day, i.e. a
price today and on the previous observation. 118 stocks list after January 2015
and simply enter when they appear. That is what an equal-weight index does, and
it needs no arbitrary cutoff.

1/N IS NOT A FEASIBLE PORTFOLIO UNDER THE BRIEF
-----------------------------------------------
Worth stating before anyone compares them as alternatives. Equal weight over
1077 names puts 0.093% in each, against the brief's 1% per-stock floor, and its
weighted ESG is 67.5 against the required 70. No equal-weight portfolio over
more than 100 names can satisfy the 1% floor at all. So 1/N is a BENCHMARK - a
reference for what no skill would have earned - not a portfolio we could have
proposed. `feasibility.csv` records exactly which conditions each series breaks.

Outputs (5_benchmark_1n/results/):
    curves.csv        daily levels of all five series, indexed to 1.0
    summary.csv       full-period CAGR, vol, Sharpe, maxDD, final multiple
    annual.csv        calendar-year returns per series
    windows.csv       the crisis windows used in 6_stress_test/, per series
    gate_vs_script21.csv  agreement with the 1/N script 21 built independently
    feasibility.csv   which of the brief's conditions each series violates
    universe.csv      how many names each series holds over time

Run:  python3 5_benchmark_1n/code/30_benchmark_1n.py

Needs 1_data_preparation/results/prices_div_usd.csv (52 MB, gitignored) - the same USD,
dividend-adjusted prices mu and Sigma are built from. Rebuild it with
1_data_preparation/code/20_dividend_adjusted_pipeline.py or ask Chloe.
"""

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)                    # <repo>/<part>
ROOT = os.path.dirname(PART)                    # <repo>

PRICES = os.path.join(ROOT, "1_data_preparation", "results", "prices_div_usd.csv")
SHARES = os.path.join(ROOT, "2_optimisation_model", "data", "shares_imputed.csv")
SECTORS = os.path.join(ROOT, "2_optimisation_model", "data", "sectors.xlsx")
OUTDIR = os.path.join(PART, "results")

TD = 252
ESG_FLOOR = 30.0          # the model's per-stock floor
ESG_MIN = 70.0            # the brief's weighted-average requirement
W_MIN, W_MAX = 0.01, 0.20  # the brief's per-stock bounds
REGION_CAP = 0.60         # the brief
MIN_STOCKS = 30           # the brief

# Same windows as 6_stress_test/, so the two are quotable side by side.
WINDOWS = [
    ("2015 China devaluation", "2015-08-10", "2015-09-29"),
    ("2016 Brexit vote",       "2016-06-23", "2016-07-15"),
    ("2018 Q4 selloff",        "2018-09-20", "2018-12-24"),
    ("2020 COVID crash",       "2020-02-19", "2020-03-23"),
    ("2020 crash + recovery",  "2020-02-19", "2020-08-31"),
    ("2022 inflation shock",   "2022-01-03", "2022-10-12"),
]

os.makedirs(OUTDIR, exist_ok=True)


def load():
    if not os.path.exists(PRICES):
        sys.exit(f"missing input: {PRICES}\n"
                 "It is gitignored (52 MB). Rebuild it with\n"
                 "  cd pipeline && python3 20_dividend_adjusted_pipeline.py\n"
                 "or ask Chloe for the export.")
    px = pd.read_csv(PRICES, index_col=0)
    px.columns = pd.to_datetime(px.columns)
    sh = pd.read_csv(SHARES).set_index("Stock")
    sec = pd.read_excel(SECTORS).set_index("Stock")["Sector"]
    common = [s for s in px.index if s in sh.index]
    px = px.loc[common]
    print(f"prices {px.shape} | {px.columns.min().date()} .. {px.columns.max().date()}")
    return px, sh.loc[common], sec.reindex(common).fillna("Unknown")


def equal_weight_curve(simple, members, freq):
    """Equal weight over whichever members have a return that day.

    freq='D'    weights re-set daily (an equal-weight index)
    freq='ME'   re-set at each month end, drifting in between
    freq=None   set once at the first day, never again (buy and hold)

    Returns (levels indexed to 1.0, number of names held each day).
    """
    R = simple.loc[[s for s in members if s in simple.index]]
    avail = R.notna()

    if freq == "D":
        daily = (R.where(avail)).mean(axis=0, skipna=True).fillna(0.0)
        n_held = avail.sum(axis=0)
        return (1.0 + daily).cumprod(), n_held

    # rebalance dates: the last trading day in each period, plus the first day
    cols = R.columns
    if freq is None:
        marks = [cols[0]]
    else:
        marks = sorted({cols[cols.searchsorted(d, "right") - 1]
                        for d in pd.date_range(cols.min(), cols.max(), freq=freq)})
        marks = [cols[0]] + [m for m in marks if m > cols[0]]

    level, out, n_out = 1.0, {}, {}
    for i, start in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else cols[-1]
        seg = cols[(cols > start) & (cols <= end)] if i + 1 < len(marks) \
            else cols[cols > start]
        if not len(seg):
            continue
        # members that can actually be bought at this rebalance
        live = [s for s in R.index if avail.loc[s, start] or avail.loc[s, seg[0]]]
        if len(live) < 2:
            continue
        w = np.full(len(live), 1.0 / len(live))
        sub = R.loc[live, seg].fillna(0.0)
        growth = (1.0 + sub).cumprod(axis=1)
        pv = (growth.T * w).sum(axis=1)
        for d, v in pv.items():
            out[d] = level * v
            n_out[d] = len(live)
        level = out[seg[-1]]
    s = pd.Series(out).sort_index()
    s.loc[cols[0]] = 1.0
    return s.sort_index(), pd.Series(n_out).sort_index()


def stats(s):
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    tot = s.iloc[-1] / s.iloc[0]
    cagr = tot ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(TD)
    return {"years": round(yrs, 2), "CAGR_%": cagr * 100, "vol_%": vol * 100,
            "Sharpe": cagr / vol if vol else np.nan,
            "maxDD_%": float((s / s.cummax() - 1).min()) * 100,
            "final_x": tot,
            "best_day_%": float(r.max()) * 100, "worst_day_%": float(r.min()) * 100}


def feasibility(members, sh, sec, label):
    """Does this equal-weight portfolio satisfy the brief's four conditions?"""
    m = [s for s in members if s in sh.index]
    n = len(m)
    w = 1.0 / n
    esg_w = float(sh.loc[m, "ESG score"].mean())
    reg = sh.loc[m, "Region"].value_counts(normalize=True).max()
    secmax = sec.reindex(m).value_counts(normalize=True).max()
    return {
        "series": label, "n_stocks": n, "weight_each_%": w * 100,
        "min_weight_ok": bool(w >= W_MIN),
        "max_weight_ok": bool(w <= W_MAX),
        "min_stocks_ok": bool(n >= MIN_STOCKS),
        "region_ok": bool(reg <= REGION_CAP), "region_max_%": float(reg) * 100,
        "weighted_esg": esg_w, "esg_ok": bool(esg_w >= ESG_MIN),
        "sector_max_%": float(secmax) * 100,
        "admissible": bool(w >= W_MIN and n >= MIN_STOCKS
                           and reg <= REGION_CAP and esg_w >= ESG_MIN),
    }


def main():
    px, sh, sec = load()
    simple = px.pct_change(axis=1).iloc[:, 1:]

    all_stocks = list(px.index)
    model_universe = [s for s in all_stocks if sh.loc[s, "ESG score"] >= ESG_FLOOR]
    esg70 = [s for s in all_stocks if sh.loc[s, "ESG score"] >= ESG_MIN]
    print(f"all {len(all_stocks)} | model universe (ESG >= {ESG_FLOOR:g}) "
          f"{len(model_universe)} | ESG >= {ESG_MIN:g} {len(esg70)}")

    SERIES = [
        ("1N_all_monthly",    all_stocks,      "ME"),
        ("1N_model_monthly",  model_universe,  "ME"),
        ("1N_esg70_monthly",  esg70,           "ME"),
        ("1N_all_daily",      all_stocks,      "D"),
        ("1N_model_buyhold",  model_universe,  None),
    ]

    curves, counts, feas = {}, {}, []
    for label, members, freq in SERIES:
        c, n = equal_weight_curve(simple, members, freq)
        curves[label] = c
        counts[label] = n
        feas.append(feasibility(members, sh, sec, label))
        print(f"  {label:20s} {len(c)} days | final {c.iloc[-1]:.3f}x | "
              f"names {int(n.min())}..{int(n.max())}")

    C = pd.DataFrame(curves).sort_index()
    C.index.name = "date"
    C.to_csv(f"{OUTDIR}/curves.csv")
    pd.DataFrame(counts).sort_index().to_csv(f"{OUTDIR}/universe.csv")

    S = pd.DataFrame({k: stats(v.dropna()) for k, v in curves.items()}).T
    S.to_csv(f"{OUTDIR}/summary.csv")

    F = pd.DataFrame(feas)
    F.to_csv(f"{OUTDIR}/feasibility.csv", index=False)

    ann = {}
    for k, v in curves.items():
        v = v.dropna()
        ann[k] = v.groupby(v.index.year).apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    A = pd.DataFrame(ann)
    A.index.name = "year"
    A.to_csv(f"{OUTDIR}/annual.csv")

    rows = []
    for label, d0, d1 in WINDOWS:
        for k, v in curves.items():
            v = v.dropna()
            seg = v.loc[(v.index >= d0) & (v.index <= d1)]
            if len(seg) < 3:
                continue
            rows.append({"window": label, "series": k,
                         "from": seg.index[0].date(), "to": seg.index[-1].date(),
                         "ret_%": (seg.iloc[-1] / seg.iloc[0] - 1) * 100,
                         "maxDD_%": float((seg / seg.cummax() - 1).min()) * 100,
                         "vol_%": float(seg.pct_change().std() * np.sqrt(TD)) * 100})
    W = pd.DataFrame(rows)
    W.to_csv(f"{OUTDIR}/windows.csv", index=False)

    print("\n" + "=" * 104)
    print(f"1/N OVER THE FULL STUDY PERIOD  {C.index.min().date()} .. {C.index.max().date()}")
    print("=" * 104)
    print(S.to_string(float_format=lambda v: f"{v:.3f}"))

    print("\n--- is any of them admissible under the brief? ---")
    print(F[["series", "n_stocks", "weight_each_%", "min_weight_ok",
             "weighted_esg", "esg_ok", "region_max_%", "region_ok",
             "admissible"]].to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    print("\n--- calendar-year returns, % ---")
    print(A.to_string(float_format=lambda v: f"{v:+.2f}"))

    print("\n--- crisis windows (primary series) ---")
    prim = W[W.series == "1N_model_monthly"]
    print(prim[["window", "ret_%", "maxDD_%", "vol_%"]].to_string(
        index=False, float_format=lambda v: f"{v:.2f}"))

    # ---- gate: agree with script 21's independently-built 1/N ----
    # Script 21 rebalances QUARTERLY over the complete-3y-history eligible set;
    # this rebalances MONTHLY over the whole universe. Close, not identical, is
    # the right outcome - if they disagreed materially one of them is wrong.
    ref = os.path.join(ROOT, "4_backtest", "results", "min_variance", "backtest_summary.csv")
    gate_rows = []
    if os.path.exists(ref):
        r21 = pd.read_csv(ref, index_col=0).loc["1/N benchmark"]
        sub = C.loc["2018-04-02":"2025-12-31"]
        for k in ("1N_all_monthly", "1N_model_monthly"):
            st = stats(sub[k].dropna())
            gate_rows.append({"series": k,
                              "CAGR_%": round(st["CAGR_%"], 3),
                              "CAGR_%_script21": round(float(r21["CAGR_%"]), 3),
                              "vol_%": round(st["vol_%"], 3),
                              "vol_%_script21": round(float(r21["vol_%"]), 3),
                              "Sharpe": round(st["Sharpe"], 3),
                              "Sharpe_script21": round(float(r21["Sharpe"]), 3),
                              "d_Sharpe": round(st["Sharpe"] - float(r21["Sharpe"]), 3)})
        G = pd.DataFrame(gate_rows)
        G.to_csv(f"{OUTDIR}/gate_vs_script21.csv", index=False)
        print("\n--- gate: this benchmark vs script 21's own 1/N, same window ---")
        print(G.to_string(index=False))
        worst = G["d_Sharpe"].abs().max()
        print(f"max |d Sharpe| {worst:.3f} -> "
              + ("constructions agree" if worst < 0.05 else
                 "THEY DISAGREE - one of the two is wrong"))

    print(f"\nWrote {6 + (1 if gate_rows else 0)} CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
