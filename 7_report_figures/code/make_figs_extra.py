import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy import stats
for f in fm.findSystemFonts():
    if "Carlito" in f: fm.fontManager.addfont(f)
plt.rcParams.update({"font.family":"Carlito","font.size":10,"axes.edgecolor":"#8a8985","axes.linewidth":0.6,
    "xtick.color":"#52514e","ytick.color":"#52514e","axes.labelcolor":"#0b0b0b","xtick.major.width":0.6,"ytick.major.width":0.6})
BLUE,ORANGE,AQUA,INK,GREY,GRID="#2a78d6","#eb6834","#1baf7a","#0b0b0b","#8a8985","#e6e5e0"
import os
_CODE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(_CODE)
R = os.path.join(os.path.dirname(PART), "")      # repository root
OUT = os.path.join(PART, "results", "")           # figures are written here

def clean(ax,grid="y"):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.grid(True,axis=grid,color=GRID,lw=0.5); ax.set_axisbelow(True)

# Figures for the report. Run from anywhere: python 7_report_figures/code/make_figs_extra.py
# Figure A: cost of each constraint at Neutral (pp of expected return)
s=pd.read_csv(R+"2_optimisation_model/results/scenario_matrix.csv"); n=s[s.profile=="Neutral"].set_index("config")["ret_%"]
esg=n["A  no ESG at all"]-n["B  average 70 only"]
floor=n["C  floor 30 only"]-n["A  no ESG at all"]       # negative cost (return rises)
sector=n["D, sector cap off"]-n["D  both (final)"]
tier2=n["D  both (final)"]-n["D + Tier 2 excluded"]
cc=pd.read_csv(R+"2_optimisation_model/results/country_cap/cap_cost.csv"); cc=cc[(cc.cap=="25%")&(cc.pt==8)]
country=-float(cc["d_ret_pp_at_matched_risk"].iloc[0])   # return given up at equal risk, Neutral (point 8)
items=[("Weighted ESG score of at least 70 (brief)",esg,BLUE,False),
       ("Country cap of 25% (optional)",country,GREY,True),
       ("Sector cap of 30%",sector,BLUE,False),
       ("Tier 2 defence exclusion (optional)",tier2,GREY,True)]
fig,ax=plt.subplots(figsize=(6.3,2.2),dpi=300)
for i,(lab,v,c,off) in enumerate(items[::-1]):
    ax.barh(i,v,height=0.55,color=("white" if off else c),edgecolor=c,linewidth=1.1,hatch=("////" if off else None))
    txt=f"{v:.3f} pp"
    ax.text(v+0.003,i,txt,va="center",fontsize=8.5,color=INK)
ax.set_yticks(range(len(items))); ax.set_yticklabels([x[0] for x in items[::-1]],fontsize=8.5)
ax.set_xlabel("Cost at Neutral (pp of expected return)"); ax.set_xlim(0,0.2)
clean(ax,"x")
fig.tight_layout(); fig.savefig(OUT+"fig_cost_constraints.png",dpi=300); plt.close(fig)

# Figure B: expected vs realised return at the 31 rebalances
e=pd.read_csv(R+"4_backtest/results/profiles/equity_curves.csv",index_col=0,parse_dates=True)
r=pd.read_csv(R+"4_backtest/results/profiles/rebalances.csv",parse_dates=["date"])
def pr(book):
    d=r[r.book==book].sort_values("date"); dates=list(d.date)+[e.index[-1]]; real=[]
    for a,b in zip(dates[:-1],dates[1:]):
        a=e.index[e.index.get_indexer([a],method="bfill")[0]]
        b=e.index[e.index.get_indexer([b],method="bfill")[0]] if b<=e.index[-1] else e.index[-1]
        yrs=(b-a).days/365.25; real.append(((e.loc[b,book]/e.loc[a,book])**(1/yrs)-1)*100)
    return d["pred_return_%"].values,np.array(real)
fig,ax=plt.subplots(figsize=(6.3,3.4),dpi=300)
ax.plot([0,90],[0,90],color=GREY,lw=0.8,ls=":",zorder=1,label="Perfect forecast")
for book,c,lab in [("minvar",BLUE,"Minimum variance"),("mandate20",ORANGE,"Mandate 20")]:
    x,y=pr(book); rr,p=stats.pearsonr(x,y)
    ax.scatter(x,y,s=16,color=c,edgecolor="white",linewidth=0.6,zorder=3,label=f"{lab} (r = {rr:.2f}"+(f", p = {p:.3f})" if p<0.05 else ", not significant)"))
    b1,b0=np.polyfit(x,y,1); xs=np.linspace(x.min(),x.max(),10); ax.plot(xs,b1*xs+b0,color=c,lw=1.2,ls="--",zorder=2)
ax.set_xlabel("Return expected at the rebalance (% a year)"); ax.set_ylabel("Return earned to the next\nrebalance (% a year)")
ax.set_xlim(0,80); ax.set_ylim(-60,120); clean(ax,"both"); ax.axhline(0,color=GREY,lw=0.6)
ax.legend(frameon=False,fontsize=8.5,loc="lower center",bbox_to_anchor=(0.5,1.0),ncol=2,handlelength=1.6,columnspacing=1.5)
fig.tight_layout(); fig.savefig(OUT+"fig_forecast_scatter.png",dpi=300); plt.close(fig)

# Figure C: point-in-time crisis test (Panel B)
b=pd.read_csv(R+"6_stress_test/results/panelB_windows.csv"); b=b[(b.cap.isna())|(b.cap=="cap off")]
wins=["2018 Q4 selloff","2020 COVID crash","2022 inflation shock"]; short=["2018 Q4\nselloff","2020 COVID\ncrash","2022 inflation\nshock"]
books=[("risk_averse","Risk Averse",BLUE),("neutral","Neutral",ORANGE),("risk_prone","Risk Prone",AQUA),("equal_weight","1/N",INK)]
fig,(a1,a2)=plt.subplots(1,2,figsize=(6.3,2.9),dpi=300,gridspec_kw={"width_ratios":[1.45,1]})
w=0.2
for j,(k,lab,c) in enumerate(books):
    v=[b[(b.window==x)&(b.book==k)]["ret_%"].values[0] for x in wins]
    a1.bar(np.arange(3)+(j-1.5)*w,v,w*0.92,color=c,label=lab)
a1.set_xticks(range(3)); a1.set_xticklabels(short,fontsize=8.5); a1.axhline(0,color=GREY,lw=0.6)
a1.set_ylabel("Return over the window (%)"); a1.set_title("Return in the crisis",fontsize=9.5,loc="left"); clean(a1)
a1.legend(frameon=False,fontsize=8,ncol=2,loc="lower left",bbox_to_anchor=(0,-0.02),handlelength=1)
a1.set_ylim(-52,5)
for j,(k,lab,c) in enumerate(books[:2]):
    ratio=[ (lambda d: d["vol_%"].values[0]/d["pred_risk_%"].values[0])(b[(b.window==x)&(b.book==k)]) for x in wins]
    xs=np.arange(3)+(j-0.5)*0.34
    a2.bar(xs,ratio,0.3,color=c,label=lab)
    for xx,rv in zip(xs,ratio): a2.text(xx,rv+0.15,f"{rv:.1f}",ha="center",fontsize=8,color=INK)
a2.axhline(1,color=GREY,lw=0.8,ls=":"); pass
a2.set_xticks(range(3)); a2.set_xticklabels(["2018 Q4","COVID","2022"],fontsize=8.5)
a2.set_ylabel("Times the forecast"); a2.set_title("Realised / forecast volatility",fontsize=9.5,loc="left"); clean(a2)
a2.set_ylim(0,10)
fig.tight_layout(); fig.savefig(OUT+"fig_stress_panelB.png",dpi=300); plt.close(fig)

# Figure D (appendix)
sw=pd.read_csv(R+"3_sensitivity_studies/results/factor_count/sweep.csv")
ks=[1,2,5,10,20,30,50]; sw=sw[sw.k.isin(ks)].sort_values("k")
fig,ax=plt.subplots(figsize=(6.3,2.7),dpi=300)
cols=[ORANGE if k==20 else (GREY if v<0 else BLUE) for k,v in zip(sw.k,sw["err_minrisk_%"])]
ax.bar(range(len(sw)),sw["err_minrisk_%"],color=cols,width=0.6)
for i,v in enumerate(sw["err_minrisk_%"]): ax.text(i,v+(1.2 if v>=0 else -4),f"{v:+.2f}",ha="center",fontsize=8.5,color=INK)
ax.set_xticks(range(len(sw))); ax.set_xticklabels([f"{int(k)}\n({v:.0f}%)" for k,v in zip(sw.k,sw["var_explained_%"])],fontsize=8.5)
ax.axhline(0,color=INK,lw=0.8)
ax.set_xlabel("Number of factors (share of variance explained in brackets)"); ax.set_ylabel("Risk error at the minimum\nvariance point (%)")
ax.set_ylim(-45,12); clean(ax)
fig.tight_layout(); fig.savefig(OUT+"fig_factor_count.png",dpi=300); plt.close(fig)
