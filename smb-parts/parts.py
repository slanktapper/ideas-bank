"""Geometry for the shelf rail, in two parts that clip together.

THE BRACKET stays on the shelf. It caps the retainer bar and presents a
front plate for the art to grab.

THE ART PANEL clips on: hook over the bracket's top plate edge, swing the
bottom in, and a bead on the bottom lip snaps past the plate's bottom edge.

Section, looking along the rail. Y is depth into the shelf, Z is up.

   Y=0  2.4   4.8  7.2      11.4   13.9
    |    |     |    |         |      |
    +----+                                  <- art's top return, over the
    |    |#####|    +----------------+         plate's top edge
    |    | lip |    |     web        |      <- top lip hangs behind it
    |    +-----+----+------+  +------+
    |ART |          |      |  | leg  |      <- the bar stands in the slot
    |    |  bracket |      |  |      |
    |    |   body   | slot |  |      |
    |    +-----+----+------+  +------+
    |    | lip |    |
    +----+#####+    the body passes through the gap between the two lips --
    |    |          with a continuous hook there is no way round it in X
    +----+

  ^ art, RELIEF proud, in -Y

The art is built as 2D polygons and extruded, not as one box per pixel: a
panel is 208 x 32 game pixels, and 6656 boolean unions is not worth waiting
for. Runs of one colour along a row collapse to rectangles first, shapely
unions them, then the result is extruded once per colour.
"""

from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Polygon as SPolygon
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import params as P

# polygon XY -> world XZ, extrusion -> -Y (art stands out of the face)
_TO_FACE = trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0])
_BITE = 0.05               # how far the art reaches back into the plate, so
                           # the union has real overlap and not a shared face

# a polygon drawn in (Y, Z) swept along X -- how every chamfer and bead here
# is made, since they are all constant section along the rail
_TO_SECTION = np.array([[0.0, 0.0, 1.0, 0.0],
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0, 1.0]])


def _box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def _sweep(points_yz, x0, x1):
    """A (Y, Z) polygon swept from x0 to x1 along the rail."""
    m = trimesh.creation.extrude_polygon(SPolygon(points_yz), x1 - x0)
    m.apply_transform(_TO_SECTION)
    m.apply_translation((x0, 0.0, 0.0))
    return m


def bracket(width=None, slot=None, grab=None) -> trimesh.Trimesh:
    """One shelf holder: caps the bar, and holds the art slab.

    All the clip geometry is here. The slab is a plain rectangle, so every
    feature that retains it -- the bottom ledge, the top lip, the snap bead
    -- belongs to this part, which is the one that stays on the shelf.
    """
    w = P.BRACKET_W if width is None else width
    slot = P.SLOT if slot is None else slot
    grab = P.CLIP_GRAB if grab is None else grab
    depth = P.SLOT_Y0 + slot + P.LEG_T
    bar_top = P.FACE_H - P.WEB_T
    y_back = P.ART_T + P.ART_FIT                 # back of the slab pocket
    z_top = P.FACE_H + P.ART_FIT                 # top of the slab pocket

    back = _box(0, w, y_back, P.SLOT_Y0, P.HOLDER_Z0, P.HOLDER_Z1)
    bot_ret = _box(0, w, P.LIP_Y0, P.SLOT_Y0, P.HOLDER_Z0, 0.0)
    top_ret = _box(0, w, P.LIP_Y0, P.SLOT_Y0, z_top, P.HOLDER_Z1)
    bot_lip = _box(0, w, P.LIP_Y0, P.LIP_Y1, 0.0, P.LIP_OVER)
    top_lip = _box(0, w, P.LIP_Y0, P.LIP_Y1, z_top - P.LIP_OVER, z_top)

    # the snap: a bead on the top lip standing `grab` over the slab's face,
    # ramped underneath so the slab pushes it open rather than jamming
    y_bead = 0.0 + grab
    z1 = z_top - P.LIP_OVER + P.GRAB_H
    bead = _sweep([(P.LIP_Y1, z_top - P.LIP_OVER + P.GRAB_H + (y_bead - P.LIP_Y1)),
                   (y_bead, z1), (y_bead, z1 - P.GRAB_H),
                   (P.LIP_Y1, z1 - P.GRAB_H)], 0.0, w)

    web = _box(0, w, P.SLOT_Y0, depth, bar_top, P.FACE_H)
    leg = _box(0, w, depth - P.LEG_T, depth, bar_top - P.GRIP, bar_top)
    solid = trimesh.boolean.union([back, bot_ret, top_ret, bot_lip, top_lip,
                                   bead, web, leg])

    # lead-in where the bar enters, so a 0.2 mm fit does not start square
    mouth = bar_top - P.GRIP
    c = P.CHAMFER
    cuts = [_sweep([(P.SLOT_Y0, mouth), (P.SLOT_Y0, mouth + c),
                    (P.SLOT_Y0 - c, mouth)], -1.0, w + 1.0),
            _sweep([(depth - P.LEG_T, mouth), (depth - P.LEG_T, mouth + c),
                    (depth - P.LEG_T + c, mouth)], -1.0, w + 1.0)]
    return trimesh.boolean.difference([solid] + cuts)


def art_body(length) -> trimesh.Trimesh:
    """The art slab. A rectangle, and nothing else."""
    return _box(0, length, 0, P.ART_T, 0, P.FACE_H)


def _colour_polygon(grid, colour, rows, cols):
    """Union of every pixel of one colour, as a shapely geometry in face XZ."""
    rects = []
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] != colour:
                c += 1
                continue
            run = c
            while run < cols and grid[r][run] == colour:
                run += 1
            rects.append(sbox(c * P.PIXEL, P.FACE_H - (r + 1) * P.PIXEL,
                              run * P.PIXEL, P.FACE_H - r * P.PIXEL))
            c = run
    poly = unary_union(rects)
    # the top and bottom margins stay flat: that is where the holder's lips
    # bear, and relief under them would leave the slab rattling
    keep = sbox(-1.0, P.ART_MARGIN, cols * P.PIXEL + 1.0, P.FACE_H - P.ART_MARGIN)
    return poly.intersection(keep)


def _extrude(g, height):
    """Extrude one shapely polygon, cutting any holes as booleans.

    trimesh triangulates a ring-with-holes through earcut, and on the hill in
    the 1-1 opening -- one outline with four dark spots inside it -- that comes
    back not watertight, so the union downstream refuses it. Extruding the
    outline and subtracting the spots is slower and always a volume.
    """
    outer = trimesh.creation.extrude_polygon(SPolygon(g.exterior), height)
    if not g.interiors:
        return outer
    holes = []
    for ring in g.interiors:
        h = trimesh.creation.extrude_polygon(SPolygon(ring), height + 2.0)
        h.apply_translation((0.0, 0.0, -1.0))
        holes.append(h)
    return trimesh.boolean.difference([outer] + holes)


def art_bodies(vig, idx) -> dict:
    """{colour: mesh} for one printed panel of a vignette."""
    cols, rows, grid = vig.panel_pixels(idx)
    out = {}
    for colour in vig.colours():
        poly = _colour_polygon(grid, colour, rows, cols)
        if poly.is_empty:
            continue
        parts = []
        for g in getattr(poly, "geoms", [poly]):
            if g.is_empty or g.area <= 0:
                continue
            m = _extrude(g, P.RELIEF + _BITE)
            m.apply_transform(_TO_FACE)
            m.apply_translation((0.0, _BITE, 0.0))
            parts.append(m)
        if parts:
            out[colour] = trimesh.util.concatenate(parts)
    return out


def panel(vig, idx: int):
    """(whole, body, {colour: mesh}) for art panel `idx` of a vignette."""
    body = art_body(P.PANEL_L)
    art = art_bodies(vig, idx)
    whole = trimesh.boolean.union([body] + list(art.values()))
    return whole, body, art


def bracket_positions():
    """Where the brackets sit along one shelf, left to right.

    Flush at each end, and the middle one centred on the shelf -- which is
    exactly the joint between the two art panels, so it lines them up and
    there is no need for a half-lap.
    """
    n = P.BRACKETS_PER_SHELF
    if n == 1:
        return [(P.SHELF_L - P.BRACKET_W) / 2.0]
    span = P.SHELF_L - P.BRACKET_W
    return [i * span / (n - 1) for i in range(n)]
