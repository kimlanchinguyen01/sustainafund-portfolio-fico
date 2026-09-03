"""
34 — metrics the deck asks for that were not in the data bundle
===============================================================
`presentation_structure_EN.md.docx` specifies two NEW slides (S14 "What the
portfolio actually does" and S17 "The expected-return model forecasts
backwards") plus a stronger significance test on S16 and a tail-risk backup
slide. Those figures are NOT in `deck_data.json`, and the build brief's first
hard rule is never to invent a number.

So they are computed here, from committed backtest output only, and written to
`deck/data/derived_metrics.json` so every slide figure traces to a file.

WHAT REPRODUCED THE DOCX EXACTLY
  up / down capture           103.1% / 89.9%   (docx: 103% / 90%)
  longest underwater stretch  661 vs 396 trading days   (docx: 661 vs 396)
  Jobson-Korkie / Memmel z    -0.149 / +0.054 / +0.182  (docx: -0.15 / +0.05 / +0.18)
  predicted vs realised       corr -0.429, 47.27% -> 31.54%  (docx: -0.43, 47.3 -> 31.5)
  CVaR 95                     -1.75% vs -2.51%          (docx: same)

WHAT DID NOT
  The docx's recovery figures - "after 2022 it took 1,073 days to recover
  against the benchmark's 529, while after COVID it recovered in 104 against
  233" - do not reproduce under any definition tried: first-dip-to-recovery,
  trough-to-recovery, trading days or calendar days. Only the 529 matches
  anything, and it matches the Panel A stress-test recovery for 1/N after 2022,
  which is a different construction on a different book. They are recorded here
  as unreproducible and must not be printed. `recovery_alternatives` holds the
  figures that DO trace, if that slide still wants a recovery statistic.

A NOTE ON THE SIGNIFICANCE TEST
The docx is right that Jobson-Korkie with the Memmel correction is the correct
test for a difference of Sharpe ratios; a t-test on daily return differences is
not. It matters that it changes nothing: z of -0.149, +0.054 and +0.182 against
t of -0.87, +0.60 and +1.12. Both say the same thing, but the JK/Memmel version
cannot be attacked on the grounds that Sharpe differences are not normally
distributed.

Run:  python3 deck/34_derived_deck_metrics.py        # ~3 s, no solver
"""

import json
import os
from math import sqrt, erf

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data", "derived_metrics.json")

TD = 252
BOOKS = ["minvar", "mandate20", "mandate10", "equal_weight"]
BENCH = "equal_weight"

E = pd.read_csv(os.path.join(ROOT, "backtest_profiles/results/equity_curves.csv"),
                index_col=0, parse_dates=True)
R = pd.read_csv(os.path.join(ROOT, "backtest_profiles/results/rebalances.csv"))
R["date"] = pd.to_datetime(R["date"])


def capture_ratios():
    """Monthly up/down capture against 1/N. Averages hide this asymmetry."""
    M = E.resample("ME").last().pct_change().dropna()
    up, dn = M[M[BENCH] > 0], M[M[BENCH] < 0]
    out = {"n_up_months": int(len(up)), "n_down_months": int(len(dn)), "books": {}}
    for b in BOOKS:
        if b == BENCH:
            continue
        out["books"][b] = {
            "up_capture_pct": round(up[b].mean() / up[BENCH].mean() * 100, 1),
            "down_capture_pct": round(dn[b].mean() / dn[BENCH].mean() * 100, 1),
        }
    return out


def longest_underwater():
    """Maximum drawdown DURATION - the longest unbroken stretch below the running
    peak, in trading days. Not the total count of days below peak, which is a
    different and much larger number."""
    out = {}
    for b in BOOKS:
        s = E[b]
        below = (s < s.cummax() - 1e-12).values
        best = cur = 0
        for x in below:
            cur = cur + 1 if x else 0
            best = max(best, cur)
        out[b] = int(best)
    return {"unit": "trading days", "longest_underwater_stretch": out}


def recovery_alternatives():
    """Every recovery definition tried, so the slide can use one that traces."""
    out = {}
    for label, (a, bd) in {"COVID": ("2020-02-01", "2021-06-30"),
                           "2022": ("2022-01-01", "2025-12-31")}.items():
        out[label] = {}
        for b in ("minvar", BENCH):
            s = E[b]
            peak = s.loc[:a].max()
            seg = s.loc[a:bd]
            below = seg[seg < peak]
            if not len(below):
                out[label][b] = None
                continue
            trough = seg.idxmin()
            after = s.loc[trough:]
            rec = after[after >= peak]
            got = {}
            if len(rec):
                got["trough_to_recovery_trading_days"] = int(
                    s.index.get_loc(rec.index[0]) - s.index.get_loc(trough))
                got["trough_to_recovery_calendar_days"] = int((rec.index[0] - trough).days)
                got["first_dip_to_recovery_calendar_days"] = int(
                    (rec.index[0] - below.index[0]).days)
            out[label][b] = got
    return out


def jobson_korkie():
    """The correct test for a difference of Sharpe ratios (Memmel 2003)."""
    Rt = E.pct_change().dropna()
    rb, sb = Rt[BENCH].mean(), Rt[BENCH].std(ddof=1)
    sh_b = rb / sb
    n = len(Rt)
    out = {"n_observations": int(n), "frequency": "daily",
           "test": "Jobson-Korkie with the Memmel (2003) correction", "books": {}}
    for b in BOOKS:
        if b == BENCH:
            continue
        ra, sa = Rt[b].mean(), Rt[b].std(ddof=1)
        sh_a = ra / sa
        rho = float(Rt[b].corr(Rt[BENCH]))
        theta = (1 / n) * (2 - 2 * rho + 0.5 * (sh_a ** 2 + sh_b ** 2
                                                - 2 * sh_a * sh_b * rho ** 2))
        z = (sh_a - sh_b) / sqrt(theta)
        p = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
        out["books"][b] = {"z": round(z, 3), "p_two_sided": round(p, 3),
                           "correlation_with_benchmark": round(rho, 3),
                           "significant_at_5pct": bool(abs(z) > 1.96)}
    return out


def predicted_vs_realised():
    """Does the model's own return forecast predict what it then earns?"""
    dates = sorted(R.date.unique())
    out = {"n_rebalances": None, "books": {}}
    for book in ("minvar", "mandate20", "mandate10"):
        sub = R[R.book == book].set_index("date")
        rows = []
        for i, d in enumerate(dates):
            if d not in sub.index:
                continue
            nxt = dates[i + 1] if i + 1 < len(dates) else E.index[-1]
            seg = E[book].loc[(E.index > d) & (E.index <= nxt)]
            if len(seg) < 5:
                continue
            start = E[book].asof(d)
            yrs = (seg.index[-1] - d).days / 365.25
            if yrs <= 0:
                continue
            rows.append({"pred": float(sub.loc[d, "pred_return_%"]),
                         "real": ((seg.iloc[-1] / start) ** (1 / yrs) - 1) * 100})
        D = pd.DataFrame(rows).dropna()
        n = len(D)
        r = float(D.pred.corr(D.real))
        t = r * sqrt((n - 2) / (1 - r ** 2))
        # exact two-sided p from Student's t with n-2 df, by numerical integration
        df = n - 2
        xs = np.linspace(0, abs(t) * 8 + 40, 400001)
        pdf = (1 + xs ** 2 / df) ** (-(df + 1) / 2)
        pdf /= np.trapezoid(pdf, xs) * 2
        tail = 2 * (0.5 - np.trapezoid(pdf[xs <= abs(t)], xs[xs <= abs(t)]))
        out["n_rebalances"] = int(n)
        out["books"][book] = {
            "correlation_predicted_vs_realised": round(r, 3),
            "t": round(t, 2), "p_two_sided": round(float(tail), 3),
            "mean_predicted_return_pct": round(float(D.pred.mean()), 2),
            "mean_realised_return_pct": round(float(D.real.mean()), 2),
        }
    return out


def tail_risk():
    Rt = E.pct_change().dropna()
    out = {}
    for b in BOOKS:
        q = Rt[b].quantile(0.05)
        out[b] = {"var95_pct": round(float(q) * 100, 2),
                  "cvar95_pct": round(float(Rt[b][Rt[b] <= q].mean()) * 100, 2)}
    return {"definition": "daily; CVaR95 is the mean of the worst 5% of days",
            "books": out}


def main():
    payload = {
        "_README": ("Figures the presentation needs that were absent from "
                    "deck_data.json. Computed from committed backtest output by "
                    "deck/34_derived_deck_metrics.py. Percentages are in PERCENT "
                    "here to match deck_data.json's convention, not decimals."),
        "_source": "backtest_profiles/results/{equity_curves,rebalances}.csv",
        "capture": capture_ratios(),
        "underwater": longest_underwater(),
        "significance_jobson_korkie": jobson_korkie(),
        "predicted_vs_realised": predicted_vs_realised(),
        "tail_risk": tail_risk(),
        "recovery_alternatives": recovery_alternatives(),
        "_UNREPRODUCIBLE_DO_NOT_PRINT": {
            "docx_claim": ("after 2022 minvar recovered in 1,073 days vs the "
                           "benchmark's 529; after COVID 104 vs 233"),
            "status": ("not reproducible under first-dip-to-recovery, "
                       "trough-to-recovery, trading days or calendar days. Only "
                       "529 matches anything: the Panel A stress-test recovery "
                       "for 1/N after 2022, a different construction on a "
                       "different book. Use recovery_alternatives instead, or "
                       "drop the element."),
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)

    c = payload["capture"]["books"]["mandate20"]
    jk = payload["significance_jobson_korkie"]["books"]
    pv = payload["predicted_vs_realised"]["books"]
    uw = payload["underwater"]["longest_underwater_stretch"]
    print("wrote", os.path.relpath(OUT, ROOT))
    print(f"  capture (mandate20)      up {c['up_capture_pct']}%  down {c['down_capture_pct']}%")
    print(f"  longest underwater       minvar {uw['minvar']}  1/N {uw['equal_weight']} trading days")
    print(f"  Jobson-Korkie z          " + "  ".join(
        f"{k} {v['z']:+.3f}" for k, v in jk.items()))
    print(f"  pred vs realised corr    " + "  ".join(
        f"{k} {v['correlation_predicted_vs_realised']:+.3f} (p={v['p_two_sided']})"
        for k, v in pv.items()))
    print(f"  CVaR95                   " + "  ".join(
        f"{k} {v['cvar95_pct']}%" for k, v in payload["tail_risk"]["books"].items()))
    print("  recovery figures from the docx: NOT reproducible - flagged in the JSON")


if __name__ == "__main__":
    main()
