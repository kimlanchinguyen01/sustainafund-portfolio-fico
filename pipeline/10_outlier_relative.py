"""
10 — Relative (per-stock) outlier detection
===========================================
Raised by Chi Chloe: 01c flags extreme daily moves with a FIXED 50% threshold,
which is scale-blind. A stock's own volatility is the right yardstick - a 20%
day in a utility is a far bigger anomaly than a 20% day in a biotech, yet the
fixed rule flags neither.

Switching to |r| > 5 * sigma_i (each stock's own daily std) fixes that. Note the
gain is mostly in one direction: the relative rule is much MORE sensitive for
low-volatility stocks, which is exactly where the fixed rule was blind.

The check in 01c is diagnostic only - it prints and nothing downstream consumes
it - so changing the rule cannot by itself move the frozen portfolio. The
question that CAN move it is different, and is the reason this runs now rather
than later:

    does the relative rule find moves that are DATA ERRORS rather than market
    events, in stocks the frozen portfolios actually hold?

An unadjusted split is the classic case and slips through a 50% rule: a 2:1
split is exactly -50%, a 3:2 split only -33%. So flagged moves are additionally
tested for split signatures (price ratio near a simple fraction, no reversal the
next day) and cross-referenced against the frozen holdings.

Runs on the frozen input, prices_clean_usd.csv, 10-year window.
"""

import numpy as np
import pandas as pd

TD = 252
FIXED = 0.50
K_SIGMA = 5.0
SPLIT_RATIOS = {"1:2": 0.5, "1:3": 1/3, "1:4": 0.25, "1:5": 0.2, "1:10": 0.1,
                "2:3": 2/3, "3:4": 0.75, "2:1": 2.0, "3:1": 3.0, "10:1": 10.0}

prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
px = prices.loc[:, end - pd.DateOffset(years=10):end]
r = np.log(px).diff(axis=1).iloc[:, 1:]
sh = pd.read_csv("shares_imputed.csv").set_index("Stock")

sd = r.std(axis=1)
print(f"Universe {len(r)} stocks | daily sigma: min {sd.min()*100:.2f}% "
      f"median {sd.median()*100:.2f}% max {sd.max()*100:.2f}%  "
      f"(annualised {sd.min()*np.sqrt(TD)*100:.0f}%..{sd.max()*np.sqrt(TD)*100:.0f}%)")

fixed_mask = r.abs() > FIXED
rel_mask = r.abs().gt(K_SIGMA * sd, axis=0)

print(f"\n{'rule':<28} {'flagged moves':>14} {'stocks':>8}")
print(f"{'fixed  |r| > 50%':<28} {int(fixed_mask.to_numpy().sum()):14d} "
      f"{int((fixed_mask.sum(axis=1) > 0).sum()):8d}")
print(f"{'relative  |r| > 5 sigma_i':<28} {int(rel_mask.to_numpy().sum()):14d} "
      f"{int((rel_mask.sum(axis=1) > 0).sum()):8d}")
both = (fixed_mask & rel_mask).to_numpy().sum()
print(f"{'in both':<28} {int(both):14d}")
print(f"{'fixed only (rel misses)':<28} {int((fixed_mask & ~rel_mask).to_numpy().sum()):14d}")
print(f"{'relative only (fixed missed)':<28} {int((~fixed_mask & rel_mask).to_numpy().sum()):14d}")

# Chloe's example: what the fixed rule misses in LOW-volatility names
print("\n" + "=" * 92)
print("WHAT THE FIXED RULE MISSED - largest moves under 50% but over 5 sigma")
print("=" * 92)
missed = (~fixed_mask & rel_mask)
recs = []
for s in r.index[missed.any(axis=1)]:
    days = r.columns[missed.loc[s]]
    for d in days:
        recs.append({"Stock": s, "date": d.date(), "move_%": r.loc[s, d] * 100,
                     "sigma_%": sd[s] * 100, "z": r.loc[s, d] / sd[s],
                     "ann_vol_%": sd[s] * np.sqrt(TD) * 100})
M = pd.DataFrame(recs)
print(f"total moves the fixed rule missed: {len(M)} across {M.Stock.nunique()} stocks")
print("\nlargest by |move| (these are big AND anomalous, and were not flagged):")
print(M.reindex(M["move_%"].abs().sort_values(ascending=False).index)
      .head(12).to_string(index=False))
print("\nmost anomalous by z-score:")
print(M.reindex(M.z.abs().sort_values(ascending=False).index).head(12).to_string(index=False))
print("\nlowest-volatility stocks among the missed (Chloe's utility case):")
print(M.sort_values("ann_vol_%").head(10).to_string(index=False))

# ---------------------------------------------------------------- split test
print("\n" + "=" * 92)
print("ARE ANY OF THESE DATA ERRORS? unadjusted-split signature test")
print("=" * 92)
all_flag = (fixed_mask | rel_mask)
cands = []
for s in r.index[all_flag.any(axis=1)]:
    row = px.loc[s]
    for d in r.columns[all_flag.loc[s]]:
        i = px.columns.get_loc(d)
        if i < 1 or i + 1 >= len(px.columns):
            continue
        p0, p1 = row.iloc[i - 1], row.iloc[i]
        if not (np.isfinite(p0) and np.isfinite(p1)) or p0 <= 0:
            continue
        ratio = p1 / p0
        nm, dist = min(((n, abs(ratio - v) / v) for n, v in SPLIT_RATIOS.items()),
                       key=lambda t: t[1])
        nxt = r.loc[s, px.columns[i + 1]] if i + 1 < len(px.columns) else np.nan
        # a genuine event partly reverses or persists noisily; a split does not
        reverses = np.isfinite(nxt) and np.sign(nxt) != np.sign(r.loc[s, d]) \
            and abs(nxt) > 0.3 * abs(r.loc[s, d])
        if dist < 0.03:
            cands.append({"Stock": s, "date": d.date(), "move_%": r.loc[s, d] * 100,
                          "ratio": round(float(ratio), 4), "looks_like": nm,
                          "rel_err_%": round(dist * 100, 2),
                          "next_day_%": round(float(nxt) * 100, 2) if np.isfinite(nxt) else None,
                          "reverses": bool(reverses)})
C = pd.DataFrame(cands)
if len(C):
    print(f"moves whose price ratio sits within 3% of a simple split ratio: {len(C)}")
    print(C.sort_values("rel_err_%").head(20).to_string(index=False))
    hard = C[~C.reverses]
    print(f"\n  of those, NOT reversed the next day (stronger split suspicion): {len(hard)}")
else:
    print("no flagged move has a clean split signature")

# ------------------------------------------------- do any touch the freeze?
print("\n" + "=" * 92)
print("THE QUESTION THAT MATTERS: does any of this touch the frozen portfolios?")
print("=" * 92)
held = {}
for prof in ["risk_averse", "neutral", "risk_prone"]:
    h = pd.read_csv(f"FROZEN_portfolio_{prof}.csv", index_col=0)
    for s in h.index:
        held.setdefault(s, []).append(prof)
print(f"distinct stocks across the three frozen portfolios: {len(held)}")

flagged_stocks = set(r.index[all_flag.any(axis=1)])
overlap = sorted(flagged_stocks & set(held))
print(f"frozen holdings with ANY flagged move: {len(overlap)}")
if overlap:
    rows = []
    for s in overlap:
        days = r.columns[all_flag.loc[s]]
        worst = max(days, key=lambda d: abs(r.loc[s, d]))
        rows.append({"Stock": s, "in": ",".join(held[s]), "n_flags": int(all_flag.loc[s].sum()),
                     "worst_%": round(float(r.loc[s, worst]) * 100, 1),
                     "date": worst.date(), "z": round(float(r.loc[s, worst] / sd[s]), 1),
                     "ann_vol_%": round(float(sd[s] * np.sqrt(TD) * 100), 1),
                     "split_suspect": s in set(C.Stock) if len(C) else False})
    print(pd.DataFrame(rows).sort_values("worst_%").to_string(index=False))
    susp = [x for x in rows if x["split_suspect"]]
    print(f"\n  of these, split-signature suspects: {len(susp)}"
          + (f" -> {[x['Stock'] for x in susp]}" if susp else " (none)"))
else:
    print("  none - no frozen holding has an extreme move under either rule")

M.to_csv("outlier_relative_missed.csv", index=False)
if len(C):
    C.to_csv("outlier_split_suspects.csv", index=False)
print("\nSaved outlier_relative_missed.csv"
      + (", outlier_split_suspects.csv" if len(C) else ""))
