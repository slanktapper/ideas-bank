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
- `setup.md` — running an X2D in an unheated garage; humidity, and the buy list.

## Open questions
- **X2D base or Combo?** The only live buying decision. See `setup.md` — the AMS 2 Pro
  is a filament dryer as much as a colour changer, which matters in a damp garage.
- What are the garage's actual temperature and humidity across a year? Worth logging
  rather than guessing; it decides what materials the space can realistically support.
- Does model creation belong in this project or its own? Parametric CAD as code
  (OpenSCAD, CadQuery) can generate printable parts without a GUI, which makes it a
  plausible sibling project rather than a widening of this one.
- Does this stay notes-only, or does it want structured data and tooling? So far
  prose has been sufficient.
