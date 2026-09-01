"""
03b — Expected return, per-stock risk and covariance in USD
===========================================================
Re-runs exactly the estimator of 01c_test_return_risk.py (annualised mean
log-return; annualised std; Ledoit-Wolf shrunk covariance on a complete-history
rectangular sample) but on the USD-converted price series from 03a.

The estimator is deliberately NOT modified. To prove that, the script first
re-derives the LOCAL-currency estimates from prices_clean.csv and asserts they
reproduce 01c's saved output. Only if that control passes does the USD run mean
anything: any difference is then attributable to the currency conversion alone,
not to an estimator change.

Outputs (nothing existing is overwritten):
    expected_return_final_usd.csv        per_stock_risk_final_usd.csv
    covariance_matrix_shrunk_usd.csv
    ... plus _5y / _3y robustness variants
"""

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

TRADING_DAYS = 252
WINDOWS = (10, 5, 3)


# --- estimator, character-for-character the logic of 01c ------------------
def compute_log_returns(prices, start=None, end=None):
    window = prices.loc[:, start:end] if (start or end) else prices
    return np.log(window).diff(axis=1)


def expected_return(daily_returns):
    return daily_returns.mean(axis=1, skipna=True) * TRADING_DAYS


def per_stock_risk(daily_returns):
    return daily_returns.std(axis=1, skipna=True) * np.sqrt(TRADING_DAYS)


def estimate(prices, years, label):
    end = prices.columns.max()
    start = end - pd.DateOffset(years=years)
    r = compute_log_returns(prices, start=start)
    r = r.dropna(axis=1, how="all")

    complete = r.notna().all(axis=1)
    kept = r.index[complete].tolist()
    dropped = r.index[~complete].tolist()

    sample = r.loc[kept].T
    assert not sample.isna().any().any(), "sample must be NaN-free"

    lw = LedoitWolf().fit(sample.values)
    cov = pd.DataFrame(lw.covariance_ * TRADING_DAYS, index=kept, columns=kept)

    eig = np.linalg.eigvalsh(cov.values)
    print(f"\n--- {label}: {years}y window ({r.shape[1]} trading days) ---")
    print(f"  kept {len(kept)} | excluded {len(dropped)}")
    print(f"  shrinkage delta={lw.shrinkage_:.4f} | eig min={eig.min():.3e} "
          f"max={eig.max():.4f} | PSD={eig.min() >= -1e-12} "
          f"| cond={eig.max()/max(eig.min(), 1e-12):.1f}")

    return cov, expected_return(r.loc[kept]), per_stock_risk(r.loc[kept]), kept, dropped


def load_prices(path):
    p = pd.read_csv(path, index_col=0)
    p.columns = pd.to_datetime(p.columns)
    return p


# --- control: reproduce 01c's local-currency output -----------------------
def control_check(prices_local):
    print("=" * 74)
    print("CONTROL: does this code reproduce 01c's local-currency output?")
    print("=" * 74)
    cov, mu, sd, kept, _ = estimate(prices_local, 10, "CONTROL local")

    ref_mu = pd.read_csv("expected_return_final.csv").set_index("Stock")["expected_return"]
    ref_sd = pd.read_csv("per_stock_risk_final.csv").set_index("Stock")["risk_std"]

    assert sorted(kept) == sorted(ref_mu.index), (
        f"stock universe differs: {len(kept)} vs {len(ref_mu)}")
    dmu = float((mu.loc[ref_mu.index] - ref_mu).abs().max())
    dsd = float((sd.loc[ref_sd.index] - ref_sd).abs().max())
    print(f"  max |delta mu| = {dmu:.3e}   max |delta sigma| = {dsd:.3e}")
    assert dmu < 1e-10 and dsd < 1e-10, "estimator does NOT reproduce 01c - stop"
    print("  PASS - estimator is identical to 01c, universe identical "
          f"({len(kept)} stocks)")
    return set(kept)


def main():
    prices_local = load_prices("prices_clean.csv")
    prices_usd = load_prices("prices_clean_usd.csv")
    assert prices_local.shape == prices_usd.shape
    assert prices_local.isna().equals(prices_usd.isna())

    kept_local = control_check(prices_local)

    print("\n" + "=" * 74)
    print("USD ESTIMATES")
    print("=" * 74)
    for years in WINDOWS:
        cov, mu, sd, kept, dropped = estimate(prices_usd, years, "USD")

        if years == 10:
            # The FX series is complete, so conversion cannot change which
            # stocks have a complete price history. If the universe moved,
            # something is wrong with the conversion.
            assert set(kept) == kept_local, (
                "USD universe differs from local - conversion introduced gaps")
            print("  universe identical to the local-currency run (as required)")
            suffix = ""
        else:
            suffix = f"_{years}y"

        mu.to_csv(f"expected_return_final_usd{suffix}.csv", header=["expected_return"])
        sd.to_csv(f"per_stock_risk_final_usd{suffix}.csv", header=["risk_std"])
        cov.to_csv(f"covariance_matrix_shrunk_usd{suffix}.csv")
        print(f"  saved *_usd{suffix}.csv")

    # --- what actually changed, per stock -------------------------------
    print("\n" + "=" * 74)
    print("LOCAL -> USD: what changed (10y window)")
    print("=" * 74)
    mu_loc = pd.read_csv("expected_return_final.csv").set_index("Stock")["expected_return"]
    mu_usd = pd.read_csv("expected_return_final_usd.csv").set_index("Stock")["expected_return"]
    sd_loc = pd.read_csv("per_stock_risk_final.csv").set_index("Stock")["risk_std"]
    sd_usd = pd.read_csv("per_stock_risk_final_usd.csv").set_index("Stock")["risk_std"]

    sh = pd.read_csv("shares_full.csv")
    sh["ccy"] = sh.Stock.str.extract(r"\.([A-Za-z]+)$")[0].str.upper().map(
        {"N": "USD", "OQ": "USD", "Z": "USD", "L": "GBP", "PA": "EUR", "DE": "EUR",
         "AS": "EUR", "MC": "EUR", "MI": "EUR", "BR": "EUR", "HE": "EUR",
         "LS": "EUR", "VI": "EUR", "I": "EUR", "S": "CHF", "ST": "SEK",
         "CO": "DKK", "OL": "NOK", "WA": "PLN"})
    sh = sh.set_index("Stock").loc[mu_loc.index]

    cmp = pd.DataFrame({
        "ccy": sh.ccy, "region": sh.Region,
        "mu_loc": mu_loc * 100, "mu_usd": mu_usd * 100,
        "sd_loc": sd_loc * 100, "sd_usd": sd_usd * 100,
    })
    cmp["d_mu"] = cmp.mu_usd - cmp.mu_loc
    cmp["d_sd"] = cmp.sd_usd - cmp.sd_loc

    out = cmp.groupby("ccy").agg(
        n=("d_mu", "size"), mu_loc=("mu_loc", "mean"), mu_usd=("mu_usd", "mean"),
        d_mu=("d_mu", "mean"), sd_loc=("sd_loc", "mean"), sd_usd=("sd_usd", "mean"),
        d_sd=("d_sd", "mean"))
    print("Means by listing currency, % p.a.:")
    print(out.round(2).to_string())
    print("\nBy region:")
    print(cmp.groupby("region")[["mu_loc", "mu_usd", "sd_loc", "sd_usd"]]
          .mean().round(2).to_string())
    print(f"\nStocks with negative mu: local {(cmp.mu_loc < 0).sum()} "
          f"-> USD {(cmp.mu_usd < 0).sum()}")


if __name__ == "__main__":
    main()
