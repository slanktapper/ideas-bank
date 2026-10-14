"""Every dimension the piano clip is built from, in one place.

Two coordinate worlds live here and they must not be confused:

  * ``*_REAL`` names are the actual Korg in Rob's workshop, in millimetres.
  * everything else is the printed miniature, also in millimetres.

``SCALE`` is the only bridge between them. It is set so that **one millimetre
of model is one inch of piano** -- the cabinet is 48 in wide and the model is
48 mm wide. That is not a coincidence chosen to be cute; it is chosen because
it makes every number here checkable in your head against the tape measure.

Model axes:   +X right (along the keyboard)   +Y back   +Z up
Origin:       centre of the cabinet in X and Y, cabinet underside at Z = 0.
"""

# ---------------------------------------------------------------------------
# The real piano -- Korg Concert C-600
# ---------------------------------------------------------------------------
# Width and depth are Rob's tape measure: 48 in x 16 in.
WIDTH_REAL = 48 * 25.4          # 1219.2 mm
DEPTH_REAL = 16 * 25.4          #  406.4 mm

# The keyboard was counted off the photograph rather than guessed. Detecting
# dark runs across the key bed found 31 black keys in the correct 3-2-3-2
# pattern, opening on a group of three and closing on a single. That is E1-G7:
# 76 keys, 45 white. An 88-key bed is 1220 mm on its own and could not fit a
# 1219 mm cabinet, which is the independent check that this is right.
N_WHITE = 45
N_BLACK = 31
WHITE_W_REAL = 165.0 / 7        # 23.571 mm -- an octave is 165 mm, always
KEYBED_W_REAL = N_WHITE * WHITE_W_REAL      # 1060.7 mm
BLACK_W_REAL = 9.5              # standard sharp width
BLACK_LEN_FRAC = 0.62           # black key length as a fraction of white

# ASSUMED, not measured -- Rob gave width and depth only. 280 mm is the case
# alone (lid down to the underside of the key slip), not floor-to-lid; the
# stand is deliberately not modelled. If this is wrong the model gets taller
# or shorter and nothing else changes.
CASE_H_REAL = 280.0

# Front-to-back breakdown of the case top, back edge first. These sum to
# DEPTH_REAL and are read off the photograph's proportions.
LID_D_REAL = 180.0              # flat lid the music rest stands on
PANEL_D_REAL = 50.0             # control strip carrying the KORG logo
KEYS_D_REAL = 145.0             # visible white key length
SLIP_D_REAL = 31.4              # key slip at the front
LID_DROP_REAL = 28.0            # lid top down to the control strip
KEYS_DROP_REAL = 10.0           # control strip down to the key tops

# The music rest: smoked translucent acrylic in a black base trough. Width and
# height are scaled off the photograph against the known cabinet width.
# THICKNESS IS PROVISIONAL -- see direction.md. It is the one number the spring
# preload depends on, and it was measured at a glancing angle.
MREST_W_REAL = 660.0
MREST_H_REAL = 250.0
MREST_T_REAL = 6.2              # inferred, see GRIPPED_T below -- not measured
                                # directly. Only the model's looks use this;
                                # the clip is sized from GRIPPED_T instead.
MREST_TILT_DEG = 12.0           # leans back off vertical
MREST_BASE_D_REAL = 40.0
MREST_BASE_H_REAL = 12.0
MREST_Y_REAL = 90.0             # base centre, back of the lid centre line

# ---------------------------------------------------------------------------
# Scale
# ---------------------------------------------------------------------------
MINI_W = 48.0                   # the model's cabinet width, mm
SCALE = MINI_W / WIDTH_REAL     # 1 : 25.4 -- one millimetre per inch

def s(real_mm: float) -> float:
    """Real piano millimetres -> model millimetres."""
    return real_mm * SCALE

# ---------------------------------------------------------------------------
# What the printer can actually resolve
# ---------------------------------------------------------------------------
# A 0.4 mm nozzle lays a 0.42 mm line. Anything thinner than one line either
# vanishes or prints as a ragged bead, so three features here are deliberately
# fatter than scale. Each one is a lie about the piano, told on purpose, and
# the size of the lie is recorded so it can be argued with.
NOZZLE = 0.4
MIN_FEATURE = 0.5               # one confident line

#   black keys  0.374 mm at scale -> 0.55 mm   (1.47x over scale)
#   music rest  0.177 mm at scale -> 1.20 mm   (6.77x over scale)
BLACK_W_MIN = 0.55
MREST_T_MIN = 1.20

# ---------------------------------------------------------------------------
# The clip
# ---------------------------------------------------------------------------
# Two blades hanging under the cabinet that saddle the music rest with the
# dust sheet draped over it. Both faces of the rest carry fabric, so nothing
# the clip touches is bare acrylic -- which is why there are gripping ribs on
# both inner faces and no worry about scratching.
GRIP_DEPTH = 25.0               # Rob's number: how far it reaches down
LEG_T = 1.2                     # blade thickness -- 3 perimeters at 0.4 mm
LEG_W = 44.0                    # narrower than the cabinet, so it tucks under
FABRIC_T = 0.30                 # one layer of cotton bedsheet
PRELOAD = 1.00                  # how far each blade is sprung open in use

# MEASURED, 2026-10-14 MDT. Rob pinched the music rest through the dust sheet
# and read the gap between his fingers: 7 mm. That is the whole stack -- the
# acrylic plus both layers of cloth, compressed about as much as a clip will
# compress it -- so it is exactly what the blades have to swallow, with no
# inference in between.
#
# It also corrects this file's first guess. The acrylic was estimated at
# 4.5 mm off a photograph taken at a glancing angle, which made the stack
# 5.1 mm. The real figure is 1.9 mm fatter. A direct measurement of the thing
# being gripped beats a photogrammetric estimate of one of its parts, which is
# why nothing downstream reads MREST_T_REAL any more.
GRIPPED_T = 7.0

# Gap between the blades at rest. Sized so that fitting it over the stack
# springs each blade out by PRELOAD.
SLOT_GAP = GRIPPED_T - 2 * PRELOAD

# A ladder of preloads for the fit coupons, so the grip can be chosen by
# feel on the real music rest rather than argued about here.
COUPON_PRELOADS = (0.6, 1.0, 1.4)

LEG_ROOT_FILLET = 1.2           # kills the stress riser where blade meets case
LEG_FLARE = 1.6                 # lead-in at the tips so it feeds over fabric
LEG_FLARE_H = 3.0
RIB_COUNT = 3                   # gripping ribs across each inner face
RIB_H = 0.35
RIB_D = 0.8

# ---------------------------------------------------------------------------
# Material -- PLA Basic, three colours, all in stock per filament.md
# ---------------------------------------------------------------------------
# Rob asked for a brown body. There is no brown PETG: the only brown on the
# shelf is PLA Basic Cocoa Brown 10802. That forces the whole part to PLA,
# which matters because PLA creeps under sustained load and this part is a
# spring held open for months. The blades are sized for low strain to buy that
# back -- see the creep check in build.py.
COL_BODY = (0.282, 0.192, 0.145)    # PLA Basic Cocoa Brown 10802
COL_WHITE = (0.941, 0.945, 0.925)   # PLA Basic Jade White
COL_BLACK = (0.102, 0.106, 0.118)   # PLA Basic Black

# PLA, printed, along the layer plane. Deliberately conservative.
E_PLA = 2500.0                  # MPa
STRAIN_LIMIT = 0.005            # 0.5 %, the long-term-under-load figure
