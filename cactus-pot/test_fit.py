"""Checks that have to pass before any of this is worth filament.

Run from inside this folder:

    python3 test_fit.py

Each check prints its own numbers and the run ends with a count. The point is
not that the code runs -- it is that the press fit, the wall left round a
socket and the overhangs are numbers someone has looked at.
"""

from __future__ import annotations

import os
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

def _spikes_in_for_size(body, sites):
    """Every spike seated, just to measure the object with its spines on."""
    one = C.spike()
    out = []
    for p, n, rake, swing in sites:
        m = C._frame_from_normal(C._rake(n, rake, swing))
        m[:3, 3] = p - C._rake(n, rake, swing) * (P.PIN_SHANK_L
                                                  - P.AREOLE_RISE * 0.25)
        s = one.copy()
        s.apply_transform(m)
        out.append(s)
    return trimesh.util.concatenate(out)


def pot_clearance(body, path):
    """Compare the real profiles, height by height, inside the pot.

    The flat check in main() puts the trunk's widest radius against the
    pot's tightest wall and ignores that they happen at different heights.
    Inside a pot that is filleted at the floor, that is the wrong comparison
    twice over: the pot is tightest exactly where the cactus's base flare
    makes it narrowest. Given a pot mesh, this measures both profiles over
    the 21 mm the cactus is down inside it and reports the worst gap.
    """
    pot = trimesh.load(path, force="mesh")
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(pot)
    rim = pot.bounds[1][2]
    hits, _, _ = ray.intersects_location(
        np.array([[P.POT_BORE_D * 0.75, 0.0, rim + 50.0]]),
        np.array([[0.0, 0.0, -1.0]]), multiple_hits=True)
    floor = float(np.sort(hits[:, 2])[-1])

    ths = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
    fan = np.column_stack([np.cos(ths), np.sin(ths), np.zeros_like(ths)])
    v = body.vertices
    vr = np.linalg.norm(v[:, :2], axis=1)

    worst, worst_z = np.inf, None
    for dz in np.arange(0.05, P.POT_FLOOR_TO_RIM, 0.5):
        band = (v[:, 2] > dz - 0.5) & (v[:, 2] <= dz + 0.5)
        if not band.any():
            continue
        cactus_r = float(vr[band].max())

        o = np.column_stack([np.zeros_like(ths), np.zeros_like(ths),
                             np.full_like(ths, floor + dz)])
        hits, idx, _ = ray.intersects_location(o, fan, multiple_hits=True)
        wall = np.inf
        for i in range(len(ths)):
            r = np.linalg.norm(hits[idx == i][:, :2], axis=1)
            if len(r):
                wall = min(wall, float(r.min()))
        if wall < np.inf and wall - cactus_r < worst:
            worst, worst_z = wall - cactus_r, dz

    head("pot clearance, profile against profile")
    check(worst > 2.0, "the cactus clears the pot's wall at every height",
          f"tightest {worst:.1f} mm, {worst_z:.1f} mm above the floor")


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

    # -- the fit coupon -----------------------------------------------------
    # The coupon is a measuring instrument, and an instrument whose scale
    # cannot be read is just a block with holes in it. These checks are on
    # the engraving: that it is there against every hole, that the nozzle can
    # lay it down, and that the counters inside an 8 or a 0 survive.
    head("fit coupon")
    steps = C.coupon_steps()
    labels = [C.coupon_label(d) for d in steps]
    check(len(set(labels)) == len(labels),
          "every hole gets its own label", " ".join(labels))
    check(abs(P.COUPON_STEP - abs(P.PRESS_FIT)) < 1e-9,
          "one step of the ladder is one press fit",
          f"step {P.COUPON_STEP:.2f} against a fit of {P.PRESS_FIT:+.2f}")

    check(P.COUPON_MARK_STROKE >= P.NOZZLE,
          "the engraved stroke is at least one extrusion wide",
          f"{P.COUPON_MARK_STROKE:.2f} on a {P.NOZZLE} nozzle")
    # The island inside an 8 is the smallest piece of material on the part.
    # Let it close up and the digit prints as a filled pit, which is worse
    # than no label at all because it still looks like a number.
    counter = min(P.COUPON_MARK_W - P.COUPON_MARK_STROKE,
                  P.COUPON_MARK_H / 2 - P.COUPON_MARK_STROKE)
    check(counter >= 2 * P.NOZZLE,
          "the counter inside an 8 is wide enough to print",
          f"{P.COUPON_MARK_W - P.COUPON_MARK_STROKE:.1f} x "
          f"{P.COUPON_MARK_H / 2 - P.COUPON_MARK_STROKE:.1f} mm")

    advance = P.COUPON_MARK_W + P.COUPON_MARK_STROKE + P.COUPON_MARK_GAP
    widest = max(advance * len(t) - P.COUPON_MARK_GAP for t in labels)
    check(widest + 1.0 <= P.COUPON_PITCH,
          "the widest label fits between two holes",
          f'"{max(labels, key=len)}" is {widest:.1f} mm in a '
          f"{P.COUPON_PITCH} pitch")

    # Engraved rather than raised, so it must not reach the holes in y and
    # must not break through a 6.4 mm block.
    gap = ((P.COUPON_HOLE_Y - (P.SOCKET_D + max(steps)) / 2)
           - (P.COUPON_MARK_Y + (P.COUPON_MARK_H + P.COUPON_MARK_STROKE) / 2))
    check(gap > 1.0, "the numbers clear the holes",
          f"{gap:.1f} mm between the label row and the widest hole")
    check(P.COUPON_MARK_DEPTH < P.COUPON_T - P.NOZZLE * 3,
          "the engraving does not break through the block",
          f"{P.COUPON_MARK_DEPTH} deep in {P.COUPON_T} of material")

    # And the thing all of the above is for, read off the finished mesh:
    # every hole has engraving beside it. A groove floor is the one surface
    # at exactly COUPON_T - COUPON_MARK_DEPTH, so finding one under a hole's
    # own x span is proof that hole got labelled.
    v = coupon.vertices
    floor_z = P.COUPON_T - P.COUPON_MARK_DEPTH
    on_floor = v[np.abs(v[:, 2] - floor_z) < 1e-6]
    w = P.COUPON_PITCH * P.COUPON_N + 2 * P.COUPON_MARGIN
    missing = []
    for i in range(P.COUPON_N):
        x = -w / 2 + P.COUPON_MARGIN + P.COUPON_PITCH * (i + 0.5)
        near = np.abs(on_floor[:, 0] - x) <= P.COUPON_PITCH / 2
        if not near.any():
            missing.append(labels[i])
    check(not missing, "every hole in the coupon is labelled on the mesh",
          f"{P.COUPON_N} holes, {len(on_floor)} vertices of groove floor")

    # -- the single pair ----------------------------------------------------
    # test-hole and test-spine: the five-minute version of the coupon. The
    # checks that matter are that it really is the same socket as the cactus
    # carries, measured on the mesh rather than assumed from params.
    head("the single pair")
    hole = C.test_hole()
    check(hole.is_volume and hole.body_count == 1,
          "the test hole is one closed solid",
          f"{len(hole.faces)} faces, {hole.volume / 1000:.2f} cm3")

    # Watertight in memory is not the same as watertight on disk. An STL has
    # no shared vertex indices, so a pair of vertices a micron apart -- which
    # socket_cutter's 1e-6 overlaps leave behind -- merge on reload and tear
    # the faces that used them. This is the check that matters to a slicer,
    # and the only one that would have caught it.
    import tempfile
    tmp = tempfile.mktemp(suffix=".stl")
    hole.export(tmp)
    reloaded = trimesh.load(tmp, force="mesh")
    os.unlink(tmp)
    check(reloaded.is_watertight,
          "the test hole is still watertight after a round trip through STL",
          f"{len(reloaded.vertices)} vertices on reload, "
          f"{reloaded.volume / 1000:.2f} cm3")

    # The bore, measured by cutting the tab in half way down the hole. Not
    # by sampling vertices in a band: a cylinder carries vertices only on its
    # two end rings, so a band taken mid-bore is empty and the measurement
    # comes back NaN rather than wrong, which is its own kind of trap.
    v = hole.vertices
    z_mid = P.TEST_HOLE_T - P.SOCKET_DEPTH / 2
    seg = trimesh.intersections.mesh_plane(
        hole, plane_normal=[0, 0, 1], plane_origin=[0, 0, z_mid])
    pts = seg.reshape(-1, 3)
    rad = np.linalg.norm(pts[:, :2], axis=1)
    bore_d = 2 * float(np.median(rad[rad < P.TEST_HOLE_W / 4]))
    check(abs(bore_d - P.SOCKET_D) < 0.05,
          "the bore is the same diameter as every socket on the cactus",
          f"Ø{bore_d:.2f} against SOCKET_D {P.SOCKET_D:.2f}")

    deepest = float(v[np.linalg.norm(v[:, :2], axis=1) < P.SOCKET_D][:, 2].min())
    cut = P.TEST_HOLE_T - deepest
    check(abs(cut - (P.SOCKET_DEPTH + P.SOCKET_RELIEF_L)) < 0.1,
          "the bore and its relief are cut to full depth",
          f"{cut:.2f} mm below the face")
    check(deepest > 1.0, "a floor is left under the hole",
          f"{deepest:.2f} mm of material")

    # The pad has to be there, or the collar seats on flat plastic and the
    # joint being tested is not the one that gets printed.
    check(hole.bounds[1][2] > P.TEST_HOLE_T + 0.2,
          "the areole pad stands proud of the tab",
          f"{hole.bounds[1][2] - P.TEST_HOLE_T:.2f} mm up")
    check(P.PIN_SHANK_L < P.SOCKET_DEPTH - 0.3,
          "the collar lands on the pad before the pin lands in the hole",
          f"pin {P.PIN_SHANK_L} into a {P.SOCKET_DEPTH} bore")
    check(hole.extents[0] < P.BED[0] and spike.extents[2] < 325.0,
          "both halves of the pair fit the bed",
          f"{np.round(hole.extents, 1).tolist()} and "
          f"{np.round(spike.extents, 1).tolist()}")

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

    # -- the arrangement ----------------------------------------------------
    # Rob complained twice about how the spines are laid out: first that they
    # read as rows, then that they read as columns. Both are checked here on
    # the finished site list rather than on the numbers that generated it.
    head("arrangement")

    # Both arms and the trunk are drawn the same way now, so they get the
    # same checks: the spacing they promise, and no ladder up any one crest.
    for i, spec in enumerate(P.ARMS):
        ap = np.array([p for p, _, _, _ in C.arm_areoles(spec)])
        ad = np.linalg.norm(ap[:, None, :] - ap[None, :, :], axis=2)
        np.fill_diagonal(ad, np.inf)
        check(float(ad.min()) >= P.ARM_AREOLE_MIN_SEP - 1e-6,
              f"arm {i}: no two pads are closer than the spacing",
              f"{len(ap)} pads, closest {float(ad.min()):.1f} mm, "
              f"asked for {P.ARM_AREOLE_MIN_SEP:.1f}")

    # The trunk is not laid out per rib at all any more, so what it gets
    # checked on is the thing the layout promises: a minimum distance between
    # any two pads, which is what rules out both a row and a column without
    # either being mentioned.
    trunk_sites = C.trunk_areoles()
    pts = np.array([p for p, _, _, _ in trunk_sites])
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    check(float(d.min()) >= P.AREOLE_MIN_SEP - 1e-6,
          "no two pads on the trunk are closer than the spacing",
          f"{len(pts)} pads, closest {float(d.min()):.1f} mm, "
          f"asked for {P.AREOLE_MIN_SEP:.1f}")

    # Group the pads back onto their crests by undoing the twist -- a pad's
    # bearing drifts with height, so grouping on the raw angle splits one rib
    # into several.
    crests = np.arange(P.RIB_COUNT) * 2 * np.pi / P.RIB_COUNT
    by_rib = {}
    for p, _, _, _ in trunk_sites:
        th = np.arctan2(p[1], p[0]) + np.radians(P.RIB_TWIST_DEG) * p[2] / P.TRUNK_H
        dd = (crests - th + np.pi) % (2 * np.pi) - np.pi
        k = int(np.argmin(np.abs(dd)))
        by_rib.setdefault(k, []).append((float(p[2]), -np.degrees(dd[k])))

    # The old layout put pads on every other rib, so the trunk wore eight
    # stripes. Every rib has to carry some now, or the stripes are back.
    check(len(by_rib) == P.RIB_COUNT,
          "every rib carries spines, so there are no bare stripes",
          f"{len(by_rib)} of {P.RIB_COUNT} ribs used")

    # A column is pads evenly stacked up one crest. Nothing fixes how many a
    # crest gets now, so the check is that no crest is a ladder: no three
    # pads up one rib with the same gap between them.
    counts = sorted(len(v) for v in by_rib.values())
    worst_ladder, spans = np.inf, []
    for k, v in by_rib.items():
        zs = np.array(sorted(z for z, _ in v))
        spans.append(max(o for _, o in v) - min(o for _, o in v))
        for i in range(len(zs) - 2):
            a, b, c = zs[i:i + 3]
            worst_ladder = min(worst_ladder, abs((b - a) - (c - b)))
    check(worst_ladder > 2.0,
          "no three pads up one rib are evenly spaced",
          f"{counts[0]}-{counts[-1]} pads per rib, "
          f"closest to a ladder {worst_ladder:.1f} mm out of step")

    # And the sideways wander has to stay on the rib: past a third of the way
    # to the valley the pad is on the flank and its socket is bored into a
    # slope.
    half_rib = 180.0 / P.RIB_COUNT
    check(max(spans) / 2 <= half_rib / 3,
          "every pad is still on its rib's crest",
          f"widest wander +/-{max(spans) / 2:.1f}°, "
          f"crest is +/-{half_rib / 3:.1f}° wide")

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
    check(low >= P.SPIKE_FLOOR_DEG - 0.5,
          "no spike hangs below the floor angle",
          f"lowest lean {low:.0f}°, floor {P.SPIKE_FLOOR_DEG:.0f}°")

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

    # The finished envelope, printed rather than asserted. There is nothing
    # here to check against -- these are what the shape came out as, not
    # targets -- but direction.md quoted four of them and had drifted wrong
    # on all four, so they belong where someone changing the shape will see
    # them.
    whole = trimesh.util.concatenate([body, _spikes_in_for_size(body, sites)])
    e, be = whole.extents, body.extents
    above_rim = whole.bounds[1][2] - P.POT_FLOOR_TO_RIM
    print(f"       cactus body {be[2]:.1f} tall, {be[0]:.1f} x {be[1]:.1f} "
          f"across; with spines {e[0]:.1f} x {e[1]:.1f}")
    print(f"       assembly {76.0 + above_rim:.1f} tall "
          f"({above_rim:.1f} of cactus above a 76.0 pot)")

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
    check(P.SPIGOT_H < P.POT_SOCKET_DEPTH - 0.3,
          "the cactus lands on the pot floor, not in the hole",
          f"{P.SPIGOT_H} mm spigot in an {P.POT_SOCKET_DEPTH} mm socket")
    check(P.TRUNK_R_BASE + P.RIB_DEPTH < P.POT_INNER_R - 4.0,
          "the trunk clears the pot's inner wall",
          f"{P.POT_INNER_R - P.TRUNK_R_BASE:.1f} mm of gap at the floor")
    check(P.AREOLE_Z_MIN > P.POT_FLOOR_TO_RIM + 1.0,
          "no spine sits down inside the pot",
          f"lowest at {P.AREOLE_Z_MIN}, rim at {P.POT_FLOOR_TO_RIM}")

    import build
    path = build.pot_path(sys.argv[1:])
    if path:
        pot_clearance(body, path)
    else:
        print("\n(no pot mesh found; pass --pot <stl> for the clearance check)")

    # -----------------------------------------------------------------------
    print(f"\n{CHECKS - len(FAILS)}/{CHECKS} checks passed")
    if FAILS:
        for f in FAILS:
            print(f"  FAILED: {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
