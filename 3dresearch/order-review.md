# Order review

Cart reviewed 2026-08-30 MDT, before purchase. **All prices CAD.**

## Current cart — 2026-08-30 MDT

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

## Outstanding before checkout

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

## Superseded: the original all-PLA cart

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

## Warranty

$89 on a $1,349 machine is roughly 6.6 %. More defensible than most extended
warranties here: the dual-nozzle toolhead is the most complex part of the printer and
the one reviewers flag for maintenance, and shipping a machine this size back for
service from Alberta is not trivial. Reasonable, not essential.

## Not in the cart, worth having

- **Spare nozzles**, plus a **hardened** one if carbon-filled filament is ever likely.
- **Airtight boxes and desiccant** for spools not loaded in an AMS. Two AMS 2 Pro
  units cover eight spools with active drying, which handles the humidity question
  raised in `setup.md` far better than expected — but a ninth spool needs somewhere
  dry to live.

## Budget note — the order is within budget

The budget is **$940–1,695 CAD** for the printer (see `requirements.md`). The Print
More Bundle at **$1,349** sits comfortably inside it, and the whole order including
warranty and 8 kg of filament comes to **$1,569.92**.

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
