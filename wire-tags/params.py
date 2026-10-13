"""Every dimension of a wire tag, and the arithmetic that derives the rest.

The cable diameter is the input.  Nothing else about the tag is fixed
independently of it: the bore, the mouth the cable snaps through, the plate
width and the height of the clip all fall out of `plan()`, so asking for a
6 mm tag gives a 6 mm tag rather than a 4 mm tag with a bigger hole in it.
"""
from __future__ import annotations

# ---------------------------------------------------------------- the machine
LAYER_H   = 0.20      # the layer height print-guide.md assumes
NOZZLE    = 0.40
BED       = (325.0, 320.0)   # H2D, single nozzle

# ------------------------------------------------------------------ the plate
PLATE_T   = 2.40      # plate thickness; the label face is the bed face
PLATE_MIN = 34.0      # shortest tag that still reads as a tag
PLATE_MAX = 56.0      # ...and the longest, before it becomes a flag
EDGE      = 1.60      # clear margin between lettering and the plate edge

# ---------------------------------------------------------------- the letters
TEXT_H    = 0.60      # recess depth = height of the lettering part (3 layers)
CAP_H     = 5.60      # glyph cap height, shrunk to fit a long word
CAP_MIN   = 3.40      # ...but never below this; it stops being readable
TRACK     = 0.00      # extra letter spacing, mm per gap

# ------------------------------------------------------------------- the clip
WALL      = 1.60      # clip wall; four 0.4 perimeters, no infill
CLIP_H    = 8.00      # how much of the cable each clip holds
CLIP_GAP  = 1.20      # clear plate between a clip and the end of the tag
FIT       = 0.30      # bore = cable + FIT.  FDM holes print undersize; this
                      # is the starting guess the fit coupon exists to correct.
MOUTH_K   = 0.82      # mouth width as a fraction of the bore.  The cable has
                      # to spread the arms by (cable - mouth), and about 12% of
                      # the cable diameter is as far as a 1.6 mm PETG arm wants
                      # to go; 0.74 asked for 21% and would have crazed them.
MOUTH_MIN = 2.60      # ...but never a mouth a thin cable cannot pass at all
LEAD      = 0.80      # 45 degree lead-in chamfer on each lip, radially
MOUTH_TILT= 46.0      # mouth aimed this far above horizontal, so the lower
                      # jaw is a jaw and not a shoulder.  It is also what
                      # sets the one overhang on the part: the underside of
                      # the upper lip sits at (90 - MOUTH_TILT) from
                      # vertical, so anything under 45 here needs support.
BRIDGE    = 1.60      # flat roof over the bore.  The bore is a horizontal
                      # hole: 45 degree flanks take it most of the way up and
                      # this much is left to bridge, which FDM does cleanly.
SINK      = 0.80      # how far the bore cuts into the plate, so the cable
                      # nests in a cradle and the ring is not merely tangent
RIB       = 0.25      # grip ribs standing proud of the bore wall
RIB_R     = 0.90      # ...as discs of this radius, two per clip
RIB_DEG   = 118.0     # ...at this angle either side of the mouth

# --------------------------------------------------------------- the defaults
CABLE_D   = 4.50      # USB-C, USB-A, most charge leads

# The four size bands, and what each is for.  Measure the cable; do not guess.
FAMILY = [
    (3.50, "thin charge leads, Lightning, earbuds"),
    (4.50, "USB-C, USB-A, braided phone cables"),
    (6.00, "ethernet, barrel DC, thicker USB 3"),
    (7.50, "HDMI, kettle leads, laptop bricks"),
]

# The set build.py makes with no arguments: a label and the cable it goes on.
# Every one of these is one `plan()` call, so the set is a starting point and
# not a catalogue -- `--label X --diameter N` makes any other.
STARTER = [
    ("USB-C",     4.50),
    ("USB-A",     4.50),
    ("LIGHTNING", 4.00),
    ("MICRO-B",   3.50),
    ("HDMI",      7.00),
    ("ETHERNET",  6.00),
    ("LAPTOP",    6.00),
    ("POWER",     7.50),
]

# The fit coupon steps the asked-for diameter either side of nominal.  Print
# it once per filament, push the real cable into each station, and build the
# tags at whichever station holds -- that is what FIT above is guessing at.
COUPON_STEPS = (-0.40, -0.20, 0.00, 0.20, 0.40)
COUPON_CAP   = 4.00   # cap height of the number engraved beside each station


def plan(cable_d: float = CABLE_D, label: str = "USB-C", text_len: float = 0.0):
    """Derive one tag's dimensions from the cable it goes on.

    `text_len` is the measured length of the set lettering; pass 0 and the
    plate comes out at its minimum.  The plate is sized to the text rather
    than the text squeezed into a fixed plate, because a tag that says
    LIGHTNING and a tag that says HDMI are not the same length of word.
    """
    bore  = cable_d + FIT
    rb    = bore / 2.0
    ro    = rb + WALL
    mouth = max(MOUTH_MIN, bore * MOUTH_K)
    # The plate has to be wider than the clip it carries, and wide enough that
    # the lettering is not pinched against its edges.
    width = max(2 * ro + 2.0, CAP_H + 2 * EDGE, 14.0)
    length = min(PLATE_MAX,
                 max(PLATE_MIN, text_len + 2 * (CLIP_H + CLIP_GAP) + 2 * EDGE))
    # Cable centre, measured from the bed face of the plate.
    zc = PLATE_T + rb - SINK
    return {
        "label": label,
        "cable_d": cable_d,
        "bore": bore, "r_bore": rb, "r_out": ro,
        "mouth": mouth, "wall": WALL,
        "clip_h": CLIP_H, "clip_y": (length / 2.0 - CLIP_GAP - CLIP_H / 2.0),
        "plate_t": PLATE_T, "plate_w": width, "plate_l": length,
        "z_cable": zc, "sink": SINK,
        "text_h": TEXT_H, "cap_h": CAP_H,
    }
