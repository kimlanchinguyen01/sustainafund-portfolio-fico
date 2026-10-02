"""
13 — Truncate price history at trading discontinuities
=====================================================
Two stocks in the universe contain a boundary across which a return is not a
return: the security before and after is not the same claim.

  ZEG.L    17 identical closing prices (2023-10-20 .. 2023-11-13), then +352%.
           Reverse takeover of Vodafone Spain: the listing was cancelled and
           re-admitted, and the equity was massively diluted. A holder did NOT
           gain 352% - the share count changed, so price ratio != return.
  BMPS.MI  219 identical closing prices ending 2017-10-24, then -69.8%. The
           2016-17 Monte dei Paschi recapitalisation with burden-sharing and
           state aid. Same problem, and the 219 zero-return days additionally
           understate its sigma - the failure mode 01c warns about.

Neither is a "bad price": the quoted levels are correct on both sides. What is
wrong is computing a log-return across the boundary.

Rule, applied uniformly and NOT conditioned on whether a stock is held:
    a discontinuity is a run of >= FREEZE_MIN identical closing prices followed
    by a move of more than JUMP_MIN; history starts after the LAST one.

Detection runs on LOCAL-currency prices. In USD a frozen local price is not
frozen, because the daily FX rate keeps moving - the detector would miss it.

Truncated stocks keep their post-discontinuity history and re-enter as recent
listings; the factor model fits betas on whatever days a stock has, so this costs
nothing and is better than dropping them (ZEG.L keeps 530 usable days).
"""

from paths import P   # where each data file lives (see paths.py)

import numpy as np
import pandas as pd

FREEZE_MIN = 10
JUMP_MIN = 0.30
MIN_KEEP = 252

loc = pd.read_csv(P("prices_clean.csv"), index_col=0)
usd = pd.read_csv(P("prices_clean_usd.csv"), index_col=0)
loc.columns = pd.to_datetime(loc.columns)
usd.columns = pd.to_datetime(usd.columns)
assert list(loc.index) == list(usd.index) and list(loc.columns) == list(usd.columns)


def discontinuities(series):
    """All (freeze_end_date, run_length, jump) meeting the rule, in time order."""
    v = series.dropna()
    if len(v) < 3:
        return []
    a = v.values
    out, run = [], 1
    for i in range(1, len(a)):
        if a[i] == a[i - 1]:
            run += 1
            continue
        if run >= FREEZE_MIN:
            jump = a[i] / a[i - 1] - 1
            if abs(jump) > JUMP_MIN:
                out.append((v.index[i], run, float(jump)))
        run = 1
    return out


print(f"Rule: run of >= {FREEZE_MIN} identical local closes, then |move| > {JUMP_MIN*100:.0f}%")
print("=" * 88)
hits = {}
for s in loc.index:
    d = discontinuities(loc.loc[s])
    if d:
        hits[s] = d
print(f"stocks with at least one discontinuity: {len(hits)} of {len(loc)}\n")

held = set()
for p in ["risk_averse", "neutral", "risk_prone"]:
    held |= set(pd.read_csv(P(f"FROZEN_v2_portfolio_{p}.csv"), index_col=0).index)

usd_out = usd.copy()
rows = []
for s, ds in hits.items():
    for dt, run, jump in ds:
        print(f"  {s:<10} freeze {run:>3} days -> {dt.date()}  jump {jump*100:+7.1f}%")
    dt_last = ds[-1][0]
    before = int(usd.loc[s].notna().sum())
    usd_out.loc[s, usd.columns < dt_last] = np.nan
    after = int(usd_out.loc[s].notna().sum())
    rows.append({"Stock": s, "n_discont": len(ds), "history_starts": dt_last.date(),
                 "days_before": before, "days_after": after,
                 "usable": after >= MIN_KEEP, "was_held": s in held})
    print(f"  {' ':<10} -> history truncated to {dt_last.date()}: "
          f"{before} -> {after} days ({'usable' if after >= MIN_KEEP else 'TOO SHORT'})"
          f"{'  [was held]' if s in held else ''}\n")

T = pd.DataFrame(rows)
print(T.to_string(index=False))
drop = T[~T.usable].Stock.tolist()
if drop:
    print(f"\nstocks left with under {MIN_KEEP} days and therefore unusable: {drop}")
    usd_out = usd_out.drop(index=drop)

# validation: nothing else touched
untouched = [s for s in usd.index if s not in hits]
assert usd_out.loc[untouched].equals(usd.loc[untouched]), "a non-flagged stock changed"
print(f"\nvalidation: all {len(untouched)} non-flagged stocks byte-identical")
print(f"universe: {len(usd)} -> {len(usd_out)} stocks "
      f"(ZEG.L returns to the universe; it was dropped entirely in v2 of the freeze)")

usd_out.to_csv(P("prices_clean_usd_v3.csv"))
T.to_csv(P("discontinuities_found.csv"), index=False)
print("\nSaved prices_clean_usd_v3.csv, discontinuities_found.csv")
