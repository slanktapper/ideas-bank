# Two ordering options: X2D and H2D

Written 2026-09-01 MDT; revised 2026-09-03 MDT when the budget was raised to $3,000
and the field narrowed to these two. **All prices CAD.**

These are the only two machines still under consideration. The wider shortlist —
P2S, Prusa Core One+, QIDI Q2C — is closed; `printer-shortlist.md` is kept as the
record of how the X2D was arrived at, not as a live comparison.

There are two carts on the table, and they are not variations on the same machine —
they are different classes of machine at close to double the price.

| | **Option A — X2D** | **Option B — H2D** |
| --- | --- | --- |
| Bundle in the cart | X2D Print More Bundle | H2D AMS Combo / Dual AMS 2 Pro Bundle |
| Bundle price | **$1,349.00** | **$2,599.00** |
| Whole cart as it stands | $1,648.48 | $2,733.12 |
| AMS slots | 8 (two AMS 2 Pro + Track Switch) | 8 (two AMS 2 Pro) |
| Headroom under the $3,000 budget (whole cart) | $1,351 | $267 |

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
- **$1,250 that would otherwise go unspent.** No longer a budget breach — the ceiling
  is $3,000 and the H2D cart lands at $2,733 — but the money is real, and worth
  measuring against what else it buys. See "What $1,250 buys instead" below.

## What $1,250 buys instead

With the budget at $3,000 both options fit, so the premium is opportunity cost rather
than an overrun. What it is worth comparing against:

- **Roughly a second X2D.** $1,349 for another whole machine. Two X2Ds print two
  things at once, give sixteen filament slots, and mean a failed hotend does not stop
  all printing. One H2D prints one bigger thing. For batches of small parts, two
  machines beat one large one; for single large parts, they are useless.
- **About 90 spools of PETG** at the $13.74 bulk tier — or twenty-odd spools plus a
  full set of spare hotends, hardened nozzles, an AMS HT and the storage kit from
  `setup.md`.
- **Nothing.** It stays in the account. A ceiling is not a target — `requirements.md`
  says so explicitly.

None of these is obviously better than the H2D. The point is that the premium now has
to beat a real alternative use rather than merely fit inside a range.

## How this reads against the requirements

`requirements.md` asks for functional parts and prototyping, in a climate-controlled
10–20 °C garage, up to $3,000, with some tinkering acceptable. Measured against that
brief as written:

- **The X2D meets it**, with $1,351 left over after the whole cart.
- **The H2D also meets it**, with $267 left over after the whole cart.

The budget no longer separates them. That is a real change: in the earlier version of
this note, the price ceiling was doing much of the work of the recommendation below,
and it is now doing none of it. What is left is a straight capability-versus-cost
judgment with no rule to settle it.

The brief still does not *ask* for a 350 mm plate, a 350 °C nozzle, or a laser. But
"not asked for" is much weaker than "out of budget", and one of those three has a
property the others do not.

## The one thing that cannot be added later

Almost everything separating these machines can be bought after the fact:

| | Upgradeable later? |
| --- | --- |
| Filament range | Yes — buy spools |
| High-flow hotends, hardened nozzles | Yes — $66.99, fits either machine |
| Drying for exotic materials | Yes — AMS HT is a separate unit |
| A second AMS, more slots | Yes |
| A laser / cutting module | Yes, on the H2D platform — no, on the X2D |
| **Build volume** | **No. Ever.** |

A 256 mm printer is 256 mm for its whole life. If a part is 300 mm, the options are
to split and glue it, redesign it smaller, or buy another printer. That asymmetry is
the real argument, and it is the argument the raised budget strengthens most — the
$1,250 is now buying the *only* irreversible spec on the list.

Against that: the H2D also carries an irreversible cost, which is 59 % more bench and
31 kg in a garage that has to hold it.

## Recommendation

**It is now genuinely close, and it turns on one question: what is the largest thing
you actually expect to print?**

- **Under 256 mm, reliably** → **X2D.** The chamber, the dual nozzle and the material
  range are identical, the machine is smaller and lighter, and the $1,250 goes
  further as filament, spares or simply unspent. Everything the H2D adds would sit
  unused, exactly as it would on the cart as it currently stands.
- **Over 256 mm, ever, with any regularity** → **H2D.** No amount of X2D fixes this,
  and the tax is paid on every affected print for the life of the machine.
- **Genuinely unsure** → **H2D**, now that the budget allows it. This is a change
  from the earlier recommendation, and the reason is the table above: an unsure buyer
  can add hotends, dryers and filament to either machine later, but can never add
  build volume. Under the old ceiling that argument lost to the budget. It no longer
  has to.

Worth being explicit about what would make this wrong: if the honest answer is
"almost everything I print fits in a hand", the H2D is $1,250 and half a bench for
headroom that never gets used, and the X2D is the better buy without qualification.

Two smaller notes that apply whichever is chosen:

- **The H2D cart contains no ABS and no ASA.** Nothing in it uses the 65 °C chamber —
  the same problem the original all-PLA X2D cart had. If the H2D is chosen, port the
  material mix across from the X2D cart, not just the colours. There is now budget
  room to do it: ABS is $14.29 a spool.
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
