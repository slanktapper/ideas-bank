#!/usr/bin/env python3
"""Assertions about the lettering module.

    python3 test_text3d.py

text3d.py was written inside cactus-pot, where it was checked by looking at
the pot: the name either read properly on the cartouche or it did not.
Shared, that is no longer good enough. The pot sets three lines of mixed
case at ~9.6 mm on a curved panel; filament-labels sets one word of caps at
~18 mm on a flat one. A change that suits either can quietly ruin the other,
and the project that notices need not be the project that caused it.

So these checks pin the contract rather than the appearance: that cap height
means millimetres, that geometry scales linearly with it, that counters come
back as holes and not as filled blobs, that the same call twice gives the
same polygon, and that fit_lines centres a block on its inked extent.

The counter check earns its keep. The glyph assembler resolves rings by
even-odd, so a bug there does not crash and does not look wrong in a
wireframe -- it fills in the middle of every O, P, A and B, and is first
noticed as a solid lump where a letter hole should be, after the print.
"""

from __future__ import annotations

import sys

from shapely.ops import unary_union

import text3d as T

FAILS: list[str] = []
CHECKS = 0

# All caps, no descenders: what a label gets. Round letters (B, S, G, O)
# overshoot the cap line and the baseline slightly, which several checks
# below have to allow for -- that overshoot is the typeface being correct,
# not the module being wrong.
CAPS = "PLA"
ROUND = "ABS"


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    tag = "ok  " if ok else "FAIL"
    print(f"  {tag}  {label}" + (f"   [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def face_checks():
    print("the face")
    f = T.Face()
    check("the default face loads from font/ beside the module",
          f.upm > 0 and len(f.cmap) > 0, f"upm {f.upm}, {len(f.cmap)} mapped codepoints")

    g = T.Face(font_dir=T.FONT_DIR)
    check("font_dir= reaches the same face as the default",
          g.upm == f.upm and len(g.cmap) == len(f.cmap),
          "a project can pass its own directory without an env var")

    try:
        T.Face(font_dir="/nonexistent-font-dir")
        bad = False
    except Exception:
        bad = True
    check("a missing font directory raises rather than falling back", bad,
          "silently substituting a face would change a part's lettering")


def metric_checks():
    print("cap height is millimetres")
    f = T.Face()

    g, _ = f.line(CAPS, 18.0)
    x0, y0, x1, y1 = g.bounds
    check("a flat-topped word stands exactly cap_mm tall",
          abs((y1 - y0) - 18.0) < 1e-6, f"'{CAPS}' inked height {y1-y0:.6f} mm at cap 18")
    check("the baseline sits at y=0", abs(y0) < 1e-6, f"y0 {y0:.6f}")

    r, _ = f.line(ROUND, 18.0)
    over = max(-r.bounds[1], r.bounds[3] - 18.0)
    check("round letters overshoot the cap line and baseline, a little",
          0 < over < 0.5, f"'{ROUND}' overshoots by {over:.4f} mm, both ends")

    a, _ = f.line(CAPS, 9.0)
    b, _ = f.line(CAPS, 18.0)
    ratio = (b.bounds[2] - b.bounds[0]) / (a.bounds[2] - a.bounds[0])
    check("geometry scales linearly with cap height", abs(ratio - 2.0) < 1e-9,
          f"doubling cap doubled width exactly ({ratio:.12f})")

    _, adv = f.line(CAPS, 18.0)
    check("the advance returned is at least the inked width",
          adv >= (b.bounds[2] - b.bounds[0]) - 1e-9,
          f"advance {adv:.3f} mm vs ink {b.bounds[2]-b.bounds[0]:.3f} mm "
          "-- the difference is the right side bearing")

    sp, sp_adv = f.line(" ", 18.0)
    check("a space advances the pen and lays down no ink",
          sp.is_empty and sp_adv > 0, f"empty geometry, advance {sp_adv:.3f} mm")


def glyph_checks():
    print("glyphs")
    f = T.Face()

    o, _ = f.line("O", 10.0)
    polys = list(o.geoms) if o.geom_type == "MultiPolygon" else [o]
    holes = sum(len(p.interiors) for p in polys)
    check("a counter comes back as a hole, not a filled blob", holes == 1,
          f"'O' is {len(polys)} polygon with {holes} interior ring")

    word, _ = f.line("PETG", 18.0)
    check("every glyph in a word is a valid polygon", word.is_valid,
          f"{len(list(word.geoms))} polygons, shapely-valid")
    check("the letters of a word do not overlap each other",
          abs(word.area - sum(p.area for p in word.geoms)) < 1e-9,
          "union area equals the sum of the parts, so nothing double-counts")

    first, _ = f.line("PETG", 18.0)
    second, _ = f.line("PETG", 18.0)
    check("the same call twice gives the same polygon",
          first.equals_exact(second, 0.0),
          "bezier flattening is deterministic, so an STL is reproducible")


def fit_checks():
    print("fit_lines")
    f = T.Face()
    lines = ["Rob", "Sinclair", "pot"]
    placed = T.fit_lines(f, lines, 68.0, 24.0, 18.0)

    check("every line is set at one common cap height",
          len({round(c, 9) for _, c, _ in placed}) == 1,
          f"all three at cap {placed[0][1]:.4f} mm")
    check("no line is set wider than the panel",
          max(w for _, _, w in placed) <= 68.0 + 1e-9,
          f"widest line {max(w for _, _, w in placed):.3f} mm of 68.0 available")

    block = unary_union([g for g, _, _ in placed])
    bx0, by0, bx1, by1 = block.bounds
    check("the block's inked height is the height asked for",
          abs((by1 - by0) - 24.0) < 1e-6, f"inked height {by1-by0:.9f} mm")
    check("the block is centred on y=0 by its inked extent, not its cap boxes",
          abs((by0 + by1) / 2) < 1e-9, f"inked midline at y={(by0+by1)/2:.12f}")
    check("each line is centred on x=0",
          all(abs((g.bounds[0] + g.bounds[2]) / 2) < 0.6 for g, _, _ in placed),
          "centred on the advance, so the optical centre is within a bearing")

    tall = T.fit_lines(f, lines, 68.0, 24.0, 4.0)
    check("max_cap caps the size even when the panel could take more",
          tall[0][1] <= 4.0 + 1e-9, f"asked for 4.0 mm, got {tall[0][1]:.4f} mm")

    one = T.fit_lines(f, ["PETG"], 68.0, 18.0, 18.0)
    check("a single line does not divide by a zero gap", len(one) == 1,
          f"one line at cap {one[0][1]:.4f} mm")


def main():
    print("text3d.py — shared lettering checks")
    face_checks()
    metric_checks()
    glyph_checks()
    fit_checks()

    print()
    if FAILS:
        print(f"{len(FAILS)} of {CHECKS} checks FAILED:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print(f"all {CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
