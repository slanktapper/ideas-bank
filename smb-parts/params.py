"""Every dimension of the smb-parts shelf rail, in millimetres.

Change a number here, run test_fit.py, then build.py. Nothing else in the
project hard-codes a size.

WHAT THE BRIEF FIXES

  - roughly three feet long, standing in front of a shelf;
  - 25 mm tall -- that is the number Rob gave, and it is the whole part;
  - a U that clips over the shelf's front edge;
  - several greatest-hits Mario scenes rather than one continuous level.

WHAT 25 MM FORCES, and it forces nearly everything.

The level maps are 14 tiles tall. Twenty-five millimetres of that is 1.79 mm
per tile and 0.112 mm per game pixel -- a third of the nozzle. A whole
playfield at this height is not printable, so the art is a TWO-TILE band:
the row things stand on, and the ground under it. That gives 12.5 mm per
tile and 0.78 mm per game pixel, which is two bead widths and prints.

The second thing 25 mm forces is the clip. The front face has to cover the
board's edge AND the leg above and below it, so

    FACE_H = LEG_T + SHELF_T + FIT + LEG_T

With FACE_H pinned at 25 by the brief, the board thickness sets how much
plastic is left for the legs. At an 18 mm board the legs are 3.3 mm, which
is plenty. Past about 20 mm there is nothing left and FACE_H has to grow --
test_fit.py says so rather than letting it print paper-thin.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# the brief
# ---------------------------------------------------------------------------

FACE_H = 25.0              # the 25 mm. Total height of the part, and the
                           # height of the art, which is the same thing.
ART_TILES_H = 2            # see the docstring: 2 is what 25 mm can carry
PANEL_TILES = 18           # tiles per printed panel -> 225 mm, well inside
                           # the 325 mm bed with room for a brim
PANELS = 4                 # 4 x 225 = 900 mm = 2.95 ft, the "like 3 feet"

# ---------------------------------------------------------------------------
# MEASURE THIS ONE
# ---------------------------------------------------------------------------

SHELF_T = 18.0             # thickness of the shelf board the rail clips over.
                           # 18 mm is a common board and is a GUESS until Rob
                           # puts a caliper on his shelf. Everything about the
                           # clip follows from it; nothing about the art does.

FIT = 0.4                  # slip clearance across the board, total. FDM holes
                           # and slots come out undersize; 0.4 lets the rail
                           # push on by hand without rattling.

# ---------------------------------------------------------------------------
# derived -- the geometry has no freedom left once the four above are set
# ---------------------------------------------------------------------------

TILE = FACE_H / ART_TILES_H        # 12.5 mm
PIXEL = TILE / 16.0                # 0.78125 mm, one NES pixel
PANEL_L = PANEL_TILES * TILE       # 225.0 mm
TOTAL_L = PANELS * PANEL_L         # 900.0 mm

LEG_T = (FACE_H - SHELF_T - FIT) / 2.0   # 3.3 mm at an 18 mm board
GAP = SHELF_T + FIT                      # the slot the board sits in

# ---------------------------------------------------------------------------
# the rest of the section
# ---------------------------------------------------------------------------

FACE_T = 2.4               # the front plate behind the art. Six 0.4 mm walls;
                           # stiff enough that 225 mm of it does not bow.
LEG_D = 20.0               # how far the legs reach back over the board. Enough
                           # to hang on; short enough to hide under a book.
RELIEF = 1.2               # how far the art stands proud of the plate. Three
                           # 0.4 mm layers -- reads in raking light, and gives
                           # the per-colour bodies something to be.

# the half-lap that keeps neighbouring panels in line. The shelf edge already
# aligns them in two axes; this stops them sliding apart in the third.
LAP_L = 8.0                # how far the tongue projects past the panel end
LAP_FIT = 0.3              # clearance on the lap, per face

# ---------------------------------------------------------------------------
# the machine, from ../available-tools.md
# ---------------------------------------------------------------------------

BED_X, BED_Y, BED_Z = 325.0, 320.0, 325.0
NOZZLE = 0.4
