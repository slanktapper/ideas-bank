"""Renders of the pot, through the shared software renderer in ../../3d-tools.

    python3 shots.py                      # everything in renders/
    python3 shots.py --compare <old.stl>  # the two halves of 04-old-vs-new
    python3 shots.py --colour             # the four-colour pot, every 120 deg
"""
from __future__ import annotations
import pathlib, sys
import numpy as np, trimesh

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / '3d-tools'))
import render as R                                      # noqa: E402
from build import PAN_Z as B_PAN_Z                      # noqa: E402

STL, OUT = HERE / 'stl', HERE / 'renders'
STONE = (0.90, 0.90, 0.92)      # the crackle zone, silver
GOLD  = (0.85, 0.66, 0.34)      # the rolled base
CLAY  = (0.78, 0.44, 0.33)      # single-colour, for shape only
LIGHT = dict(ambient=0.52, key=0.52, fill=0.26, spec=0.22, edges=0.5)


def shot(parts, name, az, el, dist=235.0, zt=40.0):
    tgt = (0.0, 0.0, zt)
    eye = R.orbit_eye(np.array(tgt), dist, az, el)
    img = R.render(parts, eye=eye, target=tgt, width=1250, height=1000,
                   fov_deg=30.0, supersample=2, **LIGHT)
    OUT.mkdir(exist_ok=True)
    img.save(OUT / name)
    print(OUT / name)


# the four filaments, as they read on the shelf
GOLD_SILK   = (0.86, 0.67, 0.29)
SILVER_SILK = (0.78, 0.80, 0.84)
JADE_WHITE  = (0.94, 0.95, 0.93)
BLACK       = (0.09, 0.09, 0.10)
COLOUR_DIR  = STL / 'colour'


def colour_parts():
    import colours
    names = dict(zip(colours.PARTS, (GOLD_SILK, SILVER_SILK, JADE_WHITE, BLACK)))
    missing = [n for n in names if not (COLOUR_DIR / f'{n}.stl').exists()]
    if missing:
        raise SystemExit('run colours.py first -- missing ' + ', '.join(missing))
    return [{'mesh': trimesh.load(COLOUR_DIR / f'{n}.stl'), 'color': c}
            for n, c in names.items()]


def colour_shots():
    """Three views 120 degrees apart, plus the panel head on."""
    parts = colour_parts()
    for i, az in enumerate((0, 120, 240)):
        shot(parts, f'07-colour-{az:03d}.png', az=az, el=12)
    tgt = (0.0, 0.0, B_PAN_Z)
    eye = R.orbit_eye(np.array(tgt), 165.0, 0.0, 0.0)
    img = R.render(parts, eye=eye, target=tgt, width=1250, height=1000,
                   fov_deg=30.0, supersample=2, **LIGHT)
    img.save(OUT / '08-colour-panel.png')
    print(OUT / '08-colour-panel.png')


def compare(source):
    """04-old-vs-new.png: the pot we started from and this one, same camera."""
    for path, name in ((source, 'old'), (STL / 'pebble-pot.stl', 'new')):
        shot([{'mesh': trimesh.load(path), 'color': CLAY}], f'04-{name}.png',
             az=0, el=10)
    print('the two halves of 04-old-vs-new.png; join them side by side')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--colour':
        colour_shots(); raise SystemExit
    if len(sys.argv) > 2 and sys.argv[1] == '--compare':
        compare(sys.argv[2]); raise SystemExit
    pot = [{'mesh': trimesh.load(STL / 'pebble-pot.stl'), 'color': CLAY}]
    two = [{'mesh': trimesh.load(STL / 'pebble-pot-upper.stl'), 'color': STONE},
           {'mesh': trimesh.load(STL / 'pebble-pot-base.stl'),  'color': GOLD}]
    shot(pot, '01-front.png', az=0, el=10)
    shot(pot, '02-three-quarter.png', az=42, el=16)
    shot(pot, '03-inside.png', az=30, el=55, dist=250, zt=34)
    shot(two, '05-two-tone-above.png', az=35, el=48, dist=255, zt=34)
