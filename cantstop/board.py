"""The cantstop board, playing pieces and fit-test coupon.

Everything here is derived from params.py. Nothing is drawn by hand.

Layout
------
Columns are centre-aligned on a shared midline, so a column of n cells runs
from k = -(n-1)/2 to +(n-1)/2. Every row count is odd, which makes k a whole
number and puts neighbouring columns on the same row grid. The result is a
symmetric lens rather than the stepped pyramid of the first version.

The lens does not reach the corners of its own bounding box, and that is what
makes the octagonal frame work: the four cut-off triangles are exactly where
the number shields and the bracing spokes go, so the frame encloses the board
without wrapping a lot of empty air.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import trimesh

import params as P
import solids as S


# ---------------------------------------------------------------------------
# cell addressing
# ---------------------------------------------------------------------------

def k_max(col_index: int) -> float:
    """Half-height of a column, in rows."""
    return (P.ROWS[col_index] - 1) / 2.0


def steps_out(col_index: int) -> int:
    """How many columns this one is from the middle of the board."""
    tallest = max(k_max(i) for i in range(len(P.ROWS)))
    return int(round(tallest - k_max(col_index)))


def half_height(col_index: int) -> float:
    """How far a column reaches above the midline, in mm.

    The longest column keeps the nominal row pitch. Every other column gives
    up the height COLUMN_SHORTFALL allows it and spreads its own cells over
    whatever span is left -- so the cell COUNT stays as the game needs it
    while the column can still be made to reach further towards the frame.
    """
    tallest = max(k_max(i) for i in range(len(P.ROWS)))
    return tallest * P.PITCH_Y - P.COLUMN_SHORTFALL[steps_out(col_index)]


def column_drop(col_index: int) -> float:
    """Extra span this column is given at the bottom only."""
    return P.COLUMN_DROP[steps_out(col_index)]


def top_y(col_index: int) -> float:
    """The grid position of a column's top row, before the summit steps out."""
    return half_height(col_index)


def bottom_y(col_index: int) -> float:
    return -half_height(col_index) - column_drop(col_index)


def row_pitch(col_index: int) -> float:
    """That column's own spacing between cells."""
    n = P.ROWS[col_index] - 1
    return (top_y(col_index) - bottom_y(col_index)) / n if n else 0.0


def grid_y(col_index: int, row: int) -> float:
    """Row position on the plain grid, before the summit steps out."""
    return bottom_y(col_index) + row * row_pitch(col_index)


def cell_xy(col_index: int, row: int) -> tuple[float, float]:
    """Centre of the cell at (column index 0..10, row 0..n-1, 0 at the bottom).

    Rows are numbered from the bottom for the game's sake; the geometry is
    centred, so row 0 of a short column is not level with row 0 of a long one.

    """
    y = grid_y(col_index, row)
    if row == P.ROWS[col_index] - 1:
        y += P.SUMMIT_STEP          # the top cell steps out, opening the gap
    return col_index * P.PITCH_X, y


def summit(col_index: int) -> tuple[float, float]:
    """The top cell of a column: its numbered, playable summit."""
    return cell_xy(col_index, P.ROWS[col_index] - 1)


def base(col_index: int) -> tuple[float, float]:
    return cell_xy(col_index, 0)


def shield_xy(col_index: int) -> tuple[float, float]:
    """Centre of a column's number box, which is its summit cell."""
    return summit(col_index)


# box, digit and post all share one centre
numeral_xy = shield_xy


def is_summit(col_index: int, row: int) -> bool:
    return row == P.ROWS[col_index] - 1


def all_cells() -> list[tuple[int, int]]:
    return [(i, r) for i, n in enumerate(P.ROWS) for r in range(n)]


def cell_exists(i: int, r: int) -> bool:
    return 0 <= i < len(P.ROWS) and 0 <= r < P.ROWS[i]


# ---------------------------------------------------------------------------
# the octagonal frame
# ---------------------------------------------------------------------------

def content_points() -> np.ndarray:
    """Outline points of everything the frame has to enclose.

    Real points, not a bounding box: the frame is an octagon, so what binds it
    is how far the content reaches along the DIAGONALS as well as the axes.
    With the columns stepping by one cell the lens now reaches well into its
    own corners, which a bounding box cannot see.
    """
    r = P.PAD_OD * 0.5
    ring = [(r * np.cos(a), r * np.sin(a))
            for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)]
    # One footprint for every number, wide enough for a two-digit one. Sizing
    # each column to its own number would push the frame out on the right and
    # leave the lens sitting off-centre in it.
    bw = max(P.PLAQUE_W, P.NUMERAL_BOX_W)
    corners = [(dx * bw / 2, dy * P.PLAQUE_H / 2)
               for dx in (-1, 1) for dy in (-1, 1)]
    pts = []
    for i, row in all_cells():
        x, y = cell_xy(i, row)
        for ox, oy in (corners if is_summit(i, row) else ring):
            pts.append((x + ox, y + oy))
    # the title hangs below the lens, so the frame has to come down to meet it
    for x0, y0, x1, y1 in title_extents():
        pts += [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]
    return np.asarray(pts, dtype=float)


def content_bounds() -> tuple[np.ndarray, np.ndarray]:
    """Bounding box of everything the frame has to enclose."""
    pts = content_points()
    return pts.min(axis=0), pts.max(axis=0)


def octagon() -> list[tuple[float, float]]:
    """The eight frame vertices: a rectangle with its corners cut at 45 deg."""
    pts = content_points()
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    cx, cy = (lo + hi) * 0.5
    d = np.abs(pts - np.array([cx, cy]))

    # the raised lip sits inside the outline, so the outline has to stand off
    # far enough that the lip never lands on a cell
    margin = max(P.OCTAGON_MARGIN, P.RIM_W + P.RIM_CLEAR)

    if P.OCTAGON_REGULAR:
        # Equal edges need a chamfer of exactly 2/(2+sqrt2) of the half-span,
        # which reduces the octagon to three constraints: |dx| <= a,
        # |dy| <= a, and |dx| + |dy| <= a*sqrt2. Size a from the content
        # against all three rather than from its bounding box, or the corner
        # cuts slice through the ends of the lens.
        need = max(d[:, 0].max(), d[:, 1].max(),
                   (d[:, 0] + d[:, 1]).max() / np.sqrt(2.0))
        # OCTAGON_ACROSS pins the size; otherwise it follows the content.
        # Either way the margin has to come out at least RIM_W + RIM_CLEAR,
        # and test_fit.py measures what it actually came out as rather than
        # trusting the number that was typed in.
        if P.OCTAGON_ACROSS:
            # the number means the BOARD's size, and the outline IS the board
            a = b = P.OCTAGON_ACROSS / 2.0
        else:
            a = b = need + margin
        c = a * 2.0 / (2.0 + np.sqrt(2.0))
    else:
        # Each axis sized to its own content, so the frame hugs a lens that
        # is taller than it is wide instead of wrapping it in a square. The
        # chamfer then has to be checked against the content as well: the cut
        # runs along x + y = a + b - c, and every content point has to stay
        # `margin` clear of it measured PERPENDICULAR to the cut, which is
        # where the sqrt2 comes from. Without that the corners slice through
        # whatever is nearest them -- here, the ends of the title.
        a = (hi[0] - lo[0]) * 0.5 + margin
        b = (hi[1] - lo[1]) * 0.5 + margin
        room = a + b - (d[:, 0] + d[:, 1]).max() - margin * np.sqrt(2.0)
        c = min(0.55 * min(a, b), max(room, 0.0))
    return [
        (cx + a - c, cy + b), (cx + a, cy + b - c),
        (cx + a, cy - b + c), (cx + a - c, cy - b),
        (cx - a + c, cy - b), (cx - a, cy - b + c),
        (cx - a, cy + b - c), (cx - a + c, cy + b),
    ]


def octagon_centre() -> np.ndarray:
    lo, hi = content_bounds()
    return (lo + hi) * 0.5


# ---------------------------------------------------------------------------
# board
# ---------------------------------------------------------------------------

def seat_z() -> float:
    """Height of every seating face -- what a piece's skirt lands on."""
    return P.SLAB_T


def rim_rings() -> tuple[list, list]:
    """(outer, inner) plan polygons of the raised lip.

    The inner ring is the outline offset inward by RIM_W -- a true offset,
    with the corners mitred, so the lip is the same width against every edge.

    It used to be a plain scale about the centre, which is the same thing on a
    REGULAR octagon because every edge shares one apothem. It is not the same
    thing on any other shape: once the frame was allowed to hug a lens taller
    than it is wide, scaling gave a lip that ran 7.66 mm on the long edges and
    8.60 on the short ones, and pulled the inner edge to within 3.4 mm of a
    number where 4 was asked for. test_fit.py caught both.
    """
    from shapely.geometry import Polygon

    outer = [tuple(p) for p in octagon()]
    inner = Polygon(outer).buffer(-P.RIM_W, join_style=2, mitre_limit=20.0)
    return outer, [tuple(q) for q in inner.exterior.coords[:-1]]


def _rim(z0: float, h: float) -> trimesh.Trimesh:
    from shapely.geometry import Polygon

    outer, inner = rim_rings()
    m = trimesh.creation.extrude_polygon(Polygon(outer, [inner]), h)
    m.apply_translation((0, 0, z0))
    return m


def rim_cap() -> trimesh.Trimesh:
    """The top RIM_CAP_H of the lip, which prints in the numbers' colour."""
    return _rim(P.SLAB_T + P.RIM_H - P.RIM_CAP_H, P.RIM_CAP_H)


def slab_plate() -> trimesh.Trimesh:
    """The solid octagonal plate, with its raised lip around the edge.

    The top RIM_CAP_H of the lip is NOT here: that part ships with the
    numerals and prints in their colour. rim_cap() builds it.
    """
    from shapely.geometry import Polygon

    outer, _ = rim_rings()
    parts = [trimesh.creation.extrude_polygon(Polygon(outer), P.SLAB_T)]
    h = P.RIM_H - P.RIM_CAP_H
    if h > 1e-9:
        parts.append(_rim(P.SLAB_T, h))
    return S.union_all(parts)


def post_capped(col_index: int, row: int) -> bool:
    """Does this cell's post get its top in the numbers' colour?"""
    if is_summit(col_index, row):
        return False           # a summit post is split by its digit instead
    mode = P.POST_CAP
    if mode == "all":
        return True
    if mode == "even-rows":
        return row % 2 == 0
    if mode == "odd-rows":
        return row % 2 == 1
    if mode == "even-columns":
        return P.COLUMNS[col_index] % 2 == 0
    return False


def _post(cx: float, cy: float, z0: float, segs: int | None = None,
          part: str = "all") -> trimesh.Trimesh:
    """A cell's post. `part` splits it for two-colour printing.

    "stem" is everything below the cap and "cap" is the rest, and the split
    is put at POST_CAP_H below the top. With that set to the chamfer height
    the cut lands exactly where the post starts bevelling in, so the cap is
    the whole of what you see from directly above and the straight sides stay
    in the board's colour.
    """
    rq = P.POST_D * 0.5
    c = P.POST_CHAMFER
    top = z0 + P.POST_H
    zc = top - P.POST_CAP_H
    full = [(0.0, z0), (rq, z0), (rq, top - c), (rq - c, top), (0.0, top)]
    if part == "all":
        prof = full
    elif part == "stem":
        prof = [(0.0, z0), (rq, z0)] + [(r, z) for r, z in full[2:] if z <= zc]
        prof += [(prof[-1][0], zc), (0.0, zc)] if prof[-1][1] < zc else [(0.0, zc)]
    elif part == "cap":
        prof = [(0.0, zc)] + [(r, z) for r, z in full[1:] if z >= zc]
        if prof[1][1] > zc:
            prof.insert(1, (rq, zc))
    else:
        raise ValueError(part)
    m = S.lathe(prof, segs=segs or P.CELL_SEGS)
    m.apply_translation((cx, cy, 0.0))
    return m


def post_caps(segs: int | None = None) -> list[trimesh.Trimesh]:
    """The accent-coloured tops, for whichever cells POST_CAP selects."""
    return [_post(*cell_xy(i, r), seat_z(), segs=segs, part="cap")
            for i, r in all_cells() if post_capped(i, r)]


def _glyph_solid(text: str, size: float, max_w: float, x: float, y: float,
                 z0: float, thickness: float) -> trimesh.Trimesh:
    """A string extruded to `thickness`, centred on (x, y), sitting at z0.

    Anything wider than max_w is condensed in X ONLY. Scaling both axes would
    drop the cap height with the width, and a label that is shorter than its
    neighbours reads as a different, lesser label -- which is exactly what
    happened to 10, 11 and 12 the first time round.
    """
    t = S.text_solid(text, size, thickness, weight=P.NUMERAL_FONT_WEIGHT)
    w = t.bounds[1][0] - t.bounds[0][0]
    if w > max_w:
        t.apply_scale((max_w / w, 1.0, 1.0))
    t.apply_translation((x, y, z0))
    return t


def _digit_solid(num: int, x: float, y: float, z0: float,
                 thickness: float) -> trimesh.Trimesh:
    return _glyph_solid(str(num), P.NUMERAL_SIZE, P.NUMERAL_MAX_W,
                        x, y, z0, thickness)


# ---------------------------------------------------------------------------
# the title along the bottom of the lens
# ---------------------------------------------------------------------------

def title_letters() -> list[tuple[str, float, float]]:
    """(letter, x, y) for each title letter, hung under its column.

    X always comes from the column -- that is what makes a letter belong to a
    number. The height is TITLE_FOLLOW between two extremes:

    1.0  each letter hangs below its OWN column's bottom cell, so the title
         follows the underside of the lens and CAN'T steps down while STOP
         steps back up.
    0.0  one straight baseline below the lowest cell on the board.

    A straight line reads better and costs a great deal more frame. An octagon
    has its corners cut off, so a letter that is both far to one side and far
    down is the most expensive content that can be put on one: levelling the
    title takes this board from 317 mm across to 395, which is off the bed by
    70 mm. The cascade keeps every letter where the octagon actually has room.
    """
    flat = min(cell_xy(i, 0)[1] for i in range(len(P.ROWS))) - P.TITLE_GAP
    out = []
    for col, ch in P.TITLE_TEXT.items():
        i = P.COLUMNS.index(col)
        x, y = cell_xy(i, 0)
        own = y - P.TITLE_GAP
        out.append((ch, x, flat + P.TITLE_FOLLOW * (own - flat)))
    return out


def pocket_fills(thickness: float | None = None):
    """The digit and letter solids that sit in the engraved pockets.

    The one thing the two-colour pair has that the single-colour board does
    not: on board.stl those pockets are left empty and read as engraving.
    Everything else -- the whole lip, the whole post tops, the whole summit
    posts -- has to be present in BOTH.
    """
    t = P.NUMERAL_DEPTH if thickness is None else thickness
    top = seat_z()
    out = []
    for i, num in enumerate(P.COLUMNS):
        x, y = numeral_xy(i)
        # the post stands on solid plate, so the pocket stops at its edge --
        # the same cut _summit_parts() makes, or the volumes do not line up
        column = S.tube(x, y, P.POST_D * 0.5 + P.NUMERAL_POST_CLEAR, 0.0,
                        top - t - 1.0, top + 2.0, segs=P.CELL_SEGS)
        out.append(trimesh.boolean.difference(
            [_digit_solid(num, x, y, top - t, t), column], engine="manifold"))
    return out + _title_parts(P.TITLE_DEPTH, top - P.TITLE_DEPTH)


def _title_parts(thickness: float, z0: float):
    """Letter solids at (z0, z0 + thickness)."""
    return [_glyph_solid(ch, P.TITLE_SIZE, P.TITLE_MAX_W, x, y, z0, thickness)
            for ch, x, y in title_letters()]


@lru_cache(maxsize=8)
def _title_extents(_key):
    """Plan bounding box of each title letter. Cached: content_points() is
    called on every octagon() and building eight glyph meshes each time is
    seconds, not milliseconds. The key carries every parameter the answer
    depends on, so changing one at runtime invalidates it."""
    return tuple((float(m.bounds[0][0]), float(m.bounds[0][1]),
                  float(m.bounds[1][0]), float(m.bounds[1][1]))
                 for m in _title_parts(1.0, 0.0))


def title_extents():
    return _title_extents((
        tuple(sorted(P.TITLE_TEXT.items())), P.TITLE_SIZE, P.TITLE_MAX_W,
        P.TITLE_GAP, P.TITLE_FOLLOW, tuple(P.COLUMN_SHORTFALL),
        tuple(P.COLUMN_DROP), P.PITCH_X, P.PITCH_Y,
        tuple(P.ROWS), P.SUMMIT_STEP))


def _summit_parts(segs: int | None = None):
    """(pocket cutters, accent solids, body posts) for the eleven summits.

    The digit is cut INTO the box rather than raised off it, because a piece
    seats on that box: a digit standing proud would be what the skirt rests on
    and the piece would rock.

    The post is then split by the same glyph, extruded vertically through it.
    Where the digit passes under the post, the post is accent-coloured; the
    rest of it is board-coloured. Seen from directly above the number is
    therefore whole -- the post is coloured by exactly what it covers. A post
    in one flat colour loses a sixth of an 8 and takes its waist with it.
    """
    segs = segs or P.CELL_SEGS
    cutters, accents, body_posts = [], [], []
    depth, t_post = P.NUMERAL_DEPTH, P.POST_H
    top = seat_z()

    # the title, cut into the plate exactly as the numbers are. No post runs
    # through a letter, so there is nothing to split and nothing to hand back.
    if P.TITLE_TEXT:
        cutters += _title_parts(P.TITLE_DEPTH + 1.0, top - P.TITLE_DEPTH)
        accents += _title_parts(P.TITLE_DEPTH, top - P.TITLE_DEPTH)

    for i, num in enumerate(P.COLUMNS):
        x, y = numeral_xy(i)

        # the pocket stops at the post's edge, so the two oranges meet flush
        column = S.tube(x, y, P.POST_D * 0.5 + P.NUMERAL_POST_CLEAR, 0.0,
                        top - depth - 1.0, top + 2.0, segs=segs)
        # the cutter runs proud of the plate so its top face is not coplanar
        # with the plate's, which is where boolean engines get fussy
        cutters.append(trimesh.boolean.difference(
            [_digit_solid(num, x, y, top - depth, depth + 1.0), column],
            engine="manifold"))
        accents.append(trimesh.boolean.difference(
            [_digit_solid(num, x, y, top - depth, depth), column],
            engine="manifold"))

        post = _post(x, y, top, segs=segs)
        prism = _digit_solid(num, x, y, top, t_post + 1.0)
        accents.append(trimesh.boolean.intersection([post, prism],
                                                    engine="manifold"))
        body_posts.append(trimesh.boolean.difference([post, prism],
                                                     engine="manifold"))
    return cutters, accents, body_posts


def build_board(numerals_only: bool = False, segs: int | None = None,
                verbose: bool = False) -> trimesh.Trimesh:
    """One half of the board; the two together are the whole of it.

    numerals_only=False  the BODY: the plate, the lip below its cap, and the
                         posts less whatever the accent part carries. Prints
                         in the board's colour.
    numerals_only=True   the ACCENT: the digit and letter fills, the slice of
                         each summit post its digit passes through, the cap on
                         the lip, and the top of every capped post. Prints in
                         the numbers' colour.

    There used to be a third: a single-colour board with the pockets left
    empty, which is what board.stl was. It was a second definition of the
    same object that nothing downstream read, and it diverged twice without
    anyone noticing -- once losing the top of every capped post, once
    shipping every summit post with a digit-shaped slot through it. The
    design has wanted two filaments since the numbers went in, so it is gone.
    build_board_assembled() is what to reach for when the whole object is
    what you mean.
    """
    segs = segs or P.CELL_SEGS
    cutters, accents, body_posts = _summit_parts(segs)

    def _post_part(i, r):
        # a capped post hands its top to the accent part, exactly as the lip
        # hands over its cap
        return "stem" if post_capped(i, r) else "all"

    if numerals_only:
        if P.RIM_CAP_H > 1e-9:
            accents = accents + [rim_cap()]
        accents = accents + post_caps(segs)
        return S.union_all(accents)

    # the plate, then a post per cell standing on it. The body hands the lip's
    # cap and the capped post tops over to the accent part.
    parts: list[trimesh.Trimesh] = [slab_plate()]
    summit_n = 0
    for i, r in all_cells():
        x, y = cell_xy(i, r)
        parts.append(body_posts[summit_n] if is_summit(i, r)
                     else _post(x, y, seat_z(), segs=segs,
                                part=_post_part(i, r)))
        summit_n += is_summit(i, r)

    if verbose:
        print(f"    fusing {len(parts)} solids ...", flush=True)
    body = S.union_all(parts)
    if verbose:
        print(f"    cutting {len(cutters)} pockets ...", flush=True)
    return trimesh.boolean.difference([body, S.union_all(cutters)],
                                      engine="manifold")


def build_board_assembled(segs: int | None = None,
                          verbose: bool = False) -> trimesh.Trimesh:
    """The board as it exists once both filaments have been through it.

    What a piece actually sits on, and what to measure when the question is
    about the finished object rather than about one of the two files.
    """
    return S.union_all([build_board(segs=segs, verbose=verbose),
                        build_board(numerals_only=True, segs=segs)])


# ---------------------------------------------------------------------------
# playing pieces
# ---------------------------------------------------------------------------

def _piece_profile(body_profile, body_h: float) -> list[tuple[float, float]]:
    """Closed (r, z) profile for a piece: open socket below, post on top.

    Wound counter-clockwise, starting at the socket mouth on the underside:
    out across the bottom face, up the outside, in across the top, up the
    post, back to the axis, down the solid core, then out and down the
    cone-roofed socket to close.

    The roof climbs at 45 degrees so it needs no support. A full cone would
    need the socket's radius in height, which a 6.30 mm body has not got, so
    it is truncated: it rises until PEG_SOCKET_ROOF of solid is left above it
    and the small flat that remains is bridged. Where there IS room for a full
    cone -- a taller body, or a narrower socket -- the flat closes to nothing
    and this reduces to the original apex.
    """
    rq = P.PEG_POST_D * 0.5
    rs = P.PEG_SOCKET_D * 0.5
    c = P.PEG_POST_CHAMFER
    sc = P.PEG_SOCKET_CHAMFER
    z_top = body_h
    z_post = z_top + P.PEG_POST_H
    z_roof = min(P.PEG_SOCKET_DEPTH + rs, body_h - P.PEG_SOCKET_ROOF)
    r_flat = max(rs - (z_roof - P.PEG_SOCKET_DEPTH), 0.0)

    prof = [
        (rs + sc, 0.0),         # socket mouth, flared to find the post
        (body_profile[0][0], 0.0),   # out across the underside to the skirt
    ]
    prof += [(r, dz) for r, dz in body_profile[1:]]
    prof += [
        (rq, z_top),            # in across the top face to the post
        (rq, z_post - c),       # up the post
        (rq - c, z_post),       # lead-in for the socket above
        (0.0, z_post),
        (0.0, z_roof),          # down the solid core to the roof
    ]
    if r_flat > 1e-9:
        prof.append((r_flat, z_roof))    # the flat the printer bridges
    prof += [
        (rs, P.PEG_SOCKET_DEPTH),   # cone roof, opening out and down
        (rs, sc),               # down the socket wall
    ]
    return prof


def socket_bridge() -> float:
    """Span of the flat left at the top of the truncated socket roof."""
    rs = P.PEG_SOCKET_D * 0.5
    z_roof = min(P.PEG_SOCKET_DEPTH + rs, P.PEG_BODY_H - P.PEG_SOCKET_ROOF)
    return 2.0 * max(rs - (z_roof - P.PEG_SOCKET_DEPTH), 0.0)


def _scallops(n: int, at_r: float, r: float, z0: float, z1: float,
              segs: int | None = None) -> list[trimesh.Trimesh]:
    """n vertical cylinders spaced round the axis, to be cut away.

    A scallop is the one decoration that costs nothing to print: the cut face
    is vertical however deep it goes, so there is no overhang to support and
    no bridge to span.
    """
    return [S.tube(at_r * np.cos(a), at_r * np.sin(a), r, 0.0, z0, z1,
                   segs=segs or P.PEG_SEGS)
            for a in np.linspace(0, 2 * np.pi, n, endpoint=False)]


def _v_notches(n: int, at_r: float, z_apex: float, z_top: float,
               slope: float = 1.0,
               segs: int | None = None) -> list[trimesh.Trimesh]:
    """n cones, apex down, opening upward at atan(slope) from vertical.

    Cut away, they leave a valley that is narrow at the bottom and wide at
    the top -- so the points between them TAPER, which is the difference
    between a crown and a castle. The piece narrows the whole way up as a
    result, which is also exactly the condition for printing without support.

    `slope` is dr/dz and must stay at or under 1.0, which is 45 degrees: past
    that the wall the notch leaves behind leans out further than the printer
    can lay it. Under it the notch is narrower and the points are fatter, and
    that is the only dial between "reads as a crown" and "carries the next
    piece" -- both of which it has to do.
    """
    out = []
    for a in np.linspace(0, 2 * np.pi, n, endpoint=False):
        m = S.lathe([(0.0, z_apex),
                     (slope * (z_top - z_apex), z_top),
                     (0.0, z_top)], segs=segs or P.PEG_SEGS)
        m.apply_translation((at_r * np.cos(a), at_r * np.sin(a), 0.0))
        out.append(m)
    return out


def _roofed_cuts(n: int, at_r: float, r: float, z_lo: float, z_hi: float,
                 segs: int | None = None) -> list[trimesh.Trimesh]:
    """n cylinders capped with a cone, for cutting a gap that has a CEILING.

    A plain scallop is open at the top, so what it leaves behind is a vertical
    wall and nothing has to span anything. Cutting a window -- material below
    it, material above it, air between -- is a different problem: the ceiling
    of that window is a downward-facing surface the printer has to produce out
    of mid-air.

    So the cut is not a cylinder but a cylinder with a 45 degree cone on top
    of it. The ceiling it leaves is that cone, inverted: the material closes
    back in at 45 degrees instead of bridging flat across the gap. It is the
    same trick as the socket roof, pointed sideways.
    """
    out = []
    for a in np.linspace(0, 2 * np.pi, n, endpoint=False):
        m = S.lathe([(0.0, z_lo), (r, z_lo), (r, z_hi), (0.0, z_hi + r)],
                    segs=segs or P.PEG_SEGS)
        m.apply_translation((at_r * np.cos(a), at_r * np.sin(a), 0.0))
        out.append(m)
    return out


def _arc(r0: float, z0: float, r1: float, z1: float, bulge: float,
         n: int = 10) -> list[tuple[float, float]]:
    """A curved run of profile points from (r0, z0) to (r1, z1).

    `bulge` picks the shape: 0 is the straight line, positive eases the START
    (so the curve leaves (r0, z0) steep in z and flattens), negative eases the
    end. The point of having it as a parameter rather than an arc is the 45
    degree rule -- every segment's dr/dz has to stay under 1.0, and what that
    costs is exactly the curvature, so the curve has to be tunable against it
    rather than assumed.

    The first point is left out: whatever it is appended to already ends there.
    """
    u = np.linspace(0.0, 1.0, n + 1)[1:]
    s = u + bulge * u * (1.0 - u)
    return [(float(r0 + (r1 - r0) * t), float(z0 + (z1 - z0) * v))
            for t, v in zip(u, s)]


def _crown_points(segs: int | None = None) -> list[trimesh.Trimesh]:
    """Six tapered spikes standing on the crown's floor, out at the rim.

    Frusta, not cut cones. Three earlier crowns were made by cutting into a
    solid rim, and a cut cannot turn a wall into six separate things standing
    up -- it can only put holes in it. Added, each point is a thing in its own
    right: 4.00 mm across at the foot, 2.30 at the top, narrowing the whole
    way, which is the printable direction and the crown-shaped one at once.
    """
    segs = segs or P.PEG_SEGS
    out = []
    for a in np.linspace(0, 2 * np.pi, P.CROWN_POINTS, endpoint=False):
        m = S.lathe([(P.CROWN_SPIKE_R0, P.CROWN_SPIKE_Z0),
                     (P.CROWN_SPIKE_R1, P.PEG_BODY_H),
                     (0.0, P.PEG_BODY_H),
                     (0.0, P.CROWN_SPIKE_Z0)], segs=segs)
        m.apply_translation((P.CROWN_SPIKE_AT * np.cos(a),
                             P.CROWN_SPIKE_AT * np.sin(a), 0.0))
        out.append(m)
    return out


def _saucer_profile() -> list[tuple[float, float]]:
    """The UFO's hull: base, column, swept underside, brim, dome.

    A lathe. The landing gear and the pads are added on top of this, because
    four legs and six bars are not surfaces of revolution and pretending
    otherwise is what produced the last two versions.
    """
    p = [(P.SAUCER_BASE_R, 0.00),
         (P.SAUCER_BASE_R, P.SAUCER_BASE_H),
         (P.SAUCER_WAIST_R, P.SAUCER_BASE_H + 0.30),
         (P.SAUCER_WAIST_R, P.SAUCER_WAIST_Z)]
    p += _arc(P.SAUCER_WAIST_R, P.SAUCER_WAIST_Z, P.PEG_MAX_R, P.SAUCER_BRIM_Z,
              bulge=P.SAUCER_UNDER_BULGE, n=14)
    # the edge, then a flat shelf inward: without the shelf the dome starts
    # at the widest point and the brim stops being a brim
    p.append((P.PEG_MAX_R, P.SAUCER_BRIM_Z + P.SAUCER_BRIM_T))
    z_shelf = P.SAUCER_BRIM_Z + P.SAUCER_BRIM_T + P.SAUCER_SHELF_DZ
    p.append((P.SAUCER_SHELF_R, z_shelf))
    p += _arc(P.SAUCER_SHELF_R, z_shelf, P.SAUCER_DOME_R, P.PEG_BODY_H,
              bulge=P.SAUCER_DOME_BULGE, n=14)
    return p


def _saucer_gear(segs: int | None = None) -> list[trimesh.Trimesh]:
    """Four square landing tubes and six rectangular landing pads."""
    segs = segs or P.PEG_SEGS
    out = []
    for a in np.linspace(0, 2 * np.pi, P.SAUCER_LEGS, endpoint=False):
        out.append(S.tube(P.SAUCER_LEG_AT * np.cos(a),
                          P.SAUCER_LEG_AT * np.sin(a),
                          P.SAUCER_LEG_R, 0.0,
                          P.SAUCER_BASE_H - 0.10, P.SAUCER_LEG_Z1, segs=4))
    for a in np.linspace(0, 2 * np.pi, P.SAUCER_PADS, endpoint=False):
        c, s = np.cos(a), np.sin(a)
        out.append(S.strut((P.SAUCER_PAD_R0 * c, P.SAUCER_PAD_R0 * s),
                           (P.SAUCER_PAD_R1 * c, P.SAUCER_PAD_R1 * s),
                           P.SAUCER_PAD_W,
                           P.PEG_BODY_H - P.SAUCER_PAD_Z, P.SAUCER_PAD_Z))
    return out


def piece_seat_r(style: str) -> float:
    """Radius of the face a piece stands on -- its profile at z = 0."""
    return piece_profile_of(style)[0][0]


def piece_max_r(style: str) -> float:
    return max(r for r, _ in piece_profile_of(style))


def build_player_piece(style: str, segs: int | None = None) -> trimesh.Trimesh:
    """One player's marker. Same interface as every other; different shape."""
    segs = segs or P.PEG_SEGS
    top = P.PEG_BODY_H + P.PEG_POST_H
    if style == "counter":
        return build_marker(segs)

    if style == "crown":
        body = S.lathe(_piece_profile(P.CROWN_BODY_PROFILE, P.PEG_BODY_H),
                       segs=segs)
        return S.union_all([body] + _crown_points(segs))

    if style == "saucer":
        body = S.lathe(_piece_profile(_saucer_profile(), P.PEG_BODY_H),
                       segs=segs)
        return S.union_all([body] + _saucer_gear(segs))

    if style == "cog":
        body = S.lathe(_piece_profile(P.COG_BODY_PROFILE, P.PEG_BODY_H),
                       segs=segs)
        cut = _scallops(P.COG_FLUTES, P.COG_CUT_AT, P.COG_CUT_R,
                        P.COG_CUT_Z, top + 1.0, segs)
        return trimesh.boolean.difference([body] + cut, engine="manifold")
    raise ValueError(style)


def piece_profile_of(style: str):
    """The lathe profile behind a style, for the printability checks.

    The saucer's is computed rather than typed, because its underside and its
    dome are curves; everything else is a handful of corners in params.py.
    """
    if style == "saucer":
        return _saucer_profile()
    return {"counter": P.PEG_BODY_PROFILE, "crown": P.CROWN_BODY_PROFILE,
            "cog": P.COG_BODY_PROFILE,
            "runner": P.RUNNER_BODY_PROFILE}[style]


def build_piece(style: str, segs: int | None = None) -> trimesh.Trimesh:
    """Any piece by name: the four player shapes, or the runner."""
    return (build_runner(segs) if style == "runner"
            else build_player_piece(style, segs))


# Every piece on the board, not just the four a player owns. The runner
# obeys the same envelope rules as a marker, so it belongs in the same list
# -- the checks that read this are the ones that would have caught it being
# 2 mm wider and 2 mm taller than everything else for as long as it was.
# The order is the piece NUMBERING; params.py owns it.
PIECE_STYLES = list(P.PIECE_STYLES)


def piece_number(style: str) -> int:
    """A piece's reference number: 1-4 the player shapes, 5 the runner."""
    return PIECE_STYLES.index(style) + 1


def piece_of_number(n: int) -> str:
    """The inverse. Raises rather than guessing if the number is not one."""
    if not 1 <= n <= len(PIECE_STYLES):
        raise ValueError(f"no piece {n}; they run 1-{len(PIECE_STYLES)}")
    return PIECE_STYLES[n - 1]


def piece_role(style: str) -> str:
    """Who owns it: a player's letter, or the shared pool."""
    i = PIECE_STYLES.index(style)
    return (f"player {P.PLAYER_LABELS[i]}" if i < len(P.PLAYER_LABELS)
            else "shared")


def build_marker(segs: int | None = None) -> trimesh.Trimesh:
    return S.lathe(_piece_profile(P.PEG_BODY_PROFILE, P.PEG_BODY_H),
                   segs=segs or P.PEG_SEGS)


def build_runner(segs: int | None = None) -> trimesh.Trimesh:
    return S.lathe(_piece_profile(P.RUNNER_BODY_PROFILE, P.RUNNER_BODY_H),
                   segs=segs or P.PEG_SEGS)


def build_plate(mesh: trimesh.Trimesh, count: int, spacing: float | None = None,
                per_row: int = 6) -> trimesh.Trimesh:
    """Arrange `count` copies in a grid, ready to drop straight into a slicer."""
    spacing = spacing or (2 * max(r for r, _ in P.PEG_BODY_PROFILE) + 4.0)
    out = []
    for k in range(count):
        c = mesh.copy()
        c.apply_translation(((k % per_row) * spacing, (k // per_row) * spacing, 0.0))
        out.append(c)
    return trimesh.util.concatenate(out)


# ---------------------------------------------------------------------------
# fit-test coupon
# ---------------------------------------------------------------------------

def build_fit_coupon(segs: int | None = None) -> trimesh.Trimesh:
    """Five posts at diameters either side of nominal, on one small bar.

    The board is male now, so the coupon carries POSTS and you try a real
    piece over each one. Same pad height, same post height and the same
    chamfered lead-in as the board, because a fit test only transfers if the
    part is shaped and cooled the same way. Each post is labelled with the
    second decimal of its diameter: the one marked 9 is 5.90 mm.
    """
    segs = segs or P.CELL_SEGS
    skirt = max(r for r, _ in P.PEG_BODY_PROFILE)
    pitch = max(P.PAD_OD, 2.0 * skirt) + 5.0
    parts = []
    n = len(P.FIT_TEST_POSTS)
    x0 = -(n - 1) * pitch * 0.5

    for k, dia in enumerate(P.FIT_TEST_POSTS):
        x = x0 + k * pitch
        rq = dia * 0.5
        c = P.POST_CHAMFER
        # a post standing on the bar, exactly as one stands on the plate
        top = P.FIT_COUPON_T + P.POST_H
        m = S.lathe([
            (0.0, P.FIT_COUPON_T - 0.5), (rq, P.FIT_COUPON_T - 0.5),
            (rq, top - c), (rq - c, top), (0.0, top),
        ], segs=segs)
        m.apply_translation((x, 0.0, 0.0))
        parts.append(m)

        digit = str(int(round(dia * 100)) % 10)      # 5.90 -> "9"
        t = S.text_solid(digit, 5.0, 1.0, weight="bold")
        t.apply_translation((x, -P.PAD_OD * 0.5 - 5.0, P.FIT_COUPON_T - 0.2))
        parts.append(t)

    bar_y0 = -P.PAD_OD * 0.5 - 9.5
    bar_y1 = P.PAD_OD * 0.5
    parts.append(S.rounded_plate(0.0, (bar_y0 + bar_y1) * 0.5,
                                 (n - 1) * pitch + P.PAD_OD,
                                 bar_y1 - bar_y0, P.FIT_COUPON_T, 2.0))
    return S.union_all(parts)


# ---------------------------------------------------------------------------
# board stub — a corner of the real board, for a test print
# ---------------------------------------------------------------------------

def stub_box() -> tuple[tuple[float, float], tuple[float, float]]:
    """The plan rectangle the stub is cut out of, ((x0, y0), (x1, y1)).

    The top side runs OUTSIDE the octagon, and does nothing: the cut is an
    intersection with the board, so what survives there is the board's own
    outline and its raised lip. The stub always takes the TOP of its columns,
    because that is where the numbers are and where the lip comes closest to
    a pad -- the two things on this board a small test print can settle.

    The other three sides are raw cut edges across open plate, and they are
    placed to miss every post rather than at a fixed offset. Sideways that is
    easy: columns are a uniform PITCH_X apart, so half a pitch out from the
    outermost kept column is always 11 mm of clearance, which is more than the
    6.6 mm skirt needs. Downwards it is not, because neighbouring columns have
    different row pitches and stagger past each other -- the gap there can be
    as little as 12 mm, and the midpoint of it would leave a piece's skirt
    hanging 0.6 mm off the raw edge. So the bottom edge drops as far as it can
    while still clearing the highest row the stub does not keep: far enough
    that every post in the stub has a full skirt's worth of plate under it.
    """
    poly = np.asarray(octagon(), dtype=float)
    idx = sorted(P.COLUMNS.index(c) for c in P.STUB_COLUMNS)

    xs = [cell_xy(i, 0)[0] for i in idx]
    x0, x1 = min(xs) - P.PITCH_X * 0.5, max(xs) + P.PITCH_X * 0.5
    if x0 - poly[:, 0].min() < P.PITCH_X:          # the outline is nearer than
        x0 = poly[:, 0].min() - 10.0               # the next column would be
    if poly[:, 0].max() - x1 < P.PITCH_X:
        x1 = poly[:, 0].max() + 10.0

    # every row height standing anywhere in that band of columns, top first
    levels = sorted({round(cell_xy(i, r)[1], 6) for i, r in all_cells()
                     if x0 < cell_xy(i, r)[0] < x1}, reverse=True)
    # STUB_ROWS is a minimum, not a target. The bottom cut wants a gap it can
    # sit in with a whole skirt of plate above it and the row below untouched,
    # and the gaps here are uneven -- as little as 12 mm where two columns of
    # different row pitch stagger past each other. So take one more row at a
    # time until a gap is found that can hold both.
    skirt = max(r for r, _ in P.PEG_BODY_PROFILE)
    y0 = poly[:, 1].min() - 10.0
    for n in range(P.STUB_ROWS, len(levels) + 1):
        kept = levels[:n]
        below = [v for v in levels if v < min(kept)]
        if not below:
            break                                   # ran out: keep the lot
        room = min(kept) - skirt - 0.5              # a whole skirt of plate
        clear = max(below) + P.POST_D * 0.5 + 0.5   # miss the row below
        if room >= clear:
            y0 = room
            break
    return (x0, y0), (x1, poly[:, 1].max() + 10.0)


def stub_cells() -> list[tuple[int, int]]:
    """(column index, row) of every cell that falls inside the stub."""
    (x0, y0), (x1, y1) = stub_box()
    return [(i, r) for i, r in all_cells()
            if x0 < cell_xy(i, r)[0] < x1 and y0 < cell_xy(i, r)[1] < y1]


def build_board_stub(part: trimesh.Trimesh) -> trimesh.Trimesh:
    """Cut the stub out of an already-built board part.

    Takes the board rather than rebuilding a lookalike, so there is no second
    definition of the slab, the lip or the numbers that could drift away from
    the first one. Pass the fused board, the two-colour body, or the numerals;
    each gives the matching piece of the stub.

    The result stays in BOARD coordinates. It has to: the stub body and the
    stub numerals are loaded into a slicer as two parts of one object and
    land in register only because neither has been moved.
    """
    (x0, y0), (x1, y1) = stub_box()
    zlo, zhi = -10.0, P.SLAB_T + P.POST_H + 10.0
    knife = trimesh.creation.box(extents=(x1 - x0, y1 - y0, zhi - zlo))
    knife.apply_translation(((x0 + x1) * 0.5, (y0 + y1) * 0.5,
                             (zlo + zhi) * 0.5))
    return trimesh.boolean.intersection([part, knife], engine="manifold")
