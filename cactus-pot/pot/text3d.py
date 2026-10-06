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


def fit_lines(face, lines, width_mm, gap_mm, max_cap):
    """Set each line as large as it can be inside `width_mm`, capped at `max_cap`.

    Returns [(geometry, cap_mm, width)] with each line centred on x=0, stacked
    downward from y=0 with `gap_mm` between baselines' cap boxes.
    """
    from shapely import affinity
    out = []
    for s in lines:
        cap = max_cap
        g, w = face.line(s, cap)
        if w > width_mm:
            cap *= width_mm / w
            g, w = face.line(s, cap)
        out.append([g, cap, w])
    y = 0.0
    placed = []
    for g, cap, w in out:
        y -= cap
        placed.append((affinity.translate(g, -w/2, y), cap, w))
        y -= gap_mm
    h = -y + gap_mm
    # recentre the block on y=0
    return [(affinity.translate(g, 0, h/2), cap, w) for g, cap, w in placed]
