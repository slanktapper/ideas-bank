"""Split the cactus into its colour parts, as separate solids to load in Studio.

    python3 colours.py            # stl/colour/

`colour_options.py` picks the scheme and draws pictures of it; it classifies
FACES, which is fine for a render and useless for a printer. This writes
bodies: watertight solids that go into the slicer as parts of one object,
each assigned a filament — the arrangement the pot already uses in
`pot/colours.py`.

Scheme B2, the one Rob chose:

    01-hollow-indigo   PLA Basic Indigo Purple   the rib valleys
    02-crest-silk      PLA Silk+ Purple          the rib crests
    the spines         GEEETECH silk silver      already a separate print,
                       `stl/spikes-x72.stl`

How the cut is made. `rib_profile` runs -0.5 to +0.5 about the mean radius,
so crest and hollow are simply the material outside and inside a surface
near that mean. Build that surface as its own closed solid -- the same
trunk and arms with the rib profile held at a constant instead of a cosine
-- and the split is two booleans:

    hollow = cactus ∩ core
    crest  = cactus − core

Which is worth doing properly rather than splitting faces into two open
shells: those have no inside, and a slicer is entitled to make nonsense of
them. These two are closed solids and add back up to the cactus, which the
run checks.

The constant is 0.15, matching the threshold `colour_options.py` uses to
call a face a crest, so the print matches the render rather than being an
even split.
"""

from __future__ import annotations

import os

import numpy as np
import trimesh

import cactus as C
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "colour")

CREST_THRESHOLD = 0.15      # as in colour_options.py


def core_body():
    """The surface between crest and hollow, as a closed solid.

    Built by holding the rib profile at a constant: every other term --
    the mean radius, the rib scaling at crown and root, the wobble, the arm
    flare -- is left exactly as the real body has it, so this tracks the
    cactus rather than approximating it.
    """
    original = P.rib_profile
    P.rib_profile = lambda theta, count, sharpness: np.full_like(
        np.asarray(theta, dtype=float), CREST_THRESHOLD)
    try:
        core = C._union([C.trunk_body()]
                        + [C.arm_body(spec) for spec in P.ARMS])
        core = C.relax_arm_seams(core)
    finally:
        P.rib_profile = original
    return core


def main():
    os.makedirs(OUT, exist_ok=True)
    body, sites = C.cactus()
    core = core_body()

    # NOT run through C._clean(). It drops faces it judges degenerate, and
    # on these two that tears the mesh: the hollow went from a watertight
    # 220766-face solid to a broken 218897-face one. Removing a zero-area
    # triangle from a closed surface leaves a zero-width crack, which is a
    # hole -- harmless on the test tabs, fatal on a cut surface made almost
    # entirely of slivers.
    hollow = trimesh.boolean.intersection([body, core], engine=C.ENGINE)
    crest = trimesh.boolean.difference([body, core], engine=C.ENGINE)

    # These are watertight manifolds in memory -- every edge on exactly two
    # faces -- but the cut surface touches itself at a few hundred points,
    # where two distinct vertices share one position. An STL is a triangle
    # soup, so reloading merges those by position and the strict watertight
    # test then fails on about half a percent of edges. It is a pinch, not a
    # hole: what matters is that the enclosed volume survives the trip
    # unchanged, which is what gets checked below.
    for name, mesh in (("01-hollow-indigo", hollow), ("02-crest-silk", crest)):
        path = os.path.join(OUT, f"{name}.stl")
        mesh.export(path)
        reloaded = trimesh.load(path, force="mesh")
        drift = reloaded.volume - mesh.volume
        print(f"{name:20s} {mesh.volume / 1000:8.2f} cm3  "
              f"{len(mesh.faces):7d} faces  "
              f"manifold in memory {mesh.is_watertight}  "
              f"volume after a round trip {drift / 1000:+.4f} cm3")
        if abs(drift) > 1.0:
            print("  MISMATCH -- the file does not enclose what was built")

    total = hollow.volume + crest.volume
    gap = total - body.volume
    print(f"\n{'the two together':20s} {total / 1000:8.2f} cm3 against a "
          f"cactus of {body.volume / 1000:.2f} -- {gap / 1000:+.3f} cm3")
    if abs(gap) > 0.5 * 1000:
        print("  MISMATCH -- the parts do not add up to the whole")
    print(f"\nthe spines are the third filament and print on their own: "
          f"stl/spikes-x{P.SPIKE_PLATE_N}.stl ({len(sites)} needed)")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
