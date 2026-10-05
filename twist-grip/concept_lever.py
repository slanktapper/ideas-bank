#!/usr/bin/env python3
"""A PROPOSAL, not the project: the finger flattener driven by levers.

Kept: the 40 mm bore, two jaw faces travelling 20 mm each so they stay
parallel, and the vee runners that lock each jaw to pure radial travel.

This revision rebuilds the mount and the lever:

    entrance    the front face of the 90 mm body, jaw starting 3 mm in
                behind a 45 degree lead-in chamfer
    pivot       a 12 mm post out of each body wall, near the front
    drive       a post out of each jaw side, ending 4 mm short of the
                body post's tip -- that is, flush with the lever's
                outer face, so it never fouls the brace
    lever       one flat piece, 8 mm thick where the holes are, running
                the length of the body and 40 mm past it
    brace       a C channel over each pair of pivot posts, picking up
                the 4 mm of post the lever leaves, holding the levers on

The drive hole is a short slot, not a round hole. The runners hold the
jaw to pure radial travel, so the jaw post stays at one height while the
lever's hole swings on an arc about the pivot: the distance from pivot
to post grows from 60.00 to 63.25 mm across the stroke, and the slot is
what absorbs those 3.25 mm.

Nutcracker, not see-saw: pivot, then drive, then handle, in that order
along the lever. Put the handle on the far side of the pivot and
squeezing opens the jaws.

    pivot    r 26, z 9        arm 60 mm to the drive at z 69
    swing    18.4 deg  ->  20 mm of jaw travel a side
    span     at the body's back face, 103 mm open -> 52 mm shut

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

BODY_R, BODY_H = 23.0, 90.0
ENTRY_CHAMFER = 2.0                    # 45 deg lead-in at the finger entrance
JAW_Z0, JAW_Z1 = 3.0, 89.0             # the jaw starts just behind the chamfer
JAW_L = 42.0
WEB_T = 3.0

# The y stack. Each number is forced by the one above it.
JAW_Y = P.JAW_W / 2.0                  # 13.00  jaw side face
WALL_Y0 = JAW_Y + 0.35                 # 13.35  body wall, inner face
RAIL_H, GROOVE_H = 2.9, 3.0            #        45 degree vees
RAIL_TIP = JAW_Y + RAIL_H              # 15.90
GROOVE_TIP = WALL_Y0 + GROOVE_H        # 16.35
WALL_Y1 = GROOVE_TIP + P.WALL_MIN      # 17.95  skin left over the groove

FIT = 0.3
LEVER_T = 8.0                          # "8 mm where the holes are"
LEVER_Y0 = WALL_Y1 + FIT               # 18.25
LEVER_Y1 = LEVER_Y0 + LEVER_T          # 26.25
POST_LEN = 12.0                        # the body post
POST_TIP = WALL_Y1 + POST_LEN          # 29.95
DRIVE_TIP = POST_TIP - 4.0             # 25.95  the jaw post's tip
BRACE_Y0 = LEVER_Y1 + FIT              # 26.55
BRACE_T = 4.0
BRACE_Y1 = BRACE_Y0 + BRACE_T          # 30.55

PIVOT = (26.0, 9.0)                    # near the front, on the wall's face
DRIVE_Z = 69.0
ARM = DRIVE_Z - PIVOT[1]               # 60.0
DRIVE_LOCAL = PIVOT[0]                 # the post's x in jaw-local terms
PSI_OPEN = math.atan(P.JAW_TRAVEL / ARM)
PSI_SHUT = 0.0
LEVER_OVERHANG = 40.0
LEVER_TIP_Z = BODY_H + LEVER_OVERHANG   # 130
POST_D, DRIVE_D = 8.0, 6.0
LEVER_HALF_W = 9.0

RAIL_X = (19.0, 39.0)
GROOVE_X = (RAIL_X[0], RAIL_X[1] + P.JAW_TRAVEL)
WALL_X = (15.0, GROOVE_X[1] + 2.0)
WALL_Z = (2.0, BODY_H)
RAIL_Z = (JAW_Z0 + 14.0, JAW_Z1 - 5.0)              # 17, 84
WINDOW_X = (22.0, 50.0)
WINDOW_Z = (DRIVE_Z - 4.0, DRIVE_Z + 4.0)           # 65 .. 73
DRIVE_BOSS_X, DRIVE_BOSS_L = 20.0, 12.0
DRIVE_BOSS_Z = (DRIVE_Z - 6.0, DRIVE_Z + 6.0)

COL = {"body": (0.055, 0.07, 0.085), "jaw": (1.00, 0.74, 0.82),
       "lever": (0.96, 0.97, 0.95), "brace": (0.85, 0.30, 0.22)}
# The body is black by choice, which is fine for an assembly and useless for
# a detail: at a base of 0.055 every face lands within a few percent of black
# whatever the lighting does. The detail figures draw it in grey.
COL_DETAIL = (0.46, 0.49, 0.54)
SHOW = dict(ambient=0.74, key=0.34, fill=0.20, spec=0.12, edges=0.46)


# ---------------------------------------------------------------------------
# kinematics
# ---------------------------------------------------------------------------

def face_at(psi):
    """Radius of the jaw's gripping face: 0 shut, 20 mm open.

    The jaw post sits at one fixed height, so the lever's angle and the
    jaw's radius are related by a tangent, not a sine.
    """
    return ARM * math.tan(psi)


def drive_at(psi):
    return (PIVOT[0] + face_at(psi), DRIVE_Z)


def swung(mesh, psi):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        psi, (0, 1, 0), (PIVOT[0], 0.0, PIVOT[1])))
    return m


SLOT_RUN = math.hypot(ARM, P.JAW_TRAVEL) - ARM      # 3.25 mm


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

def prism_x(poly, x0, x1):
    """Extrude a cross-section drawn in (y, z) along the x axis."""
    m = trimesh.creation.extrude_polygon(poly, x1 - x0)
    t = np.eye(4)
    t[:3, :3] = np.array([[0.0, 0.0, 1.0],
                          [1.0, 0.0, 0.0],
                          [0.0, 1.0, 0.0]])
    m.apply_transform(t)
    m.apply_translation((x0, 0.0, 0.0))
    return m


def vee(y_root, y_tip, zc, sign):
    """A 45 degree vee in (y, z), apex outward at y_tip.

    Drawn from a root well inside the part it belongs to, so the boolean
    has real overlap rather than a coincident face. The 45 degrees make the
    half height equal the distance back from the apex, which is what keeps
    rail and groove parallel however far either is extended -- and leaves
    every flank self-supporting when the part prints standing up.
    """
    half = abs(y_tip - y_root)
    return Polygon([(sign * y_root, zc - half),
                    (sign * y_root, zc + half),
                    (sign * y_tip, zc)])


def plate(poly, thickness, y_at):
    """A flat part in the x-z plane, occupying y_at .. y_at+thickness."""
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


def pin(d, y0, y1, at_xz, sign):
    m = along_y(T.post(d, y0, y1), sign)
    m.apply_translation((at_xz[0], 0.0, at_xz[1]))
    return m


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------

def _wall(sign):
    w = T.bar(WALL_X[1] - WALL_X[0], WALL_Y1 - WALL_Y0,
              WALL_Z[0], WALL_Z[1], x0=WALL_X[0])
    w.apply_translation((0.0, sign * (WALL_Y0 + WALL_Y1) / 2.0, 0.0))
    for zc in RAIL_Z:
        w = T.cut(w, prism_x(vee(WALL_Y0 - 1.35, GROOVE_TIP, zc, sign),
                             GROOVE_X[0], GROOVE_X[1]))
    # the slot the jaw's drive post sweeps through
    w = T.cut(w, T.bar(WINDOW_X[1] - WINDOW_X[0], 2 * (WALL_Y1 + 1.0),
                       WINDOW_Z[0], WINDOW_Z[1], x0=WINDOW_X[0]))
    return T.fuse(w, pin(POST_D, WALL_Y1 - 1.0, POST_TIP, PIVOT, sign))


def body():
    solid = T.tube(P.BORE_D / 2.0, BODY_R, 0.0, BODY_H)
    # the finger goes in here: a 45 degree lead-in, and the jaw 3 mm behind it
    cone = trimesh.creation.cone(radius=P.BORE_D / 2.0 + ENTRY_CHAMFER,
                                 height=P.BORE_D / 2.0 + ENTRY_CHAMFER,
                                 sections=128)
    solid = T.cut(solid, cone)
    reach = 80.0
    solid = T.cut(solid, T.bar(2 * reach, P.SLOT_W, JAW_Z0, JAW_Z1, x0=-reach))
    for k in range(2):
        for sign in (1, -1):
            solid = T.fuse(solid, T.spun(_wall(sign), 180.0 * k))
    return solid


def jaw(psi, index):
    web = []
    for sign in (1, -1):
        w = T.bar(JAW_L, WEB_T, JAW_Z0, JAW_Z1)
        w.apply_translation((0.0, sign * (JAW_Y - WEB_T / 2.0), 0.0))
        web.append(w)

    solid = T.fuse(
        T.bar(P.FACE_T, P.JAW_W, JAW_Z0, JAW_Z1),
        *web,
        T.bar(JAW_L, P.JAW_W, JAW_Z0, JAW_Z0 + 6.0),
        T.bar(JAW_L, P.JAW_W, JAW_Z1 - 6.0, JAW_Z1),
        T.bar(DRIVE_BOSS_L, P.JAW_W, *DRIVE_BOSS_Z, x0=DRIVE_BOSS_X))

    for sign in (1, -1):
        for zc in RAIL_Z:
            solid = T.fuse(solid, prism_x(vee(JAW_Y - 2.0, RAIL_TIP, zc, sign),
                                          *RAIL_X))
        solid = T.fuse(solid, pin(DRIVE_D, JAW_Y - 2.0, DRIVE_TIP,
                                  (DRIVE_LOCAL, DRIVE_Z), sign))

    solid.apply_translation((face_at(psi), 0.0, 0.0))
    return T.spun(solid, 180.0 * index)


def lever(psi, index, sign=1):
    """One flat piece: a round hole on the pivot post, a short slot on the
    jaw post, and 40 mm of handle past the back of the body."""
    px, pz = PIVOT
    # the plate stops at the pivot: a tail behind it would sweep into the
    # brace's web, which crosses in front of the body
    spine = LineString([(px, pz),
                        (px, LEVER_TIP_Z - LEVER_HALF_W)]).buffer(
                            LEVER_HALF_W, resolution=16)
    y0 = LEVER_Y0 if sign > 0 else -LEVER_Y1
    solid = plate(spine, LEVER_T, y0)

    bore = pin(POST_D + 0.35, -60.0, 60.0, PIVOT, 1)
    slot_poly = LineString([(px, pz + ARM),
                            (px, pz + ARM + SLOT_RUN)]).buffer(
                                (DRIVE_D + 0.35) / 2.0, resolution=16)
    slot = plate(slot_poly, 200.0, -100.0)
    return T.spun(swung(T.cut(solid, bore, slot), psi), 180.0 * index)


def brace(index):
    """A C channel over one jaw's pair of pivot posts: two flanges with a
    hole each, tied by a web that crosses clear in front of the body."""
    px, pz = PIVOT
    tab = LineString([(px, -4.0), (px, pz)]).buffer(8.0, resolution=16)
    pieces = [plate(tab, BRACE_T, BRACE_Y0),
              plate(tab, BRACE_T, -BRACE_Y1),
              # the web crosses in front of the body, kept outboard of the
              # entrance chamfer so nothing narrows the way in
              T.bar(14.0, 2 * BRACE_Y1, -6.0, -2.0, x0=px - 2.0)]
    holes = [pin(POST_D + 0.35, -60.0, 60.0, PIVOT, 1)]
    return T.spun(T.cut(T.fuse(*pieces), *holes), 180.0 * index)


def scene(psi, braces=True):
    out = [{"mesh": body(), "color": COL["body"]}]
    out += [{"mesh": jaw(psi, k), "color": COL["jaw"]} for k in range(2)]
    out += [{"mesh": lever(psi, k, s), "color": COL["lever"]}
            for k in range(2) for s in (1, -1)]
    if braces:
        out += [{"mesh": brace(k), "color": COL["brace"]} for k in range(2)]
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
        print(f"  {'PASS' if cond else 'FAIL'}  {name}"
              f"{'  ' + detail if detail else ''}")
        if not cond:
            fails.append(name)

    lv, br = lever(PSI_SHUT, 0), brace(0)
    bd, jw = body(), jaw(PSI_SHUT, 0)

    ok("the body is 90 mm long", abs(BODY_H - 90.0) < 1e-9)
    ok("the jaw sits just behind the entrance face",
       JAW_Z0 <= 3.0, f"{JAW_Z0:.0f} mm in, behind a {ENTRY_CHAMFER:.0f} mm chamfer")
    ok("the pivot is near the front, not a quarter in",
       PIVOT[1] / BODY_H < 0.15, f"{100 * PIVOT[1] / BODY_H:.0f}% of the body")
    ok("the body post stands 12 mm proud",
       abs((POST_TIP - WALL_Y1) - 12.0) < 1e-9)
    ok("the jaw post ends 4 mm short of it",
       abs((POST_TIP - DRIVE_TIP) - 4.0) < 1e-9,
       f"tips at {POST_TIP:.2f} and {DRIVE_TIP:.2f}")
    ok("the lever is 8 mm thick at the holes",
       abs(LEVER_T - 8.0) < 1e-9)
    ok("the lever prints as one piece",
       len(lv.split(only_watertight=False)) == 1)
    ok("the brace is one piece",
       len(br.split(only_watertight=False)) == 1)
    ok("the lever runs 40 mm past the body",
       abs((lv.bounds[1][2] - BODY_H) - LEVER_OVERHANG) < 1e-6,
       f"tip at z {lv.bounds[1][2]:.0f}")
    ok("the jaw post stops flush with the lever's outer face",
       abs(DRIVE_TIP - LEVER_Y1) < 0.35,
       f"post {DRIVE_TIP:.2f}, lever face {LEVER_Y1:.2f}")
    ok("the brace picks up the post the lever leaves",
       BRACE_Y0 >= LEVER_Y1 and POST_TIP > BRACE_Y0,
       f"{POST_TIP - BRACE_Y0:.2f} mm of post in the brace")
    ok("each jaw face travels 20 mm",
       abs((face_at(PSI_OPEN) - face_at(PSI_SHUT)) - P.JAW_TRAVEL) < 1e-9)
    ok("the faces meet when shut", abs(face_at(PSI_SHUT)) < 1e-9)
    ok("the bore is clear when open",
       abs(face_at(PSI_OPEN) - P.BORE_D / 2.0) < 1e-9)
    ok("the drive slot is long enough for the arc",
       SLOT_RUN > 3.0, f"{SLOT_RUN:.2f} mm of run")
    ok("the drive window clears the back runner",
       RAIL_Z[1] - RAIL_H - WINDOW_Z[1] >= P.WALL_MIN,
       f"{RAIL_Z[1] - RAIL_H - WINDOW_Z[1]:.1f} mm of wall")

    for tag, psi in (("open", PSI_OPEN), ("half", PSI_OPEN / 2), ("shut", PSI_SHUT)):
        j = jaw(psi, 0)
        lp, lm = lever(psi, 0, 1), lever(psi, 0, -1)
        ok(f"jaw runs free in the body, {tag}", _overlap(bd, j) < 1e-6,
           f"{_overlap(bd, j):.3f} mm^3")
        ok(f"lever clears the body, {tag}", _overlap(bd, lp) < 1e-6)
        ok(f"drive post rides free in the slot, {tag}",
           _overlap(j, lp) < 1e-6 and _overlap(j, lm) < 1e-6)
        ok(f"brace clears the lever, {tag}", _overlap(br, lp) < 1e-6)
        ok(f"brace clears the body, {tag}", _overlap(br, bd) < 1e-6)

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


def _greyed(items):
    return [it if it["color"] != COL["body"] else
            {"mesh": it["mesh"], "color": COL_DETAIL} for it in items]


def renders(out):
    out.mkdir(exist_ok=True)
    op, sh = scene(PSI_OPEN), scene(PSI_SHUT)

    for az, el, names in ((90, 0, ("50-side-open.png", "51-side-shut.png")),
                          (40, 16, ("52-quarter-open.png",
                                    "53-quarter-shut.png"))):
        cam = R.frame([p["mesh"] for p in op], azimuth_deg=az,
                      elevation_deg=el, margin=1.03)
        for name, ps in zip(names, (op, sh)):
            R.render(ps, width=1300, height=1050, supersample=2,
                     **SHOW, **cam).save(out / name)
            print(f"  renders/{name}")

    # straight into the finger entrance
    for name, ps in (("54-entrance-open.png", op), ("55-entrance-shut.png", sh)):
        R.render(ps, width=1150, height=1150, supersample=2, ambient=0.74,
                 key=0.32, fill=0.24, spec=0.1, edges=0.44,
                 eye=(0.0, 0.0, -185.0), target=(0.0, 0.0, 30.0),
                 fov_deg=42.0).save(out / name)
        print(f"  renders/{name}")

    # the post stack, drawn apart: body post, lever, brace
    apart = [{"mesh": _wall(1), "color": COL_DETAIL}]
    lv = lever(PSI_SHUT, 0, 1)
    lv.apply_translation((0.0, 26.0, 0.0))
    apart.append({"mesh": lv, "color": COL["lever"]})
    br = brace(0)
    br.apply_translation((0.0, 56.0, 0.0))
    apart.append({"mesh": br, "color": COL["brace"]})
    # looking near-along x, so a stack pulled apart along y reads across
    # the frame instead of hiding the post behind the lever
    cam = R.frame([p["mesh"] for p in apart], azimuth_deg=8,
                  elevation_deg=12, margin=1.03)
    R.render(apart, width=1300, height=1050, supersample=2,
             **SHOW, **cam).save(out / "56-stack-apart.png")
    print("  renders/56-stack-apart.png")

    # plan sections through each post's own axis
    for name, z, eye_x in (("57-pivot-section.png", PIVOT[1], 26.0),
                           ("58-drive-section.png", DRIVE_Z, 30.0)):
        sec = _sectioned(_greyed(scene(PSI_OPEN)), (0, 0, -1), (0.0, 0.0, z))
        R.render(sec, width=1250, height=1100, supersample=2, ambient=0.80,
                 key=0.26, fill=0.22, spec=0.06, edges=0.52,
                 eye=(eye_x, 0.0, 170.0), target=(eye_x, 0.0, 0.0),
                 fov_deg=32.0).save(out / name)
        print(f"  renders/{name}")


if __name__ == "__main__":
    good = checks()
    print()
    renders(Path(__file__).parent / "renders")
    for z, label in ((BODY_H, "at the body's back face"),
                     (LEVER_TIP_Z, "at the lever tip")):
        s = (z - PIVOT[1]) * math.sin(PSI_OPEN)
        print(f"\n  grip {label}: span {2 * (PIVOT[0] + s):.0f} mm open"
              f" -> {2 * PIVOT[0]:.0f} mm shut")
    sys.exit(0 if good else 1)
