"""Build everything: the STLs to print and the renders to look at first.

    python3 build.py                 # stl/ and renders/
    python3 build.py --stl           # just the printable files
    python3 build.py --renders       # just the pictures
    python3 build.py --pot <file>    # measure a pot mesh and check the spigot

Run it from inside this folder.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "3d-tools"))
import render as R                                      # noqa: E402

import cactus as C                                      # noqa: E402
import params as P                                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl")
RENDERS = os.path.join(HERE, "renders")

GREEN = (0.33, 0.52, 0.30)
GREEN_DARK = (0.24, 0.40, 0.24)
SPIKE_C = (0.93, 0.90, 0.80)
POT_C = (0.76, 0.46, 0.33)


# ---------------------------------------------------------------------------
# the pot, when we have it
# ---------------------------------------------------------------------------

def measure_pot(path):
    """Report the numbers params.POT_* have to agree with.

    The pot is a mesh, not source, so it is measured rather than read. What
    matters is not the mouth -- the pot's cavity is 82 mm across and the
    cactus does not fill it -- but the blind socket in the middle of the
    cavity's floor, which is what the spigot actually goes into. Found by
    casting a ray down the axis: the first thing it hits is the bottom of
    that socket.
    """
    pot = trimesh.load(path, force="mesh")
    lo, hi = pot.bounds
    rim = hi[2]
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(pot)

    down = np.array([[0.0, 0.0, -1.0]])
    hits, _, _ = ray.intersects_location(
        np.array([[0.0, 0.0, rim + 50.0]]), down, multiple_hits=True)
    socket_floor = float(np.sort(hits[:, 2])[-1]) if len(hits) else None

    # the cavity floor, probed off-axis but still inside the socket's wall
    hits, _, _ = ray.intersects_location(
        np.array([[P.POT_BORE_D * 0.75, 0.0, rim + 50.0]]), down,
        multiple_hits=True)
    floor = float(np.sort(hits[:, 2])[-1]) if len(hits) else None

    # the socket's radius, measured halfway up it
    z = (socket_floor + floor) / 2
    hits, _, _ = ray.intersects_location(
        np.array([[0.0, 0.0, z]]), np.array([[1.0, 0.0, 0.0]]),
        multiple_hits=True)
    bore = 2 * float(np.sort(np.linalg.norm(hits[:, :2], axis=1))[0])

    # The cavity's wall -- NOT measured at the socket's height, where the pot
    # is solid and the first thing a ray meets on its way out is the outside
    # of the pot. And not from one ray either: a pot with any texture on its
    # inside is tightest somewhere a single ray will miss, so this sweeps the
    # whole well and keeps the worst radius it finds.
    inner = None
    ths = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
    fan = np.column_stack([np.cos(ths), np.sin(ths), np.zeros_like(ths)])
    for z in np.arange(floor + 1.0, rim - 0.5, 1.0):
        o = np.column_stack([np.zeros_like(ths), np.zeros_like(ths),
                             np.full_like(ths, z)])
        hits, idx, _ = ray.intersects_location(o, fan, multiple_hits=True)
        for i in range(len(ths)):
            r = np.linalg.norm(hits[idx == i][:, :2], axis=1)
            if len(r) and (inner is None or float(r.min()) < inner):
                inner = float(r.min())

    print(f"pot                {np.round(hi - lo, 2).tolist()} mm, rim at "
          f"z={rim:.2f}")
    print(f"cavity floor       z={floor:.2f}")
    print(f"floor to rim       {rim - floor:.2f}   "
          f"(params.POT_FLOOR_TO_RIM = {P.POT_FLOOR_TO_RIM})")
    print(f"socket             Ø{bore:.2f} x {floor - socket_floor:.2f} deep  "
          f"(params.POT_BORE_D = {P.POT_BORE_D}, "
          f"POT_SOCKET_DEPTH = {P.POT_SOCKET_DEPTH})")
    if inner:
        print(f"inner wall         r={inner:.2f} at its tightest   "
              f"(params.POT_INNER_R = {P.POT_INNER_R})")

    bad = []
    if abs(bore - P.POT_BORE_D) > P.POT_TOL:
        bad.append("POT_BORE_D")
    if abs((floor - socket_floor) - P.POT_SOCKET_DEPTH) > P.POT_TOL:
        bad.append("POT_SOCKET_DEPTH")
    if abs((rim - floor) - P.POT_FLOOR_TO_RIM) > P.POT_TOL:
        bad.append("POT_FLOOR_TO_RIM")
    if inner is not None and inner < P.POT_INNER_R - P.POT_TOL:
        # only a tighter wall is a problem; a roomier one is free clearance
        bad.append("POT_INNER_R")
    if bad:
        print("  MISMATCH -- update " + ", ".join(bad) + " before building")
    else:
        print("  params agree with this pot")
    return pot, floor


# ---------------------------------------------------------------------------
# stl
# ---------------------------------------------------------------------------

def build_stl():
    os.makedirs(STL, exist_ok=True)
    body, sites = C.cactus()
    out = [
        ("cactus.stl", body),
        ("spike.stl", C.spike()),
        (f"spikes-x{P.SPIKE_PLATE_N}.stl", C.spike_plate()),
        ("fit-test-coupon.stl", C.fit_coupon()),
    ]
    for name, mesh in out:
        path = os.path.join(STL, name)
        mesh.export(path)
        print(f"{name:26s} {len(mesh.faces):7d} faces  "
              f"{np.round(mesh.extents, 1).tolist()} mm")
    print(f"sockets: {len(sites)}")
    return body, sites


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def _spikes_in(sites):
    """A spike seated in every socket, for the assembled renders."""
    one = C.spike()
    out = []
    for p, n, rake, swing in sites:
        s = one.copy()
        axis = C._rake(n, rake, swing)
        m = C._frame_from_normal(axis)
        # the collar sits on the pad, so the part drops by the pin's length
        m[:3, 3] = p - axis * (P.PIN_SHANK_L - P.AREOLE_RISE * 0.25)
        s.apply_transform(m)
        out.append(s)
    return trimesh.util.concatenate(out)


def build_renders(pot=None, pot_floor=0.0):
    os.makedirs(RENDERS, exist_ok=True)
    body, sites = C.cactus()
    spikes = _spikes_in(sites)

    bare = [{"mesh": body, "color": GREEN}]
    full = [{"mesh": body, "color": GREEN},
            {"mesh": spikes, "color": SPIKE_C}]

    def shot(name, parts, az, el, margin=1.02, **kw):
        meshes = [p["mesh"] for p in parts]
        cam = R.frame(meshes, az, el, margin=margin, **kw)
        img = R.render(parts, **cam)
        img.save(os.path.join(RENDERS, name))
        print("renders/" + name)

    # The arms bear 28 and 214 degrees, so a camera near 118 looks across
    # both of them. Anything near 28 puts one arm end-on to the lens and the
    # cactus reads as a tube with a lump on it.
    shot("01-cactus-iso.png", full, 104, 20)
    shot("02-cactus-side.png", full, 118, 4)
    shot("03-cactus-bare.png", bare, 104, 20)
    shot("04-crown.png", full, 70, 56, margin=0.52)

    # a close pair on one areole: the socket, and the spike in it
    p, n, rake, swing = max(
        sites, key=lambda s: s[0][2] if s[0][2] < P.TRUNK_H * 0.6 else -1)
    for name, parts in (("05-socket-detail.png", bare),
                        ("06-spike-seated.png", full)):
        meshes = [q["mesh"] for q in parts]
        eye = p + C._rake(n, rake, swing) * 26.0 + np.array([0, 0, 4.0])
        img = R.render(parts, eye=eye, target=tuple(p), fov_deg=26.0)
        img.save(os.path.join(RENDERS, name))
        print("renders/" + name)

    # The joint, sectioned. Cutting the whole cactus in half and zooming in
    # gives a frame that is nine tenths flat cut face, so a block is taken
    # out of the wall around the socket first and that block is sectioned:
    # what is left is the wall, the bore, the pin in it and nothing else.
    axis = C._rake(n, rake, swing)
    one = C.spike()
    m = C._frame_from_normal(axis)
    m[:3, 3] = p - axis * (P.PIN_SHANK_L - P.AREOLE_RISE * 0.25)
    one.apply_transform(m)

    block = trimesh.creation.box([13.0, 13.0, 13.0])
    bm = C._frame_from_normal(axis)
    bm[:3, 3] = p - axis * 4.0
    block.apply_transform(bm)
    wall = trimesh.boolean.intersection([body, block], engine=C.ENGINE)

    view = np.cross(axis, [0, 0, 1])
    view /= np.linalg.norm(view)
    cut = []
    for mesh, colour in ((wall, GREEN), (one, SPIKE_C)):
        # keep the far half, so the camera on the near side looks straight
        # into the cut face and the bore is a hole rather than a shadow
        hb, caps = R.section(mesh, -view, p)
        cut.append({"mesh": hb, "color": colour})
        if len(caps.faces):
            cut.append({"mesh": caps, "color": R.tint(colour)})
    centre = p - axis * 0.4
    # more ambient than the other shots: the inside of a 2 mm bore gets no
    # light from either lamp, and an unlit hole is just a black smudge
    R.render(cut, eye=centre + view * 80.0, target=tuple(centre),
             ortho_height=11.0, ambient=0.52, key=0.52).save(
        os.path.join(RENDERS, "07-press-fit-section.png"))
    print("renders/07-press-fit-section.png")

    # the spike on its own, and a plate of them
    one = C.spike()
    shot("08-spike.png", [{"mesh": one, "color": SPIKE_C}], 30, 12, margin=1.1)
    plate = C.spike_plate()
    shot("09-spike-plate.png", [{"mesh": plate, "color": SPIKE_C}], 40, 34)
    coupon = C.fit_coupon()
    shot("10-fit-coupon.png", [{"mesh": coupon, "color": (0.62, 0.64, 0.70)}],
         40, 40)

    # The whole point of the exercise, if a pot was given: the cactus in it.
    # The pot mesh is translated so its cavity floor lands on z=0, which is
    # where the cactus's own soil line is.
    if pot is not None:
        seated = pot.copy()
        seated.apply_translation([0.0, 0.0, -pot_floor])
        assembly = [{"mesh": seated, "color": POT_C},
                    {"mesh": body, "color": GREEN},
                    {"mesh": spikes, "color": SPIKE_C}]
        shot("11-in-the-pot.png", assembly, 104, 12)
        shot("12-in-the-pot-side.png", assembly, 118, 2)


def main():
    args = sys.argv[1:]
    pot, floor = None, 0.0
    if "--pot" in args:
        pot, floor = measure_pot(args[args.index("--pot") + 1])
        # measuring alone is a useful thing to ask for
        if len(args) == 2:
            return
    do_stl = "--renders" not in args
    do_renders = "--stl" not in args
    if do_stl:
        build_stl()
    if do_renders:
        build_renders(pot, floor)


if __name__ == "__main__":
    main()
