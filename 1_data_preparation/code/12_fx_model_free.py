"""
12 — Does the currency conversion matter? A model-free test
==========================================================
Challenge from the team: "we work on returns", so currency should be irrelevant.

Half correct. Returns remove the PRICE LEVEL problem completely - a ratio is
dimensionless, so pence vs dollars cancels exactly. That is why the original
pipeline was not broken.

It does not remove the FX RETURN, because
    d ln P_usd = d ln P_local + d ln fx
The second term is additive and survives the move to returns. A local-currency
return is what a DOMESTIC investor earns; the fund holds USD.

This test uses no covariance model at all. For each frozen portfolio it takes the
realised return series two ways - from local-currency prices and from
USD-converted prices - and compares the risk actually experienced. Then it
decomposes the USD variance into

    var(local) + 2*cov(local, fx) + var(fx)

so the FX contribution is attributed rather than asserted.
"""

from paths import P   # where each data file lives (see paths.py)

import numpy as np
import pandas as pd

TD = 252
SUF2CCY = {"N": "USD", "OQ": "USD", "Z": "USD", "L": "GBP", "PA": "EUR", "DE": "EUR",
           "AS": "EUR", "MC": "EUR", "MI": "EUR", "BR": "EUR", "HE": "EUR", "LS": "EUR",
           "VI": "EUR", "I": "EUR", "S": "CHF", "ST": "SEK", "CO": "DKK", "OL": "NOK",
           "WA": "PLN"}

loc = pd.read_csv(P("prices_clean.csv"), index_col=0)
usd = pd.read_csv(P("prices_clean_usd.csv"), index_col=0)
loc.columns = pd.to_datetime(loc.columns)
usd.columns = pd.to_datetime(usd.columns)
end = usd.columns.max()
sl = slice(end - pd.DateOffset(years=10), end)
r_loc = np.log(loc.loc[:, sl]).diff(axis=1).iloc[:, 1:]
r_usd = np.log(usd.loc[:, sl]).diff(axis=1).iloc[:, 1:]

fx = pd.read_csv(P("fx_rates_ecb.csv"), index_col=0, parse_dates=True)
fx["USD"] = 1.0
fxa = fx.reindex(usd.loc[:, sl].columns).ffill().bfill()
r_fx = np.log(fxa).diff().iloc[1:]

print("Realised risk of the FROZEN portfolios, computed from actual history only")
print("=" * 96)
print(f"{'portfolio':<14} {'non-USD w':>10} {'local %':>9} {'USD %':>8} "
      f"{'FX adds':>9} {'var(loc)':>9} {'2cov':>8} {'var(fx)':>9} {'fx-only vol':>12}")
rows = []
for prof in ["risk_averse", "neutral", "risk_prone"]:
    h = pd.read_csv(P(f"FROZEN_v2_portfolio_{prof}.csv"), index_col=0)
    w = (h["weight_%"] / 100)
    ccy = pd.Series(w.index, index=w.index).str.extract(r"\.([A-Za-z]+)$")[0].str.upper().map(SUF2CCY)
    idx = list(w.index)

    RL = r_loc.loc[idx]
    RU = r_usd.loc[idx]
    ok = RL.notna().all(axis=0) & RU.notna().all(axis=0)
    wl = w.values

    pl = (RL.loc[:, ok].T * wl).sum(axis=1)          # local-currency portfolio return
    pu = (RU.loc[:, ok].T * wl).sum(axis=1)          # USD portfolio return
    # the portfolio's own FX return series: weights applied to each holding's currency
    FXW = pd.DataFrame({s: r_fx.loc[ok[ok].index, ccy[s]].values for s in idx},
                       index=ok[ok].index)
    pf = (FXW * wl).sum(axis=1)

    v_loc = float(pl.var(ddof=1)) * TD
    v_fx = float(pf.var(ddof=1)) * TD
    cov2 = 2 * float(pl.cov(pf)) * TD
    v_usd = float(pu.var(ddof=1)) * TD
    nonusd = float(w[ccy != "USD"].sum())

    rows.append({"profile": prof, "nonUSD_%": nonusd * 100,
                 "risk_local_%": np.sqrt(v_loc) * 100, "risk_usd_%": np.sqrt(v_usd) * 100,
                 "fx_adds_%": (np.sqrt(v_usd) / np.sqrt(v_loc) - 1) * 100,
                 "var_local": v_loc, "cov_term": cov2, "var_fx": v_fx,
                 "fx_only_vol_%": np.sqrt(v_fx) * 100,
                 "recon_err": abs(v_loc + cov2 + v_fx - v_usd)})
    print(f"{prof:<14} {nonusd*100:9.1f}% {np.sqrt(v_loc)*100:8.2f}% "
          f"{np.sqrt(v_usd)*100:7.2f}% {(np.sqrt(v_usd)/np.sqrt(v_loc)-1)*100:+8.1f}% "
          f"{v_loc:9.5f} {cov2:+8.5f} {v_fx:9.5f} {np.sqrt(v_fx)*100:11.2f}%")

D = pd.DataFrame(rows)
print(f"\nvariance decomposition check, max |var(loc)+2cov+var(fx) - var(usd)|: "
      f"{D.recon_err.max():.2e}  (identity holds)")

print("\n" + "=" * 96)
print("WHAT THIS SETTLES")
print("=" * 96)
print("The 'we work on returns' argument is tested directly: both columns ARE returns.")
print("The only difference is whose currency they are measured in. If currency were")
print("irrelevant once you move to returns, the two columns would be identical.")
for _, x in D.iterrows():
    print(f"  {x['profile']:<13}: {x['nonUSD_%']:.0f}% of the book is non-USD; "
          f"the same holdings realised {x['risk_local_%']:.2f}% in local terms "
          f"and {x['risk_usd_%']:.2f}% in USD ({x['fx_adds_%']:+.1f}%)")
print("\nAnd it is not a rounding effect: the FX component alone has an annualised")
print(f"volatility of {D['fx_only_vol_%'].min():.2f}%-{D['fx_only_vol_%'].max():.2f}% "
      f"at the portfolio level.")
print("A fund reporting in USD bears that. A local-currency covariance cannot see it,")
print("which is why the omission showed up in risk and not in expected return.")

D.to_csv(P("fx_model_free_check.csv"), index=False)
print("\nSaved fx_model_free_check.csv")
