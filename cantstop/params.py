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

# How far each column falls short of the LONGEST one, in mm, counting
# outward from the middle: column 7, then 6 and 8, then 5 and 9, and so on.
# The CELL COUNTS are fixed by the game; this is purely how far apart the
# cells in a column are spread, so a column that gives up less height simply
# spaces its own cells a little wider.
#
# A whole box (20 mm) per step is the plain version, where every column shares
# one row pitch and the lens comes to a sharp point at the top.
#
# Here the middle five columns -- 5 through 9 -- step by only a QUARTER of a
# box, which flattens the top of the lens and pulls its shoulders right out
# towards the frame. Every column beyond them follows by the same amount
# rather than staying put; otherwise the next step down would be an awkward
# box and three quarters and the silhouette would kink.
# So: a quarter box twice, then whole boxes all the way out.
COLUMN_SHORTFALL = [0.0, 5.0, 10.0, 30.0, 50.0, 70.0]

PITCH_X = 22.0      # centre-to-centre spacing between columns
PITCH_Y = 20.0      # row pitch of the LONGEST column. Shorter columns get a
                    # pitch of their own, set by COLUMN_SHORTFALL above.

# --------------------------------------------------------------------------
# Cells — a pad with a post standing on it
# --------------------------------------------------------------------------
# The interface runs MALE-UP throughout: the board offers a post, a piece has
# a socket underneath and a post of its own on top. So a piece drops onto the
# board, and the next piece drops onto that one, with one geometry doing both.
#
# The pad is what a piece actually sits on. Its top face is an unobstructed
# annulus from the post out past the piece's skirt, which is a far wider and
# steadier seat than the rim of a ring.
PAD_OD    = 13.8    # outer diameter of the pad
PAD_H     = 4.00    # pad height; also the height of every seating face
POST_D    = 5.90    # nominal 6.0 less 0.10 for FDM swell
POST_H    = 3.20    # how far the post stands proud of its pad
POST_CHAMFER = 0.60 # 45 deg lead-in at the top, so a piece self-centres
CELL_SEGS = 48      # facets around a pad (export quality)

# Nothing needs a through-bore any more, which removes a whole class of
# problem: struts cannot plug a hole that does not exist. The only rule left
# is that struts stay BELOW the pad tops, so they never foul a seating face
# or a post.

# --------------------------------------------------------------------------
# The wireframe lattice
# --------------------------------------------------------------------------
# Struts are RECTANGULAR in section, not round, and their underside sits flat
# on z = 0. That is the whole printability trick: a round rod spanning two
# collars is a 3.2 mm unsupported overhang, a flat-bottomed bar is just a
# wide extrusion. The entire board prints support-free.
STRUT_W = 3.20      # width of a lattice strut
STRUT_H = 3.40      # height; deliberately shorter than PAD_H so the pads
                    # stand proud and the lattice reads as recessed webbing

FRAME_W = 5.20      # the octagon runs thicker — it is what you pick the
FRAME_H = 4.40      # board up by, and it is the only frame-section member

# Staggered columns make the lattice triangular on their own: every cell ties
# to the two nearest in each neighbouring column, which is already a braced
# truss. There is no quad left to put a diagonal in.

# --------------------------------------------------------------------------
# The octagonal frame
# --------------------------------------------------------------------------
# A true octagon: a rectangle around everything with its four corners cut at
# 45 degrees. The lattice is a lens and does not reach the corners, so the
# cut-off triangles are where the number shields and the bracing spokes live.
OCTAGON_MARGIN  = 6.0    # clear air between the content and the frame
# A REGULAR octagon: all eight edges the same length. That needs a square
# bounding box (so the half-span is taken as the larger of the two) and a
# chamfer of exactly 2/(2+sqrt2) = 0.5858 of it, at which point the four flats
# and the four corner cuts come out identical.
OCTAGON_REGULAR = True
OCTAGON_SPOKE_W = 3.20   # bracing struts from the lattice out to the frame
OCTAGON_SPOKE_H = 3.40

# --------------------------------------------------------------------------
# Column number shields — at the TOP of each column, and playable
# --------------------------------------------------------------------------
# Each column's topmost cell is its numbered summit. The ring is a normal
# cell, so a piece drops into it like any other; the number sits on a shield
# fused to the ring from above. Climbing a column and landing on its number
# is therefore the same move as any other, which is the point.
PLAQUE_W       = 17.0   # narrow enough to leave 5 mm between neighbouring
PLAQUE_H       = 20.0   # summit boxes: the columns now step down in half
                        # boxes, so the summits run in a shallow staircase
                        # and their boxes sit much closer than they used to
PLAQUE_T       = 4.00   # same as PAD_H, so every seating face is at one
                        # height. Struts stand 3.4 mm, so anything running
                        # under a box is buried inside it.
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
# Each column's topmost cell IS its number box: a rounded plate standing in
# for the usual round pad. The digit and the post share the box's centre.
#
# The post stands in the middle of the digit, so the only question is what
# colour it should be -- and the answer is neither black nor orange but BOTH,
# split by the digit itself. The post is cut by the glyph extruded vertically
# through it: the part of the post where the digit passes goes in the number's
# colour, the rest in the board's. Seen from directly above the number is
# therefore complete -- the post is coloured by exactly what it covers.
#
# Rendered head on and counted in pixels: a solid black post loses 16% of an
# 8 and destroys its waist; split this way, 100% of the glyph survives.
#
# That only works if the digit is large next to the post, hence a box big
# enough to carry a 16 mm cap height over a 5.9 mm post.
SUMMIT_STEP  = 4.0    # small step out for the top cell, so its box clears the
                      # pad below it

NUMERAL_SIZE   = 16.0   # cap height of the digits
NUMERAL_MAX_W  = 14.0   # widest a number may be; 10, 11 and 12 scale to fit,
                        # and on those the post falls in the gap BETWEEN the
                        # two digits, where it costs nothing
NUMERAL_DEPTH  = 1.20   # how deep the digit is cut into the box
NUMERAL_POST_CLEAR = 0.00  # the pocket stops exactly at the post's edge, so
                           # the orange in the pocket and the orange on the
                           # post meet with no black seam between them. The
                           # post still stands on solid plate.
NUMERAL_FONT_WEIGHT = "bold"

# --------------------------------------------------------------------------
# Playing pieces
# --------------------------------------------------------------------------
# A piece is a socket underneath and a post on top, both on the same axis and
# the same nominal size as the board's post. So:
#   board post -> piece socket          (a piece sits in a cell)
#   piece post -> the socket above it   (player A stacks on player B)
# One interface, used twice, and it is the only tolerance that matters.
#
# Reversed from the first version, which had the pin on the piece and the bore
# in the board. Male-up means the board carries no through-holes at all, so a
# strut can never plug one; it also means the piece seats on a wide annular
# face rather than on the rim of a ring.
PEG_POST_D       = 5.90   # the post on top of a piece; matches the board's
PEG_POST_H       = 3.20
PEG_POST_CHAMFER = 0.60   # lead-in at the top of the post

PEG_SOCKET_D     = 6.35   # holes print undersize, so the socket is cut over
PEG_SOCKET_DEPTH = 3.80   # deeper than a post is long: the post never bottoms
                          # out, the SKIRT seats on the face below instead.
                          # Stack height is exact regardless of how hard you
                          # press.
PEG_SOCKET_CHAMFER = 0.50

# The socket roof is a 45 degree cone rather than a flat ceiling. Printed the
# right way up -- post uppermost -- a flat roof would be a 6.35 mm bridge over
# thin air; a cone self-supports and nothing ever touches it.

PEG_BODY_H = 9.40         # skirt to top face. This is also the stack pitch:
                          # each piece stacked adds exactly this much height.

# 13.2 mm across. The width buys two things -- something to actually grip,
# and a wide skirt, which is what lets the post be short: the skirt does the
# work of keeping a piece upright, so the post only has to locate it.
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
# There is no bore to protect any more -- the post starts at z = PAD_H and
# every strut stops below that -- so struts can run well in under the pad and
# weld properly instead of just grazing its edge.
WELD_R = 4.00

# --------------------------------------------------------------------------
# Fit-test coupon
# --------------------------------------------------------------------------
# Print this FIRST. It is a ~6 g, ~12 minute part carrying five bores either
# side of nominal. Whichever one takes a test pin with a firm push and holds
# the piece upside down is your number; set COLLAR_BORE to it and rebuild
# before you commit ten hours to the board.
# The board is male now, so the coupon carries POSTS and you try a real piece
# over each. Print it in the BOARD's material; print the test pieces in the
# pieces' material, or the coupon tests the wrong pair.
FIT_TEST_POSTS = [5.70, 5.80, 5.90, 6.00, 6.10]
FIT_COUPON_T   = 3.0    # backing bar only; it does not want the shields'
                        # extra thickness, which is there to lift the digits

# --------------------------------------------------------------------------
# Printer envelope (Bambu Lab H2D, single nozzle) — see ../available-tools.md
# --------------------------------------------------------------------------
BED_X = 325.0
BED_Y = 320.0
BED_Z = 325.0
