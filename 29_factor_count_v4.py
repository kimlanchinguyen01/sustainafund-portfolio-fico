"""
SustainaFund — 29: is 20 factors still the right number on the CURRENT data?
=============================================================================
WHY THIS EXISTS
The 20-factor choice was made by `pipeline/05d_factor_count.py`, and that script
reads `prices_clean_usd.csv` and `expected_return_shrunk_usd.csv` - USD prices
that are NOT dividend-adjusted, with the pre-v4 expected returns, solved against
the OLD `Model2` (no sector cap, no per-stock ESG floor, no Tier-1 screen).

The data then changed. `20_dividend_adjusted_pipeline.py` rebuilt everything
from total-return prices, and it carries the choice forward as a hard-coded
constant on line 27:

    TD, K, MIN_OBS = 252, 20, 252

So K = 20 is INHERITED, not re-derived. On the current inputs nobody has checked
whether it is still the smallest sufficient number. This checks.

WHAT IS MEASURED
Exactly what 05d measured, because the point is comparability:

    for each k, build the factor covariance, solve the frontier, and compare
    each portfolio's PREDICTED risk (from that covariance) against the risk
    those same weights actually realised over the estimation window.

    error = predicted / realised - 1, in %.  NEGATIVE MEANS THE MODEL
    UNDERSTATES RISK, which is the one failure mode a risk-averse mandate
    cannot tolerate. The right k is the smallest with no negative error
    anywhere on the frontier.

This is an IN-SAMPLE consistency check and has to be read as one. It does not
ask whether the covariance predicts the future; it asks whether a covariance
that declares the residual block diagonal can be gamed by a minimum-variance
optimiser hunting for the blind spot. That is a real and specific failure, and
it is what a low factor count causes.

CONSTRUCTION mirrors `20_dividend_adjusted_pipeline.py` line for line: PCA on
the complete-history stocks, betas fitted per stock on whatever days it has,
residual variance on the diagonal, Sigma = B Fcov B' + diag(D), symmetrised.
PSD by construction.

THE GATE: at k = 20 the rebuilt Sigma must reproduce `covariance_matrix_v4.csv`.
If it does not, the sweep is measuring something other than our model and
nothing below it can be trusted.

Difference from 05d, deliberately: the frontier is solved with the CURRENT model
(`Model2_ori`, so sector cap 30%, per-stock ESG floor 30, Tier-1 exclusion),
because the question is which k is right for the model we ship.

Outputs (results_factor_count/):
    sweep.csv        per k: variance explained, median R2, PSD, condition, errors
    frontier.csv     every frontier point at every k, predicted vs realised
    gate.csv         rebuilt k=20 Sigma vs covariance_matrix_v4.csv

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 29_factor_count_v4.py            # ~10 min

Needs pipeline/prices_div_usd.csv (52 MB, gitignored). Rebuild with
pipeline/20_dividend_adjusted_pipeline.py or ask Chloe.
"""

import os
import sys
import numpy as np
import pandas as pd

import Model2_ori as m2

TD, MIN_OBS = 252, 252
K_GRID = [1, 2, 5, 10, 20, 30, 50]
K_SHIPPED = 20
N_POINTS = m2.N_FRONTIER_POINTS

PRICES = "pipeline/prices_div_usd.csv"
COV_SHIPPED = "covariance_matrix_v4.csv"
OUTDIR = "results_factor_count"

os.makedirs(OUTDIR, exist_ok=True)


def load_returns():
    if not os.path.exists(PRICES):
        sys.exit(f"missing input: {PRICES}\n"
                 "It is gitignored (52 MB). Rebuild it with\n"
                 "  cd pipeline && python3 20_dividend_adjusted_pipeline.py\n"
                 "or ask Chloe for the export.")
    px = pd.read_csv(PRICES, index_col=0)
    px.columns = pd.to_datetime(px.columns)
    end = px.columns.max()
    rets = np.log(px.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]
    print(f"prices {px.shape} | 10y window {rets.shape[1]} days ending {end.date()}")
    return rets


def factor_sigma(rets, k):
    """Mirrors 20_dividend_adjusted_pipeline.py exactly, with K = k."""
    Rv = rets.values
    valid = ~np.isnan(Rv)
    long_mask = valid.all(axis=1)
    stocks = list(rets.index)

    L = Rv[long_mask]
    Lc = (L - L.mean(axis=1, keepdims=True)).T
    U, S_, _ = np.linalg.svd(Lc, full_matrices=False)
    evr = (S_ ** 2) / (S_ ** 2).sum()
    F = (U[:, :k] * S_[:k]) / np.sqrt(len(Lc))
    Fcov = np.cov(F, rowvar=False) * TD
    if k == 1:                      # np.cov collapses to a scalar at k=1
        Fcov = np.atleast_2d(Fcov)
    X = np.column_stack([np.ones(len(F)), F])

    B = np.zeros((len(stocks), k))
    dv = np.full(len(stocks), np.nan)
    r2 = np.full(len(stocks), np.nan)

    li = np.where(long_mask)[0]
    coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
    B[li] = coef[1:].T
    resid = Rv[li].T - X @ coef
    dv[li] = resid.var(axis=0, ddof=k + 1) * TD
    y = Rv[li].T
    ss = ((y - y.mean(axis=0)) ** 2).sum(axis=0)
    r2[li] = 1.0 - (resid ** 2).sum(axis=0) / np.where(ss > 0, ss, np.nan)

    for i in np.where(~long_mask)[0]:
        m = valid[i]
        if m.sum() < MIN_OBS:
            continue
        cf, *_ = np.linalg.lstsq(X[m], Rv[i][m], rcond=None)
        B[i] = cf[1:]
        e = Rv[i][m] - X[m] @ cf
        dv[i] = e.var(ddof=k + 1) * TD
        yy = Rv[i][m]
        s = ((yy - yy.mean()) ** 2).sum()
        r2[i] = 1.0 - (e ** 2).sum() / s if s > 0 else np.nan

    keep = ~np.isnan(dv)
    names = [stocks[i] for i in np.where(keep)[0]]
    Sig = B[keep] @ Fcov @ B[keep].T
    Sig[np.diag_indices_from(Sig)] += dv[keep]
    Sig = (Sig + Sig.T) / 2
    Sigma = pd.DataFrame(Sig, index=names, columns=names)
    Sigma.index.name = "Stock"
    return Sigma, float(evr[:k].sum()), pd.Series(r2[keep], index=names), long_mask, stocks


def realised_vol(rets, w):
    """Volatility those exact weights actually had over the window. Days where
    any held stock is missing are dropped, as 05d did."""
    R = rets.loc[list(w.index)]
    ok = R.notna().all(axis=0)
    return float((R.loc[:, ok].T * w.values).sum(axis=1).std(ddof=1) * np.sqrt(TD))


def main():
    rets = load_returns()
    mu_all = pd.read_csv("expected_return_v4.csv").set_index("Stock")["expected_return"]
    shares = pd.read_csv(m2.FILE_SHARES).set_index("Stock")
    sectors = pd.read_excel(m2.FILE_SECTORS).set_index("Stock")["Sector"]

    sweep, front_rows, gate = [], [], None

    for k in K_GRID:
        Sigma, evr, r2, long_mask, stocks = factor_sigma(rets, k)
        eig = np.linalg.eigvalsh(Sigma.values)

        if k == K_SHIPPED and os.path.exists(COV_SHIPPED):
            shipped = pd.read_csv(COV_SHIPPED, index_col=0)
            common = sorted(set(shipped.index) & set(Sigma.index))
            d = (Sigma.loc[common, common].values - shipped.loc[common, common].values)
            gate = {"k": k, "stocks_rebuilt": len(Sigma), "stocks_shipped": len(shipped),
                    "stocks_common": len(common),
                    "max_abs_diff": float(np.abs(d).max()),
                    "max_rel_diff": float(np.abs(d).max()
                                          / np.abs(shipped.loc[common, common].values).max())}
            print(f"\n  GATE at k=20: rebuilt {len(Sigma)} vs shipped {len(shipped)} stocks, "
                  f"max |diff| {gate['max_abs_diff']:.3e}")

        # solve the frontier on this Sigma, with the CURRENT constraint set
        common = sorted(set(mu_all.index) & set(Sigma.index) & set(shares.index))
        esg = shares.loc[common, "ESG score"].astype(float)
        keep = esg >= m2.ESG_FLOOR if m2.ENABLE_ESG_FLOOR else pd.Series(True, index=common)
        univ = [s for s in common if keep[s]]
        args = (mu_all.loc[univ], Sigma.loc[univ, univ], shares.loc[univ, "Region"],
                shares.loc[univ, "ESG score"].astype(float),
                sectors.reindex(univ).fillna("Unknown"))
        kw = dict(time_limit=180, verbose=False)

        lo = m2.solve_model2(*args, mode="min_risk_only", **kw)
        hi = m2.solve_model2(*args, mode="max_return_only", **kw)
        if not (lo["feasible"] and hi["feasible"]):
            print(f"k={k:3d}  corners infeasible - skipped")
            continue

        errs = []
        for i, b in enumerate(np.linspace(lo["portfolio_return"],
                                          hi["portfolio_return"], N_POINTS)):
            r = m2.solve_model2(*args, mode="min_risk", target_return=b, **kw)
            if not r["feasible"]:
                continue
            w = r["weights"]
            w = w[w > 1e-9]
            w = w / w.sum()
            rv = realised_vol(rets, w)
            err = (r["portfolio_risk"] / rv - 1) * 100
            errs.append(err)
            front_rows.append({"k": k, "pt": i, "ret_%": r["portfolio_return"] * 100,
                               "pred_risk_%": r["portfolio_risk"] * 100,
                               "realised_risk_%": rv * 100, "err_%": err,
                               "n": r["n_selected"]})

        row = {"k": k, "universe": len(univ), "var_explained_%": evr * 100,
               "r2_median": float(r2.median()), "psd": bool(eig.min() >= 0),
               "cond": float(eig.max() / eig.min()),
               "err_mean_%": float(np.mean(errs)), "err_minrisk_%": float(errs[0]),
               "err_worst_%": float(np.min(errs)),
               "understates_anywhere": bool(np.min(errs) < 0)}
        sweep.append(row)
        print(f"k={k:3d}  var expl {evr*100:5.1f}%  R2 med {r2.median():.3f}  "
              f"PSD {str(eig.min() >= 0):>5}  cond {eig.max()/eig.min():8.1f}  "
              f"err mean {np.mean(errs):+7.2f}%  min-risk {errs[0]:+7.1f}%  "
              f"worst {np.min(errs):+7.2f}%", flush=True)

    S = pd.DataFrame(sweep)
    S.to_csv(f"{OUTDIR}/sweep.csv", index=False)
    pd.DataFrame(front_rows).to_csv(f"{OUTDIR}/frontier.csv", index=False)
    if gate:
        pd.DataFrame([gate]).to_csv(f"{OUTDIR}/gate.csv", index=False)

    print("\n" + "=" * 100)
    print("IS 20 STILL THE RIGHT NUMBER, ON THE CURRENT (DIVIDEND-ADJUSTED) DATA?")
    print("=" * 100)
    print(S.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    ok = S[~S.understates_anywhere]
    if len(ok):
        kbest = int(ok["k"].min())
        print(f"\nSmallest k with NO understatement anywhere on the frontier: k = {kbest}")
        if kbest == K_SHIPPED:
            print(f"  -> the shipped choice of {K_SHIPPED} is confirmed on the new data")
        elif kbest < K_SHIPPED:
            print(f"  -> {K_SHIPPED} is MORE than needed; {kbest} would do. "
                  f"Keeping {K_SHIPPED} is conservative, not wrong.")
        else:
            print(f"  -> {K_SHIPPED} is NOT ENOUGH on the new data; the smallest "
                  f"sufficient k is {kbest}. This would need acting on.")
    else:
        print("\nNo k in the grid avoids understatement everywhere.")

    print("\nFor comparison, 05d on the OLD (non-dividend-adjusted) data reported:")
    print("  k=1 understated risk by 39.9% at the min-risk end; 20 was the")
    print("  smallest k with no understatement anywhere.")
    print(f"\nWrote 3 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
