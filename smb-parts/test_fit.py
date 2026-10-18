#!/usr/bin/env python3
"""Checks that have to hold before any of this is worth printing.

    python3 test_fit.py

No test framework: a script of assertions, like the other projects here. It
builds the real panels, so it is slow-ish and honest.
"""

from __future__ import annotations

import sys

import trimesh

import params as P
import coupons as C
import parts as T
import vignettes as V

# Tolerance for anything read off a mesh. manifold3d works in float32, so a
# bound comes back a few nanometres from the arithmetic -- 1e-6 mm is tighter
# than the representation, let alone the printer. Exact params are still
# compared exactly.
MESH_TOL = 1e-3

fails = []


def check(name, cond, detail=""):
    print("  %-56s %s" % (name, "ok" if cond else "FAIL"))
    if not cond:
        fails.append("%s %s" % (name, detail))


print("the shelf, and the cap that has to fit it")
check("slot is the bar plus the fit", abs(P.SLOT - (P.MAT_T + P.FIT)) < 1e-9)
check("grip is shorter than the bar stands proud (%.1f < %.2f)"
      % (P.GRIP, P.BAR_RISE), P.GRIP < P.BAR_RISE,
      "the cap would bottom out on the shelf floor before seating")
hang = (P.FACE_H - P.WEB_T) - P.BAR_RISE - P.MAT_T
check("face reaches past the shelf's front elevation (%.2f mm spare)" % hang,
      hang >= 0.0, "%.2f -- the face stops short of the shelf underside" % hang)
check("inner leg does not reach the shelf floor",
      P.WEB_T + P.GRIP < P.WEB_T + P.BAR_RISE)
check("depth taken off the shelf stays under 12 mm (%.1f)" % P.DEPTH,
      P.DEPTH <= 12.0)

print("\nthe art")
check("art is a whole number of tiles tall",
      abs(P.ART_TILES_H * P.TILE - P.FACE_H) < 1e-9)
check("art height is within 1 mm of the 25 Rob asked for (%.2f)" % P.FACE_H,
      abs(P.FACE_H - 25.0) <= 1.0)
check("a game pixel is at least 1.5 nozzles (%.2f)" % (P.PIXEL / P.NOZZLE),
      P.PIXEL >= P.NOZZLE * 1.5)
check("tiles divide evenly into panels",
      P.TILES_PER_SHELF % P.PANELS_PER_SHELF == 0)
check("panels add back up to the shelf",
      abs(P.PANELS_PER_SHELF * P.PANEL_L - P.SHELF_L) < 1e-9)
check("panel plus its tongue fits the bed (%.1f)" % (P.PANEL_L + P.LAP_L),
      P.PANEL_L + P.LAP_L <= P.BED_X - 10.0)

print("\nvignettes")
for v in V.RAIL:
    w, h, grid = v.pixels()
    check("%-12s crop is %d x %d px" % (v.key, P.TILES_PER_SHELF * 16, P.ART_TILES_H * 16),
          w == P.TILES_PER_SHELF * 16 and h == P.ART_TILES_H * 16)
    n = len(v.colours())
    check("%-12s colours fit the 8 AMS slots (%d)" % (v.key, n), n <= 8)
    covered = sum(1 for row in grid for c in row if c != v.background)
    frac = covered / float(w * h)
    check("%-12s art covers 15-85%% of the face (%.0f%%)" % (v.key, 100 * frac),
          0.15 <= frac <= 0.85)

print("\npanels")
by_vig = {}
for vig in V.RAIL:
    made = []
    for idx in range(P.PANELS_PER_SHELF):
        whole, body, art = T.panel(vig, idx)
        made.append(whole)
        lo, hi = whole.bounds
        tag = "%s-%d" % (vig.key, idx + 1)
        check("%-14s watertight solid" % tag, whole.is_volume)
        check("%-14s is exactly FACE_H tall" % tag,
              abs((hi[2] - lo[2]) - P.FACE_H) < MESH_TOL, "%.4f" % (hi[2] - lo[2]))
        check("%-14s art stands %.1f mm proud, no more" % (tag, P.RELIEF),
              abs(lo[1] + P.RELIEF) < MESH_TOL, "%.4f" % lo[1])
        check("%-14s depth is DEPTH" % tag,
              abs(hi[1] - P.DEPTH) < MESH_TOL, "%.4f" % hi[1])
    by_vig[vig.key] = made

print("\nthe half-lap between a shelf's two panels")
for key, made in by_vig.items():
    a = made[0].copy()
    b = made[1].copy()
    b.apply_translation((P.PANEL_L, 0.0, 0.0))
    inter = trimesh.boolean.intersection([a, b])
    vol = 0.0 if inter is None or inter.is_empty else float(inter.volume)
    check("%-12s panels do not interfere (%.3f mm3)" % (key, vol), vol < 1e-3)
    check("%-12s pair ends flush at the shelf length" % key,
          abs(b.bounds[1][0] - P.SHELF_L) < MESH_TOL, "%.3f" % b.bounds[1][0])

print("\nthe test coupons")
check("the ladder brackets the design slot (%.1f)" % P.SLOT,
      min(P.COUPON_SLOTS) < P.SLOT < max(P.COUPON_SLOTS),
      "a ladder that does not straddle 4.4 cannot confirm it")
check("the design slot is one of the rungs", P.SLOT in P.COUPON_SLOTS)
check("every rung is a different width", len(set(P.COUPON_SLOTS)) == len(P.COUPON_SLOTS))
check("a two-digit label fits the coupon face",
      2 * (C.DIGIT_H * P.DIGIT_PX) + P.DIGIT_PX <= P.FACE_H
      and C.DIGIT_W * P.DIGIT_PX <= P.COUPON_W)
check("every label has a glyph",
      all(c in C.FONT for s_ in P.COUPON_SLOTS for c in "%d" % round(s_ * 10)))
check("the spine is thinner than the web, so it snaps not tears",
      P.SPINE_T < P.WEB_T)

comb, total = C.fit_ladder()
check("fit ladder is a watertight solid", comb.is_volume)
check("ladder is %.0f mm, a couple of minutes of printing" % total,
      total <= 80.0)
check("ladder depth follows the widest rung",
      abs(comb.bounds[1][1] - (P.FACE_T + max(P.COUPON_SLOTS) + P.LEG_T)) < MESH_TOL,
      "%.3f" % comb.bounds[1][1])
check("ladder is the same height as the real rail",
      abs(comb.bounds[1][2] - P.FACE_H) < MESH_TOL)

sample, t0 = C.art_sample(V.RAIL[1])
check("art sample is a watertight solid", sample.is_volume)
check("art sample is two whole tiles wide",
      abs(sample.bounds[1][0] - 2 * P.TILE) < MESH_TOL, "%.3f" % sample.bounds[1][0])

print()
if fails:
    print("%d FAILED:" % len(fails))
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("all checks passed")
