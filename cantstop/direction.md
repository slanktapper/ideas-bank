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
**regular octagonal frame** — all eight edges the same 116.7 mm. The lens does
not reach the corners of its own bounding box, which is exactly the point: the
cut-off triangles are where the number tabs and the bracing spokes live.

The board is not a plate with holes in it. It is a **wireframe truss**: every
cell is a pad with a post standing on it, the pads are tied to each other by
flat-bottomed struts with one diagonal brace per bay, then tied out to the
octagon by twenty-four radial spokes. Most of the footprint is open air.

**The interface runs male-up throughout.** The board offers a post; a piece has
a socket underneath and a post of its own on top; so a piece drops onto the
board, and the next piece drops onto that one, with one geometry doing both
jobs. A piece seats when its **skirt** lands on the face below — the pad top,
or the top face of the piece beneath it — never when a post bottoms out, so
stack height is exactly 9.40 mm per piece, every time.

Two things follow from male-up that were not obvious going in. The board has
**no through-holes at all**, which retires a whole class of defect: a strut
cannot plug a hole that does not exist, and the only rule left is that struts
stay below the pad tops. And the seat becomes a 3.0-to-6.6 mm annulus rather
than the rim of a ring, which is a far steadier thing for a 13.2 mm piece to
stand on — which in turn is why the posts can be only 3.2 mm long.

**The numbers sit at the top of each column, on their own tabs.** Every
column's top cell steps 22 mm further out than the ladder pitch, and the
number rides on a small tab below that post, in line with the column, with a
4 mm gap between the two. Nothing ever stands on a tab, so seen from above a
number is always just an orange digit on black.

That gap is the whole point, and it took three arrangements to land on. A post
standing in the middle of a glyph cannot leave the glyph readable: centring
the post on the digit and colouring it to match gave a black moat and an
orange dot punched through every number, and 6, 8 and 9 became
indistinguishable. The post has to be off the number. The digits are embossed
rather than inlaid for the same reason — nothing seats on a tab, so there is
no reason to give up the crispness of raised lettering.

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
is parametric, so the ladder, cell pitch, ring size, lattice density, frame
shape, shield stand-off, piece profile and fits are all one edit in `params.py`
away from a different board. Ships STLs, test renders, and a design test suite.

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

python3 test_fit.py      # 46 design checks — run this after editing params.py
python3 build.py         # every STL into stl/, every render into renders/
python3 build.py --stl   # STLs only            (~3 s)
python3 build.py --fast  # quarter-res renders  (~9 s total)
```

Full build is about 25 seconds. `stl/` and `renders/` are regenerated from
scratch and safe to delete.

Everything dimensioned lives in `params.py`. Change a number there, run
`test_fit.py`, rebuild. See `print-guide.md` before printing anything.

## Where it stands

Designed and verified in software; **nothing has been printed yet.** The board
is 293 × 293 × 7.2 mm, which fits the H2D's 325 × 320 mm bed with 32 mm spare
in X and 27 mm in Y. A full set is about 273 g at 100% infill.

`test_fit.py` passes 46 checks, including a probe of every cell's seating
annulus against the fused mesh — the male-up analogue of the old bore probe,
and the thing that would catch a strut, spoke, shield or digit standing where
a piece has to sit.

Six real defects have been caught by this loop rather than by a print:

- a drop strut printed straight across every column numeral;
- in fixing that, a board that quietly became two detached bodies;
- a top-chain strut at frame section clipping the bottom corner of each digit
  by 0.19 mm — the octagon is the frame now, so nothing inside the lens runs
  at frame section;
- **a piece claiming a summit hiding that column's number.** The tests did not
  catch that one and `renders/06-assembly.png` did: a marker sitting on "2"
  covered it completely, and a claimed number needed about a 70 degree view to
  read. `test_fit.py` now computes that angle from the geometry;
- the first version of that sightline test said *every* number was hidden,
  which the renders plainly contradicted. It was modelling a piece as one fat
  cylinder; the body is 13.2 mm across but only 13.4 mm tall, and the post
  above it is 5.9 mm. Model both and the answer matches what you can see;
- with the number moved under the summit, the column's own vertical strut ran
  straight down the centreline through it, and the top chain grazed the digit's
  upper corners by 0.28 mm — **and neither was real.** That check measured plan
  distance only. Struts stand 3.4 mm tall and a number plate is 4.0 mm thick,
  so a strut crossing a digit in plan is buried inside the plate, not printed
  across the number. The rule that actually matters is that nothing standing
  *proud* of a plate goes near one, and that the digit lies wholly within its
  plate. Measured that way the only members taller than a box are the eight
  octagon edges, and the nearest passes 3.4 mm clear — which let the summit
  step, the shield drop, the separate digit centre, the reconnecting necks and
  the whole placement branch all come back out again.

What software cannot tell us is the fit. That is what `fit-test-coupon.stl`
is for, and it is the first thing to print. **It now carries posts, not
bores**, because the board is male: you try a real piece over each one.

## Open questions

- **Post fit.** `PEG_SOCKET_D` is 6.35 mm against a 5.90 mm post. That is a
  guess at PETG shrinkage on a machine that has not been commissioned. The
  coupon settles it; the guess may be off by a tenth either way. Note the
  socket is in the PLA piece and the post is in the PETG board, so the fit
  spans two materials — print the coupon accordingly.
- **Board rigidity.** 293 × 293 mm of 7.2 mm lattice has not been picked up
  yet, and the collars are shorter than they were. If it flexes, the fixes in
  order of preference are `FRAME_H`, then `DIAGONALS = "full"`, then
  `STRUT_H`. The octagon and its twenty-four spokes should carry most of it.
- **Seated-angle legibility.** From above a number is always clear. At a
  seated angle the only thing that can shadow a tab is a piece two cells down
  the same column, which needs a 38 degree view to see past. `SUMMIT_STEP`
  buys that back a degree or so per millimetre of board if it matters on a
  real table.
- **Empty lower half.** The numbers are all at the top, so the bottom of the
  octagon is lattice and spokes only. It looks deliberate in plan; whether it
  looks unbalanced on a table is a question for a print.
- **Print time.** Not yet measured. ~126 cm³ of thin-walled lattice is
  perimeter-dominated, so the estimate wants a real slice, not arithmetic.
- **Material.** PETG for the board (tough, does not creep), PLA for the
  pieces (crisper small features). Untested assumption.
- **Colour count.** The two-colour split is body plus numerals. Four player
  colours plus the runners means five more filaments; whether that is one
  print per colour or AMS swaps is a slicer decision, not a model one.
- **A tray or box.** Forty-seven loose pieces need somewhere to live.
  Deliberately out of scope for now.
- **Vinyl instead of printed numbers?** The cutter could do column labels as
  decals. A raised emboss was chosen because it needs no second operation, but
  decals would allow colour without a filament change, and a tab is a face
  nothing ever stands on, so one would survive.
