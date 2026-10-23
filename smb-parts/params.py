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

WEB_T = 3.0                # the bit that bridges the top of the bar
LEG_T = 2.5                # the inner leg, down the back of the bar
GRIP = 12.0                # how far down the bar the slot holds. Short of
                           # BAR_RISE so it seats on the bar, not the floor.
RELIEF = 1.2               # how far the art stands proud of the plate
CHAMFER = 0.6              # lead-in where the slot opens, so a 0.2 mm fit
                           # does not have to start on a square edge

# ---------------------------------------------------------------------------
# THE SPLIT: brackets stay on the shelf, the art clips onto them
# ---------------------------------------------------------------------------
#
# Section, front to back. Y is depth into the shelf, Z is up.
#
#   art plate | hook zone  | wall | the bar slot | inner leg
#   0 .. 2.4  | 2.4 .. 6.6 | ..7.2| 7.2 .. 11.4  | 11.4 .. 13.9
#             ^ the bracket's front plate lives at 2.4..4.8 and the art's
#               lips wrap behind it at 5.0..6.6
#
# The art's hooks are a C opening backwards. The bracket passes through the
# gap between the two lips, which is the only route from its front plate to
# the bar cap behind -- a continuous hook means there is no way round in X.

BRACKETS_PER_SHELF = 3     # flush left, centred on the panel joint, flush
                           # right. The middle one straddles the joint and
                           # lines the two panels up, so no half-lap.
BRACKET_W = 25.0           # how long each bracket is along the shelf

ART_T = 2.4                # the art plate, six 0.4 walls
BRK_T = 2.4                # the bracket's front plate -- what the hooks grab
HOOK_T = 1.6               # the art's top and bottom returns
HOOK_LIP_BOT = 2.5         # how far the bottom lip stands up behind the plate
CLIP_FIT = 0.2             # clearance around the captured plate
CLIP_GRAB = 0.25           # the snap: how far the bottom mouth is narrower
                           # than the plate, so it has to flex on. Rob asked
                           # for 0.1-0.3 and this sits in the middle.
GRAB_H = 1.0               # height of the snap bump

# HOOK_LIP_TOP is NOT free. The top lip hangs behind the bracket's front
# plate, and the bracket's body has to reach past it to meet the web over
# the bar. That leaves exactly the web's thickness to share out:
HOOK_LIP_TOP = WEB_T - HOOK_T - CLIP_FIT        # 1.2

HOOK_D = BRK_T + CLIP_FIT + HOOK_T      # 4.2, how far the returns reach back
FRONT_WALL = 0.6           # the sliver carrying the body up to the web
SLOT_Y0 = ART_T + HOOK_D + FRONT_WALL   # 7.2, where the bar slot starts
DEPTH = SLOT_Y0 + SLOT + LEG_T          # 13.9, all it takes off the shelf

BRK_Z0 = HOOK_T + CLIP_FIT                      # 1.8, plate bottom edge
BRK_Z1 = FACE_H - HOOK_T - CLIP_FIT             # 22.82, plate top edge
BODY_Z0 = HOOK_T + HOOK_LIP_BOT + CLIP_FIT      # 4.3, clear of the bottom lip
BODY_Z1 = FACE_H - WEB_T                        # 21.62, clear of the top lip

# ---------------------------------------------------------------------------
# the fit coupons -- a ladder of slot widths to try on the real shelf before
# committing to eight panels. Nothing else depends on these.
# ---------------------------------------------------------------------------

COUPON_W = 5.0             # how long a slice of the rail each coupon is
COUPON_GAP = 4.0           # space between them on the spine
COUPON_SLOTS = [4.0, 4.1, 4.2, 4.3, 4.4]   # re-centred on the measured 4.2
                                           # after the first ladder, whose
                                           # winner sat at its tight end
CLIP_GRABS = [0.15, 0.25, 0.35]            # the clip ladder: how hard the
                                           # bead flexes past the plate
SPINE_T = 1.2              # the frangible bar joining them, at the bed face
DIGIT_PX = 1.3             # pixel size of the embossed slot number

# ---------------------------------------------------------------------------
# the machine, from ../available-tools.md
# ---------------------------------------------------------------------------

BED_X, BED_Y, BED_Z = 325.0, 320.0, 325.0
NOZZLE = 0.4
