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
| `KWL1N1T` | kitchen, west wall, lower, 1st north column, 1st from top | **542.5 × 328.5 × 63** | 12 × 7 | 84 | 38.5 left / 34.5 front | 8U | **gauged 2026-09-25** |

### `KWL1N1T` — kitchen, west wall, lower section, 1st north column, 1st from top

**Intended contents:** BBQ lighters, Bic lighters, flashlights, a GPS,
accessories, keychains. Measured 2026-09-25 MDT; item list is
`items-KWL1N1T.yml`.

**Every bin in this drawer is one height.** The value is declared once, in
`items-KWL1N1T.yml` under `defaults: bin_height_u`, and reaches every bin
including the auto-filled spares.

**Currently 8U — provisional.** 59.8 mm with the lip against a 63 mm drawer,
and 9U at 66.8 mm would foul it. But the drawer's numbers are unconfirmed: the
width already measured 35 mm against a predicted 14.5, so the height deserves
the same scepticism. Confirm it against the real drawer once the first print is
in, then change the one value.

### Alignment and gaps

Grid in the **back-right corner**, flush against the back and right walls — the
standard for every drawer (see the README). All the slack collects into two
strips:

| Gap | Size | Gauge ladder |
| --- | --- | --- |
| **Left** (width slack) | 29 mm predicted, **~35 mm measured** | 32, 33, 34, 35, 36 — all owned |
| **Front** (depth slack) | 34 mm predicted | 31, 32, 33, 34, 35 — all owned |
| Right, back | 0 — against the wall | — |

Bins are numbered 1–16, front to back then left to right, so a change can be
asked for by number rather than by cell range.

### Layout as directed

Rearranged 2026-09-25 MDT. Every bin has a stated position, so the
arrangement cannot drift on a re-run. **84 of 84 units, 16 bins.**

| # | Cells | Bin | Item |
| --- | --- | --- | --- |
| 1 | A1:C1 | 3×1 | Spare |
| 2 | D1:E1 | 2×1 | Spare |
| 3 | F1:I1 | 4×1 | Spare |
| 4 | J1:L1 | 3×1 | Spare |
| 5 | A2:C3 | 3×2 | Accessories |
| 6 | D2:E3 | 2×2 | Spare |
| 7 | F2:G3 | 2×2 | Spare |
| 8 | H2:I3 | 2×2 | Spare |
| 9 | J2:L3 | 3×2 | Bic lighters (rotated 90°) |
| 10 | A4:E5 | 5×2 | GPS |
| 11 | F4:I5 | 4×2 | Accessories |
| 12 | J4:L5 | 3×2 | Accessories |
| 13 | A6:G7 | 7×2 | BBQ lighters |
| 14 | H6:L7 | 5×2 | Flashlights |

**14 bins.** Two merges, 2026-09-25 MDT: the F4 spare and the H4 accessories
bin became one 4×2 at F4:I5, and the two 2×1 spares at F1 and H1 became one
4×1 at F1:I1.

The merge fixed a real problem. The old 2×2 accessories bin was 78.7 mm square
inside and could not take an 84 mm accessory in any orientation. At 162.7 mm
inside, the 4×2 clears it.

**Bins renumber by position**, front to back then left to right, so the numbers
above are not the ones used before the rearrangement.

### The front row absorbs the front gap

Bins 1–4 are **all exactly one unit deep** and together span the full width.
They are the ones to lengthen over the 34 mm front gap once it is measured —
a bin two units deep could not be extended without losing a row.

The **left** gap has no equivalent row: bins 1, 5, 10 and 13 all start at
column A but none is one unit wide. Absorbing the left gap means widening
those four, or a spacer strip.

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
| H6:L7 flashlights | 2 | 4 |
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

### Gauged, 2026-09-25 MDT

The gaps were measured with the printed gauges, with the grid in the
back-right corner so each gap is the whole slack on that axis:

| Gap | Measured | Predicted from the recorded 533 × 328 |
| --- | --- | --- |
| **Left** | **38.5 mm** | 29 mm |
| **Front** | **34.5 mm** | 34 mm |

So the drawer is **542.5 × 328.5 mm**, not 533 × 328. The depth was right to
within half a millimetre; the width was **9.5 mm** out.

**The grid stays 12 × 7.** Thirteen columns would need 546 mm and the drawer is
542.5 — short by 3.5 mm. Frustratingly close, and worth knowing that it was
checked rather than assumed.

### Bins that reach into the gap

The leftover is never a whole unit, so closing it means a few bins that are not
standard sizes. The grid keeps the 42 mm pitch throughout; only the bins facing
a wall are odd, and only on that one side.

| Bin | Grid | Reach | Printed |
| --- | --- | --- | --- |
| 13 BBQ lighters, A6:F7 | 6×2 | +38.5 mm left | 290.0 × 83.5 mm |
| 1 Spare, A1:C1 | 3×1 | +34.5 mm front | 125.5 × 76.0 mm |
| 2 Spare, D1:E1 | 2×1 | +34.5 mm front | 83.5 × 76.0 mm |
| 3 Spare, F1:I1 | 4×1 | +34.5 mm front | 167.5 × 76.0 mm |
| 4 Spare, J1:L1 | 3×1 | +34.5 mm front | 125.5 × 76.0 mm |

**The left gap is closed only in rows 6–7**, by the BBQ bin. Rows 1–5 keep it,
as directed. Dropping the BBQ bin from 7 units to 6 freed column G, filled by
a new 1×2 spare at G6:G7 between the lighters and the flashlights.

**The extension rescued the BBQ bin.** At 6×2 on the grid alone it is 246.7 mm
inside and a 272 mm lighter does not fit at all. With the 38.5 mm reach it is
285.2 mm inside and holds two.

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
