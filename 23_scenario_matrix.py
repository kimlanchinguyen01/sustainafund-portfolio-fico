"""
23 — The full scenario matrix, every cell solved rather than inferred
=====================================================================
Axes 2, 3, 4 and 5 of the scenario framework, run end to end on the current
inputs so no figure in the deck is an estimate.

For every configuration the three risk profiles are extracted with Chloe's
definitions from analyze_risk.py: minimum risk, maximum return/risk ratio,
maximum return.
"""
import numpy as np, pandas as pd, Model2_ori as m2, profile_rule as pr

BASE=dict(ENABLE_ESG_CONSTRAINT=True, ENABLE_ESG_FLOOR=True, ESG_FLOOR=30.0,
          ENABLE_SECTOR_CAP=True, ENABLE_TIER1_EXCLUSION=True, ENABLE_TIER2_EXCLUSION=False)

CONFIGS=[
 # axis 2 — the 2x2 ESG matrix
 ("A  no ESG at all",        dict(ENABLE_ESG_CONSTRAINT=False, ENABLE_ESG_FLOOR=False)),
 ("C  floor 30 only",        dict(ENABLE_ESG_CONSTRAINT=False, ENABLE_ESG_FLOOR=True)),
 ("B  average 70 only",      dict(ENABLE_ESG_CONSTRAINT=True,  ENABLE_ESG_FLOOR=False)),
 ("D  both (final)",         dict()),
 # axis 4 — floor threshold sensitivity
 ("D + floor 40",            dict(ESG_FLOOR=40.0)),
 ("D + floor 20",            dict(ESG_FLOOR=20.0)),
 # axis 5 — sector cap on/off
 ("D, sector cap off",       dict(ENABLE_SECTOR_CAP=False)),
 # axis 3 — controversial-industry policy
 ("D + Tier 2 excluded",     dict(ENABLE_TIER2_EXCLUSION=True)),
]

def apply(over):
    for k,v in {**BASE,**over}.items(): setattr(m2,k,v)

rows=[]
for label,over in CONFIGS:
    apply(over)
    mu,Sigma,region,esg,sector=m2.load_data()
    kw=dict(time_limit=300, mip_gap=0.001, verbose=False)
    lo=m2.solve_model2(mu,Sigma,region,esg,sector,mode="min_risk_only",**kw)
    hi=m2.solve_model2(mu,Sigma,region,esg,sector,mode="max_return_only",**kw)
    assert lo["feasible"] and hi["feasible"], label
    grid=np.linspace(lo["portfolio_return"],hi["portfolio_return"],15)
    front=[r for r in (m2.solve_model2(mu,Sigma,region,esg,sector,mode="min_risk",
                                       target_return=b,**kw) for b in grid) if r["feasible"]]
    F=pd.DataFrame([{k:v for k,v in r.items() if k!="weights"} for r in front])
    F["sharpe"]=F.portfolio_return/F.portfolio_risk
    # canonical rule - see profile_rule.py. Was idxmax(return), which picks the
    # degenerate max-return corner rather than a portfolio.
    PROF=pr.pick_profiles(pr.rows_from_results(front))
    print(f"\n{label}  (universe {len(mu)})")
    for p,i in PROF.items():
        r=front[i]; w=r["weights"]; w=w[w>1e-9]
        rows.append({"config":label,"profile":p,"universe":len(mu),
                     "ret_%":r["portfolio_return"]*100,"risk_%":r["portfolio_risk"]*100,
                     "sharpe":r["portfolio_return"]/r["portfolio_risk"],
                     "esg":r["esg_weighted"],"n":len(w),
                     "min_esg_held":float(esg.loc[w.index].min()),
                     "top3_%":float(w.head(3).sum())*100 if len(w)>=3 else np.nan})
        print(f"    {p:12s} ret {r['portfolio_return']*100:6.2f}%  risk {r['portfolio_risk']*100:6.2f}%  "
              f"sharpe {r['portfolio_return']/r['portfolio_risk']:.3f}  ESG {r['esg_weighted']:5.2f}  "
              f"n {len(w):3d}  minESG {esg.loc[w.index].min():5.1f}")
M=pd.DataFrame(rows); M.to_csv("scenario_matrix.csv",index=False)
print("\n"+"="*100); print("ЗВЕДЕНА МАТРИЦЯ"); print("="*100)
for p in ["Risk Averse","Neutral","Risk Prone"]:
    print(f"\n{p}")
    t=M[M.profile==p].set_index("config")[["ret_%","risk_%","sharpe","esg","n","min_esg_held"]]
    print(t.round(3).to_string())
print("\nSaved scenario_matrix.csv")
