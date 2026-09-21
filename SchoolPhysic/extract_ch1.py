#!/usr/bin/env python3
"""Extract graphs (vector figures) directly from the Yakovlev PDF by cropping page regions."""
import os
import sys
import pymupdf

PDF = "/Users/evgenykon/Documents/obsidian/Женя/Projects/Наука/Школьный физмат/Fisica - yakovlev.pdf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ch1")
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(PDF)

# Each figure: (output_name, page_number_1indexed, figure_caption_text)
FIGURES = [
    ("1_2_derivative", 15, "Рис. 1.2"),         # parabola y=x^2 (derivative intro)
    ("1_5_circular", 42, "Рис. 1.17"),          # uniform circular motion
    ("1_19_path_uniform", 45, "Рис. 1.19"),     # path under uniform motion
    ("1_22_path_nonuniform", 46, "Рис. 1.22"),  # path under non-uniform motion
    ("1_26_hooke", 55, "Рис. 1.26"),            # Hooke's law
    ("1_31_friction", 60, "Рис. 1.31"),         # friction
    ("1_39_pressure", 70, "Рис. 1.39"),         # archimedes cylinder
    ("1_51_lever", 87, "Рис. 1.51"),            # lever
    ("1_2_kinematics", 40, "Рис. 1.15"),        # horizontal throw
    ("1_36_hydrostatic", 67, "Рис. 1.36"),      # hydrostatic pressure
]


def find_caption(pno, caption):
    page = doc[pno]
    for b in page.get_text("blocks"):
        if caption in b[4]:
            return pymupdf.Rect(b[0], b[1], b[2], b[3])
    return None


def crop_figure(name, pno, caption, margin_top=6, margin_x=10):
    page = doc[pno]
    cap = find_caption(pno, caption)
    if cap is None:
        print(f"  !! caption not found on page {pno+1}: {caption}")
        return
    # find drawings that sit just above the caption and overlap horizontally.
    # cluster by proximity to the caption to avoid pulling in text formulas.
    cand = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.y1 <= cap.y0 + 4 and r.x1 > cap.x0 - 60 and r.x0 < cap.x1 + 60:
            cand.append(r)
    if not cand:
        print(f"  !! no drawings found on page {pno+1}: {caption}")
        return
    # sort by distance to caption (bottom-most first), keep a tight cluster
    cand.sort(key=lambda r: (cap.y0 - r.y1))
    keep = [cand[0]]
    for r in cand[1:]:
        # keep if it overlaps vertically with the growing cluster
        if any(not (r.y1 < c.y0 or r.y0 > c.y1) for c in keep):
            keep.append(r)
    minx = min(r.x0 for r in keep) - margin_x
    miny = min(r.y0 for r in keep) - margin_top
    maxx = max(r.x1 for r in keep) + 18
    # bottom bound: just above the caption so the label is not included, but keep
    # enough room for axis labels near the bottom of the figure
    maxy = cap.y0 - 2
    clip = pymupdf.Rect(minx, miny, maxx, maxy)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=clip)
    path = os.path.join(OUT, name + ".png")
    pix.save(path)
    print(f"  ok {name}  page {pno+1}  clip=({round(minx)},{round(miny)},{round(maxx)},{round(maxy)})")


for name, pno, cap in FIGURES:
    crop_figure(name, pno - 1, cap)
print("done")
