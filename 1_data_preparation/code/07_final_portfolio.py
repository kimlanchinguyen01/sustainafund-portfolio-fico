"""
07 — FINAL PORTFOLIO SELECTION (freeze candidate)
=================================================
Model decisions, all fixed:
    prices      USD-converted (03a), ECB reference rates, cached
    mu          James-Stein shrinkage by sample size (04a)
    Sigma       20-factor PCA model, all 1093 stocks, PSD (05d)
    window      10 YEARS - chosen on economic grounds, see below
    solver      Model2.py, unmodified

Why 10 years and not 5
----------------------
This is a judgement, not a computation, and it is stated as one. SustainaFund's
mandate is mid-term asset allocation, so the estimate should span a full market
cycle including the 2018 correction and the 2020 drawdown, rather than only the
post-2020 regime. The 5-year window covers COVID recovery, the inflation shock
and the AI boom - a single, unusually favourable regime - and it inflates the
frontier accordingly (max return 21.2% on 5y vs 16.6% on 10y).

The cost of that choice is measured, not hidden: see the limitation section at
the end, which reports how far the 5-year window would have moved the portfolio.

Three risk profiles, as the case study requests:
    risk-averse  minimum-variance portfolio
    neutral      highest return/risk ratio on the frontier
    risk-prone   maximum-return portfolio

Every constraint is re-verified independently of the solver, so the numbers can
be audited without rerunning anything.
"""

from paths import P   # where each data file lives (see paths.py)

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

BUDGET = 100_000_000
TD = 252
SHARES = P("shares_imputed.csv")

sh = pd.read_csv(SHARES).set_index("Stock")
W = pd.read_csv(P("efficient_frontier_weights_final.csv"), index_col=0)
EF = pd.read_csv(P("efficient_frontier_final.csv"))
Sigma = pd.read_csv(P("covariance_matrix_factor_final.csv"), index_col=0)
mu = pd.read_csv(P("expected_return_shrunk_usd.csv")).set_index("Stock")["expected_return"]

prices = pd.read_csv(P("prices_clean_usd.csv"), index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
rets = np.log(prices.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]

ratio = EF.portfolio_return / EF.portfolio_risk
PROFILES = {
    "risk-averse": int(EF.portfolio_risk.idxmin()),
    "neutral": int(ratio.idxmax()),
    "risk-prone": int(EF.portfolio_return.idxmax()),
}
print("Frontier (10y, 20-factor, all 1093 stocks):")
show = EF[["n_selected", "portfolio_return", "portfolio_risk", "esg_weighted",
           "weight_region_Europe"]].copy()
show.columns = ["n", "ret", "risk", "ESG", "wEU"]
show[["ret", "risk", "wEU"]] *= 100
show["ret/risk"] = ratio.round(3)
show["profile"] = ["" for _ in range(len(show))]
for k, v in PROFILES.items():
    show.loc[v, "profile"] = k
print(show.round(2).to_string())
print("\n(return/risk uses a zero risk-free rate - no risk-free series in the dataset)")


def realised_risk(w):
    R = rets.loc[list(w.index)]
    ok = R.notna().all(axis=0)
    s = (R.loc[:, ok].T * w.values).sum(axis=1)
    return float(s.std(ddof=1) * np.sqrt(TD)), int(ok.sum())


def audit(w, label):
    """Re-verify every constraint from the weight vector alone."""
    n = len(w)
    reg = sh.loc[w.index, "Region"]
    esg = sh.loc[w.index, "ESG score"]
    checks = [
        ("budget fully invested   sum(w) == 1", abs(w.sum() - 1) < 1e-6, f"{w.sum():.10f}"),
        ("min weight              w >= 1%", w.min() >= 0.01 - 1e-9, f"min {w.min()*100:.4f}%"),
        ("max weight              w <= 20%", w.max() <= 0.20 + 1e-9, f"max {w.max()*100:.4f}%"),
        ("diversification         n >= 30", n >= 30, f"n = {n}"),
        ("region cap              <= 60%",
         w.groupby(reg).sum().max() <= 0.60 + 1e-6,
         " | ".join(f"{k} {v*100:.2f}%" for k, v in w.groupby(reg).sum().items())),
        ("ESG                     >= 70", float(esg @ w) >= 70 - 1e-6, f"{float(esg @ w):.4f}"),
    ]
    print(f"\n  CONSTRAINT AUDIT - {label}")
    for name, ok, val in checks:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name:38s} {val}")
    assert all(c[1] for c in checks), f"{label}: constraint violated"


summary = []
for label, pt in PROFILES.items():
    w = W[f"beta_{pt}"].fillna(0.0)
    w = w[w > 1e-9].sort_values(ascending=False)
    print("\n" + "=" * 92)
    print(f"{label.upper()}  (frontier point {pt})")
    print("=" * 92)
    audit(w, label)

    real, ndays = realised_risk(w)
    pred = float(EF.loc[pt, "portfolio_risk"])
    ret = float(EF.loc[pt, "portfolio_return"])
    print(f"\n  expected return     {ret*100:6.2f}% p.a.   -> ${ret*BUDGET/1e6:,.1f}M on $100M")
    print(f"  predicted risk      {pred*100:6.2f}% p.a.")
    print(f"  realised risk       {real*100:6.2f}% p.a.  (same portfolio over {ndays} "
          f"days of actual history; model is {'conservative' if pred>=real else 'optimistic'} "
          f"by {abs(pred/real-1)*100:.1f}%)")
    print(f"  holdings            {len(w)}")
    print(f"  largest position    {w.max()*100:.2f}%  (${w.max()*BUDGET/1e6:.1f}M)")

    reg = w.groupby(sh.loc[w.index, "Region"]).sum()
    print(f"  region              " + " | ".join(f"{k} {v*100:.1f}%" for k, v in reg.items()))
    ctry = w.groupby(sh.loc[w.index, "Country"]).sum().sort_values(ascending=False)
    print(f"  top countries       " + ", ".join(f"{k} {v*100:.1f}%" for k, v in ctry.head(5).items()))
    print(f"  ESG weighted        {float(sh.loc[w.index,'ESG score'] @ w):.2f}  "
          f"(range held: {sh.loc[w.index,'ESG score'].min():.1f}-"
          f"{sh.loc[w.index,'ESG score'].max():.1f})")

    hold = pd.DataFrame({
        "weight_%": (w * 100).round(3),
        "amount_USD": (w * BUDGET).round(0),
        "Region": sh.loc[w.index, "Region"],
        "Country": sh.loc[w.index, "Country"],
        "ESG": sh.loc[w.index, "ESG score"].round(1),
        "exp_return_%": (mu.reindex(w.index) * 100).round(2),
    })
    print(f"\n  Top 12 holdings:")
    print(hold.head(12).to_string())
    hold.to_csv(P(f"FINAL_portfolio_{label.replace('-','_')}.csv"))

    summary.append({"profile": label, "frontier_pt": pt, "n_holdings": len(w),
                    "exp_return_%": ret * 100, "risk_predicted_%": pred * 100,
                    "risk_realised_%": real * 100, "return_risk_ratio": ret / pred,
                    "ESG": float(sh.loc[w.index, "ESG score"] @ w),
                    "weight_Europe_%": float(reg.get("Europe", 0)) * 100,
                    "weight_US_%": float(reg.get("United States", 0)) * 100,
                    "max_position_%": float(w.max()) * 100})

S = pd.DataFrame(summary)
S.to_csv(P("FINAL_portfolio_summary.csv"), index=False)
print("\n" + "=" * 92)
print("SUMMARY - the three portfolios put to management")
print("=" * 92)
print(S.round(2).to_string(index=False))

# ------------------------------------------------------------------ limitation
print("\n" + "=" * 92)
print("STATED LIMITATION: what the window choice costs")
print("=" * 92)
f10 = pd.read_csv(P("bootstrap_selection_freq_10y.csv"), index_col=0)
f5 = pd.read_csv(P("bootstrap_selection_freq_5y.csv"), index_col=0)
a = set(f10.index[f10.pt0 >= 0.9])
b = set(f5.index[f5.pt0 >= 0.9])
print(f"Bootstrap (100 resamples per window) selection core at the min-risk end:")
print(f"  stocks selected in >=90% of resamples: 10y {len(a)} | 5y {len(b)} | "
      f"in both {len(a & b)} | Jaccard {len(a&b)/len(a|b):.2f}")
print(f"\n  Within a window the bootstrap is stable (top frequency "
      f"{f10.pt0.max():.2f}); across windows even the core disagrees.")
print(f"  This is regime change, not sampling noise - which is why resampling")
print(f"  cannot resolve it and the window has to be chosen and defended.")

ex = ["LMT.N", "NOC.N", "RTX.N", "BA.N"]
ex = [s for s in ex if s in f10.index]
print(f"\n  The clearest example - defence names:")
print(pd.DataFrame({
    "freq_10y": f10.loc[ex, "pt0"].round(2),
    "freq_5y": f5.loc[ex, "pt0"].round(2),
    "Country": sh.loc[ex, "Country"],
    "ESG": sh.loc[ex, "ESG score"].round(1),
}).to_string())
print("  Defence became a low-volatility holding only after 2022. The 5-year")
print("  window treats that as a permanent feature; the 10-year window does not.")
print("  We chose the 10-year view deliberately and report this as its cost.")
print("\nSaved FINAL_portfolio_{risk_averse,neutral,risk_prone}.csv, "
      "FINAL_portfolio_summary.csv")
