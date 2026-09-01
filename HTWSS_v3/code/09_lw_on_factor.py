"""
09 — Priority 3: Ledoit-Wolf shrinkage on top of the factor covariance
=====================================================================
Chloe's P3. This is canonical Ledoit-Wolf (2003), where the shrinkage TARGET is
a factor model and the shrunk estimator is

    Sigma(delta) = delta * F + (1 - delta) * S

with F the 20-factor PCA covariance (all 1093 stocks) and S the sample
covariance. delta = 1 is what is currently frozen; delta = 0 is the raw sample.

Two things make this a sensitivity check rather than a model change:
  * S exists only for the 997 complete-history stocks, so the blend can only be
    applied to that block; the 96 recent listings keep pure F. Block-wise
    blending is NOT automatically PSD, so every candidate is eigenvalue-checked
    and any that fails is reported rather than patched.
  * Model3.py and the FROZEN_* portfolios are not touched. The question asked
    here is only: would shrinkage have changed the answer?

delta is chosen OUT OF SAMPLE, not by an analytic formula. Every estimator is
built on 2015-12-31..2020-12-31 and scored on how well it predicts the risk that
portfolios actually realised over 2021-01-01..2025-12-31. That also closes the
limitation flagged earlier - every previous risk validation in this project was
in-sample.
"""

import os

import warnings

import numpy as np
import pandas as pd

# stocks absent from a window produce all-NaN slices; they are dropped by the
# `keep` mask below, so the warnings carry no information
warnings.filterwarnings('ignore', message='Mean of empty slice')
warnings.filterwarnings('ignore', message='Degrees of freedom <= 0')

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model3

TD = 252
K = 20
MIN_OBS = 252
DELTAS = [0.0, 0.25, 0.50, 0.75, 0.90, 1.0]
SPLIT = "2020-12-31"

sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
prices = pd.read_csv("prices_clean_usd.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
allr = np.log(prices.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]

train = allr.loc[:, :SPLIT]
test = allr.loc[:, SPLIT:].iloc[:, 1:]
print(f"train {train.columns.min().date()}..{train.columns.max().date()} "
      f"({train.shape[1]} days) | test {test.columns.min().date()}.."
      f"{test.columns.max().date()} ({test.shape[1]} days)")


def factor_sigma(R, k=K):
    """20-factor PCA Sigma + James-Stein mu on a returns frame."""
    Rv = R.values
    valid = ~np.isnan(Rv)
    n_obs = valid.sum(axis=1)
    long_mask = valid.all(axis=1)
    L = Rv[long_mask]
    Lc = (L - L.mean(axis=1, keepdims=True)).T
    U, S_, _ = np.linalg.svd(Lc, full_matrices=False)
    F = (U[:, :k] * S_[:k]) / np.sqrt(len(Lc))
    Fcov = np.cov(F, rowvar=False) * TD
    X = np.column_stack([np.ones(len(F)), F])

    stocks = list(R.index)
    B = np.zeros((len(stocks), k))
    dv = np.full(len(stocks), np.nan)
    li = np.where(long_mask)[0]
    coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
    B[li] = coef[1:].T
    dv[li] = (Rv[li].T - X @ coef).var(axis=0, ddof=k + 1) * TD
    for i in np.where(~long_mask)[0]:
        m = valid[i]
        if m.sum() < MIN_OBS:
            continue
        c, *_ = np.linalg.lstsq(X[m], Rv[i][m], rcond=None)
        B[i] = c[1:]
        dv[i] = (Rv[i][m] - X[m] @ c).var(ddof=k + 1) * TD

    keep = ~np.isnan(dv)
    names = [stocks[i] for i in np.where(keep)[0]]
    Sig = B[keep] @ Fcov @ B[keep].T
    Sig[np.diag_indices_from(Sig)] += dv[keep]
    Sig = (Sig + Sig.T) / 2

    mu_hat = np.nanmean(Rv, axis=1) * TD
    sd_hat = np.nanstd(Rv, axis=1, ddof=1) * np.sqrt(TD)
    tgt = float(np.mean(mu_hat[long_mask]))
    tau2 = float(np.var(mu_hat[long_mask]))
    se2 = (sd_hat ** 2) / np.maximum(n_obs, 1) * TD
    wgt = tau2 / (tau2 + se2)
    mu = wgt * mu_hat + (1 - wgt) * tgt
    return (pd.Series(mu[keep], index=names),
            pd.DataFrame(Sig, index=names, columns=names),
            [stocks[i] for i in li])


def blend(Fdf, R, long_names, delta):
    """delta*F + (1-delta)*S on the complete-history block; pure F elsewhere."""
    if delta >= 1.0:
        return Fdf.copy()
    ln = [s for s in long_names if s in Fdf.index]
    S = pd.DataFrame(np.cov(R.loc[ln].values) * TD, index=ln, columns=ln)
    out = Fdf.to_numpy(copy=True)          # pandas 3.0: to_numpy() alone is read-only
    pos = {s: i for i, s in enumerate(Fdf.index)}
    ix = np.array([pos[s] for s in ln])
    blk = delta * Fdf.loc[ln, ln].to_numpy() + (1 - delta) * S.to_numpy()
    out[np.ix_(ix, ix)] = blk
    out = (out + out.T) / 2
    return pd.DataFrame(out, index=Fdf.index, columns=Fdf.columns)


def attach(mu, Sg):
    c = sorted(set(mu.index) & set(Sg.index) & set(sh.index))
    return (mu.loc[c], Sg.loc[c, c], sh.loc[c, "Region"], sh.loc[c, "ESG score"],
            sh.loc[c, "Country"])


def frontier(mu, Sg, n=8):
    a = attach(mu, Sg)
    args = (a[0], a[1], a[2], a[3])
    lo = Model3.solve_model2(*args, country=a[4], mode="min_risk_only", time_limit=180)
    hi = Model3.solve_model2(*args, country=a[4], mode="max_return_only", time_limit=180)
    if not (lo["feasible"] and hi["feasible"]):
        return []
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n)
    return [r for r in (Model3.solve_model2(*args, country=a[4], mode="min_risk",
                                            target_return=b, time_limit=180)
                        for b in grid) if r["feasible"]]


def realised(w, R):
    Rw = R.loc[[s for s in w.index if s in R.index]]
    ok = Rw.notna().all(axis=0)
    ww = w.loc[Rw.index]
    ww = ww / ww.sum()
    return float((Rw.loc[:, ok].T * ww.values).sum(axis=1).std(ddof=1) * np.sqrt(TD)), int(ok.sum())


# ---------------------------------------------------------------- OUT OF SAMPLE
print("\n" + "=" * 94)
print("CHOOSING delta OUT OF SAMPLE: fit on train, score risk prediction on test")
print("=" * 94)
mu_tr, F_tr, long_tr = factor_sigma(train)
print(f"train universe {len(mu_tr)} | complete-history {len(long_tr)}")

print(f"\n{'delta':>6} {'PSD':>6} {'min eig':>11} {'cond':>9} "
      f"{'mean err %':>11} {'minrisk err %':>14} {'|err| mean %':>13}")
res = {}
for d in DELTAS:
    Sg = blend(F_tr, train, long_tr, d)
    eig = np.linalg.eigvalsh(Sg.to_numpy())
    psd = eig.min() >= -1e-10
    front = frontier(mu_tr, Sg)
    if not front:
        print(f"{d:6.2f} {'--':>6} infeasible")
        continue
    errs = []
    for r in front:
        w = r["weights"]
        w = w[w > 1e-9]
        rl, nd = realised(w, test)
        errs.append((r["portfolio_risk"] / rl - 1) * 100)
    res[d] = {"errs": errs, "psd": psd, "eig": eig.min(),
              "cond": eig.max() / eig.min() if eig.min() > 0 else np.inf,
              "front": front}
    print(f"{d:6.2f} {str(psd):>6} {eig.min():11.3e} "
          f"{res[d]['cond']:9.1f} {np.mean(errs):+10.2f}% {errs[0]:+13.2f}% "
          f"{np.mean(np.abs(errs)):12.2f}%")

valid = {d: v for d, v in res.items() if v["psd"]}
best = min(valid, key=lambda d: abs(np.mean(valid[d]["errs"])))
best_abs = min(valid, key=lambda d: np.mean(np.abs(valid[d]["errs"])))
print(f"\nclosest to unbiased out of sample : delta = {best:.2f} "
       f"(mean error {np.mean(valid[best]['errs']):+.2f}%)")
print(f"lowest absolute error            : delta = {best_abs:.2f} "
       f"(mean |error| {np.mean(np.abs(valid[best_abs]['errs'])):.2f}%)")
print(f"currently frozen                 : delta = 1.00 "
      f"(mean error {np.mean(valid[1.0]['errs']):+.2f}%, "
      f"mean |error| {np.mean(np.abs(valid[1.0]['errs'])):.2f}%)")
if any(not v["psd"] for v in res.values()):
    print("NOT PSD at delta = " + ", ".join(f"{d:.2f}" for d, v in res.items() if not v["psd"]))
else:
    print("all blends PSD - block-wise blending held up here (it is not guaranteed to)")

# ---------------------------------------------------- would it move the freeze?
print("\n" + "=" * 94)
print("WOULD SHRINKAGE HAVE CHANGED THE FROZEN PORTFOLIOS? (full 10y window)")
print("=" * 94)
mu_full, F_full, long_full = factor_sigma(allr)
FROZ = pd.read_csv("FROZEN_portfolio_summary.csv")
Wf = pd.read_csv("efficient_frontier_weights_final_capped.csv", index_col=0)

print(f"{'delta':>6} {'PSD':>6} {'minrisk ret%':>13} {'minrisk risk%':>14} "
      f"{'n':>4} {'Jac vs frozen':>14} {'active vs frozen':>17}")
w_frozen = Wf["beta_0"].fillna(0.0)
w_frozen = w_frozen[w_frozen > 1e-9]
for d in DELTAS:
    Sg = blend(F_full, allr, long_full, d)
    eig = np.linalg.eigvalsh(Sg.to_numpy())
    front = frontier(mu_full, Sg)
    if not front:
        print(f"{d:6.2f} infeasible")
        continue
    r0 = front[int(np.argmin([r["portfolio_risk"] for r in front]))]
    w = r0["weights"]
    w = w[w > 1e-9]
    sa, sb = set(w.index), set(w_frozen.index)
    idx = sorted(sa | sb)
    jac = len(sa & sb) / len(sa | sb)
    act = 0.5 * float((w.reindex(idx).fillna(0) - w_frozen.reindex(idx).fillna(0)).abs().sum())
    print(f"{d:6.2f} {str(eig.min() >= -1e-10):>6} {r0['portfolio_return']*100:12.2f}% "
          f"{r0['portfolio_risk']*100:13.2f}% {r0['n_selected']:4d} "
          f"{jac:14.2f} {act*100:16.1f}%")

print("\nJaccard 1.00 / active 0.0% would mean shrinkage changes nothing.")
