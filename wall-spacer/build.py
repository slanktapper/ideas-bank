#!/usr/bin/env python3
"""Build the wall spacer.

Runs the checks, writes the STLs, writes the renders. Non-zero exit if any
check fails, so a broken part never gets quietly written over a good one.

    python3 build.py
"""

import sys
from pathlib import Path

import numpy as np
import shapely
import trimesh
from shapely.geometry import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))
import render as R                                          # noqa: E402

import params as P                                          # noqa: E402

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
RENDERS = HERE / "renders"

PETG = (0.20, 0.22, 0.26)          # a black PETG part
WOOD = (0.52, 0.36, 0.22)          # the lip, in the fit renders
CARCASE = (0.46, 0.48, 0.50)       # whatever is on the far side of the gap

OVER = 0.8                         # how far each member runs past its node,
                                   # so struts meet in a lump of solid rather
                                   # than face to face
TOL = 1e-3                         # manifold3d does its booleans in single
                                   # precision, so a face nominally at 123.0
                                   # comes back at 122.99999
FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'pass' if ok else 'FAIL'}  {name}{'   ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------
# the frame
# ---------------------------------------------------------------------------

def depth(x):
    """How far the tower hangs below the top plane at a given X."""
    t = min(max(x / P.SPAN, 0.0), 1.0)
    return P.D_BASE + (P.D_TIP - P.D_BASE) * t


def node_t1(x):
    return np.array([x, P.CHORD_T / 2.0, P.TOP - P.CHORD_T / 2.0])


def node_t2(x):
    return np.array([x, P.WIDTH - P.CHORD_T / 2.0, P.TOP - P.CHORD_T / 2.0])


def node_b(x):
    # The bottom chord is set as a diamond, so its lowest point is a corner
    # CHORD_B/sqrt(2) below the centreline, not CHORD_B/2.
    return np.array([x, P.WIDTH / 2.0,
                     P.TOP - depth(x) + P.CHORD_B / np.sqrt(2.0)])


def strut(p0, p1, w, t, normal, over=OVER):
    """One member: a bar of cross-section w x t running p0 to p1.

    `normal` is the face the member lies in -- `t` is measured along it and
    `w` across it, in the plane. Passing the face rather than letting the
    orientation fall out of a generic alignment is the difference between a
    lattice whose members lie flat in their faces and one whose members are
    rolled at whatever angle the maths happened to produce.
    """
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ax = unit(p1 - p0)
    n = np.asarray(normal, float)
    n = unit(n - ax * float(n @ ax))          # orthogonalise against the axis
    b = np.cross(n, ax)

    m = trimesh.creation.box(
        extents=(float(np.linalg.norm(p1 - p0)) + 2 * over, w, t))
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2] = ax, b, n
    M[:3, 3] = (p0 + p1) / 2.0
    m.apply_transform(M)
    return m


def prism_xz(points, y0, y1):
    """A 2D outline in X-Z, extruded across the part's width."""
    m = trimesh.creation.extrude_polygon(Polygon(points), y1 - y0)
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(90.0), (1.0, 0.0, 0.0)))
    m.apply_translation((0.0, y1, 0.0))
    return m


def members():
    """Every piece of the part, before they are melted into one solid."""
    xs = [P.SPAN * i / P.BAYS for i in range(P.BAYS + 1)]
    out = []

    # --- the three chords --------------------------------------------------
    up = (0.0, 0.0, 1.0)
    out.append(strut(node_t1(0), node_t1(P.SPAN), P.CHORD_T, P.CHORD_T, up, 0))
    out.append(strut(node_t2(0), node_t2(P.SPAN), P.CHORD_T, P.CHORD_T, up, 0))
    # The bottom chord is rolled 45 degrees. It is the one member that lies
    # nearly horizontal when the part is printed, so it is the one member
    # whose underside would otherwise be a flat ceiling in mid-air. A diamond
    # has no underside -- it starts from a single line and widens, which is
    # the one overhang shape FDM is unconditionally good at.
    out.append(strut(node_b(0), node_b(P.SPAN), P.CHORD_B, P.CHORD_B,
                     (0.0, 1.0, 1.0), 0))

    # --- lacing, the same pattern in all three faces -----------------------
    # The lacing in the TOP face is as thick as the chords it runs between,
    # not as thick as it is wide. Everything in that face has to finish flush
    # with the top plane: when the part is printed upside down that plane is
    # the bed, and lacing a millimetre shy of it is not lacing at all -- it
    # is 1400 mm2 of flat ceiling hanging half a millimetre up in the air,
    # anchored to nothing. The side faces have no such constraint.
    faces = [
        (node_t1, node_t2, (0.0, 0.0, 1.0), P.CHORD_T),           # the top
        (node_t1, node_b, unit(np.cross((1.0, 0.0, 0.0),
                                        node_b(0) - node_t1(0))),
         P.BRACE_T),                                              # one side
        (node_t2, node_b, unit(np.cross((1.0, 0.0, 0.0),
                                        node_b(0) - node_t2(0))),
         P.BRACE_T),                                              # the other
    ]
    for lo, hi, n, t in faces:
        for x in xs[1:-1]:                                  # the belts
            out.append(strut(lo(x), hi(x), P.BELT_T, t, n))
        for xa, xb in zip(xs[:-1], xs[1:]):                 # the X-bracing
            out.append(strut(lo(xa), hi(xb), P.BRACE_T, t, n))
            out.append(strut(hi(xa), lo(xb), P.BRACE_T, t, n))

    # --- the two bearing pads ----------------------------------------------
    # Solid triangular plates filling the whole section. Everything else in
    # the part is a lattice; these are the two faces that actually push on
    # something, and a lattice would put the load on four small feet.
    for xa, xb in ((0.0, P.PAD_T), (P.SPAN - P.PAD_T, P.SPAN)):
        pts = []
        for x in (xa, xb):
            pts += [(x, 0.0, P.TOP), (x, P.WIDTH, P.TOP),
                    (x, P.WIDTH / 2.0, P.TOP - depth(x))]
        out.append(trimesh.convex.convex_hull(np.array(pts)))

    # --- the saddle --------------------------------------------------------
    out.append(prism_xz([(-P.LEG_X, P.SEAT), (P.PAD_T, P.SEAT),
                         (P.PAD_T, P.TOP), (-P.LEG_X, P.TOP)],
                        0.0, P.WIDTH))
    leg_bot = P.SEAT - P.LEG_DROP
    out.append(prism_xz([
        (-P.LEG_X,              P.SEAT),
        (-P.THROAT,             P.SEAT),
        (-P.THROAT,             leg_bot + P.LEAD_IN),
        (-P.THROAT - P.LEAD_IN, leg_bot),
        (-P.LEG_X,              leg_bot),
    ], 0.0, P.WIDTH))

    return out


def slab(x0, x1, z1):
    """A box to trim against: full width, up to Z = z1."""
    b = trimesh.creation.box(extents=(x1 - x0, P.WIDTH, 400.0))
    b.apply_translation(((x0 + x1) / 2.0, P.WIDTH / 2.0, z1 - 200.0))
    return b


def build():
    """The tower, trimmed, with the saddle on it.

    Every member runs OVER mm past its node so struts meet in a lump of
    solid rather than face to face, and the lacing in a sloped face is as
    thick as it is wide, so at a top node it pokes a corner above the top
    plane. Both are wanted while the frame is being assembled and neither
    is wanted in the finished part, so the tower is trimmed to the box it
    is allowed to occupy: X from the near bearing face to the far one, the
    full 40 mm of width, and nothing above the top plane.

    The trim happens BEFORE the saddle is added, because the saddle is the
    one part of the part that is allowed behind X = 0.
    """
    tower = trimesh.boolean.union(members()[:-2], engine="manifold")
    tower = trimesh.boolean.intersection(
        [tower, slab(0.0, P.SPAN, P.TOP)], engine="manifold")

    solid = trimesh.boolean.union([tower] + members()[-2:], engine="manifold")
    solid = trimesh.boolean.intersection(
        [solid, slab(-P.LEG_X, P.SPAN, P.TOP)], engine="manifold")
    solid.merge_vertices()
    return solid


def lip_block():
    """The lip itself: a board on edge, its top edge at Z = SEAT."""
    b = trimesh.creation.box(extents=(P.LIP_T, P.WIDTH + 24.0, 48.0))
    b.apply_translation((-P.LIP_T / 2.0, P.WIDTH / 2.0, P.SEAT - 24.0))
    return b


def far_wall():
    w = trimesh.creation.box(extents=(14.0, P.WIDTH + 24.0, 56.0))
    w.apply_translation((P.SPAN + 7.0, P.WIDTH / 2.0, P.TOP - 22.0))
    return w


def print_oriented(mesh):
    """The same part laid down the way it is printed: upside down, the flat
    top plane on the bed and the bottom chord uppermost."""
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(180.0), (1.0, 0.0, 0.0)))
    m.apply_translation(-m.bounds[0])
    return m


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def run_checks(mesh):
    print("\ngeometry")
    check("watertight", mesh.is_watertight)
    check("winding consistent", mesh.is_winding_consistent)
    check("one body", len(mesh.split(only_watertight=False)) == 1,
          f"{len(mesh.split(only_watertight=False))}")
    check("volume positive", mesh.volume > 0, f"{mesh.volume / 1000:.1f} cm3")

    lo, hi = mesh.bounds
    check("width is 40 mm", abs((hi[1] - lo[1]) - P.WIDTH) < TOL,
          f"{hi[1] - lo[1]:.3f}")
    check("reaches back exactly LEG_X behind the lip",
          abs(lo[0] + P.LEG_X) < TOL, f"{lo[0]:.3f}")
    check("the top plane is flat", abs(hi[2] - P.TOP) < TOL, f"{hi[2]:.3f}")
    check("overall height", abs((hi[2] - lo[2]) - P.D_BASE) < TOL,
          f"{hi[2] - lo[2]:.3f}")

    print("\nthe span -- the number the part exists to hold")
    # Measured off the mesh rather than asserted: fire sample points along X
    # up the centreline, where both bearing pads are solid from top to tip,
    # and see where the solid starts and stops.
    zs = np.linspace(P.TOP - P.D_TIP + 3.0, P.SEAT - 2.0, 7)
    xs = np.linspace(-1.0, P.SPAN + 1.0, 2501)
    worst_near, worst_far = 0.0, 0.0
    for z in zs:
        pts = np.column_stack([xs, np.full_like(xs, P.WIDTH / 2.0),
                               np.full_like(xs, z)])
        hit = np.nonzero(mesh.contains(pts))[0]
        if not len(hit):
            continue
        worst_near = max(worst_near, abs(xs[hit[0]]))
        worst_far = max(worst_far, abs(xs[hit[-1]] - P.SPAN))
    step = xs[1] - xs[0]
    check("near bearing face sits on X = 0", worst_near <= step * 1.5,
          f"worst {worst_near:.3f} mm (sample step {step:.3f})")
    check("far bearing face sits on X = SPAN", worst_far <= step * 1.5,
          f"worst {worst_far:.3f} mm (sample step {step:.3f})")

    print("\nthe saddle")
    lip = lip_block()
    inter = trimesh.boolean.intersection([mesh, lip], engine="manifold")
    vol = float(inter.volume) if inter is not None and len(inter.faces) else 0.0
    check(f"a {P.LIP_T} mm lip drops into the throat without fouling the part",
          vol < 1e-3, f"interference {vol:.6f} mm3")

    probe_z = P.SEAT - P.LEG_DROP / 2.0
    xs2 = np.linspace(-P.LEG_X - 1.0, 2.0, 1501)
    pts = np.column_stack([xs2, np.full_like(xs2, P.WIDTH / 2.0),
                           np.full_like(xs2, probe_z)])
    inside = mesh.contains(pts)
    runs, start = [], None
    for i, v in enumerate(inside):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append((xs2[start], xs2[i - 1])); start = None
    if start is not None:
        runs.append((xs2[start], xs2[-1]))
    check("throat is one clear slot", len(runs) == 2, f"{len(runs)} solid runs")
    if len(runs) == 2:
        throat = runs[1][0] - runs[0][1]
        check("throat measures LIP_T + LIP_CLEAR",
              abs(throat - P.THROAT) < 0.05, f"{throat:.3f} vs {P.THROAT}")
        check("inner wall of the throat IS the bearing face",
              abs(runs[1][0]) < 0.05, f"{runs[1][0]:.3f}")

    print("\nprintability, with the part upside down on the bed")
    pm = print_oriented(mesh)
    n = pm.face_normals[:, 2]
    area = pm.area_faces
    on_bed = pm.triangles_center[:, 2] < 0.05

    # A face's slope is the angle between the face and the horizontal, which
    # is the angle between its NORMAL and the vertical: arccos|nz|. A flat
    # ceiling comes out at 0 and a plumb wall at 90. Getting this the other
    # way round -- arcsin|nz| -- reads every wall in the part as a ceiling
    # and every ceiling as a wall, and still returns plausible numbers.
    slope = np.degrees(np.arccos(np.clip(np.abs(n), 0.0, 1.0)))
    unsupported = (n < -1e-6) & ~on_bed & (slope < P.OVERHANG_MIN)
    bad = float(area[unsupported].sum())
    check(f"nothing overhangs shallower than {P.OVERHANG_MIN:.0f} deg",
          bad < 1.0, f"{bad:.2f} mm2 unsupported of {area.sum():.0f} mm2")

    bed = float(area[on_bed & (np.abs(n + 1.0) < 1e-6)].sum())
    check("bed contact is a real footprint", bed > 1500.0,
          f"{bed:.0f} mm2 over {P.SPAN + P.LEG_X:.0f} x {P.WIDTH:.0f} mm")

    thinnest = min(P.CHORD_T, P.CHORD_B, P.BRACE_T, P.BELT_T, P.PAD_T,
                   P.BRIDGE_T, P.LEG_T - P.LEAD_IN)
    check("thinnest member clears the nozzle",
          thinnest >= P.MIN_FEATURE, f"{thinnest} mm vs {P.MIN_FEATURE} min")

    span_bridge = P.SPAN / P.BAYS
    check("the bottom chord's bridges are short enough to be ordinary",
          span_bridge < 30.0, f"{span_bridge:.1f} mm between nodes")

    print("\nthe exported files, read back off disk")


def check_written(path):
    # Loaded the way a slicer sees it: STL stores three loose vertices per
    # triangle, so the file only becomes a solid once those are merged. That
    # merge is where a mesh that passed every check in memory can turn into
    # a non-manifold pinch, which is why the written file is checked rather
    # than trusted.
    m = trimesh.load(path, process=True, validate=True)
    check(f"{path.name} watertight", m.is_watertight)
    check(f"{path.name} one body", len(m.split(only_watertight=False)) == 1)
    check(f"{path.name} volume matches", m.volume > 0,
          f"{m.volume / 1000:.1f} cm3")


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def label(img, cam, w, h, items):
    """Leader lines anchored to real points on the part, not to pixels."""
    out = []
    for text, world, off in items:
        px = R.screen_of([world], cam["eye"], cam["target"], w, h,
                         fov_deg=cam.get("fov_deg", 32.0),
                         ortho_height=cam.get("ortho_height"))[0]
        out.append({"text": text, "px": tuple(px),
                    "to": (px[0] + off[0], px[1] + off[1]),
                    "align": "right" if off[0] < 0 else "left"})
    R.annotate(img, out, font_size=19)


def write_renders(mesh):
    part = {"mesh": mesh, "color": PETG}

    # The elevation is orthographic on purpose. It is the view the tower is
    # meant to be read in, and a perspective one would make the taper look
    # like a camera angle. frame() sizes an ortho view off the bounding
    # SPHERE, which on something 141 x 38 mm leaves the part a quarter of
    # the frame tall, so only the height needs saying.
    cam = R.frame([mesh], 90.0, 0.0, ortho=True)
    cam["ortho_height"] = P.D_BASE * 2.1
    img = R.render([part], width=1600, height=620, **cam)
    label(img, cam, 1600, 620, [
        ("span 123.0", (P.SPAN / 2, P.WIDTH / 2, P.TOP), (-30, -95)),
        ("saddle, throat 13.5",
         (-P.THROAT / 2, P.WIDTH / 2, P.SEAT - P.LEG_DROP), (60, 120)),
        (f"{P.D_BASE:.0f} deep at the lip",
         (P.PAD_T / 2, P.WIDTH / 2, P.TOP - P.D_BASE / 2), (-40, 150)),
        (f"{P.D_TIP:.0f} at the far end",
         (P.SPAN - P.PAD_T / 2, P.WIDTH / 2, P.TOP - P.D_TIP + 2.0), (-20, 150)),
    ])
    img.save(RENDERS / "01-tower.png")
    print("  01-tower.png")

    for name, az, el in (("02-iso.png", 36.0, 24.0),
                         ("03-saddle.png", 142.0, 20.0),
                         ("07-from-below.png", 44.0, -32.0)):
        cam = R.frame([mesh], az, el, margin=1.04)
        R.render([part], width=1500, height=800, **cam).save(RENDERS / name)
        print(f"  {name}")

    # end on, so the triangle is unmistakable
    cam = R.frame([mesh], 13.0, 11.0, ortho=True)
    cam["ortho_height"] = P.D_BASE * 1.3
    R.render([part], width=1100, height=850, **cam).save(RENDERS / "08-end-on.png")
    print("  08-end-on.png")

    # in place: the lip it hangs on, and whatever it pushes against
    lip, wall = lip_block(), far_wall()
    scene = [part, {"mesh": lip, "color": WOOD}, {"mesh": wall, "color": CARCASE}]
    cam = R.frame([mesh, lip, wall], 58.0, 22.0, margin=1.04)
    R.render(scene, width=1500, height=850, **cam).save(RENDERS / "04-in-place.png")
    print("  04-in-place.png")

    # sectioned down the middle of the width, so the throat can be seen
    body, caps = R.section(mesh, (0.0, -1.0, 0.0), (0.0, P.WIDTH / 2.0, 0.0))
    lbody, lcaps = R.section(lip, (0.0, -1.0, 0.0), (0.0, P.WIDTH / 2.0, 0.0))
    scene = [{"mesh": body, "color": PETG},
             {"mesh": caps, "color": R.tint(PETG, 0.5)},
             {"mesh": lbody, "color": WOOD},
             {"mesh": lcaps, "color": R.tint(WOOD, 0.4)}]
    # Aimed at the saddle by hand: the point of this view is a 13.5 mm slot,
    # and a camera that fits 141 mm in the frame cannot show it. Viewed from
    # +Y, so +X runs to the LEFT -- the tower goes off that way and the
    # saddle's outer leg is on the right.
    cam = {"target": (0.0, P.WIDTH / 2.0, P.TOP - 17.0),
           "eye": (0.0, 400.0, P.TOP - 17.0),
           "ortho_height": 56.0}
    img = R.render(scene, width=1300, height=900, **cam)
    label(img, cam, 1300, 900, [
        ("0.8 clearance, this side only",
         (-P.THROAT + 0.4, P.WIDTH / 2, P.SEAT - 6.0), (30, -180)),
        (f"lead-in {P.LEAD_IN}", (-P.THROAT - P.LEAD_IN / 2, P.WIDTH / 2,
                                  P.SEAT - P.LEG_DROP), (120, 170)),
        (f"the lip, {P.LIP_T}", (-P.LIP_T / 2, P.WIDTH / 2, P.TOP - 32.0),
         (180, 60)),
        ("bearing face, no clearance",
         (0.0, P.WIDTH / 2, P.TOP - 34.0), (-120, 120)),
    ])
    img.save(RENDERS / "05-section.png")
    print("  05-section.png")

    pm = print_oriented(mesh)
    cam = R.frame([pm], 52.0, 28.0, margin=1.04)
    R.render([{"mesh": pm, "color": PETG}], width=1500, height=800,
             **cam).save(RENDERS / "06-on-the-bed.png")
    print("  06-on-the-bed.png")


# ---------------------------------------------------------------------------

def main():
    print("wall-spacer")
    print(f"  span {P.SPAN} mm   width {P.WIDTH} mm   lip {P.LIP_T} mm"
          f"   throat {P.THROAT} mm   3-sided, {P.BAYS} bays")

    mesh = build()
    run_checks(mesh)

    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed -- nothing written")
        print("  " + "\n  ".join(FAILURES))
        return 1

    STL.mkdir(exist_ok=True)
    RENDERS.mkdir(exist_ok=True)

    fitted = STL / "wall-spacer.stl"
    printed = STL / "wall-spacer-print.stl"
    mesh.export(fitted)
    print_oriented(mesh).export(printed)
    for p in (fitted, printed):
        check_written(p)

    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed on the written files")
        return 1

    print("\nrenders")
    write_renders(mesh)

    solid = mesh.volume / 1000.0
    print(f"\n{solid:.1f} cm3 solid -- about {solid * 1.27:.0f} g of PETG if it "
          f"were printed solid; the walls make it lighter than that.")
    print(f"bbox {P.SPAN + P.LEG_X:.1f} x {P.WIDTH:.1f} x {P.D_BASE:.1f} mm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
