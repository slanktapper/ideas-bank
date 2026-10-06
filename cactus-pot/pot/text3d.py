"""Glyph outlines from a TTF, as shapely polygons, so text can be cut into a face.

fontTools gives the outlines; the curves are flattened here rather than by a
rasteriser, so the polygons stay exact at any size.
"""
from __future__ import annotations
import os, pathlib
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

# The typeface ships with the project: Outfit, SIL Open Font License, in font/.
# Point POT_FONT_DIR at another directory to set the name in a different face.
FONT_DIR = os.environ.get('POT_FONT_DIR',
                          str(pathlib.Path(__file__).resolve().parent / 'font'))


def _bez(p0, pts, n):
    """Flatten a bezier of any order through de Casteljau."""
    ctrl = [np.asarray(p0, float)] + [np.asarray(p, float) for p in pts]
    ts = np.linspace(0, 1, n + 1)[1:]
    out = []
    for t in ts:
        q = list(ctrl)
        while len(q) > 1:
            q = [(1-t)*q[i] + t*q[i+1] for i in range(len(q)-1)]
        out.append(q[0])
    return out


class Face:
    def __init__(self, name='Outfit-Bold'):
        self.font = TTFont(f'{FONT_DIR}/{name}.ttf')
        self.gs = self.font.getGlyphSet()
        self.upm = self.font['head'].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font['hmtx']
        try:    self.kern = self.font['kern'].kernTables[0].kernTable
        except Exception: self.kern = {}

    def _glyph(self, ch, steps=10):
        gname = self.cmap[ord(ch)]
        pen = RecordingPen(); self.gs[gname].draw(pen)
        rings, cur, start = [], [], None
        for op, args in pen.value:
            if op == 'moveTo':
                if cur: rings.append(cur)
                start = args[0]; cur = [start]
            elif op == 'lineTo':
                cur.append(args[0])
            elif op == 'curveTo':
                cur += _bez(cur[-1], list(args), steps)
            elif op == 'qCurveTo':
                pts = list(args)
                on = pts[-1]
                offs = pts[:-1]
                if on is None:                       # all-off-curve contour
                    on = tuple((np.asarray(offs[0])+np.asarray(offs[-1]))/2)
                    pts = offs + [on]
                prev = cur[-1]
                for i in range(len(offs)):
                    c = offs[i]
                    nxt = offs[i+1] if i+1 < len(offs) else on
                    if i+1 < len(offs):
                        nxt = tuple((np.asarray(c)+np.asarray(nxt))/2)
                    cur += _bez(prev, [c, nxt], steps); prev = cur[-1]
            elif op == 'closePath':
                if cur: rings.append(cur); cur = []
        if cur: rings.append(cur)
        polys = []
        for ring in rings:
            if len(ring) < 3: continue
            p = Polygon(ring)
            if not p.is_valid: p = p.buffer(0)
            if not p.is_empty: polys.append(p)
        if not polys: return None, self.hmtx[gname][0]
        # even-odd: counters are rings inside rings
        polys.sort(key=lambda p: -p.area)
        shape = polys[0]
        for p in polys[1:]:
            shape = shape.symmetric_difference(p) if shape.contains(p) else shape.union(p)
        return shape, self.hmtx[gname][0]

    def line(self, s, cap_mm, tracking=0.0):
        """One line of text as a shapely geometry. Baseline at y=0, left at x=0.

        `cap_mm` is the cap height in millimetres; everything scales from it.
        """
        capq = self.font['OS/2'].sCapHeight if hasattr(self.font['OS/2'], 'sCapHeight') else self.upm*0.7
        k = cap_mm / capq
        parts, x = [], 0.0
        prev = None
        for ch in s:
            if ch == ' ':
                x += self.hmtx[self.cmap[ord(' ')]][0]*k + tracking; prev = None; continue
            if prev is not None:
                x += self.kern.get((self.cmap[ord(prev)], self.cmap[ord(ch)]), 0)*k
            g, adv = self._glyph(ch)
            if g is not None:
                from shapely import affinity
                parts.append(affinity.translate(affinity.scale(g, k, k, origin=(0,0)), x, 0))
            x += adv*k + tracking
            prev = ch
        geom = unary_union(parts) if parts else Polygon()
        return geom, x


def fit_lines(face, lines, width_mm, height_mm, max_cap, min_gap=1.6):
    """Set `lines` to one common cap height, stacked, to fill a panel.

    Every line gets the *same* size: the largest cap height at which the widest
    of them still fits `width_mm`, capped at `max_cap`. The gap between lines is
    then solved so that the block's **inked** extent is exactly `height_mm`, and
    the block is centred on (0, 0) by that same inked extent -- not by the cap
    boxes, which is the thing to get right here. Ascenders overshoot the cap line
    and descenders fall below the baseline, so a stack centred on its cap boxes
    sits visibly high in its panel.

    Returns [(geometry, cap_mm, width)], and the caller insets `height_mm` from
    the panel to leave a margin top and bottom. Those two margins are then equal
    by construction.
    """
    from shapely import affinity
    from shapely.ops import unary_union

    def stack(cap, gap):
        """Lay the lines out at one size, each centred on x=0, and return the
        geometries together with the inked height of the block."""
        placed, y = [], 0.0
        for s in lines:
            g, w = face.line(s, cap)
            y -= cap
            placed.append((affinity.translate(g, -w/2, y), cap, w))
            y -= gap
        ink = unary_union([g for g, _, _ in placed]).bounds
        return placed, ink[3] - ink[1], ink

    # one size for all of them, set by whichever line is widest
    cap = max_cap
    widest = max(face.line(s, cap)[1] for s in lines)
    if widest > width_mm:
        cap *= width_mm / widest

    # the inked height is linear in the gap, so one measurement solves it
    while True:
        _, h0, _ = stack(cap, 0.0)
        gap = (height_mm - h0) / max(len(lines) - 1, 1)
        if gap >= min_gap or cap < 1.0:
            break
        cap *= 0.97                      # too tall to breathe: take a size off

    placed, _, ink = stack(cap, gap)
    mid = (ink[1] + ink[3]) / 2
    return [(affinity.translate(g, 0, -mid), cap, w) for g, cap, w in placed]
