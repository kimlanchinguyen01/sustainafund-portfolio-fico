"""
15 — Model 1: linear risk measure, and what ignoring correlation costs
======================================================================
The case study offers two routes to portfolio risk and encourages comparing
them. Model 2/3 takes the covariance route (quadratic). This is the other one.

    Model 1 (MILP)   minimise  sum_i w_i * sigma_i
    Model 3 (MIQP)   minimise  w' Sigma w

sum_i w_i*sigma_i is the portfolio standard deviation you would get if every
pair of stocks were PERFECTLY correlated. It is therefore an upper bound on the
true portfolio risk, and it is completely blind to diversification: swapping a
stock for another with the same sigma never changes the objective, no matter how
differently the two move.

Constraints are identical, so the two models differ only in the objective. That
is asserted, not assumed: the same problem builder is first run with the
QUADRATIC objective and checked against Model3's own solution.

The comparison that matters is not "which reports a lower number" - the two
numbers are not on the same scale. It is: take the portfolio Model 1 chooses,
measure its TRUE risk w'Sigma w, and compare with what Model 3 achieves at the
same expected return. That difference is the cost of ignoring correlation.
"""

import os
import numpy as np, pandas as pd
os.environ["XPAUTH_PATH"]=os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import xpress as xp
import Model3

Model3.COUNTRY_CAP=0.25
W_MIN,W_MAX,REGION_CAP,MIN_STOCKS,ESG_MIN,CTRY_CAP=0.01,0.20,0.60,30,70.0,0.25
EXEMPT={"United States"}

sh=pd.read_csv("shares_imputed.csv").set_index("Stock")
mu=pd.read_csv("expected_return_v3.csv",index_col=0)["expected_return"]
sd=pd.read_csv("per_stock_risk_v3.csv",index_col=0)["risk_std"]
Sg=pd.read_csv("covariance_matrix_v3.csv",index_col=0)
common=sorted(set(mu.index)&set(sd.index)&set(Sg.index)&set(sh.index))
MU=mu.loc[common].values; SD=sd.loc[common].values
SIG=Sg.loc[common,common].values
REG=sh.loc[common,"Region"].values; ESG=sh.loc[common,"ESG score"].values.astype(float)
CTY=sh.loc[common,"Country"].values
n=len(common)
print(f"universe {n} | per-stock sigma {SD.min()*100:.1f}%..{SD.max()*100:.1f}% "
      f"(mean {SD.mean()*100:.1f}%)")


def solve(objective, target_return=None, risk_cap=None, tl=180):
    """Identical constraint set; objective is 'linear' or 'quadratic'."""
    p=xp.problem("Model1" if objective=="linear" else "Model1_qcontrol")
    p.controls.outputlog=0; p.controls.miprelstop=0.01; p.controls.timelimit=tl
    w=p.addVariables(n,lb=0,ub=W_MAX,name="w")
    y=p.addVariables(n,vartype=xp.binary,name="y")
    p.addConstraint(w<=W_MAX*y); p.addConstraint(w>=W_MIN*y)
    p.addConstraint(xp.Sum(w)==1); p.addConstraint(xp.Sum(y)>=MIN_STOCKS)
    for r in np.unique(REG):
        p.addConstraint(xp.Sum(w[REG==r])<=REGION_CAP)
    p.addConstraint(xp.Dot(ESG,w)>=ESG_MIN)
    for c in np.unique(CTY):
        if c in EXEMPT: continue
        p.addConstraint(xp.Sum(w[CTY==c])<=CTRY_CAP)
    if target_return is not None:
        p.addConstraint(xp.Dot(MU,w)>=target_return)
    obj = xp.Dot(SD,w) if objective=="linear" else xp.Dot(w,SIG,w)
    p.setObjective(obj,sense=xp.minimize)
    ss,sol=p.optimize()
    if sol.name not in ("OPTIMAL","FEASIBLE"): return None
    ws=np.array(p.getSolution(w))
    return {"w":pd.Series(ws,index=common),"ret":float(MU@ws),
            "risk_true":float(np.sqrt(ws@SIG@ws)),"risk_linear":float(SD@ws),
            "n":int(round(sum(p.getSolution(y)))),"esg":float(ESG@ws)}


# ------------------------------------------------ control: same constraints?
print("\n"+"="*90)
print("CONTROL: same builder with the QUADRATIC objective must equal Model3")
print("="*90)
a=solve("quadratic")
b=Model3.solve_model2(mu.loc[common],Sg.loc[common,common],sh.loc[common,"Region"],
                      sh.loc[common,"ESG score"],country=sh.loc[common,"Country"],
                      mode="min_risk_only",time_limit=180)
dw=float((a["w"]-b["weights"]).abs().max())
print(f"  risk: mine {a['risk_true']*100:.4f}%  Model3 {b['portfolio_risk']*100:.4f}%  "
      f"| max|dw| {dw:.2e}")
assert dw<1e-6 and abs(a["risk_true"]-b["portfolio_risk"])<1e-8, "constraint sets differ!"
print("  PASS - the constraint set is identical; only the objective differs")

# ------------------------------------------------ frontiers
print("\n"+"="*90)
print("MODEL 1 (linear) vs MODEL 3 (quadratic), at matched expected return")
print("="*90)
q_lo=solve("quadratic"); q_hi_ret=max(MU)
grid=np.linspace(max(q_lo["ret"],solve("linear")["ret"]),0.155,10)
print(f"{'target ret':>11} {'M1 true risk':>13} {'M3 true risk':>13} {'M1 penalty':>11} "
      f"{'M1 linear obj':>14} {'M1 n':>5} {'M3 n':>5}")
rows=[]
for t in grid:
    m1=solve("linear",target_return=t); m3=solve("quadratic",target_return=t)
    if not (m1 and m3): continue
    pen=(m1["risk_true"]/m3["risk_true"]-1)*100
    rows.append({"target_ret_%":t*100,"m1_true_risk_%":m1["risk_true"]*100,
                 "m3_true_risk_%":m3["risk_true"]*100,"penalty_%":pen,
                 "m1_linear_obj_%":m1["risk_linear"]*100,"m1_n":m1["n"],"m3_n":m3["n"],
                 "overlap":len(set(m1["w"][m1["w"]>1e-9].index)&set(m3["w"][m3["w"]>1e-9].index))})
    print(f"{t*100:10.2f}% {m1['risk_true']*100:12.2f}% {m3['risk_true']*100:12.2f}% "
          f"{pen:+10.1f}% {m1['risk_linear']*100:13.2f}% {m1['n']:5d} {m3['n']:5d}")
R=pd.DataFrame(rows)
print(f"\nmean risk penalty from ignoring correlation: {R['penalty_%'].mean():+.1f}%"
      f"  (range {R['penalty_%'].min():+.1f}% .. {R['penalty_%'].max():+.1f}%)")
print(f"holdings overlap between the two models: "
      f"{R.overlap.min()}-{R.overlap.max()} of ~{int(R.m3_n.mean())} names")

print("\n"+"="*90)
print("WHY THE TWO RISK NUMBERS ARE NOT COMPARABLE")
print("="*90)
m1=solve("linear",target_return=0.13)
print(f"Model 1's own objective for its own portfolio : {m1['risk_linear']*100:.2f}%")
print(f"That portfolio's actual standard deviation     : {m1['risk_true']*100:.2f}%")
print(f"ratio                                          : "
      f"{m1['risk_linear']/m1['risk_true']:.2f}x")
print("sum(w_i sigma_i) assumes every pair is perfectly correlated, so it is an")
print("upper bound. The gap between the two IS the diversification the linear")
print("model cannot see - and therefore cannot optimise for.")
R.to_csv("model1_vs_model3.csv",index=False)
print("\nSaved model1_vs_model3.csv")
