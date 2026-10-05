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

    The pot is a mesh, not source, so its mouth is measured rather than read:
    slice it just below the rim and take the inner loop's radius.
    """
    pot = trimesh.load(path, force="mesh")
    lo, hi = pot.bounds
    print(f"pot bounds      {np.round(lo, 2).tolist()} .. {np.round(hi, 2).tolist()}")
    print(f"pot height      {hi[2] - lo[2]:.2f}")
    z = hi[2] - 2.0
    sec = pot.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        print("no section at the rim -- measure it by hand")
        return None
    planar, _ = sec.to_2D()
    radii = [np.linalg.norm(e.discrete(planar.vertices), axis=1)
             for e in planar.entities]
    rings = sorted(float(np.mean(r)) for r in radii)
    print(f"rim rings at z={z:.1f}: " +
          ", ".join(f"Ø{2 * r:.2f}" for r in rings))
    if len(rings) >= 2:
        bore = 2 * rings[0]
        print(f"measured bore   Ø{bore:.2f}   (params.POT_BORE_D = {P.POT_BORE_D})")
        if abs(bore - P.POT_BORE_D) > P.POT_TOL:
            print("  MISMATCH -- update params.POT_BORE_D before building")
        return bore
    return None


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


def build_renders():
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


def main():
    args = sys.argv[1:]
    if "--pot" in args:
        measure_pot(args[args.index("--pot") + 1])
        return
    do_stl = "--renders" not in args
    do_renders = "--stl" not in args
    if do_stl:
        build_stl()
    if do_renders:
        build_renders()


if __name__ == "__main__":
    main()
