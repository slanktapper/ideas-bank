#!/usr/bin/env python3
"""Assertions about the tags, run before anything is sliced.

    python3 test_fit.py

A label is a simple part, so these checks are not about whether it is
printable -- a 1.2 mm slab always is. They are about the three things that
would come off the printer looking fine and still be wrong:

1.  The lettering reading BACKWARDS. The word is in the face at z=0, which is
    the face against the plate, so it is read from below. Text laid out the
    way it looks in a viewer comes off the printer mirrored. This was caught
    in a render, after the first version had already been built, and it is the
    check most likely to save a reprint.

2.  The white skin being too THIN to hide the colour behind it. Rob asked for
    two layers; two layers of a pale filament over black reads grey. The floor
    here is 0.60 mm, and the set is built at 0.80.

3.  The two parts not adding up to the tag -- a gap, or an overlap, between
    the white and the colour. Either shows as a seam or as a slicer resolving
    an intersection however it feels like.

Everything else is dimensions, and dimensions are cheap to check.
"""

from __future__ import annotations

import sys

from shapely import affinity
from shapely.geometry import LineString

import build as B
import params as P

FAILS: list[str] = []
CHECKS = 0

# The floor a pale filament needs to hide a dark one. 0.40 mm reads grey,
# 0.60 mm is the working minimum, 0.80 mm is safe over black. See params.py.
OPACITY_FLOOR = 0.60


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def layer_checks():
    print("layers")
    check("the tag is a whole number of layers",
          abs(P.TAG_T / P.LAYER - round(P.TAG_T / P.LAYER)) < 1e-9,
          f"{P.TAG_T:.2f} mm = {round(P.TAG_T/P.LAYER)} x {P.LAYER:.2f}")
    check("the white skin is a whole number of layers",
          abs(P.WHITE_D / P.LAYER - round(P.WHITE_D / P.LAYER)) < 1e-9,
          f"{P.WHITE_D:.2f} mm = {P.WHITE_LAYERS} x {P.LAYER:.2f}")
    check("the white is thick enough to hide the colour behind it",
          P.WHITE_D >= OPACITY_FLOOR - 1e-9,
          f"{P.WHITE_D:.2f} mm against a {OPACITY_FLOOR:.2f} mm floor "
          f"-- this is the check Rob's '2 layers' question failed")
    check("there is letter colour left behind the white",
          P.COLOUR_BEHIND > 0,
          f"{P.COLOUR_BEHIND:.2f} mm, so the letters have a body to join onto")


def geometry_checks(built, cap):
    print("geometry")
    slab = B.prism(B.outline(), P.TAG_T)

    o = B.outline().bounds
    check("the tag is exactly the size asked for",
          abs((o[2]-o[0]) - P.TAG_W) < 1e-6 and abs((o[3]-o[1]) - P.TAG_H) < 1e-6,
          f"{o[2]-o[0]:.3f} x {o[3]-o[1]:.3f} mm, corners r{P.CORNER_R:.1f}")

    for key, (white, colour, word, _) in built.items():
        check(f"{word}: both parts are watertight",
              white.is_watertight and colour.is_watertight)

        total = white.volume + colour.volume
        check(f"{word}: white + colour is exactly the plain slab",
              abs(total - slab.volume) < 1e-3,
              f"{total:.4f} vs {slab.volume:.4f} mm3, "
              f"out by {total-slab.volume:+.2e} -- no gap, no overlap")

        wz, cz = white.bounds, colour.bounds
        check(f"{word}: the white is a skin on the printed face",
              abs(wz[0][2]) < 1e-6 and abs(wz[1][2] - P.WHITE_D) < 1e-6,
              f"z {wz[0][2]:.3f}..{wz[1][2]:.3f}, and z=0 is the face "
              f"against the plate")
        check(f"{word}: the colour runs the full thickness",
              abs(cz[0][2]) < 1e-6 and abs(cz[1][2] - P.TAG_T) < 1e-6,
              f"z {cz[0][2]:.3f}..{cz[1][2]:.3f} -- the letters reach the "
              f"printed face")
        check(f"{word}: the colour is one solid, not loose tiles in a pocket",
              colour.body_count == 1,
              "letters continuous with the body behind them, nothing to glue")


def lettering_checks(built, cap, face):
    print("lettering")
    words = [w for _, w, _ in P.TAGS]

    # One size for the set. common_cap solves it from the widest word, so this
    # is really a check that no tag quietly got its own size.
    again, by_w, by_h = B.common_cap(face, words)
    check("all three tags are set at one cap height",
          abs(again - cap) < 1e-12,
          f"{cap:.3f} mm, set by width ({by_w:.2f}) rather than height "
          f"({by_h:.2f})")

    for word in words:
        g = B.word_polygon(face, word, cap)
        x0, y0, x1, y1 = g.bounds
        check(f"{word}: the word fits inside the side margins",
              x0 >= P.MARGIN_X - 1e-6 and x1 <= P.TAG_W - P.MARGIN_X + 1e-6,
              f"x {x0:.2f}..{x1:.2f} inside {P.MARGIN_X:.1f}.."
              f"{P.TAG_W-P.MARGIN_X:.1f}")
        check(f"{word}: the word fits inside the top and bottom margins",
              y0 >= P.MARGIN_Y - 1e-6 and y1 <= P.TAG_H - P.MARGIN_Y + 1e-6,
              f"y {y0:.2f}..{y1:.2f} inside {P.MARGIN_Y:.1f}.."
              f"{P.TAG_H-P.MARGIN_Y:.1f}")

    # Baselines must agree across the set, or the three tags look wrong side
    # by side even though each one is centred. Cap-box centring is what buys
    # this; ink centring would not, because ABS and PETG have round letters
    # that overshoot and PLA does not.
    baselines = []
    for word in words:
        g = B.word_polygon(face, word, cap)
        flat, _ = face.line(word, cap)        # unplaced, baseline at y=0
        baselines.append(g.bounds[1] - flat.bounds[1])
    check("the three words share one baseline",
          max(baselines) - min(baselines) < 1e-9,
          f"baseline at y={baselines[0]:.4f} mm on all three")

    # The one that matters most.
    for word in words:
        placed = B.word_polygon(face, word, cap)
        unmirrored = affinity.scale(placed, xfact=-1.0, yfact=1.0,
                                    origin=(P.TAG_W / 2, P.TAG_H / 2))
        flat, _ = face.line(word, cap)
        fx0, _, fx1, _ = flat.bounds
        expect = affinity.translate(flat,
                                    P.TAG_W / 2 - (fx0 + fx1) / 2,
                                    P.TAG_H / 2 - cap / 2)
        check(f"{word}: the lettering is mirrored, so it reads off the plate",
              unmirrored.equals_exact(expect, 1e-9),
              "un-mirroring the model reproduces the plain glyph outline")


def print_checks(built, cap, face):
    print("what the slicer will see")
    for key, (white, colour, word, _) in built.items():
        # Counters are islands: the hole in a P or an A is white, and the
        # letter encircles it, so it cannot touch the rest of the skin. That
        # is expected, not a fault -- every island sits flat on the plate and
        # welds to the colour beside it. Worth pinning so it is never
        # "fixed" by someone filling the counters in.
        check(f"{word}: white is a skin plus one island per counter",
              white.body_count >= 1,
              f"{white.body_count} bodies = 1 skin + "
              f"{white.body_count-1} enclosed counter(s)")

    # A stem has to be wide enough that the slicer lays real extrusions in it
    # rather than a thin-wall gap fill. Two 0.4 mm lines is the floor.
    face_, cap_ = face, cap
    for key, (_, _, word, _) in built.items():
        g = B.word_polygon(face_, word, cap_)
        hit = LineString([(0, P.TAG_H / 2), (P.TAG_W, P.TAG_H / 2)]).intersection(g)
        spans = [s for s in (hit.geoms if hasattr(hit, 'geoms') else [hit])
                 if not s.is_empty]
        narrowest = min(s.bounds[2] - s.bounds[0] for s in spans)
        check(f"{word}: the narrowest stem is wider than two extrusions",
              narrowest >= 0.8,
              f"{narrowest:.2f} mm at mid-height, against a 0.80 mm floor")


def main():
    print("filament-labels — fit checks")
    built, cap, face = B.build(verbose=False)
    layer_checks()
    geometry_checks(built, cap)
    lettering_checks(built, cap, face)
    print_checks(built, cap, face)

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
