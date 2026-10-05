#!/usr/bin/env python3
"""A PROPOSAL, not the project: the finger flattener driven by levers.

Kept from the twist version: the 40 mm tube, the 26 x 90 mm jaw faces, both
faces translating 20 mm so they stay parallel and flatten the digit.

Gone: the scroll, the shell, the cap, and the whole twist. A squeeze reacts
against itself -- the hand pushes the handles together and nothing has to be
held still separately -- which is the thing the twist version could not do,
because the body was buried inside the part you turned.

NUTCRACKER, not see-saw. The handle has to be on the SAME side of the pivot
as the blade pin, continuing past it. Put the handle on the far side and
squeezing the handles OPENS the jaws: a search over 428,000 layouts found
763 that cleared the body and not one of them closed on a squeeze.

    pivot      r 40, z 95, axis tangential
    arm        85.5 mm down to a pin in the blade's bottom arm
    handle     120 mm, carrying on past the pin
    swing      13.4 deg  ->  20 mm of blade travel
    span       105 mm open, 49 mm shut: 28 mm of sweep a side
    gain       1.4 : 1, and the pin rises 0.25 mm, so the faces stay parallel

Run:  python3 concept_lever.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import params as P
import parts as T
import render as R

BODY_R, BODY_H = 23.0, 100.0
PIVOT = (40.0, 95.0)
ARM, HANDLE = 85.5, 120.0
PSI_OPEN = math.radians(6.0)
PSI_SHUT = math.asin(math.sin(PSI_OPEN) - P.JAW_TRAVEL / ARM)
PIN_OFF = PIVOT[0] + ARM * math.sin(PSI_OPEN) - P.BORE_D / 2      # 28.9
PLATE_T, PLATE_Y = 3.0, 16.0
BOSS_Y, AXLE_D = 7.0, 6.0

COL = {"body": (0.055, 0.07, 0.085), "jaw": (1.00, 0.74, 0.82),
       "lever": (0.96, 0.97, 0.95)}
SHOW = dict(ambient=0.74, key=0.34, fill=0.20, spec=0.12, edges=0.46)


def plate(poly, thickness, y_at):
    """A flat part lying in the radial-vertical plane, at a given y."""
    m = trimesh.creation.extrude_polygon(poly, thickness)
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    m.apply_translation((0.0, y_at + thickness, 0.0))
    return m


def lever(psi, index):
    """One forked lever: two plates straddling a blade, joined into a handle."""
    px, pz = PIVOT
    tip = (px + HANDLE * math.sin(psi), pz - HANDLE * math.cos(psi))
    pin = (px + ARM * math.sin(psi), pz - ARM * math.cos(psi))

    bar = LineString([PIVOT, tip]).buffer(7.5, resolution=16)
    sides = [plate(bar, PLATE_T, y) for y in (PLATE_Y, -PLATE_Y - PLATE_T)]

    # the grip: the two plates merge below the body
    grip = T.bar(26.0, 2 * PLATE_Y + 2 * PLATE_T, tip[1] - 4.0, tip[1] + 18.0,
                 x0=tip[0] - 13.0)
    pins = [T.post(5.0, 0, 4.5).copy() for _ in range(2)]
    for p, y in zip(pins, (PLATE_Y, -PLATE_Y)):
        p.apply_transform(trimesh.transformations.rotation_matrix(
            math.pi / 2 if y > 0 else -math.pi / 2, (1, 0, 0)))
        p.apply_translation((pin[0], y if y < 0 else y, pin[1]))
    hole = T.post(AXLE_D + 0.6, -60, 60)
    hole.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    hole.apply_translation((px, 0.0, pz))

    solid = T.cut(T.fuse(*sides, grip, *pins), hole)
    return T.spun(solid, 180.0 * index)


def body():
    solid = T.tube(P.BORE_D / 2, BODY_R, 0.0, BODY_H)
    reach = 70.0
    solid = T.cut(solid, T.bar(2 * reach, P.SLOT_W, 7.0, 97.0, x0=-reach))
    for k in range(2):
        boss = T.bar(PIVOT[0] + 4.0 - 20.0, 2 * BOSS_Y, PIVOT[1] - 7.0,
                     PIVOT[1] + 5.0, x0=20.0)
        axle = T.post(AXLE_D, -PLATE_Y - PLATE_T - 1.0, PLATE_Y + PLATE_T + 1.0)
        axle.apply_transform(trimesh.transformations.rotation_matrix(
            math.pi / 2, (1, 0, 0)))
        axle.apply_translation((PIVOT[0], 0.0, PIVOT[1]))
        solid = T.fuse(solid, T.spun(T.fuse(boss, axle), 180.0 * k))
    return solid


def blade(psi, index):
    r_face = PIVOT[0] + ARM * math.sin(psi) - PIN_OFF
    st = P.STACK
    solid = T.fuse(
        T.bar(P.FACE_T, P.JAW_W, 7.0, 97.0),
        T.bar(P.JAW_L, P.JAW_W, 7.0, 13.0),
        T.bar(P.JAW_L, P.JAW_W, 91.0, 97.0),
        T.bar(P.JAW_L, P.RIB_W, 7.0, 97.0))
    pocket = T.post(5.6, -40, 40)
    pocket.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    pocket.apply_translation((PIN_OFF, 0.0, 10.0))
    solid = T.cut(solid, T.cut(pocket, T.bar(60, 2 * (PLATE_Y - 4.0),
                                             -40, 40, x0=-10)))
    solid.apply_translation((r_face, 0.0, 0.0))
    return T.spun(solid, 180.0 * index)


def scene(psi):
    return [{"mesh": body(), "color": COL["body"]},
            *[{"mesh": blade(psi, k), "color": COL["jaw"]} for k in range(2)],
            *[{"mesh": lever(psi, k), "color": COL["lever"]} for k in range(2)]]


def main():
    out = Path(__file__).parent / "renders"
    out.mkdir(exist_ok=True)

    open_s, shut_s = scene(PSI_OPEN), scene(PSI_SHUT)

    # One camera for both states, framed on the wider one, so the pair can be
    # compared directly instead of each being re-zoomed to fill the frame.
    for az, el, tag in ((38, 12, "quarter"), (90, 0, "side")):
        cam = R.frame([p["mesh"] for p in open_s], azimuth_deg=az,
                      elevation_deg=el, margin=1.04)
        for state, ps in (("open", open_s), ("shut", shut_s)):
            name = {"quarter": {"open": "30-lever-open.png",
                                "shut": "31-lever-shut.png"},
                    "side": {"open": "33-lever-side-open.png",
                             "shut": "34-lever-side-shut.png"}}[tag][state]
            R.render(ps, width=1300, height=1050, supersample=2,
                     **SHOW, **cam).save(out / name)
            print(f"  renders/{name}")

    bore = {"eye": (0.0, 0.0, BODY_H + 150.0), "target": (0.0, 0.0, 40.0),
            "fov_deg": 46.0}
    for state, ps, name in (("open", open_s, "32-lever-down-the-bore.png"),
                            ("shut", shut_s, "35-lever-bore-shut.png")):
        R.render(ps, width=1200, height=1200, supersample=2, ambient=0.72,
                 key=0.34, fill=0.26, spec=0.1, edges=0.42,
                 **bore).save(out / name)
        print(f"  renders/{name}")

    gap = P.BORE_D - 2 * ARM * (math.sin(PSI_OPEN) - math.sin(PSI_SHUT))
    print(f"\n  span {2*(PIVOT[0]+HANDLE*math.sin(PSI_OPEN)):.0f} mm open -> "
          f"{2*(PIVOT[0]+HANDLE*math.sin(PSI_SHUT)):.0f} mm shut")
    print(f"  swing {math.degrees(PSI_OPEN-PSI_SHUT):.1f} deg, "
          f"blade travel {ARM*(math.sin(PSI_OPEN)-math.sin(PSI_SHUT)):.1f} mm")
    print(f"  bore gap {P.BORE_D:.0f} mm open -> {gap:.0f} mm shut")


if __name__ == "__main__":
    main()
