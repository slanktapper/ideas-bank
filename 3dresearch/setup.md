# Setup: the printer in the workshop

Written 2026-08-30 MDT, after the printer decision. Revised the same day once the
space turned out to be climate controlled at 10–20 °C rather than unheated. Revised
again 2026-09-01 MDT for the H2D option.

Written around the X2D, but the temperature and humidity reasoning applies unchanged
to the H2D — same 65 °C chamber, same AMS 2 Pro units. What differs is bench space;
see "Bench space" below.

## Bench space

| | X2D | H2D |
| --- | --- | --- |
| Machine | 392 × 406 × 478 mm | 492 × 514 × 626 mm |
| Weight | 16.25 kg | 31 kg |

The H2D needs about **59 % more benchtop** and stands 148 mm taller, before the two
AMS 2 Pro units that sit beside or on top of it. At 31 kg it is a two-person lift and
wants a bench that will not flex. **Measure the actual spot before ordering** — this
is the one setup question the H2D option raises that the X2D does not.

## What climate control already solves

Temperature is handled. At 10–20 °C the X2D's active chamber has an easy job, and
even a passive enclosure would have coped with most work. Cold-start and condensation
worries largely go away too, since the space is not swinging between freezing and warm.

What climate control may *not* handle is humidity — that depends on whether the
control is temperature-only or manages moisture as well. The section below still
applies in full if it is temperature-only, and mostly falls away if it is not.

## Humidity, if it is not controlled

Filament is hygroscopic — it pulls moisture out of the air. Wet filament causes
stringing, popping and crackling during extrusion, poor layer adhesion, and outright
failed prints. Sources researching garage printing consistently name humidity, not
temperature, as the biggest environmental challenge.

The numbers:

| Relative humidity | Effect |
| --- | --- |
| 30–45 % | Ideal storage range |
| Above 55–60 % | Moisture absorption begins to show in prints |
| Around 70 % | Rapid absorption; stringing, popping, weak layers |

An unheated UK garage sits above 60 % RH for much of the year. A *heated* space
generally runs drier, because warming air lowers its relative humidity — so a
controlled 10–20 °C works in your favour here. Whether it lands inside the 30–45 %
ideal band is worth measuring rather than assuming.

## The Combo case — resolved by the order

The **AMS 2 Pro has active filament drying built in** — a heating module with
controlled intake and exhaust vents, drying to 65 °C, rotating spools for evenness,
and RFID auto-matching of drying settings for Bambu filament.

**The order resolves this.** The Print More Bundle includes *two* AMS 2 Pro units —
eight spools kept in sealed, actively dried enclosures. Whatever the workshop's
humidity turns out to be, the filament in regular use is protected.

A hygrometer (about $20) is still worth having, but it is now a diagnostic rather
than a purchasing decision: it tells you whether spools stored *outside* the AMS need
better protection.

One caveat: drying ABS or PETG runs hotter than PLA and TPU can survive. Remove
PLA and TPU spools from the AMS before running a high-temperature dry cycle.

## Storage — bought 2026-09-23 MDT

The gap this file flagged from the start is closed. **$132.88 CAD**, ordered after the
printer arrived:

| Item | Qty | Price |
| --- | --- | --- |
| YOOPAI filament storage boxes, 4.0 L, airtight, with desiccant and labels | 6 | $54.99 |
| Wisesorb indicating silica gel beads, blue→pink, rechargeable | 8 lb (3.6 kg) | $59.99 |
| JEDEW digital hygrometer/thermometer, °F/°C | 6 | $17.90 |
| **Total** | | **$132.88** |

**The coverage works out.** Thirteen 1 kg spools against eight actively-dried AMS slots
leaves **five outside**; six boxes covers them with one spare for the 0.5 kg ABS
support. Six hygrometers, one per box.

Three notes on using it:

- **Put one hygrometer in the room, not in a box.** A box with fresh desiccant reads
  low by definition; that tells you the box works, not whether the workshop is dry.
  The open question in this file — whether the climate control manages moisture or only
  temperature — is answered by the *ambient* reading, and that is the number that
  decides whether the AMS units are fighting the room. Five boxes monitored, one room
  monitored, is the better split than six boxes.
- **Indicating gel means you can see when it is spent** — blue when dry, pink when
  saturated — and it recharges rather than being thrown away. Regeneration wants an
  oven at roughly 120 °C; the AMS dries to 65 °C, which is not hot enough to drive the
  water back out properly. Do not plan to recharge desiccant in the printer.
- **Blue-to-pink indicating gel is traditionally cobalt chloride.** Worth checking the
  listing, keeping it out of the kitchen, and not handling the beads bare-handed.

Box fit is worth checking on arrival: the boxes are listed at 9.03 × 8 × 3 in
(≈ 229 × 203 × 76 mm) and a Bambu 1 kg spool is about 200 mm across by 67 mm wide. It
fits, but with only a few millimetres to spare on the short axis.

## Buy list

**Storage is done** — see above. The rest:

Essential:

- **PLA** — for learning the machine and for parts that don't need heat resistance.
- **PETG** — the functional workhorse. Tougher and more heat-tolerant than PLA,
  far easier than ABS.
- ~~**Airtight storage + desiccant**~~ — **bought 2026-09-23 MDT.** Six 4 L boxes and
  8 lb of rechargeable indicating silica gel.
- ~~**Hygrometer**~~ — **bought 2026-09-23 MDT.** Six of them; put one in the room.

Worth having early:

- **Spare nozzles**, including a **hardened** one if carbon-filled filament is likely
  (CF is abrasive and will destroy a brass nozzle).
- **ABS or ASA** — only once the basics are working. This is what the chamber
  heater was bought for, but it is not where to start.

## First things to do

1. Print in PLA first to verify the machine.
2. Log ambient humidity in the space with one of the hygrometers left out of a box.
   That reading, not the in-box one, says whether the climate control manages moisture
   or only temperature.
3. Enable **LAN-only mode** if the cloud dependency matters to you.
4. Only then move to PETG, and to ABS/ASA after that.

## Sources

- [Filament drying guide for AMS 2 Pro — Bambu Lab Wiki](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function)
- [Bambu Lab AMS 2 Pro — official store](https://us.store.bambulab.com/en/products/ams-2-pro)
- [Filament Storage Humidity: Dry Box Setup — PrintForge HQ](https://printforgehq.com/filament-storage-humidity/)
- [3D Printing in a Garage: Fix Hot & Humid Environments — Prked](https://prked.com/post/is-your-garage-too-hot-or-humid-for-3d-printing-creating-the-perfect-environment)
- [Humidity — your #1 3D printing enemy — KiwiFil](https://www.kiwifil.shop/pages/humidity-your-number-one-3d-printing-enemy)
- [Managing temperature and humidity in 3D printing — Ruuvi](https://ruuvi.com/managing-temperature-and-humidity-in-3d-printing-and-filament-storage/)
