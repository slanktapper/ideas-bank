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

**Intended contents:** BBQ lighters, Bic lighters, flashlights, a GPS,
accessories, keychains. Measured 2026-09-25 MDT; item list is
`items-KWL1N1T.yml`.

**Every bin in this drawer is 8U** — 59.8 mm tall with the lip, 49 mm usable.
That is the tallest that clears the 63 mm drawer; 9U would be 66.8 mm and foul it.

### Layout as directed

Columns A–L from the left, rows 1–7 with **row 1 at the front**. Full drawer,
**84 of 84 units, 16 bins, nothing wasted.**

| Cells | Bin | Item |
| --- | --- | --- |
| A6:G7 | 7×2 | BBQ lighters |
| H6:L7 | 5×2 | GPS |
| A4:E5 | 5×2 | Flashlights |
| H4:I5 | 2×2 | Accessories |
| J4:L5 | 3×2 | Accessories |
| H1:I3 | 2×3 | Bic lighters |
| A1:C2 | 3×2 | Accessories |
| D1:E2, F1:G2, J1:K2, F3:G4 | 2×2 | Spare |
| A3:C3, J3:L3 | 3×1 | Spare |
| D3:E3, F5:G5 | 2×1 | Spare |
| L1:L2 | 1×2 | Spare |

Nine spare bins, 28 units, for the keychains and anything else.

**"Accessories" is the item formerly called GPS small.**

### The BBQ lighter bin holds two, not four

A 7×2 at 8U is **288.7 × 78.7 × 49 mm** inside. A lighter is 272 × 43 × 24:

- across the 78.7 mm width — **one** fits; two would need 86 mm
- stacked in the 49 mm depth — **two** layers

So capacity is **2 lighters**, against the 3–4 held. A second 7×2 elsewhere, or
a 7×3 here, would take all four — a 7×3 is 120.7 mm wide, enough for two
abreast, and two stacked gives four. That costs 7 more units, which the drawer
does not currently have.

### Bin capacity does not follow from bin size

Two bins hold less than the quantity held. `gfneg layout` now prints a `holds`
column and warns, because a stated bin size says nothing about what goes in it.

| Bin | Holds | Have |
| --- | --- | --- |
| A6:G7 BBQ lighters | 2 | 3–4 |
| A4:E5 flashlights | 2 | 4 |
| H4:I5 accessories | 0 at the assumed 84 mm | — |

- **Flashlights.** One 5×2 takes two: 78.7 mm across the width fits two 39 mm
  barrels, and 49 mm of depth is one layer. The right-hand bin became
  accessories, so two flashlights have no home here.
- **H4:I5 is 78.7 mm square inside**, and the small GPS is assumed to be 84 mm
  long. It does not fit. If that unit lives in this pair, it must be J4:L5.
  The 2×2 takes anything up to 78.7 × 78.7 × 49.

### Addressing the gaps

The 42 mm pitch leaves **14.5 mm at each side and 17.0 mm front and back** —
266 cm² of the 1748 cm² floor, 15%. Four ways to deal with it:

| Option | What it gives |
| --- | --- |
| **Gap gauges (do this first)** | Printed feeler sticks at known lengths — 5 per gap, ±2 mm around nominal. Foot butts against the baseplate edge, arm reaches across the gap; the longest that drops in is the gap. Length engraved underneath so they are reusable. `gfneg gauge --gap 14.5` |
| **Printed spacers** | cq-gridfinity generates corner, side and front/back fillers with interlocking pegs. Both margins clear the 4 mm minimum. Stops the grid sliding when the drawer is pulled. Already implemented — `gfneg drawer` writes them. |
| **Pad the edge baseplate tiles** | Extend the outer tiles to the drawer walls, so there is no gap and no separate parts. Neatest result, but needs code cq-gridfinity does not have. |
| **Push the grid to one corner** | Consolidates the slack into one **34 × 533 mm** back channel or a **29 × 328 mm** side channel — usable for long thin things rather than four dead strips. |
| **Leave it** | Bins shift when the drawer opens. Free. |

Re-measuring the depth remains worth doing first: at ≥336 mm the drawer takes
an eighth row, which both removes the front/back gap and adds 12 positions.

### First print set

Generated 2026-09-25 MDT. The point is to establish the real gap before
committing to a drawer's worth of parts.

| Part | Size | Mass |
| --- | --- | --- |
| Baseplate tile 6×7 | 252 × 294 × 4.75 mm | ~37 g |
| Bin 1×1×8U, coded | 41.6 × 41.6 × 59.8 mm | ~13 g |
| Bin 2×1×8U, coded | 83.6 × 41.6 × 59.8 mm | ~23 g |
| Gauges, side, 12.5–16.5 mm | 26 × L × 3 mm | ~0.7 g each |
| Gauges, front/back, 15–19 mm | 26 × L × 3 mm | ~0.7 g each |

About 80 g all in. The baseplate is one plate on its own; the bins and all
ten gauges fit together on a second.

Both bins are engraved `KWL1N1T` underneath.

### Print sessions

The full baseplate is **504 × 294 mm = 148,176 mm²** against a single-nozzle bed
of **325 × 320 = 104,000 mm²**. It cannot go on one plate however it is split,
so **two plate sessions is a hard floor**, not a choice.

Both tiles are **6×7 and identical** — one STL, printed twice.

| Session | Contents | Mass |
| --- | --- | --- |
| 1 | baseplate 6×7 + three 2-unit bar bins in the side strip | ~106 g |
| 2 | baseplate 6×7 alone | ~37 g |
| 3+ | remaining bins, including the 2×2 test bin | — |

**Use one nozzle.** Single-nozzle print area is 325 mm in X; engaging the second
drops it to 300 mm. The tile fits either way, but the leftover strip beside it
goes from **69 mm to 44 mm**, which is the difference between the bar bins
riding along and not. Everything here is one colour, so there is no reason to
load the second nozzle.

The 2×2 test bin is **83.6 mm** and the strip is **69 mm**, so it cannot share a
plate with a tile. It goes in the first bin session.

### Width re-measure, 2026-09-25 MDT

The width gap measured at roughly **35 mm**, against the 14.5 mm predicted from
a 533 mm drawer. Gauges at 34 / 34.5 / 35 / 36 mm were cut to pin it down;
36 mm is there to bound the top, since a gauge that drops in tells you nothing
about the ceiling.

**What 35 mm means depends on how it was taken**, and the two readings differ
by a whole column:

| Reading | Drawer width | Grid | Effect |
| --- | --- | --- | --- |
| 35 mm is the **total** leftover, grid pushed to one side | 539 mm | still 12 units | Layout unchanged. Margins become 17.5 mm a side if centred. |
| 35 mm is **one of two** gaps | 574 mm | **13 units** would fit (546 mm) | A whole extra column, 7 more positions. Layout changes. |

A grid of 11 units in a 533 mm drawer would also give 35.5 mm a side, which is
suspiciously close to the recorded width — worth ruling out that only 11
units' worth of baseplate was laid down when the measurement was taken.

**Either way the number is significant**: a grid unit is 42 mm, so a 35 mm gap
is 7 mm short of one. 70 mm of total dead width would swallow another column
with 28 mm to spare.

### Still unmeasured

- **Bic lighter** — commodity size, not measured from yours.
- **Accessories** — width and height assumed to match the large GPS.

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
