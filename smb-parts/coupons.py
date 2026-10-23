"""Test pieces: short slices of the rail, to try on the real shelf.

Two open questions need a part in hand rather than arithmetic, and both are
cheap to answer with a few grams of filament.

0. DOES THE CLIP CLIP? (clip_ladder) -- the new unknown since the design
   split into a bracket and an art panel. Three art stubs at bead
   interferences of 0.15, 0.25 and 0.35 mm, with one bracket to try them
   on. "Easy and safe to add and remove" is a feel, not a number.

1. DOES THE SLOT GRIP? The design slot is 4.4 mm over a 4 mm bar. FDM slots
   print undersize, sheet metal has its own tolerance, and neither is known
   here. One coupon tests one guess, so this builds a LADDER: five 5 mm
   slices at 4.2 to 4.6 mm, joined by a frangible spine, each with its slot
   width embossed on the face so they cannot be mixed up. SETTLED on
   2026-10-23: 4.2 gripped, and FIT is 0.2.

2. IS THE BAR 16 MM OR 20 MM PROUD? `params.py` reads the drawing's 0.79 in
   as underside-to-bar-top, which puts the bar 16.07 mm above the floor. Any
   coupon answers it: push one on and look at whether the face reaches past
   the shelf's underside. If it stops short, the other reading was right.

The numbers are drawn with a 3 x 5 pixel font and the same extrusion path as
the Mario art, because a pixel font is the one kind this project already
knows how to make, and it costs no new dependency.
"""

from __future__ import annotations

import trimesh
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import params as P
import parts as T

# 3 x 5, row 0 at the top. Only 2-6 are used today; the rest are here so a
# different COUPON_SLOTS list does not need new glyphs.
FONT = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "001", "001", "001"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}

DIGIT_W, DIGIT_H = 3, 5


def _digit_rects(ch, x0, z_top):
    """Pixel rectangles for one glyph, in face XZ, growing downward."""
    out = []
    for r, row in enumerate(FONT[ch]):
        for c, bit in enumerate(row):
            if bit != "1":
                continue
            out.append(sbox(x0 + c * P.DIGIT_PX, z_top - (r + 1) * P.DIGIT_PX,
                            x0 + (c + 1) * P.DIGIT_PX, z_top - r * P.DIGIT_PX))
    return out


def _number_on_face(text, width):
    """The glyphs of `text` stacked vertically, centred on a coupon face."""
    gh = DIGIT_H * P.DIGIT_PX
    gap = P.DIGIT_PX
    total = len(text) * gh + (len(text) - 1) * gap
    x0 = (width - DIGIT_W * P.DIGIT_PX) / 2.0
    z = (P.FACE_H + total) / 2.0
    rects = []
    for ch in text:
        rects += _digit_rects(ch, x0, z)
        z -= gh + gap
    poly = unary_union(rects)
    parts = []
    for g in getattr(poly, "geoms", [poly]):
        m = T._extrude(g, P.RELIEF + T._BITE)
        m.apply_transform(T._TO_FACE)
        m.apply_translation((0.0, T._BITE, 0.0))
        parts.append(m)
    return parts


def clip_ladder(split=False):
    """Holders at three snap strengths, plus one art stub to try them on.

    The bead moved onto the holder when the art became a plain slab, so the
    ladder is now holders rather than art. The bar slot is settled at 4.2;
    the open number is how hard the bead should have to flex past, and
    "easy and safe to add and remove" is a feel, not a calculation.
    """
    pieces, plains, numbers = [], [], []
    x = 0.0
    for grab in P.CLIP_GRABS:
        body = T.bracket(width=P.BRACKET_W, grab=grab)
        label = "%d" % round(grab * 100)       # 0.25 -> "25"
        marks = _number_on_face(label, P.BRACKET_W)
        one = trimesh.boolean.union([body] + marks)
        one.apply_translation((x, 0.0, 0.0))
        pieces.append(one)
        if split:
            b = body.copy(); b.apply_translation((x, 0.0, 0.0)); plains.append(b)
            n = trimesh.util.concatenate(marks)
            n.apply_translation((x, 0.0, 0.0)); numbers.append(n)
        x += P.BRACKET_W + P.COUPON_GAP
    holders = trimesh.boolean.union(pieces)
    stub = T.art_body(P.BRACKET_W * 2)
    if split:
        return holders, trimesh.boolean.union(plains), \
            trimesh.util.concatenate(numbers), stub, x - P.COUPON_GAP
    return holders, stub, x - P.COUPON_GAP


def fit_ladder(split=False):
    """Every slot width on one snap-apart comb, tightest first.

    With `split`, hands back (comb, plain, numbers) where `plain` is the
    same comb without the digits on it. A render needs the two apart: drawn
    on top of the finished comb the digits are coincident with its surface
    and z-fight into invisibility.
    """
    pieces = []
    plains = []
    numbers = []
    x = 0.0
    for slot in P.COUPON_SLOTS:
        body = T.bracket(width=P.COUPON_W, slot=slot)
        label = "%d" % round(slot * 10)        # 4.4 -> "44", stacked 4 over 4
        marks = _number_on_face(label, P.COUPON_W)
        one = trimesh.boolean.union([body] + marks)
        one.apply_translation((x, 0.0, 0.0))
        pieces.append(one)
        if split:
            b = body.copy()
            b.apply_translation((x, 0.0, 0.0))
            plains.append(b)
            n = trimesh.util.concatenate(marks)
            n.apply_translation((x, 0.0, 0.0))
            numbers.append(n)
        x += P.COUPON_W + P.COUPON_GAP
    total = x - P.COUPON_GAP
    # The spine lies on the bed when the comb is printed upside down, so it
    # is trivial to cut. Keep it inside the thinnest coupon's depth.
    thin = P.SLOT_Y0 + min(P.COUPON_SLOTS) + P.LEG_T
    spine = T._box(0.0, total, P.SLOT_Y0 - P.SPINE_T, thin,
                   P.FACE_H - P.SPINE_T, P.FACE_H)
    comb = trimesh.boolean.union(pieces + [spine])
    if split:
        plain = trimesh.boolean.union(plains + [spine])
        return comb, plain, trimesh.util.concatenate(numbers), total
    return comb, total


def _busiest_window(vig, tiles):
    """The `tiles`-wide window of a vignette with the most colours in it."""
    _, _, grid = vig.pixels()
    width = len(grid[0])
    best, best_score = 0, -1
    for t0 in range(0, width // 16 - tiles + 1):
        c0, c1 = t0 * 16, (t0 + tiles) * 16
        seen = {grid[r][c] for r in range(len(grid)) for c in range(c0, c1)}
        score = len(seen)
        if score > best_score:
            best, best_score = t0, score
    return best


def art_sample(vig, tiles=2):
    """A couple of tiles of real art at the design slot, to judge the relief."""
    t0 = _busiest_window(vig, tiles)
    _, _, grid = vig.pixels()
    c0, c1 = t0 * 16, (t0 + tiles) * 16
    sub = [row[c0:c1] for row in grid]
    rows, cols = len(sub), c1 - c0
    width = tiles * P.TILE

    body = T.art_body(width)
    art = []
    for colour in vig.colours():
        poly = T._colour_polygon(sub, colour, rows, cols)
        if poly.is_empty:
            continue
        for g in getattr(poly, "geoms", [poly]):
            if g.is_empty or g.area <= 0:
                continue
            m = T._extrude(g, P.RELIEF + T._BITE)
            m.apply_transform(T._TO_FACE)
            m.apply_translation((0.0, T._BITE, 0.0))
            art.append(m)
    return trimesh.boolean.union([body] + art), t0
