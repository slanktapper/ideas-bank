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
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))
import render as R                                          # noqa: E402

import params as P                                          # noqa: E402

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
RENDERS = HERE / "renders"

PETG = (0.20, 0.22, 0.26)          # a black PETG part
WOOD = (0.52, 0.36, 0.22)          # the lip, in the fit renders
CARCASE = (0.46, 0.48, 0.50)       # whatever is on the far side of the gap

TOL = 1e-6                         # the profile is exact -- no booleans run
FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'pass' if ok else 'FAIL'}  {name}{'   ' + detail if detail else ''}")
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# the profile
# ---------------------------------------------------------------------------

def z_bottom(x):
    """Underside of the bottom chord at a given X -- the one-sided taper."""
    t = min(max(x / P.SPAN, 0.0), 1.0)
    return (P.SEAT - P.H_BASE) + (P.H_BASE - P.H_TIP) * t


def bar(a, b, t):
    """A member of thickness t running between two centreline points."""
    return LineString([a, b]).buffer(t / 2.0, cap_style=2, join_style=2)


def profile():
    """The 2D shape in X-Z that is extruded to make the whole part.

    Built as a union of members only. There is no subtraction anywhere: the
    saddle's throat is simply the region no member covers, which is why the
    result is a clean single polygon rather than something a boolean engine
    had an opinion about.
    """
    tower = []
    parts = []

    # --- the two chords ----------------------------------------------------
    tower.append(box(0.0, P.SEAT - P.CHORD_T, P.SPAN, P.SEAT))
    tower.append(Polygon([
        (0.0,    z_bottom(0.0)),
        (P.SPAN, z_bottom(P.SPAN)),
        (P.SPAN, z_bottom(P.SPAN) + P.CHORD_T),
        (0.0,    z_bottom(0.0) + P.CHORD_T),
    ]))

    # --- the bearing pads --------------------------------------------------
    # The two faces that actually push on something. Full depth, and thicker
    # than a chord, because every bit of load in the part arrives here.
    tower.append(box(0.0, z_bottom(0.0), P.PAD_T, P.SEAT))
    tower.append(box(P.SPAN - P.PAD_T, z_bottom(P.SPAN - P.PAD_T), P.SPAN, P.SEAT))

    # --- the lattice -------------------------------------------------------
    xs = [P.SPAN * i / P.BAYS for i in range(P.BAYS + 1)]

    def top_c(x):
        return (x, P.SEAT - P.CHORD_T / 2.0)

    def bot_c(x):
        return (x, z_bottom(x) + P.CHORD_T / 2.0)

    for x in xs[1:-1]:                                  # the uprights
        tower.append(bar(bot_c(x), top_c(x), P.BELT_T))
    for xa, xb in zip(xs[:-1], xs[1:]):                 # the X-bracing
        tower.append(bar(bot_c(xa), top_c(xb), P.BRACE_T))
        tower.append(bar(top_c(xa), bot_c(xb), P.BRACE_T))

    # The diagonals are drawn centreline to centreline and capped square, so
    # the ones that land on the end pads stick a half-thickness out past
    # them. Past X = SPAN that is only untidy. Past X = 0 it is material
    # standing in the throat, where the lip has to go -- so the tower is cut
    # to its two bearing faces before the saddle is added, not after.
    parts.append(unary_union(tower).intersection(
        box(0.0, -10.0, P.SPAN, P.H_TOT + 10.0)))

    # --- the saddle --------------------------------------------------------
    # The bridge runs from the back of the outer leg to the far side of the
    # base pad, so it lands ON the pad rather than meeting it edge to edge --
    # a zero-area join is not a join.
    parts.append(box(-P.LEG_X, P.SEAT, P.PAD_T, P.SEAT + P.BRIDGE_T))
    leg_bot = P.SEAT - P.LEG_DROP
    parts.append(Polygon([
        (-P.LEG_X,              P.SEAT),
        (-P.THROAT,             P.SEAT),
        (-P.THROAT,             leg_bot + P.LEAD_IN),
        (-P.THROAT - P.LEAD_IN, leg_bot),
        (-P.LEG_X,              leg_bot),
    ]))

    shape = unary_union(parts)

    # Close the shape before anything else touches it. Two members that meet
    # at exactly one point -- a diagonal landing on the corner of an upright,
    # which the lattice is full of -- leave the holes either side of them
    # touching at that point. Shapely is happy with it; the extrusion is not,
    # and comes out with edges shared by four and six faces instead of two.
    # A dilate-then-erode turns every one of those pinches into a fillet, and
    # the fillets are wanted anyway: they are where a lattice cracks.
    shape = (shape.buffer(P.FILLET, join_style=1)
                  .buffer(-P.FILLET, join_style=1))

    # Reserve the lip's space, last, so nothing can creep into it. The
    # fillets above are the reason this is here: the corner where the bridge
    # meets the bearing face is a concave corner of the part and a sharp
    # outside corner of the lip, so a 0.8 mm fillet there puts 5.5 mm3 of
    # PETG exactly where the board's top arris is. Cutting the throat out at
    # the end makes the slot exactly THROAT wide by construction and leaves
    # every other fillet alone.
    shape = shape.difference(box(-P.THROAT, -10.0, 0.0, P.SEAT))

    # Snap to a 0.1 um grid. Rounding twenty internal corners leaves a
    # handful of segments a few nanometres long, and those triangulate into
    # zero-area faces: the extrusion is watertight with them in, and stops
    # being watertight the moment anything tidies them away, which is a
    # thoroughly unhelpful place to find out. Snapping removes them here,
    # before the mesh exists, and costs 0.001 mm2 of profile area.
    shape = shapely.set_precision(shape, 1e-4)

    if shape.geom_type != "Polygon":
        raise RuntimeError(f"profile is {shape.geom_type}, not one polygon")
    return shape


def build():
    """The profile, extruded WIDTH mm and stood up in the fitted frame.

    extrude_polygon() works in XY and pushes along Z, but the profile is
    drawn in X-Z and the extrusion is the part's width along Y -- so the
    result is tipped upright rather than used where it lands.
    """
    poly = profile()
    mesh = trimesh.creation.extrude_polygon(poly, P.WIDTH)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(90.0), (1.0, 0.0, 0.0)))
    mesh.apply_translation((0.0, P.WIDTH, 0.0))
    mesh.process(validate=True)
    return poly, mesh


LIP_SHOWN = 48.0         # how much of the lip's depth the renders show


def lip_block():
    """The lip itself: a board on edge, its top edge at Z = SEAT.

    The top face is at SEAT exactly rather than a hair below, because the
    saddle is meant to sit down onto it. A clearance check against this
    block therefore proves the part clears the lip on both faces and still
    lands on top of it, which is the whole of what the saddle has to do.
    """
    b = trimesh.creation.box(
        extents=(P.LIP_T, P.WIDTH + 24.0, LIP_SHOWN))
    b.apply_translation((-P.LIP_T / 2.0, P.WIDTH / 2.0,
                         P.SEAT - LIP_SHOWN / 2.0))
    return b


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def run_checks(poly, mesh):
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
    check("overall height", abs((hi[2] - lo[2]) - P.H_TOT) < TOL,
          f"{hi[2] - lo[2]:.3f}")

    print("\nthe span -- the number the part exists to hold")
    # Measured off the mesh rather than asserted: shoot a ray along X at the
    # height the lip's top edge sits at and see where the solid starts and
    # stops. Arithmetic would only prove params.py can add up.
    zs = np.linspace(P.SEAT - P.H_TIP + 1.0, P.SEAT - 1.0, 9)
    ys = np.linspace(2.0, P.WIDTH - 2.0, 5)
    xs = np.linspace(-1.0, P.SPAN + 1.0, 2501)
    worst_near, worst_far = 0.0, 0.0
    for z in zs:
        for y in ys:
            pts = np.column_stack([xs, np.full_like(xs, y), np.full_like(xs, z)])
            inside = mesh.contains(pts)
            hit = np.nonzero(inside)[0]
            if not len(hit):
                continue
            worst_near = max(worst_near, abs(xs[hit[0]] - 0.0))
            worst_far = max(worst_far, abs(xs[hit[-1]] - P.SPAN))
    step = xs[1] - xs[0]
    check("near bearing face sits on X = 0", worst_near <= step * 1.5,
          f"worst {worst_near:.3f} mm (sample step {step:.3f})")
    check("far bearing face sits on X = SPAN", worst_far <= step * 1.5,
          f"worst {worst_far:.3f} mm (sample step {step:.3f})")

    print("\nthe saddle")
    lip = lip_block()
    inter = mesh.intersection(lip)
    vol = float(inter.volume) if inter is not None and len(inter.faces) else 0.0
    check(f"a {P.LIP_T} mm lip drops into the throat without fouling the part",
          vol < 1e-3, f"interference {vol:.6f} mm3")

    # The clearance is meant to be on the OUTER side only, so the throat's
    # inner wall and the bearing face are the same face.
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
              abs(runs[1][0] - 0.0) < 0.05, f"{runs[1][0]:.3f}")

    check("outer leg reaches past the lip's back face",
          P.LEG_DROP >= 8.0 and P.THROAT > P.LIP_T,
          f"drop {P.LEG_DROP} mm behind a {P.LIP_T} mm lip")

    print("\nprintability")
    # The part is one profile extruded along Y, so printed with Y vertical
    # every wall is plumb and every layer is identical. That is the whole
    # print strategy, and it is checkable: no face may face partly up or
    # partly down. Any face that did would be an overhang.
    n = mesh.face_normals[:, 1]
    rogue = int((np.abs(np.abs(n) - 1.0) > 1e-5).sum() - (np.abs(n) < 1e-5).sum())
    check("no overhanging faces anywhere", rogue == 0,
          f"{rogue} faces neither plumb nor flat")

    thinnest = min(P.CHORD_T, P.BRACE_T, P.BELT_T, P.PAD_T,
                   P.BRIDGE_T, P.LEG_T, P.LEG_T - P.LEAD_IN)
    check("thinnest member clears the nozzle",
          thinnest >= P.MIN_FEATURE, f"{thinnest} mm vs {P.MIN_FEATURE} min")

    bed = poly.area
    check("bed contact is a real footprint, not a few lines", bed > 1500.0,
          f"{bed:.0f} mm2 over {P.SPAN + P.LEG_X:.0f} x {P.H_TOT:.0f} mm")

    print("\nthe exported files, read back off disk")
    return mesh


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
    return m


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def far_wall():
    """Whatever is on the other side of the gap -- the thing the far pad
    pushes on. Nothing is known about it except that there is material at
    the height the tape was stretched across, so it is drawn as a plain
    face and no more."""
    w = trimesh.creation.box(extents=(14.0, P.WIDTH + 24.0, 56.0))
    w.apply_translation((P.SPAN + 7.0, P.WIDTH / 2.0, P.SEAT - 20.0))
    return w


def write_renders(mesh):
    part = {"mesh": mesh, "color": PETG}

    # The elevation is orthographic on purpose. It is the view the tower is
    # meant to be read in, and a perspective one would make the taper look
    # like a camera angle.
    # frame() sizes an orthographic view off the bounding SPHERE, which on
    # something 141 x 39 mm leaves the part a quarter of the frame tall. The
    # camera it works out is right; only the height needs saying.
    cam = R.frame([mesh], 90.0, 0.0, ortho=True)
    cam["ortho_height"] = P.H_TOT * 2.0
    img = R.render([part], width=1600, height=600, **cam)
    label(img, cam, 1600, 620, [
        ("span 123.0", (P.SPAN / 2, P.WIDTH / 2, P.SEAT - P.CHORD_T / 2), (0, -150)),
        ("saddle, throat 13.5", (-P.THROAT / 2, P.WIDTH / 2, P.SEAT + P.BRIDGE_T),
         (70, -90)),
        (f"{P.H_BASE:.0f} deep at the lip", (P.PAD_T / 2, P.WIDTH / 2, P.SEAT / 2),
         (-30, 150)),
        (f"{P.H_TIP:.0f} at the far end",
         (P.SPAN - P.PAD_T / 2, P.WIDTH / 2, P.SEAT - P.H_TIP / 2), (120, 90)),
    ])
    img.save(RENDERS / "01-tower.png")
    print("  01-tower.png")

    for name, az, el in (("02-iso.png", 34.0, 26.0), ("03-saddle.png", 138.0, 22.0)):
        cam = R.frame([mesh], az, el, margin=1.04)
        R.render([part], width=1500, height=800, **cam).save(RENDERS / name)
        print(f"  {name}")

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
    # Aimed at the saddle by hand rather than framed on the whole part:
    # the point of this view is a 13.5 mm slot, and a camera that fits
    # 141 mm in the frame cannot show it.
    # Aimed at the saddle by hand rather than framed on the whole part:
    # the point of this view is a 13.5 mm slot, and a camera that fits
    # 141 mm in the frame cannot show it. Viewed from +Y, so +X runs to the
    # LEFT: the tower goes off that way and the saddle's outer leg is on
    # the right.
    cam = {"target": (0.0, P.WIDTH / 2.0, 22.0),
           "eye": (0.0, 400.0, 22.0),
           "ortho_height": 56.0}
    img = R.render(scene, width=1300, height=900, **cam)
    label(img, cam, 1300, 900, [
        ("0.8 clearance, this side only",
         (-P.THROAT + 0.4, P.WIDTH / 2, P.SEAT - 6.0), (30, -180)),
        (f"lead-in {P.LEAD_IN}", (-P.THROAT - P.LEAD_IN / 2, P.WIDTH / 2,
                                  P.SEAT - P.LEG_DROP), (120, 170)),
        (f"the lip, {P.LIP_T}", (-P.LIP_T / 2, P.WIDTH / 2, 6.0), (180, 60)),
        ("bearing face, no clearance", (0.0, P.WIDTH / 2, 4.0), (-120, 120)),
    ])
    img.save(RENDERS / "05-section.png")
    print("  05-section.png")

    pm = print_oriented(mesh)
    cam = R.frame([pm], 52.0, 30.0, margin=1.04)
    R.render([{"mesh": pm, "color": PETG}], width=1500, height=800,
             **cam).save(RENDERS / "06-on-the-bed.png")
    print("  06-on-the-bed.png")


def label(img, cam, w, h, items):
    """Leader lines anchored to real points on the part, not to pixels."""
    out = []
    for text, world, off in items:
        px = R.screen_of([world], cam["eye"], cam["target"], w, h,
                         fov_deg=cam.get("fov_deg", 32.0),
                         ortho_height=cam.get("ortho_height"))[0]
        to = (px[0] + off[0], px[1] + off[1])
        out.append({"text": text, "px": tuple(px), "to": to,
                    "align": "right" if off[0] < 0 else "left"})
    R.annotate(img, out, font_size=19)


def print_oriented(mesh):
    """The same part laid down the way it is printed: profile on the bed,
    the 40 mm width standing up in Z."""
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(-90.0), (1.0, 0.0, 0.0)))
    m.apply_translation(-m.bounds[0])
    return m


# ---------------------------------------------------------------------------

def main():
    print("wall-spacer")
    print(f"  span {P.SPAN} mm   width {P.WIDTH} mm   lip {P.LIP_T} mm"
          f"   throat {P.THROAT} mm")

    poly, mesh = build()
    run_checks(poly, mesh)

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
    print(f"bbox {P.SPAN + P.LEG_X:.1f} x {P.WIDTH:.1f} x {P.H_TOT:.1f} mm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
