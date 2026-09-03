"""
36 — the slide content, defined once
=====================================
Structure follows `presentation_structure_EN.md.docx` (19 main slides in seven
sections, including its two NEW slides S14 and S17 and its Jobson-Korkie test on
S16). Design system, hard rules and furniture follow `BRIEF_build_deck.md`.

Defined once here and consumed by two renderers - 36_build_pptx.py and
36_build_pdf.py - because the brief wants a PPTX and a PDF and the two must not
drift apart. libreoffice is absent on this machine, so the PDF is rendered
natively rather than converted.

EVERY FIGURE traces to deck/data/deck_data.json, deck/data/derived_metrics.json
or a committed CSV. Two elements the docx asked for are deliberately absent:

  * its recovery figures (1,073 / 529 / 104 / 233) do not reproduce under any
    definition, so S14 uses the trough-to-recovery figures that do, and the
    speaker note says so;
  * nothing anywhere prints 16.6% or 38.8%, and Risk Prone is point 11
    throughout - both required by the brief's final checklist.

SLIDE SPEC
  stage     which segment of the progress ribbon is lit
  headline  a complete claim, <= 10 words
  sub       optional sub-headline, muted
  chart     PNG path, or None
  table     {"cols": [...], "rows": [[...]], "widths": [...], "hi": row index}
  bignums   [(value, label), ...]
  bullets   <= 3, <= 12 words each
  sowhat    the line the presenter says to close the slide
  notes     speaker notes, starting with a [m:ss] timing marker
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "charts")

D = json.load(open(os.path.join(HERE, "data", "deck_data.json")))
X = json.load(open(os.path.join(HERE, "data", "derived_metrics.json")))

STAGES = ["MANDATE", "DATA", "RISK MODEL", "OPTIMISATION", "RESULTS", "VALIDATION"]

BG = "#FBFAF7"; INK = "#12283F"; BODY = "#33475B"; MUTED = "#7C8B99"
RULE = "#DDE3E8"; STRIP = "#F1EEE8"; PANEL = "#F4F2ED"; HILITE = "#EDF0F3"
RA = "#3E7C8C"; NEU = "#12283F"; RP = "#C08A2E"; BENCH = "#A0A8AE"
DEGEN = "#F1E9DA"; NEG = "#A63A2E"; POS = "#4B7F52"

c = X["capture"]["books"]["mandate20"]
uw = X["underwater"]["longest_underwater_stretch"]
rec22 = X["recovery_alternatives"]["2022"]
recc = X["recovery_alternatives"]["COVID"]
jk = X["significance_jobson_korkie"]["books"]
pv = X["predicted_vs_realised"]["books"]
tail = X["tail_risk"]["books"]
dp = {r["profile"]: r for r in D["delivered_portfolios"]}
NEUK = "Neutral - recommended" if "Neutral - recommended" in dp else "Neutral"

SLIDES = [
# ============================== A · MANDATE ==============================
dict(kind="title", stage=None,
     headline="SustainaFund",
     sub="A $100 million ESG-constrained equity portfolio — efficient frontier, "
         "three mandates, and what survived out-of-sample testing",
     meta="HTW Berlin Summer School 2026 · FICO Xpress case study · September 2026",
     chart=f"{CH}/s01_title_backdrop.png",
     notes="[0:15] Good morning. Over the next twenty minutes I will show you a "
           "hundred-million-dollar equity portfolio built as a mixed-integer "
           "quadratic programme, and I will spend most of the time on why each "
           "choice was made rather than on what the model produced. Every "
           "methodology decision in this deck arrives with the measurement that "
           "decided it. Two of the slides say outright that our recommended book "
           "has no statistically significant edge — I would rather volunteer that "
           "than have it extracted."),

dict(kind="content", stage="MANDATE",
     headline="The deliverable is a frontier, not a single portfolio",
     table={"cols": ["Given by the brief", "Added by us"],
            "rows": [["1% ≤ weight ≤ 20% per stock", "Sector cap 30%"],
                     ["Each region ≤ 60%", "Per-stock ESG floor ≥ 30"],
                     ["At least 30 holdings", "Tier 1 weapons exclusion (always on)"],
                     ["Weighted-average ESG ≥ 70", "Tier 2 weapons exclusion (toggle, off)"],
                     ["", "Country cap 25% (built, measured, ships off)"]],
            "widths": [3.3, 3.5], "hdr_colors": [INK, RP]},
     bignums=[("$100M", "budget"), ("1,077", "investable stocks"),
              ("15", "frontier points")],
     bullets=["Risk appetite was never specified in the brief",
              "So we solve the whole frontier and report three points",
              "Every addition of ours is priced later in this deck"],
     sowhat="Risk appetite was never given to us, so we report the frontier and "
            "three mandates on it.",
     notes="[1:15] The brief fixes four conditions and leaves the most important "
           "input unspecified: how much risk the fund wants. So the deliverable "
           "cannot be one portfolio. We solve fifteen points along the frontier "
           "and report three of them. The left column is the brief's own "
           "conditions; the right is what we added, and I will show you the "
           "measured cost of each. Worth noting now: the ESG requirement that "
           "carries almost the entire cost is the one the brief itself imposed — "
           "the per-stock floor we added is free."),

# ================================ B · DATA ================================
dict(kind="content", stage="DATA",
     headline="1,093 tickers in, 1,077 investable out",
     chart=f"{CH}/s03_funnel.png",
     bullets=["Ten years of daily LSEG data, 2015 to 2025",
              "Converted to USD at daily ECB reference rates",
              "Total-return prices, not closing prices"],
     sowhat="Every exclusion is a written rule applied to all names, not a "
            "judgement about a company.",
     notes="[0:40] Sixteen names leave the universe and both reasons are "
           "mechanical. Six lost their total-return series entirely — 2,870 of "
           "2,870 values absent — and three of those six are REITs, whose "
           "dividend adjustment factors are the largest, so the extraction most "
           "likely failed on them. We dropped them rather than substituting the "
           "unadjusted series, because an unadjusted series carries about three "
           "percentage points less return and the optimiser would then punish "
           "those stocks for a data defect. Ten more fall below our per-stock ESG "
           "floor. No name is excluded by opinion."),

dict(kind="content", stage="DATA",
     headline="Currency is a risk factor, not a unit conversion",
     chart=f"{CH}/s04_fx.png",
     bullets=["ln(P_usd) = ln(P_local) + ln(fx) — the FX term does not cancel",
              "FX is 17.6% of total portfolio variance",
              "A fund reports in one currency, not eight"],
     sowhat="Optimising on local-currency returns optimises a return no investor "
            "ever receives.",
     notes="[0:45] The natural objection is that currency cannot matter because "
           "returns are ratios. That holds for a constant, and an exchange rate "
           "is not constant. Take logs and the FX term is additive, so it "
           "survives into the return series — and because every stock in a "
           "currency shares it, it is a common factor, exactly what a covariance "
           "matrix exists to capture. The left panel is the same weight vector "
           "priced two ways. The right panel is the consequence: a "
           "local-currency covariance tells the minimum-variance book it carries "
           "8.46% risk when it actually carries 10.13%. Understating risk is the "
           "one failure a risk-averse mandate cannot tolerate."),

dict(kind="content", stage="DATA",
     headline="Price returns penalise the stocks min-variance wants",
     chart=f"{CH}/s05_dividends.png",
     bullets=["Stocks with negative expected return: 3 → 0",
              "Rank correlation 0.972 — levels move, order mostly holds",
              "We validated the vendor series with three checks"],
     sowhat="We tested the adjusted series rather than trusting it: ratio "
            "anchored at 1.00, volatility unchanged, uplift ordered by dividend "
            "yield.",
     notes="[0:35] A closing price omits dividends, and the bias is not neutral — "
           "it falls hardest on the high-yield, low-volatility names a "
           "minimum-variance book is made of. Median expected return moves from "
           "7.80% to 10.39%. We did not simply trust the vendor's adjusted file: "
           "the adjustment ratio is anchored at 1.00 at the most recent date, "
           "volatility is unchanged at 31.05% against 31.08% because dividends "
           "add drift and not noise, and the uplift is ordered by dividend yield "
           "across sectors. Any one of those failing would have meant a broken "
           "series."),

dict(kind="content", stage="DATA",
     headline="A 62.6% historical mean is not a forecast",
     chart=f"{CH}/s06_shrinkage.png",
     bullets=["w_i = τ² / (τ² + se_i²), shrinking toward the grand mean",
              "Both τ² and se² are estimated from the data",
              "No tuning parameter anywhere in the estimator"],
     sowhat="The amount of shrinkage is measured, not chosen — there is no knob "
            "for a referee to attack.",
     notes="[0:50] A ten-year sample mean is a noisy estimate, and a "
           "mean-variance optimiser is not a passive reader of its inputs: it "
           "actively hunts for the highest-return assets, so it preferentially "
           "buys whatever the estimation error flattered. It is an error "
           "maximiser. James-Stein shrinkage pulls each estimate toward the "
           "grand mean of the 989 full-history stocks by an amount proportional "
           "to that stock's own standard error. The weight a stock keeps on its "
           "own estimate ranges from 0.03 to 0.70. If asked what we tuned: "
           "nothing — both quantities in that weight are estimated."),

# ============================= C · RISK MODEL =============================
dict(kind="content", stage="RISK MODEL",
     headline="Twenty factors, chosen by measurement, not convention",
     chart=f"{CH}/s07_factor_count.png",
     bullets=["20 is not the smallest k that reaches zero — five is",
              "It is the smallest k whose margin holds either way",
              "At k = 50 the condition number worsens 2,957 → 4,389"],
     sowhat="We chose the smallest factor count whose margin does not depend on "
            "which portfolio you pick.",
     notes="[1:10] We had to choose a factor count, and it is the most "
           "arbitrary-looking parameter in the model, so we measured it. For each "
           "k we compared the predicted risk of every frontier portfolio against "
           "the risk those weights actually realised. One or two factors "
           "understate risk by thirty-eight percent at the minimum-risk point — "
           "that is a cliff, and it is the argument against a single-index model. "
           "Five factors already crosses zero, but by a third of a point, and ten "
           "falls back below zero, which tells us that region is measurement "
           "noise rather than signal. Twenty is the smallest count whose margin "
           "is wide enough that the answer does not depend on which portfolio the "
           "optimiser picks."),

# ============================ D · OPTIMISATION ============================
dict(kind="content", stage="OPTIMISATION",
     headline="A MIQP, because the cheaper formulations failed",
     formula=["minimise    w' Σ w",
              "subject to  w' μ  ≥  β",
              "            Σ w   =  1",
              "            0.01 y_i ≤ w_i ≤ 0.20 y_i",
              "            y_i ∈ {0,1},   Σ y_i ≥ 30"],
     formula_note="1,077 continuous + 1,077 binary variables · ~1.16 M quadratic "
                  "elements · 0.3–1.1 s per solve · FICO Xpress 9.9.1 at a 0.1% "
                  "MIP gap",
     table={"cols": ["Rejected", "The measurement that killed it"],
            "rows": [["Linear risk proxy  Σ wᵢσᵢ",
                      "19.2% more true risk; misreports its own risk by 1.64×"],
                     ["Semi-continuous variables",
                      "returned 26 real positions while reporting 30"],
                     ["Weighted-sum λ scalarisation",
                      "binaries make the set non-convex — reaches only the convex "
                      "hull; native multi-objective turned 0.8 s into >2 min"]],
            "widths": [2.3, 4.4], "hdr_colors": [INK, INK]},
     sowhat="Each rejection is an experiment we ran, not an argument we made.",
     notes="[1:15] The objective is quadratic and the variables include one "
           "binary per stock, and both of those were tested rather than assumed. "
           "A linear risk proxy is tempting because it turns this into a MILP, "
           "but it cannot see correlation — it treats two perfectly correlated "
           "stocks as diversification — and the book it picks carries "
           "nineteen percent more true risk while misreporting itself by a factor "
           "of 1.64. Semi-continuous variables would remove a thousand binaries, "
           "but then nothing counts holdings, and the model reported thirty "
           "positions while holding twenty-six. This slide also answers why there "
           "is no risk-aversion parameter: we sweep the return target instead, "
           "because a weighted sum only reaches the convex hull of a non-convex "
           "frontier."),

dict(kind="content", stage="OPTIMISATION",
     headline="Every constraint carries a price we can quote",
     chart=f"{CH}/s09_constraint_costs.png",
     callout=("Rheinmetall carries an ESG score of 87.3 and would take 10.2% of "
              "the book with no explicit weapons screen.", NEG),
     bullets=["The brief's own averaging rule carries nearly all the cost",
              "The per-stock floor we added is effectively free",
              "The sector cap does not bind at Neutral — 27.10% uncapped"],
     sowhat="We can price any constraint the investment committee wants to "
            "change, in advance.",
     notes="[1:05] Every constraint here has a measured price in percentage "
           "points of expected return at the recommended profile, so if the "
           "investment committee wants to change one we can quote the cost "
           "immediately. Two things to notice. The expensive constraint is the "
           "brief's own weighted-average ESG rule at 0.151 points; our per-stock "
           "floor measures plus 0.008, which is inside the noise — it does not "
           "cost return. And the Rheinmetall figure is the strongest single "
           "illustration that an ESG score measures governance and disclosure "
           "quality, not what a company makes. A well-run munitions manufacturer "
           "scores 87.3. No ESG threshold fixes that, which is why the weapons "
           "screen is explicit and separate."),

# =============================== E · RESULTS ===============================
dict(kind="content", stage="RESULTS", hero=True,
     headline="Fifteen solved portfolios — three are mandates",
     chart=f"{CH}/s10_frontier.png",
     bullets=["Steep on the left, flat on the right",
              "Past roughly 14% risk, extra risk buys very little return"],
     sowhat="That shape is the entire argument for not choosing the right-hand "
            "corner.",
     notes="[1:25] I will pause for a moment and let the shape land. Fifteen "
           "separate MIQP solves, the return target swept between the two "
           "corners. The shape is the argument: steep on the left, flat on the "
           "right, and past roughly fourteen percent volatility extra risk buys "
           "very little extra return. The shaded region on the right is excluded "
           "by a degeneracy test I will explain in two slides. The three marked "
           "points are the mandates we report, and the largest marker is the one "
           "we recommend."),

dict(kind="content", stage="RESULTS",
     headline="Neutral is the best risk-adjusted point on the frontier",
     table={"cols": ["Profile", "Return", "Risk", "Return/Risk", "Holdings", "Weighted ESG"],
            "rows": [["Risk Averse (pt 0)", "9.87%", "9.26%", "1.067", "42", "70.00"],
                     ["Neutral — recommended (pt 8)", "14.30%", "10.62%", "1.346", "30", "70.00"],
                     ["Risk Prone (pt 11)", "15.97%", "12.77%", "1.250", "30", "70.00"]],
            "widths": [2.9, 1.2, 1.1, 1.4, 1.1, 1.5], "hi": 1,
            "hdr_colors": [INK] * 6},
     bignums=[("14.30%", "expected return"), ("10.62%", "risk"),
              ("1.346", "return / risk")],
     bullets=["Risk Averse = minimum variance",
              "Neutral = highest return/risk on the frontier",
              "Risk Prone = highest return among non-degenerate points"],
     sowhat="Neutral needs no risk-aversion parameter — it is the best point on "
            "a frontier we did not tune.",
     notes="[1:05] Three points, three rules, and none of them has a free "
           "parameter. Risk Averse is the global minimum-variance portfolio. "
           "Neutral is the highest return-to-risk ratio on the frontier, which is "
           "why we can recommend it without asking anyone to nominate a risk "
           "aversion coefficient. Risk Prone is the highest return among the "
           "points that pass a degeneracy test. Weighted ESG is exactly seventy "
           "in all three, because that constraint binds everywhere. The "
           "recommendation holds thirty stocks with no position at either the "
           "twenty percent cap or the one percent floor."),

dict(kind="content", stage="RESULTS",
     headline="The maximum-return corner is a dominated portfolio",
     table={"cols": ["Point", "Return", "Risk", "Return/Risk", "Top-3 weight",
                     "At the 1% floor", "Status"],
            "rows": [["11", "15.97%", "12.77%", "1.250", "33.8%", "10", "Risk Prone"],
                     ["12", "16.52%", "14.38%", "1.146", "34.0%", "16", "degenerate — floor count"],
                     ["13", "17.08%", "17.15%", "1.000", "40.5%", "21", "degenerate — both tests"],
                     ["14", "17.63%", "22.62%", "0.779", "60.0%", "23", "degenerate — the corner"]],
            "widths": [0.8, 1.1, 1.0, 1.3, 1.4, 1.5, 2.6], "hi": 0,
            "tint_rows": [1, 2, 3], "hdr_colors": [INK] * 7},
     callout=("0.779 is worse than the risk-averse book's 1.067 — more risk for "
              "less reward per unit.", NEG),
     bullets=["Degenerate: top-3 above 40%, or over 15 positions at the floor",
              "Thresholds swept 9×9: point 11 wins for floors 10–15",
              "More than 15 of 30 is simply more than half the book"],
     sowhat="Maximum return without a degeneracy filter returns a corner of the "
            "feasible set, not a portfolio anyone would sign.",
     notes="[0:50] This slide exists to pre-empt the most likely challenge: why "
           "not report the maximum-return portfolio. Because at point fourteen "
           "sixty percent of the budget sits in three stocks and twenty-three of "
           "thirty positions are pinned at the one percent floor, and its "
           "return-to-risk ratio of 0.779 is worse than the risk-averse book's "
           "1.067. It is a corner of the feasible set. If asked where the "
           "thresholds come from: they were a judgement call originally, so we "
           "swept them on a nine-by-nine grid — point eleven is selected for any "
           "floor threshold between ten and fifteen, and at thirty holdings "
           "fifteen simply means more than half the book at minimum weight."),

dict(kind="content", stage="RESULTS",
     headline="ESG binds everywhere, and the constraints missed Switzerland",
     chart=f"{CH}/s13_esg_switzerland.png",
     bullets=["A region cap cannot see one country",
              "A sector cap cannot see a country spanning two sectors",
              "A 25% cap costs 0.067 pp and removes 11.7 pp of concentration"],
     sowhat="The US exemption is forced, not chosen — with a 25% cap the "
            "infeasibility is exactly 1 − 0.60 − 0.25 = 0.15.",
     notes="[0:45] Two findings on one slide. Weighted ESG sits at exactly "
           "seventy at all fifteen points, so that constraint is always active — "
           "and, as we saw, it is also the expensive one. Then the gap: the brief "
           "caps regions and we capped sectors, and Switzerland slipped between "
           "the two, because it is not a region and it spans two sectors — "
           "cantonal banks and real estate. It reaches forty-seven percent of the "
           "risk-averse book, and Switzerland plus the United States is "
           "ninety-two percent of it. We built a country cap, measured it at "
           "0.067 points of return, and it ships switched off pending your "
           "decision. The US exemption is not a preference: the solver proves it "
           "with an infeasibility of exactly 0.15."),

dict(kind="content", stage="RESULTS",
     headline="Averages hide what the portfolio actually does",
     chart=f"{CH}/s14_capture_underwater.png",
     bullets=[f"Captures {c['up_capture_pct']:.0f}% of up months, "
              f"{c['down_capture_pct']:.0f}% of down months",
              f"Minimum variance stays underwater {uw['minvar']} days vs "
              f"{uw['equal_weight']} for 1/N",
              "The shallower drawdown is also the longer one"],
     sowhat="The capture asymmetry is the strongest argument for the "
            "recommendation, and a Sharpe ratio cannot show it.",
     notes="[0:55] Two things a Sharpe ratio cannot show you. First, capture "
           "asymmetry: the recommended book takes 103% of the benchmark's up "
           "months and only 90% of its down months, over 58 up and 34 down "
           "months. That asymmetry is the real argument for the recommendation. "
           "Second, the cost of the min-variance book's shallower drawdown is "
           "duration — its longest unbroken stretch below peak is 661 trading "
           "days against the benchmark's 396, and after 2022 it took "
           f"{rec22['minvar']['trough_to_recovery_trading_days']} trading days "
           f"from trough to recovery against the benchmark's "
           f"{rec22['equal_weight']['trough_to_recovery_trading_days']}. A note "
           "for the record: the recovery figures circulated in an earlier draft "
           "could not be reproduced, so these are the trough-to-recovery numbers "
           "that do trace."),

# ============================= F · VALIDATION =============================
dict(kind="content", stage="VALIDATION",
     headline="Out of sample: risk edge real, return edge not",
     chart=f"{CH}/s15_equity_curves.png",
     table={"cols": ["Book", "CAGR", "Volatility", "Sharpe", "Max DD"],
            "rows": [["minvar", "10.94%", "13.20%", "0.829", "−33.81%"],
                     ["mandate20  (Neutral stand-in)", "17.60%", "20.08%", "0.876", "−42.31%"],
                     ["mandate10", "21.29%", "23.30%", "0.914", "−46.00%"],
                     ["1/N benchmark", "14.65%", "16.91%", "0.866", "−37.68%"]],
            "widths": [3.2, 1.4, 1.6, 1.2, 1.4], "hi": 1, "hdr_colors": [INK] * 5},
     bullets=["31 rebalances, 3-year rolling window, 7.7 years",
              "Only data available before each date is used",
              "The profile is a relative mandate, comparable across regimes"],
     sowhat="Higher CAGR came with proportionally higher risk — the ranking on "
            "Sharpe barely moves.",
     notes="[1:05] The protocol: a three-year rolling estimation window, "
           "quarterly rebalancing, thirty-one rebalances over 7.7 years, and at "
           "each date only data strictly before it. We express the return-seeking "
           "profile as a relative mandate — give up at most twenty percent of the "
           "achievable maximum — because an absolute return target is not "
           "comparable across regimes; the same target is easy in 2021 and "
           "infeasible in 2018. Read the table across rather than down: the "
           "higher CAGR comes with proportionally higher volatility and a deeper "
           "drawdown, and the Sharpe column barely separates."),

dict(kind="content", stage="VALIDATION",
     headline="Every Sharpe difference sits inside the noise band",
     chart=f"{CH}/s16_significance.png",
     bullets=["After 10 bp of costs the return-seeking book falls below 1/N",
              "0.857 against 0.866, at 170% annual turnover",
              "Jobson-Korkie with Memmel, not a t-test on returns"],
     sowhat="Over 7.7 years the honest answer is that no book is statistically "
            "distinguishable from the benchmark — in either direction.",
     notes="[1:00] This is the slide I would most want you to take away. The "
           "correct test for a difference of Sharpe ratios is Jobson-Korkie with "
           "the Memmel correction, not a t-test on daily return differences, "
           "because Sharpe differences are not normally distributed. It gives z "
           f"of {jk['minvar']['z']:+.2f}, {jk['mandate20']['z']:+.2f} and "
           f"{jk['mandate10']['z']:+.2f}. Every one is inside the band, and the "
           "conclusion is unchanged from the simpler test but no longer "
           "attackable on distributional grounds. Note the direction: this cuts "
           "against our own return-seeking book as much as it cuts against the "
           "claim that the optimiser destroys value. And after ten basis points "
           "of costs that book falls below the benchmark outright."),

dict(kind="content", stage="VALIDATION",
     headline="The expected-return model forecasts backwards",
     chart=f"{CH}/s17_pred_vs_realised.png",
     bullets=[f"Correlation {pv['mandate20']['correlation_predicted_vs_realised']:+.2f} "
              f"over 31 rebalances, p = {pv['mandate20']['p_two_sided']:.3f}",
              f"Predicted {pv['mandate20']['mean_predicted_return_pct']:.1f}%, "
              f"realised {pv['mandate20']['mean_realised_return_pct']:.1f}%",
              f"Minimum variance predicted "
              f"{pv['minvar']['mean_predicted_return_pct']:.1f}%, realised "
              f"{pv['minvar']['mean_realised_return_pct']:.1f}%"],
     sowhat="That is error maximisation made visible, and it is why the edge is "
            "in risk and not in return.",
     notes="[0:55] This is the quantitative evidence behind everything I have "
           "said about the return estimate. At each of thirty-one rebalances the "
           "model states an expected return; here it is against what those exact "
           "weights then earned. The correlation is minus 0.43 with a p-value of "
           "0.016 — not merely uninformative, actively inverted. It predicted an "
           "average of 47.3% and realised 31.5%. The minimum-variance book, which "
           "barely uses the return estimate, predicted 9.7% and realised 15.6% — "
           "it under-promises. The optimiser is an error maximiser and this is "
           "the picture of it."),

dict(kind="content", stage="VALIDATION",
     headline="The crash realised 6.7× the risk we forecast",
     chart=f"{CH}/s18_crisis.png",
     bullets=["Panel A is in-sample, wins 7 of 7 — not evidence",
              "Panel B re-estimates on the three years before each window",
              "Risk Averse wins 3 of 3 crises, Neutral 1 of 3"],
     sowhat="Any risk number this model produces has to be presented as a lower "
            "bound.",
     notes="[0:50] Two panels kept deliberately apart. Panel A holds the "
           "delivered books through the same windows their inputs were estimated "
           "over — it wins seven of seven and we do not present it as evidence, "
           "because the optimiser had already seen those crises. Panel B "
           "re-estimates on the three years strictly before each window and "
           "re-solves. There, minimum variance beats the benchmark in all three "
           "crisis windows and the recommended book in one of three. And the "
           "right-hand panel is the number I would not want extracted from me: "
           "in the COVID crash the recommended construction realised 6.71 times "
           "the risk it had forecast."),

# ================================ G · CLOSE ================================
dict(kind="content", stage="VALIDATION",
     headline="Recommend on the estimate, recommend risk on the evidence",
     columns=[("What we recommend", INK,
               ["Neutral, point 8", "14.30% return at 10.62% risk",
                "ratio 1.346, 30 holdings, ESG exactly 70.00",
                "103% up capture against 90% down"]),
              ("What we can demonstrate", POS,
               ["Volatility 13.20% vs 16.91% — a 21.9% cut",
                "Lower in 5 of 6 sub-periods",
                "Drawdown −33.81% vs −37.68%",
                "Beats 1/N in all three crisis windows",
                "— all at the minimum-variance end"]),
              ("What we cannot claim", NEG,
               ["A statistically significant risk-adjusted edge",
                "Every Jobson-Korkie z inside ±1.96",
                "Over 7.7 years and 31 rebalances",
                "In either direction"])],
     limits=["ESG scores and sectors are a single present-day snapshot — a 2018 "
             "rebalance uses 2025 information",
             "The universe is today's index constituents, so every strategy "
             "including the benchmark looks optimistic",
             "Transaction costs are measured but not priced inside the optimiser"],
     sowhat="The defensible claim is about risk, not return — and stating that is "
            "stronger than a Sharpe ratio that fails a t-test.",
     notes="[1:10] I will state the recommendation conditionally, because the "
           "estimate and the evidence point to different ends of the frontier and "
           "pretending otherwise invites the obvious attack. If you accept mu as "
           "the best available estimate, take Neutral: it is the highest "
           "return-to-risk point on the frontier, it captures more upside than "
           "downside, and the mandate asks for growth. If you weight "
           "out-of-sample evidence above the estimate, take Risk Averse: it beats "
           "the benchmark in every crisis window and cuts volatility by "
           "twenty-two percent. Neither claim extends to a statistically "
           "demonstrable risk-adjusted edge, and there are three limitations this "
           "dataset cannot fix."),

# ============================== BACKUP ==============================
dict(kind="divider", headline="Backup",
     sub="Detail held back for questions",
     notes="[—] Backup slides from here. I will go to these only if asked."),

dict(kind="content", stage=None, backup=True,
     headline="Factor selection, the full table",
     table={"cols": ["k", "Variance explained", "Median R²", "Risk error at min-risk"],
            "rows": [[str(r["k"]), f"{r['variance_explained_pct']:.1f}%",
                      f"{r['median_r2']:.3f}",
                      f"{r['risk_error_at_min_risk_pct']:+.2f}%"]
                     for r in D["risk_model"]["selection_table"]],
            "widths": [1.0, 2.4, 1.8, 2.6], "hi": 4, "hdr_colors": [INK] * 4},
     bullets=["Negative means the model understates portfolio risk",
              "k = 20 is the chosen row",
              "In-sample consistency check, not a forecast test"],
     notes="[—] The full sweep. The error is predicted risk over realised risk "
           "minus one, at the minimum-risk point, and negative means the model "
           "understates. Note that this is an in-sample consistency check: it "
           "asks whether the optimiser can game a covariance that assumes "
           "diagonal residuals, not whether that covariance predicts the future."),

dict(kind="content", stage=None, backup=True,
     headline="The first four factors are economically readable",
     table={"cols": ["Factor", "Variance", "Reading", "Evidence"],
            "rows": [[f["factor"], f"{f['variance_pct']:.1f}%",
                      f["reading"], f["evidence"]]
                     for f in D["risk_model"]["factor_interpretation"]],
            "widths": [1.0, 1.2, 2.6, 4.0], "hdr_colors": [INK] * 4},
     bullets=["Nothing about these was specified in advance",
              "They are eigenvectors of the return covariance",
              "An explicit region factor moved the error 13.6% → 13.1% only"],
     notes="[—] These are principal components, not factors we named in advance. "
           "Factor two is worth the detail: we added an explicit Europe-versus-US "
           "factor as a test and it barely moved the residual correlation, "
           "because PCA had already found that split by itself. The failure was "
           "never which factor is named — it is how much variance is left in the "
           "residual block the model treats as independent."),

dict(kind="content", stage=None, backup=True,
     headline="Shorter estimation windows look better and are worse",
     chart=f"{CH}/b03_windows.png",
     bullets=["10y Jaccard 1.00 by construction; 5y 0.283; 3y 0.193",
              "3y weight correlation with the 10y book: −0.019",
              "μ's range widens from 2.7–19.1% to −9.8–46.1%"],
     notes="[—] The window length is the input this model is least robust to, and "
           "we choose it. Re-estimating mu and sigma on five and three years "
           "makes the book look dramatically better — a ratio of 3.24 on three "
           "years against 1.35 on ten — while sharing only eleven of thirty-eight "
           "names with the ten-year book and a weight correlation of minus 0.019. "
           "That is not an alternative recommendation, it is estimation error."),

dict(kind="content", stage=None, backup=True,
     headline="Why 31 rebalances and not two",
     table={"cols": ["Split", "Book", "Δ Sharpe vs 1/N", "Verdict"],
            "rows": [["2019-12 / 2022-12", "mandate20", "+0.087", "beats 1/N"],
                     ["2020-06 / 2023-06", "mandate20", "−0.244", "loses to 1/N"],
                     ["three-point variant", "mandate20", "−0.130", "loses to 1/N"],
                     ["31 rebalances", "mandate20", "+0.010", "not distinguishable"]],
            "widths": [2.4, 1.8, 2.2, 2.4], "hi": 3, "hdr_colors": [INK] * 4},
     bullets=["A spread of 0.331, decided by where the boundary falls",
              "Two observations cannot separate skill from luck",
              "We tested the objection rather than asserting it"],
     notes="[—] A simpler protocol was proposed: three chunks, two rebalance "
           "points. We declined it on the argument that two out-of-sample "
           "observations cannot separate skill from luck, and then we tested that "
           "argument rather than leaving it as an assertion. The same protocol "
           "with two equally defensible split dates says the book beats the "
           "benchmark on one and loses on the other — a spread of 0.331 from "
           "nothing but the boundary."),

dict(kind="content", stage=None, backup=True,
     headline="Six reproducibility gates, and three defects they caught",
     table={"cols": ["Gate", "Result"],
            "rows": [[g["gate"], g["result"]] for g in D["reproducibility"]["gates"]],
            "widths": [4.0, 4.8], "hdr_colors": [INK] * 2},
     bullets=["A number that cannot be reproduced is not evidence",
              "The deck itself was unbuildable by anyone else at one point",
              "A 1e-6 tolerance counted zero positions where there was one"],
     notes="[—] Every rebuild in this project is gated against something it must "
           "reproduce, and the gates caught three real defects. The deck-building "
           "script read a file from a temporary directory that nothing in the "
           "repository wrote, so it worked on one machine and crashed everywhere "
           "else. Two backtest inputs were read but never written. And counting "
           "positions at the one percent floor with a tolerance of ten to the "
           "minus six reported zero where there was plainly one, because the MIP "
           "gap leaves the smallest holding five parts per million above the "
           "bound."),

dict(kind="content", stage=None, backup=True,
     headline="Weapons screening, and a ticker that would have hidden it",
     bullets=["Tier 1: weapons are the core business — always excluded",
              "Tier 2: diversified defence — a toggle, currently off, costs 0.004 pp",
              "Four of ten Tier 2 tickers were absent from the dataset"],
     callout=("BA.L was the dangerous one. BA.N exists in this dataset and is "
              "Boeing, so a plausible-looking correction would have excluded the "
              "wrong company.", NEG),
     notes="[—] Two tiers, deliberately separated. Tier one is the narrow, "
           "near-consensus case following Norwegian sovereign-fund precedent, and "
           "is always excluded. Tier two is diversified defence, where defence is "
           "a major but not the sole segment — that category is genuinely "
           "contested after 2022, so it is a toggle and we can quote its cost "
           "rather than baking in a judgement. The data defect is worth telling: "
           "four of ten tier-two tickers did not exist in this dataset, so the "
           "screen was silently excluding six of ten."),

dict(kind="content", stage=None, backup=True,
     headline="What the 1/N benchmark is, and is not",
     bullets=["0.093% per name against the brief's 1% floor",
              "Rebalancing frequency moves it 0.9 pp of CAGR",
              "The ESG-screened variant breaks the 60% region cap"],
     callout=("No 1/N variant is admissible under the brief. It is a reference "
              "for what no skill would have earned, not a portfolio we could have "
              "proposed.", INK),
     notes="[—] Worth saying before anyone offers it as an alternative. Equal "
           "weight over 1,077 names puts 0.093 percent in each, against a one "
           "percent floor, and no equal-weight portfolio over more than a hundred "
           "names can satisfy that floor at all. The unscreened variants also "
           "miss weighted ESG of seventy. And the ESG-screened variant clears ESG "
           "and then breaks the region cap, because the high-ESG half of this "
           "universe is sixty-three percent European. Also: the choice of "
           "rebalancing frequency moves the benchmark by nine tenths of a point "
           "of CAGR, which is larger than most differences we report against it."),

dict(kind="content", stage=None, backup=True,
     headline="The sub-period record across six regimes",
     table={"cols": ["Period", "Regime", "minvar CAGR", "1/N CAGR",
                     "minvar vol", "1/N vol"],
            "rows": None,  # filled by the renderer from the CSV
            "csv": "backtest_profiles/results/subperiods.csv",
            "widths": [1.8, 1.9, 1.5, 1.3, 1.4, 1.2], "hdr_colors": [INK] * 6},
     bullets=["Volatility lower in 5 of 6 sub-periods",
              "It wins the 2020 crash and the 2022 inflation shock",
              "It gives up the 2021 boom and the AI rally"],
     notes="[—] The volatility edge is not an artefact of one period. Minimum "
           "variance realises lower volatility in five of the six regimes, and "
           "the two it wins outright on return are the two drawdowns. What it "
           "gives up is the boom and the AI rally, which is exactly what a "
           "low-volatility book should do."),

dict(kind="content", stage=None, backup=True,
     headline="Tail risk, where the minimum-variance book earns its keep",
     chart=f"{CH}/b09_tail.png",
     bullets=[f"CVaR 95 of {tail['minvar']['cvar95_pct']:.2f}% against "
              f"{tail['equal_weight']['cvar95_pct']:.2f}% for 1/N",
              "The mean of the worst 5% of days",
              "The return-seeking books are worse than the benchmark"],
     notes="[—] Conditional value at risk is the mean of the worst five percent "
           "of days, and it is the statistic a mandate holder actually feels. "
           "Minimum variance loses 1.75 percent on such a day against the "
           "benchmark's 2.51. Both return-seeking books are worse than the "
           "benchmark on this measure, which is the same story as the drawdown "
           "column but in the tail rather than the peak-to-trough."),
]

MAIN_COUNT = sum(1 for s in SLIDES if not s.get("backup") and s.get("kind") != "divider")
BACKUP_COUNT = sum(1 for s in SLIDES if s.get("backup"))

if __name__ == "__main__":
    print(f"slides defined: {len(SLIDES)}  (main {MAIN_COUNT}, divider 1, "
          f"backup {BACKUP_COUNT})")
    for i, s in enumerate(SLIDES, 1):
        tag = "BACKUP" if s.get("backup") else s.get("kind", "content").upper()[:7]
        nb = len(s.get("bullets") or [])
        long = [b for b in (s.get("bullets") or []) if len(b.split()) > 12]
        hl = len(s["headline"].split())
        flags = []
        if nb > 3: flags.append(f"{nb} BULLETS")
        if long: flags.append(f"{len(long)} LONG BULLET(S)")
        if hl > 10 and s.get("kind") == "content": flags.append(f"HEADLINE {hl} WORDS")
        print(f"  {i:2d} {tag:8s} {s['headline'][:52]:52s} {' '.join(flags)}")
