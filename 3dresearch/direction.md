# 3dresearch

**Status:** working

## What it is
A place to research 3D printers — the machines, not the models they produce.
Gathering what is worth knowing before spending money or time: which printers are
worth buying, how the technologies differ, what materials suit what jobs, what goes
wrong and why.

The first question — which printer to buy — is settled: a Bambu Lab X2D, for an
unheated garage, aimed at functional parts. See `decision.md`. The project now
carries that reasoning forward into running the machine well.

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

- `decision.md` — **the printer chosen, and why.** Start here.
- `requirements.md` — the buying brief the decision was judged against.
- `printer-shortlist.md` — the candidates and comparison that led to it.
- `setup.md` — running an X2D in the workshop; humidity, and the buy list.
- `order-review.md` — review of the actual cart before purchase.
- `filament-catalogue.md` — Bambu CA filament prices, captured 2026-08-30 MDT.

## Open questions
- **Is this a functional-parts machine or a multi-colour one?** The order (8 slots,
  8 PLA colours, no PETG or ABS) contradicts the requirements on both counts. One of
  the two needs correcting. See `order-review.md`.
- Base vs Combo is **resolved**: the Print More Bundle carries two AMS 2 Pro units,
  which also settles the humidity question — eight spools live in active drying.
- Does model creation belong in this project or its own? Parametric CAD as code
  (OpenSCAD, CadQuery) can generate printable parts without a GUI, which makes it a
  plausible sibling project rather than a widening of this one.
- Does this stay notes-only, or does it want structured data and tooling? So far
  prose has been sufficient.
