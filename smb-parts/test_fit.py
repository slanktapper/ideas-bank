#!/usr/bin/env python3
"""Checks that have to hold before any of this is worth printing.

    python3 test_fit.py

No test framework: this is a script of assertions, like the other projects
here. It builds the real panels, so it is slow-ish and honest.
"""

from __future__ import annotations

import sys

import numpy as np
import trimesh

import params as P
import parts as T
import vignettes as V

fails = []


def check(name, cond, detail=""):
    print("  %-52s %s" % (name, "ok" if cond else "FAIL"))
    if not cond:
        fails.append("%s %s" % (name, detail))


print("params")
check("section closes: 2*LEG_T + GAP == FACE_H",
      abs(2 * P.LEG_T + P.GAP - P.FACE_H) < 1e-9,
      "%.3f vs %.3f" % (2 * P.LEG_T + P.GAP, P.FACE_H))
check("legs are thick enough to print (>= 2.5 mm)", P.LEG_T >= 2.5,
      "LEG_T=%.2f -- raise FACE_H or the board is too thick for 25 mm"
      % P.LEG_T)
check("a game pixel is at least 1.5 nozzles", P.PIXEL >= P.NOZZLE * 1.5,
      "PIXEL=%.3f NOZZLE=%.2f" % (P.PIXEL, P.NOZZLE))
check("art is a whole number of tiles tall",
      abs(P.ART_TILES_H * P.TILE - P.FACE_H) < 1e-9)
check("panel plus its tongue fits the bed in X",
      P.PANEL_L + P.LAP_L <= P.BED_X - 10.0,
      "%.1f vs %.1f" % (P.PANEL_L + P.LAP_L, P.BED_X - 10.0))
check("rail is within 25 mm of three feet",
      abs(P.TOTAL_L - 914.4) <= 25.0, "%.1f mm" % P.TOTAL_L)

print("\nvignettes")
for v in V.RAIL:
    w, h, grid = v.pixels()
    check("%-12s crop is %d x %d px" % (v.key, P.PANEL_TILES * 16, P.ART_TILES_H * 16),
          w == P.PANEL_TILES * 16 and h == P.ART_TILES_H * 16)
    n = len(v.colours())
    check("%-12s colours fit the 8 AMS slots (%d)" % (v.key, n), n <= 8)
    covered = sum(1 for row in grid for c in row if c != v.background)
    frac = covered / float(w * h)
    check("%-12s art covers 15-85%% of the face (%.0f%%)" % (v.key, 100 * frac),
          0.15 <= frac <= 0.85)

print("\npanels")
built = []
for i, vig in enumerate(V.RAIL):
    whole, body, art = T.panel(vig, first=(i == 0), last=(i == len(V.RAIL) - 1))
    built.append(whole)
    lo, hi = whole.bounds
    check("%-12s watertight solid" % vig.key, whole.is_volume)
    check("%-12s height is exactly FACE_H" % vig.key,
          abs((hi[2] - lo[2]) - P.FACE_H) < 1e-6,
          "%.3f" % (hi[2] - lo[2]))
    check("%-12s art stands %.1f mm proud, no more" % (vig.key, P.RELIEF),
          abs(lo[1] + P.RELIEF) < 1e-6, "%.3f" % lo[1])
    check("%-12s depth is FACE_T + LEG_D" % vig.key,
          abs(hi[1] - (P.FACE_T + P.LEG_D)) < 1e-6, "%.3f" % hi[1])

print("\nthe half-lap between panels")
for i in range(len(built) - 1):
    a = built[i].copy()
    b = built[i + 1].copy()
    b.apply_translation((P.PANEL_L, 0.0, 0.0))
    inter = trimesh.boolean.intersection([a, b])
    vol = 0.0 if inter is None or inter.is_empty else float(inter.volume)
    check("panels %d-%d do not interfere (%.3f mm3)" % (i + 1, i + 2, vol),
          vol < 1e-3)
    # and the tongue really does reach into its neighbour
    check("panel %d's tongue reaches past the join" % (i + 1),
          built[i].bounds[1][0] > P.PANEL_L + P.LAP_L - 0.01,
          "%.2f" % built[i].bounds[1][0])

print("\nassembled")
total = built[-1].bounds[1][0] + (len(built) - 1) * P.PANEL_L
check("last panel ends flush at %.0f mm" % P.TOTAL_L,
      abs(total - P.TOTAL_L) < 1e-6, "%.2f" % total)

print()
if fails:
    print("%d FAILED:" % len(fails))
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("all checks passed")
