# smb-parts — printing the shelf rail

**Two parts.** Small **holders** cap the shelf's retainer bar and live there
permanently; **art panels** are plain rectangular slabs that clip into them.
One shelf takes **3 holders and 2 art slabs**, the slabs butting into
320.04 mm — the shelf's exact length. Three shelves is about three feet.

| Part | Each | Per shelf |
| --- | --- | --- |
| holder, 20 mm | 2.8 g | 3 = 8.4 g |
| art slab, 160 mm | ~14.8 g | 2 = ~30 g |
| | | **~38 g a shelf** |

**The art carries nothing.** It is a rectangle 160.02 x 24.618 x 2.4 mm with
relief on one face and nothing at all on its back — no hooks, no returns, no
features. Every part of the clip lives on the holder, which is the piece that
stays on the shelf. That is why the slab prints flat with no supports, and
why the holders barely show: their lips sit **flush** with the deepest relief.

## Print the clip ladder first

The bar slot is settled at 4.2 mm. **The snap is not.** `CLIP_GRAB` is 0.25 mm —
the middle of the 0.1–0.3 you asked for — but "easy and safe to add and
remove" is a feel, not a number.

```bash
.venv/bin/python build.py --test
```

`clip-ladder-stubs.stl` (6 g) is three 20 mm art stubs at bead interferences
of **0.15, 0.25 and 0.35 mm**, labelled on the face as 15 / 25 / 35.
`clip-ladder-bracket.stl` (4.5 g) is one real bracket to try them on. Clip
each stub on and off a few times:

- **Too easy?** It will fall off when you knock the shelf. Go up.
- **Too hard?** You will mark the art levering it off. Go down.
- Whichever feels right becomes `CLIP_GRAB`.

`fit-ladder.stl` only matters if something about the shelf or the filament
changes — the 4.2 mm slot is already settled.

## The shelf this is cut to## The shelf this is cut to

From the product drawing: pressed sheet **4 mm** thick, **12.6 in (320.04 mm)**
long, **3.95 in** deep, with the front edge turned **up** into a retainer bar.
The front elevation — underside of the floor to the top of the bar — is
**0.79 in (20.07 mm)**, so the bar stands **16.07 mm** above the floor.

There is no board edge to clip over, so the rail **caps the bar**: a 4.4 mm
slot drops over it, an inner leg runs 12 mm down the back of it, and the art
hangs down the outside, covering the shelf's whole front elevation with
1.5 mm to spare. It takes **9.3 mm** off the shelf's depth and no usable
height at all.

**Worth a caliper before you print eight panels.** The 0.79 in is read as
*underside of the floor to the top of the bar*. If it turns out to be the
bar's rise above the floor instead, the bar is 4 mm taller than assumed and
the face will stop ~2.5 mm short of the shelf's underside — visible, though
it still grips. Measure floor-top to bar-top; if it is 20 mm rather than 16,
raise `FACE_H` or `WEB_T` to suit.

## Print this first: the fit ladder

**Two things here are arithmetic, not measurement, and ~8 g of filament
settles both.**

```bash
.venv/bin/python build.py --test
```

**The slot is settled: 4.2 mm.** Rob printed the first ladder on
2026-10-23 MDT and the 4.2 rung gripped, so `FIT` is 0.2 and the panels are
built to it. The ladder below has been re-centred on that result, and is
only worth reprinting if something changes — a different shelf, a different
filament, a different printer.

**One caveat before trusting it over a whole panel.** 4.2 was the *tightest*
rung on that ladder, and a coupon is 5 mm of contact where a panel is
160 mm — thirty-two times as much. Friction scales with contact length, and
an FDM slot wanders by a few hundredths over that distance. A fit that is a
firm push at 5 mm can bind at 160 mm. If the first panel fights you, go to
`FIT = 0.3` rather than forcing it.

`stl/test/fit-ladder.stl` — five 5 mm slices of the rail at slot widths
**4.0, 4.1, 4.2, 4.3 and 4.4 mm**, joined by a thin spine, each with its own
width embossed on the face as two stacked digits (`4` over `2` is 4.2). 41 mm
long, 3.8 g, a couple of minutes. Snap or cut them off the spine — it is
1.2 mm thick and lies flat on the bed — and push each onto the shelf's
retainer bar.

- **Which one grips?** Tight enough to need a push, loose enough not to
  crack. Put that number in `FIT` (slot minus the 4 mm bar: a winning 4.3
  means `FIT = 0.3`) and rebuild. **Answered: 4.2, so `FIT = 0.2`.**
- **Does the face reach past the shelf's underside?** Look at the coupon
  from the side once it is on. It should hang about 1.5 mm below. If it
  stops short instead, the drawing's 0.79 in is the bar's rise above the
  floor rather than the whole front elevation, and `BAR_RISE` is 20.07 —
  tell me and I will raise `FACE_H`.

`stl/test/art-sample.stl` — two tiles of real art from the `pipes` vignette
at the design slot, 3.9 g. This is the one to look at to judge whether a
0.77 mm pixel at 1.2 mm relief reads the way you want before 150 g goes into
three shelves.

Neither coupon carries the half-lap, so print them flat side down like the
panels: **web on the bed.**

## Build

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_fit.py      # ~30 s, must pass
.venv/bin/python build.py         # STLs + renders
```

## Which STLs

Two routes from the same geometry; they are the same solid, one of them cut up.

**One colour, relief.** `stl/shelf-KEY-N.stl`. The art stands 1.2 mm proud and
reads in raking light. One filament, no purge. Start here.

**Colour, multi-material.** `stl/colour/shelf-KEY-N-cap.stl` plus one
`...-<hex>.stl` per NES colour. Load them as one object with parts and assign
a filament to each. The hex in the filename *is* the NES colour. Worst case is
8 bodies (the 1-1 opening), exactly the eight AMS slots.

## Filament, honestly

Checked against `../filament.md`. The overworld is nearly coverable; **the
underground shelf is not.**

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
| `#9cfcf0` | coins | **no match** — jade white is nearest |
| `#183c5c` | underground shadow | **no match** |

The three overworld shelves print in colour today, losing the light green
(bushes come out the same green as the hills) and an olive detail. **The
underground shelf has no correct colour in stock at all** — print it
single-colour, substitute freely, or order teal and cyan.

**The sky is the cap.** Background pixels are not raised, so what shows through
is the body. Print the overworld caps in blue and the underground cap in black
and the sky is right for free.

## Orientation and settings

**Art slabs: flat on the bed, relief up, no supports.** The back is a plain
face, so it lies straight down and nothing overhangs. This is the payoff from
moving every feature onto the holder — the previous design needed supports
under its hooks and this one needs none.

**Holders: stand them on end**, the 20 mm length vertical. The holder is a
constant section swept along its length, so with that axis up, every face is
either a vertical wall or one of the two ends: zero overhang, no supports, no
bridges. Footprint is about 12.5 x 27 mm, so use a brim — they are tall for
their base. Print all three at once.

| | |
| --- | --- |
| Nozzle | 0.4 mm. A game pixel is 0.77 mm, just under two beads. |
| Layer | 0.2 mm. Relief is 1.2 mm, so six layers. |
| Walls | 3+. The slab is 2.4 mm, which is six walls, i.e. solid. |
| Material | PLA. Indoors on a shelf; nothing is structural. |
| Brim | on the holders. The slabs do not need one. |

### What the margin costs

The top and bottom **1.2 mm** of each slab carry no relief — that is the flat
the holder's lips bear on, plus 0.2 mm of daylight so the lip's top face is
not exactly coplanar with the first row of pixels. It works out at about
**1.6 game pixels** top and bottom. Without it the lips would have to clear the raised pixels and the
slab would rattle 1.2 mm front to back. The colour is unaffected; only the
relief stops short.

## Assembly

1. **Push the three holders onto the retainer bar**, down from above. Flush
   at each end and one in the middle. The middle one sits at 150.0 mm and
   spans to 170.0, so it straddles the joint at 160.0 and lines the two
   slabs up.
2. **Drop a slab in:** sit its bottom edge on the holders' bottom ledges,
   push the top back until the bead on each top lip snaps over the face.
3. Same for the second slab.

To swap a scene, ease the top of a slab forward past the beads and lift it
out. The holders never move.

The four shelves available, each a straight crop of a real level map:

1. `opening` — Mario on the first hill, bushes, a goomba
2. `pipes` — pipes, goombas and the big hill
3. `underground` — coins over teal brick, two goombas
4. `castle` — the staircase, the flagpole base and the castle door
