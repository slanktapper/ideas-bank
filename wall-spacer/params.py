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
    Z   up. Z = TOP is the flat top plane: the top chords, the saddle bridge
        and nothing else, all at one level. The tower hangs below it and
        narrows to a single chord at the bottom.

The section is a TRIANGLE: two chords along the top, one along the bottom.
That is the shape of the tower in the reference photograph, and it is also
what makes the part printable upside down -- see direction.md, "Why it
prints upside down".
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

# --- the tower --------------------------------------------------------------

WIDTH     = 40.0         # asked for. It is also the width of the TOP face:
                         # the two top chords sit on Y = 0 and Y = WIDTH, and
                         # the bottom chord runs up the middle at Y = WIDTH/2.

D_BASE    = 38.0         # how far the tower hangs below the top plane at the
                         # lip end, and D_TIP at the far end. Free to taste:
                         # the load is axial, so depth buys stiffness the
                         # part does not especially need. What it does buy is
                         # the side faces' slope -- see build.py's overhang
                         # check, which is why these two are not arbitrary.
D_TIP     = 28.0         # The top plane stays flat and the bottom chord
                         # rises, so the taper is one-sided. A symmetric
                         # taper would be more like a real tower and would
                         # also tilt the top plane, which is the one thing
                         # that has to stay flat.

BAYS      = 5            # X-braced bays along the span, in all three faces.
                         # Five over 123 mm gives 24.6 mm bays. That pitch is
                         # also how far the bottom chord has to bridge
                         # between nodes when the part is printed, so it is
                         # not only a question of looks.

CHORD_T   = 4.0          # the two top chords, square, their outer faces
                         # flush with Y = 0, Y = WIDTH and Z = TOP
CHORD_B   = 5.0          # the bottom chord. Bigger than the top two because
                         # it is the only member that is nearly horizontal
                         # when the part is printed, so it is the only one
                         # that bridges. Set as a DIAMOND -- see build.py.
BRACE_T   = 3.0          # the diagonals, in all three faces
BELT_T    = 3.0          # the transverse members at each bay boundary. One
                         # in each face, so each bay boundary is a complete
                         # triangular ring -- which is also what pins the
                         # bottom chord every 24.6 mm while it prints.

PAD_T     = 4.5          # the two bearing pads, at X = 0 and X = SPAN. Solid
                         # triangular plates filling the whole section: these
                         # are the faces that actually push on something, so
                         # they are the one place a lattice would be wrong.

# --- the saddle -------------------------------------------------------------

LEG_T     = 5.0          # thickness of the outer leg
BRIDGE_T  = 5.0          # the bridge over the top of the lip. Its top face
                         # is in the top plane with everything else, so the
                         # lip's top edge seats BRIDGE_T below that plane.
LEAD_IN   = 2.5          # chamfer up the inside bottom corner of the leg, so
                         # the saddle finds the lip instead of catching on it

THROAT    = LIP_T + LIP_CLEAR            # 13.5 -- the slot the lip sits in
LEG_X     = THROAT + LEG_T               # 18.5 -- how far the part reaches
                                         # behind the lip's near face
TOP       = D_BASE                       # Z of the flat top plane
SEAT      = TOP - BRIDGE_T               # Z of the lip's top edge

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

OVERHANG_MIN = 40.0          # degrees from horizontal. A downward-facing
                             # face shallower than this needs support. 40
                             # rather than the usual 45 for one reason: the
                             # bottom chord is a diamond, so its two lower
                             # faces sit at exactly 45 and a 45 threshold
                             # would be deciding the check on a rounding
                             # error.
