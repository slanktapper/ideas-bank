"""The geometry: a ribbed cactus with spike sockets, and the spike itself.

Built as lofted surfaces rather than as a stack of booleaned primitives. A
cactus is one continuous skin whose radius varies with both height and
bearing -- ribs, taper, swell and asymmetry are all the same function -- and
writing it that way means the ribs are genuinely part of the body instead of
grooves cut into a tube afterwards. Only the things that are topologically
separate from the skin get booleaned: the apical dimple, the arms, the
areole pads and the sockets.

Everything takes its numbers from params.py. Nothing here hardcodes a
dimension.
"""

from __future__ import annotations

import numpy as np
import trimesh

import params as P

ENGINE = "manifold"


# ---------------------------------------------------------------------------
# mesh helpers
# ---------------------------------------------------------------------------

def _loft(rings: np.ndarray, cap_bottom=True, cap_top=True) -> trimesh.Trimesh:
    """Stitch an (n_rings, n_theta, 3) stack of closed rings into a solid.

    Caps are fans to the ring's own centroid rather than a single vertex, so a
    cap stays flat when the ring is not a circle -- which, with ribs, it never
    is.
    """
    n_r, n_t, _ = rings.shape
    verts = [rings.reshape(-1, 3)]
    faces = []

    idx = np.arange(n_r * n_t).reshape(n_r, n_t)
    a = idx[:-1, :]
    b = idx[:-1, (np.arange(n_t) + 1) % n_t]
    c = idx[1:, (np.arange(n_t) + 1) % n_t]
    d = idx[1:, :]
    faces.append(np.column_stack([a.ravel(), b.ravel(), c.ravel()]))
    faces.append(np.column_stack([a.ravel(), c.ravel(), d.ravel()]))

    nxt = n_r * n_t
    if cap_bottom:
        centre = rings[0].mean(axis=0)
        verts.append(centre[None, :])
        ring = idx[0]
        faces.append(np.column_stack([
            np.full(n_t, nxt), ring[(np.arange(n_t) + 1) % n_t], ring]))
        nxt += 1
    if cap_top:
        centre = rings[-1].mean(axis=0)
        verts.append(centre[None, :])
        ring = idx[-1]
        faces.append(np.column_stack([
            np.full(n_t, nxt), ring, ring[(np.arange(n_t) + 1) % n_t]]))
        nxt += 1

    mesh = trimesh.Trimesh(vertices=np.vstack(verts),
                           faces=np.vstack(faces), process=True)
    mesh.fix_normals()
    return mesh


def _union(meshes):
    meshes = [m for m in meshes if m is not None and len(m.faces)]
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.boolean.union(meshes, engine=ENGINE)


def _difference(base, cutters):
    cutters = [m for m in cutters if m is not None and len(m.faces)]
    if not cutters:
        return base
    return trimesh.boolean.difference([base] + cutters, engine=ENGINE)


def _frame_from_normal(n):
    """An orthonormal frame whose +Z is `n`, for placing a part on a surface."""
    n = np.asarray(n, dtype=float)
    n = n / np.linalg.norm(n)
    helper = np.array([0.0, 0.0, 1.0])
    if abs(n @ helper) > 0.95:
        helper = np.array([1.0, 0.0, 0.0])
    u = np.cross(helper, n)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = u, v, n
    return m


# ---------------------------------------------------------------------------
# the trunk's radius field
# ---------------------------------------------------------------------------

def trunk_mean_radius(z: np.ndarray) -> np.ndarray:
    """Mean radius up the column: base -> low swell -> tapered shoulder.

    Two smooth arcs rather than one, because a single curve from base to top
    either loses the swell or puts it halfway up, and halfway up is where a
    cartoon cactus bulges.
    """
    t = np.clip(z / P.TRUNK_H, 0.0, 1.0)
    m = P.TRUNK_MID_FRAC
    lower = t < m
    r = np.empty_like(t)

    # base -> swell: ease out
    u = np.where(lower, t / m, 0.0)
    r_low = P.TRUNK_R_BASE + (P.TRUNK_R_MID - P.TRUNK_R_BASE) * np.sin(u * np.pi / 2)

    # swell -> shoulder: a smoothstep, flattening as it reaches the top
    w = np.where(lower, 0.0, (t - m) / (1.0 - m))
    s = w * w * (3 - 2 * w)
    r_high = P.TRUNK_R_MID + (P.TRUNK_R_TOP - P.TRUNK_R_MID) * s

    r[:] = np.where(lower, r_low, r_high)
    return r


def _rib_scale(z: np.ndarray) -> np.ndarray:
    """How much of RIB_DEPTH is present at this height.

    Nothing below the top of the base flare: ribs on a cone that is still
    growing would be chased by the clip and come out as a frill.
    """
    t = np.clip(z / P.TRUNK_H, 0.0, 1.0)
    flare_top = (P.TRUNK_R_BASE - P.SPIGOT_R) / P.TRUNK_H
    base = np.clip((t - flare_top - P.RIB_FADE_BASE) / 0.10, 0.0, 1.0)
    top = np.clip((1.0 - t) / (1.0 - P.RIB_FADE_TOP), 0.0, 1.0)
    return base * (top ** 0.8)


def trunk_radius(theta: np.ndarray, z: np.ndarray) -> np.ndarray:
    """The skin: mean radius, plus ribs, plus a slow asymmetric wobble.

    The mean is clipped by a 45-degree cone rising off the spigot. The trunk
    is 26 mm in radius and the spigot is 15.65, so without it the part has a
    10 mm flat ledge round its first layer -- an overhang the printer would
    have to bridge over nothing. The cone spends the first 10 mm of height
    growing out to full width instead, which is both printable and what a
    cactus does where it leaves the soil. All of it is hidden inside the pot.
    """
    t = np.clip(z / P.TRUNK_H, 0.0, 1.0)
    mean = np.minimum(trunk_mean_radius(z), P.SPIGOT_R + np.maximum(z, 0.0))
    twist = np.radians(P.RIB_TWIST_DEG) * t
    ribs = P.rib_profile(theta + twist, P.RIB_COUNT, P.RIB_SHARPNESS)
    wobble = P.WOBBLE_AMP * np.cos(theta - 2 * np.pi * P.WOBBLE_TURNS * t)
    return mean + P.RIB_DEPTH * _rib_scale(z) * ribs + wobble * (0.35 + 0.65 * t)


def trunk_point(theta, z):
    r = trunk_radius(np.atleast_1d(theta), np.atleast_1d(z))
    th = np.atleast_1d(theta)
    return np.column_stack([r * np.cos(th), r * np.sin(th), np.atleast_1d(z)])


def trunk_normal(theta, z, eps=1e-3):
    """Outward normal by finite difference on the parametric surface."""
    th = np.atleast_1d(np.asarray(theta, dtype=float))
    zz = np.atleast_1d(np.asarray(z, dtype=float))
    p = trunk_point(th, zz)
    dt = trunk_point(th + eps, zz) - trunk_point(th - eps, zz)
    dz = trunk_point(th, zz + eps) - trunk_point(th, zz - eps)
    n = np.cross(dt, dz)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    # cross(dtheta, dz) points inwards for this winding; flip it
    out = p.copy()
    out[:, 2] = 0.0
    flip = np.einsum("ij,ij->i", n, out) < 0
    n[flip] *= -1.0
    return n


# ---------------------------------------------------------------------------
# trunk solid
# ---------------------------------------------------------------------------

def trunk_body() -> trimesh.Trimesh:
    """The column, with its spigot below the soil line and a crowned top."""
    theta = np.linspace(0.0, 2 * np.pi, P.SEG_THETA, endpoint=False)

    spigot_r = P.SPIGOT_R
    rings = []

    # --- the spigot: a plain cylinder with a chamfered lead-in, below z=0.
    #     It stops at z=0, which is the pot's inner floor; the trunk's own
    #     base flare takes over from there. Every ring's z is distinct: two
    #     rings at the same height make a zero-area band, which trimesh drops
    #     and leaves a hole behind.
    z0 = -P.SPIGOT_H
    for z, r in ((z0, spigot_r - P.SPIGOT_CHAMFER),
                 (z0 + P.SPIGOT_CHAMFER, spigot_r),
                 (-0.30, spigot_r)):
        rings.append(np.column_stack([
            r * np.cos(theta), r * np.sin(theta), np.full_like(theta, z)]))

    # --- the column itself
    zs = np.linspace(0.0, P.TRUNK_H, P.SEG_Z)
    TH, Z = np.meshgrid(theta, zs)
    R = trunk_radius(TH, Z)
    rings.append(np.stack([R * np.cos(TH), R * np.sin(TH), Z], axis=-1))

    # --- the crown: a flattened dome over the shoulder, closing to a disc
    r_top = trunk_radius(theta, np.full_like(theta, P.TRUNK_H))
    flat = P.CROWN_FLAT_FRAC
    for u in np.linspace(0.0, 1.0, 26)[1:]:
        # ellipse quadrant: radius shrinks as the crown rises
        rr = r_top * (flat + (1 - flat) * np.cos(u * np.pi / 2))
        zz = P.TRUNK_H + P.CROWN_RISE * np.sin(u * np.pi / 2)
        rings.append(np.column_stack([
            rr * np.cos(theta), rr * np.sin(theta), np.full_like(theta, zz)]))

    stack = np.concatenate([r if r.ndim == 3 else r[None, ...] for r in rings],
                           axis=0)
    body = _loft(stack, cap_bottom=True, cap_top=True)

    # --- the apical depression, scooped out of the crown
    dimple = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    dimple.apply_scale([r_top.mean() * flat * 1.45,
                        r_top.mean() * flat * 1.45,
                        P.CROWN_DIMPLE * 2.2])
    dimple.apply_translation([0.0, 0.0, P.TRUNK_H + P.CROWN_RISE
                              + P.CROWN_DIMPLE * 2.2 - P.CROWN_DIMPLE])
    return _difference(body, [dimple])


# ---------------------------------------------------------------------------
# arms
# ---------------------------------------------------------------------------

def _arm_spine(spec):
    """Centreline of an arm: out of the trunk, elbow, then up.

    A quadratic Bezier from the trunk wall to a point above and outside it.
    `elbow` slides the control point between 'bends straight away' and 'runs
    out level then turns'; `rise` is how close to vertical the tip ends up.
    """
    bearing = np.radians(spec["bearing"])
    z_root = spec["z_frac"] * P.TRUNK_H
    r_root = trunk_mean_radius(np.array([z_root]))[0] - 2.0
    out = np.array([np.cos(bearing), np.sin(bearing), 0.0])

    p0 = out * r_root + np.array([0, 0, z_root])
    L = spec["length"]
    ctrl = p0 + out * L * spec["elbow"] + np.array([0, 0, L * 0.12])
    p2 = (p0 + out * L * (1.0 - 0.45 * spec["rise"])
          + np.array([0, 0, L * spec["rise"]]))

    u = np.linspace(0.0, 1.0, 64)[:, None]
    pts = (1 - u) ** 2 * p0 + 2 * (1 - u) * u * ctrl + u ** 2 * p2
    return pts


def arm_rings(spec):
    """Ribbed cross sections swept along the arm's spine."""
    pts = _arm_spine(spec)
    tang = np.gradient(pts, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)

    theta = np.linspace(0.0, 2 * np.pi, P.SEG_THETA // 2, endpoint=False)
    ribs = P.rib_profile(theta, P.ARM_RIB_COUNT, P.RIB_SHARPNESS)

    n_pts = len(pts)
    rings = np.empty((n_pts, len(theta), 3))
    up = np.array([0.0, 0.0, 1.0])
    for i, (p, t) in enumerate(zip(pts, tang)):
        u = np.cross(up, t)
        if np.linalg.norm(u) < 1e-6:
            u = np.array([1.0, 0.0, 0.0])
        u /= np.linalg.norm(u)
        v = np.cross(t, u)
        s = i / (n_pts - 1)

        # a root flare for the fillet into the trunk, and a rounded tip
        flare = P.ARM_BLEND * np.exp(-(s / 0.10) ** 2)
        tip = np.sqrt(max(1e-9, 1.0 - max(0.0, (s - 0.86) / 0.14) ** 2))
        r = (spec["r"] * (1.0 - 0.22 * s) + flare) * tip
        rib_scale = np.clip(min(s / 0.14, (1 - s) / 0.10), 0.0, 1.0)
        rr = r + P.ARM_RIB_DEPTH * rib_scale * ribs
        rings[i] = p + rr[:, None] * u[None, :] + 0.0 * v
        rings[i] = (p[None, :]
                    + (rr * np.cos(theta))[:, None] * u[None, :]
                    + (rr * np.sin(theta))[:, None] * v[None, :])
    return rings, pts, tang


def arm_body(spec) -> trimesh.Trimesh:
    rings, _, _ = arm_rings(spec)
    return _loft(rings, cap_bottom=True, cap_top=True)


# ---------------------------------------------------------------------------
# areoles and sockets
# ---------------------------------------------------------------------------

def _poisson_crest_sites():
    """Pad sites on the trunk as (bearing, height), scattered over all ribs.

    This replaced a per-rib run of pads, and the reason is Rob's second
    complaint. Giving each rib its own starting height fixed the rows; it
    could not fix the columns, because a pad still belonged to a rib, so
    every rib carrying pads was a vertical line of them and the eye read the
    lines. Wandering a pad a few degrees off its own crest only made each
    line wobble -- measured, +/-4.6 degrees is +/-2.2 mm against a 11.3 mm
    gap to the next rib, which is not enough to stop being a line.

    So a pad no longer belongs to a rib. A crest and a height are drawn
    together and kept only if the pad is AREOLE_MIN_SEP from every pad
    already placed, until the surface will not take another. Every crest is
    in the draw, not every other one, and nothing decides in advance how many
    pads a crest gets -- which is what stops them being columns. The pad is
    still ON a crest, because that is where an areole grows and where the
    socket has a flat top to be bored into.

    Drawing until it is full rather than to a count means AREOLE_MIN_SEP sets
    the spine count. That is the honest dial: spacing is the thing with a
    physical meaning, and the count follows from it.
    """
    rng = np.random.default_rng(P.SEED + 611953)
    crest_thetas = np.arange(P.RIB_COUNT) * 2 * np.pi / P.RIB_COUNT
    z_lo, z_hi = P.AREOLE_Z_MIN, P.TRUNK_H * P.AREOLE_CROWN_KEEP
    sites, pts, misses = [], [], 0
    per_crest = {k: [] for k in range(P.RIB_COUNT)}
    while misses < P.AREOLE_FILL_TRIES:
        k = int(rng.integers(P.RIB_COUNT))
        z = float(rng.uniform(z_lo, z_hi))
        th0 = crest_thetas[k] + np.radians(
            rng.uniform(-P.AREOLE_TH_SCATTER, P.AREOLE_TH_SCATTER))
        th = th0 - np.radians(P.RIB_TWIST_DEG) * z / P.TRUNK_H
        p = trunk_point(th, z)[0]
        if pts and np.min(np.linalg.norm(np.array(pts) - p, axis=1)) \
                < P.AREOLE_MIN_SEP:
            misses += 1
            continue
        if not _ladder_ok(per_crest[k], z):
            misses += 1
            continue
        misses = 0
        pts.append(p)
        per_crest[k].append(z)
        sites.append((th0, z))
    return sites


def _ladder_ok(zs: list, z: float) -> bool:
    """Would adding z give three evenly spaced pads up this one crest?

    Spacing alone does not rule this out, and it happens: two pads both
    landing at exactly AREOLE_MIN_SEP from the one between them is three in a
    line with identical gaps, which is a column in miniature and the eye
    finds it.
    """
    run = sorted(zs + [z])
    for i in range(len(run) - 2):
        a, b, c = run[i:i + 3]
        if abs((b - a) - (c - b)) < P.AREOLE_LADDER_TOL:
            return False
    return True


def trunk_areoles():
    """Every socket site on the trunk, sitting on the rib crests.

    Each site is (point, normal, rake, swing). Where the sites come from is
    `_poisson_crest_sites`. The crest is followed up the twist, so a pad
    stays on top of its rib instead of sliding into the valley by the time it
    reaches the shoulder.
    """
    raw = _poisson_crest_sites()
    jit = _scatter(len(raw))
    out = []
    # no z jitter here: the height came out of a continuous draw already, and
    # nudging it afterwards is exactly what would undo the spacing the draw
    # was rejected on. The rake and swing still vary per spike.
    for (th0, zz), (_dz, rake, swing) in zip(raw, jit):
        t = zz / P.TRUNK_H
        th = th0 - np.radians(P.RIB_TWIST_DEG) * t
        out.append((trunk_point(th, zz)[0], trunk_normal(th, zz)[0],
                    float(rake), float(swing)))
    return out


def arm_areoles(spec):
    """(point, normal, rake, swing) on the crests of one arm.

    Drawn the same way as the trunk, and for the same reason: an arm laid out
    per rib wore its own lines of spines down the crests, which is what Rob
    was looking at when he said the main body and both sides had them. Every
    crest is in the draw, the pad is kept only if it clears the pads already
    on this arm by ARM_AREOLE_MIN_SEP and does not make three evenly spaced
    pads along one crest, and the draw runs until the arm is full. Each arm
    seeds from its own bearing, so the two do not share an arrangement with
    each other or with the trunk.
    """
    rings, pts, tang = arm_rings(spec)
    n_pts = len(pts)
    arc = np.concatenate([[0.0], np.cumsum(
        np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    theta = np.linspace(0.0, 2 * np.pi, P.SEG_THETA // 2, endpoint=False)
    crest_idx = [int(round(j * len(theta) / P.ARM_RIB_COUNT))
                 % len(theta) for j in range(P.ARM_RIB_COUNT)]
    step_deg = 360.0 / len(theta)   # one ring vertex, in degrees of bearing
    s_lo, s_hi = 9.0, arc[-1] - 4.0

    def point_at(ti, ss):
        """Surface point at a fractional crest index and an arc length."""
        i = min(max(int(np.searchsorted(arc, ss)), 1), n_pts - 2)
        # ti is fractional, so walk round the closed ring between the two
        # vertices either side of it. At one vertex per 3 degrees the chord
        # sits about 4 microns inside the surface, which is nothing.
        j0 = int(np.floor(ti)) % len(theta)
        j1 = (j0 + 1) % len(theta)
        f = float(ti - np.floor(ti))
        return i, rings[i, j0] * (1.0 - f) + rings[i, j1] * f

    rng = np.random.default_rng(P.SEED + 86243 * (1 + int(spec["bearing"])))
    sites, placed, misses = [], [], 0
    per_crest = {k: [] for k in range(P.ARM_RIB_COUNT)}
    while misses < P.AREOLE_FILL_TRIES:
        k = int(rng.integers(P.ARM_RIB_COUNT))
        ss = float(rng.uniform(s_lo, s_hi))
        ti = crest_idx[k] + rng.uniform(
            -P.AREOLE_TH_SCATTER, P.AREOLE_TH_SCATTER) / step_deg
        _, p = point_at(ti, ss)
        if placed and np.min(np.linalg.norm(np.array(placed) - p, axis=1)) \
                < P.ARM_AREOLE_MIN_SEP:
            misses += 1
            continue
        if not _ladder_ok(per_crest[k], ss):
            misses += 1
            continue
        misses = 0
        placed.append(p)
        per_crest[k].append(ss)
        sites.append((ti, ss))

    jit = _scatter(len(sites))
    out = []
    for (ti, ss), (_ds, rake, swing) in zip(sites, jit):
        i, p = point_at(ti, ss)
        # normal: radially out from the spine at that station
        n = p - pts[i]
        n -= tang[i] * (n @ tang[i])
        n /= np.linalg.norm(n)
        out.append((p, n, float(rake), float(swing)))
    return out


def _rotate(v, axis, deg):
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return c * v + s * np.cross(axis, v) + (1 - c) * (axis @ v) * axis


def _rake(n, extra=0.0, swing=0.0):
    """Tilt a surface normal up towards vertical, and swing it sideways.

    Spines on a saguaro point up and out, never straight out, and no two of
    them agree on by how much. The lean is SPIKE_RAKE_DEG plus whatever
    scatter the site carries; the swing turns the spike about its own pad so
    a rib does not read as a row of identical pins.
    """
    n = np.asarray(n, dtype=float)
    n = n / np.linalg.norm(n)
    up = np.array([0.0, 0.0, 1.0])
    axis = np.cross(n, up)
    if np.linalg.norm(axis) < 1e-9:
        return n
    out = _rotate(n, axis, P.SPIKE_RAKE_DEG + extra)
    if swing:
        out = _rotate(out, up, swing)
    return out / np.linalg.norm(out)


def _scatter(n):
    """Deterministic per-site (z offset, rake, swing) jitter.

    The z offset is no longer used by anything: both the trunk and the arms
    draw a pad's position continuously now, and nudging it afterwards would
    undo the spacing the draw was rejected on. It is still drawn, because
    dropping it would shift every rake and swing after it and move every
    socket in the model for no reason.
    """
    rng = np.random.default_rng(P.SEED)
    return np.column_stack([
        rng.uniform(-P.AREOLE_Z_SCATTER, P.AREOLE_Z_SCATTER, n),
        rng.uniform(-P.SPIKE_RAKE_SCATTER, P.SPIKE_RAKE_SCATTER, n),
        rng.uniform(-P.SPIKE_SWING_SCATTER, P.SPIKE_SWING_SCATTER, n),
    ])


def areole_pad(p, n) -> trimesh.Trimesh:
    """The woolly pad: a squashed dome on the skin."""
    pad = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    pad.apply_scale([P.AREOLE_R, P.AREOLE_R, P.AREOLE_RISE * 2.0])
    m = _frame_from_normal(n)
    m[:3, 3] = p - n * P.AREOLE_RISE   # so the dome's pole lands
    #                                   exactly AREOLE_RISE proud of the skin
    pad.apply_transform(m)
    return pad


def socket_cutter(p, n, rake=0.0, swing=0.0) -> trimesh.Trimesh:
    """Bore, countersunk mouth and debris relief, aimed along the raked axis."""
    axis = _rake(n, rake, swing)
    d = P.SOCKET_D
    depth = P.SOCKET_DEPTH

    parts = []
    bore = trimesh.creation.cylinder(radius=d / 2, height=depth,
                                     sections=P.SEG_SOCKET)
    bore.apply_translation([0, 0, -depth / 2 + 1e-6])
    parts.append(bore)

    relief = trimesh.creation.cylinder(
        radius=(d - P.SOCKET_RELIEF_D) / 2, height=P.SOCKET_RELIEF_L,
        sections=P.SEG_SOCKET)
    relief.apply_translation([0, 0, -depth - P.SOCKET_RELIEF_L / 2 + 1e-6])
    parts.append(relief)

    cs = trimesh.creation.cone(radius=d / 2 + P.SOCKET_MOUTH_CHAMFER,
                               height=P.SOCKET_MOUTH_CHAMFER * 2.0,
                               sections=P.SEG_SOCKET)
    cs.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    cs.apply_translation([0, 0, P.SOCKET_MOUTH_CHAMFER * 2.0 - 0.001])
    parts.append(cs)

    # a stub proud of the surface, so the cut always breaks through the pad
    proud = trimesh.creation.cylinder(radius=d / 2, height=2.0,
                                      sections=P.SEG_SOCKET)
    proud.apply_translation([0, 0, 1.0])
    parts.append(proud)

    cutter = _union(parts)
    m = _frame_from_normal(axis)
    m[:3, 3] = p
    cutter.apply_transform(m)
    return cutter


# ---------------------------------------------------------------------------
# the assembled cactus
# ---------------------------------------------------------------------------

def cactus(with_sockets=True, with_arms=True):
    body = trunk_body()
    sites = trunk_areoles()
    if with_arms:
        arms = [arm_body(spec) for spec in P.ARMS]
        body = _union([body] + arms)
        for spec in P.ARMS:
            sites += arm_areoles(spec)

    # Drop any site that is not on the outside of the finished skin. An arm's
    # own crest runs on into the trunk for the first few millimetres, and a
    # pad placed down there is a blob sealed inside the part -- which the
    # bore then hollows out into a loose shell rattling around in the print.
    probe = np.array([p + n * 0.35 for p, n, _, _ in sites])
    buried = body.contains(probe)
    sites = [s for s, b in zip(sites, buried) if not b]

    # Drop any site whose spine would hang below SPIKE_FLOOR_DEG. A saguaro
    # does carry spines under its arms, but the socket for one is a hole
    # drilled into a roof: it prints as a sagging ellipse and the spike it
    # takes points at the floor. Not worth it for something nobody sees.
    sites = [s for s in sites
             if _rake(s[1], s[2], s[3])[2]
             > np.sin(np.radians(P.SPIKE_FLOOR_DEG))]

    pads = [areole_pad(p, n) for p, n, _, _ in sites]
    body = _union([body] + pads)

    if with_sockets:
        body = _difference(body, [socket_cutter(*s) for s in sites])
    return body, sites


# ---------------------------------------------------------------------------
# the spike
# ---------------------------------------------------------------------------

def spike() -> trimesh.Trimesh:
    """Pin, collar, needle. Standing on the pin's flat end, point up."""
    theta = np.linspace(0.0, 2 * np.pi, P.SEG_SPIKE, endpoint=False)

    def ring(z, r):
        return np.column_stack([r * np.cos(theta), r * np.sin(theta),
                                np.full_like(theta, z)])

    rings = []
    pin_r = P.PIN_SHANK_D / 2
    lead = 0.30                      # chamfer on the pin's nose
    rings.append(ring(0.0, pin_r - lead))
    rings.append(ring(lead, pin_r))
    rings.append(ring(P.PIN_SHANK_L, pin_r))

    # collar: a flat washer, which is also the part's first layer
    rings.append(ring(P.PIN_SHANK_L, P.SPIKE_COLLAR_D / 2))
    rings.append(ring(P.PIN_SHANK_L + P.SPIKE_COLLAR_H, P.SPIKE_COLLAR_D / 2))

    # needle: a convex taper, not a straight cone
    z0 = P.PIN_SHANK_L + P.SPIKE_COLLAR_H
    r0 = P.SPIKE_COLLAR_D / 2 * 0.60
    rings.append(ring(z0 + 1e-3, r0))
    for u in np.linspace(0.0, 1.0, 26)[1:]:
        shape = (1.0 - u) ** (1.0 + P.SPIKE_BELLY * 1.6)
        r = P.SPIKE_TIP_D / 2 + (r0 - P.SPIKE_TIP_D / 2) * shape
        rings.append(ring(z0 + P.SPIKE_L * u, r))

    return _loft(np.stack(rings, axis=0), cap_bottom=True, cap_top=True)


def spike_plate(n=None, pitch=None) -> trimesh.Trimesh:
    """A square array of spikes, as they go on the bed."""
    n = n or P.SPIKE_PLATE_N
    pitch = pitch or P.SPIKE_PLATE_PITCH
    one = spike()
    cols = int(np.ceil(np.sqrt(n)))
    out = []
    for i in range(n):
        m = one.copy()
        m.apply_translation([(i % cols) * pitch, (i // cols) * pitch, 0.0])
        out.append(m)
    return trimesh.util.concatenate(out)


def test_section(body=None) -> trimesh.Trimesh:
    """A wedge of the real trunk: real ribs, real pads, real raked sockets.

    The coupon measures one number -- the hole diameter that gives the right
    bite. This proves the whole joint on the surface it will live on, and it
    is the print to make before committing a day to the cactus.
    """
    if body is None:
        body, _ = cactus(with_arms=False)

    half = np.radians(P.TEST_WEDGE_DEG) / 2
    r = (P.TRUNK_R_MID + P.RIB_DEPTH) * 2.0
    ths = np.linspace(-half, half, 48)
    poly = np.vstack([[0.0, 0.0],
                      np.column_stack([r * np.cos(ths), r * np.sin(ths)])])
    wedge = trimesh.creation.extrude_triangulation(
        *trimesh.creation.triangulate_polygon(
            __import__("shapely").geometry.Polygon(poly)),
        height=P.TEST_Z1 - P.TEST_Z0)
    wedge.apply_translation([0.0, 0.0, P.TEST_Z0])
    return trimesh.boolean.intersection([body, wedge], engine=ENGINE)


def fit_coupon() -> trimesh.Trimesh:
    """A test block of sockets stepping either side of SOCKET_D.

    The press fit is the one number on this model that cannot be calculated
    with confidence -- it depends on the filament, the flow calibration and
    the first-layer squish. So it gets measured instead: print the coupon and
    a handful of spikes, find the hole the spike seats firmly in, and set
    SOCKET_COMP from the step that won.
    """
    steps = np.arange(-3, 4) * 0.06         # +/- 0.18 in 0.06 steps
    pitch = 7.0
    w = pitch * len(steps) + 6.0
    block = trimesh.creation.box([w, 14.0, P.SOCKET_DEPTH + 3.0])
    block.apply_translation([0, 0, (P.SOCKET_DEPTH + 3.0) / 2])

    cutters = []
    for i, ds in enumerate(steps):
        x = -w / 2 + 3.0 + pitch * (i + 0.5)
        c = trimesh.creation.cylinder(radius=(P.SOCKET_D + ds) / 2,
                                      height=P.SOCKET_DEPTH * 2,
                                      sections=P.SEG_SOCKET)
        c.apply_translation([x, 0.0, P.SOCKET_DEPTH + 3.0])
        cutters.append(c)
    return _difference(block, cutters)
