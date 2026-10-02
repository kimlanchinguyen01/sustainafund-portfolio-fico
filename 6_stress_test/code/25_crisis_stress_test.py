"""
SustainaFund — 25: crisis-window stress test
=============================================
The walk-forward backtest (`4_backtest/code/21_backtest_walkforward.py`) tests the
MINIMUM-VARIANCE book. The book we actually recommend is NEUTRAL (14.30% at
10.62%), and it has never been put through a crisis. This does that.

Two panels, because they answer two different questions and only one of them
is a real stress test.

PANEL A — "how would the book we are delivering have behaved?"
    The three delivered portfolios (2_optimisation_model/results/portfolio_tier2off_*.csv) are
    held through each crisis window, weights drifting with prices as a real
    book does. Benchmark: 1/N over the same holdings-eligible universe.

    This is IN-SAMPLE and must be read as such: mu and Sigma were estimated on
    2015-2025, which contains every one of these crises. The optimiser had
    already seen them. Panel A is a description of the delivered book, not
    evidence that the method protects anyone.

PANEL B — "would our method have protected us?"
    Point-in-time. For each window: estimate on the 3 years strictly BEFORE it,
    build the frontier, take the same three profile definitions, hold through
    the window. Nothing after the window start is used.

    Estimation follows script 21 rather than the 20-factor James-Stein
    pipeline: trailing mean log-return and a Ledoit-Wolf shrunk sample
    covariance. Re-running the full factor pipeline per window would change the
    estimator and the window at once, and the comparison would mean nothing.

    Panel B also runs NEUTRAL with the 25% country cap on, which answers a
    question the static numbers cannot: does forcing the book out of
    Switzerland help or hurt when markets break?

Inherited limitations, all three from script 21 and none fixable here: ESG
scores and sectors are a present-day snapshot (look-ahead), the universe is
today's index constituents (survivorship bias), no transaction costs.

Outputs (6_stress_test/results/):
    panelA_windows.csv      delivered books through each window
    panelB_windows.csv      point-in-time books through each window
    panelB_portfolios.csv   one row per point-in-time book: solstatus, solve time, top country
    panelB_holdings.csv     window x book x cap x stock x weight - the full point-in-time
                            allocations, decimals, renormalised to sum to 1
    drawdown_attribution.csv  who caused the COVID drawdown, by country
    worst_windows.csv       the 5 worst 60-day stretches, found empirically

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 6_stress_test/code/25_crisis_stress_test.py        # ~7 min

Needs 1_data_preparation/results/prices_div_usd.csv, which is gitignored (52 MB). Rebuild it with
1_data_preparation/code/20_dividend_adjusted_pipeline.py or ask Chloe for the export.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

# This script lives in 6_stress_test/code/ but its inputs come from other parts of
# the repository, so paths are anchored to the repository rather than to the
# working directory. It can then be
# run from anywhere:  python3 6_stress_test/code/25_crisis_stress_test.py
HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)                    # <repo>/<part>
ROOT = os.path.dirname(PART)                    # <repo>
sys.path.insert(0, os.path.join(ROOT, "2_optimisation_model", "code"))

import Model2_ori as m2

TD = 252
WINDOW_Y = 3
FRONTIER_PTS = 5          # per estimation date per configuration; 15 would triple runtime
ESG_FLOOR = 30.0
OUTDIR = os.path.join(PART, "results")

# prices_div_usd.csv is GITIGNORED (52 MB, LSEG-derived). Rebuild it with
# 1_data_preparation/code/20_dividend_adjusted_pipeline.py, or ask Chloe for the export.
PRICES = os.path.join(ROOT, "1_data_preparation", "results", "prices_div_usd.csv")
SHARES = os.path.join(ROOT, "2_optimisation_model", "data", "shares_imputed.csv")
SECTORS = os.path.join(ROOT, "2_optimisation_model", "data", "sectors.xlsx")
PORTFOLIOS = os.path.join(ROOT, "2_optimisation_model", "results", "portfolio_tier2off_{}.csv")

# Named windows. Dated from the market, not from the calendar: each is a
# peak-to-trough or peak-to-recovery stretch a mandate holder would remember.
WINDOWS = [
    ("2015 China devaluation", "2015-08-10", "2015-09-29"),
    ("2016 Brexit vote",       "2016-06-23", "2016-07-15"),
    ("2018 Q4 selloff",        "2018-09-20", "2018-12-24"),
    ("2020 COVID crash",       "2020-02-19", "2020-03-23"),
    ("2020 crash + recovery",  "2020-02-19", "2020-08-31"),
    ("2022 inflation shock",   "2022-01-03", "2022-10-12"),
]

os.makedirs(OUTDIR, exist_ok=True)


# ============================================================
# data
# ============================================================
def load_prices():
    if not os.path.exists(PRICES):
        sys.exit(f"missing input: {PRICES}\n"
                 "It is gitignored (52 MB, LSEG-derived). Rebuild it with\n"
                 "  cd pipeline && python3 20_dividend_adjusted_pipeline.py\n"
                 "or ask Chloe for the export.")
    px = pd.read_csv(PRICES, index_col=0)
    px.columns = pd.to_datetime(px.columns)
    sh = pd.read_csv(SHARES).set_index("Stock")
    sec = pd.read_excel(SECTORS).set_index("Stock")["Sector"]
    common = [s for s in px.index if s in sh.index and s in sec.index]
    px = px.loc[common]
    print(f"universe {len(px)} | {px.columns.min().date()} .. {px.columns.max().date()}")
    return px, sh.loc[common], sec.reindex(common).fillna("Unknown")


def snap(dates, d):
    """Nearest trading date at or after d."""
    d = pd.Timestamp(d)
    i = dates.searchsorted(d, "left")
    return dates[min(i, len(dates) - 1)]


# ============================================================
# buy-and-hold valuation and window metrics
# ============================================================
def hold_value(simple, weights, seg):
    """Value of a fixed-weight book over `seg`, positions compounding
    independently so weights drift - the same convention as script 21."""
    held = [s for s in weights.index if s in simple.index]
    w = weights.loc[held]
    w = w / w.sum()
    seg = seg.intersection(simple.columns)     # simple has no first date: it is a diff
    sub = simple.loc[held, seg].fillna(0.0)
    growth = (1.0 + sub).cumprod(axis=1)
    return pd.Series((growth.T * w.values).sum(axis=1).values, index=seg)


def window_stats(v, simple, weights, dates, w_end):
    """Metrics for one window. `recovery_days` looks PAST the window end, which
    is the only forward-looking thing here and is labelled as such."""
    r = v.pct_change().dropna()
    out = {
        "ret_%": (v.iloc[-1] / v.iloc[0] - 1) * 100,
        "maxDD_%": float((v / v.cummax() - 1).min()) * 100,
        "vol_%": float(r.std() * np.sqrt(TD)) * 100 if len(r) > 1 else np.nan,
        "worst_1d_%": float(r.min()) * 100 if len(r) else np.nan,
        "worst_5d_%": float((v / v.shift(5) - 1).min()) * 100 if len(v) > 5 else np.nan,
        "n_held": int(len([s for s in weights.index if s in simple.index])),
    }
    # Time to recovery: days from the window start until the book first regains
    # that level AFTER the window's trough. Continuing forward past w_end is the
    # only forward-looking thing in this script.
    #
    # NOT "the last date below the start level", which is what a naive version
    # does and which is wrong in a way that flatters nothing: for the 2018 Q4
    # window it finds the book below its 2018 level again during COVID and
    # reports a 614-day recovery instead of the real one in 2019.
    fwd = dates[dates >= w_end]
    out["recovery_days"] = np.nan
    if len(fwd) > 1:
        tail = hold_value(simple, weights, fwd)
        tail = tail / tail.iloc[0] * v.iloc[-1]
        full = pd.concat([v, tail.iloc[1:]])
        start_level = v.iloc[0]
        trough_date = v.idxmin()
        after_trough = full[full.index >= trough_date]
        regained = after_trough[after_trough >= start_level]
        if v.min() >= start_level:
            out["recovery_days"] = 0            # never fell below its own start
        elif len(regained):
            out["recovery_days"] = (regained.index[0] - v.index[0]).days
        # else: still under water at the end of the data -> stays NaN
    return out


# ============================================================
# point-in-time estimation and solve
# ============================================================
MIN_EST_DAYS = 500        # ~2 years; below this the estimate is not worth solving


def estimate(rets, sh, sec, t):
    """Estimate on the 3 years strictly before t.

    Returns a string reason instead of data when the window cannot be built.
    The 2015 and 2016 crises fall inside the first three years of the dataset,
    so no point-in-time estimate exists for them - that is missing data, not an
    infeasible model, and the two must not be reported the same way. Script 21
    hits the same wall and starts its walk-forward in 2018-04.
    """
    w_start = t - pd.DateOffset(years=WINDOW_Y)
    win = rets.loc[:, (rets.columns >= w_start) & (rets.columns < t)]
    if win.shape[1] < MIN_EST_DAYS:
        return (f"only {win.shape[1]} trading days of history before "
                f"{t.date()} (need {MIN_EST_DAYS}); the dataset starts "
                f"{rets.columns.min().date()}")
    ok = win.notna().all(axis=1)
    elig = [s for s in win.index[ok] if sh.loc[s, "ESG score"] >= ESG_FLOOR]
    if len(elig) < m2.MIN_STOCKS + 20:
        return (f"only {len(elig)} stocks have a complete history in that "
                f"window (need {m2.MIN_STOCKS + 20})")
    R = win.loc[elig]
    mu = pd.Series(R.mean(axis=1).values * TD, index=elig)
    Sigma = pd.DataFrame(LedoitWolf().fit(R.T.values).covariance_ * TD,
                         index=elig, columns=elig)
    return (mu, Sigma,
            sh.loc[elig, "Region"], sh.loc[elig, "ESG score"].astype(float),
            sec.loc[elig], sh.loc[elig, "Country"], len(win.columns))


def profiles_point_in_time(est, cap):
    """min-var, max-ratio ("neutral") and max-return, from a small frontier.
    Reuses Model2_ori.solve_model2, so the constraint set cannot drift."""
    mu, Sigma, reg, esg, sec, ctry, _ = est
    m2.ENABLE_COUNTRY_CAP = cap is not None
    if cap is not None:
        m2.COUNTRY_CAP = cap
    kw = dict(country=ctry, time_limit=120, verbose=False)

    lo = m2.solve_model2(mu, Sigma, reg, esg, sec, mode="min_risk_only", **kw)
    hi = m2.solve_model2(mu, Sigma, reg, esg, sec, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        return None

    rows = []
    for b in np.linspace(lo["portfolio_return"], hi["portfolio_return"], FRONTIER_PTS):
        r = m2.solve_model2(mu, Sigma, reg, esg, sec, mode="min_risk",
                            target_return=b, **kw)
        if r["feasible"]:
            rows.append(r)
    if not rows:
        return None
    ratio = [r["portfolio_return"] / r["portfolio_risk"] for r in rows]
    return {
        "risk_averse": rows[int(np.argmin([r["portfolio_risk"] for r in rows]))],
        "neutral": rows[int(np.argmax(ratio))],
        "risk_prone": rows[int(np.argmax([r["portfolio_return"] for r in rows]))],
    }


# ============================================================
# main
# ============================================================
def main():
    px, sh, sec = load_prices()
    simple = px.pct_change(axis=1).iloc[:, 1:]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]
    dates = simple.columns          # the return grid, not the price grid

    # ---------- PANEL A ----------
    print("\n" + "=" * 78)
    print("PANEL A - the delivered books, held through each crisis (IN-SAMPLE)")
    print("=" * 78)

    books = {}
    for name in ("risk_averse", "neutral", "risk_prone"):
        d = pd.read_csv(PORTFOLIOS.format(name), index_col=0)
        books[name] = d["weight_%"] / d["weight_%"].sum()
    universe = [s for s in px.index if sh.loc[s, "ESG score"] >= ESG_FLOOR]
    books["equal_weight"] = pd.Series(1.0 / len(universe), index=universe)

    rows = []
    for label, d0, d1 in WINDOWS + [("FULL 2015-2025", str(dates.min().date()),
                                     str(dates.max().date()))]:
        a, b = snap(dates, d0), snap(dates, d1)
        seg = dates[(dates >= a) & (dates <= b)]
        for bk, w in books.items():
            v = hold_value(simple, w, seg)
            st = window_stats(v, simple, w, dates, b)
            rows.append({"window": label, "book": bk, "from": a.date(), "to": b.date(),
                         "trading_days": len(seg), **st})
    A = pd.DataFrame(rows)
    A.to_csv(f"{OUTDIR}/panelA_windows.csv", index=False)
    show = ["window", "book", "ret_%", "maxDD_%", "vol_%", "worst_1d_%", "recovery_days"]
    print(A[show].to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    # ---------- drawdown attribution, COVID ----------
    a, b = snap(dates, "2020-02-19"), snap(dates, "2020-03-23")
    seg = dates[(dates >= a) & (dates <= b)]
    w = books["neutral"]
    held = [s for s in w.index if s in simple.index]
    contrib = ((px.loc[held, seg[-1]] / px.loc[held, seg[0]] - 1) * w.loc[held])
    att = pd.DataFrame({"weight_%": w.loc[held] * 100,
                        "stock_ret_%": (px.loc[held, seg[-1]] / px.loc[held, seg[0]] - 1) * 100,
                        "contribution_pp": contrib * 100,
                        "country": sh.loc[held, "Country"],
                        "sector": sec.loc[held]})
    by_c = att.groupby("country").agg(weight_pct=("weight_%", "sum"),
                                      contribution_pp=("contribution_pp", "sum")).sort_values("contribution_pp")
    att.sort_values("contribution_pp").to_csv(f"{OUTDIR}/drawdown_attribution.csv")
    print("\n--- COVID crash: who caused it, by country (neutral book) ---")
    print(by_c.to_string(float_format=lambda v: f"{v:.2f}"))

    # ---------- worst windows, found empirically ----------
    vfull = hold_value(simple, books["neutral"], dates)
    roll = (vfull / vfull.shift(60) - 1).dropna()
    # Greedy non-overlapping minima: walk the rolling returns from worst to best
    # and accept one only if it is at least 60 trading days clear of every
    # window already accepted. Taking the FIRST date in each bad stretch instead
    # reports the shallowest window in it, not the deepest.
    order = roll.sort_values().index
    pos = {d: i for i, d in enumerate(roll.index)}
    picked = []
    for d in order:
        if all(abs(pos[d] - pos[q]) >= 60 for q in picked):
            picked.append(d)
        if len(picked) == 5:
            break
    W = pd.DataFrame([{"window_start": vfull.index[max(0, vfull.index.get_loc(d) - 60)].date(),
                       "window_end": d.date(), "ret_60d_%": roll[d] * 100}
                      for d in picked]).sort_values("ret_60d_%")
    W.to_csv(f"{OUTDIR}/worst_windows.csv", index=False)
    print("\n--- worst 60-day stretches for the neutral book, found from the data ---")
    print(W.to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    # ---------- PANEL B ----------
    print("\n" + "=" * 78)
    print("PANEL B - point-in-time: estimate before the window, hold through it")
    print("=" * 78)

    rowsB, held_rows, weight_rows, skipped = [], [], [], []
    # Two windows can share a start date ("2020 COVID crash" and "2020 crash +
    # recovery" both begin 2020-02-19). The estimate and every solve are then
    # identical, so they are computed once and reused.
    est_cache, solve_cache = {}, {}

    for label, d0, d1 in WINDOWS:
        a, b = snap(dates, d0), snap(dates, d1)
        seg = dates[(dates >= a) & (dates <= b)]
        if a not in est_cache:
            est_cache[a] = estimate(rets, sh, sec, a)
        est = est_cache[a]
        if isinstance(est, str):
            print(f"\n{label}: NOT TESTABLE point-in-time - {est}")
            skipped.append({"window": label, "reason": est})
            continue
        n_elig, n_days = len(est[0]), est[6]
        reused = " (reusing the solves from the window above)" if (a, "cap off") in solve_cache else ""
        print(f"\n{label}  estimated on {n_days} days before {a.date()}, "
              f"{n_elig} eligible{reused}", flush=True)

        for cap_label, cap in (("cap off", None), ("cap 25%", 0.25)):
            key = (a, cap_label)
            if key not in solve_cache:
                solve_cache[key] = profiles_point_in_time(est, cap)
            prof = solve_cache[key]
            if prof is None:
                print(f"  {cap_label}: infeasible - skipped")
                continue
            for pname, res in prof.items():
                if cap is not None and pname != "neutral":
                    continue                      # cap comparison only needs neutral
                w = res["weights"]
                w = w[w > 1e-9]
                v = hold_value(simple, w, seg)
                st = window_stats(v, simple, w, dates, b)
                rowsB.append({"window": label, "book": pname, "cap": cap_label,
                              "from": a.date(), "to": b.date(),
                              "pred_ret_%": res["portfolio_return"] * 100,
                              "pred_risk_%": res["portfolio_risk"] * 100, **st})
                held_rows.append({"window": label, "book": pname, "cap": cap_label,
                                  "solstatus": res["solstatus"],   # OPTIMAL, or FEASIBLE if it hit the time limit
                                  "solve_sec": round(res["elapsed_sec"], 1),
                                  "n": len(w), "top_country": res.get("max_country"),
                                  "top_country_%": (res.get("max_country_weight") or 0) * 100,
                                  "holdings": "|".join(w.sort_values(ascending=False)
                                                        .head(8).index)})
                # Full weights, one row per position. The `holdings` column above
                # is a pipe-joined string of the top 8 names and cannot drive an
                # allocation chart; this can. Weights are DECIMALS and are
                # renormalised the same way hold_value() does, so they sum to 1.
                wn = w / w.sum()
                for stock, wt in wn.sort_values(ascending=False).items():
                    weight_rows.append({
                        "window": label, "book": pname, "cap": cap_label,
                        "from": a.date(), "to": b.date(),
                        "stock": str(stock), "weight": float(wt),
                        "solstatus": res["solstatus"]})
                print(f"  {pname:12s} {cap_label:8s} predicted {res['portfolio_risk']*100:5.2f}% risk "
                      f"-> realised {st['vol_%']:6.2f}%, window return {st['ret_%']:7.2f}%, "
                      f"maxDD {st['maxDD_%']:7.2f}%")

        eq_u = [s for s in est[0].index]
        w_eq = pd.Series(1.0 / len(eq_u), index=eq_u)
        v = hold_value(simple, w_eq, seg)
        st = window_stats(v, simple, w_eq, dates, b)
        rowsB.append({"window": label, "book": "equal_weight", "cap": "n/a",
                      "from": a.date(), "to": b.date(),
                      "pred_ret_%": np.nan, "pred_risk_%": np.nan, **st})
        # 1/N holds too many names to chart individually, but its allocation by
        # country/sector is exactly what a comparison wants, so it is dumped
        # alongside the optimised books rather than left implicit.
        # NOT "n/a": pandas reads that string back as a MISSING VALUE, and a NaN
        # group key makes groupby silently drop the rows - which hid these 3,979
        # benchmark positions from a weights-sum check that was supposed to cover
        # them. Any token here must survive a round trip through read_csv.
        for stock, wt in w_eq.items():
            weight_rows.append({"window": label, "book": "equal_weight",
                                "cap": "not applicable",
                                "from": a.date(), "to": b.date(),
                                "stock": str(stock), "weight": float(wt),
                                "solstatus": "benchmark"})
        print(f"  {'1/N':12s} {'':8s} {'':22s} -> realised {st['vol_%']:6.2f}%, "
              f"window return {st['ret_%']:7.2f}%, maxDD {st['maxDD_%']:7.2f}%")

    B = pd.DataFrame(rowsB)
    B.to_csv(f"{OUTDIR}/panelB_windows.csv", index=False)
    if skipped:
        pd.DataFrame(skipped).to_csv(f"{OUTDIR}/panelB_not_testable.csv", index=False)
        print("\n--- windows with no point-in-time estimate available ---")
        for r in skipped:
            print(f"  {r['window']}: {r['reason']}")
    pd.DataFrame(held_rows).to_csv(f"{OUTDIR}/panelB_portfolios.csv", index=False)
    WH = pd.DataFrame(weight_rows)
    WH.to_csv(f"{OUTDIR}/panelB_holdings.csv", index=False)
    chk = WH.groupby(["window", "book", "cap"])["weight"].sum()
    bad = chk[(chk - 1.0).abs() > 1e-6]
    assert not len(bad), f"point-in-time weights do not sum to 1: {bad.to_dict()}"
    print(f"\npanelB_holdings.csv: {len(WH)} position rows across "
          f"{WH.groupby(['window','book','cap']).ngroups} books, all summing to 1")

    print("\n--- Panel B summary: predicted vs realised risk ---")
    q = B[B.book.isin(["neutral", "equal_weight"])].copy()
    q["risk_ratio"] = q["vol_%"] / q["pred_risk_%"]
    print(q[["window", "book", "cap", "pred_risk_%", "vol_%", "risk_ratio",
             "ret_%", "maxDD_%"]].to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    m2.ENABLE_COUNTRY_CAP = False
    print(f"\nWrote 6 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
