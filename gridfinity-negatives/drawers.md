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

| Code | Location | W × D × H (mm) | Grid | Positions | Margins | Bin height | Bins printed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `KWL1N1T` | kitchen, west wall, lower, 1st north column, 1st from top | **533 × 328.5 × 63** | 12 × 7 | 84 | 29.0 left / 34.5 front | 5U | **1 of 15** |

Measured 2026-09-25 MDT; the left gap corrected 2026-09-26 — see below.

### `KWL1N1T` — kitchen, west wall, lower section, 1st north column, 1st from top

**Intended contents:** BBQ lighters, Bic lighters, flashlights, a GPS,
accessories, keychains. Measured 2026-09-25 MDT; item list is
`items-KWL1N1T.yml`.

**Every bin in this drawer is one height.** The value is declared once, in
`items-KWL1N1T.yml` under `defaults: bin_height_u`, and reaches every bin
including the auto-filled spares.

**5U, locked in 2026-09-25 MDT.** 38.8 mm tall with the lip, **28 mm usable
depth**. Well under the 63 mm drawer, so shallow bins you can see into rather
than deep ones things get lost in.

Items thicker than 28 mm stand proud of the rim. The drawer has room for it:

| Item | Thickness | At 5U |
| --- | --- | --- |
| BBQ lighter | 24 mm | inside |
| Bic lighter | 12 mm | inside |
| Flashlight | 39 mm | protrudes 11 mm |
| GPS, Accessories | 40 mm | protrudes 12 mm |

The cost is stacking. At 8U the BBQ bin took two lighters stacked in 49 mm; at
5U it takes **one**. The Bic bin drops from 12 to 6.

### Alignment and gaps

Grid in the **back-right corner**, flush against the back and right walls — the
standard for every drawer (see the README). All the slack collects into two
strips:

| Gap | Size | How it was established |
| --- | --- | --- |
| **Left** (width slack) | **29.0 mm** | Re-measured by tape after bin 1 misfitted. `533 − 12 × 42 = 29.0` exactly, so it agrees with the recorded drawer width. |
| **Front** (depth slack) | **34.5 mm** | Gauged with the 31–35 mm sticks, and confirmed by bin 1's front edge fitting. Never in doubt. |
| Right, back | 0 — against the wall | — |

The gauges in `gauge-library.yml` are the 12.5–19 mm set from before the grid
was pushed into the corner, plus the 31–36 mm set. **No 26–30 mm ladder was
ever printed**, and none is needed now: the left gap is settled by measurement
and by arithmetic that agrees with it.

Bins are numbered 1–15, front to back then left to right, so a change can be
asked for by number rather than by cell range.

### Layout as directed

Rearranged 2026-09-25 MDT. Every bin has a stated position, so the
arrangement cannot drift on a re-run. **84 of 84 units, 15 bins.**

Printed sizes are what lands on the plate, extensions included.

| # | Cells | Bin | Printed mm | Item | Holds | Printed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A1:C1 | 3×1 **+29L +34.5F** | 154.5 × 76.0 | Spare — corner bin | — | |
| 2 | D1:E1 | 2×1 +34.5F | 83.5 × 76.0 | Spare | — | |
| 3 | F1:I1 | 4×1 +34.5F | 167.5 × 76.0 | **GPS** | **0 of 1** | |
| 4 | J1:L1 | 3×1 +34.5F | 125.5 × 76.0 | Spare | — | |
| 5 | A2:B3 | 2×2 **+29L** | 112.5 × 83.5 | Spare | — | |
| 6 | C2:E3 | 3×2 | 125.5 × 83.5 | Accessories | 1 | |
| 7 | F2:J3 | 5×2 | 209.5 × 83.5 | Flashlights | 2 of 4 | |
| 8 | K2:L3 | 2×2 | 83.5 × 83.5 | Spare | — | |
| 9 | A4:A5 | 1×2 **+29L** | 70.5 × 83.5 | Spare | — | |
| 10 | B4:C5 | 2×2 | 83.5 × 83.5 | Spare | — | |
| 11 | D4:H5 | 5×2 | 209.5 × 83.5 | Spare | — | |
| 12 | I4:L5 | 4×2 | 167.5 × 83.5 | Accessories (right edge) | 1 | |
| 13 | A6:F7 | 6×2 **+29L** | 280.5 × 83.5 | BBQ lighters | 1 of 4 | |
| 14 | G6:I7 | 3×2 | 125.5 × 83.5 | Accessories | 1 | |
| 15 | J6:L7 | 3×2 | 125.5 × 83.5 | Bic lighters | 6 of 10 | **✓ 2026-09-26** |

### Print status

**Bin 15 is printed and in the drawer.** `J6:L7`, a plain 3×2×5U — no
extension, no moulded label shelf, code engraved underneath — 125.5 × 83.5 ×
38.8 mm, about 51 g.

It is the first of the fifteen to be printed **and fit**. Bin 1 was printed
before it and is scrap: its front extension fitted and its left did not, which
is exactly what located the 9.5 mm error in the left gap. Bin 15 touches
neither wall, so it was never in doubt — which is also why it is the useful
one to have in hand: it confirms the 42 mm pitch, the 5U height and the
engraving on a part with no extension to explain a misfit.

The flag lives in `items-KWL1N1T.yml`, on the bin itself:

```yaml
- name: Bic lighter
  at: J6
  printed: true   # 2026-09-26 MDT
```

so `gfneg layout` reports progress rather than this file being the only record
of it:

```
Printed  : 1 of 15 bins (✓).  Still to print: 1, ..., 14
```

**Fourteen bins outstanding, ~809 g.** Four of them — 1, 5, 9 and 13 — are the
left-reaching parts regenerated after the gap correction; the earlier bin 1
that located the error is scrap.

### The GPS does not fit box 3

A front-row bin is **1 unit + the 34.5 mm gap = 76.0 mm deep, whatever its
length**. The GPS is 75 mm wide, which leaves 1 mm for two walls.

| Wall | Interior | vs GPS 167 × 75 |
| --- | --- | --- |
| 2.4 mm | 162.7 × 71.2 | short 4.3 and 3.8 mm |
| 1.0 mm | 165.5 × 74.0 | short 1.5 and 1.0 mm |

Lengthening the bin does not help — depth is the binding constraint, and every
front-row bin has the same depth. **The GPS needs two units of depth.** Until
that is resolved it is recorded as holding 0 of 1.

**Bins renumber by position**, front to back then left to right, so the numbers
above are not the ones used before the rearrangement.

### The front row absorbs the front gap

Bins 1–4 are **all exactly one unit deep** and together span the full width.
They are the ones lengthened over the measured 34.5 mm front gap — a bin two
units deep could not be extended without losing a row.

The **left** gap has no equivalent row: bins 1, 5, 9 and 13 all start at
column A but none is one unit wide. Absorbing it meant widening those four,
which is what they now do.

### What the bins actually hold

`gfneg layout` prints a `holds` column, because a stated bin size says nothing
about what goes in it. Four bins report a shortfall against the quantity held:

| Bin | Holds | Have | Why |
| --- | --- | --- | --- |
| 3 GPS, F1:I1 | 0 | 1 | 76.0 mm deep against a 75 mm GPS — see above |
| 7 Flashlights, F2:J3 | 2 | 4 | 78.7 mm across takes two 39 mm barrels; 28 mm of depth is one layer |
| 13 BBQ lighters, A6:F7 | 1 | 4 | 78.7 mm across takes one 43 mm lighter; at 5U there is no second layer |
| 15 Bic lighters, J6:L7 | 6 | 10 | assumed 81 × 24 mm, not measured |

Two of those are the price of the **5U height, locked in deliberately**: at 8U
the BBQ bin stacked two lighters and the Bic bin held twelve. Shallow bins you
can see into were worth more than the stacking.

The BBQ figure is also understated — see *Bin capacity is a lower bound* at the
foot of this file. The lighters go in diagonally and were measured doing so.

Taking all four BBQ lighters squarely would need a 3-unit-deep bin, 120.7 mm
across, enough for two abreast. That is 6 units the drawer does not have.

### How the gaps were dealt with — settled

The 42 mm pitch leaves 29.0 mm down the left and 34.5 mm across the front, 15%
of the floor. The options were weighed and the answer is now decided:

| Option | Outcome |
| --- | --- |
| **Push the grid to one corner** | **Done — back-right, and now the rule for every drawer.** Collects the slack into two usable strips instead of four dead ones. |
| **Gap gauges first** | **Partly.** The front gap was gauged with printed sticks. The left was not, and a 9.5 mm error survived into bin 1 — the strongest argument there is for gauging both. The standard ladder is −3, −2, −1, 0, +1. |
| **Bins that reach into the gap** | **Done — the chosen answer.** Seven bins are built oversize and meet the walls, so there is no leftover to fill. |
| **Printed spacers** | Not needed. `gfneg drawer` still writes them for drawers whose edge bins are standard. |
| **Pad the edge baseplate tiles** | Rejected — needs code cq-gridfinity does not have, and the oversize bins already close the gap. |
| **Leave it** | Rejected. Bins shift when the drawer is pulled. |

The depth was re-measured and is 328.5 mm. An eighth row needs 336 mm, so the
grid stays 12 × 7.

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

### Measured, corrected 2026-09-26 MDT

The left gap was first taken as 38.5 mm. **It is 29.0 mm.** Bin 1 carries both
extensions, and when it was printed its front fitted and its left did not —
which located the error precisely, because only one of the two could be wrong.

29.0 is exactly `533 − 12 × 42`, so the drawer is the **533 mm** originally
recorded. The front measurement of 34.5 stands and was never in doubt.

| Gap | First taken as | Actual |
| --- | --- | --- |
| Left | 38.5 mm | **29.0 mm** |
| Front | 34.5 mm | 34.5 mm |

Cost: four bins reprinted — 1, 5, 9 and 13, the ones reaching left.

### Superseded: gauged, 2026-09-25 MDT

The gaps were measured with the printed gauges, with the grid in the
back-right corner so each gap is the whole slack on that axis:

| Gap | Measured | Predicted from the recorded 533 × 328 |
| --- | --- | --- |
| **Left** | **29.0 mm** | 29 mm |
| **Front** | **34.5 mm** | 34 mm |

So the drawer is **533 × 328.5 mm**, not 533 × 328. The depth was right to
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
| 1 Spare, A1:C1 | 3×1 | +29.0 left **and** +34.5 front | 154.5 × 76.0 mm |
| 2 Spare, D1:E1 | 2×1 | +34.5 mm front | 83.5 × 76.0 mm |
| 3 GPS, F1:I1 | 4×1 | +34.5 mm front | 167.5 × 76.0 mm |
| 4 Spare, J1:L1 | 3×1 | +34.5 mm front | 125.5 × 76.0 mm |
| 5 Spare, A2:B3 | 2×2 | +29.0 mm left | 112.5 × 83.5 mm |
| 9 Spare, A4:A5 | 1×2 | +29.0 mm left | 70.5 × 83.5 mm |
| 13 BBQ lighters, A6:F7 | 6×2 | +29.0 mm left | 280.5 × 83.5 mm |

**Every wall is met.** Row 1 closes the front gap across the full width; bins
1, 5, 9 and 13, the leftmost of each band, close the left gap down the full
depth. Bin 1 is the corner and the only one extended both ways.

Dropping the BBQ bin from 7 units to 6 freed column G, taken by the
accessories bin at G6:I7 between the lighters and the Bics.

**The extension rescued the BBQ bin.** At 6×2 on the grid alone it is 246.7 mm
inside and a 272 mm lighter does not fit at all, at any angle. With the 29.0 mm
reach it is 275.7 mm inside, and 286.7 mm across the diagonal.

### Still unmeasured

- **Bic lighter** — commodity size, not measured from yours.
- **Accessories** — width and height assumed to match the large GPS.

**Grid: 12 × 7 units, 84 positions.** 504 × 294 mm of grid in a 533 × 328.5 mm
floor, leaving 29.0 mm down the left and 34.5 mm across the front — 15% of the
floor, all of it now inside a bin rather than left over.

**Baseplate: two 6×7 tiles.** Each is 252 × 294 mm, inside the H2D's
325 × 320 mm bed with room to spare.

**Two things worth knowing about these numbers:**

1. **The width is robust.** 12 units holds anywhere from 504 mm to 545 mm, so
   533 mm sits clear of both thresholds. This is why the 9.5 mm error in the
   left gap changed four bins and not the grid.
2. **The depth is 7.5 mm short of an eighth row.** 8 units needs 336 mm and the
   drawer is 328.5 — an eighth row would have been 96 positions instead of 84,
   a 14% gain. Measured, not assumed, so this one is closed.

**Settled:** 533 × 328.5 is internal clear, measured at the base with the
printed gauges rather than taken from a catalogue.

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


## Bin capacity is a lower bound

`gfneg` reports capacity from **square packing only** — across the width, along
the depth, stacked in the height. It cannot see a diagonal fit.

The BBQ bin is the case in point: 275.7 × 78.7 mm inside against a 272 mm
lighter, so square packing says one. The floor's diagonal is **286.7 mm**, and
the lighters go in at an angle. Measured in the bin, they fit.

Treat a reported shortfall as *check it*, not as *it will not fit*.
