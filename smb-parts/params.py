"""Every dimension of the smb-parts shelf rail, in millimetres.

Change a number here, run test_fit.py, then build.py. Nothing else in the
project hard-codes a size.

THE SHELF, from Rob's product drawing (2026-10-17). It is a floating shelf,
not a board: pressed sheet 4 mm thick, 12.6 in long, with the front edge
turned UP into a retainer bar.

    12.6 in  = 320.04 mm   length
    3.95 in  = 100.33 mm   depth
    2.95 in  =  74.93 mm   back plane height
    3.50 in  =  88.90 mm   the flat part of the floor
    0.79 in  =  20.07 mm   the front, floor underside to retainer top
    4 mm                   material thickness

SO THERE IS NOTHING TO CLIP OVER in the way a wooden shelf would offer. The
rail instead CAPS THE RETAINER BAR: a slot 4 mm wide drops over it, the art
hangs down the outside, and the shelf's whole 20 mm front elevation ends up
behind Mario. It intrudes 9.3 mm into the shelf and eats no usable depth.

AND THE RAIL IS PER SHELF. 320 mm is not three feet; three of these shelves
are (960 mm). A single 900 mm rail cannot span separate floating shelves, so
one rail is one shelf, and the three feet comes from printing three of them.

WHAT 25 MM STILL FORCES. The maps are 14 tiles tall and 25 mm of that is
0.112 mm a game pixel -- a third of the nozzle. So the art is a TWO-TILE
band: the row things stand on, and the ground under it. Tile size now falls
out of the shelf rather than being chosen: 26 tiles span 320.04 mm, so a
tile is 12.31 mm, the art is 24.62 mm tall -- within half a millimetre of
the 25 Rob asked for -- and a game pixel is 0.77 mm, just under two beads.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# the shelf, measured off the drawing
# ---------------------------------------------------------------------------

IN = 25.4

SHELF_L = 12.6 * IN        # 320.04 -- one shelf, and one rail
MAT_T = 4.0                # sheet thickness, and so the retainer bar's
FRONT_H = 0.79 * IN        # 20.07 -- underside of floor to top of retainer
BAR_RISE = FRONT_H - MAT_T  # 16.07 -- how far the bar stands above the floor

# ---------------------------------------------------------------------------
# the art
# ---------------------------------------------------------------------------

TILES_PER_SHELF = 26       # 26 divides into two printed panels of 13, and
                           # lands the art at 24.62 mm. 25 would be a nicer
                           # 0.80 mm pixel but does not halve.
ART_TILES_H = 2            # what 25 mm can carry; see the docstring
PANELS_PER_SHELF = 2       # 160.02 mm each, comfortable on the bed

TILE = SHELF_L / TILES_PER_SHELF        # 12.309
PIXEL = TILE / 16.0                     # 0.7693, one NES pixel
FACE_H = ART_TILES_H * TILE             # 24.618, the height of the whole part
PANEL_L = SHELF_L / PANELS_PER_SHELF    # 160.02
PANEL_TILES = TILES_PER_SHELF // PANELS_PER_SHELF   # 13

# ---------------------------------------------------------------------------
# the clip that caps the retainer bar
# ---------------------------------------------------------------------------

FIT = 0.2                  # slip clearance across the bar. MEASURED, not
                           # guessed: Rob printed the fit ladder on
                           # 2026-10-23 MDT and the 4.2 mm rung was the one
                           # that gripped, so the slot is bar + 0.2. Note it
                           # was the TIGHTEST rung on that ladder -- see the
                           # scale caveat in print-guide.md before trusting
                           # it over 160 mm of panel.
SLOT = MAT_T + FIT         # 4.4

FACE_T = 2.4               # the plate behind the art, six 0.4 walls
WEB_T = 3.0                # the bit that bridges the top of the bar
LEG_T = 2.5                # the inner leg, down the back of the bar
GRIP = 12.0                # how far down the bar the slot holds. Short of
                           # BAR_RISE so it seats on the bar, not the floor.
RELIEF = 1.2               # how far the art stands proud of the plate

DEPTH = FACE_T + SLOT + LEG_T           # 9.3, all it takes off the shelf

# the half-lap in the web that keeps the two panels of a shelf in line
LAP_L = 8.0
LAP_FIT = 0.3

# ---------------------------------------------------------------------------
# the fit coupons -- a ladder of slot widths to try on the real shelf before
# committing to eight panels. Nothing else depends on these.
# ---------------------------------------------------------------------------

COUPON_W = 5.0             # how long a slice of the rail each coupon is
COUPON_GAP = 4.0           # space between them on the spine
COUPON_SLOTS = [4.0, 4.1, 4.2, 4.3, 4.4]   # re-centred on the measured 4.2
                                           # after the first ladder, whose
                                           # winner sat at its tight end
SPINE_T = 1.2              # the frangible bar joining them, at the bed face
DIGIT_PX = 1.3             # pixel size of the embossed slot number

# ---------------------------------------------------------------------------
# the machine, from ../available-tools.md
# ---------------------------------------------------------------------------

BED_X, BED_Y, BED_Z = 325.0, 320.0, 325.0
NOZZLE = 0.4
