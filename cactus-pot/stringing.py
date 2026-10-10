"""A two-filament coupon that reproduces the cactus's stringing geometry.

    python3 stringing.py          # stl/stringing/

Why not a stringing cube. The Silk+ purple is not stringing because silk
strings; it is stringing because of what this part asks it to do. The silk
is 2.95% of the cactus by volume and 15 separate islands on every one of
1015 layers, each about 6 mm of arc, with a travel across a rib valley
between every pair. Most of the travel moves in the whole print belong to
the 3% of it that is silk. A test cube shares none of that.

So this is the real trunk, cut to a short band at mid height, split into the
same two solids by the same two booleans -- the printer sees the same island
count, the same arc widths, the same hop distances.

Three bands, stacked, differing only in where the crest/hollow cut is made:

    bottom   CREST_THRESHOLD  0.15   as shipped: 6.0 mm of silk, 7.0 mm hop
    middle                   -0.25                 7.8 mm silk, 5.3 mm hop
    top                      -0.45                10.6 mm silk, 2.4 mm hop

Bottom to top the silk stripe widens and the hop between islands shortens
by about 3x, which is the thing worth knowing if drying does not settle it:
a wider island is a longer extrusion with a shorter hop, and it is the ratio
between those two that makes hairs. If the top band strings as badly as the
bottom one, geometry is not the answer and no amount of widening will help.

These three are spread across the usable range on purpose. A first draft
used 0.15 / 0.00 / -0.15, which measured 6.0 / 6.5 / 7.0 mm -- three bands
that differ by a tenth of nothing, because the profile is steep through its
middle and the threshold barely moves the cut there. It only bites past
-0.25. No labels are engraved -- the stripe width IS the label, in order.

What is deliberately left out: the arms, the areole pads and their sockets.
Pads do add a few islands, but they are not where the travel is, and leaving
them off keeps the coupon to one clean column that cannot fail for a reason
unrelated to the question.
"""

from __future__ import annotations

import os

import numpy as np
import trimesh

import cactus as C
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "stringing")

Z0 = 96.0                  # mid height, clear of the base flare and the crown
BAND_H = 12.0              # each threshold gets this much
BANDS = ((0.15, "as shipped"), (-0.25, "wider"), (-0.45, "widest"))
LAYER = 0.2                # only used to report the tool-change count


def _slab(z_lo, z_hi, r=200.0):
    """A box big enough in xy to cut the column, exact in z."""
    box = trimesh.creation.box(extents=[2 * r, 2 * r, z_hi - z_lo])
    box.apply_translation([0.0, 0.0, 0.5 * (z_lo + z_hi)])
    return box


def _trunk_at(threshold):
    """The trunk with its rib profile held at a constant -- the core solid.

    Same trick colours.py uses: every other term (mean radius, the rib
    scaling at crown and root, the wobble) is left exactly as the real body
    has it, so this tracks the trunk rather than approximating it.
    """
    original = P.rib_profile
    P.rib_profile = lambda theta, count, sharpness: np.full_like(
        np.asarray(theta, dtype=float), threshold)
    try:
        return C.trunk_body()
    finally:
        P.rib_profile = original


def main():
    os.makedirs(OUT, exist_ok=True)
    z_top = Z0 + BAND_H * len(BANDS)

    body = trimesh.boolean.intersection(
        [C.trunk_body(), _slab(Z0, z_top)], engine=C.ENGINE)

    # one core per band, each clipped to its own slice of height
    cores = []
    for i, (k, _) in enumerate(BANDS):
        lo = Z0 + i * BAND_H
        cores.append(trimesh.boolean.intersection(
            [_trunk_at(k), _slab(lo, lo + BAND_H)], engine=C.ENGINE))
    core = C._union(cores)

    # NOT run through C._clean(): it drops faces it judges degenerate, and on
    # a cut surface made almost entirely of slivers that tears the mesh. The
    # round trip below is the check that matters, not is_watertight in memory.
    hollow = trimesh.boolean.intersection([body, core], engine=C.ENGINE)
    crest = trimesh.boolean.difference([body, core], engine=C.ENGINE)

    for name, mesh in (("01-hollow-indigo", hollow), ("02-crest-silk", crest)):
        path = os.path.join(OUT, f"{name}.stl")
        mesh.export(path)
        drift = trimesh.load(path, force="mesh").volume - mesh.volume
        print(f"{name:20s} {mesh.volume / 1000:7.2f} cm3  "
              f"{len(mesh.faces):7d} faces  "
              f"volume after a round trip {drift / 1000:+.4f} cm3")
        if abs(drift) > 0.5:
            print("  MISMATCH -- the file does not enclose what was built")

    gap = hollow.volume + crest.volume - body.volume
    print(f"\n{'the two together':20s} "
          f"{(hollow.volume + crest.volume) / 1000:7.2f} cm3 against a column "
          f"of {body.volume / 1000:.2f} -- {gap / 1000:+.3f} cm3")
    if abs(gap) > 0.5 * 1000:
        print("  MISMATCH -- the parts do not add up to the whole")

    e = body.extents
    print(f"\ncolumn {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm, "
          f"{e[2] / LAYER:.0f} layers at {LAYER} mm")
    _report_islands()


def _report_islands():
    """Island count and arc width per band -- the number the coupon varies.

    Taken from `rib_profile` directly rather than measured off the mesh. A
    first attempt sampled the silk part's vertices in a thin band of height
    and clustered them by angle; it reported 0.0 mm for one band and could
    not find the next, because the vertices bunch at the band boundaries and
    a 0.3 mm window catches a joining ring or nothing at all. The profile is
    what the geometry is built from, so ask it: the crest is exactly where
    the profile stands above the threshold.
    """
    th = np.linspace(0.0, 2 * np.pi, 20001)[:-1]
    prof = P.rib_profile(th, P.RIB_COUNT, P.RIB_SHARPNESS)
    print(f"\n{'band':12s} {'threshold':>10s} {'islands':>8s} "
          f"{'arc each':>10s} {'hop between':>13s}")
    for i, (k, label) in enumerate(BANDS):
        z = Z0 + (i + 0.5) * BAND_H
        r = float(C.trunk_radius(th, np.full_like(th, z)).mean())
        on = prof > k
        if not on.any() or on.all():
            print(f"{label:12s} {k:10.2f}   the cut falls outside the "
                  f"profile -- one colour only")
            continue
        # contiguous runs round the circle, counted on the wrapped array
        edges = int(np.count_nonzero(on != np.roll(on, 1))) // 2
        frac = float(on.mean())
        circ = 2 * np.pi * r
        print(f"{label:12s} {k:10.2f} {edges:8d} "
              f"{circ * frac / edges:7.1f} mm {circ * (1 - frac) / edges:10.1f} mm")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
