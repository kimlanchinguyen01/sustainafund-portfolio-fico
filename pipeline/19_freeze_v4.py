"""
19 — Freeze v4: our USD/factor inputs + Chloe's 30% sector cap
==============================================================
Team decision: keep one concentration constraint, and keep hers (sector 30%)
rather than the country cap. Inputs are the ones prepared today - USD-converted
prices, James-Stein mu, 20-factor PCA covariance, 1093 stocks with the two
trading discontinuities truncated.

Controls run first, so anything that moves afterwards is attributable:
  Model4 with every addition disabled must reproduce Model2 exactly.

Variants solved (tags derive from the config, so they cannot collide):
  sec30            sector cap only            <- the deliverable, per instruction
  sec30_t1         + Tier 1 screen            <- Chloe's shipped default
  nosec            neither                    <- baseline, to price the cap
"""

import os
import numpy as np, pandas as pd
os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2, Model4

BUDGET, TD = 100_000_000, 252
sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
mu = pd.read_csv("expected_return_v3.csv", index_col=0)["expected_return"]
Sg = pd.read_csv("covariance_matrix_v3.csv", index_col=0)
sec = pd.read_excel("sectors.xlsx").set_index("Stock")["Sector"]
c = sorted(set(mu.index) & set(Sg.index) & set(sh.index) & set(sec.index))
MU, SG = mu.loc[c], Sg.loc[c, c]
REG, ESG, SEC = sh.loc[c, "Region"], sh.loc[c, "ESG score"], sec.loc[c]
prices = pd.read_csv("prices_clean_usd_v3.csv", index_col=0)
prices.columns = pd.to_datetime(prices.columns)
end = prices.columns.max()
rets = np.log(prices.loc[:, end - pd.DateOffset(years=10):end]).diff(axis=1).iloc[:, 1:]
print(f"universe {len(c)} | sectors {SEC.nunique()} | inputs: expected_return_v3, covariance_matrix_v3")

# ---------------------------------------------------------------- control
print("\n" + "=" * 96)
print("CONTROL: Model4 with all additions off must equal Model2")
print("=" * 96)
Model4.ENABLE_SECTOR_CAP = False
Model4.ENABLE_TIER1 = Model4.ENABLE_TIER2 = False
Model2.MIP_GAP = Model4.MIP_GAP = 0.001
for mode in ["min_risk_only", "max_return_only"]:
    a = Model4.solve_model2(MU, SG, REG, ESG, sector=SEC, mode=mode, time_limit=300, mip_gap=0.001)
    b = Model2.solve_model2(MU, SG, REG, ESG, mode=mode, time_limit=300, mip_gap=0.001)
    dw = float((a["weights"] - b["weights"]).abs().max())
    print(f"  {mode:16s} dret {abs(a['portfolio_return']-b['portfolio_return']):.2e} "
          f"drisk {abs(a['portfolio_risk']-b['portfolio_risk']):.2e} max|dw| {dw:.2e}")
    assert dw < 1e-8, "Model4 diverges from Model2 with additions off!"
print("  PASS — the only behavioural changes are the cap and the screen")


def frontier(sector_cap, t1, n=15):
    Model4.ENABLE_SECTOR_CAP = sector_cap
    Model4.ENABLE_TIER1 = t1
    Model4.ENABLE_TIER2 = False
    tag = Model4.scenario_tag()
    kw = dict(time_limit=300, mip_gap=0.001, verbose=False)
    lo = Model4.solve_model2(MU, SG, REG, ESG, sector=SEC, mode="min_risk_only", **kw)
    hi = Model4.solve_model2(MU, SG, REG, ESG, sector=SEC, mode="max_return_only", **kw)
    grid = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n)
    out = [r for r in (Model4.solve_model2(MU, SG, REG, ESG, sector=SEC, mode="min_risk",
                                           target_return=b, **kw) for b in grid) if r["feasible"]]
    print(f"  tag={tag:12s} {len(out):2d}/{n} pts | risk "
          f"{min(r['portfolio_risk'] for r in out)*100:5.2f}.."
          f"{max(r['portfolio_risk'] for r in out)*100:5.2f}% | return "
          f"{out[0]['portfolio_return']*100:5.2f}..{out[-1]['portfolio_return']*100:5.2f}%")
    return tag, out


print("\n" + "=" * 96)
print("VARIANTS (tag auto-derived from config — the bug in Model2_ori is gone)")
print("=" * 96)
V = {}
for scap, t1 in [(False, False), (True, False), (True, True)]:
    tag, out = frontier(scap, t1)
    V[tag] = out

DELIVERABLE = "sec30"
print(f"\n=> deliverable: {DELIVERABLE} (sector cap only, per instruction)")


def H(r):
    w = r["weights"]
    return w[w > 1e-9].sort_values(ascending=False)


def realised(w):
    R = rets.loc[list(w.index)]
    ok = R.notna().all(axis=0)
    return float((R.loc[:, ok].T * w.values).sum(axis=1).std(ddof=1) * np.sqrt(TD)), int(ok.sum())


for tag, out in V.items():
    EF = pd.DataFrame([{k: v for k, v in r.items() if k != "weights"} for r in out])
    ratio = EF.portfolio_return / EF.portfolio_risk
    rows = []
    for i, r in enumerate(out):
        w = H(r)
        rows.append({"pt": i, "top3": w.head(3).sum(), "floor": int((w <= 0.01001).sum())})
    T = pd.DataFrame(rows)
    deg = (T.top3 > 0.40) | (T.floor > 15)
    ok = EF[~deg.values]
    PROF = {"risk-averse": int(EF.portfolio_risk.idxmin()),
            "neutral": int(ratio.idxmax()),
            "risk-prone": int(ok.portfolio_return.idxmax())}
    EF.to_csv(f"efficient_frontier_{tag}.csv", index=False)
    pd.DataFrame({f"beta_{i}": r["weights"] for i, r in enumerate(out)}).to_csv(
        f"efficient_frontier_weights_{tag}.csv")
    if tag != DELIVERABLE:
        continue
    print("\n" + "=" * 96)
    print(f"FROZEN v4  ({tag})")
    print("=" * 96)
    summary = []
    for label, pt in PROF.items():
        r = out[pt]
        w = H(r)
        cw = w.groupby(sh.loc[w.index, "Country"]).sum().sort_values(ascending=False)
        sw = w.groupby(SEC.loc[w.index]).sum().sort_values(ascending=False)
        rw = w.groupby(sh.loc[w.index, "Region"]).sum()
        esgw = float(sh.loc[w.index, "ESG score"] @ w)
        checks = [("sum(w)=1", abs(w.sum() - 1) < 1e-6), ("w>=1%", w.min() >= 0.01 - 1e-9),
                  ("w<=20%", w.max() <= 0.20 + 1e-9), ("n>=30", len(w) >= 30),
                  ("region<=60%", rw.max() <= 0.60 + 1e-6), ("ESG>=70", esgw >= 70 - 1e-6),
                  ("sector<=30%", sw.max() <= 0.30 + 1e-6)]
        assert all(x[1] for x in checks), (label, [x for x in checks if not x[1]])
        rl, nd = realised(w)
        exus = cw.drop("United States", errors="ignore")
        print(f"\n{label} (pt{pt}) — PASS all 7")
        print(f"  return {r['portfolio_return']*100:.2f}% | risk {r['portfolio_risk']*100:.2f}% "
              f"(realised {rl*100:.2f}%, {nd}d) | ratio {r['portfolio_return']/r['portfolio_risk']:.2f} "
              f"| {len(w)} holdings | max pos {w.max()*100:.2f}%")
        print(f"  sectors : " + ", ".join(f"{k} {v*100:.1f}%" for k, v in sw.head(4).items()))
        print(f"  countries: US {cw.get('United States',0)*100:.1f}%, "
              + ", ".join(f"{k} {v*100:.1f}%" for k, v in exus.head(3).items()))
        print(f"  ESG {esgw:.2f} | Europe {rw.get('Europe',0)*100:.1f}% | "
              f"Rheinmetall {float(w.get('RHMG.DE',0))*100:.2f}%")
        pd.DataFrame({"weight_%": (w * 100).round(3), "amount_USD": (w * BUDGET).round(0),
                      "Region": sh.loc[w.index, "Region"], "Country": sh.loc[w.index, "Country"],
                      "Sector": SEC.loc[w.index], "ESG": sh.loc[w.index, "ESG score"].round(1),
                      "exp_return_%": (mu.reindex(w.index) * 100).round(2)}).to_csv(
            f"FROZEN_v4_portfolio_{label.replace('-','_')}.csv")
        prev = pd.read_csv(f"FROZEN_v3_portfolio_{label.replace('-','_')}.csv",
                           index_col=0)["weight_%"] / 100
        sa, sb = set(w.index), set(prev.index)
        idx = sorted(sa | sb)
        summary.append({"profile": label, "pt": pt, "n": len(w),
                        "ret_%": r["portfolio_return"] * 100, "risk_%": r["portfolio_risk"] * 100,
                        "risk_realised_%": rl * 100,
                        "ratio": r["portfolio_return"] / r["portfolio_risk"], "ESG": esgw,
                        "wEU_%": float(rw.get("Europe", 0)) * 100,
                        "max_pos_%": float(w.max()) * 100,
                        "top_sector": sw.index[0], "top_sector_%": float(sw.iloc[0]) * 100,
                        "top_ctry_exUS": exus.index[0], "top_ctry_exUS_%": float(exus.iloc[0]) * 100,
                        "RHMG_%": float(w.get("RHMG.DE", 0)) * 100,
                        "jaccard_vs_v3": len(sa & sb) / len(sa | sb),
                        "active_vs_v3_%": 0.5 * float((w.reindex(idx).fillna(0) -
                                                       prev.reindex(idx).fillna(0)).abs().sum()) * 100})
    S = pd.DataFrame(summary)
    S.to_csv("FROZEN_v4_portfolio_summary.csv", index=False)
    print("\n" + S.round(2).to_string(index=False))

print("\n" + "=" * 96)
print("WHAT THE SECTOR CAP COSTS, AND WHAT DROPPING THE COUNTRY CAP COSTS")
print("=" * 96)
cur = {}
for tag, out in V.items():
    x = np.array([r["portfolio_risk"] for r in out]) * 100
    y = np.array([r["portfolio_return"] for r in out]) * 100
    o = np.argsort(x)
    cur[tag] = (x[o], y[o])
lo_r = max(v[0].min() for v in cur.values()); hi_r = min(v[0].max() for v in cur.values())
risks = np.linspace(lo_r, hi_r, 6)
tab = pd.DataFrame({k: [float(np.interp(r, v[0], v[1])) for r in risks] for k, v in cur.items()},
                   index=[f"{r:.2f}%" for r in risks])
print(tab.round(3).to_string())
print("\nmean cost vs no cap (pp):")
for k in tab.columns:
    if k != "nosec":
        print(f"  {k:12s} {(tab[k]-tab['nosec']).mean():+7.3f}")
tab.to_csv("v4_variant_scenarios.csv")
print("\nSaved FROZEN_v4_portfolio_*.csv, efficient_frontier_{nosec,sec30,sec30_t1}.csv, "
      "v4_variant_scenarios.csv")
