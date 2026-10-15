# sim-control-prints

**Status:** prototype — first part modelled and checked, not yet printed

## What it is

Printed attachments for flight-sim control hardware. The first is for the
**VKB T-Rudder Mk.V** rudder pedals: an **end cap for the foot rest** that
bolts to the end of the ribbed aluminium extrusion, using the two threaded
bosses already in its end face, and carries a lip standing 25 mm proud of
the ribbed surface so a foot cannot slide off.

One part does all four positions — top and bottom of each foot rest, on both
pedals. Turn it 180° about the extrusion axis and the lip still points away
from the aluminium, so there is no handed version and nothing to label.

The folder is deliberately named for the category rather than for one part.
Sim hardware is a stream of small bolt-on fixes — a stop here, a spacer
there — and each one is too small to be its own idea.

## Why

The T-Rudder's foot rest is a bare 50 mm extrusion with open mounting bosses
at each end. VKB ships nothing to put in them. Anything that wants to extend,
cap or stop the foot rest has a ready-made, rigid, two-bolt interface sitting
unused.

## Scope

**What it does.** Parts that bolt to existing sim hardware through mounting
points the hardware already has.

**What it deliberately does not do.**

- **Modify the hardware.** No drilling, no tapping, no cutting. If a part
  needs a hole that is not already there, it is the wrong part.
- **Carry a person's weight.** A rudder pedal takes a push from a seated
  foot, not a stand-on load. Nothing here is a step.
- **Replace structure.** The pedal's own arms, springs and linkage are left
  alone.

## The T-Rudder Mk.V mount

Measured from the hardware, 2026-10-15 MDT. These are the numbers everything
bolts to, so they are recorded here rather than buried in code.

| | |
| --- | --- |
| Mounting face | the **end face** of the ribbed foot rest extrusion |
| Bosses | 2, tapped, one in each corner lobe |
| Hole spacing | **39 mm ± 0.5** (measured) |
| Thread | **M5** |
| Extrusion width | **52 mm** (measured) |
| Extrusion depth | **15 mm** (measured, at the deepest point) |
| Foot face | **crowned across the width**, not flat |
| Crown height | **≈4 mm** (PROVISIONAL) |
| Boss centre, from the back | **≈5.5 mm** (PROVISIONAL, derived from the crown) |
| Bolts on hand | **M5 × 16 mm**, **domed** head, 10 mm across (measured) |

The crown is the thing the photograph hides. The foot face rises on a gentle
arc from the side edges to the middle, so "15 mm deep" is the depth at the
crown and the edges are shallower. Tracking the line of rib ends across the
end face gave 28 px of noise on a 740 px chord — enough to confirm the curve
exists, nowhere near enough to size it.

**The 16 mm bolt is the real constraint.** M5 into aluminium wants 8–10 mm of
thread engagement, which leaves only 6–8 mm of part thickness above the boss
unless the hole is counterbored or longer bolts are bought. M5 × 25 or × 30
is a hardware-store item and removes the problem entirely.

### Still to confirm

- **Boss centre to the flat back.** The critical one. Everything else can be
  a millimetre out and the cap still fits.
- Crown height, if it is easy to get at.
- Tapped depth of the bosses — sets how much of a 16 mm bolt is usable.
- Whether both ends of the extrusion carry the same boss pattern.

## How it works

The cap is a chamfered rounded-rectangular block bolted to the end face. It
is 13 mm long along the extrusion, which is not an arbitrary number: an
M5 × 16 bolt wants 9 mm of thread in the aluminium, leaving 7 mm of grip,
and a socket cap head is 5 mm tall and sits 1 mm below the surface. 7 + 5 + 1
is the whole of it.

    mount    2 x M5 at 39 mm, 11.0 mm pocket, open at the back
    bolt     16 mm = 7 grip + 9 engagement, 10 mm domed head
    cap      52.6 x 40.0 x 13.0 mm, 25.3 cm3, print 4x
    lip      25 mm proud of the crown

**The crown turns out to change almost nothing.** The lip is a full-width
wall standing 25 mm above the highest point of the face, so the cap is solid
from the back of the extrusion all the way up, and the curve is interior to
it — there is no surface of the part that follows the arc. What the crown
does change is where the bosses sit: it pulls them to about 5.5 mm from the
back rather than the 7.5 mm a flat 15 mm bar would give, and that is the one
number the part cannot be wrong about.

**The bolt pocket is open at the back, on purpose.** The head is domed and
10 mm across, which an 11 mm pocket swallows — but the bosses are only 5.5 mm
from the flat back, so a closed bore would have left 0 mm of material behind
it. The alternatives were to push the whole cap behind the extrusion, into
the pedal arm, where nothing has been measured, or to drop the counterbore
and let the heads stand proud.

Opening it costs nothing real, and that is checkable rather than asserted.
The head is 5.0 mm in radius and the back face is 5.5 mm from the bolt axis,
so **the head itself never reaches the back** — only clearance air is being
let out. The ring it bears on at the bottom of the pocket is complete, and
`build.py` samples it to prove so. `OPEN_BACK` is derived, so a real `BOSS_Y`
of 6.7 mm or more closes the bore again with nothing else changing.

**The outer face is deliberately not chamfered**, which is the same
constraint seen earlier. Three arithmetic checks once called a version fine
that had 0.4 mm of wall beside a head, because arithmetic does not know about
chamfers. Replacing them with checks that sample the mesh caught it, and then
caught a second thin wall nobody had thought to look for — the bores sit near
the side edges too. `CAP_W` is derived from that clearance, which is why it
sits at 52.6 mm rather than the extrusion's 52.

The outer body is built as the convex hull of four stacked outlines rather
than by chamfering with booleans. The outline is convex, so the hull *is* the
chamfered prism, and it is manifold by construction.

## The alignment gauge

`stl/alignment-gauge.stl` is the cap's silhouette as a four-layer card —
0.8 mm, about two grams — with the same holes in the same places and
`BOSS Y 5.5` engraved on it.

It exists because the part's one unconfirmed dimension is also its most
dangerous. The card answers it without committing a cap: offer it up, and the
step between its straight back edge and the extrusion's back face *is* the
error in `BOSS_Y`. Being the full silhouette, it answers the base-plate
clearance question in the same motion.

The label is engraved rather than cut through. On a 0.8 mm card a cut-through
`O` drops its counter out as a loose disc, so the glyph outlines are
accumulated with `symmetric_difference` — the even-odd rule — and sunk two
layers into a two-layer floor, which `build.py` checks both ways round.

## Stack

Python, matching the three sibling 3D projects. `trimesh` with `manifold3d`
for the booleans, `shapely` for the outline, and the renderer in
`../3d-tools`. No CAD application, no GUI.

Two packages that `../3d-tools/requirements.txt` explicitly says are **not**
needed are needed here, on trimesh 5.1.1: `rtree`, because almost every check
is a `Trimesh.contains()` test, and `networkx`, because capping a section cut
reaches for a graph. `requirements.txt` says so and says why.

## How to run

```bash
cd sim-control-prints
python3 -m pip install -r requirements.txt
python3 build.py          # 38 checks, then two STLs and seven renders
```

It will not write files if a check fails, and the exit code is non-zero.
`print-guide.md` is the one to read before printing.

## Open questions

- **`BOSS_Y` is still a guess**, 5.5 mm, derived from an unmeasured crown.
  It is the dangerous one: if the tapped boss is not centred in the corner
  lobe the cap does not bolt on at all.
- **`CROWN` is still a guess**, 4.0 mm. It only reaches the part through
  `BOSS_Y`, `EDGE_DEPTH` and the render stub.
- **`HEAD_H` is assumed at 5.0 mm.** The photo puts the dome nearer 4.7.
  Overstating it only sinks the head deeper, so it is not worth chasing.
- **The open back is untested in the hand.** It should be invisible once
  bolted, since the extrusion is behind it, but nobody has seen one yet.
- **Does the bottom cap clear the base plate?** A 25 mm lip at the lower end
  swings through an arc as the pedal moves. Unknown until one is held
  against the hardware.
- **Does the back of the cap clear the pedal arm?** The cap is flush with the
  back of the extrusion, so in principle yes.
- **How deep are the bosses tapped?** The cap assumes at least 9 mm. If they
  are shallower the bolt jams before it clamps, and `GRIP` has to go up.
- **Nothing is textured.** The lip is a plain face. If a foot slides on it,
  the ribs on the aluminium are the pattern to copy.
