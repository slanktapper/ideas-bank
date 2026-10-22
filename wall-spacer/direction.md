# wall-spacer

**Status:** prototype — modelled and checked, not yet printed

## What it is

A printed strut that fills the **123 mm gap** behind Rob's cabinet so the
cabinet cannot slide back off the table it stands on. It is **40 mm wide**,
it **hooks over the wooden lip** at the near side of the gap so it hangs
there instead of falling in, and the 123 mm it spans is a **three-sided
lattice radio tower** — two chords along the top, one along the bottom,
X-braced in all three faces, tapering away from the lip.

The tower is not decoration bolted onto a block. It *is* the part: there is
no solid section anywhere except the two bearing pads and the saddle.

## Why

The cabinet sits on a table with a gap behind it. Nothing holds it, so it
can work its way back and go over the edge. A 123 mm block of something in
that gap fixes it, and nothing that shape is for sale.

The hook is the part that makes it a design rather than an offcut. A plain
block dropped into the gap falls to the bottom of it the first time the
cabinet is nudged forward. Hooked over the lip, it stays at the height it
was put at and can be lifted out with one finger.

## Scope

**What it does.** Fills one measured gap, hangs itself on one measured lip,
and takes a horizontal push from a piece of furniture.

**What it deliberately does not do.**

- **Carry weight.** Nothing stands on it, and it is not a shelf. It takes a
  shove along its own length and nothing else.
- **Fix the cabinet to anything.** No screws, no adhesive, no damage. It
  lifts straight out.
- **Fit any other gap.** `SPAN` and `LIP_T` are this gap and this lip. The
  file is parametric, so another gap is a one-line change — but it is a
  change, not a feature.
- **Look like anything from the front.** It lives in a gap behind furniture.
  The tower is there because Rob asked for it, and it costs nothing.

## The gap and the lip

Measured 2026-10-22 MDT. These are the numbers the part is wrong if it gets
wrong, so they are recorded here rather than buried in code.

| | |
| --- | --- |
| Gap, lip face to the far side | **123 mm** (Rob, tape) |
| Lip thickness | **12.7 mm** (from the photograph — see below) |
| Lip | a board standing on edge, open void behind it |
| Part width | **40 mm** (asked for) |

**The photograph was measured, not glanced at.** The tape in it was
straightened by rotating the image 51.18° onto the tape's own principal
axis, and the scale came from the tape's millimetre ticks rather than from
its printed numbers: **19.86 px/mm**, fitted over a 1380 px stretch of
clean graduations. On that scale

- the near face of the lip sits at **124.1 mm** from the tape's zero —
  1.1 mm from Rob's 123, which is what a tape hooked over an edge and
  photographed at an angle is worth. Rob's number is the one in `params.py`;
  the photo only confirms it is not a typo.
- the lip reads **11.9–12.4 mm** thick across six sampled rows. The tape
  crosses the lip square-on, so that is a true thickness and not a
  foreshortened one. Called at **12.7 mm**, half an inch nominal, and
  rounded **up**: a throat slightly too wide rattles, a throat slightly too
  narrow does not go on.

The lip's top edge is what the saddle sits down on, and the photograph shows
open void behind the board, which is what lets the outer leg drop 14 mm.

## How it works

Three pieces, in one solid:

    saddle   13.5 mm throat over a 12.7 mm lip, 5 mm bridge, 14 mm outer leg
    tower    123.0 mm between bearing faces, 5 X-braced bays, 38 -> 28 deep
    pads     4.5 mm solid triangular plates at both ends -- the two that push

    32.2 cm3, 141.5 x 40.0 x 38.0 mm

**The section is a triangle.** Two chords run along the top at Y = 0 and
Y = 40, and one runs along the bottom up the middle at Y = 20. All three
faces — the top and the two sides — carry the same belt-and-X-bracing, so
there is no solid face anywhere in the span.

**All the clearance is on the outer side.** The throat's inner wall and the
strut's bearing face are the same face, at X = 0, so the strut always sits
flush against the lip and the 0.8 mm of slop lives behind the lip where it
costs nothing. Get that backwards and the 123 mm becomes 122.2 mm.

**It works in both directions.** Nobody has said which way the cabinet
wants to go, and a saddle does not care: push it towards the lip and the
bearing face takes it, push it away and the outer leg does.

**The two end pads are solid on purpose.** Everything else is a lattice, but
these are the faces that actually push on something, and a lattice there
would stand the whole load on four small feet.

**The top plane stays flat and the taper is one-sided.** A symmetric taper
would be more like a real tower, and it would tilt the top plane, which is
the one surface that cannot be tilted — see below. It also keeps the far
bearing pad up at the top, where the only thing known about the far side of
the gap is that there is material at the level the tape was stretched
across.

## Why it prints upside down

**The whole top of the part is one flat plane**, at `TOP`: the two top
chords, the lacing between them and the saddle bridge all finish at exactly
that level and nothing rises above it. Printed **upside down**, that plane
is the bed — 3399 mm² of first-layer contact, most of it the solid saddle
bridge — and the tower builds upwards, narrowing to the single bottom chord
at the very top.

A shape that narrows as it rises has nothing to support. `build.py` checks
it rather than claiming it: in the print orientation, **0.00 mm² of the
part's 27,000 mm² faces downwards at less than 40° from horizontal**.

Two details exist only because of that check.

- **The bottom chord is a diamond, not a square.** It is the one member that
  lies nearly horizontal when printed, so it is the one member whose
  underside would otherwise be a flat ceiling in mid-air. Rolled 45°, it has
  no underside at all: it starts from a single line and widens, which is the
  one overhang shape FDM is unconditionally good at.
- **The lacing in the top face is as thick as the chords, not as thick as it
  is wide.** Drawn 3 mm like the rest, it finished half a millimetre shy of
  the top plane — 1387 mm² of flat ceiling hanging just above the bed,
  anchored to nothing. The check found it; nothing else would have, until
  the print.

What is left is bridging. The bottom chord is pinned at every bay boundary,
where the belts of all three faces meet it in a complete triangular ring, so
between nodes it bridges **24.6 mm** — an ordinary distance, and it bridges
from a single line rather than a face. That is why `BAYS` is a structural
number rather than a cosmetic one.

It is also why the tower is three-sided rather than four. A four-sided box
has a bottom face, and a bottom face printed this way is a 123 × 40 mm
ceiling.

## Stack

Python, matching the four sibling 3D projects here. `trimesh` builds and
unions the members, `manifold3d` does the booleans, `shapely` draws the two
outlines that are extruded rather than assembled, and the renderer in
`../3d-tools` draws it. No CAD application, no GUI.

The frame is assembled as about fifty boxes, each one run 0.8 mm past its
node so that struts meet in a lump of solid rather than face to face, and
then trimmed back to the box it is allowed to occupy. The trim is what puts
the bearing faces exactly on X = 0 and X = SPAN and the top plane exactly
flat, rather than wherever the last lap of a diagonal happened to finish.
It happens **before** the saddle goes on, because the saddle is the one part
of the part that is allowed behind X = 0.

## How to run

```bash
cd wall-spacer
python3 -m pip install -r requirements.txt
python3 build.py          # 24 checks, two STLs (verified on disk), eight renders
```

It will not write files if a check fails, and the exit code is non-zero.

**The checks read both STLs back off disk and check those too.** An STL
stores three loose vertices per triangle, so the file only becomes a solid
once a reader merges them — and that merge is where a mesh that passed every
check in memory can turn into a non-manifold pinch. `../sim-control-prints`
found exactly that fault the hard way; this project inherited the habit
rather than the bug.

`print-guide.md` is the one to read before printing.

## Open questions

- **`LEG_DROP` is a guess**, 14 mm. The photograph shows void behind the
  lip, not how much. If something is 10 mm down there, the saddle will not
  seat and the number has to come down.
- **The far side of the gap is unmeasured.** The part assumes a face it can
  push on somewhere in the top 28 mm below the top plane. That is where the
  tape was stretched across, so there is something there — but "something"
  is not "a flat face square to the span".
- **Is 123 mm the gap, or the gap plus a skirting?** If the far face is
  recessed behind a moulding, the pad lands on the moulding and the span is
  short. First fit will say.
- **Nothing resists the cabinet lifting the strut out.** It hangs by gravity.
  That is deliberate — it is also the whole of why it is removable — but if
  the cabinet rides up the bearing face the strut will walk upwards.
- **It is light now.** 32.2 cm³ against the 96.7 cm³ the first, solid-topped
  version weighed. That should still be ample for a shove from furniture,
  but it has not been pushed on yet. If it flexes, `CHORD_T` and `CHORD_B`
  are the two numbers to raise, not the depth.
- **One or two?** One strut in the middle of a cabinet lets it skew. Two,
  one near each end, do not. The part is about an hour to print, so this is
  a question for after the first fit.
