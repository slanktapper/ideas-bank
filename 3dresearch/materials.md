# Material choice by job

Working notes on picking filament for a given part. Prices from
`filament-catalogue.md` (CAD, Bambu CA store).

## Toolbox trays and drawer organisers

**Use PETG Basic ($13.74).** Two independent reasons, either of which alone would
decide it.

**Chemical exposure.** A toolbox means oils, grease, WD-40, brake cleaner, degreaser.
PETG is unaffected by most oils and household chemicals. PLA has genuinely poor
chemical resistance — testing shows tensile strength losses above 70 % and impact
resistance dropping below 20 % after acetone exposure. This applies even in a
climate-controlled workshop, because it is contact rather than temperature.

**Heat, if the box ever travels.** PLA softens around 60 °C. A toolbox left in a
vehicle in summer sun exceeds that easily, and trays sag. PETG holds to roughly
80 °C, which survives vehicle storage. If the box never leaves a 10–20 °C workshop
this factor is moot — but the chemical one is not.

**Toughness.** Tools get dropped into trays. PLA is brittle and cracks at corners and
thin walls; PETG flexes instead. Better failure mode for something holding heavy metal.

### Why not the others

- **PLA** — cheapest to print and best dimensional accuracy, and genuinely fine for
  *indoor, dry, gentle* storage. A toolbox is none of those things.
- **ABS** — wrong despite the printer having the chamber for it. Trays are large flat
  parts, the exact geometry ABS warps worst on; its higher shrinkage makes drawer fit
  less predictable; and it is soluble in acetone, which lives in most toolboxes.
- **ASA** ($38.99) — same warping problem, three times the price, and its UV
  resistance is worthless inside a closed drawer.
- **PETG-CF** ($40.99) — stiffer and warps less, but abrasive (needs a hardened
  nozzle) and triple the cost. Overkill for trays.
- **PLA Tough+** ($26.99) — tougher, but still PLA on heat and chemicals, at double
  the price of PETG.

### Practical notes

- **Trays eat filament.** A full drawer of Gridfinity-style bins can run 1–2 kg.
  PETG Basic being the cheapest filament on the store is a real advantage here.
- **Gridfinity** is the de-facto standard modular bin system — worth adopting rather
  than designing a bespoke grid, since thousands of compatible bins already exist.
  See `gridfinity.md` for the spec, the generators, and what a drawer actually costs.
- Print flat on the bed. Low infill (10–15 %) is plenty; wall count matters far more
  than infill for stiffness — use 3.
- PETG has slightly more dimensional variance than PLA. **Print one test bin and
  check the drawer fit before committing to a full set.**

## Quick reference

| Job | Material | Why |
| --- | --- | --- |
| Toolbox trays, drawer organisers | PETG Basic | Oils, toughness, heat |
| General functional parts | PETG Basic | The default workhorse |
| Prototypes, fit checks, decorative | PLA Basic | Cheap, accurate, easy |
| Hot environments, engine bay, near heat | ABS | Uses the 65 °C chamber |
| Outdoor parts | ASA | UV stable |
| Flexible parts | TPU for AMS | Only AMS-compatible TPU |
| Stiff structural parts | PETG-CF / PLA-CF | Needs a hardened nozzle |
