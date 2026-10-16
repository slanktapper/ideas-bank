"""Which bits of which level maps go on the rail, and the pixels themselves.

A vignette is a straight rectangular crop out of one of the real maps in
maps/ -- no redrawing, no invented pixels. It is `PANEL_TILES` wide and
`ART_TILES_H` tall, taken from a chosen tile column and a chosen band.

WHY BANDS 11-12. A level map is 14 bands of 16 px. Band 13 and most of 12
are the ground mass; band 11 is where things stand on it. A two-band window
at 11-12 therefore catches a goomba's whole body, the foot of a pipe, the
castle doorway and one row of ground -- the walking line of the game. Taking
12-13 instead gets two rows of identical ground blocks, which is nothing.

The four chosen here were picked by cropping every candidate and looking at
it; the ones that turned out to be mostly empty sky are not here.

BACKGROUND IS PER-VIGNETTE. Overworld sky is #5c94fc and underground "sky"
is #000000. Black is also an outline colour inside the sprites, so in the
underground vignette those outlines fall away to the plate -- which is what
the eye expects there anyway, since the background is black too.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

import params as P

MAPS = Path(__file__).parent / "maps"

SKY_OVERWORLD = (0x5c, 0x94, 0xfc)
SKY_UNDERGROUND = (0x00, 0x00, 0x00)

BAND_TOP = 11              # first band of the two-band window


class Vignette:
    def __init__(self, key, gif, tile_x, background, caption):
        self.key = key
        self.gif = gif
        self.tile_x = tile_x
        self.background = background
        self.caption = caption

    def pixels(self):
        """(cols, rows, grid) with grid[row][col] = rgb tuple, row 0 at top."""
        im = Image.open(MAPS / self.gif).convert("RGB")
        x0 = self.tile_x * 16
        y0 = BAND_TOP * 16
        w = P.PANEL_TILES * 16
        h = P.ART_TILES_H * 16
        if x0 + w > im.width:
            raise ValueError("%s: crop runs off the right of %s (%d > %d)"
                             % (self.key, self.gif, x0 + w, im.width))
        crop = im.crop((x0, y0, x0 + w, y0 + h))
        px = crop.load()
        grid = [[px[c, r] for c in range(w)] for r in range(h)]
        return w, h, grid

    def colours(self):
        """Every colour in the crop except the background, most common first."""
        from collections import Counter
        _, _, grid = self.pixels()
        n = Counter(c for row in grid for c in row)
        del n[self.background]
        return [c for c, _ in n.most_common()]


# The rail, left to right. An arc through the game: the first screen anyone
# ever saw, the pipes, a dip underground, and the castle at the end of 1-1.
RAIL = [
    Vignette("opening",   "mario-1-1.gif",   0, SKY_OVERWORLD,
             "1-1 opening: Mario on the first hill, bushes"),
    Vignette("pipes",     "mario-1-1.gif",  34, SKY_OVERWORLD,
             "1-1: a goomba between two pipes"),
    Vignette("underground", "mario-1-2.gif", 12, SKY_UNDERGROUND,
             "1-2 underground: coins over teal brick, two goombas"),
    Vignette("castle",    "mario-1-1.gif", 190, SKY_OVERWORLD,
             "1-1 finish: the flagpole base and the castle door"),
]

assert len(RAIL) == P.PANELS, "RAIL has %d vignettes, PANELS is %d" % (len(RAIL), P.PANELS)
