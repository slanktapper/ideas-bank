"""Every dimension of twist-grip, in millimetres and degrees.

Change a number here, run test_fit.py, then build.py. Nothing else in the
project hard-codes a size; if a number appears twice, one of them is wrong.

WHAT THE BRIEF FIXES, and what that forces:

  - a circular 40 mm opening, straight through;
  - two jaws driven inward by twisting the outside;
  - faces that touch when the twist is run all the way over;
  - a grip 90 mm long, so the jaws hold the whole length of a finger
    rather than a 7 mm band of it.

The first three fix how WIDE it is, and the fourth fixes how TALL. A face
flush with a 40 mm bore that ends on the axis travels 20 mm; the cam pin
cannot sit in front of its face and its groove cannot cross the finger hole,
so the pin's inner limit is the bore plus the body wall, the turning fit, the
lip that holds it together and one wall between that and the groove -- about
r=29. The pin therefore sweeps r 29.4 to 49.4, a jaw tail reaches r=53.9 when
open, and the shell has to be outside all of it. Hence 115 mm across.

THE ONE THING THE 90 MM GRIP CHANGES, beyond height: a 90 mm blade driven by
a single pin at one end is a drawer pulled by one corner. It cocks, and it
jams. So there are TWO scroll plates -- the shell's floor and the cap -- and
each jaw has a pin at each end. The two plates turn together, so both ends of
a jaw are driven identically and there is no couple to cock it.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

# ---------------------------------------------------------------------------
# the brief
# ---------------------------------------------------------------------------

BORE_D = 40.0              # the finger opening, clear and circular when open
TWIST_SWEEP = 180.0        # degrees from fully open to shut. Half a turn is
                           # one wrist movement, and it also makes the two cam
                           # grooves tile the face exactly -- see scroll.py.
JAW_COUNT = 2
GRIP_L = 90.0              # how much of a finger the jaws hold

JAW_TRAVEL = BORE_D / 2.0  # 20.0 -- derived, never set: it IS the bore radius

# ---------------------------------------------------------------------------
# print tolerances
# ---------------------------------------------------------------------------

FIT_SLIDE = 0.35           # faces that slide across each other in use
FIT_TURN = 0.35            # the rotating bearing between shell and body
FIT_FREE = 0.30            # faces that only need to not touch
WALL_MIN = 1.6             # thinnest wall anywhere -- four 0.4 mm lines

# ---------------------------------------------------------------------------
# the cam pin and its groove
# ---------------------------------------------------------------------------

PIN_D = 5.0
GROOVE_W = PIN_D + 2 * FIT_SLIDE      # 5.7
GROOVE_DEPTH = 4.6
PIN_LEN = GROOVE_DEPTH - FIT_FREE     # 4.3, so a pin never bottoms out
GROOVE_END_CLEAR = FIT_FREE
_pad = lambda r: math.degrees((GROOVE_W / 2 + GROOVE_END_CLEAR) / r)

# ---------------------------------------------------------------------------
# the chain of walls that sets how wide it is
# ---------------------------------------------------------------------------
# Read top to bottom: every radius derives from the one above it, and the
# first is the finger. Setting any of them by hand breaks the chain and puts
# a wall somewhere at nothing. test_fit.py measures the real walls.

BODY_WALL = 3.0                                    # 90 mm of unsupported tube
                                                   # wants more than the 1.6 a
                                                   # flat plate needed
SKIRT_ID = BORE_D
SKIRT_OD = SKIRT_ID + 2 * BODY_WALL                # 46.0
RING_ID = SKIRT_OD + 2 * FIT_TURN                  # 46.7, the turning fit

LIP_OVERLAP = 1.6
LIP_R_OUT = RING_ID / 2 + LIP_OVERLAP              # 24.95
LIP_Z0 = 3.8                                       # underside of the lip

RING_INNER_WALL = WALL_MIN
R_GROOVE_IN = LIP_R_OUT + RING_INNER_WALL          # 26.55
R_PIN_IN = R_GROOVE_IN + GROOVE_W / 2              # 29.4
R_PIN_OUT = R_PIN_IN + JAW_TRAVEL                  # 49.4
R_GROOVE_OUT = R_PIN_OUT + GROOVE_W / 2            # 52.25

RING_T = 7.0                                       # the shell's floor
RING_FLOOR = RING_T - GROOVE_DEPTH                 # 2.4 under every groove

GROOVE_PAD_IN = _pad(R_PIN_IN)                     # ~6.1 deg
GROOVE_PAD_OUT = _pad(R_PIN_OUT)                   # ~3.7 deg

# ---------------------------------------------------------------------------
# the jaws -- now blades, not bars
# ---------------------------------------------------------------------------

JAW_W = 26.0                           # width across, in its slot. Two of
                                       # these cover about 160 degrees of the
                                       # bore's circumference between them,
                                       # against 80 at half the width, so a
                                       # finger is held on nearly half its
                                       # perimeter rather than a quarter.
SLOT_W = JAW_W + 2 * FIT_SLIDE         # 26.7
FACE_T = 3.5                           # thickness of the face plate itself
RIB_W = 5.0                            # the web joining the two arms
ARM_H = 6.0                            # the arms that carry the pins

PIN_OFFSET = R_PIN_IN                  # 29.4 -- the pin sits this far behind
                                       # the face, which is exactly the pin's
                                       # inner limit, because the face is on
                                       # the axis when the pin is innermost
JAW_TAIL = PIN_D / 2 + 2.0
JAW_L = PIN_OFFSET + JAW_TAIL          # 33.9
JAW_TAIL_R_MAX = BORE_D / 2 + JAW_L    # 53.9 at full open

# AND THE TAIL IS CUT TO THAT RADIUS, not left square. A blade is a
# rectangle, so its outer corners sit further from the axis than the middle
# of its end does -- at 26 mm wide that is 55.4 mm against 53.9, and the
# corners foul the shell wall at full open. Widening the shell to clear them
# would cost 3 mm of diameter for two corners nobody wants; trimming the end
# to an arc about the axis costs 1.6 mm off each corner and nothing else.
# parts.jaw() does the cut, so it follows JAW_W automatically.

# ---------------------------------------------------------------------------
# the flat-printing blade: separate dowel pins
# ---------------------------------------------------------------------------
# An ALTERNATIVE to the blade with pins moulded on. Printed flat on its face
# the blade needs no support at all -- rib and both arms rise straight off
# the face plate -- but its two pins would be horizontal cylinders hanging in
# mid-air, and the support under them lands on the one circumference that has
# to slide in a 5.7 mm groove.
#
# So the pins come off and become dowels, printed standing beside the blade,
# where a 5 mm cylinder is the most accurate thing the machine makes.
#
# The socket is a TEARDROP, not a round hole. Lying flat, the socket's axis
# is horizontal, and the roof of a horizontal round hole prints as a droop
# into the bore. A 45 degree peak over the circle is self-supporting, and the
# dowel simply ignores it.
SOCKET_DEPTH = 5.0                     # blind, so the dowel bottoms out and
                                       # sets its own protrusion
SOCKET_ROOF = 45.0                     # degrees, self-supporting
DOWEL_L = PIN_LEN + SOCKET_DEPTH       # 9.3
DOWEL_SPARES = 1                       # a jaw needs two; print three

# The press fit is the one joint in this object that can work loose -- every
# other one is a lug through a notch, a peg in a hole or a pin in a groove.
# So it gets a comb of its own: five dowels either side of nominal, and five
# real sockets to press them into.
DOWEL_TEST_D = (4.90, 4.95, 5.00, 5.05, 5.10)

# ---------------------------------------------------------------------------
# the body: a tube, not a plate
# ---------------------------------------------------------------------------

BODY_ARC_R_OUT = LIP_R_OUT - 0.15      # 24.8. The tube is thicker above the
                                       # shell's floor than the skirt below
                                       # it, and the step is the shoulder the
                                       # whole body stands on.
TOPRING_T = 3.0                        # the ring closing the top of the tube

# THE CAP'S HOOK, and why it lives in such a narrow band. The cap has to be
# held DOWN: a finger pulled out of a shut jaw drags the blades up, and they
# push on the cap. The only thing above them to hook onto is the body, and
# the only free annulus is between the body's bore and the start of the
# spiral -- 6.5 mm, which has to hold the body's own wall, two clearances,
# the hook, and a wall between the hook and the groove.
#
# The first version of this had the hook ABOVE the body's lugs, which holds
# nothing at all: lifting the cap just moves it further away. The hook goes
# UNDER them.
CAP_HOOK_R_IN = SKIRT_OD / 2 + FIT_FREE            # 23.3, clear of the neck
CAP_HOOK_R_OUT = CAP_HOOK_R_IN + WALL_MIN          # 24.9
CAP_HOOK_T = 3.0
TOP_LUG_OUT = CAP_HOOK_R_OUT - FIT_FREE            # 24.6, overlapping it
LUG_ARC = 30.0
LUG_R_OUT = LIP_R_OUT - FIT_FREE       # 24.65
LUG_H = 2.2
NOTCH_SLACK = 3.0

# WHY UNEVEN ANGLES. The lugs pass through notches to go together, and the
# shell must never find those notches again while in use. Evenly spaced lugs
# line up every 120 degrees -- including at 120, the middle of a 180 degree
# sweep, where the body would lift straight off a shut mechanism. These gaps
# are 100, 115 and 145 degrees, all different, so no turn maps the set onto
# itself and the notches are open at full open and nowhere else.
LUG_ANGLES = (0.0, 100.0, 215.0)
LUG_COUNT = len(LUG_ANGLES)

# The top set is the same pattern turned 40 degrees, to miss the two jaw
# slots at 0 and 180 -- at the top of the tube there is no material there.
TOP_LUG_ANGLES = tuple((a + 40.0) % 360.0 for a in LUG_ANGLES)

# ---------------------------------------------------------------------------
# the shell and the cap: the rotating assembly
# ---------------------------------------------------------------------------

WALL_ID = 2 * (JAW_TAIL_R_MAX + 0.8)   # 109.4 -- clear of the jaw tails
WALL_T = 3.0
OVERALL_D = WALL_ID + 2 * WALL_T       # 115.4

FLUTE_COUNT = 28
FLUTE_D = 4.0
FLUTE_DEPTH = 1.0


# Three pegs, not a ring of teeth: the cap has to turn with the shell, and
# three pegs on the same uneven angles go together exactly one way round.
PEG_D = 5.0
PEG_H = 4.0
PEG_R = (WALL_ID / 2 + OVERALL_D / 2) / 2.0        # mid-wall

PLATE_GAP = 0.30

# ---------------------------------------------------------------------------
# the ratchet
# ---------------------------------------------------------------------------
# A clicker, and a positive lock that does not depend on friction. It lives
# ABOVE the cap because that is the only place it can: everywhere a fixed
# surface faces a turning one lower down, the gap is 0.3 mm, and the bore
# has to stay clear. Above the cap's top face there is nothing at all.
#
# A collar rises from the cap with sawteeth inside it, and a springy post
# rises from the body inside that. Turning to close walks the post's nose
# over the ramps -- click -- and the steep flank of each tooth blocks it
# turning back. Press the pad on top of the post inward and the nose comes
# off the teeth, and it twists open freely.
#
# Both pieces stand UP from parts that already print standing up, so the
# whole mechanism adds no supports and no extra part.

RATCHET_TEETH = 36                     # 10 deg a click, 1.11 mm of jaw
                                       # travel, 18 clicks over the sweep.
                                       # Not finer: the nose has to be
                                       # NARROWER than the flat bottom of a
                                       # valley or its edges ride the ramps
                                       # either side and it never rests
                                       # anywhere, and a nose much under
                                       # 1.4 mm is not worth printing.
RATCHET_DEPTH = 0.8
RATCHET_FLAT = 0.40                    # of each tooth, a flat valley at the
                                       # root. A pure sawtooth comes to a
                                       # knife edge, so the nose has no
                                       # definite place to rest and sits
                                       # part-way up a ramp wherever it
                                       # stops -- preloaded, rattling, and
                                       # impossible to model as a part that
                                       # is not interfering with another.
COLLAR_R_ROOT = CAP_HOOK_R_OUT         # 24.9, the valley the nose sits in
COLLAR_R_CREST = COLLAR_R_ROOT - RATCHET_DEPTH     # 24.1, what blocks it
COLLAR_R_OUT = 26.6
COLLAR_H = 9.5

PAWL_ANGLE = -50.0                     # clear of the top lugs and the slots
POST_R_IN = 22.9
POST_R_OUT = 23.9                      # 0.2 inside the crests, so only the
POST_W = 3.4                           # nose ever touches a tooth
POST_BOSS_R_OUT = 24.0                 # the pad on the top ring it stands on
POST_BOSS_ARC = 14.0
NOSE_R = 24.70                         # just inside the valley floor
NOSE_W = 1.4                           # narrower than a valley's flat, which
                                       # is 1.73 mm of arc at this radius
NOSE_H = 3.0
PAD_T = 3.0
PAD_W = 9.0                            # the pad is wide, not deep: anything
                                       # standing further out than the post
                                       # stops the collar being lowered over
                                       # it, and the thing would not go
                                       # together at all

# The post is a cantilever and its length is the only thing setting how hard
# the click is. 1.0 mm thick and 3.4 wide, a nose about 8 mm up needs
# roughly 2 N to push aside -- a firm click rather than a vague one. Shorten
# it and the force climbs with the cube.

# ---------------------------------------------------------------------------
# the stack, as a function of how long the grip is
# ---------------------------------------------------------------------------
# Heights are a function, not constants, so a short-grip prototype is the
# same object with one argument changed rather than a second model.


def stack(grip_l: float = GRIP_L) -> SimpleNamespace:
    jaw_0 = RING_T                              # jaws ride on the shell floor
    jaw_top = jaw_0 + grip_l
    cap_0 = jaw_top + PLATE_GAP                 # the cap sits on the shell
    cap_hook_1 = cap_0 + CAP_HOOK_T
    topring_0 = cap_hook_1 + FIT_FREE           # the body's top ring, ABOVE
    topring_1 = topring_0 + TOPRING_T           # the hook that holds the cap
    cap_top = topring_1 + 0.5
    collar_0 = cap_top
    collar_1 = collar_0 + COLLAR_H
    nose_1 = collar_1 - 0.6                     # the nose stays in the teeth
    post_top = collar_1 + 0.9 + PAD_T
    return SimpleNamespace(
        grip_l=grip_l,
        ring_0=0.0,
        ring_top=RING_T,
        jaw_0=jaw_0,
        jaw_top=jaw_top,
        pin_bot_0=jaw_0 - PIN_LEN,              # bottom pin, into the floor
        pin_top_1=jaw_top + PIN_LEN,            # top pin, into the cap
        groove_floor=RING_FLOOR,
        arc_top=jaw_top,                        # the thick tube ends here
        topring_0=topring_0,
        topring_1=topring_1,
        wall_top=cap_0,
        cap_0=cap_0,
        cap_hook_1=cap_hook_1,
        cap_top=cap_top,
        collar_0=collar_0,
        collar_1=collar_1,
        nose_0=nose_1 - NOSE_H,
        nose_1=nose_1,
        post_top=post_top,
        lug_z1=LIP_Z0 - FIT_FREE,
        lug_z0=LIP_Z0 - FIT_FREE - LUG_H,
        overall_h=post_top,
    )


STACK = stack()

# ---------------------------------------------------------------------------
# materials and the machine -- see ../available-tools.md
# ---------------------------------------------------------------------------

BED = (325.0, 320.0)
NOZZLE = 0.4
LAYER = 0.2

# Every render uses these, so a part is the same colour wherever you see it.
# All four are filament actually on the shelf -- see ../available-tools.md.
#
# These are RENDER colours, not swatches. Flat shading multiplies a colour by
# a shade factor that is always under 1, so a colour entered at its true
# value only ever comes out darker than the filament -- a milky pink lands on
# mauve. Each of these is the filament lifted to survive that.
COL_SHELL = (0.96, 0.97, 0.95)         # jade white / PETG white
COL_BODY = (0.055, 0.07, 0.085)        # black
COL_JAW = (1.00, 0.74, 0.82)           # PLA Pure, milky pink
COL_CAP = (0.20, 0.38, 0.70)           # blue / PETG reflex blue
COL_CUT = (0.62, 0.64, 0.68)

DEG = math.pi / 180.0
