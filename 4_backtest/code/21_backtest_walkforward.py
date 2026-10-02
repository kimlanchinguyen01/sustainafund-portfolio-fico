"""
21 — Walk-forward backtest of Model 2 (option A, tightly scoped)

Constraint set matches Main_model.py as of 3 Sep, including the per-stock
ESG floor of 30 that Chloe added.
================================================================
Protocol
--------
Rolling 3-year estimation window, quarterly rebalance, buy-and-hold in between.
At each rebalance date t:
    1. estimate on the trailing 3 years, using ONLY data strictly before t
    2. eligible universe = stocks with a complete price history inside that
       window (you cannot buy what has no history - here this is realism, not
       the complete-case defect we fixed for the static model)
    3. mu = annualised mean log-return, Sigma = Ledoit-Wolf shrunk sample
       covariance, both as Chloe specified - deliberately NOT the James-Stein /
       20-factor pipeline, which would be re-estimated 32 times for no gain here
    4. solve Model 2's constraint set for MINIMUM VARIANCE
    5. hold those weights until the next rebalance; weights drift with prices,
       as a real portfolio does

Minimum variance rather than a target-return point because a target return is
arbitrary and, worse, not comparable across regimes: the same beta is easy in
2021 and infeasible in 2018. Min-variance needs no free parameter.

Benchmark: 1/N over the SAME eligible universe at each rebalance, so the
comparison isolates the optimiser rather than the universe.

Prices are dividend-adjusted. This is not optional for a backtest - a closing
price omits dividends and would understate every strategy's realised return,
the high-yield names most of all.

THREE LIMITATIONS, none of them fixable with this dataset
---------------------------------------------------------
1. ESG scores and sectors are a single present-day snapshot. Applying ESG >= 70
   at a 2018 rebalance uses information from 2025. This is look-ahead and it
   cannot be removed without a historical ESG panel. Reported, not hidden.
2. The universe is today's STOXX 600 / S&P 500 constituents, so it is
   survivorship-biased by construction: companies that failed or were delisted
   are absent. Realised returns are therefore optimistic for every strategy
   here, benchmark included.
3. No transaction costs in the optimisation. Turnover is measured and a cost
   sensitivity is applied afterwards.
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

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import xpress as xp

TD = 252
WINDOW_Y = 3
W_MIN, W_MAX, REGION_CAP, MIN_STOCKS, ESG_MIN, SECTOR_CAP = 0.01, 0.20, 0.60, 30, 70.0, 0.30
ESG_FLOOR = 30.0        # per-stock floor added by Chloe: no single holding below this
MIP_GAP, TIME_LIMIT = 0.001, 120
COST_BPS = 10          # one-way transaction cost applied in the sensitivity

prices = pd.read_csv(os.path.join(PREP_RESULTS, "prices_div_usd.csv"), index_col=0)
prices.columns = pd.to_datetime(prices.columns)
sh = pd.read_csv(os.path.join(MODEL_DATA, "shares_imputed.csv")).set_index("Stock")
sec = pd.read_excel(os.path.join(MODEL_DATA, "sectors.xlsx")).set_index("Stock")["Sector"]
common = [s for s in prices.index if s in sh.index and s in sec.index]
prices = prices.loc[common]
print(f"universe {len(prices)} | {prices.columns.min().date()} .. {prices.columns.max().date()}")

rets = np.log(prices).diff(axis=1).iloc[:, 1:]
simple = prices.pct_change(axis=1).iloc[:, 1:]

# quarterly rebalance dates, first one once a full window exists
start = prices.columns.min() + pd.DateOffset(years=WINDOW_Y)
qs = pd.date_range(start, prices.columns.max(), freq="QE")
rebal = [prices.columns[prices.columns.searchsorted(d, "left")] for d in qs]
rebal = sorted(set(d for d in rebal if d < prices.columns.max()))
print(f"rebalance dates: {len(rebal)} | first {rebal[0].date()} | last {rebal[-1].date()}")


def solve_minvar(mu, Sigma, region, esg, sector):
    n = len(mu)
    p = xp.problem(); p.controls.outputlog = 0
    p.controls.miprelstop = MIP_GAP; p.controls.timelimit = TIME_LIMIT
    w = p.addVariables(n, lb=0, ub=W_MAX, name="w")
    y = p.addVariables(n, vartype=xp.binary, name="y")
    p.addConstraint(w <= W_MAX * y); p.addConstraint(w >= W_MIN * y)
    p.addConstraint(xp.Sum(w) == 1); p.addConstraint(xp.Sum(y) >= MIN_STOCKS)
    for r in np.unique(region): p.addConstraint(xp.Sum(w[region == r]) <= REGION_CAP)
    for s_ in np.unique(sector): p.addConstraint(xp.Sum(w[sector == s_]) <= SECTOR_CAP)
    p.addConstraint(xp.Dot(esg, w) >= ESG_MIN)
    p.setObjective(xp.Dot(w, Sigma, w), sense=xp.minimize)
    _, st = p.optimize()
    if st.name not in ("OPTIMAL", "FEASIBLE"): return None
    return np.array(p.getSolution(w))


records, hold_opt, hold_eq, turn = [], None, None, []
val_opt, val_eq = [1.0], [1.0]
dates_out = [rebal[0]]

for i, t in enumerate(rebal):
    w_start = t - pd.DateOffset(years=WINDOW_Y)
    win = rets.loc[:, (rets.columns >= w_start) & (rets.columns < t)]     # strictly before t
    ok = win.notna().all(axis=1)
    elig = [s for s in win.index[ok]]
    # per-stock ESG floor, applied to the eligible set exactly as load_data does
    elig = [s for s in elig if sh.loc[s, "ESG score"] >= ESG_FLOOR]
    if len(elig) < MIN_STOCKS + 20:
        print(f"  {t.date()}  only {len(elig)} eligible - skipped")
        continue
    R = win.loc[elig]
    mu = R.mean(axis=1).values * TD
    Sigma = LedoitWolf().fit(R.T.values).covariance_ * TD
    reg = sh.loc[elig, "Region"].values
    esg = sh.loc[elig, "ESG score"].values.astype(float)
    scv = sec.loc[elig].values
    w = solve_minvar(mu, Sigma, reg, esg, scv)
    if w is None:
        print(f"  {t.date()}  infeasible - skipped")
        continue
    w = pd.Series(w, index=elig)
    w = w[w > 1e-9]
    eq = pd.Series(1.0 / len(elig), index=elig)

    if hold_opt is not None:
        idx = sorted(set(w.index) | set(hold_opt.index))
        turn.append(0.5 * float((w.reindex(idx).fillna(0) - hold_opt.reindex(idx).fillna(0)).abs().sum()))
    hold_opt, hold_eq = w, eq

    nxt = rebal[i + 1] if i + 1 < len(rebal) else prices.columns.max()
    seg = simple.columns[(simple.columns > t) & (simple.columns <= nxt)]
    for pf, holder, vals in (("opt", w, val_opt), ("eq", eq, val_eq)):
        sub = simple.loc[holder.index, seg].fillna(0.0)
        # buy-and-hold: value of each position compounds, so weights drift
        growth = (1.0 + sub).cumprod(axis=1)
        pv = (growth.T * holder.values).sum(axis=1).values
        base = vals[-1]
        vals.extend(list(base * pv))
    dates_out.extend(list(seg))
    records.append({"date": t, "n_eligible": len(elig), "n_held": len(w),
                    "pred_risk_%": float(np.sqrt(w.values @ Sigma[np.ix_([elig.index(s) for s in w.index],
                                                                        [elig.index(s) for s in w.index])] @ w.values)) * 100,
                    "esg": float((sh.loc[w.index, "ESG score"] * w).sum()),
                    "turnover_%": turn[-1] * 100 if turn else np.nan})
    print(f"  {t.date()}  eligible {len(elig):4d} | held {len(w):3d} | "
          f"pred risk {records[-1]['pred_risk_%']:5.2f}% | ESG {records[-1]['esg']:.1f}"
          + (f" | turnover {turn[-1]*100:5.1f}%" if turn else ""))

E = pd.DataFrame({"optimised": val_opt[:len(dates_out)], "equal_weight": val_eq[:len(dates_out)]},
                 index=pd.DatetimeIndex(dates_out[:len(val_opt)]))
E = E[~E.index.duplicated()]


def stats(s, cost_bps=0.0, turnover=None):
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    tot = s.iloc[-1] / s.iloc[0]
    if cost_bps and turnover:
        tot *= (1 - cost_bps / 1e4) ** (2 * sum(turnover))
    cagr = tot ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(TD)
    dd = float((s / s.cummax() - 1).min())
    return {"CAGR_%": cagr * 100, "vol_%": vol * 100, "Sharpe": cagr / vol,
            "maxDD_%": dd * 100, "final_x": tot}


print("\n" + "=" * 88)
print(f"OUT-OF-SAMPLE RESULTS  {E.index[0].date()} .. {E.index[-1].date()} "
      f"({(E.index[-1]-E.index[0]).days/365.25:.1f} years, {len(records)} rebalances)")
print("=" * 88)
rows = {"Model 2 (min-variance)": stats(E.optimised),
        "1/N benchmark": stats(E.equal_weight),
        f"Model 2 after {COST_BPS}bp costs": stats(E.optimised, COST_BPS, turn)}
S = pd.DataFrame(rows).T
print(S.round(3).to_string())
print(f"\nSharpe uses a zero risk-free rate. Turnover per rebalance: "
      f"mean {np.mean(turn)*100:.1f}%, total {sum(turn)*100:.0f}% over {len(turn)} rebalances.")
print(f"Cost row applies {COST_BPS}bp one-way on measured turnover.")

OUT21 = os.path.join(PART, "results", "min_variance")
os.makedirs(OUT21, exist_ok=True)
pd.DataFrame(records).to_csv(os.path.join(OUT21, "backtest_rebalances.csv"), index=False)
E.to_csv(os.path.join(OUT21, "backtest_equity_curves.csv"))
S.to_csv(os.path.join(OUT21, "backtest_summary.csv"))
print("\nSaved backtest_rebalances.csv, backtest_equity_curves.csv, backtest_summary.csv")
