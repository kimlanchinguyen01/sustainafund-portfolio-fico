"""
03a — Currency conversion of the price history to USD
=====================================================
Why this exists
---------------
The fund's budget is 100M USD, but stockprices_full.csv quotes each stock in the
currency of its primary listing (8 currencies across 19 exchanges). Log-returns
computed on the raw series are therefore LOCAL-currency returns, i.e. what a
domestic investor earns - not what SustainaFund earns.

Because ln(P_usd) = ln(P_local) + ln(fx), the two effects are exactly additive:
    mu_usd    = mu_local + fx_drift          (exact, not an approximation)
    Sigma_usd = Sigma_local + FX cross-terms + var(fx)
The second line is the reason for this step: stocks sharing a currency share an
FX exposure, so their USD returns are more correlated than their local returns.
A local-currency Sigma therefore OVERSTATES the diversification benefit.

Measured effect (see 03c comparison): mu moves by <0.3pp - negligible - but the
risk of the min-variance portfolio is understated by ~20% (8.5% -> 10.2%),
and the error is largest exactly at the risk-averse end of the frontier.

Data source
-----------
ECB reference rates via the Frankfurter API (https://api.frankfurter.dev),
free, no API key. Rates are cached to fx_rates_ecb.csv on first run so every
later rerun is offline and reproducible (required: external data must be
documented and reproducible).

Outputs
-------
    fx_rates_ecb.csv    cached daily FX, USD per 1 unit of each currency
    prices_clean_usd.csv    prices_clean.csv converted to USD

Nothing existing is overwritten.
"""

import io
import json
import os
import urllib.request

import numpy as np
import pandas as pd

FILE_PRICES_IN = "prices_clean.csv"
FILE_PRICES_OUT = "prices_clean_usd.csv"
FILE_SHARES = "shares_full.csv"
FILE_FX_CACHE = "fx_rates_ecb.csv"

CURRENCIES = ["EUR", "GBP", "CHF", "SEK", "DKK", "NOK", "PLN"]

# Exchange suffix -> listing currency. Verified against the Country column:
# every suffix maps to exactly one country (see the assertion below), so there
# are no USD- or EUR-quoted secondary lines hiding inside a group.
SUF2CCY = {
    "N": "USD", "OQ": "USD", "Z": "USD",          # NYSE, NASDAQ, Cboe BZX
    "L": "GBP",                                   # London - quoted in PENCE, see PENCE_SUFFIXES
    "PA": "EUR", "DE": "EUR", "AS": "EUR", "MC": "EUR", "MI": "EUR",
    "BR": "EUR", "HE": "EUR", "LS": "EUR", "VI": "EUR", "I": "EUR",
    "S": "CHF", "ST": "SEK", "CO": "DKK", "OL": "NOK", "WA": "PLN",
}

# London quotes in pence, not pounds (verified: median level 711, quartiles
# 274-1836 - consistent with pence, not with pounds). This rescaling is
# COSMETIC ONLY: a constant factor cancels in ln(P(t)/P(t-1)), so it changes
# no model input. It is applied so that prices_clean_usd.csv holds genuine
# USD prices, which matters for the dashboard and for any future work on
# transaction costs or share counts.
PENCE_SUFFIXES = {"L"}


def fetch_fx(start, end):
    """ECB reference rates, USD per 1 unit of foreign currency."""
    if os.path.exists(FILE_FX_CACHE):
        fx = pd.read_csv(FILE_FX_CACHE, index_col=0, parse_dates=True)
        print(f"FX loaded from cache {FILE_FX_CACHE}: {fx.shape[0]} days, "
              f"{fx.index.min().date()} -> {fx.index.max().date()}")
        return fx

    url = (f"https://api.frankfurter.dev/v1/{start:%Y-%m-%d}..{end:%Y-%m-%d}"
           f"?base=USD&symbols={','.join(CURRENCIES)}")
    print(f"Fetching ECB rates: {url}")
    try:
        with urllib.request.urlopen(url, timeout=90) as resp:
            payload = json.load(resp)
    except Exception as exc:
        # python.org macOS builds ship without root certificates, so urllib
        # fails TLS verification where curl succeeds. Fall back rather than
        # disabling verification.
        print(f"  urllib failed ({type(exc).__name__}); retrying via curl")
        import subprocess
        out = subprocess.run(["curl", "-sSf", "--max-time", "90", url],
                             capture_output=True, text=True, check=True).stdout
        payload = json.loads(out)

    # API returns CCY per 1 USD; invert to get USD per 1 CCY
    raw = pd.DataFrame(payload["rates"]).T
    raw.index = pd.to_datetime(raw.index)
    fx = (1.0 / raw.sort_index())[CURRENCIES]
    fx.to_csv(FILE_FX_CACHE)
    print(f"Fetched {fx.shape[0]} days, cached to {FILE_FX_CACHE}")
    return fx


def main():
    prices = pd.read_csv(FILE_PRICES_IN, index_col=0)
    prices.columns = pd.to_datetime(prices.columns)
    shares = pd.read_csv(FILE_SHARES)

    shares["suffix"] = shares.Stock.str.extract(r"\.([A-Za-z]+)$")[0].str.upper()

    # Guard: the suffix->currency map must be exhaustive and country-consistent
    unmapped = sorted(set(shares.suffix) - set(SUF2CCY))
    assert not unmapped, f"Unmapped exchange suffixes: {unmapped}"
    mixed = {s: sorted(g.unique()) for s, g in shares.groupby("suffix").Country
             if g.nunique() > 1}
    assert not mixed, f"Suffix spanning several countries - check currency map: {mixed}"

    shares["ccy"] = shares.suffix.map(SUF2CCY)
    shares = shares.set_index("Stock")
    ccy = shares.loc[prices.index, "ccy"]
    print("\nStocks per listing currency:")
    print(ccy.value_counts().to_string())

    fx = fetch_fx(prices.columns.min(), prices.columns.max())
    fx["USD"] = 1.0

    # Align FX onto the dataset's trading days. ECB publishes on TARGET business
    # days, so a handful of the dataset's trading days have no published rate
    # (national holidays); forward-fill those - consistent with the 1-day
    # forward-fill already applied to prices in 02a. bfill covers the case where
    # the very first trading day precedes the first published rate.
    fx_aligned = fx.reindex(prices.columns)
    n_missing = int(fx_aligned["EUR"].isna().sum())
    fx_aligned = fx_aligned.ffill().bfill()
    assert not fx_aligned.isna().any().any(), "FX still has gaps after ffill/bfill"
    print(f"\nTrading days: {len(prices.columns)} | without a published ECB rate "
          f"(forward-filled): {n_missing} ({n_missing/len(prices.columns)*100:.1f}%)")

    # Convert. rate_matrix is stocks x days, matching prices' orientation.
    rate_matrix = fx_aligned[ccy.values].T.values
    assert rate_matrix.shape == prices.shape, (rate_matrix.shape, prices.shape)

    scale = pd.Series(1.0, index=prices.index)
    pence = shares.loc[prices.index, "suffix"].isin(PENCE_SUFFIXES).values
    scale[pence] = 0.01
    print(f"Pence->major-unit rescaling applied to {int(pence.sum())} stocks "
          f"(cosmetic; cancels in log-returns)")

    prices_usd = pd.DataFrame(
        prices.values * rate_matrix * scale.values[:, None],
        index=prices.index, columns=prices.columns,
    )

    # Validation: NaN pattern must be untouched (FX is complete, so conversion
    # must not create or remove a single missing observation).
    assert prices_usd.isna().equals(prices.isna()), "conversion altered the NaN pattern"
    # NB: pandas 3.0 stack() retains NaN, so compare on the underlying array
    # instead - NaN > 0 is False and would fail this check spuriously.
    assert np.nanmin(prices_usd.values) > 0, "non-positive USD price produced"
    print("Validation: NaN pattern unchanged, all USD prices strictly positive")

    prices_usd.to_csv(FILE_PRICES_OUT)
    print(f"\nSaved {FILE_PRICES_OUT}  ({prices_usd.shape[0]} stocks x "
          f"{prices_usd.shape[1]} days)")

    print("\nMedian USD price level by currency (sanity check):")
    lvl = prices_usd.median(axis=1)
    print(pd.DataFrame({"ccy": ccy, "usd_level": lvl}).groupby("ccy").usd_level
          .describe()[["count", "min", "50%", "max"]].round(2).to_string())


if __name__ == "__main__":
    main()
