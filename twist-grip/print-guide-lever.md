# twist-grip — print guide, lever version

For the lever design in `concept_lever.py`, not the twist design that
`build.py` and `print-guide.md` still describe. Files are in `stl-lever/`,
kept out of `stl/` because `build.py` wipes that directory on every run.

Nothing in this version has been printed. The scale references were, and
they say nothing about fit.

## What to print

| file | qty | size (mm) | ~weight at 35% |
| --- | --- | --- | --- |
| `body.stl` | 1 | 144 × 60 × 90 | 64 g |
| `jaw.stl` | 2 | 42 × 52 × 78 | 25 g each |
| `lever.stl` | 2 | 140 × 53 × 43 | 30 g each |
| `brace.stl` | 2 | 30 × 61 × 16 | 6 g each |

About **186 g** all in. Seven pieces, four distinct.

Every file is already turned the way it wants to go and sits on z = 0, so
drop it on the plate and do not let the slicer re-orient it. The lever in
particular: stood on its pivot end it is 130 mm tall on two small pads.

## Supports

Only for the posts, and only under them:

- **`body.stl`** — the four pivot posts at z 8. Horizontal cylinders
  cantilevered 12 mm off a vertical wall.
- **`jaw.stl`** — the two drive posts at z 39. Same shape, same reason.
  Nothing else: a spine runs cap to cap through the drive boss, so the
  widest bridge left inside the jaw is 7 mm.
- **`lever.stl`** — the underside of the drive-slot stub. Small.
- **`brace.stl`** — none.

Everything else is self-supporting by design. The vee runners and their
grooves are at 45° precisely so their upper flanks need nothing, and the
entrance chamfer closes inward at 45°. The drive window's roof is a 28 mm
bridge, which wants no support either.

**These posts cannot be teardropped**, which is a correction to what this
guide would otherwise have said. A teardrop is the fix for a horizontal
*hole*. These are posts that have to stay round: the lever turns on the
pivot post and slides along the drive post. Flatten either and the
mechanism stops working. Support them, then clean the underside with a
knife — the bottom millimetre is a bearing surface.

## Material

**The levers must be PETG.** They are not dropped onto the posts, they are
sprung onto them: 11.7 mm a side, 1.20% strain, about 43 N. PETG takes
that elastically. PLA's useful range gets you there with little margin and
it fails brittle, so a lever that survives assembly may still split later.

The body also prefers PETG — the pivot posts are cantilevers carrying the
whole squeeze — but PLA Pure will do, as it did for the twist body. The
jaws and braces are not fussy.

## Assembly

1. **Jaws into the body.** Each goes in radially from outside, runners into
   grooves, drive post through the wall window. Push it in until the face
   reaches the bore. The grooves and the window run out to the wall's edge
   for exactly this reason; nothing else lets a jaw in. The tie slabs above
   and below the slot clear the jaw's path by 0.3 mm.
2. **Levers onto the posts.** Spread the two plates about 12 mm a side,
   slide the lever on from the back with the plates straddling the walls,
   and let go when the pivot hole lines up with the pivot post. The drive
   post drops into the slot at the same moment — the spacing is the same.
3. **Braces on last.** Press one onto each pair of pivot posts. It picks up
   the 3.4 mm of post the lever leaves and is what stops the lever
   springing off again.

## What this print is actually testing

Three things that have never been in plastic:

- **The vee runner in its groove.** 0.32 mm between the flanks, from the
  comb you printed for the twist version. The fit was measured on a round
  pin in a round groove, not on a 45° vee, so it is an inference.
- **Springing the lever on.** The 43 N and 1.20% are beam theory, not
  experience.
- **The squeeze.** 118 mm open to 50 shut, closing on the grab bar.

If the vee is tight, the number to change is `RAIL_H` in
`concept_lever.py`; the groove is cut from `GROOVE_H` and the clearance is
the difference between them over √2.
