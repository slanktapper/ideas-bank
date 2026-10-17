"""Geometry for the shelf rail: the cap that grips the retainer bar, and the
pixels on its face.

The section, looking along the rail. Y is depth, back into the shelf; Z is up.
The shelf's retainer bar stands up into the slot.

      Y=0  FACE_T        FACE_T+SLOT   DEPTH
       |     |                |          |
  Z=FACE_H  +--+--------------------------+   <- web, bridges the bar's top
            |  |              |           |
            |  |   the bar    |###########|   <- inner leg, GRIP deep,
            |  |   4 mm       |###########|      down the back of the bar
            |  |              +-----------+
            |  |
            |  |                              the face keeps going down past
            |  |                              the bar, over the shelf's front
  Z=0       +--+                              edge. The art is all of it.

      ^ art, RELIEF proud, in -Y

Printed UPSIDE DOWN -- web flat on the bed, both walls growing up. Nothing
overhangs, nothing bridges except the 8 mm half-lap notch. The art ends up
on a vertical wall, which is why its pixel rows land on layer boundaries.

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


def _box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def cap(first: bool, last: bool) -> trimesh.Trimesh:
    """One panel's bar-cap, with the half-lap at the ends that need it."""
    web_z0 = P.FACE_H - P.WEB_T
    leg_y0 = P.FACE_T + P.SLOT

    face = _box(0, P.PANEL_L, 0, P.FACE_T, 0, P.FACE_H)
    web = _box(0, P.PANEL_L, P.FACE_T, P.DEPTH, web_z0, P.FACE_H)
    leg = _box(0, P.PANEL_L, leg_y0, P.DEPTH, web_z0 - P.GRIP, web_z0)
    solid = trimesh.boolean.union([face, web, leg])

    # The lap lives in the half of the web that lies ON THE BED when printed
    # upside down -- the top half here. A tongue anywhere else would print
    # into thin air, because past the panel end there is nothing under it.
    lap_z = P.FACE_H - P.WEB_T / 2.0
    if not last:
        solid = trimesh.boolean.union([
            solid,
            _box(P.PANEL_L, P.PANEL_L + P.LAP_L, P.FACE_T, P.DEPTH,
                 lap_z, P.FACE_H)])
    if not first:
        # Y starts at FACE_T so the notch never reaches the art face
        solid = trimesh.boolean.difference([
            solid,
            _box(-1.0, P.LAP_L + P.LAP_FIT, P.FACE_T, P.DEPTH + 1.0,
                 lap_z - P.LAP_FIT, P.FACE_H + 1.0)])
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
            rects.append(sbox(c * P.PIXEL, P.FACE_H - (r + 1) * P.PIXEL,
                              run * P.PIXEL, P.FACE_H - r * P.PIXEL))
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
    """(whole, body, {colour: mesh}) for panel `idx` of a vignette."""
    first = idx == 0
    last = idx == P.PANELS_PER_SHELF - 1
    body = cap(first, last)
    art = art_bodies(vig, idx)
    whole = trimesh.boolean.union([body] + list(art.values()))
    return whole, body, art
