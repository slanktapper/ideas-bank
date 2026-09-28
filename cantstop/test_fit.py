#!/usr/bin/env python3
"""Assertions about the design, run before you spend ten hours of printer time.

    python3 test_fit.py

These are not unit tests of the code so much as design rules. Editing
params.py is the whole point of this project, and most of the ways to get it
wrong are silent: a bore that swallows the pin, a strut that ploughs through
a hole, a socket the waist has thinned to nothing, a board that has quietly
grown past the bed. Each one costs a print to discover and nothing to check.
"""

from __future__ import annotations

import sys

import numpy as np

import board as B
import params as P

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
    check("ladder is symmetric about 7", P.ROWS == P.ROWS[::-1],
          f"{P.ROWS}")
    check("7 is the longest column, 2 and 12 the shortest",
          P.ROWS[5] == max(P.ROWS) and P.ROWS[0] == P.ROWS[-1] == min(P.ROWS))
    check("row count rises strictly towards the middle",
          all(P.ROWS[i] < P.ROWS[i + 1] for i in range(5)),
          f"{P.ROWS[:6]}")

    print("\nthe pin/socket interface")
    bore_clear = P.COLLAR_BORE - P.PEG_PIN_D
    sock_clear = P.PEG_SOCKET_D - P.PEG_PIN_D
    check("pin clears the collar bore", 0.25 <= bore_clear <= 0.75,
          f"{bore_clear:.2f} mm diametral")
    check("pin clears a socket below it", 0.25 <= sock_clear <= 0.75,
          f"{sock_clear:.2f} mm diametral")
    check("socket is deeper than the pin is long, so the SHOULDER seats "
          "and stack height is exact",
          P.PEG_SOCKET_DEPTH > P.PEG_PIN_H + 0.2,
          f"socket {P.PEG_SOCKET_DEPTH:.2f} vs pin {P.PEG_PIN_H:.2f}")
    check("pin is shorter than the collar is deep",
          P.PEG_PIN_H <= P.COLLAR_H,
          f"pin {P.PEG_PIN_H:.2f}, collar {P.COLLAR_H:.2f}")

    shoulder_r = P.PEG_BODY_PROFILE[0][0]
    rim_r = P.PEG_BODY_PROFILE[-1][0]
    check("shoulder overhangs the rim of the piece below, so it seats on a "
          "ring rather than balancing on a lip",
          shoulder_r > rim_r,
          f"shoulder r{shoulder_r:.2f} vs rim r{rim_r:.2f}")
    check("shoulder lands on the collar, not outside it",
          P.COLLAR_BORE / 2 < shoulder_r < P.COLLAR_OD / 2,
          f"r{shoulder_r:.2f} between bore r{P.COLLAR_BORE/2:.2f} "
          f"and collar r{P.COLLAR_OD/2:.2f}")

    print("\nwall thickness")
    for name, prof, body_h in [("marker", P.PEG_BODY_PROFILE, P.PEG_BODY_H),
                               ("runner", P.RUNNER_BODY_PROFILE, P.RUNNER_BODY_H)]:
        floor = body_h - P.PEG_SOCKET_DEPTH        # socket floor, above shoulder
        walls = [r - P.PEG_SOCKET_D / 2 for r, dz in prof if dz >= floor]
        check(f"{name}: wall between socket and outside stays printable",
              min(walls) >= 1.20,
              f"min {min(walls):.2f} mm (~{min(walls)/0.42:.1f} perimeters)")

    print("\nlattice vs bore  (measured against every built strut)")
    struts = B.final_struts()
    worst = None
    for i, r in B.all_cells():
        c = B.cell_xy(i, r)
        for p0, p1, w, _h, _k in struts:
            dist = B.strut_distance_to(c, p0, p1, w)
            if worst is None or dist < worst[0]:
                worst = (dist, P.COLUMNS[i], r)
    wall = worst[0] - P.COLLAR_BORE / 2
    check("no strut anywhere reaches into a bore", wall > 0.8,
          f"tightest is column {worst[1]} row {worst[2]}: "
          f"{wall:.2f} mm of collar wall")
    lattice = [s for s in struts if s[4] == "lattice"]
    loose = []
    for p0, p1, w, _h, _k in lattice:
        for end in (p0, p1):
            d = min(np.linalg.norm(np.asarray(B.cell_xy(*c)) - np.asarray(end))
                    for c in B.all_cells())
            if d >= P.COLLAR_OD / 2:
                loose.append(round(d, 2))
    check("every lattice strut ends inside a collar, so it fuses rather than "
          "meeting the ring edge to edge",
          not loose,
          f"{len(lattice)} lattice struts, {len(struts) - len(lattice)} "
          f"rail/drop struts")

    check("collars stand proud of the lattice",
          P.COLLAR_H > max(P.STRUT_H, P.FRAME_H),
          f"collar {P.COLLAR_H:.2f} vs strut {max(P.STRUT_H, P.FRAME_H):.2f}")

    print("\nneighbouring pieces do not touch")
    body_r = max(r for r, _ in P.PEG_BODY_PROFILE)
    for axis, pitch in [("along a row", P.PITCH_X), ("up a column", P.PITCH_Y)]:
        gap = pitch - 2 * body_r
        check(f"pieces clear each other {axis}", gap >= 3.0, f"{gap:.2f} mm gap")
    check("collars clear each other up a column",
          P.PITCH_Y - P.COLLAR_OD >= 3.0,
          f"{P.PITCH_Y - P.COLLAR_OD:.2f} mm gap")

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
    check("board fits the print bed", w <= P.BED_X and h <= P.BED_Y and t <= P.BED_Z,
          f"{w:.1f} x {h:.1f} x {t:.1f} mm in {P.BED_X:.0f} x {P.BED_Y:.0f} x {P.BED_Z:.0f}")
    check("board keeps a margin off the bed edge",
          P.BED_X - w >= 10 and P.BED_Y - h >= 10,
          f"{P.BED_X - w:.0f} mm spare in X, {P.BED_Y - h:.0f} mm in Y")

    print("\nstacking, measured on the real meshes")
    seat_z = P.COLLAR_H - P.PEG_PIN_H
    heights = []
    for lvl in range(3):
        m = marker.copy()
        m.apply_translation((0, 0, seat_z + lvl * P.PEG_BODY_H))
        heights.append(m.bounds[1][2])
    steps = np.diff(heights)
    check("every stacked piece adds the same height",
          np.allclose(steps, P.PEG_BODY_H, atol=1e-6),
          f"{np.round(steps, 3).tolist()} mm")
    check("three stacked pieces stay inside a sane table height",
          heights[-1] < 60, f"{heights[-1]:.1f} mm tall")

    # the pin of the piece above must land inside the socket of the one below,
    # without bottoming out on the socket floor
    socket_floor = seat_z + P.PEG_PIN_H + P.PEG_BODY_H - P.PEG_SOCKET_DEPTH
    pin_bottom = seat_z + P.PEG_BODY_H
    check("pin lands clear of the socket floor",
          pin_bottom > socket_floor + 0.2,
          f"{pin_bottom - socket_floor:.2f} mm of air under the pin")

    print("\ncolumn numbers are legible")
    drops = [s for s in B.final_struts() if s[4] == "drop"]
    half_digit = (2 * P.PLAQUE_DROP_DX - 4.0) / 2
    over = []
    for i in range(len(P.ROWS)):
        cx, _ = B.cell_xy(i, 0)
        for p0, p1, w, _h, _k in drops:
            # does this drop pass over the digit's footprint on the plaque?
            xs = (p0[0], p1[0])
            ys = (p0[1], p1[1])
            if min(ys) - w / 2 < P.PLAQUE_DY + P.NUMERAL_SIZE / 2 and \
               max(ys) + w / 2 > P.PLAQUE_DY - P.NUMERAL_SIZE / 2 and \
               min(xs) - w / 2 < cx + half_digit and \
               max(xs) + w / 2 > cx - half_digit:
                over.append(P.COLUMNS[i])
    check("no strut is printed across a column number", not over,
          f"{len(drops)} drop struts clear all 11 plaques"
          if not over else f"crosses {sorted(set(over))}")

    print("\nbores are actually open in the finished mesh")
    # The checks above reason about struts. This one asks the finished, fused
    # board directly: take a ring of points just inside every bore, up the
    # full depth, and confirm not one of them is inside solid plastic.
    ring = []
    rr = P.COLLAR_BORE / 2 - 0.05
    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    zs = np.linspace(0.3, P.COLLAR_H - 0.3, 4)
    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        for a in angles:
            for z in zs:
                ring.append((cx + rr * np.cos(a), cy + rr * np.sin(a), z))
    inside = brd.contains(np.asarray(ring))
    check(f"all {sum(P.ROWS)} bores are clear of plastic",
          not inside.any(),
          f"{len(ring)} probe points, {int(inside.sum())} obstructed")

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
