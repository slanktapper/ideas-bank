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

def k_max(col_index: int) -> int:
    """Half-height of a column in rows. ROWS are all odd, so this is exact."""
    return (P.ROWS[col_index] - 1) // 2


def cell_xy(col_index: int, row: int) -> tuple[float, float]:
    """Centre of the cell at (column index 0..10, row 0..n-1, 0 at the bottom).

    Rows are numbered from the bottom for the game's sake; the geometry is
    centred, so row 0 of a short column is not level with row 0 of a long one.

    """
    return col_index * P.PITCH_X, (row - k_max(col_index)) * P.PITCH_Y


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


# the digit, the box and the post all share one centre
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

def content_bounds() -> tuple[np.ndarray, np.ndarray]:
    """Bounding box of everything the frame has to enclose."""
    r = P.PAD_OD * 0.5
    xs, ys = [], []
    for i, row in all_cells():
        x, y = cell_xy(i, row)
        hx, hy = ((P.PLAQUE_W / 2, P.PLAQUE_H / 2) if is_summit(i, row)
                  else (r, r))
        xs += [x - hx, x + hx]
        ys += [y - hy, y + hy]
    return np.array([min(xs), min(ys)]), np.array([max(xs), max(ys)])


def octagon() -> list[tuple[float, float]]:
    """The eight frame vertices: a rectangle with its corners cut at 45 deg."""
    lo, hi = content_bounds()
    cx, cy = (lo + hi) * 0.5
    a = (hi[0] - lo[0]) * 0.5 + P.OCTAGON_MARGIN
    b = (hi[1] - lo[1]) * 0.5 + P.OCTAGON_MARGIN
    if P.OCTAGON_REGULAR:
        # equal edges need a square bounding box and a chamfer of exactly
        # 2/(2+sqrt2) of the half-span: then flat and cut come out the same
        a = b = max(a, b)
        c = a * 2.0 / (2.0 + np.sqrt(2.0))
    else:
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

    # horizontals and diagonals, wherever neighbouring columns share a row.
    # Centre-aligned columns share rows around the midline, so the overlap is
    # symmetric: k from -kmin to +kmin.
    for i in range(ncol - 1):
        kmin = min(k_max(i), k_max(i + 1))
        for k in range(-kmin, kmin + 1):
            a = (i, k + k_max(i))
            b = (i + 1, k + k_max(i + 1))
            out.append((cell_xy(*a), cell_xy(*b), False))

        if P.DIAGONALS == "none":
            continue
        for k in range(-kmin, kmin):
            lo_a, hi_a = k + k_max(i), k + 1 + k_max(i)
            lo_b, hi_b = k + k_max(i + 1), k + 1 + k_max(i + 1)
            rising = (cell_xy(i, lo_a), cell_xy(i + 1, hi_b), False)
            falling = (cell_xy(i, hi_a), cell_xy(i + 1, lo_b), False)
            if P.DIAGONALS == "full":
                out.extend([rising, falling])
            else:
                out.append(rising if (i + k) % 2 == 0 else falling)

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


def summit_posts(segs: int | None = None) -> list[trimesh.Trimesh]:
    """The eleven posts that stand in the middle of the numbers.

    These belong to the NUMBER, not to the board: they are exported with the
    digits so they print in the accent colour, and a post then reads as part
    of the number it stands on rather than as another anonymous peg.
    """
    return [_post(*shield_xy(i), P.PLAQUE_T, segs=segs)
            for i in range(len(P.ROWS))]


def _numeral_shapes(segs: int | None = None):
    """(cutters, fills) for the inlaid digits.

    The digit is cut INTO the box rather than raised off it, because a piece
    seats on that box: a digit standing proud would be what the skirt rests on
    and the piece would rock. The fill is exactly the pocket, so in two
    colours it comes out flush; in one colour the pocket is simply left empty
    and reads as engraving.

    The post's footprint is kept out of both, so the post stands on solid
    plate instead of bridging over the engraving.
    """
    cutters, fills = [], []
    for i, num in enumerate(P.COLUMNS):
        x, y = shield_xy(i)
        keep_out = S.tube(x, y, P.POST_D * 0.5 + P.NUMERAL_POST_CLEAR, 0.0,
                          P.PLAQUE_T - P.NUMERAL_DEPTH - 1.0, P.PLAQUE_T + 2.0,
                          segs=segs or P.CELL_SEGS)

        def _digit(z0, thickness):
            t = S.text_solid(str(num), P.NUMERAL_SIZE, thickness,
                             weight=P.NUMERAL_FONT_WEIGHT)
            w = t.bounds[1][0] - t.bounds[0][0]
            if w > P.NUMERAL_MAX_W:
                k = P.NUMERAL_MAX_W / w
                t.apply_scale((k, k, 1.0))
            t.apply_translation((x, y, z0))
            return t

        # the cutter runs proud of the plate so its top face is not coplanar
        # with the plate's, which is where boolean engines get fussy
        cut = _digit(P.PLAQUE_T - P.NUMERAL_DEPTH, P.NUMERAL_DEPTH + 1.0)
        fill = _digit(P.PLAQUE_T - P.NUMERAL_DEPTH, P.NUMERAL_DEPTH)
        cutters.append(trimesh.boolean.difference([cut, keep_out],
                                                  engine="manifold"))
        fills.append(trimesh.boolean.difference([fill, keep_out],
                                                engine="manifold"))
    return cutters, fills


def build_board(with_numerals: bool = True, numerals_only: bool = False,
                segs: int | None = None, verbose: bool = False) -> trimesh.Trimesh:
    """Construct the board.

    numerals_only=True   the accent parts on their own: the digit fills and
                         the eleven summit posts, for a second filament
    with_numerals=True   the single-colour board -- pockets left empty, so the
                         numbers read as engraved -- with the posts fused in
    with_numerals=False  the body alone, to be paired with numerals_only
    """
    segs = segs or P.CELL_SEGS
    cutters, fills = _numeral_shapes(segs)

    if numerals_only:
        return S.union_all(fills + summit_posts(segs))

    parts: list[trimesh.Trimesh] = []
    for i, r in all_cells():
        x, y = cell_xy(i, r)
        if is_summit(i, r):
            parts.append(build_summit_box(x, y))
        else:
            parts.append(build_cell(x, y, segs=segs))

    for p0, p1, w, h, _kind in final_struts():
        parts.append(S.strut(p0, p1, w, h))

    if with_numerals:
        parts.extend(summit_posts(segs))

    if verbose:
        print(f"    fusing {len(parts)} solids ...", flush=True)
    body = S.union_all(parts)

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
