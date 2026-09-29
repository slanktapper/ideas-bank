# cantstop — print guide

Read this before starting a long print. The short version: **print the fit
coupon first**, it costs twelve minutes and settles the only number in the
design that software cannot verify.

---

## 1. Print the fit coupon first

```
stl/fit-test-coupon.stl    ~9 g, ~12 min   in the BOARD's material
stl/piece-marker.stl       ~1 g, ~4 min    in the PIECES' material (print two)
```

The board is male: every cell is a post, and the socket is in the piece. So
the coupon carries **posts**, and you try a real piece over each one.

The coupon carries five posts at 5.70, 5.80, 5.90, 6.00 and 6.10 mm,
ascending left to right. Against the current 6.24 mm socket those are
clearances of 0.54, 0.44, **0.34 (nominal)**, 0.24 and 0.14 mm diametral, so
the coupon brackets the design value with two looser and two tighter. Each is labelled with the **second decimal** of its
diameter: the post marked `9` is 5.90 mm. Seat height, post height and the
chamfered lead-in all match the real board, because a fit test only transfers
if the plastic is shaped and cooled the same way.

Then:

1. Push a marker onto each post in turn.
2. You want the one that takes a firm push, holds the coupon upside down, and
   still comes off without a fight. Too loose and pieces fall off when the
   table is knocked; too tight and you will split a socket levering one off.
3. Set `POST_D` in `params.py` to that number.
4. Also check the two markers stack on each other. That fit is set by
   `PEG_POST_D` against `PEG_SOCKET_D`; if it differs from the board fit,
   move `PEG_POST_D` by the same amount you moved `POST_D`.
5. `python3 test_fit.py && python3 build.py`

Only then print the board.

---

## 1a. Then print the stub

```
stub-board-body.stl + stub-board-numerals.stl   ~4 g,  ~20 min   two colours
stub-pieces-x6.stl                              ~8 g,  ~35 min   one of every piece
```

The coupon answers one question. The stub answers the rest of them, and it
answers them about the real board, because **it is the real board**: the
finished mesh intersected with a 22 x 55 mm box, not a small part built to
look similar. The slab thickness, the raised lip, the engraved digits, the
split posts, the clearance between the lip and the topmost pads and the
seating faces are all bit-for-bit what the full board would print.

It is the corner over columns 6, 7 and 8 — the densest part of the board, so
it carries three numbers, six posts at the real 22 mm column pitch, and the
run of raised lip that comes closest to a pad anywhere on the board — with
its white cap on. Three of
its four edges are raw cuts through open plate; the fourth is the board's own
outline.

Print it in the two colours you mean to use, then check:

1. **The numbers read.** Look straight down. Each digit should be whole, with
   the post in the middle of it in the number's colour and no ring of body
   colour around it. This is the one thing that cannot be settled from a
   render, because it depends on how your printer handles a colour boundary
   running up the side of a 5.9 mm post — bleed, seam, purge staining.
2. **A piece seats flat** on a plain post and does not rock.
3. **A second piece stacks** on the first, sits square, and comes off again.
4. **Two pieces on neighbouring posts** clear each other. 8.8 mm along a row.
5. **The lip.** Look for a seam where the ring starts each layer, and check it
   has not crept in far enough to foul a piece on the top row of posts.
6. **The engraved pockets.** Six layers at 0.20 mm. If the colour smears,
   raise `NUMERAL_DEPTH` (and `RIM_H` with it) rather than fighting the purge.
7. **The white cap on the lip.** Three layers. Check the colour boundary
   partway up the lip is clean and lands where it should — it is the longest
   two-colour boundary on the board, and the only one you can measure with a
   caliper.

`renders/07-test-print.png` is what it should come out like.

What the stub cannot tell you is whether 310 mm of flat PLA warps. Nothing
66 mm across will.

---

## 2. What to print

| File | Qty | Material | Notes |
| --- | --- | --- | --- |
| `board-body.stl` + `board-numerals.stl` | 1 | PLA red + jade white | the board; two files, one object |
| `game-pieces-A.stl` | 1 | PLA | **piece 1** — player A, 11 counters |
| `game-pieces-B.stl` | 1 | PLA | **piece 2** — player B, 11 crowns |
| `game-pieces-C.stl` | 1 | PLA | **piece 3** — player C, 11 saucers |
| `game-pieces-D.stl` | 1 | PLA | **piece 4** — player D, 11 cogs |
| `plate-runners-x3.stl` | 1 | PLA or PETG | **piece 5** — the shared neutral runners |
| `plate-active-x4.stl` | 1 | PLA | **piece 6** — one active-player marker each; print each in that player's colour |

### The piece numbers

Every piece has a number, and it is the same number in conversation, in the
report `build.py` prints, in the STL notes and in the catalogue render. See
`renders/09-piece-catalogue.png`, or `renders/piece-<n>-<style>.png` for one
on its own.

| # | Shape | Whose | One piece | The printable set |
| --- | --- | --- | --- | --- |
| **1** | counter | player A | `piece-counter.stl` | `game-pieces-A.stl` |
| **2** | crown | player B | `piece-crown.stl` | `game-pieces-B.stl` |
| **3** | saucer | player C | `piece-saucer.stl` | `game-pieces-C.stl` |
| **4** | cog | player D | `piece-cog.stl` | `game-pieces-D.stl` |
| **5** | runner | shared | `piece-runner.stl` | `plate-runners-x3.stl` |
| **6** | active | one each | `piece-active.stl` | `plate-active-x4.stl` |

Pieces 1 to 5 are 17.5 mm across and 8.45 mm tall, to the micron, and any of
them stacks on any other adding exactly 6.30 mm. **Piece 6 is the odd one
out on purpose**: square, 23.0 mm tall, no post on top, so nothing stacks on
it. It takes the same socket and the same 17.5 mm footprint, so it drops onto
a board post or onto a marker like anything else — it is just the end of the
stack. Being square it reaches 12.37 mm into its corners against a round
piece's 8.75, which still clears both its neighbours and the raised lip;
`test_fit.py` puts it on all 83 cells and measures. A number stays with its shape: a new shape takes the next free number
rather than shuffling these, which is exactly what 6 did.

and, for the test print above:

| File | Qty | Material | Notes |
| --- | --- | --- | --- |
| `stub-board-body.stl` + `stub-board-numerals.stl` | 1 | PLA red + jade white | a 22 x 55 mm strip of the real board, top of column 7 |
| `stub-pieces-x6.stl` | 1 | PLA | one of every piece — four markers, a runner and the active marker — to seat and to stack |

**The board is two files and needs both.** There is no single-colour version
any more: the numbers, the title, the border and the alternating post tops
are all carried by the second filament, and without it the board is a plate
of identical dots. Load both, always.

For two colours: load `board-body.stl`, then add `board-numerals.stl` to the
*same object* as a second part (in Bambu Studio: right-click the object →
Add part → Load, then assign the numerals to a different filament). They are
modelled in the same coordinate system, so they land in the right place with
no manual positioning.

`board-numerals.stl` carries four things: the digits and the title letters,
**the slice of each summit post the digit passes through**, **the top 0.60 mm
of the raised lip**, and **the top 0.60 mm of every post in an even-numbered
column**, so neighbouring columns alternate white and red and each one reads
as its own line.

The lip is split rather than handed over whole: the bottom 0.60 mm stays with
the body, so the edge of the board is a red wall with a white cap on it, not a
white wall standing on red. `RIM_CAP_H` in `params.py` sets how much of it
goes white — 0 for none, `RIM_H` for all of it.

**`RIM_CAP_H` must be a whole number of layers**, and `params.py` assumes you
will slice the board at `LAYER_H` = 0.20 mm. Slice it at 0.16 or 0.28 and
0.60 mm no longer lands on a layer boundary: the slicer gives that layer to
one colour or the other, and a 3-layer cap comes out 2 or 4. If you change the
layer height, change `LAYER_H` to match, pick a `RIM_CAP_H` that divides by
it, and rerun `test_fit.py` — it checks the division.

On the split post: That is what makes the numbers readable: a post stands
in the middle of each digit, and rather than pick one flat colour for it, the
post is split by the glyph. Where the digit passes, the post prints in the
number's colour; the rest prints with the body. Seen from above the post is
coloured by exactly what it covers and the number is whole.

So the two files interlock more tightly than usual — each summit post is
shared between them. Load both, assign `board-numerals.stl` to the accent
filament, and do not try to print either alone and expect a complete post.

The digits are **pockets in the plate, filled flush**, not raised lettering: a
piece seats on the plate where the number is, and a raised digit is what it
would rest on. Printed single-colour from `board.stl` the pockets are left
empty and the numbers read as engraved.

A full set is roughly **223 g**: ~158 g board, body and numerals together
(6 mm slab at 10% infill),
~58 g of markers (11 each of four shapes), ~5 g of runners (3). A marker is 17.5 mm across and
8.45 mm tall and so is a runner — every piece on this board is the same size
to the micron — and every stacked piece adds exactly 6.30 mm. The board is
285.0 × 285.0 × 9.2 mm. Note that the board is a **two-filament** part, so
the envelope that applies is the H2D's **dual-nozzle** one — 300 × 320, not
the 325 × 320 you get with a single nozzle. It fits with 15 mm spare in X and
35 in Y.

---

## 3. Orientation and supports

**Everything prints flat on the bed with no supports.** That is a design
constraint, not a happy accident:

- Every cell is a **post** standing on the plate — solid, upward, nothing to
  bridge. The board has no through-holes at all.
- The digits are cut 1.2 mm **into** the plate, so nothing stands proud of a
  face a piece has to sit on.
- The raised lip around the edge is 8 mm wide and 1.2 mm tall, a plain
  extrusion off the top of the plate. No overhang.

**Do not let the slicer auto-orient the board.** It has no reason to keep it
flat and every reason to stand it on edge.

**Each player gets a different shape**, so a glance across the table tells
you whose piece is whose without having to judge a colour. They are
interchangeable in every way that matters: any one stacks on any other and
adds the same 6.30 mm.

**Pieces print the right way up — skirt down, post up.** The first layer is
the full 17.5 mm bottom face — flat by rule, with vertical walls for the
first 0.40 mm — which is a generous footprint, so no brim is needed.

The socket faces downward and is closed by a **45° cone**, not a flat ceiling.
That is deliberate: a flat roof would be a 6.24 mm bridge over thin air part
way up the print, whereas a 45° cone self-supports. Nothing ever touches that
surface, so its finish does not matter.

The piece is short enough now that the cone cannot reach a point — it needs
3.07 mm of height and has 1.90 — so it is truncated and **2.33 mm of the roof
is bridged**. That is short enough that no slicer will complain and no
support is wanted. If you ever make the pieces shorter still, watch that
number: `test_fit.py` prints it and fails it past 4 mm.

Do **not** print pieces upside down to "avoid" the socket. Inverted, the step
from post to skirt becomes a flat overhang ring and genuinely needs support.

---

## 4. Slicer settings

| | Board | Pieces |
| --- | --- | --- |
| Layer height | 0.20 mm | 0.16 mm |
| Walls | 3 | 3 |
| Top/bottom layers | 3 | 3 |
| Infill | **10%** | 20% |
| Brim | see below | none needed — 17.5 mm flat bottom |
| Supports | **none** | **none** |

**The 10% is the design, not a suggestion.** A solid plate's cost is its
skins, and over this octagon three skin layers top and bottom come to 94 g
before any infill at all. Everything between them is the infill setting, so
moving it does far less than it looks: at 5% the board is 131 g, at 10% it is
158 g, at 29% it is 221 g. Six millimetres at 10% is about twenty-three times
as stiff in bending as the old lattice was, for 13% more plastic. Turning the
infill up buys very little more.

**Brim.** 310 mm of flat 6 mm PLA is a large area and the corners of the
octagon are exactly where a plate lifts. The H2D's heated chamber helps; a
brim is cheap insurance on the first attempt.

**Your slicer will probably offer to repair `board-numerals.stl`.** Let it,
or ignore it — either is fine. It is 60 separate bodies, and an STL has no
way to say so: every loader welds coincident vertices, which turns the rim
where a number's pocket meets the post standing in it into an edge with four
faces on it. Every body is closed and correctly wound on its own, which is
all a slicer actually needs. `test_fit.py` checks that those welds only ever
happen at the seat plane, because anywhere else would mean two solids really
were intersecting.

On the **numerals**: at 1.2 mm deep they are six layers at 0.20 mm. If the
colour change smears, raise `NUMERAL_DEPTH` rather than fighting the purge.
Note that `RIM_H` is deliberately the same number, so raising one without the
other splits the board's single depth step into two.

---

## 5. Material

Per `../available-tools.md`, on the shelf:

- **Board — PLA Basic, red.** This is a compromise worth knowing about.
  **There is no red PETG**: PETG is stocked in yellow, reflex blue, orange,
  white and black, and red exists only as PLA. PETG would be the better
  engineering choice for a large flat part — tough, ~80 °C, does not creep —
  so choosing red means accepting PLA, which softens around 60 °C and sags
  under a sustained load. On a table indoors that is fine. In a car in
  July it is scrap. If that matters more than the colour, an orange or black
  PETG board is the swap.
- **Numbers — PLA Basic, jade white.** Same family as the body, so the
  two-colour interface bonds properly. (PLA and PETG barely bond to each
  other — do not mix them *within* one part.)
- **Pieces — PLA.** Crisper small features, less stringing on a 5.9 mm post,
  and the colours on hand (red, blue, indigo purple, jade white) give four
  players straight off. Runners in PETG yellow or PLA — either; they are
  separate parts, so the material mix costs nothing.

With the board now in PLA, the post/socket fit is **PLA against PLA**, which
is one variable fewer than the old PETG board. Print the coupon in whatever
the board will be.

---

## 6. After printing

- Check the board is flat. Sight down it. 310 mm of solid PLA is the most
  warp-prone thing in this project.
- Check a piece seats on a post at the middle, at the ends of the lens, and on
  a summit. FDM parts are not dimensionally uniform across 310 mm; if the
  edges differ from the middle, that is bed levelling or warp, not the model.
- Check three pieces stack without wobble. The posts are deliberately short
  (3.2 mm), so if a stack rocks, look at the skirt seating on the face below
  rather than at the post.
- Check every number still reads with the post standing in it. A piece on a
  summit does cover that column's number — expected, since by then the column
  is claimed.
- Look along the raised lip for a seam where the ring starts each layer.

---

## 7. If you change anything

```bash
python3 test_fit.py    # 123 checks, ~2 min
python3 build.py       # regenerate STLs and renders, ~50 s
```

`test_fit.py` is there because most ways of getting this wrong are silent: a
socket that swallows its post, a wall thinned to nothing, a board that has
quietly grown past the bed, a lip that has crept in far enough to land on a
pad, a number you cannot read once a piece is sitting on it. Each one costs a
print to discover and nothing to check.

Look at `renders/03-surface-detail.png`, `renders/05-stacking-section.png`,
`renders/06-assembly.png` and `renders/07-test-print.png` after any change. Those three catch the things the
tests do not — the hidden-number defect was found in the assembly render, and
only then written into the test suite.
