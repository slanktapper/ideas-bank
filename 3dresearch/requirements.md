# Requirements

Settled 2026-08-29 MDT; location corrected 2026-08-30 MDT. These drive every
recommendation in `printer-shortlist.md`.
Revisit them before acting on any conclusion — if one of these changes, the answer
changes.

| Requirement | Decision | Consequence |
| --- | --- | --- |
| What gets printed | Functional parts; prototyping and general making | FDM, not resin. Strength and dimensional accuracy over surface finish. |
| Budget (printer only) | **$940–1,695 CAD** | **Met by the X2D option** ($1,349 bundle, $1,648.48 cart). **Broken by the H2D option** ($2,599 bundle, $2,733.12 cart) — $904 over the top of the range. |
| Location | Garage / workshop, **climate controlled, 10–20 °C year round** | Not a cold space. An enclosure is still wanted, but active chamber heating is an upgrade rather than a necessity. Noise and fumes are not constraints. |
| Tinkering appetite | Some tinkering fine | Calibration and maintenance acceptable; the machine should not itself be the project. |

## Region and currency

**All prices in this project are CAD.** The user is in Alberta, Canada.

The original budget was discussed in pounds and has been restated above in CAD. The
shortlist research in `printer-shortlist.md` was priced from UK retailers in GBP —
an unfounded assumption. Treat those figures as indicating the machines' relative
positions only, never as prices available here.

Canadian retailers (NEX3D, Spool3D in Calgary, Voxel Factory, Shop3D.ca, Digitmakers)
avoid cross-border duties; Spool3D offers local pickup in Alberta.

## Build volume — unstated, and now the deciding requirement

This brief never named a build volume, because every machine on the original shortlist
sat at roughly 256 mm cubed and the question never came up. The H2D option makes it
the deciding one: 350 mm against 256 mm is the only meaningful difference between the
two live options (`x2d-vs-h2d.md`).

**Unresolved:** what is the largest single part expected? Under 256 mm, the H2D
premium buys headroom. Over it, the X2D means splitting and gluing parts indefinitely.

If the H2D is chosen, this file needs a raised budget line and a stated build-volume
requirement in the same edit. Buying above the brief without amending the brief is how
the all-PLA cart happened.

## What these rule out

- **Resin (SLA/MSLA).** Detail-focused, brittle parts, plus IPA washing, curing, and
  fume handling. Wrong for functional parts.
- **Open-frame printers.** Still ruled out — an enclosure helps at 10–20 °C, and is
  needed for anything beyond PLA/PETG. But the case is now about draft exclusion and
  material range, not about surviving a freezing space.
- **Self-build kits as the default.** "Some tinkering" is not "the machine is the
  hobby". A kit stays viable only where it saves meaningful money.
