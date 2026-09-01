"""
05b — Does the single-index model understate PORTFOLIO risk?
============================================================
The per-stock check in 05a (model sigma vs sample sigma, ratio 1.000) is an OLS
identity: for a one-factor regression, beta^2 var(M) + var(eps) equals the
sample variance by the variance decomposition. It cannot fail, so it is not
evidence of anything.

The assumption that CAN fail is that residuals are mutually uncorrelated. The
single-index model sets every off-diagonal residual covariance to zero, and with
a median R^2 of 0.276 that discards 72% of each stock's variance from the
covariance structure. If residuals actually co-move (same sector, same country,
same currency), portfolio risk is understated - and minimum-variance
optimisation will hunt for exactly the portfolios where the understatement is
largest. That is the failure mode 01c documents from the earlier fillna(0) bug.

Test: for every portfolio on every candidate frontier, compare the risk the
model PREDICTS against the risk that portfolio actually REALISED over the same
window, and do it for all three covariance candidates:

    single-index (1093 stocks)
    10-factor PCA (1093 stocks)
    complete-case Ledoit-Wolf (997 stocks)

Realised risk is computed from the actual USD return series of the held stocks,
so it embeds whatever residual correlation is really there.
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 252

prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
px = prices.loc[:, end - pd.DateOffset(years=10):end]
rets = np.log(px).diff(axis=1).iloc[:, 1:]

S_si = pd.read_csv("covariance_matrix_singleindex.csv", index_col=0)
S_pca = pd.read_csv("covariance_matrix_factor_usd.csv", index_col=0)
S_lw = pd.read_csv("covariance_matrix_shrunk_usd.csv", index_col=0)
MODELS = {"single-index": S_si, "10-factor PCA": S_pca, "complete-case LW": S_lw}


def realised_risk(w):
    """Annualised std of the portfolio's actual return series."""
    idx = list(w.index)
    R = rets.loc[idx]
    ok = R.notna().all(axis=0)          # days where every holding has data
    series = (R.loc[:, ok].T * w.values).sum(axis=1)
    return float(series.std(ddof=1) * np.sqrt(TRADING_DAYS)), int(ok.sum())


def predicted(w, S):
    idx = [s for s in w.index if s in S.index]
    if len(idx) < len(w):
        return np.nan
    ww = (w.loc[idx] / w.loc[idx].sum()).values
    return float(np.sqrt(ww @ S.loc[idx, idx].values @ ww))


FRONTIERS = {
    "single-index + shrunk mu": "efficient_frontier_weights_singleindex.csv",
    "10-factor + shrunk mu": "efficient_frontier_weights_factor.csv",
    "complete-case LW + raw mu": "efficient_frontier_weights_usd.csv",
}

for fname, path in FRONTIERS.items():
    W = pd.read_csv(path, index_col=0)
    print("=" * 96)
    print(f"PORTFOLIOS FROM: {fname}")
    print("=" * 96)
    hdr = f"{'pt':>3} {'n':>4} {'days':>6} {'realised%':>10}"
    for m in MODELS:
        hdr += f" {m[:13]:>14}"
    print(hdr + f" {'si err%':>9}")
    recs = []
    for i, col in enumerate(W.columns):
        w = W[col].fillna(0.0)
        w = w[w > 1e-9]
        w = w / w.sum()
        real, ndays = realised_risk(w)
        line = f"{i:3d} {len(w):4d} {ndays:6d} {real*100:9.2f}%"
        row = {"realised": real}
        for m, S in MODELS.items():
            p = predicted(w, S)
            row[m] = p
            line += f" {p*100:13.2f}%" if not np.isnan(p) else f" {'n/a':>14}"
        err = (row["single-index"] / real - 1) * 100
        line += f" {err:+8.1f}%"
        recs.append(row)
        print(line)

    D = pd.DataFrame(recs)
    print("\n  mean signed error vs realised risk:")
    for m in MODELS:
        e = (D[m] / D.realised - 1) * 100
        if e.notna().any():
            print(f"    {m:18s}: {e.mean():+6.2f}%  (range {e.min():+.1f}% .. {e.max():+.1f}%)")
        else:
            print(f"    {m:18s}: n/a - portfolio holds stocks outside its universe")
    print()

# ---------------------------------------------------------------- residual test
print("=" * 96)
print("DIRECT TEST OF THE ASSUMPTION: are single-index residuals uncorrelated?")
print("=" * 96)
P = pd.read_csv("single_index_params.csv", index_col=0)
long_hist = rets.index[rets.notna().all(axis=1)].tolist()
r_M = rets.loc[long_hist].mean(axis=0)
sub = long_hist[:500]
resid = rets.loc[sub].sub(P.loc[sub, "beta"].values[:, None] * r_M.values, axis=0)
resid = resid.sub(resid.mean(axis=1), axis=0)
C = np.corrcoef(resid.values)
iu = np.triu_indices(len(sub), k=1)
off = C[iu]
print(f"Pairwise residual correlations on {len(sub)} complete-history stocks:")
print(f"  mean {off.mean():+.4f} | median {np.median(off):+.4f} | "
      f"share > 0.2: {(off > 0.2).mean()*100:.1f}% | share > 0.3: {(off > 0.3).mean()*100:.1f}%")
print(f"  the model assumes every one of these is exactly 0")
# pandas 3.0 returns arrow-backed arrays here; force plain numpy for broadcasting
sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
SUF2CCY = {"N":"USD","OQ":"USD","Z":"USD","L":"GBP","PA":"EUR","DE":"EUR","AS":"EUR",
           "MC":"EUR","MI":"EUR","BR":"EUR","HE":"EUR","LS":"EUR","VI":"EUR","I":"EUR",
           "S":"CHF","ST":"SEK","CO":"DKK","OL":"NOK","WA":"PLN"}
for name, key in [("region", np.asarray(sh.loc[sub, "Region"].astype(str))),
                  ("country", np.asarray(sh.loc[sub, "Country"].astype(str))),
                  ("currency", np.asarray(pd.Series(sub).str.extract(r"\.([A-Za-z]+)$")[0]
                                          .str.upper().map(SUF2CCY).astype(str)))]:
    same = (key[:, None] == key[None, :])[iu]
    print(f"  mean residual corr, same {name:8s} {off[same].mean():+.4f} "
          f"({same.sum():,} pairs) | different {off[~same].mean():+.4f} "
          f"({(~same).sum():,} pairs)")
