"""The cantstop board, playing pieces and fit-test coupon.

Everything here is derived from params.py. Nothing is drawn by hand.
"""

from __future__ import annotations

import numpy as np
import trimesh

import params as P
import solids as S


# ---------------------------------------------------------------------------
# cell addressing
# ---------------------------------------------------------------------------

def cell_xy(col_index: int, row: int) -> tuple[float, float]:
    """Centre of the cell at (column index 0..10, row 0..n-1)."""
    return col_index * P.PITCH_X, row * P.PITCH_Y


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
        return None                      # cells too close to bridge; skip
    d /= L
    return p0 + d * r0, p1 - d * r1


# ---------------------------------------------------------------------------
# board
# ---------------------------------------------------------------------------

def _lattice_struts() -> list[tuple[tuple, tuple, bool]]:
    """Every strut in the lattice as (p0, p1, is_frame), centre-to-centre."""
    out = []
    ncol = len(P.ROWS)

    # verticals, within a column. The outermost two columns carry the left and
    # right edges of the pyramid, so they run at frame section.
    for i in range(ncol):
        edge = (i == 0 or i == ncol - 1)
        for r in range(P.ROWS[i] - 1):
            out.append((cell_xy(i, r), cell_xy(i, r + 1), edge))

    # horizontals, between neighbouring columns wherever both have that row
    for i in range(ncol - 1):
        for r in range(min(P.ROWS[i], P.ROWS[i + 1])):
            out.append((cell_xy(i, r), cell_xy(i + 1, r), False))

    # diagonal bracing: this is what stops the lattice folding up like a
    # parallelogram. One per quad, flipping direction each quad, gives most of
    # the stiffness of full X-bracing for half the plastic.
    if P.DIAGONALS != "none":
        for i in range(ncol - 1):
            for r in range(min(P.ROWS[i], P.ROWS[i + 1]) - 1):
                rising = (cell_xy(i, r), cell_xy(i + 1, r + 1), False)
                falling = (cell_xy(i, r + 1), cell_xy(i + 1, r), False)
                if P.DIAGONALS == "full":
                    out.extend([rising, falling])
                else:
                    out.append(rising if (i + r) % 2 == 0 else falling)

    # the stepped top chain, tying each column's summit to its neighbour's.
    # This closes the perimeter and is why the pyramid holds its shape.
    for i in range(ncol - 1):
        out.append((cell_xy(i, P.ROWS[i] - 1), cell_xy(i + 1, P.ROWS[i + 1] - 1), True))

    return out


def final_struts() -> list[tuple[tuple, tuple, float, float, str]]:
    """Every strut actually built, trimmed, as (p0, p1, width, height, kind).

    `kind` is "lattice" (both ends land in a collar), "rail" or "drop"
    (ends land on the rail or a plaque instead).

    build_board() consumes this list verbatim, so a test that measures these
    is measuring the real board rather than re-deriving it and hoping.
    """
    out = []
    for p0, p1, is_frame in _lattice_struts():
        t = _trim(p0, p1, P.WELD_R, P.WELD_R)
        if t is None:
            continue
        w, h = (P.FRAME_W, P.FRAME_H) if is_frame else (P.STRUT_W, P.STRUT_H)
        out.append((tuple(t[0]), tuple(t[1]), w, h, "lattice"))

    x_left = cell_xy(0, 0)[0] - P.COLLAR_OD * 0.5
    x_right = cell_xy(len(P.ROWS) - 1, 0)[0] + P.COLLAR_OD * 0.5
    out.append(((x_left, P.BASE_RAIL_DY), (x_right, P.BASE_RAIL_DY),
                P.BASE_RAIL_W, P.BASE_RAIL_H, "rail"))
    for i in range(len(P.ROWS)):
        x, _ = cell_xy(i, 0)
        # collar down to the base rail. This one is load-bearing in the
        # literal sense: without it the rail and all eleven plaques are a
        # second, detached body and the board is not one solid.
        out.append(((x, -P.WELD_R), (x, P.BASE_RAIL_DY),
                    P.STRUT_W, P.STRUT_H, "drop"))
        # rail down to the plaque, on two legs either side of the number so
        # nothing is printed across the digit
        for dx in (-P.PLAQUE_DROP_DX, P.PLAQUE_DROP_DX):
            out.append(((x + dx, P.BASE_RAIL_DY + 2.0),
                        (x + dx, P.PLAQUE_DROP_Y), P.STRUT_W, P.STRUT_H, "drop"))
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


def build_board(with_numerals: bool = True, numerals_only: bool = False,
                segs: int | None = None, verbose: bool = False) -> trimesh.Trimesh:
    """Construct the board.

    with_numerals=True   the single-colour board, digits fused in
    numerals_only=True   just the digits, for loading as a second material
    """
    segs = segs or P.COLLAR_SEGS
    parts: list[trimesh.Trimesh] = []

    numerals = _build_numerals()
    if numerals_only:
        return S.union_all(numerals)

    # --- collars -----------------------------------------------------------
    for i, r in all_cells():
        x, y = cell_xy(i, r)
        parts.append(S.tube(
            x, y,
            P.COLLAR_OD * 0.5, P.COLLAR_BORE * 0.5,
            0.0, P.COLLAR_H,
            segs=segs, top_chamfer=P.COLLAR_CHAMFER,
        ))

    # --- lattice, base rail and the drops onto it -------------------------
    for p0, p1, w, h, _kind in final_struts():
        parts.append(S.strut(p0, p1, w, h))

    # --- number plaques ----------------------------------------------------
    for i in range(len(P.ROWS)):
        x, _ = cell_xy(i, 0)
        parts.append(S.rounded_plate(x, P.PLAQUE_DY, P.PLAQUE_W, P.PLAQUE_H,
                                     P.PLAQUE_T, P.PLAQUE_FILLET))

    if with_numerals:
        parts.extend(numerals)

    if verbose:
        print(f"    fusing {len(parts)} solids ...", flush=True)
    return S.union_all(parts)


def _build_numerals() -> list[trimesh.Trimesh]:
    """The embossed column numbers, as separate solids sitting on the plaques."""
    out = []
    max_w = 2 * P.PLAQUE_DROP_DX - 4.0   # clear of both drop legs
    for i, num in enumerate(P.COLUMNS):
        x, _ = cell_xy(i, 0)
        t = S.text_solid(str(num), P.NUMERAL_SIZE, P.NUMERAL_EMBOSS,
                         weight=P.NUMERAL_FONT_WEIGHT)
        # two-digit numbers are wider than the plaque allows; shrink to fit
        w = t.bounds[1][0] - t.bounds[0][0]
        if w > max_w:
            k = max_w / w
            t.apply_scale((k, k, 1.0))
        # drop it onto the plaque face, overlapping 0.2 mm so the union welds
        t.apply_translation((x, P.PLAQUE_DY, P.PLAQUE_T - 0.2))
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


def build_plate(mesh: trimesh.Trimesh, count: int, spacing: float = 16.0,
                per_row: int = 6) -> trimesh.Trimesh:
    """Arrange `count` copies in a grid, ready to drop straight into a slicer."""
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
        t.apply_translation((x, -P.COLLAR_OD * 0.5 - 5.0, P.PLAQUE_T - 0.2))
        parts.append(t)

    # backing bar, tying the collars together and carrying the labels
    bar_y0 = -P.COLLAR_OD * 0.5 - 9.5
    bar_y1 = P.COLLAR_OD * 0.5
    parts.append(S.rounded_plate(0.0, (bar_y0 + bar_y1) * 0.5,
                                 (n - 1) * pitch + P.COLLAR_OD,
                                 bar_y1 - bar_y0, P.PLAQUE_T, 2.0))
    return S.union_all(parts)
