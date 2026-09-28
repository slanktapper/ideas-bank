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
**regular octagon** — all eight edges the same 118.1 mm, and the board is
pinned to exactly **285.0 mm** across rather than being sized to its content.

A regular octagon is square by definition, and the board is a **two-filament**
part: two nozzles on one toolhead cost 25 mm of X, so the usable bed is
300 × 320, not 325 × 320. The board's width is therefore the binding
dimension and everything has to fit inside it.

What it costs is the piece diameter, and that was measured rather than
guessed. With 16.5 mm pieces a square board could not get under 291 mm even
after giving up the title, the level 6/7/8 spacing and every millimetre of
clearance between pieces. At **14.5 mm** the column pitch comes down to 22.0
and the row pitch to 18.0, and 285 mm then holds the title, the level
spacing and 5.07 mm between neighbouring pieces, with 15 mm of bed to spare
in X and 35 in Y.

`OCTAGON_ACROSS` pins the size; 0 goes back to sizing it to the content.
Because the margin is then whatever is left over rather than something asked
for, `test_fit.py` measures it: 14.12 mm, against the 12 the lip and its
clearance need.

At that point the frame is about as small as this content allows. The eleven
summits sit on a staircase that runs very nearly parallel to the corner cut,
so they bind it together rather than one of them binding it alone, and the
three constraints have all but converged: X wants a half-span of 134.0 mm,
Y wants 140.4, the diagonal 140.3. Dropping the outer columns further buys
nothing now, and shrinking the numbers and letters buys 1 mm per millimetre
of cap height, which is a poor trade. The columns do not all share one row
pitch: the middle columns step down by a fraction of a box and the rest
follow by whole ones, which flattens the top of the lens and pulls its
shoulders out towards the frame instead of leaving it a narrow spike in a
wide octagon.

The board is a **6 mm solid octagonal slab, printed at 10% infill**, with a
raised lip 8 mm wide around the edge. Every cell is a post standing on that
plate; the plate itself is the seat. Around the outside the lip stands 1.2 mm
proud — the same relief the numbers are sunk by, so the board has one depth
step and not two — and its **top 0.6 mm prints in the numbers' colour**, so
the board is framed in white as well as numbered in it. The lip is split
rather than handed over whole, which puts a white cap on a red edge instead of
a white wall standing on red. `RIM_CAP_H` has to be a whole number of layers
or the slicer rounds the border a layer thicker or thinner than asked; that is
the one parameter here tied to a slicer setting, and `test_fit.py` checks it.

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
height is exactly 6.30 mm per piece, every time.

Two things follow from male-up that were not obvious going in. The board has
**no through-holes at all**, which retires a whole class of defect. And the
seat is a 3.0-to-8.3 mm annulus rather than the rim of a ring, which is a far
steadier thing for a 16.5 mm piece to stand on — which in turn is why the posts
can be only 2 to 3 mm long.

**Four shapes, one interface.** Each player gets a different piece: a
counter, a crown, a saucer and a cog. What none of them may change is the
socket underneath, the post on top, the skirt that seats and the 6.30 mm
body — player A stacks on player B, so every piece has to accept every other
one and add exactly the same height doing it. `test_fit.py` builds all
sixteen pairings and measures the rise.

What that leaves free is the silhouette, and it is less than it looks:

- the top face is what the **next** piece stands on, so it cannot taper away
  to a point. It has to keep an unbroken seating ring 3 mm wide, which puts a
  floor of about 6 mm on the top radius. No cones, no spires — the saucer's
  dome is shallow because 8.25 down to 6.10 is the whole budget;
- nothing may exceed 8.25 mm of radius, or pieces touch in adjacent cells;
- printed flat with no supports, so no surface may overhang more than 45
  degrees. A profile may widen going up by at most a millimetre of radius per
  millimetre of height, and the saucer's brim sits exactly on that line.

Anything beyond the lathe is **cut, never added**. The crown's points are six
45-degree cones taken out of its rim, and the cog's flutes are ten vertical
cylinders taken out of its side: both leave a part that narrows all the way
up, which is the condition for printing without support. The saucer's base is
6.60 where the others are 8.25, because a brim has to stand proud of what it
sits on or the thing reads as a bell.

**The pieces are counters, not pegs.** 16.5 mm across and 8.45 mm tall: a
squat disc you pick up with two fingers and can see past. The first version
was 13.2 x 12.6 — taller than it was wide — and read as a peg standing on the
board rather than a counter sitting in it. A third off the height and a
quarter onto the width fixes that and, because volume went one way as fast as
the other, costs nothing: 0.98 cm3 against 1.00.

The one thing that had to give is the socket roof. It is a 45 degree cone so
it self-supports, and a full cone needs the socket's own radius in height —
3.18 mm on top of the 3.60 the socket takes — which a 6.30 mm body has not
got. So the cone is truncated: it climbs until 0.80 mm of solid is left above
it, and the 2.55 mm of flat that remains is bridged. A 2.55 mm bridge is
nothing; the rule that matters is that it stays small, and `test_fit.py`
measures both the 45 degrees and the span off the real profile.

**The title is spelled out along the bottom.** One letter per column,
engraved into the plate exactly as the numbers are and printed in their
colour: CAN'T under 2 3 4 5, STOP under 9 10 11 12, and nothing under 6, 7
and 8 — the hole they leave in the middle is the word space. The lower half
of the board was a cell field with nothing to read on it; this is what goes
there.

The letters hang below each column's own bottom cell rather than sitting on
one straight baseline, so the title follows the underside of the lens and
mirrors the numbers' cascade at the top. That is not a stylistic choice. An
octagon has its corners cut off, so a letter that is both far to one side and
far down is the most expensive content that can be put on one: levelling the
title takes the board from 310 mm across to 395, which is off the bed by
70 mm. `TITLE_FOLLOW` blends between the two if it is ever worth revisiting.

**Three columns are level at the top, not five, and 6, 7 and 8 hang lower.**
6, 7 and 8 give up nothing, so the top of the lens runs flat across three
columns instead of coming to a point. Their bottoms used to be level too, and
that was the problem: the same span with 9, 11 and 13 cells in it means
column 7's dots are packed at 20 mm while column 5's are strung out at 30.

`COLUMN_DROP` lengthens a column at the bottom only. Columns 6, 7 and 8 carry
no title letter, so the plate directly below them is empty — dropping their
bottoms 14 and 19 mm fills it and evens the spacing (7 goes 18.0 → 19.6 mm,
6 goes 21.6 → 23.0), and costs nothing at all, because what sets the bottom
of the board is the letters either side of that gap and not the dots. The
lowest pad now reaches −133.9 mm against a title bottom of −134.8.

**5 and 9 take half a step down.** They were level with 6, 7 and 8, which
left 4 and 10 dropping a full 25 mm off each end of a flat run of five —
a step that read as a mistake rather than as a shape, and left an empty
wedge of plate between the numbers 4 and 5 under the corner cut. They now
carry a 12.5 mm shortfall, which splits that 25 into 12.5 and 12.5 and walks
the numbers down to the corner evenly.

The same 12.5 goes into `COLUMN_DROP`, and the two cancel at the bottom: the
shortfall lifts that end and the drop puts it back, so only the top of those
columns moves. Nothing below the midline changes, the title stays where it
was, and column 5's nine dots close from 27.0 to 25.4 mm — a step towards
column 6's 23.0 rather than away from it. It also unpins the frame. With 5
and 9 level it was the top outer corner of *their* number box that bound the
octagon's diagonal; half a step takes that corner off the cut, and the spare
inside the 285 mm goes from 12.13 to 14.12 mm.

**Alternate columns have white post tops.** Eighty-three identical red dots
on a red plate give the eye nothing to follow, and the columns are what a
player has to read. `POST_CAP = "even-columns"` prints the top 0.60 mm of
every post in 2, 4, 6, 8, 10 and 12 in the numbers' colour, so neighbouring
columns alternate and each one reads as its own line.

The cut lands exactly on the post's chamfer, which is the whole point: what
you see from directly above is all accent, and the straight sides stay in the
board's colour, so it is a white dot rather than a white peg. It costs no
extra colour changes either — the accent filament is already on those layers
for the digits and the split summit posts.

Alternating by ROW instead (`"even-rows"`) was rendered and rejected. The
columns run at six different row pitches, so the pattern does not line up
between them and the board reads as speckle. `"all"` and `"none"` are there
too; every summit post is excluded whatever the setting, because its top is
already split by its digit and flooding it with the number's colour is the
exact failure that split exists to prevent.

**Every number is the same size, one digit or two.** A two-digit number is
about 26 mm wide at this 16 mm cap height and a one-digit one is 12, and the
first version dealt with that by scaling 10, 11 and 12 down to fit — which
took their cap height down with their width, so the three of them came out
8.6 mm tall against everyone else's 16 and read as a smaller, separate set of
labels. They are condensed in X only now: same 16 mm height as the rest, 8%
narrower than natural, which is not visible next to a difference in height.

The ceiling on that is not typographic. A piece seated on the next column
reaches to within 13.75 mm of this column's centre, so a number wider than
27.5 mm would have its ends stood on by the column next door. At 24 mm there
is 1.75 mm in hand, and `test_fit.py` checks every cell on the board against
every column's digits.

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

**Does:** the board, the playing pieces, and the files to print them. The
board is **two files and needs both** — `board-body.stl` in the board's
colour and `board-numerals.stl` in the numbers'. A single-colour variant
existed and was dropped: it was a second definition of the same object that
nothing downstream read, it diverged twice without anyone noticing, and by
then the numbers, title, border and column stripes were all in the second
filament anyway. Everything
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

python3 test_fit.py      # 99 design checks — run this after editing params.py
python3 build.py         # every STL into stl/, every render into renders/
python3 build.py --stl   # STLs only            (~6 s)
python3 build.py --fast  # quarter-res renders  (~12 s total)
```

Full build is about 50 seconds. `stl/` and `renders/` are regenerated from
scratch and safe to delete.

Everything dimensioned lives in `params.py`. Change a number there, run
`test_fit.py`, rebuild. See `print-guide.md` before printing anything.

## Where it stands

The **test stub has been printed and came out right** — the engraved numbers,
the split posts and the white cap on the lip all read as intended. The board
itself has not been printed. It is
285.0 × 285.0 × 9.2 mm, which fits the H2D's **dual-nozzle** envelope of
300 × 320 mm with 15 mm spare in X and 35 mm in Y. A full set is about
**205 g** — 158 g of board at 10% infill plus 47 g of solid pieces.

`test_fit.py` passes 99 checks. The ones that earn their keep are the ones that
touch the fused mesh rather than the parameters: a probe of every cell's
seating annulus, a check that every square millimetre the post covers comes
back in the number's colour, and — for the slab — that the lip is the same
width on every edge, clears the outermost pads by 4 mm, and is genuinely a
lip rather than a plate that came out 7.2 mm thick everywhere.

Defects this loop has caught rather than a print:

- a drop strut printed straight across every column numeral;
- in fixing that, a board that quietly became two detached bodies;
- **a piece claiming a summit hiding that column's number.** The tests did not
  catch that one and `renders/06-assembly.png` did: a marker sitting on "2"
  covered it completely. Accepted now, because by then the column is claimed;
- the first version of that sightline test said *every* number was hidden,
  which the renders plainly contradicted. It was modelling a piece as one fat
  cylinder; the body was 13.2 mm across but only 13.4 mm tall, and the post
  above it 5.9 mm;
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
- `stub-board-*.stl` plus `stub-pieces-x4.stl` — about half an hour. The stub is a
  72 x 115 mm corner of the **real board**, cut from the finished mesh rather
  than built to resemble it, so the slab, the lip, the engraved digits and the
  split posts are all exactly what the full board would print. It takes
  the corner over columns 6, 7 and 8: three numbers, six posts at the real
  pitch, and the stretch of lip that comes closest to a pad anywhere on the
  board. One of each of the four shapes comes with it, so every shape gets seated and
  every pairing gets stacked.

## Open questions

- **Red means PLA.** There is no red PETG on the shelf — `available-tools.md`
  lists PETG in yellow, reflex blue, orange, white and black, and red exists
  only as PLA Basic. So a red board is a PLA board, giving up PETG's toughness
  for a part that softens around 60 °C and creeps under load. For a board that
  lives flat on a table that is probably fine; a car in July would not be. The
  alternatives are an orange or black PETG board, or dyeing the plan.
- **Post fit, second value.** `PEG_SOCKET_D` started at 6.35 mm against a
  5.90 mm post — 0.45 mm diametral, deliberately loose because nothing had
  been printed and the machine had not been commissioned. The stub came off
  at size, so that slack was insurance against a problem that did not
  materialise, and the socket is now **6.13 mm: 0.23 mm diametral, half what
  it was**, which is 0.115 of a radius or about a quarter of a line width.
  The board's post is untouched at 5.90, so the stub already printed is still
  the fixture to try new pieces on. Below roughly 0.15 diametral this stops
  being a fit and becomes an interference the plastic has to absorb, so there
  is no third halving; if 0.23 is tight, the next move is up, not down.
- **Warp.** 300 mm of solid 6 mm PLA is a much bigger flat area than the
  lattice ever was, and flat PLA that size is exactly what lifts at the
  corners. The heated chamber is on our side here; a brim may still be wanted.
- **The lip on a slicer.** 8 mm wide and 1.2 mm tall is six layers of a narrow
  ring right at the outline. Worth looking at in preview for a seam artefact
  before committing three hours.
- **The split post on a real print.** Geometrically the number is whole. What a
  two-material boundary running up the side of a 5.9 mm post actually looks
  like off the printer — colour bleed, a seam, purge staining — is a thing only
  a print will tell us. **The stub answered it: the first stub printed clean**,
  numbers and lip both. What it was printed against was the narrower version
  of 10, 11 and 12 and the taller pieces, so a second one is worth 22 g before
  the board itself goes on.
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
