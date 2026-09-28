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
#
# LEVELLING 5 TO 9 -- [0, 0, 0, 20, 40, 60] -- was tried and rendered. It
# looks better: the top of the lens is flat across five columns instead of
# coming to a point. It costs 13 mm of frame, because the shoulders of the
# lens move out into the octagon's cut corners, and the board goes 284.9 ->
# 297.6 mm. On its own that still fits the bed. Together with the title
# below it does not; see TITLE_TEXT.
#
# The four outer steps are 25 mm -- a box and a quarter each -- rather than a
# whole box. That is not a silhouette decision, it is what buys back a REGULAR
# octagon. The frame is bound by its DIAGONAL, and the point that binds it is
# the top outer corner of column 2's number box: far out in x and well up in
# y, which is exactly where the corner cut is. Dropping the outer columns
# lowers that corner, and lowers the letter hanging under the same column
# too, so it pays twice. [0, 0, 0, 20, 40, 60] needs a 326 mm frame; this
# needs 310.
COLUMN_SHORTFALL = [0.0, 0.0, 0.0, 25.0, 50.0, 75.0]

# Extra span given to a column at the BOTTOM only, same indexing. Shortfall
# moves both ends of a column because the grid is centred; this moves one.
#
# It exists because 5 through 9 being level leaves them all the same span with
# 9, 11 and 13 cells in it -- so column 7's dots are packed at 20 mm while
# column 5's are strung out at 30. Columns 6, 7 and 8 carry no title letter,
# so the plate directly below them is empty: dropping their bottoms fills that
# and evens the spacing out, and costs nothing, because what sets the bottom
# of the board is the letters either side of that gap, not the dots.
COLUMN_DROP = [21.0, 16.0, 0.0, 0.0, 0.0, 0.0]

PITCH_X = 24.0      # centre-to-centre spacing between columns. Widened from
                    # 22 along with the title: a regular octagon is square, so
                    # a lens that is much taller than it is wide leaves the
                    # left and right flats empty. 24 brings the content to
                    # 266 x 282, which is close enough to square to fill it.
PITCH_Y = 20.0      # row pitch of the LONGEST column. Shorter columns get a
                    # pitch of their own, set by COLUMN_SHORTFALL above.

# --------------------------------------------------------------------------
# Board style
# --------------------------------------------------------------------------
# "lattice"  the open wireframe truss: rings tied by flat-bottomed struts and
#            braced out to the octagon. Light, but floppy.
# "slab"     a solid octagonal plate with the posts standing on it. Nine to
#            twenty times stiffer, and -- because a lattice is nearly all
#            perimeter and cannot be hollowed -- no heavier, so long as the
#            infill stays low.
BOARD_STYLE = "slab"

SLAB_T = 6.0        # plate thickness
SLAB_INFILL = 0.10  # what the slicer should be set to; the geometry does not
                    # care, but every mass figure in the build report assumes
                    # it. Skins cost 94 g over this octagon before any infill
                    # at all, so the infill number matters far less than it
                    # looks: 5% and 29% are 131 g and 221 g respectively.

RIM_W = 8.0         # a raised lip around the edge of the slab
RIM_H = 1.20        # matched to NUMERAL_DEPTH, so the lip and the numbers
                    # share one relief dimension
RIM_CLEAR = 4.0     # air between the inside of the lip and the nearest pad

# The top of the lip prints in the NUMBERS' colour, so the board carries a
# white border as well as white numerals. Only the top few layers change: the
# rest of the lip stays with the body, so there is a red edge under a white
# cap rather than a white wall standing on red.
#
# This must be a whole number of layers. Land it mid-layer and the slicer has
# to give that layer to one colour or the other, and the border comes out a
# layer thicker or thinner than asked for -- on a 3-layer cap that is a third
# of it. test_fit.py checks the division.
LAYER_H   = 0.20    # what the board will be sliced at; see print-guide.md
RIM_CAP_H = 0.60    # 3 layers. 0 puts the whole lip in the body colour;
                    # RIM_H puts the whole lip in the numbers' colour

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

# The top of a post can print in the NUMBERS' colour instead of the board's,
# which turns a field of 83 identical red dots into something with a rhythm
# you can follow up a column.
#
#   "none"          every post in the board's colour
#   "even-rows"     every other cell up a column, counting from the bottom
#   "odd-rows"      the other half
#   "even-columns"  all of 2, 4, 6, 8, 10, 12
#   "all"           every post
#
# SUMMIT posts are never capped whatever this says. The top of a summit post
# is already split by its digit so the number reads whole from above, and
# flooding it with the number's colour is exactly the failure that split was
# built to avoid -- the post merges into the glyph and the number turns to
# mush.
POST_CAP   = "even-columns"
POST_CAP_H = 0.60   # 3 layers at 0.20, same as the cap on the lip. It lands
                    # on the chamfer, so the whole of what you see from above
                    # is the accent colour and the sides stay board-coloured.

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
# A REGULAR octagon -- all eight edges the same length -- needs a square
# bounding box (so the half-span is taken as the larger of the two) and a
# chamfer of exactly 2/(2+sqrt2) = 0.5858 of it, at which point the four flats
# and the four corner cuts come out identical.
#
# FALSE, and not for looks: a regular octagon is SQUARE, and the dual-nozzle
# bed is not. 300 x 320 mm has 20 mm more in Y than in X, and the content --
# thirteen cells tall, eleven columns wide, with the title below -- is 266 x
# 282. Forcing a square frame around that spends the board's width on empty
# plate at the left and right and puts it 10 mm over the bed in exactly the
# axis that is short.
#
# Sizing each axis to its own content gives 290.0 x 306.0 and fits with 10 mm
# to spare in X and 14 in Y. Nothing else moves: same pitches, same drops,
# same numbers, same lip, same pieces.
#
# It was regular for one revision and it did look better. Equal edges cost
# 20 mm of X and the bed has not got it. True is one line away if the board
# is ever printed in one colour, or on something bigger.
OCTAGON_REGULAR = False
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

NUMERAL_SIZE   = 16.0   # cap height of EVERY number, one and two digit alike
NUMERAL_MAX_W  = 24.0   # widest a number may be. A two-digit number is 26 mm
                        # at this cap height, so 10, 11 and 12 are condensed
                        # by 8% -- X ONLY, never a uniform scale, which would
                        # take their cap height down with their width and make
                        # them read as a smaller set of labels. Every number
                        # on the board is 16 mm tall.
                        #
                        # The 2 mm matters: this box's outer corner is what
                        # binds the octagon's diagonal, so every millimetre
                        # off it is two off the frame.
                        #
                        # Scaling them uniformly was the first version and it
                        # was wrong: clamped to 14 mm, "12" came out at 0.54
                        # scale and so 8.6 mm tall against everyone else's 16,
                        # and the three of them read as a different, smaller
                        # set of labels. Cap height is what the eye reads as
                        # SIZE; 8% of width is not visible next to it.
                        #
                        # The ceiling is not typographic. A piece seated on a
                        # neighbouring column reaches to within 13.75 mm of
                        # this column's centre, so a number wider than 27.5 mm
                        # would have its ends stood on by the column next door.
                        # 24 leaves 1.75 mm.
NUMERAL_BOX_W  = 26.0   # footprint a number reserves on the plate: the widest
                        # number plus a margin, and the SAME for every column
                        # so the octagon stays symmetric about the lens rather
                        # than growing only on the two-digit side
NUMERAL_DEPTH  = 1.20   # how deep the digit is cut into the box
NUMERAL_POST_CLEAR = 0.00  # the pocket stops exactly at the post's edge, so
                           # the orange in the pocket and the orange on the
                           # post meet with no black seam between them. The
                           # post still stands on solid plate.
NUMERAL_FONT_WEIGHT = "bold"

# --------------------------------------------------------------------------
# The title, spelled out along the bottom of the lens
# --------------------------------------------------------------------------
# One letter per column, engraved into the plate exactly as the numbers are
# and printed in their colour. The lower half of the board is a cell field
# with nothing to read on it, and this is what goes there.
#
# CAN'T descends left to right and STOP climbs back, because the columns
# they hang under do -- 2 is short and 5 is long, then 8 and 9 are long and
# 11 is short. Columns 6 and 7 carry no letter, and the hole they leave in
# the middle is the word space.
#
# OFF BY DEFAULT, because it does not come free. The letters hang below the
# lens, which is the one direction the board has no room in: the octagon's
# corners are cut away and a letter that is both far to one side and far down
# is the most expensive content that can be put on one.
#
#   as it stands, no title                        284.9 mm   35 mm bed spare
#   level 5-9, no title                           297.6 mm   22 mm
#   title, 16 mm letters, 6 mm lip                308.5 mm   11 mm
#   title, 20 mm letters, 8 mm lip                316.7 mm    3 mm  -- no
#   title on one level baseline                   394.8 mm   off the bed
#
# Those figures are all for a REGULAR octagon, which is what made it a
# straight trade against the 8 mm lip. Letting the frame hug the content
# instead (OCTAGON_REGULAR = False) pays for the whole thing: 290 x 306 mm
# with the title, the levelled top, a wider column pitch AND the 8 mm lip.
#
# Set TITLE_TEXT = {} to take the title off.
#
# CAN'T hangs under 2345 and STOP under 9 10 11 12, so the two halves are
# mirror images. 6, 7 and 8 carry no letter, and the hole they leave in the
# middle is the word space.
TITLE_TEXT  = {2: "C", 3: "A", 4: "N'", 5: "T",
               9: "S", 10: "T", 11: "O", 12: "P"}
TITLE_SIZE  = 16.0   # cap height
TITLE_MAX_W = 20.0   # condensed in X only past this, as the numbers are
TITLE_FOLLOW = 1.0   # 1 = each letter hangs under its own column and the
                     # title follows the underside of the lens; 0 = one
                     # straight baseline. See board.title_letters(): a level
                     # title is worth 78 mm of extra frame on an octagon.
TITLE_GAP   = 20.0   # from the bottom cell's centre to the letter's centre.
                     # A piece on that cell reaches 8.25 mm and a letter
                     # reaches 10, so this leaves about 6 mm of plate between
                     # the two.
TITLE_DEPTH = 1.20   # same relief as the numbers and the lip

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
# THE BOARD IS PRINTED. Everything it carries -- POST_D, POST_H, the pitches,
# the octagon, the numbers -- is frozen from here on, and these numbers have
# to work against a board that already exists. What a piece may change is its
# own proportions.
#
# Second pass: a THIRD shorter and a QUARTER wider than the first. The first
# pieces were taller than they were wide (12.60 x 13.20) and read as pegs
# standing on the board rather than counters sitting in it; 8.45 x 16.50 is
# a squat disc you can pick up with two fingers and see past.
PEG_POST_D       = 5.90   # the post on top of a piece; matches the board's
PEG_POST_H       = 2.15   # scaled with the rest of the piece. Shorter than
                          # the board's 3.20 post, which is fine: the socket
                          # is sized for the BOARD's post, and the skirt is
                          # what keeps a piece upright -- the post only
                          # locates it, and it does that in 2 mm as well as 3.
PEG_POST_CHAMFER = 0.40   # lead-in at the top of the post

PEG_SOCKET_D     = 6.13   # Holes print undersize, so the socket is cut over
                          # the 5.90 post it has to swallow. This is the one
                          # number in the project that only a print can
                          # settle, and it is on its second value.
                          #
                          # 6.35 was the first guess: 0.45 mm diametral, a
                          # deliberately loose slip fit for a machine that had
                          # not been commissioned. HALVED to 0.23 here, on the
                          # evidence of the stub -- which came off the printer
                          # at size, so the 0.45 was insurance against a
                          # problem that did not materialise and was only
                          # buying slop.
                          #
                          # 0.23 diametral is 0.115 of a radius, half a line
                          # width. Below about 0.15 diametral it stops being a
                          # fit and becomes an interference the plastic has to
                          # absorb, so there is not another halving after this
                          # one.
                          #
                          # THE BOARD'S POST IS UNCHANGED at 5.90, so the stub
                          # that is already printed is still the right fixture
                          # to try new pieces on.
PEG_SOCKET_DEPTH = 3.60   # deeper than the BOARD's post is long: the post
                          # never bottoms out, the SKIRT seats on the face
                          # below instead. Stack height is exact regardless
                          # of how hard you press.
PEG_SOCKET_CHAMFER = 0.50

# The socket roof is a 45 degree cone rather than a flat ceiling. Printed the
# right way up -- post uppermost -- a flat roof would be a 6.35 mm bridge over
# thin air; a cone self-supports and nothing ever touches it.
#
# A FULL cone needs the socket radius in height -- 3.18 mm on top of the 3.60
# the socket itself takes -- and the body is only 6.30 mm tall now, so there
# is no room for one. The cone is truncated instead: it climbs at 45 degrees
# until PEG_SOCKET_ROOF of solid is left above it, and the small flat left at
# the top is bridged. The span comes out around 2.5 mm, which is nothing; the
# rule that matters is that it stays small, and test_fit.py checks it.
PEG_SOCKET_ROOF  = 0.80   # solid above the socket roof; 4 layers at 0.20

PEG_BODY_H = 6.30         # skirt to top face. This is also the stack pitch:
                          # each piece stacked adds exactly this much height.

# 16.5 mm across. The width buys two things -- something to actually grip,
# and a wide skirt, which is what lets the post be short: the skirt does the
# work of keeping a piece upright, so the post only has to locate it. At this
# width the skirt is wider than the lattice board's 13.8 mm pads, so a piece
# overhangs one by 1.35 mm; the seat is still a 4 mm annulus and that is what
# matters. On the slab -- which is what is printed -- the plate is the pad and
# the question does not arise.
PEG_BODY_PROFILE = [
    (8.25, 0.00),
    (8.25, 0.75),
    (7.16, 2.20),
    (6.72, 3.60),
    (7.16, 5.10),
    (7.38, 5.85),
    (7.38, 6.30),
]
PEG_SEGS = 64

# --------------------------------------------------------------------------
# Four pieces, one interface
# --------------------------------------------------------------------------
# Each player gets a different SHAPE. What none of them may change is the
# interface: the socket underneath, the post on top, the skirt that seats,
# and PEG_BODY_H. Player A stacks on player B, so every piece has to accept
# every other piece and add exactly the same height doing it.
#
# What that leaves free is the silhouette between the skirt and the top face,
# and it is less than it looks:
#
#   - the top face is what the NEXT piece stands on, so it cannot taper away
#     to a point. It has to keep a seating annulus 3 mm wide, which puts a
#     floor of about 6 mm on the top radius. No cones, no spires.
#   - nothing may exceed PEG_MAX_R, or pieces touch in adjacent cells.
#   - printed flat with no supports, so no surface may overhang more than 45
#     degrees: a profile may widen going up by at most one millimetre of
#     radius per millimetre of height. test_fit.py measures this on all four.
#
# Anything added on top of the lathe is cut, never added: a vertical cylinder
# taken out of the side leaves a scallop, and scallops are self-supporting
# whatever their depth.
PLAYER_STYLES = ["counter", "crown", "saucer", "cog"]
PLAYER_LABELS = ["A", "B", "C", "D"]   # what the printable sets are called
PEG_MAX_R = 8.25          # half of 16.5; the skirt, and nothing wider

# crown -- a cup that flares to a straight rim, with V notches taken out of it
CROWN_BODY_PROFILE = [
    (8.25, 0.00),
    (8.25, 0.80),
    (6.90, 1.80),
    (6.90, 2.60),
    (8.10, 4.00),   # flares out at 41 degrees, and is done flaring before
    (8.10, 6.30),   # the notches start, so they cut a vertical wall
]
CROWN_POINTS = 6          # V notches, leaving 6 points
CROWN_CUT_AT = 8.40       # how far out each notch's axis sits: at the top
                          # face it has cut in to r6.10, which still leaves a
                          # 3.15 mm seating ring for whatever stacks on it
CROWN_CUT_Z  = 4.00       # the apex of the V, level with the top of the
                          # flare, so the notches bite exactly where the rim
                          # goes vertical and nothing is removed below it
                          #
                          # The notch is a CONE, apex down, opening upward at
                          # 45 degrees -- so the points taper to a tip rather
                          # than standing square like castle merlons, and the
                          # piece narrows all the way up, which is what makes
                          # it printable without support. At the top face it
                          # has cut in to about r6.4, which still leaves a
                          # 3.4 mm seating ring for whatever stacks on it.

# saucer -- a narrow base, a brim that overhangs it, a shallow dome on top.
# The base is 6.60 where every other piece is 8.25: the brim has to stand
# PROUD of what it sits on or the thing reads as a bell. It still seats on a
# 3.65 mm annulus, which is what the rule actually asks for -- the rule is
# about the width of the CONTACT, not about matching the others.
#
# The dome is shallow and there is no helping it. A saucer wants to taper to
# a point and the top face is what the next piece stands on, so it cannot go
# below about r6 without losing the 3 mm seating ring. 8.25 down to 6.10 is
# the whole budget.
SAUCER_BODY_PROFILE = [
    (6.60, 0.00),
    (6.60, 0.50),
    (5.80, 1.00),
    (5.80, 1.30),
    (8.25, 3.75),   # the underside of the brim, at 45 degrees exactly
    (8.25, 4.05),   # the brim edge, 0.30 thick and 1.65 proud of the base
    (6.60, 4.60),
    (6.10, 6.30),   # the dome, such as there is room for
]

# cog -- a barrel with vertical flutes cut round it
COG_BODY_PROFILE = [
    (8.25, 0.00),
    (8.25, 1.20),   # the skirt stays a whole ring; the flutes start above it
    (7.80, 1.90),
    (7.80, 5.40),
    (8.10, 6.00),
    (8.10, 6.30),
]
COG_FLUTES = 10
COG_CUT_R  = 1.70
COG_CUT_AT = 8.90         # cuts in to r7.20
COG_CUT_Z  = 1.40

# The runner (the shared neutral marker you advance during a turn, before you
# decide to bank) uses the identical pin/socket interface so it still stacks,
# but carries two raised bands and stands taller so it is unmistakable across
# the table.
RUNNER_BODY_H = 8.30
RUNNER_BODY_PROFILE = [
    (8.25, 0.00),
    (8.25, 0.75),
    (7.16, 1.75),
    (8.10, 2.15),   # lower band
    (8.10, 2.90),
    (7.16, 3.30),
    (6.80, 4.15),
    (7.16, 5.00),
    (8.10, 5.40),   # upper band
    (8.10, 6.15),
    (7.16, 6.55),
    (7.38, 7.55),
    (7.38, 8.30),
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
# Board stub — a corner of the real board, for a test print
# --------------------------------------------------------------------------
# The coupon above answers one question (what diameter fits). The stub answers
# the rest of them, and it answers them about the REAL board because it IS the
# real board: the finished mesh intersected with a box, not a small part built
# to look similar. So the slab thickness, the raised lip, the mitre where two
# outline edges meet, the engraved digits, the split posts and the seating
# faces are all exactly what the 285 mm board would print.
#
# The corner chosen is the one columns 2 and 3 sit in: the shortest columns,
# so their summits (and therefore two numbers, one of them single-digit and
# one not) come with the fewest cells attached, and the octagon's top-left
# vertex and both of its neighbouring edges land inside the same small box.
STUB_COLUMNS = (6, 7)     # which columns the stub keeps. 6 and 7 are the
                          # pair worth printing: 6 is even so its posts get
                          # white tops and 7 is odd so its do not, which puts
                          # the column striping on a 48 mm part.
STUB_ROWS    = 2          # how many ROW HEIGHTS down from the top of the
                          # board it reaches, AT LEAST. Not cells: neighbouring
                          # columns have different row pitches and stagger past
                          # each other, so a horizontal cut sees row heights.
                          # The bottom cut then goes on down until it finds a
                          # gap it can sit in with a whole skirt of plate above
                          # it, so this is a floor and not a target.
STUB_PIECES  = 4          # full pieces printed alongside the stub: ONE OF
                          # EACH shape, so the test print checks that every
                          # shape seats and that any of them stacks on any
                          # other. Lower it to 2 for a quicker fit check.

# --------------------------------------------------------------------------
# Printer envelope (Bambu Lab H2D, single nozzle) — see ../available-tools.md
# --------------------------------------------------------------------------
BED_X = 325.0        # single nozzle
BED_Y = 320.0
BED_Z = 325.0

# TWO NOZZLES ON ONE TOOLHEAD, so the second one has to be able to reach
# everywhere the first one does and the usable bed shrinks by 25 mm in X.
# The BOARD is a two-filament part and has to fit inside THIS, not the figure
# above; everything else -- the pieces, the coupon -- is one colour and gets
# the full bed. available-tools.md has had both numbers all along and
# params.py only ever carried the larger one, which is how a 309.7 mm board
# came to be declared a fit.
BED_X_DUAL = 300.0
BED_Y_DUAL = 320.0
