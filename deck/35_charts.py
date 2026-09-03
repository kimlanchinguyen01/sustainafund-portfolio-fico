"""
35 — every chart for the final deck, at 300 dpi
================================================
One function per chart, all sharing the brief's design system. Each returns the
PNG path so the slide builders can place it, and each is sized in inches to the
placeholder box it will occupy so nothing is rescaled on the slide.

DESIGN SYSTEM (from BRIEF_build_deck.md section 3)
  background #FBFAF7   ink #12283F   body #33475B   muted #7C8B99   rule #DDE3E8
  Risk Averse #3E7C8C   Neutral #12283F (hero)   Risk Prone #C08A2E
  1/N #A0A8AE dashed and always subordinate   mandate10 #8FA9B5
  degenerate fill #F1E9DA   negative #A63A2E   positive #4B7F52

  No top or right spine. Horizontal gridlines only. Direct labelling instead of
  legends wherever there are four series or fewer. The headline figure is
  annotated on the chart, so a reader never has to consult an axis for it.

FONT: the brief asks for Inter, falling back to Source Sans 3, Helvetica Neue,
Arial. Neither Inter nor Source Sans 3 is installed here, and Helvetica Neue
exists only on macOS - using it would make the charts disagree with the slide
text the moment the deck is opened on Windows. So Arial is used for BOTH, which
is the one face present on every platform the deck might be shown from. Recorded
as a deliberate deviation.

EVERY FIGURE TRACES to deck/data/deck_data.json or deck/data/derived_metrics.json
or a committed CSV. Nothing is estimated, interpolated-then-printed, or invented.

Run:  python3 deck/35_charts.py        # ~20 s, writes deck/charts/*.png
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHARTS = os.path.join(HERE, "charts")
os.makedirs(CHARTS, exist_ok=True)

BG = "#FBFAF7"
INK = "#12283F"
BODY = "#33475B"
MUTED = "#7C8B99"
RULE = "#DDE3E8"
GRID = "#E6E9EC"
RA = "#3E7C8C"
NEU = "#12283F"
RP = "#C08A2E"
BENCH = "#A0A8AE"
M10 = "#8FA9B5"
DEGEN = "#F1E9DA"
NEG = "#A63A2E"
POS = "#4B7F52"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 11,
    "axes.edgecolor": RULE,
    "axes.labelcolor": BODY,
    "text.color": BODY,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.grid": False,
})

D = json.load(open(os.path.join(HERE, "data", "deck_data.json")))
X = json.load(open(os.path.join(HERE, "data", "derived_metrics.json")))


# --------------------------------------------------------------------------
def _frame(ax, ygrid=True):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(RULE)
    if ygrid:
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.xaxis.grid(False)


def _save(fig, name):
    p = os.path.join(CHARTS, name)
    fig.savefig(p, dpi=300, bbox_inches="tight", pad_inches=0.02,
                transparent=False, facecolor=BG)
    plt.close(fig)
    return p


def pct(v, dec=2):
    return f"{v:.{dec}f}%"


# ============================ S1 · title backdrop ==========================
def title_backdrop(w=13.0, h=2.3):
    """The frontier drawn very faintly across the lower third of the title."""
    pts = D["frontier"]["KNOWN_POINTS_EXACT"]
    fp = pd.read_csv(os.path.join(ROOT, "dashboard_data/scenarios/frontier_points.csv"))
    b = fp[fp.scenario_id == "base"].sort_values("risk")
    fig, ax = plt.subplots(figsize=(w, h))
    ax.plot(b["risk"] * 100, b["expected_return"] * 100, color=INK, alpha=0.12, lw=2)
    ax.scatter([p["risk_pct"] for p in pts], [p["return_pct"] for p in pts],
               color=INK, alpha=0.16, s=26, zorder=3)
    ax.set_axis_off()
    return _save(fig, "s01_title_backdrop.png")


# ============================ S3 · data funnel =============================
def data_funnel(w=7.1, h=3.5):
    u = D["universe"]
    stages = [("Raw tickers supplied", u["raw_tickers"], INK),
              ("No total-return series", -u["dropped_no_total_return_series"], NEG),
              ("Below the ESG floor of 30", -u["dropped_below_esg_floor"], NEG),
              ("Optimisable universe", u["optimizable_universe"], RA)]
    fig, ax = plt.subplots(figsize=(w, h))
    ys = np.arange(len(stages))[::-1]
    for y, (lab, val, col) in zip(ys, stages):
        width = abs(val) if abs(val) > 50 else 40   # deductions need visible bars
        ax.barh(y, width, color=col, height=0.52,
                alpha=1.0 if abs(val) > 50 else 0.9)
        txt = f"{val:+,}" if val < 0 else f"{val:,}"
        ax.text(width + 18, y, txt, va="center", ha="left", color=col,
                fontsize=13, fontweight="bold")
        ax.text(-20, y, lab, va="center", ha="right", color=BODY, fontsize=11)
    ax.set_xlim(-20, 1330)
    ax.set_ylim(-0.6, len(stages) - 0.4)
    ax.set_yticks([])
    ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(0.60, 0.03, "deductions shown at a fixed width so they stay visible",
            transform=ax.transAxes, fontsize=9, color=MUTED, ha="center")
    return _save(fig, "s03_funnel.png")


# ============================ S4 · FX ======================================
def fx_panels(w=7.3, h=3.6):
    f = D["fx"]
    fig, axes = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"wspace": 0.42})

    ax = axes[0]
    vals = [f["same_weights_vol_local_pct"], f["same_weights_vol_usd_pct"]]
    bars = ax.bar(["Local\ncurrency", "USD"], vals, color=[BENCH, RA], width=0.52)
    for b_, v in zip(bars, vals):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 0.12, pct(v),
                ha="center", color=INK, fontsize=12, fontweight="bold")
    ax.annotate("", xy=(1, vals[1]), xytext=(0, vals[0]),
                arrowprops=dict(arrowstyle="->", color=NEG, lw=1.4))
    ax.text(0.5, max(vals) + 0.62, f"+{vals[1]-vals[0]:.2f} pp", ha="center",
            color=NEG, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(vals) * 1.30)
    ax.set_ylabel("annualised volatility, %")
    ax.set_title("Identical weights, two measuring sticks",
                 fontsize=11, color=INK, pad=8)
    _frame(ax)

    ax = axes[1]
    vals = [f["min_variance_predicted_risk_local_pct"], f["min_variance_true_risk_usd_pct"]]
    bars = ax.bar(["Predicted\n(local Σ)", "True\n(USD Σ)"], vals,
                  color=[BENCH, NEG], width=0.52)
    for b_, v in zip(bars, vals):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 0.14, pct(v),
                ha="center", color=INK, fontsize=12, fontweight="bold")
    ax.text(0.5, max(vals) * 1.16,
            f"understated by {f['risk_understatement_pct']:.1f}%",
            ha="center", color=NEG, fontsize=11.5, fontweight="bold")
    ax.set_ylim(0, max(vals) * 1.32)
    ax.set_title("The minimum-variance book's own risk",
                 fontsize=11, color=INK, pad=8)
    _frame(ax)
    return _save(fig, "s04_fx.png")


# ============================ S5 · dividends ===============================
def dividends(w=7.2, h=3.4):
    d = D["dividends"]
    fig, axes = plt.subplots(2, 1, figsize=(w, h),
                             gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.62})
    ax = axes[0]
    a = d["median_expected_return_price_only_pct"]
    b_ = d["median_expected_return_total_return_pct"]
    ax.plot([a, b_], [0, 0], color=RULE, lw=3, zorder=1)
    ax.scatter([a], [0], s=150, color=BENCH, zorder=3)
    ax.scatter([b_], [0], s=190, color=RA, zorder=3)
    ax.annotate("", xy=(b_ - 0.06, 0), xytext=(a + 0.06, 0),
                arrowprops=dict(arrowstyle="->", color=RA, lw=1.6))
    ax.text(a, 0.30, f"price only\n{pct(a)}", ha="center", color=MUTED, fontsize=10.5)
    ax.text(b_, 0.30, f"total return\n{pct(b_)}", ha="center", color=INK,
            fontsize=11, fontweight="bold")
    ax.text((a + b_) / 2, -0.42, f"median expected return, +{b_-a:.2f} pp",
            ha="center", color=BODY, fontsize=10.5)
    ax.set_xlim(a - 1.1, b_ + 1.1)
    ax.set_ylim(-0.75, 0.75)
    ax.set_axis_off()

    ax = axes[1]
    sectors = [("Energy", 3.89), ("Technology", 1.18)]
    ys = np.arange(len(sectors))[::-1]
    for y, (lab, v) in zip(ys, sectors):
        ax.barh(y, v, color=RA, height=0.46)
        ax.text(v + 0.08, y, f"+{v:.2f} pp", va="center", color=INK,
                fontsize=11.5, fontweight="bold")
        ax.text(-0.12, y, lab, va="center", ha="right", color=BODY, fontsize=11)
    ax.set_xlim(0, 4.9)
    ax.set_ylim(-0.6, len(sectors) - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("uplift in expected return, pp")
    ax.set_title("Uplift is ordered by dividend yield — the two sectors we can quote",
                 fontsize=10, color=MUTED, pad=6, loc="left")
    _frame(ax, ygrid=False)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return _save(fig, "s05_dividends.png")


# ============================ S6 · shrinkage ===============================
def shrinkage(w=7.4, h=3.2):
    e = D["expected_returns"]
    lo, hi = 2.7, 19.1
    tgt = e["shrink_target_pct"]
    raw, shr = e["max_raw_mu_pct"], e["max_shrunk_mu_pct"]
    fig, ax = plt.subplots(figsize=(w, h))
    ax.hlines(0, 0, 66, color=RULE, lw=1.2)
    ax.add_patch(plt.Rectangle((lo, -0.16), hi - lo, 0.32, color=RA, alpha=0.92, zorder=2))
    ax.text((lo + hi) / 2, 0.30, f"shrunk estimates  {pct(lo,1)} – {pct(hi,1)}",
            ha="center", color=INK, fontsize=11, fontweight="bold")
    ax.vlines(tgt, -0.42, 0.42, color=INK, lw=1.8, zorder=4)
    ax.text(tgt, -0.62, f"target {pct(tgt)}\ngrand mean of 989 full-history stocks",
            ha="center", va="top", color=BODY, fontsize=9.5)
    ax.scatter([raw], [0], s=110, color=NEG, zorder=5)
    ax.text(raw, 0.30, f"{pct(raw)} raw", ha="center", color=NEG,
            fontsize=11.5, fontweight="bold")
    ax.annotate("", xy=(shr + 0.4, 0.10), xytext=(raw - 0.6, 0.10),
                arrowprops=dict(arrowstyle="->", color=NEG, lw=1.5,
                                connectionstyle="arc3,rad=0.32"))
    ax.text((raw + shr) / 2, 0.86, "the most extreme estimate, shrunk to "
            f"{pct(shr)}", ha="center", color=NEG, fontsize=10.5)
    ax.set_xlim(-1, 68)
    ax.set_ylim(-1.5, 1.15)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    ax.set_xlabel("annualised expected return")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    return _save(fig, "s06_shrinkage.png")


# ============================ S7 · factor count ============================
def factor_count(w=7.5, h=3.9):
    t = pd.DataFrame(D["risk_model"]["selection_table"])
    fig, ax = plt.subplots(figsize=(w, h))
    xs = np.arange(len(t))
    cols = [NEG if v < 0 else RA for v in t.risk_error_at_min_risk_pct]
    chosen = t.index[t.k == D["risk_model"]["factors_chosen"]][0]
    cols[chosen] = INK
    ax.bar(xs, t.risk_error_at_min_risk_pct, color=cols, width=0.6, zorder=3)
    ax.axhline(0, color=INK, lw=1.4, zorder=4)
    for x, v in zip(xs, t.risk_error_at_min_risk_pct):
        ax.text(x, v + (1.6 if v >= 0 else -2.4), f"{v:+.2f}", ha="center",
                color=INK if v >= 0 else NEG, fontsize=10,
                fontweight="bold" if x == chosen else "normal")
    ax.text(chosen, t.risk_error_at_min_risk_pct[chosen] + 6.4, "CHOSEN",
            ha="center", color=INK, fontsize=10, fontweight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels(t.k)
    ax.set_xlabel("number of factors in the covariance model")
    ax.set_ylabel("risk error at the minimum-risk point, %")
    ax.set_ylim(-46, 16)
    _frame(ax)

    i5, i10 = int(t.index[t.k == 5][0]), int(t.index[t.k == 10][0])
    ax.annotate("", xy=(i10, 4.2), xytext=(i5, 4.2),
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.1))
    ax.text((i5 + i10) / 2, 5.6, "not monotone — this region is measurement noise",
            ha="center", color=MUTED, fontsize=9.5)

    ax2 = ax.twinx()
    ax2.plot(xs, t.variance_explained_pct, color=MUTED, lw=1.2, marker="o", ms=3)
    ax2.set_ylabel("variance explained, %", color=MUTED)
    ax2.set_ylim(0, 100)
    for sp in ("top", "left"):
        ax2.spines[sp].set_visible(False)
    ax2.spines["right"].set_color(RULE)
    ax2.tick_params(colors=MUTED)
    return _save(fig, "s07_factor_count.png")


# ============================ S9 · constraint costs ========================
def constraint_costs(w=7.4, h=3.9):
    rows = [("Weighted-average ESG ≥ 70  (given)", 0.151, INK, False),
            ("Country cap 25%  (ships off)", 0.067, RP, True),
            ("Sector cap 30%", 0.020, RA, False),
            ("Per-stock ESG floor ≥ 30", 0.008, RA, False),
            ("Tier 2 weapons exclusion  (off)", 0.004, RP, True)]
    fig, ax = plt.subplots(figsize=(w, h))
    ys = np.arange(len(rows))[::-1]
    for y, (lab, v, col, hatch) in zip(ys, rows):
        ax.barh(y, v, color=col, height=0.5, zorder=3,
                hatch="///" if hatch else None,
                edgecolor=col if not hatch else "white", linewidth=0.8)
        note = "  +0.008 — no cost" if abs(v - 0.008) < 1e-9 else f"  {v:.3f} pp"
        ax.text(v + 0.003, y, note, va="center", color=INK, fontsize=11,
                fontweight="bold")
        ax.text(-0.004, y, lab, va="center", ha="right", color=BODY, fontsize=10.5)
    ax.set_xlim(0, 0.20)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("cost at the Neutral profile, pp of expected return")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.text(0.0, -0.30, "hatched = built and measured but not active. The country-cap "
            "figure is return given up at\nmatched risk; the same cap costs 0.112 pp of "
            "risk at matched return.", fontsize=8.5, color=MUTED, va="top",
            transform=ax.transAxes)
    return _save(fig, "s09_constraint_costs.png")


# ============================ S10 · the frontier (hero) ====================
def frontier_hero(w=11.6, h=4.5):
    fp = pd.read_csv(os.path.join(ROOT, "dashboard_data/scenarios/frontier_points.csv"))
    b = fp[fp.scenario_id == "base"].sort_values("frontier_point")
    known = {p["point"]: p for p in D["frontier"]["KNOWN_POINTS_EXACT"]}
    fig, ax = plt.subplots(figsize=(w, h))

    ax.add_patch(plt.Rectangle((13.5, 8.6), 24 - 13.5, 18.6 - 8.6,
                               color=DEGEN, zorder=1))
    ax.text(19.0, 9.35, "DEGENERATE — points 12–14 excluded", color="#8F6A15",
            fontsize=10.5, ha="center", fontweight="bold")

    try:
        from scipy.interpolate import PchipInterpolator
        s = b.sort_values("risk")
        f = PchipInterpolator(s["risk"].values * 100, s["expected_return"].values * 100)
        xs = np.linspace(s["risk"].min() * 100, s["risk"].max() * 100, 300)
        ax.plot(xs, f(xs), color=INK, lw=2.0, zorder=3)
    except Exception:
        ax.plot(b["risk"] * 100, b["expected_return"] * 100, color=INK, lw=2.0, zorder=3)

    ax.scatter(b["risk"] * 100, b["expected_return"] * 100, s=22,
               color=INK, alpha=0.30, zorder=4)
    # Label placement is deliberate, not default: pt 11 goes UP-LEFT into the
    # empty region above the steep part, because down-right would put its label
    # inside the degenerate shading and imply the point is degenerate. pt 0 goes
    # right at marker height so it clears the x-axis tick labels.
    marks = [(0, RA, "Risk Averse · pt 0", (15, 4), 150),
             (8, NEU, "Neutral · pt 8 — recommended", (16, 6), 260),
             (11, RP, "Risk Prone · pt 11", (-208, 16), 170)]
    for pt, col, lab, off, size in marks:
        k = known[pt]
        ax.scatter([k["risk_pct"]], [k["return_pct"]], s=size, color=col,
                   edgecolor=BG, linewidth=2.0, zorder=6)
        # pt 11's label sits far from its marker to stay out of the shaded zone,
        # so it gets a faint leader; the other two sit beside their markers.
        arrow = dict(arrowstyle="-", color=col, lw=0.9, alpha=0.55,
                     shrinkA=2, shrinkB=8) if pt == 11 else None
        ax.annotate(lab, (k["risk_pct"], k["return_pct"]), textcoords="offset points",
                    xytext=off, fontsize=11.5, color=col, fontweight="bold", zorder=7,
                    arrowprops=arrow)
        ax.annotate(f"{pct(k['return_pct'])} at {pct(k['risk_pct'])}   ratio {k['ratio']:.3f}",
                    (k["risk_pct"], k["return_pct"]), textcoords="offset points",
                    xytext=(off[0], off[1] - 13), fontsize=9.5, color=BODY, zorder=7)

    ax.set_xlim(8.5, 24)
    ax.set_ylim(9.0, 18.9)
    ax.set_xlabel("risk — annualised volatility, %")
    ax.set_ylabel("expected return, % p.a.")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:.0f}%"))
    _frame(ax)
    ax.text(0.995, -0.235, "curve interpolated between solved points for shape; "
            "only the six exact points are labelled",
            transform=ax.transAxes, fontsize=9, color=MUTED, ha="right")
    return _save(fig, "s10_frontier.png")


# ============================ S13 · ESG + Switzerland ======================
def esg_and_switzerland(w=7.4, h=3.6):
    fig, axes = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"wspace": 0.40})
    ax = axes[0]
    fp = pd.read_csv(os.path.join(ROOT, "dashboard_data/scenarios/frontier_points.csv"))
    b = fp[fp.scenario_id == "base"].sort_values("frontier_point")
    ax.plot(b.frontier_point, b.weighted_esg, color=INK, lw=2, marker="o", ms=4)
    ax.axhline(70, color=NEG, lw=1.0, ls="--")
    ax.set_ylim(60, 80)
    ax.set_xlabel("frontier point")
    ax.set_ylabel("weighted ESG")
    ax.text(7, 71.4, "pinned on 70.00 at all 15 points", color=INK, fontsize=10.5,
            ha="center", fontweight="bold")
    ax.set_title("The ESG constraint is always binding", fontsize=10.5, color=INK, pad=8)
    _frame(ax)

    ax = axes[1]
    c = D["concentration"]
    labs = ["Switzerland", "Switzerland\n+ United States"]
    vals = [c["switzerland_share_of_risk_averse_book_pct"], c["switzerland_plus_us_share_pct"]]
    for i, (lab, v) in enumerate(zip(labs, vals)):
        ax.barh(i, v, color=[RP, BENCH][i], height=0.46, zorder=3)
        ax.text(v + 1.4, i, pct(v), va="center", color=INK, fontsize=12,
                fontweight="bold")
    ax.axvline(25, color=NEG, ls="--", lw=1.3, zorder=4)
    ax.text(25.8, 1.44, "25% cap", color=NEG, fontsize=10, fontweight="bold")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(labs, fontsize=10)
    ax.set_xlim(0, 108)
    ax.set_xlabel("share of the risk-averse book, %")
    ax.set_title("What the given constraints could not see", fontsize=10.5,
                 color=INK, pad=8)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return _save(fig, "s13_esg_switzerland.png")


# ============================ S14 · what it actually does ==================
def capture_and_underwater(w=7.4, h=3.6):
    cap = X["capture"]["books"]["mandate20"]
    uw = X["underwater"]["longest_underwater_stretch"]
    rec = X["recovery_alternatives"]
    fig, axes = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"wspace": 0.45})

    ax = axes[0]
    vals = [cap["up_capture_pct"], cap["down_capture_pct"]]
    bars = ax.bar(["Up months", "Down months"], vals, color=[POS, NEU], width=0.5)
    ax.axhline(100, color=MUTED, ls="--", lw=1.1)
    ax.text(1.42, 100.6, "1/N = 100", color=MUTED, fontsize=9.5, ha="right")
    for b_, v in zip(bars, vals):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 1.4, f"{v:.1f}%",
                ha="center", color=INK, fontsize=13, fontweight="bold")
    ax.set_ylim(0, 128)
    ax.set_ylabel("capture vs 1/N, %")
    ax.set_title(f"Recommended book: captures more up than down\n"
                 f"{X['capture']['n_up_months']} up months, "
                 f"{X['capture']['n_down_months']} down",
                 fontsize=10, color=INK, pad=8)
    _frame(ax)

    ax = axes[1]
    labs = ["Minimum\nvariance", "1/N"]
    vals = [uw["minvar"], uw["equal_weight"]]
    for i, (lab, v) in enumerate(zip(labs, vals)):
        ax.bar(i, v, color=[RA, BENCH][i], width=0.5, zorder=3)
        ax.text(i, v + 14, f"{v}", ha="center", color=INK, fontsize=13,
                fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labs, fontsize=10)
    ax.set_ylim(0, 810)
    ax.set_ylabel("longest unbroken stretch below peak, trading days")
    r22 = rec["2022"]
    ax.set_title("The shallower drawdown lasts longer\n"
                 f"after 2022: {r22['minvar']['trough_to_recovery_trading_days']} "
                 f"vs {r22['equal_weight']['trough_to_recovery_trading_days']} "
                 "trading days trough-to-recovery",
                 fontsize=10, color=INK, pad=8)
    _frame(ax)
    return _save(fig, "s14_capture_underwater.png")


# ============================ S15 · equity curves ==========================
def equity_curves(w=11.4, h=3.5):
    E = pd.read_csv(os.path.join(ROOT, "backtest_profiles/results/equity_curves.csv"),
                    index_col=0, parse_dates=True)
    M = E.resample("ME").last()
    fig, ax = plt.subplots(figsize=(w, h))
    for a, b_, lab in [("2020-02-01", "2020-03-31", "COVID"),
                       ("2022-01-01", "2022-10-31", "2022")]:
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b_), color=DEGEN, zorder=1)
        ax.text(pd.Timestamp(a), 0.62, lab, color="#8F6A15", fontsize=9.5,
                rotation=90, va="bottom")
    series = [("mandate10", M10, 1.6), ("mandate20", NEU, 2.4),
              ("minvar", RA, 1.9), ("equal_weight", BENCH, 1.7)]
    NAMES = {"mandate10": "mandate10", "mandate20": "mandate20  (Neutral stand-in)",
             "minvar": "minvar", "equal_weight": "1/N"}
    for col, c, lw in series:
        ax.plot(M.index, M[col], color=c, lw=lw, zorder=3,
                ls="--" if col == "equal_weight" else "-")
        ax.text(M.index[-1] + pd.Timedelta(days=42), M[col].iloc[-1],
                f"{NAMES[col]}  {M[col].iloc[-1]:.2f}×", color=c, fontsize=10,
                va="center", fontweight="bold" if col == "mandate20" else "normal")
    ax.set_yscale("log")
    ax.set_yticks([1, 1.5, 2, 3, 4, 5])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}×"))
    ax.set_ylabel("indexed wealth (log scale)")
    ax.set_xlim(M.index[0], M.index[-1] + pd.Timedelta(days=760))
    _frame(ax)
    return _save(fig, "s15_equity_curves.png")


# ============================ S16 · significance ===========================
def significance(w=7.5, h=3.3):
    jk = X["significance_jobson_korkie"]["books"]
    tt = {r["book"]: r for r in D["backtest"]["significance_vs_1N"]}
    order = ["minvar", "mandate20", "mandate10"]
    fig, ax = plt.subplots(figsize=(w, h))
    ax.axvspan(-1.96, 1.96, color=DEGEN, zorder=1)
    ax.text(0, 2.62, "not distinguishable from the benchmark", ha="center",
            color="#8F6A15", fontsize=10.5, fontweight="bold")
    ax.axvline(0, color=MUTED, lw=1.0, zorder=2)
    cols = {"minvar": RA, "mandate20": NEU, "mandate10": M10}
    for i, b_ in enumerate(order):
        y = len(order) - 1 - i
        z = jk[b_]["z"]
        ax.scatter([z], [y], s=190, color=cols[b_], zorder=5, edgecolor=BG, linewidth=1.8)
        ds = tt[b_]["delta_sharpe"] if b_ in tt else None
        lab = f"  z = {z:+.3f}"
        if ds is not None:
            lab += f"   ΔSharpe {ds:+.3f}"
        ax.text(z + 0.10, y, lab, va="center", color=INK, fontsize=11)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([{"minvar": "minvar", "mandate20": "mandate20",
                         "mandate10": "mandate10"}[b_] for b_ in order[::-1]],
                       fontsize=11)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-0.6, 2.9)
    ax.set_xlabel("Jobson-Korkie z with the Memmel correction, vs 1/N")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return _save(fig, "s16_significance.png")


# ============================ S17 · predicted vs realised ==================
def predicted_vs_realised(w=7.4, h=3.6):
    E = pd.read_csv(os.path.join(ROOT, "backtest_profiles/results/equity_curves.csv"),
                    index_col=0, parse_dates=True)
    R = pd.read_csv(os.path.join(ROOT, "backtest_profiles/results/rebalances.csv"))
    R["date"] = pd.to_datetime(R["date"])
    dates = sorted(R.date.unique())
    fig, ax = plt.subplots(figsize=(w, h))
    for book, col, lab in [("mandate20", NEU, "mandate20"), ("minvar", RA, "minvar")]:
        sub = R[R.book == book].set_index("date")
        xs, ys = [], []
        for i, d in enumerate(dates):
            if d not in sub.index:
                continue
            nxt = dates[i + 1] if i + 1 < len(dates) else E.index[-1]
            seg = E[book].loc[(E.index > d) & (E.index <= nxt)]
            if len(seg) < 5:
                continue
            start = E[book].asof(d)
            yrs = (seg.index[-1] - d).days / 365.25
            if yrs <= 0:
                continue
            xs.append(float(sub.loc[d, "pred_return_%"]))
            ys.append(((seg.iloc[-1] / start) ** (1 / yrs) - 1) * 100)
        ax.scatter(xs, ys, s=44, color=col, alpha=0.85, zorder=4, label=lab)
        m = X["predicted_vs_realised"]["books"][book]
        z = np.polyfit(xs, ys, 1)
        xr = np.linspace(min(xs), max(xs), 20)
        ax.plot(xr, np.polyval(z, xr), color=col, lw=1.5, ls="--", zorder=3)
        ax.text(max(xs), np.polyval(z, max(xs)) - 6,
                f"{lab}   r = {m['correlation_predicted_vs_realised']:+.3f}"
                + (f"  (p = {m['p_two_sided']:.3f})" if book == "mandate20" else ""),
                color=col, fontsize=10.5, ha="right", fontweight="bold")
    lim = [-15, 95]
    ax.plot(lim, lim, color=MUTED, lw=1.0, ls=":", zorder=2)
    ax.text(84, 88, "perfect forecast", color=MUTED, fontsize=9, rotation=38, ha="right")
    ax.set_xlim(*lim)
    ax.set_ylim(-45, 95)
    ax.set_xlabel("predicted annualised return at the rebalance, %")
    ax.set_ylabel("realised annualised return, %")
    ax.axhline(0, color=RULE, lw=1.0)
    _frame(ax)
    ax.text(0.02, 0.04, "31 rebalances. A negative slope means the forecast is "
            "worse than useless.", transform=ax.transAxes, fontsize=9.5, color=MUTED)
    return _save(fig, "s17_pred_vs_realised.png")


# ============================ S18 · crisis =================================
def crisis(w=11.4, h=3.5):
    pb = D["crisis_stress_test"]["panel_b_results_pct"]
    rows = [r for r in pb if r["window"] != "2020 crash + recovery"]
    fig, axes = plt.subplots(1, 2, figsize=(w, h),
                             gridspec_kw={"wspace": 0.30, "width_ratios": [1.35, 1]})
    ax = axes[0]
    xs = np.arange(len(rows))
    wid = 0.26
    for j, (key, col, lab) in enumerate([("risk_averse", RA, "Risk Averse"),
                                         ("neutral", NEU, "Neutral"),
                                         ("equal_weight", BENCH, "1/N")]):
        vals = [r[key] for r in rows]
        ax.bar(xs + (j - 1) * wid, vals, width=wid, color=col, zorder=3,
               hatch="///" if key == "equal_weight" else None,
               edgecolor="white" if key == "equal_weight" else col, linewidth=0.7)
        for x, v in zip(xs, vals):
            ax.text(x + (j - 1) * wid, v - 1.9, f"{v:.1f}", ha="center", va="top",
                    color=col if key != "equal_weight" else "#6E767C", fontsize=9.5,
                    fontweight="bold")
        ax.text(xs[-1] + (j - 1) * wid + 0.42, vals[-1] / 2, lab, color=col,
                fontsize=10, va="center", fontweight="bold")
    ax.axhline(0, color=INK, lw=1.2)
    ax.set_xticks(xs)
    ax.set_xticklabels([r["window"] for r in rows], fontsize=10)
    ax.set_ylabel("window return, %")
    ax.set_ylim(-44, 6)
    ax.set_title("Panel B — point-in-time, the actual test", fontsize=10.5,
                 color=INK, pad=8)
    _frame(ax)

    ax = axes[1]
    pv = D["crisis_stress_test"]["predicted_vs_realised_risk_neutral"]
    labs = [p["window"].replace(" crash + recovery", "\ncrash+recovery") for p in pv]
    vals = [p["ratio"] for p in pv]
    cols = [NEG if v > 5 else NEU for v in vals]
    ax.bar(np.arange(len(vals)), vals, color=cols, width=0.55, zorder=3)
    ax.axhline(1.0, color=MUTED, ls="--", lw=1.2)
    ax.text(len(vals) - 0.4, 1.18, "forecast", color=MUTED, fontsize=9.5, ha="right")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.16, f"{v:.2f}×", ha="center", color=INK, fontsize=11.5,
                fontweight="bold")
    ax.set_xticks(np.arange(len(vals)))
    ax.set_xticklabels(labs, fontsize=9)
    ax.set_ylim(0, 7.9)
    ax.set_ylabel("realised ÷ predicted risk")
    ax.set_title("The Neutral book's own risk forecast", fontsize=10.5, color=INK, pad=8)
    _frame(ax)
    return _save(fig, "s18_crisis.png")


# ============================ backup charts ================================
def backup_windows(w=7.4, h=3.4):
    w3 = D["estimation_window_instability"]["neutral_by_window"]
    fig, ax = plt.subplots(figsize=(w, h))
    xs = [r["risk_pct"] for r in w3]
    ys = [r["return_pct"] for r in w3]
    labs = [f"{r['window_years']}y" for r in w3]
    ax.plot(xs, ys, color=RULE, lw=1.4, zorder=2)
    for x, y, lab, r in zip(xs, ys, labs, w3):
        col = NEU if r["window_years"] == 10 else NEG
        ax.scatter([x], [y], s=190, color=col, zorder=4, edgecolor=BG, linewidth=1.8)
        ax.annotate(f"{lab}   {pct(y)} at {pct(x)}   ratio {r['ratio']:.2f}",
                    (x, y), textcoords="offset points", xytext=(12, -4),
                    fontsize=10.5, color=col, fontweight="bold")
    ax.set_xlabel("risk — annualised volatility, %")
    ax.set_ylabel("expected return, % p.a.")
    ax.set_xlim(6.5, 12.5)
    ax.set_ylim(12, 29)
    _frame(ax)
    ax.text(0.02, 0.05, "Shorter windows look better and are worse: μ's range widens "
            "from 2.7–19.1% to −9.8–46.1%.", transform=ax.transAxes,
            fontsize=9.5, color=MUTED)
    return _save(fig, "b03_windows.png")


def backup_tail(w=7.2, h=3.2):
    tr = X["tail_risk"]["books"]
    order = ["minvar", "equal_weight", "mandate20", "mandate10"]
    NAMES = {"minvar": "minvar", "equal_weight": "1/N", "mandate20": "mandate20",
             "mandate10": "mandate10"}
    COLS = {"minvar": RA, "equal_weight": BENCH, "mandate20": NEU, "mandate10": M10}
    fig, ax = plt.subplots(figsize=(w, h))
    ys = np.arange(len(order))[::-1]
    for y, b_ in zip(ys, order):
        v = tr[b_]["cvar95_pct"]
        ax.barh(y, v, color=COLS[b_], height=0.5, zorder=3)
        ax.text(v - 0.08, y, f"{v:.2f}%", va="center", ha="right", color=INK,
                fontsize=11.5, fontweight="bold")
        ax.text(0.06, y, NAMES[b_], va="center", ha="left", color=BODY, fontsize=10.5)
    ax.set_xlim(-3.8, 0.9)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("CVaR 95 — mean of the worst 5% of days, %")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    return _save(fig, "b09_tail.png")


ALL = {
    "s01": title_backdrop, "s03": data_funnel, "s04": fx_panels,
    "s05": dividends, "s06": shrinkage, "s07": factor_count,
    "s09": constraint_costs, "s10": frontier_hero, "s13": esg_and_switzerland,
    "s14": capture_and_underwater, "s15": equity_curves, "s16": significance,
    "s17": predicted_vs_realised, "s18": crisis,
    "b03": backup_windows, "b09": backup_tail,
}

if __name__ == "__main__":
    for k, fn in ALL.items():
        p = fn()
        print(f"  {k}  {os.path.relpath(p, ROOT)}")
    print(f"\n{len(ALL)} charts written to {os.path.relpath(CHARTS, ROOT)}/ at 300 dpi")
