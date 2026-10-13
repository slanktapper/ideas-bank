"""Set a short word as shapely polygons, so it can be cut into a face.

Written for this project rather than borrowed from `cactus-pot`, which does
the same job against a bundled TTF with fontTools.  This one asks matplotlib
for the outlines, because matplotlib is already a dependency of the renders
and it ships DejaVu Sans with itself -- so there is no font file to keep in
version control and no second way for a build to fail.

The one thing that matters here and is easy to get wrong: the lettering goes
on the face that is printed against the bed, and that face is seen from
below.  `outline(..., mirror=True)` is what makes the word read the right way
round on the finished tag.
"""
from __future__ import annotations
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.affinity import scale as sscale, translate as stranslate
from shapely.ops import unary_union

FONT = FontProperties(family="DejaVu Sans", weight="bold")
REF = 100.0          # outlines are taken at this size, then scaled


def _glyph_set(s: str, size: float) -> list[Polygon]:
    tp = TextPath((0, 0), s, size=size, prop=FONT)
    rings = [Polygon(p) for p in tp.to_polygons() if len(p) >= 3]
    rings = [g for g in rings if g.is_valid and g.area > 1e-6]
    rings.sort(key=lambda g: -g.area)
    out: list[Polygon] = []
    for g in rings:                      # even-odd: a counter is a hole
        host = next((i for i, f in enumerate(out) if f.contains(g)), None)
        if host is None:
            out.append(g)
        else:
            out[host] = out[host].difference(g)
    return out


def outline(s: str, cap_h: float, track: float = 0.0, mirror: bool = False,
            along_y: bool = True):
    """The word as one geometry, centred on the origin.

    Returns (geometry, length, height).  `cap_h` is the height of the set
    characters themselves, not the font's nominal size -- the string is
    measured and scaled, so two labels in the same tag family come out the
    same visual size whatever letters they use.
    """
    if track:
        parts, x = [], 0.0
        for ch in s:
            if ch != " ":
                g = unary_union(_glyph_set(ch, REF))
                parts.append(stranslate(g, x, 0))
            adv = TextPath((0, 0), ch or " ", size=REF, prop=FONT)
            x += (adv.get_extents().width if ch != " " else REF * 0.32) + track * REF / cap_h
        geom = unary_union(parts)
    else:
        geom = unary_union(_glyph_set(s, REF))

    x0, y0, x1, y1 = geom.bounds
    geom = sscale(geom, cap_h / (y1 - y0), cap_h / (y1 - y0), origin=(0, 0, 0))
    x0, y0, x1, y1 = geom.bounds
    geom = stranslate(geom, -(x0 + x1) / 2.0, -(y0 + y1) / 2.0)

    if along_y:          # the word runs up the tag, not across it
        geom = _rot90(geom)
    if mirror:           # ...and is read from the bed side
        geom = sscale(geom, -1.0, 1.0, origin=(0, 0, 0))

    x0, y0, x1, y1 = geom.bounds
    length = (y1 - y0) if along_y else (x1 - x0)
    height = (x1 - x0) if along_y else (y1 - y0)
    return geom, length, height


def _rot90(geom):
    from shapely.affinity import rotate
    return rotate(geom, 90, origin=(0, 0))


def measure(s: str, cap_h: float, track: float = 0.0) -> float:
    """How long the word is once set -- what `params.plan` needs."""
    return outline(s, cap_h, track)[1]
