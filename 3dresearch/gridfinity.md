# Gridfinity

Written 2026-08-30 MDT. `materials.md` already names Gridfinity as the grid to adopt
for toolbox trays rather than designing a bespoke one. This note works out what that
actually commits you to: the spec, the tooling, the cost in filament and time, and
the two or three decisions that are hard to reverse once a hundred bins exist.

## What it is

Gridfinity is an open modular storage standard: a flat **baseplate** sits in a drawer
or on a bench, and **bins** drop into it on a fixed grid. Everything — bins, lids,
tool holders, adapters — is built on the same pitch, so any part from any designer
drops into any baseplate.

Zack Freedman published it in April 2022, building on earlier work by Alexandre
Chappel, and released it for the community to extend rather than as a finished
product. That is the whole reason it matters: there are now thousands of
ready-made bins and holders, several parametric generators, and a catalogue of
800+ published designs. Adopting it means most of the parts you want already exist.

**A note on licence.** Sources disagree — the derivative generators (kennetek's, for
one) state MIT and say they match the original, while other write-ups describe a
Creative Commons NonCommercial licence. For personal workshop use the distinction
is irrelevant; it would only matter if prints were ever sold. Not worth resolving now.

## The specification

The numbers that matter, and that every generator implements:

| Thing | Value |
| --- | --- |
| Grid pitch | **42 × 42 mm** |
| Height unit (1U) | **7 mm** |
| Bin footprint | **41.5 mm** square per unit — 0.5 mm total clearance, 0.25 mm a side |
| Bin base profile | 0.8 / 1.8 / 2.15 mm chamfer stack = **4.75 mm** tall |
| Baseplate thickness | ~4.75 mm minimal, up to 7 mm for the full/reinforced version |
| Magnets | **6 × 2 mm** neodymium, one per corner per grid unit |
| Screws | M3 from below; 4.2 mm holes if using M3 heat-set inserts |

Two consequences worth internalising before ordering anything:

- **Height is quoted in units including the base.** A 1×1×3 bin is 41.5 × 41.5 × 21 mm
  overall, and the first 7 mm is the base profile, so usable interior depth is roughly
  `(U − 1) × 7 mm`. A 3U bin holds about 14 mm of stuff, not 21 mm.
- **The stacking lip adds about 4.4 mm** on top of the nominal height, and eats into
  the usable cutout depth. Bins that never stack can drop it and save both.

Sizes are written `X × Y × U` — a 2×3×6 bin is 84 × 126 mm on the plate and 42 mm tall.

The 42 mm pitch is widely reported to be as much a *Hitchhiker's Guide* joke as an
engineering decision, and it draws the most consistent criticism of the system: 1×1
gives roughly 38 mm of finger space once the lip is accounted for, which is tight,
and the next step up is 1×2 — there is no half-step in the standard. Half-pitch
(21 mm) variants exist but are a parallel ecosystem, not a compatible one.

## Fitting it to a real drawer

This is where most wasted filament goes. A 42 mm pitch almost never divides a drawer
evenly: a 400 mm drawer takes nine units (378 mm) and leaves 22 mm of dead space.
Three ways to handle it, in order of preference:

1. **Parametric baseplate with a border** — generators will pad the grid out to the
   exact drawer dimensions, centring it or pushing it to the front. This is the right
   answer for a fitted drawer and costs nothing extra.
2. **Print the grid short and leave the gap** at the back, filled with a printed
   spacer or nothing at all.
3. **Half-pitch bins** in the leftover strip — works, but it is a second system to
   maintain.

**Measure the drawer before printing anything.** Not the nominal size, the actual
internal clear dimensions at the base, which are usually a few millimetres under.

## Baseplates: pick one style and stay with it

Bins are interchangeable across the whole ecosystem. Baseplates are where the
variants diverge, and where a decision gets locked in.

| Style | What it is | When |
| --- | --- | --- |
| **Frame / thin** | Minimal grid, no magnet or screw provision | Inside a drawer, where nothing slides |
| **Skeletonised** | Thick enough for magnets, centre removed | Magnets wanted, filament not wasted |
| **Weighted** | Solid, with cavities for weights and rubber feet | Bench or desktop, where knocking things over matters |
| **Click-lock** (Clickfinity, CLICKbase) | Latching tiles, flush outer edges, no magnets | Large areas tiled from bed-sized pieces |

For a drawer that already constrains the bins on all four sides, the thin frame plate
is enough and magnets are largely redundant — gravity and the drawer walls do the
work. Magnets earn their keep on open shelving, on a bench, or in a drawer that gets
yanked hard. If magnets are wanted at all, buy 6 × 2 mm discs in bulk early; the cost
per bin is trivial but four per unit adds up fast in quantity.

Click-lock plates solve a real problem — flush edges and rigid tiling for areas
bigger than the bed — at the cost of committing to one designer's ecosystem for the
plates. Bins stay standard either way, so it is a recoverable decision, unlike the
grid pitch itself.

## Generators — do not model bins by hand

There is no reason to open CAD for a standard bin. The options, roughly:

- **Gridfinity Extended** (ostat) — the most feature-complete OpenSCAD implementation:
  swappable click-in labels, sub-divided compartments, label positioning, magnet
  options, efficient bin bottoms. Its official online version runs in **MakerWorld's
  customizer**, which means parametric generation in a browser and straight into
  Bambu Studio. Given the printer, this is the path of least resistance. GPL.
- **gridfinity-rebuilt-openscad** (kennetek) — the most widely used generator, a
  mathematical ground-up rebuild covering every bin variant, with "printable holes"
  that bridge the countersunk magnet cavities so no supports are needed. MIT.
- **Fusion 360 add-in** (Le0Michine) and various web generators for one-off bins.
- **Tool-outline tracers** (photo → cut-out insert) for tool control shadow boards.

The catalogue at `jeffbarr/gridfinity-catalog` indexes the lot — 60+ baseplates,
800+ bins, plus lids, adapters and templates. Check there before designing anything.

## What it costs, in this workshop

Community figures, for a Bambu-class printer:

| Part | Filament | Time |
| --- | --- | --- |
| 1×1 bin, ~3U | 8–15 g | minutes |
| 2×2 bin | 20–40 g | 20–40 min on a Bambu (1–2 h on a slower machine) |
| 1×1 of baseplate | ~5 g | — |
| 4×4 baseplate | 60–70 g | — |

`materials.md` puts a full drawer of bins at 1–2 kg, which at **PETG Basic $13.74/kg**
is **$14–27 per drawer** in material. That is cheap enough that filament cost is not
the constraint — *print time and attention are*. A drawer is a day of printing, not
an afternoon.

Where the waste actually happens, per the criticism worth taking seriously:

- **Fourth walls.** A bin against a drawer wall or another bin does not need all four
  sides; the redundant wall is roughly 12 % extra material for no strength.
- **Bins taller than the contents.** A 6U bin is double the filament of a 3U bin.
  Size to what goes in it.
- **Solid bases on multi-unit bins.** Bins larger than 1×1 need infill under the floor
  to sit flat. Generators offer "efficient" or "eco" bin bottoms that skip most of it.
- **Multi-colour.** Colour changes burn filament in the purge tower on every swap. On
  a plate of eight bins that is significant. Colour-code with *whole bins* in different
  colours, printed one colour per plate, not two-tone bins.

That last point is the honest use for the eight PLA colours in the order
(`order-review.md`): a colour-coded bin system, printed a plate at a time, is a
genuine reason to have eight colours loaded — but it argues for eight *single*-colour
plates, not for AMS colour changes mid-print.

## Printing them on the X2D

- **Bed size sets the maximum piece.** At 256 mm in X, one plate holds up to **6 × 6
  units** (252 mm). Anything bigger tiles from multiple pieces — most baseplate designs
  include connectors for exactly this. On the second nozzle the 235 mm limit drops that
  to 5 units, another reason bins are single-nozzle work.
- **Material: PETG Basic**, per `materials.md` — oils, toughness, heat. PLA Basic is
  fine for indoor, dry, gentle storage and for fit tests.
- **3 walls minimum, 4 for bins holding heavy tools.** Wall count, not infill, is what
  makes a bin feel solid. 10–15 % infill on bins; 15–20 % grid or gyroid on baseplates.
- **0.2 mm layers** throughout; drop to 0.16 mm only if embossed labels look rough.
- **No supports.** Bins print base-down; generators bridge the magnet cavities.
- **Large flat PETG baseplates can lift at the corners.** This is a known complaint on
  open-frame machines — the enclosed, actively heated chamber is exactly the fix, so
  it should be a non-issue here. Print baseplates with the chamber closed.
- **Tolerance is printer-specific.** PETG runs slightly looser and more flexible than
  PLA, and ±0.1–0.2 mm of horizontal expansion in the slicer is the standard
  adjustment either way.

**First job: print one 1×1 bin and one 2×2 baseplate, check the fit, tune horizontal
expansion, and only then commit to a drawer's worth.** This is the same advice
`materials.md` gives for drawer fit, and it applies twice over here — a tolerance
error found after a hundred bins is a hundred bins.

## Alternatives, and why Gridfinity anyway

Parts from these systems do not interoperate. The choice decides the next hundred
prints.

| System | Grid | Made for |
| --- | --- | --- |
| **Gridfinity** | 42 mm square | Horizontal — drawers, benchtops, cases |
| **Multiboard** | 25 mm | Vertical walls, heavy tools |
| **OpenGrid** | — | Vertical, heavy, newer |
| **HSW / IKEA Skadis** | — | Vertical, light and decorative |

Gridfinity is the standard for horizontal storage and that is the actual problem here
(toolbox trays, drawer organisers). It is not a wall system and does not pretend to be.
The common pattern is to run both: Gridfinity in the drawers, a wall system above the
bench, with adapter plates between them where needed. That is a separate decision for
a separate day.

## What this means for the project

Adopting Gridfinity is a materials-and-printing decision, not a modelling one — the
bins already exist, and the generators produce STLs from parameters without opening
CAD. That keeps it inside this project's scope. It does not answer the open question
about whether parametric CAD as code deserves its own project; if custom
tool-shaped inserts start getting designed from scratch, that is when it does.

## Open questions

- **Magnets or not?** Leaning no for drawers, yes for anything on an open bench.
  Deferrable — but not if the baseplates are printed without magnet cavities first.
- **Which baseplate style**, and whether to accept a click-lock ecosystem for large
  tiled areas.
- **Which drawers get done first**, and what their measured internal dimensions are.
  Nothing else can be sized until that is known.
- Whether the eight PLA colours become a **colour-coding scheme** with a written
  meaning per colour, or just whatever spool is loaded.

## Sources

- [Gridfinity unofficial specification — gridfinity-unofficial/specification](https://github.com/gridfinity-unofficial/specification)
- [Gridfinity Documentation (dimensioned drawings) — Stu142](https://github.com/Stu142/Gridfinity-Documentation)
- [gridfinity-rebuilt-openscad — kennetek](https://github.com/kennetek/gridfinity-rebuilt-openscad)
- [Gridfinity Rebuilt baseplate docs](https://kennetek.github.io/gridfinity-rebuilt-openscad/baseplates/)
- [Gridfinity Extended OpenSCAD — Chris's Notes](https://docs.ostat.com/docs/openscad/gridfinity-extended)
- [Gridfinity Extended on MakerWorld](https://makerworld.com/en/models/481168-gridfinity-extended)
- [Catalog of Gridfinity Designs and Other Resources — jeffbarr](https://github.com/jeffbarr/gridfinity-catalog)
- [Gridfinity — Wikipedia](https://en.wikipedia.org/wiki/Gridfinity)
- [Gridfinity unofficial wiki](https://gridfinity.xyz/)
- [Gridfinity Sizes & Dimensions](https://gridfinitylayouttool.com/gridfinity-sizes)
- [Gridfinity Print Settings: Layer Height, Infill, and Tolerances — GridPilot](https://gridpilot.us/blog/gridfinity-print-settings-guide)
- [How Much Filament Do Gridfinity Trays Actually Use? — GridPilot](https://gridpilot.us/blog/gridfinity-filament-cost)
- [7 Gridfinity Design Mistakes That Waste Your Filament — GridPilot](https://gridpilot.us/blog/gridfinity-design-mistakes)
- [Gridfinity Problems — Michael B. Musgrove](https://mmusgrove.com/3d-printing/gridfinity-problems)
- [Gridfinity vs Multiboard vs MinuteGrid — GridPilot](https://gridpilot.us/blog/gridfinity-vs-multiboard-vs-minutegrid)
- [3D Printed Organization: Gridfinity, Multiboard, HSW, OpenGrid & Skadis — Snapmaker](https://www.snapmaker.com/blog/3d-printed-organizers/)
- [CLICKbase — a no-magnet, latching Gridfinity baseplate](https://www.printables.com/model/982173-clickbase-a-no-magnet-latching-gridfinity-baseplat/files)
- [Parametric Gridfinity baseplate to fill any size drawer](https://www.printables.com/model/591623-parametric-gridfinity-baseplate-to-fill-any-size-d)
- [Unsolvable warping when printing Gridfinity in PETG — Prusa forum](https://forum.prusa3d.com/forum/prusa-core-one-how-do-i-print-this-printing-help/unsolvable-warping-when-printing-gridfinity-in-petg/)
