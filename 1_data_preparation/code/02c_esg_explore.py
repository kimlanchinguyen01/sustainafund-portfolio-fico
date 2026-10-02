"""
ESG score exploration — SustainaFund
================================================================
Standalone EDA script, separate from Main_model.py. Looks at the
distribution of individual-stock ESG scores to pick a defensible
ESG_FLOOR value (per-stock minimum) instead of guessing a number.

Reads shares_full.csv directly — no mu/Sigma/Xpress needed here.
"""

from paths import P   # where each data file lives (see paths.py)
import pandas as pd
import matplotlib.pyplot as plt

FILE_SHARES = P("shares_full.csv")
COL_STOCK = "Stock"
COL_ESG = "ESG score"

shares = pd.read_csv(FILE_SHARES)
esg = shares.set_index(COL_STOCK)[COL_ESG]

print(f"Total stocks: {len(esg)}")
print("ESG score distribution: min=%.1f  p10=%.1f  p25=%.1f  median=%.1f  p75=%.1f  max=%.1f" % (
    esg.min(), esg.quantile(0.10), esg.quantile(0.25), esg.median(), esg.quantile(0.75), esg.max()))

print("\nLowest 10 individual ESG scores:")
print(esg.sort_values().head(10))

print("\nHow many stocks fall below each candidate floor:")
for floor in [10, 20, 30, 40, 49.3, 58.6]:
    n = int((esg < floor).sum())
    print(f"  ESG < {floor}: {n} stocks ({100 * n / len(esg):.1f}% of universe)")

# Quick histogram — useful for the report / slides too
plt.figure(figsize=(8, 5))
plt.hist(esg.dropna(), bins=40, edgecolor="black")
plt.axvline(70, color="red", linestyle="--", label="Portfolio-average floor (ESG_MIN=70)")
plt.xlabel("Individual stock ESG score")
plt.ylabel("Number of stocks")
plt.title("ESG score distribution — SustainaFund universe")
plt.legend()
plt.tight_layout()
plt.savefig(P("esg_distribution.png"), dpi=150)
print("\nSaved esg_distribution.png")