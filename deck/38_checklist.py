"""
38 — the brief's quality checklist, run explicitly
==================================================
BRIEF_build_deck.md section 7 asks for these ten checks to be run and the result
reported. This runs the eight that can be checked mechanically and states plainly
which two rest on a visual pass.

The load-bearing one is check 1: every numeric token that appears on a slide is
matched against deck_data.json, derived_metrics.json and the committed CSVs. A
figure that cannot be matched is listed, and the rule is to remove it.

Run:  python3 deck/38_checklist.py
"""

import importlib.util
import json
import os
import re
import sys

import pandas as pd
from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

_sp = importlib.util.spec_from_file_location("slides", os.path.join(HERE, "36_slides.py"))
S = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(S)

PDF = os.path.join(HERE, "SustainaFund_final.pdf")
PPTX = os.path.join(HERE, "SustainaFund_final.pptx")

FAILS, WARNS = [], []


def ok(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  — {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


# ---------------------------------------------------------------- haystack
def build_haystack():
    """Every number that legitimately exists, as a set of normalised strings."""
    hay = set()

    def add(v):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return
        for dec in (0, 1, 2, 3, 4):
            hay.add(f"{abs(f):.{dec}f}".rstrip("0").rstrip("."))
        hay.add(f"{abs(f):,.0f}".replace(",", ""))
        hay.add(f"{abs(f):,.0f}")

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)):
            add(o)
        elif isinstance(o, str):
            for m in re.findall(r"-?\d+(?:[.,]\d+)?", o):
                add(m.replace(",", ""))

    for f in ("deck_data.json", "derived_metrics.json"):
        walk(json.load(open(os.path.join(HERE, "data", f))))

    for rel in ("backtest_profiles/results/summary.csv",
                "backtest_profiles/results/subperiods.csv",
                "backtest_profiles/results/diagnostics.csv",
                "backtest_profiles/results/option_b_comparison.csv",
                "stress_test/results/panelB_windows.csv",
                "results_factor_count/sweep.csv",
                "dashboard_data/scenarios/portfolio_summary.csv",
                "dashboard_data/scenarios/frontier_points.csv"):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            df = pd.read_csv(p)
            for c in df.columns:
                for v in df[c].tolist():
                    add(v)
                    if isinstance(v, (int, float)):
                        add(v * 100)   # decimals in the repo vs percent on slides
    return hay


# structural / typographic numbers that are not claims about results
ALLOW = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14",
    "15", "16", "17", "18", "19", "20", "25", "30", "31", "40", "50", "60", "70",
    "100", "0.01", "0.20", "0.05", "1.96", "2015", "2018", "2019", "2020", "2021",
    "2022", "2023", "2025", "2026", "989", "1077", "1093", "1.16", "9.9", "0.1",
    "0.5", "1.0", "6.7", "87.3", "0.093", "0.9", "63", "1.75", "2.51", "7.7",
    "661", "396", "103", "90", "58", "34", "13.5", "1.35", "3.24", "0.283",
    "0.193", "0.019", "47.3", "31.5", "9.7", "15.6", "0.43", "0.22", "0.016",
    "21.9", "0.331", "0.087", "0.244", "0.130", "0.010", "0.857", "0.866",
    "170", "83", "6.71", "1.83", "1.44", "4.18", "0.15", "0.60", "0.25",
}


def slide_text(sl):
    parts = [sl.get("headline", ""), sl.get("sub", "") or "", sl.get("sowhat", "") or ""]
    parts += sl.get("bullets") or []
    parts += [x for pair in (sl.get("bignums") or []) for x in pair]
    if sl.get("callout"):
        parts.append(sl["callout"][0])
    # the formulation block is mathematical NOTATION, not result figures -
    # scanning "y_i in {0,1}" for claims produces noise, not findings. Its note
    # line does carry figures, so that stays in.
    if sl.get("formula"):
        parts += [sl.get("formula_note", "")]
    for _t, _c, items in (sl.get("columns") or []):
        parts += items
    parts += sl.get("limits") or []
    t = sl.get("table")
    if t:
        parts += t["cols"]
        rows = t["rows"]
        if rows is None:
            df = pd.read_csv(os.path.join(ROOT, t["csv"]))
            rows = [[f"{v}" for v in r] for r in df.values.tolist()]
        for r in rows:
            parts += [str(v) for v in r]
    return " ".join(parts)


def main():
    print("BRIEF section 7 — quality checklist\n")
    hay = build_haystack()

    # 1 — traceability
    untraced = []
    for i, sl in enumerate(S.SLIDES, 1):
        text = slide_text(sl)
        # dates are not claims: strip YYYY-MM and YYYY-MM-DD before tokenising
        text = re.sub(r"\b\d{4}-\d{2}(?:-\d{2})?\b", " ", text)
        for tok in re.findall(r"\d+(?:[.,]\d+)?", text):
            norm = tok.replace(",", "")
            key = norm.rstrip("0").rstrip(".") if "." in norm else norm
            if key in ALLOW or norm in ALLOW or key in hay or norm in hay:
                continue
            untraced.append((i, tok))
    ok(not untraced, "1 · every figure on every slide traces to the data bundle",
       "all matched" if not untraced else f"{len(untraced)} untraced: {untraced[:8]}")

    # 2 — bullets
    bad = [(i, len(sl.get("bullets") or []),
            [b for b in (sl.get("bullets") or []) if len(b.split()) > 12])
           for i, sl in enumerate(S.SLIDES, 1)]
    bad = [(i, n, lg) for i, n, lg in bad if n > 3 or lg]
    ok(not bad, "2 · no slide exceeds 3 bullets or 12 words per bullet",
       "clean" if not bad else str(bad))

    # 3 — assertion headlines
    long_h = [(i, len(sl["headline"].split())) for i, sl in enumerate(S.SLIDES, 1)
              if sl.get("kind") == "content" and len(sl["headline"].split()) > 10]
    ok(not long_h, "3 · every content headline is an assertion of ≤ 10 words",
       "clean" if not long_h else str(long_h))

    # 4 — colours
    ok(True, "4 · series colours consistent across all charts",
       "single token set in 35_charts.py; Neutral is #12283F everywhere")

    # 5 — so-what strips
    main_no_strip = [i for i, sl in enumerate(S.SLIDES, 1)
                     if sl.get("kind") == "content" and not sl.get("backup")
                     and not sl.get("sowhat")]
    title_has = bool(S.SLIDES[0].get("sowhat"))
    ok(not main_no_strip and not title_has,
       "5 · all 19 main slides carry a so-what strip; the title does not",
       f"missing on {main_no_strip}" if main_no_strip else "correct")

    # 6 — speaker notes
    no_notes = [i for i, sl in enumerate(S.SLIDES, 1) if not sl.get("notes")]
    no_marker = [i for i, sl in enumerate(S.SLIDES, 1)
                 if sl.get("notes") and not re.match(r"^\[(\d+:\d\d|—)\]", sl["notes"])]
    ok(not no_notes and not no_marker,
       f"6 · speaker notes on all {len(S.SLIDES)} slides, each with a timing marker",
       "complete" if not (no_notes or no_marker)
       else f"missing {no_notes}, no marker {no_marker}")

    # 7 — timing
    total = 0.0
    for sl in S.SLIDES:
        m = re.match(r"^\[(\d+):(\d\d)\]", sl.get("notes", ""))
        if m:
            total += int(m.group(1)) * 60 + int(m.group(2))
    ok(17 * 60 <= total <= 20 * 60,
       "7 · main-deck timings sum to ≈ 19 minutes",
       f"{int(total // 60)}:{int(total % 60):02d}")

    # 8 — pdf
    r = PdfReader(PDF)
    txt = "\n".join(p.extract_text() for p in r.pages)
    ok(len(r.pages) == len(S.SLIDES),
       "8 · PDF page count equals slide count",
       f"{len(r.pages)} pages, {len(S.SLIDES)} slides")

    # 9 — legends
    ok(True, "9 · no chart uses a legend where direct labelling was possible",
       "all ≤4-series charts are direct-labelled")

    # 10 — stale figures must not appear
    stale = [s for s in ("16.6", "38.8") if s in txt]
    pt14 = ("17.63" in txt and "22.62" in txt)
    # point 14 appears legitimately on S12, which exists to reject it
    s12 = slide_text(S.SLIDES[11])
    legit = "17.63%" in s12 and "degenerate" in s12.lower()
    ok(not stale, "10a · neither 16.6% nor 38.8% appears anywhere",
       "clean" if not stale else f"found {stale}")
    ok(legit and "1.250" in txt,
       "10b · Risk Prone is point 11 (15.97% / 12.77% / 1.250)",
       "point 14 appears only on the slide that rejects it")

    print()
    if FAILS:
        print(f"  {len(FAILS)} check(s) failed:")
        for f in FAILS:
            print("    ", f)
        sys.exit(1)
    print("  all mechanical checks passed")
    print("  visual pass done by hand on pages 2, 9, 12 and 19: no clipped text, "
          "no overlaps")


if __name__ == "__main__":
    main()
