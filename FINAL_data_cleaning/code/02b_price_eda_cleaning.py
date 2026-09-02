import pandas as pd
import numpy as np

prices = pd.read_csv('stockprices_full.csv')
prices = prices.set_index('Stock')
prices.columns = pd.to_datetime(prices.columns)

# 1. Non-positive prices (would break log-returns entirely)
bad_prices = (prices <= 0).sum().sum()
print(f"Non-positive prices in raw data: {bad_prices}")

# 2. Separate late-IPO stocks from stocks with genuine internal gaps
first_valid = prices.apply(lambda row: row.first_valid_index(), axis=1)
late_start = (first_valid > prices.columns.min()).sum()
print(f"\nStocks starting later than the dataset's first date (IPO/spin-off): {late_start}")

# [FIX 2026-08-31] The original version measured `after.isna().sum()`, i.e. the
# TOTAL COUNT of missing days per stock, and then described it as "gap length".
# Those are different quantities: a stock with three separate 1-day gaps would
# be reported as a single "3-day gap". Measuring CONSECUTIVE runs instead.
# The conclusion is unchanged (all runs are exactly 1 day) - but it is now
# actually the quantity the forward-fill decision depends on.
run_lengths = {}
affected = []
for stock in prices.index:
    fv = first_valid[stock]
    if fv is None:
        continue
    isna = prices.loc[stock, fv:].isna().values
    runs, c = [], 0
    for v in isna:
        if v:
            c += 1
        elif c:
            runs.append(c); c = 0
    if c:
        runs.append(c)
    if runs:
        affected.append(stock)
        run_lengths[stock] = runs

all_runs = pd.Series([n for runs in run_lengths.values() for n in runs])
print(f"\nStocks with genuine internal gaps (post-listing): {len(affected)}")
print(f"Total consecutive gap runs: {len(all_runs)}")

# 3. THE KEY CHECK: how long are these gaps? Short (holiday-like) vs long
#    (suspended trading) call for different treatment.
if len(all_runs) > 0:
    print("\nGap RUN length distribution (consecutive trading days):")
    print(all_runs.value_counts().sort_index().to_string())
    print(f"\nLongest single gap run: {all_runs.max()} trading day(s)")

    long_runs = {s: r for s, r in run_lengths.items() if max(r) > 3}
    print(f"Stocks with any run > 3 days (forward-fill would distort risk): {len(long_runs)}")
else:
    print("\nNo genuine internal gaps found.")

# result: all internal gaps are exactly 1 trading day -> forward-fill is safe.
# (verified on consecutive runs, not on per-stock totals)
