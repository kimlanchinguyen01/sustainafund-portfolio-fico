"""
04a — Factor risk model: make ALL stocks eligible
=================================================
Addresses Chi Chloe's critique directly. The complete-history rule excludes 96
of 1093 stocks from the covariance, so they can never be bought. Shortening the
estimation window is not an acceptable fix (it inflates mu badly: the frontier's
max return goes 38.8% on 10y -> 85.6% on 3y, which is estimation error, not
opportunity).

The standard fix is a factor model. Instead of estimating every pairwise
covariance directly - which needs a common history for every pair - estimate how
each stock responds to a small set of common factors:

    r_i(t) = beta_i . f(t) + eps_i(t)
    Sigma  = B F B' + diag(residual variance)

Each stock's betas are fitted on whatever days it actually has, so a stock
listed in 2022 contributes without forcing every other pair down to a 2022
window. Sigma is positive semi-definite by construction (F is PSD, D >= 0), so
the MIQP stays well posed.

Factors: principal components of the 997 complete-history USD return series.
Data-driven, no external factor library needed, and the factors are defined over
the whole 10-year window so short-history stocks can be regressed onto them.

Expected return is NOT taken from the factor model. A factor model built on
demeaned returns cannot carry a mean (lambda = mean of the factor series is zero
by construction), and more fundamentally a factor model of this kind is a RISK
model, not a return model - which is also the industry position (Barra, Axioma
deliver risk, not expected returns).

mu instead uses James-Stein shrinkage with intensity driven by sample size:

    w_i   = tau^2 / (tau^2 + sigma_i^2 / n_i)
    mu_i  = w_i * mu_hat_i + (1 - w_i) * mu_target

tau^2 is the cross-sectional dispersion of mu among the long-history stocks and
sigma_i^2 / n_i is the sampling variance of stock i's own mean. A stock with 293
observations is therefore pulled hard toward the target, one with 2607 barely at
all - which is exactly the right behaviour for the newly-admitted names, whose
own sample means reach 88% p.a. (GEV.N) purely from the 2023-25 regime.

This also attacks the instability measured in 03e (Jaccard 0.28 between two
estimation windows): mu error is the dominant source, and until now mu was the
one input with no regularisation at all while Sigma had Ledoit-Wolf.

Outputs (nothing existing is touched):
    expected_return_shrunk_usd.csv     James-Stein mu, all 1093 stocks
    covariance_matrix_factor_usd.csv   factor Sigma, all 1093 stocks
    factor_model_betas.csv
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 252
WINDOW_YEARS = 10
N_FACTORS = 10
MIN_OBS = 252            # a stock needs >= 1 year of returns to get a beta


def main():
    prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
    prices.columns = pd.to_datetime(prices.columns)

    end = prices.columns.max()
    start = end - pd.DateOffset(years=WINDOW_YEARS)
    px = prices.loc[:, start:end]
    rets = np.log(px).diff(axis=1).iloc[:, 1:]
    print(f"Window {px.columns.min().date()} -> {px.columns.max().date()} "
          f"({rets.shape[1]} return days), {rets.shape[0]} stocks")

    n_obs = rets.notna().sum(axis=1)
    complete = rets.notna().all(axis=1)
    long_hist = rets.index[complete].tolist()
    short_hist = rets.index[~complete].tolist()
    print(f"Complete history: {len(long_hist)} | partial: {len(short_hist)}")
    print(f"Partial-history observation counts: min={n_obs[short_hist].min()}, "
          f"median={int(n_obs[short_hist].median())}, max={n_obs[short_hist].max()}")

    eligible = [s for s in rets.index if n_obs[s] >= MIN_OBS]
    too_short = sorted(set(rets.index) - set(eligible))
    print(f"\nEligible with >= {MIN_OBS} observations: {len(eligible)} of {len(rets)}")
    if too_short:
        print(f"Still excluded (under 1 year of data): {len(too_short)} -> {too_short}")

    # ---------------- factors: PCA on the complete-history block -------------
    R = rets.loc[long_hist].T                       # days x stocks, no NaN
    Rc = R - R.mean()
    # economically: PC1 is the market, the next few are region / sector tilts
    U, S, Vt = np.linalg.svd(Rc.values, full_matrices=False)
    evr = (S ** 2) / (S ** 2).sum()
    print(f"\nPCA on {R.shape[1]} complete-history stocks:")
    print("  variance explained by PC1..PC10: " +
          ", ".join(f"{v*100:.1f}%" for v in evr[:10]))
    print(f"  cumulative with {N_FACTORS} factors: {evr[:N_FACTORS].sum()*100:.1f}%")

    # factor return series (days x N_FACTORS), in daily return units
    F = pd.DataFrame(U[:, :N_FACTORS] * S[:N_FACTORS],
                     index=R.index, columns=[f"F{i+1}" for i in range(N_FACTORS)])
    F = F / np.sqrt(len(F))     # scale so factor vols are per-day, not per-window

    Fcov = F.cov() * TRADING_DAYS
    lam = F.mean() * TRADING_DAYS
    print(f"  factor annualised vols: " +
          ", ".join(f"{np.sqrt(Fcov.iloc[i,i])*100:.1f}%" for i in range(min(5, N_FACTORS))))

    # ---------------- per-stock regression on whatever days exist ------------
    betas, resid_var, r2 = {}, {}, {}
    Fv = F.values
    for s in eligible:
        y = rets.loc[s]
        mask = y.notna().values
        X = Fv[mask]
        yy = y.values[mask]
        X1 = np.column_stack([np.ones(len(X)), X])
        coef, *_ = np.linalg.lstsq(X1, yy, rcond=None)
        fitted = X1 @ coef
        resid = yy - fitted
        betas[s] = coef[1:]
        resid_var[s] = float(resid.var(ddof=len(coef)) * TRADING_DAYS)
        ss = float(((yy - yy.mean()) ** 2).sum())
        r2[s] = 1.0 - float((resid ** 2).sum()) / ss if ss > 0 else np.nan

    B = pd.DataFrame(betas, index=F.columns).T.loc[eligible]
    D = pd.Series(resid_var).loc[eligible]
    R2 = pd.Series(r2).loc[eligible]
    print(f"\nRegression fit (R^2): median {R2.median():.2f} | "
          f"long-history {R2.loc[[s for s in eligible if s in long_hist]].median():.2f} | "
          f"short-history {R2.loc[[s for s in eligible if s in short_hist]].median():.2f}")

    # ---------------- assemble Sigma ----------------------------------------
    # Build in numpy: pandas 3.0 exposes .values read-only, so the diagonal
    # must be added before wrapping.
    Sig = B.values @ Fcov.values @ B.values.T
    Sig[np.diag_indices_from(Sig)] += D.values
    Sig = (Sig + Sig.T) / 2                         # kill float asymmetry
    Sigma = pd.DataFrame(Sig, index=eligible, columns=eligible)

    eig = np.linalg.eigvalsh(Sigma.values)
    print(f"\nSigma: {Sigma.shape} | eig min={eig.min():.3e} max={eig.max():.4f} "
          f"| PSD={eig.min() >= -1e-10} | cond={eig.max()/max(eig.min(),1e-12):.1f}")
    assert eig.min() > -1e-10, "factor Sigma is not PSD"

    # ---------------- mu: James-Stein shrinkage by sample size --------------
    # lam is retained only for reporting; it is ~0 by construction (centered PCA)
    # and is deliberately NOT used to build mu. See the module docstring.
    mu_hat = rets.loc[eligible].mean(axis=1) * TRADING_DAYS
    sd_hat = rets.loc[eligible].std(axis=1) * np.sqrt(TRADING_DAYS)
    n_i = n_obs.loc[eligible]

    # target and dispersion measured on the long-history block only, so the
    # noisy short-history estimates cannot contaminate the shrinkage target
    mu_target = float(mu_hat.loc[long_hist].mean())
    tau2 = float(mu_hat.loc[long_hist].var())
    se2 = (sd_hat ** 2) / n_i * TRADING_DAYS      # sampling variance of the annualised mean
    w = tau2 / (tau2 + se2)
    mu_shrunk = w * mu_hat + (1.0 - w) * mu_target

    print(f"\nmu shrinkage: target {mu_target*100:.2f}% | tau {np.sqrt(tau2)*100:.2f}%")
    print(f"  shrinkage weight w: median {w.median():.2f} | "
          f"long-history median {w.loc[long_hist].median():.2f} | "
          f"short-history median {w.loc[[x for x in eligible if x in short_hist]].median():.2f}")
    print(f"  mu raw    range {mu_hat.min()*100:6.1f}% .. {mu_hat.max()*100:6.1f}%")
    print(f"  mu shrunk range {mu_shrunk.min()*100:6.1f}% .. {mu_shrunk.max()*100:6.1f}%")
    print(f"  negative mu: raw {(mu_hat<0).sum()} -> shrunk {(mu_shrunk<0).sum()}")
    print(f"  (factor lambda is {np.abs(lam).max()*100:.4f}% at most - zero by "
          f"construction, hence unused)")

    # ---------------- validation against the existing shrunk Sigma ----------
    print("\n" + "=" * 74)
    print("VALIDATION vs the shrunk sample covariance (997 long-history stocks)")
    print("=" * 74)
    S_ref = pd.read_csv("covariance_matrix_shrunk_usd.csv", index_col=0)
    shared = [s for s in S_ref.index if s in Sigma.index][:400]
    a = Sigma.loc[shared, shared].values
    b = S_ref.loc[shared, shared].values
    iu = np.triu_indices(len(shared), k=1)
    print(f"  off-diagonal correlation : {np.corrcoef(a[iu], b[iu])[0,1]:.3f}")
    print(f"  median off-diag: factor {np.median(a[iu]):.5f} vs sample {np.median(b[iu]):.5f}")
    da, db = np.sqrt(np.diag(a)), np.sqrt(np.diag(b))
    print(f"  per-stock sigma: factor median {np.median(da)*100:.1f}% vs "
          f"sample {np.median(db)*100:.1f}% | corr {np.corrcoef(da, db)[0,1]:.3f}")

    mu_raw = pd.read_csv("expected_return_final_usd.csv").set_index("Stock")["expected_return"]
    both = mu_shrunk.index.intersection(mu_raw.index)
    print(f"  mu vs the existing 10y estimate (997 shared): "
          f"corr {np.corrcoef(mu_shrunk.loc[both], mu_raw.loc[both])[0,1]:.3f}, "
          f"mean abs shift {np.abs(mu_shrunk.loc[both]-mu_raw.loc[both]).mean()*100:.2f} pp")

    # what the newly-included stocks look like under each mu
    newly = [s for s in eligible if s in short_hist]
    print(f"\n  Newly included stocks: {len(newly)}")
    cmp = pd.DataFrame({"n_obs": n_i.loc[newly],
                        "mu_raw": mu_hat.loc[newly] * 100,
                        "w": w.loc[newly],
                        "mu_shrunk": mu_shrunk.loc[newly] * 100}).sort_values(
                        "mu_raw", ascending=False)
    print("  Their raw sample mean vs shrunk mu (top 8, %):")
    print(cmp.head(8).round(2).to_string())
    print(f"  mean: raw {cmp.mu_raw.mean():.1f}% -> shrunk {cmp.mu_shrunk.mean():.1f}%")

    mu_shrunk.to_csv("expected_return_shrunk_usd.csv", header=["expected_return"])
    Sigma.to_csv("covariance_matrix_factor_usd.csv")
    B.to_csv("factor_model_betas.csv")
    print("\nSaved expected_return_shrunk_usd.csv, covariance_matrix_factor_usd.csv, "
          "factor_model_betas.csv")


if __name__ == "__main__":
    main()
