"""Three two-colour tags -- PLA, PETG, ABS -- to tape to the side of a bin.

Each tag is a rounded slab printed face down, so the visible face picks up the
plate texture. Through the thickness it is two filaments: a jade white skin
four layers deep on the printed face, and the letter colour behind it, coming
through that skin to form the word. Two STLs per tag, one per filament, which
puts the colour split in the geometry rather than in a slicer painting session
that has to be redone every time the model changes.

Rob asked for it this way round to spend as little jade white as possible. The
white is the thin part, so it is the part that can ghost -- hence four layers
rather than two. params.py has that argument in full.

The lettered face is the one at z=0. The STLs come out that way round, so they
load lettering-down with no rotation -- see print-guide.md.

    python3 build.py              # stl/ and renders/
    python3 build.py --no-renders # just the STLs, in a couple of seconds

Geometry notes worth keeping:

* The colour part is built as the literal complement of the white one -- the
  full slab minus the white. So the two cannot gap and cannot overlap, whatever
  the boolean engine does with the letter walls: together they are exactly the
  plain slab, which test_fit.py checks by volume to a millionth of a cubic mm.

* The letter cutter is pushed 0.1 mm below z=0 before the boolean. Cutting with
  a face exactly coincident with the face being cut is how a boolean hands back
  a mesh with holes in it; the overshoot costs nothing because everything below
  z=0 is outside the tag anyway.

* All three words are set at ONE cap height, solved from whichever word is
  widest, so the set reads as a set. "PETG" is that word, and it is what sizes
  the other two.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import trimesh
from shapely.geometry import box
from shapely.ops import unary_union

import params as P

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '3d-tools'))
import render as R                                      # noqa: E402
from text3d import Face                                 # noqa: E402

STL = HERE / 'stl'
RENDERS = HERE / 'renders'


# ---------------------------------------------------------------------------
# lettering
# ---------------------------------------------------------------------------

def common_cap(face, words):
    """The one cap height every tag is set at.

    Geometry out of text3d scales linearly with cap height, so a single
    measurement at any size solves it exactly -- no search, no iteration.
    Both the panel width and the panel height are constraints, and the
    binding one wins. Height is measured on the *inked* extent, which for
    round letters like the B, S and G here overshoots the cap line a little.
    """
    avail_w = P.TAG_W - 2 * P.MARGIN_X
    avail_h = P.TAG_H - 2 * P.MARGIN_Y

    probe = 10.0
    widest = 0.0
    tallest = 0.0
    for w in words:
        g, _ = face.line(w, probe)
        x0, y0, x1, y1 = g.bounds
        widest = max(widest, x1 - x0)
        tallest = max(tallest, y1 - y0)

    by_width = probe * avail_w / widest
    by_height = probe * avail_h / tallest
    return min(by_width, by_height, P.MAX_CAP), by_width, by_height


def word_polygon(face, word, cap):
    """One word, placed on the tag, as a shapely geometry.

    Centred left-to-right on its inked extent, which is the optical centre --
    centring on the advance width would push it left by the right side bearing.

    Vertically it is centred on its CAP BOX, not on its ink: the baseline
    lands at the same height on all three tags, so the set lines up when the
    three are side by side on the shelf. All three words are caps with no
    descender, so the only thing outside the cap box is the few tenths that
    round letters overshoot by, and that overshoot is symmetric -- it costs
    nothing at the top or bottom margin.

    And it is MIRRORED, which is the one thing in this file that will look
    like a bug to whoever reads it next. It is not. The lettering is in the
    face at z=0, and z=0 is the face against the plate. To look at that face
    on a finished tag you turn the tag over, so you are reading it from -Z.
    Text laid out to read correctly from +Z -- the way it looks in any viewer
    -- comes off the printer backwards. Mirroring here is what makes the
    printed part right, and the renders are generated from the same geometry,
    so they show it the way Rob will hold it.
    """
    from shapely import affinity

    g, _ = face.line(word, cap)
    x0, _, x1, _ = g.bounds
    g = affinity.translate(g,
                           P.TAG_W / 2 - (x0 + x1) / 2,     # ink-centred in x
                           P.TAG_H / 2 - cap / 2)           # cap box centred in y
    g = affinity.scale(g, xfact=-1.0, yfact=1.0,
                       origin=(P.TAG_W / 2, P.TAG_H / 2))   # read from below
    if P.LETTER_GROW:
        g = g.buffer(P.LETTER_GROW, join_style=2)
    return g


# ---------------------------------------------------------------------------
# solids
# ---------------------------------------------------------------------------

def outline():
    """The tag footprint: exactly TAG_W by TAG_H, with CORNER_R corners.

    Inset a box by the radius and dilate it back out -- the result is the
    rounded rectangle at its true outside size, rather than a box eroded
    smaller the way buffer(-r).buffer(r) would leave it.
    """
    r = P.CORNER_R
    return box(r, r, P.TAG_W - r, P.TAG_H - r).buffer(r, quad_segs=24)


def prism(geom, height, z=0.0):
    """Extrude a shapely polygon or multipolygon into one mesh."""
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    parts = [trimesh.creation.extrude_polygon(p, height) for p in polys]
    m = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    if z:
        m.apply_translation((0.0, 0.0, z))
    return m


def tag(face, word, cap):
    """(white, colour) for one tag, as two watertight meshes that interlock.

    `white` is the jade white skin on the printed face, WHITE_D deep, with the
    word punched out of it. `colour` is everything else: the letters filling
    those holes, and the slab behind the skin that they join onto -- one solid,
    because the letters are continuous with the body behind them rather than
    being loose tiles sitting in a pocket. Nothing in the set needs gluing.
    """
    letters_2d = word_polygon(face, word, cap)
    slab = prism(outline(), P.TAG_T)

    # Down through z=0 so the cut face is not coincident with the tag face.
    cutter = prism(letters_2d, P.WHITE_D + 0.1, z=-0.1)
    skin = prism(outline(), P.WHITE_D)
    white = trimesh.boolean.difference([skin, cutter], engine='manifold')

    # The complement, so white + colour is exactly the slab by construction.
    colour = trimesh.boolean.difference([slab, white], engine='manifold')
    return white, colour


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def build(verbose=True):
    face = Face(P.FACE)
    cap, by_w, by_h = common_cap(face, [w for _, w, _ in P.TAGS])

    if verbose:
        print(f"cap height {cap:.2f} mm "
              f"(width allows {by_w:.2f}, height allows {by_h:.2f}, "
              f"ceiling {P.MAX_CAP:.2f})")
        print(f"tag {P.TAG_W:.0f} x {P.TAG_H:.0f} x {P.TAG_T:.2f} mm: "
              f"jade white skin {P.WHITE_D:.2f} mm ({P.WHITE_LAYERS} layers at "
              f"{P.LAYER:.2f}), letter colour behind it "
              f"{P.COLOUR_BEHIND:.2f} mm")

    built = {}
    for key, word, filament in P.TAGS:
        white, colour = tag(face, word, cap)
        built[key] = (white, colour, word, filament)
        if verbose:
            g, _ = face.line(word, cap)
            print(f"  {word:5} ink {g.bounds[2]-g.bounds[0]:5.1f} mm wide, "
                  f"white {white.volume/1000:5.2f} cm3 watertight "
                  f"{white.is_watertight}, "
                  f"colour {colour.volume/1000:5.2f} cm3 watertight "
                  f"{colour.is_watertight}")
    return built, cap, face


def export_stls(built, verbose=True):
    STL.mkdir(exist_ok=True)
    if verbose:
        print("stl/")
    white_cm3 = colour_cm3 = 0.0
    for key, (white, colour, word, filament) in built.items():
        for part, mesh, fil in (('white', white, P.WHITE_FILAMENT),
                                ('colour', colour, filament)):
            path = STL / f"{key}-{part}.stl"
            mesh.export(path)
            if part == 'white':
                white_cm3 += mesh.volume / 1000
            else:
                colour_cm3 += mesh.volume / 1000
            if verbose:
                print(f"  {path.name:20} {mesh.volume/1000:5.2f} cm3   {fil}")
    if verbose:
        # ~1.24 g/cm3 for PLA. The jade white figure is the one Rob asked the
        # question about, so it is reported on its own rather than buried in a
        # total, and the lines below say what the other skin depths would cost.
        g = 1.24
        print(f"  jade white {white_cm3:.2f} cm3, about {white_cm3*g:.1f} g")
        print(f"  letter colours {colour_cm3:.2f} cm3, about "
              f"{colour_cm3*g:.1f} g across three spools")
        for n in (2, 3, 4, 5):
            # the skin is prismatic, so scaling the measured white by the depth
            # ratio is exact rather than an estimate
            cm3 = white_cm3 * (n * P.LAYER) / P.WHITE_D
            mark = "  <- current" if n == P.WHITE_LAYERS else ""
            print(f"    {n} white layers ({n*P.LAYER:.2f} mm): "
                  f"{cm3:5.2f} cm3, {cm3*g:4.1f} g{mark}")


def face_up(mesh):
    """A copy turned over, lettering upwards, for rendering only.

    Half a turn about Y: x -> -x and z -> -z, then slide it back into the
    positive octant. That undoes the mirror in the geometry and puts the
    lettered face towards the key light, so a render shows the tag the way it
    looks in the hand rather than as a dark grey underside with the word
    backwards.

    Rotating about X instead would also point the face upwards and would be
    wrong: it flips y as well, which lands the word upside down. The exported
    STLs are never passed through here -- they go out lettering-down, which is
    how they print.
    """
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (0, 1, 0)))
    m.apply_translation((P.TAG_W, 0.0, P.TAG_T))
    return m


def export_renders(built, cap, face, verbose=True):
    RENDERS.mkdir(exist_ok=True)
    if verbose:
        print("renders/")

    def parts_of(key):
        white, colour, _, filament = built[key]
        return [{"mesh": face_up(white), "color": P.RGB[P.WHITE_FILAMENT]},
                {"mesh": face_up(colour), "color": P.RGB[filament]}]

    for i, (key, word, _) in enumerate(P.TAGS, start=1):
        parts = parts_of(key)
        meshes = [p["mesh"] for p in parts]
        img = R.render(parts, width=1400, height=700,
                       **R.frame(meshes, azimuth_deg=-90, elevation_deg=58,
                                 margin=1.02))
        path = RENDERS / f"0{i}-{key}-face.png"
        img.save(path)
        if verbose:
            print(f"  {path.name}")

    # The three together, lettered faces towards the camera, as they will sit
    # on the shelf -- this is the view that shows whether the set reads as a
    # set at one cap height.
    parts, meshes = [], []
    for i, (key, _, _) in enumerate(P.TAGS):
        dy = -i * (P.TAG_H + 6.0)
        for p in parts_of(key):
            m = R.placed(p["mesh"], (0.0, dy, 0.0))
            parts.append({"mesh": m, "color": p["color"]})
            meshes.append(m)
    img = R.render(parts, width=1300, height=1100,
                   **R.frame(meshes, azimuth_deg=-90, elevation_deg=90,
                             margin=1.04))
    path = RENDERS / '04-the-set.png'
    img.save(path)
    if verbose:
        print(f"  {path.name}")

    # The drawing the whole design turns on: a section across a letter stem,
    # showing 0.80 mm of jade white with 0.40 mm of colour behind it. It has to
    # be a dead-on orthographic close-up. A 1.2 mm stack seen across an 80 mm
    # tag is a sliver, and tilting the camera even 2 degrees lets the far end
    # of the tag show above the cut face, which reads as extra layers that are
    # not there.
    from shapely.geometry import LineString

    white, colour_mesh, word, filament = built['pla']
    y_cut = P.TAG_H / 2                      # straight through the letter stems

    # Window the view on a real stem rather than on the middle of the tag --
    # the middle of "PLA" is the gap between L and A, and a section through a
    # gap shows a plain slab and proves nothing.
    letters_2d = word_polygon(face, word, cap)
    hit = LineString([(0, y_cut), (P.TAG_W, y_cut)]).intersection(letters_2d)
    spans = [g for g in (hit.geoms if hasattr(hit, 'geoms') else [hit])
             if not g.is_empty]
    mids = sorted(((g.bounds[0] + g.bounds[2]) / 2 for g in spans),
                  key=lambda x: abs(x - P.TAG_W / 2))
    x_model = mids[0] if mids else P.TAG_W / 2
    x_view = P.TAG_W - x_model               # face_up() mirrors x

    cut = []
    for mesh, colour in ((face_up(white), P.RGB[P.WHITE_FILAMENT]),
                         (face_up(colour_mesh), P.RGB[filament])):
        keep, faces = R.section(mesh, normal=(0, 1, 0), origin=(0, y_cut, 0))
        if len(keep.faces):
            cut.append({"mesh": keep, "color": colour})
        if faces is not None and len(faces.faces):
            cut.append({"mesh": faces, "color": R.tint(colour)})

    w, h = 1400, 560
    window = 3.4                             # mm of height in frame
    target = (x_view, y_cut, P.TAG_T / 2)
    # Camera on the far side of the cut plane from the kept half, so what it
    # sees is the cut face itself and not the tag's outer edge.
    eye = (x_view, y_cut - 80.0, P.TAG_T / 2)   # dead level: no tilt, no bleed
    img = R.render(cut, width=w, height=h, eye=eye, target=target,
                   ortho_height=window)

    # Anchor the callouts to the real geometry rather than to guessed pixels.
    # face_up() has turned the tag over, so the printed face is the TOP of the
    # section: white skin above, letter colour below.
    pts = [(x_view - 3.6, y_cut, P.TAG_T - P.WHITE_D / 2),   # clear of the stem
           (x_view + 3.6, y_cut, P.COLOUR_BEHIND / 2)]
    px = R.screen_of(pts, eye=eye, target=target, width=w, height=h,
                     ortho_height=window)
    # The two labels go to opposite sides, so neither leader has to cross the
    # letter stem that the drawing exists to show.
    R.annotate(img, [
        {"text": f"jade white {P.WHITE_D:.2f} mm, {P.WHITE_LAYERS} layers",
         "px": tuple(px[0]), "to": (int(w * 0.24), int(h * 0.14)),
         "align": "right"},
        {"text": f"letter colour {P.COLOUR_BEHIND:.2f} mm behind it",
         "px": tuple(px[1]), "to": (int(w * 0.62), int(h * 0.86))},
    ])
    path = RENDERS / '05-inlay-section.png'
    img.save(path)
    if verbose:
        print(f"  {path.name}  (section at the '{word}' stem nearest centre)")


def main():
    do_renders = '--no-renders' not in sys.argv
    built, cap, face = build()
    export_stls(built)
    if do_renders:
        export_renders(built, cap, face)
    return 0


if __name__ == '__main__':
    sys.exit(main())
