"""Split the pot into one body per filament colour, for a four-colour print.

The pot prints as one object in four materials. Rather than paint it in the
slicer, each colour is its own watertight solid here, so the split is in the
geometry and survives being reopened:

    cocoa   the body, the foot, the inside, the borders round the stones and
            the raised bottom below the scalloped line
    silver  the raised stones themselves
    white   the smooth cartouche the name sits in
    black   the letters, filling the engraving flush

The borders and the raised bottom keep their shape; they simply print in the
body colour, so they read by their own shadow rather than by contrast.

The letters are raised on both: `stl/pebble-pot.stl` carries them too, where they
read by their own shadow. Here they read by colour as well. So unlike the earlier
engraved version, the four parts together are the same shape as the one-piece
pot.
"""
from __future__ import annotations
import pathlib
import trimesh

import build as B
import potlib as P

OUT = pathlib.Path(__file__).resolve().parent / 'stl' / 'colour'
PANEL_SKIN = 1.6          # how deep the white runs behind the panel face

PARTS = ('01-cocoa-body', '02-silver-stones', '03-white-panel', '04-black-letters')


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
    letters, skin, stone = B.text_solid(quiet=True), panel_skin(), B.stone_solid()
    # the whole pot, lettering and all -- the letters stand proud of the panel, so
    # unlike the engraved version they are not inside `body_unlettered`
    solid = P.union(B.body_unlettered(), letters)
    print('solid %.0f mm3, watertight %s' % (solid.volume, solid.is_watertight))

    # The borders and the raised bottom print in the body colour now, so they are
    # not parts of their own. They still have to come off the stones: the wider
    # bead bites about 18 mm3 into the stones' feet, and that material is cocoa.
    relief = P.union(B.stone_border(), B.bottom_band())
    silver = P.diff(stone, relief)
    black = letters
    white = P.diff(P.intersect(solid, skin), letters)
    # cut against the silver rather than the whole stone field, so the bitten
    # feet stay with the body
    cocoa = P.diff(solid, silver, skin, letters)

    OUT.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for name, m in zip(PARTS, (cocoa, silver, white, black)):
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
