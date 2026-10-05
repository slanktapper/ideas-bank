#!/usr/bin/env python3
"""A PROPOSAL, not the project: the finger flattener driven by levers.

Kept: the 40 mm bore, two jaw faces travelling 20 mm each so they stay
parallel, and the vee runners that lock each jaw to pure radial travel.

This revision rebuilds the mount and the lever:

    entrance    the front face of the 90 mm body, jaw starting 3 mm in
                behind a 45 degree lead-in chamfer
    pivot       a 12 mm post out of each body wall, near the front
    runners     a vee rail near each end of each jaw side, 66 mm apart,
                which is the separation that holds the jaw square
    drive       a post out of the middle of each jaw side, ending 4 mm
                short of the
                body post's tip -- flush with the lever's outer
                face, so it never fouls the brace
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

    pivot    r 25, z 8        arm 38 mm to the drive at z 46, mid jaw
    swing    27.8 deg  ->  20 mm of jaw travel a side
    span     104 mm open -> 50 mm shut, closing on the lever from z 66,
             which is where its outer edge first clears the guide wall

Run:  python3 concept_lever.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import params as P
import parts as T
import render as R

# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------

BODY_R, BODY_H = 23.0, 90.0
ENTRY_CHAMFER = 2.0                    # 45 deg lead-in at the finger entrance
# The jaw's ends are where the two halves of the body get to meet. Run the
# jaw to 89 and they meet over 3 mm at the front and 1 mm at the back -- 20
# mm^2 of material across the whole y = 0 plane, holding two walls that a
# squeeze is trying to prise apart. Pulling the jaw in at both ends buys a
# tie slab at each, spanning the walls over their full radial length.
JAW_Z0, JAW_Z1 = 4.0, 82.0             # 78 mm of jaw
JAW_L = 42.0
WEB_T = 3.0
# The jaw's own ends stand back from the ends of the slot. Built flush they
# meet the uncut tube above and below face to face, which reads as zero
# interference in CAD -- coincident surfaces overlap by nothing -- and binds
# in plastic. The runners and the drive stay where they are, so this is a
# change to the jaw alone and leaves a printed body still correct.
JAW_END_FIT = 0.3

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

# The pivot sits OUTBOARD of the body, past the walls, so the brace that
# caps it can reach across from one side to the other beside the body
# instead of wrapping round the front of the entrance. It costs a boss on
# each wall and buys a longer, more inclined arm: 18.3 degrees of swing
# instead of 27.8, and a 67 mm squeeze instead of 93.
PIVOT = (66.0, 8.0)
PIVOT_BOSS_X = (56.0, 72.0)
# Kept below the front runner's sweep: at z 2..18 the boss stood in the
# groove's own height out past x 59, and the jaw fouled it on the way in.
PIVOT_BOSS_Z = (0.0, 14.0)
DRIVE_Z = (JAW_Z0 + JAW_Z1) / 2.0      # 46.0, the middle of the jaw
DRIVE_LOCAL = 25.0                     # the post's x in jaw-local terms
DZ_ARM = DRIVE_Z - PIVOT[1]            # 38.0, the only term that sets sense
# The arm now leans inboard, so its angle -- not a plain tangent -- carries
# the jaw. Rotation about the pivot drops the arm's polar angle, and the
# post, held at one height by the runners, slides along the arm as it goes.
ALPHA_SHUT = math.atan2(DZ_ARM, DRIVE_LOCAL - PIVOT[0])
ALPHA_OPEN = math.atan2(DZ_ARM, DRIVE_LOCAL + P.JAW_TRAVEL - PIVOT[0])
PSI_OPEN = ALPHA_SHUT - ALPHA_OPEN
PSI_SHUT = 0.0
ARM_SHUT = DZ_ARM / math.sin(ALPHA_SHUT)
ARM_OPEN = DZ_ARM / math.sin(ALPHA_OPEN)
LEVER_OVERHANG = 40.0
LEVER_TIP_Z = BODY_H + LEVER_OVERHANG   # 130
POST_D, DRIVE_D = 8.0, 6.0
LEVER_HALF_W = 9.0
GRIP_R = 8.0                           # the round bar tying the two sides
# A straight bar from the pivot to the grab bar, with a stub off its side
# for the drive slot -- a simpler outline to print than a cranked arm, and
# the same mechanism: pivot, drive and grab bar are where they were, and
# only the metal between them changes shape.
GRIP = (25.0, 108.0)                   # the grab bar, clear behind the body
LEVER_END_Z = 121.0                    # buffered, this puts the tip at 130
BRACE_WEB_X = (80.0, 88.0)             # the web crosses outboard of the lever

RAIL_X = (19.0, 39.0)
GROOVE_X = (RAIL_X[0], RAIL_X[1] + P.JAW_TRAVEL)
# The wall stops where the groove does, and the drive window runs out to
# the same edge. Blind at their outer ends the jaw cannot be got in at all:
# it has to enter radially from outside, and a 2 mm lip across the end of a
# groove is enough to stop its runner dead.
WALL_X = (15.0, GROOVE_X[1])
# The walls run all the way to the entrance face. Started at z = 2 they
# began 38 mm out over thin air, with only the tube under their inner end.
WALL_Z = (0.0, BODY_H)
# front and back, as far apart as they will go: the pair's separation is
# what holds the jaw square, and it has to clear the pivot post at one end
RAIL_Z = (JAW_Z0 + 15.0, JAW_Z1 - 5.0)              # 18, 84
WINDOW_X = (22.0, WALL_X[1])
WINDOW_Z = (DRIVE_Z - 4.0, DRIVE_Z + 4.0)           # 42 .. 50
TIE_X = (22.0, WALL_X[1])              # clear of the entrance chamfer
TIE_FRONT_Z = (0.0, JAW_Z0 - FIT)
TIE_BACK_Z = (JAW_Z1 + FIT, BODY_H)
# The boss cannot narrow in x: 12 mm is the 6 mm post plus 3 mm of wall
# each side. It can narrow in y and z, and the webs carry on past it at
# |y| 10..13, so the solid section the post roots into is unchanged.
DRIVE_BOSS_X, DRIVE_BOSS_L = 20.0, 12.0
DRIVE_BOSS_W = 20.0
DRIVE_BOSS_Z = (DRIVE_Z - 5.0, DRIVE_Z + 5.0)
DRIVE_RIB_W = 6.0

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
    """Radius of the jaw's gripping face: 0 shut, 20 mm open."""
    return (PIVOT[0] + DZ_ARM / math.tan(ALPHA_SHUT - psi)) - DRIVE_LOCAL


def on_arm(r):
    """A point r along the arm, in the lever's own (shut) frame."""
    return (PIVOT[0] + r * math.cos(ALPHA_SHUT),
            PIVOT[1] + r * math.sin(ALPHA_SHUT))


def drive_at(psi):
    return (PIVOT[0] + face_at(psi), DRIVE_Z)


def swung(mesh, psi):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        psi, (0, 1, 0), (PIVOT[0], 0.0, PIVOT[1])))
    return m


SLOT_RUN = ARM_SHUT - ARM_OPEN


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
    # the boss goes on before the grooves are cut: added after, it fills the
    # outer end of the front groove, exactly where that runner sits at full
    # open, and the jaw jams on it
    boss = T.bar(PIVOT_BOSS_X[1] - PIVOT_BOSS_X[0], WALL_Y1 - WALL_Y0,
                 *PIVOT_BOSS_Z, x0=PIVOT_BOSS_X[0])
    boss.apply_translation((0.0, sign * (WALL_Y0 + WALL_Y1) / 2.0, 0.0))
    w = T.fuse(w, boss)
    for zc in RAIL_Z:
        w = T.cut(w, prism_x(vee(WALL_Y0 - 1.35, GROOVE_TIP, zc, sign),
                             GROOVE_X[0], GROOVE_X[1]))
    # the slot the jaw's drive post sweeps through
    w = T.cut(w, T.bar(WINDOW_X[1] - WINDOW_X[0], 2 * (WALL_Y1 + 1.0),
                       WINDOW_Z[0], WINDOW_Z[1], x0=WINDOW_X[0]))
    return T.fuse(w, pin(POST_D, WALL_Y1 - 1.0, POST_TIP, PIVOT, sign))


def body():
    solid = T.tube(P.BORE_D / 2.0, BODY_R, 0.0, BODY_H)
    # the finger goes in here: a 45 degree lead-in, with the jaw just behind
    cone = trimesh.creation.cone(radius=P.BORE_D / 2.0 + ENTRY_CHAMFER,
                                 height=P.BORE_D / 2.0 + ENTRY_CHAMFER,
                                 sections=128)
    solid = T.cut(solid, cone)
    reach = 80.0
    solid = T.cut(solid, T.bar(2 * reach, P.SLOT_W, JAW_Z0, JAW_Z1, x0=-reach))
    for k in range(2):
        for sign in (1, -1):
            solid = T.fuse(solid, T.spun(_wall(sign), 180.0 * k))
    # The ties. Beyond each end of the jaw, a slab right across the slot,
    # joining each pair of walls over the whole length they stand on. These
    # are the only material anywhere that crosses y = 0 between the walls,
    # and a squeeze works to prise those walls apart.
    for zs in (TIE_FRONT_Z, TIE_BACK_Z):
        tie = T.bar(TIE_X[1] - TIE_X[0], P.SLOT_W, *zs, x0=TIE_X[0])
        for k in range(2):
            solid = T.fuse(solid, T.spun(tie, 180.0 * k))
    return solid


def jaw(psi, index):
    z0, z1 = JAW_Z0 + JAW_END_FIT, JAW_Z1 - JAW_END_FIT
    web = []
    for sign in (1, -1):
        w = T.bar(JAW_L, WEB_T, z0, z1)
        w.apply_translation((0.0, sign * (JAW_Y - WEB_T / 2.0), 0.0))
        web.append(w)

    solid = T.fuse(
        T.bar(P.FACE_T, P.JAW_W, z0, z1),
        *web,
        T.bar(JAW_L, P.JAW_W, z0, JAW_Z0 + 6.0),
        T.bar(JAW_L, P.JAW_W, JAW_Z1 - 6.0, z1),
        T.bar(DRIVE_BOSS_L, DRIVE_BOSS_W, *DRIVE_BOSS_Z, x0=DRIVE_BOSS_X),
        # The boss stood in mid-channel with 20 mm of air under it, and the
        # top end cap did the same. A spine from one cap to the other, in
        # the boss's own width, gives both something to grow from, and a
        # short rib ties the boss back to the face plate.
        T.bar(DRIVE_BOSS_L, DRIVE_RIB_W, JAW_Z0 + 6.0, JAW_Z1 - 6.0,
              x0=DRIVE_BOSS_X),
        T.bar(DRIVE_BOSS_X - P.FACE_T, DRIVE_RIB_W, *DRIVE_BOSS_Z,
              x0=P.FACE_T))

    for sign in (1, -1):
        for zc in RAIL_Z:
            solid = T.fuse(solid, prism_x(vee(JAW_Y - 2.0, RAIL_TIP, zc, sign),
                                          *RAIL_X))
        solid = T.fuse(solid, pin(DRIVE_D, JAW_Y - 2.0, DRIVE_TIP,
                                  (DRIVE_LOCAL, DRIVE_Z), sign))

    solid.apply_translation((face_at(psi), 0.0, 0.0))
    return T.spun(solid, 180.0 * index)


def grip_xy():
    return GRIP


def _on_axis(z):
    """A point at height z on the straight bar through pivot and grab bar."""
    (px, pz), (gx, gz) = PIVOT, GRIP
    return (px + (gx - px) * (z - pz) / (gz - pz), z)


def _stub():
    """The side tab carrying the drive slot.

    The slot cannot lie along the bar. In the lever's own frame the jaw post
    tracks a line radial from the pivot -- that is what the runners holding
    the jaw at one height force -- and the bar runs from the pivot to the
    grab bar, which is a different direction. So the tab stands off the bar
    and the slot inside it sits about 25 degrees across.
    """
    slot = LineString([on_arm(ARM_OPEN), on_arm(ARM_SHUT)])
    mid = slot.interpolate(0.5, normalized=True)
    rel = (mid.x - PIVOT[0], mid.y - PIVOT[1])
    (px, pz), (gx, gz) = PIVOT, GRIP
    ux, uz = (gx - px), (gz - pz)
    n = math.hypot(ux, uz)
    ux, uz = ux / n, uz / n
    t = rel[0] * ux + rel[1] * uz                     # foot of the perpendicular
    foot = (px + t * ux, pz + t * uz)
    return slot.buffer(9.0, resolution=16).union(
        Point(foot).buffer(LEVER_HALF_W, resolution=16)).convex_hull


def lever(psi, index):
    """One piece: a straight bar from the outboard pivot to the grab bar,
    with a stub off its side carrying the drive slot."""
    spine = LineString([PIVOT, _on_axis(LEVER_END_Z)]).buffer(
        LEVER_HALF_W, resolution=16).union(_stub())
    pieces = [plate(spine, LEVER_T, LEVER_Y0),
              plate(spine, LEVER_T, -LEVER_Y1),
              pin(2 * GRIP_R, -LEVER_Y1, LEVER_Y1, grip_xy(), 1)]

    bore = pin(POST_D + 0.35, -60.0, 60.0, PIVOT, 1)
    # the slot runs along the arm, because that is the way the post slides
    slot_poly = LineString([on_arm(ARM_OPEN), on_arm(ARM_SHUT)]).buffer(
        (DRIVE_D + 0.35) / 2.0, resolution=16)
    slot = plate(slot_poly, 200.0, -100.0)
    return T.spun(swung(T.cut(T.fuse(*pieces), bore, slot), psi),
                  180.0 * index)


def brace(index):
    """A C channel capping one jaw's pair of pivot posts. With the posts
    outboard of the walls, its web reaches across beside the body rather
    than wrapping round the entrance."""
    px, pz = PIVOT
    tab = LineString([(px, pz), (BRACE_WEB_X[0] - 2.0, pz)]).buffer(
        8.0, resolution=16)
    pieces = [plate(tab, BRACE_T, BRACE_Y0),
              plate(tab, BRACE_T, -BRACE_Y1),
              T.bar(BRACE_WEB_X[1] - BRACE_WEB_X[0], 2 * BRACE_Y1,
                    0.0, 16.0, x0=BRACE_WEB_X[0])]
    hole = pin(POST_D + 0.35, -60.0, 60.0, PIVOT, 1)
    return T.spun(T.cut(T.fuse(*pieces), hole), 180.0 * index)


def scene(psi, braces=True):
    out = [{"mesh": body(), "color": COL["body"]}]
    out += [{"mesh": jaw(psi, k), "color": COL["jaw"]} for k in range(2)]
    out += [{"mesh": lever(psi, k), "color": COL["lever"]} for k in range(2)]
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
       JAW_Z0 <= 5.0,
       f"{JAW_Z0:.0f} mm in, behind a {ENTRY_CHAMFER:.0f} mm chamfer")
    tie = trimesh.creation.box(extents=(400.0, 1.0, 400.0))
    across = _overlap(bd, tie) / 1.0
    ok("the two sides of the body are properly tied together",
       across > 400.0, f"{across:.0f} mm^2 crossing y = 0")
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
       abs((lv.bounds[1][2] - BODY_H) - LEVER_OVERHANG) < 0.3,
       f"{lv.bounds[1][2] - BODY_H:.1f} mm past, tip at z {lv.bounds[1][2]:.1f}")
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
       SLOT_RUN > 4.5, f"{SLOT_RUN:.2f} mm of run")
    ok("the drive post is at the middle of the jaw",
       abs(DRIVE_Z - (JAW_Z0 + JAW_Z1) / 2.0) < 1e-9, f"z {DRIVE_Z:.0f}")
    ok("a runner sits near each end of the jaw",
       RAIL_Z[0] - JAW_Z0 <= 15.0 and JAW_Z1 - RAIL_Z[1] <= 15.0,
       f"{RAIL_Z[0] - JAW_Z0:.0f} and {JAW_Z1 - RAIL_Z[1]:.0f} mm in, "
       f"{RAIL_Z[1] - RAIL_Z[0]:.0f} mm apart")
    ok("the drive window clears both runners",
       min(RAIL_Z[1] - RAIL_H - WINDOW_Z[1],
           WINDOW_Z[0] - (RAIL_Z[0] + RAIL_H)) >= P.WALL_MIN,
       f"{min(RAIL_Z[1] - RAIL_H - WINDOW_Z[1], WINDOW_Z[0] - RAIL_Z[0] - RAIL_H):.1f} mm of wall")
    ok("the front runner's groove clears the pivot post",
       (RAIL_Z[0] - RAIL_H) - (PIVOT[1] + POST_D / 2.0) >= 1.5,
       f"{(RAIL_Z[0] - RAIL_H) - (PIVOT[1] + POST_D / 2.0):.1f} mm")
    ok("the lever's pivot end clears the tube",
       math.hypot(PIVOT[0] - LEVER_HALF_W, LEVER_Y0) > BODY_R,
       f"r {math.hypot(PIVOT[0] - LEVER_HALF_W, LEVER_Y0):.1f} vs {BODY_R}")

    # the grab bar ties both sides, so the lever is one body, and its
    # worst case against the walls is mid-stroke rather than at either end
    worst = max(_overlap(bd, lever(PSI_OPEN * k / 8.0, 0)) for k in range(9))
    ok("the grab bar clears the body right through the stroke",
       worst < 1e-6, f"worst {worst:.3f} mm^3 over 9 positions")

    gx, gz = grip_xy()
    grip_arm = math.hypot(gx - PIVOT[0], gz - PIVOT[1])
    spread = POST_TIP - LEVER_Y0
    strain = 3 * LEVER_T * spread / (2 * grip_arm ** 2)
    ok("the lever can be sprung onto the posts without yielding",
       strain < 0.02,
       f"{spread:.1f} mm a side, {100 * strain:.2f}% strain")

    ok("the pivot post stands outboard of the guide wall",
       PIVOT[0] - POST_D / 2.0 > WALL_X[1] or
       PIVOT_BOSS_X[1] > WALL_X[1], f"pivot at x {PIVOT[0]:.0f}, wall ends {WALL_X[1]:.0f}")
    ok("the brace stays off the front of the entrance",
       br.bounds[0][2] >= -1e-9, f"nearest face at z {br.bounds[0][2]:.1f}")
    ok("the brace's web reaches across outboard of the lever",
       BRACE_WEB_X[0] > lv.bounds[1][0],
       f"web from x {BRACE_WEB_X[0]:.0f}, lever reaches {lv.bounds[1][0]:.0f}")
    # The jaw can only go in radially from outside, so every runner groove
    # and the drive window have to run out to the wall's edge, and nothing
    # may stand in the sweep on the way. A design that passes every running
    # check can still be a design that cannot be put together.
    worst_in = 0.0
    for extra in (0, 3, 6, 10, 15, 20, 25, 30, 40, 50, 65):
        j = jaw(PSI_OPEN, 0).copy()
        j.apply_translation((extra, 0.0, 0.0))
        worst_in = max(worst_in, _overlap(bd, j))
    ok("a jaw can be slid in radially to assemble",
       worst_in < 1e-6, f"worst {worst_in:.1f} mm^3 over 11 positions")

    span = (DRIVE_BOSS_W / 2.0 - DRIVE_RIB_W / 2.0)
    ok("nothing in the jaw bridges more than 10 mm",
       span <= 10.0,
       f"widest span under the boss {span:.0f} mm, between spine and web")

    # Zero interference is not the same as clearance: two faces flush
    # against each other overlap by nothing and pass every boolean test,
    # then bind in plastic. Nudge the jaw and insist it is actually free.
    free = {}
    for name, idx in (("along the bore", 2), ("across the slot", 1)):
        j = jaw(PSI_OPEN, 0).copy()
        t = [0.0, 0.0, 0.0]
        t[idx] = 0.2
        j.apply_translation(t)
        free[name] = _overlap(bd, j)
    ok("the jaw has real clearance, not coincident faces",
       max(free.values()) < 1e-6,
       "free to move 0.2 mm in both z and y")

    ok("the stub keeps a printable wall round the drive slot",
       9.0 - (DRIVE_D + 0.35) / 2.0 >= P.WALL_MIN,
       f"{9.0 - (DRIVE_D + 0.35) / 2.0:.2f} mm all round")
    ok("the load path from grab bar to pivot is a straight bar",
       abs((GRIP[0] - PIVOT[0]) * (_on_axis(LEVER_END_Z)[1] - PIVOT[1])
           - (GRIP[1] - PIVOT[1]) * (_on_axis(LEVER_END_Z)[0] - PIVOT[0])) < 1e-9)
    ok("the drive post still slides along the arm, not across it",
       abs(ARM_SHUT - ARM_OPEN - SLOT_RUN) < 1e-9,
       f"arm {ARM_SHUT:.1f} -> {ARM_OPEN:.1f} mm")

    for tag, psi in (("open", PSI_OPEN), ("half", PSI_OPEN / 2), ("shut", PSI_SHUT)):
        j, lv2 = jaw(psi, 0), lever(psi, 0)
        ok(f"jaw runs free in the body, {tag}", _overlap(bd, j) < 1e-6,
           f"{_overlap(bd, j):.3f} mm^3")
        ok(f"lever clears the body, {tag}", _overlap(bd, lv2) < 1e-6)
        ok(f"drive post rides free in the slot, {tag}", _overlap(j, lv2) < 1e-6)
        ok(f"brace clears the lever, {tag}", _overlap(br, lv2) < 1e-6)
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
    lv = lever(PSI_SHUT, 0)
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

    # runner and groove, drawn apart: the jaw's two vee rails and the
    # drive post in the middle, against the wall they land in
    apart = [{"mesh": jaw(PSI_SHUT, 0), "color": COL["jaw"]}]
    w = _wall(-1)
    w.apply_translation((0.0, -36.0, 0.0))
    apart.append({"mesh": w, "color": COL_DETAIL})
    cam = R.frame([p["mesh"] for p in apart], azimuth_deg=56,
                  elevation_deg=20, margin=1.03)
    R.render(apart, width=1300, height=1050, supersample=2,
             **SHOW, **cam).save(out / "59-runners.png")
    print("  renders/59-runners.png")

    # the lever on its own: one piece, both sides tied by the grab bar
    one = [{"mesh": lever(PSI_SHUT, 0), "color": COL["lever"]}]
    cam = R.frame([p["mesh"] for p in one], azimuth_deg=34,
                  elevation_deg=22, margin=1.04)
    R.render(one, width=1300, height=1050, supersample=2,
             **SHOW, **cam).save(out / "60-lever.png")
    print("  renders/60-lever.png")

    # plan sections through each post's own axis
    for name, z, eye_x in (("57-pivot-section.png", PIVOT[1], 26.0),
                           ("58-drive-section.png", DRIVE_Z, 30.0)):
        sec = _sectioned(_greyed(scene(PSI_OPEN)), (0, 0, -1), (0.0, 0.0, z))
        R.render(sec, width=1250, height=1100, supersample=2, ambient=0.80,
                 key=0.26, fill=0.22, spec=0.06, edges=0.52,
                 eye=(eye_x, 0.0, 170.0), target=(eye_x, 0.0, 0.0),
                 fov_deg=32.0).save(out / name)
        print(f"  renders/{name}")


# ---------------------------------------------------------------------------
# scale reference
# ---------------------------------------------------------------------------

SCALE_DIR = Path(__file__).parent / "stl-lever"
# A tenth is what was asked for and is the right size to hold. A quarter is
# also written because at a tenth the jaw's own walls (0.35 and 0.30 mm)
# fall under one 0.4 mm extrusion, so they come out only if the slicer is
# told to detect thin walls, and then at 0.4 mm -- chunkier than scale. At a
# quarter they are real walls and the silhouette is honest.
SCALES = (0.1, 0.25)


def scale_model(out, scales=SCALES):
    """A shrunk solid of the whole assembly, to look at and hold.

    Not a working model and not meant to be one: a mechanism whose fits are
    already at the process minimum cannot be scaled down, because the fits
    do not scale with it. At a tenth the 0.35 mm sliding clearance is
    0.035 mm, a tenth of a layer, so every part fuses to its neighbour.
    That is fine here -- fused is what a scale reference wants -- but it is
    why this file is for looking at, not for trying.

    Written as one mesh in the open position and one shut, each sitting on
    z = 0 so it drops straight onto the bed.
    """
    out.mkdir(exist_ok=True)
    written = []
    for tag, psi in (("open", PSI_OPEN), ("shut", PSI_SHUT)):
        whole = trimesh.util.concatenate([p["mesh"] for p in scene(psi)])
        lo, hi = whole.bounds
        whole.apply_translation((-(lo[0] + hi[0]) / 2.0,
                                 -(lo[1] + hi[1]) / 2.0, -lo[2]))
        for scale in scales:
            m = whole.copy()
            m.apply_scale(scale)
            path = out / f"scale-1-{round(1 / scale)}-{tag}.stl"
            m.export(path)
            size = m.bounds[1] - m.bounds[0]
            written.append((path.name, size))
            print(f"  {path.relative_to(Path(__file__).parent)}"
                  f"   {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    return written


# ---------------------------------------------------------------------------
# printable parts
# ---------------------------------------------------------------------------

QUANTITY = {"body": 1, "jaw": 2, "lever": 2, "brace": 2}


def _on_bed(m):
    m = m.copy()
    m.apply_translation((0.0, 0.0, -m.bounds[0][2]))
    return m


def printable():
    """Each distinct part, turned the way it wants to go on the bed."""
    out = {"body": _on_bed(body()),
           "jaw": _on_bed(jaw(PSI_SHUT, 0)),
           "brace": _on_bed(brace(0))}
    # The lever lies down with its plates vertical and its spine flat along
    # the bed. Stood on the pivot end it is 130 mm tall on a footprint of
    # two small pads, which is asking to be knocked over.
    lv = lever(PSI_SHUT, 0)
    (px, pz), (ex, ez) = PIVOT, _on_axis(LEVER_END_Z)
    lv.apply_transform(trimesh.transformations.rotation_matrix(
        math.atan2(ez - pz, ex - px), (0, 1, 0)))
    out["lever"] = _on_bed(lv)
    return out


def write_stls(out):
    out.mkdir(exist_ok=True)
    total = 0.0
    for name, m in printable().items():
        path = out / f"{name}.stl"
        m.export(path)
        s = m.bounds[1] - m.bounds[0]
        n = QUANTITY[name]
        g = m.volume / 1000.0 * 1.27 * 0.4 + m.volume / 1000.0 * 1.27 * 0.0
        g = m.volume / 1000.0 * 1.27          # solid; infill scales it down
        total += g * n
        print(f"  {name}.stl  x{n}   {s[0]:5.1f} x {s[1]:5.1f} x {s[2]:5.1f} mm"
              f"   {g:5.1f} g solid, about {g * 0.45:4.1f} g at 35% infill")
    print(f"  whole mechanism: about {total * 0.45:.0f} g at 35% infill")


if __name__ == "__main__":
    good = checks()
    print()
    renders(Path(__file__).parent / "renders")
    print()
    write_stls(SCALE_DIR)
    print()
    scale_model(SCALE_DIR)
    # The hand now closes on the bar, so there is only one grip point left
    # to quote, and it is the one the bar's clearance forces.
    gx, gz = grip_xy()
    R = math.hypot(gx - PIVOT[0], gz - PIVOT[1])
    beta = math.atan2(gz - PIVOT[1], gx - PIVOT[0])
    gx_o = PIVOT[0] + R * math.cos(beta - PSI_OPEN)
    print(f"  grab bar: span {2 * gx_o:.0f} mm open -> {2 * gx:.0f} shut,"
          f" a {2 * (gx_o - gx):.0f} mm stroke")
    # full travel is a 93 mm stroke, wider than a hand opens. What matters
    # is how far it has to open to admit a finger, which is a lot less.
    spread = POST_TIP - LEVER_Y0
    print(f"  springing it on: {spread:.1f} mm a side, "
          f"{100 * 3 * LEVER_T * spread / (2 * R ** 2):.2f}% strain, "
          f"{2000 * 2 * LEVER_HALF_W * LEVER_T ** 3 * spread / (4 * R ** 3):.0f} N")
    sys.exit(0 if good else 1)
