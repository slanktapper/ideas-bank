"""Dimensions for the VKB T-Rudder Mk.V foot rest end cap.

Every number the part depends on lives here. Anything marked PROVISIONAL has
not been confirmed with a caliper yet -- see direction.md.

Coordinate frame, used by build.py and by the print guide:

    Z   along the extrusion axis. Z = 0 is the mating face, the one that sits
        against the aluminium end face. Z grows away from the pedal.
    X   across the extrusion width. X = 0 is the centreline.
    Y   through the extrusion depth. Y = 0 is the back (the side the pedal arm
        is on), Y = EXT_DEPTH is the ribbed face the foot touches, and the lip
        carries on to Y = EXT_DEPTH + LIP_H.

The part is the same at both ends of the extrusion and on both pedals: rotate
it 180 deg about Y and the lip still points away from the foot rest. One STL,
printed four times.
"""

# --- the hardware -----------------------------------------------------------

HOLE_PITCH = 39.0        # measured, caliper, +/- 0.5
EXT_DEPTH  = 15.0        # measured -- "A". Deepest point, at the crown.
EXT_WIDTH  = 52.0        # measured -- "B".

CROWN      = 4.0         # PROVISIONAL. The foot face is not flat: it is
                         # crowned across the width, clearly so in the photo
                         # but not measurably -- tracking the line of rib
                         # ends gave 28 px of noise on a 740 px chord, which
                         # is not a measurement.
                         #
                         # It matters less than it looks. The lip is a
                         # full-width wall standing 25 mm above the crown, so
                         # the cap is solid from the back face all the way up
                         # and the curve never becomes a surface of the part.
                         # It survives here only because the two numbers
                         # below are derived from it.

EDGE_DEPTH = EXT_DEPTH - CROWN
                         # depth at the side edges, where the bosses live

BOSS_Y     = EDGE_DEPTH / 2.0
                         # PROVISIONAL, and the one that matters. Assumes the
                         # tapped boss is centred in the corner lobe, and the
                         # lobe is a circle of diameter EDGE_DEPTH sitting on
                         # the flat back. That is consistent with the ~9.5 mm
                         # lobe measured off the photograph, but consistency
                         # is not confirmation: get this wrong and the cap
                         # does not bolt on at all.

# --- the bolts --------------------------------------------------------------

BOLT_D     = 5.0         # M5
BOLT_LEN   = 16.0        # what Rob has on the shelf
HEAD_D     = 10.0        # measured with calipers. The head is DOMED -- a
                         # button or pan head, not the flat-topped socket cap
                         # this was first drawn for. Measured off a photo
                         # against a tape it reads nearer 9 mm, but a caliper
                         # beats a blurred photograph and a clearance pocket
                         # is the right place to err large.
HEAD_H     = 5.0         # PROVISIONAL. The photo puts the dome at about
                         # 4.7 mm. Overstating it is safe: the counterbore
                         # floor is fixed at GRIP, so a shorter head simply
                         # sits deeper and the bolt still gets its 7 and 9.
ENGAGE_MIN = 1.5 * BOLT_D    # 7.5 mm, the usual minimum into aluminium

GRIP       = 7.0         # bolt length spent inside the cap; the rest threads
                         # into the boss. 7 + 9 = 16, and 9 > 7.5.
HEAD_SINK  = 1.0         # how far below the outer face the head finishes

CLEAR_D    = BOLT_D + 0.6    # 5.6, a free-fit hole for an M5 shank
CBORE_D    = HEAD_D + 1.0    # 11.0. Wider clearance than a cap head would
                             # get, for two reasons: a domed head has to drop
                             # in freely rather than slide down a matching
                             # bore, and FDM prints holes undersize. The back
                             # of the bore is open anyway (see OPEN_BACK), so
                             # the tenths no longer come off a wall that
                             # cannot afford them -- only off CAP_W, which
                             # has room.

# --- the cap ----------------------------------------------------------------

MIN_WALL   = 1.2         # least material allowed beside a counterbore

WALL_SLACK = 0.1         # so MIN_WALL is genuinely met, not just touched

LIP_H      = 25.0        # how far the lip stands proud of the ribbed face
CAP_L      = GRIP + HEAD_H + HEAD_SINK   # 13.0, along the extrusion axis

CAP_W      = max(EXT_WIDTH,
                 HOLE_PITCH + CBORE_D + 2 * MIN_WALL + 2 * WALL_SLACK)
                         # The cap is normally just as wide as the extrusion.
                         # It gets wider only if the counterbores would
                         # otherwise come too close to the side edge: the
                         # bolts sit 19.5 mm out, so a 9.2 mm bore leaves
                         # 0.9 mm of edge on a 50 mm face, and 0.9 mm is two
                         # perimeters. Deriving the width instead of fixing
                         # it means this re-solves itself when EXT_WIDTH is
                         # finally measured.

CBORE_WALL_BACK = BOSS_Y - CBORE_D / 2.0
OPEN_BACK  = CBORE_WALL_BACK < MIN_WALL
                         # Whether the counterbore is left open at the back.
                         #
                         # With BOSS_Y at 5.5 and a 10 mm head, a closed bore
                         # leaves 0.15 mm of material behind it -- a third of
                         # an extrusion width, which no slicer will produce.
                         # The alternatives were to push the cap 1.15 mm
                         # behind the extrusion, where the pedal arm is and
                         # nothing has been measured, or to drop the
                         # counterbore and let the heads stand proud.
                         #
                         # Opening the pocket costs nothing real. The head is
                         # 5.0 mm in radius and the back face is BOSS_Y away,
                         # so the head itself never reaches it: the only
                         # thing removed is clearance air and that 0.15 mm
                         # skin. The head's full bearing ring on the
                         # counterbore floor survives, and build.py checks
                         # that rather than assuming it.
                         #
                         # Derived, so a real BOSS_Y of 6.65 or more closes
                         # the bore again with no other change.

R_BACK     = 2.0         # Corner radius at the back edge of the XY profile.
                         # The aluminium's own lobes are rounder than this --
                         # about EDGE_DEPTH/2 -- but a radius that large
                         # sweeps into the counterbore wall, so the cap is
                         # left very slightly fuller than the extrusion at
                         # the two back corners. They face away from the foot.
R_TIP      = 8.0         # corner radius at the lip tip -- the corner a foot
                         # actually meets, so it is the generous one

CH_MATE    = 1.0         # chamfer around the Z = 0 face. Does two jobs: keeps
                         # elephant's foot off the mating face, and takes the
                         # sharp edge off the surface the foot slides into.
CH_OUTER   = 0.0         # chamfer around the Z = CAP_L face -- deliberately
                         # none. That face is the one the counterbores open
                         # through, and with the boss only BOSS_Y from the
                         # back there is 1.4 mm of wall beside a head. A 1 mm
                         # chamfer takes it to 0.4 mm, which is less than one
                         # perimeter. The edge it leaves sharp faces away
                         # from the foot, so it costs nothing.

# --- print ------------------------------------------------------------------

GAUGE_LAYERS = 4
GAUGE_T    = GAUGE_LAYERS * 0.2
                         # The alignment gauge: the cap's own silhouette, four
                         # layers thick. It answers the question the cap
                         # cannot be wrong about -- where the bolt centres sit
                         # relative to the flat back -- for about a gram.
GAUGE_ENGRAVE = 0.4      # two layers, so the label leaves two layers of floor

MATERIAL   = "PETG Basic"    # see ../filament.md; black and white are in stock
NOZZLE     = 0.4
LAYER      = 0.2
