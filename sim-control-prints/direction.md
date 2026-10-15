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
| Bosses | 2, blind tapped, one in each corner lobe |
| Hole spacing | **39 mm ± 0.5** (measured) |
| Thread | **M5** |
| Extrusion width | **≈50 mm** (derived: end face spans 1.283 × the 39 mm hole pitch) |
| Boss inset | **≈5.5 mm** from each outer edge |
| Bolts on hand | **M5 × 16 mm** |

Derived figures are marked as such. The width and inset come from pixel
measurement of a photograph scaled against the known 39 mm pitch, not from
calipers — good to about a millimetre, and worth confirming before a final
print.

**The 16 mm bolt is the real constraint.** M5 into aluminium wants 8–10 mm of
thread engagement, which leaves only 6–8 mm of part thickness above the boss
unless the hole is counterbored or longer bolts are bought. M5 × 25 or × 30
is a hardware-store item and removes the problem entirely.

### Still to confirm

- Tapped depth of the bosses — sets how much of a 16 mm bolt is usable.
- Extrusion width and boss inset, by caliper rather than by photograph.
- Whether both ends of the extrusion carry the same boss pattern.

## How it works

The cap is a chamfered rounded-rectangular block bolted to the end face. It
is 13 mm long along the extrusion, which is not an arbitrary number: an
M5 × 16 bolt wants 9 mm of thread in the aluminium, leaving 7 mm of grip,
and a socket cap head is 5 mm tall and sits 1 mm below the surface. 7 + 5 + 1
is the whole of it.

    mount    2 x M5 at 39 mm, counterbored 9.2 mm
    bolt     16 mm = 7 grip + 9 engagement
    cap      50.8 x 37.0 x 13.0 mm, 22.8 cm3, print 4x
    lip      25 mm proud of the ribbed face

**The outer face is deliberately not chamfered.** The boss sits 6 mm from the
back of a 12 mm extrusion, so a 9.2 mm counterbore leaves 1.4 mm of wall
beside a bolt head. A 1 mm chamfer on that face took it to 0.4 mm — less than
one perimeter — and three separate arithmetic checks said pass, because
arithmetic does not know about chamfers. The check that found it measures the
mesh instead, and it then found a second thin wall nobody had thought to look
for: the counterbores are 5.5 mm from the side edges, so they only had 0.9 mm
of material outboard. The cap is now 50.8 mm rather than 50 mm wide for that
reason alone, which leaves it 0.4 mm proud of the extrusion on each side.

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
python3 build.py          # 26 checks, then the STL and six renders
```

It will not write files if a check fails, and the exit code is non-zero.
`print-guide.md` is the one to read before printing.

## Open questions

- **`EXT_DEPTH` and `BOSS_Y` are still guesses.** 12.0 mm and 6.0 mm, from a
  photograph. `BOSS_Y` is the dangerous one: if the tapped boss is not
  centred in the thickness, the cap does not bolt on at all.
- **Does the bottom cap clear the base plate?** A 25 mm lip at the lower end
  swings through an arc as the pedal moves. Unknown until one is held
  against the hardware.
- **Does the back of the cap clear the pedal arm?** The cap is flush with the
  back of the extrusion, so in principle yes.
- **How deep are the bosses tapped?** The cap assumes at least 9 mm. If they
  are shallower the bolt jams before it clamps, and `GRIP` has to go up.
- **Nothing is textured.** The lip is a plain face. If a foot slides on it,
  the ribs on the aluminium are the pattern to copy.
