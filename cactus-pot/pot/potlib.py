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
