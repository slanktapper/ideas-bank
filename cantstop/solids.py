"""Parametric mesh primitives.

Deliberately built by hand rather than by boolean subtraction. A collar is an
annulus because we emit an annulus, not because we drilled a cylinder; a
playing piece is a surface of revolution because we revolve its profile. That
keeps the meshes small, exactly watertight, and fast enough to regenerate the
whole project in a couple of seconds.

Booleans are still used, but only once at the end, to fuse the ~500 overlapping
parts of the board into a single manifold solid.
"""

from __future__ import annotations

import numpy as np
import trimesh


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _mesh(vertices, faces) -> trimesh.Trimesh:
    m = trimesh.Trimesh(
        vertices=np.asarray(vertices, dtype=np.float64),
        faces=np.asarray(faces, dtype=np.int64),
        process=False,
    )
    return m


def quad(a, b, c, d):
    """Two triangles for a quad wound a-b-c-d."""
    return [(a, b, c), (a, c, d)]


# ---------------------------------------------------------------------------
# lathe — a closed (r, z) profile revolved about the Z axis
# ---------------------------------------------------------------------------

def lathe(profile, segs: int = 48) -> trimesh.Trimesh:
    """Revolve a closed 2D profile given as [(r, z), ...] about the Z axis.

    The profile is a closed loop in the half-plane r >= 0, wound
    counter-clockwise in (r, z) so that the resulting solid has outward
    normals. Points sitting exactly on the axis (r == 0) are collapsed to a
    single shared vertex and the surrounding quads degenerate to triangles,
    which is what lets a piece have a solid bottom and a blind socket in the
    same watertight body.
    """
    prof = np.asarray(profile, dtype=np.float64)
    n = len(prof)
    if n < 3:
        raise ValueError("lathe profile needs at least 3 points")

    theta = np.linspace(0.0, 2.0 * np.pi, segs, endpoint=False)
    cos_t, sin_t = np.cos(theta), np.sin(theta)

    verts: list[tuple[float, float, float]] = []
    # index[i][s] -> vertex id for profile point i at angular step s
    index: list[list[int]] = []

    for r, z in prof:
        if r <= 1e-9:
            # on the axis: one vertex shared by every angular step
            vid = len(verts)
            verts.append((0.0, 0.0, float(z)))
            index.append([vid] * segs)
        else:
            row = []
            base = len(verts)
            for s in range(segs):
                verts.append((float(r) * cos_t[s], float(r) * sin_t[s], float(z)))
                row.append(base + s)
            index.append(row)

    faces: list[tuple[int, int, int]] = []
    for i in range(n):
        j = (i + 1) % n
        for s in range(segs):
            t = (s + 1) % segs
            a, b = index[i][s], index[i][t]
            c, d = index[j][t], index[j][s]
            # collapse degenerate edges on the axis
            if a == b:                      # profile point i is on the axis
                if c != d:
                    faces.append((a, c, d))
            elif c == d:                    # profile point j is on the axis
                faces.append((a, b, c))
            else:
                faces.extend(quad(a, b, c, d))

    return _mesh(verts, faces)


# ---------------------------------------------------------------------------
# tube — an annular prism, i.e. a ring with a through-bore
# ---------------------------------------------------------------------------

def tube(cx, cy, r_outer, r_inner, z0, z1, segs=48, top_chamfer=0.0) -> trimesh.Trimesh:
    """A ring standing on z0 and topping out at z1, bored through.

    `top_chamfer` opens the top of the bore out by that amount at 45 deg,
    giving a lead-in so a playing piece self-centres on the way in.
    """
    if top_chamfer > 0.0:
        prof = [
            (r_inner, z0),
            (r_outer, z0),
            (r_outer, z1),
            (r_inner + top_chamfer, z1),
            (r_inner, z1 - top_chamfer),
        ]
    else:
        prof = [
            (r_inner, z0),
            (r_outer, z0),
            (r_outer, z1),
            (r_inner, z1),
        ]
    m = lathe(prof, segs=segs)
    m.apply_translation((cx, cy, 0.0))
    return m


# ---------------------------------------------------------------------------
# strut — a flat-bottomed rectangular bar between two points in the XY plane
# ---------------------------------------------------------------------------

def strut(p0, p1, width, height, z0=0.0) -> trimesh.Trimesh:
    """A bar of rectangular section running from p0 to p1 in plan.

    Rectangular rather than round, and sitting flat on z0, so it prints
    without support no matter which way it runs across the bed.
    """
    p0 = np.asarray(p0, dtype=np.float64)
    p1 = np.asarray(p1, dtype=np.float64)
    d = p1 - p0
    length = float(np.linalg.norm(d))
    if length < 1e-9:
        raise ValueError("zero-length strut")
    d /= length
    nrm = np.array([-d[1], d[0]])          # left-hand perpendicular in plan
    h = width * 0.5

    # wound counter-clockwise in plan, so the +Z face really does face up
    corners = [
        p0 + nrm * h, p0 - nrm * h,
        p1 - nrm * h, p1 + nrm * h,
    ]
    z1 = z0 + height
    verts = [(c[0], c[1], z0) for c in corners] + [(c[0], c[1], z1) for c in corners]
    faces = []
    faces.extend(quad(0, 3, 2, 1))          # bottom, wound downward
    faces.extend(quad(4, 5, 6, 7))          # top
    for i in range(4):
        j = (i + 1) % 4
        faces.extend(quad(i, j, j + 4, i + 4))
    return _mesh(verts, faces)


# ---------------------------------------------------------------------------
# rounded plate — the number plaques
# ---------------------------------------------------------------------------

def rounded_plate(cx, cy, w, h, t, radius, z0=0.0, segs=8) -> trimesh.Trimesh:
    """An axis-aligned plate with rounded corners, extruded in Z."""
    from shapely.geometry import Polygon

    r = min(radius, w * 0.5 - 1e-3, h * 0.5 - 1e-3)
    x0, x1 = cx - w * 0.5, cx + w * 0.5
    y0, y1 = cy - h * 0.5, cy + h * 0.5

    pts: list[tuple[float, float]] = []
    corners = [
        (x1 - r, y1 - r, 0.0),
        (x0 + r, y1 - r, np.pi * 0.5),
        (x0 + r, y0 + r, np.pi),
        (x1 - r, y0 + r, np.pi * 1.5),
    ]
    for ox, oy, start in corners:
        for k in range(segs + 1):
            a = start + (np.pi * 0.5) * k / segs
            pts.append((ox + r * np.cos(a), oy + r * np.sin(a)))

    return trimesh.creation.extrude_polygon(Polygon(pts), t).apply_translation((0, 0, z0))


# ---------------------------------------------------------------------------
# text — extruded numerals, cut from real glyph outlines
# ---------------------------------------------------------------------------

def text_solid(s: str, cap_height: float, thickness: float,
               weight: str = "bold", z0: float = 0.0) -> trimesh.Trimesh:
    """Extrude a string into a solid, centred on the origin in X and Y.

    Glyph outlines come from matplotlib's TextPath (DejaVu Sans, which ships
    with matplotlib, so the result is identical on any machine).

    The fiddly part is the counters -- the enclosed holes in 0, 4, 6, 8, 9.
    TextPath hands back a flat list of closed loops with no indication of
    which is an outline and which is a hole, so we recover that with a
    nesting-depth test: sort the loops largest first, count how many larger
    loops contain each one, and apply the even-odd rule. Depth 0 is an
    outline, depth 1 is a counter, and the smallest loop containing a counter
    is the outline it belongs to.
    """
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from shapely.geometry import Polygon

    fp = FontProperties(family="DejaVu Sans", weight=weight)
    path = TextPath((0, 0), s, size=100, prop=fp)
    loops = [np.asarray(p) for p in path.to_polygons(closed_only=True) if len(p) >= 3]
    if not loops:
        raise ValueError(f"no outline for {s!r}")

    rings = [Polygon(p) for p in loops]
    rings = [r if r.is_valid else r.buffer(0) for r in rings]

    order = sorted(range(len(rings)), key=lambda i: -rings[i].area)
    depth: dict[int, int] = {}
    parent: dict[int, int | None] = {}
    for rank, i in enumerate(order):
        rp = rings[i].representative_point()
        containing = [j for j in order[:rank] if rings[j].contains(rp)]
        depth[i] = len(containing)
        parent[i] = containing[-1] if containing else None   # smallest, so immediate

    parts = []
    for i in range(len(rings)):
        if depth[i] % 2:
            continue                                          # this one is a counter
        counters = [rings[j].exterior.coords
                    for j in range(len(rings))
                    if depth[j] % 2 and parent[j] == i]
        parts.append(Polygon(rings[i].exterior.coords, counters))

    # each glyph is its own island, so extrude separately and concatenate
    mesh = trimesh.util.concatenate(
        [trimesh.creation.extrude_polygon(p, thickness) for p in parts]
    )

    # scale so the digit cap height (not the em box) matches the request
    lo, hi = mesh.bounds
    scale = cap_height / (hi[1] - lo[1])
    mesh.apply_scale((scale, scale, 1.0))
    lo, hi = mesh.bounds
    mesh.apply_translation((
        -(lo[0] + hi[0]) * 0.5,
        -(lo[1] + hi[1]) * 0.5,
        z0,
    ))
    return mesh


# ---------------------------------------------------------------------------
# union — fuse many overlapping solids into one manifold body
# ---------------------------------------------------------------------------

def union_all(meshes, engine="manifold") -> trimesh.Trimesh:
    """Boolean-union a list of meshes using a balanced binary reduction.

    Folding left-to-right would make the accumulator grow with every step and
    turn this into an O(n^2) crawl. Pairing them up instead keeps the operands
    the same size as each other and gets the whole board done in seconds.
    """
    items = [m for m in meshes if m is not None and len(m.faces)]
    if not items:
        raise ValueError("nothing to union")
    while len(items) > 1:
        nxt = []
        for i in range(0, len(items) - 1, 2):
            nxt.append(trimesh.boolean.union([items[i], items[i + 1]], engine=engine))
        if len(items) % 2:
            nxt.append(items[-1])
        items = nxt
    return items[0]
