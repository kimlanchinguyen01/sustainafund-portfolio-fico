import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
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


# Figure 1: efficient frontier
f=pd.read_csv(R+"2_optimisation_model/results/efficient_frontier_model2_sec30_tier1_tier2off_esgfloor30.csv")
ret=f.portfolio_return*100; risk=np.sqrt(f.portfolio_variance)*100
fig,ax=plt.subplots(figsize=(6.3,3.0),dpi=300)
ax.plot(risk,ret,color=GREY,lw=1.5,zorder=1)
ok=[i for i in range(15) if i<=11]; deg=[12,13,14]
ax.scatter(risk[ok],ret[ok],s=18,color=GREY,zorder=2,edgecolor="white",linewidth=1)
ax.scatter(risk[deg],ret[deg],s=22,facecolor="white",edgecolor=GREY,linewidth=1.2,zorder=2)
for i,c,lab,dx,dy,ha in [(0,BLUE,"Risk Averse (pt 0)\n9.87% / 9.26%",0.45,-0.35,"left"),
                         (8,ORANGE,"Neutral (pt 8)\n14.30% / 10.62%",0.35,-1.35,"left"),
                         (11,AQUA,"Risk Prone (pt 11)\n15.97% / 12.77%",0.45,-1.35,"left")]:
    ax.scatter(risk[i],ret[i],s=60,color=c,edgecolor="white",linewidth=2,zorder=3)
    ax.annotate(lab,(risk[i],ret[i]),xytext=(risk[i]+dx,ret[i]+dy),fontsize=8.5,color=INK,ha=ha,va="center")
ax.annotate("Degenerate points 12 to 14\n(excluded)",(risk[13],ret[13]),xytext=(risk[13]+0.6,ret[13]-1.6),fontsize=8.5,color="#52514e",
            arrowprops=dict(arrowstyle="-",color=GREY,lw=0.6))
ax.set_xlabel("Risk, annualised volatility (%)"); ax.set_ylabel("Expected return (%)")
ax.set_xlim(8.5,24); ax.set_ylim(8.5,18.5)
ax.grid(True,color=GRID,lw=0.5); ax.set_axisbelow(True)
for s in ["top","right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(OUT+"fig1_frontier.png",dpi=300); plt.close(fig)

# Figure 2: backtest equity curves
e=pd.read_csv(R+"4_backtest/results/profiles/equity_curves.csv",index_col=0,parse_dates=True)
fig,ax=plt.subplots(figsize=(6.3,3.2),dpi=300)
spec=[("mandate10",AQUA,"Mandate 10%"),("mandate20",ORANGE,"Mandate 20%"),("equal_weight",INK,"1/N"),("minvar",BLUE,"Minimum variance")]
for col,c,lab in spec:
    ls="--" if col=="equal_weight" else "-"
    ax.plot(e.index,e[col],color=c,lw=1.4 if col!="equal_weight" else 1.1,ls=ls,label=lab)
    ax.annotate(f"{lab}  {e[col].iloc[-1]:.2f}x",(e.index[-1],e[col].iloc[-1]),xytext=(6,0),textcoords="offset points",fontsize=8.5,color=INK,va="center")
for a,b,t in [("2020-02-19","2020-03-23","COVID"),("2022-01-03","2022-10-12","2022")]:
    ax.axvspan(pd.Timestamp(a),pd.Timestamp(b),color=GRID,alpha=0.8,lw=0)
    ax.text(pd.Timestamp(a),0.6,t,fontsize=8,color="#52514e")
ax.set_ylabel("Value of 1 USD invested")
ax.set_ylim(0.5,4.8); ax.set_xlim(e.index[0],e.index[-1])
ax.legend(loc="upper center",bbox_to_anchor=(0.5,-0.13),frameon=False,fontsize=8.5,ncol=4)
ax.grid(True,axis="y",color=GRID,lw=0.5); ax.set_axisbelow(True)
for s in ["top","right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.subplots_adjust(right=0.76,bottom=0.22); fig.savefig(OUT+"fig2_backtest.png",dpi=300); plt.close(fig)
print("done")
