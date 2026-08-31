"""Turning a traced outline into a pocket profile.

Everything here works in millimetres on shapely geometry. No CAD, no images.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from shapely import affinity
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union

from .config import DEFAULTS, GRID_PITCH_MM, Tuning


def clean(poly: Polygon) -> Polygon:
    """Repair self-intersections that tracing sometimes produces."""
    if not poly.is_valid:
        poly = poly.buffer(0)
    if isinstance(poly, MultiPolygon):
        poly = max(poly.geoms, key=lambda p: p.area)
    return poly


def pocket_profile(
    outline: Polygon,
    tuning: Tuning = DEFAULTS,
    *,
    relief: bool | tuple[float, float] = False,
) -> Polygon:
    """Grow a traced tool outline into the shape of the pocket to cut.

    The traced outline is the tool. The pocket has to be bigger than the tool
    by the clearance, or the tool will not go in.
    """
    poly = clean(outline)
    poly = poly.buffer(tuning.clearance_mm, join_style="round", quad_segs=8)
    poly = clean(poly)
    poly = poly.simplify(tuning.simplify_mm, preserve_topology=True)

    if relief:
        centre = (
            relief
            if isinstance(relief, tuple)
            else finger_relief_point(poly, tuning.relief_radius_mm)
        )
        scallop = Point(centre).buffer(tuning.relief_radius_mm, quad_segs=24)
        poly = clean(unary_union([poly, scallop]))
        poly = poly.simplify(tuning.simplify_mm, preserve_topology=True)

    return poly


def finger_relief_point(poly: Polygon, radius: float) -> tuple[float, float]:
    """Where to put the thumb notch, so that it actually is one.

    The scallop has to make the pocket *wider than the tool* somewhere, or a
    finger still cannot get under it. Centring it on the fattest interior
    point does the opposite: on anything chunkier than the scallop it lands
    entirely inside the outline and changes nothing at all.

    So the centre goes on the outline's edge, halfway along the tool's long
    axis -- normally the slimmest part of a hand tool, and the natural place
    to pinch it. Half the circle bites out past the tool, which is the bit
    that does the work.
    """
    rect = poly.minimum_rotated_rectangle
    centroid = poly.centroid
    if not isinstance(rect, Polygon):
        return (centroid.x, centroid.y)

    coords = list(rect.exterior.coords)[:4]
    edges = [
        (math.dist(coords[i], coords[(i + 1) % 4]),
         np.array(coords[(i + 1) % 4]) - np.array(coords[i]))
        for i in range(4)
    ]
    _, long_axis = max(edges, key=lambda e: e[0])
    perp = np.array([-long_axis[1], long_axis[0]], dtype=float)
    norm = np.linalg.norm(perp)
    if norm < 1e-9:
        return (centroid.x, centroid.y)
    perp /= norm

    # March out from the centre until we leave the shape; that crossing is
    # the edge we want to sit astride.
    origin = np.array([centroid.x, centroid.y])
    if not poly.contains(Point(origin)):
        origin = np.array(list(poly.representative_point().coords)[0])

    minx, miny, maxx, maxy = poly.bounds
    limit = math.hypot(maxx - minx, maxy - miny)
    step = 0.25
    d = 0.0
    while d < limit:
        d += step
        if not poly.contains(Point(origin + perp * d)):
            break
    return tuple(origin + perp * max(0.0, d - step / 2.0))


def straighten(poly: Polygon) -> tuple[Polygon, float]:
    """Rotate so the shape's natural axes line up with the grid.

    A scan is never perfectly square to the platen, and an outline that sits
    at 3 degrees needs a bin a whole unit larger for no reason. Returns the
    rotated polygon and the angle applied, in degrees.
    """
    rect = poly.minimum_rotated_rectangle
    if not isinstance(rect, Polygon):
        return poly, 0.0
    coords = list(rect.exterior.coords)[:4]
    # Longest edge of the min-area rectangle defines the shape's own axis.
    edges = [
        (
            math.dist(coords[i], coords[(i + 1) % 4]),
            math.degrees(
                math.atan2(
                    coords[(i + 1) % 4][1] - coords[i][1],
                    coords[(i + 1) % 4][0] - coords[i][0],
                )
            ),
        )
        for i in range(4)
    ]
    _, angle = max(edges, key=lambda e: e[0])
    angle = -angle
    # Never rotate more than a quarter turn; 91 degrees is 1 degree the other way.
    angle = ((angle + 45.0) % 90.0) - 45.0
    if abs(angle) < 1e-9:
        return poly, 0.0
    return clean(affinity.rotate(poly, angle, origin="centroid")), angle


def centre_on(poly: Polygon, x: float = 0.0, y: float = 0.0) -> Polygon:
    """Move a polygon so its bounding box centre lands on (x, y)."""
    minx, miny, maxx, maxy = poly.bounds
    return affinity.translate(
        poly, x - (minx + maxx) / 2.0, y - (miny + maxy) / 2.0
    )


def grid_units_for(
    poly: Polygon, tuning: Tuning = DEFAULTS
) -> tuple[int, int]:
    """Smallest (length, width) in grid units that fits this pocket.

    Interior room across ``n`` units is ``n * 42 - 0.5`` of bin footprint,
    less the wall material on both sides.
    """
    minx, miny, maxx, maxy = poly.bounds
    needed = []
    for span in (maxx - minx, maxy - miny):
        n = (span + 2 * tuning.wall_mm + 0.5) / GRID_PITCH_MM
        needed.append(max(1, math.ceil(round(n, 6))))
    return needed[0], needed[1]


def height_units_for(depth_mm: float) -> int:
    """Smallest height in units whose usable depth reaches ``depth_mm``.

    Usable depth is ``(U - 1) * 7`` -- the first unit is the base profile.
    """
    return max(2, math.ceil(round(depth_mm / 7.0 + 1.0, 6)))


def polygons_from_contours(
    contours: Iterable[Sequence[Sequence[float]]], min_area_mm2: float
) -> list[Polygon]:
    """Build valid polygons from traced point rings, largest first."""
    out: list[Polygon] = []
    for c in contours:
        pts = np.asarray(c, dtype=float).reshape(-1, 2)
        if len(pts) < 3:
            continue
        poly = clean(Polygon(pts))
        if poly.is_empty or poly.area < min_area_mm2:
            continue
        out.append(poly)
    return sorted(out, key=lambda p: p.area, reverse=True)
