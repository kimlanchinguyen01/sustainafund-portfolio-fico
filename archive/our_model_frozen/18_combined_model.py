"""
18 — Do the two caps overlap? Country (ours) vs sector (Chloe's)
===============================================================
Both models descend from Model2 with the same objective and the same core
constraints. Ours adds a 25% country cap; Chloe's adds a 30% sector cap plus a
controversial-industry screen. The question is not which model is better but
whether the two caps do the same work.

They might: the 45% Switzerland exposure our country cap removed was Swiss
cantonal banks and real estate, so a sector cap could catch part of it, and the
35% Consumer Defensive exposure her sector cap removed is largely US staples,
which a country cap would not touch.

One builder with a toggle per constraint, so every combination is the same code.
Validated against both existing models before being trusted.
"""

import os
import numpy as np, pandas as pd
os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import xpress as xp
import Model3

W_MIN, W_MAX, REGION_CAP, MIN_STOCKS, ESG_MIN = 0.01, 0.20, 0.60, 30, 70.0
COUNTRY_CAP, SECTOR_CAP = 0.25, 0.30
EXEMPT = {"United States"}
T1 = ["RHMG.DE"]
T2 = ["LMT.N","RTX.N","NOC.N","GD.N","LHX.N","KOG.OL","BAES.L","TCFP.PA","LDOF.MI","SAABb.ST"]
GAP, N_PTS = 0.001, 12

sh = pd.read_csv("shares_imputed.csv").set_index("Stock")
mu = pd.read_csv("expected_return_v3.csv", index_col=0)["expected_return"]
Sg = pd.read_csv("covariance_matrix_v3.csv", index_col=0)
sec = pd.read_excel("sectors.xlsx").set_index("Stock")["Sector"]
c = sorted(set(mu.index) & set(Sg.index) & set(sh.index) & set(sec.index))
MU, SIG = mu.loc[c].values, Sg.loc[c, c].values
REG, ESG = sh.loc[c,"Region"].values, sh.loc[c,"ESG score"].values.astype(float)
CTY, SEC = sh.loc[c,"Country"].values, sec.loc[c].values
TICK = np.array(c); n = len(c)


def solve(country=False, sector=False, t1=False, t2=False, target=None, mode="min_risk", tl=300):
    p = xp.problem("combined"); p.controls.outputlog=0
    p.controls.miprelstop=GAP; p.controls.timelimit=tl
    w = p.addVariables(n, lb=0, ub=W_MAX, name="w")
    y = p.addVariables(n, vartype=xp.binary, name="y")
    p.addConstraint(w <= W_MAX*y); p.addConstraint(w >= W_MIN*y)
    p.addConstraint(xp.Sum(w) == 1); p.addConstraint(xp.Sum(y) >= MIN_STOCKS)
    for r in np.unique(REG): p.addConstraint(xp.Sum(w[REG==r]) <= REGION_CAP)
    p.addConstraint(xp.Dot(ESG, w) >= ESG_MIN)
    if country:
        for k in np.unique(CTY):
            if k not in EXEMPT: p.addConstraint(xp.Sum(w[CTY==k]) <= COUNTRY_CAP)
    if sector:
        for s in np.unique(SEC): p.addConstraint(xp.Sum(w[SEC==s]) <= SECTOR_CAP)
    if t1:
        m = np.isin(TICK, T1)
        if m.any(): p.addConstraint(xp.Sum(w[m]) <= 0.0)
    if t2:
        m = np.isin(TICK, T2)
        if m.any(): p.addConstraint(xp.Sum(w[m]) <= 0.0)
    if target is not None: p.addConstraint(xp.Dot(MU, w) >= target)
    p.setObjective(xp.Dot(w, SIG, w) if mode!="max_return_only" else xp.Dot(MU, w),
                   sense=xp.minimize if mode!="max_return_only" else xp.maximize)
    ss, sol = p.optimize()
    if sol.name not in ("OPTIMAL","FEASIBLE"): return None
    ws = np.array(p.getSolution(w))
    return {"w": pd.Series(ws, index=c), "ret": float(MU@ws),
            "risk": float(np.sqrt(ws@SIG@ws)), "n": int((ws>1e-9).sum())}


# ---------------------------------------------------------------- validation
print("VALIDATION against the two existing models")
print("=" * 90)
a = solve()
b = Model3.solve_model2(mu.loc[c], Sg.loc[c,c], sh.loc[c,"Region"], sh.loc[c,"ESG score"],
                        country=sh.loc[c,"Country"], mode="min_risk_only", time_limit=300)
Model3.COUNTRY_CAP = 1.0
b0 = Model3.solve_model2(mu.loc[c], Sg.loc[c,c], sh.loc[c,"Region"], sh.loc[c,"ESG score"],
                         country=sh.loc[c,"Country"], mode="min_risk_only", time_limit=300)
print(f"  no caps      : mine {a['risk']*100:.4f}%  Model3(cap off) {b0['portfolio_risk']*100:.4f}%  "
      f"delta {abs(a['risk']-b0['portfolio_risk'])*1e4:.3f} bp")
Model3.COUNTRY_CAP = 0.25
d = solve(country=True)
b1 = Model3.solve_model2(mu.loc[c], Sg.loc[c,c], sh.loc[c,"Region"], sh.loc[c,"ESG score"],
                         country=sh.loc[c,"Country"], mode="min_risk_only", time_limit=300)
print(f"  country cap  : mine {d['risk']*100:.4f}%  Model3           {b1['portfolio_risk']*100:.4f}%  "
      f"delta {abs(d['risk']-b1['portfolio_risk'])*1e4:.3f} bp")
print("  (Model3 uses gap 0.01, this builder 0.001, so a few bp of difference is expected)")


def frontier(**kw):
    lo = solve(mode="min_risk_only", **kw); hi = solve(mode="max_return_only", **kw)
    if not (lo and hi): return None
    g = np.linspace(lo["ret"], hi["ret"], N_PTS)
    out = [r for r in (solve(target=t, **kw) for t in g) if r]
    x = np.array([r["risk"] for r in out])*100; y = np.array([r["ret"] for r in out])*100
    o = np.argsort(x); return x[o], y[o], out


def binds(res):
    """max country and sector exposure reached anywhere on the frontier"""
    mc = ms = 0.0; nc = ns = ""
    for r in res:
        w = r["w"][r["w"]>1e-9]
        cw = w.groupby(sh.loc[w.index,"Country"]).sum().drop("United States", errors="ignore")
        sw = w.groupby(sec.loc[w.index]).sum()
        if len(cw) and cw.max()>mc: mc, nc = float(cw.max()), str(cw.idxmax())
        if sw.max()>ms: ms, ns = float(sw.max()), str(sw.idxmax())
    return mc, nc, ms, ns


print("\n" + "=" * 90)
print("DO THE CAPS OVERLAP?  max exposure reached with each combination")
print("=" * 90)
COMBOS = [("neither", dict()),
          ("country only (ours)", dict(country=True)),
          ("sector only (Chloe)", dict(sector=True)),
          ("both", dict(country=True, sector=True)),
          ("both + Tier1", dict(country=True, sector=True, t1=True)),
          ("both + Tier1 + Tier2", dict(country=True, sector=True, t1=True, t2=True))]
F = {}
print(f"{'combination':24s} {'top country ex-US':>26s} {'top sector':>26s}")
for lbl, kw in COMBOS:
    f = frontier(**kw)
    if not f: print(f"{lbl:24s} INFEASIBLE"); continue
    F[lbl] = f
    mc, nc, ms, ns = binds(f[2])
    print(f"{lbl:24s} {nc[:14]:>14s} {mc*100:6.2f}%{'*' if mc>0.249 else ' '} "
          f"{ns[:16]:>16s} {ms*100:6.2f}%{'*' if ms>0.299 else ' '}")
print("  * = at its cap, i.e. the constraint is binding")

print("\n" + "=" * 90)
print("RETURN AT MATCHED RISK, and the cost of each combination")
print("=" * 90)
lo_r = max(v[0].min() for v in F.values()); hi_r = min(v[0].max() for v in F.values())
risks = np.linspace(lo_r, hi_r, 6)
tab = pd.DataFrame({k: [float(np.interp(r, v[0], v[1])) for r in risks] for k, v in F.items()},
                   index=[f"{r:.2f}%" for r in risks])
print(tab.round(3).to_string())
cost = tab.drop(columns=["neither"]).sub(tab["neither"], axis=0)
print("\nmean cost vs unconstrained (pp):")
for k in cost.columns: print(f"  {k:24s} {cost[k].mean():+7.3f}")
tab.to_csv("combined_cap_scenarios.csv")
print("\nSaved combined_cap_scenarios.csv")
