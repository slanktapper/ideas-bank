# cantstop

**Status:** prototype

## What it is

A 3D-printed push-your-luck dice board game. The board is eleven columns, one
for each total you can roll on two dice, 2 through 12. Each column is a ladder
of cells, and the number of cells is roughly inverse to how likely that total
is: 2 and 12 are three cells deep, 3 and 11 are five, and so on up to 7, which
is thirteen — eighty-three cells in all.

Columns are **centre-aligned** on a shared midline, so the cell field is a
symmetric lens rather than a pyramid, and the whole thing sits inside a
**regular octagon** — all eight edges the same 118.0 mm, 284.9 mm across the
flats. The columns do not all share one row pitch: the middle five step down by
only a quarter of a box and the rest follow by the same amount, which flattens
the top of the lens and pulls its shoulders out towards the frame instead of
leaving it a narrow spike in a wide octagon.

The board is a **6 mm solid octagonal slab, printed at 10% infill**, with a
raised lip 8 mm wide around the edge. Every cell is a post standing on that
plate; the plate itself is the seat. Around the outside the lip stands 1.2 mm
proud — the same relief the numbers are sunk by, so the board has one depth
step and not two.

**This started as a wireframe and stopped being one on the numbers.** The
original brief asked for an open truss, and that is built and still selectable
(`BOARD_STYLE = "lattice"`): rings tied by flat-bottomed struts with a diagonal
per bay, braced out to the octagon by twenty-four spokes. The catch is that a
lattice is nearly all perimeter — infill can reach 11% of a strut and 49% of a
pad — so it cannot be lightened, and at 128 cm³ it came out at about 140 g and
was still the floppiest option on the table. A slab's cost is its **skins**,
which are a fixed 94 g over this octagon however thick it is, and everything
between them is whatever the infill is set to. So 6 mm at 10% weighs 158 g —
13% more than the lattice — and is roughly **twenty-three times** as stiff in
bending (sandwich model: two 0.6 mm skins 5.4 mm apart plus a 10% core; 4 mm
would be nine times, 10 mm seventy-six). That is the trade, and it is why the
wireframe lost.

**The interface runs male-up throughout.** The board offers a post; a piece has
a socket underneath and a post of its own on top; so a piece drops onto the
board, and the next piece drops onto that one, with one geometry doing both
jobs. A piece seats when its **skirt** lands on the face below — the plate, or
the top face of the piece beneath it — never when a post bottoms out, so stack
height is exactly 9.40 mm per piece, every time.

Two things follow from male-up that were not obvious going in. The board has
**no through-holes at all**, which retires a whole class of defect. And the
seat is a 3.0-to-6.6 mm annulus rather than the rim of a ring, which is a far
steadier thing for a 13.2 mm piece to stand on — which in turn is why the posts
can be only 3.2 mm long.

**The number is the top of the column, and you land on it.** Each column's
topmost cell carries its number: the digit and the post share one centre. The
summit is an ordinary cell — you land on it exactly as you land on any other —
and the thing you land on is the number. On the slab there is no separate
number box; the digit is cut straight into the plate. `PLAQUE_W`/`PLAQUE_H`
still define the footprint the number reserves, which is what keeps the summits
from crowding each other and what the octagon is sized against.

**The post is split by the digit, and that is the whole trick.** It has to
stand in the middle of the glyph, so the only question is what colour it
should be — and the answer is neither the board's nor the number's but both.
The post is cut by the digit extruded vertically through it: where the glyph
passes, the post goes in the number's colour; the rest goes in the board's.
Seen from directly above, the post is coloured by exactly what it covers, so
the number is whole.

Both flat colours were tried first and both failed. In the number's colour the
post merged with the glyph into one mass. In the board's colour it punched a
hole through the middle. Rendered head-on at the same camera and counted in
pixels: a solid post loses **16% of an 8** and takes its waist with it; split
this way, **100% of the glyph survives** — 14 pixels out of 74,000, which is
antialiasing on the chamfer. `test_fit.py` checks that every square millimetre
the post covers is handed back in the number's colour.

The digit is **inlaid flush, not embossed**, and that is structural rather than
decorative: a piece seats on the plate, so a digit standing 1.2 mm proud of it
would be what the skirt rests on, and the piece would rock. Cut into the plate
instead and the seating face stays flat. In two colours the fill comes out
flush; in one colour the pocket is left empty and reads as engraving.

This is Sid Sackson's *Can't Stop* (1980). The rules are not ours; the physical
design is.

## Why

Two reasons, and the second is the real one.

The commercial editions are cardboard and the pieces are flat plastic discs
that slide when the table is knocked. A pegged board fixes that outright.

More to the point, this is the kind of object the workshop is for. It is well
inside the printer's envelope, it needs no supports, it wants two colours
(which the AMS gives for free), and it is 47 small identical parts plus one
large one — exactly the shape of problem where a printer beats buying.

## Scope

**Does:** the board, the playing pieces, and the files to print them. Everything
is parametric, so the ladder, cell pitch, column spacing, board style, slab
thickness, lip, frame shape, piece profile and fits are all one edit in
`params.py` away from a different board. Ships STLs, test renders, and a design
test suite.

**Deliberately does not:**

- Ship the rules. The game is Sackson's; look them up.
- Model dice. Four D6 out of a drawer will do, and printed dice roll badly.
- Do a box, tray or insert. Worth doing later; not the interesting part.
- Slice. Build a 3MF/gcode for a specific machine in the slicer, not here.
- Chase a "nice" render. The renders exist to catch mistakes before filament
  is spent, not to sell anything.

## Stack

Parametric CAD as code, in Python. No GUI, no OpenGL, no system packages.

| | |
| --- | --- |
| Geometry | `trimesh`, with `manifold3d` as the boolean engine |
| Polygons | `shapely` + `mapbox_earcut`, for the extruded numerals |
| Glyphs | `matplotlib.textpath` (DejaVu Sans, bundled — same result anywhere) |
| Renders | a ~150-line software rasteriser in `render.py`; numpy z-buffer, no GPU |
| Output | binary STL, PNG |

**Why not OpenSCAD.** It was the obvious first choice and it is installable
(2021.01). Its CGAL boolean engine on an 83-ring lattice is minutes per render,
against 1.3 s for `manifold3d` here, and the renders would still have needed a
second toolchain. Python keeps geometry, tests and renders in one place.

**Why a hand-written rasteriser.** The usual headless options (pyrender/OSMesa,
pyglet under xvfb) are a stack of system libraries that break whenever the base
image moves. A numpy z-buffer has no dependencies past numpy and pillow and is
deterministic — the same geometry gives the same PNG on any machine.

## How to run

```bash
cd cantstop
python3 -m pip install -r requirements.txt

python3 test_fit.py      # 64 design checks — run this after editing params.py
python3 build.py         # every STL into stl/, every render into renders/
python3 build.py --stl   # STLs only            (~6 s)
python3 build.py --fast  # quarter-res renders  (~12 s total)
```

Full build is about 50 seconds. `stl/` and `renders/` are regenerated from
scratch and safe to delete.

Everything dimensioned lives in `params.py`. Change a number there, run
`test_fit.py`, rebuild. See `print-guide.md` before printing anything.

## Where it stands

Designed and verified in software; **nothing has been printed yet.** The board
is 284.9 × 284.9 × 9.2 mm, which fits the H2D's 325 × 320 mm bed with 40 mm
spare in X and 35 mm in Y. A full set is about **216 g** — 158 g of board at
10% infill plus 58 g of solid pieces.

`test_fit.py` passes 64 checks. The ones that earn their keep are the ones that
touch the fused mesh rather than the parameters: a probe of every cell's
seating annulus, a check that every square millimetre the post covers comes
back in the number's colour, and — for the slab — that the lip is the same
width on all eight edges, clears the outermost pads by 4 mm, and is genuinely a
lip rather than a plate that came out 7.2 mm thick everywhere.

Defects this loop has caught rather than a print:

- a drop strut printed straight across every column numeral;
- in fixing that, a board that quietly became two detached bodies;
- **a piece claiming a summit hiding that column's number.** The tests did not
  catch that one and `renders/06-assembly.png` did: a marker sitting on "2"
  covered it completely. Accepted now, because by then the column is claimed;
- the first version of that sightline test said *every* number was hidden,
  which the renders plainly contradicted. It was modelling a piece as one fat
  cylinder; the body is 13.2 mm across but only 13.4 mm tall, and the post
  above it is 5.9 mm;
- a lattice that was not mirror-symmetric, because the herringbone parity keyed
  on a row *index* and a gap and its mirror number their rows differently. No
  one reported it; it was visible in a render as a denser right-hand side;
- **a "defect" that was not real.** A check said the column's vertical strut
  ran down the centreline through its digit. It measured *plan* distance only,
  and struts are 3.4 mm tall where a number plate is 4.0 mm thick — a strut
  crossing a digit in plan is buried inside the plate. Four separate "fixes"
  built on it came back out again;
- the build report billing the set for 44 runners and 3 marker plates. It
  totalled the parts by row index, and when a file was added to the export the
  indices moved under it. Quoted 271 g; the answer is 216;
- the renderer interpolating depth linearly in screen space. That is only
  correct under orthographic projection, and the error grows with the triangle,
  so nothing in the lattice ever showed it. The slab's top face is one
  57,000 mm² sheet and it showed at once, as wedges of z-fighting radiating
  from its vertices. `render.py` now interpolates 1/z, which is exact.

What software cannot tell us is the fit, or what a colour boundary looks like
coming off a printer. There are two test prints for that, in order:

- `fit-test-coupon.stl` — five posts either side of nominal, ~12 minutes. It
  carries **posts, not bores**, because the board is male: you try a real
  piece over each one.
- `stub-board-*.stl` plus `stub-pieces-x2.stl` — ~40 minutes. The stub is a
  66 x 61 mm corner of the **real board**, cut from the finished mesh rather
  than built to resemble it, so the slab, the lip, the engraved digits and the
  split posts are all exactly what the 285 mm version would print. It takes
  the corner over columns 6, 7 and 8: three numbers, six posts at the real
  pitch, and the stretch of lip that comes closest to a pad anywhere on the
  board. Two full markers come with it, one to seat and one to stack.

## Open questions

- **Red means PLA.** There is no red PETG on the shelf — `available-tools.md`
  lists PETG in yellow, reflex blue, orange, white and black, and red exists
  only as PLA Basic. So a red board is a PLA board, giving up PETG's toughness
  for a part that softens around 60 °C and creeps under load. For a board that
  lives flat on a table that is probably fine; a car in July would not be. The
  alternatives are an orange or black PETG board, or dyeing the plan.
- **Post fit.** `PEG_SOCKET_D` is 6.35 mm against a 5.90 mm post — a guess at
  shrinkage on a machine that has not been commissioned. The coupon settles it;
  the guess may be off by a tenth either way. With the board now in PLA, both
  halves of the fit are the same material, which removes one variable.
- **Warp.** 285 mm of solid 6 mm PLA is a much bigger flat area than the
  lattice ever was, and flat PLA that size is exactly what lifts at the
  corners. The heated chamber is on our side here; a brim may still be wanted.
- **The lip on a slicer.** 8 mm wide and 1.2 mm tall is six layers of a narrow
  ring right at the outline. Worth looking at in preview for a seam artefact
  before committing three hours.
- **The split post on a real print.** Geometrically the number is whole. What a
  two-material boundary running up the side of a 5.9 mm post actually looks
  like off the printer — colour bleed, a seam, purge staining — is a thing only
  a print will tell us. The stub is there to answer it for 11 g.
- **Empty lower half.** The numbers are all at the top, so the bottom of the
  octagon is bare plate. It looks deliberate in plan; whether it looks
  unbalanced on a table is a question for a print. The lip helps.
- **Print time.** Not yet measured. A 10%-infill slab is skin-dominated, so the
  estimate wants a real slice, not arithmetic.
- **Colour count.** The board is two colours, body plus numerals. Four player
  colours plus the runners means five more filaments; whether that is one print
  per colour or AMS swaps is a slicer decision, not a model one.
- **A tray or box.** Forty-seven loose pieces need somewhere to live.
  Deliberately out of scope for now.
- **Vinyl instead of inlaid numbers?** The cutter could do column labels as
  decals, and it has red vinyl in stock. Inlay was chosen because it needs no
  second operation and keeps the seating face flat — a decal on a face a piece
  stands on would not last.
