# Drawer register

Measured drawers, their locations, and the Gridfinity grid each one takes.
Started 2026-09-25 MDT.

Dimensions are **internal clear** at the base of the drawer unless a row says
otherwise. Grid figures come from `gfneg drawer --width W --depth D --height H`;
re-run it rather than doing the arithmetic by hand.

## Naming

Locations are written coarse to fine, so the list sorts usefully as it grows:

```
<room> <wall> <section> <drawer> <column>
kitchen west   lower     top      north
```

## The drawers

| # | Location | W × D × H (mm) | Grid | Positions | Margins | Max bin | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | kitchen west wall, lower section, top drawer, north column | 533 × 328 × 63 | 12 × 7 | 84 | 14.5 / 17.0 | 8U | measured, unverified |

### 1 — kitchen west wall, lower section, top drawer, north column

**Intended contents:** keychains and fobs.

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
