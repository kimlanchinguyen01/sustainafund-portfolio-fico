"""
SustainaFund — 26b: what option B would have concluded
======================================================
Option B was "split history into 3 chunks, re-optimise at 2 rebalance points,
hold fixed between them". It was not run as the deliverable because the full
walk-forward (31 rebalances) already existed and B carries the same estimation
machinery with 1/15th of the sample.

That is an argument. This is the test of it.

B is run here properly, and run TWICE with different split dates - both
defensible a priori, neither cherry-picked - plus a third scheme with 3
rebalance points. If B were a sound protocol on this data, the three should
agree with each other and with the 31-rebalance answer.

Everything else is identical to 26_backtest_profiles.py: same prices, same
3-year trailing estimation, same eligibility, same ESG floor, same buy-and-hold
convention, same books.

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 4_backtest/code/26b_why_not_option_b.py       # ~3 min
"""

import os
import sys
import importlib.util
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)                    # <repo>/<part>
ROOT = os.path.dirname(PART)                    # <repo>
sys.path.insert(0, os.path.join(ROOT, "2_optimisation_model", "code"))

# reuse script 26's helpers rather than re-implementing them, so the two cannot
# disagree about estimation, eligibility or statistics
spec = importlib.util.spec_from_file_location(
    "bt26", os.path.join(HERE, "26_backtest_profiles.py"))
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)

BOOKS = ["minvar", "mandate20", "equal_weight"]

# Three split schemes. The first two give B exactly what it asked for - two
# rebalance points, three chunks - and differ only in where the boundaries fall.
SCHEMES = {
    "B: split 2019-12 / 2022-12": ["2019-12-31", "2022-12-31"],
    "B: split 2020-06 / 2023-06": ["2020-06-30", "2023-06-30"],
    "B+: 3 points, yearly-ish":   ["2019-12-31", "2021-12-31", "2023-12-31"],
}


def run_scheme(px, simple, rets, sh, sec, split_dates):
    cols = px.columns
    rebal = [cols[cols.searchsorted(pd.Timestamp(d), "left")] for d in split_dates]
    vals = {b: [1.0] for b in BOOKS}
    dates_out = [rebal[0]]
    preds = {b: [] for b in BOOKS}

    for i, t in enumerate(rebal):
        est, elig = bt.estimate(rets, sh, t)
        if est is None:
            return None, f"only {len(elig)} eligible at {t.date()}"
        solved = bt.solve_books(est, sh, sec, elig)
        if "minvar" not in solved or "mandate20" not in solved:
            return None, f"infeasible at {t.date()}"

        w_books = {b: solved[b]["weights"][solved[b]["weights"] > 1e-9]
                   for b in ("minvar", "mandate20")}
        w_books["equal_weight"] = pd.Series(1.0 / len(elig), index=elig)
        for b in ("minvar", "mandate20"):
            preds[b].append(solved[b]["portfolio_risk"] * 100)

        nxt = rebal[i + 1] if i + 1 < len(rebal) else cols.max()
        seg = simple.columns[(simple.columns > t) & (simple.columns <= nxt)]
        for b, w in w_books.items():
            sub = simple.loc[w.index, seg].fillna(0.0)
            growth = (1.0 + sub).cumprod(axis=1)
            pv = (growth.T * w.values).sum(axis=1).values
            vals[b].extend(list(vals[b][-1] * pv))
        dates_out.extend(list(seg))

    n = min(len(dates_out), min(len(v) for v in vals.values()))
    E = pd.DataFrame({b: vals[b][:n] for b in BOOKS},
                     index=pd.DatetimeIndex(dates_out[:n]))
    E = E[~E.index.duplicated()]
    return E, preds


def main():
    px, sh, sec = bt.load()
    simple = px.pct_change(axis=1).iloc[:, 1:]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]

    rows = []
    for label, splits in SCHEMES.items():
        print(f"\n--- {label} ---", flush=True)
        E, preds = run_scheme(px, simple, rets, sh, sec, splits)
        if E is None:
            print(f"  not runnable: {preds}")
            continue
        st = {b: bt.stats(E[b]) for b in BOOKS}
        for b in ("minvar", "mandate20"):
            t_stat, _ = bt.paired_t(E[b], E["equal_weight"])
            d_sharpe = st[b]["Sharpe"] - st["equal_weight"]["Sharpe"]
            rows.append({
                "scheme": label, "rebalances": len(splits), "book": b,
                "from": E.index[0].date(), "to": E.index[-1].date(),
                "CAGR_%": round(st[b]["CAGR_%"], 2),
                "vol_%": round(st[b]["vol_%"], 2),
                "Sharpe": round(st[b]["Sharpe"], 3),
                "eq_Sharpe": round(st["equal_weight"]["Sharpe"], 3),
                "d_Sharpe": round(d_sharpe, 3),
                "t": round(t_stat, 2),
                "maxDD_%": round(st[b]["maxDD_%"], 2),
                "eq_maxDD_%": round(st["equal_weight"]["maxDD_%"], 2),
                "verdict": "beats 1/N" if d_sharpe > 0 else "loses to 1/N",
            })
            print(f"  {b:10s} Sharpe {st[b]['Sharpe']:.3f} vs 1/N "
                  f"{st['equal_weight']['Sharpe']:.3f}  -> {rows[-1]['verdict']}"
                  f"  (t={t_stat:+.2f})")

    B = pd.DataFrame(rows)
    out = os.path.join(PART, "results", "profiles", "option_b_comparison.csv")
    B.to_csv(out, index=False)

    print("\n" + "=" * 96)
    print("WHAT OPTION B WOULD HAVE CONCLUDED, BY WHERE YOU HAPPEN TO SPLIT")
    print("=" * 96)
    print(B[["scheme", "book", "Sharpe", "eq_Sharpe", "d_Sharpe", "t",
             "maxDD_%", "eq_maxDD_%", "verdict"]].to_string(index=False))

    print("\n--- does B agree with itself? ---")
    for b in ("minvar", "mandate20"):
        v = B[B.book == b]
        agree = v["verdict"].nunique() == 1
        print(f"  {b:10s} verdicts: {sorted(set(v['verdict']))} -> "
              + ("consistent" if agree else "CONTRADICTORY"))
        print(f"             d_Sharpe range {v['d_Sharpe'].min():+.3f} .. "
              f"{v['d_Sharpe'].max():+.3f}  (spread {v['d_Sharpe'].max()-v['d_Sharpe'].min():.3f})")

    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
