# Printing the foot rest end cap

**Print the alignment gauge first.** It is four layers and about two grams,
and it settles the one dimension the cap cannot be wrong about. Only then
print a cap; only after that fits, print the other three.

## First: the alignment gauge

| | |
| --- | --- |
| File | `stl/alignment-gauge.stl` |
| Size | 52.6 × 40.0 × **0.8 mm** — four layers at 0.2 |
| Volume | 1.6 cm³, about 2 g |
| Quantity | 1 |

It is the cap's own silhouette as a card, with the same two clearance holes
in the same two places, and `BOSS Y 5.5` engraved on it so a later one can be
told apart. Print it flat, engraved side up, any material — PLA is fine, this
one is not going underfoot.

Then hold it against the end of a foot rest and read three things off it:

1. **Do both bolts go through into the bosses?** If yes, the 39 mm pitch is
   right and the cap will bolt on.
2. **Does the straight back edge sit flush with the back of the extrusion?**
   This is the one that matters. Any step between the card's back edge and
   the aluminium's back face *is* the error in `BOSS_Y`, readable straight
   off with a rule. Tell me which way it sits proud and by how much.
3. **Does the lip clear everything?** The card is the full silhouette, so
   hold it on the *bottom* end and work the pedal through its travel. If the
   top of the card fouls the base plate or the linkage, a 25 mm lip will too,
   and better to find out on two grams of plastic.

If all three are good, the numbers are confirmed and the cap is ready.

## The part

| | |
| --- | --- |
| File | `stl/footrest-end-cap.stl` |
| Size | 52.6 × 40.0 × 13.0 mm |
| Volume | 25.3 cm³ solid; expect 17–20 g each at the settings below |
| Quantity | **4** — two ends, two pedals. One STL does all four. |

The same part serves the top and the bottom of a foot rest, and the left and
right pedals. Rotate it 180° about its long axis and the lip still points
away from the extrusion. `build.py` checks that this is true rather than
asserting it.

## Material

**PETG Basic, black** — in stock per `../filament.md`, and it matches the
anodised aluminium. PETG is the right call rather than the default-prototype
PLA: the cap takes a sustained push from a foot, and PLA creeps under steady
load and goes brittle. ABS would also do it and is on the shelf in orange
only, which is not the colour anyone wants here.

White PETG is also in stock if a visible stop is wanted at the bottom end.

## Orientation and settings

**Mating face down on the bed** — the flat face with the two 5.6 mm holes in
it, the one that ends up against the aluminium. The lip then points straight
up and the counterbores open at the top.

That orientation is chosen, not incidental:

- A 52.6 × 40 mm first layer, so nothing needs a brim.
- **No supports anywhere.** The only overhang is the 1 mm chamfer round the
  mating face, which is 45°. The counterbore is a hole that gets *wider* as
  it rises, so its step is an upward-facing ledge, not a ceiling.
- The mating face comes off the smooth bed flat, which is what it has to be.
- The two bolt pockets are **open at the back edge** of the cap. That is
  deliberate, not a modelling slip — see `direction.md`. They print as open
  slots and need nothing special.

| | |
| --- | --- |
| Nozzle / layer | 0.4 mm / 0.2 mm |
| Walls | **4** — the material beside each bolt pocket is only 1.3 mm, so it wants to be solid perimeter rather than infill |
| Infill | 25 %, gyroid |
| Supports | none |
| Brim | none |

The 1 mm chamfer round the mating face is there to keep elephant's foot off
it. Leave first-layer squish at its usual setting and do not add a second
chamfer in the slicer.

## Fitting

1. **Check the bolts bottom out on the part, not in the boss.** Wind an
   M5 × 16 into a bare boss by hand first and see how deep it goes. The cap
   is cut for 9 mm of thread in the boss and 7 mm of bolt inside itself. If a
   boss is tapped shallower than 9 mm the bolt will jam before it clamps —
   tell me and I will raise `GRIP` to suit.
2. Offer the cap up with the lip pointing **away from the extrusion**, on the
   ribbed side. The open side of the bolt pockets faces the back, where the
   extrusion closes them off.
3. Nip both bolts up finger-tight, check the cap is square to the face, then
   tighten gently. This is plastic: snug, not torqued.

## Before you print

The gauge above answers most of this. Width (52 mm) and depth (15 mm) are
measured. Two numbers are not:

- **`BOSS_Y` (5.5 mm)** — how far the bolt centres sit from the flat back.
  **If this is wrong the cap will not bolt on at all**, so it is the one to
  check. A depth gauge from the back face to the hole does it.
- **`CROWN` (4.0 mm)** — how much higher the middle of the foot face is than
  the side edges. It only reaches the part through `BOSS_Y`, so a millimetre
  either way is survivable.

Change the numbers in `params.py`, run `python3 build.py`, and the STL and
every render regenerate.

## Two things to watch on the first fit

- **The bottom cap and the base plate.** A 25 mm lip at the lower end of the
  foot rest sweeps through an arc as the pedal moves. Check it clears the
  base plate and the linkage at full travel before printing the other three.
- **The back of the cap and the pedal arm.** The cap reaches 0.4 mm *behind*
  the extrusion's back face, to keep material behind the bolt heads. That is
  little enough to ignore unless the arm is hard up against the end of the
  extrusion — worth a glance when the first one goes on.
