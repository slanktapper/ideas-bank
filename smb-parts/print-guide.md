# smb-parts — printing the shelf rail

Four panels, 225 mm each, clipping over a shelf's front edge to make a 900 mm
(2.95 ft) Mario frieze 25 mm tall.

## Before anything: measure the shelf

`SHELF_T` in `params.py` is **18 mm, and that is a guess.** It is the only
number in the project taken from nowhere. Put a caliper on the board, set it,
re-run `test_fit.py`, re-run `build.py`.

Everything about the clip hangs off it. The front face is fixed at 25 mm by the
brief, so the board eats into what is left for the legs:

| Board | Leg thickness | Verdict |
| --- | --- | --- |
| 15 mm | 4.8 mm | fine |
| 18 mm | 3.3 mm | fine — the default |
| 20 mm | 2.3 mm | thin; `test_fit.py` fails it |
| 22 mm+ | — | raise `FACE_H` above 25 mm, or the clip has no legs |

Nothing about the **art** changes with the board. Only the clip.

## Build

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_fit.py      # ~20 s, must pass
.venv/bin/python build.py         # STLs + renders
```

## Which STLs

Two routes from the same geometry. They are the same solid, one of them cut up.

**One colour, relief.** `stl/panel-N-*.stl`. The art stands 1.2 mm proud and
reads in raking light. One filament, no purge, nothing to assign. Start here.

**Colour, multi-material.** `stl/colour/panel-N-*-channel.stl` plus one
`panel-N-*-<hex>.stl` per NES colour. Load them as one object with parts in
the slicer, assign a filament to each. The hex in the filename *is* the NES
colour. Worst case is 8 bodies (the 1-1 opening), which is exactly the eight
AMS slots.

## Filament, honestly

Checked against `../filament.md`. The overworld is nearly coverable; **the
underground panel is not.**

| NES colour | What it is | Nearest on the shelf |
| --- | --- | --- |
| `#5c94fc` | overworld sky | PETG reflex blue, or PLA Basic blue |
| `#c84c0c` | brick and ground | PLA Basic Cocoa Brown |
| `#00a800` | pipes, hills | PLA Basic Mistletoe Green |
| `#80d010` | bushes, hill tops | **no match** — only one green exists |
| `#000000` | outlines | PLA Basic black |
| `#fcbcb0` | Mario's face, block faces | PLA Pure milky pink |
| `#d82800` | Mario's shirt | PLA Basic red |
| `#fc9838` | Mario's trim | PLA Basic orange |
| `#887000` | dark olive detail | **no match** |
| `#008088` | underground brick | **no match** — no teal |
| `#9cfcf0` | coins | **no match** — jade white is the nearest |
| `#183c5c` | underground shadow | **no match** |

So: the three overworld panels can be printed in colour today, losing only the
light green (bushes come out the same green as the hills, which is survivable)
and the olive. **The underground panel has no correct colour in stock at all** —
print it single-colour, substitute freely, or order teal and cyan.

**The sky is the channel.** Background pixels are not raised; what shows through
is the body. So print the three overworld channels in blue and the underground
channel in black, and the sky is right for free. That is the cheapest colour in
the whole job.

## Orientation and settings

Print **face up, flat on the bed** — the panel lying on its back, legs pointing
up, art on top. No supports: the legs are vertical walls and nothing overhangs.
Printing it the other way up would bridge the plate over the raised pixels.

| | |
| --- | --- |
| Nozzle | 0.4 mm. A game pixel is 0.78 mm, just under two beads. |
| Layer | 0.2 mm. The relief is 1.2 mm, so six layers. |
| Walls | 3+. The face is 2.4 mm, which is six walls, i.e. solid. |
| Infill | barely matters — at these thicknesses it is near solid anyway |
| Material | PLA. It lives indoors on a shelf; nothing is structural. |
| Brim | worth it. 225 mm long and 22 mm wide is a tippy footprint. |

Roughly **232 g for the whole rail**, about 58 g a panel, from the mesh volume
at PLA's 1.24 g/cm³. The walls are thick enough that it prints essentially
solid, so treat that as the real number rather than a floor.

## Assembly

Panels butt left to right in the order they are numbered:

1. `opening` — Mario on the first hill
2. `pipes` — a goomba between two pipes
3. `underground` — coins over teal brick
4. `castle` — the flagpole base and the castle door

The bottom leg carries a **half-lap**: each panel's tongue runs 8 mm past its
right end into the next panel's socket. It stops them sliding apart. They need
no glue — the shelf edge aligns them in the other two axes, which is why there
are no dowels.

Push the rail on from the front. The slot is the board plus 0.4 mm, so it
should go on by hand and stay. If your board is not flat, a strip of foam tape
inside the top leg takes up the slack.
