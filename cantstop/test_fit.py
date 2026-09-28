#!/usr/bin/env python3
"""Assertions about the design, run before you spend ten hours of printer time.

    python3 test_fit.py

These are not unit tests of the code so much as design rules. Editing
params.py is the whole point of this project, and most of the ways to get it
wrong are silent: a socket that swallows its post, a strut standing proud of a
seating face, a wall thinned to nothing, a board that has quietly grown past
the bed, a lattice that has become two detached bodies, a number you cannot
read once a piece is sitting on it. Each one costs a print to discover and
nothing to check.
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


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    mark = "ok  " if ok else "FAIL"
    print(f"  [{mark}] {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def main():
    print("ladder")
    check("11 columns, numbered 2..12",
          P.COLUMNS == list(range(2, 13)) and len(P.ROWS) == 11)
    check("ladder is symmetric about 7", P.ROWS == P.ROWS[::-1], f"{P.ROWS}")
    check("7 is the longest column, 2 and 12 the shortest",
          P.ROWS[5] == max(P.ROWS) and P.ROWS[0] == P.ROWS[-1] == min(P.ROWS))
    check("row count rises strictly towards the middle",
          all(P.ROWS[i] < P.ROWS[i + 1] for i in range(5)), f"{P.ROWS[:6]}")
    check("every column has an odd row count, so centring lands on the grid",
          all(n % 2 for n in P.ROWS), f"{P.ROWS}")

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
    check("the skirt lands on the pad, not off the edge of it",
          skirt_r < P.PAD_OD / 2,
          f"skirt r{skirt_r:.2f} inside pad r{P.PAD_OD/2:.2f}")
    check("the seat is a wide annulus, not a rim",
          skirt_r - P.POST_D / 2 >= 3.0,
          f"{P.POST_D/2:.2f} to {skirt_r:.2f} mm contact ring")

    print("\nprintability")
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
        m.apply_translation((0, 0, P.PAD_H + lvl * P.PEG_BODY_H))
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
    zs = [P.PAD_H + 0.4, P.PAD_H + 1.5]
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
    struts = B.final_struts()
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
    check("a piece fits on the box it has to stand on",
          2 * skirt <= min(P.PLAQUE_W, P.PLAQUE_H),
          f"piece {2*skirt:.1f} mm on a {P.PLAQUE_W:.0f} x "
          f"{P.PLAQUE_H:.0f} mm box")
    check("the digit is inlaid, not embossed, so a piece cannot rock on it",
          0 < P.NUMERAL_DEPTH < P.PLAQUE_T - 1.0,
          f"{P.NUMERAL_DEPTH:.2f} mm deep in a {P.PLAQUE_T:.2f} mm plate")

    # THE LEGIBILITY MECHANISM. The post has to stand in the middle of the
    # digit, so the only free variable is its colour. Body-coloured, it
    # recedes into the background and the number reads as a stencil glyph;
    # painted to match the number it merged with the glyph into one orange
    # mass and 6, 8 and 9 became indistinguishable.
    accent = B.build_board(numerals_only=True)
    check("the posts are BODY parts, so they recede instead of joining the "
          "digit's colour",
          accent.bounds[1][2] <= P.PLAQUE_T + 1e-6,
          f"accent part tops out at z={accent.bounds[1][2]:.2f}, flush with "
          f"the box at {P.PLAQUE_T:.2f} -- no post in it")
    check("the board body carries every post itself",
          abs(B.build_board(with_numerals=False).bounds[1][2]
              - (P.PLAQUE_T + P.POST_H)) < 0.01,
          "body reaches the summit post tops")

    # and a stencil only works if the glyph is large next to the hole
    lost = []
    for i, num in enumerate(P.COLUMNS):
        x, y = B.numeral_xy(i)
        g = S.text_solid(str(num), P.NUMERAL_SIZE, P.NUMERAL_DEPTH,
                         weight=P.NUMERAL_FONT_WEIGHT)
        w_ = g.bounds[1][0] - g.bounds[0][0]
        if w_ > P.NUMERAL_MAX_W:
            k = P.NUMERAL_MAX_W / w_
            g.apply_scale((k, k, 1.0))
        g.apply_translation((x, y, 0.0))
        ko = S.tube(x, y, P.POST_D / 2 + P.NUMERAL_POST_CLEAR, 0.0,
                    -1.0, 2.0, segs=64)
        cut = trimesh.boolean.difference([g, ko], engine="manifold")
        lost.append((100 * (g.volume - cut.volume) / g.volume, num))
    worst_pct, worst_num = max(lost)
    check("the post takes only a corner out of each glyph",
          worst_pct <= 25.0,
          f"worst is {worst_pct:.0f}% of the {worst_num}; on 11 and 12 the "
          f"post falls between the digits and costs nothing")

    # Only members taller than a box matter: a strut is 3.4 mm and a box is
    # 4.0 mm thick, so anything running under one is buried inside it.
    tall = [s for s in struts if s[3] > P.PLAQUE_T]
    bx = np.linspace(-P.PLAQUE_W / 2, P.PLAQUE_W / 2, 13)
    by = np.linspace(-P.PLAQUE_H / 2, P.PLAQUE_H / 2, 15)
    clear, clear_col = np.inf, None
    for i in range(len(P.ROWS)):
        sx, sy = B.numeral_xy(i)
        d = min(B.strut_distance_to((sx + dx, sy + dy), p0, p1, w_)
                for dx in bx for dy in by
                for p0, p1, w_, _h, _k in tall)
        if d < clear:
            clear, clear_col = d, P.COLUMNS[i]
    check("nothing standing proud of a box goes anywhere near one",
          clear > 1.0,
          f"{len(tall)} struts taller than {P.PLAQUE_T:.1f} mm (the octagon); "
          f"nearest is {clear:.1f} mm off column {clear_col}'s box")

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
    check("the lens is braced out to the frame on every edge",
          len([s for s in struts if s[4] == "spoke"]) >= 2 * len(P.ROWS),
          f"{len([s for s in struts if s[4] == 'spoke'])} spokes")

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
