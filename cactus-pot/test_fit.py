"""Checks that have to pass before any of this is worth filament.

Run from inside this folder:

    python3 test_fit.py

Each check prints its own numbers and the run ends with a count. The point is
not that the code runs -- it is that the press fit, the wall left round a
socket and the overhangs are numbers someone has looked at.
"""

from __future__ import annotations

import sys

import numpy as np
import trimesh

import cactus as C
import params as P

FAILS = []
CHECKS = 0


def check(ok, label, detail=""):
    global CHECKS
    CHECKS += 1
    mark = "pass" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILS.append(label)


def head(title):
    print(f"\n{title}")


# ---------------------------------------------------------------------------

def main():
    body, sites = C.cactus()
    spike = C.spike()
    plate = C.spike_plate()
    coupon = C.fit_coupon()

    # -- solids -------------------------------------------------------------
    head("solids")
    for name, m in (("cactus", body), ("spike", spike), ("coupon", coupon)):
        check(m.is_volume, f"{name} is a closed volume",
              f"{len(m.faces)} faces, {m.volume / 1000:.1f} cm3")
    check(body.body_count == 1, "the cactus is one piece",
          f"{body.body_count} bodies")

    # -- the press fit ------------------------------------------------------
    # The only numbers in this project that decide whether a spike stays in.
    head("press fit")
    printed_hole = P.SOCKET_D - P.SOCKET_COMP
    printed_pin = P.PIN_SHANK_D + P.PIN_COMP
    fit = printed_hole - printed_pin
    check(abs(fit - P.PRESS_FIT) < 1e-9,
          "modelled sizes land on the intended printed fit",
          f"hole Ø{printed_hole:.2f} - pin Ø{printed_pin:.2f} = {fit:+.3f} mm")
    check(-0.12 <= P.PRESS_FIT <= -0.02,
          "the fit is an interference a thumb can still seat",
          f"{P.PRESS_FIT:+.2f} mm (want -0.02 .. -0.12)")
    check(P.PIN_SHANK_L < P.SOCKET_DEPTH - 0.3,
          "the pin bottoms on the collar, not on the hole",
          f"pin {P.PIN_SHANK_L} into a {P.SOCKET_DEPTH} bore")
    check(P.SPIKE_COLLAR_D > P.SOCKET_D + 2 * P.SOCKET_MOUTH_CHAMFER + 0.2,
          "the collar covers the countersunk mouth",
          f"collar Ø{P.SPIKE_COLLAR_D} over a Ø"
          f"{P.SOCKET_D + 2 * P.SOCKET_MOUTH_CHAMFER:.2f} mouth")
    check(P.PIN_SHANK_D >= 3 * P.NOZZLE,
          "the pin is thick enough to be more than two perimeters",
          f"Ø{P.PIN_SHANK_D:.2f} on a {P.NOZZLE} nozzle")
    check(P.SPIKE_TIP_D >= P.NOZZLE,
          "the tip is at least one extrusion wide",
          f"Ø{P.SPIKE_TIP_D:.2f}")

    # -- the sockets --------------------------------------------------------
    head("sockets")
    check(len(sites) > 0, "there are sockets", f"{len(sites)} of them")

    # every socket has to be a real hole: its mouth open to the air and its
    # floor still inside the part.
    mouths = np.array([p for p, _, _, _ in sites])
    axes = np.array([C._rake(n, r, s) for _, n, r, s in sites])
    floors = mouths - axes * (P.SOCKET_DEPTH - 0.4)
    inside = body.contains(floors)
    check(bool(np.all(~inside)), "every bore is cut to full depth",
          f"{int(np.sum(inside))} short")

    # Does the bore break out of the far side? Measure the wall left beyond
    # the bottom of each hole along its own axis.
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(body)
    starts = mouths + axes * 0.05
    hit, idx_ray, _ = ray.intersects_location(
        starts, -axes, multiple_hits=True)
    worst = np.inf
    for i in range(len(sites)):
        d = np.linalg.norm(hit[idx_ray == i] - starts[i], axis=1)
        # ignore the bore's own floor AND the relief below it
        d = d[d > P.SOCKET_DEPTH + P.SOCKET_RELIEF_L + 0.3]
        if len(d):
            worst = min(worst,
                        float(d.min()) - P.SOCKET_DEPTH - P.SOCKET_RELIEF_L)
    check(worst > 2.0, "a solid wall is left under every socket",
          f"thinnest {worst:.1f} mm beyond the bore")

    # Sockets must not run into each other.
    d = np.linalg.norm(mouths[:, None, :] - mouths[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    gap = float(d.min())
    check(gap > P.SOCKET_D + 2.0, "no two sockets overlap",
          f"closest pair {gap:.1f} mm apart")

    # Every pad has to be ON the skin. Its own bore makes contains() useless
    # here -- the point behind a pad is inside the hole -- so this measures
    # the distance from the site to the nearest surface instead.
    # Every pad has to stand PROUD of the skin, not sit flush in it. Measured
    # by probing a point just outside the bare skin but off to one side of
    # the bore: material there means the pad is really raised, air there
    # means it drowned in the body it was grown on. (Probing on the axis
    # proves nothing -- the bore is drilled straight through that point.)
    side = np.cross(axes, np.array([0.0, 0.0, 1.0]))
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    probe = (mouths
             + np.array([n for _, n, _, _ in sites]) * 0.10
             + side * (P.SOCKET_D / 2 + 0.18))
    proud = body.contains(probe)
    check(bool(np.all(proud)), "every areole stands proud of the skin",
          f"{int(np.sum(~proud))} flush or drowned of {len(sites)}")

    # -- seated spikes ------------------------------------------------------
    head("assembly")
    tips = mouths + axes * (P.SPIKE_L + P.SPIKE_COLLAR_H)
    d = np.linalg.norm(tips[:, None, :] - tips[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    check(float(d.min()) > 3.0, "seated spikes do not touch each other",
          f"closest tips {float(d.min()):.1f} mm")
    # A spine under an arm really does point down on a saguaro, so this is
    # not asking for zero -- it is asking that none of them hangs so far
    # below horizontal that its socket becomes a hole in a roof.
    low = np.degrees(np.arcsin(np.min(axes[:, 2])))
    check(low > -25.0, "no spike hangs far below horizontal",
          f"lowest lean {low:.0f}° (arm undersides)")

    # -- printing -----------------------------------------------------------
    head("printing")
    for name, m in (("cactus", body), ("spike plate", plate),
                    ("coupon", coupon)):
        e = m.extents
        check(e[0] < P.BED[0] and e[1] < P.BED[1] and e[2] < 325.0,
              f"{name} fits the bed",
              f"{np.round(e, 1).tolist()} in {P.BED[0]}x{P.BED[1]}x325")

    # Overhangs, measured on the finished mesh. The trunk and crown should
    # carry themselves; the arms are the part that will want support, and
    # this says by how much rather than pretending otherwise.
    n = body.face_normals
    area = body.area_faces
    down = np.degrees(np.arcsin(np.clip(-n[:, 2], -1, 1)))   # 90 = flat floor
    steep = (down > 45.0) & (body.triangles_center[:, 2] > 1.0)
    frac = float(area[steep].sum() / area.sum())
    print(f"       unsupported-facing area above the soil line: {frac * 100:.1f}%")
    check(frac < 0.12, "most of the part carries itself",
          f"{frac * 100:.1f}% needs support (the arms' undersides)")

    spike_n = spike.face_normals
    spike_down = np.degrees(np.arcsin(np.clip(-spike_n[:, 2], -1, 1)))
    collar = spike.area_faces[(spike_down > 45) &
                              (spike.triangles_center[:, 2] > 0.5)].sum()
    check(collar < 10.0, "the spike needs no support but its own collar",
          f"{collar:.1f} mm2 of flat underside, bridged off the pin")

    # -- the pot ------------------------------------------------------------
    head("pot")
    spigot_d = P.POT_BORE_D - 2 * P.SPIGOT_CLEAR
    check(0.2 <= P.SPIGOT_CLEAR <= 0.6,
          "the spigot is a drop-in fit, not a press fit",
          f"Ø{spigot_d:.2f} in a Ø{P.POT_BORE_D:.2f} bore")
    print("       POT_BORE_D is provisional until the pot mesh is measured:")
    print("       python3 build.py --pot reference/pot.stl")

    # -----------------------------------------------------------------------
    print(f"\n{CHECKS - len(FAILS)}/{CHECKS} checks passed")
    if FAILS:
        for f in FAILS:
            print(f"  FAILED: {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
