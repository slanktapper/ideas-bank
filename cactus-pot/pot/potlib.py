"""Parametric pot bodies, built from profiles revolved about Z.

Everything is a closed (r, z) profile touching the axis, revolved into a solid,
and combined with booleans. Round bodies revolve on many segments; faceted ones
revolve on few, with the profile read as the inradius so the flats land where
they are asked for.
"""
from __future__ import annotations
import numpy as np, trimesh
from shapely.geometry import Polygon
from shapely import segmentize

BOOL = 'manifold'


def revolve(profile, seg=192, flat=False, phase=None):
    """Revolve a closed (r, z) profile. `flat=True` reads r as the inradius."""
    prof = np.asarray(profile, dtype=float)
    if phase is None:
        phase = np.pi/seg if flat else 0.0
    k = 1.0/np.cos(np.pi/seg) if flat else 1.0
    th = np.linspace(0, 2*np.pi, seg, endpoint=False) + phase
    V, idx = [], []
    for r, z in prof:
        if r < 1e-9:                       # a single vertex on the axis
            idx.append(('pole', len(V))); V.append([0.0, 0.0, z])
        else:
            idx.append(('ring', len(V)))
            V.extend(np.c_[r*k*np.cos(th), r*k*np.sin(th), np.full(seg, z)])
    V = np.asarray(V, dtype=float)
    F = []
    n = len(prof)
    for i in range(n):
        j = (i+1) % n
        (ki, bi), (kj, bj) = idx[i], idx[j]
        for a in range(seg):
            b = (a+1) % seg
            if ki == 'ring' and kj == 'ring':
                F.append([bi+a, bi+b, bj+b]); F.append([bi+a, bj+b, bj+a])
            elif ki == 'ring':
                F.append([bi+a, bi+b, bj])
            elif kj == 'ring':
                F.append([bi, bj+b, bj+a])
    m = trimesh.Trimesh(V, np.array(F), process=True)
    m.merge_vertices(); m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
    if m.volume < 0: m.invert()
    return m


def cyl(r, z0, z1, seg=96):
    return revolve([(0, z0), (r, z0), (r, z1), (0, z1)], seg=seg)


def text_prism(geom, depth, over=0.6, dens=1.5):
    """A flat cutting prism from a shapely geometry, in the XY plane.

    Spans z from -over to depth, so it always breaks the surface it is cut from.
    """
    geom = segmentize(geom, dens)
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    parts = [trimesh.creation.extrude_polygon(p, depth+over) for p in polys if p.area > 1e-9]
    m = trimesh.util.concatenate(parts)
    m.apply_translation([0, 0, -over])
    return m


def sweep_on_cylinder(path, section, radius):
    """Sweep a closed 2D `section` along a closed 2D `path`, onto a cylinder.

    `path` is (u, z) on the unrolled wall; `section` is (t, h) where t runs along
    the path's own normal and h is depth out from the wall. Both are closed loops
    given once, without a repeated last point. The result is a quad tube, so it
    is watertight with no caps and no booleans -- which is why this exists rather
    than stacking extruded bands: a swept bead comes out two orders of magnitude
    lighter than the same shape unioned out of slabs.
    """
    P = np.asarray(path, float)
    S = np.asarray(section, float)
    nxt, prv = np.roll(P, -1, axis=0), np.roll(P, 1, axis=0)
    tang = nxt - prv
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    norm = np.c_[-tang[:, 1], tang[:, 0]]                 # in the (u, z) plane

    u = P[:, 0][:, None] + norm[:, 0][:, None] * S[:, 0][None, :]
    z = P[:, 1][:, None] + norm[:, 1][:, None] * S[:, 0][None, :]
    r = radius + S[:, 1][None, :]
    ang = u / radius
    V = np.stack([r*np.cos(ang), r*np.sin(ang), z], axis=-1).reshape(-1, 3)

    n, m = len(P), len(S)
    i = np.arange(n)[:, None]; j = np.arange(m)[None, :]
    a = i*m + j
    b = i*m + (j + 1) % m
    c = ((i + 1) % n)*m + (j + 1) % m
    d = ((i + 1) % n)*m + j
    F = np.vstack([np.stack([a, b, c], -1).reshape(-1, 3),
                   np.stack([a, c, d], -1).reshape(-1, 3)])
    mesh = trimesh.Trimesh(V, F, process=True)
    mesh.merge_vertices(); mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    if mesh.volume < 0: mesh.invert()
    return mesh


def bend_to_cylinder(mesh, radius):
    """Wrap a flat prism (x across, y up, z = outward depth) onto a cylinder.

    x becomes arc length at `radius`, so the lettering keeps its true width.
    """
    m = mesh.copy()
    m = m.subdivide_to_size(max_edge=3.0, max_iter=6)
    V = np.asarray(m.vertices)
    ang = V[:, 0] / radius
    rad = radius + V[:, 2]
    m.vertices = np.c_[rad*np.cos(ang), rad*np.sin(ang), V[:, 1]]
    return m


def place_flat(mesh, y, z, yaw=0.0):
    """Stand a flat prism up on the -Y side of the pot, facing outward."""
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
    if yaw: m.apply_transform(trimesh.transformations.rotation_matrix(yaw, [0, 0, 1]))
    m.apply_translation([0, y, z])
    return m


def diff(a, *bs):
    for b in bs:
        a = trimesh.boolean.difference([a, b], engine=BOOL)
    return a


def intersect(a, b):
    return trimesh.boolean.intersection([a, b], engine=BOOL)


def union(*ms):
    return trimesh.boolean.union(list(ms), engine=BOOL)
