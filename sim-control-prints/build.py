#!/usr/bin/env python3
"""Build the VKB T-Rudder Mk.V foot rest end cap.

Runs the checks, writes the STL, writes the renders. Non-zero exit if any
check fails, so a broken part never gets quietly written over a good one.

    python3 build.py
"""

import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))
import render as R                                          # noqa: E402

import params as P                                          # noqa: E402

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
RENDERS = HERE / "renders"

STUB_LEN = 45.0          # how much of the extrusion the renders show
RIB_PITCH = 2.8
RIB_R = 0.8

GREY = (0.62, 0.64, 0.68)         # the aluminium extrusion
PETG = (0.20, 0.22, 0.26)         # a black PETG cap
STEEL = (0.78, 0.80, 0.84)        # a bolt

# manifold3d does its booleans in single precision, so a face nominally at
# 25.3 comes back at 25.299998. Dimension checks are held to a micron, which
# is four orders of magnitude tighter than anything an FDM printer can hold
# and still loose enough not to trip over float32.
TOL = 1e-3

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'pass' if ok else 'FAIL'}  {name}{'   ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


# --- geometry ---------------------------------------------------------------

def profile(pad=0.0):
    """The cap's XY outline: a rounded rectangle, generous at the lip tip.

    Built as the convex hull of four discs so the two corner radii can differ
    without any arc arithmetic. Convexity is not incidental -- chamfering
    below relies on it.
    """
    w, d = P.CAP_W + 2 * pad, P.EXT_DEPTH + P.LIP_H + 2 * pad
    y0, y1 = -pad, d - pad
    rb, rt = P.R_BACK + pad, P.R_TIP + pad
    discs = [
        Point(-w / 2 + rb + pad, y0 + rb).buffer(rb, quad_segs=32),
        Point(+w / 2 - rb - pad, y0 + rb).buffer(rb, quad_segs=32),
        Point(-w / 2 + rt + pad, y1 - rt).buffer(rt, quad_segs=32),
        Point(+w / 2 - rt - pad, y1 - rt).buffer(rt, quad_segs=32),
    ]
    return unary_union(discs).convex_hull


def _ring(poly, z):
    xy = np.asarray(poly.exterior.coords[:-1])
    return np.column_stack([xy, np.full(len(xy), z)])


def cap_body():
    """The outer solid: a prism with the two end faces chamfered.

    A convex hull over four stacked outlines -- inset, full, full, inset --
    is exactly a chamfered prism when the outline is convex, and it is
    manifold by construction, which a boolean of mitred side walls is not.
    """
    base = profile()
    pts = np.vstack([
        _ring(base.buffer(-P.CH_MATE), 0.0),
        _ring(base, P.CH_MATE),
        _ring(base, P.CAP_L - P.CH_OUTER),
        _ring(base.buffer(-P.CH_OUTER), P.CAP_L),
    ])
    return trimesh.points.PointCloud(pts).convex_hull


def bolt_holes(mesh):
    """Through hole plus counterbore, at each boss."""
    cuts = []
    for sx in (-1, 1):
        x = sx * P.HOLE_PITCH / 2.0
        thru = trimesh.creation.cylinder(radius=P.CLEAR_D / 2.0,
                                         height=P.CAP_L + 4.0, sections=64)
        thru.apply_translation([x, P.BOSS_Y, P.CAP_L / 2.0])
        cuts.append(thru)

        cb_h = P.CAP_L - P.GRIP + 2.0
        cb = trimesh.creation.cylinder(radius=P.CBORE_D / 2.0,
                                       height=cb_h, sections=64)
        cb.apply_translation([x, P.BOSS_Y, P.GRIP + cb_h / 2.0])
        cuts.append(cb)
    return trimesh.boolean.difference([mesh] + cuts, engine="manifold")


def cap():
    return bolt_holes(cap_body())


def stub():
    """A length of the foot rest extrusion, for the fit renders.

    Not a part and never printed: it stands where the aluminium stands so a
    render shows the cap in context rather than floating.
    """
    r = P.EXT_DEPTH / 2.0
    sect = unary_union([
        Point(-P.EXT_WIDTH / 2 + r, r).buffer(r, quad_segs=32),
        Point(+P.EXT_WIDTH / 2 - r, r).buffer(r, quad_segs=32),
    ]).convex_hull
    body = trimesh.creation.extrude_polygon(sect, STUB_LEN)
    body.apply_translation([0, 0, -STUB_LEN])

    cuts = []
    n = int((P.EXT_WIDTH - 8.0) / RIB_PITCH)
    for i in range(n + 1):
        x = -(n * RIB_PITCH) / 2.0 + i * RIB_PITCH
        g = trimesh.creation.cylinder(radius=RIB_R, height=STUB_LEN + 2, sections=20)
        g.apply_translation([x, P.EXT_DEPTH, -STUB_LEN / 2.0])
        cuts.append(g)
    for sx in (-1, 1):
        h = trimesh.creation.cylinder(radius=P.BOLT_D / 2.0, height=30.0, sections=40)
        h.apply_translation([sx * P.HOLE_PITCH / 2.0, P.BOSS_Y, -15.0 + 0.001])
        cuts.append(h)
    return trimesh.boolean.difference([body] + cuts, engine="manifold")


def bolt():
    """An M5 x 16 socket cap screw, drawn where it ends up."""
    parts = []
    for sx in (-1, 1):
        x = sx * P.HOLE_PITCH / 2.0
        shank = trimesh.creation.cylinder(radius=P.BOLT_D / 2.0,
                                          height=P.BOLT_LEN, sections=40)
        shank.apply_translation([x, P.BOSS_Y, P.CAP_L - P.HEAD_SINK - P.HEAD_H
                                 - P.BOLT_LEN / 2.0])
        head = trimesh.creation.cylinder(radius=P.HEAD_D / 2.0,
                                         height=P.HEAD_H, sections=40)
        head.apply_translation([x, P.BOSS_Y, P.CAP_L - P.HEAD_SINK - P.HEAD_H / 2.0])
        parts += [shank, head]
    return trimesh.util.concatenate(parts)


# --- checks -----------------------------------------------------------------

def run_checks(m):
    print("\nchecks")

    check("mesh is watertight", m.is_watertight)
    check("mesh is one body", len(m.split(only_watertight=False)) == 1)
    check("mesh winding is consistent", m.is_winding_consistent)
    check("volume is positive", m.volume > 0, f"{m.volume / 1000:.2f} cm3")

    lo, hi = m.bounds
    check("width is CAP_W", abs((hi[0] - lo[0]) - P.CAP_W) < TOL,
          f"{hi[0] - lo[0]:.2f} mm")
    proud = (P.CAP_W - P.EXT_WIDTH) / 2.0
    check("cap is not noticeably proud of the extrusion", proud <= 0.5,
          f"{proud:.2f} mm a side")
    check("depth is EXT_DEPTH + LIP_H",
          abs((hi[1] - lo[1]) - (P.EXT_DEPTH + P.LIP_H)) < TOL,
          f"{hi[1] - lo[1]:.2f} mm")
    check("length along the axis is CAP_L", abs((hi[2] - lo[2]) - P.CAP_L) < TOL,
          f"{hi[2] - lo[2]:.2f} mm")
    check("lip stands LIP_H proud of the ribbed face",
          abs(hi[1] - (P.EXT_DEPTH + P.LIP_H)) < TOL, f"{P.LIP_H:.1f} mm")

    # --- the bolts fit, and the arithmetic of a 16 mm bolt works out --------
    engage = P.BOLT_LEN - P.GRIP
    check("grip + engagement equals the bolt length",
          abs((P.GRIP + engage) - P.BOLT_LEN) < 1e-9,
          f"{P.GRIP:.1f} + {engage:.1f} = {P.BOLT_LEN:.1f} mm")
    check("thread engagement clears the minimum", engage >= P.ENGAGE_MIN,
          f"{engage:.1f} >= {P.ENGAGE_MIN:.1f} mm")
    check("counterbore swallows the head",
          P.CAP_L - P.GRIP >= P.HEAD_H + P.HEAD_SINK - 1e-9,
          f"{P.CAP_L - P.GRIP:.1f} >= {P.HEAD_H + P.HEAD_SINK:.1f} mm")
    check("counterbore clears the head diameter", P.CBORE_D > P.HEAD_D,
          f"{P.CBORE_D:.1f} > {P.HEAD_D:.1f} mm")

    # --- the counterbore has to live inside EXT_DEPTH, which is tight -------
    wall_back = P.BOSS_Y - P.CBORE_D / 2.0
    wall_front = P.EXT_DEPTH - P.BOSS_Y - P.CBORE_D / 2.0
    check("wall behind the counterbore, on paper", wall_back >= P.MIN_WALL,
          f"{wall_back:.2f} >= {P.MIN_WALL:.2f} mm")
    check("wall in front of the counterbore, on paper",
          wall_front >= P.MIN_WALL,
          f"{wall_front:.2f} >= {P.MIN_WALL:.2f} mm")
    check("counterbores do not run into each other",
          P.HOLE_PITCH - P.CBORE_D >= 2 * P.MIN_WALL,
          f"{P.HOLE_PITCH - P.CBORE_D:.2f} mm between them")

    # --- the holes are actually holes, and in the right places --------------
    axes = [(-P.HOLE_PITCH / 2.0, P.BOSS_Y), (P.HOLE_PITCH / 2.0, P.BOSS_Y)]
    zs = np.linspace(0.3, P.CAP_L - 0.3, 25)
    on_axis = np.array([[x, y, z] for x, y in axes for z in zs])
    check("both bolt axes are clear through the part",
          not m.contains(on_axis).any())

    # a ring just inside the clearance hole is void; just outside is material
    def ring(rad, z, n=24):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return np.array([[x + rad * np.cos(t), y + rad * np.sin(t), z]
                         for x, y in axes for t in a])

    check("clearance hole is at least CLEAR_D",
          not m.contains(ring(P.CLEAR_D / 2 - 0.1, P.GRIP / 2)).any())
    check("material surrounds the clearance hole in the grip",
          m.contains(ring(P.CLEAR_D / 2 + 0.3, P.GRIP / 2)).all())
    check("counterbore is open at CBORE_D",
          not m.contains(ring(P.CBORE_D / 2 - 0.1, P.CAP_L - 1.0)).any())
    check("counterbore has a floor to bear on",
          m.contains(ring(P.CBORE_D / 2 - 0.1, P.GRIP - 0.4)).all())

    # The two checks above are arithmetic on BOSS_Y, and arithmetic does not
    # know about chamfers. A 1 mm chamfer on the outer face took the real
    # wall beside a head from 1.40 mm to 0.40 mm and both of them still said
    # pass. This one asks the mesh: is there MIN_WALL of material all the way
    # round each counterbore, at every height it exists, including the last
    # layer. Measure the part, not the plan.
    wall_zs = np.linspace(P.GRIP + 0.3, P.CAP_L - 0.05, 12)
    shell = np.vstack([ring(P.CBORE_D / 2 + P.MIN_WALL, z) for z in wall_zs])
    inside = m.contains(shell)
    check("measured: MIN_WALL of material all round every counterbore",
          inside.all(),
          f"{inside.sum()}/{len(inside)} sample points in material")

    # --- the mating face is flat where it meets aluminium -------------------
    xs = np.linspace(-P.EXT_WIDTH / 2 + 3, P.EXT_WIDTH / 2 - 3, 9)
    ys = np.linspace(2.0, P.EXT_DEPTH - 2.0, 5)
    just_inside = np.array([[x, y, 0.2] for x in xs for y in ys])
    keep = np.array([min(abs(x - ax), 9) > P.CBORE_D / 2 + 0.5
                     for x in xs for _ in ys for ax in [0]])
    near_hole = np.array([
        min(np.hypot(p[0] - ax, p[1] - ay) for ax, ay in axes) < P.CLEAR_D / 2 + 0.4
        for p in just_inside])
    check("mating face is solid where it lands on the aluminium",
          m.contains(just_inside[~near_hole]).all())

    # --- it is the same part at both ends -----------------------------------
    flipped = m.copy()
    flipped.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi, [0, 1, 0], [0, 0, P.CAP_L / 2.0]))
    check("the part is its own mirror, so one STL serves both ends",
          np.allclose(np.sort(m.bounds, axis=0), np.sort(flipped.bounds, axis=0),
                      atol=TOL)
          and abs(flipped.volume - m.volume) < TOL)

    # --- it fits the printer ------------------------------------------------
    check("fits the H2D bed", all(hi - lo < np.array([325, 320, 325])),
          " x ".join(f"{v:.1f}" for v in (hi - lo)) + " mm")

    print(f"\n{len(FAILURES)} failed")
    return not FAILURES


# --- renders ----------------------------------------------------------------

def shot(name, parts, az, el, margin=1.08, w=1400, h=1000, ortho=False):
    meshes = [p["mesh"] for p in parts]
    cam = R.frame(meshes, az, el, margin=margin, ortho=ortho)
    img = R.render(parts, width=w, height=h, **cam)
    img.save(RENDERS / name)
    print(f"  {name}")


def dimensioned_section(parts, org):
    """The section with the numbers on it.

    The point of this one is the bolt: 16 mm of it, 7 inside the cap and 9
    inside the boss, with the head buried. Those three numbers are the whole
    reason the cap is 13 mm long, so they are written on the picture rather
    than left in params.py.
    """
    W, H = 1500, 1150
    meshes = [p["mesh"] for p in parts]
    cam = R.frame(meshes, 180, 0, margin=1.30, ortho=True)
    img = R.render(parts, width=W, height=H, **cam)

    x = -P.HOLE_PITCH / 2.0
    anchors = {
        "head, 1.0 mm below the face": (x, P.BOSS_Y, P.CAP_L - P.HEAD_SINK),
        f"counterbore {P.CBORE_D:.1f} mm": (x + 0, P.BOSS_Y + P.CBORE_D / 2,
                                            P.CAP_L - 3.0),
        f"grip {P.GRIP:.0f} mm in the cap": (x, P.BOSS_Y - 1.0, P.GRIP / 2),
        f"engagement {P.BOLT_LEN - P.GRIP:.0f} mm in the boss":
            (x, P.BOSS_Y, -(P.BOLT_LEN - P.GRIP) / 2),
        f"lip {P.LIP_H:.0f} mm proud": (x, P.EXT_DEPTH + P.LIP_H - 3.0, 1.5),
        "mating face": (x, P.EXT_DEPTH - 2.0, 0.0),
        f"cap {P.CAP_L:.0f} mm long": (x, 1.0, P.CAP_L / 2),
    }
    px = R.screen_of(list(anchors.values()), cam["eye"], cam["target"], W, H,
                     ortho_height=cam["ortho_height"])
    # label lanes, hand-placed: the leaders all come off a part only 37 mm
    # tall, so letting them find their own height stacks them on top of
    # each other. x is pulled well inside the frame -- "engagement 9 mm in
    # the boss" is 300 px of text and runs off the edge from any closer.
    lanes = [150, 260, 700, 840, 330, 560, 980]
    items = []
    for (text, _), q, lane in zip(anchors.items(), px, lanes):
        right = q[0] > W * 0.5
        items.append({"text": text, "px": (q[0], q[1]),
                      "to": (W - 470 if right else 300, lane),
                      "align": "left" if right else "right"})
    R.annotate(img, items, font_size=21)
    img.save(RENDERS / "05-section-dimensioned.png")
    print("  05-section-dimensioned.png")


def write_renders(m):
    print("\nrenders")
    RENDERS.mkdir(exist_ok=True)
    st, bo = stub(), bolt()

    shot("01-cap.png", [{"mesh": m, "color": PETG}], 48, 26)
    shot("02-cap-back.png", [{"mesh": m, "color": PETG}], 215, 24)
    shot("03-on-the-extrusion.png",
         [{"mesh": st, "color": GREY}, {"mesh": m, "color": PETG}], 52, 22)
    shot("04-bolted.png",
         [{"mesh": st, "color": GREY}, {"mesh": m, "color": PETG},
          {"mesh": bo, "color": STEEL}], 62, 40)

    # Section on a bolt axis, viewed square to the cut. The normal points at
    # the material being kept, so [1,0,0] keeps everything inboard of the
    # left-hand bolt and leaves its axis lying in the cut face.
    org = [-P.HOLE_PITCH / 2.0, 0, 0]
    cut = [R.section(x, [1, 0, 0], org) for x in (st, m, bo)]
    (st_b, st_c), (cap_b, cap_c), (bo_b, bo_c) = cut
    sect_parts = [
        {"mesh": st_b, "color": GREY}, {"mesh": st_c, "color": R.tint(GREY)},
        {"mesh": cap_b, "color": PETG}, {"mesh": cap_c, "color": R.tint(PETG)},
        {"mesh": bo_b, "color": STEEL}, {"mesh": bo_c, "color": R.tint(STEEL)},
    ]
    dimensioned_section(sect_parts, org)

    # looking along X: the only view that shows the lip standing off the
    # ribbed face, which is the whole point of the part
    shot("06-side-elevation.png",
         [{"mesh": st, "color": GREY}, {"mesh": m, "color": PETG}],
         0, 0, margin=1.04, ortho=True, w=1100, h=1300)


def main():
    print(f"cap  {P.EXT_WIDTH:.1f} x {P.EXT_DEPTH + P.LIP_H:.1f} x {P.CAP_L:.1f} mm"
          f"   lip {P.LIP_H:.0f} mm proud   M5 at {P.HOLE_PITCH:.1f} mm")
    m = cap()
    ok = run_checks(m)
    if not ok:
        print("\nchecks failed -- nothing written")
        return 1
    STL.mkdir(exist_ok=True)
    m.export(STL / "footrest-end-cap.stl")
    print(f"\nstl\n  footrest-end-cap.stl   {m.volume / 1000:.2f} cm3, print 4x")
    write_renders(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
