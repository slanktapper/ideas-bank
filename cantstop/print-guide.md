# cantstop — print guide

Read this before starting a ten-hour print. The short version: **print the fit
coupon first**, it costs twelve minutes and settles the only number in the
design that software cannot verify.

---

## 1. Print the fit coupon first

```
stl/fit-test-coupon.stl    ~10 g, ~12 min
stl/piece-marker.stl       ~1 g, ~4 min   (print two)
```

Print them together, in the material you intend to use for the *board*
(the coupon is a stand-in for the board's rings).

The coupon carries five rings at 6.20, 6.30, 6.40, 6.50 and 6.60 mm bore,
ascending left to right. Each is labelled with the **second decimal** of its
bore: the ring marked `4` is 6.40 mm. Ring height, wall thickness and the
chamfered lead-in all match the real board, because a fit test only transfers
if the plastic around the hole cools the same way.

Then:

1. Push a marker into each ring in turn.
2. You want the one that takes a firm push, holds the board upside down, and
   still comes out without a fight. Too loose and pieces fall out when the
   table is knocked; too tight and you will crack a ring levering one out.
3. Set `COLLAR_BORE` in `params.py` to that number.
4. Also check the two markers stack. If the stack is loose or tight, adjust
   `PEG_SOCKET_D` by the same amount you moved `COLLAR_BORE`.
5. `python3 test_fit.py && python3 build.py`

Only then print the board.

---

## 2. What to print

| File | Qty | Material | Notes |
| --- | --- | --- | --- |
| `board.stl` | 1 | PETG | single colour, digits fused in |
| `board-body.stl` + `board-numerals.stl` | 1 | PETG ×2 | two-colour pair — see below |
| `plate-markers-x11.stl` | 4 | PLA | one per player colour |
| `plate-runners-x3.stl` | 1 | PLA | the shared neutral runners |

Print **either** `board.stl` **or** the body/numerals pair, not both.

For two colours: load `board-body.stl`, then add `board-numerals.stl` to the
*same object* as a second part (in Bambu Studio: right-click the object →
Add part → Load, then assign the numerals to a different filament). They are
modelled in the same coordinate system and the numerals overlap the plaques by
0.2 mm, so they land in the right place with no manual positioning.

A full set is roughly **296 g** at 100% infill: ~179 g board, ~53 g of markers
(44), ~5 g of runners (3). The board is 300 × 300 × 5.5 mm and sits on the
H2D bed with 25 mm spare in X and 20 mm in Y — comfortable, but not enough to
be casual about a skirt.

---

## 3. Orientation and supports

**Everything prints flat on the bed with no supports.** That is a design
constraint, not a happy accident:

- Every lattice strut is **rectangular** in section with its underside on the
  bed. A round rod spanning two rings would be a 3.2 mm unsupported overhang;
  a flat-bottomed bar is just a wide extrusion.
- Every ring bore is a **vertical through-hole**, which needs no support and
  lets you push a stuck piece out from underneath.
- The plaques and numerals are flat plates with a 1.2 mm emboss on top.

**Do not let the slicer auto-orient the board.** It has no reason to keep it
flat and every reason to stand it on edge.

**Pieces print pin-down.** The first layer is then a ~5.9 mm disc, which is a
small footprint for a 12.6 mm part — use a **brim of 4–5 mm**. Printing them
the other way up would put the socket bore face-down and need a bridge.

---

## 4. Slicer settings

Nothing exotic. Starting points:

| | Board | Pieces |
| --- | --- | --- |
| Layer height | 0.20 mm | 0.16 mm |
| Walls | 3 | 3 |
| Infill | 15% (it is nearly all perimeter anyway) | 20% |
| Brim | none needed — large footprint | 4–5 mm |
| Supports | **none** | **none** |

The board is 5.5 mm tall and mostly wall, so infill barely moves the number;
don't bother pushing it up for strength.

On the **numerals**: at 1.2 mm emboss they are six layers at 0.20 mm. If the
colour change smears, raise `NUMERAL_EMBOSS` rather than fighting the purge.

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

- Check a piece seats in a ring at the middle, at the ends of the lens, and on
  a summit. FDM parts are not dimensionally uniform across 300 mm; if the
  edges differ from the middle, that is bed levelling or warp, not the model.
- Check three pieces stack without wobble. The stub is deliberately short
  (3.2 mm), so if a stack rocks, look at the shoulder seating on the ring rim
  rather than at the pin.
- Sit down at the table and check you can read a column number with a piece
  on that column's summit. The model says 40 degrees; the table decides.
- Pick the board up by the perimeter frame. If it flexes more than you like,
  see the rigidity note in `direction.md` — the fix is a parameter, not a
  redesign.

---

## 7. If you change anything

```bash
python3 test_fit.py    # 44 checks, ~5 s
python3 build.py       # regenerate STLs and renders, ~25 s
```

`test_fit.py` is there because most ways of getting this wrong are silent: a
bore that swallows the pin, a strut that ploughs through a hole or across a
numeral, a socket thinned to nothing by the waist, a board that has quietly
grown past the bed, a lattice that has become two detached bodies, a number
you cannot read once a piece is sitting on it. Each one costs a print to
discover and nothing to check.

Look at `renders/03-lattice-detail.png`, `renders/05-stacking-section.png` and
`renders/06-assembly.png` after any change. Those three catch the things the
tests do not — the hidden-number defect was found in the assembly render, and
only then written into the test suite.
