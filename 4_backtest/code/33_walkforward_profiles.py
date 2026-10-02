"""
SustainaFund — 33: walk-forward with the CANONICAL profiles, not a proxy
=========================================================================
Closes the last real gap in the out-of-sample work.

WHAT WAS MISSING
`4_backtest/code/21_backtest_walkforward.py` optimises for MINIMUM VARIANCE at every
rebalance, so it validates the risk-averse end. `4_backtest/` (script 26)
added return-seeking books, but expressed them as MANDATES - "give up at most X
of the achievable maximum" - because an absolute return target is not comparable
across regimes. That was a defensible proxy for Neutral, not Neutral itself.

Neutral is defined as the MAXIMUM RETURN/RISK POINT ON THE FRONTIER. To test it
out of sample you have to build a frontier at every rebalance date and apply the
selection rule there. That is what this does: a 7-point frontier at each of the
31 rebalances, then profile_rule.py picks all three profiles from it.

Cost: about 280 solves against script 26's 124. That is the whole reason it was
deferred rather than skipped.

WHY IT IS WORTH THE SOLVES
Because the answer might differ. The mandate anchors on the max-return corner of
an unshrunk 3-year sample mean - at the first rebalance it predicted 45.85%
return - whereas max-return/risk is scale-free in that anchor. If the two agree,
script 26's proxy is vindicated. If they disagree, script 26's numbers were
measuring the anchor rather than the profile.

PROTOCOL - identical to scripts 21 and 26 so the numbers are comparable:
rolling 3-year estimation window, quarterly rebalance, buy-and-hold in between
so weights drift, only data strictly before each rebalance used, trailing mean
log-return and a Ledoit-Wolf shrunk sample covariance, 1/N over the same
eligible universe as benchmark. Solving goes through Model2_ori.solve_model2 so
the constraint set cannot drift, and the country cap stays off.

THE GATE: the Risk Averse leg is minimum variance by definition, so it must
reproduce script 21's published 1/N-relative result. If it does not, the harness
is wrong and nothing else here counts.

Outputs (dashboard_data/walkforward/):
    summary.csv      per profile: CAGR, vol, Sharpe, maxDD, final, turnover
    equity_curves.csv  long format: profile x date x indexed_wealth
    rebalances.csv   per rebalance per profile: frontier point chosen, predicted
                     risk, holdings, ESG, solstatus - so the SELECTION is auditable
    diagnostics.csv  Sharpe vs 1/N with paired t-tests, risk understatement
    subperiods.csv   the six regimes plus FULL
    gate.csv         min-variance leg vs script 21

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 33_walkforward_profiles.py        # ~35 min
"""

# --- repository layout (added when the repo was grouped by part) -------------
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))     # <repo>/<part>/code
PART = os.path.dirname(_HERE)                          # <repo>/<part>
_REPO = os.path.dirname(PART)                          # <repo>
MODEL_CODE = os.path.join(_REPO, "2_optimisation_model", "code")
MODEL_DATA = os.path.join(_REPO, "2_optimisation_model", "data")
MODEL_RESULTS = os.path.join(_REPO, "2_optimisation_model", "results")
PREP_RESULTS = os.path.join(_REPO, "1_data_preparation", "results")
sys.path.insert(0, MODEL_CODE)
# -----------------------------------------------------------------------------


import os
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

import Model2_ori as m2
import profile_rule as pr

TD = 252
WINDOW_Y = 3
FRONTIER_PTS = 7          # enough to locate the max-ratio point; 15 doubles the cost
ESG_FLOOR = 30.0
COST_BPS = 10
TIME_LIMIT = 90
OUTDIR = os.path.join(PART, "results", "walkforward")

PRICES = os.path.join(PREP_RESULTS, "prices_div_usd.csv")
BOOKS = list(pr.PROFILES) + ["1/N Equal Weight"]

# script 21's published 1/N benchmark, for the gate
GATE_REF = {"CAGR": 14.652, "vol": 16.911, "Sharpe": 0.866}

REGIMES = [
    ("2018-04..2019-12", "calm market",       "2018-04-01", "2019-12-31"),
    ("2020 full year",   "crash and rebound", "2020-01-01", "2020-12-31"),
    ("2020-02..2020-03", "the crash itself",  "2020-02-19", "2020-03-31"),
    ("2021",             "boom",              "2021-01-01", "2021-12-31"),
    ("2022",             "inflation shock",   "2022-01-01", "2022-12-31"),
    ("2023-2025",        "AI rally",          "2023-01-01", "2025-12-31"),
]

os.makedirs(OUTDIR, exist_ok=True)


def load():
    px = pd.read_csv(PRICES, index_col=0)
    px.columns = pd.to_datetime(px.columns)
    sh = pd.read_csv(m2.FILE_SHARES).set_index("Stock")
    sec = pd.read_excel(m2.FILE_SECTORS).set_index("Stock")["Sector"]
    common = [s for s in px.index if s in sh.index and s in sec.index]
    return px.loc[common], sh.loc[common], sec.reindex(common).fillna("Unknown")


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


def frontier_at(est, sh, sec, elig):
    """A short frontier, then the canonical rule. Returns {profile: result}."""
    mu, Sigma = est
    args = (mu, Sigma, sh.loc[elig, "Region"],
            sh.loc[elig, "ESG score"].astype(float), sec.loc[elig])
    kw = dict(time_limit=TIME_LIMIT, verbose=False)

    lo = m2.solve_model2(*args, mode="min_risk_only", **kw)
    hi = m2.solve_model2(*args, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        return None
    results = []
    for b in np.linspace(lo["portfolio_return"], hi["portfolio_return"], FRONTIER_PTS):
        results.append(m2.solve_model2(*args, mode="min_risk", target_return=b, **kw))
    rows = pr.rows_from_results(results)
    if not rows:
        return None
    picks = pr.pick_profiles(rows)
    return {prof: (pt, results[pt]) for prof, pt in picks.items()}


def stats(s, cost_bps=0.0, turnover=None):
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    tot = s.iloc[-1] / s.iloc[0]
    if cost_bps and turnover:
        tot *= (1 - cost_bps / 1e4) ** (2 * sum(turnover))
    cagr = tot ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(TD)
    return {"cagr": cagr, "volatility": vol,
            "sharpe": cagr / vol if vol else np.nan,
            "max_drawdown": float((s / s.cummax() - 1).min()),
            "final_multiple": tot}


def paired_t(a, b):
    d = (a.pct_change() - b.pct_change()).dropna()
    if len(d) < 3 or d.std(ddof=1) == 0:
        return np.nan
    return float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d))))


def main():
    assert not m2.ENABLE_COUNTRY_CAP, "the delivered model has the country cap off"
    px, sh, sec = load()
    simple = px.pct_change(axis=1).iloc[:, 1:]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]
    rebal = rebalance_dates(px.columns)
    print(f"universe {len(px)} | rebalances {len(rebal)} | "
          f"{rebal[0].date()} .. {rebal[-1].date()}")
    print(f"{FRONTIER_PTS}-point frontier per rebalance -> about "
          f"{len(rebal)*(FRONTIER_PTS+2)} solves\n")

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
        picks = frontier_at(est, sh, sec, elig)
        if picks is None:
            print(f"  {t.date()}  frontier infeasible - skipped")
            continue

        w_books = {}
        for prof, (pt, res) in picks.items():
            w = res["weights"]
            w_books[prof] = w[w > 1e-9]
        w_books["1/N Equal Weight"] = pd.Series(1.0 / len(elig), index=elig)

        for b, w in w_books.items():
            if holds[b] is not None:
                idx = sorted(set(w.index) | set(holds[b].index))
                turn[b].append(0.5 * float((w.reindex(idx).fillna(0)
                                            - holds[b].reindex(idx).fillna(0)).abs().sum()))
            holds[b] = w
            pt, res = picks.get(b, (None, None))
            records.append({
                "date": t.date(), "profile": b,
                "profile_rule": pr.PROFILE_RULES.get(b, "equal weight over the eligible universe"),
                "frontier_point": pt, "n_eligible": len(elig), "n_holdings": len(w),
                "predicted_return": res["portfolio_return"] if res else np.nan,
                "predicted_risk": res["portfolio_risk"] if res else np.nan,
                "weighted_esg": (res["esg_weighted"] if res else
                                 float((sh.loc[w.index, "ESG score"] * w).sum())),
                "solstatus": res["solstatus"] if res else "n/a - benchmark",
                "turnover": turn[b][-1] if turn[b] else np.nan,
            })

        nxt = rebal[i + 1] if i + 1 < len(rebal) else px.columns.max()
        seg = simple.columns[(simple.columns > t) & (simple.columns <= nxt)]
        for b, w in w_books.items():
            sub = simple.loc[w.index, seg].fillna(0.0)
            growth = (1.0 + sub).cumprod(axis=1)
            pv = (growth.T * w.values).sum(axis=1).values
            vals[b].extend(list(vals[b][-1] * pv))
        dates_out.extend(list(seg))

        neu_pt, neu = picks["Neutral"]
        ra_pt, ra = picks["Risk Averse"]
        rp_pt, rp = picks["Risk Prone"]
        print(f"  {t.date()}  elig {len(elig):4d} | pts RA={ra_pt} N={neu_pt} RP={rp_pt} | "
              f"Neutral ret {neu['portfolio_return']*100:6.2f}% risk "
              f"{neu['portfolio_risk']*100:5.2f}% n={len(w_books['Neutral']):3d}", flush=True)

    n = min(len(dates_out), min(len(v) for v in vals.values()))
    E = pd.DataFrame({b: vals[b][:n] for b in BOOKS},
                     index=pd.DatetimeIndex(dates_out[:n]))
    E = E[~E.index.duplicated()]

    rows = {b: stats(E[b]) for b in BOOKS}
    for b in pr.PROFILES:
        rows[f"{b} (after {COST_BPS}bp costs)"] = stats(E[b], COST_BPS, turn[b])
    S = pd.DataFrame(rows).T
    S.index.name = "profile"
    S["turnover_per_rebalance"] = [float(np.mean(turn[b.split(" (after")[0]]))
                                   if b.split(" (after")[0] in turn and
                                   turn[b.split(" (after")[0]] else np.nan
                                   for b in S.index]
    S.to_csv(f"{OUTDIR}/summary.csv")

    print("\n" + "=" * 100)
    print(f"OUT-OF-SAMPLE, CANONICAL PROFILES  {E.index[0].date()} .. {E.index[-1].date()}")
    print("=" * 100)
    print(S.round(4).to_string())

    # ---- gate ----
    g = stats(E["1/N Equal Weight"])
    gate = pd.DataFrame([{
        "metric": k,
        "script_21": v,
        "here": round(g[{"CAGR": "cagr", "vol": "volatility", "Sharpe": "sharpe"}[k]]
                      * (100 if k != "Sharpe" else 1), 3),
    } for k, v in GATE_REF.items()])
    gate["diff"] = gate["here"] - gate["script_21"]
    gate.to_csv(f"{OUTDIR}/gate.csv", index=False)
    print("\n--- GATE: the 1/N benchmark here vs script 21's published one ---")
    print(gate.to_string(index=False))
    worst = gate["diff"].abs().max()
    print(f"max |difference| {worst:.3f} -> "
          + ("harness agrees with script 21" if worst < 0.6 else "DISAGREES - investigate"))

    # ---- diagnostics ----
    R = pd.DataFrame(records)
    diag = []
    for b in pr.PROFILES:
        t_stat = paired_t(E[b], E["1/N Equal Weight"])
        pr_mean = R[R.profile == b]["predicted_risk"].mean()
        diag += [
            {"profile": b, "metric": "sharpe", "value": round(rows[b]["sharpe"], 4)},
            {"profile": b, "metric": "sharpe_minus_1N",
             "value": round(rows[b]["sharpe"] - rows["1/N Equal Weight"]["sharpe"], 4)},
            {"profile": b, "metric": "t_stat_vs_1N", "value": round(t_stat, 3)},
            {"profile": b, "metric": "significant_at_5pct", "value": float(abs(t_stat) > 1.96)},
            {"profile": b, "metric": "mean_predicted_risk", "value": round(pr_mean, 4)},
            {"profile": b, "metric": "realised_volatility",
             "value": round(rows[b]["volatility"], 4)},
            {"profile": b, "metric": "risk_understatement",
             "value": round(rows[b]["volatility"] / pr_mean - 1, 4)},
            {"profile": b, "metric": "turnover_per_rebalance",
             "value": round(float(np.mean(turn[b])), 4)},
        ]
    diag.append({"profile": "1/N Equal Weight", "metric": "sharpe",
                 "value": round(rows["1/N Equal Weight"]["sharpe"], 4)})
    pd.DataFrame(diag).to_csv(f"{OUTDIR}/diagnostics.csv", index=False)

    print("\n--- vs the 1/N benchmark ---")
    D = pd.DataFrame(diag)
    piv = D[D.metric.isin(["sharpe", "sharpe_minus_1N", "t_stat_vs_1N",
                           "risk_understatement", "turnover_per_rebalance"])] \
        .pivot(index="profile", columns="metric", values="value")
    print(piv.to_string())

    # ---- subperiods ----
    sub = []
    for label, regime, a, b_ in REGIMES + [("FULL", "whole test period",
                                            str(E.index[0].date()), str(E.index[-1].date()))]:
        seg = E.loc[(E.index >= a) & (E.index <= b_)]
        if len(seg) < 5:
            continue
        for bk in BOOKS:
            st = stats(seg[bk])
            sub.append({"period": label, "regime": regime, "profile": bk,
                        "cagr": round(st["cagr"], 4),
                        "volatility": round(st["volatility"], 4),
                        "max_drawdown": round(st["max_drawdown"], 4)})
    pd.DataFrame(sub).to_csv(f"{OUTDIR}/subperiods.csv", index=False)

    rowsE = [{"profile": b, "date": d.date(), "indexed_wealth": float(v)}
             for b in BOOKS for d, v in E[b].items()]
    pd.DataFrame(rowsE).to_csv(f"{OUTDIR}/equity_curves.csv", index=False)
    R.to_csv(f"{OUTDIR}/rebalances.csv", index=False)
    print(f"\nWrote 6 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
