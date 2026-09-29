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


def R_placed(mesh, dz):
    m = mesh.copy()
    m.apply_translation((0.0, 0.0, dz))
    return m


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
          and abs(plate.bounds[1][2]
                  - (P.SLAB_T + P.RIM_H - P.RIM_CAP_H)) < 1e-6
          and abs(B.rim_cap().bounds[1][2] - (P.SLAB_T + P.RIM_H)) < 1e-6,
          f"{P.SLAB_T:.1f} mm plate + {P.RIM_H - P.RIM_CAP_H:.2f} mm of lip "
          f"in the body colour + {P.RIM_CAP_H:.2f} mm of cap = "
          f"{P.SLAB_T + P.RIM_H:.2f} mm")
    check("pieces seat on the top of the plate",
          abs(SEAT_Z - P.SLAB_T) < 1e-9,
          f"seat at z={SEAT_Z:.2f}, posts to z={SEAT_Z + P.POST_H:.2f}")
    check("the lip is raised by exactly as much as the numbers are sunk",
          abs(P.RIM_H - P.NUMERAL_DEPTH) < 1e-9,
          f"lip {P.RIM_H:.2f} mm up, numerals {P.NUMERAL_DEPTH:.2f} mm down")

    # THE WHITE BORDER. The top of the lip ships with the numerals, so the
    # board has a white edge as well as white numbers. The height of that cap
    # has to fall on a layer boundary: land it mid-layer and the slicer gives
    # the layer to one colour or the other, and a 3-layer cap comes out 2 or
    # 4. Nothing downstream would notice -- the mesh is perfectly valid either
    # way -- so it is checked here.
    layers = P.RIM_CAP_H / P.LAYER_H
    check("the lip's white cap is a whole number of layers",
          abs(layers - round(layers)) < 1e-9 and 0 <= P.RIM_CAP_H <= P.RIM_H,
          f"{P.RIM_CAP_H:.2f} mm = {round(layers):g} layers at "
          f"{P.LAYER_H:.2f}, on a {P.RIM_H:.2f} mm lip")

    body_lip = P.RIM_H - P.RIM_CAP_H
    check("the two colours divide the lip and neither loses its share",
          abs(B.build_board().bounds[1][2]
              - (SEAT_Z + P.POST_H)) < 1e-6
          and abs(B.rim_cap().bounds[0][2] - (P.SLAB_T + body_lip)) < 1e-6
          and abs(B.rim_cap().bounds[1][2] - (P.SLAB_T + P.RIM_H)) < 1e-6,
          f"{body_lip:.2f} mm of lip in the body colour, then "
          f"{P.RIM_CAP_H:.2f} mm in the numbers'")

    # 0.01 mm, not 1e-6: the plate comes back through a boolean engine that
    # rounds its coordinates, so an exact comparison here fails on float noise
    # rather than on anything about the geometry.
    cap = B.rim_cap()
    over = max(abs(cap.bounds[0][:2] - plate.bounds[0][:2]).max(),
               abs(cap.bounds[1][:2] - plate.bounds[1][:2]).max())
    check("the cap sits on the lip, not over the edge of it",
          over < 0.01,
          f"same footprint as the lip below it, to {over*1000:.0f} um")

    check("the plate the body prints stops below the cap",
          abs(B.slab_plate().bounds[1][2] - (P.SLAB_T + body_lip)) < 1e-6,
          f"body lip to z={P.SLAB_T + body_lip:.2f}, then the accent's cap")

    # Measured against the rings the plate is actually built from, at the
    # midpoint of every outer edge. Not recomputed from the parameters: the
    # inset is the thing under test, and it was wrong -- a scale about the
    # centre is only an even inset on a REGULAR octagon, and this one is not
    # regular any more.
    _outer, _inner = B.rim_rings()
    ring_in = Poly2D(_inner).exterior
    op = np.asarray(_outer, dtype=float)
    widths = [ring_in.distance(Point(*(op[j] + op[(j + 1) % len(op)]) / 2))
              for j in range(len(op))]
    check("the lip is the same width the whole way round",
          max(widths) - min(widths) < 0.05 and abs(min(widths) - P.RIM_W) < 0.05,
          f"{min(widths):.2f}-{max(widths):.2f} mm against a {P.RIM_W:.0f} mm "
          f"target, on all {len(op)} edges")

    face = Poly2D(_inner)
    pad_gap = min(face.exterior.distance(Point(*q)) for q in B.content_points())
    check("the lip clears every pad, every number and every letter",
          face.contains(Poly2D([tuple(q) for q in B.content_points()]).convex_hull)
          and pad_gap >= P.RIM_CLEAR - 0.05,
          f"{pad_gap:.1f} mm of flat between the lip and the nearest content, "
          f"against a {P.RIM_CLEAR:.0f} mm target")

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


def stub_checks(brd, body_only, accent):
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

    # the assembled stub for anything about the finished part, and the body
    # alone for the one thing that has to print as a single object
    stub = B.build_board_stub(brd)
    stub_body = B.build_board_stub(body_only)
    stub_n = B.build_board_stub(accent)
    lo, hi = stub.bounds
    if not SLAB:
        check("the stub is a solid piece of board",
              stub_body.is_watertight and stub_body.is_winding_consistent,
              f"{len(stub_body.faces)} triangles, "
              f"{stub_body.body_count} bodies")
    else:
        check("the stub's body is a watertight single solid",
              stub_body.is_watertight and stub_body.is_winding_consistent
              and stub_body.body_count == 1,
              f"{len(stub_body.faces)} triangles, {stub_body.body_count} body;"
              f" the assembled stub is {stub.body_count} touching bodies")
    check("the stub is the real board's full thickness, not a thin sample",
          abs((hi[2] - lo[2]) - (SEAT_Z + P.POST_H)) < 1e-6,
          f"{hi[0]-lo[0]:.0f} x {hi[1]-lo[1]:.0f} x {hi[2]-lo[2]:.1f} mm")
    # 10%, not 6%: the stub has to reach down far enough to give every post in
    # it a whole skirt of plate, and the skirt got a quarter wider.
    check("the stub is small enough to be worth printing before the board",
          (hi[0] - lo[0]) * (hi[1] - lo[1]) < 0.10 * (P.BED_X * P.BED_Y),
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
    # Non-decreasing, not strictly increasing. Equal entries level a run of
    # columns -- [0, 0, 0, ...] puts 5 through 9 on one line -- and that is a
    # legitimate shape, not a mistake. What is never allowed is a shortfall
    # going DOWN as you move outward, which would have a short column reach
    # higher than a long one.
    check("column shortfalls are listed outward from the middle and never "
          "go backwards",
          (len(P.COLUMN_SHORTFALL) >= int(round(
               max(B.k_max(i) for i in range(len(P.ROWS)))
               - min(B.k_max(i) for i in range(len(P.ROWS))))) + 1
           and P.COLUMN_SHORTFALL[0] == 0
           and all(P.COLUMN_SHORTFALL[k] <= P.COLUMN_SHORTFALL[k + 1]
                   for k in range(len(P.COLUMN_SHORTFALL) - 1))),
          f"{[round(v) for v in P.COLUMN_SHORTFALL]} mm")
    drops = [round(B.half_height(i + 1) - B.half_height(i), 3) for i in range(5)]
    check("the lens never steps back UP on its way out from the middle",
          all(d >= 0 for d in drops),
          f"drops of {drops} mm, in units of a {P.PITCH_Y:.0f} mm box: "
          f"{[round(d / P.PITCH_Y, 2) for d in drops]}"
          + ("; a zero is a levelled run of columns" if 0 in drops else ""))
    check("no column's cells are spread so far apart they stop reading as a "
          "column",
          max(B.row_pitch(i) for i in range(len(P.ROWS))) <= 3 * P.PITCH_Y,
          f"widest is {max(B.row_pitch(i) for i in range(len(P.ROWS))):.0f} mm "
          f"in column {P.COLUMNS[max(range(len(P.ROWS)), key=B.row_pitch)]}")

    # A column's TOP is where COLUMN_SHORTFALL puts it and nothing else moves
    # it; COLUMN_DROP only ever lengthens the bottom. Get those two mixed up
    # and a column quietly climbs above its neighbour, which is the one thing
    # the ladder must never do.
    check("a column's top is set by its shortfall alone",
          all(abs(B.summit(i)[1] - P.SUMMIT_STEP - B.half_height(i)) < 1e-9
              for i in range(len(P.ROWS))),
          "the drop lengthens a column downward, never upward")
    check("columns hang from a shared midline, dropping only where told to",
          all(abs(B.cell_xy(i, 0)[1] + B.half_height(i)
                  + B.column_drop(i)) < 1e-9
              for i in range(len(P.ROWS))),
          f"drops of {[round(v) for v in P.COLUMN_DROP]} mm counting out "
          f"from column 7")
    check("no column's drop takes it below the title",
          min(B.cell_xy(i, 0)[1] - P.PAD_OD / 2 for i in range(len(P.ROWS)))
          >= min(y0 for _x0, y0, _x1, _y1 in B.title_extents())
          if P.TITLE_TEXT else True,
          f"lowest cell reaches "
          f"{min(B.cell_xy(i, 0)[1] - P.PAD_OD/2 for i in range(len(P.ROWS))):.1f}"
          f" against a title bottom of "
          f"{min(y0 for _x0, y0, _x1, _y1 in B.title_extents()):.1f} mm"
          if P.TITLE_TEXT else "no title")

    print("\nthe post/socket interface  (male-up: board, then every piece)")
    # The floor is 0.15, not 0.25. 0.25 was set when nothing had been printed
    # and the fit was a guess; the stub came off at size, so the socket has
    # been taken in to half of what it was. Below 0.15 diametral the joint
    # stops being a fit and becomes an interference the plastic has to absorb,
    # and a piece that has to be forced on will split a socket coming off.
    board_clear = P.PEG_SOCKET_D - P.POST_D
    piece_clear = P.PEG_SOCKET_D - P.PEG_POST_D
    check("socket clears the board's post", 0.15 <= board_clear <= 0.75,
          f"{board_clear:.2f} mm diametral, {board_clear/2:.3f} radial "
          f"(~{board_clear/2/0.42:.1f} line widths)")
    check("socket clears the post of a piece below it",
          0.15 <= piece_clear <= 0.75, f"{piece_clear:.2f} mm diametral")
    check("socket is deeper than a post is long, so the SKIRT seats and "
          "stack height is exact",
          P.PEG_SOCKET_DEPTH > max(P.POST_H, P.PEG_POST_H) + 0.2,
          f"socket {P.PEG_SOCKET_DEPTH:.2f} vs posts "
          f"{P.POST_H:.2f}/{P.PEG_POST_H:.2f}")

    # What a piece actually stands on: the whole skirt on a slab, or as much
    # of it as the pad is wide on a lattice. The rule is that the CONTACT is
    # wide, not that the skirt is wholly supported -- a skirt that overhangs
    # its pad a little still sits on a generous annulus.
    # FIVE shapes, so every one of these is the worst of the five -- the
    # runner included, which is the whole point of reading B.PIECE_STYLES
    # here rather than P.PLAYER_STYLES. The widest is what has to clear a
    # neighbour; the narrowest BASE is what has to seat, and they are not the
    # same piece -- the saucer's brim overhangs a base 1.15 mm narrower.
    skirt_r = max(B.piece_max_r(s) for s in B.PIECE_STYLES)
    worst = min(B.PIECE_STYLES, key=B.piece_seat_r)
    base_r = B.piece_seat_r(worst)
    seat_r = base_r if SLAB else min(base_r, P.PAD_OD / 2)
    check("the seat is a wide annulus, not a rim",
          seat_r - P.POST_D / 2 >= 3.0,
          f"{P.POST_D/2:.2f} to {seat_r:.2f} mm contact ring on the {worst}, "
          f"which is the narrowest based of the four")
    if not SLAB:
        check("a piece does not overhang its pad far enough to teeter",
              skirt_r - P.PAD_OD / 2 <= 2.0,
              f"skirt r{skirt_r:.2f} on pad r{P.PAD_OD/2:.2f}: "
              f"{max(0.0, skirt_r - P.PAD_OD/2):.2f} mm of air")

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
    # THE SOCKET ROOF, measured on the profile rather than asserted from the
    # parameters. It closes the socket over thin air, printed the right way
    # up, so it is the one surface in a piece that could need support. The
    # body is too short for a full cone now, so the cone is truncated and the
    # small flat left at the top is bridged -- which is fine while the flat
    # stays small, and silently is not the moment it does not.
    prof = B._piece_profile(P.PEG_BODY_PROFILE, P.PEG_BODY_H)
    rs = P.PEG_SOCKET_D / 2
    # the cone is the single edge arriving at the top of the socket wall
    i = next(k for k, (r, z) in enumerate(prof)
             if abs(r - rs) < 1e-9 and abs(z - P.PEG_SOCKET_DEPTH) < 1e-9)
    (r0, z0), (r1, z1) = prof[i - 1], prof[i]
    slope = abs(z1 - z0) - abs(r1 - r0)
    check("the socket roof climbs at 45 degrees, so it needs no support",
          abs(slope) < 1e-6,
          f"rises {abs(z1-z0):.2f} mm over {abs(r1-r0):.2f} mm, from r"
          f"{r0:.2f} to the socket wall at r{r1:.2f}")
    span = B.socket_bridge()
    check("what is left flat at the top of it is a span, not a ceiling",
          span <= 4.0,
          f"{span:.2f} mm bridged, out of the {P.PEG_SOCKET_D:.2f} mm a flat "
          f"roof would have spanned")
    check("there is solid plastic above the roof to print the top face on",
          P.PEG_SOCKET_ROOF >= 3 * P.LAYER_H,
          f"{P.PEG_SOCKET_ROOF:.2f} mm = "
          f"{P.PEG_SOCKET_ROOF/P.LAYER_H:g} layers")

    if P.POST_CAP != "none":
        print("\nthe accent tops on the posts")
        capped = [(i, r) for i, r in B.all_cells() if B.post_capped(i, r)]
        layers = P.POST_CAP_H / P.LAYER_H
        check("the cap is a whole number of layers and fits on the post",
              abs(layers - round(layers)) < 1e-9
              and 0 < P.POST_CAP_H <= P.POST_H - 1.0,
              f"{P.POST_CAP_H:.2f} mm = {round(layers):g} layers on a "
              f"{P.POST_H:.2f} mm post")
        # The cut is meant to land where the post starts bevelling in, so what
        # you see from straight above is all accent and the straight sides
        # stay in the board's colour. Off that line it is either a red rim
        # round every dot or a white band down its side.
        check("the cap starts exactly where the post's chamfer does",
              abs(P.POST_CAP_H - P.POST_CHAMFER) < 1e-9,
              f"cap {P.POST_CAP_H:.2f} against a {P.POST_CHAMFER:.2f} mm "
              f"chamfer")
        check("no summit post is capped",
              not any(B.is_summit(i, r) for i, r in capped),
              f"{len(capped)} of {sum(P.ROWS)} cells capped, none of them a "
              f"summit -- a summit post is split by its digit instead, and "
              f"flooding it with the number's colour is what that split "
              f"exists to avoid")
    print("\nwall thickness")
    rs = P.PEG_SOCKET_D / 2
    for name, prof in [(s, B.piece_profile_of(s)) for s in B.PIECE_STYLES]:
        walls = [r - rs for r, dz in prof if dz <= P.PEG_SOCKET_DEPTH]
        check(f"{name}: wall between socket and outside stays printable",
              min(walls) >= 1.20,
              f"min {min(walls):.2f} mm (~{min(walls)/0.42:.1f} perimeters)")

    # FOUR SHAPES, ONE INTERFACE. Player A stacks on player B, so every piece
    # has to accept every other and add exactly the same height doing it. The
    # silhouette is the only thing a style may change.
    print(f"\n{len(B.PIECE_STYLES)} shapes, one interface, ONE ENVELOPE")
    built = {s: B.build_piece(s) for s in B.PIECE_STYLES}
    tall = {s: m.bounds[1][2] - m.bounds[0][2] for s, m in built.items()}
    check("every piece is the same height, to the micron",
          max(tall.values()) - min(tall.values()) < 1e-6
          and abs(min(tall.values()) - (P.PEG_BODY_H + P.PEG_POST_H)) < 1e-6,
          f"{min(tall.values()):.2f} mm each: {P.PEG_BODY_H:.2f} of body and "
          f"{P.PEG_POST_H:.2f} of post")
    for s, m in built.items():
        check(f"{s}: one watertight solid, flat on the bed",
              m.is_watertight and m.is_winding_consistent
              and m.body_count == 1 and abs(m.bounds[0][2]) < 1e-6,
              f"{len(m.faces)} triangles, {m.body_count} body")
    wide = {s: max(m.bounds[1][0] - m.bounds[0][0],
                   m.bounds[1][1] - m.bounds[0][1]) for s, m in built.items()}
    check("no shape is wider than the cell pitch allows",
          max(wide.values()) <= 2 * P.PEG_MAX_R + 1e-6,
          f"widest is the {max(wide, key=wide.get)} at "
          f"{max(wide.values()):.2f} mm against a {2*P.PEG_MAX_R:.2f} limit")
    # A CEILING IS NOT THE RULE. The rule is that they are all the same size,
    # and a ceiling is passed just as happily by a piece that is 2 mm short of
    # it -- which is how the runner stayed the odd one out. So measure the
    # spread, not the maximum.
    check("every piece is the same width, to the micron",
          max(wide.values()) - min(wide.values()) < 1e-6
          and abs(max(wide.values()) - 2 * P.PEG_MAX_R) < 1e-6,
          f"{max(wide.values()):.2f} mm across, all {len(wide)} of them")
    # Measured on the mesh, not on the profile: the crown's notches are cut
    # into its top face after the lathe, so the profile says r8.10 and the
    # UNBROKEN ring is a good deal less than that. What the next piece stands
    # on is the ring that goes all the way round.
    rings = {}
    for s, m in built.items():
        z = P.PEG_BODY_H - 0.05
        rr = np.linspace(P.PEG_POST_D / 2 + 0.05, B.piece_max_r(s), 60)
        worst_r = np.inf
        for a in np.linspace(0, 2 * np.pi, 36, endpoint=False):
            pts = np.column_stack([rr * np.cos(a), rr * np.sin(a),
                                   np.full_like(rr, z)])
            solid = m.contains(pts)
            k = int(np.argmin(solid)) if not solid.all() else len(rr)
            worst_r = min(worst_r, rr[k - 1] if k else 0.0)
        rings[s] = float(worst_r)
    thin = min(rings, key=rings.get)
    check("every shape keeps an unbroken seating ring for what stacks on it",
          rings[thin] - P.PEG_POST_D / 2 >= 3.0,
          "rings out to "
          + ", ".join(f"{s} r{rings[s]:.2f}" for s in B.PIECE_STYLES)
          + f"; tightest is the {thin} at "
          f"{rings[thin] - P.PEG_POST_D/2:.2f} mm wide")

    # PRINTED FLAT, NO SUPPORTS. A profile that widens going up is an
    # overhang, and the angle from vertical is atan(dr/dz) -- so a
    # millimetre of radius per millimetre of height is 45 degrees and the
    # limit. Measured on the profiles, because it is the one rule a new
    # silhouette will break without anything else noticing.
    worst_over, who = 0.0, None
    for s in B.PIECE_STYLES:
        prof = B.piece_profile_of(s)
        for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
            if r1 > r0 and z1 > z0 and (r1 - r0) / (z1 - z0) > worst_over:
                worst_over, who = (r1 - r0) / (z1 - z0), (s, z0, z1)
    check("nothing overhangs more than 45 degrees, so nothing needs support",
          worst_over <= 1.0 + 1e-9,
          f"steepest is the {who[0]} between z{who[1]:.2f} and z{who[2]:.2f}, "
          f"at {np.degrees(np.arctan(worst_over)):.0f} degrees from vertical")

    # and the thing all of that is for: any of them on any of them
    heights = []
    for a in B.PIECE_STYLES:
        for b in B.PIECE_STYLES:
            lower = built[a].copy()
            upper = R_placed(built[b], P.PEG_BODY_H)
            heights.append(upper.bounds[1][2] - lower.bounds[1][2])
    check("any shape stacks on any other and adds the same height",
          max(heights) - min(heights) < 1e-6
          and abs(heights[0] - P.PEG_BODY_H) < 1e-6,
          f"{len(heights)} pairings, every one adding {P.PEG_BODY_H:.2f} mm")

    print("\nneighbours do not touch")
    narrow = min(B.row_pitch(i) for i in range(len(P.ROWS)))
    for axis, pitch in [("along a row", P.PITCH_X), ("up a column", narrow)]:
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
    # Both filaments, fused: what a piece actually sits on. There is no
    # single-colour board any more, so "the board" means the assembly.
    brd = B.build_board_assembled()
    body_only = B.build_board()
    coupon = B.build_fit_coupon()

    # body_only, not brd: what has to come off the bed as ONE object is the
    # file the board's colour prints from. The assembly is the body plus 16
    # fills and caps sitting in and on it, touching but not merged, and that
    # is what it should be.
    for name, m in [("board body", body_only), ("marker", marker),
                    ("runner", runner), ("fit coupon", coupon)]:
        check(f"{name} is a watertight single solid",
              m.is_watertight and m.is_winding_consistent and m.body_count == 1,
              f"{len(m.faces)} triangles, {m.body_count} body")
        check(f"{name} sits on the bed at z=0 and needs no raft",
              abs(m.bounds[0][2]) < 1e-6, f"min z = {m.bounds[0][2]:.4f}")

    # THE DUAL-NOZZLE BED, not the single-nozzle one. The board is two
    # filaments and always has been since the numbers went in, so the figure
    # that applies is the smaller one -- 25 mm less in X. Checking it against
    # the single-nozzle bed is how a 309.7 mm board came to be declared a fit.
    lo, hi = brd.bounds
    w, h, t = hi - lo
    check("board fits the DUAL-nozzle bed",
          w <= P.BED_X_DUAL and h <= P.BED_Y_DUAL and t <= P.BED_Z,
          f"{w:.1f} x {h:.1f} x {t:.1f} mm in "
          f"{P.BED_X_DUAL:.0f} x {P.BED_Y_DUAL:.0f} x {P.BED_Z:.0f}")
    check("board keeps a margin off the bed edge",
          P.BED_X_DUAL - w >= 10 and P.BED_Y_DUAL - h >= 10,
          f"{P.BED_X_DUAL - w:.0f} mm spare in X, "
          f"{P.BED_Y_DUAL - h:.0f} mm in Y")

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

    box_w = max(P.PLAQUE_W, P.NUMERAL_BOX_W)
    hw, hh = P.NUMERAL_MAX_W / 2, P.NUMERAL_SIZE / 2
    check("every digit fits inside the footprint reserved for it",
          hw + 1.0 <= box_w / 2 and hh + 1.0 <= P.PLAQUE_H / 2,
          f"digit {2*hw:.0f} x {2*hh:.0f} in a footprint "
          f"{box_w:.0f} x {P.PLAQUE_H:.0f}")

    # EVERY NUMBER THE SAME SIZE. Two-digit numbers are wider than one-digit
    # ones and there is nothing to be done about that, but they must not end
    # up SHORTER. Clamping their width by a uniform scale did exactly that --
    # "12" came out 8.6 mm tall against everyone else's 16 -- and the only
    # sign of it was that the three of them looked wrong on the plan render.
    inks = {}
    for i in range(len(P.ROWS)):
        x, y = B.numeral_xy(i)
        g = B._digit_solid(P.COLUMNS[i], x, y, 0.0, 1.0)
        inks[P.COLUMNS[i]] = (g.bounds[0][:2], g.bounds[1][:2])
    caps = {n: hi[1] - lo[1] for n, (lo, hi) in inks.items()}
    check("every number is the same height, one digit or two",
          max(caps.values()) - min(caps.values()) < 0.05,
          f"{min(caps.values()):.2f}-{max(caps.values()):.2f} mm cap height "
          f"across all 11; widest is "
          f"{max(hi[0]-lo[0] for lo, hi in inks.values()):.1f} mm")
    skirt = max(r for r, _ in P.PEG_BODY_PROFILE)

    def _gap(a, b):
        """Clear air between two axis-aligned rectangles, negative if they
        overlap. Separation on EITHER axis is enough."""
        return max(max(a[0][k] - b[1][k], b[0][k] - a[1][k]) for k in (0, 1))

    sep, pair = np.inf, None
    cols = list(inks)
    for a in range(len(cols)):
        for b in range(a + 1, len(cols)):
            g = _gap(inks[cols[a]], inks[cols[b]])
            if g < sep:
                sep, pair = g, (cols[a], cols[b])
    check("no two numbers run into each other",
          sep >= 3.0,
          f"tightest is {sep:.1f} mm, the {pair[0]} and the {pair[1]}; the "
          f"summits step down diagonally, so the two-digit numbers clear "
          f"their neighbours vertically rather than sideways")

    # The two-digit numbers now reach 12 mm either side of their column, which
    # is past halfway to the next one. A piece on a neighbouring cell must
    # still not be standing on part of a number -- except on that number's own
    # summit, where standing on it is the whole design.
    stood_on = []
    for i in range(len(P.ROWS)):
        lo_i, hi_i = inks[P.COLUMNS[i]]
        for j, r in B.all_cells():
            if j == i and B.is_summit(j, r):
                continue
            cx, cy = B.cell_xy(j, r)
            dx = max(lo_i[0] - cx, 0.0, cx - hi_i[0])
            dy = max(lo_i[1] - cy, 0.0, cy - hi_i[1])
            gap = float(np.hypot(dx, dy)) - skirt
            if gap < 0.5:
                stood_on.append((P.COLUMNS[i], P.COLUMNS[j], r, round(gap, 2)))
    check("no piece stands on a number except the one it claims",
          not stood_on,
          f"nearest piece clears every other column's digits"
          if not stood_on else f"{stood_on}")

    # The title, when it is switched on. Nothing here runs otherwise.
    if P.TITLE_TEXT:
        print("\nthe title along the bottom")
        letters = B.title_letters()
        check("every letter is in line with its column",
              all(abs(x - B.cell_xy(P.COLUMNS.index(c), 0)[0]) < 1e-9
                  for (ch, x, y), c in zip(letters, P.TITLE_TEXT)),
              "".join(ch for ch, _, _ in letters))
        ext = B.title_extents()
        caps = [y1 - y0 for _x0, y0, _x1, y1 in ext]
        check("every letter is the same height",
              max(caps) - min(caps) < 0.05,
              f"{min(caps):.2f}-{max(caps):.2f} mm cap height")
        worst, who = np.inf, None
        for (ch, _lx, _ly), (x0, y0, x1, y1) in zip(letters, ext):
            for j, r in B.all_cells():
                cx, cy = B.cell_xy(j, r)
                dx = max(x0 - cx, 0.0, cx - x1)
                dy = max(y0 - cy, 0.0, cy - y1)
                g = float(np.hypot(dx, dy)) - skirt
                if g < worst:
                    worst, who = g, (ch, P.COLUMNS[j], r)
        check("no piece stands on a letter",
              worst >= 2.5,
              f"tightest is {worst:.2f} mm, the {who[0]} against column "
              f"{who[1]}")
        gaps = [max(max(a[0]-b[2], b[0]-a[2]), max(a[1]-b[3], b[1]-a[3]))
                for i, a in enumerate(ext) for b in ext[i+1:]]
        check("no two letters run into each other",
              min(gaps) >= 3.0, f"tightest is {min(gaps):.1f} mm")

    if not SLAB:
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
    # Asked of the mesh, not of its body count: how many separate bodies the
    # accent part comes out as depends on which glyphs their post happens to
    # cut in two, and widening the two-digit numbers changed that.
    if SLAB and P.RIM_CAP_H > 1e-9:
        poly_ = np.asarray(B.octagon(), dtype=float)
        ctr_ = B.octagon_centre()
        mid = (poly_[0] + poly_[1]) / 2
        n_ = (ctr_ - mid) / np.linalg.norm(ctr_ - mid)
        probe = np.append(mid + n_ * (P.RIM_W / 2),
                          P.SLAB_T + P.RIM_H - P.RIM_CAP_H / 2)
        check("the accent part carries the cap on the lip as well as the "
              "digits",
              bool(accent.contains(probe[None, :])[0]),
              f"solid at z={probe[2]:.2f} in the lip band")
    check("the accent part reaches the tops of the posts",
          abs(accent.bounds[1][2] - (SEAT_Z + P.POST_H)) < 1e-6,
          f"z={accent.bounds[1][2]:.2f}; the digit is carried up through "
          f"each post, not stopped at the plate")
    if P.POST_CAP != "none":
        # Body and accent have to meet at the cut with nothing missing and
        # nothing doubled, which is only true if both halves were built off
        # the same profile. Probed on the finished meshes, a fifth of a
        # millimetre either side of the join.
        i0, r0 = next((i, r) for i, r in B.all_cells() if B.post_capped(i, r))
        cx, cy = B.cell_xy(i0, r0)
        zc = SEAT_Z + P.POST_H - P.POST_CAP_H
        pr = np.array([[cx, cy, zc - 0.2], [cx, cy, zc + 0.2]])
        stem, cap_m = body_only.contains(pr), accent.contains(pr)
        check("body and cap meet at the cut with no gap and no overlap",
              bool(stem[0] and not stem[1] and cap_m[1] and not cap_m[0]),
              f"the body is solid below z={zc:.2f} and the accent above it, "
              f"on column {P.COLUMNS[i0]}")

    check("the board body still carries the rest of every post",
          abs(body_only.bounds[1][2] - (SEAT_Z + P.POST_H)) < 1e-6,
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

    # WHAT THE SLICER WILL SEE. An STL has no notion of separate bodies: it
    # is a bag of triangles, and every loader welds coincident vertices on
    # the way in. The accent part is 60 bodies, and where two of them TOUCH,
    # welding turns the shared rim into an edge with four faces on it -- so
    # the file that is perfectly watertight in memory loads back as "not
    # watertight" and a slicer offers to repair it.
    #
    # That is expected here and harmless: every body is closed and correctly
    # wound on its own, and each touch is a pocket fill meeting the slice of
    # the post standing in it, at the seat plane. What must not happen is
    # non-manifold edges appearing ANYWHERE ELSE, which would mean two solids
    # actually intersecting rather than abutting.
    print("\nthe accent part as a slicer will load it")
    welded = accent.copy()
    welded.merge_vertices()
    import collections
    counts = collections.Counter(map(tuple, welded.edges_sorted))
    odd = [e for e, n in counts.items() if n != 2]
    zs = welded.vertices[list({v for e in odd for v in e})][:, 2] if odd else \
        np.zeros(0)
    check("every body of it is closed and wound the right way on its own",
          all(c.is_watertight and c.is_winding_consistent
              for c in accent.split(only_watertight=False)),
          f"{accent.body_count} bodies, all closed")
    check("bodies only ever touch at the seat plane, never intersect",
          len(zs) == 0 or (abs(zs - SEAT_Z).max() < 1e-6),
          f"{len(odd)} welded edges, all at z={SEAT_Z:.2f} -- each one a "
          f"number's pocket meeting the post standing in it"
          if len(zs) else "nothing touches at all")

    # THE TWO HALVES. The board is two files now and only two, so the thing
    # to check is that they partition it: every cubic millimetre belongs to
    # exactly one filament. An OVERLAP means both claim the same space and
    # the slicer picks; a GAP means a void nobody fills.
    #
    # The old single-colour board.stl was a third definition of the same
    # object that nothing downstream read, and it diverged twice before it
    # was dropped -- once losing the top of every capped post, once shipping
    # every summit post with a digit-shaped slot through it.
    print("\nthe two colours partition the board")
    overlap = (body_only.volume + accent.volume - brd.volume) / 1000.0
    check("body and accent claim no space twice and leave none unclaimed",
          abs(overlap) < 0.002,
          f"{body_only.volume/1000:.2f} + {accent.volume/1000:.2f} = "
          f"{brd.volume/1000:.2f} cm3 fused, to within "
          f"{abs(overlap)*1000:.2f} mm3")
    check("the two of them fuse into one watertight solid",
          brd.is_watertight and brd.is_winding_consistent,
          f"{len(brd.faces)} triangles in {brd.body_count} touching bodies -- "
          f"the fills and caps sit in and on the body rather than merge "
          f"with it")

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
    if P.OCTAGON_REGULAR:
        check("all eight edges are the same length",
              max(edges) - min(edges) < 0.05,
              f"{min(edges):.1f} mm each" if max(edges) - min(edges) < 0.05
              else f"{np.round(edges, 1).tolist()}")
    else:
        # Not a regular octagon: each axis is sized to its own content. The
        # rule that still has to hold is that it is a SENSIBLE octagon --
        # four flats and four corner cuts, none of them vanishing.
        check("the frame is an octagon with no degenerate edge",
              min(edges) > 20.0,
              f"flats and chamfers run {min(edges):.0f}-{max(edges):.0f} mm")

    # OCTAGON_ACROSS pins the frame to a number somebody typed, so the margin
    # is whatever is left over rather than something that was asked for. If
    # the content ever grows past it the lip starts eating into the board
    # instead of the board growing, and nothing else would say so.
    if P.OCTAGON_REGULAR and P.OCTAGON_ACROSS:
        pts_ = B.content_points()
        lo_, hi_ = pts_.min(axis=0), pts_.max(axis=0)
        dd = np.abs(pts_ - (lo_ + hi_) / 2)
        need = max(dd[:, 0].max(), dd[:, 1].max(),
                   (dd[:, 0] + dd[:, 1]).max() / np.sqrt(2.0))
        spare = P.OCTAGON_ACROSS / 2 - need
        check("the size it is pinned to still leaves room for the lip",
              spare >= P.RIM_W + P.RIM_CLEAR - 0.05,
              f"{P.OCTAGON_ACROSS:.0f} mm across leaves {spare:.2f} mm "
              f"outside the content, against {P.RIM_W + P.RIM_CLEAR:.0f} the "
              f"lip and its clearance need")

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

    stub_checks(brd, body_only, accent)

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
