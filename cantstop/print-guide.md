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
ascending left to right. Each is labelled with the **second decimal** of its
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

## 2. What to print

| File | Qty | Material | Notes |
| --- | --- | --- | --- |
| `board.stl` | 1 | PLA red | single colour, numbers engraved |
| `board-body.stl` + `board-numerals.stl` | 1 | PLA red + jade white | two-colour pair — see below |
| `plate-markers-x11.stl` | 4 | PLA | one per player colour |
| `plate-runners-x3.stl` | 1 | PLA or PETG | the shared neutral runners |

Print **either** `board.stl` **or** the body/numerals pair, not both.

For two colours: load `board-body.stl`, then add `board-numerals.stl` to the
*same object* as a second part (in Bambu Studio: right-click the object →
Add part → Load, then assign the numerals to a different filament). They are
modelled in the same coordinate system, so they land in the right place with
no manual positioning.

`board-numerals.stl` is the digits **plus the slice of each summit post the
digit passes through**. That is what makes the numbers readable: a post stands
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

A full set is roughly **216 g**: ~158 g board (6 mm slab at 10% infill),
~53 g of markers (44), ~5 g of runners (3). The board is
284.9 × 284.9 × 9.2 mm and sits on the H2D bed with 40 mm spare in X and
35 mm in Y.

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

**Pieces print the right way up — skirt down, post up.** The first layer is
the full 13.2 mm skirt, which is a generous footprint, so no brim is needed.

The socket faces downward and is closed by a **45° cone**, not a flat ceiling.
That is deliberate: a flat roof would be a 6.35 mm bridge over thin air part
way up the print, whereas a 45° cone self-supports. Nothing ever touches that
surface, so its finish does not matter.

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
| Brim | see below | none needed — 13.2 mm skirt |
| Supports | **none** | **none** |

**The 10% is the design, not a suggestion.** A solid plate's cost is its
skins, and over this octagon three skin layers top and bottom come to 94 g
before any infill at all. Everything between them is the infill setting, so
moving it does far less than it looks: at 5% the board is 131 g, at 10% it is
158 g, at 29% it is 221 g. Six millimetres at 10% is about twenty-three times
as stiff in bending as the old lattice was, for 13% more plastic. Turning the
infill up buys very little more.

**Brim.** 285 mm of flat 6 mm PLA is a large area and the corners of the
octagon are exactly where a plate lifts. The H2D's heated chamber helps; a
brim is cheap insurance on the first attempt.

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

- Check the board is flat. Sight down it. 285 mm of solid PLA is the most
  warp-prone thing in this project.
- Check a piece seats on a post at the middle, at the ends of the lens, and on
  a summit. FDM parts are not dimensionally uniform across 285 mm; if the
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
python3 test_fit.py    # 56 checks, ~20 s
python3 build.py       # regenerate STLs and renders, ~50 s
```

`test_fit.py` is there because most ways of getting this wrong are silent: a
socket that swallows its post, a wall thinned to nothing, a board that has
quietly grown past the bed, a lip that has crept in far enough to land on a
pad, a number you cannot read once a piece is sitting on it. Each one costs a
print to discover and nothing to check.

Look at `renders/03-surface-detail.png`, `renders/05-stacking-section.png` and
`renders/06-assembly.png` after any change. Those three catch the things the
tests do not — the hidden-number defect was found in the assembly render, and
only then written into the test suite.

Switching back to the open truss is `BOARD_STYLE = "lattice"` in `params.py`.
The tests and the renders follow it; this guide does not, and sections 3, 4
and 5 would all need rereading.
