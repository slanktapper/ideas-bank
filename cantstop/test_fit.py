#!/usr/bin/env python3
"""Assertions about the design, run before you spend ten hours of printer time.

    python3 test_fit.py

These are not unit tests of the code so much as design rules. Editing
params.py is the whole point of this project, and most of the ways to get it
wrong are silent: a socket that swallows its post, a strut standing proud of a
seating face, a wall thinned to nothing, a board that has quietly grown past
the bed, a lattice that has become two detached bodies, a raised lip that has
crept in far enough to land on a pad, a number you cannot read once a piece is
sitting on it. Each one costs a print to discover and nothing to check.

The board has two styles and the checks follow whichever params.py selects.
Some rules only exist for one of them -- there are no struts to keep clear of
a number box on a slab, and no lip to measure on a lattice -- so those are
gated rather than deleted. Everything about the ladder, the post/socket
interface, the pieces and the octagon is common to both and always runs.
"""

from __future__ import annotations

import sys

import numpy as np

import trimesh

import board as B
import params as P
import solids as S

FAILS: list[str] = []
CHECKS = 0

SLAB = P.BOARD_STYLE == "slab"
SEAT_Z = B.seat_z()          # height of every seating face, whichever style


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    mark = "ok  " if ok else "FAIL"
    print(f"  [{mark}] {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def _apothems(poly, ctr) -> list[float]:
    """Perpendicular distance from the centre to each edge of a polygon."""
    out = []
    for j in range(len(poly)):
        a, b = poly[j], poly[(j + 1) % len(poly)]
        e = b - a
        v = ctr - a
        out.append(abs(e[0] * v[1] - e[1] * v[0])
                   / float(np.linalg.norm(e)))
    return out


def slab_checks(brd, poly, ctr, skirt_r):
    """The solid plate and its raised lip.

    The lip is made by scaling the outline about its centre, which is only an
    even inset because the octagon is regular -- every edge shares one
    apothem. If OCTAGON_REGULAR is ever turned off, or the sizing loses its
    equal edges, the scale quietly becomes a wider lip on the long sides than
    the short ones, and nothing else in the build would notice.

    The other thing worth checking is what the lip is standing on. It grows
    INWARD from the outline, so the outline has to have been pushed out to
    make room for it; get that wrong and the lip lands on the outermost pads
    of columns 2 and 12 and a piece cannot seat.
    """
    from shapely.geometry import Point, Polygon as Poly2D

    print("\nthe slab and its raised lip")
    plate = B.slab_plate()
    check("the plate is one watertight solid",
          plate.is_watertight and plate.is_winding_consistent
          and plate.body_count == 1,
          f"{len(plate.faces)} triangles, {plate.body_count} body")
    check("the plate is the thickness asked for and the lip stands on top "
          "of it",
          abs(plate.bounds[0][2]) < 1e-6
          and abs(plate.bounds[1][2] - (P.SLAB_T + P.RIM_H)) < 1e-6,
          f"{P.SLAB_T:.1f} mm plate + {P.RIM_H:.2f} mm lip = "
          f"{plate.bounds[1][2]:.2f} mm")
    check("pieces seat on the top of the plate",
          abs(SEAT_Z - P.SLAB_T) < 1e-9,
          f"seat at z={SEAT_Z:.2f}, posts to z={SEAT_Z + P.POST_H:.2f}")
    check("the lip is raised by exactly as much as the numbers are sunk",
          abs(P.RIM_H - P.NUMERAL_DEPTH) < 1e-9,
          f"lip {P.RIM_H:.2f} mm up, numerals {P.NUMERAL_DEPTH:.2f} mm down")

    # the same inset slab_plate() uses, rebuilt here so the check is on the
    # construction and not on a number copied out of it
    apothem = max(abs(np.asarray(poly) - ctr).max(axis=1))
    k = (apothem - P.RIM_W) / apothem
    inner = (np.asarray(poly) - ctr) * k + ctr
    widths = [o - i for o, i in zip(_apothems(poly, ctr),
                                    _apothems(inner, ctr))]
    check("the lip is the same width the whole way round",
          max(widths) - min(widths) < 0.05 and abs(min(widths) - P.RIM_W) < 0.05,
          f"{min(widths):.2f}-{max(widths):.2f} mm against a {P.RIM_W:.0f} mm "
          f"target, on all eight edges")

    ring = Poly2D([tuple(q) for q in inner]).exterior
    pad_gap = min(ring.distance(Point(*q)) for q in B.content_points())
    check("the lip clears every pad and every number box",
          Poly2D([tuple(q) for q in inner]).contains(
              Poly2D([tuple(q) for q in B.content_points()]).convex_hull)
          and pad_gap >= P.RIM_CLEAR - 0.05,
          f"{pad_gap:.1f} mm of flat between the lip and the nearest content, "
          f"against a {P.RIM_CLEAR:.0f} mm target")

    face = Poly2D([tuple(q) for q in inner])
    off = []
    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            if not face.contains(Point(cx + skirt_r * np.cos(a),
                                       cy + skirt_r * np.sin(a))):
                off.append((P.COLUMNS[i], r))
    check(f"all {sum(P.ROWS)} skirts land on flat plate, none on the lip",
          not off, "16 points round every skirt" if not off
          else f"{sorted(set(off))} overhang")

    # And the lip has to actually BE a lip in the finished mesh: solid in its
    # own band, open air immediately inside it. A plate that came out
    # uniformly SLAB_T + RIM_H thick would pass every measurement above.
    z = P.SLAB_T + P.RIM_H / 2
    on_lip, in_field = [], []
    pts = np.asarray(poly, dtype=float)
    for j in range(len(pts)):
        mid = (pts[j] + pts[(j + 1) % len(pts)]) / 2
        nrm = (ctr - mid) / np.linalg.norm(ctr - mid)
        on_lip.append(np.append(mid + nrm * (P.RIM_W / 2), z))
        in_field.append(np.append(mid + nrm * (P.RIM_W + P.RIM_CLEAR / 2), z))
    hit = brd.contains(np.asarray(on_lip))
    miss = brd.contains(np.asarray(in_field))
    check("the lip is solid where it should be and absent where it should not",
          hit.all() and not miss.any(),
          f"{int(hit.sum())}/8 points inside the lip band, "
          f"{int(miss.sum())}/8 wrongly solid just inside it")


def stub_checks(brd, accent):
    """The test-print stub: a corner of the real board, cut out of it.

    The stub is an intersection with the finished board, so almost everything
    about it is guaranteed by the board's own checks. What is not guaranteed
    is where the knife lands. Three of its four sides cut across open plate,
    and a cut line half a millimetre out shaves a post in half or leaves a
    piece's skirt hanging over a raw edge -- neither of which the board tests
    would ever see, because on the board those cells are in the middle of a
    slab.
    """
    print("\nthe test-print stub")
    (x0, y0), (x1, y1) = B.stub_box()
    cells = B.stub_cells()
    skirt = max(r for r, _ in P.PEG_BODY_PROFILE)
    post_r = P.POST_D / 2

    check("the stub keeps whole columns' worth of summits",
          sum(1 for i, r in cells if B.is_summit(i, r)) == len(P.STUB_COLUMNS),
          f"{len(cells)} cells, numbers "
          f"{[P.COLUMNS[i] for i, r in cells if B.is_summit(i, r)]}")

    sliced = []
    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        touches = (x0 - post_r < cx < x1 + post_r
                   and y0 - post_r < cy < y1 + post_r)
        whole = (x0 + post_r <= cx <= x1 - post_r
                 and y0 + post_r <= cy <= y1 - post_r)
        if touches and not whole:
            sliced.append((P.COLUMNS[i], r))
    check("no cut line shaves a post in half",
          not sliced, "every post is wholly in or wholly out"
          if not sliced else f"{sliced} are cut")

    room = min(min(B.cell_xy(i, r)[0] - x0, x1 - B.cell_xy(i, r)[0],
                   B.cell_xy(i, r)[1] - y0) for i, r in cells)
    check("every post in the stub has a whole skirt of plate under it",
          room >= skirt,
          f"tightest is {room:.2f} mm of plate against a {skirt:.2f} mm skirt")

    stub = B.build_board_stub(brd)
    stub_n = B.build_board_stub(accent)
    lo, hi = stub.bounds
    if not SLAB:
        check("the stub is a solid piece of board",
              stub.is_watertight and stub.is_winding_consistent,
              f"{len(stub.faces)} triangles, {stub.body_count} bodies")
    else:
        check("the stub is a watertight single solid",
              stub.is_watertight and stub.is_winding_consistent
              and stub.body_count == 1,
              f"{len(stub.faces)} triangles, {stub.body_count} body")
    check("the stub is the real board's full thickness, not a thin sample",
          abs((hi[2] - lo[2]) - (SEAT_Z + P.POST_H)) < 1e-6,
          f"{hi[0]-lo[0]:.0f} x {hi[1]-lo[1]:.0f} x {hi[2]-lo[2]:.1f} mm")
    check("the stub is small enough to be worth printing before the board",
          (hi[0] - lo[0]) * (hi[1] - lo[1]) < 0.06 * (P.BED_X * P.BED_Y),
          f"{(hi[0]-lo[0]) * (hi[1]-lo[1]) / 100:.0f} cm2 of bed against the "
          f"board's {284.9 * 284.9 / 100:.0f}")
    check("the stub carries the digits and their share of each post",
          len(stub_n.faces) > 0
          and abs(stub_n.bounds[1][2] - (SEAT_Z + P.POST_H)) < 1e-6,
          "body and accent split each summit post here too")

    if SLAB:
        # One side of the stub has to be real board edge, or it tests
        # everything about the board except the lip.
        # measured off the stub's own outer edge, not off the knife: the top
        # side of the box is out in open air, and what bounds the stub there
        # is the octagon
        z = P.SLAB_T + P.RIM_H / 2
        band = np.asarray([(x, hi[1] - P.RIM_W / 2, z)
                           for x in np.linspace(lo[0] + 15, hi[0] - 15, 9)])
        check("one side of the stub is real board edge, lip and all",
              stub.contains(band).all(),
              f"{int(stub.contains(band).sum())}/9 points land in the lip "
              f"along the top edge")


def main():
    print("ladder")
    check("11 columns, numbered 2..12",
          P.COLUMNS == list(range(2, 13)) and len(P.ROWS) == 11)
    check("ladder is symmetric about 7", P.ROWS == P.ROWS[::-1], f"{P.ROWS}")
    check("7 is the longest column, 2 and 12 the shortest",
          P.ROWS[5] == max(P.ROWS) and P.ROWS[0] == P.ROWS[-1] == min(P.ROWS))
    check("row count rises strictly towards the middle",
          all(P.ROWS[i] < P.ROWS[i + 1] for i in range(5)), f"{P.ROWS[:6]}")
    check("every column has an odd row count, so centring lands on a cell",
          all(n % 2 for n in P.ROWS), f"{P.ROWS}")
    check("column shortfalls are listed outward from the middle and never "
          "go backwards",
          (len(P.COLUMN_SHORTFALL) >= int(round(
               max(B.k_max(i) for i in range(len(P.ROWS)))
               - min(B.k_max(i) for i in range(len(P.ROWS))))) + 1
           and P.COLUMN_SHORTFALL[0] == 0
           and all(P.COLUMN_SHORTFALL[k] < P.COLUMN_SHORTFALL[k + 1]
                   for k in range(len(P.COLUMN_SHORTFALL) - 1))),
          f"{[round(v) for v in P.COLUMN_SHORTFALL]} mm")
    drops = [round(B.half_height(i + 1) - B.half_height(i), 3) for i in range(5)]
    check("the lens still steps down monotonically from the middle out",
          all(d > 0 for d in drops),
          f"drops of {drops} mm, in units of a {P.PITCH_Y:.0f} mm box: "
          f"{[round(d / P.PITCH_Y, 2) for d in drops]}")
    check("no column's cells are spread so far apart they stop reading as a "
          "column",
          max(B.row_pitch(i) for i in range(len(P.ROWS))) <= 3 * P.PITCH_Y,
          f"widest is {max(B.row_pitch(i) for i in range(len(P.ROWS))):.0f} mm "
          f"in column {P.COLUMNS[max(range(len(P.ROWS)), key=B.row_pitch)]}")

    check("columns are centred on a shared midline",
          all(abs(B.cell_xy(i, 0)[1] + B.summit(i)[1] - P.SUMMIT_STEP) < 1e-9
              for i in range(len(P.ROWS))),
          "bottom and summit equal and opposite, plus the summit step")

    print("\nthe post/socket interface  (male-up: board, then every piece)")
    board_clear = P.PEG_SOCKET_D - P.POST_D
    piece_clear = P.PEG_SOCKET_D - P.PEG_POST_D
    check("socket clears the board's post", 0.25 <= board_clear <= 0.75,
          f"{board_clear:.2f} mm diametral")
    check("socket clears the post of a piece below it",
          0.25 <= piece_clear <= 0.75, f"{piece_clear:.2f} mm diametral")
    check("socket is deeper than a post is long, so the SKIRT seats and "
          "stack height is exact",
          P.PEG_SOCKET_DEPTH > max(P.POST_H, P.PEG_POST_H) + 0.2,
          f"socket {P.PEG_SOCKET_DEPTH:.2f} vs posts "
          f"{P.POST_H:.2f}/{P.PEG_POST_H:.2f}")

    skirt_r = max(r for r, _ in P.PEG_BODY_PROFILE)
    if not SLAB:
        check("the skirt lands on the pad, not off the edge of it",
              skirt_r < P.PAD_OD / 2,
              f"skirt r{skirt_r:.2f} inside pad r{P.PAD_OD/2:.2f}")
    check("the seat is a wide annulus, not a rim",
          skirt_r - P.POST_D / 2 >= 3.0,
          f"{P.POST_D/2:.2f} to {skirt_r:.2f} mm contact ring")

    print("\nprintability")
    if not SLAB:
        check("struts stay below every seating face, so nothing fouls a piece "
              "and no strut can touch a post",
              max(P.STRUT_H, P.OCTAGON_SPOKE_H) < P.PAD_H,
              f"struts {max(P.STRUT_H, P.OCTAGON_SPOKE_H):.2f} vs pad "
              f"{P.PAD_H:.2f}")
        check("number shields sit flush with the pads",
              P.PLAQUE_T <= P.PAD_H,
              f"shield {P.PLAQUE_T:.2f} vs pad {P.PAD_H:.2f}")
    apex_rise = P.PEG_SOCKET_D / 2
    check("the socket roof is a self-supporting cone, not a bridge",
          apex_rise >= P.PEG_SOCKET_D / 2 - 1e-9,
          f"45 deg over a {P.PEG_SOCKET_D:.2f} mm opening")

    print("\nwall thickness")
    rs = P.PEG_SOCKET_D / 2
    for name, prof in [("marker", P.PEG_BODY_PROFILE),
                       ("runner", P.RUNNER_BODY_PROFILE)]:
        walls = [r - rs for r, dz in prof if dz <= P.PEG_SOCKET_DEPTH]
        check(f"{name}: wall between socket and outside stays printable",
              min(walls) >= 1.20,
              f"min {min(walls):.2f} mm (~{min(walls)/0.42:.1f} perimeters)")

    print("\nneighbours do not touch")
    for axis, pitch in [("along a row", P.PITCH_X), ("up a column", P.PITCH_Y)]:
        check(f"pieces clear each other {axis}", pitch - 2 * skirt_r >= 3.0,
              f"{pitch - 2*skirt_r:.2f} mm gap")
    if SLAB:
        check("posts clear each other up a column", P.PITCH_Y - P.POST_D >= 3.0,
              f"{P.PITCH_Y - P.POST_D:.2f} mm gap; on a slab the plate is the "
              f"pad, so only the posts stand apart")
    else:
        check("pads clear each other up a column", P.PITCH_Y - P.PAD_OD >= 3.0,
              f"{P.PITCH_Y - P.PAD_OD:.2f} mm gap")

    print("\ngeometry (building meshes)")
    marker = B.build_marker()
    runner = B.build_runner()
    brd = B.build_board()
    coupon = B.build_fit_coupon()

    for name, m in [("board", brd), ("marker", marker),
                    ("runner", runner), ("fit coupon", coupon)]:
        check(f"{name} is a watertight single solid",
              m.is_watertight and m.is_winding_consistent and m.body_count == 1,
              f"{len(m.faces)} triangles, {m.body_count} body")
        check(f"{name} sits on the bed at z=0 and needs no raft",
              abs(m.bounds[0][2]) < 1e-6, f"min z = {m.bounds[0][2]:.4f}")

    lo, hi = brd.bounds
    w, h, t = hi - lo
    check("board fits the print bed",
          w <= P.BED_X and h <= P.BED_Y and t <= P.BED_Z,
          f"{w:.1f} x {h:.1f} x {t:.1f} mm in "
          f"{P.BED_X:.0f} x {P.BED_Y:.0f} x {P.BED_Z:.0f}")
    check("board keeps a margin off the bed edge",
          P.BED_X - w >= 10 and P.BED_Y - h >= 10,
          f"{P.BED_X - w:.0f} mm spare in X, {P.BED_Y - h:.0f} mm in Y")

    print("\nstacking, measured on the real meshes")
    heights = []
    for lvl in range(3):
        m = marker.copy()
        m.apply_translation((0, 0, SEAT_Z + lvl * P.PEG_BODY_H))
        heights.append(m.bounds[1][2])
    steps = np.diff(heights)
    check("every stacked piece adds the same height",
          np.allclose(steps, P.PEG_BODY_H, atol=1e-6),
          f"{np.round(steps, 3).tolist()} mm")
    check("three stacked pieces stay inside a sane table height",
          heights[-1] < 60, f"{heights[-1]:.1f} mm tall")
    check("a post never bottoms out in the socket above it",
          P.PEG_SOCKET_DEPTH - P.PEG_POST_H > 0.2,
          f"{P.PEG_SOCKET_DEPTH - P.PEG_POST_H:.2f} mm of air above the post")

    print("\nseating faces are actually clear in the finished mesh")
    # A piece's skirt has to land on an unobstructed annulus. Probe just above
    # every pad, out where the skirt sits, and confirm nothing -- strut, spoke,
    # shield or digit -- is in the way.
    probes = []
    zs = [SEAT_Z + 0.4, SEAT_Z + 1.5]
    rr = np.linspace(P.POST_D / 2 + 0.4, skirt_r - 0.2, 3)
    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        for a in np.linspace(0, 2 * np.pi, 12, endpoint=False):
            for rad in rr:
                for z in zs:
                    probes.append((cx + rad * np.cos(a), cy + rad * np.sin(a), z))
    inside = brd.contains(np.asarray(probes))
    check(f"all {sum(P.ROWS)} cells have a clear seat",
          not inside.any(),
          f"{len(probes)} probe points, {int(inside.sum())} obstructed")

    print("\ncolumn numbers")
    struts = [] if SLAB else B.final_struts()
    check("every number is in line with its column, not off to the side",
          all(abs(B.numeral_xy(i)[0] - B.summit(i)[0]) < 1e-9
              for i in range(len(P.ROWS))),
          "digit x == column x for all 11")
    check("the digit and the post share the box's centre",
          all(B.numeral_xy(i) == B.summit(i) for i in range(len(P.ROWS))),
          "box, digit and post on one centre")

    hw, hh = P.NUMERAL_MAX_W / 2, P.NUMERAL_SIZE / 2
    check("every digit fits inside its box",
          hw + 1.0 <= P.PLAQUE_W / 2 and hh + 1.0 <= P.PLAQUE_H / 2,
          f"digit {2*hw:.0f} x {2*hh:.0f} in a box "
          f"{P.PLAQUE_W:.0f} x {P.PLAQUE_H:.0f}")
    skirt = max(r for r, _ in P.PEG_BODY_PROFILE)
    sep = np.inf
    for i in range(len(P.ROWS)):
        for j in range(i + 1, len(P.ROWS)):
            d = np.abs(np.asarray(B.summit(i)) - np.asarray(B.summit(j))) \
                - np.array([P.PLAQUE_W, P.PLAQUE_H])
            sep = min(sep, d.max())
    check("neighbouring summit boxes stand apart",
          sep >= 3.0,
          f"{sep:.1f} mm; the middle columns step down by a quarter of a box, "
          f"so the summits run in a shallow staircase and crowd easily")
    check("a piece fits on the box it has to stand on",
          2 * skirt <= min(P.PLAQUE_W, P.PLAQUE_H),
          f"piece {2*skirt:.1f} mm on a {P.PLAQUE_W:.0f} x "
          f"{P.PLAQUE_H:.0f} mm box")
    plate_t = P.SLAB_T if SLAB else P.PLAQUE_T
    check("the digit is inlaid, not embossed, so a piece cannot rock on it",
          0 < P.NUMERAL_DEPTH < plate_t - 1.0,
          f"{P.NUMERAL_DEPTH:.2f} mm deep in a {plate_t:.2f} mm plate")

    # THE LEGIBILITY MECHANISM. The post stands in the middle of the digit,
    # so the only question is its colour -- and the answer is both, split by
    # the glyph itself. Whatever orange the pocket gives up under the post,
    # the post gives back on its own top face, so from directly above the
    # number is whole. A post in one flat colour loses a sixth of an 8 and
    # takes its waist with it.
    accent = B.build_board(numerals_only=True)
    check("the accent part reaches the tops of the posts",
          abs(accent.bounds[1][2] - (SEAT_Z + P.POST_H)) < 1e-6,
          f"z={accent.bounds[1][2]:.2f}; the digit is carried up through "
          f"each post, not stopped at the plate")
    check("the board body still carries the rest of every post",
          abs(B.build_board(with_numerals=False).bounds[1][2]
              - (SEAT_Z + P.POST_H)) < 1e-6,
          "body and accent split each post between them")

    def _vol(m):
        # an empty boolean result has no volume, and trimesh reports NaN
        return float(m.volume) if len(m.faces) else 0.0

    worst_gap, worst_num, untouched = 0.0, None, []
    for i, num in enumerate(P.COLUMNS):
        x, y = B.numeral_xy(i)
        glyph = B._digit_solid(num, x, y, 0.0, 1.0)
        column = S.tube(x, y, P.POST_D / 2 + P.NUMERAL_POST_CLEAR, 0.0,
                        -1.0, 2.0, segs=96)
        # orange the pocket gives up because the post's footprint is cut out
        given_up = _vol(glyph) - _vol(trimesh.boolean.difference(
            [glyph, column], engine="manifold"))
        # orange the post hands back on its own face
        handed_back = _vol(trimesh.boolean.intersection(
            [column, B._digit_solid(num, x, y, 0.0, 1.0)], engine="manifold"))
        if given_up < 0.05:
            untouched.append(num)          # the post misses this glyph entirely
            continue
        gap = abs(given_up - handed_back) / given_up
        if gap > worst_gap:
            worst_gap, worst_num = gap, num
    check("every square millimetre the post covers, it hands back in the "
          "number's colour",
          worst_gap < 0.01,
          f"worst mismatch {100*worst_gap:.3f}% (the {worst_num}); "
          f"{sorted(untouched)} are missed by their post entirely")

    # Only members taller than a box matter: a strut is 3.4 mm and a box is
    # 4.0 mm thick, so anything running under one is buried inside it.
    tall = [s for s in struts if s[3] > P.PLAQUE_T] if not SLAB else []
    if tall:
        bx = np.linspace(-P.PLAQUE_W / 2, P.PLAQUE_W / 2, 13)
        by = np.linspace(-P.PLAQUE_H / 2, P.PLAQUE_H / 2, 15)
        clear, clear_col = np.inf, None
        for i in range(len(P.ROWS)):
            sx, sy = B.numeral_xy(i)
            dd = min(B.strut_distance_to((sx + dx, sy + dy), p0, p1, w_)
                     for dx in bx for dy in by
                     for p0, p1, w_, _h, _k in tall)
            if dd < clear:
                clear, clear_col = dd, P.COLUMNS[i]
        check("nothing standing proud of a box goes anywhere near one",
              clear > 1.0,
              f"{len(tall)} struts taller than {P.PLAQUE_T:.1f} mm (the "
              f"octagon); nearest is {clear:.1f} mm off column "
              f"{clear_col}'s box")

    if struts:
        print("\nthe board is symmetric")
        cx = (len(P.ROWS) - 1) * P.PITCH_X / 2

        def _key(a, b_):
            return tuple(sorted([(round(a[0], 3), round(a[1], 3)),
                                 (round(b_[0], 3), round(b_[1], 3))]))

        have = {_key(s[0], s[1]) for s in struts}
        mirrored = {_key((2 * cx - s[0][0], s[0][1]),
                         (2 * cx - s[1][0], s[1][1])) for s in struts}
        # Easy to break and hard to see: the herringbone diagonals are chosen
        # by a parity, and keying that on a row INDEX rather than its position
        # makes a gap and its mirror disagree, because the two number their
        # rows differently. The board then comes out visibly handed.
        check("every strut has a mirror twin across the centreline",
              have == mirrored,
              f"{len(have)} struts, {len(have ^ mirrored)} unmatched")

    print("\nthe lens fills the frame evenly")
    lo_, hi_ = B.content_bounds()
    w_, h_ = hi_ - lo_
    check("the cell field is roughly square, so a regular octagon wraps it "
          "without wasting a side",
          abs(w_ - h_) < 0.25 * max(w_, h_), f"{w_:.1f} x {h_:.1f} mm")

    print("\nthe octagonal frame")
    poly = np.asarray(B.octagon(), dtype=float)
    edges = [float(np.linalg.norm(poly[(j + 1) % 8] - poly[j])) for j in range(8)]
    check("the frame really is an octagon (8 distinct vertices)",
          len(poly) == 8 and len(set(map(tuple, np.round(poly, 3)))) == 8)
    check("all eight edges are the same length",
          max(edges) - min(edges) < 0.05,
          f"{min(edges):.1f} mm each" if max(edges) - min(edges) < 0.05
          else f"{np.round(edges, 1).tolist()}")

    ctr = B.octagon_centre()

    def _inside(pt):
        for j in range(len(poly)):
            a, bb = poly[j], poly[(j + 1) % len(poly)]
            e = bb - a
            side = e[0] * (pt[1] - a[1]) - e[1] * (pt[0] - a[0])
            ref = e[0] * (ctr[1] - a[1]) - e[1] * (ctr[0] - a[0])
            if np.sign(side) != np.sign(ref):
                return False
        return True

    outside = []
    pr = P.PAD_OD / 2
    for i, r in B.all_cells():
        if B.is_summit(i, r):
            continue                       # checked as a box, just below
        cx, cy = B.cell_xy(i, r)
        for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            if not _inside(np.array([cx + pr * np.cos(a), cy + pr * np.sin(a)])):
                outside.append(("cell", P.COLUMNS[i], r))
    for i in range(len(P.ROWS)):
        sx, sy = B.shield_xy(i)
        for dx in (-1, 1):
            for dy in (-1, 1):
                pt = np.array([sx + dx * P.PLAQUE_W / 2,
                               sy + dy * P.PLAQUE_H / 2])
                if not _inside(pt):
                    outside.append(("box", P.COLUMNS[i], None))
    check("the frame encloses every pad and every number box",
          not outside,
          "72 pads + 11 boxes" if not outside
          else f"{sorted(set(outside))} pokes out")
    if not SLAB:
        check("the lens is braced out to the frame on every edge",
              len([s for s in struts if s[4] == "spoke"]) >= 2 * len(P.ROWS),
              f"{len([s for s in struts if s[4] == 'spoke'])} spokes")

    if SLAB:
        slab_checks(brd, poly, ctr, skirt_r)

    stub_checks(brd, accent)

    print("\ncounts")
    check("83 cells", sum(P.ROWS) == 83, f"{sum(P.ROWS)}")
    check("one marker per column per player",
          P.MARKERS_PER_PLAYER == len(P.COLUMNS))

    print()
    if FAILS:
        print(f"{len(FAILS)} of {CHECKS} checks FAILED:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print(f"all {CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
