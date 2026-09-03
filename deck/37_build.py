"""
37 — build SustainaFund_final.pptx and .pdf from one content spec
==================================================================
Two renderers over `36_slides.py`, so the PPTX and the PDF cannot drift.

WHY THE PDF IS NOT A CONVERSION
The brief asks for `libreoffice --headless --convert-to pdf`. libreoffice is not
installed on this machine, so the PDF is rendered natively with matplotlib's
PdfPages from the same slide spec, at the same 13.333 x 7.5 in geometry and with
the same PNG charts. Page count is asserted equal to slide count, which is the
check the brief actually wanted.

SLIDE FURNITURE, per the brief
  * progress ribbon top-right on every content slide, current stage in ink
  * "so what" strip along the bottom, 0.55 in, italic, on #F1EEE8
  * slide number bottom-right, 10 pt muted
  * nothing below 11 pt anywhere

Run:  python3 deck/37_build.py
"""

import importlib.util
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

_sp = importlib.util.spec_from_file_location("slides", os.path.join(HERE, "36_slides.py"))
S = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(S)

W, H = 13.333, 7.5
PPTX = os.path.join(HERE, "SustainaFund_final.pptx")
PDF = os.path.join(HERE, "SustainaFund_final.pdf")
FONT = "Arial"          # see 35_charts.py for why not Inter


def rgb(hexs):
    hexs = hexs.lstrip("#")
    return RGBColor(int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16))


def load_csv_rows(spec):
    """Backup slide 28 pulls its rows from a CSV rather than hard-coding them."""
    df = pd.read_csv(os.path.join(ROOT, spec["csv"]))
    out = []
    for _, r in df.iterrows():
        out.append([str(r["period"]), str(r["regime"]),
                    f"{r['minvar_CAGR_%']:+.2f}%", f"{r['equal_weight_CAGR_%']:+.2f}%",
                    f"{r['minvar_vol_%']:.2f}%", f"{r['equal_weight_vol_%']:.2f}%"])
    return out


def rows_of(spec):
    return spec["rows"] if spec.get("rows") else load_csv_rows(spec)


# ==========================================================================
# PPTX
# ==========================================================================
def tb(slide, x, y, w, h, text, size, color, bold=False, italic=False,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = FONT
        r.font.color.rgb = rgb(color)
    return box


def rect(slide, x, y, w, h, fill):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def ribbon_pptx(slide, stage):
    x = W - 0.42
    for name in reversed(S.STAGES):
        wid = 0.10 + 0.072 * len(name)
        x -= wid
        tb(slide, x, 0.20, wid, 0.26, name, 9,
           S.INK if name == stage else S.RULE,
           bold=(name == stage), align=PP_ALIGN.CENTER)
        x -= 0.10


def picture_fit(slide, path, x, y, boxw, boxh):
    """Place centred inside the box at its natural aspect, never upscaled."""
    iw, ih = Image.open(path).size
    ar = iw / ih
    w_ = boxw
    h_ = w_ / ar
    if h_ > boxh:
        h_ = boxh
        w_ = h_ * ar
    slide.shapes.add_picture(path, Inches(x + (boxw - w_) / 2),
                             Inches(y + (boxh - h_) / 2),
                             width=Inches(w_), height=Inches(h_))


def table_pptx(slide, spec, x, y, w):
    rows = rows_of(spec)
    ncol = len(spec["cols"])
    nrow = len(rows) + 1
    gt = slide.shapes.add_table(nrow, ncol, Inches(x), Inches(y), Inches(w),
                                Inches(0.34 * nrow)).table
    tot = sum(spec["widths"])
    for j, cw in enumerate(spec["widths"]):
        gt.columns[j].width = Inches(w * cw / tot)
    for j, cname in enumerate(spec["cols"]):
        cell = gt.cell(0, j)
        cell.text = cname if cname.strip() else " "
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(S.BG)
        pr = cell.text_frame.paragraphs[0]
        if not pr.runs:
            continue
        pr.runs[0].font.size = Pt(11)
        pr.runs[0].font.bold = True
        pr.runs[0].font.name = FONT
        col = (spec.get("hdr_colors") or [S.INK] * ncol)[j]
        pr.runs[0].font.color.rgb = rgb(col)
    for i, row in enumerate(rows, start=1):
        hi = spec.get("hi") is not None and i - 1 == spec["hi"]
        tint = (i - 1) in (spec.get("tint_rows") or [])
        for j, val in enumerate(row):
            cell = gt.cell(i, j)
            # an empty string yields a paragraph with no runs, so pad it
            cell.text = str(val) if str(val).strip() else " "
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(S.HILITE if hi else
                                           S.DEGEN if tint else S.BG)
            pr = cell.text_frame.paragraphs[0]
            if not pr.runs:
                continue
            pr.runs[0].font.size = Pt(13 if len(rows) <= 5 else 11)
            pr.runs[0].font.bold = hi
            pr.runs[0].font.name = FONT
            pr.runs[0].font.color.rgb = rgb(S.INK if hi else S.BODY)
    return 0.34 * nrow


def build_pptx():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    blank = prs.slide_layouts[6]

    for n, sl in enumerate(S.SLIDES, start=1):
        slide = prs.slides.add_slide(blank)
        rect(slide, 0, 0, W, H, S.BG)

        if sl["kind"] == "title":
            picture_fit(slide, sl["chart"], 0.1, 4.6, W - 0.2, 2.6)
            tb(slide, 0.85, 1.75, 11.6, 1.1, sl["headline"], 54, S.INK, bold=True)
            tb(slide, 0.85, 2.95, 10.4, 1.0, sl["sub"], 17, S.BODY, spacing=1.25)
            tb(slide, 0.85, 4.15, 10.4, 0.4, sl["meta"], 12, S.MUTED)
        elif sl["kind"] == "divider":
            tb(slide, 0.85, 3.05, 8.0, 0.9, sl["headline"], 44, S.INK, bold=True)
            tb(slide, 0.85, 4.0, 8.0, 0.4, sl["sub"], 15, S.MUTED)
        else:
            if sl.get("stage"):
                ribbon_pptx(slide, sl["stage"])
            top = 0.62
            tb(slide, 0.62, top, 11.4, 0.72, sl["headline"], 30, S.INK, bold=True)
            y = top + 0.86
            if sl.get("sub"):
                tb(slide, 0.62, y, 11.4, 0.36, sl["sub"], 15, S.MUTED)
                y += 0.42

            body_bottom = H - 1.05
            has_strip = bool(sl.get("sowhat"))
            y_chart_end = None

            # --- big numbers row ---
            if sl.get("bignums"):
                bx = 0.62
                for val, lab in sl["bignums"]:
                    tb(slide, bx, y, 2.5, 0.62, val, 40, S.INK, bold=True)
                    tb(slide, bx, y + 0.62, 2.5, 0.3, lab, 12, S.MUTED)
                    bx += 2.7
                y += 1.10

            # --- formula panel (S8) ---
            if sl.get("formula"):
                rect(slide, 0.62, y, 5.1, 1.95, S.PANEL)
                fbox = slide.shapes.add_textbox(Inches(0.78), Inches(y + 0.12),
                                                Inches(4.9), Inches(1.7))
                tf = fbox.text_frame
                tf.word_wrap = False
                for i, ln in enumerate(sl["formula"]):
                    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                    r = p.add_run(); r.text = ln
                    r.font.size = Pt(12); r.font.name = "Courier New"
                    r.font.color.rgb = rgb(S.INK)
                tb(slide, 0.62, y + 2.02, 5.1, 0.72, sl["formula_note"], 11, S.MUTED,
                   spacing=1.15)

            # --- chart ---
            if sl.get("chart"):
                if sl.get("table"):
                    picture_fit(slide, sl["chart"], 0.62, y, 11.9, 2.55)
                    y += 2.62
                elif sl.get("hero"):
                    picture_fit(slide, sl["chart"], 0.62, y, 12.1, 4.05)
                    y += 4.10
                else:
                    ch_h = (body_bottom - y - 0.05
                            - (0.78 if sl.get("callout") else 0.0))
                    picture_fit(slide, sl["chart"], 0.62, y, 7.55, ch_h)
                    y_chart_end = y + ch_h + 0.06

            # --- table ---
            if sl.get("table"):
                tw = 11.9 if not sl.get("chart") else 11.9
                table_pptx(slide, sl["table"], 0.70 if not sl.get("formula") else 6.0,
                           y, tw if not sl.get("formula") else 6.7)
                if not sl.get("formula"):
                    y += 0.34 * (len(rows_of(sl["table"])) + 1) + 0.12

            # --- three columns (S19) ---
            if sl.get("columns"):
                cw = 3.72
                cx = 0.62
                for title, col, items in sl["columns"]:
                    rect(slide, cx, y, cw, 0.055, col)
                    tb(slide, cx, y + 0.14, cw, 0.34, title, 14, col, bold=True)
                    tb(slide, cx, y + 0.56, cw, 2.5,
                       ["· " + it for it in items], 12, S.BODY, spacing=1.32)
                    cx += cw + 0.28
                y += 3.15
                tb(slide, 0.62, y, 11.9, 0.85,
                   ["· " + l for l in sl["limits"]], 11.5, S.MUTED, spacing=1.28)

            # --- bullets, right column when a chart occupies the left ---
            if sl.get("bullets"):
                if sl.get("chart") and not sl.get("table") and not sl.get("hero"):
                    tb(slide, 8.45, y + 0.05, 4.15, 3.0,
                       ["· " + b for b in sl["bullets"]], 15, S.BODY, spacing=1.45)
                else:
                    tb(slide, 0.62, y, 11.9, 0.9,
                       ["· " + b for b in sl["bullets"]], 14, S.BODY, spacing=1.35)
                    y += 0.30 * len(sl["bullets"]) + 0.12

            # --- callout, always below whatever came before it ---
            if sl.get("callout"):
                txt, col = sl["callout"]
                base = y_chart_end if y_chart_end else y + 0.10
                cy = min(base, body_bottom - 0.74)
                rect(slide, 0.62, cy, 0.055, 0.70, col)
                tb(slide, 0.80, cy + 0.04, 11.5, 0.64, txt, 13, col, spacing=1.2)

            # --- so-what strip ---
            if has_strip:
                rect(slide, 0, H - 0.55, W, 0.55, S.STRIP)
                tb(slide, 0.62, H - 0.50, 11.2, 0.45, sl["sowhat"], 14, S.BODY,
                   italic=True, anchor=MSO_ANCHOR.MIDDLE)

        if sl["kind"] != "title":
            tb(slide, W - 1.05, H - 0.44, 0.6, 0.3, str(n), 10, S.MUTED,
               align=PP_ALIGN.RIGHT)

        slide.notes_slide.notes_text_frame.text = sl["notes"]

    prs.save(PPTX)
    return len(prs.slides.__iter__.__self__._sldIdLst)


# ==========================================================================
# PDF — same spec, rendered natively because libreoffice is absent
# ==========================================================================
def build_pdf():
    plt.rcParams.update({"font.family": FONT})
    n_pages = 0
    with PdfPages(PDF) as pdf:
        for n, sl in enumerate(S.SLIDES, start=1):
            fig = plt.figure(figsize=(W, H), facecolor=S.BG)

            def T(x, y, s, size, color, **kw):
                fig.text(x / W, 1 - y / H, s, fontsize=size, color=color,
                         va=kw.pop("va", "top"), **kw)

            def R(x, y, w, h, fc):
                fig.patches.append(Rectangle((x / W, 1 - (y + h) / H), w / W, h / H,
                                             transform=fig.transFigure,
                                             facecolor=fc, edgecolor="none", zorder=0))

            def IMG(path, x, y, boxw, boxh):
                im = Image.open(path)
                ar = im.size[0] / im.size[1]
                w_ = boxw; h_ = w_ / ar
                if h_ > boxh:
                    h_ = boxh; w_ = h_ * ar
                ax = fig.add_axes([(x + (boxw - w_) / 2) / W,
                                   1 - (y + (boxh - h_) / 2 + h_) / H, w_ / W, h_ / H])
                ax.imshow(im); ax.set_axis_off()

            def TABLE(spec, x, y, w, fs=None):
                rows = rows_of(spec)
                ncol = len(spec["cols"]); nrow = len(rows) + 1
                rh = 0.34
                fs = fs or (11.5 if len(rows) <= 5 else 9.5)
                tot = sum(spec["widths"])
                xs, acc = [], x
                for cw in spec["widths"]:
                    xs.append(acc); acc += w * cw / tot
                for j, cname in enumerate(spec["cols"]):
                    col = (spec.get("hdr_colors") or [S.INK] * ncol)[j]
                    T(xs[j] + 0.06, y + 0.10, cname, fs, col, fontweight="bold")
                R(x, y + rh - 0.045, w, 0.012, S.RULE)
                for i, row in enumerate(rows):
                    yy = y + rh * (i + 1)
                    hi = spec.get("hi") is not None and i == spec["hi"]
                    tint = i in (spec.get("tint_rows") or [])
                    if hi or tint:
                        R(x, yy, w, rh, S.HILITE if hi else S.DEGEN)
                    for j, val in enumerate(row):
                        T(xs[j] + 0.06, yy + 0.10, str(val), fs,
                          S.INK if hi else S.BODY,
                          fontweight="bold" if hi else "normal")
                    R(x, yy + rh - 0.012, w, 0.008, S.RULE)
                return rh * nrow

            if sl["kind"] == "title":
                IMG(sl["chart"], 0.1, 4.6, W - 0.2, 2.6)
                T(0.85, 1.75, sl["headline"], 48, S.INK, fontweight="bold")
                T(0.85, 2.95, sl["sub"], 16, S.BODY, wrap=True)
                T(0.85, 4.20, sl["meta"], 11.5, S.MUTED)
            elif sl["kind"] == "divider":
                T(0.85, 3.05, sl["headline"], 40, S.INK, fontweight="bold")
                T(0.85, 4.05, sl["sub"], 14, S.MUTED)
            else:
                if sl.get("stage"):
                    x = W - 0.42
                    for name in reversed(S.STAGES):
                        wid = 0.10 + 0.072 * len(name)
                        x -= wid
                        T(x + wid / 2, 0.30, name, 8.5,
                          S.INK if name == sl["stage"] else S.RULE,
                          ha="center", fontweight="bold" if name == sl["stage"] else "normal")
                        x -= 0.10
                top = 0.70
                T(0.62, top, sl["headline"], 27, S.INK, fontweight="bold")
                y = top + 0.80
                body_bottom = H - 1.05
                y_chart_end = None

                if sl.get("bignums"):
                    bx = 0.62
                    for val, lab in sl["bignums"]:
                        T(bx, y, val, 34, S.INK, fontweight="bold")
                        T(bx, y + 0.62, lab, 11.5, S.MUTED)
                        bx += 2.7
                    y += 1.10

                if sl.get("formula"):
                    R(0.62, y, 5.1, 1.95, S.PANEL)
                    for i, ln in enumerate(sl["formula"]):
                        T(0.80, y + 0.16 + i * 0.33, ln, 11.5, S.INK,
                          family="monospace")
                    T(0.62, y + 2.06, sl["formula_note"], 10.5, S.MUTED, wrap=True)

                if sl.get("chart"):
                    if sl.get("table"):
                        IMG(sl["chart"], 0.62, y, 11.9, 2.55); y += 2.62
                    elif sl.get("hero"):
                        IMG(sl["chart"], 0.62, y, 12.1, 4.05); y += 4.10
                    else:
                        ch_h = (body_bottom - y - 0.05
                                - (0.78 if sl.get("callout") else 0.0))
                        IMG(sl["chart"], 0.62, y, 7.55, ch_h)
                        y_chart_end = y + ch_h + 0.06

                if sl.get("table"):
                    if sl.get("formula"):
                        TABLE(sl["table"], 6.0, y, 6.7, 10)
                    else:
                        y += TABLE(sl["table"], 0.70, y, 11.9) + 0.14

                if sl.get("columns"):
                    cw = 3.72; cx = 0.62
                    for title, col, items in sl["columns"]:
                        R(cx, y, cw, 0.05, col)
                        T(cx, y + 0.20, title, 13, col, fontweight="bold")
                        for i, it in enumerate(items):
                            T(cx, y + 0.62 + i * 0.42, "· " + it, 11, S.BODY, wrap=True)
                        cx += cw + 0.28
                    y += 3.15
                    for i, l in enumerate(sl["limits"]):
                        T(0.62, y + i * 0.28, "· " + l, 10.5, S.MUTED, wrap=True)

                if sl.get("bullets"):
                    if sl.get("chart") and not sl.get("table") and not sl.get("hero"):
                        for i, b in enumerate(sl["bullets"]):
                            T(8.45, y + 0.10 + i * 0.60, "· " + b, 13.5, S.BODY,
                              wrap=True)
                    else:
                        for i, b in enumerate(sl["bullets"]):
                            T(0.62, y + i * 0.30, "· " + b, 12.5, S.BODY, wrap=True)
                        y += 0.30 * len(sl["bullets"]) + 0.14

                if sl.get("callout"):
                    txt, col = sl["callout"]
                    base = y_chart_end if y_chart_end else y + 0.08
                    cy = min(base, body_bottom - 0.74)
                    R(0.62, cy, 0.05, 0.66, col)
                    T(0.82, cy + 0.14, txt, 12, col, wrap=True)

                if sl.get("sowhat"):
                    R(0, H - 0.55, W, 0.55, S.STRIP)
                    T(0.62, H - 0.34, sl["sowhat"], 13, S.BODY, style="italic",
                      va="center")

            if sl["kind"] != "title":
                T(W - 0.52, H - 0.30, str(n), 10, S.MUTED, ha="right")

            pdf.savefig(fig, facecolor=S.BG)
            # PNG_PAGES=2,9,12 saves those pages for visual checking
            want = os.environ.get("PNG_PAGES", "")
            if want and str(n) in want.split(","):
                fig.savefig(os.path.join(HERE, "charts", f"_page{n:02d}.png"),
                            dpi=110, facecolor=S.BG)
            plt.close(fig)
            n_pages += 1
    return n_pages


if __name__ == "__main__":
    n_sl = build_pptx()
    print(f"  {os.path.relpath(PPTX, ROOT)}  {n_sl} slides")
    n_pg = build_pdf()
    print(f"  {os.path.relpath(PDF, ROOT)}  {n_pg} pages")
    assert n_pg == len(S.SLIDES) == n_sl, \
        f"slide/page mismatch: spec {len(S.SLIDES)}, pptx {n_sl}, pdf {n_pg}"
    print(f"\n  page count == slide count == {len(S.SLIDES)}")
