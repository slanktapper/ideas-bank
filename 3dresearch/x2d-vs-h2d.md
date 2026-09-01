# Two ordering options: X2D and H2D

Written 2026-09-01 MDT. **All prices CAD.**

The purchase is no longer a single cart. There are two carts on the table, and they
are not variations on the same machine — they are different classes of machine at
close to double the price.

| | **Option A — X2D** | **Option B — H2D** |
| --- | --- | --- |
| Bundle in the cart | X2D Print More Bundle | H2D AMS Combo / Dual AMS 2 Pro Bundle |
| Bundle price | **$1,349.00** | **$2,599.00** |
| Whole cart as it stands | $1,648.48 | $2,733.12 |
| AMS slots | 8 (two AMS 2 Pro + Track Switch) | 8 (two AMS 2 Pro) |
| Against the $940–1,695 budget | **inside it** | **$904 over the top** |

The full carts, line by line, are in `order-review.md`.

## What is actually the same

These are the specs the printer choice was originally made on, and the two machines
do not differ on any of them:

- **Active 65 °C chamber heating.** Both. This was *the* deciding factor in
  `decision.md`, and it does not separate these two at all.
- **Dual nozzle on one shared toolhead.** Neither is IDEX. On both machines the idle
  nozzle lifts out of the way while the other prints, and on both the usable X axis
  shrinks when the second nozzle is in play. Same maintenance burden, same caveats.
- **Bambu ecosystem.** Same cloud-leaning platform, same LAN-only escape hatch, same
  AMS 2 Pro units, same filament catalogue and pricing.
- **Eight filament slots**, in both carts.

So the H2D is not "the X2D but it can do ABS properly". The X2D already does that.

## What the extra $1,250 buys

**1. Roughly twice the build volume.**

| | X2D | H2D |
| --- | --- | --- |
| Single nozzle | 256 × 256 × 256 mm | 325 × 320 × 325 mm |
| Dual nozzle | 235 mm in X | 300 × 320 × 325 mm |
| Total plate span | 256 mm | 350 mm in X |
| Print volume | ~16.8 L | ~33.8 L |
| Bed area | 65,536 mm² | 104,000 mm² |

Twice the volume, and 59 % more bed area. This is the difference between cutting a
part into pieces and gluing it, and printing it whole. It is the single most
concrete thing on this list, and the only one that cannot be worked around with
patience.

**2. A 350 °C hotend rather than 300 °C.** Opens PPS-CF, PPA-CF and the other
high-temperature composites. Note what this costs to actually use: those materials
are abrasive (hardened nozzles), hygroscopic beyond what an AMS 2 Pro can handle
(an AMS HT dries to 85 °C and is a separate purchase), and expensive — PPA-CF is
**$190.99** a spool in `filament-catalogue.md`, thirteen times PETG. The 300 °C
nozzle on the X2D already covers ABS, ASA, PC and nylon, which is where functional
parts actually live.

**3. An expansion path into laser and cutting.** The H2D platform takes a 10 W or
40 W laser module and a cutting module — engraving, cutting plywood and acrylic,
drawing. **The bundle in the cart does not include any of this.** That is the
*Laser Full Combo*, a different and dearer SKU with laser-safe glazing, an air pump,
exhaust ducting and an emergency stop. The AMS Combo in the cart is a 3D printer.
The laser is a door left open, not a thing being bought — and switching between
print and laser is a physical toolhead swap, not a menu option.

**4. Faster motion.** 1000 mm/s toolhead speed, 20,000 mm/s² acceleration, servo
motors. Real, but the smallest item on this list: print time on functional parts is
dominated by geometry and cooling, not by how fast the gantry can theoretically move.

## What the extra $1,250 also costs

- **Bench space.** 492 × 514 × 626 mm against the X2D's 392 × 406 × 478 mm — about
  59 % more benchtop, and 148 mm taller. Worth measuring the actual spot in the
  garage before ordering, along with the two AMS units that sit beside or on top.
- **Weight.** 31 kg against 16.25 kg. A two-person lift, and it wants a bench that
  will not flex.
- **$904 over the recorded budget**, which is not a rounding error. It is a 53 %
  overrun on a range that was settled deliberately in `requirements.md`.

## How this reads against the requirements

`requirements.md` asks for functional parts and prototyping, in a climate-controlled
10–20 °C garage, within $940–1,695, with some tinkering acceptable. Measured against
that brief as written:

- **The X2D meets it.** Every requirement, including the budget, with room left for
  filament and accessories.
- **The H2D exceeds it on capability and breaks it on budget.** Nothing in the brief
  asks for a 350 mm build plate, a 350 °C nozzle, or a laser.

That is not an argument that the H2D is wrong. It is an argument that choosing it
means **changing the brief**, not just spending more — and the honest version of
that change is one of:

- *"Build volume is a requirement I under-specified."* The most likely one. If parts
  over 256 mm are genuinely expected, no amount of X2D is going to help, and the
  gluing-parts-together tax is paid on every single print for years.
- *"Laser and cutting are wanted."* If so, the AMS Combo in the cart is the wrong
  H2D SKU — the Laser Full Combo is. Buying the AMS Combo *for* the laser path means
  paying the H2D premium now and the laser premium later.
- *"The budget was a guess and $2,600 is fine."* Legitimate, but it should be
  written down as such rather than left contradicting the requirements file.

## Recommendation

**Option A, the X2D, unless build volume is the answer to a real question.**

The reasoning that picked the X2D — active chamber heating, functional parts, a
climate-controlled workshop — is entirely unaffected by the H2D's existence, because
the H2D's chamber is identical. What separates them is size, a hotter nozzle, and a
laser that this bundle does not include. Of those three, only size is likely to
matter for what `requirements.md` describes, and it matters *a lot* if it matters
at all.

So the deciding question is narrow and answerable: **what is the largest thing you
actually expect to print?** Under 256 mm, the H2D is $1,250 for headroom. Over it,
the X2D is a machine that will annoy you on a schedule.

Two smaller notes that apply whichever is chosen:

- **The H2D cart contains no ABS and no ASA.** Nothing in it uses the 65 °C chamber —
  the same problem the original all-PLA X2D cart had. If the H2D is chosen, port the
  material mix across from the X2D cart, not just the colours.
- **The X2D cart carries an $89 extended warranty; the H2D cart does not.** On a
  $2,599 machine the warranty argument gets stronger, not weaker.

## Sources

- [Bambu Lab H2D — Technical Specifications](https://bambulab.com/en/h2d/tech-specs)
- [Bambu Lab's New H2D 3D Printer: Technical Specifications and Pricing — 3D Printing Industry](https://3dprintingindustry.com/news/bambu-labs-new-h2d-3d-printer-technical-specifications-and-pricing-237763/)
- [Bambu Lab X2D vs Bambu Lab H2D: Key Differences — Vertex 3D](https://www.vertex3d.co/blog/bambu-lab-3d-printers-14/bambu-lab-x2d-vs-bambu-lab-h2d-compact-efficiency-vs-full-power-120)
- [Bambu Lab H2D vs X2D — MakerSpecs](https://makerspecs.com/en/compare/bambu-lab-h2d-vs-bambu-lab-x2d/)
- [Beyond Single Extrusion: A Maker's Guide to the X2D and H2D — MatterHackers](https://www.matterhackers.com/articles/beyond-single-extrusion-a-makers-guide-to-the-bambu-lab-x2d-and-h2d)
- [How to Use Dual Nozzles to Print Large Models on the H2D — Bambu Lab Wiki](https://wiki.bambulab.com/en/h2/print-350mm-model-dual-nozzle)
- [Unboxing Guide for H2D AMS Combo and Laser Full Combo — Bambu Lab Wiki](https://wiki.bambulab.com/en/h2/manual/unboxing-ams-combo-and-laser-full-combo)
- [Bambu Lab H2D Pro vs H2D Combo — 3DChimera](https://3dchimera.com/blogs/connecting-the-dots/bambu-lab-h2d-pro-vs-h2d-combo-which-one-is-right-for-you)
- [Bambu Lab H2D Review (2026) — 3DTechValley](https://www.3dtechvalley.com/bambu-lab-h2d-review/)
