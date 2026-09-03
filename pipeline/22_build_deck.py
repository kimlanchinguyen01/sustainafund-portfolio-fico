"""Interim-review deck for the SustainaFund case study, built with matplotlib."""
import os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

NAVY="#1F3864"; BLUE="#2E75B6"; GREY="#595959"; LIGHT="#F2F5F9"
RED="#C00000"; GREEN="#375623"; AMBER="#BF8F00"
W,H=13.333,7.5
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11})

def slide(title=None, kicker=None):
    fig=plt.figure(figsize=(W,H)); fig.patch.set_facecolor("white")
    if title:
        fig.text(0.055,0.945,title,fontsize=24,color=NAVY,weight="bold",va="top")
        fig.add_artist(plt.Line2D([0.055,0.945],[0.862,0.862],color=BLUE,lw=2.2))
    if kicker:
        fig.text(0.055,0.818,kicker,fontsize=11.5,color=GREY,va="top",style="italic")
    return fig

def foot(fig,n):
    fig.text(0.945,0.035,str(n),fontsize=9.5,color=GREY,ha="right")
    fig.text(0.055,0.035,"SustainaFund · FICO case study · interim review · 3 Sep 2026",
             fontsize=8.5,color="#A6A6A6")

def table(fig, rect, cols, rows, widths, hi=None, fs=10.5, hdr_fs=10.5):
    """Cells wrap to their column width instead of overflowing the table."""
    import textwrap
    x0,y0,w,h=rect
    # characters that fit in a column, calibrated for this font size
    cpl=[max(8,int(cw*w/(fs*0.00058))) for cw in widths]
    wrapped=[[textwrap.wrap(str(v),cpl[j]) or [""] for j,v in enumerate(r)] for r in rows]
    lines=[max(len(c) for c in r) for r in wrapped]
    units=1+sum(lines); rh=h/units
    hcpl=[max(6,int(cw*w/(hdr_fs*0.00058))) for cw in widths]
    hdr=[textwrap.wrap(str(c),hcpl[j]) or [""] for j,c in enumerate(cols)]
    hlines=max(len(x) for x in hdr)
    rh=h/(hlines+sum(lines)); hh=rh*hlines
    for j,(c,cw) in enumerate(zip(hdr,widths)):
        xx=x0+sum(widths[:j])*w
        fig.patches.append(plt.Rectangle((xx,y0+h-hh),cw*w,hh,transform=fig.transFigure,
                                         facecolor=NAVY,edgecolor="none",zorder=1))
        fig.text(xx+0.007,y0+h-hh/2,"\n".join(c),fontsize=hdr_fs,color="white",weight="bold",
                 va="center",zorder=2,linespacing=1.2)
    ytop=y0+h-hh
    for i,r in enumerate(wrapped):
        rhi=rh*lines[i]; ybot=ytop-rhi
        bg=LIGHT if i%2==0 else "white"
        if hi and i in hi: bg="#FFF2CC"
        fig.patches.append(plt.Rectangle((x0,ybot),w,rhi,transform=fig.transFigure,
                                         facecolor=bg,edgecolor="none",zorder=1))
        for j,cell in enumerate(r):
            xx=x0+sum(widths[:j])*w
            bold = j==0 or (hi and i in hi)
            fig.text(xx+0.007,ybot+rhi/2,"\n".join(cell),fontsize=fs,color="#222222",
                     va="center",weight="bold" if bold else "normal",zorder=2,
                     linespacing=1.25)
        ytop=ybot
    return ytop

def bullets(fig,x,y,items,dy=0.052,fs=12,wrap=95):
    import textwrap
    for lead,body in items:
        t=""
        if lead: t+=lead
        fig.text(x,y,"▪",fontsize=11,color=BLUE,va="top")
        line=textwrap.fill((lead+body) if lead else body,wrap)
        fig.text(x+0.016,y,line,fontsize=fs,color="#222222",va="top")
        y-=dy*(1+line.count("\n")*0.62)
    return y

# ---------------------------------------------------------------- data
# portfolio_summary.csv was loaded here and never used - every scenario number
# on the slides comes from SC below. Removed rather than left in place, because
# that file disagrees with the rest of the repo about which frontier point
# risk-prone is (point 11 vs point 14); see HANDOFF.md.
FR=pd.read_csv("results_chloe/efficient_frontier_model2_sec30_tier1_tier2off_esgfloor30.csv")
BT=pd.read_csv("results_chloe/backtest/backtest_summary.csv",index_col=0)
SUB=pd.read_csv("results_chloe/backtest/backtest_subperiods.csv")
DG=pd.read_csv("results_chloe/backtest/backtest_diagnostics.csv")
DG=dict(zip(DG.metric,DG.value))
EQ=pd.read_csv("results_chloe/backtest/backtest_equity_curves.csv",index_col=0,parse_dates=True)
mu=pd.read_csv("expected_return_v4.csv",index_col=0)["expected_return"]
NEU=pd.read_csv("results_chloe/portfolio_tier2off_neutral.csv",index_col=0)
import json as _json
# Was: _json.load(open("/tmp/scen.json")) - a file NOTHING in the repo wrote, so
# this line made the deck unrebuildable on any machine where /tmp had been
# cleared. Regenerated into the repo by 28_scenarios_for_deck.py, which was
# verified field-by-field against the original /tmp copy.
SCEN_JSON="results_chloe/scenarios_for_deck.json"
if not os.path.exists(SCEN_JSON):
    raise SystemExit(f"missing {SCEN_JSON}\n  run: python3 28_scenarios_for_deck.py")
SC=_json.load(open(SCEN_JSON))
ESGD=SC.pop("esg")
MX=pd.read_csv("scenario_matrix.csv")
def mx(cfg,prof,col): return float(MX[(MX.config==cfg)&(MX.profile==prof)][col].iloc[0])

pdf=PdfPages("SustainaFund_interim_review.pdf"); pg=0
PNG=[]
def emit(fig,n):
    foot(fig,n); pdf.savefig(fig)
    fig.savefig(f"/tmp/slide{n:02d}.png",dpi=72)
    plt.close(fig)

# ============================================================ 1 title
fig=slide()
fig.patches.append(plt.Rectangle((0,0.62),1,0.38,transform=fig.transFigure,facecolor=NAVY,zorder=0))
fig.text(0.055,0.86,"SustainaFund — Portfolio Selection",fontsize=34,color="white",weight="bold",va="top")
fig.text(0.055,0.775,"Interim review",fontsize=19,color="#BDD7EE",va="top")
fig.text(0.055,0.70,"$100M mid-term mandate · 1,087 stocks · MIQP in FICO Xpress",
         fontsize=13.5,color="#DEEBF7",va="top")
fig.text(0.055,0.50,"What we have, why this model, how the data was cleaned, and what the numbers say",
         fontsize=15,color=NAVY,va="top",weight="bold")
b=[("","The model is a mixed-integer quadratic program — Markowitz with cardinality, "
       "concentration and ESG constraints, solved in FICO Xpress in under a second."),
   ("","Every non-obvious choice in it was measured rather than assumed, and the "
       "measurements are reproducible from the scripts."),
   ("","One result is negative and reported as such: out of sample the optimiser and an "
       "equal-weight benchmark are statistically indistinguishable on risk-adjusted return.")]
bullets(fig,0.055,0.42,b,dy=0.075,fs=12.5,wrap=105)
fig.text(0.055,0.072,"HTW Berlin summer school 2026",fontsize=10.5,color=GREY)
pg+=1; emit(fig,pg)

# ============================================================ 2 problem
fig=slide("The problem","Two objectives that cannot both be maximised, under six hard constraints")
table(fig,(0.055,0.40,0.42,0.40),["Constraint","Value"],
      [["Budget","$100,000,000, fully invested"],
       ["Position size","1% – 20% of budget if held"],
       ["Diversification","at least 30 different stocks"],
       ["Region","no region above 60%"],
       ["ESG, weighted","at least 70"],
       ["ESG, per stock","at least 30  (added)"],
       ["Sector","no sector above 30%  (added)"]],
      [0.42,0.58],hi=[5,6],fs=11)
fig.text(0.055,0.345,"The last two are additions to the brief, not requirements.",
         fontsize=10.5,color=GREY,style="italic")
fig.text(0.545,0.79,"The trade-off",fontsize=15,color=NAVY,weight="bold",va="top")
b=[("Maximise return — ","the weighted sum of expected returns. But expected return is "
    "not given in the data; it has to be estimated from ten years of prices, and the "
    "choice of estimator is itself part of the work."),
   ("Minimise risk — ","the variance of the portfolio, which needs the covariance between "
    "every pair of stocks. This is what captures diversification: combining stocks that "
    "do not move together lowers total risk."),
   ("","Higher return comes with higher risk, so there is no single best portfolio — only "
    "a frontier. We present three points on it for three risk appetites.")]
bullets(fig,0.545,0.72,b,dy=0.058,fs=11.5,wrap=62)
pg+=1; emit(fig,pg)

# ============================================================ 3 model
fig=slide("The model","Mixed-integer quadratic program, solved with FICO Xpress in 0.3-1.1 s")
fig.patches.append(plt.Rectangle((0.055,0.315,),0.455,0.455,transform=fig.transFigure,
                                 facecolor=LIGHT,edgecolor=BLUE,lw=1.3))
# NB: DejaVu Sans has no U+1D62 subscript i - it silently substitutes a
# subscript ONE, which would print w_1 where the formula means w_i. Plain
# underscore notation instead.
form=[("minimise",  "w' S w",                     "portfolio variance"),
      ("subject to","w' mu  >=  beta",            "target return, swept"),
      ("",          "sum w_i  =  1",              "budget fully invested"),
      ("",          "0.01 y_i <= w_i <= 0.20 y_i", "1-20% if selected"),
      ("",          "y_i in {0, 1}",              "selected or not"),
      ("",          "sum y_i  >=  30",            "minimum holdings"),
      ("",          "sum w_i <= 0.60  per region", ""),
      ("",          "sum w_i <= 0.30  per sector", ""),
      ("",          "sum ESG_i w_i >= 70",        "weighted ESG"),
      ("",          "ESG_i >= 30  if held",       "per-stock floor")]
y=0.740
for lead,eq,note in form:
    if lead: fig.text(0.070,y,lead,fontsize=10,color=GREY,va="top",style="italic")
    fig.text(0.150,y,eq,fontsize=11.5,color=NAVY,va="top",family="monospace")
    if note: fig.text(0.375,y,note,fontsize=8.8,color=GREY,va="top")
    y-=0.0405
fig.text(0.070,0.335,"S = covariance matrix,  mu = expected returns",fontsize=8.5,
         color=GREY,style="italic",va="top")
fig.text(0.545,0.755,"Why quadratic and not linear",fontsize=14,color=NAVY,weight="bold",va="top")
b=[("","The brief offers two routes to risk: per-stock volatilities, which give a linear "
       "model, or the covariance matrix, which gives a quadratic one. We built both."),
   ("","A linear objective is the risk you would bear if every pair of stocks moved "
       "together. It is blind to diversification: swapping a stock for another of equal "
       "volatility never changes it."),
   ("Measured:  ","at the same expected return the linear model carries 19.2% more true "
       "risk, and it always holds exactly the 30-stock minimum - adding a 31st cannot "
       "improve its objective."),
   ("","For its own portfolio the linear objective reads 21.95% while that portfolio's "
       "actual volatility is 13.42%. The 1.64x gap is the diversification it cannot see.")]
bullets(fig,0.545,0.695,b,dy=0.050,fs=10.8,wrap=60)
import textwrap as _tw
fig.text(0.055,0.265,_tw.fill("Binary variables are required, not a workaround: Xpress "
         "semi-continuous variables express \"0 or in [1%, 20%]\" natively but cannot be "
         "counted, so the 30-stock constraint still needs them. Tested - dropping the link "
         "returns 26 positions while reporting 30.",84),
         fontsize=9.5,color=GREY,style="italic",va="top")
pg+=1; emit(fig,pg)

# ============================================================ 4 cleaning
fig=slide("How the data was cleaned","Seven decisions, each with the number that justifies it")
table(fig,(0.055,0.185,0.89,0.60),
      ["Step","Decision","Why - the measured reason"],
      [["Missing ESG","49 of 1,093 filled with the 25th percentile within the region",
        "the 25th percentile, not the mean, so a missing score is not rewarded"],
       ["Price gaps","forward-filled, never before a stock's first trading day",
        "every internal gap is exactly 1 trading day, checked on consecutive runs"],
       ["Dividends","switched to total-return prices",
        "median expected return 7.80% → 10.39%; the rise is ordered by dividend yield across sectors"],
       ["Currencies","converted to USD at daily ECB rates",
        "a local-currency Σ understated the min-variance book's risk by 19.7%"],
       ["Discontinuities","ZEG.L and BMPS.MI truncated, not dropped",
        "identical closes then a large jump = corporate action; a return across it is meaningless"],
       ["Outliers","flagged, not removed",
        "a 5σ per-stock rule fires on 0.31% of observations, mostly genuine events"],
       ["Expected return","James-Stein shrinkage by sample size",
        "a raw mean gave 88% p.a. on 460 observations; after shrinkage no stock is negative"]],
      [0.15,0.36,0.49],fs=10,hdr_fs=11)
import textwrap as _tw
fig.text(0.055,0.145,_tw.fill("Universe 1,093 to 1,087. Six stocks are empty in the total-return "
         "source file (three of them REITs) and were dropped rather than back-filled from "
         "unadjusted prices, which would have cost them ~3pp of return for a data defect.",132),
         fontsize=9.8,color=GREY,style="italic",va="top")
pg+=1; emit(fig,pg)

# ============================================================ 5 estimator choices
fig=slide("Why these estimator choices","Each one changed the answer, and each was measured")
ax=fig.add_axes([0.06,0.13,0.40,0.60])
k=[1,2,5,10,20,30,50]
err=[-18.09,-17.56,3.87,3.08,7.68,8.25,10.79]
mn=[-39.9,-39.5,-0.8,-1.6,1.5,2.9,6.3]
ax.axhline(0,color=GREY,lw=1)
ax.plot(range(len(k)),err,"o-",color=BLUE,lw=2.2,ms=7,label="mean across the frontier")
ax.plot(range(len(k)),mn,"s--",color=RED,lw=1.8,ms=6,label="at the min-risk end")
ax.set_xticks(range(len(k))); ax.set_xticklabels(k)
ax.set_xlabel("number of factors in the covariance model",fontsize=10.5)
ax.set_ylabel("risk error, %   (negative = understates)",fontsize=10.5)
ax.set_title("Why 20 factors: a cliff, not a gradient",fontsize=12,color=NAVY,weight="bold")
ax.axvspan(-0.4,1.4,color=RED,alpha=0.07)
ax.text(0.5,-30,"1–2 factors\nunderstate risk\nby ~18–40%",fontsize=9.5,color=RED,ha="center")
ax.axvline(4,color=GREEN,lw=1.5,ls=":"); ax.text(4.1,-25,"chosen",fontsize=9.5,color=GREEN)
ax.legend(fontsize=9.5,loc="lower right"); ax.grid(alpha=0.25)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
fig.text(0.52,0.79,"The three that moved the result most",fontsize=14,color=NAVY,weight="bold",va="top")
b=[("Prices → USD.  ","Returns are ratios, so price levels cancel — but the FX return does "
    "not: ln(P_usd)=ln(P_local)+ln(fx). It barely moves μ (<0.3pp, currencies offset) yet "
    "puts a shared factor into Σ. At the same true risk the corrected model returns 12.78% "
    "against 7.07%."),
   ("μ shrunk.  ","A raw historical mean is very noisy and the optimiser preferentially picks "
    "whatever that noise flattered. Shrinkage cut the frontier's top from 38.8% to 16.6% — "
    "and 38.8% would not have survived one question."),
   ("Covariance → factor model.  ","The complete-history rule silently excluded 96 recent "
    "listings. A factor model fits betas on whatever days a stock has, keeps all of them, and "
    "is positive semi-definite by construction.")]
bullets(fig,0.52,0.72,b,dy=0.052,fs=11,wrap=68)
import textwrap as _tw
fig.text(0.52,0.16,_tw.fill("Two things we tried that did not work, reported as such: bootstrap "
         "resampling of the weights (no effect on stability) and an explicit region factor "
         "(absorbs the structure, leaves the risk error unchanged).",72),
         fontsize=9.6,color=GREY,style="italic",va="top")
pg+=1; emit(fig,pg)

# ============================================================ ESG
fig=slide("Choosing the ESG floor","The per-stock floor was picked from the distribution, not guessed")
ax=fig.add_axes([0.06,0.20,0.40,0.53])
ax.hist(ESGD["vals"],bins=42,color=BLUE,edgecolor="white",linewidth=0.6)
st=ESGD["stats"]
ax.axvline(70,color=RED,ls="--",lw=2)
ax.text(70.8,ax.get_ylim()[1]*0.93,"70\nportfolio\naverage",fontsize=9,color=RED,va="top")
ax.axvline(30,color=GREEN,ls="-",lw=2)
ax.text(31,ax.get_ylim()[1]*0.60,"30\nper-stock\nfloor",fontsize=9,color=GREEN,va="top")
ax.axvline(st["median"],color=GREY,ls=":",lw=1.5)
ax.text(st["median"]-1.5,ax.get_ylim()[1]*0.93,f"median {st['median']}",fontsize=8.5,
        color=GREY,va="top",ha="right")
ax.set_xlabel("individual stock ESG score",fontsize=10.5)
ax.set_ylabel("number of stocks",fontsize=10.5); ax.grid(axis="y",alpha=0.22)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.set_title("1,093 stocks — where the two thresholds sit",fontsize=11.5,color=NAVY,weight="bold")
rows=[[f"ESG < {k}",f"{v}",f"{100*v/1093:.1f}%"] for k,v in ESGD["below"].items()]
table(fig,(0.51,0.44,0.21,0.29),["Candidate floor","Stocks","Share"],rows,
      [0.46,0.26,0.28],hi=[2],fs=9.5,hdr_fs=9)
worst=[[k,f"{v}"] for k,v in ESGD["worst"][:6]]
table(fig,(0.745,0.44,0.20,0.29),["Lowest ESG","Score"],worst,[0.60,0.40],fs=9.5,hdr_fs=9)
fig.text(0.51,0.375,"Two things this settles",fontsize=13,color=NAVY,weight="bold",va="top")
b=[("","The universe median is 69.6, essentially the 70 the brief asks for as a weighted "
       "average. So the ESG constraint means \"above the median on average\" — which is why "
       "it binds in every solve yet costs almost nothing."),
   ("","A weighted average of 70 can still be met while holding names scored in the twenties. "
       "The floor of 30 removes ten stocks, 0.9% of the universe, and closes that gap. "
       "Berkshire Hathaway at 24.1 is the most recognisable of them."),
   ("","40 would have cost four times as many stocks (41) for no clear principle, so 30 is "
       "the smallest floor that removes the outliers without reshaping the universe.")]
bullets(fig,0.51,0.325,b,dy=0.052,fs=10.5,wrap=64)
pg+=1; emit(fig,pg)

# ============================================================ 6 results
fig=slide("Results — the efficient frontier","1,087 stocks; the three scenarios are the two corners and the best trade-off between them")
ax=fig.add_axes([0.06,0.185,0.42,0.545])
x=FR.portfolio_risk*100; y=FR.portfolio_return*100
ax.plot(x,y,"o-",color=BLUE,lw=2.2,ms=6,zorder=2)
MK={"Risk Averse":("#375623","o",(12,-16)),"Neutral":(RED,"D",(12,-16)),
    "Risk Prone":(AMBER,"s",(-8,-22))}
for lbl,(c,m,off) in MK.items():
    d=SC[lbl]
    ax.scatter([d["risk"]],[d["ret"]],s=200,color=c,marker=m,zorder=5,
               edgecolor="white",linewidth=1.7)
    ax.annotate(lbl,(d["risk"],d["ret"]),textcoords="offset points",xytext=off,
                fontsize=10,color=c,weight="bold")
ax.set_xlabel("risk — annualised volatility, %",fontsize=10.5)
ax.set_ylabel("expected return, % p.a.",fontsize=10.5)
ax.grid(alpha=0.25)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.set_title("15 points, every one solved to optimality",fontsize=11.5,color=NAVY)
rows=[[lbl,f"{SC[lbl]['ret']:.2f}%",f"{SC[lbl]['risk']:.2f}%",f"{SC[lbl]['sharpe']:.3f}",
       f"{int(SC[lbl]['n'])}",f"{SC[lbl]['esg']:.1f}"] for lbl in MK]
table(fig,(0.53,0.545,0.41,0.185),
      ["Scenario","Return","Risk","Ret/Risk","Held","ESG"],rows,
      [0.29,0.15,0.14,0.16,0.13,0.13],hi=[1],fs=9.8,hdr_fs=9)
import textwrap as _tw
fig.text(0.53,0.505,_tw.fill("Definitions follow the brief: minimum risk, maximum return, "
         "and the highest return/risk ratio between them. No arbitrary target and no "
         "risk-aversion parameter.",84),fontsize=9.4,color=GREY,style="italic",va="top")
fig.text(0.53,0.415,"The neutral book is the recommendation",fontsize=13,color=NAVY,
         weight="bold",va="top")
b=[("","Best risk-adjusted profile at 1.35, 30 holdings, largest position 12.9%, and no "
       "position at either the 20% cap or the 1% floor."),
   ("","ESG binds at exactly 70.00 at every one of the 15 points, so the constraint is "
       "always active — and costs almost nothing."),
   ("","The frontier is steep to the left and flat to the right: past roughly 14% risk, "
       "extra risk buys very little extra return. That is the argument for not choosing "
       "the risk-prone corner.")]
bullets(fig,0.53,0.365,b,dy=0.052,fs=10.6,wrap=70)
pg+=1; emit(fig,pg)

# ============================================================ scenarios
fig=slide("Three investment scenarios","As the brief asks: minimise risk, maximise return, and the best trade-off between them")
COL={"Risk Averse":("#375623",0.075),"Neutral":(RED,0.365),"Risk Prone":(AMBER,0.655)}
for lbl,(c,x) in COL.items():
    d=SC[lbl]
    fig.patches.append(plt.Rectangle((x,0.185),0.27,0.61,transform=fig.transFigure,
                                     facecolor="white",edgecolor=c,lw=1.8))
    fig.patches.append(plt.Rectangle((x,0.736),0.27,0.06,transform=fig.transFigure,
                                     facecolor=c,edgecolor="none"))
    fig.text(x+0.012,0.765,lbl,fontsize=13.5,color="white",weight="bold",va="center")
    defn={"Risk Averse":"lowest risk on the frontier",
          "Neutral":"highest return / risk ratio",
          "Risk Prone":"highest return on the frontier"}[lbl]
    fig.text(x+0.012,0.712,defn,fontsize=9,color=GREY,style="italic",va="top")
    y=0.672
    for k,v in [("Expected return",f"{d['ret']:.2f}%"),("Risk",f"{d['risk']:.2f}%"),
                ("Return / risk",f"{d['sharpe']:.3f}"),("Holdings",f"{int(d['n'])}"),
                ("Weighted ESG",f"{d['esg']:.1f}"),
                ("Top sector",f"{d['sector'][:18]} {d['sector_w']:.0f}%"),
                ("Top country",f"{d['country'][:14]} {d['country_w']:.0f}%")]:
        fig.text(x+0.012,y,k,fontsize=9.3,color=GREY,va="top")
        big = k in ("Expected return","Risk","Return / risk")
        fig.text(x+0.258,y,v,fontsize=11 if big else 9.6,color=c if big else "#222222",
                 weight="bold" if big else "normal",va="top",ha="right")
        y-=0.036
    fig.add_artist(plt.Line2D([x+0.012,x+0.258],[y+0.014,y+0.014],color="#D9D9D9",lw=1))
    fig.text(x+0.012,y-0.008,"Largest positions",fontsize=9,color=GREY,va="top",weight="bold")
    y-=0.045
    for tk,wv in d["top"][:5]:
        fig.text(x+0.012,y,tk,fontsize=9.3,color="#222222",va="top",family="monospace")
        fig.text(x+0.258,y,f"{wv:.1f}%",fontsize=9.3,color="#222222",va="top",ha="right")
        y-=0.031
rp=SC["Risk Prone"]
fig.patches.append(plt.Rectangle((0.075,0.062),0.85,0.093,transform=fig.transFigure,
                                 facecolor="#FFF2CC",edgecolor=AMBER,lw=1.2))
import textwrap as _tw
fig.text(0.088,0.137,"Read the risk-prone column with care.",fontsize=10.5,color="#7F6000",
         weight="bold",va="top")
fig.text(0.088,0.113,_tw.fill(f"\"Maximise return\" lands on a corner of the feasible set: "
    f"{rp['at20']} positions sit at the 20% cap and {rp['at1']} of {int(rp['n'])} at the 1% floor, "
    f"so {rp['top3']:.0f}% of the budget is in three stocks. Its return/risk ratio of "
    f"{rp['sharpe']:.2f} is worse than the risk-averse book's {SC['Risk Averse']['sharpe']:.2f} — "
    "it is a valid answer to the question asked, not a portfolio we would recommend.",158),
    fontsize=9.5,color="#7F6000",va="top")
pg+=1; emit(fig,pg)

# ============================================================ ESG matrix
fig=slide("ESG policy: four configurations, not two",
          "The portfolio average and the per-stock floor are independent levers — each was toggled separately")
# (csv key, display title, subtitle, x, y, colour) - the csv key is carried
# explicitly rather than derived from the title, which broke on the em dash
CELLS=[("A  no ESG at all","A  no ESG at all","no average, no floor",0.075,0.44,GREY),
       ("C  floor 30 only","C  floor 30 only","floor only",0.075,0.20,GREY),
       ("B  average 70 only","B  average 70 only","average only",0.325,0.44,BLUE),
       ("D  both (final)","D  both — FINAL","average + floor",0.325,0.20,GREEN)]
fig.text(0.075,0.735,"Neutral profile shown in each cell",fontsize=10,color=GREY,style="italic")
for key,cfg,sub,x,yy,col in CELLS:
    final = key.startswith("D")
    fig.patches.append(plt.Rectangle((x,yy),0.235,0.215,transform=fig.transFigure,
        facecolor="#EAF3E8" if final else "white",edgecolor=col,lw=2.2 if final else 1.4))
    fig.text(x+0.012,yy+0.185,cfg,fontsize=11.5,color=col,weight="bold",va="center")
    fig.text(x+0.012,yy+0.155,sub,fontsize=8.8,color=GREY,style="italic",va="center")
    r=mx(key,"Neutral","ret_%"); k=mx(key,"Neutral","risk_%"); e=mx(key,"Neutral","esg")
    fig.text(x+0.012,yy+0.105,f"{r:.2f}%",fontsize=19,color=col,weight="bold",va="center")
    fig.text(x+0.120,yy+0.105,"return",fontsize=9,color=GREY,va="center")
    fig.text(x+0.012,yy+0.058,f"risk {k:.2f}%      ESG {e:.2f}",fontsize=9.8,color="#222222",va="center")
    fig.text(x+0.012,yy+0.025,f"Sharpe {r/k:.3f}",fontsize=9.5,color=GREY,va="center")
fig.add_artist(plt.Line2D([0.192,0.322],[0.548,0.548],color=RED,lw=1.6,ls="--"))
fig.text(0.257,0.556,"−0.151 pp",fontsize=9.5,color=RED,ha="center",weight="bold")
fig.add_artist(plt.Line2D([0.192,0.322],[0.308,0.308],color=RED,lw=1.6,ls="--"))
fig.text(0.257,0.316,"−0.187 pp",fontsize=9.5,color=RED,ha="center",weight="bold")
fig.text(0.113,0.424,"+0.008 pp",fontsize=9.5,color=GREEN,ha="center",weight="bold")
fig.text(0.363,0.424,"−0.025 pp",fontsize=9.5,color=GREEN,ha="center",weight="bold")
fig.text(0.60,0.755,"Which rule actually costs anything",fontsize=14,color=NAVY,weight="bold",va="top")
rows=[["Floor alone   A → C",f"{mx('C  floor 30 only','Risk Averse','ret_%')-mx('A  no ESG at all','Risk Averse','ret_%'):+.3f}",
       f"{mx('C  floor 30 only','Neutral','ret_%')-mx('A  no ESG at all','Neutral','ret_%'):+.3f}",
       f"{mx('C  floor 30 only','Risk Prone','ret_%')-mx('A  no ESG at all','Risk Prone','ret_%'):+.3f}"],
      ["Average alone A → B",f"{mx('B  average 70 only','Risk Averse','ret_%')-mx('A  no ESG at all','Risk Averse','ret_%'):+.3f}",
       f"{mx('B  average 70 only','Neutral','ret_%')-mx('A  no ESG at all','Neutral','ret_%'):+.3f}",
       f"{mx('B  average 70 only','Risk Prone','ret_%')-mx('A  no ESG at all','Risk Prone','ret_%'):+.3f}"],
      ["Floor on top  B → D",f"{mx('D  both (final)','Risk Averse','ret_%')-mx('B  average 70 only','Risk Averse','ret_%'):+.3f}",
       f"{mx('D  both (final)','Neutral','ret_%')-mx('B  average 70 only','Neutral','ret_%'):+.3f}",
       f"{mx('D  both (final)','Risk Prone','ret_%')-mx('B  average 70 only','Risk Prone','ret_%'):+.3f}"]]
table(fig,(0.60,0.575,0.345,0.155),["Lever, cost in pp","Averse","Neutral","Prone"],
      rows,[0.40,0.20,0.20,0.20],hi=[1],fs=9.5,hdr_fs=9)
b=[("A and C move together, B and D move together.  ","That is the whole finding. The "
    "per-stock floor changes nothing on its own — +0.008 pp at Neutral and exactly zero at "
    "Risk Prone, both inside solver tolerance."),
   ("The average constraint carries the entire cost.  ","−0.151 pp at Neutral, −0.270 pp at "
    "Risk Prone. Anything said about \"what ESG costs\" is a statement about this rule alone."),
   ("So the floor is free insurance.  ","Its job is not performance, it is closing the "
    "loophole where a weighted average of 70 hides a stock scored in the twenties — "
    "Berkshire Hathaway at 24.1 is the clearest example. A governance improvement at no "
    "measurable return cost.")]
bullets(fig,0.60,0.545,b,dy=0.052,fs=10.3,wrap=63)
pg+=1; emit(fig,pg)

# ============================================================ coverage
fig=slide("Scenario coverage","Every axis tested, and the two that were not, said plainly")
table(fig,(0.055,0.20,0.89,0.585),
      ["Axis","What was varied","Result"],
      [["1  Risk profile","min risk / max return-risk / max return, on every configuration below",
        "the spine of the analysis: 9.87% at 9.26% risk up to 17.63% at 22.63%"],
       ["2  ESG policy","the full 2x2: no ESG, floor only, average only, both",
        "the average rule carries all the cost; the floor is free — see the previous slide"],
       ["3  Controversial industry","Tier 1 (Rheinmetall) vs Tier 1 + ten defence primes",
        f"broad exclusion costs {mx('D + Tier 2 excluded','Neutral','ret_%')-mx('D  both (final)','Neutral','ret_%'):+.3f} pp at Neutral — a policy choice, not an economic one"],
       ["4  ESG floor threshold","20 / 30 / 40",
        f"{mx('D + floor 20','Neutral','ret_%'):.3f}% / {mx('D  both (final)','Neutral','ret_%'):.3f}% / {mx('D + floor 40','Neutral','ret_%'):.3f}% at Neutral — the answer does not depend on the number picked"],
       ["5  Sector cap 30%","on vs off",
        f"off is worth {mx('D, sector cap off','Neutral','ret_%')-mx('D  both (final)','Neutral','ret_%'):+.3f} pp at Neutral, but raises Risk Prone volatility from 22.63% to 23.14% — the cap lowers risk where it binds"],
       ["6  Estimation window","3-year rolling window, 31 quarterly re-estimations",
        "answered by the walk-forward backtest, not by re-solving: it needs the data pipeline rerun"],
       ["7  Out-of-sample behaviour","1/N benchmark, COVID and 2022 stress periods",
        "done: Sharpe 0.835 vs 0.866, indistinguishable; wins in both crises, loses in rallies"]],
      [0.20,0.33,0.47],fs=9.5,hdr_fs=10.5,hi=[1])
import textwrap as _tw
fig.text(0.055,0.155,_tw.fill("Twenty-four solved scenarios: eight configurations x three risk "
   "profiles, plus the 31-rebalance backtest. Not run and worth saying so: a factor-level "
   "attribution of where the return comes from, and transaction costs inside the optimiser "
   "rather than applied afterwards.",150),fontsize=9.8,color=GREY,style="italic",va="top")
pg+=1; emit(fig,pg)

# ============================================================ 7 composition
fig=slide("What the recommended portfolio holds","Neutral profile - 30 positions, $100M")
ISO={"United States":"US","Switzerland":"CH","Belgium":"BE","United Kingdom":"GB",
     "Norway":"NO","Italy":"IT","Germany":"DE","France":"FR","Netherlands":"NL",
     "Sweden":"SE","Denmark":"DK","Spain":"ES","Finland":"FI","Ireland":"IE",
     "Austria":"AT","Poland":"PL","Portugal":"PT"}
SHORT={"Consumer Defensive":"Cons. Defensive","Communication Services":"Comm. Services",
       "Financial Services":"Financials","Consumer Cyclical":"Cons. Cyclical",
       "Basic Materials":"Materials"}
sw_all=NEU.groupby("Sector")["weight_%"].sum().sort_values(ascending=False)
sw=sw_all.head(7).copy()
if len(sw_all)>7:
    sw[f"other {len(sw_all)-7} sectors"]=sw_all.iloc[7:].sum()
ax=fig.add_axes([0.175,0.345,0.235,0.385])
c=[RED if v>29.5 else BLUE for v in sw.values]
ax.barh(range(len(sw))[::-1],sw.values,color=c,height=0.7)
ax.set_yticks(range(len(sw))[::-1])
ax.set_yticklabels([SHORT.get(x,x) for x in sw.index],fontsize=9)
ax.axvline(30,color=RED,ls="--",lw=1.4)
ax.text(30.5,len(sw)-1.3,"30% cap",fontsize=8.5,color=RED,va="top",rotation=90)
ax.set_xlim(0,36); ax.set_xlabel("weight, %",fontsize=10); ax.grid(axis="x",alpha=0.25)
for sp in ("top","right","left"): ax.spines[sp].set_visible(False)
ax.set_title("By sector - the cap binds",fontsize=11,color=NAVY,weight="bold")

cw=NEU.groupby("Country")["weight_%"].sum().sort_values(ascending=False).head(6)
ax2=fig.add_axes([0.485,0.42,0.155,0.31])
ax2.barh(range(len(cw))[::-1],cw.values,color=AMBER,height=0.62)
ax2.set_yticks(range(len(cw))[::-1])
ax2.set_yticklabels([ISO.get(x,x[:6]) for x in cw.index],fontsize=9.5)
ax2.set_xlabel("weight, %",fontsize=10); ax2.grid(axis="x",alpha=0.25)
for sp in ("top","right","left"): ax2.spines[sp].set_visible(False)
ax2.set_title("By country - unconstrained",fontsize=10.5,color=NAVY,weight="bold")

top=NEU.head(8)
rows=[[i,f"{r['weight_%']:.1f}%",f"${r['amount_USD']/1e6:.1f}M",
       ISO.get(str(r['Country']),str(r['Country'])[:3]),f"{r['ESG']:.0f}"] for i,r in top.iterrows()]
table(fig,(0.695,0.40,0.25,0.33),["Top holdings","Wt","USD","Ctry","ESG"],rows,
      [0.34,0.16,0.20,0.14,0.16],fs=9,hdr_fs=8.5)

fig.text(0.055,0.285,"The concentration the sector cap cannot see",fontsize=13,color=NAVY,
         weight="bold",va="top")
b=[("","A sector cap holds Consumer Defensive to exactly 30.00%, but nothing restrains "
       "country exposure - Switzerland reaches 47% of the risk-averse book, concentrated in "
       "cantonal banks and real estate."),
   ("","A 25% country cap held it to 25.0% for 0.156pp of return. It is not in the current "
       "model, and it is the most obvious next addition.")]
bullets(fig,0.055,0.225,b,dy=0.058,fs=11,wrap=112)
pg+=1; emit(fig,pg)

# ============================================================ 9 regimes
fig=slide("How the portfolio behaves across market regimes",
          "Out-of-sample, from a walk-forward test: rolling 3-year window, quarterly rebalance, 31 rebalances over 7.7 years")
fig.text(0.055,0.775,"Benchmark is an equal-weight (1/N) portfolio over the same eligible "
         "universe at each rebalance date, so the comparison isolates the optimiser rather "
         "than the choice of stocks.",fontsize=10,color=GREY,style="italic",va="top")
sb=SUB[SUB.period!="FULL"]
ax=fig.add_axes([0.06,0.365,0.40,0.35])
xx=np.arange(len(sb))
ax.bar(xx-0.2,sb["opt_vol_%"],0.4,color=BLUE,label="Model 2")
ax.bar(xx+0.2,sb["eq_vol_%"],0.4,color=GREY,label="1/N")
ax.set_xticks(xx); ax.set_xticklabels([p.replace("2018-04..2019-12","2018-19")
    .replace("2020-02..2020-03","crash").replace("2020 full year","2020")
    .replace("2023-2025","2023-25") for p in sb.period],fontsize=9,rotation=20,ha="right")
ax.set_ylabel("annualised volatility, %",fontsize=10.5); ax.legend(fontsize=9.5)
ax.grid(axis="y",alpha=0.25)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.set_title("Volatility, by regime",fontsize=11.5,color=NAVY,weight="bold")
rows=[[r.period.replace("2018-04..2019-12","2018-19").replace("2020-02..2020-03","the crash")
        .replace("2020 full year","2020 full").replace("2023-2025","2023-25"),
       r.regime,f"{r['CAGR_diff_pp']:+.1f}",f"{r['vol_reduction_%']:+.0f}%",
       f"{r['opt_maxDD_%']:.0f}% vs {r['eq_maxDD_%']:.0f}%"] for _,r in sb.iterrows()]
table(fig,(0.51,0.375,0.435,0.34),
      ["Period","Regime","Return \u0394, pp","Vol change","Max DD"],
      rows,[0.17,0.25,0.17,0.15,0.26],hi=[2,4],fs=9.3,hdr_fs=9)
fig.text(0.51,0.335,"Max DD shown as model vs 1/N. Highlighted: the two periods the model wins.",fontsize=9.2,
         color=GREY,style="italic",va="top")
b=[("The pattern is the point.  ","It wins in the drawdowns and loses in the rallies - in the "
    "COVID crash it lost 3.7pp less than the benchmark, and in 2022 it fell less while running "
    "36% lower volatility, giving that back in 2021 and 2023-25. That is the trade a "
    "low-volatility mandate explicitly buys, and the reason to present this as a risk-control "
    "product rather than a return-maximising one."),
   ("One exception, stated rather than glossed:  ","in the calm 2018-19 window it ran higher "
    "volatility than 1/N and earned +11pp for it. Volatility is lower in five of six "
    "sub-periods, not all six.")]
bullets(fig,0.055,0.295,b,dy=0.058,fs=10.5,wrap=120)
pg+=1; emit(fig,pg)

# ============================================================ 10 limitations
fig=slide("Limitations, measured not guessed","Four of these are properties of the data and cannot be fixed with this dataset")
table(fig,(0.055,0.185,0.89,0.59),
      ["Limitation","The measurement","Consequence for the reader"],
      [["Risk is understated out of sample",
        f"predicted {DG['mean predicted risk at rebalances_%']:.2f}% at rebalances vs "
        f"{DG['realised volatility_%']:.2f}% realised, i.e. "
        f"{abs(DG['risk understatement_%']):.0f}% understated",
        "say \"consistent with the estimation period\", never \"conservative\""],
       ["The estimation window is a judgement",
        "Lockheed is picked in 100% of 5-year bootstrap resamples and 50% of 10-year ones",
        "we chose 10 years for a full cycle; the cost is reported, not hidden"],
       ["ESG and sector data are a snapshot",
        "one present-day value per stock, no history",
        "applying ESG ≥ 70 at a 2018 rebalance uses 2025 information — look-ahead"],
       ["The universe is survivorship-biased",
        "today's STOXX 600 and S&P 500 constituents only",
        "returns are optimistic for every strategy here, benchmark included"],
       ["Country concentration is unconstrained",
        "Switzerland reaches 47% of the risk-averse book",
        "a 25% country cap costs 0.156pp — the obvious next addition"],
       ["The 30-stock floor pads the book",
        "11 of 30 positions sit exactly on the 1% minimum",
        "a higher minimum weight would give a cleaner portfolio — worth raising with the client"],
       ["Transaction costs are outside the model",
        f"turnover {DG.get('turnover per rebalance mean_%',20.9):.0f}% per rebalance, "
        f"~{DG.get('turnover annualised_%',84):.0f}% a year",
        "at 10bp that is 0.18pp of CAGR, so costs are not the binding issue"]],
      [0.27,0.34,0.39],fs=9.6,hdr_fs=10.5)
fig.text(0.055,0.145,"The first two we can act on. The third and fourth are properties of the dataset. "
         "The last three are choices open to the client.",fontsize=10.5,color=GREY,style="italic")
pg+=1; emit(fig,pg)

# ============================================================ 11 next
fig=slide("Where this stands, and what is next")
fig.text(0.055,0.795,"Settled",fontsize=14.5,color=GREEN,weight="bold",va="top")
b=[("","Model formulation, solved to optimality in under a second on 1,087 stocks"),
   ("","Data cleaning — every decision measured and reproducible from a script"),
   ("","Both risk models compared: quadratic beats linear by 19.2% of risk"),
   ("","Three portfolios, all seven constraints verified independently of the solver"),
   ("","Walk-forward backtest, 7.7 years and 31 rebalances")]
bullets(fig,0.055,0.745,b,dy=0.043,fs=10.5,wrap=57)
fig.text(0.055,0.415,"Open",fontsize=14.5,color=AMBER,weight="bold",va="top")
b=[("Country cap.  ","Switzerland at 47% is the one concentration nothing restrains. "
    "Measured cost 0.156pp."),
   ("Dashboard.  ","Not started, and the largest remaining piece of work."),
   ("Six missing series.  ","Three REITs among them — worth re-extracting.")]
bullets(fig,0.055,0.365,b,dy=0.048,fs=10.5,wrap=57)
fig.patches.append(plt.Rectangle((0.52,0.17),0.425,0.62,transform=fig.transFigure,
                                 facecolor=LIGHT,edgecolor=BLUE,lw=1.3))
fig.text(0.545,0.755,"The one slide to remember",fontsize=13.5,color=NAVY,weight="bold",va="top")
b=[("","The optimiser reliably delivers what it optimises — 22% less volatility than equal "
       "weight, and smaller drawdowns in every crisis in the sample."),
   ("","It does not deliver a higher risk-adjusted return out of sample. That is a known "
       "result in the literature, not a defect in this implementation, and the cause — "
       "estimation error — we measured three independent ways."),
   ("","So this should be presented as a risk-control product, not a return-maximising one. "
       "That is what the constraints describe and what the backtest supports.")]
bullets(fig,0.545,0.695,b,dy=0.052,fs=10.8,wrap=58)
fig.text(0.545,0.225,"Educational exercise. Not investment advice.\nPast performance does not "
         "guarantee future results.",fontsize=8.8,color=GREY,style="italic",va="top")
pg+=1; emit(fig,pg)

pdf.close()
print(f"деку зібрано: {pg} слайдів -> SustainaFund_interim_review.pdf")
