"""
03c — Efficient frontier on USD inputs
======================================
Runs the UNMODIFIED Model2.py against the USD estimates from 03b. Model2 is
imported as a module and only its input-file constants are overridden, so the
formulation, the constraints and the solver settings are byte-identical to the
local-currency run - the frontier moves only because mu and Sigma changed.

Also reports the two comparisons that matter:
  (a) old (local) frontier vs new (USD) frontier
  (b) the OLD portfolios re-priced under the USD covariance - i.e. the risk
      those portfolios actually carried, which is what the model was blind to.

Outputs: efficient_frontier_model2_usd.csv, efficient_frontier_weights_usd.csv
"""

import os

import numpy as np
import pandas as pd

# Must precede the Model2 import: Model2 uses os.environ.setdefault, so a value
# already present wins. Model2 would otherwise look for xpauth.xpr inside
# pipeline/, where it does not live.
LICENSE = os.path.expanduser("~/Documents/FICO-case-study/xpauth.xpr")
assert os.path.exists(LICENSE), f"license not found: {LICENSE}"
os.environ["XPAUTH_PATH"] = LICENSE

import Model2

Model2.FILE_EXPECTED_RETURN = "expected_return_final_usd.csv"
Model2.FILE_COVARIANCE = "covariance_matrix_shrunk_usd.csv"
Model2.FILE_SHARES = "shares_imputed.csv"

print("Model2 input files overridden ->")
print("  returns   :", Model2.FILE_EXPECTED_RETURN)
print("  covariance:", Model2.FILE_COVARIANCE)
print("  shares    :", Model2.FILE_SHARES)
print("Constraints unchanged:",
      f"w in [{Model2.W_MIN}, {Model2.W_MAX}], region cap {Model2.REGION_CAP},",
      f"min stocks {Model2.MIN_STOCKS}, ESG >= {Model2.ESG_MIN}")

mu, Sigma, region, esg = Model2.load_data()
r_min, r_max = Model2.check_feasibility_and_scale(mu, Sigma, region, esg)

frontier = Model2.efficient_frontier(mu, Sigma, region, esg, r_min, r_max)

rows = [{k: v for k, v in r.items() if k != "weights"} for r in frontier]
pd.DataFrame(rows).to_csv("efficient_frontier_model2_usd.csv", index=False)
W_usd = pd.DataFrame({f"beta_{i}": r["weights"]
                      for i, r in enumerate(frontier) if r["feasible"]})
W_usd.to_csv("efficient_frontier_weights_usd.csv")
print("\nSaved efficient_frontier_model2_usd.csv, efficient_frontier_weights_usd.csv")

# ---------------------------------------------------------------- comparison
S_usd = pd.read_csv("covariance_matrix_shrunk_usd.csv", index_col=0)
mu_usd = pd.read_csv("expected_return_final_usd.csv").set_index("Stock")["expected_return"]

EF_loc = pd.read_csv("efficient_frontier_model2.csv")
W_loc = pd.read_csv("efficient_frontier_weights.csv", index_col=0)
EF_usd = pd.read_csv("efficient_frontier_model2_usd.csv")


def reprice(w):
    """Return and risk of a weight vector under the USD estimates."""
    w = w.fillna(0.0)
    w = w[w > 1e-9]
    idx = w.index.intersection(S_usd.index)
    w = (w.loc[idx] / w.loc[idx].sum()).values
    S = S_usd.loc[idx, idx].values
    return float(mu_usd.loc[idx].values @ w), float(np.sqrt(w @ S @ w))


print("\n" + "=" * 92)
print("(a) OLD local-currency frontier, RE-PRICED under the USD estimates")
print("=" * 92)
rows = []
for i, col in enumerate(W_loc.columns):
    r_true, s_true = reprice(W_loc[col])
    rows.append({"pt": i,
                 "ret_believed_%": EF_loc.loc[i, "portfolio_return"] * 100,
                 "risk_believed_%": EF_loc.loc[i, "portfolio_risk"] * 100,
                 "ret_actual_%": r_true * 100,
                 "risk_actual_%": s_true * 100,
                 "risk_understated_%": (s_true / EF_loc.loc[i, "portfolio_risk"] - 1) * 100})
old = pd.DataFrame(rows)
print(old.round(2).to_string(index=False))

print("\n" + "=" * 92)
print("(b) NEW frontier solved on USD inputs")
print("=" * 92)
new = EF_usd[["n_selected", "portfolio_return", "portfolio_risk", "esg_weighted",
              "weight_region_Europe", "weight_region_United States", "elapsed_sec"]].copy()
new.columns = ["n", "ret_%", "risk_%", "ESG", "w_EU", "w_US", "sec"]
new[["ret_%", "risk_%"]] *= 100
new[["w_EU", "w_US"]] *= 100
print(new.round(2).to_string())

print("\n" + "=" * 92)
print("(c) At matched risk, how much return does the correct model give?")
print("=" * 92)
print("For each OLD portfolio's ACTUAL risk, the return the NEW frontier offers")
print("at that risk level (linear interpolation along the new frontier):")
xs = EF_usd.portfolio_risk.values * 100
ys = EF_usd.portfolio_return.values * 100
o = np.argsort(xs)
for _, r in old.iterrows():
    best = float(np.interp(r["risk_actual_%"], xs[o], ys[o]))
    print(f"  pt {int(r['pt']):>2}: risk {r['risk_actual_%']:6.2f}%  ->  "
          f"old portfolio returns {r['ret_actual_%']:6.2f}%,  "
          f"new frontier offers {best:6.2f}%  (gain {best - r['ret_actual_%']:+5.2f} pp)")
