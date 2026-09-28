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
**true octagonal frame**: a 300 mm square with its corners cut at 45 degrees.
The lens does not reach those corners, which is exactly the point — the cut-off
triangles are where the number shields and the bracing spokes live.

The board is not a plate with holes in it. It is a **wireframe truss**: every
cell is a standing ring, and the rings are tied to each other by flat-bottomed
struts with one diagonal brace per bay, then tied out to the octagon by
twenty-four radial spokes. Most of the footprint is open air.

**The number is the top of the column.** Each column's topmost cell is its
summit, and the summit carries that column's number on a shield standing off
it on a short neck. The summit is an ordinary ring, so climbing a column and
landing on its number is an ordinary move — reaching the number *is* claiming
it. The shields lean outward rather than sitting straight above their rings,
so that the piece claiming a column does not hide the number it just claimed.

The playing pieces **stack**. Each piece has a pin on the bottom and a socket
on the top, same size, on the same axis. One interface does three jobs: the
pin drops into a board ring, or into the socket of a piece already there, so
player A simply sits on top of player B in a contested cell. The socket is cut
deeper than the pin is long, so a piece always seats on its shoulder rather
than bottoming out — stack height is exactly 9.40 mm per piece, every time.
The pieces are 13.2 mm across and the stub is only 3.2 mm: with a body that
wide the shoulder seats on a 3.2-to-6.6 mm ring and does the work of keeping a
piece upright, so the stub only has to locate it.

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

python3 test_fit.py      # 44 design checks — run this after editing params.py
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
is 300 × 300 × 5.5 mm, which fits the H2D's 325 × 320 mm bed with 25 mm spare
in X and 20 mm in Y. A full set is about 296 g at 100% infill.

`test_fit.py` passes 44 checks, including a probe of all 83 bores against the
fused mesh. Four real defects have been caught by this loop rather than by a
print:

- a drop strut printed straight across every column numeral;
- in fixing that, a board that quietly became two detached bodies;
- a top-chain strut at frame section clipping the bottom corner of each digit
  by 0.19 mm — the octagon is the frame now, so nothing inside the lens runs
  at frame section;
- **a piece claiming a summit hiding that column's number.** This one the
  tests did not catch and `renders/06-assembly.png` did: the white marker
  sitting on "2" covered it completely. A claimed number needed a viewing
  angle of about 70 degrees to read. Leaning the shields outward and standing
  them off 26 mm brings that to 40 degrees, and `test_fit.py` now computes
  that angle from the geometry so it cannot regress.

What software cannot tell us is the fit. That is what `fit-test-coupon.stl`
is for, and it is the first thing to print.

## Open questions

- **Bore fit.** `COLLAR_BORE` is 6.40 mm against a 5.90 mm pin. That is a
  guess at PETG shrinkage on a machine that has not been commissioned. The
  coupon settles it; the guess may be off by a tenth either way.
- **Board rigidity.** 300 × 300 mm of 5.5 mm lattice has not been picked up
  yet, and the collars are shorter than they were. If it flexes, the fixes in
  order of preference are `FRAME_H`, then `DIAGONALS = "full"`, then
  `STRUT_H`. The octagon and its twenty-four spokes should carry most of it.
- **Number legibility at a low angle.** 40 degrees is a seated player looking
  at the middle of the board, not the far edge. It is a geometric limit: a
  12.6 mm piece casts a shadow, and the only levers are standing the shields
  off further (which grows a board already at 300 mm), thickening them to lift
  the digits, or making the pieces shorter. Worth judging on a real print
  before spending board size on it.
- **Empty lower half.** The numbers are all at the top, so the bottom of the
  octagon is lattice and spokes only. It looks deliberate in plan; whether it
  looks unbalanced on a table is a question for a print.
- **Print time.** Not yet measured. ~141 cm³ of thin-walled lattice is
  perimeter-dominated, so the estimate wants a real slice, not arithmetic.
- **Material.** PETG for the board (tough, does not creep), PLA for the
  pieces (crisper small features). Untested assumption.
- **Colour count.** The two-colour split is body plus numerals. Four player
  colours plus the runners means five more filaments; whether that is one
  print per colour or AMS swaps is a slicer decision, not a model one.
- **A tray or box.** Forty-seven loose pieces need somewhere to live.
  Deliberately out of scope for now.
- **Vinyl instead of embossed numbers?** The cutter could do column labels as
  decals. Embossing was chosen because it needs no second operation, but decals
  would allow colour without a filament change.
