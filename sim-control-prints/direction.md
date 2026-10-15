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
| Bolts on hand | **M5 × 16 mm**, socket cap head |

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

    mount    2 x M5 at 39 mm, counterbored 9.2 mm
    bolt     16 mm = 7 grip + 9 engagement
    cap      52.0 x 40.4 x 13.0 mm, 25.7 cm3, print 4x
    lip      25 mm proud of the crown

**The crown turns out to change almost nothing.** The lip is a full-width
wall standing 25 mm above the highest point of the face, so the cap is solid
from the back of the extrusion all the way up, and the curve is interior to
it — there is no surface of the part that follows the arc. What the crown
does change is where the bosses sit: it pulls them to about 5.5 mm from the
back rather than the 7.5 mm a flat 15 mm bar would give, and that is the one
number the part cannot be wrong about.

**The outer face is deliberately not chamfered**, and the cap reaches 0.4 mm
behind the extrusion. Both are the counterbore's doing. With the boss 5.5 mm
from the back, a 9.2 mm bore leaves 0.9 mm of wall behind a bolt head; a 1 mm
chamfer on the outer face would have taken it to nothing. Three separate
arithmetic checks called the original version fine, because arithmetic does
not know about chamfers. Replacing them with one that samples the mesh all
round each counterbore caught it, and immediately caught a second thin wall
nobody had thought to look for — the bores sit 5.5 mm from the side edges and
had 0.9 mm of material outboard. `CAP_W` and `BACK_EXT` are both derived from
that clearance now, which is why they came back to 52.0 mm and 0.4 mm on
their own when the real width arrived.

The outer body is built as the convex hull of four stacked outlines rather
than by chamfering with booleans. The outline is convex, so the hull *is* the
chamfered prism, and it is manifold by construction.

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
python3 build.py          # 28 checks, then the STL and six renders
```

It will not write files if a check fails, and the exit code is non-zero.
`print-guide.md` is the one to read before printing.

## Open questions

- **`BOSS_Y` is still a guess**, 5.5 mm, derived from an unmeasured crown.
  It is the dangerous one: if the tapped boss is not centred in the corner
  lobe the cap does not bolt on at all.
- **`CROWN` is still a guess**, 4.0 mm. It only reaches the part through
  `BOSS_Y`, `EDGE_DEPTH` and the render stub.
- **Does the bottom cap clear the base plate?** A 25 mm lip at the lower end
  swings through an arc as the pedal moves. Unknown until one is held
  against the hardware.
- **Does the back of the cap clear the pedal arm?** The cap is flush with the
  back of the extrusion, so in principle yes.
- **How deep are the bosses tapped?** The cap assumes at least 9 mm. If they
  are shallower the bolt jams before it clamps, and `GRIP` has to go up.
- **Nothing is textured.** The lip is a plain face. If a foot slides on it,
  the ribs on the aluminium are the pattern to copy.
