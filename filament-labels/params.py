"""Every dimension of a filament label, and the filament each part prints in.

A coloured tag with the word in white. The number that matters is how deep the
white runs:

    WHITE_D   0.80 mm   the white LETTERS, 4 layers, from the printed face
    TAG_T     3.00 mm   the tag, so 2.20 mm of colour over the back of them

The white is the letters and nothing else. Everything else -- background,
edges, back, and the counter inside each P and A -- is the letter colour,
solid through all 3 mm.

WHITE_D is 0.80 rather than the 0.40 first suggested, and the reason survives
every rearrangement this design has been through, because it is about one
interface rather than about the layout. A light filament over a dark one is
the direction that ghosts, and white letters with a dark body behind them are
exactly that interface. 0.40 mm of white over black reads grey, not white. The
working minimum for a pale colour hiding a dark one is about 0.60 mm, and
bright white over black wants 0.80 mm. Printing face-down makes it worse
rather than better: the first layer is squashed into the plate texture, so in
the valleys the white is thinner than its nominal 0.20 mm. 4 layers is the
number that is safe over black, the worst of the three.

What did change is how little of it there is. The white was the whole tag,
then a skin over the whole face, and is now just the glyphs: 5.6 g down to
1.5 g for a set of three. The background no longer costs any white at all,
because the background is no longer white.
"""
from __future__ import annotations

# ---- the printer's units ---------------------------------------------------
# A 0.4 mm nozzle at Bambu's 0.20 mm default. Everything vertical below is a
# whole number of these on purpose: a feature that is not a multiple of the
# layer height gets rounded by the slicer, and a 0.8 mm skin quietly becoming
# 0.7 mm is exactly the kind of change that only shows up in the print.
LAYER = 0.20

# ---- the tag --------------------------------------------------------------
TAG_W = 80.0              # along the lettering
TAG_H = 30.0              # up the side of the bin
TAG_LAYERS = 15
TAG_T = round(TAG_LAYERS * LAYER, 6)      # 3.00 mm -- rigid, a plaque not a sticker
CORNER_R = 4.0            # rounded corners, so a bumped edge does not lift

# ---- the two filaments, through the thickness ------------------------------
WHITE_LAYERS = 4
WHITE_D = round(WHITE_LAYERS * LAYER, 6)          # 0.80 mm deep white letters
COLOUR_BEHIND = round(TAG_T - WHITE_D, 6)         # 2.20 mm of colour over them

# round() above is not fussiness, even though 15 * 0.20 happens to land on
# exactly 3.0. The tail comes and goes with the layer count -- 6 * 0.20 is
# 1.2000000000000002 and 7 * 0.20 is 1.4000000000000001 -- so a thickness that
# is clean today stops being clean the next time TAG_LAYERS is touched, and
# that tail propagates into every assertion about a layer count and into the
# STL's own coordinates.

# ---- the plate ------------------------------------------------------------
# Bambu Lab H2D, from ../available-tools.md. The DUAL-nozzle envelope is the one
# that applies: two filaments means both nozzles are in play, which costs 25 mm
# in X against the single-nozzle figure. Using 325 here would lay out a plate
# that does not fit the machine it is going to be printed on.
BED_W, BED_D = 300.0, 320.0
BED_MARGIN = 10.0         # kept clear all round, for clips and first-layer edge
TAG_GAP = 6.0             # between neighbouring tags

# ---- the lettering --------------------------------------------------------
MARGIN_X = 7.0            # clear tag each side of the widest word
MARGIN_Y = 5.0            # clear tag above and below the letters
MAX_CAP = 20.0            # a ceiling, in case a future tag is much taller

# The letters and their pockets are cut from one polygon, so their walls
# coincide exactly and no dark hairline can appear around a letter. If a slicer
# ever does leave one, grow the letters by a hair -- 0.02 mm is well under what
# a 0.4 mm nozzle resolves, and will not change how the word reads.
LETTER_GROW = 0.0

FACE = 'Outfit-Bold'      # from ../3d-tools/font

# ---- the three tags -------------------------------------------------------
# Colours are from ../filament.md and nothing else. The lettering is PLA Basic
# Jade White, which is the only pale PLA on the shelf -- there is no plain white
# PLA at all, and the white in stock is PETG.
#
# That matters more than it looks. The letter colours Rob asked for, indigo
# purple and cocoa brown, exist only in PLA; the white he asked for exists only
# in PETG. Those two cannot be the same part: available-tools.md notes that PLA
# and PETG barely bond, and leans on exactly that for breakaway supports. A PLA
# letter set into a PETG tag is a part designed to shed its lettering. So the
# whole set is PLA, and the lettering is jade white.
WHITE_FILAMENT = 'PLA Basic Jade White'

TAGS = (
    # key     word     the body colour                    filament.md says
    ('abs',  'ABS',  'PLA Basic Black'),           # bulk stock
    ('pla',  'PLA',  'PLA Basic Indigo Purple'),   # bulk stock
    ('petg', 'PETG', 'PLA Basic Cocoa Brown'),     # single spool, code 10802
)

# ---- render colours -------------------------------------------------------
# Approximations for the PNGs only. These are eyeballed from Bambu's swatches,
# not measured, and nothing is designed around them -- the filament names above
# are the spec. Do not quote these at Rob as the colour of anything.
RGB = {
    'PLA Basic Jade White':     (0.93, 0.95, 0.91),
    'PLA Basic Black':          (0.11, 0.11, 0.12),
    'PLA Basic Indigo Purple':  (0.29, 0.18, 0.42),
    'PLA Basic Cocoa Brown':    (0.44, 0.29, 0.24),
}
