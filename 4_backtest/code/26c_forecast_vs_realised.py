"""
26c: expected vs realised return in the walk-forward backtest
==============================================================
Reads only the saved outputs of 26_backtest_profiles.py (no solver, no price file).

At each of the 31 rebalances the optimiser reports the return it expects
(`pred_return_%` in results/profiles/rebalances.csv). This script compares it with the
annualised return the book actually earned from that rebalance to the next one
(last window: to the end of the sample), using results/profiles/equity_curves.csv.

Outputs (4_backtest/results/profiles/):
  forecast_vs_realised.csv       one row per book: n, Pearson r, p-value, mean expected, mean realised
  forecast_vs_realised_detail.csv  one row per book and rebalance

Used in the report: Section 3.3.4 (correlation -0.43, p = 0.016 for the 20% mandate,
-0.22 not significant for minimum variance) and Figure 3.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results", "profiles")
BOOKS = ["minvar", "mandate20", "mandate10"]

eq = pd.read_csv(os.path.join(RES, "equity_curves.csv"), index_col=0, parse_dates=True)
rb = pd.read_csv(os.path.join(RES, "rebalances.csv"), parse_dates=["date"])


def first_on_or_after(d):
    i = eq.index.get_indexer([d], method="bfill")[0]
    return eq.index[i] if i >= 0 else eq.index[-1]


summary, detail = [], []
for book in BOOKS:
    d = rb[rb["book"] == book].sort_values("date")
    edges = list(d["date"]) + [eq.index[-1]]
    expected, realised = [], []
    for a, b, pred in zip(edges[:-1], edges[1:], d["pred_return_%"]):
        a, b = first_on_or_after(a), first_on_or_after(b)
        years = (b - a).days / 365.25                      # calendar-day annualisation
        r = ((eq.loc[b, book] / eq.loc[a, book]) ** (1 / years) - 1) * 100
        expected.append(pred)
        realised.append(r)
        detail.append({"book": book, "rebalance": a.date(), "next": b.date(),
                       "expected_%": pred, "realised_%": r})
    x, y = np.array(expected), np.array(realised)
    r, p = stats.pearsonr(x, y)
    summary.append({"book": book, "n": len(x), "pearson_r": r, "p_value": p,
                    "mean_expected_%": x.mean(), "mean_realised_%": y.mean()})

S = pd.DataFrame(summary)
S.to_csv(os.path.join(RES, "forecast_vs_realised.csv"), index=False)
pd.DataFrame(detail).to_csv(os.path.join(RES, "forecast_vs_realised_detail.csv"), index=False)
print(S.round(3).to_string(index=False))
