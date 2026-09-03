"""
Assemble dashboard_data/ from the result files scattered across the repo.

The dashboard should read from ONE place with stable names, not from
results_chloe/ plus the repo root plus results_country_cap/ plus stress_test/.
This copies what a dashboard needs, renames it predictably, and builds the one
table that does not exist yet: a joined per-stock universe.

Nothing here computes a model result. Every number is copied from an existing
output, so this script is safe to re-run and cannot disagree with the model.
Sources are listed per file in README.md.

Run:  python3 dashboard_data/build_dashboard_data.py      # ~5 s, no solver
"""

import os
import shutil
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TIER2OFF = "sec30_tier1_tier2off_esgfloor30"
TIER2ON = "sec30_tier1_tier2on_esgfloor30"

# (destination, source) - destination is relative to dashboard_data/
COPIES = [
    # the frontier
    (f"frontier/frontier_points.csv",
     f"results_chloe/efficient_frontier_model2_{TIER2OFF}.csv"),
    (f"frontier/frontier_weights.csv",
     f"results_chloe/efficient_frontier_weights_{TIER2OFF}.csv"),
    (f"frontier/frontier_points_tier2on.csv",
     f"results_chloe/efficient_frontier_model2_{TIER2ON}.csv"),
    (f"frontier/frontier_weights_tier2on.csv",
     f"results_chloe/efficient_frontier_weights_{TIER2ON}.csv"),

    # the three delivered books
    ("portfolios/summary.csv",              "results_chloe/portfolio_summary.csv"),
    ("portfolios/risk_averse.csv",          "results_chloe/portfolio_tier2off_risk_averse.csv"),
    ("portfolios/neutral.csv",              "results_chloe/portfolio_tier2off_neutral.csv"),
    ("portfolios/risk_prone.csv",           "results_chloe/portfolio_tier2off_risk_prone.csv"),
    ("portfolios/risk_averse_tier2on.csv",  "results_chloe/portfolio_tier2on_risk_averse.csv"),
    ("portfolios/neutral_tier2on.csv",      "results_chloe/portfolio_tier2on_neutral.csv"),
    ("portfolios/risk_prone_tier2on.csv",   "results_chloe/portfolio_tier2on_risk_prone.csv"),
    ("portfolios/profile_definitions.csv",  "results_chloe/risk_profile_scenarios_summary.csv"),

    # constraint sensitivity
    ("sensitivity/scenario_matrix.csv",     "results_chloe/scenario_matrix.csv"),
    ("sensitivity/tier2_comparison.csv",    "results_chloe/comparison_tier2.csv"),
    ("sensitivity/country_cap_frontier.csv", "results_country_cap/cap_frontier.csv"),
    ("sensitivity/country_cap_cost.csv",    "results_country_cap/cap_cost.csv"),
    ("sensitivity/country_cap_profiles.csv", "results_country_cap/cap_profiles.csv"),
    ("sensitivity/mandate_sweep.csv",       "results_country_cap/mandate.csv"),
    ("sensitivity/top_countries.csv",       "results_country_cap/top_countries.csv"),

    # walk-forward backtest
    ("backtest/equity_curves.csv",          "results_chloe/backtest/backtest_equity_curves.csv"),
    ("backtest/subperiods.csv",             "results_chloe/backtest/backtest_subperiods.csv"),
    ("backtest/summary.csv",                "results_chloe/backtest/backtest_summary.csv"),
    ("backtest/rebalances.csv",             "results_chloe/backtest/backtest_rebalances.csv"),
    ("backtest/diagnostics.csv",            "results_chloe/backtest/backtest_diagnostics.csv"),

    # walk-forward backtest of the recommended profile (script 26)
    ("backtest_profiles/summary.csv",       "backtest_profiles/results/summary.csv"),
    ("backtest_profiles/equity_curves.csv", "backtest_profiles/results/equity_curves.csv"),
    ("backtest_profiles/subperiods.csv",    "backtest_profiles/results/subperiods.csv"),
    ("backtest_profiles/rebalances.csv",    "backtest_profiles/results/rebalances.csv"),
    ("backtest_profiles/diagnostics.csv",   "backtest_profiles/results/diagnostics.csv"),
    ("backtest_profiles/gate.csv",          "backtest_profiles/results/gate.csv"),
    ("backtest_profiles/option_b_comparison.csv",
     "backtest_profiles/results/option_b_comparison.csv"),

    # crisis stress test
    ("stress/panelA_windows.csv",           "stress_test/results/panelA_windows.csv"),
    ("stress/panelB_windows.csv",           "stress_test/results/panelB_windows.csv"),
    ("stress/panelB_portfolios.csv",        "stress_test/results/panelB_portfolios.csv"),
    ("stress/panelB_not_testable.csv",      "stress_test/results/panelB_not_testable.csv"),
    ("stress/covid_attribution.csv",        "stress_test/results/drawdown_attribution.csv"),
    ("stress/worst_windows.csv",            "stress_test/results/worst_windows.csv"),
]


def build_universe():
    """One row per stock, everything a dashboard filters or colours by.

    Three membership flags, because 1093 stocks entered and 1077 reached the
    model and a dashboard that silently shows one of those numbers as the other
    is misleading:
        has_price_data      survived the price/covariance pipeline (1087)
        passes_esg_floor    individual ESG >= 30
        in_model_universe   both of the above - what Model 2 optimised over
    """
    shares = pd.read_csv(f"{ROOT}/shares_imputed.csv").set_index("Stock")
    sectors = pd.read_excel(f"{ROOT}/sectors.xlsx").set_index("Stock")["Sector"]
    mu = pd.read_csv(f"{ROOT}/expected_return_v4.csv").set_index("Stock")["expected_return"]
    sd = pd.read_csv(f"{ROOT}/per_stock_risk_v4.csv").set_index("Stock")["risk_std"]

    # header row only: the file is 24 MB and we need the ticker list, not the matrix
    cov_cols = pd.read_csv(f"{ROOT}/covariance_matrix_v4.csv", nrows=0).columns.tolist()[1:]

    u = pd.DataFrame(index=shares.index)
    u["region"] = shares["Region"]
    u["country"] = shares["Country"]
    u["sector"] = sectors.reindex(u.index).fillna("Unknown")
    u["esg"] = shares["ESG score"]
    u["expected_return"] = mu.reindex(u.index)
    u["risk_std"] = sd.reindex(u.index)
    u["has_price_data"] = u.index.isin(cov_cols)
    u["passes_esg_floor"] = u["esg"] >= 30.0
    u["in_model_universe"] = u["has_price_data"] & u["passes_esg_floor"]
    u.index.name = "stock"

    # which of the delivered books holds it, and at what weight
    for name in ("risk_averse", "neutral", "risk_prone"):
        w = pd.read_csv(f"{ROOT}/results_chloe/portfolio_tier2off_{name}.csv",
                        index_col=0)["weight_%"]
        u[f"weight_{name}_%"] = w.reindex(u.index).fillna(0.0)
    return u.sort_index()


def main():
    n_copied, missing = 0, []
    for dst, src in COPIES:
        s = os.path.join(ROOT, src)
        d = os.path.join(HERE, dst)
        if not os.path.exists(s):
            missing.append(src)
            continue
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(s, d)
        n_copied += 1
    print(f"copied {n_copied} files")
    if missing:
        print("MISSING sources (regenerate them, then re-run):")
        for m in missing:
            print(f"  {m}")

    os.makedirs(os.path.join(HERE, "universe"), exist_ok=True)
    u = build_universe()
    u.to_csv(os.path.join(HERE, "universe/stocks.csv"))
    print(f"built universe/stocks.csv  {len(u)} stocks | "
          f"{int(u['in_model_universe'].sum())} in the model universe | "
          f"{int(u['weight_neutral_%'].gt(0).sum())} held by neutral")

    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(HERE) for f in fs)
    print(f"dashboard_data/ total {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
