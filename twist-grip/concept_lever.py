#!/usr/bin/env python3
"""A PROPOSAL, not the project: the finger flattener driven by levers.

Kept from the twist version: the 40 mm bore, the 26 x 90 mm jaw faces, and
both faces translating 20 mm so they stay parallel. Gone: the scroll, the
shell, the cap, and the whole twist -- a squeeze reacts against itself, so
one hand supplies both the force and the reaction.

This revision moves the drive to the middle of the jaw and gives the jaw a
real prismatic guide, which is what the stub-pin joint at the jaw's foot
never was:

    body        extruded out beside each jaw into two flanking walls
    runners     a 45 deg vee rail on each side face of the jaw, near each
                end but set 14 mm in from it, running along the travel
    grooves     matching vees in the body walls, 20 mm longer than the rail
    drive       a dowel at mid height, through fork, wall window and a
                vertical slot in the jaw

The slot is not slop. The jaw is now locked to pure radial travel, while a
pin on a swinging arm must move in z as well; the slot takes that 4.4 mm
and passes on only the radial push.

    pivot       r 25, z 95, on the outer face of the body wall
    arm         47.4 mm to the dowel at z 52, mid jaw
    handle      66.3 mm, carrying on past the dowel (nutcracker, not
                see-saw: the handle has to be on the SAME side of the
                pivot as the dowel, or a squeeze opens the jaws)
    swing       25.0 deg  ->  20 mm of jaw travel
    span        106 mm open, 50 mm shut

Run:  python3 concept_lever.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import params as P
import parts as T
import render as R

# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------

BODY_R, BODY_H = 23.0, 100.0           # the tube around the 40 mm bore
JAW_Z0, JAW_Z1 = 7.0, 97.0             # the 90 mm of jaw
JAW_MID = (JAW_Z0 + JAW_Z1) / 2.0      # 52.0
JAW_L = 42.0                           # how far a jaw reaches out radially
WEB_T = 3.0                            # the jaw's side webs

# The y stack, measured out from the mid plane. Every number below is forced
# by the one above it: the jaw's half width sets where the body wall can
# start, the groove depth sets how thick that wall has to be, and the wall's
# outer face sets where the lever's fork can run.
JAW_Y = P.JAW_W / 2.0                  # 13.00  jaw side face
WALL_Y0 = JAW_Y + 0.35                 # 13.35  body wall, inner face
RAIL_H, GROOVE_H = 2.9, 3.0            #        45 deg vees
RAIL_TIP = JAW_Y + RAIL_H              # 15.90
GROOVE_TIP = WALL_Y0 + GROOVE_H        # 16.35
WALL_Y1 = GROOVE_TIP + P.WALL_MIN      # 17.95  skin left over the groove
PLATE_Y0 = WALL_Y1 + 1.0               # 18.95  lever fork plate, inner face
PLATE_T = 4.0
PLATE_Y1 = PLATE_Y0 + PLATE_T          # 22.95
PAD_Y1 = PLATE_Y1 + 5.0                #        grip pad, flared outward

RAIL_X = (19.0, 39.0)                  # runner, in jaw-local x
GROOVE_X = (RAIL_X[0], RAIL_X[1] + P.JAW_TRAVEL)       # 19 .. 59, absolute
WALL_X = (15.0, GROOVE_X[1] + 2.0)                     # 15 .. 61
WALL_Z = (6.0, BODY_H)
RAIL_Z = (JAW_Z0 + 14.0, JAW_Z1 - 14.0)                # 21, 83: in from each end

PIVOT = (25.0, 95.0)
YOKE_X = 25.0                          # where the lever drives the jaw
ARM = math.hypot(PIVOT[1] - JAW_MID, P.JAW_TRAVEL)     # 47.42
PSI_OPEN = math.asin(P.JAW_TRAVEL / ARM)               # 24.95 deg
PSI_SHUT = 0.0                         # shut is the arm hanging straight down
HANDLE = 66.3
BRACE_D = 14.0                         # the fork's tie, clear above the body

AXLE_D, DOWEL_D = 6.0, 5.0
YOKE_BOSS_X, YOKE_BOSS_L = 18.0, 16.0
YOKE_BOSS_Z = (41.5, 57.5)
WINDOW_X, WINDOW_Z = (21.0, 49.0), (44.0, 56.0)

COL = {"body": (0.055, 0.07, 0.085), "jaw": (1.00, 0.74, 0.82),
       "lever": (0.96, 0.97, 0.95), "pin": (0.85, 0.30, 0.22)}
# The body is black by choice, which is fine for an assembly and useless for
# a detail: at a base of 0.055 every face lands within a few percent of black
# whatever the lighting does, so a 45 degree groove flank is invisible. The
# detail figures draw the same part in grey.
COL_DETAIL = (0.46, 0.49, 0.54)
SHOW = dict(ambient=0.74, key=0.34, fill=0.20, spec=0.12, edges=0.46)


# ---------------------------------------------------------------------------
# kinematics
# ---------------------------------------------------------------------------

def pin_at(psi):
    """The dowel centre, in the x-z plane."""
    return (PIVOT[0] + ARM * math.sin(psi), PIVOT[1] - ARM * math.cos(psi))


def face_at(psi):
    """Radius of the jaw's gripping face: 20 mm open, 0 shut."""
    return pin_at(psi)[0] - YOKE_X


SLOT_W = DOWEL_D + 0.35
SLOT_Z = (pin_at(PSI_SHUT)[1] - DOWEL_D / 2.0 - 0.3,
          pin_at(PSI_OPEN)[1] + DOWEL_D / 2.0 + 0.3)


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

def prism_x(poly, x0, x1):
    """Extrude a cross-section drawn in (y, z) along the x axis."""
    m = trimesh.creation.extrude_polygon(poly, x1 - x0)
    t = np.eye(4)
    t[:3, :3] = np.array([[0.0, 0.0, 1.0],      # polygon's extrusion -> x
                          [1.0, 0.0, 0.0],      # polygon's X         -> y
                          [0.0, 1.0, 0.0]])     # polygon's Y         -> z
    m.apply_transform(t)
    m.apply_translation((x0, 0.0, 0.0))
    return m


def vee(y_root, y_tip, zc, sign):
    """A 45 degree vee in (y, z), apex outward at y_tip.

    Drawn from a root well inside the part it belongs to, so the boolean
    has real overlap to work with rather than a coincident face. Because
    the flanks are at 45 degrees the half height always equals the distance
    back from the apex, which is what keeps the rail and the groove
    parallel however far each is extended.
    """
    half = abs(y_tip - y_root)
    return Polygon([(sign * y_root, zc - half),
                    (sign * y_root, zc + half),
                    (sign * y_tip, zc)])


def plate(poly, thickness, y_at):
    """A flat part lying in the x-z plane, occupying y_at .. y_at+thickness."""
    m = trimesh.creation.extrude_polygon(poly, thickness)
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    m.apply_translation((0.0, y_at + thickness, 0.0))
    return m


def along_y(mesh_zspan, sign):
    """Lay a z-axis post along y; sign picks which way it points."""
    m = mesh_zspan.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        -math.pi / 2 * sign, (1, 0, 0)))
    return m


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------

def _wall(sign):
    """One of the two walls the body extrudes out beside a jaw."""
    w = T.bar(WALL_X[1] - WALL_X[0], WALL_Y1 - WALL_Y0,
              WALL_Z[0], WALL_Z[1], x0=WALL_X[0])
    w.apply_translation((0.0, sign * (WALL_Y0 + WALL_Y1) / 2.0, 0.0))
    for zc in RAIL_Z:
        w = T.cut(w, prism_x(vee(WALL_Y0 - 1.35, GROOVE_TIP, zc, sign),
                             GROOVE_X[0], GROOVE_X[1]))
    # the window the drive dowel reaches through
    w = T.cut(w, T.bar(WINDOW_X[1] - WINDOW_X[0], 2 * (WALL_Y1 + 1.0),
                       WINDOW_Z[0], WINDOW_Z[1], x0=WINDOW_X[0]))
    axle = along_y(T.post(AXLE_D, WALL_Y1 - 1.0, PLATE_Y1 + 1.0), sign)
    axle.apply_translation((PIVOT[0], 0.0, PIVOT[1]))
    return T.fuse(w, axle)


def body(expose=False):
    """expose drops the near wall of the +x jaw, to show a runner in place."""
    solid = T.tube(P.BORE_D / 2.0, BODY_R, 0.0, BODY_H)
    reach = 80.0
    # the jaws pass clean through; cut before the walls go on, since the
    # walls start exactly where this slot stops
    solid = T.cut(solid, T.bar(2 * reach, P.SLOT_W, JAW_Z0, JAW_Z1, x0=-reach))
    for k in range(2):
        for sign in (1, -1):
            if expose and k == 0 and sign > 0:
                continue
            solid = T.fuse(solid, T.spun(_wall(sign), 180.0 * k))
    return solid


def jaw(psi, index):
    """A face, two side webs, end caps, the yoke boss, and four runners."""
    web = []
    for sign in (1, -1):
        w = T.bar(JAW_L, WEB_T, JAW_Z0, JAW_Z1)
        w.apply_translation((0.0, sign * (JAW_Y - WEB_T / 2.0), 0.0))
        web.append(w)

    solid = T.fuse(
        T.bar(P.FACE_T, P.JAW_W, JAW_Z0, JAW_Z1),                 # the face
        *web,
        T.bar(JAW_L, P.JAW_W, JAW_Z0, JAW_Z0 + 6.0),              # end caps
        T.bar(JAW_L, P.JAW_W, JAW_Z1 - 6.0, JAW_Z1),
        T.bar(YOKE_BOSS_L, P.JAW_W, *YOKE_BOSS_Z, x0=YOKE_BOSS_X))

    for sign in (1, -1):
        for zc in RAIL_Z:
            solid = T.fuse(solid, prism_x(vee(JAW_Y - 2.0, RAIL_TIP, zc, sign),
                                          *RAIL_X))

    solid = T.cut(solid, T.bar(SLOT_W, 2 * (JAW_Y + 2.0), *SLOT_Z,
                               x0=YOKE_X - SLOT_W / 2.0))
    solid.apply_translation((face_at(psi), 0.0, 0.0))
    return T.spun(solid, 180.0 * index)


def lever(psi, index, drop_near=False):
    """A fork: two plates outboard of the body walls, tied above the body."""
    px, pz = PIVOT

    def at(s):
        return (px + s * math.sin(psi), pz - s * math.cos(psi))

    top, tip = at(-BRACE_D), at(HANDLE)
    spine = LineString([top, tip]).buffer(7.5, resolution=16)

    pieces = []
    for sign in (1, -1):
        if drop_near and sign > 0:
            continue
        y0 = PLATE_Y0 if sign > 0 else -PLATE_Y1
        pieces.append(plate(spine, PLATE_T, y0))
        # the pad's inner corner has to stay off the tube: at the fork's
        # own y the tube still reaches x 13.0, so it starts outboard of that
        pad = T.bar(26.0, PAD_Y1 - PLATE_Y0, tip[1] - 6.0, tip[1] + 22.0,
                    x0=tip[0] - 9.0)
        pad.apply_translation((0.0, sign * (PLATE_Y0 + PAD_Y1) / 2.0, 0.0))
        pieces.append(pad)

    # the tie has to clear the body, so it sits above the tube's top face
    brace = T.bar(15.0, 2 * PLATE_Y1, top[1] - 5.0, top[1] + 5.0,
                  x0=top[0] - 7.5)
    pieces.append(brace)

    hole = along_y(T.post(AXLE_D + 0.6, -60.0, 60.0), 1)
    hole.apply_translation((px, 0.0, pz))
    pin_x, pin_z = at(ARM)
    pin_hole = along_y(T.post(DOWEL_D + 0.1, -60.0, 60.0), 1)
    pin_hole.apply_translation((pin_x, 0.0, pin_z))

    solid = T.cut(T.fuse(*pieces), hole, pin_hole)
    return T.spun(solid, 180.0 * index)


def dowel(psi, index):
    x, z = pin_at(psi)
    m = along_y(T.post(DOWEL_D, -PLATE_Y1 - 1.0, PLATE_Y1 + 1.0), 1)
    m.apply_translation((x, 0.0, z))
    return T.spun(m, 180.0 * index)


def scene(psi, pins=True):
    out = [{"mesh": body(), "color": COL["body"]}]
    out += [{"mesh": jaw(psi, k), "color": COL["jaw"]} for k in range(2)]
    out += [{"mesh": lever(psi, k), "color": COL["lever"]} for k in range(2)]
    if pins:
        out += [{"mesh": dowel(psi, k), "color": COL["pin"]} for k in range(2)]
    return out


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def _overlap(a, b):
    try:
        m = trimesh.boolean.intersection([a, b])
        return 0.0 if m is None or m.is_empty else abs(m.volume)
    except Exception:
        return float("nan")


def checks():
    fails = []

    def ok(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
        if not cond:
            fails.append(name)

    mid = PSI_OPEN / 2.0
    ok("each jaw face travels 20 mm",
       abs((face_at(PSI_OPEN) - face_at(PSI_SHUT)) - P.JAW_TRAVEL) < 1e-9,
       f"{face_at(PSI_OPEN):.1f} -> {face_at(PSI_SHUT):.1f} mm")
    ok("the faces meet when shut", abs(face_at(PSI_SHUT)) < 1e-9)
    ok("the bore is clear when open",
       abs(face_at(PSI_OPEN) - P.BORE_D / 2.0) < 1e-9)
    ok("the wall keeps a printable skin over its groove",
       WALL_Y1 - GROOVE_TIP >= P.WALL_MIN,
       f"{WALL_Y1 - GROOVE_TIP:.2f} mm, min {P.WALL_MIN}")
    ok("rail flanks clear groove flanks",
       0.2 < (GROOVE_TIP - RAIL_TIP) / math.sqrt(2.0) < 0.5,
       f"{(GROOVE_TIP - RAIL_TIP) / math.sqrt(2.0):.2f} mm")
    ok("the groove is a jaw-travel longer than the runner",
       abs((GROOVE_X[1] - GROOVE_X[0])
           - (RAIL_X[1] - RAIL_X[0]) - P.JAW_TRAVEL) < 1e-9)
    ok("runners sit in from each end of the jaw",
       RAIL_Z[0] - JAW_Z0 > 10.0 and JAW_Z1 - RAIL_Z[1] > 10.0,
       f"{RAIL_Z[0] - JAW_Z0:.0f} mm in from each end")
    ok("the drive is at the middle of the jaw",
       abs(pin_at(PSI_OPEN)[1] - JAW_MID) < 1e-9, f"z {JAW_MID:.0f}")
    ok("the slot is long enough for the pin's rise",
       SLOT_Z[0] <= pin_at(PSI_SHUT)[1] - DOWEL_D / 2.0
       and SLOT_Z[1] >= pin_at(PSI_OPEN)[1] + DOWEL_D / 2.0,
       f"{pin_at(PSI_OPEN)[1] - pin_at(PSI_SHUT)[1]:.2f} mm of rise")

    for tag, psi in (("open", PSI_OPEN), ("half", mid), ("shut", PSI_SHUT)):
        b, j, l, d = (body(), jaw(psi, 0), lever(psi, 0), dowel(psi, 0))
        ok(f"jaw runs free in the body, {tag}", _overlap(b, j) < 1e-6,
           f"{_overlap(b, j):.3f} mm^3")
        ok(f"lever clears the body, {tag}", _overlap(b, l) < 1e-6)
        ok(f"lever clears the jaw, {tag}", _overlap(j, l) < 1e-6)
        ok(f"dowel slides in the slot, {tag}", _overlap(j, d) < 1e-6)
        ok(f"dowel clears the body window, {tag}", _overlap(b, d) < 1e-6)

    print(f"\n  {'all checks pass' if not fails else str(len(fails)) + ' FAILED'}")
    return not fails


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def _has_faces(m):
    """section() hands back an empty list, not a mesh, for a part that falls
    entirely on one side of the plane -- so ask before trusting it."""
    return m is not None and hasattr(m, "faces") and len(m.faces) > 0


def _sectioned(items, normal, origin):
    out = []
    for it in items:
        solid, faces = R.section(it["mesh"], normal, origin)
        if _has_faces(solid):
            out.append({"mesh": solid, "color": it["color"]})
        if _has_faces(faces):
            # cut faces go darker than the part, never lighter: tinting the
            # near-white lever upward turns its section into blank paper
            out.append({"mesh": faces,
                        "color": tuple(c * 0.45 + 0.04 for c in it["color"])})
    return out


def renders(out):
    out.mkdir(exist_ok=True)
    op, sh = scene(PSI_OPEN), scene(PSI_SHUT)

    # one camera per pair, framed on the open state, so the two compare
    for az, el, names in ((90, 0, ("40-guide-side-open.png",
                                   "41-guide-side-shut.png")),
                          (38, 14, ("42-guide-quarter-open.png",
                                    "43-guide-quarter-shut.png"))):
        cam = R.frame([p["mesh"] for p in op], azimuth_deg=az,
                      elevation_deg=el, margin=1.04)
        for name, ps in zip(names, (op, sh)):
            R.render(ps, width=1300, height=1050, supersample=2,
                     **SHOW, **cam).save(out / name)
            print(f"  renders/{name}")

    bore = {"eye": (0.0, 0.0, BODY_H + 190.0), "target": (0.0, 0.0, 40.0),
            "fov_deg": 46.0}
    for name, ps in (("44-guide-bore-open.png", op),
                     ("45-guide-bore-shut.png", sh)):
        R.render(ps, width=1200, height=1200, supersample=2, ambient=0.72,
                 key=0.34, fill=0.26, spec=0.1, edges=0.42,
                 **bore).save(out / name)
        print(f"  renders/{name}")

    # runner and groove, drawn apart: a cutaway here just shows the inside
    # of the far wall, where pulling the two walls off sideways shows the
    # thing being asked about -- which rail lands in which groove
    psi = PSI_SHUT
    apart = [{"mesh": jaw(psi, 0), "color": COL["jaw"]}]
    w = _wall(-1)
    w.apply_translation((0.0, -34.0, 0.0))
    apart.append({"mesh": w, "color": COL_DETAIL})
    cam = R.frame([p["mesh"] for p in apart], azimuth_deg=56,
                  elevation_deg=22, margin=1.03)
    R.render(apart, width=1300, height=1050, supersample=2,
             **SHOW, **cam).save(out / "46-guide-runner.png")
    print("  renders/46-guide-runner.png")

    # the vee engagement, cut across the runners
    sec = _sectioned(scene(PSI_SHUT), (-1, 0, 0), (30.0, 0.0, 0.0))
    R.render(sec, width=1250, height=1250, supersample=2, ambient=0.80,
             key=0.26, fill=0.22, spec=0.06, edges=0.52,
             eye=(230.0, 0.0, 52.0), target=(0.0, 0.0, 52.0),
             fov_deg=34.0).save(out / "47-guide-section.png")
    print("  renders/47-guide-section.png")

    # the drive at mid height, cut through the dowel's own axis: in any
    # solid view the jaw's open end stands in front of the thing to see
    plan = scene(PSI_OPEN)
    plan = [p if p["color"] != COL["body"] else
            {"mesh": p["mesh"], "color": COL_DETAIL} for p in plan]
    sec = _sectioned(plan, (0, 0, -1), (0.0, 0.0, JAW_MID))
    R.render(sec, width=1250, height=1150, supersample=2, ambient=0.80,
             key=0.26, fill=0.22, spec=0.06, edges=0.52,
             eye=(36.0, 0.0, 190.0), target=(36.0, 0.0, 0.0),
             fov_deg=30.0).save(out / "48-guide-drive.png")
    print("  renders/48-guide-drive.png")


if __name__ == "__main__":
    good = checks()
    print()
    renders(Path(__file__).parent / "renders")
    print(f"\n  span {2 * (PIVOT[0] + HANDLE * math.sin(PSI_OPEN)):.0f} mm open"
          f" -> {2 * PIVOT[0]:.0f} mm shut")
    print(f"  swing {math.degrees(PSI_OPEN - PSI_SHUT):.1f} deg, "
          f"jaw travel {P.JAW_TRAVEL:.0f} mm a side")
    sys.exit(0 if good else 1)
