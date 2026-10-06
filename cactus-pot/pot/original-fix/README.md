# original-fix

The pot this project started from, and the one thing that was done to it before
it was replaced.

Rob supplied a downloaded model — a tapered pot reading *Eleanor Shellstrop's
File* on the wall — and the middle line of it was badly set: the baseline sagged
8.16 mm across the word, and it wrapped 156.6° of the circumference against 94°
and 52° for the lines above and below it. `fix.py` re-sets that one line.

The trick is that it does not re-typeset anything. A thin band of revolved solid
is cut by the pot, which leaves one watertight body per glyph — the pot's own
letterforms, in whatever typeface the original used. Those 12 bodies are
measured, the band they came out of is packed flush (it holds nothing but that
word), and they are re-laid-out level, centred and tracked to a 106 mm span
before being cut back in.

`lettering-before-after.png` and `lettering-unwrapped.png` are the result: the
same camera on both, and the wall unrolled flat so the sag is visible as a
curve rather than something to take on trust.

## The mesh is not here

The source is someone else's model, so this folder does not carry a copy of it
or of the fixed version — same call `../../reference/README.md` makes for the
cactus half. The fixed STL lives on the project share with the renders.

    SOURCE_POT_STL='/path/to/Good Place Cactus (Pot).stl' python3 fix.py 106

## Why it was superseded

The fix was sound and the word reads straight now, but the panel it sits on is
not flat: it is a constant-radius cylinder, so a 106 mm line turns through 132°
and the ends rake away from anyone looking at the front. That is a property of
the body, not of the lettering, and it is why `../build.py` exists — the pebble
pot puts the name on a patch of bare cylinder of a single radius, where every
line wraps the same amount and the widest line is 68 mm rather than 106.

A round pot cannot carry a genuinely flat panel at this size: a 78 mm chord on a
Ø92 body sinks 21.6 mm from the surface, and the well's inner wall is only
3.2 mm in — the flat would cut straight through it. That was measured,
offered as a choice, and Rob kept the round body.
