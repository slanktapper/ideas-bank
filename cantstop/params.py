"""Every dimension in the cantstop board game, in millimetres.

This is the single source of truth. Nothing else in the project hard-codes a
number you would ever want to change. Edit here, re-run `python3 build.py`,
and every STL and render regenerates consistently.

Coordinate convention
---------------------
X  across the board, column 2 on the left, column 12 on the right
Y  up the board, row 0 at the bottom (y=0), climbing positive
Z  out of the print bed; the whole board sits on z = 0 and prints flat
"""

# --------------------------------------------------------------------------
# The ladder
# --------------------------------------------------------------------------
# Column numbers 2..12 and how many cells each one holds. The length of a
# column is roughly inverse to how often that total comes up on 2d6, which is
# what makes the push-your-luck maths work: 7 is easy to roll and long to
# climb, 2 is a 1-in-36 shot but only three cells deep.
COLUMNS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
ROWS    = [3, 5, 7, 9, 11, 13, 11, 9, 7, 5, 3]   # 83 cells total

# Columns are CENTRE-aligned: every column is centred on the same midline, so
# a column of n cells runs from k = -(n-1)/2 to +(n-1)/2. Every row count is
# odd, so k is always a whole number and neighbouring columns share rows on
# the same grid.
#
# Bottom-aligning them instead gives the stepped pyramid of the first version.
# Centred, the lattice is a symmetric lens, which is what lets the board sit
# inside an octagonal frame without one end of it being mostly air.

PITCH_X = 22.0      # centre-to-centre spacing between columns
PITCH_Y = 20.0      # centre-to-centre spacing between rows

# --------------------------------------------------------------------------
# Cell collars — the rings a playing piece drops into
# --------------------------------------------------------------------------
COLLAR_OD      = 14.6   # outer diameter of the ring
COLLAR_BORE    = 6.40   # through-bore; the piece's pin lives in here
COLLAR_H       = 5.5    # how proud the ring stands off the bed
COLLAR_CHAMFER = 0.60   # 45 deg lead-in at the top of the bore, so a piece
                        # self-centres instead of catching on the rim
COLLAR_SEGS    = 48     # facets around the ring (export quality)

# The bore runs all the way through. Two reasons: a vertical through-hole
# prints with no support at all, and you can push a stuck piece out from
# underneath instead of levering it out with a fingernail.

# --------------------------------------------------------------------------
# The wireframe lattice
# --------------------------------------------------------------------------
# Struts are RECTANGULAR in section, not round, and their underside sits flat
# on z = 0. That is the whole printability trick: a round rod spanning two
# collars is a 3.2 mm unsupported overhang, a flat-bottomed bar is just a
# wide extrusion. The entire board prints support-free.
STRUT_W = 3.20      # width of a lattice strut
STRUT_H = 4.00      # height; deliberately shorter than COLLAR_H so the rings
                    # stand proud and the lattice reads as recessed webbing

FRAME_W = 5.20      # the octagon runs thicker — it is what you pick the
FRAME_H = 4.80      # board up by, and it is the only frame-section member

# Diagonal bracing between adjacent cells. "alternating" puts one diagonal in
# each lattice quad, flipping direction like herringbone: about half the
# plastic and print time of full X-bracing for most of the stiffness.
DIAGONALS = "alternating"   # "none" | "alternating" | "full"

# --------------------------------------------------------------------------
# The octagonal frame
# --------------------------------------------------------------------------
# A true octagon: a rectangle around everything with its four corners cut at
# 45 degrees. The lattice is a lens and does not reach the corners, so the
# cut-off triangles are where the number shields and the bracing spokes live.
OCTAGON_MARGIN  = 6.0    # clear air between the content and the frame
OCTAGON_CHAMFER = 0.55   # corner cut, as a fraction of the shorter half-span.
                         # 0.586 would give a regular octagon when the span is
                         # square; the board is taller than it is wide, so
                         # slightly under that reads best.
OCTAGON_SPOKE_W = 3.20   # bracing struts from the lattice out to the frame
OCTAGON_SPOKE_H = 4.00

# --------------------------------------------------------------------------
# Column number shields — at the TOP of each column, and playable
# --------------------------------------------------------------------------
# Each column's topmost cell is its numbered summit. The ring is a normal
# cell, so a piece drops into it like any other; the number sits on a shield
# fused to the ring from above. Climbing a column and landing on its number
# is therefore the same move as any other, which is the point.
PLAQUE_W       = 20.0
PLAQUE_H       = 18.0
PLAQUE_T       = 4.5    # shield thickness in Z. Thicker than it needs to be
                        # for strength: it lifts the digit, which is what
                        # decides the viewing angle below.
PLAQUE_FILLET  = 2.0    # corner rounding (approximated by an inset polygon)

# The shield stands off its summit ring on a short neck, and it leans OUTWARD
# -- radially away from the middle of the lattice -- rather than straight up.
#
# Both of those exist for one reason. A piece sitting on a summit is 12.6 mm
# tall and the digit is 5.7 mm off the bed, so a shield tucked in behind the
# ring is hidden by the very piece that claims the column: in the first
# octagon build you had to be looking down from nearly 70 degrees to read a
# claimed number. Leaning the shield outward moves the digit sideways out of
# the piece's shadow, and the stand-off buys the rest of the angle back.
SHIELD_OFFSET   = 26.0   # ring centre to shield centre
SHIELD_MAX_TILT = 55.0   # degrees off vertical; past this the outer columns
                         # push the board wider than it is tall
NUMERAL_SIZE   = 9.0    # cap height of the digits (10-12 scale down to fit)
NUMERAL_MAX_W  = 12.0   # widest a number may be. The shield is sized so that
                        # the digit keeps 1.2 mm from the ring below it and
                        # 2.0 mm from every edge the bracing spoke leaves by --
                        # at 18 mm wide the spoke passed 0.19 mm off the "2".
NUMERAL_EMBOSS = 1.20   # how far the digits stand proud of the shield
NUMERAL_FONT_WEIGHT = "bold"

# --------------------------------------------------------------------------
# Playing pieces
# --------------------------------------------------------------------------
# The stacking interface. A piece has a PIN on the bottom and a SOCKET on the
# top, both on the same axis and the same nominal size as a collar bore. So:
#   pin -> board collar        (piece sits in a cell)
#   pin -> socket of the piece below   (player A stacks on player B)
# One interface, used three ways, and it is the only tolerance in the design
# that actually matters.
PEG_PIN_D        = 5.90   # nominal 6.0 less 0.10 for FDM swell
PEG_PIN_H        = 3.20   # short. With a body this wide the SHOULDER does the
                          # work of keeping a piece upright -- it seats on a
                          # 3.2-to-6.6 mm contact ring -- so the stub only has
                          # to locate, not stabilise.
PEG_PIN_CHAMFER  = 0.60   # lead-in at the very bottom of the pin

PEG_SOCKET_D     = 6.35   # holes print undersize, so the socket is cut over
PEG_SOCKET_DEPTH = 3.80   # deeper than the pin is long: the pin never bottoms
                          # out, the shoulder seats instead. Consistent stack
                          # height regardless of how hard you press.
PEG_SOCKET_CHAMFER = 0.50

# Body profile, as (radius, height-above-the-shoulder) pairs. A pawn-ish waist
# so it can be picked up with fingertips rather than fingernails.
PEG_BODY_H = 9.40         # this is also the stack pitch: each piece stacked
                          # adds exactly this much height
# Widened from the first version: shoulder radius 5.70 -> 6.60, so the piece
# is 13.2 mm across rather than 11.4 mm. The extra width buys two things --
# something to actually grip, and a much wider seating ring, which is what
# lets the stub be short. It also thickens the wall around the socket at the
# waist to 5.38 - 3.175 = 2.21 mm, about five perimeters.
PEG_BODY_PROFILE = [
    (6.60, 0.00),
    (6.60, 1.10),
    (5.73, 3.30),
    (5.38, 5.40),
    (5.73, 7.60),
    (5.90, 8.70),
    (5.90, 9.40),
]
PEG_SEGS = 64

# The runner (the shared neutral marker you advance during a turn, before you
# decide to bank) uses the identical pin/socket interface so it still stacks,
# but carries two raised bands and stands taller so it is unmistakable across
# the table.
RUNNER_BODY_H = 12.40
RUNNER_BODY_PROFILE = [
    (6.60,  0.00),
    (6.60,  1.10),
    (5.73,  2.60),
    (6.48,  3.20),   # lower band
    (6.48,  4.30),
    (5.73,  4.90),
    (5.44,  6.20),
    (5.73,  7.50),
    (6.48,  8.10),   # upper band
    (6.48,  9.20),
    (5.73,  9.80),
    (5.90, 11.30),
    (5.90, 12.40),
]

# --------------------------------------------------------------------------
# Piece counts
# --------------------------------------------------------------------------
PLAYERS            = 4
MARKERS_PER_PLAYER = 11   # one per column
RUNNERS            = 3    # shared, neutral colour

# --------------------------------------------------------------------------
# Lattice-to-collar weld radius
# --------------------------------------------------------------------------
# Struts are drawn between cell CENTRES, then trimmed back to this radius
# before they are built. That matters: a strut run all the way to the centre
# would plough straight through the bore and plug the hole. At 5.5 mm the
# strut still bites 1.0 mm into the collar wall for a solid weld, while
# leaving 3.0 mm of ring between it and the 3.2 mm bore.
WELD_R = 6.20

# --------------------------------------------------------------------------
# Fit-test coupon
# --------------------------------------------------------------------------
# Print this FIRST. It is a ~6 g, ~12 minute part carrying five bores either
# side of nominal. Whichever one takes a test pin with a firm push and holds
# the piece upside down is your number; set COLLAR_BORE to it and rebuild
# before you commit ten hours to the board.
FIT_TEST_BORES = [6.20, 6.30, 6.40, 6.50, 6.60]
FIT_COUPON_T   = 3.0    # backing bar only; it does not want the shields'
                        # extra thickness, which is there to lift the digits

# --------------------------------------------------------------------------
# Printer envelope (Bambu Lab H2D, single nozzle) — see ../available-tools.md
# --------------------------------------------------------------------------
BED_X = 325.0
BED_Y = 320.0
BED_Z = 325.0
