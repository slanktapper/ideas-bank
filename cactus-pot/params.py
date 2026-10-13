"""Every dimension of the cactus and its spikes, in millimetres.

One file so a number is changed in one place and the geometry, the checks and
the renders all follow. Nothing here is a magic constant without a reason
written beside it.

The pot itself is not modelled here. It is built by the other half of this
project, in `pot/`, and lands as a mesh at `POT_STL`; the cactus only has to
agree with it where they meet -- the socket the spigot drops into, the floor
it stands on and the rim height. Those live in the POT block and are the first
things to re-measure when the pot changes. `build.py` and `test_fit.py` read
that mesh and fail loudly if these numbers have drifted from it.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# machine and material
# ---------------------------------------------------------------------------

NOZZLE = 0.40           # Bambu H2D stock nozzle; the thinnest wall worth asking for
LAYER = 0.20            # a sane default layer for a decorative part this size
BED = (325.0, 320.0)    # single-nozzle build area; the plate check uses it

# ---------------------------------------------------------------------------
# THE TWO DIALS
# ---------------------------------------------------------------------------
# Every length below is written as its original design number times SCALE, so
# the shape that was drawn and argued over stays legible and the size is one
# number. Rob asked for everything 25% bigger on 2026-10-07.
#
# What is NOT multiplied by it: anything a 0.4 mm nozzle decides. PRESS_FIT,
# SOCKET_COMP, PIN_COMP, SPIGOT_CLEAR, the mouth chamfer and the engraving on
# the coupon are all compensations for what hot plastic does on its way out of
# a fixed-size hole, and the nozzle does not get 25% bigger with the model.
# Scaling them would quietly take the interference from 0.06 to 0.075 mm.
SCALE = 1.25

# The spine's own thickness, which does not follow SCALE. Rob asked for 3x;
# a 3x pin needs a Ø5.86 socket and the rib crest it has to sit on measures
# 3.0 mm, so the hole broke out of the crest into the hollows either side and
# 31 of 110 pads came out drowned. 1.9x is the most the existing ribs carry:
# it puts a Ø3.76 socket on a crest that is 3.8 mm wide at this scale.
SPINE_THICK = 1.9

# ---------------------------------------------------------------------------
# POT — the two numbers the cactus shares with the printed pot
# ---------------------------------------------------------------------------
# PROVISIONAL until the pot mesh is measured. `build.py --pot <stl>` prints
# the measured bore and soil line and refuses to build if these disagree with
# it by more than POT_TOL, so a stale number here fails loudly rather than
# producing a cactus that does not drop in.

# The pot is the other half of this project and lives in pot/, built by its
# own code. It is a mesh to this half -- measured, never imported -- so what
# `build.py --pot` and `test_fit.py --pot` read by default is its STL. Pass
# --pot <path> to measure a different one.
POT_STL = "pot/stl/pebble-pot.stl"

POT_BORE_D = 32.00 * SCALE      # the blind socket in the pot's inner floor
POT_SOCKET_DEPTH = 8.00 * SCALE # how deep that socket goes
POT_FLOOR_TO_RIM = 21.0 * SCALE # the cactus's first 21 mm are down inside the pot
POT_INNER_R = 38.80 * SCALE     # the pot's inner wall, at its tightest, above the
                        # floor. Deliberately the TIGHTER of the two pots
                        # measured. The pebble pot is filleted where its wall
                        # meets its floor, so it is 38.8 right in that corner
                        # and opens to 42.8 by 4 mm up -- and the corner is
                        # the number to hold, because the check this feeds
                        # only cares about the worst case.
POT_TOL = 0.50          # how far the measured pot may differ before the build stops

SPIGOT_CLEAR = 0.35     # the spigot is this much under the bore, per side:
                        # a drop-in fit, not a press fit. The cactus should
                        # lift out, and it is a long lever arm.
SPIGOT_H = 7.40 * SCALE         # shorter than the socket, so the cactus lands on the
                        # pot's floor rather than on the bottom of the hole
SPIGOT_CHAMFER = 0.60 * SCALE   # lead-in so it finds the bore without a fight
SPIGOT_R = 0.5 * (POT_BORE_D - 2 * SPIGOT_CLEAR)

# ---------------------------------------------------------------------------
# TRUNK — the columnar body
# ---------------------------------------------------------------------------
# A saguaro, not a ball. The cartoon version of this shape is a smooth
# capsule with a bulge; what makes it read as a real cactus is three things,
# all of them here: ribs that run the whole height, a waist that narrows
# going up rather than a constant tube, and a crown that is flattened and
# slightly sunken instead of a hemisphere.

TRUNK_H = 168.0 * SCALE         # soil line to the top of the crown
TRUNK_R_BASE = 26.0 * SCALE     # radius at the soil line (mean, before ribbing)
TRUNK_R_MID = 27.6 * SCALE      # the slight swell a real trunk carries low down
TRUNK_R_TOP = 21.4 * SCALE      # tapered in at the shoulder
TRUNK_MID_FRAC = 0.22   # height fraction where the swell peaks

RIB_COUNT = 15          # saguaros run 12-24. An odd count stops the eye
                        # pairing ribs across the silhouette, which is what
                        # makes a ribbed column look machined.
RIB_DEPTH = 3.60 * SCALE        # crest-to-valley, at mid height
RIB_SHARPNESS = 0.78    # 0 = sinusoid, 1 = crests pinched and valleys wide,
                        # which is how an areole-bearing rib actually sits
RIB_TWIST_DEG = 7.0     # total twist over the full height: nothing in nature
                        # runs dead straight, and 7 degrees is below the point
                        # where it reads as a deliberate spiral
RIB_FADE_TOP = 0.90     # height fraction where the fade towards the crown
                        # starts, and ...
RIB_TIP_KEEP = 1.00     # ... how much rib depth is still there at the top of
                        # it. At 1.0 there is no fade: the ribs run at full
                        # depth right up to TRUNK_H, which is what carries
                        # them over the crown, because the crown's rings are
                        # the ring at TRUNK_H scaled down -- ribs and all --
                        # so they converge at the apical depression the way a
                        # saguaro's do. It used to be 0, and the top 21 mm of
                        # the plant came out as a turned dome with no ribs on
                        # it at all. The crest colour part simply stopped
                        # there, which is how it was noticed.
RIB_FADE_BASE = 0.04    # Ribs die into the soil line, so the spigot's
                        # shoulder is a clean circle

WOBBLE_AMP = 0.68 * SCALE       # low-frequency asymmetry on the whole column. Small,
WOBBLE_TURNS = 1.6      # and the single biggest thing separating "grown" from
                        # "revolved". Without it the trunk is a lathe part.

CROWN_FLAT_FRAC = 0.46  # how much of the top radius is the flattened crown
CROWN_RISE = 11.4 * SCALE        # how far the crown lifts above the shoulder
CROWN_DIMPLE = 2.00 * SCALE     # the apical depression, where a saguaro grows from

# ---------------------------------------------------------------------------
# ARMS
# ---------------------------------------------------------------------------
# Each arm: (height fraction on the trunk, bearing in degrees, length,
#            radius, how far it is bent up towards vertical)
# Two arms, at different heights and nowhere near 180 degrees apart. A
# symmetric pair is the single most cartoonish thing a cactus can do.

ARMS = (
    dict(z_frac=0.42, bearing=28.0, length=88.0 * SCALE, r=12.4 * SCALE,
         elbow=0.50, rise=0.95),
    dict(z_frac=0.66, bearing=214.0, length=64.0 * SCALE, r=10.4 * SCALE,
         elbow=0.46, rise=0.90),
)
# Where an arm becomes the trunk. The flare used to decay over a FRACTION of
# the arm's length -- 10% of it -- which meant the long arm and the short one
# blended over different distances, and 4 mm of swell was not enough for
# either: the arm met the trunk at nearly full width and crossed it in a
# crease, so the cactus read as three pieces stuck together rather than one
# plant. These are millimetres along the spine, so both arms blend alike.
ARM_BLEND_REACH = 12.0   # how far down the arm the flare reaches
ARM_ROOT_INSET = 12.0     # how far inside the trunk the spine starts,
                                 # so the widest part of the flare is buried
                                 # and the arm grows out instead of poking
                                 # through

# The seam, where an arm becomes the trunk.
#
# Fattening the arm's root and swelling the trunk were both tried and both
# failed, for the same reason: a boolean union meets along a curve with a
# hard tangent break, and adding material to either side moves the break
# rather than softening it. The big shoulder was worse than no shoulder --
# at size it stopped reading as a swelling and started reading as a cuff.
#
# So the fillet is made the way a fillet actually is: by pulling material
# across the corner. After the arms are unioned on, the mesh is relaxed in a
# ball around each arm's root, hard at the root and fading to nothing by
# ARM_SEAM_REACH, which leaves the ribs further up the arm and down the
# trunk untouched.
ARM_SEAM_REACH = 35.0 * SCALE    # how far from the root the relaxing reaches
ARM_SEAM_SWEEPS = 0              # Laplacian sweeps. OFF: the junction Rob
                                 # chose on 2026-10-09 was test-arm-d, and
                                 # every one of those test files was built
                                 # with the relaxing off. Turning it back on
                                 # would hand him a model he has not seen.
                                 # The flare at blend 3 / reach 12 is doing
                                 # the work instead.
ARM_SEAM_STRENGTH = 0.65         # how far a vertex moves towards its
                                 # neighbours' average each sweep

ARM_RIB_COUNT = 11      # fewer ribs on a thinner stem, as in the real plant
ARM_RIB_DEPTH = 2.40 * SCALE
ARM_RIB_FADE_TIP = 0.90     # the arm's own RIB_FADE_TOP: where the fade to
                            # ARM_RIB_TIP_KEEP starts, as a fraction along the
                            # spine. This was a bare 0.10 inside arm_rings.
ARM_RIB_TIP_KEEP = 1.00     # and how much survives. At 1.0 the ribs shrink
                            # only with the tip's own rounding, so they close
                            # on the tip instead of flattening out before it.
ARM_RIB_ROOT_RAMP = 0.14    # fraction of the arm over which the ribs come up
                            # out of the trunk. Was bare too.
ARM_BLEND = 3.0         # radius of the fillet where an arm meets the trunk.
                        # An un-filleted join is both ugly and a stress riser
                        # in a printed part that will be picked up by an arm.

# ---------------------------------------------------------------------------
# AREOLES — the raised pads the spikes grow out of
# ---------------------------------------------------------------------------
# On a real cactus spines never come straight out of the skin: they come out
# of a woolly pad sitting on the crest of a rib. Modelling the pad is what
# stops the sockets looking like drilled holes. Where the pads go is further
# down, under AREOLE_MIN_SEP; it is not as simple as evenly up a rib, and the
# reason it is not is written there.

AREOLE_R = 2.60 * SCALE         # radius of the pad. Grown with the spine: a Ø5.86
                        # socket in the Ø5.20 pad it used to be would have
                        # been a hole with a hairline of pad around it.
AREOLE_RISE = 0.70 * SCALE      # how far it stands off the crest
AREOLE_Z_JITTER = 2.1   # DEAD. Kept only so an old params file is obviously
                        # stale rather than silently different: the trunk's
                        # pads are not stepped up a rib at all now, and the
                        # arms' pads are not stepped either. Spacing is the
                        # dial now: see AREOLE_MIN_SEP.
AREOLE_Z_MIN = 24.0 * SCALE     # none below this. The pot's rim stands 21 mm above
                        # its floor and the trunk is 13 mm clear of the pot's
                        # inner wall, so a spine down there would either be
                        # invisible or foul the pot going in.
AREOLE_CROWN_KEEP = 0.96  # and none above this height fraction

# Which ribs carry pads: all of them, on the trunk and on both arms. There
# used to be a SPIKE_RIB_STEP and an ARM_SPIKE_RIB_STEP that put pads on
# every other rib, and they are the reason the spines read as stripes -- see
# AREOLE_MIN_SEP. Both are gone; if an old params file still sets them,
# nothing reads them.

# ---------------------------------------------------------------------------
# PRESS FIT — the socket in the cactus and the pin on the spike
# ---------------------------------------------------------------------------
# The whole point of the exercise, so it gets the most words.
#
# An FDM hole comes out undersize. The extrusion is laid on the hole's
# centreline and the inside corner of every layer is pulled in by the
# nozzle's own width and by die swell, so a Ø2.00 hole modelled as a circle
# measures about Ø1.85 printed with a 0.4 nozzle, more on the first layers.
# A pin comes out slightly OVERSIZE for the mirror of the same reason. Design
# both at nominal and the joint is an interference fit you cannot push home
# without snapping a 1 mm spike.
#
# So the numbers below are deliberately asymmetric: the socket is modelled
# OVER its nominal by SOCKET_COMP and the pin UNDER by PIN_COMP, and what is
# left between them after printing is PRESS_FIT -- a light interference that
# a thumb can seat and that holds without glue.

PIN_D = 1.90 * SPINE_THICK            # 3x the 1.90 it was: Rob asked for a spine three
                        # times thicker, and with the collar gone this is
                        # also the footprint the part prints on.
                        # Nominal joint diameter. Below ~1.6 the pin is one
                        # perimeter with no infill and shears off in the hole;
                        # above ~2.4 the pad has to grow to hold it and the
                        # spike stops looking like a spine.
PRESS_FIT = -0.06       # negative = interference. The target *printed*
                        # clearance: the pin is 0.06 fatter than the hole, so
                        # it bites. -0.04 is loose in PETG, -0.10 needs pliers.
SOCKET_COMP = 0.16      # modelled oversize on the hole, to cancel shrink-in
PIN_COMP = 0.10         # modelled undersize on the pin, to cancel swell

SOCKET_D = PIN_D + SOCKET_COMP              # 2.06 modelled -> ~1.90 printed
PIN_SHANK_D = PIN_D - PRESS_FIT - PIN_COMP  # 1.86 modelled -> ~1.96 printed
                                            # 1.96 into 1.90 = the 0.06 bite

SOCKET_DEPTH = 3.40 * SCALE     # bored this deep. Deeper would hold better and it
                        # cannot be had: a raked bore cuts a long chord, and
                        # on the thinner arm this is what leaves 2 mm of wall
                        # under the hole. test_fit.py measures it.
PIN_SHANK_L = SOCKET_DEPTH   # the post fills the bore exactly. With no
                        # collar there is nothing else to stop it: the post
                        # bottoms on the floor of the bore, and that is what
                        # sets how much spine stands out. Shorter and the
                        # spine would sink; longer and it would stand proud.
SOCKET_MOUTH_CHAMFER = 0.25   # a lead-in, so the pin self-centres instead of
                              # peeling the mouth of the hole. Small, because
                              # the collar has to cover it.
SOCKET_RELIEF_D = 0.60  # a narrower blind extension past the bore's bottom:
SOCKET_RELIEF_L = 1.00 * SCALE  # somewhere for stringing and a first-layer blob to
                        # go, so neither can hold the spike proud. It is
                        # narrower than the bore so it never touches the pin.

# ---------------------------------------------------------------------------
# SPIKE — the separate part
# ---------------------------------------------------------------------------
# Printed standing on the flat end of its own pin, point up: every layer is
# smaller than the one below, which is the only orientation that gives a
# needle a clean taper and no supports. The collar doubles as its own brim.

SPIKE_L = 12.0 * SCALE          # exposed length above the pad. Was 16.0; Rob asked
                        # for 75% of it on 2026-10-06, and shorter spines
                        # read as a saguaro's rather than a hedgehog's.
                        # The socket, the pin and the collar are untouched,
                        # so a printed spike still seats the same way.
SPIKE_TIP_D = 0.42 * SPINE_THICK      # 3x, in step with the rest of the spine. One
                        # nozzle width was the old limit; A true point cannot be printed;
                        # 0.42 is the smallest honest number and it still
                        # feels sharp to a fingertip.
SPIKE_BELLY = 0.18      # how much the needle bows out from a straight cone,
                        # 0 = cone, 1 = strongly convex. A real spine is not
                        # a straight taper.
# No collar. Rob asked for a plain post in a plain hole, so the washer that
# used to sit between the needle and the pad is gone. Two things it was
# quietly doing have to be picked up elsewhere:
#
#   * it covered the socket's countersunk mouth. SOCKET_MOUTH_CHAMFER is now
#     the only thing at the surface, so it is kept small -- it is a lead-in
#     for the post, not a feature.
#   * it was the spike's first layer, a flat Ø2.90 disc that held a 12 mm
#     needle upright on the bed. Without it the part stands on the end of
#     the post itself, so the post's diameter is now also the footprint it
#     prints on. At Ø1.86 that is marginal and wants a brim; at the 3x
#     thickness it is ample, which is the version this is drawn for.
SPIKE_FLOOR_DEG = -14.0  # no spine may hang lower than this off horizontal:
                         # its socket would be a hole in a roof. The arm
                         # undersides are where this bites.
# A socket is a straight hole, so a spine can only go in along its axis. If
# anything of the cactus stands on that line -- the trunk above an arm, the
# far side of a crook -- the spine cannot be got in at all, however good the
# fit is. Rob found several of these by eye on the printed model. This is how
# much clear air a socket needs along its own axis: the spine's whole length
# plus room to hold it.
SPIKE_CLEAR_L = SPIKE_L + PIN_SHANK_L + 12.0

SPIKE_RAKE_DEG = 34.0   # how far the spike leans up from the surface normal.
                        # Spines on a saguaro point up and out, not straight
                        # out, and this one number does more for realism than
                        # anything else on the part.

# ---------------------------------------------------------------------------
# FIT COUPON — the first thing to print
# ---------------------------------------------------------------------------
# A ladder of holes stepping either side of SOCKET_D, so the press fit gets
# measured in the filament it will be printed in rather than trusted from
# arithmetic. Find the hole a spike seats firmly in, read its label, and move
# SOCKET_COMP by that much.
#
# The label is the point of the numbers below. Seven identical holes in a
# plain block are only legible while you still remember which end you started
# counting from -- which is not the state anyone is in a week later, or when
# the coupon turns up in a drawer next to a second one printed in a different
# filament. So each hole carries its own step, engraved beside it in
# hundredths of a millimetre, and the coupon is sized around the label rather
# than the label squeezed into whatever room the holes left.

COUPON_N = 7            # odd, so one hole is the model as drawn and is
                        # labelled 0. Three steps either side of it.
COUPON_STEP = 0.01      # Rob printed the 0.06 ladder on 2026-10-09: 0 won
                        # and +06 was "way too big", so the answer is inside
                        # one step of nominal and the coarse ladder cannot
                        # say where. This is the fine ladder, +/-0.03 across
                        # seven holes.
                        #
                        # It was 0.06, chosen to equal PRESS_FIT so a
                        # neighbour was one whole press fit away and the
                        # winner was obvious. That property is deliberately
                        # given up here: 0.01 is below what the process
                        # repeats to, so the middle holes may well feel
                        # identical -- and if they do, that IS the answer.
                        # It means 0 is right and the fit is already as close
                        # as this printer can place it.
COUPON_PITCH = 10.5     # hole to hole. Set by the label -- "-18" is 8.1 mm of
                        # engraving and wants a gutter either side. It was 7.0
                        # when the holes were unlabelled.
COUPON_MARGIN = 3.0     # material left beyond the outermost label
COUPON_DEPTH_Y = 16.0   # across the block: a row of holes along the top, the
                        # numbers in a row under them, like a rule
COUPON_HOLE_Y = 4.0     # the hole row, off the block's middle
COUPON_T = SOCKET_DEPTH + 3.0   # thick enough that a bored hole still leaves
                                # a floor under it, and stiff enough to push
                                # a spike into without flexing

# The engraving. Cut into the top face, so it needs no support and the digits
# are the last thing the nozzle touches.
# These three are not free of each other, and the binding constraint is the
# counter -- the island of material inside an 8 or a 0, which the engraving
# leaves standing proud and the nozzle has to print. It measures
# (W - stroke) wide by (H/2 - stroke) tall, so a fat stroke in a small box
# closes it up: at H=2.4, W=1.5, stroke=0.8 the counter is 0.7 x 0.4 mm, too
# small for a 0.4 nozzle to lay down, and an engraved 8 comes out as a filled
# pit with no 8 in it. The numbers below leave 1.2 x 1.0 mm, three extrusions
# by two and a half.
COUPON_MARK_H = 3.2     # cap height
COUPON_MARK_W = 1.8     # width of a digit's box, before the stroke is added
COUPON_MARK_STROKE = 0.6    # the groove itself. Narrower than this and the
                            # slicer stops leaving a gap between perimeters
                            # and the number fills in.
COUPON_MARK_GAP = 0.45  # between one character and the next
COUPON_MARK_DEPTH = 0.6     # three layers at 0.2. Deep enough to read as
                            # shadow in a dark filament, shallow enough that
                            # it is not a hole in a 6.4 mm block.
COUPON_MARK_Y = -3.6    # where the row of numbers sits

# ---------------------------------------------------------------------------
# THE SINGLE PAIR — one hole, one spine
# ---------------------------------------------------------------------------
# The smallest thing that answers "does a spike go in and stay in": one
# socket in a tab you can hold, and one spike to push into it. The coupon
# ladders seven diameters and the wedge proves the joint on the real curved
# wall; this is the five-minute version that comes before either, for when
# the question is simply whether the number in SOCKET_COMP is anywhere near
# right in this filament.
#
# It is the *real* socket, not a drilled hole: socket_cutter() gives it the
# countersunk mouth and the debris relief, and the areole pad is unioned on
# first, so the spike's collar lands on a dome exactly as it does on the
# cactus. Without the pad the collar seats on flat plastic and the thing
# worth testing -- that the collar bottoms on the pad before the pin bottoms
# in the hole -- is not being tested at all.

TEST_HOLE_W = 18.0 * SCALE      # across the tab. Wide enough to hold between finger
                        # and thumb and push a spike in without it skating
                        # across the bench.
TEST_HOLE_T = SOCKET_DEPTH + SOCKET_RELIEF_L + 2.0    # 6.4: the bore and its
                        # relief go 4.4 down, and what is left under them is
                        # a 2 mm floor rather than a membrane.

# ---------------------------------------------------------------------------
# TEST PRINT
# ---------------------------------------------------------------------------
# A wedge cut out of the real trunk, so the fit is proved on the geometry it
# will actually be used on rather than on a flat block. A hole in a curved,
# ribbed wall drilled at a 34 degree rake does not print like a hole in a
# coupon: it breaks out through a crest, its mouth is an ellipse, and the
# first layers over it are bridging. If the press fit is going to disagree
# with the arithmetic anywhere, it is here.
#
# Sized to be worth printing twice rather than once: a third of the trunk,
# standing on its own flat bottom, in the same orientation as the real part.

TEST_Z0 = 25.0          # bottom of the wedge, just above the lowest pads
TEST_Z1 = 70.0          # top, just below where the first arm leaves
TEST_WEDGE_DEG = 150.0  # how much of the trunk to keep

SPIKE_PLATE_N = 72      # how many go on a plate
SPIKE_PLATE_PITCH = 6.0

# ---------------------------------------------------------------------------
# tessellation
# ---------------------------------------------------------------------------

SEG_THETA = 240         # points around the trunk: 18 per rib, enough that a
                        # crest is a curve rather than a crease, and low
                        # enough that the exported mesh is megabytes and not
                        # tens of them
SEG_Z = 150             # slices up the trunk
SEG_SPIKE = 20          # facets round a spike; it is 2 mm across. Times 72
                        # on a plate, so this is the number that decides how
                        # big spikes-x72.stl lands
SEG_SOCKET = 32

# ---------------------------------------------------------------------------
# variation
# ---------------------------------------------------------------------------
# Nothing on a plant is on a grid. Pads get a little scatter in height and
# every spike leans at its own angle -- from a fixed seed, so the model is
# still reproducible and a socket does not wander between two builds.

SEED = 20261005
AREOLE_Z_SCATTER = 1.4 * SCALE      # +/- mm on a pad's position along its rib. Small
                            # on purpose: the rib-to-rib stagger below is
                            # what stops the pads reading as rows, and a
                            # scatter bigger than half that stagger just
                            # undoes it at random.

# TRUNK pads: how close two of them may get, measured straight through the
# air rather than along a rib.
#
# The stagger above fixed the rows and could not fix the columns, because a
# pad still belonged to a rib: every rib carrying pads was a vertical line of
# them, and only every other rib carried any, so the trunk wore eight stripes
# of spines. Wandering a pad off its own crest does not help enough to
# matter -- a few degrees is a couple of mm at the trunk's radius, against
# the 11.3 mm gap to the next rib, so the line only wobbles. It was built,
# rendered and measured, and it still read as eight lines.
#
# So a trunk pad no longer belongs to a rib. A crest and a height are drawn
# together, every crest in the draw rather than every other one, and the pad
# is kept only if it clears every pad already placed by AREOLE_MIN_SEP. The
# draw runs until the surface will not take another. Nothing decides in
# advance how many pads a crest gets, which is what stops them being columns.
#
# That makes this number, not a count, the dial: spacing is the thing with a
# physical meaning and the count follows from it. 14.5 lands 65 on the trunk,
# which is where the per-rib layout it replaced had got to. Smaller means
# more spines and more evenings with tweezers.
AREOLE_MIN_SEP = 14.5 * SCALE
ARM_AREOLE_MIN_SEP = 11.0 * SCALE   # the same for an arm, which is a thinner stem
                            # carrying a smaller spine, so they sit closer
AREOLE_FILL_TRIES = 600     # consecutive rejections before calling it full
AREOLE_LADDER_TOL = 2.0     # three pads up one crest whose two gaps agree
                            # within this many mm are a column in miniature,
                            # so the draw rejects the third. Spacing alone
                            # does not rule it out: two pads both landing at
                            # exactly AREOLE_MIN_SEP make a perfect ladder.
AREOLE_TH_SCATTER = 3.8     # +/- degrees a pad may sit off the top of its
                            # crest. Ribs are 360/RIB_COUNT apart so a crest
                            # is half that wide; past about a third of the
                            # way to the valley the pad is on the flank and
                            # its socket is bored into a slope, so this stays
                            # inside that. It is the finishing touch, not the
                            # fix -- AREOLE_MIN_SEP is the fix.
SPIKE_RAKE_SCATTER = 9.0    # +/- degrees on the lean
SPIKE_SWING_SCATTER = 7.0   # +/- degrees of sideways swing off the crest


def rib_profile(theta: np.ndarray, count: int, sharpness: float) -> np.ndarray:
    """Rib cross-section shape, in [-0.5, +0.5]; +0.5 is a crest.

    A plain cosine gives crests and valleys of the same width, which reads as
    fluting on a column. Real ribs have narrow crests and broad valleys, so
    the cosine is warped towards its peaks by `sharpness`.
    """
    c = np.cos(theta * count)
    warped = np.sign(c) * np.abs(c) ** (1.0 - 0.55 * sharpness)
    return 0.5 * warped


# Two sockets in one tab, at the spacing they sit at on the trunk. The single
# hole says whether a spine goes in; this says what two of them look like next
# to each other, which is the question the new thickness actually raises --
# a spine you judge on its own always looks reasonable. It is also the piece
# to be rough with: seat both, then pull one out and keep the other, so the
# destructive test and the kept reference are the same print.
TEST_PAIR_SEP = AREOLE_MIN_SEP      # the real trunk spacing, not a guess
TEST_PAIR_W = TEST_PAIR_SEP + 4 * AREOLE_R + 6.0
