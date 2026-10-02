"""
03e — Does the excluded universe change the PORTFOLIO, not just the objective?
=============================================================================
Chi Chloe's refined point (2026-09-01): the cost in return may be small, but the
optimisation RESULT - the actual set of stocks bought - is affected if not all
stocks are eligible. That is a different claim from the one 03d tested, and it
matters more, because what gets frozen on Thursday is the portfolio itself.

It is also the right thing to worry about: the Markowitz objective is famously
flat near the optimum, so a negligible change in risk/return is NOT evidence
that the composition is stable.

Experiment
----------
For each portfolio on frontier A (5y window, full 1055-stock universe), solve
the restricted problem B (same mu, same Sigma, only the 997 long-history stocks)
at THE SAME target return. Both portfolios then sit at the same return, so any
difference in holdings is attributable to eligibility alone.

Reported per matched point:
    Jaccard overlap of the selected sets
    active share  = 0.5 * sum |w_A - w_B|   (fraction of capital differently placed)
    how many of the names unique to A are actually the newly-eligible stocks
    vs how many are substitutions among stocks BOTH problems could have chosen

That last split is the crux. If A's extra names are only the newcomers, the
effect is contained. If admitting newcomers reshuffles the incumbents too, the
composition is genuinely unstable and no single portfolio can be called "the"
optimum.

Baseline for scale: the same comparison between two runs that differ only in
estimation window (10y vs 5y, universe held at 997) - i.e. how much the
composition churns from an ordinary data change.
"""

from paths import P   # where each data file lives (see paths.py)

import os

import numpy as np
import pandas as pd

os.environ["XPAUTH_PATH"] = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
import Model2

SHARES = P("shares_imputed.csv")


def load(mu_file, cov_file, restrict_to=None):
    mu = pd.read_csv(mu_file).set_index("Stock")["expected_return"]
    cov = pd.read_csv(cov_file, index_col=0)
    sh = pd.read_csv(SHARES).set_index("Stock")
    common = sorted(set(mu.index) & set(cov.index) & set(sh.index))
    if restrict_to is not None:
        common = sorted(set(common) & set(restrict_to))
    return (mu.loc[common], cov.loc[common, common],
            sh.loc[common, "Region"], sh.loc[common, "ESG score"])


def held(res, tol=1e-9):
    w = res["weights"]
    return w[w > tol]


def compare(pa, pb):
    a, b = held(pa), held(pb)
    sa, sb = set(a.index), set(b.index)
    union = sa | sb
    jac = len(sa & sb) / len(union) if union else 1.0
    idx = sorted(union)
    wa = a.reindex(idx).fillna(0.0)
    wb = b.reindex(idx).fillna(0.0)
    active = 0.5 * float((wa - wb).abs().sum())
    return sa, sb, jac, active


u10 = pd.read_csv(P("expected_return_final_usd.csv")).set_index("Stock").index
u5 = pd.read_csv(P("expected_return_final_usd_5y.csv")).set_index("Stock").index
newcomers = set(u5) - set(u10)

MU5, COV5 = P("expected_return_final_usd_5y.csv"), P("covariance_matrix_shrunk_usd_5y.csv")
full = load(MU5, COV5)
restr = load(MU5, COV5, restrict_to=u10)
print(f"Universe A (full 5y): {len(full[0])}   Universe B (long-history only): {len(restr[0])}")
print(f"Newly eligible on 5y: {len(newcomers)}\n")

lo = Model2.solve_model2(*full, mode="min_risk_only", time_limit=120)
hi = Model2.solve_model2(*full, mode="max_return_only", time_limit=120)
betas = np.linspace(lo["portfolio_return"], hi["portfolio_return"], 15)

print("=" * 100)
print("A (1055 eligible) vs B (997 eligible), SOLVED AT THE SAME TARGET RETURN")
print("=" * 100)
hdr = (f"{'ret %':>7} {'nA':>4} {'nB':>4} {'riskA%':>7} {'riskB%':>7} "
       f"{'Jaccard':>8} {'active':>7} {'onlyA':>6} {'new':>4} {'subst':>6} {'onlyB':>6}")
print(hdr)
rows = []
for beta in betas:
    ra = Model2.solve_model2(*full, mode="min_risk", target_return=beta, time_limit=120)
    rb = Model2.solve_model2(*restr, mode="min_risk", target_return=beta, time_limit=120)
    if not (ra["feasible"] and rb["feasible"]):
        print(f"{beta*100:7.2f}  infeasible in one of the two - skipped")
        continue
    sa, sb, jac, active = compare(ra, rb)
    only_a = sa - sb
    n_new = len(only_a & newcomers)
    n_sub = len(only_a) - n_new
    rows.append({"ret": beta * 100, "jac": jac, "active": active,
                 "only_a": len(only_a), "new": n_new, "subst": n_sub,
                 "only_b": len(sb - sa)})
    print(f"{beta*100:7.2f} {len(sa):4d} {len(sb):4d} "
          f"{ra['portfolio_risk']*100:7.2f} {rb['portfolio_risk']*100:7.2f} "
          f"{jac:8.2f} {active*100:6.1f}% {len(only_a):6d} {n_new:4d} "
          f"{n_sub:6d} {len(sb-sa):6d}")

R = pd.DataFrame(rows)
print(f"\nMean Jaccard overlap : {R.jac.mean():.2f}   (1.00 = identical holdings)")
print(f"Mean active share    : {R.active.mean()*100:.1f}% of capital placed differently")
print(f"Names unique to A    : {R.only_a.mean():.1f} on average, of which "
      f"{R.new.mean():.1f} newcomers and {R.subst.mean():.1f} SUBSTITUTIONS "
      f"among stocks both problems could pick")
print(f"Names unique to B    : {R.only_b.mean():.1f} on average")

# ---------------------------------------------------------- baseline for scale
print("\n" + "=" * 100)
print("BASELINE: same universe (997), estimation window changed 5y -> 10y")
print("=" * 100)
print("How much does composition churn from an ORDINARY data change?")
b10 = load(P("expected_return_final_usd.csv"), P("covariance_matrix_shrunk_usd.csv"))
lo10 = Model2.solve_model2(*b10, mode="min_risk_only", time_limit=120)
hi10 = Model2.solve_model2(*b10, mode="max_return_only", time_limit=120)
betas10 = np.linspace(lo10["portfolio_return"], hi10["portfolio_return"], 8)
print(f"{'ret %':>7} {'Jaccard':>8} {'active':>8}")
base = []
for beta in betas10:
    r10 = Model2.solve_model2(*b10, mode="min_risk", target_return=beta, time_limit=120)
    r5 = Model2.solve_model2(*restr, mode="min_risk", target_return=beta, time_limit=120)
    if not (r10["feasible"] and r5["feasible"]):
        continue
    _, _, jac, active = compare(r10, r5)
    base.append({"jac": jac, "active": active})
    print(f"{beta*100:7.2f} {jac:8.2f} {active*100:7.1f}%")
B = pd.DataFrame(base)
print(f"\nMean Jaccard {B.jac.mean():.2f} | mean active share {B.active.mean()*100:.1f}%")

print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)
print(f"eligibility change (1055 vs 997) : Jaccard {R.jac.mean():.2f}, "
      f"active share {R.active.mean()*100:.1f}%")
print(f"ordinary window change (5y vs 10y): Jaccard {B.jac.mean():.2f}, "
      f"active share {B.active.mean()*100:.1f}%")
