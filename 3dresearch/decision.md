# Decision: Bambu Lab X2D

**Decided 2026-08-30 MDT.** Supersedes the open comparison in `printer-shortlist.md`,
which stays as the record of how this was reached.

## What was chosen

Bambu Lab X2D. ~£569 base, ~£769 for the Combo with AMS 2 Pro.

> **Premise revised 2026-08-30 MDT.** This decision was made on the assumption of an
> unheated garage. The space is in fact climate controlled at 10–20 °C year round,
> which materially weakens the argument below. The decision still stands, but for
> narrower reasons — see "How the revised premise changes this".

## Why

- **Active 65 °C chamber heating.** The original deciding factor. A passive enclosure
  drifts with ambient temperature; an active chamber holds its own regardless, which
  is what prevents ABS and ASA warping and improves layer bonding on tall parts.
- **It removes a decision instead of forcing one.** The research had stalled on
  "will you actually print ABS/ASA, or is PETG enough?" The X2D makes that question
  moot — the capability is present either way.
- **In budget.** £569 against a £500–900 range, leaving room for the accessories
  that materially affect print quality.
- **300 °C nozzle** covers ABS, ASA, PC and nylon. Only a narrow band of exotic
  materials needs more.

## What was knowingly accepted

- **Dual-nozzle maintenance.** The second nozzle is the X2D's marketing headline and
  the least relevant feature for single-material functional parts. It still needs
  cleaning and alignment whether or not it gets used.
- **Reduced build area on the second nozzle** — 235 mm in X rather than 256 mm.
- **Nylon and carbon-filled filaments are single-nozzle only.** Relevant if
  functional parts later push toward CF composites.
- **Bambu ecosystem lock-in.** Cloud-leaning platform, closed firmware. LAN-only
  mode exists and is worth enabling. Prusa was the open alternative and was passed
  over on cost.

## How the revised premise changes this

At 10–20 °C controlled ambient rather than a freezing garage, a passive enclosure
performs far better than assumed. A P2S with its bed at 100 °C reaches roughly
40–50 °C in the chamber — enough for ASA and for small-to-medium ABS parts. The
optimal band for ABS/ASA is 55–65 °C, which only the X2D's active chamber reaches.

So the honest position:

- The X2D remains the **better** machine for ABS/ASA, especially larger warp-prone
  parts, and at the low end of the range (10 °C in winter) passive heating gets
  marginal.
- It is no longer close to a **necessity**. The P2S at ~£90 less would have been a
  defensible choice, and the earlier framing overstated the case.
- The X2D is still justified if ABS/ASA is genuinely in the plan, and it still buys
  freedom from having to predict that in advance. That was always the strongest
  argument, and it survives.

## Still to decide

**Base (~£569) or Combo with AMS 2 Pro (~£769)?** The case for the Combo was built on
a damp garage, and climate control undermines it. See `setup.md`.
