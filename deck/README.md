# deck/ — the final presentation

`SustainaFund_final.pptx` and `SustainaFund_final.pdf`: 29 slides — 19 main, a
divider, and 9 backup slides used only in questions. Built from source, not
hand-edited; every figure on every slide traces to a committed file.

## Rebuild from a clean clone

```bash
python3 deck/34_derived_deck_metrics.py   # ~3 s, no solver
python3 deck/35_charts.py                 # ~40 s, writes charts/
python3 deck/37_build.py                  # ~20 s, writes the PPTX and the PDF
python3 deck/38_checklist.py              # the brief's 10 quality checks
```

No solver licence is needed: everything reads committed backtest and frontier
output. `36_slides.py` is imported, not run — it is the single slide spec that
both renderers read, so the PPTX and the PDF cannot drift apart. `37_build.py`
asserts the two page counts are equal to `len(SLIDES)`.

## Which structure this follows

Two documents specified the deck and they disagree in places:
`BRIEF_build_deck.md` (formatting rules, hard rules, the quality checklist) and
`presentation_structure_EN.md.docx` (the slide-by-slide narrative). The
narrative follows the **docx**, by decision. Where they differ:

| | brief | docx | built |
|---|---|---|---|
| backup slides | 8 | 9 | **9** |
| significance test on S16 | t-test | Jobson-Korkie / Memmel | **JK/Memmel** |
| S14, S17 | not present | added | **added** |

The brief's rules still govern *how* each slide is built: ≤ 3 bullets, ≤ 12
words per bullet, assertion headlines of ≤ 10 words, direct labelling over
legends, a so-what strip on every main slide, and never inventing a number.

## The figures the docx asked for that did not exist

`34_derived_deck_metrics.py` computes them from committed backtest output and
writes `data/derived_metrics.json`. Five of six reproduce the docx exactly
(up/down capture, longest underwater stretch, JK/Memmel z, predicted-vs-realised
correlation, CVaR 95). The sixth — the recovery-day figures — does not
reproduce under any definition tried, so it is flagged
`_UNREPRODUCIBLE_DO_NOT_PRINT` in that JSON and **appears on no slide**. That is
the brief's hard rule 1 applied to the brief's own source document.

## Checklist result

All ten checks in `BRIEF_build_deck.md` section 7 pass. Check 1 — traceability —
matches every numeric token on every slide against `data/deck_data.json`,
`data/derived_metrics.json` and eight committed CSVs. Two checks (colour
consistency, legend use) are asserted by construction rather than measured:
charts draw from one colour token set in `35_charts.py`, and no chart with four
or fewer series uses a legend.

Layout was eyeballed by rendering pages 2, 9, 12 and 19 to PNG
(`PNG_PAGES=2,9,12,19 python3 deck/37_build.py`). That pass caught three real
defects — a callout overlapping bullets, a chart footnote colliding with its
axis label, and an overflowing third column — all fixed. Those `_pageNN.png`
renders are scratch and are gitignored; the 16 chart PNGs are not.

## Fonts

Charts are set in **Arial**. Inter and Source Sans 3 are not installed here, and
Helvetica Neue is macOS-only — using it would render chart text in a different
face from the slide text on any Windows machine, which is exactly the kind of
mismatch nobody notices until it is on a projector.
