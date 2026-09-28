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


def shield_dir(col_index: int) -> np.ndarray:
    """Unit direction a column's number shield leans, out from the middle.

    Clamped to SHIELD_MAX_TILT off vertical. Unclamped, columns 2 and 12 lean
    almost flat sideways and stretch the board wider than it is tall, which
    spoils the octagon for no gain in legibility.
    """
    d = np.asarray(summit(col_index), dtype=float) - lattice_centre()
    n = np.linalg.norm(d)
    if n < 1e-9:
        return np.array([0.0, 1.0])
    d = d / n
    tilt = np.arctan2(abs(d[0]), max(d[1], 1e-9))
    limit = np.radians(P.SHIELD_MAX_TILT)
    if tilt > limit:
        d = np.array([np.sign(d[0]) * np.sin(limit), np.cos(limit)])
    return d


def shield_xy(col_index: int) -> tuple[float, float]:
    p = np.asarray(summit(col_index), dtype=float) \
        + shield_dir(col_index) * P.SHIELD_OFFSET
    return float(p[0]), float(p[1])


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
    r = P.COLLAR_OD * 0.5
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
    c = P.OCTAGON_CHAMFER * min(a, b)
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


def _necks() -> list[tuple[tuple, tuple]]:
    """The short stand-off from each summit ring out to its number shield."""
    out = []
    for i in range(len(P.ROWS)):
        d = shield_dir(i)
        start = np.asarray(summit(i), dtype=float) + d * P.WELD_R
        end = _rect_exit(shield_xy(i), P.PLAQUE_W, P.PLAQUE_H, -d, inset=2.0)
        out.append((tuple(start), tuple(end)))
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
        # out from the number shield, carrying on the way the shield leans
        sc = np.asarray(shield_xy(i), dtype=float)
        d = shield_dir(i)
        start = _rect_exit(sc, P.PLAQUE_W, P.PLAQUE_H, d, inset=2.0)
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

def build_board(with_numerals: bool = True, numerals_only: bool = False,
                segs: int | None = None, verbose: bool = False) -> trimesh.Trimesh:
    """Construct the board.

    with_numerals=True   the single-colour board, digits fused in
    numerals_only=True   just the digits, for loading as a second material
    """
    segs = segs or P.COLLAR_SEGS
    numerals = _build_numerals()
    if numerals_only:
        return S.union_all(numerals)

    parts: list[trimesh.Trimesh] = []

    for i, r in all_cells():
        x, y = cell_xy(i, r)
        parts.append(S.tube(
            x, y,
            P.COLLAR_OD * 0.5, P.COLLAR_BORE * 0.5,
            0.0, P.COLLAR_H,
            segs=segs, top_chamfer=P.COLLAR_CHAMFER,
        ))

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
        x, y = shield_xy(i)
        t = S.text_solid(str(num), P.NUMERAL_SIZE, P.NUMERAL_EMBOSS,
                         weight=P.NUMERAL_FONT_WEIGHT)
        w = t.bounds[1][0] - t.bounds[0][0]
        if w > P.NUMERAL_MAX_W:          # 10, 11 and 12 are wider than a shield
            k = P.NUMERAL_MAX_W / w
            t.apply_scale((k, k, 1.0))
        # overlap the shield by 0.2 mm so the union welds them
        t.apply_translation((x, y, P.PLAQUE_T - 0.2))
        out.append(t)
    return out


# ---------------------------------------------------------------------------
# playing pieces
# ---------------------------------------------------------------------------

def _piece_profile(body_profile, body_h: float) -> list[tuple[float, float]]:
    """Closed (r, z) profile for a piece: pin, body, blind socket.

    Wound counter-clockwise, starting on the axis at the bottom:
    out along the underside, up the outside, in across the top face, down
    into the socket, and back to the axis.
    """
    rp = P.PEG_PIN_D * 0.5
    rs = P.PEG_SOCKET_D * 0.5
    c = P.PEG_PIN_CHAMFER
    sc = P.PEG_SOCKET_CHAMFER
    z_shoulder = P.PEG_PIN_H
    z_top = z_shoulder + body_h
    z_socket_floor = z_top - P.PEG_SOCKET_DEPTH

    prof = [
        (0.0, 0.0),
        (rp - c, 0.0),          # underside, less the lead-in chamfer
        (rp, c),                # 45 deg chamfer so the pin finds the hole
        (rp, z_shoulder),       # up the pin
    ]
    prof += [(r, z_shoulder + dz) for r, dz in body_profile]
    prof += [
        (rs + sc, z_top),       # in across the top rim
        (rs, z_top - sc),       # chamfered socket mouth
        (rs, z_socket_floor),   # down the socket
        (0.0, z_socket_floor),  # socket floor
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
    """Five collars at bores either side of nominal, on one small bar.

    Same collar height, same wall thickness and same bore geometry as the real
    board, because a fit test only transfers if the part around the hole
    cools the same way. Each collar is labelled with the second decimal of its
    bore: the one marked 4 is 6.40 mm.
    """
    segs = segs or P.COLLAR_SEGS
    pitch = P.COLLAR_OD + 5.0
    parts = []
    n = len(P.FIT_TEST_BORES)
    x0 = -(n - 1) * pitch * 0.5

    for k, bore in enumerate(P.FIT_TEST_BORES):
        x = x0 + k * pitch
        parts.append(S.tube(x, 0.0, P.COLLAR_OD * 0.5, bore * 0.5,
                            0.0, P.COLLAR_H, segs=segs,
                            top_chamfer=P.COLLAR_CHAMFER))
        digit = str(int(round(bore * 100)) % 10)     # 6.40 -> "4"
        t = S.text_solid(digit, 5.0, 1.0, weight="bold")
        t.apply_translation((x, -P.COLLAR_OD * 0.5 - 5.0, P.FIT_COUPON_T - 0.2))
        parts.append(t)

    bar_y0 = -P.COLLAR_OD * 0.5 - 9.5
    bar_y1 = P.COLLAR_OD * 0.5
    parts.append(S.rounded_plate(0.0, (bar_y0 + bar_y1) * 0.5,
                                 (n - 1) * pitch + P.COLLAR_OD,
                                 bar_y1 - bar_y0, P.FIT_COUPON_T, 2.0))
    return S.union_all(parts)
