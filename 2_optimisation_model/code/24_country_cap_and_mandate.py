"""
SustainaFund — 24: country cap, and risk profiles stated as mandates
=====================================================================
Produces the numbers behind the two additions of 3 Sep 2026. Both come out of
FICO's own python-notebooks/xpress-api/modeling_examples; the ADDITIONS block
in Model2_ori.py records which ideas were adopted and which were measured and
rejected.

Part A — COUNTRY CAP
    Model 2 capped region and sector. Switzerland fell between the two: it is
    not a region, and it spans two sectors (cantonal banks, real estate), so
    neither cap could see it. Sweeps the frontier with the cap off and at
    several cap levels, and reports what the cap costs in risk at matched
    return, and in return at matched risk.

Part B — MANDATES
    The three profiles in analyze_risk.py are picked off a 15-point grid with
    idxmin / idxmax / idxmax(sharpe), so each is the best of 15 sampled points.
    A mandate states the same intent directly: "maximise return, then minimise
    risk while giving up at most X of the maximum". Sweeps X.

Outputs (2_optimisation_model/results/country_cap/):
    cap_frontier.csv        every frontier point at every cap level
    cap_cost.csv            cost of the cap, both framings
    cap_profiles.csv        the three profiles, cap off vs cap on
    mandate.csv             the mandate sweep, cap off vs cap on
    top_countries.csv       country concentration of the uncapped profiles

Run:  export XPAUTH_PATH=~/Documents/FICO-case-study/xpauth.xpr
      python3 24_country_cap_and_mandate.py          # ~6 min
"""

import os
import numpy as np
import pandas as pd

import Model2_ori as m2

OUTDIR = os.path.join(m2.RESULTS_DIR, "country_cap")
CAP_LEVELS = [0.20, 0.25, 0.30, 0.40]
MANDATE_RELTOLS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
N_POINTS = m2.N_FRONTIER_POINTS

os.makedirs(OUTDIR, exist_ok=True)


def sweep_frontier(data, n_points=N_POINTS):
    """Corners, then a linspace between them. The corners MOVE with the cap, so
    they are re-solved per configuration rather than reused from the uncapped run."""
    mu, Sigma, region, esg, sector, country = data
    kw = dict(country=country, time_limit=300, verbose=False)

    lo = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk_only", **kw)
    hi = m2.solve_model2(mu, Sigma, region, esg, sector, mode="max_return_only", **kw)
    if not (lo["feasible"] and hi["feasible"]):
        return None, None, None

    betas = np.linspace(lo["portfolio_return"], hi["portfolio_return"], n_points)
    rows = []
    for i, b in enumerate(betas):
        r = m2.solve_model2(mu, Sigma, region, esg, sector, mode="min_risk",
                            target_return=b, **kw)
        row = {"pt": i, "target_beta": b, "feasible": r["feasible"]}
        if r["feasible"]:
            row.update({
                "ret": r["portfolio_return"], "risk": r["portfolio_risk"],
                "ratio": r["portfolio_return"] / r["portfolio_risk"],
                "n": r["n_selected"], "esg": r["esg_weighted"],
                "max_country": r.get("max_country"),
                "max_country_w": r.get("max_country_weight"),
                "CH": r.get("weight_country_Switzerland", 0.0),
                "US": r.get("weight_country_United States", 0.0),
            })
        else:
            row["solstatus"] = r["solstatus"]
            if r.get("iis", {}).get("iis_found"):
                row["iis"] = " | ".join(r["iis"]["iis_list"][0]["constraints"][:6])
        rows.append(row)
    return pd.DataFrame(rows), lo, hi


def profiles(front):
    """The three profiles exactly as analyze_risk.py defines them."""
    f = front[front["feasible"]].reset_index(drop=True)
    return {"risk_averse": f.loc[f["risk"].idxmin()],
            "neutral": f.loc[f["ratio"].idxmax()],
            "risk_prone": f.loc[f["ret"].idxmax()]}


def interp_return_at_risk(front, risk):
    """Return attainable at a given risk, linearly interpolated along the
    frontier. Lets the cap's cost be quoted at MATCHED RISK, which is the
    framing a mandate holder cares about, not only at matched return."""
    f = front[front["feasible"]].sort_values("risk")
    if risk < f["risk"].min() or risk > f["risk"].max():
        return np.nan
    return float(np.interp(risk, f["risk"].to_numpy(), f["ret"].to_numpy()))


def main():
    data = m2.load_data(return_country=True)
    mu, Sigma, region, esg, sector, country = data

    # ---------- Part A ----------
    print("\n" + "=" * 70)
    print("PART A - COUNTRY CAP")
    print("=" * 70)

    m2.ENABLE_COUNTRY_CAP = False
    print("\n--- cap OFF ---", flush=True)
    off, off_lo, off_hi = sweep_frontier(data)
    off["cap"] = "off"
    all_front = [off]

    for lvl in CAP_LEVELS:
        m2.ENABLE_COUNTRY_CAP = True
        m2.COUNTRY_CAP = lvl
        print(f"\n--- cap {lvl:.0%} ---", flush=True)
        f, _, _ = sweep_frontier(data)
        if f is None:
            print(f"    cap {lvl:.0%}: corners infeasible, skipped")
            continue
        f["cap"] = f"{lvl:.0%}"
        all_front.append(f)
        n_bind = int((f["max_country_w"] > lvl - 1e-6).sum())
        n_inf = int((~f["feasible"]).sum())
        print(f"    binds at {n_bind}/{len(f)} points, {n_inf} infeasible")

    front = pd.concat(all_front, ignore_index=True)
    front.to_csv(f"{OUTDIR}/cap_frontier.csv", index=False)

    # cost of the cap, both framings, point by point against the uncapped sweep
    cost_rows = []
    for lvl in [c for c in front["cap"].unique() if c != "off"]:
        f = front[front["cap"] == lvl]
        for _, r in f[f["feasible"]].iterrows():
            o = off[(off["pt"] == r["pt"]) & off["feasible"]]
            if o.empty:
                continue
            o = o.iloc[0]
            cost_rows.append({
                "cap": lvl, "pt": int(r["pt"]), "beta": r["target_beta"],
                "risk_off": o["risk"], "risk_cap": r["risk"],
                "d_risk_pp": (r["risk"] - o["risk"]) * 100,
                "ret_off_at_capped_risk": interp_return_at_risk(off, r["risk"]),
                "ret_cap": r["ret"],
                "CH_off": o["CH"], "CH_cap": r["CH"],
                "n_off": o["n"], "n_cap": r["n"],
            })
    cost = pd.DataFrame(cost_rows)
    if len(cost):
        cost["d_ret_pp_at_matched_risk"] = \
            (cost["ret_cap"] - cost["ret_off_at_capped_risk"]) * 100
    cost.to_csv(f"{OUTDIR}/cap_cost.csv", index=False)

    # the three profiles, cap off vs each cap level
    prof_rows = []
    for lvl in front["cap"].unique():
        f = front[front["cap"] == lvl]
        for name, row in profiles(f).items():
            prof_rows.append({
                "cap": lvl, "profile": name, "pt": int(row["pt"]),
                "ret_%": row["ret"] * 100, "risk_%": row["risk"] * 100,
                "ratio": row["ratio"], "n": int(row["n"]), "esg": row["esg"],
                "top_country": row["max_country"],
                "top_country_%": row["max_country_w"] * 100,
                "CH_%": row["CH"] * 100, "US_%": row["US"] * 100,
            })
    prof = pd.DataFrame(prof_rows)
    prof.to_csv(f"{OUTDIR}/cap_profiles.csv", index=False)
    print("\n--- the three profiles, by cap level ---")
    print(prof.to_string(float_format=lambda v: f"{v:.3f}", index=False))

    # country concentration of the uncapped profiles, for the deck
    m2.ENABLE_COUNTRY_CAP = False
    top_rows = []
    for name, row in profiles(off).items():
        r = m2.solve_model2(mu, Sigma, region, esg, sector, country=country,
                            mode="min_risk", target_return=row["target_beta"],
                            time_limit=300, verbose=False)
        w = pd.Series(r["weights"].to_numpy(), index=country.to_numpy())
        for c, v in w.groupby(level=0).sum().nlargest(6).items():
            top_rows.append({"profile": name, "country": c, "weight_%": v * 100})
    pd.DataFrame(top_rows).to_csv(f"{OUTDIR}/top_countries.csv", index=False)

    # ---------- Part B ----------
    print("\n" + "=" * 70)
    print("PART B - PROFILES AS MANDATES")
    print("=" * 70)

    man_rows = []
    for cap_on, lvl in ((False, None), (True, 0.25)):
        m2.ENABLE_COUNTRY_CAP = cap_on
        if cap_on:
            m2.COUNTRY_CAP = lvl
        for tol in MANDATE_RELTOLS:
            r = m2.solve_mandate(mu, Sigma, region, esg, sector,
                                 country=country, reltol=tol, time_limit=300)
            row = {"cap": f"{lvl:.0%}" if cap_on else "off", "reltol": tol,
                   "feasible": r["feasible"]}
            if r["feasible"]:
                row.update({
                    "max_return_%": r["max_return"] * 100,
                    "return_floor_%": r["return_floor"] * 100,
                    "ret_%": r["portfolio_return"] * 100,
                    "risk_%": r["portfolio_risk"] * 100,
                    "ratio": r["portfolio_return"] / r["portfolio_risk"],
                    "n": r["n_selected"], "esg": r["esg_weighted"],
                    "gave_up_pp": r["return_given_up_pp"],
                    "top_country": r.get("max_country"),
                    "top_country_%": (r.get("max_country_weight") or 0) * 100,
                    "sec": r["elapsed_sec"],
                })
            man_rows.append(row)
    man = pd.DataFrame(man_rows)
    man.to_csv(f"{OUTDIR}/mandate.csv", index=False)
    print("\n--- mandate sweep ---")
    print(man.to_string(float_format=lambda v: f"{v:.3f}", index=False))

    print(f"\nWrote 5 CSVs to {OUTDIR}/")


if __name__ == "__main__":
    main()
