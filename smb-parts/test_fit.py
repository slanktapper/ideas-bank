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


print("the shelf, and the bracket that has to fit it")
check("slot is the bar plus the fit", abs(P.SLOT - (P.MAT_T + P.FIT)) < 1e-9)
check("grip is shorter than the bar stands proud (%.1f < %.2f)"
      % (P.GRIP, P.BAR_RISE), P.GRIP < P.BAR_RISE,
      "the cap would bottom out on the shelf floor before seating")
hang = (P.FACE_H - P.WEB_T) - P.BAR_RISE - P.MAT_T
check("face reaches past the shelf's front elevation (%.2f mm spare)" % hang,
      hang >= 0.0, "%.2f -- the face stops short of the shelf underside" % hang)
check("inner leg does not reach the shelf floor",
      P.WEB_T + P.GRIP < P.WEB_T + P.BAR_RISE)

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
check("an art panel fits the bed (%.1f)" % P.PANEL_L,
      P.PANEL_L <= P.BED_X - 10.0)

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

print("\nthe clip")
check("top lip clears the bracket body by CLIP_FIT",
      abs((P.FACE_H - P.HOOK_T - P.HOOK_LIP_TOP) - P.BODY_Z1 - P.CLIP_FIT) < 1e-9,
      "the body has to pass between the two lips")
check("bottom lip clears the bracket body by CLIP_FIT",
      abs(P.BODY_Z0 - (P.HOOK_T + P.HOOK_LIP_BOT) - P.CLIP_FIT) < 1e-9)
check("top hook actually overlaps the plate (%.2f mm)"
      % (P.BRK_Z1 - (P.FACE_H - P.HOOK_T - P.HOOK_LIP_TOP)),
      P.BRK_Z1 > P.FACE_H - P.HOOK_T - P.HOOK_LIP_TOP)
check("the snap is in the 0.1-0.3 Rob asked for (%.2f)" % P.CLIP_GRAB,
      0.10 <= P.CLIP_GRAB <= 0.30)
check("the bead is shallower than the lip it sits on",
      P.GRAB_H < P.HOOK_LIP_BOT)
check("art still clears the shelf underside (%.2f mm)"
      % ((P.FACE_H - P.WEB_T) - P.BAR_RISE - P.MAT_T),
      (P.FACE_H - P.WEB_T) - P.BAR_RISE - P.MAT_T >= 0)
check("depth off the shelf stays under 15 mm (%.1f)" % P.DEPTH, P.DEPTH <= 15.0)

print("\nbrackets")
brk = T.bracket()
check("bracket is a watertight solid", brk.is_volume)
check("bracket is one connected body (%d)" % brk.body_count, brk.body_count == 1,
      "the body has to reach the web past both lips")
check("bracket is FACE_H tall", abs(brk.bounds[1][2] - P.FACE_H) < MESH_TOL)
pos = T.bracket_positions()
check("%d brackets, none hanging off the shelf" % len(pos),
      pos[0] >= -1e-9 and pos[-1] + P.BRACKET_W <= P.SHELF_L + 1e-9)
check("a bracket straddles the joint between the two art panels",
      any(x < P.SHELF_L / 2 < x + P.BRACKET_W for x in pos))

print("\nart panels")
made = {}
for vig in V.RAIL:
    for idx in range(P.PANELS_PER_SHELF):
        whole, body, art = T.panel(vig, idx)
        made.setdefault(vig.key, []).append(whole)
        lo, hi = whole.bounds
        tag = "%s-%d" % (vig.key, idx + 1)
        check("%-14s watertight solid" % tag, whole.is_volume)
        check("%-14s is exactly FACE_H tall" % tag,
              abs((hi[2] - lo[2]) - P.FACE_H) < MESH_TOL, "%.4f" % (hi[2] - lo[2]))
        check("%-14s art stands %.1f mm proud, no more" % (tag, P.RELIEF),
              abs(lo[1] + P.RELIEF) < MESH_TOL, "%.4f" % lo[1])
        check("%-14s hooks reach back to HOOK_D" % tag,
              abs(hi[1] - (P.ART_T + P.HOOK_D)) < MESH_TOL, "%.4f" % hi[1])

print("\nthe art actually clips onto the bracket")
probe = made[V.RAIL[1].key][0]
b = T.bracket()
b.apply_translation((40.0, 0.0, 0.0))
inter = trimesh.boolean.intersection([probe, b])
vol = 0.0 if inter is None or inter.is_empty else float(inter.volume)
check("there IS interference, or nothing snaps (%.3f mm3)" % vol, vol > 0.1)
if vol > 0.1:
    lo, hi = inter.bounds
    check("interference is only the bead, %.3f mm deep" % (hi[1] - lo[1]),
          abs((hi[1] - lo[1]) - P.CLIP_GRAB) < 0.02,
          "anything else means the hooks foul the bracket")
    check("interference sits at the bead's Y",
          abs(lo[1] - (P.ART_T + P.BRK_T - P.CLIP_GRAB)) < MESH_TOL)
    check("interference is one place, not several (%d)" % inter.body_count,
          inter.body_count == 1)
    check("interference stays inside the bracket's span",
          lo[0] >= 40.0 - MESH_TOL and hi[0] <= 40.0 + P.BRACKET_W + MESH_TOL)

print("\nthe two art panels of a shelf")
for key, pair in made.items():
    a = pair[0].copy()
    bb = pair[1].copy()
    bb.apply_translation((P.PANEL_L, 0.0, 0.0))
    i2 = trimesh.boolean.intersection([a, bb])
    v2 = 0.0 if i2 is None or i2.is_empty else float(i2.volume)
    check("%-12s panels do not interfere (%.3f mm3)" % (key, v2), v2 < 1e-3)
    check("%-12s pair ends flush at the shelf length" % key,
          abs(bb.bounds[1][0] - P.SHELF_L) < MESH_TOL, "%.3f" % bb.bounds[1][0])

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
      abs(comb.bounds[1][1] - (P.SLOT_Y0 + max(P.COUPON_SLOTS) + P.LEG_T)) < MESH_TOL,
      "%.3f" % comb.bounds[1][1])
check("ladder is the same height as the real rail",
      abs(comb.bounds[1][2] - P.FACE_H) < MESH_TOL)

stubs, test_brk, _ = C.clip_ladder()
check("clip ladder stubs are a watertight solid", stubs.is_volume)
check("clip ladder brackets the design grab (%.2f)" % P.CLIP_GRAB,
      min(P.CLIP_GRABS) < P.CLIP_GRAB < max(P.CLIP_GRABS))
check("every clip label has a glyph",
      all(c in C.FONT for g in P.CLIP_GRABS for c in "%d" % round(g * 100)))
check("clip ladder ships a bracket to try the stubs on", test_brk.is_volume)

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
