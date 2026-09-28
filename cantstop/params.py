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

# Columns are bottom-aligned: every column starts on the same baseline and
# climbs to a different height, so the silhouette is a stepped pyramid peaking
# at 7. That is the iconic shape and it is also what makes the lattice
# self-bracing.

PITCH_X = 22.0      # centre-to-centre spacing between columns
PITCH_Y = 20.0      # centre-to-centre spacing between rows

# --------------------------------------------------------------------------
# Cell collars — the rings a playing piece drops into
# --------------------------------------------------------------------------
COLLAR_OD      = 13.0   # outer diameter of the ring
COLLAR_BORE    = 6.40   # through-bore; the piece's pin lives in here
COLLAR_H       = 7.0    # how proud the ring stands off the bed
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
STRUT_H = 4.60      # height; deliberately shorter than COLLAR_H so the rings
                    # stand proud and the lattice reads as recessed webbing

FRAME_W = 5.20      # the perimeter runs thicker — it is what you pick the
FRAME_H = 6.20      # board up by, and it stops the pyramid racking

# Diagonal bracing between adjacent cells. "alternating" puts one diagonal in
# each lattice quad, flipping direction like herringbone: about half the
# plastic and print time of full X-bracing for most of the stiffness.
DIAGONALS = "alternating"   # "none" | "alternating" | "full"

BASE_RAIL_DY = -14.0    # y of the full-width rail under row 0
BASE_RAIL_W  = 6.0
BASE_RAIL_H  = 6.20

# --------------------------------------------------------------------------
# Column number plaques
# --------------------------------------------------------------------------
PLAQUE_W       = 17.0
PLAQUE_H       = 13.0   # in Y
PLAQUE_T       = 3.0    # plaque thickness in Z
PLAQUE_DY      = -26.0  # y centre, hanging below the base rail
PLAQUE_DROP_DX = 7.5    # the two drop struts that hang each plaque off the
PLAQUE_DROP_Y  = -24.0  # base rail sit either side of the digit, not over it.
                        # One central drop reads fine in plan and then prints
                        # a bar straight across the numeral -- caught in
                        # renders/03-lattice-detail.png.
PLAQUE_FILLET  = 2.0    # corner rounding (approximated by an inset polygon)
NUMERAL_SIZE   = 9.0    # cap height of the digits (single digits;
                        # 10-12 scale down to fit between the drops)
NUMERAL_EMBOSS = 1.20   # how far the digits stand proud of the plaque
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
PEG_PIN_H        = 5.20
PEG_PIN_CHAMFER  = 0.60   # lead-in at the very bottom of the pin

PEG_SOCKET_D     = 6.35   # holes print undersize, so the socket is cut over
PEG_SOCKET_DEPTH = 5.70   # deeper than the pin is long: the pin never bottoms
                          # out, the shoulder seats instead. Consistent stack
                          # height regardless of how hard you press.
PEG_SOCKET_CHAMFER = 0.50

# Body profile, as (radius, height-above-the-shoulder) pairs. A pawn-ish waist
# so it can be picked up with fingertips rather than fingernails.
PEG_BODY_H = 9.40         # this is also the stack pitch: each piece stacked
                          # adds exactly this much height
# The waist radius is bounded from below by the socket: at the narrowest
# point the wall between the outside of the piece and the socket bore is
# 4.65 - 3.175 = 1.48 mm, which is about 3.5 perimeters at a 0.42 mm line
# width. Take the waist in any further and the socket starts showing through.
PEG_BODY_PROFILE = [
    (5.70, 0.00),
    (5.70, 1.10),
    (4.95, 3.30),
    (4.65, 5.40),
    (4.95, 7.60),
    (5.10, 8.70),
    (5.10, 9.40),
]
PEG_SEGS = 64

# The runner (the shared neutral marker you advance during a turn, before you
# decide to bank) uses the identical pin/socket interface so it still stacks,
# but carries two raised bands and stands taller so it is unmistakable across
# the table.
RUNNER_BODY_H = 12.40
RUNNER_BODY_PROFILE = [
    (5.70,  0.00),
    (5.70,  1.10),
    (4.95,  2.60),
    (5.60,  3.20),   # lower band
    (5.60,  4.30),
    (4.95,  4.90),
    (4.70,  6.20),
    (4.95,  7.50),
    (5.60,  8.10),   # upper band
    (5.60,  9.20),
    (4.95,  9.80),
    (5.10, 11.30),
    (5.10, 12.40),
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
# leaving 2.3 mm of ring between it and the 3.2 mm bore.
WELD_R = 5.50

# --------------------------------------------------------------------------
# Fit-test coupon
# --------------------------------------------------------------------------
# Print this FIRST. It is a ~6 g, ~12 minute part carrying five bores either
# side of nominal. Whichever one takes a test pin with a firm push and holds
# the piece upside down is your number; set COLLAR_BORE to it and rebuild
# before you commit ten hours to the board.
FIT_TEST_BORES = [6.20, 6.30, 6.40, 6.50, 6.60]

# --------------------------------------------------------------------------
# Printer envelope (Bambu Lab H2D, single nozzle) — see ../available-tools.md
# --------------------------------------------------------------------------
BED_X = 325.0
BED_Y = 320.0
BED_Z = 325.0
