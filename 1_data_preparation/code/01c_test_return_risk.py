
from paths import P   # where each data file lives (see paths.py)
# %%
import pandas as pd
import numpy as np
from sklearn.covariance import LedoitWolf

TRADING_DAYS = 252

# Load cleaned prices (output of the cleaning step)
prices = pd.read_csv(P('prices_clean.csv'), index_col=0)
prices.columns = pd.to_datetime(prices.columns)

# Core functions - all take an optional (start, end) window so the SAME
# code is reused later for robustness checks (3/5-year windows) and for
# the out-of-sample backtest, without rewriting anything.
def compute_log_returns(prices, start=None, end=None):
    window = prices.loc[:, start:end] if (start or end) else prices
    return np.log(window).diff(axis=1)

def expected_return(daily_returns):
    # annualised mean log-return per stock
    return daily_returns.mean(axis=1, skipna=True) * TRADING_DAYS

def per_stock_risk(daily_returns):
    # annualised standard deviation per stock (linear-model risk measure)
    return daily_returns.std(axis=1, skipna=True) * np.sqrt(TRADING_DAYS)

def covariance_matrix(daily_returns):
    # annualised covariance across stocks (Markowitz-model risk measure)
    return daily_returns.T.cov() * TRADING_DAYS

# Run on the full 10-year window (baseline)
daily_returns = compute_log_returns(prices)

exp_ret = expected_return(daily_returns)
risk = per_stock_risk(daily_returns)
cov = covariance_matrix(daily_returns)

# Sanity checks
n_obs = daily_returns.notna().sum(axis=1)
print(f"Observations per stock: min={n_obs.min()}, median={int(n_obs.median())}, max={n_obs.max()}")
print(f"\nStocks with negative expected return: {(exp_ret < 0).sum()} / {len(exp_ret)}")
print("\nExpected return (annualised) summary:")
print(exp_ret.describe())
print("\nPer-stock risk (annualised std) summary:")
print(risk.describe())

print(f"\nCovariance matrix shape: {cov.shape}")
print(f"NaN entries in covariance matrix: {cov.isna().sum().sum()}")

# %%
# Outlier check on daily returns - flag extreme single-day moves that
# likely indicate a data error (bad tick, unadjusted stock split) rather
# than genuine market movement

extreme_threshold = 0.50
extreme_moves = daily_returns[(daily_returns.abs() > extreme_threshold)]
extreme_count = extreme_moves.notna().sum(axis=1)
extreme_count = extreme_count[extreme_count > 0].sort_values(ascending=False)

print(f"\nStocks with at least one daily move > {extreme_threshold*100:.0f}%:")
print(extreme_count)

if len(extreme_count) > 0:
    top_stock = extreme_count.index[0]
    worst_moves = daily_returns.loc[top_stock][daily_returns.loc[top_stock].abs() > extreme_threshold]
    print(f"\nExample - {top_stock} extreme moves:")
    print(worst_moves)

print("\nTop 10 highest expected returns:")
print(exp_ret.sort_values(ascending=False).head(10))
print("\nTop 10 lowest (most negative) expected returns:")
print(exp_ret.sort_values().head(10))

# Save the raw (pre-shrinkage) baseline outputs
exp_ret.to_csv(P('expected_return.csv'), header=['expected_return'])
risk.to_csv(P('per_stock_risk.csv'), header=['risk_std'])
cov.to_csv(P('covariance_matrix.csv'))
print("\nSaved: expected_return.csv, per_stock_risk.csv, covariance_matrix.csv")


# %%
# ============================================================
# [FIX 2026-08-31] COVARIANCE ESTIMATION - REWRITTEN
# ============================================================
# What the previous version did:
#     kept = stocks with >= 504 observations          (dropped 9 of 1093)
#     returns_kept = daily_returns.loc[kept].fillna(0).T
#     LedoitWolf().fit(returns_kept)
#
# Two problems, both traced back to the same root cause:
#
# 1. The >= 504 filter checks each stock's OWN history length. What the
#    covariance actually needs is enough OVERLAP for each PAIR. A stock
#    listed in 2015 and one listed in 2024 both pass the filter, yet share
#    only ~400 common trading days. The filter removed 9 stocks and left
#    87 with ragged history, so the inconsistency it was meant to fix
#    survived almost intact.
#
# 2. fillna(0) then papered over that inconsistency by treating "no
#    observation" as "price did not move". That is not a neutral filler:
#    it injects days of artificial zero volatility. 47 stocks received
#    >40% artificial zeros; for the worst, annualised sigma was understated
#    by ~55%.
#
#    This also silently undoes the pre-IPO decision made in 02a. We were
#    careful never to backfill prices before a stock's first trading day -
#    but filling its RETURNS with zero is the same assumption through the
#    back door.
#
#    The consequence is not cosmetic. Minimum-variance optimisation
#    actively seeks out whatever looks least volatile, so it concentrates
#    precisely on the corrupted minority: the selected min-risk portfolio
#    averaged 35.7% missing data vs 3.6% across the universe, and its true
#    sigma was 9.5% against the 5.0% the model believed.
#    The bitter irony: those stocks are in reality the RISKIEST group in
#    the universe (mean sigma 38.9% vs 30.3%), not the safest.
#
# What we do instead:
#    Estimate the covariance only over stocks with a COMPLETE price series
#    inside the estimation window. No filling, no imputation - the matrix
#    is built from a genuine rectangular sample, which is also the input
#    Ledoit-Wolf assumes. PSD then holds by construction rather than by
#    accident, and shrinkage does its actual job (conditioning) instead of
#    repairing damage.
#
# Cost of the fix: on the 10-year window this excludes 87 recent listings.
# That exclusion is NOT random and we report it as a limitation - see the
# systematic-difference check printed below.

def estimate_covariance(prices, years, label):
    """Ledoit-Wolf covariance on a complete-history rectangular sample."""
    end = prices.columns.max()
    start = end - pd.DateOffset(years=years)
    r = compute_log_returns(prices, start=start)
    r = r.dropna(axis=1, how='all')            # drop the first (all-NaN) diff column

    complete = r.notna().all(axis=1)
    kept = r.index[complete].tolist()
    dropped = r.index[~complete].tolist()

    print(f"\n--- {label}: {years}-year window ({r.shape[1]} trading days) ---")
    print(f"  Complete-history stocks kept: {len(kept)}  |  excluded: {len(dropped)}")

    sample = r.loc[kept].T                      # rows=days, cols=stocks, no NaN
    assert not sample.isna().any().any(), "sample must be NaN-free"

    lw = LedoitWolf().fit(sample.values)
    cov_shrunk = pd.DataFrame(lw.covariance_ * TRADING_DAYS, index=kept, columns=kept)

    eig = np.linalg.eigvalsh(cov_shrunk.values)
    print(f"  Shrinkage intensity (delta): {lw.shrinkage_:.4f}")
    print(f"  Eigenvalues: min={eig.min():.3e}, max={eig.max():.4f}  |  PSD: {eig.min() >= -1e-12}")
    print(f"  Condition number: {eig.max()/max(eig.min(), 1e-12):.1f}")

    mu = expected_return(r.loc[kept])
    sd = per_stock_risk(r.loc[kept])
    return cov_shrunk, mu, sd, kept, dropped


def report_exclusion_bias(dropped, kept, exp_ret, risk, shares_file=P('shares_imputed.csv')):
    """Is the excluded set systematically different? Measure, don't assume."""
    if not dropped:
        print("  No stocks excluded - nothing to check.")
        return
    sh = pd.read_csv(shares_file).set_index('Stock')
    print(f"  Excluded set profile ({len(dropped)} stocks):")
    print(f"    Region split      : {sh.loc[dropped, 'Region'].value_counts().to_dict()}")
    print(f"    Mean exp. return  : excluded {exp_ret[dropped].mean()*100:5.1f}%  vs kept {exp_ret[kept].mean()*100:5.1f}%")
    print(f"    Mean risk (sigma) : excluded {risk[dropped].mean()*100:5.1f}%  vs kept {risk[kept].mean()*100:5.1f}%")
    print(f"    Mean ESG          : excluded {sh.loc[dropped, 'ESG score'].mean():5.1f}   vs kept {sh.loc[kept, 'ESG score'].mean():5.1f}")


# Primary estimate: 10-year baseline window (unchanged from the original plan)
cov_shrunk, mu_final, risk_final, kept, dropped = estimate_covariance(prices, 10, "PRIMARY")
report_exclusion_bias(dropped, kept, exp_ret, risk)

mu_final.to_csv(P('expected_return_final.csv'), header=['expected_return'])
risk_final.to_csv(P('per_stock_risk_final.csv'), header=['risk_std'])
cov_shrunk.to_csv(P('covariance_matrix_shrunk.csv'))
print("\nSaved: expected_return_final.csv, per_stock_risk_final.csv, covariance_matrix_shrunk.csv")

# %%
# Robustness variants (planned check 2.3): shorter estimation windows.
# Now free of charge, since the estimator is parameterised by window.
for years in (5, 3):
    cov_w, mu_w, sd_w, kept_w, dropped_w = estimate_covariance(prices, years, "ROBUSTNESS")
    report_exclusion_bias(dropped_w, kept_w, exp_ret, risk)
    mu_w.to_csv(P(f'expected_return_final_{years}y.csv'), header=['expected_return'])
    sd_w.to_csv(P(f'per_stock_risk_final_{years}y.csv'), header=['risk_std'])
    cov_w.to_csv(P(f'covariance_matrix_shrunk_{years}y.csv'))
    print(f"  Saved {years}-year variant files.")

# %%
