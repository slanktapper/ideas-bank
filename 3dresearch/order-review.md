# Order review

**All prices CAD.** There are now **two** carts under consideration — an X2D order and
an H2D order. Side-by-side reasoning on which machine to buy is in `x2d-vs-h2d.md`;
this file reviews the carts themselves.

| | Option A — X2D | Option B — H2D |
| --- | --- | --- |
| Printer bundle | $1,349.00 | $2,599.00 |
| Cart total | **$1,648.48** | **$2,733.12** |
| Filament | 12 spools (6 PETG, 3 ABS, 1 ASA, 2 PLA) | 8 spools (4 PETG, 4 PLA) |
| Warranty | $89 included | not in cart |
| Headroom under $3,000 budget | $1,351 | $267 |

---

# Option A — X2D cart

Cart reviewed 2026-08-30 MDT.

## The cart

Excludes the two Low Temp reusable spools that were added and are the wrong part
(see "Outstanding" below).

| Item | Qty | Unit | Line |
| --- | --- | --- | --- |
| X2D Print More Bundle | 1 | $1,349.00 | $1,349.00 |
| Extended Warranty for X2D | 1 | $89.00 | $89.00 |
| PETG Basic — Reflex Blue, Orange, Yellow, Red, White, Black | 6 | $15.94 | $95.64 |
| ABS **Refill** — Navy Blue, Orange, Red | 3 | $14.29 | $42.87 |
| ASA — White | 1 | $38.99 | $38.99 |
| PLA Basic — Indigo Purple, Hot Pink | 2 | $16.49 | $32.98 |
| **Total** | | | **$1,648.48** |

Filament: **12 spools**, 12 kg. All bulk-sale lines are at the 45 % tier.

### Why this mix is right

Six PETG makes the functional workhorse the default, which is what `requirements.md`
asks for. Three ABS finally use the 65 °C chamber the printer was chosen for. One ASA
covers outdoor and UV work. Two PLA is enough for prototypes and fit checks without
dominating the shelf. This is the lineup the earlier all-PLA cart lacked.

## Outstanding before checkout — X2D cart

1. **The three ABS lines are Refills — bare coils with no spool.** They cannot load
   into the AMS as they are.
   - Two Bambu Reusable Spools were added, but in **Low Temp (≤ 70 °C)**, which is
     rated for PLA and PETG only. ABS needs the **High Temperature (≤ 90 °C)** spool
     (black, ABS+PC).
   - The count was also short: three refills need three spools, not two.
   - **Either** add 3 × High Temperature Reusable Spool, **or** switch the three ABS
     lines to spooled ABS.
   - The low-temp spools were discounted to $8.99 each under an "Add-ons Deal"
     ($14.99 list). Whether the high-temp SKU gets the same discount is unconfirmed.
     At full price, 3 refills + 3 high-temp spools ≈ $88 against ≈ $43 for 3 spooled
     ABS — so **unless the discount carries over, spooled ABS is cheaper**, and
     refills can be bought later to reuse those spools.
   - Not verified: whether the High Temperature spool is listed on the Canadian
     store. If it is not, switching to spooled ABS is the clean answer.

2. **Twelve spools, eight AMS slots.** Four live outside active drying, so the
   airtight boxes, desiccant and hygrometer from `setup.md` are needed after all.
   Keep PETG and ABS outside if any must be — they absorb less moisture than nylon.

3. **Possibly a discount tier short.** The cart sits at 45 % off; the collection page
   listed PLA Basic at $14.29 and PETG Basic at $13.74, implying a ~52 % tier. That is
   about $2.20 a spool. The "45% off unlocked" badge has a chevron — worth opening it
   to see what the next tier needs.

4. **No support material** for the second nozzle. Support for ABS $19.99, Support for
   PLA/PETG $44.99. Optional; the dual nozzle sits idle without one.

---

# Option B — H2D cart

Cart reviewed 2026-09-01 MDT.

## The cart

| Item | Qty | Unit | Line |
| --- | --- | --- | --- |
| Bambu Lab H2D — AMS Combo / Dual AMS 2 Pro Bundle | 1 | $2,599.00 | $2,599.00 |
| PETG Basic — Orange, Red, White, Black | 4 | $15.94 | $63.76 |
| PLA Pure — Absolute Black, Pure White | 2 | $18.69 | $37.38 |
| PLA Basic — Blue, Sunflower Yellow | 2 | $16.49 | $32.98 |
| **Total** | | | **$2,733.12** |

Filament: **8 spools**, 8 kg. Discount badge reads "Combo Deal" rather than the
"Bulk Sale" on the X2D cart.

### What is right about it

**Eight spools against eight AMS slots.** The Dual AMS 2 Pro bundle gives exactly
eight actively dried slots and the cart fills them exactly. That removes the storage
problem the X2D cart has — no airtight boxes, desiccant or hygrometer needed on day
one, because nothing lives outside a dryer.

**Half the filament is PETG.** Four PETG Basic makes the functional workhorse a real
presence rather than an afterthought, which is what `requirements.md` asks for. This
is a much better material mix than the original all-PLA X2D cart.

**No refills, so no spool problem.** Every line is a spooled product. The ABS Refill
trap that the X2D cart fell into does not arise here.

## Outstanding before checkout — H2D cart

1. **~~Over budget.~~ Resolved 2026-09-03 MDT.** The budget was raised to $3,000, so
   the $2,599 bundle and the $2,733.12 cart both fit. Price no longer rules this
   option out or decides between the two; see `x2d-vs-h2d.md`. What remains is that
   $267 of headroom is not much room for the warranty and support material in items 4
   and 5 below — the cart is close to the ceiling in a way the X2D cart is not.

2. **Nothing in this cart uses the 65 °C chamber.** No ABS, no ASA, no PC, no nylon.
   PETG and PLA both print fine on a passive enclosure. This is exactly the criticism
   made of the original all-PLA X2D cart, and it lands harder here: the H2D's chamber
   is the same 65 °C unit as the X2D's, so on this cart's contents the $1,250 premium
   buys build volume and nothing else. Port the ABS and ASA across from the X2D cart —
   ABS is **$14.29**, cheaper than every PLA line already in this order.

3. **PLA Pure at $18.69 is above the bulk tier.** `filament-catalogue.md` records PLA
   Pure at **$16.49** on the bulk tier — $2.20 a spool, $4.40 across the two. Eight
   spools may sit below the tier threshold the twelve-spool X2D cart cleared. Worth
   opening the discount badge to see what the next tier needs; adding the ABS and ASA
   from item 2 may cross it on its own.

4. **No extended warranty.** The X2D cart carries one at $89 on a $1,349 machine
   (6.6 %). On a $2,599 machine with a heavier toolhead, a bigger gantry and a 31 kg
   shipping weight, the argument for one is stronger, not weaker. Price it before
   checkout.

5. **No support material** for the second nozzle — same gap as the X2D cart. Support
   for ABS $19.99, Support for PLA/PETG $44.99.

6. **Measure the bench first.** 492 × 514 × 626 mm and 31 kg, plus two AMS 2 Pro units
   beside or on top. Substantially larger than the X2D and a two-person lift.

### Accessories the store surfaced alongside it

Not in the cart; noted because they show what the platform expects you to add.

| Item | Price | Comment |
| --- | --- | --- |
| Bambu High Flow Hotend — H2/P2S/X2D | $66.99 | Fits either machine. Worth having as a spare regardless. |
| Vision Encoder | $128.00 | Calibration accessory. Not needed to start. |
| Cutting Material Kit — Starter Pack | $59.00 | Only useful with the cutting module, which this bundle does not include. |
| Laser Material Kit — Starter Pack (49 pcs) | $96.90 | Same — the laser is on the *Laser Full Combo*, not the AMS Combo. |

The last two are the tell: if the laser and cutter are part of the appeal, this is
the wrong H2D SKU. See `x2d-vs-h2d.md`.

---

# Superseded: the original all-PLA X2D cart

## What is in it

| Item | Qty | Unit | Line |
| --- | --- | --- | --- |
| X2D Print More Bundle | 1 | $1,349.00 | $1,349.00 |
| Extended Warranty Service for X2D | 1 | $89.00 | $89.00 |
| PLA Basic 1 kg — 8 colours | 8 | $16.49 | $131.92 |
| **Total** | | | **$1,569.92** |

Filament colours: Hot Pink, Pumpkin Orange, Indigo Purple, Mistletoe Green, Red,
Blue, Jade White, Black. All PLA Basic. Combo Deal takes each from $29.99 to
$16.49 — $108 saved in total, a genuine ~45 % discount.

**The Print More Bundle** is the X2D AMS Combo *plus* a second AMS 2 Pro and a
Filament Track Switch: **eight** automatic filament slots rather than four. The
eight spools map exactly onto those eight slots, so the order is internally
consistent — it is a fully loaded multi-colour rig.

## Issue 1: every spool is PLA

This is the substantive problem. `requirements.md` says functional parts and
prototyping. PLA is the weakest common choice for that:

- Softens around 60 °C. A part in a hot vehicle, near a motor, or in direct summer
  sun will deform. Alberta summers reach this easily inside a closed car.
- Brittle. Poor impact resistance, and it snaps rather than bends.
- Creeps under sustained load — a PLA bracket under constant force slowly sags.

PLA is excellent for learning the machine, for prototypes and for anything
decorative. It is a poor structural material.

**There is no PETG in the order**, and PETG is the functional workhorse: far tougher,
much better heat resistance, still easy to print.

## Issue 2: nothing in the order needs the heated chamber

The X2D was chosen over the cheaper P2S specifically for its 65 °C active
chamber, which exists to print ABS, ASA, PC and nylon without warping. The order
contains none of those. As it stands, the machine's deciding feature goes unused, and
everything in the cart would have printed fine on the cheaper printer.

That is not an argument to change the printer — capability held in reserve has value,
and the decision is made. It does mean the material order should catch up with it.

## Issue 3: the order implies different requirements

Eight slots and eight colours is a multi-colour setup. `requirements.md` recorded
multi-colour as *not* a priority and functional parts as the goal. The cart says the
opposite on both counts.

Either is fine — but the requirements should be corrected to match reality rather
than left contradicting the purchase. Worth deciding which is actually true before
ordering, because it is the difference between a machine bought for engineering work
and one bought for colourful making.

## Suggested change — it costs less, not more

Prices from the store's filament collection (see `filament-catalogue.md`) remove any
cost argument for all-PLA: **PETG Basic at $13.74 is cheaper than PLA Basic, and ABS
at $14.29 is the same price.**

Keep the bundle. Change the eight spools to:

| | Qty | Unit | Line |
| --- | --- | --- | --- |
| PLA Basic (colours) | 4 | $14.29 | $57.16 |
| PETG Basic | 3 | $13.74 | $41.22 |
| ABS | 1 | $14.29 | $14.29 |
| **Total** | **8** | | **$112.67** |

Against the current $131.92 for eight PLA, that is **$19.25 cheaper** while covering
functional strength and finally using the heated chamber. All eight slots still full,
four PLA colours still available.

**ABS rather than ASA.** ASA is $38.99 — nearly three times PLA. Its advantage is UV
stability for outdoor parts; indoors ABS does the heat-resistance job for a third of
the price. Add ASA later if something needs to live outside.

**Not included, worth considering:** support material for the second nozzle — Support
for PLA (New Version) at $29.99, or Support for PLA/PETG at $44.99. The dual nozzle's
whole purpose is clean peelable supports, and nothing in the order feeds it. Optional
rather than essential, since single-material functional parts rarely need it.

**Tip for two AMS units:** dedicate one to PLA and the other to higher-temperature
materials. Drying cycles for PETG/ABS run hotter than PLA can survive, so keeping
them in separate units means never having to unload spools before drying.

---

# Notes that apply to either order

## Warranty

On the X2D, $89 on a $1,349 machine is roughly 6.6 %. More defensible than most extended
warranties here: the dual-nozzle toolhead is the most complex part of the printer and
the one reviewers flag for maintenance, and shipping a machine this size back for
service from Alberta is not trivial. Reasonable, not essential. The H2D cart carries no warranty line; at $2,599 and
31 kg the same reasoning argues for one more strongly.

## Not in the cart, worth having

- **Spare nozzles**, plus a **hardened** one if carbon-filled filament is ever likely.
- **Airtight boxes and desiccant** for spools not loaded in an AMS. Two AMS 2 Pro
  units cover eight spools with active drying, which handles the humidity question
  raised in `setup.md` far better than expected — but a ninth spool needs somewhere
  dry to live. The X2D cart's twelve spools need this; the H2D cart's eight do not.

## Budget note

The budget is **up to $3,000 CAD** for the printer, raised 2026-09-03 MDT from
$940–1,695 (see `requirements.md`). **Both options now fit.**

- **X2D Print More Bundle, $1,349** — full cart $1,648.48, leaving $1,351 unspent.
- **H2D AMS Combo / Dual AMS 2 Pro Bundle, $2,599** — full cart $2,733.12, leaving
  $267. Enough for the warranty *or* a support-material spool, not comfortably both.

An earlier version of this file recorded the H2D as $904 over budget. That is no
longer the case; the number was right against the old ceiling.

An earlier version of this note called the order "substantially above budget". That
was wrong — it read the prices as USD.

Worth noting: at **$16.49/kg** the filament is cheap for branded spools, so the
suggested material swaps cost effectively nothing. There is no reason to compromise
on the material mix to save money.

## Where to buy

Canadian retailers avoid cross-border delays and duties, and one is local: **Spool3D
is Calgary-based**, with in-store pickup. That is worth weighing — local support makes
warranty service far less painful than shipping a machine of this size, and it
slightly reduces the case for the extended warranty rather than strengthening it.

NEX3D lists the plain X2D Combo (single AMS) at CAD $1,199. If the same store prices
the Print More Bundle near $1,349, the second AMS 2 Pro plus Filament Track Switch is
costing about $150 — well below what a standalone AMS 2 Pro sells for, and a genuinely
good deal. Worth confirming the Combo price at whichever store you order from, since
comparing across retailers is not like for like.

## Sources

- [Bambu Lab X2D Print More Bundle — 3D Universe](https://shop3duniverse.com/products/bambu-lab-x2d-print-more-bundle)
- [Bambu Lab X2D Combo with AMS 2 Pro — NEX3D Canada](https://www.nex3d.com/products/bambu-lab-x2d-combo-with-ams-2-pro)
- [Filament drying guide for AMS 2 Pro — Bambu Lab Wiki](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function)

H2D sources are in `x2d-vs-h2d.md`.
