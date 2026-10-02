"""
paths.py - where every data file of part 1 lives.

The scripts in this folder were written to read and write files in the current
directory. After the repository was grouped by part they call P("name.csv")
instead, which returns the full path, so they run from any working directory.

  raw inputs of this part        -> 1_data_preparation/data/
  files the model also reads     -> 2_optimisation_model/data/   (single copy)
  everything these scripts write -> 1_data_preparation/results/
"""
import os

CODE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(CODE)
REPO = os.path.dirname(PART)

DATA = os.path.join(PART, "data")
RESULTS = os.path.join(PART, "results")
MODEL_DATA = os.path.join(REPO, "2_optimisation_model", "data")
MODEL_CODE = os.path.join(REPO, "2_optimisation_model", "code")

# raw inputs (LSEG / course data)
RAW = {"stockprices_full.csv", "stockprices_test.csv", "FINAL_stock_data.xlsx",
       "fx_rates_ecb.csv", "shares_test.csv", "prices_lseg_dividend_adjusted.csv"}

# the six files that ARE the model's inputs; one copy, kept next to the model
SHARED = {"covariance_matrix_v4.csv", "expected_return_v4.csv", "per_stock_risk_v4.csv",
          "shares_imputed.csv", "shares_full.csv", "sectors.xlsx"}


def P(name):
    """Full path of a data file, by name."""
    base = os.path.basename(name)
    if base in SHARED:
        folder = MODEL_DATA
    elif base in RAW:
        folder = DATA
    else:
        folder = RESULTS
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, name)
