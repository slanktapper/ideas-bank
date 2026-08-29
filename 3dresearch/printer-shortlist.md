# Printer shortlist

Researched 2026-08-29 against `requirements.md`. Prices are UK retail as found on
that date and move constantly — re-check before buying.

## The headline finding

The budget is £500–900. Nothing in that band is the right answer.

The strongest match costs about £480, and the next genuine step up costs about
£1,240. The middle of the stated budget buys machines that are worse than the
£480 one — it is a dead zone. So the real decision is: spend less than planned,
or spend meaningfully more for open hardware and an actively heated chamber.

## Candidates

| Printer | ~UK price | Enclosure | Chamber heating | Notes |
| --- | --- | --- | --- | --- |
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

## Recommendation

**Bambu Lab P2S, ~£480.** It meets every requirement, comes in well under budget,
and the £400+ left over buys filament, a dry box, spare nozzles and a hardened
nozzle for abrasives — accessories that affect output more than the price gap to a
dearer printer would. Reliable out of the box, which matches "some tinkering is
fine" rather than demanding it.

Two things to weigh against it before committing:

- **Ecosystem lock-in.** Bambu leans on cloud connectivity and its own ecosystem.
  There is a LAN-only mode. If open firmware and long-term repairability rank
  highly, this is the argument for the Core One instead — and you did not pick
  repairability as your priority, so this is a flag, not an objection.
- **Passive enclosure.** Fine for PLA/PETG in a cold garage; limiting for ABS/ASA.

**If you expect high-temp materials:** QIDI Q2C. Active chamber and a 370 °C hotend
for roughly the price of the P2S. Trade-off is a less polished experience and more
setup — acceptable given your tinkering answer, and it runs Klipper, which is open.

**If open hardware and repairability matter more than money:** Prusa Core One+,
~£1,240 assembled or ~£250 less as a kit. Over budget, but it is the only candidate
combining an active chamber with a genuinely open platform and EU spares. Building
the kit is also the fastest way to actually understand the machine.

## Open questions before buying

- ABS/ASA, or is PETG enough? This single answer decides P2S vs Q2C.
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
- [QIDI Q2C Review — 3DTechValley](https://www.3dtechvalley.com/qidi-q2c-3d-printer-review/)
- [QIDI Q2 vs Q2C: Do You Need the Heated Chamber?](https://printer-hub.ru/en/posts/qidi-q2-vs-q2c)
- [Understanding Chamber Heating — ThreeDimensionPrinters](https://threedimensionprinters.com/understanding-chamber-heating-why-ambient-temperature-matters-for-abs-and-asa/)
- [Can a 3D Printer Be Used in a Garage? — 3D Printerly](https://3dprinterly.com/can-a-3d-printer-be-used-outside-or-in-a-garage/)
