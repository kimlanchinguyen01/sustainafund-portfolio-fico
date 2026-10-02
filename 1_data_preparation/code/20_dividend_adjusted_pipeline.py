"""
20 — Rebuild the model inputs from dividend-adjusted (total-return) prices
=========================================================================
prices_lseg_dividend_adjusted.csv replaces stockprices_full.csv as the raw input.
It is back-adjusted and anchored at the end of the window: adj/raw runs 0.68 ->
0.81 -> 1.00 for Unilever and 0.959 -> 0.999 for NVDA, which is what a correct
total-return series looks like.

Why it matters here rather than being a detail: a plain closing price omits
dividends, so it understates the return of exactly the high-yield, low-volatility
names our minimum-variance book is built from. Measured on this file, the mean
annualised return rises 2.45pp and the sector ordering of the increase follows
dividend yield precisely - Energy +3.89, Utilities +3.66, Financial Services
+3.36, Real Estate +3.31, Consumer Defensive +2.76, against Technology +1.18 and
Healthcare +1.23. Volatility is unchanged (31.08% -> 31.05%), as it should be:
dividends add drift, not noise. Stocks with a negative expected return fall from
153 to 88.

    SIX STOCKS ARE EMPTY in the new file - 2870 of 2870 values missing, where the
    old file had a full history: HOLN.S, URW.PA, EA.OQ, AVB.N, EQR.N, HWM.N.
    Three of the six are REITs, whose adjustment factors are the largest, so the
    extraction most likely failed on them. They are DROPPED here rather than
    back-filled from the unadjusted file: an unadjusted series would carry a
    ~3pp lower return and the optimiser would penalise them for the data defect.
    EA.OQ was held at ~1% in the current risk-averse book. Worth asking for a
    re-extraction.

The rest of the chain is the already-validated logic, unchanged: forward-fill of
post-listing gaps only (02a), USD conversion at daily ECB rates (03a),
truncation at trading discontinuities detected on LOCAL prices (13), James-Stein
mu and a 20-factor PCA covariance (14).

Outputs: expected_return_v4.csv, covariance_matrix_v4.csv, per_stock_risk_v4.csv,
prices_div_usd.csv
"""

from paths import P   # where each data file lives (see paths.py)

import numpy as np
import pandas as pd

TD, K, MIN_OBS = 252, 20, 252
FREEZE_MIN, JUMP_MIN = 10, 0.30
SUF2CCY = {"N": "USD", "OQ": "USD", "Z": "USD", "L": "GBP", "PA": "EUR", "DE": "EUR",
           "AS": "EUR", "MC": "EUR", "MI": "EUR", "BR": "EUR", "HE": "EUR", "LS": "EUR",
           "VI": "EUR", "I": "EUR", "S": "CHF", "ST": "SEK", "CO": "DKK", "OL": "NOK",
           "WA": "PLN"}
PENCE = {"L"}

px = pd.read_csv(P("prices_lseg_dividend_adjusted.csv"), index_col=0)
px.columns = pd.to_datetime(px.columns)
sh = pd.read_csv(P("shares_full.csv")).set_index("Stock")
print(f"raw dividend-adjusted file: {px.shape}")

# ---- 1. drop the fully-empty series ----
empty = [s for s in px.index if px.loc[s].isna().all()]
print(f"\nfully empty in the new file ({len(empty)}): {empty}")
px = px.drop(index=empty)
print(f"universe {px.shape[0]}")

# ---- 2. forward-fill post-listing gaps only (02a logic) ----
first = px.apply(lambda r: r.first_valid_index(), axis=1)
before = int(px.isna().sum().sum())
for s in px.index:
    fv = first[s]
    if fv is not None:
        px.loc[s, fv:] = px.loc[s, fv:].ffill()
print(f"forward-filled post-listing gaps: {before - int(px.isna().sum().sum())} values")
assert (np.nanmin(px.values) > 0), "non-positive price"

# ---- 3. discontinuities, detected on LOCAL prices (13 logic) ----
def discont(series):
    v = series.dropna()
    a = v.values
    out, run = [], 1
    for i in range(1, len(a)):
        if a[i] == a[i - 1]:
            run += 1
            continue
        if run >= FREEZE_MIN and abs(a[i] / a[i - 1] - 1) > JUMP_MIN:
            out.append((v.index[i], run, float(a[i] / a[i - 1] - 1)))
        run = 1
    return out

print("\ndiscontinuities (>=%d identical local closes then >%.0f%% move):" % (FREEZE_MIN, JUMP_MIN * 100))
cut = {}
for s in px.index:
    d = discont(px.loc[s])
    if d:
        for dt, run, j in d:
            print(f"  {s:10s} freeze {run:>3}d -> {dt.date()}  jump {j*100:+7.1f}%")
        cut[s] = d[-1][0]
for s, dt in cut.items():
    n0 = int(px.loc[s].notna().sum())
    px.loc[s, px.columns < dt] = np.nan
    print(f"  {s:10s} history truncated to {dt.date()}: {n0} -> {int(px.loc[s].notna().sum())} days")

# ---- 4. USD conversion at daily ECB rates (03a logic) ----
suf = pd.Series(px.index, index=px.index).str.extract(r"\.([A-Za-z]+)$")[0].str.upper()
ccy = suf.map(SUF2CCY)
assert ccy.notna().all(), sorted(suf[ccy.isna()].unique())
fx = pd.read_csv(P("fx_rates_ecb.csv"), index_col=0, parse_dates=True)
fx["USD"] = 1.0
fxa = fx.reindex(px.columns).ffill().bfill()
rate = fxa[ccy.values].T.values
scale = np.where(suf.isin(PENCE).values, 0.01, 1.0)[:, None]
usd = pd.DataFrame(px.values * rate * scale, index=px.index, columns=px.columns)
assert usd.isna().equals(px.isna()), "conversion changed the NaN pattern"
usd.to_csv(P("prices_div_usd.csv"))
print(f"\nconverted to USD | currencies {ccy.nunique()} | pence rescaled: {int(suf.isin(PENCE).sum())}")

# ---- 5. estimate mu and Sigma (14 logic) ----
end = usd.columns.max()
rets = np.log(usd.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]
Rv = rets.values
valid = ~np.isnan(Rv)
n_obs = valid.sum(axis=1)
long_mask = valid.all(axis=1)
stocks = list(rets.index)
print(f"\n10y window: {rets.shape[1]} days | complete-history {long_mask.sum()} | partial {(~long_mask).sum()}")

L = Rv[long_mask]
Lc = (L - L.mean(axis=1, keepdims=True)).T
U, S_, _ = np.linalg.svd(Lc, full_matrices=False)
F = (U[:, :K] * S_[:K]) / np.sqrt(len(Lc))
Fcov = np.cov(F, rowvar=False) * TD
X = np.column_stack([np.ones(len(F)), F])
B = np.zeros((len(stocks), K)); dv = np.full(len(stocks), np.nan)
li = np.where(long_mask)[0]
coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
B[li] = coef[1:].T
dv[li] = (Rv[li].T - X @ coef).var(axis=0, ddof=K + 1) * TD
for i in np.where(~long_mask)[0]:
    m = valid[i]
    if m.sum() < MIN_OBS:
        continue
    cf, *_ = np.linalg.lstsq(X[m], Rv[i][m], rcond=None)
    B[i] = cf[1:]
    dv[i] = (Rv[i][m] - X[m] @ cf).var(ddof=K + 1) * TD
keep = ~np.isnan(dv)
names = [stocks[i] for i in np.where(keep)[0]]
Sig = B[keep] @ Fcov @ B[keep].T
Sig[np.diag_indices_from(Sig)] += dv[keep]
Sig = (Sig + Sig.T) / 2
Sigma = pd.DataFrame(Sig, index=names, columns=names)
Sigma.index.name = "Stock"
eig = np.linalg.eigvalsh(Sig)
print(f"Sigma {Sigma.shape} | PSD {eig.min() >= 0} | cond {eig.max()/eig.min():.1f}")
assert eig.min() >= 0

mu_hat = np.nanmean(Rv, axis=1) * TD
sd_hat = np.nanstd(Rv, axis=1, ddof=1) * np.sqrt(TD)
tgt = float(np.mean(mu_hat[long_mask])); tau2 = float(np.var(mu_hat[long_mask]))
se2 = (sd_hat ** 2) / np.maximum(n_obs, 1) * TD
wgt = tau2 / (tau2 + se2)
mu = pd.Series((wgt * mu_hat + (1 - wgt) * tgt)[keep], index=names, name="expected_return")
mu.index.name = "Stock"
sd = pd.Series(sd_hat[keep], index=names, name="risk_std"); sd.index.name = "Stock"
print(f"mu: {mu.min()*100:.2f}%..{mu.max()*100:.2f}% | median {mu.median()*100:.2f}% | "
      f"shrinkage target {tgt*100:.2f}%")

mu.to_csv(P("expected_return_v4.csv")); sd.to_csv(P("per_stock_risk_v4.csv"))
Sigma.to_csv(P("covariance_matrix_v4.csv"))

# ---- 6. what changed vs v3 (price-only inputs) ----
# Informational only: compare against the closing-price estimate if it happens
# to be around. Skipped rather than fatal - the outputs above are already saved.
try:
    prev = pd.read_csv(P("expected_return_v3.csv"), index_col=0)["expected_return"]
except FileNotFoundError:
    print("\n(expected_return_v3.csv not present - skipping the closing-price comparison)")
else:
    both = mu.index.intersection(prev.index)
    print("\n" + "=" * 78)
    print("v3 (closing prices) -> v4 (dividend-adjusted)")
    print("=" * 78)
    print(f"  stocks: {len(prev)} -> {len(mu)}  ({len(prev)-len(both)} dropped, all from the 6 empty)")
    print(f"  mu median : {prev.loc[both].median()*100:+.2f}% -> {mu.loc[both].median()*100:+.2f}%")
    print(f"  mu mean   : {prev.loc[both].mean()*100:+.2f}% -> {mu.loc[both].mean()*100:+.2f}%")
    print(f"  negative  : {(prev.loc[both]<0).sum()} -> {(mu.loc[both]<0).sum()}")
    print(f"  correlation between the two: {np.corrcoef(prev.loc[both], mu.loc[both])[0,1]:.3f}")
print("\nSaved expected_return_v4.csv, per_stock_risk_v4.csv, covariance_matrix_v4.csv, "
      "prices_div_usd.csv")
