import pandas as pd
import numpy as np

# Load raw data (before dropping any missing ESG rows)
shares = pd.read_csv('shares_full.csv')
prices = pd.read_csv('stockprices_full.csv')
prices = prices.set_index('Stock')
prices.columns = pd.to_datetime(prices.columns)
print(f"Shares: {shares.shape[0]} stocks")
print(f"Prices: {prices.shape[0]} stocks, {prices.shape[1]} trading days")

#2. Measure the missing-ESG rate, broken down by region
n_missing = shares['ESG score'].isna().sum()
print(f"\nMissing ESG: {n_missing} / {len(shares)} ({n_missing/len(shares)*100:.1f}%)")

missing_by_region = shares[shares['ESG score'].isna()].groupby('Region')['Stock'].count()
total_by_region = shares.groupby('Region')['Stock'].count()
print("Missing rate by region (%):")
print((missing_by_region / total_by_region * 100).round(1))
# Quick-and-temporary return/risk calc, just for this diagnostic
# (not the final estimation - that comes later in the main pipeline)
log_prices = np.log(prices)
daily_returns = log_prices.diff(axis=1)

exp_return = daily_returns.mean(axis=1, skipna=True) * 252
risk = daily_returns.std(axis=1, skipna=True) * np.sqrt(252)

# Split stocks into the two groups
missing_stocks = shares[shares['ESG score'].isna()]['Stock'].tolist()
present_stocks = shares[shares['ESG score'].notna()]['Stock'].tolist()

print(f"Missing-ESG group: {len(missing_stocks)} stocks")
print(f"Has-ESG group: {len(present_stocks)} stocks")

print("\n--- Return comparison ---")
print(f"Missing-ESG group: mean return = {exp_return[missing_stocks].mean():.4f}, "
      f"median = {exp_return[missing_stocks].median():.4f}")
print(f"Has-ESG group:     mean return = {exp_return[present_stocks].mean():.4f}, "
      f"median = {exp_return[present_stocks].median():.4f}")

print("\n--- Risk comparison ---")
print(f"Missing-ESG group: mean risk = {risk[missing_stocks].mean():.4f}")
print(f"Has-ESG group:     mean risk = {risk[present_stocks].mean():.4f}")

# Also check: is the missing pattern concentrated in specific countries?
missing_countries = shares[shares['ESG score'].isna()]['Country'].value_counts()
print("\n--- Which countries have the missing ESG stocks? ---")
print(missing_countries)

# Conservative imputation: use the 25th percentile of ESG within each
# region, not the mean/median - this avoids rewarding missing data with an optimistic score, appropriate for an ESG-focused fund
region_p25 = shares.groupby('Region')['ESG score'].quantile(0.25)
print("25th percentile ESG by region (used for imputation):")
print(region_p25)

shares_imputed = shares.copy()
mask = shares_imputed['ESG score'].isna()
shares_imputed.loc[mask, 'ESG score'] = shares_imputed.loc[mask, 'Region'].map(region_p25)

print(f"\nImputed {mask.sum()} stocks")
print(shares_imputed[mask][['Stock', 'Region', 'Country', 'ESG score']])

shares_imputed.to_csv('shares_imputed.csv', index=False)
print("\nSaved: shares_imputed.csv")

# 7. Version A: exclude missing-ESG stocks entirely
#    (kept for later sensitivity comparison against Version B)
shares_excluded = shares.dropna(subset=['ESG score']).copy()
shares_excluded.to_csv('shares_excluded.csv', index=False)
print(f"Saved: shares_excluded.csv ({len(shares_excluded)} stocks)")


# 8. Price cleaning - forward-fill genuine post-listing gaps only,
# never before a stock's first trading day (that would be a late IPO, not a data error)
first_valid = prices.apply(lambda row: row.first_valid_index(), axis=1)
prices_clean = prices.copy()
for stock in prices_clean.index:
    fv = first_valid[stock]
    if fv is None:
        continue
    prices_clean.loc[stock, fv:] = prices_clean.loc[stock, fv:].ffill()

prices_clean.to_csv('prices_clean.csv')
print("Saved: prices_clean.csv")