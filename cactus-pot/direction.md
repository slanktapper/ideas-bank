# cactus-pot

**Status:** prototype

## What it is

A printed cactus that drops into a printed flower pot, with its spines printed
as a separate part and press-fitted into sockets on the body. Both halves are
parametric code: the cactus here, the pot in `pot/` — see
[pot/direction.md](pot/direction.md). The cactus was rebuilt rather than edited
because the thing that was wrong with it — it read as a cartoon — is not
something you can edit out of a mesh.

## Why

The original cactus is a smooth capsule with cone spikes modelled into it. Two
separate problems:

- **It reads as a toy.** A real columnar cactus is ribbed from soil to crown,
  tapers, leans slightly, and carries its spines on raised pads along the rib
  crests. A smooth tube with spikes stuck on it is a cucumber with pins in it.
- **Spines printed as part of the body cannot be sharp.** Modelled onto a
  vertical part they are horizontal cantilevers: they need support, they print
  furry, and they come out blunt. Printed separately, standing point-up on
  their own pins, every layer is smaller than the one below and the taper comes
  out clean.

Splitting them also buys colour — spines in white or pale yellow against a
green body, with no multi-material printing on the big part at all.

## Scope

**Does:**

- The cactus body: ribbed trunk, two arms, areole pads, 110 spike sockets, and
  a spigot that drops into the socket in the pot's floor.
- The spike: one part, printed many times.
- Three test prints, in the order you would reach for them: a single pair —
  one socket in a tab and one spine, as `test-hole` and `test-spine` — that
  says in five minutes whether the fit is anywhere near; a fit-test coupon
  that steps the socket diameter either side of nominal, with each step
  engraved beside its hole so the answer can be read off the part instead of
  counted from an end; and a wedge of the real trunk that proves the joint on
  the curved ribbed wall it actually lives on.

  All three cut their sockets with the same `socket_cutter()` the cactus
  uses, so a test is never of a simplified hole. The single pair carries its
  areole pad for the same reason: the collar lands on a dome, and a flat tab
  would be testing a joint that does not get printed.
- Renders, so the shape is judged before filament is spent.

**Does not:**

- Model the pot. The pot is an input, a mesh, and the only things read from it
  are the socket, the floor and the rim.
- Glue anything. The joint is an interference fit; if it ends up loose, the fix
  is a different socket diameter, not adhesive.
- Try to be botanically exact. It is a saguaro in silhouette, not a specimen.

## Stack

Python 3.10+, `numpy` + `trimesh` with the `manifold3d` boolean engine, the
same combination `cantstop` uses. Renders go through `../3d-tools/render.py`.
No GUI, no CAD application, no OpenSCAD.

    python3 -m pip install -r requirements.txt

## How to run

    python3 build.py                  # stl/ and renders/
    python3 build.py --stl            # just the printable files
    python3 build.py --renders        # just the pictures
    python3 build.py --pot <pot.stl>  # measure the pot, and render it seated
    python3 colours.py                # stl/colour/ -- the two body filaments
    python3 stringing.py              # stl/stringing/ -- the silk test coupon
    python3 test_fit.py               # 57 checks; all have to pass
    python3 test_fit.py --pot <stl>   # 58, the last one against a real pot

Every dimension lives in `params.py`. The two that matter most:

| | |
| --- | --- |
| `PRESS_FIT` | the *printed* interference, −0.06 mm. Negative is a bite. |
| `AREOLE_MIN_SEP` | how close two pads may get: 14.5 mm on the trunk, 11.0 on an arm. It is what sets the spike count — 99 — because pads are drawn until the part will not take another, and only the ones a spine can actually be pushed into are kept. |

## The pot, measured

Measured off the real mesh with `build.py --pot`, not guessed:

| | |
| --- | --- |
| Pot | Ø92.2 × 76.0 mm |
| Cavity floor | 21.0 mm below the rim |
| Socket in that floor | **Ø32.00 × 8.00 deep** |
| Cavity wall, at the floor | r 40.6 |

So the cactus stands on the floor, 21 mm of it hidden inside the pot, with a
Ø31.30 spigot in the Ø32.00 socket and never less than 14.9 mm of air to the
pot's wall. `test_fit.py` checks those against `params.py`, and
`build.py --pot` fails loudly if the pot changes.

The finished sizes, measured off `stl/cactus.stl` and `pot/stl/pebble-pot.stl`
rather than worked out from the parameters:

| | |
| --- | --- |
| Pot | Ø117.9 × 95.0 |
| Cactus body | 233.5 tall; 9.2 of that is spigot, below the soil line |
| Trunk | Ø74.3 at its widest, z=46; Ø59.7 at the crown shoulder |
| Span, arms only | 149.1 × 98.8 |
| Span, with all 99 spines | 172.0 × 122.3 |
| Above the pot's rim | 198.0 |
| **The assembly** | **293.0 tall, 172.0 across** |

The spines add nothing to the height — `AREOLE_CROWN_KEEP` stops pads before
the apex, so the crown is the highest point of the object.

An earlier version of this section said Ø52–55, 175 mm tall, 147 above the
rim and about 223 overall. All four were wrong against the mesh, and nothing
caught it because a paragraph is not a test. The version after it was right
when written and went stale the moment `SCALE` went to 1.25 — every number
in it was the design figure, not the printed one. `test_fit.py` prints the
envelope on every run, so the numbers are in front of whoever changes the
shape next; this table is copied from that line rather than worked out.

### The interface, as a contract

These numbers are what the cactus needs from whatever pot it ends up in rather
than facts about one mesh. **The pebble pot is the chosen one** — a round body
with a stone texture, picked over a square-sectioned variant that was drawn at
the same time. Both carried the same mount and the cactus fits either; the
square one is not what ships. The pebble pot keeps all four numbers, so the
cactus fits it unchanged:

    python3 build.py --pot <pebble-pot.stl>
    socket Ø32.00 x 8.00 deep, floor 21.00 below a rim at z=76.00,
    inner wall r=39.37 at its tightest -- params agree with this pot

That 39.37 is the narrowest the sampler finds over the heights it walks, not the
wall's true minimum. The wall is straight at r=42.80 and filleted into the
floor, so the real minimum is **38.80**, in the corner itself, opening to 42.80
by 4 mm up. It costs nothing here, because the cactus's base flare makes the
cactus narrowest exactly where the pot is tightest.
`test_fit.py --pot <stl>` measures both profiles over the 21 mm the cactus is
down inside the pot and reports the worst gap, which is **14.9 mm**, 20 mm up
— not down in the corner at all.


- **A blind socket in the middle of the inner floor**, concentric with the
  pot's axis. Blind matters: a drainage hole straight through the floor is a
  different mount and would need a different base on the cactus.
- **Deeper than the spigot**, so the cactus seats on the floor and not in the
  hole. Any diameter works; `POT_BORE_D` follows it and the spigot is sized
  from it with `SPIGOT_CLEAR` per side.
- **A cavity wall far enough out** that the trunk clears it — `POT_INNER_R`
  against `TRUNK_R_BASE + RIB_DEPTH`, checked in `test_fit.py`.
- **A known floor-to-rim height**, because `AREOLE_Z_MIN` has to stay above it
  or the pot's rim fouls the lowest spines going in.

The cactus is scaled to the pot rather than the other way round, so a pot that
changes size much from Ø92 × 76 should take the cactus's proportions with it.

## Open questions

- **`cactus.stl` does not reload watertight, and never has.** Found while
  checking the single pair: every part built from booleans is watertight in
  memory and some of them are not once written out. An STL is a soup of
  triangles with no shared vertex indices, so vertex pairs a micron apart --
  which `socket_cutter()`'s deliberate 1e-6 overlaps leave behind -- merge on
  reload and tear the faces that used them.

  `_clean()` fixes the single pair completely, at zero change in volume, and
  `test_fit.py` now checks the round trip rather than only the mesh in
  memory. It does **not** fix the two big ones:

  | | open edges on reload |
  | --- | --- |
  | `test-hole.stl` | 0, after `_clean()` |
  | `test-print-wedge.stl` | 4038 |
  | `cactus.stl` | 51264 |

  **Mostly answered, 2026-10-08.** It was not a different fault after all.
  `socket_cutter()`'s stub -- the bit that breaks the cut through the pad --
  was only as wide as the bore, so the countersink's rim was left uncut and
  every one of the 110 sockets shed slivers where the cone ran tangent to
  the pad's dome. Widening the stub to the countersink's rim took
  `cactus.stl` from 51264 open edges to **0**: it reloads watertight.

  The wedge is still open, at 2614 edges. It is an intersection of the
  finished trunk with a box, so the suspicion is the cut face rather than
  the sockets, but that is not measured yet.

  The lesson worth keeping is the one about the test: nothing caught any of
  this for months because the suite asked the mesh in memory whether it was
  closed, and that is not the question a slicer asks. The round-trip check
  on the single pair is what turned it up.

- **Does −0.06 hold?** It is the right number on paper and the coupon exists
  because paper is not the same as PETG at 240 °C. Print the coupon, find the
  hole the spike seats in, and add that hole's engraved number to
  `SOCKET_COMP`. The ladder steps by `COUPON_STEP`, which is set equal to
  `PRESS_FIT` on purpose: one hole either side of the winner is a whole press
  fit away, so the answer is one hole rather than a region.

  The engraving is seven-segment characters built from boxes in `cactus.py`,
  not type. The pot half of this project sets real glyph outlines and that
  machinery is deliberately not reached for: the two halves do not import
  from each other, and what a gauge needs is a stroke a 0.4 nozzle can cut
  and a counter it can leave standing, which is a different problem from
  setting a name on a pot. The binding number is the counter inside an 8 —
  `COUPON_MARK_W` and `COUPON_MARK_H` are sized around it, and `test_fit.py`
  checks it, because a stroke too fat for its box engraves an 8 as a filled
  pit that still looks like a number.
- **The spines must not read as rows, and must not read as columns.** They did
  both, and the second one is why the trunk's layout no longer has ribs in it.

  The rows came from a fixed 2.1 mm step from one rib to the next: with evenly
  spaced pads the eye joined them into rings and a spiral. That was replaced by
  drawing each rib's starting height at random and rejecting it until no rib
  sat level with its neighbour and no four ribs marched in step. It fixed the
  rows and left the columns untouched, because a pad still belonged to a rib —
  so every rib carrying pads was a vertical line of them, and with pads on
  every other rib the trunk wore eight stripes. Letting a pad wander a few
  degrees off its own crest was built and measured and is not enough: ±3.8° is
  ±1.8 mm against the 11.3 mm gap to the next rib, so the line only wobbles.

  So a trunk pad does not belong to a rib any more. A crest and a height are
  drawn together, every rib in the draw, and the pad is kept only if it clears
  every pad already placed by `AREOLE_MIN_SEP` and does not make three evenly
  spaced pads up one crest. The draw runs until the trunk will not take
  another. Nothing decides in advance how many pads a rib gets, which is the
  thing that stops them being columns — the ribs now carry between 1 and 6
  each. Pads are still *on* crests, because that is where an areole grows and
  where a socket has a flat top to be bored into. Both arms are drawn the same
  way, with their own spacing — they had lines of their own down each crest,
  which is what Rob was looking at when he said the body and both sides had
  them.

  `test_fit.py` checks all of it on the finished sites rather than on the
  numbers that made them: the spacing, that all 15 ribs are used, that no three
  pads up a rib are evenly spaced, and that the wander keeps every pad on its
  crest.
- **110 spikes is an evening.** `AREOLE_MIN_SEP` and `ARM_AREOLE_MIN_SEP` are
  the dials now, and they are the honest ones: spacing is the thing with a
  physical meaning and the count follows from it. Raising the trunk's to 16 mm
  drops it to about 55 pads. If seating them turns out to be tedious rather
  than pleasant, that is where it gets backed off.
- **No spines on the arm undersides.** `SPIKE_FLOOR_DEG` drops any socket that
  would be a hole in a roof. A real saguaro has them; a printer does not enjoy
  them.
- **Arm undersides want support.** 4% of the part faces down at more than 45°,
  all of it under the two arms. PETG interface layers under a PLA body give
  breakaway supports from filament already on the shelf — see
  `../available-tools.md`.

## The three filaments, as parts

`colours.py` writes the body as two solids for a multi-material plate, which
is the arrangement the pot already uses — load `01` as the object, add `02` to
it as a part, assign a filament to each:

| | | |
| --- | --- | --- |
| `stl/colour/01-hollow-indigo.stl` | PLA Basic Indigo Purple | the rib valleys, 744.15 cm³ |
| `stl/colour/02-crest-silk.stl` | PLA Silk+ Purple | the rib crests, 22.63 cm³ |
| `stl/spikes-x72.stl` | GEEETECH silk silver | the 99 spines, on their own plate |

Both are real booleans against a core solid built by holding `rib_profile` at
a constant, not a face-group split: those are open shells and a slicer is
entitled to make nonsense of them. The run checks that the two add back up to
the cactus — 766.77 cm³ against 766.77 — and that each survives the trip
through an STL with its volume intact.

### The ribs run to the tip

They did not. `RIB_FADE_TOP` faded them to nothing by `TRUNK_H`, and because
the crown is built by scaling the ring at `TRUNK_H` down over the dome, a ring
with no ribs in it makes a dome with no ribs on it. The top 14 mm of the plant
was a turned bulb. It showed up in the crest part before it showed up in the
silhouette: `02-crest-silk.stl` stopped at 210.6 mm while the body went on to
224.1, so the silk simply ended.

`RIB_TIP_KEEP` is how much rib depth survives that fade, and at 1.0 there is
no fade: full depth to `TRUNK_H`, then the dome tapers ribs and all, 5.93 mm
peak-to-valley at the shoulder closing to 2.85 at the apical depression — the
way a saguaro's converge. `ARM_RIB_TIP_KEEP` does the same for the arms, where
the ribs now shrink with the tip's own rounding rather than flattening out
a few millimetres short of it. The crest part reaches 224.2 mm, which is the
top.

Dropping the fade cost seven spine sites — 106 to 99. Deeper ribs at the top
of the trunk mean more pads up there that the insertability sweep cannot find
a straight path into, and it drops them rather than ship a hole nothing fits.

### The silk strings, and why this part is the reason

PLA Silk+ Purple started throwing hairs. Silk PLA strings more than matte --
the additives that make it glossy drop the melt viscosity -- but the part is
doing most of the work. The silk is **2.95%** of the cactus by volume and
**15 separate islands on every one of 1015 layers**, each about 6 mm of arc
with a 7 mm hop across a rib valley between them. Most of the travel moves
in the print belong to the smallest, oozier third of the material.

`stringing.py` writes a coupon that reproduces that rather than a generic
stringing cube: the real trunk's skin at `Z_SRC`, split by the same two
booleans into the same two solids, on a foot shaped like the cactus's own,
with three spine sockets in it. 67 mm across, 30 mm tall, 150 layers, 15
islands per layer at 6.0 mm of arc and a 7.0 mm hop -- the cactus's own
numbers.

**The foot is styled, not copied.** The real bottom 30 mm of the cactus has
nothing in it to test: the base flare runs to z=12.9, ribs do not start
until z=21.2 and reach only 42% depth by z=30, and `AREOLE_Z_MIN` is 30.0,
so the lowest pad the model will ever place sits exactly at the height cap.
A literal slice would be a smooth cone with no silk and no holes. What is
copied is the shape: a true 45° cone, as the trunk's own base clip makes,
but starting from a wider radius so it finishes in 7 mm instead of 13.

`FOOT_BIAS` exists because the foot has no ribs, so body and core are the
same cone down there and a boolean between coincident surfaces is how a mesh
comes back with holes in it. The core is built 1 mm fatter through the foot,
tapering to exactly zero where the ribs come up -- so the split is untouched
everywhere it matters, and the foot prints in one colour, which is right
anyway.

**A site's third field is not its rake.** `cactus._rake` applies
`SPIKE_RAKE_DEG` itself and adds the field on top, so it carries the
per-site scatter. Passing `SPIKE_RAKE_DEG` into it doubles the lean to 68°,
at which angle the insertion sweep finds the lower side of the post still
buried in the skin and reports every socket blocked -- which is how it was
caught, at 0 of 3. The build now prints each socket's lean and flags one
that falls outside `SPIKE_RAKE_DEG ± SPIKE_RAKE_SCATTER`.

**The threshold is a weaker lever than it looks.** An earlier three-band
version of this coupon swept `CREST_THRESHOLD`; its first draft used
0.15 / 0.00 / −0.15 and measured 6.0 / 6.5 / 7.0 mm of arc -- three bands
that differ by nothing, because the rib profile is steep through its middle
and the cut barely moves there. It only bites past −0.25. That coupon is in
git history at `d64e112`, 36 mm tall, sweeping 0.15 to −0.45, if the
geometry question comes back after the drying one is settled.

**Worth checking in the slicer before committing to the full part.** Two
filaments on one object means a colour change on essentially every layer:
about 150 on this coupon, about **1015 on the cactus**, each with its own
purge. `filament.md` already notes that a part split into separately printed
pieces is usually cheaper than one printed in two colours, and this is the
part that tests whether that applies here.
