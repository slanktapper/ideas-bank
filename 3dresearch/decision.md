# Decision: Bambu Lab X2D

**Decided 2026-08-30.** Supersedes the open comparison in `printer-shortlist.md`,
which stays as the record of how this was reached.

## What was chosen

Bambu Lab X2D. ~£569 base, ~£769 for the Combo with AMS 2 Pro.

## Why

- **Active 65 °C chamber heating.** The deciding factor. The printer lives in an
  unheated garage, where a passive enclosure drifts with ambient temperature. An
  active chamber holds its own temperature regardless, which is what prevents ABS
  and ASA warping and improves layer bonding on tall parts.
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

## Still to decide

**Base (~£569) or Combo with AMS 2 Pro (~£769)?** See `setup.md` — the humidity
argument makes this less about multi-colour than it first appears.
