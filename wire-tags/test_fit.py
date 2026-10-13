#!/usr/bin/env python3
"""Assertions about the design, run before you spend filament on it.

    python3 test_fit.py

These are design rules rather than unit tests. Editing params.py is the whole
point of this project, and most of the ways to get it wrong are silent: a
mouth so tight the arm crazes or so slack the tag falls off, a wall thinner
than the perimeters that have to build it, lettering that runs into a clip or
off the edge of the plate, a recess that is not a whole number of layers so
the colour change lands in the wrong place, a bore roof steep enough to need
support, a label that comes out mirrored because someone "fixed" the mirror
in glyphs.py. Each one costs a print to find and nothing to check.

Every check runs against every size in `FAMILY`, because a rule that holds at
4.5 mm and fails at 7.5 is exactly the kind of thing a single-size check
misses.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import glyphs
import params as P
import tag as T

FAILS: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)


def overhang_ok(poly, limit_deg: float = 45.5, bridge: float = None):
    """Worst unsupported overhang on a section boundary, in degrees.

    The part is extruded along the cable, so every surface except the two end
    faces is vertical in Y and printability is decided entirely by this 2D
    boundary: an edge whose outward normal points downwards is an overhang,
    and its angle from vertical -- 0 for a wall, 90 for a ceiling -- is what
    the slicer judges.

    Two downward-facing things are not overhangs and are excluded: the face
    the part rests on, and a flat ceiling no wider than `bridge`, which is
    the short span over the bore that FDM bridges on purpose.
    """
    from shapely.geometry.polygon import orient
    bridge = P.BRIDGE if bridge is None else bridge
    poly = orient(poly, 1.0)      # exterior CCW, holes CW; the sign of the
                                  # normal below depends on it, and shapely's
                                  # booleans do not guarantee either way
    worst, where = 0.0, None
    for ring in [poly.exterior, *poly.interiors]:
        pts = np.asarray(ring.coords)
        seg = np.diff(pts, axis=0)
        mid = (pts[:-1] + pts[1:]) / 2.0
        length = np.linalg.norm(seg, axis=1)
        keep = length > 1e-7
        seg, mid, length = seg[keep], mid[keep], length[keep]
        if not len(seg):
            continue
        # With the orientation above, (dy, -dx) is the outward normal of
        # every ring: the material is always on its left.
        n = np.c_[seg[:, 1], -seg[:, 0]] / length[:, None]
        ang = np.degrees(np.arcsin(np.clip(-n[:, 1], 0.0, 1.0)))
        live = (n[:, 1] < -1e-9) & (mid[:, 1] > 0.05)          # not the bed face
        live &= ~((ang > 88.0) & (length <= bridge + 0.05))    # not a bridge
        if live.any() and ang[live].max() > worst:
            worst = float(ang[live].max())
            where = tuple(np.round(mid[live][ang[live].argmax()], 2))
    return worst <= limit_deg, worst, where


def main() -> int:
    print(f"wire-tags: {len(P.FAMILY)} sizes, nominal {P.CABLE_D} mm\n")

    for d, _ in P.FAMILY:
        p = P.plan(d, "ETHERNET", glyphs.measure("ETHERNET", P.CAP_H))
        snap = d - p["mouth"]
        print(f"{d:g} mm cable")
        check("mouth is narrower than the cable, so it snaps",
              0 < snap, f"snap {snap:.2f}")
        check("snap stays inside what a 1.6 mm PETG arm will take",
              snap / d <= 0.16, f"{100 * snap / d:.0f}% of diameter")
        check("bore clears the cable",
              p["bore"] > d, f"bore {p['bore']:.2f}")
        check("grip ribs pinch, but do not crush",
              0.0 <= 2 * P.RIB - P.FIT <= 0.35,
              f"{2 * P.RIB - P.FIT:+.2f} interference")
        check("clip wall is a whole number of perimeters",
              abs(round(p["wall"] / P.NOZZLE) - p["wall"] / P.NOZZLE) < 1e-9,
              f"{p['wall'] / P.NOZZLE:.0f} x {P.NOZZLE}")
        check("plate is wider than the clip standing on it",
              p["plate_w"] >= 2 * p["r_out"] + 1.0,
              f"{p['plate_w']:.1f} vs {2 * p['r_out']:.1f}")
        check("cable sits in a cradle, not on a tangent",
              0.2 <= P.SINK <= p["plate_t"] - 1.0, f"sink {P.SINK}")
        check("plate under the cradle is still 4 layers thick",
              p["plate_t"] - P.SINK >= 4 * P.LAYER_H,
              f"{p['plate_t'] - P.SINK:.2f} mm")

        # printability of the two sections that make the part
        outer = T.outer_section(p)
        hole = T.bore_section(p)
        solid = outer.difference(hole).difference(T.mouth_section(p, 1.0))
        ok, worst, where = overhang_ok(solid)
        check("nothing overhangs past 45 degrees, so no supports",
              ok, f"worst {worst:.0f} deg from vertical at {where}")
        check("the clip is one body, not an arm and a crumb",
              solid.geom_type == "Polygon" or len(solid.geoms) == 1,
              solid.geom_type)
        check("mouth tilt keeps the upper lip's underside printable",
              45.0 <= P.MOUTH_TILT <= 60.0,
              f"{P.MOUTH_TILT:g} deg tilt -> {90 - P.MOUTH_TILT:g} deg overhang")
        print()

    # ---------------------------------------------------------- the lettering
    print("lettering")
    check("recess is a whole number of layers",
          abs(round(P.TEXT_H / P.LAYER_H) - P.TEXT_H / P.LAYER_H) < 1e-9,
          f"{P.TEXT_H / P.LAYER_H:.0f} x {P.LAYER_H}")
    plain, _, _ = glyphs.outline("R", 6.0, mirror=False)
    mirrored, _, _ = glyphs.outline("R", 6.0, mirror=True)
    check("the label is mirrored, because it is read from the bed face",
          not plain.equals_exact(mirrored, 1e-9)
          and abs(plain.area - mirrored.area) < 1e-6)

    longest = max(P.STARTER, key=lambda lb: glyphs.measure(lb[0], P.CAP_H))
    for label, d in P.STARTER + [("A", 4.5), longest]:
        body, letters, p = T.build(d, label)
        lo, hi = letters.bounds
        room_y = p["plate_l"] / 2.0 - P.CLIP_H - P.CLIP_GAP
        check(f"{label}: letters clear of both clips",
              hi[1] <= room_y + 1e-6 and lo[1] >= -room_y - 1e-6,
              f"{hi[1]:.1f} vs {room_y:.1f}")
        check(f"{label}: letters clear of the plate edge",
              hi[0] <= p["plate_w"] / 2.0 - P.EDGE + 1e-6,
              f"{hi[0]:.1f} vs {p['plate_w'] / 2.0 - P.EDGE:.1f}")
        check(f"{label}: lettering is readable, not shrunk to nothing",
              p["text_cap"] >= P.CAP_MIN - 1e-9, f"cap {p['text_cap']:.2f}")
        check(f"{label}: body and lettering are both printable solids",
              body.is_watertight and letters.is_watertight
              and body.volume > 0 and letters.volume > 0)
        check(f"{label}: lettering sits in the recess cut for it",
              abs(letters.bounds[0][2]) < 1e-9
              and abs(letters.bounds[1][2] - P.TEXT_H) < 1e-9)
        check(f"{label}: the tag is one piece",
              body.body_count == 1, f"{body.body_count} bodies")
        check(f"{label}: fits the bed",
              body.extents[0] < P.BED[0] and body.extents[1] < P.BED[1])
    print()

    # -------------------------------------------------------------- the coupon
    print("fit coupon")
    body, info = T.coupon(P.CABLE_D)
    check("coupon is one piece", body.body_count == 1, f"{body.body_count}")
    check("coupon has a station per step",
          len(info["plans"]) == len(P.COUPON_STEPS))
    check("coupon steps straddle nominal",
          min(P.COUPON_STEPS) < 0 < max(P.COUPON_STEPS)
          and 0.0 in P.COUPON_STEPS)
    check("coupon stations do not run into each other",
          info["pitch"] >= 2 * max(q["r_out"] for q in info["plans"]) + 4.0,
          f"pitch {info['pitch']:.1f}")
    check("coupon fits the bed",
          body.extents[0] < P.BED[0] and body.extents[1] < P.BED[1],
          f"{body.extents[0]:.0f} x {body.extents[1]:.0f} mm")
    check("coupon numbers are on the top face, where you can read them",
          body.bounds[1][2] >= P.PLATE_T - 1e-9)

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
