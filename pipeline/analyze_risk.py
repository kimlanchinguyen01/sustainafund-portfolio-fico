"""
Risk-profile scenario analysis for Model 2 (Markowitz / MIQP)
================================================================
Case study requirement (Case Study Description 2.pdf, p.2):
  "The decision-makers would like to evaluate multiple solutions and
   compare outcomes for different risk profiles (e.g. risk averse,
   neutral, and risk prone), for example by maximizing return subject
   to a maximum risk level, minimizing risk, or combining both
   objectives."

This script does NOT call the Xpress solver again. It reads the two
files already saved by Model2_ori.py's full frontier sweep
(RUN_FULL_SWEEP = True):
    efficient_frontier_model2.csv
    efficient_frontier_weights.csv

and extracts 3 named scenario portfolios from the frontier already computed:

    Risk Averse = lowest-risk point on the frontier
                  (same as the "min_risk_only" corner)
    Risk Prone  = highest-return point on the frontier
                  (same as the "max_return_only" corner)
    Neutral     = the point with the BEST risk-adjusted return, i.e.
                  highest Sharpe ratio = portfolio_return / portfolio_risk.
                  This uses the case study's own simplified Sharpe
                  definition (p.2: "mean return divided by its standard
                  deviation", no risk-free rate subtracted). Chosen over
                  an arbitrary "middle" target return or an arbitrary
                  risk-aversion parameter lambda, because it needs no
                  extra assumption and is the standard finance definition
                  of the best risk/return trade-off point.

NOTE: still running on the provisional ~997-stock universe (data
cleaning in progress) -- rerun this script after Model2_ori.py is
rerun on the final cleaned data.
"""

import pandas as pd
import Model2_ori as m2
tag = m2.scenario_tag()
FRONTIER_CSV = f"efficient_frontier_model2_{tag}.csv"
WEIGHTS_CSV = f"efficient_frontier_weights_{tag}.csv"
TOP_N = 10

frontier = pd.read_csv(FRONTIER_CSV)
weights = pd.read_csv(WEIGHTS_CSV, index_col=0)

# robust bool parsing regardless of how pandas inferred the column
frontier["feasible"] = frontier["feasible"].astype(str).str.strip() == "True"

# IMPORTANT: do NOT reset_index here. The row position in this CSV
# matches the "beta_<i>" column names in efficient_frontier_weights.csv
# (both come from the same enumerate() in Model2_ori.py's sweep loop).
frontier = frontier[frontier["feasible"]]
if frontier.empty:
    raise RuntimeError("No feasible point found in efficient_frontier_model2.csv")

frontier["sharpe"] = frontier["portfolio_return"] / frontier["portfolio_risk"]

idx_risk_averse = frontier["portfolio_risk"].idxmin()
idx_risk_prone = frontier["portfolio_return"].idxmax()
idx_neutral = frontier["sharpe"].idxmax()

scenarios = {
    "Risk Averse (min risk)": idx_risk_averse,
    "Neutral (max Sharpe = return/risk)": idx_neutral,
    "Risk Prone (max return)": idx_risk_prone,
}

print("=" * 70)
print("RISK PROFILE SCENARIOS  (Case Study Description 2.pdf, p.2)")
print("=" * 70)

summary_rows = []
for label, idx in scenarios.items():
    row = frontier.loc[idx]
    beta_col = f"beta_{idx}"
    print(f"\n--- {label} ---")
    print(f"  frontier row index = {idx}")
    print(f"  target_beta        = {row['target_beta']:.4f}")
    print(f"  portfolio_return   = {row['portfolio_return']:.4f}")
    print(f"  portfolio_risk     = {row['portfolio_risk']:.4f}")
    print(f"  sharpe (ret/risk)  = {row['sharpe']:.4f}")
    print(f"  n_selected         = {int(row['n_selected'])}")
    print(f"  esg_weighted       = {row['esg_weighted']:.2f}")

    if beta_col in weights.columns:
        top = weights[beta_col].sort_values(ascending=False).head(TOP_N)
        print(f"  Top {TOP_N} holdings:")
        for tkr, w in top.items():
            if w > 1e-6:
                print(f"    {tkr:<12s} {w * 100:6.2f}%")
    else:
        print(f"  WARNING: weight column '{beta_col}' not found in "
              f"{WEIGHTS_CSV} -- check that row order in "
              f"efficient_frontier_model2.csv matches the beta_<i> "
              f"column naming in efficient_frontier_weights.csv")

    summary_rows.append({
        "scenario": label,
        "target_beta": row["target_beta"],
        "portfolio_return": row["portfolio_return"],
        "portfolio_risk": row["portfolio_risk"],
        "sharpe": row["sharpe"],
        "n_selected": row["n_selected"],
        "esg_weighted": row["esg_weighted"],
    })

summary_df = pd.DataFrame(summary_rows).set_index("scenario")
summary_df.to_csv("risk_profile_scenarios_summary.csv")
print("\nSaved risk_profile_scenarios_summary.csv")