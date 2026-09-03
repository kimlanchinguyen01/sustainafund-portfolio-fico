# BRIEF — Build a 20-minute presentation deck: "SustainaFund"

You are building the final presentation for a graduate-level portfolio-optimisation case study, to be
delivered live in **20 minutes** to finance faculty and FICO Xpress practitioners at the HTW Berlin
Summer School 2026. The audience is technical: they will ask *why* every choice was made.

Attached with this brief:

- `data/deck_data.json` — **every verified figure**, structured. This is the single source of truth.
- `data/equity_curves_monthly.csv` — month-end equity curves, 4 books, 2018-04 → 2025-12 (94 rows).
- `data/backtest_summary.csv`, `data/backtest_subperiods.csv`, `data/backtest_diagnostics.csv`
- `data/crisis_panelB_windows.csv`, `data/crisis_panelA_windows.csv`, `data/crisis_drawdown_attribution.csv`
- `data/option_b_comparison.csv`

---

## 0 — What to deliver

1. `SustainaFund_final.pptx` — 16:9, **19 main slides + 8 backup slides** (backup after a divider).
2. `SustainaFund_final.pdf` — same deck exported to PDF.
3. Speaker notes filled in on every slide via `python-pptx` `slide.notes_slide` (3–5 sentences of talk
   track per slide, written in the first person plural: "we measured…", "we rejected…").
4. `charts/` — every chart also saved as a standalone 300 dpi PNG, so single charts can be reused.

---

## 1 — Hard rules (these override anything else)

1. **Never invent a number.** Every figure on every slide must come from `deck_data.json` or the
   attached CSVs. If a slide idea needs a number that is not there, drop that element and leave a
   short note in the speaker notes saying what was missing. Do not estimate, do not interpolate a
   value and print it, do not "reconstruct" a plausible distribution.
2. **One idea per slide.** Each slide has exactly one assertion. Never more than **3 bullets**, never
   more than **12 words per bullet**. No slide with 5–10 bullets. If content does not fit, it belongs
   in the speaker notes or a backup slide.
3. **Assertion headlines.** Every headline is a complete claim, not a label. Write
   "Currency is a risk factor, not a unit conversion", never "FX methodology". Max 10 words.
4. **The visual is the argument.** Each main slide is built around one chart, one table or one
   big-number row occupying **at least 55%** of the slide area. Text supports the visual, not the
   reverse.
5. **Every methodology choice arrives with the number that justified it.** This deck's purpose is to
   pre-empt questions: whenever a choice is stated, the measurement that decided it appears on the
   same slide. This is the single most important editorial rule here.
6. **Percentages:** returns and risks to 2 decimals (14.30%), ratios to 3 (1.346), percentage-point
   differences with the "pp" suffix (0.151 pp). Never mix pp and % in one sentence without the suffix.
7. **British/neutral English, no emoji, no clipart, no stock photography, no 3D, no gradients, no
   drop shadows.**

---

## 2 — Tooling

- Build with **`python-pptx`**; render every chart with **matplotlib** to PNG at **300 dpi** and place
  the PNG on the slide. Do not use PowerPoint native charts.
- Figure sizes must match their placeholder box exactly (set `figsize` in inches to the box size) so
  nothing is rescaled and no text is blurred or distorted.
- Save charts with `bbox_inches="tight", pad_inches=0.02, transparent=False,
  facecolor=BACKGROUND`.
- Export PDF with `libreoffice --headless --convert-to pdf`. Verify the PDF has the same page count
  as the deck has slides.
- Slide size: `Inches(13.333) x Inches(7.5)`.

---

## 3 — Design system

**Canvas**

| Token | Value | Use |
|---|---|---|
| background | `#FBFAF7` | slide and chart background |
| ink | `#12283F` | headlines |
| body | `#33475B` | body text, table text |
| muted | `#7C8B99` | captions, axis labels, footnotes |
| rule | `#DDE3E8` | hairlines, table borders, gridlines |

**Series colours — use these consistently in every chart**

| Series | Hex | Notes |
|---|---|---|
| Risk Averse / minimum variance | `#3E7C8C` | teal |
| **Neutral (recommended)** | `#12283F` | deep navy — the hero series, always the strongest line |
| Risk Prone | `#C08A2E` | amber |
| 1/N benchmark | `#A0A8AE` | grey, **dashed**, always visually subordinate |
| mandate10 (backtest only) | `#8FA9B5` | pale teal |
| degenerate zone fill | `#F1E9DA` | 55% alpha |
| negative / warning | `#A63A2E` | |
| positive | `#4B7F52` | |

**Type**

- Family: `Inter`, falling back to `Source Sans 3`, `Helvetica Neue`, `Arial`.
- Headline 30 pt bold, ink. Sub-headline 15 pt, muted. Body 15 pt. Table 13 pt. Chart labels 11 pt.
  Big-number callouts 46 pt bold. Nothing below 11 pt anywhere.
- Numbers use tabular/lining figures wherever the font allows.

**Slide furniture**

- **Progress ribbon**, top-right of every content slide: `MANDATE · DATA · RISK MODEL · OPTIMISATION ·
  RESULTS · VALIDATION` in 9 pt small caps, current stage in ink, others in `rule` colour.
- **"So what" strip**, bottom of every content slide: a single sentence in 14 pt italic on a
  `#F1EEE8` band, 0.55 in tall, full width. This is the line the presenter says out loud to close the
  slide. Text for each is given below.
- Slide number bottom-right, 10 pt muted. No company logos unless supplied.

**Chart style (apply to all)**

- No top or right spine. Horizontal gridlines only, `#E6E9EC`, 0.8 pt, behind the data.
- **Direct labelling instead of legends** wherever there are ≤4 series — put the series name at the
  end of its line/bar in the series colour.
- Annotate the numbers that matter directly on the chart. A reader must not have to consult an axis
  to get the headline figure.
- Axis labels sentence case, units stated once ("annualised volatility, %").

---

## 4 — Slide-by-slide specification

Timings are the presenter's plan; put them in the speaker notes as `[0:45]` etc.

---

### S1 · Title — 15 s
**Title:** SustainaFund
**Subtitle:** A $100 million ESG-constrained equity portfolio — efficient frontier, three mandates, and what survived out-of-sample testing
**Meta line:** HTW Berlin Summer School 2026 · FICO Xpress case study · [Presenter name] · September 2026
**Visual:** the efficient-frontier curve drawn very faintly (`#12283F` at 12% alpha, 2 pt) across the
lower third as a background element. No so-what strip on this slide.

---

### S2 · The mandate — 1 min 15 s
**Headline:** The deliverable is a frontier, not a single portfolio
**Left (55%):** two-column constraint table.

| Given by the brief | Added by us |
|---|---|
| 1% ≤ weight ≤ 20% per stock | Sector cap 30% |
| Each region ≤ 60% | Per-stock ESG floor ≥ 30 |
| At least 30 holdings | Tier 1 weapons exclusion (always on) |
| Weighted-average ESG ≥ 70 | Tier 2 weapons exclusion (toggle, off) |
| | Country cap 25% (built, measured, ships off) |

Colour the two columns differently (`ink` header vs `#C08A2E` header) so "given" and "added" are
instantly separable — the audience will ask which is which.

**Right (45%):** three big numbers stacked — `$100M` budget · `1,077` investable stocks · `15` frontier points.
**So what:** "Risk appetite was never given to us, so we report the frontier and three mandates on it."

---

### S3 · Data funnel — 45 s
**Headline:** 1,093 tickers in, 1,077 investable out
**Visual:** horizontal waterfall/funnel, four stages, values from `universe`:
`1,093 raw` → `−6 no total-return series` → `−10 below the ESG floor` → `1,077 optimisable`.
Bars in `ink`, deductions in `#A63A2E`, final bar in `#3E7C8C`.
**Bullets (3 max):** 10 years of daily LSEG data · converted to USD at ECB rates · total-return, not price.
**So what:** "Every exclusion is a written rule applied to all names, not a judgement about a company."

---

### S4 · FX — 45 s
**Headline:** Currency is a risk factor, not a unit conversion
**Visual — two panels side by side:**
- *Left:* a 2-bar comparison, **identical weights** priced two ways — local currency `8.04%` vs USD
  `8.99%` volatility. Annotate the gap. Caption under: "same portfolio, two measuring sticks".
- *Right:* a single "understatement" bar pair — predicted `8.46%` vs true `10.13%` for the
  minimum-variance book, annotated **"understated by 19.7%"** in `#A63A2E`.
- Below both, one callout box: **"FX is 17.6% of total portfolio variance"**.

**Bullets:** `ln(P_usd) = ln(P_local) + ln(fx)` — the FX term does not cancel · a fund reports in one currency.
**So what:** "Optimising on local-currency returns optimises a return no investor ever receives."

---

### S5 · Dividends — 40 s
**Headline:** Price returns systematically penalise the stocks min-variance wants
**Visual:** two elements.
- A before/after marker pair for the **median expected return**: `7.80%` → `10.39%`, drawn as a
  dumbbell with an arrow.
- A small horizontal bar chart of sector uplift: Energy `+3.89 pp` … Technology `+1.18 pp`
  (only these two values are known — label them and draw the two bars only; **do not invent
  intermediate sectors**).
**Bullets:** stocks with negative expected return: 3 → 0 · ranking correlation 0.972 — levels move, order mostly holds · we validated the vendor series with 3 checks.
**So what:** "We tested the adjusted series rather than trusting it: ratio anchored at 1.00, volatility unchanged, uplift ordered by dividend yield."

---

### S6 · Expected returns — 50 s
**Headline:** A 62.6% historical mean is not a forecast
**Visual — a single horizontal number line**, 0% to 65%, showing:
- the shrunk-μ band `2.7% – 19.1%` as a filled bar in `#3E7C8C`,
- the shrink target `10.44%` as a vertical marker labelled "grand mean of 989 full-history stocks",
- a curved arrow from `62.63%` (raw, far right, in `#A63A2E`) down to `17.63%` (shrunk), labelled
  "the most extreme estimate".
**This is the only honest chart here — do NOT draw a scatter of all 1,077 stocks; those values are not
in the data bundle.**
**Bullets:** `w_i = τ²/(τ² + se_i²)` · both τ² and se² estimated from the data · no tuning parameter to defend.
**So what:** "The amount of shrinkage is measured, not chosen — there is no knob for a referee to attack."

---

### S7 · Factor count — 1 min 15 s  *(RESULTS-CRITICAL, do not cut)*
**Headline:** Twenty factors, chosen by measurement, not by convention
**Visual:** combination chart from `risk_model.selection_table`, x-axis = k (1, 2, 5, 10, 20, 30, 50,
plotted on a categorical axis so spacing is even):
- **Bars** = risk error at the minimum-risk point (%), diverging around a bold zero line; negative
  bars `#A63A2E`, positive bars `#3E7C8C`, **k = 20 bar in `#12283F` with a "CHOSEN" tag**.
- **Line on a secondary axis** = variance explained (%), thin, `#7C8B99`.
- Annotate directly: `k=5 → +0.31` and `k=10 → −1.56` with a small bracket labelled
  "not monotone — this region is measurement noise".
**Bullets:** 20 is not the smallest k that reaches zero · it is the smallest k with a margin that holds · at k=50 the condition number worsens 2,957 → 4,389.
**So what:** "We chose the smallest factor count whose margin does not depend on which portfolio you pick."

---

### S8 · Factor interpretation — 1 min 15 s  *(CUTTABLE to backup if rehearsal overruns)*
**Headline:** The first four factors are economically readable
**Visual:** horizontal bar chart, F1–F4, bar length = variance explained
(27.8 / 7.5 / 3.4 / 2.4 %), each bar labelled at its end with the reading and the evidence:
- F1 — broad market · correlation 0.996 with the equally weighted index
- F2 — Europe vs United States · β +1.43 / −1.73
- F3 — Energy vs Technology · β −2.76 / +1.75
- F4 — Technology vs Utilities · β −1.47 / +2.94
**Bullets:** we added an explicit Europe/US factor as a test · residual correlation barely moved, 13.6% → 13.1% · PCA had already found that split at F2.
**So what:** "The open question is not naming factors 5 to 20 — it is the variance left in the residual that the model treats as independent."

---

### S9 · Model form — 1 min 15 s
**Headline:** A MIQP, because the cheaper formulations were measured and failed
**Left (45%):** the formulation, set in a monospace block on a `#F4F2ED` panel:

```
minimise    w' Σ w
subject to  w' μ  ≥  β
            Σ w   =  1
            0.01 y_i ≤ w_i ≤ 0.20 y_i
            y_i ∈ {0,1},   Σ y_i ≥ 30
```
Under it, in muted 12 pt: 1,077 continuous + 1,077 binary variables · ~1.16 M quadratic elements ·
0.3–1.1 s per solve · FICO Xpress 9.9.1 at a 0.1% MIP gap.

**Right (55%):** three rejected alternatives, each as a row: name — **the number that killed it**.

| Rejected | Measured outcome |
|---|---|
| Linear risk proxy `Σ w_i σ_i` | carries **19.2% more true risk**, and misreports its own risk by **1.64×** |
| Semi-continuous variables | returned **26 real positions while reporting 30** |
| Weighted-sum λ scalarisation | binaries make the feasible set non-convex — reaches only the convex hull; Xpress's native multi-objective turned a 0.8 s MIQP into an MIQCP that **did not finish in 2 minutes** |

**So what:** "Each rejection is an experiment we ran, not an argument we made."

---

### S10 · Constraint costs — 1 min 15 s
**Headline:** Every constraint carries a price we can quote
**Visual:** horizontal bar chart, cost in pp of expected return at the Neutral profile, sorted
descending. Use exactly these five bars (values from `constraints`):

| Constraint | pp | Colour |
|---|---|---|
| Weighted-average ESG ≥ 70 (given by the brief) | 0.151 | `#12283F` |
| Country cap 25% *(built, ships OFF)* | 0.067 | `#C08A2E`, **hatched** to mark "not active" |
| Sector cap 30% | 0.020 | `#3E7C8C` |
| ESG floor ≥ 30 per stock | 0.008 | `#3E7C8C`, label it **"+0.008 — no cost"** |
| Tier 2 weapons exclusion *(toggle, OFF)* | 0.004 | `#C08A2E`, hatched |

Annotate every bar with its value. Add a note under the axis: "country-cap figure is return given up at
matched risk; the same cap costs 0.112 pp of risk at matched return."

**Important on the ESG-floor bar:** the measured effect is *+*0.008 pp — the floor does **not** cost
return, the figure is inside the noise. Label it so no one reads it as a cost.

**Bullets:** the brief's own averaging constraint carries nearly all the ESG cost · the floor we added is effectively free · the sector cap does not bind at Neutral (uncapped top sector 27.10%).
**So what:** "We can price any constraint the investment committee wants to change, in advance."

---

### S11 · The efficient frontier — 1 min 30 s  ★ HERO SLIDE
**Headline:** Fifteen solved portfolios — three are mandates, three are degenerate
**Visual:** full-width scatter/line, x = annualised volatility (9% → 24%), y = expected return (9% → 18%).
- Plot **only the six exact points** in `frontier.KNOWN_POINTS_EXACT` as markers; connect all fifteen
  with a smooth monotone interpolating curve (`PCHIP`) so the shape is right, but **label only the six**.
  Add a 9 pt muted footnote: "curve interpolated between solved points for shape".
- Shade the region right of ~13.5% volatility in `#F1E9DA` and label it `DEGENERATE — points 12–14 excluded`.
- Mark and label: `Risk Averse · pt 0` (`#3E7C8C`), `Neutral · pt 8 — recommended` (`#12283F`, largest
  marker), `Risk Prone · pt 11` (`#C08A2E`).
**Bullets:** steep on the left, flat on the right · past roughly 14% risk, extra risk buys very little extra return.
**So what:** "That shape is the entire argument for not choosing the right-hand corner."

---

### S12 · The three portfolios — 1 min 15 s
**Headline:** Neutral is the best risk-adjusted point, and it required no preference parameter
**Visual:** the delivered-portfolios table, Neutral row highlighted with a `#EDF0F3` fill.

| Profile | Return | Risk | Return/Risk | Holdings | Weighted ESG |
|---|---|---|---|---|---|
| Risk Averse (pt 0) | 9.87% | 9.26% | 1.067 | 42 | 70.00 |
| **Neutral — recommended (pt 8)** | **14.30%** | **10.62%** | **1.346** | 30 | 70.00 |
| Risk Prone (pt 11) | 15.97% | 12.77% | 1.250 | 30 | 70.00 |

Above the table, three big-number callouts for the recommendation: `14.30%` return · `10.62%` risk ·
`1.346` return/risk.
**Bullets:** Risk Averse = minimum variance · Neutral = highest return/risk on the frontier · Risk Prone = highest return among non-degenerate points.
**So what:** "Neutral needs no risk-aversion parameter — it is the best point on a frontier we did not tune."

---

### S13 · Why point 11, not point 14 — 1 min  *(pre-empts the most likely challenge)*
**Headline:** The maximum-return corner is a dominated portfolio
**Visual:** four-row table, points 11–14, with the ratio column emphasised and rows 12–14 tinted
`#F1E9DA`:

| Point | Return | Risk | Return/Risk | Top-3 weight | At the 1% floor | Status |
|---|---|---|---|---|---|---|
| **11** | 15.97% | 12.77% | **1.250** | 33.8% | 10 | **Risk Prone** |
| 12 | 16.52% | 14.38% | 1.146 | 34.0% | 16 | degenerate — floor count |
| 13 | 17.08% | 17.15% | 1.000 | 40.5% | 21 | degenerate — both tests |
| 14 | 17.63% | 22.62% | **0.779** | 60.0% | 23 | degenerate — the corner |

Add a red callout: **"0.779 is worse than the risk-averse book's 1.067"**.
**Bullets:** degenerate = top-3 above 40% of budget, or more than 15 positions at the 1% floor · thresholds swept on a 9×9 grid: point 11 is selected for any floor threshold from 10 to 15 · "more than 15 of 30" simply means more than half the book sitting at the minimum weight.
**So what:** "Maximum return without a degeneracy filter returns a corner of the feasible set, not a portfolio anyone would sign."

---

### S14 · ESG — 50 s
**Headline:** The ESG constraint is active at every point on the frontier
**Visual — two elements:**
- *Left:* a small chart or strip showing weighted ESG = **70.00 at all 15 frontier points** — draw a
  flat line pinned exactly on 70 against a y-axis running 60–80, which makes "always binding" visible
  at a glance.
- *Right:* the cost decomposition as two stacked bars — weighted-average requirement **0.151 pp** vs
  per-stock floor **0.008 pp** — plus the floor-sensitivity row underneath:
  floor 20 / 30 / 40 → 14.299% / 14.300% / 14.305%.
- Beneath, a bordered callout in `#A63A2E`: **"Rheinmetall carries an ESG score of 87.3 and would take
  10.2% of the book with no explicit weapons screen."**
**Bullets:** the brief's averaging rule carries the whole cost · our per-stock floor is nearly free · the floor level is not load-bearing.
**So what:** "An ESG rating measures governance and disclosure, not what a company makes — no threshold fixes that."

---

### S15 · Concentration — 55 s
**Headline:** The constraints we were given could not see Switzerland
**Visual:** a horizontal bar showing **Switzerland = 46.98%** of the risk-averse book against the
25% cap line (drawn as a dashed vertical rule in `#A63A2E`), plus a second bar
**Switzerland + United States = 92.2%**.
**Bullets:** a region cap cannot see one country · a sector cap cannot see a country spanning two sectors — Swiss cantonal banks and Swiss real estate · a 25% cap costs 0.067 pp of return and removes 11.7 pp of Swiss concentration.
**So what:** "The US exemption is forced, not chosen — with a 25% cap the infeasibility is exactly 1 − 0.60 − 0.25 = 0.15."

---

### S16 · Walk-forward backtest — 1 min 10 s
**Headline:** Out of sample the risk edge is real; the return edge is not
**Visual:** equity curves from `equity_curves_monthly.csv`, 2018-04 → 2025-12, **log-scaled y-axis**,
four series, direct-labelled at the right end:
`mandate10` (pale teal) · `mandate20` (navy — this is the Neutral stand-in) · `equal_weight` (grey dashed) ·
`minvar` (teal). Shade 2020-02→2020-03 and 2022-01→2022-10 very lightly (`#F1E9DA`) and label them
"COVID" and "2022".
**Strip table under the chart** (4 columns, from `backtest.headline`):

| Book | CAGR | Vol | Sharpe | Max DD |
|---|---|---|---|---|
| minvar | 10.94% | 13.20% | 0.829 | −33.81% |
| mandate20 | 17.60% | 20.08% | 0.876 | −42.31% |
| mandate10 | 21.29% | 23.30% | 0.914 | −46.00% |
| 1/N | 14.65% | 16.91% | 0.866 | −37.68% |

**Bullets:** 31 rebalances, 3-year rolling window, 7.7 years · the profile is a *relative* mandate, because an absolute return target is not comparable across regimes.
**So what:** "Higher CAGR came with proportionally higher risk — the ranking on Sharpe barely moves."

---

### S17 · Statistical significance — 1 min  ★ THE CRITICAL-THINKING SLIDE
**Headline:** Every Sharpe difference sits inside the noise band
**Visual:** a dot plot. y-axis = the three books; x-axis = t-statistic of the daily return difference
against 1/N, running −3 to +3. Shade the band **−1.96 to +1.96** in `#F1E9DA` and label it
"not distinguishable from the benchmark". Plot:
`minvar t = −0.87 (ΔSharpe −0.038)` · `mandate20 t = +0.60 (ΔSharpe +0.010)` ·
`mandate10 t = +1.12 (ΔSharpe +0.047)`. Every point falls inside the band — that is the whole message.
**Bullets:** after 10 bp of costs the return-seeking book falls **below** 1/N — 0.857 vs 0.866 · it turns over 170% a year against minimum variance's 83%.
**So what:** "Over 7.7 years the honest answer is that no book is statistically distinguishable from the naive benchmark — in either direction."

---

### S18 · Crisis stress test — 50 s
**Headline:** In the crash the model realised 6.7× the risk it had forecast
**Visual — two panels:**
- *Left:* grouped bars, point-in-time (Panel B) returns by window, three series — Risk Averse
  (`#3E7C8C`), Neutral (`#12283F`), 1/N (`#A0A8AE` hatched). Windows and values from
  `crisis_stress_test.panel_b_results_pct`: 2018 Q4 · COVID crash · 2022. *(Use the three crisis
  windows only; the "2020 crash + recovery" row is a different hold length on the same decision —
  keep it for the backup slide.)*
- *Right:* bars of realised ÷ predicted risk for the Neutral book: 2018 Q4 `1.83×`, COVID `6.71×`,
  crash+recovery `4.18×`, 2022 `1.44×`. Draw a reference line at 1.0×. COVID bar in `#A63A2E`.
**Bullets:** Panel A holds the delivered books through the same windows they were estimated over — in-sample, 7 of 7, **not evidence** · Panel B re-estimates on the three years strictly before each window · Risk Averse beats 1/N in 3 of 3, Neutral in 1 of 3.
**So what:** "Any risk number this model produces has to be presented as a lower bound."

---

### S19 · Recommendation and limits — 1 min
**Headline:** Recommend Neutral on the estimate; recommend risk reduction on the evidence
**Visual:** three columns, equal width, each with a coloured rule above it.

| What we recommend (`#12283F`) | What we can demonstrate (`#4B7F52`) | What we cannot claim (`#A63A2E`) |
|---|---|---|
| Neutral, point 8 — 14.30% return at 10.62% risk, ratio 1.346, 30 holdings, ESG exactly 70.00 | Volatility 13.20% vs 16.91% for 1/N (−21.9%), lower in 5 of 6 sub-periods; drawdown −33.81% vs −37.68%; beats 1/N in all three crisis windows — **all at the minimum-variance end** | A statistically significant risk-adjusted edge: every t-statistic is inside ±1.96 over 7.7 years |

Bottom band, 3 short limitation lines in muted 13 pt: ESG scores and sectors are a single present-day
snapshot (look-ahead) · the universe is today's index constituents (survivorship bias) · transaction
costs are measured but not priced inside the optimiser.
**So what:** "The defensible claim is about risk, not return — and stating that is stronger than a Sharpe ratio that fails a t-test."

---

## 5 — Backup slides (after a plain divider slide reading "Backup")

Same design system, denser tables are acceptable here.

- **B1 — Factor selection, full table.** All seven rows of `risk_model.selection_table`.
- **B2 — Estimation-window instability.** 10 / 5 / 3-year table (14.30-10.63-1.35 / 17.47-9.32-1.87 /
  25.73-7.93-3.24), Jaccard 0.283, weight correlation −0.019, plus the line "shorter windows look
  better and are worse".
- **B3 — The two-rebalance protocol contradicts itself.** From `option_b_comparison.csv`: the
  mandate20 book records ΔSharpe **+0.087 ("beats 1/N")** with the 2019-12 / 2022-12 split and
  **−0.244 ("loses to 1/N")** with the 2020-06 / 2023-06 split — a spread of 0.331 — while a
  three-point variant gives −0.130. The 31-rebalance answer is +0.010.
- **B4 — Sub-period record.** The six-regime table from `backtest_subperiods.csv`, with the
  `mandate20_vs_eq_vol_%` column, and minvar volatility highlighted where it is below 1/N.
- **B5 — Reproducibility gates and the three defects they caught.** Table of gates and results, then
  the three defects (the `/tmp` JSON, the two unwritten inputs, the 1e-6 → 1e-5 tolerance bug).
- **B6 — Weapons screening.** Tier 1 vs Tier 2, the Rheinmetall figure, and the data defect: four of
  ten Tier-2 tickers absent, and `BA.L` (BAE Systems) versus `BA.N`, which exists in the dataset and
  is Boeing.
- **B7 — What the 1/N benchmark is and is not.** 0.093% per name against a 1% floor; rebalancing
  moves it 0.9 pp of CAGR; the ESG-screened variant breaks the region cap because the high-ESG half
  of the universe is 63% European.
- **B8 — Full crisis table.** All four Panel B windows, all four books, from
  `crisis_panelB_windows.csv`.

---

## 6 — Speaker notes

For each slide write 3–5 sentences the presenter can read aloud, in this shape:
one sentence stating the claim, one or two giving the number that supports it, one anticipating the
obvious question and answering it. Start each note with the timing marker, e.g. `[1:15]`.

Example, S7: `[1:15] We had to choose a factor count, and it is the most arbitrary-looking parameter in
the model, so we measured it rather than picking a convention. We compared predicted against realised
risk at the minimum-risk point for k of 1, 2, 5, 10, 20, 30 and 50. Five factors already crosses zero,
but the margin is thin and it is not monotone — ten factors falls back below zero — which tells us that
region is measurement noise rather than signal. Twenty is the smallest count whose margin is wide
enough that the answer does not depend on which portfolio you pick. If asked why not fifty: the error
grows to nearly six percent and the condition number worsens from 2,957 to 4,389.`

---

## 7 — Quality checklist before you deliver

Run through this explicitly and report the result:

1. Every number on every slide traced to `deck_data.json` or an attached CSV — **list any figure you
   could not trace, and remove it**.
2. No slide has more than 3 bullets or a bullet longer than 12 words.
3. Every headline is an assertion, ≤ 10 words.
4. Series colours are consistent across all charts (Neutral is always the navy hero).
5. All 19 main slides carry a "so what" strip; the title slide does not.
6. Speaker notes present on all 27 slides, each starting with a timing marker.
7. Timings in the notes sum to ≈ 19 minutes for the main deck.
8. The PDF renders with no clipped text and the same page count as the slide count.
9. No chart uses a legend where direct labelling was possible.
10. Nowhere in the deck do the numbers `16.6%` or `38.8%` appear — they are stale figures from an
    earlier data generation. Likewise Risk Prone is **point 11, 15.97% / 12.77% / ratio 1.250** —
    never point 14's 17.63% / 22.62%.
