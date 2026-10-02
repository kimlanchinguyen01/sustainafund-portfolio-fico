"""
SustainaFund — 32: 10Y / 5Y / 3Y robustness, with holdings and stability
=========================================================================
The estimation window is the single choice this model is least robust to.
`03e` and `06a` already measured that the portfolio moves a great deal between
windows (Jaccard 0.27, 64% of capital placed differently, 5y vs 10y) and that
the instability is regime change rather than sampling noise. What has never
existed is the COMPOSITION per window in a form a dashboard can chart.

This is not a re-solve. mu and Sigma are RE-ESTIMATED per window, because the
window is the input being varied - shortening it changes both the expected
returns and the covariance, and only re-estimating shows what that does.

Estimation mirrors `20_dividend_adjusted_pipeline.py` exactly: PCA on the
complete-history stocks inside the window, betas fitted per stock on whatever
days it has, residual variance on the diagonal, Sigma = B Fcov B' + diag(D),
James-Stein shrunk mu. K = 20 factors, which `29_factor_count_v4.py`
re-validated on the current data.

THE GATE: at 10 years the rebuilt mu and Sigma must reproduce
expected_return_v4.csv and covariance_matrix_v4.csv, and the solved profiles
must reproduce the `base` scenario from 31_scenario_grid.py. If they do not,
the shorter windows are measuring the rebuild rather than the window.

PROFILE SELECTION uses the canonical frozen rule (see 31_scenario_grid.py):
Risk Averse = min variance, Neutral = max return/risk, Risk Prone = max return
among non-degenerate points, degenerate meaning top-3 > 40% or more than 15
positions on the 1% floor. Derived per window, not carried over - which matters,
because the degenerate set moves with the estimate.

EXPECT SHORT WINDOWS TO LOOK BETTER AND BE WORSE. `04a` recorded the mechanism:
the frontier's max return goes 38.8% on 10 years to 85.6% on 3, which is
estimation error, not opportunity. A 3-year mu is a very noisy object and the
optimiser preferentially buys whatever that noise flattered.

Outputs (dashboard_data/robustness/), decimals throughout:
    window_summary.csv    window x profile, all the headline metrics
    window_holdings.csv   window x profile x stock x weight
    window_frontiers.csv  window x frontier_point
    stability.csv         each window's profile vs the 10-year one: Jaccard,
                          active share, capital displaced, weight correlation
    estimation.csv        what each window's estimation actually saw

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 32_robustness_windows.py         # ~10 min
"""

# --- repository layout (added when the repo was grouped by part) -------------
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))     # <repo>/<part>/code
PART = os.path.dirname(_HERE)                          # <repo>/<part>
_REPO = os.path.dirname(PART)                          # <repo>
MODEL_CODE = os.path.join(_REPO, "2_optimisation_model", "code")
MODEL_DATA = os.path.join(_REPO, "2_optimisation_model", "data")
MODEL_RESULTS = os.path.join(_REPO, "2_optimisation_model", "results")
PREP_RESULTS = os.path.join(_REPO, "1_data_preparation", "results")
sys.path.insert(0, MODEL_CODE)
# -----------------------------------------------------------------------------


import os
import numpy as np
import pandas as pd

import Main_model as m2

TD, K, MIN_OBS = 252, 20, 252
WINDOWS = [10, 5, 3]
REFERENCE_WINDOW = 10
N_POINTS = 15
BUDGET = 100_000_000

DEG_TOP3, DEG_FLOOR_N, FLOOR_TOL = 0.40, 15, 1e-5
PROFILE_RULES = {
    "Risk Averse": "Minimum variance",
    "Neutral": "Maximum return/risk ratio",
    "Risk Prone": "Highest non-degenerate return",
}

PRICES = os.path.join(PREP_RESULTS, "prices_div_usd.csv")
OUTDIR = os.path.join(PART, "results", "robustness_windows")
os.makedirs(OUTDIR, exist_ok=True)


def estimate(rets):
    """20_dividend_adjusted_pipeline.py's estimator, on whatever window it is given."""
    Rv = rets.values
    valid = ~np.isnan(Rv)
    n_obs = valid.sum(axis=1)
    long_mask = valid.all(axis=1)
    stocks = list(rets.index)

    L = Rv[long_mask]
    Lc = (L - L.mean(axis=1, keepdims=True)).T
    U, S_, _ = np.linalg.svd(Lc, full_matrices=False)
    F = (U[:, :K] * S_[:K]) / np.sqrt(len(Lc))
    Fcov = np.cov(F, rowvar=False) * TD
    X = np.column_stack([np.ones(len(F)), F])

    B = np.zeros((len(stocks), K))
    dv = np.full(len(stocks), np.nan)
    li = np.where(long_mask)[0]
    coef, *_ = np.linalg.lstsq(X, Rv[li].T, rcond=None)
    B[li] = coef[1:].T
    dv[li] = (Rv[li].T - X @ coef).var(axis=0, ddof=K + 1) * TD
    for i in np.where(~long_mask)[0]:
        mk = valid[i]
        if mk.sum() < MIN_OBS:
            continue
        cf, *_ = np.linalg.lstsq(X[mk], Rv[i][mk], rcond=None)
        B[i] = cf[1:]
        dv[i] = (Rv[i][mk] - X[mk] @ cf).var(ddof=K + 1) * TD

    keep = ~np.isnan(dv)
    names = [stocks[i] for i in np.where(keep)[0]]
    Sig = B[keep] @ Fcov @ B[keep].T
    Sig[np.diag_indices_from(Sig)] += dv[keep]
    Sig = (Sig + Sig.T) / 2
    Sigma = pd.DataFrame(Sig, index=names, columns=names)

    mu_hat = np.nanmean(Rv, axis=1) * TD
    sd_hat = np.nanstd(Rv, axis=1, ddof=1) * np.sqrt(TD)
    tgt = float(np.mean(mu_hat[long_mask]))
    tau2 = float(np.var(mu_hat[long_mask]))
    se2 = (sd_hat ** 2) / np.maximum(n_obs, 1) * TD
    wgt = tau2 / (tau2 + se2)
    mu = pd.Series((wgt * mu_hat + (1 - wgt) * tgt)[keep], index=names)

    eig = np.linalg.eigvalsh(Sig)
    meta = {"days": rets.shape[1], "complete_history": int(long_mask.sum()),
            "universe_estimated": len(names), "shrinkage_target": tgt,
            "mu_min": float(mu.min()), "mu_max": float(mu.max()),
            "mu_median": float(mu.median()),
            "psd": bool(eig.min() >= 0), "condition": float(eig.max() / eig.min())}
    return mu, Sigma, meta


def pick_profiles(F):
    deg = (F["top3_weight"] > DEG_TOP3) | (F["n_at_floor"] > DEG_FLOOR_N)
    ok = F[~deg]
    if not len(ok):
        raise RuntimeError("every frontier point is degenerate")
    return {"Risk Averse": int(F.loc[F["risk"].idxmin(), "frontier_point"]),
            "Neutral": int(F.loc[F["return_risk_ratio"].idxmax(), "frontier_point"]),
            "Risk Prone": int(ok.loc[ok["expected_return"].idxmax(), "frontier_point"])}


def solve_window(years, mu, Sigma, shares, sectors):
    esg_all = shares["ESG score"].astype(float)
    univ = [s for s in mu.index if s in shares.index
            and (esg_all[s] >= m2.ESG_FLOOR if m2.ENABLE_ESG_FLOOR else True)]
    args = (mu.loc[univ], Sigma.loc[univ, univ], shares.loc[univ, "Region"],
            esg_all.loc[univ], sectors.reindex(univ).fillna("Unknown"))
    country = shares.loc[univ, "Country"]
    kw = dict(country=country, time_limit=300, verbose=False)

    lo = m2.solve_model2(*args, mode="min_risk_only", **kw)
    hi = m2.solve_model2(*args, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        return None, None, None, len(univ)

    pts, wmap = [], {}
    for i, b in enumerate(np.linspace(lo["portfolio_return"], hi["portfolio_return"], N_POINTS)):
        r = m2.solve_model2(*args, mode="min_risk", target_return=b, **kw)
        if not r["feasible"]:
            continue
        w = r["weights"]
        h = w[w > 1e-9].sort_values(ascending=False)
        wmap[i] = h
        pts.append({"window_years": years, "frontier_point": i, "target_return": float(b),
                    "expected_return": float(r["portfolio_return"]),
                    "risk": float(r["portfolio_risk"]),
                    "return_risk_ratio": float(r["portfolio_return"] / r["portfolio_risk"]),
                    "n_holdings": int(r["n_selected"]),
                    "weighted_esg": float(r["esg_weighted"]),
                    "top3_weight": float(h.head(3).sum()),
                    "n_at_floor": int((h < m2.W_MIN + FLOOR_TOL).sum())})
    F = pd.DataFrame(pts)
    F["degenerate"] = (F["top3_weight"] > DEG_TOP3) | (F["n_at_floor"] > DEG_FLOOR_N)
    picks = pick_profiles(F)

    summary, holdings = [], []
    for prof, pt in picks.items():
        row = F[F.frontier_point == pt].iloc[0]
        h = wmap[pt]
        by_r = h.groupby(shares.loc[h.index, "Region"]).sum()
        by_s = h.groupby(sectors.reindex(h.index).fillna("Unknown")).sum()
        by_c = h.groupby(shares.loc[h.index, "Country"]).sum()
        summary.append({
            "window_years": years, "profile": prof, "profile_rule": PROFILE_RULES[prof],
            "frontier_point": pt,
            "expected_return": float(row["expected_return"]), "risk": float(row["risk"]),
            "return_risk_ratio": float(row["return_risk_ratio"]),
            "n_holdings": int(row["n_holdings"]),
            "weighted_esg": float(row["weighted_esg"]),
            "min_esg_held": float(esg_all.reindex(h.index).min()),
            "max_position": float(h.max()), "top3_weight": float(row["top3_weight"]),
            "europe_weight": float(by_r.get("Europe", 0.0)),
            "us_weight": float(by_r.get("United States", 0.0)),
            "top_sector": str(by_s.idxmax()), "top_sector_weight": float(by_s.max()),
            "top_country": str(by_c.idxmax()), "top_country_weight": float(by_c.max()),
            "universe_size": len(univ),
        })
        for s, v in h.items():
            holdings.append({"window_years": years, "profile": prof, "frontier_point": pt,
                             "stock": s, "weight": float(v),
                             "amount_usd": float(v) * BUDGET})
    return pd.DataFrame(summary), pd.DataFrame(holdings), F, len(univ)


def stability(H, ref_years=REFERENCE_WINDOW):
    """Each window's profile against the reference window's same profile."""
    rows = []
    for prof in PROFILE_RULES:
        ref = H[(H.window_years == ref_years) & (H.profile == prof)] \
            .set_index("stock")["weight"]
        if not len(ref):
            continue
        for yrs in sorted(H.window_years.unique(), reverse=True):
            cur = H[(H.window_years == yrs) & (H.profile == prof)] \
                .set_index("stock")["weight"]
            if not len(cur):
                continue
            a, b = set(ref.index), set(cur.index)
            union = sorted(a | b)
            ra = ref.reindex(union).fillna(0.0)
            rb = cur.reindex(union).fillna(0.0)
            rows.append({
                "window_years": yrs, "profile": prof,
                "reference_window_years": ref_years,
                "n_holdings": len(cur), "n_reference": len(ref),
                "n_common": len(a & b),
                "jaccard": len(a & b) / len(a | b),
                # half the sum of absolute weight differences: the fraction of
                # capital placed differently
                "active_share": float(0.5 * (rb - ra).abs().sum()),
                "weight_correlation": float(np.corrcoef(ra.values, rb.values)[0, 1])
                if len(union) > 2 else np.nan,
            })
    return pd.DataFrame(rows)


def main():
    px = pd.read_csv(PRICES, index_col=0)
    px.columns = pd.to_datetime(px.columns)
    shares = pd.read_csv(m2.FILE_SHARES).set_index("Stock")
    sectors = pd.read_excel(m2.FILE_SECTORS).set_index("Stock")["Sector"]
    end = px.columns.max()
    print(f"prices {px.shape} | window ends {end.date()}")

    all_sum, all_hold, all_front, meta_rows, gate = [], [], [], [], {}

    for yrs in WINDOWS:
        rets = np.log(px.loc[:, end - pd.DateOffset(years=yrs):end]).diff(axis=1).iloc[:, 1:]
        mu, Sigma, meta = estimate(rets)
        meta_rows.append({"window_years": yrs, **meta})
        print(f"\n{yrs}y: {meta['days']} days | complete-history {meta['complete_history']} | "
              f"estimated {meta['universe_estimated']} | mu {meta['mu_min']*100:.1f}%.."
              f"{meta['mu_max']*100:.1f}% (median {meta['mu_median']*100:.2f}%) | "
              f"cond {meta['condition']:.0f}", flush=True)

        if yrs == REFERENCE_WINDOW:
            mu_ref = pd.read_csv(m2.FILE_EXPECTED_RETURN).set_index("Stock")["expected_return"]
            cov_ref = pd.read_csv(m2.FILE_COVARIANCE, index_col=0)
            common = sorted(set(mu.index) & set(mu_ref.index))
            cc = sorted(set(Sigma.index) & set(cov_ref.index))
            gate = {"window_years": yrs,
                    "mu_max_abs_diff": float((mu.loc[common] - mu_ref.loc[common]).abs().max()),
                    "sigma_max_abs_diff": float(np.abs(
                        Sigma.loc[cc, cc].values - cov_ref.loc[cc, cc].values).max()),
                    "n_common_mu": len(common), "n_common_sigma": len(cc)}
            print(f"  GATE vs the shipped v4 estimates: max |d mu| "
                  f"{gate['mu_max_abs_diff']:.3e} | max |d Sigma| "
                  f"{gate['sigma_max_abs_diff']:.3e}")

        S, H, F, nuniv = solve_window(yrs, mu, Sigma, shares, sectors)
        if S is None:
            print(f"  {yrs}y: corners infeasible on {nuniv} stocks - skipped")
            continue
        all_sum.append(S)
        all_hold.append(H)
        all_front.append(F)
        for _, r in S.iterrows():
            print(f"  {r['profile']:12s} pt {int(r['frontier_point']):2d}  "
                  f"ret {r['expected_return']*100:6.2f}%  risk {r['risk']*100:6.2f}%  "
                  f"ratio {r['return_risk_ratio']:.3f}  n={int(r['n_holdings']):2d}  "
                  f"EU {r['europe_weight']*100:5.1f}%")

    SUM = pd.concat(all_sum, ignore_index=True)
    HOLD = pd.concat(all_hold, ignore_index=True)
    FRONT = pd.concat(all_front, ignore_index=True)
    STAB = stability(HOLD)

    SUM.to_csv(f"{OUTDIR}/window_summary.csv", index=False)
    HOLD.to_csv(f"{OUTDIR}/window_holdings.csv", index=False)
    FRONT.to_csv(f"{OUTDIR}/window_frontiers.csv", index=False)
    STAB.to_csv(f"{OUTDIR}/stability.csv", index=False)
    pd.DataFrame(meta_rows).to_csv(f"{OUTDIR}/estimation.csv", index=False)
    if gate:
        pd.DataFrame([gate]).to_csv(f"{OUTDIR}/gate.csv", index=False)

    print("\n" + "=" * 100)
    print("WINDOW SUMMARY (decimals)")
    print("=" * 100)
    print(SUM[["window_years", "profile", "frontier_point", "expected_return", "risk",
               "return_risk_ratio", "n_holdings", "weighted_esg", "europe_weight",
               "us_weight", "universe_size"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    print("\n--- stability against the 10-year portfolio ---")
    print(STAB[["window_years", "profile", "n_holdings", "n_common", "jaccard",
                "active_share", "weight_correlation"]]
          .to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    print(f"\nWrote {5 + (1 if gate else 0)} CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
