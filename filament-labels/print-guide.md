# filament-labels — print guide

Three tags, six STLs, one job. Everything below assumes the files in `stl/` as
`build.py` writes them.

## 1. The parts

| File | Filament | Volume |
| --- | --- | --- |
| `abs-white.stl` | PLA Basic Jade White | 1.53 cm³ |
| `abs-colour.stl` | PLA Basic Black | 1.34 cm³ |
| `pla-white.stl` | PLA Basic Jade White | 1.59 cm³ |
| `pla-colour.stl` | PLA Basic Indigo Purple | 1.27 cm³ |
| `petg-white.stl` | PLA Basic Jade White | 1.43 cm³ |
| `petg-colour.stl` | PLA Basic Cocoa Brown | 1.44 cm³ |

8.6 cm³ of PLA in total, about 10.7 g — 5.6 g of it jade white. All four colours
are in `../filament.md`; the cocoa brown is the single spool, code 10802.

**Four slots, so one job.** Two AMS 2 Pro units give eight, and this needs four.
Printing the three tags separately would not save purge — the flushes scale with
the number of two-colour layers, and that is the same either way — so there is no
reason to split the job.

## 2. Do not rotate anything

**The lettered face is at z=0 and the STLs are already that way round.** Drop them
on the plate and leave them alone. That face goes against the textured plate, which
is the point: the surface you read is the one that was pressed into the texture.

The lettering in the model is **mirrored on purpose**. You read that face from
below once the tag is off the plate, so geometry that looks correct in the slicer's
preview would come off the printer backwards. If the words look reversed in the
preview with the tag lying lettering-down, that is right. If they look correct
there, something has flipped the model and the print will be wrong.

`test_fit.py` checks this, and it is the check most likely to save a reprint.

## 3. Load each tag as one object with two parts

The white and the colour share an origin and interlock exactly — together they are
precisely the plain slab, to within a ten-thousandth of a cubic millimetre. They
only do that if the slicer keeps them in the same place.

Select both files for a tag at once on import. Bambu Studio asks whether to load
multiple files as a single object with multiple parts; the answer is yes. If they
come in as two separate objects instead, select both and assemble them — do not
move either one, since their positions are already correct.

Then assign the filament per part: the `-white` part to jade white, the `-colour`
part to that tag's colour.

## 4. Settings

| | |
| --- | --- |
| Layer height | **0.20 mm**, and not something else — see below |
| Plate | Textured PEI. The texture is the finish on the readable face |
| Supports | None. Nothing overhangs |
| Brim | Not needed. A 1.2 mm slab with a 24 cm² footprint is not going anywhere |
| Infill | Irrelevant — at 1.2 mm it is all solid layers regardless |

**0.20 mm is not a suggestion.** Every depth in the design is a whole number of
layers: 6 for the tag, 4 for the white skin. At 0.25 mm the white skin becomes
three layers and change, the slicer rounds it, and the number that stops the black
showing through the white quietly stops being the number that was checked. If you
want a different layer height, change `LAYER` in `params.py` and rebuild — the
geometry will follow it.

## 5. Print the ABS tag first

Black under white is the worst case of the three. If 0.80 mm of jade white hides
black, it hides indigo and cocoa brown too, and the other two can be printed with
confidence. If it does not — if the white reads grey or blotchy — raise
`WHITE_LAYERS` in `params.py` to 5 and rebuild before printing the rest.

What `build.py` says each choice costs, across all three tags:

| White skin | Jade white used |
| --- | --- |
| 2 layers, 0.40 mm | 2.8 g — what was first suggested, and too thin |
| 3 layers, 0.60 mm | 4.2 g — the floor; probably fine for brown and indigo |
| **4 layers, 0.80 mm** | **5.6 g — what is built** |
| 5 layers, 1.00 mm | 7.0 g |

## 6. What to expect from the purge

The parts are tiny and the flushing will not be. Layers 1–4 carry all four
filaments and layers 5–6 carry three, so there are roughly twenty colour changes
in the job. Depending on the flush volumes, the purge can be comparable to the
8.6 cm³ of actual tag — the slicer's own estimate is the number to look at before
starting, not this paragraph.

Nothing about that is avoidable at this size; it is the cost of a two-colour part,
and it is still one job and about ten grams of filament.

## 7. The counters are meant to be islands

The hole in the P and the A is jade white, and the letter encircles it, so each one
is a separate island of white with colour all round it. The slicer will show them
as disconnected, and that is correct — do not fill them in. They sit flat on the
plate from layer one and weld to the colour beside them. `test_fit.py` counts them:
four bodies for ABS, three for PLA, two for PETG.

## 8. After printing

Peel off the plate cold. The tags are 1.2 mm and will flex; they are PLA, so they
will also snap if you fold them — lift from a corner rather than levering from the
middle.

Tape to the bin with whatever is to hand. PLA softens around 60 °C, which a garage
in Alberta will never see, so there is nothing to worry about there.

## 9. If you change anything

    python3 build.py        # regenerates stl/ and renders/
    python3 test_fit.py     # 37 checks

Change numbers in `params.py`, not the STLs. Tag size, skin depth, layer height,
margins and the list of tags all live there, and the lettering re-solves itself —
all three words are set at one cap height, the largest at which the widest of them
still fits, so narrowing the tag shrinks all three together rather than letting
PETG overflow.
