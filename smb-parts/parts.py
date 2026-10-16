"""Geometry for the shelf rail: the U-channel, and the pixels on its face.

The section, looking along the rail. Y is depth, into the shelf; Z is up.

        Y=0   FACE_T                 FACE_T+LEG_D
         |      |                         |
    Z=FACE_H  +-+-------------------------+   <- top leg, lies on the shelf
              | |                         |
              | |      the board          |   <- GAP = SHELF_T + FIT
              | |                         |
    Z=0       +-+-------------------------+   <- bottom leg, under the shelf
              ^
              the front plate, FACE_T thick, with the art standing RELIEF
              proud of it in -Y. The art is the whole 25 mm of the face.

The art is built as 2D polygons and extruded, not as one box per pixel: a
panel is 288 x 32 game pixels, and 9216 boolean unions is not a thing worth
waiting for. Runs of one colour along a row collapse to rectangles first,
then shapely unions them, then the result is extruded once per colour.
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


def _box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def channel(first: bool, last: bool) -> trimesh.Trimesh:
    """One panel's U-channel, with the half-lap at the ends that need it."""
    face = _box(0, P.PANEL_L, 0, P.FACE_T, 0, P.FACE_H)
    y0, y1 = P.FACE_T, P.FACE_T + P.LEG_D
    bottom = _box(0, P.PANEL_L, y0, y1, 0, P.LEG_T)
    top = _box(0, P.PANEL_L, y0, y1, P.LEG_T + P.GAP, P.FACE_H)

    solid = trimesh.boolean.union([face, bottom, top])

    half = P.LEG_T / 2.0
    if not last:
        # tongue: the lower half of the bottom leg, running past the end
        tongue = _box(P.PANEL_L, P.PANEL_L + P.LAP_L, y0, y1, 0, half)
        solid = trimesh.boolean.union([solid, tongue])
    if not first:
        # socket: the same slot taken out of this end, with clearance
        socket = _box(-1.0, P.LAP_L + P.LAP_FIT, y0 - 1.0, y1 + 1.0,
                      -1.0, half + P.LAP_FIT)
        solid = trimesh.boolean.difference([solid, socket])
    return solid


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
            x0 = c * P.PIXEL
            x1 = run * P.PIXEL
            # row 0 is the top of the crop
            z1 = P.FACE_H - r * P.PIXEL
            z0 = P.FACE_H - (r + 1) * P.PIXEL
            rects.append(sbox(x0, z0, x1, z1))
            c = run
    return unary_union(rects)


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
        h.apply_translation((0.0, 0.0, -1.0))      # through, both ends
        holes.append(h)
    return trimesh.boolean.difference([outer] + holes)


def art_bodies(vig) -> dict:
    """{colour: mesh} -- one body per colour, each standing RELIEF proud."""
    cols, rows, grid = vig.pixels()
    out = {}
    for colour in vig.colours():
        poly = _colour_polygon(grid, colour, rows, cols)
        geoms = getattr(poly, "geoms", [poly])
        parts = []
        for g in geoms:
            if g.is_empty or g.area <= 0:
                continue
            m = _extrude(g, P.RELIEF + _BITE)
            m.apply_transform(_TO_FACE)
            m.apply_translation((0.0, _BITE, 0.0))
            parts.append(m)
        if parts:
            out[colour] = trimesh.util.concatenate(parts)
    return out


def panel(vig, first: bool, last: bool):
    """(whole, body, {colour: mesh}) for one panel."""
    body = channel(first, last)
    art = art_bodies(vig)
    whole = trimesh.boolean.union([body] + list(art.values()))
    return whole, body, art
