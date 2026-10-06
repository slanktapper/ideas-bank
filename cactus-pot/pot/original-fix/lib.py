import os
import numpy as np, trimesh

# The source mesh is a third-party model and is not in this repository. Point
# SOURCE_POT_STL at your copy before running fix.py.
POT = os.environ.get('SOURCE_POT_STL', 'Good Place Cactus (Pot).stl')
CONE_M, CONE_C = 0.222222, 33.888870      # r = m*z + c, refined below
R_COLLAR = 46.111
Z_KNEE = (R_COLLAR - CONE_C) / CONE_M

def r_env(z):
    z = np.asarray(z, dtype=float)
    return np.where(z < Z_KNEE, CONE_M * z + CONE_C, R_COLLAR)

def revolve_band_at(z0, z1, outer_offset, thickness, seg=512, nz=48):
    return _band(z0, z1, outer_offset, thickness, seg, nz)


def revolve_band(z0, z1, thickness, seg=512, nz=48):
    return _band(z0, z1, -0.25, thickness, seg, nz)


def _band(z0, z1, outer_offset, thickness, seg=512, nz=48):
    """Annular solid of revolution hugging the envelope, z0..z1, given radial thickness."""
    zs = np.linspace(z0, z1, nz)
    ro = r_env(zs) + outer_offset
    ri = ro - thickness
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    V = []
    for k, (a, b) in enumerate(zip(ro, ri)):
        V.append(np.c_[a*ct, a*st, np.full(seg, zs[k])])
    for k, (a, b) in enumerate(zip(ro, ri)):
        V.append(np.c_[b*ct, b*st, np.full(seg, zs[k])])
    V = np.vstack(V)
    F = []
    def q(a, b, c, d): F.append([a, b, c]); F.append([a, c, d])
    OUT = 0; IN = nz*seg
    for k in range(nz-1):
        for i in range(seg):
            j = (i+1) % seg
            q(OUT+k*seg+i, OUT+k*seg+j, OUT+(k+1)*seg+j, OUT+(k+1)*seg+i)       # outer
            q(IN+k*seg+j, IN+k*seg+i, IN+(k+1)*seg+i, IN+(k+1)*seg+j)           # inner
    for i in range(seg):                                                         # caps
        j = (i+1) % seg
        q(OUT+j, OUT+i, IN+i, IN+j)
        k = nz-1
        q(OUT+k*seg+i, OUT+k*seg+j, IN+k*seg+j, IN+k*seg+i)
    mesh = trimesh.Trimesh(V, np.array(F), process=True)
    mesh.fix_normals()
    return mesh

def cyl(v):
    """xyz -> (theta_deg, z, r)"""
    return np.degrees(np.arctan2(v[:,1], v[:,0])), v[:,2], np.hypot(v[:,0], v[:,1])

def xyz(th_deg, z, r):
    t = np.radians(th_deg)
    return np.c_[r*np.cos(t), r*np.sin(t), z]


def revolve_outside(z0, z1, out=1.5, seg=512, nz=48):
    """The thin shell of space just OUTSIDE the envelope, for trimming proud fill."""
    import numpy as _np
    zs = _np.linspace(z0, z1, nz)
    ri = r_env(zs); ro = ri + out
    th = _np.linspace(0, 2*_np.pi, seg, endpoint=False)
    ct, st = _np.cos(th), _np.sin(th)
    V=[]
    for k in range(nz): V.append(_np.c_[ro[k]*ct, ro[k]*st, _np.full(seg, zs[k])])
    for k in range(nz): V.append(_np.c_[ri[k]*ct, ri[k]*st, _np.full(seg, zs[k])])
    V=_np.vstack(V); F=[]
    def q(a,b,c,d): F.append([a,b,c]); F.append([a,c,d])
    OUT=0; IN=nz*seg
    for k in range(nz-1):
        for i in range(seg):
            j=(i+1)%seg
            q(OUT+k*seg+i, OUT+k*seg+j, OUT+(k+1)*seg+j, OUT+(k+1)*seg+i)
            q(IN+k*seg+j, IN+k*seg+i, IN+(k+1)*seg+i, IN+(k+1)*seg+j)
    for i in range(seg):
        j=(i+1)%seg
        q(OUT+j, OUT+i, IN+i, IN+j)
        k=nz-1
        q(OUT+k*seg+i, OUT+k*seg+j, IN+k*seg+j, IN+k*seg+i)
    import trimesh as _tm
    m=_tm.Trimesh(V,_np.array(F),process=True); m.fix_normals(); return m
