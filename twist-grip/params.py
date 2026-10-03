"""Every dimension of twist-grip, in millimetres and degrees.

Change a number here, run test_fit.py, then build.py. Nothing else in the
project hard-codes a size; if a number appears twice, one of them is wrong.

THE ONE SHAPE THAT IS NOT NEGOTIABLE. The brief fixes three things: a
circular 40 mm opening, two jaws driven inward by twisting the outside, and
jaw faces that touch when the twist is run all the way over. Those three
together fix the size of the whole object, and it is worth seeing why before
changing anything:

  - A face that starts flush with a 40 mm bore and ends at the axis travels
    20 mm. That is not adjustable while both of those hold.
  - The cam pin that drives a jaw cannot sit in front of its face, and the
    cam groove cannot cross the finger hole. So the pin sits behind the face
    by at least the bore radius plus the ring's inner wall plus half a
    groove -- about 27 mm here.
  - So the pin sweeps a band from r=27 to r=47, the ring that carries it is
    about 100 mm across, and the jaw tail reaches r=51 when open, which the
    body plate has to keep supported.

Hence a device about 111 mm across. Shrinking it means giving up one of the
three fixed things, or adding a 2:1 lever between pin and jaw -- two more
moving parts, discussed in direction.md.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# the brief
# ---------------------------------------------------------------------------

BORE_D = 40.0              # the finger opening, clear and circular when open
TWIST_SWEEP = 180.0        # degrees of ring rotation from fully open to shut.
                           # Half a turn: one comfortable wrist movement, and
                           # it makes the two cam grooves tile the ring's face
                           # exactly (see scroll.py).
JAW_COUNT = 2

JAW_TRAVEL = BORE_D / 2.0  # 20.0 -- flush with the bore, to touching at the
                           # axis. Derived, never set: it IS the bore radius.

# ---------------------------------------------------------------------------
# print tolerances
# ---------------------------------------------------------------------------
# An FDM part is not its model. Holes come out undersize, outside corners
# come out oversize, and a sliding fit designed at nominal is a press fit in
# plastic. Every clearance in this file is one of these four, so that a first
# print can move all of them at once.

FIT_SLIDE = 0.35           # faces that slide across each other in use
FIT_TURN = 0.35            # the rotating bearing between ring and skirt
FIT_FREE = 0.30            # faces that only need to not touch
WALL_MIN = 1.6             # thinnest wall anywhere -- four 0.4 mm lines

# ---------------------------------------------------------------------------
# the cam pin and its groove
# ---------------------------------------------------------------------------

PIN_D = 5.0                # the pin standing under each jaw
GROOVE_W = PIN_D + 2 * FIT_SLIDE      # 5.7
GROOVE_DEPTH = 4.6
PIN_LEN = GROOVE_DEPTH - FIT_FREE     # 4.3, so the pin never bottoms out
# EACH END OF A GROOVE GETS A FLAT PAD, and its length is not a free
# choice. The groove is a swept slot with a cap square to its path, so the
# pin's CENTRE has to come to rest a pin radius short of that cap -- measured
# along the arc, which means the angle depends on the radius. A flat 2 deg
# looked generous and was not: at the inner end, where the arc is shortest,
# 2 deg put a third of the pin through the end wall of its own groove.
GROOVE_END_CLEAR = FIT_FREE
_pad = lambda r: math.degrees((GROOVE_W / 2 + GROOVE_END_CLEAR) / r)

# ---------------------------------------------------------------------------
# the twist ring, and the chain of walls that sets the whole size
# ---------------------------------------------------------------------------
# Read this top to bottom: every radius is derived from the one above it, and
# the first one is the finger. Setting any of them by hand breaks the chain
# and puts a wall somewhere at nothing. test_fit.py measures the real walls
# in the finished meshes, not these numbers, so a broken chain shows up.

SKIRT_ID = BORE_D                                  # the bore runs straight
SKIRT_OD = SKIRT_ID + 2 * WALL_MIN                 # 43.2
RING_ID = SKIRT_OD + 2 * FIT_TURN                  # 43.9, the turning fit

# The lip inside the ring, and the lugs that hook under it, are what holds
# the object together. LIP_OVERLAP is how much of the lug the lip actually
# covers -- the only thing resisting a finger being pulled out of a shut jaw.
LIP_OVERLAP = 1.6
LIP_R_OUT = RING_ID / 2 + LIP_OVERLAP              # 23.55
LIP_Z0 = 3.8                                       # underside of the lip

# THE SIZE DRIVER. The groove cannot start until the lip has ended and a wall
# has been put between them -- it is measured from LIP_R_OUT, not from the
# bore. Getting this wrong is how the first version of this file left a
# 0.35 mm wall between the lip pocket and the groove.
RING_INNER_WALL = WALL_MIN
R_GROOVE_IN = LIP_R_OUT + RING_INNER_WALL          # 25.15
R_PIN_IN = R_GROOVE_IN + GROOVE_W / 2              # 28.0
R_PIN_OUT = R_PIN_IN + JAW_TRAVEL                  # 48.0
R_GROOVE_OUT = R_PIN_OUT + GROOVE_W / 2            # 50.85

RING_OUTER_WALL = 2.45
RING_T = 7.0
RING_FLOOR = RING_T - GROOVE_DEPTH                 # 2.4 under every groove

# The end pads, now that the two radii exist. The inner one is the longer in
# angle because the same arc length subtends more of a smaller circle.
GROOVE_PAD_IN = _pad(R_PIN_IN)                     # ~6.4 deg
GROOVE_PAD_OUT = _pad(R_PIN_OUT)                   # ~3.8 deg

# ---------------------------------------------------------------------------
# the jaws
# ---------------------------------------------------------------------------

JAW_W = 13.0                           # the sliding base, in its channel
SLOT_W = JAW_W + 2 * FIT_SLIDE         # 13.7
JAW_H = 4.4                            # height of that base

# The pin sits exactly R_PIN_IN behind the face, because when the face is on
# the axis the pin is at its innermost. One number, two meanings, and they
# cannot drift apart.
PIN_OFFSET = R_PIN_IN                  # 28.0
JAW_TAIL = PIN_D / 2 + 2.0             # material behind the pin
JAW_L = PIN_OFFSET + JAW_TAIL          # 32.5

# The pad is what touches the finger, and what touches the other pad when
# shut. It rises through the window in the channel's lid, so it can be taller
# than the base it rides on.
PAD_W = 8.6
PAD_L = 6.0
WINDOW_W = PAD_W + 2 * FIT_SLIDE       # 9.3

# ---------------------------------------------------------------------------
# the body
# ---------------------------------------------------------------------------

PLATE_T = 7.0
PLATE_GAP = 0.30                       # body plate clear of the ring's face
# LIP_T is derived from the lid's underside in the stack below, not stated
# here: the jaw rides on the RING's face, a little below the plate's own
# underside, so stating a lid thickness directly gave the jaw 0.6 mm of float
# where 0.3 was meant.

# The plate has to stay under the jaw tail at full open. That is what sets
# its diameter -- the jaw does, not a styling choice.
JAW_TAIL_R_MAX = BORE_D / 2 + JAW_L    # 52.5
PLATE_OD = 2 * (JAW_TAIL_R_MAX + 0.5)  # 106.0

SKIRT_Z0 = 0.0                         # flush with the ring's underside, so
                                       # the object stands on both
LUG_ARC = 30.0                         # degrees of arc per lug
LUG_R_OUT = LIP_R_OUT - FIT_FREE       # 23.25
LUG_H = 2.2
LUG_Z1 = LIP_Z0 - FIT_FREE             # 3.5, just under the lip, so the body
LUG_Z0 = LUG_Z1 - LUG_H                # can only ever lift by FIT_FREE

# WHY THESE THREE ANGLES AND NOT 0/120/240. The lugs pass through notches in
# the lip to go together, and the ring must never find those notches again
# while in use. Evenly spaced lugs line up with their notches every 120
# degrees -- including at 120, the middle of a 180 degree sweep, where the
# body would lift straight off a shut mechanism. Spacing them unevenly means
# the only rotation lining all three up at once is none at all: the gaps here
# are 100, 115 and 145 degrees, all different, so no turn maps the set onto
# itself. The notches are open at full open and nowhere else, which is where
# it is meant to come apart.
LUG_ANGLES = (0.0, 100.0, 215.0)
LUG_COUNT = len(LUG_ANGLES)
NOTCH_SLACK = 3.0                      # degrees each side, to assemble by hand

# ---------------------------------------------------------------------------
# the grip
# ---------------------------------------------------------------------------
# The ring is the thing you twist, so it has to be the outermost thing, and
# it has to stand proud of the body plate -- which the jaw tails have already
# pushed out to 104 mm.

WALL_ID = PLATE_OD + 2 * FIT_FREE      # 106.6
WALL_T = 3.2
WALL_H = 16.0                          # a little above the plate's top face
FLUTE_COUNT = 24
FLUTE_D = 3.4                          # scalloped out of the wall's outside
FLUTE_DEPTH = 0.9

# ---------------------------------------------------------------------------
# the stack, bottom to top
# ---------------------------------------------------------------------------

Z_RING_0 = 0.0
Z_RING_TOP = Z_RING_0 + RING_T                  # 7.0
Z_JAW_0 = Z_RING_TOP                            # jaws ride on the ring's face
Z_PLATE_0 = Z_RING_TOP + PLATE_GAP              # 7.3
Z_PLATE_TOP = Z_PLATE_0 + PLATE_T               # 14.3
Z_LID_0 = Z_JAW_0 + JAW_H + FIT_FREE            # 11.7, underside of the lid:
                                                # measured from the jaw that
                                                # has to fit under it
LIP_T = Z_PLATE_TOP - Z_LID_0                   # 2.6
Z_PAD_TOP = Z_PLATE_TOP                         # pad flush with the top face
Z_PIN_BASE = Z_JAW_0 - PIN_LEN                  # 2.7
Z_GROOVE_FLOOR = RING_FLOOR                     # 2.4

OVERALL_D = 2 * (WALL_ID / 2 + WALL_T)          # 113.0
OVERALL_H = max(WALL_H, Z_PLATE_TOP)            # 16.0

# ---------------------------------------------------------------------------
# materials and the machine
# ---------------------------------------------------------------------------
# See ../available-tools.md. PETG is the functional default: tough, slides on
# itself without galling the way PLA does, and does not creep under a held
# load the way PLA does -- and this thing is meant to be squeezed and left
# squeezed. Colours are filament actually on the shelf.

BED = (325.0, 320.0)       # H2D single-nozzle envelope
NOZZLE = 0.4
LAYER = 0.2

COL_RING = (0.05, 0.08, 0.10)          # PETG Basic, black
COL_BODY = (0.93, 0.94, 0.92)          # PETG Basic, white
COL_JAW = (0.95, 0.42, 0.05)           # PETG Basic, orange
COL_CUT = (0.62, 0.64, 0.68)           # section-cut faces

# ---------------------------------------------------------------------------

DEG = math.pi / 180.0
