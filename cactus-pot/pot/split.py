"""Split the pot at the scalloped line, so the two zones can print in two colours."""
import pathlib
import numpy as np, trimesh
import potlib as P
from build import wave, R

def wave_solid(seg=720, rmax=60.0, zbot=-10.0):
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    zt = wave(th*R)
    V = [[0.0, 0.0, zbot], [0.0, 0.0, float(zt.mean())]]
    V += list(np.c_[rmax*np.cos(th), rmax*np.sin(th), np.full(seg, zbot)])   # 2 .. 2+seg
    V += list(np.c_[rmax*np.cos(th), rmax*np.sin(th), zt])                   # 2+seg ..
    V = np.asarray(V, float)
    B, T = 2, 2+seg
    F = []
    for a in range(seg):
        b = (a+1) % seg
        F.append([0, B+b, B+a])                      # bottom fan
        F.append([1, T+a, T+b])                      # top fan
        F.append([B+a, B+b, T+b]); F.append([B+a, T+b, T+a])   # wall
    m = trimesh.Trimesh(V, np.array(F), process=True)
    m.merge_vertices()
    if m.volume < 0: m.invert()
    return m

def tidy(m):
    """Make a boolean result survive the round trip through an STL.

    A cut of this mesh comes out watertight in memory but not after a reload:
    STL stores every triangle's own three vertices, and the cut face carries
    duplicate and zero-area triangles that only merge once the vertices do.
    Slicers care, so fix it here rather than leaving it to them.
    """
    c = m.copy()
    c.merge_vertices(merge_tex=True, merge_norm=True)
    c.update_faces(c.nondegenerate_faces())
    c.update_faces(c.unique_faces())
    c.remove_unreferenced_vertices()
    # dropping duplicate faces closes most results but opens a few: keep the
    # cleaned copy only when it is still closed
    return c if c.is_watertight or not m.is_watertight else m


if __name__ == '__main__':
    stl = pathlib.Path(__file__).resolve().parent / 'stl'
    pot = trimesh.load(stl / 'pebble-pot.stl')
    ws = wave_solid()
    print('wave solid watertight', ws.is_watertight)
    base = trimesh.boolean.intersection([pot, ws], engine='manifold')
    top  = trimesh.boolean.difference([pot, ws], engine='manifold')
    print('base %.0f mm3 watertight %s' % (base.volume, base.is_watertight))
    print('top  %.0f mm3 watertight %s' % (top.volume, top.is_watertight))
    base, top = tidy(base), tidy(top)
    print('after tidy: base %s, upper %s' % (base.is_watertight, top.is_watertight))
    base.export(stl / 'pebble-pot-base.stl')
    top.export(stl / 'pebble-pot-upper.stl')
    print('wrote', stl / 'pebble-pot-base.stl', 'and', stl / 'pebble-pot-upper.stl')
