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
#
# 5 AND 9 ARE NOT LEVEL WITH 6, 7 AND 8. They were, and the top of the lens
# read as a flat run of five numbers with 4 and 10 dropping a full 25 mm off
# each end -- a step that looked like a mistake rather than a shape. Half a
# step here splits that 25 into 12.5 and 12.5, so the numbers walk down to
# the corner cut evenly. It also unpins the frame: with 5 and 9 level it was
# the top outer corner of THEIR number box that bound the octagon's diagonal,
# and half a step takes that corner off the cut entirely.
COLUMN_SHORTFALL = [0.0, 0.0, 12.5, 25.0, 50.0, 75.0]

# Extra span given to a column at the BOTTOM only, same indexing. Shortfall
# moves both ends of a column because the grid is centred; this moves one.
#
# It exists because 5 through 9 being level leaves them all the same span with
# 9, 11 and 13 cells in it -- so column 7's dots are packed at 20 mm while
# column 5's are strung out at 30. Columns 6, 7 and 8 carry no title letter,
# so the plate directly below them is empty: dropping their bottoms fills that
# and evens the spacing out, and costs nothing, because what sets the bottom
# of the board is the letters either side of that gap, not the dots.
#
# 5 and 9 carry the same 12.5 here as they do in the shortfall, and the two
# cancel at the bottom: the shortfall lifts that end 12.5 and the drop puts
# it back, so only the TOP of those columns moves. The bottom of the board,
# and the title hanging off it, stay exactly where they were -- and column
# 5's nine dots now sit at 25.4 mm rather than 27.0, which is a step towards
# column 6's 23.0 instead of a step away from it.
COLUMN_DROP = [19.0, 14.0, 12.5, 0.0, 0.0, 0.0]

PITCH_X = 22.0      # centre-to-centre spacing between columns
PITCH_Y = 18.0      # row pitch of the LONGEST column. Shorter columns get a
                    # pitch of their own, set by COLUMN_SHORTFALL above.
                    #
                    # Both pitches follow the piece diameter, and the piece
                    # diameter follows the board: 13 cells at this pitch is
                    # what sets the height of the lens, and a square frame
                    # has to be that wide as well as that tall.

# --------------------------------------------------------------------------
# The board: a 6 mm solid octagonal slab
# --------------------------------------------------------------------------
# There was a second board once -- an open wireframe truss of struts and
# rings, with a round pad at every cell and an octagonal frame round the
# outside. It is gone. It was abandoned in favour of the slab a long time ago
# and then maintained anyway: every parameter, every branch and twenty of the
# checks went on being carried, and the only thing that ever came of it was a
# failing check about a pad no printed board has.
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
# The PLATE is what a piece sits on -- the whole top face of the slab, so the
# seat is unobstructed from the post out past the piece's skirt wherever a
# piece lands. There is no pad: the wireframe board had one at every cell and
# the wireframe board is gone.
PAD_OD    = 13.8    # the footprint a cell RESERVES. Nothing is built to this
                    # any more; it is what content_points() hands the octagon
                    # so the frame is sized against the cells and not against
                    # bare post diameters.
POST_D    = 5.90    # nominal 6.0 less 0.10 for FDM swell
POST_H    = 3.20    # how far the post stands proud of the plate
POST_CHAMFER = 0.60 # 45 deg lead-in at the top, so a piece self-centres
CELL_SEGS = 48      # facets around a post (export quality)

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
# The octagonal frame
# --------------------------------------------------------------------------
# A true octagon: a rectangle around everything with its four corners cut at
# 45 degrees. The cell field is a lens and does not reach the corners, so the
# cut-off triangles are where the number boxes live.
OCTAGON_MARGIN  = 6.0    # clear air between the content and the frame
# A REGULAR octagon -- all eight edges the same length -- needs a square
# bounding box (so the half-span is taken as the larger of the two) and a
# chamfer of exactly 2/(2+sqrt2) = 0.5858 of it, at which point the four flats
# and the four corner cuts come out identical.
#
# TRUE: all eight edges the same length, on a board 285.0 mm across.
#
# A regular octagon is SQUARE by definition and the dual-nozzle bed is not --
# 300 x 320 -- so the board's WIDTH is the binding dimension and the whole
# design has to fit inside it. That was measured rather than guessed. With
# the 16.5 mm pieces a square board could not get under 291 mm even after
# giving up the title, the level 6/7/8 spacing and every millimetre of
# clearance between pieces. What buys it back is the piece diameter: at
# 14.5 mm the column pitch comes down to 22.0 and the row pitch to 18.0, and
# 285 mm then holds the title, the level spacing AND 5.07 mm between
# neighbouring pieces.
OCTAGON_REGULAR = True
OCTAGON_ACROSS  = 285.0   # pin the octagon to exactly this across the flats
                          # rather than sizing it to its content. 0 sizes it
                          # to the content, as it used to. Whatever is left
                          # over becomes the margin the lip lives in, so
                          # test_fit.py checks it still clears RIM_W +
                          # RIM_CLEAR rather than trusting the number.

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
NUMERAL_MAX_W  = 22.0   # widest a number may be. A two-digit number is 26 mm
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
NUMERAL_BOX_W  = 24.0   # footprint a number reserves on the plate: the widest
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
TITLE_GAP   = 19.30  # from the bottom cell's centre to the letter's centre.
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

PEG_SOCKET_D     = 6.24   # Holes print undersize, so the socket is cut over
                          # the 5.90 post it has to swallow. This is the one
                          # number in the project that only a print can
                          # settle, and it is on its THIRD value -- both of
                          # the others were printed and judged by hand:
                          #
                          #   6.35   0.45 diametral   printed, too loose
                          #   6.13   0.23 diametral   printed, a little tight
                          #   6.24   0.34 diametral   <- exactly between them
                          #
                          # The halving overshot. 0.34 is the midpoint of a
                          # bracket with a print at each end, which is as good
                          # as this number gets without a third data point.
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
                          # absorb -- and in the hand it was already short of
                          # that, so the next move was upward, not down.
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

# 17.5 mm across. The width buys two things -- something to actually grip,
# and a wide skirt, which is what lets the post be short: the skirt does the
# work of keeping a piece upright, so the post only has to locate it.
PEG_BODY_PROFILE = [
    (8.75, 0.00),
    (8.75, 0.75),
    (7.59, 2.20),
    (7.13, 3.60),
    (7.59, 5.10),
    (7.83, 5.85),
    (7.83, 6.30),
]
PEG_SEGS = 64

# --------------------------------------------------------------------------
# The seat: what a piece stands on, and what stands on it
# --------------------------------------------------------------------------
# Two faces have to agree for a stack to sit straight: the BOTTOM of the piece
# going on, and the TOP of the piece underneath. This is the contract between
# them, and it is written once here rather than being a property each
# silhouette happens to have.
#
# The seat is the annulus from the socket mouth out to SEAT_BAND_R, and the
# contract is DELIBERATELY ASYMMETRIC, because the two faces are not doing
# the same job:
#
#   SEAT_BAND_R     how far out the agreement reaches.
#   SEAT_BOTTOM_R   every piece's bottom is CONTINUOUS from the socket mouth
#                   to here -- a whole flat annulus, no gaps, no exceptions.
#                   Which means a top may put its support wherever it likes
#                   inside the band and be certain of landing on something,
#                   at every rotation, with no case to reason about.
#   SEAT_MIN_FRAC   the top then only has to carry ENOUGH: this fraction of
#                   the band, and at least that much again in every one of
#                   SEAT_SECTORS sectors, so nothing is held up on one side.
#   SEAT_MIN_ARM    and it has to carry it OUT THERE. Area alone would let a
#                   piece be balanced on a pip round the post; what stops a
#                   stack leaning is the moment arm, so the area-weighted
#                   mean radius of the support has a floor of its own.
#   BOTTOM_FLAT_H   the bottom is flat: one plane at z = 0 with vertical
#                   walls above it for this height. No knife edges, no taper
#                   running out to nothing, and a first layer that is the
#                   face the piece will stand on for the rest of its life.
#
# This replaced a symmetric rule -- 42% on BOTH faces and a continuous core
# ring on both -- which sounded stricter and was not. It forced every piece
# to keep a wide flat table at full height in the middle, and that table is
# exactly what stopped the crown reading as a crown: points cannot look tall
# next to a disc of their own height. Six pads out at r7 hold a piece far
# more steadily than a narrow ring at r4 does anyway, which the arm floor
# below is there to say out loud.
SEAT_BAND_R   = 7.40
SEAT_BOTTOM_R = 7.40
SEAT_MIN_FRAC = 0.18
SEAT_MIN_ARM  = 4.80
SEAT_SECTORS  = 6
BOTTOM_FLAT_H = 0.40

# How much air is left between two pieces in neighbouring cells. It was 3.0,
# which is what held the pieces to 16.5 mm; the tightest spacing on the board
# is column 7's 19.58 mm and 3.0 of that is a fifth of the piece. The printed
# board says there is more room than that rule believed, so it comes down to
# 2.0 -- still a fingernail's width, and it is what buys 17.5 mm pieces.
PIECE_GAP_MIN = 2.0

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
#     to a point. It has to meet the seat contract above: enough area, far
#     enough out, present in every sector.
#   - nothing may exceed PEG_MAX_R, or pieces touch in adjacent cells.
#   - printed flat with no supports, so no surface may overhang more than 45
#     degrees: a profile may widen going up by at most one millimetre of
#     radius per millimetre of height.
#
# ONE ENVELOPE, EVERY PIECE. Those rules are not "the four player shapes plus
# whatever the runner does". Every piece on this board is 2 * PEG_MAX_R across
# and PEG_BODY_H + PEG_POST_H tall, without exception, and test_fit.py
# measures all five against the same numbers rather than the markers against
# each other. The runner spent a while wider and taller than a marker and it
# was not a decision -- it simply kept the old size through a resize that took
# the markers down, and no check was looking. What tells a runner apart is its
# silhouette and its colour, which is a job the bands do without costing it a
# millimetre of clearance on the board's tightest row.
#
# Anything added on top of the lathe is cut, never added: a vertical cylinder
# taken out of the side leaves a scallop, and scallops are self-supporting
# whatever their depth.
PLAYER_STYLES = ["counter", "crown", "saucer", "cog"]
PLAYER_LABELS = ["A", "B", "C", "D"]   # what the printable sets are called

# THE PIECE NUMBERS. Every piece has one, and it is its position in this list:
#
#   1  counter   player A      2  crown   player B      3  saucer  player C
#   4  cog       player D      5  runner  shared, neutral
#   6  active    one per player: whose turn it is
#
# They exist so a piece can be named in one character in conversation, a
# render, a print note or a commit message, without "the round one" having to
# do the work. The order is the order the shapes were designed in and it is
# FIXED: a number, once given out, stays with its shape. A new shape takes the
# next free number; a retired one leaves a hole rather than letting everything
# below it shuffle up and silently rename four pieces that are already printed
# and sitting on somebody's table. 6 is the first number this rule has had to
# hand out, and it went on the end exactly as promised.
#
# renders/09-piece-catalogue.png is this list, drawn.
PIECE_STYLES = PLAYER_STYLES + ["runner", "active"]

# ...but 1 to 5 STACK and 6 does not, and most of the rules in here are about
# stacking. A piece with no post on top is the end of a stack by construction:
# nothing lands on it, so it owes nothing to a seat above, and the height that
# makes stack pitch exact is a number it has no use for. What it still owes is
# everything on the way IN -- the same socket, the same flat whole bottom, the
# same 17.5 mm footprint, because it sits in a cell like anything else.
#
# So the envelope rules run over STACKING_STYLES and the interface rules run
# over all of PIECE_STYLES, and test_fit.py is careful about which is which.
STACKING_STYLES = PIECE_STYLES[:5]
TERMINAL_STYLES = PIECE_STYLES[5:]
PEG_MAX_R = 8.75          # half of 17.5; the skirt, and nothing wider.
                          #
                          # 20 mm was asked for and 20 mm does not exist. The
                          # tightest spacing on the board is column 7, whose
                          # cells are 19.58 mm apart centre to centre, so two
                          # 20 mm pieces in adjacent cells of that column
                          # would INTERSECT by 0.42 mm. Buying it would mean
                          # 22 mm of row pitch there, which is 29 mm more lens
                          # than the board has, and a ~304 mm octagon against
                          # a 300 mm dual-nozzle bed.
                          #
                          # 17.5 is what the 19.58 allows with 2.08 mm left
                          # between two pieces, and 4.5 mm along a row. It is
                          # the board that sets this number now, not the bed:
                          # the cells have not moved, the pieces have grown
                          # into the space that was already there.

# crown -- a BAND at the bottom, and six tapered points standing on it.
#
# Four goes at this. A disc with shallow V notches nicked out of the edge,
# which read as a gear. Square merlons round an open trough, which read as a
# castle turret. Cones cut into a thick rim, which read as dimples drilled
# into a bowl -- a cut can make a hole in a wall but it cannot make the wall
# into six separate things standing up.
#
# So the points are ADDED, like the saucer's legs and for the same reason.
# What the lathe makes is a shallow cup: a band, a low wall, a floor, and the
# column the socket needs up the middle. Six tapered spikes are then stood on
# that floor, and they are the only thing at full height out at the rim.
#
# The three things a crown silhouette has, which the first three attempts all
# missed at least one of:
#
#   a solid band across the bottom, wider than what stands on it
#   points that TAPER as they rise
#   an EMPTY middle -- nothing between the points at their own height
#
# The third is what the old seat rule made impossible: it wanted a
# continuous ring of support up at 6.30, which is a table, and points cannot
# look tall standing next to a table of their own height. The rule is
# asymmetric now (see SEAT_*) and the middle of this piece is a column barely
# wider than the post coming out of it.
#
# The spikes still have FLAT TOPS dead level at PEG_BODY_H, because the next
# piece stands on them, and on nothing else: six pads at r6.2 carry it with a
# far better moment arm than the old table ever had.
CROWN_BODY_PROFILE = [
    (8.75, 0.00),
    (8.75, 1.20),   # the band: full, plain, and the widest part of the piece
    (8.20, 1.55),   # stepped in 0.55 -- the line under the band that most of
    (8.20, 3.00),   # the drawn ones have.
    (4.60, 3.00),   # THE FLOOR. It sat at 1.95, which made the middle of the
                    # crown a well nearly two thirds of the piece deep -- and
                    # from anywhere but straight overhead what you saw was
                    # the inside of a bowl with some points behind it. At
                    # 3.00 it is a shallow tray: the eye reads a band with
                    # points standing out of it, which is the thing. It also
                    # buries the bottom third of each point's foot, so the
                    # points look like they grow out of the rim instead of
                    # being parked on it.
    (4.60, 4.00),   # the column: 1.48 mm of wall round the socket
    (3.40, 5.20),   # tapering once it is past the socket roof, so what shows
    (3.40, 6.30),   # in the middle is barely wider than the post itself
]
CROWN_POINTS   = 6
CROWN_SPIKE_AT = 6.55     # centre radius of each point

# A POINT IS A BLADE, NOT A BOLLARD. The lathe makes a spike with a circular
# section -- as wide through the wall as it is along the rim -- and six of
# those round the rim read as a ring of little posts, whatever their profile
# does. A drawn crown's points are flat: wide along the band, thin through
# it, and standing right out at the edge.
#
# So the section is squashed after it is turned: radially by the first of
# these, tangentially by the second. Four facets rather than sixty-four, so
# it is a pyramid on a pyramid and not a cone on a cone -- crisper, closer to
# the drawn ones, and a flat facet is the easiest thing a printer ever laid.
CROWN_SPIKE_SEGS   = 4
CROWN_SPIKE_SQUASH = (0.62, 1.72)   # (through the wall, along the rim)
                                    #
                                    # 1.34 left 1.06 mm of air between one
                                    # point's foot and the next, which is a
                                    # gap you can see and a neck you can
                                    # snap. At 1.72, with a straight foot at
                                    # r2.20, the feet are 7.57 mm across on a
                                    # 6.55 mm spacing -- they overlap by a
                                    # millimetre and weld into one scalloped
                                    # rim, the way drawn crowns have their
                                    # points rising out of a band rather than
                                    # standing on it. The knobs still clear
                                    # each other by 1.8 mm, so the gaps are
                                    # up where they read.

# A POINT IS A CONE ON A CONE. It narrows to a waist and then flares back out
# to a knob, which is the shape a crown point has in half the drawn ones --
# and, more to the point here, it is something to PICK UP BY. A plain taper
# gives a finger nothing: pinch it and it slides. A waist with a knob over it
# lets a nail get under the knob, and six of them round the rim means one is
# always where your fingers are.
#
# (r, z) up the outside of one point; the lathe closes it across the top and
# the bottom. The flare out of the waist is 20 degrees from vertical, well
# inside the 45 the printer will carry, and the knob's top is FLAT at
# PEG_BODY_H because the next piece stands on it.
CROWN_SPIKE_PROFILE = [
    (2.20, 1.75),   # THE FOOT, buried in the floor so there is no seam...
    (2.20, 3.40),   # ...and STRAIGHT for the first 1.65 mm of it, which is
                    # the only reason the points touch where you can see it.
                    #
                    # The foot was a cone from r2.35 straight to the waist,
                    # and measured at its widest it overlapped its neighbours
                    # by 1.53 mm -- every millimetre of which was under the
                    # floor. A cone is narrowing the whole way up, so by the
                    # time it came out at z3.00 it was down to r1.76, which
                    # is 6.04 mm along the rim on a 6.55 spacing: half a
                    # millimetre APART. The overlap was real and invisible,
                    # which is the worst kind.
                    #
                    # What matters is the width where the foot LEAVES THE
                    # FLOOR, so the foot holds its radius until 0.40 mm above
                    # it. At r2.20 that is 7.57 mm along the rim -- a full
                    # millimetre of overlap on each side, out in the open,
                    # and the six feet are one scalloped rim that six blades
                    # rise out of. Reach is 7.91, inside the band's own 8.20,
                    # so nothing pokes out past the edge of the piece.
    (0.95, 4.70),   # the waist: the thing you grip, and it moved UP 1.10 mm.
                    # That is the "taller" half of the job -- the foot is the
                    # pyramid you see, and it now rises 1.70 mm clear of the
                    # raised floor instead of being a stub. The waist widened
                    # with the foot (0.78 -> 0.95) because a blade this wide
                    # necking to 1.56 mm read as a pinch rather than a shape.
    (1.59, 5.85),   # out to the knob. THIS RISE IS NOT FREE: the squash
                    # multiplies the flare, so the limit is dr/dz <= 1/1.72,
                    # and raising the waist shortened the rise to 1.15 mm.
                    # At 1.61 the flare came out at 44.6 degrees -- inside
                    # the 45 and passing, and far too close to it to want to
                    # print. 1.59 puts it back to 43.7. There is no more
                    # room here: widen the foot again and the waist has to
                    # come back down to pay for it.
    (1.56, 6.30),   # the flat top. Squashed, six of them is 31 mm2, a
                    # quarter of the band and half again over the 18% asked.
                    #
                    # That is tight on purpose and it is the crown that made
                    # it tight: a blade is thin through the wall, so it puts
                    # a third less area up there than a round spike did. What
                    # it buys back is REACH -- r6.60, the longest arm of any
                    # piece -- which is what actually stops a stack leaning.
                    # SEAT_BAND_R went 7.30 -> 7.40 to meet it, which costs
                    # nothing: every bottom is whole out to the cog's 7.45
                    # root anyway, and that is the number that caps it.
]

# saucer -- a flying one. A landing pad on the ground, four struts holding the
# hull up off it, a hull whose underside sweeps out to a thin brim at the full
# radius, a domed top curving back in to the post, and six raised lugs round
# the dome for the next piece to stand on.
#
# The old one was a bell with a lip. Three things make this one read as a
# saucer instead: the brim is at the WIDEST point of the piece with air above
# and below it, the underside sweeping up to it is curved rather than a
# straight cone, and the hull is lifted clear of the ground on legs.
#
# The height budget is the whole difficulty. The body is 6.30 mm and a brim
# can only flare at 45 degrees or the printer has nothing to lay it on, so
# every millimetre the brim stands out costs a millimetre of height, and the
# legs and the dome want that height too. What follows is that budget spent:
# 0.95 on legs, 2.35 sweeping out to the brim, 0.40 of brim edge, 2.60 of
# dome. There is no slack in it anywhere.
SAUCER_BODY_PROFILE = None   # built as a curve; see board.py:_saucer_profile
SAUCER_BASE_R     = 7.80     # a WHOLE base, not a windowed one: the bottom
SAUCER_BASE_H     = 0.40     # face is a plain disc, 70% of the seat annulus,
                             # and the landing gear stands on top of it
SAUCER_WAIST_R    = 5.90     # the hull column the legs stand beside
SAUCER_WAIST_Z    = 1.50
SAUCER_BRIM_Z     = 4.45     # the swept underside meets the brim edge here
SAUCER_BRIM_T     = 0.25     # and the edge is this thick
SAUCER_SHELF_R    = 7.70     # the brim's top is a flat shelf in to here, so
SAUCER_SHELF_DZ   = 0.10     # the brim reads as a disc and not as the start
                             # of the dome
SAUCER_DOME_R     = 5.60     # where the dome flattens into its collar
SAUCER_UNDER_BULGE = 0.03    # how much the underside curves. The straight
SAUCER_DOME_BULGE  = 0.70    # line from waist to brim is already at 44
                             # degrees, so there is almost nothing left to
                             # spend on curvature down there; the dome above
                             # goes up and IN and can curve as it likes.

# LANDING GEAR. Four square tubes standing on the base, beside the hull
# column, reaching up into the underside. Square because a square tube is
# four vertical walls and prints without a thought, and because that is what
# the reference actually looks like. They are ADDED, not cut: everything
# about them is vertical or welded into something above, so nothing
# overhangs and nothing bridges.
SAUCER_LEGS       = 4
SAUCER_LEG_AT     = 6.80     # centre radius: outside the column, flush with
SAUCER_LEG_R      = 0.85     # the rim of the base. Half-diagonal, so the
                             # tube is 1.41 mm square.
SAUCER_LEG_Z1     = 2.60     # runs up past the hull's underside and welds in

# The six pads the next piece stands on: RECTANGLES lying on the dome, not a
# ring with bites taken out of it. A bar is what it looks like it is -- a
# landing pad -- and it puts its area where the seat contract wants it,
# out beyond the collar rather than smeared across the whole dome.
SAUCER_PADS       = 6
SAUCER_PAD_R0     = 5.40     # bar runs from here to here, radially
SAUCER_PAD_R1     = 7.60
SAUCER_PAD_W      = 3.00
SAUCER_PAD_Z      = 5.00     # rises from inside the dome to a flat top dead
                             # level at PEG_BODY_H

# cog -- a gear: a straight cylinder with square slots milled out of its rim.
#
# It was a barrel with ten ROUND flutes cut into it, and round flutes leave
# teeth with hollow flanks, which reads as a fluted column and not as a gear.
# It also flared at both ends -- the body went 8.75, in to 8.27, back out to
# 8.63 -- so every tooth had a lip top and bottom and none of them stood
# straight.
#
# Both are gone. The body is one straight cylinder, top to bottom, no taper
# and no flare anywhere, and the gaps are cut with straight radial BARS
# rather than cylinders. A bar leaves what a milling cutter leaves: flat
# flanks, a flat root, an arc tip, and square ends at the top and the bottom.
# Ten of them and the thing is a spur gear.
#
# Cutting the gaps rather than adding the teeth is right here, where it was
# wrong for the crown and the saucer: a gear tooth is not a thing standing on
# a surface, it is what is LEFT of the rim once the gaps are taken out, and
# cutting it that way keeps the tips on the piece's own 8.75 circle instead
# of poking past it at the corners.
COG_BODY_PROFILE = [
    (8.75, 0.00),
    (8.75, 6.30),
]
COG_TEETH  = 10
COG_ROOT_R = 7.45    # how deep the slots go: 1.30 mm of tooth, which is a
                     # sixth of the radius and chunkier than a real gear of
                     # this tooth count. It cannot go deeper -- the root has
                     # to stay outside SEAT_BOTTOM_R or the bottom face stops
                     # being the whole annulus the seat contract promises.
COG_SLOT_W = 2.60    # 18.7 degrees of gap at the tip against 17.3 of tooth,
                     # so the two read as the same size

# active -- THE ACTIVE PLAYER'S PIECE, and the only one that does not stack.
#
# It marks whose turn it is, so it wants to be seen across the table and it
# wants to be unmistakable from the markers. Everything else on this board is
# round, squat and solid; this is SQUARE, tall, and open.
#
# No post on top. Nothing lands on it -- it is the end of a stack by
# construction -- so it owes nothing to a seat above it and it is free of the
# 8.45 mm height that makes stack pitch exact. It keeps everything on the way
# IN: the same socket, the same whole flat bottom, the same 17.5 mm footprint.
#
# SQUARE IS SAFE, and it is worth saying why rather than hoping. Columns are
# 22.0 mm apart and the tightest row pitch is 19.58, so two cells are never
# closer than 19.58 in Y or 22.0 in X -- and an axis-aligned 17.5 mm square
# clears both. What a square DOES reach further into is the corner: 12.37 mm
# from the cell centre against a circle's 8.75, which is why test_fit.py puts
# the footprint on all 83 cells and checks the corners stay off the lip.
# NO FLANGE. The first square version had a full-width 17.5 x 1.6 plate with
# a block sitting on it, and the plate read as a washer somebody had left
# under the piece. It is one tapered plinth now, drawing in as it rises.
#
# It stays 17.5 at the bed, which keeps every piece in the set the same width
# -- the one envelope rule this piece does still owe, since it has to sit in
# a cell like anything else. What it lost is the FLANGE, not the footprint.
#
# There is a hard floor under this as well, and it is worth knowing where.
# The seat contract says every bottom is a WHOLE flat annulus out to
# SEAT_BOTTOM_R, which is what lets a gappy top -- the crown's six blades,
# the saucer's six pads -- be certain of landing on something at any
# rotation. A square of side s covers that circle when s >= 2 *
# SEAT_BOTTOM_R, which is 14.8. So this could come down to 15 if it ever
# wanted to; below that it stops being able to sit on a crown at all.
# THE SILHOUETTE COMES FROM THE SKETCH, and it took a review to notice it
# had drifted off it. The sketch is a section: a foot that FLARES from the
# full width of a cell up into a slim shaft over about a sixth of the height,
# a long parallel shaft, and a FLAT TOP. What had been built instead was a
# 24%-tall plinth barely narrower at the top than the bottom, a shaft at 72%
# of the base width, and a solid pyramid cap eating the top quarter.
#
# The fat shaft was the root of it, and it came from one assumption nobody
# checked: that a row of the surface pattern needed three cells across, which
# needs a face of at least 12.4 mm. It does not. The print this piece is
# modelled on has narrow limbs carrying two cells, and a narrow face carries
# them at a BETTER ratio of hole to rib than a wide one does.
ACTIVE_BASE    = 17.50    # at the bed: the DIAMETER of a round foot, the
                          # same 17.50 across as
                          # every other piece, because it still has to sit in
                          # one. There is a hard floor at 2 * SEAT_BOTTOM_R =
                          # 14.8, below which it cannot cover a crown's top.
ACTIVE_FOOT_H  = 4.60     # the flare, 18% of the height. Its outside runs in
                          # at 43 degrees from vertical -- and that is a face
                          # sloping INWARD as it rises, which is not an
                          # overhang at all, so the 45 rule is not what caps
                          # it. What caps it is the socket underneath.
ACTIVE_SHAFT   = 9.00     # the shaft, parallel all the way up. 51% of the
                          # base against the sketch's 46%, and the 5% is
                          # bought by the socket: the bore is 6.24 across, so
                          # at 9.00 the wall beside it is 1.38 mm and at 8.00
                          # it would be 0.88 -- one hair over two perimeters,
                          # on the one part of this piece that takes a load.
ACTIVE_TOP_Z   = 23.95    # where the SHAFT stops. The octagon cap sits on
                          # top of it and the piece finishes at 28.40, which
                          # is where it finished before the cap existed --
                          # the height the cap costs was taken back off the
                          # shaft rather than added to the piece.
                          #
                          # THE HEIGHT IS AN OUTPUT, NOT A CHOICE. Two webs
                          # and a rib between them need 17.15 mm of hollow
                          # shaft; the hollow cannot start until the socket's
                          # roof has closed at z7.92, and it has to end
                          # 3.30 mm below the top so its own roof can be a
                          # pyramid rather than a bridge. 7.92 + 17.15 + 3.30
                          # is 28.37, and this is that rounded up.
                          #
                          # It is 3.4 times a marker's 8.45 and it is meant
                          # to be: this is the piece that says whose turn it
                          # is, from across a table.
ACTIVE_BASE_R  = 1.20     # corner radius, so it is square and not sharp

# THE SHAFT IS HOLLOW, and that is what makes four webs possible at once.
#
# Every version until now cut its pattern straight THROUGH the shaft, front
# to back. That works for two faces and cannot work for four: a cut opening
# the left and right faces at the same height as one opening the front and
# back would cross it in the middle and take the shaft apart. The old piece
# dodged it by alternating -- one row on the front and back, the next on the
# left and right -- which means every face is blank at every other row, and
# the web could never be continuous on any one of them.
#
# A hollow shaft has no such problem. Each web is cut through ONE WALL, 1.20
# mm deep, so the four of them never meet. What is left is a square tube with
# a spider web in each of its four walls and four continuous corner posts
# holding it up, and you see in through the near web and out through the far
# one. That is the wireframe.
ACTIVE_WALL    = 1.20     # about three perimeters. The webs are cut through
                          # this and nothing deeper, so it is also how proud
                          # the web reads.
# The hollow used to be closed by a 45-degree pyramid to avoid bridging, at
# the cost of a solid band at the top a third the height of the shaft. The
# drawing has the web running all the way to the top plate, so the pyramid is
# gone and the plate bridges the core instead. See ACTIVE_TOP_T.

# THE WEB IS A COBWEB: an irregular net of thin lines, edge to edge, with
# nothing behind it. It is drawn by scattering seed points over the face,
# taking their Voronoi diagram, and cutting every cell out -- so what is left
# is the EDGES of that diagram, which is a web. Nothing is ever drawn as a
# line; the lines are what the cuts leave between them.
#
# THE RIB IS ONE EXTRUSION WIDE, NOT TWO, AND THAT IS A DELIBERATE BREAK
# WITH THE REST OF THE PROJECT. Everywhere else 0.85 is the floor, because
# everywhere else the thin thing is a WALL: something that has to hold a
# shape, take a load, or look solid, and a wall one extrusion wide is a
# defect. A web is not a wall. Its ribs are struts, laid as a single
# extrusion path -- exactly what a slicer lays for infill, and what the
# reference print in reference/ is made of.
#
# The arithmetic says there is no choice about it. A net of line w and cell d
# is (d/(d+w))^2 open. The drawing in reference/active-web-wanted.png is 73%
# open with lines 3% of the shaft's width. To reach 73% at w=0.85 you need
# 5 mm cells, which is one and a half of them across a 9 mm face. At w=0.45
# you need 2.5 mm cells, which is three and a half. Two perimeters cannot
# make a web at this size; they can only make a wall with holes in it, which
# is what the last three versions were.
ACTIVE_RIB     = 0.45     # one 0.42 line plus a hair, so the slicer lays a
                          # single bead and does not try to fit two.
ACTIVE_WEB_CELL = 2.50    # the target size of one opening. With a 0.45 rib
                          # this is 73% open, which is the drawing.
ACTIVE_WEB_FRAME = 0.90   # the border left round each face's web. Two ribs,
                          # not one: it ties the web into the corner posts
                          # and it is the only part of a wall that is not
                          # web, so it is what stops the tube unzipping.
ACTIVE_WEB_RELAX = 2      # rounds of Lloyd relaxation on the seed points.
                          # None at all leaves slivers -- cells so thin the
                          # rib eats them and the web grows bald patches.
                          # Too many and it converges on a honeycomb, which
                          # is the thing this is not. Two is organic and
                          # even at the same time.
ACTIVE_WEB_SEED = 20260929
                          # the RNG seed. The web is random but it is not
                          # arbitrary: this is fixed so the same STL comes
                          # out of the same commit, and so a print that went
                          # wrong can be looked at again.
ACTIVE_TOP_T   = 1.20     # the plate that closes the hollow. It bridges the
                          # core -- see direction.md; this is the one bridge
                          # left in the piece, anchored on all four walls.

# THE CAP IS AN OCTAGON, like the board it is played on, and it is turned so
# its FLAT SIDES RUN PARALLEL TO THE SHAFT'S. That orientation is the whole
# reason it is as big as it is.
#
# The cap has to cover the square shaft or the top stops being an octagon,
# and a square of half width 4.50 has its corners 6.364 out. Which part of
# the octagon has to reach that far depends entirely on how it is turned:
#
#   vertex at 45 (what this was)   the CIRCUMRADIUS reaches the corner,
#                                  so R >= 6.364 and the cap is 12.8 across
#   flat at 45 (what this is)      the INRADIUS reaches it, and the inradius
#                                  is only 0.924 of R, so R >= 6.89 and the
#                                  cap is 14.3 across
#
# Turning it to line the flats up therefore costs 1.5 mm of width and 0.2 mm
# of flare height, and it is worth it: the cap's sides now sit square to the
# shaft's instead of cutting across them at 22.5 degrees.
ACTIVE_CAP_R   = 7.15     # circumradius. The number that matters is the
                          # INRADIUS it implies, 6.606, which clears the
                          # shaft's corners by 0.24 mm. 6.90 would clear them
                          # by 0.011 -- passing, and no place for a number to
                          # sit, since any later nudge to ACTIVE_SHAFT would
                          # put the corners outside the cap.
ACTIVE_CAP_RISE = 2.45    # how far the cap flares out over. The flare is the
                          # CONVEX HULL of the shaft's square top and the
                          # cap's octagon, which is the one construction that
                          # gets this right: both outlines are convex, so
                          # their hull is exactly the solid between them.
                          #
                          # WHICH FACE IS STEEPEST MOVES WITH THE ORIENTATION,
                          # so board.active_cap_overhang() measures the mesh
                          # rather than working it out from these numbers.
                          # Here it is the square-on one -- a face of the
                          # shaft to the octagon flat parallel to it, 2.106
                          # out over 2.45 up, which is 40.7 degrees.
                          #
                          # Sizing it by the longest RADIAL run instead says
                          # 2.279, out at 22.5 degrees to a vertex, and that
                          # is simply the wrong measurement: a face's slope
                          # is its run PERPENDICULAR to itself, and the
                          # diagonal run is spread across a triangle that
                          # leans less than the square-on face does. The
                          # radial figure is conservative here, but it is not
                          # conservative by design, and there is no reason to
                          # think it errs the same way for another shape.
ACTIVE_CAP_T   = 1.20     # the flat octagonal top itself

# TWO MATERIALS, AND THE SPLIT IS A PLANE. The cap is RED and everything
# below it is WHITE, and the boundary is z = ACTIVE_TOP_Z -- one flat cut
# right across the piece, so the slicer changes filament once on the way up
# and never goes back. That is the cheapest two-colour print there is: no
# interleaving, no purge tower to speak of, no chance of a seam wandering.
#
# The lip is the exception and it is deliberate. It is WHITE, and it sits on
# top of the RED cap, so the print goes white, red, white -- the same trick
# the board plays with its own lip, where the top RIM_CAP_H prints in the
# numbers' colour rather than the body's. It means the body part has two
# separate solids in it, the tower and a ring floating above it, exactly as
# board-numerals.stl has sixty.
ACTIVE_LIP_W   = 1.20     # how far in from the cap's edge the lip runs
ACTIVE_LIP_H   = 0.80     # four layers at 0.20, and it stands this proud of
                          # the red. The height it costs came off the shaft
                          # rather than the piece, which still ends at 28.40.

ACTIVES = 4               # one per player

# The runner (the shared neutral marker you advance during a turn, before you
# decide to bank) uses the identical pin/socket interface so it still stacks,
# and now the identical envelope as well: it is a marker's size to the micron.
# What makes it unmistakable is the shape -- three square-edged tiers cut by
# two deep grooves, against the markers' smooth waisted bodies -- and the
# neutral colour, not bulk.
#
# It used to stand 16.5 x 10.45 against a marker's 14.5 x 8.45, and the bands
# flared at 67 degrees from vertical, which is an overhang the machine would
# have had to bridge or droop through. No check caught either, because every
# piece rule was written over PLAYER_STYLES and the runner is not one. Both
# are fixed here: the flares are 43.5 degrees, and the checks now run over all
# five pieces.
RUNNER_BODY_H = PEG_BODY_H    # the rule, in the one place it could be broken
RUNNER_BODY_PROFILE = [
    (8.75, 0.00),
    (8.75, 0.75),   # tier 1 is the skirt
    (7.60, 1.40),   # groove, 1.15 deep
    (7.60, 1.75),
    (8.75, 2.95),   # tier 2, flaring at 44 degrees so it self-supports
    (8.75, 3.45),
    (7.60, 4.05),   # groove
    (7.60, 4.35),
    (8.75, 5.55),   # tier 3, the same flare
    (8.75, 5.95),
    (7.79, 6.30),   # in to the top face
]

# --------------------------------------------------------------------------
# Piece counts
# --------------------------------------------------------------------------
PLAYERS            = 4
MARKERS_PER_PLAYER = 11   # one per column
RUNNERS            = 3    # shared, neutral colour

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
# The stub always takes the TOP of whichever columns it keeps, because that is
# where the numbers are and where the lip comes closest to a pad.
#
# It is on COLUMN 7 ALONE now. The 6/7 pair was cut to put the white/red post
# striping on one part; that has been printed and it works. What is being
# settled this time is only the socket fit, so the part wants to be as small
# and as quick as it can be while still standing a piece on a real board post
# under a real lip. One column does that in a 22 mm wide strip.
STUB_COLUMNS = (7,)       # which columns the stub keeps. 7 is the middle
                          # column: the tightest row pitch on the board, an
                          # odd column so its posts are plain red, and a
                          # single-digit number under the top post.
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
STUB_ACTIVE  = True       # and one active-player piece: it is the only other
                          # thing on the board with this socket, and the one
                          # whose weight is furthest from the joint
STUB_RUNNER  = True       # add one neutral runner to that plate. It carries
                          # the same socket as a marker, so a fit judged on
                          # the markers alone would be assumed rather than
                          # checked on the one piece that gets pushed on and
                          # pulled off most in a game.

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
