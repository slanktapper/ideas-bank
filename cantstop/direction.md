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
original brief asked for an open truss, and one was built: rings tied by
flat-bottomed struts with a diagonal per bay, braced out to the octagon by
twenty-four spokes. The catch is that a lattice is nearly all perimeter —
infill can reach 11% of a strut and 49% of a pad — so it cannot be lightened,
and at 128 cm³ it came out at about 140 g and was still the floppiest option
on the table. A slab's cost is its **skins**, which are a fixed 94 g over this
octagon however thick it is, and everything between them is whatever the
infill is set to. So 6 mm at 10% weighs 158 g — 13% more than the lattice —
and is roughly **twenty-three times** as stiff in bending (sandwich model: two
0.6 mm skins 5.4 mm apart plus a 10% core; 4 mm would be nine times, 10 mm
seventy-six). That is the trade, and it is why the wireframe lost.

**And it is deleted, not parked.** It stayed selectable as
`BOARD_STYLE = "lattice"` long after the decision was made, and the cost of
that was not the dead code: it was that every parameter, every branch and
twenty-odd checks went on being carried and re-run against a board nobody was
ever going to print. What it eventually produced was a *failing* check about a
pad that does not exist, on a build of a board that does not exist. `git log`
has it if it is ever wanted back. There is one board now, and every check in
`test_fit.py` runs against it every time.

**The interface runs male-up throughout.** The board offers a post; a piece has
a socket underneath and a post of its own on top; so a piece drops onto the
board, and the next piece drops onto that one, with one geometry doing both
jobs. A piece seats when its **skirt** lands on the face below — the plate, or
the top face of the piece beneath it — never when a post bottoms out, so stack
height is exactly 6.30 mm per piece, every time.

Two things follow from male-up that were not obvious going in. The board has
**no through-holes at all**, which retires a whole class of defect. And the
seat is a wide annulus rather than the rim of a ring, which is a far
steadier thing for a 17.5 mm piece to stand on — which in turn is why the posts
can be only 2 to 3 mm long.

**Six shapes, one interface, one envelope.** Each player gets a different
piece — a counter, a crown, a saucer and a cog — the runner is the fifth, and
the active-player marker is the sixth.

Each carries a **number**, which is its position in `PIECE_STYLES`:

| # | Shape | Whose | Stacks? |
| --- | --- | --- | --- |
| 1 | counter | player A | yes |
| 2 | crown | player B | yes |
| 3 | saucer | player C | yes |
| 4 | cog | player D | yes |
| 5 | runner | shared | yes |
| 6 | active | one each | **no** — square, 23.0 mm tall |

The numbers exist so a piece can be named in one character — in conversation,
in a render, in a print note, in a commit message — instead of "the round
one" having to do that work. They are fixed: a number, once given out, stays
with its shape, and a new shape takes the next free one rather than shuffling
everything below it and silently renaming four pieces that are already
printed. `test_fit.py` spells the mapping out literally so a reordering fails
loudly instead of being agreed with. `renders/09-piece-catalogue.png` is the
table drawn, and `renders/piece-<n>-<style>.png` is each one on its own.
What none of them may change is the socket underneath, the post on top, the
skirt that seats and the 6.30 mm body: player A stacks on player B, so every
piece has to accept every other one and add exactly the same height doing it.
`test_fit.py` builds all twenty-five pairings and measures the rise.

**Terminal pieces are exempt from the stacking rules, and only those.**
Piece 6 has no post: nothing lands on it, it is the end of a stack by
construction. So it owes nothing to a seat above it and it is free of the
8.45 mm that makes stack pitch exact — holding it to that number would be
cargo cult. What it still owes is everything on the way *in*: the same
socket, the same whole flat bottom, the same 17.5 mm footprint, because it
sits in a cell like anything else. `params.py` splits `PIECE_STYLES` into
`STACKING_STYLES` and `TERMINAL_STYLES`, and `test_fit.py` is careful about
which rule asks which list.

**And none of the stacking ones may change its size.** Every piece is 17.5 mm
across and 8.45 mm tall, to the micron. That is a rule rather than a ceiling, and the
difference matters: a ceiling is passed just as happily by a piece 2 mm short
of it, which is exactly how the runner stayed 16.5 x 10.45 through a resize
that took every marker down. Nothing caught it, because every piece rule in
`test_fit.py` was written over the four player styles and the runner is not
one of them. The checks now run over `B.PIECE_STYLES`, all five, and they
measure the SPREAD of width and height rather than their maximum.

**17.5 mm, and 20 does not exist.** 20 was asked for. The tightest spacing on
the board is column 7, whose thirteen cells sit 19.58 mm apart centre to
centre, so two 20 mm pieces in adjacent cells of that column would intersect
by 0.42 mm. Buying it means 22 mm of row pitch there, which is 29 mm more
lens than the board has and a roughly 304 mm octagon against a 300 mm
dual-nozzle bed. 17.5 is what the 19.58 allows with 2.08 mm of air left
between two pieces and 4.5 mm along a row — a 21% jump on 14.5 with nothing
on the board moving at all. The cells have not shifted; the pieces have grown
into space that was already there.

That did cost one rule. Neighbour clearance was 3.0 mm, which is what held
the pieces to 16.5; it is `PIECE_GAP_MIN` now and it is 2.0. The printed
board is what argued it down.

### The seat contract

What that leaves free is the silhouette, and it is less than it looks. Two
faces have to agree for a stack to sit straight — the bottom of the piece
going on, and the top of the piece underneath — and `params.py` states that
agreement once rather than letting each shape happen to have it:

It is **deliberately asymmetric**, because the two faces are not doing the
same job:

- **`SEAT_BOTTOM_R` = 7.30** — every piece's bottom is a *whole* flat
  annulus from the socket mouth out to here. No gaps, no exceptions. Which
  means a top may put its support wherever it likes inside the band and be
  certain of landing on something, at every rotation, with no case left to
  reason about.
- **`SEAT_MIN_FRAC` = 18%** of that band — all the top has to do is carry
  *enough*, and at least that much again in each of six sectors so nothing
  is held up on one side.
- **`SEAT_MIN_ARM` = 4.80** — and carry it *out there*. Area alone would let
  a piece balance on a pip round the post; what stops a stack leaning is the
  moment arm, so the area-weighted mean radius of the support has a floor of
  its own. The crown's six pads come in at r6.30, the best arm of the five.

The rule before this one was symmetric — 42% on both faces and a continuous
core ring on both — and it sounded stricter while being worse. It forced
every piece to keep a wide flat table at full height in the middle, and that
table is precisely what stopped the crown reading as a crown: points cannot
look tall standing next to a disc of their own height. `test_fit.py` proves
the new one the same way, stacking all twenty-five pairings at seventy-two
relative rotations each and taking the worst contact it can find.
- **`SEAT_SECTORS` = 6** — what is out beyond the core has to be spread, so
  every 60° sector carries its share and nothing is held up on one side.
- **`BOTTOM_FLAT_H` = 0.40** — the bottom is *flat*: one plane at z = 0 with
  vertical walls above it. No knife edges, no taper running out to nothing,
  and a first layer that is the face the piece will stand on for the rest of
  its life.
- nothing may exceed `PEG_MAX_R`, or pieces touch in adjacent cells;
- printed flat with no supports, so no surface may overhang more than 45
  degrees. A profile may widen going up by at most a millimetre of radius per
  millimetre of height, and the saucer's underside sits on that line.

All of it is measured by **area, on the finished meshes** — the crown's
points and the saucer's lugs appear after the lathe, so a profile knows
nothing about either.

### What each shape does with that

- **1 counter** — the plain waisted spool. Nothing to explain.
- **2 crown** — a band, six tapered points standing on it, an empty middle,
  and the post rising out of a column barely wider than itself. It took four
  goes. A disc with shallow V notches nicked out of the edge read as a gear.
  Square merlons round an open trough read as a castle turret. Cones cut into
  a thick rim read as dimples drilled in a bowl — **a cut can put holes in a
  wall but it cannot turn the wall into six separate things standing up**. So
  the points are added, like the saucer's legs and for the same reason.

  **Each point is a pyramid on a pyramid, and a blade rather than a bollard.**
  It narrows to a waist and flares back out to a knob — the shape half the
  drawn crowns have, and the only thing on this piece a finger can get hold
  of, since a plain taper just slides out from between two fingertips.

  A lathe makes a spike with a *circular* section, as wide through the wall
  as it is along the rim, and six of those read as a ring of little posts
  whatever their profile does. A drawn crown's points are flat: wide along
  the band, thin through it, standing right out at the edge. So the section
  is squashed after it is turned — 0.62 through the wall, **1.72 along the
  rim** — and cut to four facets rather than sixty-four, which is crisper,
  closer to the drawn ones, and the easiest thing a printer ever laid.

  **The points overlap at the foot, and the foot is STRAIGHT.** That second
  part is the whole of it. The foot was a cone running from r2.35 up to the
  waist, and measured at its widest it overlapped its neighbours by 1.53 mm
  — every millimetre of which was under the floor. A cone narrows the whole
  way up, so by the time it came out at z3.00 it was down to r1.76, which is
  6.04 mm along the rim on a 6.55 mm spacing: half a millimetre **apart**.
  The overlap was real and invisible, which is the worst kind, and it is why
  there is now a check that measures the width where the foot *leaves the
  floor* rather than where it is widest.

  So the foot holds r2.20 until 0.40 mm above the floor and only then draws
  in. That is 7.57 mm along the rim — a millimetre of overlap on each side,
  out in the open — and the six feet are one continuous scalloped rim that
  six blades rise out of. It is both what a drawn crown looks like and what
  makes them survive a box: a blade standing on its own at this scale is a
  thing waiting to snap off. Reach is 7.91, inside the band's own 8.20, so
  nothing pokes out past the edge of the piece. The knobs still clear each
  other by 1.18 mm, and there is a check on that too — the gaps belong up at
  the top, where they read as a crown, and a piece whose points touch all the
  way up is a cup.

  The waist moved **up** 1.10 mm at the same time, to z 4.70, which is what
  makes the foot read as a pyramid rather than a stub: it rises 1.70 mm clear
  of the floor.

  **That rise is not free, and it is the tightest number on the piece.** The
  squash multiplies the flare, so the limit is dr/dz ≤ 1/1.72 — raising the
  waist shortens the rise the flare has to happen over, and the flare gets
  steeper for it. At a knob of r1.61 it came out at 44.6°: inside the 45 and
  *passing*, and far too close to it to want to print. r1.59 puts it back to
  43.7°. There is no more room here — widen the foot again and the waist has
  to come back down to pay for it. `test_fit.py` checks this separately,
  because the points are turned and *then* squashed, and the ordinary
  overhang loop reads profiles, which know nothing about the squash.

  **The floor came up to z 3.00.** It sat at 1.95, which made the middle of
  the crown a well nearly two thirds of the piece deep, and from anywhere but
  straight overhead what you saw was the inside of a bowl with some points
  behind it. At 3.00 it is a shallow tray: the eye reads a band with points
  standing out of it, which is the thing. It also buries the bottom third of
  each foot, so the points grow out of the rim instead of being parked on it.

  The knobs have flat tops dead level at 6.30 because the next piece stands
  on them and on nothing else. Six of them is 31 mm², 24% of the band and
  comfortably over the 18% the contract asks for. That is tight on purpose and
  the crown is what made it tight: a blade puts a third less area up there
  than a round spike did. What it buys back is **reach** — r6.60, the longest
  arm of any piece — which is what actually stops a stack leaning.
  `SEAT_BAND_R` went 7.30 → 7.40 to meet it, which costs nothing: every
  bottom is whole out to the cog's 7.45 root anyway, and that is the number
  that caps it.
- **3 saucer** — a flying one. A whole disc base on the ground, four square
  landing tubes standing on it with daylight between them, a hull sweeping
  out to a thin brim at the full radius, a domed top, and six rectangular
  pads on the dome for the next piece to stand on. The legs and the pads are
  *added*, not cut: four vertical tubes and six flat bars, none of which is a
  surface of revolution, and pretending otherwise is what produced the two
  versions before this one.

  The height budget is the whole difficulty and it shows. A brim can only
  flare at 45 degrees, so the hull's underside is at 44.8 and there is no
  curvature left to spend down there — the curve that survives is on the
  dome, which goes up and IN and so can bend as it likes. Lifting the hull
  high enough for the legs to read as legs costs the dome its height: what is
  there is 1.45 mm of it. Everything on this piece is a trade against the
  same 6.30 mm.
- **4 cog** — a spur gear: one straight cylinder, no taper and no flare
  anywhere, with ten square slots milled out of the rim. It was a barrel with
  ten *round* flutes cut into it, and a round flute leaves teeth with hollow
  flanks, which reads as a fluted column and not as a gear; the body also
  flared at both ends, so every tooth had a lip top and bottom and none of
  them stood straight. A straight radial **bar** leaves what a cutter leaves:
  flat flanks, a flat root, an arc tip, square ends.

  Cutting is right here where it was wrong for the crown and the saucer. A
  gear tooth is not a thing standing on a surface — it is what is *left* of
  the rim once the gaps are taken out, and cutting it that way keeps the tips
  on the piece's own 8.75 circle instead of poking past it at the corners.
  The teeth are 1.30 mm deep and cannot be deeper: the root has to stay
  outside `SEAT_BOTTOM_R` or the bottom stops being the whole annulus the
  seat contract promises.
- **5 runner** — three square-edged tiers and two deep grooves, all turned,
  with the flares at 44 degrees so they carry themselves.
- **6 active** — the active player's marker: the only piece that does not
  stack, and the only one in **two colours**. Everything else on this board
  is squat and solid; this is tall and hollow. A round flared foot with the
  socket in it, a slim square shaft webbed through all four walls, and a red
  octagonal cap with a raised white lip round its edge. 28.4 mm against a
  marker's 8.45, one per player.

  **The foot is round, and that retired two checks.** It was a 17.50 mm
  *square*, whose corners reach 12.37 mm from the cell centre against a
  circle's 8.75 — so it needed two tests of its own that every radius-based
  check in the suite was blind to: one for clearing its neighbours, one for
  keeping its corners off the raised lip. A round 17.50 foot is the same disc
  as every other piece, so the ordinary skirt checks cover it and both
  special cases are **gone** rather than left passing about a shape that no
  longer exists. What is still wide up high is the cap, and there is one new
  check for the only thing it can ever meet: another active piece's cap on a
  neighbouring cell.

  It is built as the **convex hull** of three outlines — the disc at the bed,
  the same disc a hair above it, and the shaft's square at the top. The
  second disc is what gives the piece a straight side before the taper
  starts, so it stands on a face and not on an edge. Nothing in the foot
  overhangs: the whole thing narrows as it rises.

  **Two materials, and the split is a plane.** The cap is red, everything
  below it is white, and the boundary is z = `ACTIVE_TOP_Z` — one flat cut
  across the piece, so the slicer changes filament once on the way up and
  never goes back. No interleaving, no purge tower to speak of, no seam to
  wander.

  The **lip is the exception, and it is deliberate**: white, sitting on top
  of the red cap, so the print goes white → red → white. That is the board's
  own trick upside down — there the body is dark and the top `RIM_CAP_H` of
  the lip prints in the numbers' colour; here the field is red and the lip is
  white all through. It means the white part contains two separate solids,
  the tower and a ring floating above it, exactly as `board-numerals.stl`
  holds sixty. The ring rests on the red cap, so it is supported.

  It ships as `piece-active-body.stl` and `piece-active-accent.stl`, in the
  same coordinates, landing in register only because neither has been moved.

  **The rib went up a quarter, from 0.45 to 0.56, and openness is what that
  cost** — 65% → 58% on the same cell pitch. The pattern is unchanged, same
  cells in the same places; the lines through it are simply heavier, which is
  the right lever, because the struts are what a dropped piece loses. It is
  still a **single bead**: 0.56 is 1.4 nozzles, which a 0.4 lays as one line,
  where two 0.42 lines would need 0.84. There is no width in between where
  the slicer tries to fit two and leaves a void down the middle of every rib,
  and `test_fit.py` holds it under 1.5 nozzles so there never is.

  The lip came down with it — **0.85 wide and 0.60 tall**, from 1.20 and
  0.80. The width is two perimeters, the floor for anything on this project
  that is a wall, and a rim standing on a face is one. The height is the same
  0.60 the board's own lip cap is, which is the thing it was modelled on.

  **The silhouette comes from the sketch, and it took a review to notice it
  had drifted off it.** The sketch is a section: a foot that *flares* from
  the full width of a cell into a slim shaft over about a sixth of the
  height, a long parallel shaft, a flat top. What had been built instead was
  a 24%-tall plinth barely narrower at the top than the bottom, a shaft at
  72% of the base width, and a solid pyramid cap eating the top quarter.

  The fat shaft was the root of it, and it came from one assumption nobody
  checked: **that a row of the surface pattern needed three cells across**,
  which needs a face of at least 12.4 mm. It does not. The print this is
  modelled on has narrow limbs carrying two, and a narrow face carries them
  at a *better* ratio of hole to rib than a wide one.

  **The shaft is hollow, and that is what makes four webs possible at once.**
  Every version until this one cut its pattern straight *through* the shaft.
  That works for two faces and cannot work for four: a cut opening the left
  and right at the same height as one opening the front and back would cross
  it in the middle and take the shaft apart. The old honeycomb dodged it by
  alternating — one row front and back, the next left and right — which means
  every face was blank at every other row, and no face was ever continuously
  webbed. A hollow shaft has no such problem: each web is cut through **one
  wall**, 1.20 mm deep, so the four never meet. What is left is a square tube
  with a web in each wall and four continuous corner posts holding it up, and
  you see in through the near web and out through the far one.

  **The web is a cobweb, and it is drawn by not drawing it.** Seed points are
  scattered over each face, their Voronoi diagram is taken, and every cell is
  cut away — so what is left is the *edges* of that diagram, which is a web.
  No line is ever drawn; the lines are what the cuts leave between them. Two
  rounds of Lloyd relaxation settle the seeds: none at all leaves slivers
  that the rib eats into bald patches, too many converges on a honeycomb,
  which is precisely the thing this is not. The seed is fixed, so the same
  commit gives the same STL.

  An **orb web** came before it — concentric octagon rings and radial
  spokes — and it was wrong for a reason worth keeping: a regular figure at
  this size cannot be open enough. See below.

  **THE RIB IS ONE EXTRUSION, NOT TWO, AND THAT BREAKS A PROJECT-WIDE RULE.**
  Everywhere else 0.85 mm is the floor, because everywhere else the thin
  thing is a **wall** — something that holds a shape, takes a load, or has to
  look solid, and a wall one bead wide is a defect. A web is not a wall. Its
  ribs are *struts*, laid as a single extrusion path: exactly what a slicer
  lays for infill, and what the print in `reference/` is made of.

  The arithmetic leaves no choice. A net of line *w* and cell *d* is
  (d/(d+w))² open. The drawing in `reference/active-web-wanted.png` measures
  **73% open with lines 3% of the shaft's width**. To reach 73% at w = 0.85
  you need 5 mm cells — one and a half of them across a 9 mm face. At
  w = 0.45 you need 2.5 mm cells, which is three and a half. **Two perimeters
  cannot make a web at this size**; they can only make a wall with holes in
  it, which is what three consecutive versions were, and why each one was
  rejected. This one is 65% open.

  **The 45° rule does not apply to a strut, and that is the only reason an
  irregular web prints at all.** The rule is about *surfaces*: a sloping face
  whose outer edge has nothing underneath it. A rib is not a face — each of
  its layers only has to land on the one below, and it has the rib's whole
  **width** to do that in. At half a rib of overlap the limit is
  arctan(rib/2 / layer): **62° at a 0.45 rib and a 0.12 mm layer**, against
  the 45° a surface gets. The same rib at 0.20 mm layers only reaches 48°,
  which is why this piece is sliced fine and the print guide says so.

  **The shaft is hollow, and that is what makes four webs possible at once.**
  Every version before this cut its pattern straight *through* the shaft.
  That works for two faces and cannot work for four: a cut opening the left
  and right at the same height as one opening the front and back crosses it
  in the middle and takes the shaft apart. The honeycomb dodged it by
  alternating — one row front and back, the next left and right — which is
  why no face was ever continuously webbed. Each web is cut through **one
  wall**, 1.20 mm deep, so the four never meet. Four faces, four different
  webs, four continuous corner posts, and you see in through the near web and
  out through the far one.

  **The 0.90 mm frame** round each face is the only part of a wall that is
  not web, and it is what ties the web into those corner posts. It is two
  perimeters where the ribs inside it are one.

  **The web runs the whole shaft, and getting it there cost the socket's
  roof.** The hollow used to wait for the socket's roof cone to close at
  z6.72, which left four millimetres of bare shaft under the web — the blank
  band this design kept being judged on. It does not have to wait: the core
  is a 3.30 half-width box and the cone at the foot's own top is only r2.12,
  so there is 1.18 mm of floor between them. The core simply swallows the
  roof, and the bore opens into the hollow instead of being capped.

  Nothing is lost by that. A piece seats on the **top face of the one below
  it**, never on the inside of its own socket, and an open bore has no
  ceiling to bridge — so the piece went from three bridges to two by
  extending the web, which is not the usual direction of travel.

  **The cap is an octagon, like the board**, turned so its **flat sides run
  parallel to the shaft's**. That orientation is the whole reason it is as
  big as it is.

  The cap has to cover the square shaft or the top stops being an octagon,
  and a square of half-width 4.50 has its corners 6.364 out. *Which part of
  the octagon has to reach that far depends entirely on how it is turned:*

  | Orientation | What reaches the corner | Size needed |
  | --- | --- | --- |
  | Vertex at 45° | the **circumradius** | R ≥ 6.364, a 12.8 mm cap |
  | Flat at 45° (this one) | the **inradius**, only 0.924 of R | R ≥ 6.89, a 14.3 mm cap |

  So lining the flats up costs 1.5 mm of width and 0.2 mm of flare height.
  `ACTIVE_CAP_R` is 7.15, whose inradius of 6.606 clears the corners by
  0.24 mm — 6.90 would clear them by 0.011, which passes and is no place for
  a number to sit.

  The flare under it is the **convex hull** of the shaft's square top and the
  cap's octagon: both outlines are convex, so their hull is exactly the solid
  between them. Its steepest face is the square-on one — a face of the shaft
  to the octagon flat parallel to it, 2.106 out over 2.45 up, **40.7°**.

  **That figure is measured off the mesh, not derived**, because which face
  is steepest moves with the orientation. Sizing it by the longest *radial*
  run instead gives 2.279, out at 22.5° to a vertex — and that is simply the
  wrong measurement. A face's slope is its run *perpendicular to itself*, and
  the diagonal run is spread across a triangle that leans less than the
  square-on face does. The radial figure happens to be conservative here, but
  it is not conservative *by design*, and there is no reason to think it errs
  the same way for the next shape.

  Rotating the cap also turned up a live bug in the *other* check. The
  "profile" `piece_profile_of` hands the overhang and wall checks is the
  **inscribed half-width** at each height — for the square parts, exactly
  half the side. The cap had gone in as its *circumradius*, so the loop was
  comparing a circumradius at the top against a half-side at the bottom,
  which is not the slope of anything: it read the flare as 47° where the mesh
  measures 40.7°, and failed. It goes in as R·cos(π/8) now, and the two
  agree to the second decimal.

  The height the cap costs was taken back off the shaft rather than added to
  the piece, so it still finishes at 28.40.

  **Two bridges, both deliberate.** An irregular web has cells that come to a
  peak and cells with a flat top; the flat ones are bridges, and the widest
  measures 2.66 mm. The **top plate** is the other: it spans the 6.60 mm
  core, anchored on all four walls, and it is the trade for having the web
  run to the top. The 45° pyramid that used to roof the core bridged nothing
  and cost a solid band a third of the shaft's height.

  **Square is safe, and it is checked rather than hoped.** Columns are
  22.0 mm apart and the tightest row pitch is 19.58, and two axis-aligned
  squares miss each other when *either* axis clears — so a 17.5 mm square is
  fine on both. What a square does reach further into is the corner: 12.37 mm
  from the cell centre against a circle's 8.75, which every radius-based
  check in the suite is blind to. So `test_fit.py` puts the footprint on all
  83 cells: 2.08 mm to the nearest neighbour, and 5.40 mm of flat between a
  corner and the raised lip.

  It stays 17.5 wide, which keeps every piece in the set the same width — the
  one envelope rule it still owes, since it sits in a cell like anything
  else. What it lost was the flange, not the footprint. The floor under that
  is 14.8: a square of side s covers the seat band when s ≥ 2 ×
  `SEAT_BOTTOM_R`, and below that it stops being able to sit on a crown.

Anything beyond the lathe is **cut where cutting works and added where it
does not**, and the line between the two turned out to be sharper than it
looked. A vertical cylinder taken out of the side is self-supporting whatever
its depth and the floor it leaves is an upward face, which is why the cog's
flutes are cuts. But a cut only ever *removes*, and three of the five shapes
wanted something to *stand up*: the saucer's legs, its pads, the crown's
points. Cutting the saucer's leg gaps out of a solid ring leaves a ceiling,
and a ceiling is either a bridge or an overhang; cutting the crown's valleys
into a solid rim leaves a rim with dents in it. Added, each of those is four
vertical walls and a flat top, printable from the first layer and shaped like
the thing it is meant to be.

**The pieces are counters, not pegs.** 17.5 mm across and 8.45 mm tall: a
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
**223 g** — 158 g of board at 10% infill plus 65 g of solid pieces.

`test_fit.py` passes 141 checks. The ones that earn their keep are the ones that
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
- `stub-board-*.stl` plus `stub-pieces-x6.stl` — about an hour. The stub is a
  22 x 55 mm strip of the **real board**, cut from the finished mesh rather
  than built to resemble it, so the slab, the lip, the engraved digits and
  the split posts are all exactly what the full board would print. It takes
  the top of column 7: the number, two posts at the board's tightest row
  pitch, and the stretch of lip that comes closest to a pad. One of every
  piece comes with it — the four markers, the runner and the active marker —
  so every shape gets seated and every pairing gets stacked. The active
  marker earns its place on that plate twice over: it shares the socket, and
  its weight sits further from the joint than anything else's.

  It used to take columns 6 and 7 together, to get a red post and a
  white-capped one onto one part. That has been printed and it works, so the
  strip is down to one column: what is being settled now is the socket fit,
  and that wants the smallest part that still has a real post under a real
  lip.

## Open questions

- **Red means PLA.** There is no red PETG on the shelf — `available-tools.md`
  lists PETG in yellow, reflex blue, orange, white and black, and red exists
  only as PLA Basic. So a red board is a PLA board, giving up PETG's toughness
  for a part that softens around 60 °C and creeps under load. For a board that
  lives flat on a table that is probably fine; a car in July would not be. The
  alternatives are an orange or black PETG board, or dyeing the plan.
- **Post fit, third value — and now bracketed.** `PEG_SOCKET_D` is the one
  number here that only a print can settle, and there is a print at each end
  of it now:

  | socket | diametral | verdict |
  | --- | --- | --- |
  | 6.35 | 0.45 | printed — too loose |
  | 6.13 | 0.23 | printed — a little tight |
  | **6.24** | **0.34** | the midpoint, awaiting a print |

  6.35 was a guess made before anything had come off the machine. The stub
  printed at size, so that slack was insurance against a problem that did not
  materialise — but halving it overshot, and every shape came out tight in
  the hand. 6.24 splits the bracket, which is as good as this number gets
  without a third data point. Below roughly 0.15 diametral a fit stops being
  a fit and becomes an interference the plastic has to absorb, so 0.23 was
  already near the floor and the move had to be upward.

  The board's post is untouched at 5.90 throughout, so every stub printed so
  far is still the right fixture to try new pieces on.
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
  of 10, 11 and 12 and the 16.5 mm pieces, so a second one is worth a few
  grams before the board itself goes on.
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
