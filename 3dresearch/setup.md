# Setup: X2D in an unheated garage

Written 2026-08-30 MDT, after the printer decision. Revised the same day once the
space turned out to be climate controlled at 10–20 °C rather than unheated.

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

## The Combo case, weakened

The **AMS 2 Pro has active filament drying built in** — a heating module with
controlled intake and exhaust vents, drying to 65 °C, rotating spools for evenness,
and RFID auto-matching of drying settings for Bambu filament.

That was the argument for paying ~£200 more: in a damp garage the AMS is a filament
dryer as much as a colour changer, addressing the biggest environmental risk to your
prints.

**Climate control undermines that argument.** If the space is drier than an unheated
garage — which a heated space usually is — then the drying function is a convenience
rather than a fix for a real problem, and the Combo reverts to being a ~£200
multi-colour upgrade. Multi-colour was explicitly not a priority.

**Revised recommendation: measure first, then decide.** Buy a £10 hygrometer, put it
in the space, and look at it for a fortnight.

- **Consistently under ~50 % RH** → base X2D, keep the £200. Airtight boxes with
  desiccant handle storage perfectly well at that humidity.
- **Regularly above ~55–60 %** → the Combo earns its place, or buy a standalone
  dryer later if multi-colour still holds no appeal.

The AMS can also be added afterwards. There is no penalty for starting with the base
machine and buying one later if the readings justify it.

One caveat: drying ABS or PETG runs hotter than PLA and TPU can survive. Remove
PLA and TPU spools from the AMS before running a high-temperature dry cycle.

## Buy list

Essential:

- **PLA** — for learning the machine and for parts that don't need heat resistance.
- **PETG** — the functional workhorse. Tougher and more heat-tolerant than PLA,
  far easier than ABS.
- **Airtight storage + desiccant** — even with an AMS, spools not loaded need it.
  4-litre food containers with reusable desiccant work as well as anything sold for
  the purpose.
- **Hygrometer** — now the highest-value £10 you can spend, because it decides the
  £200 Combo question. Buy it before the printer if possible.

Worth having early:

- **Spare nozzles**, including a **hardened** one if carbon-filled filament is likely
  (CF is abrasive and will destroy a brass nozzle).
- **ABS or ASA** — only once the basics are working. This is what the chamber
  heater was bought for, but it is not where to start.

## First things to do

1. **Log humidity in the space for two weeks** — ideally starting now, before the
   printer arrives. This decides base vs Combo.
2. Print in PLA first to verify the machine.
3. Enable **LAN-only mode** if the cloud dependency matters to you.
4. Only then move to PETG, and to ABS/ASA after that.

## Sources

- [Filament drying guide for AMS 2 Pro — Bambu Lab Wiki](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function)
- [Bambu Lab AMS 2 Pro — official store](https://us.store.bambulab.com/en/products/ams-2-pro)
- [Filament Storage Humidity: Dry Box Setup — PrintForge HQ](https://printforgehq.com/filament-storage-humidity/)
- [3D Printing in a Garage: Fix Hot & Humid Environments — Prked](https://prked.com/post/is-your-garage-too-hot-or-humid-for-3d-printing-creating-the-perfect-environment)
- [Humidity — your #1 3D printing enemy — KiwiFil](https://www.kiwifil.shop/pages/humidity-your-number-one-3d-printing-enemy)
- [Managing temperature and humidity in 3D printing — Ruuvi](https://ruuvi.com/managing-temperature-and-humidity-in-3d-printing-and-filament-storage/)
