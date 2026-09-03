# Likely questions, and answers

Every figure below is reproducible from a named script. Where we are weak, the
answer concedes it first — that is what makes the rest credible.

---

## A. The model

**Q1. Why a quadratic model? The brief allowed a linear risk measure, which would have solved faster.**

We built both and compared them under an identical constraint set — asserted, not
assumed: the same problem builder given the quadratic objective reproduces the
MIQP solution to `max|dw| = 0.00e+00`.

At the same expected return the linear model carries **19.2% more true risk**.
Two reasons. First, `Σ wᵢσᵢ` is the risk you would bear if every pair of stocks
moved together, so it is blind to diversification — swapping a stock for another
of equal volatility never changes it. Second, it always holds exactly the
30-stock minimum, because adding a 31st cannot improve its objective, while the
quadratic model voluntarily holds up to 47.

The clearest single number: for the linear model's own portfolio its objective
reads 21.95% while that portfolio's actual volatility is 13.42%. That **1.64×
gap is the diversification it cannot see**.

**Q2. Why binary variables? Xpress has semi-continuous variables for exactly this pattern.**

It does, and they express "zero or in [1%, 20%]" natively. But they cannot be
counted, and the brief requires at least 30 holdings. We tested it: dropping the
`wᵢ ≥ 0.01·yᵢ` link and relying on semi-continuous alone makes `Σyᵢ ≥ 30`
vacuous — the solver sets thirty binaries to one while only **26 positions
actually carry weight**, and reports a lower risk it has not earned. So the
binaries are required, not a workaround.

**Q3. How do you know your covariance matrix is valid?**

Positive semi-definite **by construction**, not by luck: `Σ = B F Bᵀ + D` with `F`
a factor covariance and `D` a non-negative diagonal. Condition number 3,672
against 13,245 for the complete-case sample estimator we started from. It also
reproduces that earlier matrix where they overlap — off-diagonal correlation
0.982, per-stock volatility correlation 1.000 — so it is not a different answer,
it is the same answer extended to every stock.

---

## B. The data

**Q4. You converted everything to USD. But we work with returns, and a return is a ratio — currency should cancel.**

Half right, and it is the important half: price *levels* cancel exactly. Quoting
Unilever in pence and Apple in dollars changes nothing, which is why the original
pipeline was not broken.

But `ln(P_usd) = ln(P_local) + ln(fx)`, so the FX *return* is an additive term
that survives the move to returns. A local-currency return is what a domestic
investor earns; this fund holds USD.

Tested model-free, with no covariance model involved: the same frozen holdings
realised **8.04% volatility measured in local currency and 8.99% in USD**. The
identity `var(local) + 2cov + var(fx) = var(USD)` holds to 2.4e-17, and `var(fx)`
is **17.6% of total USD variance**. On expected return the effect is under
±0.3pp because European currencies moved in opposite directions and offset —
which is precisely why the omission was invisible until we looked at risk.

**Q5. Why dividend-adjusted prices?**

Because a closing price omits dividends, and that understates exactly the
high-yield, low-volatility names a minimum-variance book is made of. Median
expected return rises from **7.80% to 10.39%**.

The check that the data is genuine rather than mis-scaled: the increase is
ordered by dividend yield across sectors — Energy +3.89pp, Utilities +3.66,
Financials +3.36, Real Estate +3.31, down to Technology +1.18 — and volatility
is unchanged at 31.05%. Dividends add drift, not noise.

**Q6. Why 20 factors? That looks like an arbitrary number.**

It was chosen against a criterion, and the criterion is whether the model
understates portfolio risk. The result is a cliff rather than a gradient:

| Factors | Mean risk error | At the min-risk end |
|---|---|---|
| 1 | −18.1% | **−39.9%** |
| 2 | −17.6% | −39.5% |
| 5 | +3.9% | −0.8% |
| **20** | **+7.7%** | **+1.5%** |
| 50 | +10.8% | +6.3% |

One or two factors understate risk by 18–40%. Twenty is the **smallest count
with no understatement anywhere on the frontier**. Fifty overstates by 10.8%,
which is wasted return. For a risk-averse mandate, understating risk is the one
failure mode that cannot be tolerated, so the sign matters more than the size.

**Q7. Your complete-history rule excluded 96 stocks. Doesn't that bias the universe?**

It did, and a teammate caught it. The fix is a factor model: betas are fitted on
whatever days each stock has, so no pair needs a shared history, and **all 1,087
stocks are retained**. The recovered names are not decoration — they take
**11.2% of capital** at the minimum-risk end.

We did not fix it by shortening the estimation window, which was the obvious
move: on three years the frontier's maximum return inflates to 85.6%. That is
estimation error, not opportunity.

**Q8. Why ten years and not five?**

This is a judgement, and we present it as one. The mandate is mid-term, so the
estimate should span a full cycle including the 2018 correction and the 2020
drawdown rather than only the post-2020 regime.

We report its cost rather than hide it. Bootstrap resampling shows Lockheed
Martin is selected in **100% of five-year resamples and 50% of ten-year ones**;
Northrop 92% against 55%. Defence became a low-volatility holding only after
2022. A five-year window treats that as permanent. Ours does not.

---

## C. ESG

**Q9. What does the ESG constraint cost?**

The right answer names *which* ESG rule, because there are two independent levers
and only one of them costs anything. We solved the full 2×2 — no ESG, floor only,
average only, both — at all three risk profiles.

At the neutral profile: the **average constraint costs −0.151pp**; adding the
per-stock floor on top costs a further −0.025pp; and the **floor on its own costs
+0.008pp**, which is zero within solver tolerance. At the risk-prone profile the
floor costs exactly 0.000.

So: the average rule carries the entire cost. The floor is free insurance.

**Q10. Then why have the floor at all?**

Because a weighted average of 70 can be met while holding names scored in the
twenties. The floor closes that loophole. **Berkshire Hathaway scores 24.1** in
this dataset and is the most recognisable of the ten stocks the floor removes —
0.9% of the universe.

It is a governance improvement at no measurable return cost, which is a
different kind of argument from a performance one and should be presented as such.

**Q11. Why a floor of 30 specifically?**

From the distribution, not from a guess. Below 30 there are 10 stocks (0.9%);
below 40 there are 41 (3.8%). Thirty is the smallest floor that removes the
outliers without reshaping the universe. And it is not fragile: at 20, 30 and 40
the neutral portfolio returns **14.299%, 14.300% and 14.305%** — the answer does
not depend on the number we picked.

**Q12. Does your ESG constraint exclude weapons manufacturers?**

No, and this is worth stating plainly because it is counter-intuitive.
**Rheinmetall scores 87.3**, Leonardo 89.2, Lockheed 85.6 — all comfortably above
the 70 threshold. LSEG's methodology scores them well on environment and
governance. Without a separate screen, Rheinmetall takes up to **10.2% of the
book**.

So the controversial-industry screen does work the ESG score does not. We run it
in two tiers: Rheinmetall always excluded, and the ten diversified defence primes
as a **toggle**, because whether conventional national defence belongs in an ESG
exclusion is a contested policy question post-2022, not a technical one. Its cost
is −0.004pp at the neutral profile, so it can be decided on principle.

---

## D. Results and the backtest

**Q13. Does your optimiser beat an equal-weight portfolio?**

No. Over 7.7 years and 31 quarterly rebalances, out of sample:

| | CAGR | Volatility | Sharpe | Max drawdown |
|---|---|---|---|---|
| Model 2 | 11.03% | **13.21%** | 0.835 | **−33.9%** |
| 1/N | **14.65%** | 16.91% | **0.866** | −37.7% |

Risk-adjusted the two are **statistically indistinguishable**: the Sharpe gap is
0.031 and the t-statistic on the daily return difference is **−0.85**, far short
of significance. The honest claim is "indistinguishable, 1/N nominally ahead" —
not that either wins.

This reproduces DeMiguel, Garlappi & Uppal (2009), *Optimal Versus Naive
Diversification*, rather than revealing a defect in our implementation.
Mean-variance failing to beat 1/N out of sample is one of the best-documented
results in the literature, and the cause is estimation error.

**Q14. Then what is the model for?**

It reliably delivers what it optimises. Volatility **22% lower** than equal
weight, and lower in five of six sub-periods. Smaller drawdowns in both crises in
the sample: −3.7pp less in the COVID crash, and in 2022 it fell less while
running **36% lower volatility**.

It gives that back in every rally — 2021 and 2023-25. That is the trade a
low-volatility mandate explicitly buys, so the portfolio should be presented as a
**risk-control product, not a return-maximising one**. That is what the
constraints describe and what the backtest supports.

One exception we state rather than gloss: in the calm 2018-19 window it ran
*higher* volatility than 1/N and earned +11pp for it.

**Q15. Is your risk model accurate?**

In sample it is conservative — it overstates risk by 7.7% on average. Out of
sample it is not: mean predicted risk at the rebalance dates was **8.78%** against
**13.21%** realised, a **50% understatement**.

So the defensible phrasing is that the model is *consistent with its estimation
period*, never that it is conservative. We cannot test the frozen ten-year model
out of sample at all — it uses ten years and the dataset is ten years long, which
is a property of the data rather than an oversight.

**Q16. What is your turnover, and does it survive costs?**

**20.8% per rebalance, roughly 83% a year.** At 10bp one-way that costs 0.18pp of
CAGR, so costs are not what holds the strategy back. The turnover is itself
evidence of the instability discussed below, not a separate problem.

---

## E. The hard ones

**Q17. Is your recommended portfolio stable? Would you get the same answer next month?**

No, and this is the most serious limitation. Holding the universe fixed and
changing only the estimation window from five years to ten, the portfolio's
holdings overlap at **Jaccard 0.27** and **64% of the capital is placed
differently**. Two equally defensible estimates give two substantially different
portfolios with almost identical predicted risk and return.

We investigated the cause rather than reporting the symptom. Bootstrap resampling
*within* a window converges reliably — the top selection frequency is 1.00 and
ten names appear in at least 90% of resamples. But *across* windows even those
cores disagree at Jaccard 0.28. That makes it **regime change, not sampling
noise**, which is why resampling cannot resolve it: it resamples inside a window
and the disagreement is between windows.

The practical consequence: we can defend a *process*, not the claim that this
particular portfolio is optimal.

**Q18. Did you try to fix the instability?**

Yes, twice, and both attempts failed. We report them because the failures
identified the cause.

Bootstrap-resampled weights: Jaccard 0.29 → 0.31, no effect. Shrinking μ, which
we expected to help because μ error dominates: it compresses the *level* of μ but
preserves the *ranking*, and the churn comes from rankings disagreeing across
windows.

What did work was not naming a better factor but using more of them — hence the
twenty.

**Q19. Your ESG constraint uses today's scores at a 2018 rebalance. Isn't that look-ahead bias?**

Yes. It is, and it cannot be removed with this dataset: we have one present-day
ESG value per stock and no history. The same applies to the sector classification
used by the sector cap. We report it as look-ahead rather than presenting the
backtest as clean.

**Q20. The universe is today's index constituents. Isn't that survivorship bias?**

Yes, by construction. Companies that failed or were delisted are absent, so
realised returns are optimistic — for **every** strategy in the comparison,
including the 1/N benchmark. The relative comparison is less affected than the
absolute levels, but neither is unbiased.

**Q21. Your risk-averse portfolio holds 47% in Switzerland. How is that diversified?**

It is not, and the sector cap cannot see it because Switzerland is not one
sector — it is Swiss cantonal banks and real estate spread across two sectors.
The region constraint does not catch it either, since Europe as a whole stays
under 60%.

We measured the fix: a **25% country cap** holds it to 25.0% for **0.156pp** of
return. It is not in the current model, and it is the most obvious next addition.

We also measured that the two caps do not substitute for each other. With only
the country cap, sector exposure rises to 39.8%; with only the sector cap,
Switzerland rises to 46.8%. Blocking one concentration channel pushes exposure
into the other.

**Q22. Your risk-prone portfolio has 60% in three stocks and a worse return/risk ratio than the risk-averse one. Why present it?**

Because "maximise return" is one of the three profiles the brief asks for, and
that is what its answer looks like: a corner of the feasible set, with three
positions at the 20% cap and 23 of 30 at the 1% floor. Its ratio of 0.779 is
indeed worse than the risk-averse book's 1.067.

We present it as a valid answer to the question asked, not as a portfolio we
would recommend — and the frontier's shape is the argument. Past roughly 14%
risk it flattens, so additional risk buys very little additional return. That is
the case for the neutral book.

---

## What we have not done, and would say so

- No factor-level attribution of where the return comes from.
- Transaction costs are applied after the fact, not inside the optimisation.
- No dashboard yet — a separate requirement in the brief.
- Six price series are missing from the total-return source file and were dropped
  rather than worked around; they should be re-extracted.
