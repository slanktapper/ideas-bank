"""Dimensions for the wall spacer.

Every number the part depends on lives here. Anything marked MEASURED came
off the photograph with a calibrated tape; PROVISIONAL has not been checked
in the hand yet -- see direction.md.

Coordinate frame, used by build.py, the renders and the print guide. This is
the frame the part SITS IN, not the frame it prints in:

    X   across the gap. X = 0 is the near face of the lip -- the face looking
        into the gap -- and X grows away from it, so the far side of the gap
        is at X = SPAN. The hook's outer leg lives at negative X, behind the
        lip.
    Y   the part's width, 0 .. WIDTH. Horizontal, along the lip.
    Z   up. Z = 0 is the bottom of the tower at the lip end. Z = SEAT is the
        top edge of the lip, the surface the saddle sits down onto.

The profile is constant in Y: the whole part is one 2D shape in X-Z extruded
WIDTH millimetres. That is not a modelling convenience, it is the print
strategy -- see direction.md, "Why it is an extrusion".
"""

# --- the gap and the lip, measured ------------------------------------------

SPAN      = 123.0        # MEASURED by Rob with a tape, and the number the
                         # part exists to hold. Corroborated off the
                         # photograph: calibrating on the tape's own
                         # millimetre ticks (19.86 px/mm) puts the near face
                         # of the lip at 124.1 mm, 1.1 mm from Rob's reading
                         # and well inside what a tape hooked over an edge
                         # and photographed at an angle can resolve. Rob's
                         # number wins; the photo only says it is not a typo.

LIP_T     = 12.7         # MEASURED off the photograph: the lip is a board
                         # standing on edge and the tape crosses its top
                         # square-on, so the reading is a true thickness and
                         # not a foreshortened one. Straightened and sampled
                         # at six rows above the tape it reads 11.9-12.4 mm,
                         # so this is called at 1/2 inch nominal and rounded
                         # UP: the throat is sized from it, and a throat that
                         # is slightly wide rattles while one that is
                         # slightly narrow will not go on at all.

LIP_CLEAR = 0.8          # throat clearance, all of it on the OUTER side. The
                         # inner wall of the throat is the bearing face at
                         # X = 0, so the strut always sits flush against the
                         # lip and the slop lives where it costs nothing.
                         # Takes a lip from 11.9 (measured low) to 12.7.

LEG_DROP  = 14.0         # PROVISIONAL. How far the outer leg hangs down the
                         # back of the lip. The photograph shows open void
                         # behind the board, so this is about engagement
                         # rather than clearance -- enough to stay hooked if
                         # the strut is nudged, short enough not to foul
                         # anything that turns out to be down there.

# --- the part ---------------------------------------------------------------

WIDTH     = 40.0         # asked for

H_BASE    = 34.0         # tower depth at the lip end. Free to taste: the
                         # load is axial, so depth buys stiffness the part
                         # does not especially need. It buys the tower its
                         # silhouette, which is why it is here at all.
H_TIP     = 24.0         # depth at the far end. The top chord stays straight
                         # and the bottom chord rises, so the taper is
                         # one-sided. A symmetric taper would drop the far
                         # bearing pad to mid-height, and the only thing
                         # known about the far side of the gap is that there
                         # is material at the level the tape was stretched
                         # across -- which is the level of the lip's top
                         # edge. Keeping the top chord straight keeps the
                         # bearing pad up there with it.

SEAT      = H_BASE       # Z of the lip's top edge: the tower hangs from it

CHORD_T   = 4.0          # the two chords
BRACE_T   = 3.0          # the diagonals
BELT_T    = 3.0          # the uprights between bays
PAD_T     = 4.5          # the two bearing pads, at X = 0 and X = SPAN. These
                         # are the faces that actually push on something, so
                         # they are the full depth of the tower and thicker
                         # than a chord.

BAYS      = 5            # X-braced bays along the span. Five over 123 mm
                         # gives 24.6 mm bays, which at this depth is close
                         # to the square bay a real lattice tower uses.

# --- the saddle -------------------------------------------------------------

LEG_T     = 5.0          # thickness of the outer leg
BRIDGE_T  = 5.0          # the bridge over the top of the lip. This is the
                         # only thing carrying the part's weight, and it
                         # carries it in bending over a 13.5 mm throat, so it
                         # is a chord and a quarter rather than a chord.
LEAD_IN   = 2.5          # chamfer up the inside bottom corner of the leg, so
                         # the saddle finds the lip instead of catching on it

THROAT    = LIP_T + LIP_CLEAR            # 13.5 -- the slot the lip sits in
LEG_X     = THROAT + LEG_T               # 18.5 -- how far the part reaches
                                         # behind the lip's near face
H_TOT     = SEAT + BRIDGE_T              # 39.0 -- overall height

# --- print ------------------------------------------------------------------

MATERIAL  = "PETG Basic"     # see ../filament.md. PETG rather than PLA for
                             # one reason: this part sits under a steady push
                             # for years, and PLA creeps under sustained load
                             # at room temperature. Black is in stock and the
                             # part is invisible in the gap; orange is also in
                             # stock and is the closest thing on the shelf to
                             # an aviation obstruction marking, if the tower
                             # is to be taken seriously. There is no red PETG.
NOZZLE    = 0.4
LAYER     = 0.2

MIN_FEATURE = 3 * NOZZLE     # 1.2 -- nothing in the part may be thinner

FILLET    = 0.8          # radius put into every internal corner of the
                         # lattice. Half housekeeping, half engineering: it
                         # is what unpinches the joints where two members
                         # meet at a single point (see build.py), and a
                         # filleted node is also where a braced frame stops
                         # cracking first.
