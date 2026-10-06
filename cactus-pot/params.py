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

POT_BORE_D = 32.00      # the blind socket in the pot's inner floor
POT_SOCKET_DEPTH = 8.00 # how deep that socket goes
POT_FLOOR_TO_RIM = 21.0 # the cactus's first 21 mm are down inside the pot
POT_INNER_R = 38.80     # the pot's inner wall, at its tightest, above the
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
SPIGOT_H = 7.40         # shorter than the socket, so the cactus lands on the
                        # pot's floor rather than on the bottom of the hole
SPIGOT_CHAMFER = 0.60   # lead-in so it finds the bore without a fight
SPIGOT_R = 0.5 * (POT_BORE_D - 2 * SPIGOT_CLEAR)

# ---------------------------------------------------------------------------
# TRUNK — the columnar body
# ---------------------------------------------------------------------------
# A saguaro, not a ball. The cartoon version of this shape is a smooth
# capsule with a bulge; what makes it read as a real cactus is three things,
# all of them here: ribs that run the whole height, a waist that narrows
# going up rather than a constant tube, and a crown that is flattened and
# slightly sunken instead of a hemisphere.

TRUNK_H = 168.0         # soil line to the top of the crown
TRUNK_R_BASE = 26.0     # radius at the soil line (mean, before ribbing)
TRUNK_R_MID = 27.6      # the slight swell a real trunk carries low down
TRUNK_R_TOP = 21.4      # tapered in at the shoulder
TRUNK_MID_FRAC = 0.22   # height fraction where the swell peaks

RIB_COUNT = 15          # saguaros run 12-24. An odd count stops the eye
                        # pairing ribs across the silhouette, which is what
                        # makes a ribbed column look machined.
RIB_DEPTH = 3.60        # crest-to-valley, at mid height
RIB_SHARPNESS = 0.78    # 0 = sinusoid, 1 = crests pinched and valleys wide,
                        # which is how an areole-bearing rib actually sits
RIB_TWIST_DEG = 7.0     # total twist over the full height: nothing in nature
                        # runs dead straight, and 7 degrees is below the point
                        # where it reads as a deliberate spiral
RIB_FADE_TOP = 0.90     # ribs shallow out towards the crown (height fraction
                        # where fading starts)
RIB_FADE_BASE = 0.04    # and die into the soil line, so the spigot's shoulder
                        # is a clean circle

WOBBLE_AMP = 0.68       # low-frequency asymmetry on the whole column. Small,
WOBBLE_TURNS = 1.6      # and the single biggest thing separating "grown" from
                        # "revolved". Without it the trunk is a lathe part.

CROWN_FLAT_FRAC = 0.46  # how much of the top radius is the flattened crown
CROWN_RISE = 11.4        # how far the crown lifts above the shoulder
CROWN_DIMPLE = 2.00     # the apical depression, where a saguaro grows from

# ---------------------------------------------------------------------------
# ARMS
# ---------------------------------------------------------------------------
# Each arm: (height fraction on the trunk, bearing in degrees, length,
#            radius, how far it is bent up towards vertical)
# Two arms, at different heights and nowhere near 180 degrees apart. A
# symmetric pair is the single most cartoonish thing a cactus can do.

ARMS = (
    dict(z_frac=0.42, bearing=28.0, length=88.0, r=12.4, elbow=0.50, rise=0.95),
    dict(z_frac=0.66, bearing=214.0, length=64.0, r=10.4, elbow=0.46, rise=0.90),
)
ARM_RIB_COUNT = 11      # fewer ribs on a thinner stem, as in the real plant
ARM_RIB_DEPTH = 2.40
ARM_BLEND = 3.2         # radius of the fillet where an arm meets the trunk.
                        # An un-filleted join is both ugly and a stress riser
                        # in a printed part that will be picked up by an arm.

# ---------------------------------------------------------------------------
# AREOLES — the raised pads the spikes grow out of
# ---------------------------------------------------------------------------
# On a real cactus spines never come straight out of the skin: they come out
# of a woolly pad sitting on the crest of a rib, evenly spaced up the rib.
# Modelling the pad is what stops the sockets looking like drilled holes.

AREOLE_PITCH = 18.0     # vertical spacing along a rib crest
AREOLE_R = 2.60         # radius of the pad
AREOLE_RISE = 0.70      # how far it stands off the crest
AREOLE_Z_JITTER = 2.1   # DEAD. Kept only so an old params file is obviously
                        # stale rather than silently different: the rib-to-rib
                        # stagger is no longer a fixed step. See RIB_PHASE_*.
AREOLE_Z_MIN = 24.0     # none below this. The pot's rim stands 21 mm above
                        # its floor and the trunk is 13 mm clear of the pot's
                        # inner wall, so a spine down there would either be
                        # invisible or foul the pot going in.
AREOLE_CROWN_KEEP = 0.96  # and none above this height fraction

# Which ribs carry pads. Every rib on the trunk is 13 x 7 = 91 sockets and an
# evening with tweezers; every other rib is half that and still reads as a
# spiny cactus from any distance. SPIKE_RIB_STEP is the dial.
SPIKE_RIB_STEP = 2      # 1 = every rib, 2 = every other rib
ARM_SPIKE_RIB_STEP = 2

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

PIN_D = 1.90            # nominal joint diameter. Below ~1.6 the pin is one
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

SOCKET_DEPTH = 3.40     # bored this deep. Deeper would hold better and it
                        # cannot be had: a raked bore cuts a long chord, and
                        # on the thinner arm this is what leaves 2 mm of wall
                        # under the hole. test_fit.py measures it.
PIN_SHANK_L = 2.80      # the pin is shorter than the bore, so the collar
                        # lands on the pad and a blob in the hole's bottom
                        # cannot hold the spike proud
SOCKET_MOUTH_CHAMFER = 0.25   # a lead-in, so the pin self-centres instead of
                              # peeling the mouth of the hole. Small, because
                              # the collar has to cover it.
SOCKET_RELIEF_D = 0.60  # a narrower blind extension past the bore's bottom:
SOCKET_RELIEF_L = 1.00  # somewhere for stringing and a first-layer blob to
                        # go, so neither can hold the spike proud. It is
                        # narrower than the bore so it never touches the pin.

# ---------------------------------------------------------------------------
# SPIKE — the separate part
# ---------------------------------------------------------------------------
# Printed standing on the flat end of its own pin, point up: every layer is
# smaller than the one below, which is the only orientation that gives a
# needle a clean taper and no supports. The collar doubles as its own brim.

SPIKE_L = 16.0          # exposed length above the pad
SPIKE_TIP_D = 0.42      # one nozzle width. A true point cannot be printed;
                        # 0.42 is the smallest honest number and it still
                        # feels sharp to a fingertip.
SPIKE_BELLY = 0.18      # how much the needle bows out from a straight cone,
                        # 0 = cone, 1 = strongly convex. A real spine is not
                        # a straight taper.
SPIKE_COLLAR_D = 2.90   # seats on the areole, hides the socket mouth, and
SPIKE_COLLAR_H = 0.55   # gives the part a first layer worth printing
SPIKE_FLOOR_DEG = -14.0  # no spine may hang lower than this off horizontal:
                         # its socket would be a hole in a roof. The arm
                         # undersides are where this bites.
SPIKE_RAKE_DEG = 34.0   # how far the spike leans up from the surface normal.
                        # Spines on a saguaro point up and out, not straight
                        # out, and this one number does more for realism than
                        # anything else on the part.

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
AREOLE_Z_SCATTER = 1.4      # +/- mm on a pad's position along its rib. Small
                            # on purpose: the rib-to-rib stagger below is
                            # what stops the pads reading as rows, and a
                            # scatter bigger than half that stagger just
                            # undoes it at random.

# Where each rib starts its run of pads, as a fraction of AREOLE_PITCH.
# This was a fixed step of 2.1 mm per rib, and a fixed step is a pattern: a
# small one reads as a spiral winding up the cactus, and with the pads
# otherwise evenly spaced the eye joins them into rings. Real spines do not
# line up with their neighbours in either direction.
#
# So the phases are drawn at random from SEED and then REJECTED until they
# satisfy both rules below, which is why they are constraints rather than a
# formula -- a formula is the thing that produced the pattern.
RIB_PHASE_MIN_SEP = 0.24    # no two neighbouring ribs may start within this
                            # fraction of a pitch of each other: that is what
                            # makes pads look level with the ones beside them
RIB_PHASE_RUN_TOL = 0.13    # and no three consecutive gaps may agree this
                            # closely -- three equal gaps is four ribs in a
                            # row marching, which is the diagonal version of
                            # the same fault
RIB_PHASE_TRIES = 4000      # draws allowed before giving up and saying so
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
