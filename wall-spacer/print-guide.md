# wall-spacer — print guide

Read this before slicing. The part is easy to print and easy to print in
the wrong orientation, and the orientation is the whole design.

## The files

| File | What it is |
| --- | --- |
| `stl/wall-spacer-print.stl` | **print this one.** Already laid down the way it goes on the bed, sitting on Z = 0. |
| `stl/wall-spacer.stl` | the same part in the frame it is *fitted* in — lip at X = 0, up is up. Matches the renders and `direction.md`. Do not print it without rotating it. |

Both are the same solid. There are two only so that nobody has to work out
the rotation from a photograph.

## Orientation — the one thing that matters

The part is one profile extruded 40 mm, and it goes on the bed **standing on
that profile**, with the 40 mm width pointing straight up. `renders/06-on-the-bed.png`
is what it should look like in the slicer.

Get that right and there is nothing else to think about: every wall is
plumb, every layer is identical, the lattice holes are outlines rather than
ceilings, and **no supports are needed anywhere**. `build.py` checks there
is not one overhanging face in the mesh.

Get it wrong — laid on its side, say — and the slicer will want supports
through all five bays and through the saddle throat, the throat will come
out undersize, and the compressive load will run across the layer bonds
instead of along the extrusions.

    bed footprint   141.5 x 39.0 mm, 2417 mm2 of contact
    height          40.0 mm
    supports        none

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
| Walls | **3** — the members are 3–4.5 mm, so three walls makes most of them solid, which is what is wanted |
| Top/bottom | 4 each — these are the two 40 mm-apart faces, and they are not structural |
| Infill | 20%, gyroid. There is very little of the part that is not wall. |
| Supports | **none** |
| Brim | **5 mm.** The footprint is 2417 mm2 but it is spread thin along 141 mm, and the saddle end is heavier than the rest. A brim costs minutes. |
| Elephant's foot | leave the slicer's compensation on. The bed face is a 40 mm-tall wall's bottom edge, not a surface anything mates to, but a squashed first layer on a 3 mm brace is a visible lump. |
| Seam | aligned or rear. Random seams on 20 small loops per layer is 20 blobs per layer. |

Roughly **90 g and two to three hours**, which the slicer will put a real
number on. 96.7 cm3 is the *solid* volume; walls and infill come in well
under that.

## Fitting it

1. **Check the lip first.** The throat is 13.5 mm and the model assumes a
   12.7 mm board. Anything from about 11.5 to 13.4 mm goes on. Thicker than
   13.4 and it does not — change `LIP_T` in `params.py` and re-run.
2. **Check there is 14 mm of clear board behind the lip** for the outer leg.
   The photograph says void; the photograph has been wrong before. If there
   is less, drop `LEG_DROP`.
3. Drop the saddle over the lip. The lead-in chamfer on the inside of the
   outer leg means it should find the board rather than catch on it.
4. Push the cabinet back against it. The far pad is 4.5 mm thick and
   24 mm deep and should land flat on whatever is across the gap.
5. **Then look at whether one is enough.** A single strut in the middle lets
   the cabinet skew about it. Two, one towards each end, do not.

## If the first one is wrong

Everything is in `params.py` and everything is derived from it. The three
numbers most likely to need moving, in the order they are likely to need it:

    LIP_T       the lip turns out thicker or thinner than 12.7
    LEG_DROP    there is less room behind the lip than the photo suggested
    SPAN        the far face is recessed, or there is a skirting in the way

Change one, re-run `python3 build.py`, and both STLs and all six renders
move together.
