"""Split the pot into one body per filament colour, for a four-colour print.

The pot prints as one object in four materials. Rather than paint it in the
slicer, each colour is its own watertight solid here, so the split is in the
geometry and survives being reopened:

    gold    the body, the foot, the inside, and the grooves between the stones
    silver  the raised stones themselves
    white   the smooth cartouche the name sits in
    black   the letters, filling the engraving flush
    purple  the rounded border running round every stone

Note what this changes: on `stl/pebble-pot.stl` the name is a void cut 1.0 mm
into the panel. Here it is *filled*, so the four parts together make the shape
of `build.body_unlettered()` -- a flush face with the letters in a second
filament, not a recess. The single-colour pot is unchanged and still built by
build.py.
"""
from __future__ import annotations
import pathlib
import trimesh

import build as B
import potlib as P

OUT = pathlib.Path(__file__).resolve().parent / 'stl' / 'colour'
PANEL_SKIN = 1.6          # how deep the white runs behind the panel face

PARTS = ('01-gold-body', '02-silver-stones', '03-white-panel', '04-black-letters',
         '05-purple-borders')


def panel_skin():
    """A slab of the wall under the cartouche, from R-2.1 out to R+1.

    The footprint is grown 0.05 mm so that its sides do not land exactly on the
    pocket's own walls. Coincident faces are what makes a boolean give back a
    mesh with holes in it, and 0.05 mm is far below anything a nozzle resolves.
    """
    return P.bend_to_cylinder(
        P.text_prism(B.panel_shape().buffer(0.05), 1.0,
                     over=PANEL_SKIN + B.PAN_SINK, dens=1.2), B.R)


def tidy(m):
    """Merge the duplicate vertices an STL round trip would otherwise leave.

    Only if it helps: dropping duplicate faces closes most meshes but opens a
    few, so the cleaned copy is kept only when it is still watertight.
    """
    c = m.copy()
    c.merge_vertices(merge_tex=True, merge_norm=True)
    c.update_faces(c.nondegenerate_faces())
    c.update_faces(c.unique_faces())
    c.remove_unreferenced_vertices()
    return c if c.is_watertight or not m.is_watertight else m


def split():
    solid = B.body_unlettered()
    print('solid %.0f mm3, watertight %s' % (solid.volume, solid.is_watertight))

    cutter, skin, stone = B.text_cutter(quiet=True), panel_skin(), B.stone_solid()
    bead = B.stone_border()

    # The stone field was unioned onto the body and lies wholly inside it, so it
    # is already the silver part -- 179 separate closed cells, no boolean needed.
    silver = stone
    black = P.intersect(solid, cutter)
    white = P.diff(P.intersect(solid, skin), cutter)
    # The borders, like the stones, were unioned on and lie wholly inside the
    # finished body, so they are their own part with no boolean needed.
    purple = bead
    gold = P.diff(solid, stone, skin, cutter, bead)

    OUT.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for name, m in zip(PARTS, (gold, silver, white, black, purple)):
        m = tidy(m)
        m.export(OUT / f'{name}.stl')
        total += m.volume
        print('  %-18s %8.0f mm3  %6d faces  watertight %s'
              % (name, m.volume, len(m.faces), m.is_watertight))
    print('%d parts %.0f mm3 against a solid of %.0f -- %+.1f mm3'
          % (len(PARTS), total, solid.volume, total - solid.volume))
    print('wrote', OUT)


if __name__ == '__main__':
    split()
