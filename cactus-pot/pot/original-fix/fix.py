"""Re-set the middle line of the pot: level baseline, centred, sized to the measure.

The glyphs themselves are the pot's own -- they are lifted out of the wall as
solids, re-laid-out, and cut back in -- so the typeface is untouched.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np, trimesh, lib

TARGET_SPAN = float(sys.argv[1]) if len(sys.argv)>1 else 100.0
TRACK       = 0.62
CENTRE      = 0.0
Z_LINE1_BASE = 56.92      # Eleanor's baseline
Z_LINE3_TOP  = 24.33      # top of the F in File
PROUD        = 0.5        # how far the cutter stands off the wall

pot = trimesh.load(lib.POT)
band = lib.revolve_band(27.0, 55.5, 3.0, nz=110)
cav  = trimesh.boolean.difference([band, pot], engine='manifold')
glyphs = [p for p in cav.split(only_watertight=False) if p.volume > 0.5]
glyphs.sort(key=lambda p: np.degrees(np.arctan2(p.centroid[1], p.centroid[0])))
assert len(glyphs) == 12, len(glyphs)

box = []
for p in glyphs:
    th, z, r = lib.cyl(np.asarray(p.vertices))
    box.append(dict(t0=th.min(), t1=th.max(), z0=z.min(), z1=z.max(), m=p))

sit = [i for i in range(12) if i not in (9, 10)]          # not the p, not the apostrophe
tc  = np.array([0.5*(box[i]['t0']+box[i]['t1']) for i in sit])
bow = np.polyfit(tc, np.array([box[i]['z0'] for i in sit]), 2)

widths = np.array([b['t1']-b['t0'] for b in box])
gaps   = np.array([box[i+1]['t0'] - box[i]['t1'] for i in range(11)])
s = TARGET_SPAN / (widths.sum() + TRACK*gaps.sum())

# vertical: balance the gap to the line above and the line below
asc  = max(b['z1'] - np.polyval(bow, 0.5*(b['t0']+b['t1'])) for b in box) * s
desc = min(b['z0'] - np.polyval(bow, 0.5*(b['t0']+b['t1'])) for b in box) * s
base = 0.5*((Z_LINE1_BASE - asc) + (Z_LINE3_TOP - desc))
print(f'span {TARGET_SPAN:.0f}deg  scale {s:.3f}  ascender {asc:.1f}  descender {desc:.1f}  baseline {base:.2f}')
print(f'  clearance above {Z_LINE1_BASE-(base+asc):.1f} mm, below {(base+desc)-Z_LINE3_TOP:.1f} mm')

new_w = widths*s; new_g = gaps*s*TRACK
x = CENTRE - (new_w.sum()+new_g.sum())/2
starts=[]
for i in range(12):
    starts.append(x); x += new_w[i]
    if i < 11: x += new_g[i]

Dmin, Dmax = 0.25, 2.075                                   # as extracted

def deepen(m, proud):
    """Stretch a cavity solid radially so its open face stands `proud` of the wall."""
    a = (Dmax + proud)/(Dmax - Dmin); b_ = Dmax - a*Dmax
    th, z, r = lib.cyl(np.asarray(m.vertices))
    D = np.clip(lib.r_env(z) - r, Dmin, None)
    g = m.copy(); g.vertices = lib.xyz(th, z, lib.r_env(z) - (a*D + b_)); return g

a = (Dmax + PROUD)/(Dmax - Dmin); b_ = Dmax - a*Dmax        # D -> a*D+b_, so Dmin -> -PROUD

placed=[]
for i, bx in enumerate(box):
    th, z, r = lib.cyl(np.asarray(bx['m'].vertices))
    D = np.clip(lib.r_env(z) - r, Dmin, None)
    here = np.polyval(bow, 0.5*(bx['t0']+bx['t1']))
    z_new = base + (z - here)*s
    sa = s * lib.r_env(here+6.0) / lib.r_env(base+6.0*s)
    th_new = starts[i] + (th - bx['t0'])*sa
    g = bx['m'].copy()
    g.vertices = lib.xyz(th_new, z_new, lib.r_env(z_new) - (a*D + b_))
    placed.append(g)

text = trimesh.util.concatenate(placed)
# The band between the two neighbouring lines holds nothing but this word, so
# the old engraving is filled by packing the whole band solid and trimming it
# back flush with the wall.
packer  = lib.revolve_band_at(26.0, 54.3, outer_offset=+0.4, thickness=2.6, nz=2)   # pure cone below the knee
outside = lib.revolve_outside(26.0, 54.3, 1.5, nz=2)
filled = trimesh.boolean.union([pot, packer], engine='manifold')
filled = trimesh.boolean.difference([filled, outside], engine='manifold')
out = trimesh.boolean.difference([filled, text], engine='manifold')
print('watertight', out.is_watertight, 'volume %.0f' % out.volume)
out.export('pot-fixed.stl')
