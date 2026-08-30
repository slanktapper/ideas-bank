# Order review

Cart reviewed 2026-08-30 MDT, before purchase. **All prices CAD.**

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

## Suggested change

Keep the bundle. Swap **two or three** of the eight PLA spools for:

- **PETG × 2** (black and one colour) — the functional default.
- **ASA × 1** — optional, but it is what the chamber was bought for, and ASA is
  UV-stable so parts can live outdoors.

That still fills all eight slots, costs about the same, and makes the material
lineup match the stated purpose. Five or six PLA colours is still plenty.

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
