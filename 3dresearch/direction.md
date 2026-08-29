# 3dresearch

**Status:** working

## What it is
A place to research 3D printers — the machines, not the models they produce.
Gathering what is worth knowing before spending money or time: which printers are
worth buying, how the technologies differ, what materials suit what jobs, what goes
wrong and why. For now it is notes and findings; whether it grows any code depends on
what the research turns up.

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

- `requirements.md` — the buying brief. Everything else is judged against it.
- `printer-shortlist.md` — candidate machines, comparison, and a recommendation.

## Open questions
- **ABS/ASA, or is PETG enough?** The one question that decides the recommendation,
  because it decides whether an actively heated chamber is worth paying for.
- How cold does the garage actually get in winter? Below ~10 °C changes the answer.
- Is multi-colour printing wanted? Only really easy on the Bambu AMS route.
- Does this stay notes-only, or does it want structured data (a table of printers with
  specs and prices) that would justify a small tool?
- Once a printer is chosen: does model creation belong here, or in its own project?
  Parametric CAD as code (OpenSCAD, CadQuery) can generate printable parts without a
  GUI, which makes it a plausible sibling project.
