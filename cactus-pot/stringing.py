"""A two-filament coupon that reproduces the cactus's stringing geometry.

    python3 stringing.py          # stl/stringing/

Why not a stringing cube. The Silk+ purple is not stringing because silk
strings; it is stringing because of what this part asks it to do. The silk
is 2.95% of the cactus by volume and 15 separate islands on every one of
1015 layers, about 6 mm of arc each with a 7 mm hop across a rib valley
between them. Most of the travel moves in the whole print belong to the
smallest, oozier third of the material. A test cube shares none of that.

So this is the real trunk's skin -- the same 15 ribs at the same depth,
split by the same two booleans into the same two solids -- on a foot shaped
like the cactus's own, with three spine sockets in it.

THE FOOT IS STYLED, NOT COPIED, and the reason is worth keeping. The real
bottom 30 mm of the cactus has nothing in it to test: the base flare runs to
z=12.9, ribs do not start until z=21.2 and reach only 42% depth by z=30, and
AREOLE_Z_MIN is 30.0, so the lowest pad the model will ever place sits
exactly at the height limit. A literal slice would be a smooth cone with no
silk and no holes. What is copied instead is the shape of the thing: a true
45 degree cone, as the trunk's own base clip makes, but starting from a
wider radius so it finishes in FOOT_H instead of 13 mm. Same first layers,
same flare, in a quarter of the height.

Everything above the foot is the real trunk sampled at Z_SRC -- its mean
radius, its rib depth, its wobble -- so the islands the printer sees are the
ones the cactus has.

One threshold, 0.15, as shipped. An earlier three-band version is in git
history at d64e112 if the geometry question comes back; it is 36 mm tall and
sweeps the threshold from 0.15 to -0.45.
"""

from __future__ import annotations

import os

import numpy as np
import trimesh

import cactus as C
import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "stringing")

TOTAL_H = 30.0             # Rob's cap
FOOT_H = 7.0               # the flared cone, as the cactus's own base
RIB_RAMP = 4.0             # over which the ribs come up out of the foot
Z_SRC = 120.0              # the height of the real trunk this copies
CREST_THRESHOLD = 0.15     # as in colours.py and colour_options.py
LAYER = 0.2                # only used to report the tool-change count

# Pads on crests 0, 5 and 10 of 15 -- 120 degrees apart, so they cannot
# interact, and climbing so each sits on a different part of the rib run.
# The top one is held at 25.0: AREOLE_R is 3.25, so its dome reaches 28.3
# and the socket's proud stub another 1.1 above that, still inside 30.
PADS = ((0, 14.0), (5, 19.5), (10, 25.0))

MEAN_R = float(C.trunk_mean_radius(np.array([Z_SRC]))[0])
R_START = MEAN_R - FOOT_H           # so the 45 degree cone lands at FOOT_H
FOOT_BIAS = 1.0
"""How much fatter the core is than the body down in the foot.

Without it the two surfaces are identical there -- the foot has no ribs, so
body and core are the same cone -- and a boolean between coincident surfaces
is how a mesh comes back with holes in it. The bias tapers out as the ribs
come up, so it is exactly zero everywhere the split actually matters, and it
makes the foot print in one colour, which is what it should do anyway.
"""


def _rib_scale(z):
    """Ribs absent in the foot, full above the ramp. The trunk's own fade."""
    return np.clip((np.asarray(z, dtype=float) - FOOT_H) / RIB_RAMP, 0.0, 1.0)


def _radius(theta, z, profile=None, bias=0.0):
    """The coupon's skin: mid-height trunk character sat on a cone.

    `profile` None means the real rib profile; pass a constant to get the
    core surface the colour split is cut against, exactly as colours.py
    holds `rib_profile` at a constant to build its own.
    """
    theta = np.asarray(theta, dtype=float)
    z = np.asarray(z, dtype=float)
    scale = _rib_scale(z)
    mean = np.minimum(MEAN_R, R_START + z)          # the 45 degree base clip
    ribs = (P.rib_profile(theta, P.RIB_COUNT, P.RIB_SHARPNESS)
            if profile is None else np.full_like(theta, float(profile)))
    wobble = P.WOBBLE_AMP * np.cos(
        theta - 2 * np.pi * P.WOBBLE_TURNS * (Z_SRC / P.TRUNK_H))
    return (mean + P.RIB_DEPTH * scale * ribs + wobble * scale
            + bias * (1.0 - scale))


def _point(theta, z, **kw):
    th = np.atleast_1d(theta)
    r = _radius(th, np.atleast_1d(z), **kw)
    return np.column_stack([r * np.cos(th), r * np.sin(th), np.atleast_1d(z)])


def _normal(theta, z, eps=1e-3):
    """Outward normal by finite difference, as cactus.trunk_normal does it."""
    th = np.atleast_1d(np.asarray(theta, dtype=float))
    zz = np.atleast_1d(np.asarray(z, dtype=float))
    p = _point(th, zz)
    dt = _point(th + eps, zz) - _point(th - eps, zz)
    dz = _point(th, zz + eps) - _point(th, zz - eps)
    n = np.cross(dt, dz)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    out = p.copy()
    out[:, 2] = 0.0
    n[np.einsum("ij,ij->i", n, out) < 0] *= -1.0
    return n


def _solid(z_lo, z_hi, **kw):
    theta = np.linspace(0.0, 2 * np.pi, P.SEG_THETA, endpoint=False)
    # dense through the ramp, where the surface is actually changing
    zs = np.unique(np.concatenate([
        np.linspace(z_lo, z_hi, 140),
        np.linspace(FOOT_H - 0.5, FOOT_H + RIB_RAMP + 0.5, 60)]))
    zs = zs[(zs >= z_lo) & (zs <= z_hi)]
    TH, Z = np.meshgrid(theta, zs)
    R = _radius(TH, Z, **kw)
    rings = np.stack([R * np.cos(TH), R * np.sin(TH), Z], axis=-1)
    return C._loft(rings, cap_bottom=True, cap_top=True)


def _sites():
    """(point, normal, rake, swing) for each spine hole, on a rib crest.

    The third field is NOT the rake. `cactus._rake` applies SPIKE_RAKE_DEG
    itself and adds this on top, so it is the per-site scatter -- the same
    thing `trunk_areoles` takes out of `_scatter`. Passing SPIKE_RAKE_DEG
    here doubles it to 68 degrees off horizontal, which is steep enough that
    the insertion sweep finds the lower side of the post still buried in the
    skin and calls every socket blocked. That is how this was caught.
    """
    jit = C._scatter(len(PADS))
    out = []
    for (crest, z), (_dz, rake, swing) in zip(PADS, jit):
        th = 2 * np.pi * crest / P.RIB_COUNT        # rib_profile peaks at 0
        out.append((_point(th, z)[0], _normal(th, z)[0],
                    float(rake), float(swing)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)

    body = _solid(0.0, TOTAL_H)
    sites = _sites()
    body = C._union([body] + [C.areole_pad(p, n) for p, n, _, _ in sites])
    body = C._difference(body, [C.socket_cutter(*s) for s in sites])
    body = C._clean(body)

    # The core runs 1 mm past the body at both ends so no cap is coplanar
    # with one of the body's -- the same reason FOOT_BIAS exists.
    core = _solid(-1.0, TOTAL_H + 1.0, profile=CREST_THRESHOLD,
                  bias=FOOT_BIAS)

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
          f"{(hollow.volume + crest.volume) / 1000:7.2f} cm3 against a coupon "
          f"of {body.volume / 1000:.2f} -- {gap / 1000:+.3f} cm3")
    if abs(gap) > 0.2 * 1000:
        print("  MISMATCH -- the parts do not add up to the whole")

    _report(body, sites)


def _report(body, sites):
    e = body.extents
    print(f"\ncoupon {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm, "
          f"{e[2] / LAYER:.0f} layers at {LAYER} mm")
    if e[2] > TOTAL_H + 0.01:
        print(f"  OVER HEIGHT -- {e[2]:.2f} mm against a cap of {TOTAL_H}")
    print(f"foot  Ø{2 * R_START:.1f} at the bed, flaring at 45° to "
          f"Ø{2 * (MEAN_R + P.RIB_DEPTH / 2):.1f} by z={FOOT_H:.0f}")

    # The island count and arc width, taken from rib_profile rather than
    # measured off the mesh. A first attempt clustered the silk part's
    # vertices by angle in a thin band of height; it reported 0.0 mm for one
    # band and could not find another, because the vertices bunch wherever
    # the surface changes. The profile is what the geometry is built from.
    th = np.linspace(0.0, 2 * np.pi, 20001)[:-1]
    on = P.rib_profile(th, P.RIB_COUNT, P.RIB_SHARPNESS) > CREST_THRESHOLD
    n = int(np.count_nonzero(on != np.roll(on, 1))) // 2
    circ = 2 * np.pi * float(_radius(th, np.full_like(th, 20.0)).mean())
    frac = float(on.mean())
    print(f"ribs  {n} silk islands per layer above z={FOOT_H + RIB_RAMP:.0f}, "
          f"{circ * frac / n:.1f} mm of arc each, "
          f"{circ * (1 - frac) / n:.1f} mm hop between")

    print(f"holes {len(sites)} sockets, Ø{P.SOCKET_D:.2f} x "
          f"{P.SOCKET_DEPTH:.2f} deep -- the same spine as the cactus, "
          f"stl/spike.stl")
    for i, s in enumerate(sites):
        p = s[0]
        lean = np.degrees(np.arcsin(np.clip(C._rake(*s[1:])[2], -1, 1)))
        print(f"      {i + 1}: z {p[2]:5.1f} mm, bearing "
              f"{np.degrees(np.arctan2(p[1], p[0])) % 360:5.1f}°, "
              f"leaning {lean:4.1f}° above horizontal")
        if abs(lean - P.SPIKE_RAKE_DEG) > P.SPIKE_RAKE_SCATTER + 1.0:
            print(f"         WRONG LEAN -- SPIKE_RAKE_DEG is "
                  f"{P.SPIKE_RAKE_DEG:.0f}; the site's third field is the "
                  f"scatter on top of it, not the rake")
    ok = C._insertable(body, sites)
    print(f"      a spine can be got into {int(sum(ok))} of {len(sites)}")
    if not all(ok):
        print("         BLOCKED -- a socket nothing fits is not a test")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
