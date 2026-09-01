# 3dresearch

**Status:** working

## What it is
A place to research 3D printers — the machines, not the models they produce.
Gathering what is worth knowing before spending money or time: which printers are
worth buying, how the technologies differ, what materials suit what jobs, what goes
wrong and why.

The first question — which printer to buy — is down to **two options**: a Bambu Lab
**X2D** at $1,349 CAD, and a Bambu Lab **H2D** at $2,599 CAD. Both are enclosed,
actively heated to 65 °C, dual nozzle, aimed at functional parts in a climate-controlled
garage; the H2D adds roughly twice the build volume and a laser/cutting path. See
`x2d-vs-h2d.md` for the comparison and `decision.md` for the case that picked the X2D
first. The project also carries the reasoning forward into running the machine well.

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

- `x2d-vs-h2d.md` — **the two live options, side by side.** Start here.
- `decision.md` — the case that picked the X2D, and what reopened it.
- `requirements.md` — the buying brief both options are judged against.
- `printer-shortlist.md` — the candidates and comparison that led to the X2D.
- `setup.md` — running the machine in the workshop; humidity, and the buy list.
- `order-review.md` — review of both carts before purchase.
- `filament-catalogue.md` — Bambu CA filament prices, captured 2026-08-30 MDT.
- `materials.md` — which filament for which job, with reasoning.
- `filament-glossary.md` — one line on every filament in the Bambu CA range.

## Open questions
- **X2D or H2D?** The deciding question is build volume — 256 mm against 350 mm — since
  the two machines share the 65 °C chamber and the dual-nozzle design. The H2D bundle
  is $904 over the recorded budget, so choosing it means amending `requirements.md`,
  not just spending more. See `x2d-vs-h2d.md`.
- **What is the largest part actually expected?** Unanswered, and it settles the above.
- **Is this a functional-parts machine or a multi-colour one?** The X2D cart has been
  fixed (6 PETG, 3 ABS, 1 ASA); the H2D cart has not — it carries no ABS or ASA, so
  nothing in it uses the heated chamber. See `order-review.md`.
- Base vs Combo is **resolved**: the Print More Bundle carries two AMS 2 Pro units,
  which also settles the humidity question — eight spools live in active drying.
- Does model creation belong in this project or its own? Parametric CAD as code
  (OpenSCAD, CadQuery) can generate printable parts without a GUI, which makes it a
  plausible sibling project rather than a widening of this one.
- Does this stay notes-only, or does it want structured data and tooling? So far
  prose has been sufficient.
