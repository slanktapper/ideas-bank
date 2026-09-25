# Drawer register

Measured drawers, their locations, and the Gridfinity grid each one takes.
Started 2026-09-25 MDT.

Dimensions are **internal clear** at the base of the drawer unless a row says
otherwise. Grid figures come from `gfneg drawer --width W --depth D --height H`;
re-run it rather than doing the arithmetic by hand.

## The location code

Every drawer has a seven-character code, and **every bin made for that drawer
carries it engraved on the underside**. Bins stay interchangeable — the grid is
the whole point — but a bin that leaves the drawer can be put back.

```
K  W  L  1N  1T
│  │  │  │   └── drawer:  1st from the Top
│  │  │  └────── column:  1st North
│  │  └───────── section: Lower
│  └──────────── wall:    West
└─────────────── room:    Kitchen
```

The **digit carries the position and the letter the reference**, so the drawer
below `KWL1N1T` is `KWL1N2T`, not `KWL1N1B`. `B` exists for counting up from
the bottom where that is the natural way to describe a stack.

| Segment | Values |
| --- | --- |
| Room | `K` kitchen, `G` garage, `W` workshop, `O` office |
| Wall | `N` `S` `E` `W` |
| Section | `L` lower, `U` upper, `M` middle |
| Column | number + `N` `S` `E` `W` |
| Drawer | number + `T` from top, `B` from bottom |

Codes are validated before anything is generated, and `gfneg` spells each one
back out in words — `KWL1N1T = Kitchen, west wall, lower section, 1st north
column, 1st drawer from the top`. A wrong code is invisible until the bins are
printed and unfixable afterwards, which is the entire reason for the check.

### Known codes

| Code | Location |
| --- | --- |
| `KWL1N1T` | kitchen, west wall, lower, 1st north column, 1st from top |
| `KWL1N2T` | kitchen, west wall, lower, 1st north column, 2nd from top |
| `KSL1W1T` | kitchen, south wall, lower, 1st west column, 1st from top |
| `KSL2W1T` | kitchen, south wall, lower, 2nd west column, 1st from top |
| `KEL1S1T` | kitchen, east wall, lower, 1st south column, 1st from top |
| `KEL1S2T` | kitchen, east wall, lower, 1st south column, 2nd from top |
| `KEL1N1T` | kitchen, east wall, lower, 1st north column, 1st from top |
| `KEL2N1T` | kitchen, east wall, lower, 2nd north column, 1st from top |

Only `KWL1N1T` is measured. The rest are named, not surveyed.

### How the engraving works

Recessed 0.6 mm (three layers) into the underside, mirrored so it reads when
the bin is turned over, auto-sized to the 35.6 mm pad, in DejaVu Sans Mono.

**Engraved, never embossed.** The underside is the first layer, printed against
the build plate — raised text there would have to print in mid-air. A recess is
simply an absence in the first few layers and needs no supports.

On a multi-unit bin the underside is **one pad per grid unit**, not one
continuous face, so the code goes on a single pad rather than being centred
across the bin where it would fall into the gap.

## The drawers

| Code | Location | W × D × H (mm) | Grid | Positions | Margins | Max bin | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `KWL1N1T` | kitchen, west wall, lower, 1st north column, 1st from top | 533 × 328 × 63 | 12 × 7 | 84 | 14.5 / 17.0 | 8U | measured, unverified |

### `KWL1N1T` — kitchen, west wall, lower section, 1st north column, 1st from top

**Intended contents:** BBQ lighters, Bic lighters, flashlights, two GPS units.
Measured 2026-09-25 MDT; the item list is `items-KWL1N1T.yml`.

| Item | Size (mm) | Qty | Bin | Height |
| --- | --- | --- | --- | --- |
| BBQ lighter | 272 × 43 × 24 | 3–4 | 7×5, four share it | 5U |
| Flashlight | 195 × 39 dia | 4 | 5×4, four share it | 7U |
| GPS large | 167 × 75 × 40 | 1 | 5×2 | 7U |
| GPS small | ~84 × 75 × 40 ? | 1 | 3×2 | 7U |
| Bic lighter | 81 × 24 × 12 ? | 2–10 | 3×2 loose | 8U |

**77 of 84 units used, 7 free.**

Two sizes are assumed, not measured, and are marked `?`:

- **GPS small** — "half as long" gives 84 mm. Width and height are assumed to
  match the large unit.
- **Bic lighter** — the commodity full-size figure, not measured from yours.

**Quantities vary with bulk buying**, so bins are sized for the maximum ever
held rather than today's count. A bin sized for one BBQ lighter fails the week
four arrive, and reprinting a 7×5 bin is not a small job.

**The BBQ lighters take 35 of 84 units** — 42% of the drawer for four objects.
That is simply what 272 mm items cost on a 42 mm pitch, and it is worth
deciding deliberately rather than discovering after printing.

**The BBQ lighter bin is sized to a bounding box.** They are not rectangular,
so 43 × 24 is the widest point. A traced negative (`gfneg build`) would hold
them far more tightly if the wasted space matters.

**Bin style:** plain, no label shelf — clip-in removable holders instead, so nothing
overhangs the opening. Every bin engraved `KWL1N1T` underneath.

**As reported:** 533 × 328 × 63 mm, described as "the size of components", with
"the full workable space is 101 mm".

Two heights are recorded because they constrain different things:

- **63 mm** — the working limit. Bins up to **8U** (59.8 mm including the lip)
  stay inside the drawer box, which is what keeps them from catching.
- **101 mm** — the hard ceiling of the opening. Only relevant if something is
  deliberately allowed to stand above the drawer sides.

For keychains, neither matters much: **2U or 3U** is the right depth. Anything
deeper and small fobs sink out of sight, which is the failure this drawer is
meant to fix.

**Grid: 12 × 7 units, 84 positions.** 503.5 × 293.5 mm of grid in a 533 × 328 mm
floor, giving 14.5 mm margins at the sides and 17.0 mm front and back — 15% of
the floor unused.

**Baseplate: two 6×7 tiles.** Each is 251.5 × 293.5 mm, inside the H2D's
325 × 320 mm bed with room to spare.

**Two things worth knowing about these numbers:**

1. **The width is robust.** 12 units holds anywhere from 504 mm to 545 mm, so
   533 mm sits 29 mm clear of both thresholds. Whether the figure is internal or
   nominal changes the margins but not the grid.
2. **The depth is 8 mm short of an eighth row.** 8 units needs 336 mm; 328 mm
   misses it. An eighth row would be 96 positions instead of 84 — a 14% gain for
   8 mm. If 328 mm was a nominal or catalogue figure rather than a measurement
   taken at the base, this one is worth re-checking with a tape.

**Open:** whether 533 × 328 is internal clear or nominal. It does not change the
grid, so it is not blocking — but it does change the spacer sizes, so confirm
before printing those.

## Notes on measuring

- Measure at the **base**, inside the walls. Drawer sides often taper, and the
  narrowest reading is the one that counts.
- Watch for a **front lip**, a back stop, or a slide mechanism intruding into
  the floor area.
- Nominal and catalogue figures are usually a few millimetres optimistic. Where
  a row says "unverified", that is what it means.

## Where this file lives

Here, because `gfneg drawer` is what consumes it. If a drawer list turns out to
be useful to projects beyond this one, it wants promoting rather than copying —
see the cross-project rule in `../CLAUDE.md`.
