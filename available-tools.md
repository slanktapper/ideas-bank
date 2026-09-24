# Available tools

Physical and fabrication capability available to projects in this repository. Read
this before concluding that an idea is software-only, or that a physical part has to
be bought.

**Status: delivered, week of 2026-09-21 MDT.** The machine is physically in the
workshop. Everything below is capability in hand, not a plan — though it has not yet
been commissioned, so allow for first-print setup before promising a turnaround. See
`3dresearch/order-review.md` for the order and what is still outstanding.

---

## Bambu Lab H2D — FDM 3D printer

Chosen over the Bambu Lab X2D on build volume; the reasoning is in
`3dresearch/x2d-vs-h2d.md`. Bought as the **AMS Combo / Dual AMS 2 Pro Bundle**.

### What it can make

| | |
| --- | --- |
| Build volume, single nozzle | **325 × 320 × 325 mm** |
| Build volume, dual nozzle | 300 × 320 × 325 mm |
| Widest single-nozzle span | 350 mm in X |
| Nozzle temperature | up to 350 °C |
| Chamber | **actively heated to 65 °C** |
| Filament slots | 8, across two AMS 2 Pro units, with active drying |
| Nozzles | two, on one shared toolhead (not IDEX) |

The 65 °C chamber is the spec that matters for engineering plastics: it is what stops
ABS and ASA warping on tall or wide parts. The 350 °C nozzle reaches PC, nylon and the
high-temperature composites, though none of those are on hand.

### Blade cutting and drawing

The **Cutting Upgrade Kit** is part of the order. It cuts and draws on sheet material:

- Vinyl, cardstock, paper, thin flexible sheet — stickers, labels, stencils, masks,
  templates, gaskets from sheet material.
- Pen holder and markers, so it plots and writes as well as cuts.
- StrongGrip and LightGrip mats for different material weights.
- **30 sheets of 300 × 300 mm matte removable vinyl** in red, black and orange.

This is easy to forget, because it is not 3D printing. If a project needs labelling,
masking, a template, or a one-off decal, this is the tool, not the printer.

**Cutting is a physical toolhead swap.** Printing and cutting are not a same-session
activity — plan them as separate jobs.

### Accuracy

A **Vision Encoder** is included: a five-minute XY calibration routine that holds motion
accuracy under 50 µm for weeks. Be careful what that claims — it is *motion* accuracy,
not the tolerance of a finished part. Real FDM parts still shrink, and holes still print
undersize. Design in clearance and expect to iterate a test fit.

### Filament on hand

| Material | Amount | Good for |
| --- | --- | --- |
| **PETG Basic** | 5 kg (yellow, reflex blue, orange, white, black) | The functional default. Tough, ~80 °C, chemical and oil resistant. |
| **PLA Basic** | 5 kg (indigo purple, blue, red, black, jade white) | Prototypes, fit checks, anything decorative. Softens ~60 °C, brittle, creeps under load. |
| PLA Pure | 1 kg (milky pink) | As PLA Basic. |
| **ABS Refill** | 2 kg (orange) | Heat resistance indoors, ~100 °C. Uses the heated chamber. |
| Support for ABS | 0.5 kg | Peelable supports under ABS and ASA only. |

Material choice by job is in `3dresearch/materials.md`; every filament Bambu sells is
summarised in `3dresearch/filament-glossary.md`.

**Not on hand:** ASA (UV-stable, outdoor), TPU (flexible), PVA (dissolvable), PC, nylon,
and any carbon-filled composite. Those are orderable but need lead time, and the
abrasive ones also need a hardened nozzle that has not been bought.

**No laser.** The laser and its engraving capability live on the *Laser Full Combo*, a
different and dearer machine variant. It was not bought and cannot be added to this one
without the upgrade path. Do not plan around engraving or laser cutting.

### Supports without buying support material

PLA and PETG barely bond to each other. On a dual-nozzle machine that means PETG
interface layers under a PLA part — or the reverse — peel away cleanly, giving
breakaway supports from filament already on the shelf. Two or three interface layers,
and a generous purge on the transition. Dedicated support material is rarely worth its
price for functional parts; see the reasoning in `3dresearch/order-review.md`.

### Where it lives

A climate-controlled garage workshop in Alberta, 10–20 °C year round. Noise and fumes
are not constraints there.

Eight of the thirteen spools live in the two AMS 2 Pro units under active drying; the
rest are in six airtight boxes with rechargeable indicating silica gel, bought
2026-09-23 MDT. Six hygrometers came with them. Setup notes, humidity and the
storage reasoning are in `3dresearch/setup.md`.

---

## Modelling: Claude can produce printable files directly

This is what makes the printer usable from inside this repository rather than merely
mentionable. Parametric CAD as code — **OpenSCAD**, **CadQuery**, **build123d** — runs
headless and exports STL or 3MF from a script. No GUI, no mouse.

So a project needing a bracket, a tray, a jig or an enclosure can go from a dimensioned
description to a printable file inside a normal working session, with the model kept in
version control as source rather than as an opaque mesh. Slicing can also be driven from
the command line, through PrusaSlicer, OrcaSlicer or CuraEngine.

No stack has been chosen or set up yet. If a project needs one, pick it inside that
project and record it in its `direction.md` — per `CLAUDE.md`, do not assume a stack
silently.

---

## Deciding whether to use it

**Every project gets this check.** Physical capability is easy to forget when the
obvious framing of an idea is software.

### Say yes without asking

Propose the printer or cutter as part of the solution when the project plainly needs a
physical object and the object is within reach of the machine:

- A rigid plastic part smaller than 325 mm in every dimension.
- A mount, bracket, enclosure, tray, jig, fixture, spacer, adapter or organiser.
- A replacement for a part that is discontinued, overpriced, or nearly right but not
  quite.
- Labels, stencils, masks or templates from sheet vinyl or card — the cutter.
- A physical prototype of a form factor, to be held before it is committed to.

### Say nothing

Do not raise it when the project has no physical component at all, or when the machine
plainly cannot do the job:

- Anything needing metal, glass, or machined tolerances.
- Elastomeric or transparent parts — no TPU or clear filament on hand.
- Anything load-bearing over a person, or safety-critical.
- Food-contact surfaces. FDM parts have layer lines that trap bacteria and are not
  food-safe as printed.
- Production quantities. This is one machine; dozens of parts means days.
- Anything larger than 325 mm that cannot sensibly be split and joined.
- Laser engraving or laser cutting — not owned.

### Ask when it is plausible but not obvious

**This is the case that matters.** When a project has a physical dimension that *could*
be served by the printer, but the user may reasonably prefer to buy the thing, do
without it, or solve it some other way — **put the choice to them with
`AskUserQuestion` rather than deciding silently in either direction.**

Typical triggers:

- The project mentions hardware, a device, a sensor, a workshop or a physical
  workflow, and something will have to hold, house or mount it.
- An off-the-shelf product would work but is expensive, oversized, or a poor fit.
- The idea involves organising, storing or labelling physical things.
- A design decision hinges on how something feels in the hand.
- The project would benefit from a custom tool or fixture that does not exist.

Frame the question with what you would print or cut, roughly what it would take, and
what the alternative is. Name a recommendation. Then wait — do not start modelling on
the strength of a guess.

The failure this rule exists to prevent is silent omission: finishing a project that
would have been better with a printed part, without the user ever being told that
option was on the table.
