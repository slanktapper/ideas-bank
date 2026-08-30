# Printer shortlist

Researched 2026-08-29 MDT against `requirements.md`.

> **Prices below are GBP from UK retailers and are NOT valid here.** This research was
> done before the Canadian context was established. The figures show only how the
> machines compare to each other. For real prices see `order-review.md` — all CAD.

## The headline finding

**Bambu Lab X2D, ~£569.** It sits inside the budget and is the cheapest machine
that pairs an enclosure with *active* chamber heating — the spec that matters most
given the garage.

> Superseded: an earlier version of this note called £500–900 a "dead zone" between
> the £480 P2S and the £1,240 Core One. That was wrong. The X2D launched 14 April
> 2026 and lands at £569, filling the gap precisely.

Note the reason to buy it is **not** its headline feature. The X2D is marketed on
its dual nozzle; for single-material functional parts that is a bonus with a
maintenance cost attached. Buy it for the chamber heater.

## Candidates

| Printer | ~UK price | Enclosure | Chamber heating | Notes |
| --- | --- | --- | --- | --- |
| **Bambu Lab X2D** | ~£569 (combo ~£769) | Yes | **Active, to 65 °C** | Apr 2026. Dual nozzle, exhaust filtration, toolhead camera. Replaces the X1 Carbon. |
| **Bambu Lab P2S** | ~£450–480 | Yes | Passive | Oct 2025 machine. Quick-swap nozzle, HEPA filtration, multi-colour via AMS (combo ~£649). |
| **Prusa Core One+** | ~£1,240 assembled | Yes | **Active, to 55 °C** | Open firmware, EU-made, spares and repair path. Kit version saves roughly £250. |
| **QIDI Q2C** | ~$379–399 | Yes | **Active** | 370 °C bimetal hotend — unusual at the price. Klipper, open-source. Reaches materials the others can't. |
| **Bambu Lab P1S** | below P2S | Yes | Passive | Older sibling, not replaced by the P2S. Only worth it on a discount. |

## Why chamber heating is the pivotal spec here

The garage is the reason this matters more for you than for most buyers.

Warping is thermal contraction: plastic laid down at ~250 °C shrinks as it cools,
pulling on the layers beneath. A *passive* enclosure just traps waste heat from the
bed and hotend — it holds maybe 30 °C and drifts with the room. An *active* heated
chamber holds 50–70 °C regardless of ambient, which is the range that actually stops
ABS and ASA warping and lets parts anneal as they print.

In a cold garage a passive enclosure is weaker than the same machine indoors. How
much that costs you depends entirely on materials:

- **PLA and PETG** — passive enclosure is fine. These cover most functional parts.
- **ABS, ASA, PC, nylon** — active chamber earns its money, especially on tall parts.

So the question that decides this: do you expect to print ABS/ASA/PC, or will PETG
cover what you need? PETG is tough, prints easily, and handles the large majority of
functional work. Most people who think they need ABS don't.

## X2D vs P2S, head to head

| | Bambu Lab X2D | Bambu Lab P2S |
| --- | --- | --- |
| Price | ~£569 (combo ~£769) | ~£450–480 (combo ~£649) |
| Chamber heating | **Active, 65 °C** | Passive |
| Nozzles | Two (main + support), 300 °C | One |
| Build volume | 256 mm cubed — drops to 235 mm in X when the right nozzle is used | 256 mm cubed |
| Filtration | Exhaust filtration, UL 2904 certified for PLA/PETG | HEPA |
| Extras | Toolhead camera | — |
| Maintenance | Higher — two nozzles to clean and keep aligned | Lower |

### What the extra ~£90–120 actually buys

**The chamber heater, and that is the part that matters for a cold garage.** A passive
enclosure traps waste heat and drifts with the room; an active one holds 65 °C
whatever the ambient. That is what stops ABS and ASA warping and lets parts anneal
as they print. It also neatly dissolves the open question this research was stuck
on — you no longer have to predict today whether you'll want ABS, because the
capability is there either way. In an unheated garage in winter that is worth more
than the price gap.

**The dual nozzle is the headline feature and the least relevant one for you.** It
exists to print supports in a second material so they peel away cleanly. Genuinely
useful for complex geometry; largely irrelevant for single-material functional parts.
And it carries real costs:

- More cleaning and nozzle-alignment work over time; repairs mean opening a
  busier toolhead.
- Build area shrinks to 235 mm in X whenever the second nozzle is in play.
- The auxiliary nozzle can't print TPU, and the AMS 2 Pro won't feed it.
- **Nylon and carbon-filled filaments are single-nozzle only** — directly relevant
  if functional parts push you toward CF composites.

So the honest framing: you are paying ~£100 for a chamber heater, and accepting a
dual nozzle you may rarely use and must maintain regardless.

## Recommendation

**Bambu Lab X2D at ~£569**, given the garage. The active chamber is the single
upgrade that most improves what this machine can reliably do in a cold, unheated
space, it fits the budget with room for accessories, and it removes the material
question from the decision entirely.

**Stay with the P2S at ~£480 if** the garage is reasonably temperate or you're
confident PETG covers your work. It is the simpler machine, with fewer things to
maintain and no dual-nozzle caveats, and reviewers consistently call it the safer,
more approachable choice. The ~£90 saved is real, and the P2S is not a compromise
for PLA/PETG functional printing.

**Prusa Core One+ (~£1,240)** remains the pick only if open firmware and long-term
repairability outrank cost. The X2D weakens its case considerably: the Core One's
main technical advantage over the P2S *was* the active chamber, and the X2D now has
that at half the price. What's left is the open platform and EU spares.

**QIDI Q2C** is now harder to justify unless you specifically need the 370 °C hotend.
The X2D's 300 °C nozzle covers ABS, ASA, PC and nylon; above that is a narrow set of
materials.

### Caveat that applies to both Bambu machines

Cloud-leaning ecosystem and vendor lock-in. LAN-only mode exists. You did not rank
repairability as your priority, so this is a flag rather than an objection — but it
is the one axis where Prusa clearly wins.

## Open questions before buying

- ABS/ASA, or is PETG enough? Decides P2S vs X2D — though buying the X2D makes the
  question moot, which is part of its value.
- Will multi-material supports ever get used? If never, the X2D's dual nozzle is
  maintenance you pay for and don't use.
- How cold does the garage get in winter? Below ~10 °C, even PETG gets unreliable
  and a passive enclosure struggles.
- Is multi-colour wanted? Only the Bambu AMS route makes it easy (combo ~£649).
- Build volume needed? All candidates sit around 256 mm cubed. Larger parts mean a
  different and dearer class of machine.

## Sources

- [Best CoreXY 3D Printers for 2026 — 3DPut](https://3dput.com/best-corexy-3d-printers-2026-complete-buyers-guide/)
- [Prusa Core One vs Bambu P1S & P2S — Eolas Prints](https://eolasprints.com/en-us/blogs/advanced-3d-printing/prusa-core-one-vs-bambu-p1s-p2s)
- [Bambu Lab P2S vs Prusa Core One — PrintPick](https://printpick.dev/compare/bambu-lab-p2s-vs-prusa-core-one)
- [Bambu Lab P2S — 3DJake UK](https://www.3djake.uk/bambu-lab/p2s)
- [Prusa CORE One+ Assembled — 3DJake UK](https://www.3djake.uk/prusa/core-one-1)
- [Bambu Lab X2D — 3DJake UK](https://www.3djake.uk/bambu-lab/x2d)
- [Bambu Lab X2 Range — Additive-X](https://www.additive-x.com/shop/3d-printers/bambu-lab/bambu-lab-x2-range.html)
- [Bambu Lab X2D: Specs, Price & What's New — Bits from Bytes](https://bitsfrombytes.com/bambu-lab-x2d-launch/)
- [Bambu Lab P2S vs X2D — Makers101](https://makers101.com/bambu-lab-p2s-vs-x2d/)
- [X2D vs P2S: Dual Nozzle Benefits vs Maintenance Tradeoffs — Call3D](https://www.call-3d.com/blogs/bambu-printer-review-hub/x2d-vs-p2s-dual-nozzle-pros-maintenance-tradeoffs-and-a-p2s-upgrade-path)
- [Bambu Lab X2D Review: Dual Nozzle, One Catch — CNC Kitchen](https://www.cnckitchen.com/blog/bambu-lab-x2d-review-affordable-dual-nozzle-printing-with-a-catch)
- [Bambu Lab X2D Combo review — Notebookcheck](https://www.notebookcheck.net/Bambu-Lab-X2D-Combo-review-Dual-nozzle-3D-printer-tested.1311491.0.html)
- [QIDI Q2C Review — 3DTechValley](https://www.3dtechvalley.com/qidi-q2c-3d-printer-review/)
- [QIDI Q2 vs Q2C: Do You Need the Heated Chamber?](https://printer-hub.ru/en/posts/qidi-q2-vs-q2c)
- [Understanding Chamber Heating — ThreeDimensionPrinters](https://threedimensionprinters.com/understanding-chamber-heating-why-ambient-temperature-matters-for-abs-and-asa/)
- [Can a 3D Printer Be Used in a Garage? — 3D Printerly](https://3dprinterly.com/can-a-3d-printer-be-used-outside-or-in-a-garage/)
