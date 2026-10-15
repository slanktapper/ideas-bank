# sim-control-prints

**Status:** idea — mounting interface measured, part not yet chosen

## What it is

Printed attachments for flight-sim control hardware. The first is for the
**VKB T-Rudder Mk.V** rudder pedals: something that bolts to the end of the
ribbed aluminium foot rest extrusion, using the two threaded bosses already
in its end face.

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

## Stack

Not yet chosen. The sibling projects here use Python with `trimesh` +
`manifold3d` for geometry and `../3d-tools` for renders, and that is the
likely choice — but per `CLAUDE.md` it gets decided and recorded when the
first part is actually modelled, not assumed now.

## How to run

Nothing to run yet.

## Open questions

- **What the first part is.** The interface is known; the part is not.
- **Material.** PETG is the functional default on the shelf and is the right
  answer for something underfoot — PLA creeps under sustained load and the
  pedals live in a 10–20 °C garage, which is kind to neither. See
  `../filament.md`; black and white PETG are in stock.
- **Left and right.** Two pedals. Whether the part is handed or symmetric
  decides whether it is one STL or two.
