# Setup: X2D in an unheated garage

Written 2026-08-30, after the printer decision. The chamber heater solves the *cold*
problem. It does not solve the *damp* problem, and in a garage that is the one that
will actually cost you prints.

## Humidity is the real garage problem

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

A UK garage sits above 60 % RH for much of the year. Assume filament left out will
degrade.

This also affects **the machine**, not just the filament: moving a cold printer into
warm humid air, or heating a cold damp garage quickly, risks condensation on
electronics. Let temperature changes happen slowly.

## Why this argues for the Combo

The **AMS 2 Pro has active filament drying built in** — a heating module with
controlled intake and exhaust vents, drying to 65 °C, rotating spools for evenness,
and RFID auto-matching of drying settings for Bambu filament.

That reframes the ~£200 Combo premium. It is usually sold as a multi-colour upgrade,
which is not a priority for functional parts. But in a damp garage it is also a
**filament dryer that stores four spools in a sealed, actively dried enclosure** —
addressing the single biggest environmental risk to your prints. Bought separately, a
decent filament dryer plus dry storage would eat a meaningful share of that £200.

**Recommendation: the Combo, for the drying rather than the colours.**

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
- **Humidity indicator** — cheap, and tells you whether any of this is working.

Worth having early:

- **Spare nozzles**, including a **hardened** one if carbon-filled filament is likely
  (CF is abrasive and will destroy a brass nozzle).
- **ABS or ASA** — only once the basics are working. This is what the chamber
  heater was bought for, but it is not where to start.

## First things to do

1. Print in PLA first, indoors-grade expectations, to verify the machine.
2. Log garage temperature and humidity across a few weeks before drawing conclusions
   about what the space can support.
3. Enable **LAN-only mode** if the cloud dependency matters to you.
4. Only then move to PETG, and to ABS/ASA after that.

## Sources

- [Filament drying guide for AMS 2 Pro — Bambu Lab Wiki](https://wiki.bambulab.com/en/ams-2-pro/manual/drying-function)
- [Bambu Lab AMS 2 Pro — official store](https://us.store.bambulab.com/en/products/ams-2-pro)
- [Filament Storage Humidity: Dry Box Setup — PrintForge HQ](https://printforgehq.com/filament-storage-humidity/)
- [3D Printing in a Garage: Fix Hot & Humid Environments — Prked](https://prked.com/post/is-your-garage-too-hot-or-humid-for-3d-printing-creating-the-perfect-environment)
- [Humidity — your #1 3D printing enemy — KiwiFil](https://www.kiwifil.shop/pages/humidity-your-number-one-3d-printing-enemy)
- [Managing temperature and humidity in 3D printing — Ruuvi](https://ruuvi.com/managing-temperature-and-humidity-in-3d-printing-and-filament-storage/)
