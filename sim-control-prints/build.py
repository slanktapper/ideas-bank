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
    w = P.CAP_W + 2 * pad
    y0 = -pad
    y1 = P.EXT_DEPTH + P.LIP_H + pad
    rb, rt = P.R_BACK + pad, P.R_TIP + pad
    discs = [
        Point(-w / 2 + rb, y0 + rb).buffer(rb, quad_segs=32),
        Point(+w / 2 - rb, y0 + rb).buffer(rb, quad_segs=32),
        Point(-w / 2 + rt, y1 - rt).buffer(rt, quad_segs=32),
        Point(+w / 2 - rt, y1 - rt).buffer(rt, quad_segs=32),
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

        if P.OPEN_BACK:
            # Run the pocket out through the back face instead of leaving a
            # skin of material no slicer would print. The head is HEAD_D/2
            # in radius and the back face is BOSS_Y away, so the head itself
            # stops short of it -- only clearance air is being let out, and
            # the bearing ring it sits on is untouched.
            depth = P.BOSS_Y + 5.0
            slot = trimesh.creation.box(extents=[P.CBORE_D, depth, cb_h])
            slot.apply_translation(
                [x, P.BOSS_Y - depth / 2.0, P.GRIP + cb_h / 2.0])
            cuts.append(slot)

    # Union the cutters before subtracting them, rather than handing six
    # overlapping solids to one difference. Three of them share the z = GRIP
    # plane, and resolving that inside a single difference left two pairs of
    # exactly coincident vertices on the clearance-hole circle. The mesh
    # still reported watertight, one body, Euler -2 -- because the duplicates
    # kept the face indices apart -- and then collapsed into a non-manifold
    # pinch the moment it was written to STL and read back, which is the
    # version a slicer sees. Unioning first makes manifold3d resolve that
    # degeneracy once, on its own, and the exported file comes back clean.
    cutter = trimesh.boolean.union(cuts, engine="manifold")
    return trimesh.boolean.difference([mesh, cutter], engine="manifold")


def cap():
    return bolt_holes(cap_body())


def stub():
    """A length of the foot rest extrusion, for the fit renders.

    Not a part and never printed: it stands where the aluminium stands so a
    render shows the cap in context rather than floating.
    """
    # Crowned, not flat. The foot face rises CROWN above the side edges on a
    # circular arc, so the rib grooves have to follow it rather than sit on
    # one plane -- cut at a constant y and only the middle few would show.
    half = P.EXT_WIDTH / 2.0
    arc_r = (half ** 2 + P.CROWN ** 2) / (2.0 * P.CROWN)
    arc_cy = P.EXT_DEPTH - arc_r

    def crown_y(x):
        return arc_cy + np.sqrt(max(arc_r ** 2 - x ** 2, 0.0))

    r = P.EDGE_DEPTH / 2.0
    xs = np.linspace(-half, half, 121)
    sect = unary_union(
        [Point(-half + r, r).buffer(r, quad_segs=32),
         Point(+half - r, r).buffer(r, quad_segs=32)]
        + [Point(x, crown_y(x)).buffer(1e-6) for x in xs]
    ).convex_hull
    body = trimesh.creation.extrude_polygon(sect, STUB_LEN)
    body.apply_translation([0, 0, -STUB_LEN])

    cuts = []
    n = int((P.EXT_WIDTH - 8.0) / RIB_PITCH)
    for i in range(n + 1):
        x = -(n * RIB_PITCH) / 2.0 + i * RIB_PITCH
        g = trimesh.creation.cylinder(radius=RIB_R, height=STUB_LEN + 2, sections=20)
        g.apply_translation([x, crown_y(x), -STUB_LEN / 2.0])
        cuts.append(g)
    for sx in (-1, 1):
        h = trimesh.creation.cylinder(radius=P.BOLT_D / 2.0, height=30.0, sections=40)
        h.apply_translation([sx * P.HOLE_PITCH / 2.0, P.BOSS_Y, -15.0 + 0.001])
        cuts.append(h)
    return trimesh.boolean.difference([body] + cuts, engine="manifold")


def label_polys(text, size, at):
    """Glyph outlines as a shapely polygon, counters and all.

    Accumulating rings with symmetric_difference applies the even-odd rule,
    which is what keeps the middle of an O a hole instead of a disc. It
    matters here: the label is engraved rather than cut through precisely so
    those counters stay attached to the card.
    """
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from shapely.geometry import Polygon as ShPoly

    tp = TextPath((0, 0), text, size=size,
                  prop=FontProperties(family="DejaVu Sans", weight="bold"))
    out = None
    for ring in tp.to_polygons():
        if len(ring) < 3:
            continue
        poly = ShPoly(ring).buffer(0)
        out = poly if out is None else out.symmetric_difference(poly)
    minx, miny, maxx, maxy = out.bounds
    return translate_poly(out, at[0] - (minx + maxx) / 2.0,
                          at[1] - (miny + maxy) / 2.0)


def translate_poly(poly, dx, dy):
    from shapely.affinity import translate
    return translate(poly, dx, dy)


def gauge():
    """A four-layer card in the shape of the cap's mating face.

    Not a scale model and not a part: a question. Offer it up to the end of
    the extrusion and three things fall out at once -- whether the holes line
    up on 39 mm, whether its straight back edge sits flush with the back of
    the extrusion (any step is the error in BOSS_Y, read straight off), and
    whether a 25 mm lip in that position clears the base plate through the
    pedal's travel.

    The holes are CLEAR_D, the same as the real part, so that the card
    answers the question that actually matters: if this bolts on, the cap
    bolts on.
    """
    plate = trimesh.creation.extrude_polygon(profile(), P.GAUGE_T)

    cuts = []
    for sx in (-1, 1):
        h = trimesh.creation.cylinder(radius=P.CLEAR_D / 2.0,
                                      height=P.GAUGE_T + 4.0, sections=64)
        h.apply_translation([sx * P.HOLE_PITCH / 2.0, P.BOSS_Y, P.GAUGE_T / 2.0])
        cuts.append(h)

    text = label_polys(f"BOSS Y {P.BOSS_Y:.1f}", 7.0,
                       (0.0, P.EXT_DEPTH + P.LIP_H * 0.55))
    # One glyph at a time: extrude_polygon takes a Polygon, and a word is a
    # MultiPolygon.
    glyphs = getattr(text, "geoms", [text])
    for gp in glyphs:
        eng = trimesh.creation.extrude_polygon(gp, P.GAUGE_ENGRAVE + 1.0)
        eng.apply_translation([0, 0, P.GAUGE_T - P.GAUGE_ENGRAVE])
        cuts.append(eng)

    cutter = trimesh.boolean.union(cuts, engine="manifold")
    return trimesh.boolean.difference([plate, cutter], engine="manifold")


def bolt():
    """An M5 x 16 socket cap screw, drawn where it ends up."""
    parts = []
    for sx in (-1, 1):
        x = sx * P.HOLE_PITCH / 2.0
        shank = trimesh.creation.cylinder(radius=P.BOLT_D / 2.0,
                                          height=P.BOLT_LEN, sections=40)
        shank.apply_translation([x, P.BOSS_Y, P.CAP_L - P.HEAD_SINK - P.HEAD_H
                                 - P.BOLT_LEN / 2.0])
        # A domed head, since that is what it is. The spherical cap through
        # base radius HEAD_D/2 and height HEAD_H has sphere radius
        # (r^2 + h^2) / 2h, which at 5 and 5 comes out a hemisphere.
        r, h = P.HEAD_D / 2.0, P.HEAD_H
        sph_r = (r ** 2 + h ** 2) / (2.0 * h)
        dome = trimesh.creation.icosphere(subdivisions=3, radius=sph_r)
        dome.apply_translation([0, 0, h - sph_r])
        dome = trimesh.intersections.slice_mesh_plane(
            dome, plane_normal=[0, 0, 1], plane_origin=[0, 0, 0], cap=True)
        dome.apply_translation([x, P.BOSS_Y, P.CAP_L - P.HEAD_SINK - h])
        parts += [shank, dome]
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
    wall_front = P.EXT_DEPTH + P.LIP_H - P.BOSS_Y - P.CBORE_D / 2.0
    if P.OPEN_BACK:
        # The bore is open at the back on purpose. What has to be true is
        # that the head never reaches the back face -- otherwise it is not a
        # pocket with a side missing, it is a head hanging out of the part.
        head_clear = P.BOSS_Y - P.HEAD_D / 2.0
        check("counterbore is open at the back, deliberately", True,
              f"{P.CBORE_WALL_BACK:.2f} mm of wall was unprintable")
        check("the head itself still stops short of the back face",
              head_clear > 0.0, f"{head_clear:.2f} mm to spare")
    else:
        check("wall behind the counterbore, on paper",
              P.CBORE_WALL_BACK >= P.MIN_WALL,
              f"{P.CBORE_WALL_BACK:.2f} >= {P.MIN_WALL:.2f} mm")
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
    rad = P.CBORE_D / 2 + P.MIN_WALL
    wall_zs = np.linspace(P.GRIP + 0.3, P.CAP_L - 0.05, 12)
    shell = np.vstack([ring(rad, z) for z in wall_zs])

    # Which samples are allowed to be air. Not "anything behind the back
    # face" -- that would also forgive the pocket eating sideways into the
    # cap. Only samples inside the slot that was cut on purpose: behind the
    # bolt axis, and no further out than the bore is wide.
    dx = np.abs(np.abs(shell[:, 0]) - P.HOLE_PITCH / 2)
    dy = shell[:, 1] - P.BOSS_Y
    opened = (dy < 0) & (dx <= P.CBORE_D / 2 + 1e-6) if P.OPEN_BACK \
        else np.zeros(len(shell), bool)
    ok = m.contains(shell) | opened
    check("measured: MIN_WALL of material all round every counterbore",
          ok.all(),
          f"{ok.sum()}/{len(ok)} in material, {opened.sum()} in the opening")

    # And the slot stays a slot: material still stands immediately either
    # side of it, all the way down the open back. Probed just outboard of
    # the bore rather than out at `rad`, which on the outboard side lands
    # within a hair of the cap's own edge and tests the sample point rather
    # than the part.
    flanks = np.array([[sx * P.HOLE_PITCH / 2 + ox * (P.CBORE_D / 2 + 0.3), y, z]
                       for sx in (-1, 1) for ox in (-1, 1)
                       for y in (1.5, 2.5, 3.5, 4.5)
                       for z in wall_zs])
    flank_ok = m.contains(flanks)
    check("measured: the slot does not break out of the cap's sides",
          flank_ok.all(), f"{flank_ok.sum()}/{len(flank_ok)} beside the slots")
    edge = P.CAP_W / 2 - P.HOLE_PITCH / 2 - P.CBORE_D / 2
    check("material outboard of each bore, to the cap's edge",
          edge >= P.MIN_WALL, f"{edge:.2f} >= {P.MIN_WALL:.2f} mm")

    # The whole case for opening the back is that the head still has a
    # complete ring to bear on. Check it rather than assert it.
    bearing = ring(P.HEAD_D / 2 - 0.2, P.GRIP - 0.3)
    seated = m.contains(bearing)
    check("measured: the head bears on a complete ring of material",
          seated.all(), f"{seated.sum()}/{len(seated)} of the bearing ring")

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

    run_gauge_checks(m)

    print(f"\n{len(FAILURES)} failed")
    return not FAILURES


def run_gauge_checks(cap_mesh):
    print("\n  -- the alignment gauge --")
    g = gauge()
    glo, ghi = g.bounds
    clo, chi = cap_mesh.bounds

    check("gauge is watertight", g.is_watertight)
    check("gauge is one body", len(g.split(only_watertight=False)) == 1)
    check("gauge is exactly GAUGE_LAYERS layers thick",
          abs((ghi[2] - glo[2]) - P.GAUGE_T) < TOL,
          f"{ghi[2] - glo[2]:.2f} mm = {P.GAUGE_LAYERS} x {P.GAUGE_T / P.GAUGE_LAYERS:.1f}")
    check("gauge silhouette is the cap's silhouette",
          abs((ghi[0] - glo[0]) - (chi[0] - clo[0])) < TOL
          and abs((ghi[1] - glo[1]) - (chi[1] - clo[1])) < TOL,
          f"{ghi[0] - glo[0]:.1f} x {ghi[1] - glo[1]:.1f} mm")
    check("gauge back edge is at y = 0, to read the step against",
          abs(glo[1]) < TOL)

    axes = [(-P.HOLE_PITCH / 2.0, P.BOSS_Y), (P.HOLE_PITCH / 2.0, P.BOSS_Y)]
    zs = np.linspace(0.1, P.GAUGE_T - 0.1, 5)
    on_axis = np.array([[x, y, z] for x, y in axes for z in zs])
    check("gauge bolt holes go right through", not g.contains(on_axis).any())

    def gring(rad, z, n=20):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return np.array([[x + rad * np.cos(t), y + rad * np.sin(t), z]
                         for x, y in axes for t in a])

    check("gauge holes are the same clearance as the cap's",
          not g.contains(gring(P.CLEAR_D / 2 - 0.1, P.GAUGE_T / 2)).any()
          and g.contains(gring(P.CLEAR_D / 2 + 0.3, P.GAUGE_T / 2)).all())

    # The label is engraved, not cut through -- otherwise the counters of the
    # O and the B drop out as loose discs on a 0.8 mm card.
    plain = trimesh.creation.extrude_polygon(profile(), P.GAUGE_T).volume
    holes = 2 * np.pi * (P.CLEAR_D / 2) ** 2 * P.GAUGE_T
    check("the label actually engraved something",
          g.volume < plain - holes - 1.0,
          f"{plain - holes - g.volume:.1f} mm3 of lettering")
    xs = np.linspace(-14, 14, 15)
    ys = np.linspace(P.EXT_DEPTH + P.LIP_H * 0.55 - 4,
                     P.EXT_DEPTH + P.LIP_H * 0.55 + 4, 7)
    floor = np.array([[x, y, 0.1] for x in xs for y in ys])
    check("the label left a floor and did not cut through",
          g.contains(floor).all())
    return g


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
    # az 290, not the 52 the other shots use: from the +X +Y side the camera
    # looks back along +X and the engraved label renders mirrored. Checked
    # with screen_of rather than squinted at.
    shot("07-gauge.png", [{"mesh": gauge(), "color": (0.85, 0.55, 0.15)}],
         290, 50, margin=1.06)

    # Imported here, not at the top: drawing.py imports this module back for
    # profile(), and at module level that is a cycle.
    import drawing
    print(f"  {Path(drawing.draw()).name}")

    shot("06-side-elevation.png",
         [{"mesh": st, "color": GREY}, {"mesh": m, "color": PETG}],
         0, 0, margin=1.04, ortho=True, w=1100, h=1300)


def verify_exports(files):
    """Read each STL back off disk and check the file, not the mesh.

    This exists because the checks above all passed on a cap whose STL was
    not watertight. An in-memory mesh can carry two coincident vertices and
    still report watertight, one body, the right Euler number -- the face
    indices keep them apart. Write it out and read it back and they merge
    into a non-manifold pinch. The file is what the slicer opens, so the
    file is what has to be checked.
    """
    print("\nexported files")
    ok = True
    for name, mem in files.items():
        disk = trimesh.load(STL / name)
        bodies = len(disk.split(only_watertight=False))
        good = (disk.is_watertight and bodies == 1
                and disk.euler_number == mem.euler_number
                and abs(disk.volume - mem.volume) < 1e-3)
        ok &= good
        if not good:
            FAILURES.append(f"export {name}")
        print(f"  {'pass' if good else 'FAIL'}  {name}   watertight "
              f"{disk.is_watertight}, {bodies} body, Euler "
              f"{disk.euler_number} (mesh {mem.euler_number})")
    return ok


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
    g = gauge()
    g.export(STL / "alignment-gauge.stl")
    if not verify_exports({"footrest-end-cap.stl": m, "alignment-gauge.stl": g}):
        print("\nexported files failed verification -- do not print these")
        return 1
    print(f"\nstl\n  footrest-end-cap.stl   {m.volume / 1000:.2f} cm3, print 4x")
    print(f"  alignment-gauge.stl    {g.volume / 1000:.2f} cm3, "
          f"{P.GAUGE_LAYERS} layers, print 1 first")
    write_renders(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
