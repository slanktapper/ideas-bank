# wall-spacer

**Status:** prototype — modelled and checked, not yet printed

## What it is

A printed strut that fills the **123 mm gap** behind Rob's cabinet so the
cabinet cannot slide back off the table it stands on. It is **40 mm wide**,
it **hooks over the wooden lip** at the near side of the gap so it hangs
there instead of falling in, and the 123 mm it spans is drawn as a
**lattice radio tower** — two chords, five X-braced bays, tapering away
from the lip.

The tower is not decoration bolted onto a block. It *is* the part: the
whole thing is one 2D profile extruded 40 mm, and the lattice is what that
profile happens to be.

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
    tower    123.0 mm between bearing faces, 5 X-braced bays, 34 -> 24 deep
    pads     4.5 mm full-depth faces at both ends -- the two that push

**All the clearance is on the outer side.** The throat's inner wall and the
strut's bearing face are the same face, at X = 0, so the strut always sits
flush against the lip and the 0.8 mm of slop lives behind the lip where it
costs nothing. Get that backwards and the 123 mm becomes 122.2 mm.

**It works in both directions.** Nobody has said which way the cabinet
wants to go, and a saddle does not care: push it towards the lip and the
bearing face takes it, push it away and the outer leg does.

**The top chord is straight and the taper is one-sided.** A symmetric taper
would be more like a real tower, and it would drop the far bearing pad to
mid-height. The only thing known about the far side of the gap is that
there is material at the level the tape was stretched across — which is
the level of the lip's top edge. Keeping the top chord straight keeps the
pad up there with it.

## Why it is an extrusion

The part is one 2D shape in X–Z, extruded 40 mm along Y. Printed with that
40 mm standing up in Z, **every wall is plumb and every layer is identical**:
no overhangs, no bridges, no supports, nothing for the slicer to be clever
about, and the lattice's holes are outlines rather than ceilings. The 123 mm
of compressive load runs along the extrusion lines instead of across the
layer bonds, which is the direction FDM is good at.

That is checkable rather than asserted, and `build.py` checks it: no face in
the mesh may be anything other than plumb or flat. One face that was neither
would be an overhang.

It is also why the tower is a flat lattice rather than a three-dimensional
one. A real four-legged tower would need supports inside every bay. Drawn as
an elevation and extruded, it reads as the same thing and prints in one go.

## Stack

Python, matching the four sibling 3D projects here. `shapely` builds the
profile, `trimesh` extrudes it, and the renderer in `../3d-tools` draws it.
No CAD application, no GUI.

**No boolean engine does any real work.** The profile is a union of members
and two deliberate cuts, all in 2D; the 3D step is a single extrusion. That
is worth saying because the sibling projects fight manifold3d for their
geometry, and this one has nothing to fight — the mesh is manifold by
construction. `manifold3d` is still installed, because the *checks* use
`mesh.intersection()` to prove a 12.7 mm lip drops into the throat without
fouling anything.

## How to run

```bash
cd wall-spacer
python3 -m pip install -r requirements.txt
python3 build.py          # 23 checks, two STLs (verified on disk), six renders
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
  lip, not how much of it. If something is 10 mm down there, the saddle
  will not seat and the number has to come down.
- **The far side of the gap is unmeasured.** The part assumes a face it can
  push on somewhere in the top 24 mm below the lip's top edge. That is where
  the tape was stretched across, so there is something there — but "something"
  is not "a flat face square to the span".
- **Is 123 mm the gap, or the gap plus a skirting?** If the far face is
  recessed behind a moulding, the pad lands on the moulding and the span is
  short. First fit will say.
- **Nothing resists the cabinet lifting the strut out.** It hangs by gravity.
  That is deliberate — it is also the whole of why it is removable — but if
  the cabinet rides up the bearing face the strut will walk upwards.
- **One or two?** One strut in the middle of a cabinet lets it skew. Two,
  one near each end, do not. The part costs about two hours to print, so
  this is a question for after the first fit.
