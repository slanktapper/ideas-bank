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


def half_height(col_index: int) -> float:
    """How far a column reaches above (and below) the midline, in mm.

    The longest column keeps the nominal row pitch. Every other column gives
    up the height COLUMN_SHORTFALL allows it and spreads its own cells over
    whatever span is left -- so the cell COUNT stays as the game needs it
    while the column can still be made to reach further towards the frame.
    """
    tallest = max(k_max(i) for i in range(len(P.ROWS)))
    steps_out = int(round(tallest - k_max(col_index)))
    return tallest * P.PITCH_Y - P.COLUMN_SHORTFALL[steps_out]


def row_pitch(col_index: int) -> float:
    """That column's own spacing between cells."""
    k = k_max(col_index)
    return half_height(col_index) / k if k else 0.0


def grid_y(col_index: int, row: int) -> float:
    """Row position on the plain centred grid, before the summit steps out."""
    return (row - k_max(col_index)) * row_pitch(col_index)


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


def lattice_centre() -> np.ndarray:
    """Middle of the cell field. Shields lean away from here."""
    pts = np.array([cell_xy(i, r) for i, r in all_cells()], dtype=float)
    return pts.mean(axis=0)


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


def _trim(p0, p1, r0: float, r1: float):
    """Pull a segment back by r0 at its start and r1 at its end.

    Struts are specified centre-to-centre because that is how you think about
    a lattice, but they must not reach the centre or they would fill the bore.
    """
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    if L <= r0 + r1 + 0.2:
        return None
    d /= L
    return p0 + d * r0, p1 - d * r1


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
    corners = [(dx * P.PLAQUE_W / 2, dy * P.PLAQUE_H / 2)
               for dx in (-1, 1) for dy in (-1, 1)]
    pts = []
    for i, row in all_cells():
        x, y = cell_xy(i, row)
        for ox, oy in (corners if is_summit(i, row) else ring):
            pts.append((x + ox, y + oy))
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

    if P.OCTAGON_REGULAR:
        # Equal edges need a chamfer of exactly 2/(2+sqrt2) of the half-span,
        # which reduces the octagon to three constraints: |dx| <= a,
        # |dy| <= a, and |dx| + |dy| <= a*sqrt2. Size a from the content
        # against all three rather than from its bounding box, or the corner
        # cuts slice through the ends of the lens.
        need = max(d[:, 0].max(), d[:, 1].max(),
                   (d[:, 0] + d[:, 1]).max() / np.sqrt(2.0))
        margin = P.OCTAGON_MARGIN
        if P.BOARD_STYLE == "slab":
            # the raised lip sits inside the outline, so the outline has to
            # stand off far enough that the lip never lands on a pad
            margin = max(margin, P.RIM_W + P.RIM_CLEAR)
        a = b = need + margin
        c = a * 2.0 / (2.0 + np.sqrt(2.0))
    else:
        a = (hi[0] - lo[0]) * 0.5 + P.OCTAGON_MARGIN
        b = (hi[1] - lo[1]) * 0.5 + P.OCTAGON_MARGIN
        c = 0.55 * min(a, b)
    return [
        (cx + a - c, cy + b), (cx + a, cy + b - c),
        (cx + a, cy - b + c), (cx + a - c, cy - b),
        (cx - a + c, cy - b), (cx - a, cy - b + c),
        (cx - a, cy + b - c), (cx - a + c, cy + b),
    ]


def octagon_centre() -> np.ndarray:
    lo, hi = content_bounds()
    return (lo + hi) * 0.5


def _ray_hit(origin, direction, poly) -> np.ndarray | None:
    """First point where a ray leaving `origin` crosses a closed polygon."""
    o = np.asarray(origin, dtype=float)
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    best_t, best = np.inf, None
    for j in range(len(poly)):
        a = np.asarray(poly[j], dtype=float)
        e = np.asarray(poly[(j + 1) % len(poly)], dtype=float) - a
        m = np.array([[d[0], -e[0]], [d[1], -e[1]]])
        if abs(np.linalg.det(m)) < 1e-12:
            continue
        t, s = np.linalg.solve(m, a - o)
        if t > 1e-9 and -1e-9 <= s <= 1 + 1e-9 and t < best_t:
            best_t, best = t, o + d * t
    return best


def _rect_exit(centre, w: float, h: float, direction, inset: float):
    """Where a ray leaving a rectangle's centre crosses its edge, pulled in.

    Spokes have to start on the edge of a number shield, not at its middle,
    or they would be printed straight across the digit. `inset` keeps a little
    overlap so the spoke still fuses into the shield.
    """
    c = np.asarray(centre, dtype=float)
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    ts = []
    if abs(d[0]) > 1e-9:
        ts.append(w * 0.5 / abs(d[0]))
    if abs(d[1]) > 1e-9:
        ts.append(h * 0.5 / abs(d[1]))
    return c + d * (min(ts) - inset)


# ---------------------------------------------------------------------------
# struts
# ---------------------------------------------------------------------------

def _lattice_struts() -> list[tuple[tuple, tuple, bool]]:
    """Every strut inside the lens, as (p0, p1, is_frame), centre to centre."""
    out = []
    ncol = len(P.ROWS)

    # verticals, within a column. Nothing inside the lens runs at frame
    # section: the octagon is the frame now, and a 5.2 mm chain strut leaving
    # a summit at 42 degrees clips the bottom corner of that column's digit.
    #
    # Struts can run right under a number box without any special handling:
    # they stand 3.4 mm tall and the box is 4.0 mm thick, so a strut that
    # crosses a digit in plan is buried inside the plate, not printed across
    # the number.
    for i in range(ncol):
        for r in range(P.ROWS[i] - 1):
            out.append((cell_xy(i, r), cell_xy(i, r + 1), False))

    # Columns need not share a row pitch, so nothing is guaranteed to be
    # level and "horizontal" is not always a meaningful word. Two cases, and
    # both have to be symmetric left-to-right or the board comes out lopsided:
    #
    #   columns that DO line up  -- a level strut at every shared row, plus
    #       one diagonal per quad, herringboned by parity. This is the plain
    #       square-grid bracing and it is what most of the board uses.
    #   columns that do NOT     -- each cell links to the two nearest in the
    #       other column, taken from BOTH sides and unioned, which is the
    #       only way to keep the pattern the same on either side of the
    #       middle.
    for i in range(ncol - 1):
        ya = [grid_y(i, r) for r in range(P.ROWS[i])]
        yb = [grid_y(i + 1, s) for s in range(P.ROWS[i + 1])]
        pairs = set()

        def _nearest(vals, y):
            return min(range(len(vals)), key=lambda k: abs(vals[k] - y))

        # "Aligned" has to be a symmetric test, or a gap and its mirror take
        # different branches and the board comes out lopsided. Equal pitches
        # and centred columns line up exactly when their half-heights differ
        # by a whole number of rows.
        pa, pb = row_pitch(i), row_pitch(i + 1)
        aligned = (abs(pa - pb) < 1e-6
                   and abs((k_max(i) - k_max(i + 1)) % 1.0) < 1e-6)
        if aligned:
            # only the rows the two columns actually share; the cells beyond
            # that are carried by their own column and by the edge chains
            shared = sorted(((r, s) for r in range(len(ya))
                             for s in range(len(yb))
                             if abs(ya[r] - yb[s]) < 1e-6),
                            key=lambda rs: ya[rs[0]])
            pairs.update(shared)
            for k in range(len(shared) - 1):
                (r0, s0), (r1, s1) = shared[k], shared[k + 1]
                # Herringbone, but mirrored about the middle of the board.
                # Keyed on i alone the pattern is the same handedness all the
                # way across, which reads as a lopsided board; keyed on the
                # distance from the middle, and flipped on the right-hand
                # side, the whole lattice comes out symmetric.
                # Key the parity on the row's POSITION, not its index: a gap
                # and its mirror share y values but number their rows
                # differently, so an index-keyed herringbone comes out
                # handed.
                level = int(round(ya[r0] / pa))
                near_mid = min(i, ncol - 2 - i)
                rising = (near_mid + level) % 2 == 0
                if i > (ncol - 2) / 2:
                    rising = not rising
                pairs.add((r0, s1) if rising else (r1, s0))
        else:
            for r, y in enumerate(ya):
                for s in sorted(range(len(yb)),
                                key=lambda s: abs(yb[s] - y))[:2]:
                    pairs.add((r, s))
            for s, y in enumerate(yb):
                for r in sorted(range(len(ya)),
                                key=lambda r: abs(ya[r] - y))[:2]:
                    pairs.add((r, s))

        for r, s in sorted(pairs):
            out.append((cell_xy(i, r), cell_xy(i + 1, s), False))

    # the stepped upper and lower edges of the lens
    for i in range(ncol - 1):
        out.append((summit(i), summit(i + 1), False))
        out.append((base(i), base(i + 1), False))
    return out


def _spokes(poly) -> list[tuple[tuple, tuple]]:
    """Bracing from the edge of the lens out to the octagonal frame.

    Radial, from the frame's centre outward, so they fan into the corners the
    lens cannot reach and tie the whole thing together. Spokes off the top of
    a column start at the edge of its number shield rather than at the ring,
    so that no strut is printed across a digit.
    """
    c = octagon_centre()
    out = []

    for i in range(len(P.ROWS)):
        # up and out, from whatever is topmost in this column
        sp = np.asarray(summit(i), dtype=float)
        d = sp - c
        if np.linalg.norm(d) < 1e-9:
            d = np.array([0.0, 1.0])
        d = d / np.linalg.norm(d)
        start = _rect_exit(sp, P.PLAQUE_W, P.PLAQUE_H, d, inset=2.0)
        hit = _ray_hit(start, d, poly)
        if hit is not None:
            out.append((tuple(start), tuple(hit)))

        # down and out, from the bottom ring
        bp = np.asarray(base(i), dtype=float)
        d = bp - c
        if np.linalg.norm(d) < 1e-9:
            d = np.array([0.0, -1.0])
        d = d / np.linalg.norm(d)
        start = bp + d * P.WELD_R
        hit = _ray_hit(start, d, poly)
        if hit is not None:
            out.append((tuple(start), tuple(hit)))

    # sideways, off the middle cells of the two end columns
    for i in (0, len(P.ROWS) - 1):
        for r in range(1, P.ROWS[i] - 1):
            pt = np.asarray(cell_xy(i, r), dtype=float)
            d = pt - c
            if np.linalg.norm(d) < 1e-9:
                continue
            d = d / np.linalg.norm(d)
            start = pt + d * P.WELD_R
            hit = _ray_hit(start, d, poly)
            if hit is not None:
                out.append((tuple(start), tuple(hit)))
    return out


def final_struts() -> list[tuple[tuple, tuple, float, float, str]]:
    """Every strut actually built, trimmed, as (p0, p1, width, height, kind).

    `kind` is "lattice" (both ends land in a collar), "frame" (the octagon
    itself) or "spoke" (lens out to frame). build_board() consumes this list
    verbatim, so a test that measures these is measuring the real board.
    """
    out = []
    for p0, p1, is_frame in _lattice_struts():
        t = _trim(p0, p1, P.WELD_R, P.WELD_R)
        if t is None:
            continue
        w, h = (P.FRAME_W, P.FRAME_H) if is_frame else (P.STRUT_W, P.STRUT_H)
        out.append((tuple(t[0]), tuple(t[1]), w, h, "lattice"))

    poly = octagon()
    for j in range(len(poly)):
        out.append((poly[j], poly[(j + 1) % len(poly)],
                    P.FRAME_W, P.FRAME_H, "frame"))

    for p0, p1 in _spokes(poly):
        out.append((p0, p1, P.OCTAGON_SPOKE_W, P.OCTAGON_SPOKE_H, "spoke"))
    return out


def strut_distance_to(point, p0, p1, width) -> float:
    """Shortest distance in plan from `point` to a strut's rectangle.

    Note this is NOT `weld_radius - width/2`: a strut is trimmed back along
    its own axis, so the nearest part of it is the midpoint of its end face,
    and the half-width runs perpendicular, away from the cell centre. Getting
    that wrong is an easy way to talk yourself into a bore that is fine.
    """
    q = np.asarray(point, dtype=float)
    a = np.asarray(p0, dtype=float)
    b = np.asarray(p1, dtype=float)
    d = b - a
    L = float(np.linalg.norm(d))
    d = d / L
    n = np.array([-d[1], d[0]])
    v = q - a
    s = float(np.clip(v @ d, 0.0, L))
    t = float(np.clip(v @ n, -width * 0.5, width * 0.5))
    return float(np.linalg.norm(q - (a + s * d + t * n)))


# ---------------------------------------------------------------------------
# board
# ---------------------------------------------------------------------------

def build_cell(cx: float, cy: float, segs: int | None = None,
               with_post: bool = True) -> trimesh.Trimesh:
    """An ordinary board cell: a round pad with a post standing on it.

    A solid of revolution, so there is no boolean and no hole to protect. The
    pad's top face is the seat; the post only locates.
    """
    rp = P.PAD_OD * 0.5
    rq = P.POST_D * 0.5
    c = P.POST_CHAMFER
    top = P.PAD_H + P.POST_H
    prof = [(0.0, 0.0), (rp, 0.0), (rp, P.PAD_H)]
    if with_post:
        prof += [(rq, P.PAD_H), (rq, top - c), (rq - c, top), (0.0, top)]
    else:
        prof += [(0.0, P.PAD_H)]
    m = S.lathe(prof, segs=segs or P.CELL_SEGS)
    m.apply_translation((cx, cy, 0.0))
    return m


def seat_z() -> float:
    """Height of every seating face -- what a piece's skirt lands on."""
    return P.SLAB_T if P.BOARD_STYLE == "slab" else P.PAD_H


def rim_rings() -> tuple[list, list]:
    """(outer, inner) plan polygons of the raised lip.

    The inner ring is the outline inset by RIM_W. A regular octagon has the
    same apothem to every edge, so insetting is a plain scale about the
    centre -- (a - RIM_W) / a -- and the lip comes out an even width the whole
    way round.
    """
    outer = [tuple(p) for p in octagon()]
    ctr = octagon_centre()
    apothem = max(abs(np.asarray(outer) - ctr).max(axis=1))
    k = (apothem - P.RIM_W) / apothem
    return outer, [tuple(ctr + (np.asarray(p) - ctr) * k) for p in outer]


def _rim(z0: float, h: float) -> trimesh.Trimesh:
    from shapely.geometry import Polygon

    outer, inner = rim_rings()
    m = trimesh.creation.extrude_polygon(Polygon(outer, [inner]), h)
    m.apply_translation((0, 0, z0))
    return m


def rim_cap() -> trimesh.Trimesh:
    """The top RIM_CAP_H of the lip, which prints in the numbers' colour."""
    return _rim(P.SLAB_T + P.RIM_H - P.RIM_CAP_H, P.RIM_CAP_H)


def slab_plate(cap: bool = True) -> trimesh.Trimesh:
    """The solid octagonal plate, with its raised lip around the edge.

    cap=False leaves the top RIM_CAP_H of the lip off, because that part
    ships with the numerals and prints in their colour. The plate itself and
    the lip below the cap are unaffected either way.
    """
    from shapely.geometry import Polygon

    outer, _ = rim_rings()
    parts = [trimesh.creation.extrude_polygon(Polygon(outer), P.SLAB_T)]
    h = P.RIM_H if cap else P.RIM_H - P.RIM_CAP_H
    if h > 1e-9:
        parts.append(_rim(P.SLAB_T, h))
    return S.union_all(parts)


def build_summit_box(cx: float, cy: float) -> trimesh.Trimesh:
    """A column's number box, which is also its summit pad.

    Same thickness as the round pads, so every seating face on the board is at
    one height and a piece sits the same whatever cell it is in.
    """
    return S.rounded_plate(cx, cy, P.PLAQUE_W, P.PLAQUE_H,
                           P.PLAQUE_T, P.PLAQUE_FILLET)


def _post(cx: float, cy: float, z0: float, segs: int | None = None
          ) -> trimesh.Trimesh:
    rq = P.POST_D * 0.5
    c = P.POST_CHAMFER
    top = z0 + P.POST_H
    m = S.lathe([(0.0, z0), (rq, z0), (rq, top - c), (rq - c, top), (0.0, top)],
                segs=segs or P.CELL_SEGS)
    m.apply_translation((cx, cy, 0.0))
    return m


def _digit_solid(num: int, x: float, y: float, z0: float,
                 thickness: float) -> trimesh.Trimesh:
    t = S.text_solid(str(num), P.NUMERAL_SIZE, thickness,
                     weight=P.NUMERAL_FONT_WEIGHT)
    w = t.bounds[1][0] - t.bounds[0][0]
    if w > P.NUMERAL_MAX_W:              # 10, 11 and 12 are wider than a box
        k = P.NUMERAL_MAX_W / w
        t.apply_scale((k, k, 1.0))
    t.apply_translation((x, y, z0))
    return t


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


def build_board(with_numerals: bool = True, numerals_only: bool = False,
                segs: int | None = None, verbose: bool = False) -> trimesh.Trimesh:
    """Construct the board.

    numerals_only=True   the accent parts: the digit fills, the slice of each
                         post the digit passes through, and the cap on the lip
    with_numerals=True   the board with the pockets cut -- single colour, the
                         numbers read as engraved, the lip whole
    with_numerals=False  the body with pockets too, and with the top of the
                         lip left off, to pair with numerals_only
    """
    segs = segs or P.CELL_SEGS
    slab = P.BOARD_STYLE == "slab"
    cutters, accents, body_posts = _summit_parts(segs)
    if numerals_only:
        if slab and P.RIM_CAP_H > 1e-9:
            accents = accents + [rim_cap()]
        return S.union_all(accents)

    parts: list[trimesh.Trimesh] = []
    if slab:
        # with_numerals is the single-colour board, so it keeps the whole lip;
        # the two-colour body hands the cap over to the numerals part
        parts.append(slab_plate(cap=with_numerals))

    summit_n = 0
    for i, r in all_cells():
        x, y = cell_xy(i, r)
        if P.BOARD_STYLE == "slab":
            # the plate is the pad; only the post stands on it
            parts.append(body_posts[summit_n] if is_summit(i, r)
                         else _post(x, y, seat_z(), segs=segs))
            summit_n += is_summit(i, r)
            continue
        if is_summit(i, r):
            # the box replaces the round pad, and the post on it is only the
            # part the digit does not pass through -- the rest ships with the
            # numbers so it prints in their colour
            parts.append(build_summit_box(x, y))
            parts.append(body_posts[summit_n])
            summit_n += 1
        else:
            parts.append(build_cell(x, y, segs=segs))

    if P.BOARD_STYLE != "slab":
        for p0, p1, w, h, _kind in final_struts():
            parts.append(S.strut(p0, p1, w, h))

    if verbose:
        print(f"    fusing {len(parts)} solids ...", flush=True)
    body = S.union_all(parts)

    if not with_numerals:
        return trimesh.boolean.difference([body, S.union_all(cutters)],
                                          engine="manifold")
    if verbose:
        print("    cutting 11 number pockets ...", flush=True)
    return trimesh.boolean.difference([body, S.union_all(cutters)],
                                      engine="manifold")


# ---------------------------------------------------------------------------
# playing pieces
# ---------------------------------------------------------------------------

def _piece_profile(body_profile, body_h: float) -> list[tuple[float, float]]:
    """Closed (r, z) profile for a piece: open socket below, post on top.

    Wound counter-clockwise, starting at the socket mouth on the underside:
    out across the bottom face, up the outside, in across the top, up the
    post, back to the axis, down the solid core, then out and down the
    cone-roofed socket to close.
    """
    rq = P.PEG_POST_D * 0.5
    rs = P.PEG_SOCKET_D * 0.5
    c = P.PEG_POST_CHAMFER
    sc = P.PEG_SOCKET_CHAMFER
    z_top = body_h
    z_post = z_top + P.PEG_POST_H
    # a 45 degree cone closes the socket, so it needs no bridging
    z_apex = P.PEG_SOCKET_DEPTH + rs

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
        (0.0, z_apex),          # down the solid core
        (rs, P.PEG_SOCKET_DEPTH),   # cone roof, opening out and down
        (rs, sc),               # down the socket wall
    ]
    return prof


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
    pitch = P.PAD_OD + 5.0
    parts = []
    n = len(P.FIT_TEST_POSTS)
    x0 = -(n - 1) * pitch * 0.5

    for k, dia in enumerate(P.FIT_TEST_POSTS):
        x = x0 + k * pitch
        rq = dia * 0.5
        c = P.POST_CHAMFER
        top = P.PAD_H + P.POST_H
        m = S.lathe([
            (0.0, 0.0), (P.PAD_OD * 0.5, 0.0), (P.PAD_OD * 0.5, P.PAD_H),
            (rq, P.PAD_H), (rq, top - c), (rq - c, top), (0.0, top),
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
    kept = levels[:P.STUB_ROWS]
    below = [v for v in levels if v < min(kept)]
    if below:
        skirt = max(r for r, _ in P.PEG_BODY_PROFILE)
        room = min(kept) - skirt - 0.5              # a whole skirt of plate
        clear = max(below) + P.POST_D * 0.5 + 0.5   # miss the row below
        y0 = room if room >= clear else (min(kept) + max(below)) * 0.5
    else:
        y0 = poly[:, 1].min() - 10.0
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
