# wall-spacer — print guide

Read this before slicing. The part is easy to print and easy to print in
the wrong orientation, and the orientation is the whole design.

## The files

| File | What it is |
| --- | --- |
| `stl/wall-spacer-print.stl` | **print this one.** Already upside down on the bed, sitting on Z = 0. |
| `stl/wall-spacer.stl` | the same part the right way up, in the frame it is *fitted* in — lip at X = 0, top plane up. Matches the renders and `direction.md`. Do not print it without flipping it. |

Both are the same solid. There are two only so that nobody has to work out
the flip from a photograph.

## Orientation — the one thing that matters

**It prints upside down.** The flat top plane — the two top chords, the
lacing between them and the saddle bridge, all finishing at exactly the same
level — goes face down on the bed, and the tower builds upwards, narrowing
to the single bottom chord at the top. `renders/06-on-the-bed.png` is what
it should look like in the slicer.

Get that right and there is nothing else to think about. A shape that
narrows as it rises has nothing to support, and **no supports are needed
anywhere**: `build.py` checks that 0.00 mm² of the part faces downwards at
less than 40° from horizontal in this orientation.

Get it wrong — the right way up, or on a side — and the slicer will want
supports through all five bays of all three faces, through the saddle
throat, and under a bottom chord that is then a 123 mm ceiling.

    bed footprint   3399 mm2 of contact, most of it the solid saddle bridge
    height          38.0 mm
    supports        none

The one thing the printer does have to do is **bridge**. The bottom chord is
pinned at every bay boundary, where the belts of all three faces meet it in
a complete ring, and between those it bridges **24.6 mm**. That is an
ordinary distance, and because the chord is set as a diamond it bridges from
a single line rather than from a flat face. If the slicer has a bridge-flow
setting, leave it on.

## Material

**PETG Basic**, from `../filament.md`.

PETG rather than PLA for one reason: this part sits under a steady sideways
push for years, and **PLA creeps under sustained load at room temperature**.
It would work for a month and be 2 mm shorter by the spring. PETG does not
do that, and it is the functional default on the shelf anyway.

**Black** is in stock, and the part is invisible in the gap. If the tower is
to be taken seriously, **orange PETG** is also in stock and is the nearest
thing on the shelf to an aviation obstruction marking. There is **no red
PETG** — the reds are PLA, and PLA is the wrong material here, so the
red-and-white tower in the reference photo is not on the table.

## Settings

Nothing exotic. 0.4 nozzle, 0.2 mm layers.

| | |
| --- | --- |
| Walls | **3** — the members are 3–5 mm, so three walls makes most of them solid, which is what is wanted |
| Top/bottom | 4 each |
| Infill | 20%, gyroid. There is very little of the part that is not wall. |
| Supports | **none** |
| Brim | **5 mm.** The bed contact is good but it is spread along 141 mm, and the saddle end is much heavier than the far end. A brim costs minutes. |
| Bridging | leave the slicer's bridge detection and flow on, for the bottom chord |
| Elephant's foot | leave the compensation on. The bed face *is* the top plane of the finished part, and it is the face that sits level with the lip. |
| Seam | aligned or rear. Random seams on twenty small loops per layer is twenty blobs per layer. |

Roughly **30 g and an hour**, which the slicer will put a real number on.
32.2 cm³ is the *solid* volume; walls and infill come in under that.

## Fitting it

1. **Check the lip first.** The throat is 13.5 mm and the model assumes a
   12.7 mm board. Anything from about 11.5 to 13.4 mm goes on. Thicker than
   13.4 and it does not — change `LIP_T` in `params.py` and re-run.
2. **Check there is 14 mm of clear board behind the lip** for the outer leg.
   The photograph says void; the photograph has been wrong before. If there
   is less, drop `LEG_DROP`.
3. Drop the saddle over the lip. The lead-in chamfer on the inside of the
   outer leg means it should find the board rather than catch on it.
4. Push the cabinet back against it. The far pad is a solid triangle 4.5 mm
   thick and 28 mm deep, and should land flat on whatever is across the gap.
5. **Then look at whether one is enough.** A single strut in the middle lets
   the cabinet skew about it. Two, one towards each end, do not.

## If the first one is wrong

Everything is in `params.py` and everything is derived from it. The numbers
most likely to need moving, in the order they are likely to need it:

    LIP_T       the lip turns out thicker or thinner than 12.7
    LEG_DROP    there is less room behind the lip than the photo suggested
    SPAN        the far face is recessed, or there is a skirting in the way
    CHORD_T     it flexes -- raise the chords before raising the depth
    CHORD_B     with CHORD_T; it is also what bridges, so raising it is safe

Change one, re-run `python3 build.py`, and both STLs and all eight renders
move together. The overhang check runs every time, so if a change quietly
makes the part need supports, the build will say so rather than the printer.
