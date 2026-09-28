# cantstop — print guide

Read this before starting a ten-hour print. The short version: **print the fit
coupon first**, it costs twelve minutes and settles the only number in the
design that software cannot verify.

---

## 1. Print the fit coupon first

```
stl/fit-test-coupon.stl    ~9 g, ~12 min   in the BOARD's material
stl/piece-marker.stl       ~1 g, ~4 min    in the PIECES' material (print two)
```

The board is male: every cell is a pad with a post on it, and the socket is
in the piece. So the coupon carries **posts**, and you try a real piece over
each one. Print the coupon in the board's material and the test pieces in the
pieces' material — otherwise the coupon tests the wrong pair, and with PETG
on the board and PLA in the pieces that matters.

The coupon carries five posts at 5.70, 5.80, 5.90, 6.00 and 6.10 mm,
ascending left to right. Each is labelled with the **second decimal** of its
diameter: the post marked `9` is 5.90 mm. Pad height, post height and the
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
| `board.stl` | 1 | PETG | single colour, numbers engraved |
| `board-body.stl` + `board-numerals.stl` | 1 | PETG ×2 | two-colour pair — see below |
| `plate-markers-x11.stl` | 4 | PLA | one per player colour |
| `plate-runners-x3.stl` | 1 | PLA | the shared neutral runners |

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
piece seats on the number box, and a raised digit is what it would rest on.
Printed single-colour from `board.stl` the pockets are left empty and the
numbers read as engraved.

A full set is roughly **264 g** at 100% infill: ~151 g board, ~52 g of markers
(44), ~5 g of runners (3). The board is 279 × 279 × 7.2 mm and sits on the
H2D bed with 46 mm spare in X and 41 mm in Y.

---

## 3. Orientation and supports

**Everything prints flat on the bed with no supports.** That is a design
constraint, not a happy accident:

- Every lattice strut is **rectangular** in section with its underside on the
  bed. A round rod spanning two pads would be a 3.2 mm unsupported overhang;
  a flat-bottomed bar is just a wide extrusion.
- Every cell is a pad with a **post** on it — solid, upward, nothing to bridge.
  The board has no through-holes at all.
- The number boxes are flat plates with the digits cut 1.2 mm INTO them, so
  nothing stands proud of a face a piece has to sit on.

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

Nothing exotic. Starting points:

| | Board | Pieces |
| --- | --- | --- |
| Layer height | 0.20 mm | 0.16 mm |
| Walls | 3 | 3 |
| Infill | 15% (it is nearly all perimeter anyway) | 20% |
| Brim | none needed — large footprint | none needed — 13.2 mm skirt |
| Supports | **none** | **none** |

The board is 7.2 mm tall and mostly wall, so infill barely moves the number;
don't bother pushing it up for strength.

On the **numerals**: at 1.2 mm deep they are six layers at 0.20 mm. If the
colour change smears, raise `NUMERAL_DEPTH` rather than fighting the purge.

---

## 5. Material

Per `../available-tools.md`, on the shelf:

- **Board — PETG.** Tough, does not creep under a static load, and will not
  soften in a warm room. A 238 × 279 mm PLA lattice left in a sunny room or a
  car will sag, and once it does it is scrap.
- **Pieces — PLA.** Crisper small features, less stringing on a 5.9 mm pin,
  and the colours on hand (red, blue, indigo purple, jade white) give four
  players straight off. Runners in PETG yellow or PLA — either.

Either material wants the H2D's heated chamber off or low; neither needs it.
ABS would work for the board and brings nothing worth the fuss here.

**Note the PETG/PLA mix is deliberate but means the pin/socket fit is across
two materials.** Print the fit coupon in the *board's* material, and the test
pieces in the *pieces'* material, or the coupon tests the wrong pair.

---

## 6. After printing

- Check a piece seats on a post at the middle, at the ends of the lens, and on
  a summit.
  FDM parts are not dimensionally uniform across 279 mm; if the edges differ
  from the middle, that is bed levelling or warp, not the model.
- Check three pieces stack without wobble. The posts are deliberately short
  (3.2 mm), so if a stack rocks, look at the skirt seating on the face below
  rather than at the post.
- Check every number still reads with the post standing in it. A piece on a
  summit does cover that column's number — expected, since by then the column
  is claimed.
- Pick the board up by the perimeter frame. If it flexes more than you like,
  see the rigidity note in `direction.md` — the fix is a parameter, not a
  redesign.

---

## 7. If you change anything

```bash
python3 test_fit.py    # 48 checks, ~10 s
python3 build.py       # regenerate STLs and renders, ~25 s
```

`test_fit.py` is there because most ways of getting this wrong are silent: a
socket that swallows its post, a strut standing proud of a seating face, a
strut printed across a numeral, a wall thinned to nothing, a board that has
quietly grown past the bed, a lattice that has become two detached bodies, a
number you cannot read once a piece is sitting on it. Each one costs a print
to discover and nothing to check.

Look at `renders/03-lattice-detail.png`, `renders/05-stacking-section.png` and
`renders/06-assembly.png` after any change. Those three catch the things the
tests do not — the hidden-number defect was found in the assembly render, and
only then written into the test suite.
