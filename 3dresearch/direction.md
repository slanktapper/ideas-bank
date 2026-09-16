# 3dresearch

**Status:** working

## What it is
A place to research 3D printers — the machines, not the models they produce.
Gathering what is worth knowing before spending money or time: which printers are
worth buying, how the technologies differ, what materials suit what jobs, what goes
wrong and why.

The first question — which printer to buy — is **answered**. A Bambu Lab **H2D** (AMS
Combo, dual AMS 2 Pro) was ordered 2026-09-16 MDT at $2,599 CAD, $3,533.56 all-in with
a cutting module, the Vision Encoder, a warranty and 13.5 kg of filament. See
`order-review.md`. The X2D was the alternative and was not taken; `x2d-vs-h2d.md` and
`decision.md` record the reasoning. The project now carries forward into running the
machine well.

## Why
3D printer information is scattered across vendor marketing, forum threads, YouTube
reviews, and subreddits, all of it aging fast and much of it sponsored. Working
through it once, in one place, with sources recorded, beats re-googling the same
questions every few months.

## Scope
What this does:

- Collect and organise research on 3D printers: models, technologies (FDM, resin/SLA,
  SLS), materials, print quality, reliability, running costs.
- Keep findings written down with their sources, so a conclusion can be re-checked
  later when it goes stale.
- Compare options against actual use cases rather than spec sheets.

What this deliberately does not do:

- Not a 3D modelling or slicing project — nothing here designs or prepares models.
- Not printer firmware, control software, or a hardware build.
- Not a public review site or buyer's guide for anyone else; it is personal research.

## Stack
Not chosen yet. The project starts as Markdown notes and any data files the research
produces. If it later needs code — a scraper, a comparison table generator, a cost
calculator — the stack gets picked then, and this section gets filled in.

## How to run
Nothing to run yet. Read the notes in this folder:

- `order-review.md` — **what was ordered, and what is open on arrival.** Start here.
- `setup.md` — running the machine in the workshop; bench space, humidity, buy list.
- `requirements.md` — the buying brief the purchase was judged against.
- `x2d-vs-h2d.md` — how the H2D beat the X2D. **Resolved**; kept as reasoning.
- `decision.md` — the earlier case for the X2D. **Not taken**; kept as history.
- `printer-shortlist.md` — the original wider field. **Closed**; kept as history.
- `filament-catalogue.md` — Bambu CA filament prices, captured 2026-08-30 MDT.
- `materials.md` — which filament for which job, with reasoning.
- `filament-glossary.md` — one line on every filament in the Bambu CA range.

## Open questions
- **~~X2D or H2D?~~ Settled** — the H2D, ordered 2026-09-16 MDT.
- **A second High Temp reusable spool is needed.** Two ABS refills were ordered against
  one spool, so the second kilo cannot be loaded until another is bought. Not urgent;
  see `order-review.md`.
- **Spool storage is still unbought.** Thirteen spools, eight AMS slots — five live
  outside active drying. Airtight boxes, desiccant, hygrometer.
- **Does the cutting module widen this project or start a sibling?** The order buys
  blade cutting and vinyl, which is not 3D printing. Worth deciding whether cutting
  notes live here or in their own folder.
- Base vs Combo is **resolved**: the Print More Bundle carries two AMS 2 Pro units,
  which also settles the humidity question — eight spools live in active drying.
- Does model creation belong in this project or its own? Parametric CAD as code
  (OpenSCAD, CadQuery) can generate printable parts without a GUI, which makes it a
  plausible sibling project rather than a widening of this one.
- Does this stay notes-only, or does it want structured data and tooling? So far
  prose has been sufficient.
