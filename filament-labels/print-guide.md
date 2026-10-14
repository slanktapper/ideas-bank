# filament-labels — print guide

Three tags, six STLs. Everything below assumes the files in `stl/` as `build.py`
writes them.

**One tag type per plate, as many copies as you want.** That is the whole of the
plate strategy, and §6 says why it is also the cheap one. 24 fit.

## 1. The parts

| File | Filament | Volume |
| --- | --- | --- |
| `abs-white.stl` | PLA Basic Jade White | 1.53 cm³ |
| `abs-colour.stl` | PLA Basic Black | 5.63 cm³ |
| `pla-white.stl` | PLA Basic Jade White | 1.59 cm³ |
| `pla-colour.stl` | PLA Basic Indigo Purple | 5.57 cm³ |
| `petg-white.stl` | PLA Basic Jade White | 1.43 cm³ |
| `petg-colour.stl` | PLA Basic Cocoa Brown | 5.73 cm³ |

21.5 cm³ of PLA in total, about 26.6 g — 5.6 g of it jade white, which is the same
5.6 g it was at 1.2 mm. Thickness is bought entirely in letter colour. These are
solid volumes; sparse infill will cut the colour figure, since at 3 mm there is
finally room for some between the solid top and bottom.

All four colours are in `../filament.md`; the cocoa brown is the single spool,
code 10802.

**Two filaments per plate, not four**, because a plate holds one tag type. The H2D
has two nozzles on the toolhead, so jade white can live in one and the letter
colour in the other, and the machine stops swapping filament altogether.

Per tag the total is always the same 7.16 cm³ — about 8.9 g, of which roughly
1.9 g is jade white — because white plus colour is exactly the slab. So a plate
costs:

| Copies | Jade white | Letter colour | Total |
| --- | --- | --- | --- |
| 6 | 11 g | 42 g | 53 g |
| 12 | 23 g | 84 g | 107 g |
| 24 — a full plate | 46 g | 168 g | 213 g |

Solid volumes again; sparse infill comes off the colour column.

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
| Brim | Not needed. A 3 mm slab with a 24 cm² footprint is not going anywhere |
| Infill | Now worth setting. At 3 mm there are layers between the solid top and bottom that do not have to be solid, and they are all letter colour |

**0.20 mm is not a suggestion.** Every depth in the design is a whole number of
layers: 15 for the tag, 4 for the white skin. At 0.25 mm the white skin becomes
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

## 6. One tag type per plate, and copies are free

The thing that costs is **mixing types on one plate**, not the number of tags.

Eleven of the fifteen layers are pure letter colour. On a plate of one type that
means eleven layers with a single filament in them and nothing to swap — and that
holds whether the plate carries one tag or twenty-four, because every copy wants
the same two filaments in the same four layers. Copies are free:

| Plate | Filament loads |
| --- | --- |
| 1 tag, one type | 4 skin layers × 2 = **8** |
| 24 tags, one type | 4 × 2 = **8** — identical |
| All three types together | 4 × 4 + 11 × 3 = **49** |

So purge is a cost per *plate*, not per tag. A dozen of something costs the same
flushing as one of it, which is the argument for running a decent batch of each
while that colour is loaded.

**On the H2D it is smaller still.** Two filaments means one per nozzle rather than
one nozzle swapping between two, so what is left are nozzle changes, not filament
flushes. That is the machine doing what it was bought for, and it is why a
two-colour plate is not worth splitting up. How little it actually wastes is the
slicer's estimate to give, not this paragraph.

**24 fit on a plate**, three across by eight down — 252 × 282 mm inside the
300 × 320 mm dual-nozzle envelope, with a 10 mm margin all round and 6 mm between
tags. `renders/06-a-plate-of-one-type.png` is the layout, and `test_fit.py` checks
it still fits if the tag size changes.

Mind that it is the **dual-nozzle** envelope. The 325 mm figure in
`../available-tools.md` is the single-nozzle one and does not apply to a two-colour
print; laying out to it would cost 25 mm the machine does not have.

The bed is not the constraint here. Print the number of each you actually want.

## 7. The counters are meant to be islands

The hole in the P and the A is jade white, and the letter encircles it, so each one
is a separate island of white with colour all round it. The slicer will show them
as disconnected, and that is correct — do not fill them in. They sit flat on the
plate from layer one and weld to the colour beside them. `test_fit.py` counts them:
four bodies for ABS, three for PLA, two for PETG.

## 8. After printing

Peel off the plate cold. At 3 mm they are rigid and will not flex out of shape the
way the 1.2 mm version would have — but they are still PLA, so they will snap
rather than bend if you lever at them. Lift from a corner.

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
