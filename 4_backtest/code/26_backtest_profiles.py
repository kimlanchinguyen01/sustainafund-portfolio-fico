"""
SustainaFund — 26: walk-forward backtest of the RECOMMENDED profile
====================================================================
Not option A and not option B. Option A already exists.

`4_backtest/code/21_backtest_walkforward.py` is a full walk-forward: rolling 3-year
window, 31 quarterly rebalances, 7.7 test years, mean log-return + Ledoit-Wolf,
against 1/N, reporting Sharpe, max drawdown and turnover. Rebuilding it would
spend the day reproducing a result we already have.

What it does NOT do is test the book we recommend. It optimises for MINIMUM
VARIANCE at every rebalance. The recommendation is NEUTRAL, and the crisis
stress test (6_stress_test/) showed the distinction decides the answer:
min-variance beat 1/N in all three testable crises while neutral lost two of
three. So "no Sharpe edge over 1/N" is a statement about min-variance, and the
recommended portfolio has never had a walk-forward test at all.

This closes that gap on the same protocol, so the numbers are comparable.

THE OBSTACLE, AND THE FIX
-------------------------
Script 21 chose min-variance for a stated and correct reason: an absolute
return target `beta` is not comparable across regimes - the same beta is easy
in 2021 and infeasible in 2018 - and picking one per rebalance would smuggle in
a free parameter.

A MANDATE removes that objection. "Maximise return, then minimise risk while
giving up at most X of the ACHIEVABLE maximum" is defined relative to whatever
is achievable in that regime, so it is comparable across regimes and has no
absolute target. It is also cheap: two solves, not a whole frontier.

In the static model reltol = 20% lands at return/risk 1.345 against the
grid-picked Neutral's 1.346, i.e. it reproduces the recommendation without
needing a 15-point grid. reltol = 10% is carried as a second, more aggressive
point.

FOUR BOOKS PER REBALANCE
------------------------
  minvar       minimum variance - reproduces script 21, and is the gate: if
               this does not match 21's published numbers, the harness is wrong
               and nothing else here can be trusted
  mandate20    give up <= 20% of achievable max return  (the Neutral stand-in)
  mandate10    give up <= 10%                            (more aggressive)
  equal_weight 1/N over the same eligible universe

Estimation, eligibility, ESG floor, rebalance dates, buy-and-hold convention
and cost treatment are all IDENTICAL to script 21. Only the objective differs.

Everything is solved through Model2_ori.solve_model2, so the constraint set
cannot drift from the model. The country cap stays OFF, as in the delivered
model.

INHERITED LIMITATIONS - all three from script 21, none fixable with this data
----------------------------------------------------------------------------
1. ESG scores and sectors are a present-day snapshot, so applying ESG >= 70 at
   a 2018 rebalance uses 2025 information. Look-ahead, reported not hidden.
2. The universe is today's index constituents: survivorship-biased by
   construction, for every strategy here including the benchmark.
3. No transaction costs inside the optimiser. Turnover is measured and a cost
   sensitivity applied afterwards.

Outputs (4_backtest/results/profiles/):
    summary.csv        CAGR / vol / Sharpe / maxDD / final, per book, with costs
    equity_curves.csv  daily curves, all four books, indexed to 1.0
    subperiods.csv     the six regimes plus FULL, per book
    rebalances.csv     per rebalance per book: held, predicted risk, ESG, turnover, solstatus
    diagnostics.csv    Sharpe vs 1/N with a t-test, risk understatement, turnover
    gate.csv           minvar here vs script 21's published numbers

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 4_backtest/code/26_backtest_profiles.py       # ~15 min

Needs 1_data_preparation/results/prices_div_usd.csv, which is gitignored (52 MB). Rebuild it with
1_data_preparation/code/20_dividend_adjusted_pipeline.py or ask Chloe for the export.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)                    # <repo>/<part>
ROOT = os.path.dirname(PART)                    # <repo>
sys.path.insert(0, os.path.join(ROOT, "2_optimisation_model", "code"))

import Model2_ori as m2

TD = 252
WINDOW_Y = 3              # script 21's window, kept
ESG_FLOOR = 30.0
COST_BPS = 10             # one-way, applied to measured turnover afterwards
TIME_LIMIT = 90
OUTDIR = os.path.join(PART, "results", "profiles")

PRICES = os.path.join(ROOT, "1_data_preparation", "results", "prices_div_usd.csv")
SHARES = os.path.join(ROOT, "2_optimisation_model", "data", "shares_imputed.csv")
SECTORS = os.path.join(ROOT, "2_optimisation_model", "data", "sectors.xlsx")

BOOKS = ["minvar", "mandate20", "mandate10", "equal_weight"]
MANDATES = {"mandate20": 0.20, "mandate10": 0.10}

# Script 21's published figures, for the gate. From
# 4_backtest/results/min_variance/backtest_summary.csv and backtest_diagnostics.csv.
GATE = {"CAGR_%": 11.03, "vol_%": 13.21, "Sharpe": 0.835, "maxDD_%": -33.89}

# The regimes the deck plots. Same windows as the existing (unreproducible)
# backtest_subperiods.csv, so this is a drop-in replacement for it.
REGIMES = [
    ("2018-04..2019-12", "calm market",       "2018-04-01", "2019-12-31"),
    ("2020 full year",   "crash and rebound", "2020-01-01", "2020-12-31"),
    ("2020-02..2020-03", "the crash itself",  "2020-02-19", "2020-03-31"),
    ("2021",             "boom",              "2021-01-01", "2021-12-31"),
    ("2022",             "inflation shock",   "2022-01-01", "2022-12-31"),
    ("2023-2025",        "AI rally",          "2023-01-01", "2025-12-31"),
]

os.makedirs(OUTDIR, exist_ok=True)


# ============================================================
# data and protocol, mirroring script 21
# ============================================================
def load():
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


def rebalance_dates(cols):
    start = cols.min() + pd.DateOffset(years=WINDOW_Y)
    qs = pd.date_range(start, cols.max(), freq="QE")
    d = [cols[cols.searchsorted(q, "left")] for q in qs]
    return sorted(set(x for x in d if x < cols.max()))


def estimate(rets, sh, t):
    w_start = t - pd.DateOffset(years=WINDOW_Y)
    win = rets.loc[:, (rets.columns >= w_start) & (rets.columns < t)]
    ok = win.notna().all(axis=1)
    elig = [s for s in win.index[ok] if sh.loc[s, "ESG score"] >= ESG_FLOOR]
    if len(elig) < m2.MIN_STOCKS + 20:
        return None, elig
    R = win.loc[elig]
    mu = pd.Series(R.mean(axis=1).values * TD, index=elig)
    Sigma = pd.DataFrame(LedoitWolf().fit(R.T.values).covariance_ * TD,
                         index=elig, columns=elig)
    return (mu, Sigma), elig


def solve_books(est, sh, sec, elig):
    """The four books at one rebalance. Stage 1 of a mandate (max return,
    unconstrained) is identical for every reltol, so it is solved once."""
    mu, Sigma = est
    args = (mu, Sigma, sh.loc[elig, "Region"], sh.loc[elig, "ESG score"].astype(float),
            sec.loc[elig])
    kw = dict(time_limit=TIME_LIMIT, verbose=False)
    out = {}

    r = m2.solve_model2(*args, mode="min_risk_only", **kw)
    if r["feasible"]:
        out["minvar"] = r

    hi = m2.solve_model2(*args, mode="max_return_only", **kw)
    if hi["feasible"]:
        for name, tol in MANDATES.items():
            r = m2.solve_model2(*args, mode="min_risk",
                                target_return=(1.0 - tol) * hi["portfolio_return"], **kw)
            if r["feasible"]:
                r = dict(r)
                r["max_return"] = hi["portfolio_return"]
                out[name] = r
    return out


# ============================================================
# statistics
# ============================================================
def stats(s, cost_bps=0.0, turnover=None):
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    tot = s.iloc[-1] / s.iloc[0]
    if cost_bps and turnover:
        tot *= (1 - cost_bps / 1e4) ** (2 * sum(turnover))
    cagr = tot ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(TD)
    dd = float((s / s.cummax() - 1).min())
    return {"CAGR_%": cagr * 100, "vol_%": vol * 100,
            "Sharpe": cagr / vol if vol else np.nan,
            "maxDD_%": dd * 100, "final_x": tot}


def paired_t(a, b):
    """t on the daily return difference. Computed rather than imported: this is
    a paired mean test, and scipy is not a dependency of this repo."""
    d = (a.pct_change() - b.pct_change()).dropna()
    if len(d) < 3 or d.std(ddof=1) == 0:
        return np.nan, np.nan
    t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
    return float(t), len(d)


# ============================================================
# main
# ============================================================
def main():
    assert not m2.ENABLE_COUNTRY_CAP, "the delivered model has the country cap off"
    px, sh, sec = load()
    simple = px.pct_change(axis=1).iloc[:, 1:]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]
    rebal = rebalance_dates(px.columns)
    print(f"rebalances: {len(rebal)} | first {rebal[0].date()} | last {rebal[-1].date()}\n")

    vals = {b: [1.0] for b in BOOKS}
    dates_out = [rebal[0]]
    holds = {b: None for b in BOOKS}
    turn = {b: [] for b in BOOKS}
    records = []

    for i, t in enumerate(rebal):
        est, elig = estimate(rets, sh, t)
        if est is None:
            print(f"  {t.date()}  only {len(elig)} eligible - skipped")
            continue
        solved = solve_books(est, sh, sec, elig)
        if "minvar" not in solved:
            print(f"  {t.date()}  min-variance infeasible - skipped")
            continue

        w_books = {}
        for b, r in solved.items():
            w = r["weights"]
            w_books[b] = w[w > 1e-9]
        w_books["equal_weight"] = pd.Series(1.0 / len(elig), index=elig)

        for b, w in w_books.items():
            if holds[b] is not None:
                idx = sorted(set(w.index) | set(holds[b].index))
                turn[b].append(0.5 * float((w.reindex(idx).fillna(0)
                                            - holds[b].reindex(idx).fillna(0)).abs().sum()))
            holds[b] = w
            r = solved.get(b)
            records.append({
                "date": t.date(), "book": b, "n_eligible": len(elig), "n_held": len(w),
                "pred_return_%": r["portfolio_return"] * 100 if r else np.nan,
                "pred_risk_%": r["portfolio_risk"] * 100 if r else np.nan,
                "esg": r["esg_weighted"] if r else float((sh.loc[w.index, "ESG score"] * w).sum()),
                "solstatus": r["solstatus"] if r else "n/a",
                "solve_sec": round(r["elapsed_sec"], 1) if r else np.nan,
                "turnover_%": turn[b][-1] * 100 if turn[b] else np.nan,
            })

        nxt = rebal[i + 1] if i + 1 < len(rebal) else px.columns.max()
        seg = simple.columns[(simple.columns > t) & (simple.columns <= nxt)]
        for b, w in w_books.items():
            sub = simple.loc[w.index, seg].fillna(0.0)
            growth = (1.0 + sub).cumprod(axis=1)
            pv = (growth.T * w.values).sum(axis=1).values
            vals[b].extend(list(vals[b][-1] * pv))
        dates_out.extend(list(seg))

        mv, m20 = solved["minvar"], solved.get("mandate20")
        print(f"  {t.date()}  elig {len(elig):4d} | minvar {len(w_books['minvar']):3d} held, "
              f"risk {mv['portfolio_risk']*100:5.2f}%"
              + (f" | mandate20 {len(w_books['mandate20']):3d} held, "
                 f"ret {m20['portfolio_return']*100:5.2f}% risk {m20['portfolio_risk']*100:5.2f}%"
                 if m20 is not None else " | mandate20 MISSING"), flush=True)

    n = min(len(dates_out), min(len(v) for v in vals.values()))
    E = pd.DataFrame({b: vals[b][:n] for b in BOOKS},
                     index=pd.DatetimeIndex(dates_out[:n]))
    E = E[~E.index.duplicated()]

    # ---------- summary ----------
    rows = {}
    for b in BOOKS:
        rows[b] = stats(E[b])
    for b in ("minvar", "mandate20", "mandate10"):
        rows[f"{b} after {COST_BPS}bp"] = stats(E[b], COST_BPS, turn[b])
    S = pd.DataFrame(rows).T
    S.to_csv(f"{OUTDIR}/summary.csv")

    print("\n" + "=" * 92)
    print(f"OUT-OF-SAMPLE  {E.index[0].date()} .. {E.index[-1].date()} "
          f"({(E.index[-1]-E.index[0]).days/365.25:.1f} years)")
    print("=" * 92)
    print(S.round(3).to_string())

    # ---------- gate: does minvar reproduce script 21? ----------
    g = stats(E["minvar"])
    gate = pd.DataFrame([{"metric": k, "script_21": v, "here": round(g[k], 3),
                          "diff": round(g[k] - v, 3)} for k, v in GATE.items()])
    gate.to_csv(f"{OUTDIR}/gate.csv", index=False)
    print("\n--- GATE: min-variance here vs script 21's published numbers ---")
    print(gate.to_string(index=False))
    worst = gate["diff"].abs().max()
    print(f"max |difference| {worst:.3f} -> "
          + ("harness reproduces script 21" if worst < 0.5 else
             "DOES NOT REPRODUCE - treat everything below as suspect"))

    # ---------- diagnostics ----------
    diag = []
    for b in ("minvar", "mandate20", "mandate10"):
        t_stat, nobs = paired_t(E[b], E["equal_weight"])
        diag += [
            {"metric": f"Sharpe {b} (rf=0)", "value": round(rows[b]["Sharpe"], 3)},
            {"metric": f"Sharpe difference {b} - 1/N",
             "value": round(rows[b]["Sharpe"] - rows["equal_weight"]["Sharpe"], 3)},
            {"metric": f"t-stat daily diff {b} - 1/N", "value": round(t_stat, 2)},
            {"metric": f"significant at 5% {b}", "value": float(abs(t_stat) > 1.96)},
            {"metric": f"turnover per rebalance mean_% {b}",
             "value": round(float(np.mean(turn[b])) * 100, 1)},
            {"metric": f"turnover annualised_% {b}",
             "value": round(float(np.mean(turn[b])) * 4 * 100, 1)},
        ]
        R = pd.DataFrame(records)
        pr = R[(R.book == b)]["pred_risk_%"].mean()
        diag += [
            {"metric": f"mean predicted risk_% {b}", "value": round(pr, 2)},
            {"metric": f"realised volatility_% {b}", "value": round(rows[b]["vol_%"], 2)},
            {"metric": f"risk understatement_% {b}",
             "value": round((rows[b]["vol_%"] / pr - 1) * 100, 1)},
        ]
    diag += [{"metric": "Sharpe 1/N (rf=0)", "value": round(rows["equal_weight"]["Sharpe"], 3)},
             {"metric": "rebalances", "value": float(len(set(r['date'] for r in records)))},
             {"metric": "test years", "value": round((E.index[-1]-E.index[0]).days/365.25, 1)}]
    pd.DataFrame(diag).to_csv(f"{OUTDIR}/diagnostics.csv", index=False)

    # ---------- subperiods ----------
    sub = []
    for label, regime, a, b_ in REGIMES + [("FULL", "whole test period",
                                            str(E.index[0].date()), str(E.index[-1].date()))]:
        seg = E.loc[(E.index >= a) & (E.index <= b_)]
        if len(seg) < 5:
            continue
        row = {"period": label, "regime": regime}
        for bk in BOOKS:
            st = stats(seg[bk])
            row[f"{bk}_CAGR_%"] = round(st["CAGR_%"], 2)
            row[f"{bk}_vol_%"] = round(st["vol_%"], 2)
            row[f"{bk}_maxDD_%"] = round(st["maxDD_%"], 2)
        row["mandate20_vs_eq_vol_%"] = round(
            (row["mandate20_vol_%"] / row["equal_weight_vol_%"] - 1) * 100, 1)
        sub.append(row)
    SUB = pd.DataFrame(sub)
    SUB.to_csv(f"{OUTDIR}/subperiods.csv", index=False)
    print("\n--- by regime: CAGR / vol / maxDD ---")
    print(SUB[["period", "regime", "minvar_CAGR_%", "mandate20_CAGR_%",
               "equal_weight_CAGR_%", "minvar_vol_%", "mandate20_vol_%",
               "equal_weight_vol_%", "mandate20_maxDD_%", "equal_weight_maxDD_%"]]
          .to_string(index=False))

    E.to_csv(f"{OUTDIR}/equity_curves.csv")
    pd.DataFrame(records).to_csv(f"{OUTDIR}/rebalances.csv", index=False)
    print(f"\nWrote 6 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
