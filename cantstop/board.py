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

    Under NUMBER_PLACEMENT == "pad_below" the top row of every column steps a
    further SUMMIT_STEP outward, opening the gap the number sits in.
    """
    y = (row - k_max(col_index)) * P.PITCH_Y
    if P.NUMBER_PLACEMENT == "pad_below" and row == P.ROWS[col_index] - 1:
        y += P.SUMMIT_STEP
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
    """Centre of a column's number SHIELD, always on the column's centreline."""
    x, y = summit(col_index)
    if P.NUMBER_PLACEMENT == "above":
        return x, y + P.SHIELD_OFFSET
    if P.NUMBER_PLACEMENT == "pad_below":
        return x, y - P.SHIELD_DROP
    return x, y - P.NUMBER_DROP


def numeral_xy(col_index: int) -> tuple[float, float]:
    """Centre of the DIGIT itself, which need not be the shield's centre.

    Under "pad_below" the shield reaches further up than the digit does, so it
    can fuse straight onto the summit pad while the digit sits low enough to
    stay out of the top chain.
    """
    x, y = summit(col_index)
    if P.NUMBER_PLACEMENT == "above":
        return shield_xy(col_index)
    return x, y - P.NUMBER_DROP


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
        xs += [x - r, x + r]
        ys += [y - r, y + r]
    for i in range(len(P.ROWS)):
        x, y = shield_xy(i)
        xs += [x - P.PLAQUE_W / 2, x + P.PLAQUE_W / 2]
        ys += [y - P.PLAQUE_H / 2, y + P.PLAQUE_H / 2]
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
    # The top vertical is skipped when the number lives below the summit,
    # because it would run straight down the column's centreline and print a
    # bar across the digit. _necks() reconnects the summit instead.
    skip_top = P.NUMBER_PLACEMENT in ("pad_below", "around")
    for i in range(ncol):
        last = P.ROWS[i] - 2
        for r in range(P.ROWS[i] - 1):
            if skip_top and r == last:
                continue
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


def numeral_half_width() -> float:
    """Half the widest a digit may be, given what has to pass beside it."""
    if P.NUMBER_PLACEMENT == "around":
        # legs flank the digit, so it has to fit between them
        return min(P.NUMERAL_MAX_W,
                   2 * (P.NECK_LEG_DX - P.STRUT_W / 2 - 0.5)) / 2
    return P.NUMERAL_MAX_W / 2


def _necks() -> list[tuple[tuple, tuple]]:
    """Whatever reconnects a summit pad to the column below it.

    "above"      the summit is part of the lattice already; the neck runs the
                 other way, on up to the shield beyond it.
    "pad_below"  the shield sits in the gap the summit step opens, so one
                 strut comes up the centreline and stops in the band of
                 shield BELOW the digit.
    "around"     there is no band to stop in, so two legs flank the digit
                 instead, and the digit is narrowed to fit between them.
    """
    out = []
    up = np.array([0.0, 1.0])

    if P.NUMBER_PLACEMENT == "above":
        for i in range(len(P.ROWS)):
            start = np.asarray(summit(i), dtype=float) + up * P.WELD_R
            end = _rect_exit(shield_xy(i), P.PLAQUE_W, P.PLAQUE_H, -up, inset=2.0)
            out.append((tuple(start), tuple(end)))
        return out

    for i in range(len(P.ROWS)):
        x, y_below = cell_xy(i, P.ROWS[i] - 2)
        _, sy = shield_xy(i)
        shield_bottom = sy - P.PLAQUE_H / 2
        if P.NUMBER_PLACEMENT == "pad_below":
            out.append(((x, y_below + P.WELD_R), (x, shield_bottom + 2.5)))
        else:
            for dx in (-P.NECK_LEG_DX, P.NECK_LEG_DX):
                out.append(((x + dx, y_below), (x + dx, sy + P.PLAQUE_H / 2)))
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
        if P.NUMBER_PLACEMENT == "above":
            start = _rect_exit(shield_xy(i), P.PLAQUE_W, P.PLAQUE_H, d, inset=2.0)
        else:
            start = sp + d * P.WELD_R
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

    for p0, p1 in _necks():
        out.append((p0, p1, P.STRUT_W, P.STRUT_H, "neck"))

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

def build_cell(cx: float, cy: float, segs: int | None = None) -> trimesh.Trimesh:
    """One board cell: a pad with a post standing on it.

    A solid of revolution, so there is no boolean and no hole to protect. The
    pad's top face is the seat; the post only locates.
    """
    rp = P.PAD_OD * 0.5
    rq = P.POST_D * 0.5
    c = P.POST_CHAMFER
    top = P.PAD_H + P.POST_H
    prof = [
        (0.0, 0.0),
        (rp, 0.0),            # underside, out to the rim
        (rp, P.PAD_H),        # up the pad
        (rq, P.PAD_H),        # in across the seating face
        (rq, top - c),        # up the post
        (rq - c, top),        # 45 deg lead-in so a socket finds it
        (0.0, top),
    ]
    m = S.lathe(prof, segs=segs or P.CELL_SEGS)
    m.apply_translation((cx, cy, 0.0))
    return m


def build_board(with_numerals: bool = True, numerals_only: bool = False,
                segs: int | None = None, verbose: bool = False) -> trimesh.Trimesh:
    """Construct the board.

    with_numerals=True   the single-colour board, digits fused in
    numerals_only=True   just the digits, for loading as a second material
    """
    segs = segs or P.CELL_SEGS
    numerals = _build_numerals()
    if numerals_only:
        return S.union_all(numerals)

    parts: list[trimesh.Trimesh] = []

    for i, r in all_cells():
        parts.append(build_cell(*cell_xy(i, r), segs=segs))

    for p0, p1, w, h, _kind in final_struts():
        parts.append(S.strut(p0, p1, w, h))

    for i in range(len(P.ROWS)):
        x, y = shield_xy(i)
        parts.append(S.rounded_plate(x, y, P.PLAQUE_W, P.PLAQUE_H,
                                     P.PLAQUE_T, P.PLAQUE_FILLET))

    if with_numerals:
        parts.extend(numerals)

    if verbose:
        print(f"    fusing {len(parts)} solids ...", flush=True)
    return S.union_all(parts)


def _build_numerals() -> list[trimesh.Trimesh]:
    """The embossed column numbers, as separate solids sitting on the shields."""
    out = []
    for i, num in enumerate(P.COLUMNS):
        x, y = numeral_xy(i)
        t = S.text_solid(str(num), P.NUMERAL_SIZE, P.NUMERAL_EMBOSS,
                         weight=P.NUMERAL_FONT_WEIGHT)
        max_w = 2 * numeral_half_width()
        w = t.bounds[1][0] - t.bounds[0][0]
        if w > max_w:                    # 10, 11 and 12 are wider than a shield
            k = max_w / w
            t.apply_scale((k, k, 1.0))
        # overlap the shield by 0.2 mm so the union welds them
        t.apply_translation((x, y, P.PLAQUE_T - 0.2))
        out.append(t)
    return out


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
