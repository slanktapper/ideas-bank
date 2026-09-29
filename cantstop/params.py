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
    (8.20, 1.95),   # the drawn ones have. Kept low: a tall cup wall competes
    (4.60, 1.95),   # with the points, and the points are the crown.
    (4.60, 3.60),   # the column: 1.48 mm of wall round the socket
    (3.40, 5.00),   # tapering once it is past the socket roof, so what shows
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
CROWN_SPIKE_SQUASH = (0.62, 1.34)   # (through the wall, along the rim)

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
    (2.05, 1.75),   # the foot, buried in the cup floor so there is no seam
    (0.78, 3.95),   # the waist: 1.56 mm across, and the thing you grip
    (1.60, 5.40),   # out to the knob
    (1.55, 6.30),   # the flat top. Squashed, each is a 1.92 x 4.15 mm
                    # diamond and six of them is 24.0 mm2, a
                    # whisker over the 18% asked for.
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

# active -- THE ACTIVE PLAYER'S PIECE, and the first one that does not stack.
#
# It marks whose turn it is, so it wants to be seen across the table and it
# wants to be unmistakable from the markers: tall where they are squat, and
# open where they are solid. One per player, in their colour.
#
# No post on top. Nothing lands on it -- it is the end of a stack by
# construction -- so it owes nothing to a seat above it and it is free of the
# 8.45 mm height that makes stack pitch exact. It keeps everything on the way
# IN: the same socket, the same whole flat bottom, the same 17.5 mm footprint.
#
# Shape: a flared foot, a slender shaft, and a head of three tiers of spikes
# that shrink and rotate as they climb, with a finial on the axis. The tiers
# are the same shape at 0.70 the size each time, which is the nearest thing
# to a fractal that survives an 0.4 mm nozzle -- a real branching tree at this
# scale ends in twigs thinner than a line width, and they snap.
ACTIVE_H = 20.00          # 2.4 times a marker. It is meant to stand out.
# The lathe is a stepped SPIRE: foot, shaft, head, and then three columns
# each narrower than the last, with a flat ledge at every step. Each ledge is
# what a tier of spikes stands on -- a spike has to land on something or the
# union leaves it floating in the air, which is exactly what the first
# version did.
ACTIVE_BODY_PROFILE = [
    (8.75, 0.00),
    (8.75, 0.70),   # the foot: full width, and the flat bottom the contract
    (7.40, 1.50),   # wants. Narrowing upward the whole way, so no support.
    (4.70, 2.90),
    (4.70, 4.30),
    (3.60, 6.60),   # the shaft. 3.60 keeps 1.20 of wall round the socket
    (3.60, 11.40),  # roof on the way past it.
    (6.60, 14.60),  # flaring back out at 43 degrees to carry the head
    (6.60, 15.20),  # the head's rim
    (4.30, 15.20),  # ledge -- tier 1 stands on this
    (4.30, 17.00),
    (2.60, 17.00),  # ledge -- tier 2
    (2.60, 18.40),
    (1.30, 18.40),  # ledge -- tier 3
    (1.30, 19.10),  # and the finial caps it
]
ACTIVE_TIERS = [
    # (ring radius, spikes, spike scale, z of the ledge it stands on)
    (5.20, 8, 1.00, 15.20),
    (3.40, 6, 0.70, 17.00),
    (1.90, 5, 0.49, 18.40),
]
ACTIVE_SPIKE = [          # (r, z) of one spike at scale 1, from its own floor
    (0.95, 0.00),         # -- the crown's cone on a cone, shrunk
    (0.42, 1.55),
    (0.72, 2.40),
    (0.66, 2.90),
]
ACTIVE_FINIAL = [         # the tip, on the axis
    (1.30, 0.00),
    (0.55, 0.90),
    (0.95, 1.45),
    (0.00, 1.70),
]
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
