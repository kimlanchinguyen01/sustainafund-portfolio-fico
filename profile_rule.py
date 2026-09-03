"""
The canonical risk-profile selection rule — one definition, all consumers.
==========================================================================
This existed in three places with two different answers, and the repo shipped
two different portfolios both labelled "Risk Prone" for a while. It now lives
here and nowhere else.

THE RULE, from the frozen archive/our_model_frozen/19_freeze_v4.py lines 101-107:

    degenerate  = top-3 weight > 0.40  OR  more than 15 positions on the 1% floor
    Risk Averse = argmin risk
    Neutral     = argmax return/risk
    Risk Prone  = argmax return AMONG NON-DEGENERATE POINTS

WHY "Risk Prone" needs the degeneracy filter. Plain argmax(return) lands on a
corner of the feasible set rather than a portfolio. On the delivered frontier
that is point 14: three positions pinned at the 20% cap, 23 of 30 positions on
the 1% floor, 60% of the budget in three stocks, and a return/risk ratio of
0.779 - WORSE than the risk-averse book's 1.067. It is a dominated portfolio.
The filter selects point 11 instead: 15.97% at 12.77%, ratio 1.250.

The rule must be DERIVED per configuration, never hard-coded, because the
degenerate set moves with the constraints: with no sector cap, Risk Prone is
point 12 rather than 11.

FLOOR_TOL is 1e-5, not 1e-6, and that matters. At MIP_GAP = 0.001 the solver
leaves the smallest holding in the min-risk book at 0.010005 - five parts per
million above the 1% floor - so a tighter tolerance counts zero positions at
the floor where there is plainly one.
"""

import pandas as pd

DEG_TOP3 = 0.40        # top-3 concentration above which a point is degenerate
DEG_FLOOR_N = 15       # positions on the weight floor above which it is degenerate
FLOOR_TOL = 1e-5       # see the docstring: NOT 1e-6
W_MIN = 0.01           # the brief's per-stock floor

PROFILE_RULES = {
    "Risk Averse": "Minimum variance",
    "Neutral": "Maximum return/risk ratio",
    "Risk Prone": "Highest non-degenerate return",
}
PROFILES = tuple(PROFILE_RULES)


def degeneracy(weights):
    """Concentration diagnostics for one portfolio. `weights` is a Series."""
    h = weights[weights > 1e-9].sort_values(ascending=False)
    return {"top3_weight": float(h.head(3).sum()),
            "n_at_floor": int((h < W_MIN + FLOOR_TOL).sum())}


def is_degenerate(top3_weight, n_at_floor):
    return bool(top3_weight > DEG_TOP3 or n_at_floor > DEG_FLOOR_N)


def pick_profiles(rows):
    """Select the three profiles from a frontier.

    `rows` is anything DataFrame-able with one row per FEASIBLE frontier point
    and these columns:
        frontier_point, expected_return, risk, top3_weight, n_at_floor

    Returns {profile name: frontier_point}.
    """
    F = pd.DataFrame(rows)
    missing = {"frontier_point", "expected_return", "risk",
               "top3_weight", "n_at_floor"} - set(F.columns)
    if missing:
        raise ValueError(f"pick_profiles needs columns {sorted(missing)}")

    deg = (F["top3_weight"] > DEG_TOP3) | (F["n_at_floor"] > DEG_FLOOR_N)
    ok = F[~deg]
    if not len(ok):
        raise RuntimeError("every frontier point is degenerate - the rule cannot "
                           "select a Risk Prone book")
    ratio = F["expected_return"] / F["risk"]
    return {"Risk Averse": int(F.loc[F["risk"].idxmin(), "frontier_point"]),
            "Neutral": int(F.loc[ratio.idxmax(), "frontier_point"]),
            "Risk Prone": int(ok.loc[ok["expected_return"].idxmax(), "frontier_point"])}


def rows_from_results(results):
    """Build pick_profiles' input from a list of solve_model2 result dicts.

    Skips infeasible points. `frontier_point` is the index within the list as
    given, so pass the full sweep in order.
    """
    rows = []
    for i, r in enumerate(results):
        if not r.get("feasible"):
            continue
        rows.append({"frontier_point": i,
                     "expected_return": float(r["portfolio_return"]),
                     "risk": float(r["portfolio_risk"]),
                     **degeneracy(r["weights"])})
    return rows
