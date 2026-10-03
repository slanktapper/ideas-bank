# reference

Images the design is being held against. They are the brief for piece 6, the
active-player marker, and they are in the repository because three versions
of that piece were built and rejected against them from memory.

| File | What it is |
| --- | --- |
| `active-web-wanted.png` | **The target.** A drawing of piece 6 from the front: orange is the top face, and the whole shaft is an irregular wireframe web with no fill. |
| `active-web-printed-example.webp` | A real FDM print with the surface this is after — a figure whose skin is exposed lattice. Proof the thing prints, and the reason the ribs on piece 6 are one extrusion wide rather than two. |
| `active-section-sketch.png` | The original section: a foot that flares from the full width of a cell into a slim shaft, a long parallel shaft, a flat top. The silhouette is measured against this. |

## What was measured off them

`active-web-wanted.png` was measured rather than eyeballed, and the numbers
decided the design:

- **73% of the shaft is open**, 27% is line.
- The lines are **3% of the shaft's width** — 0.27 mm at a 9 mm shaft.

That second figure is below one extrusion, so it cannot be printed as drawn.
What it settles is the *ratio*: a net of line `w` and cell `d` is
`(d/(d+w))^2` open, so 73% at a 0.85 mm rib needs 5 mm cells, which is one
and a half of them across a 9 mm face. At 0.45 it needs 2.5 mm cells, which
is three and a half. **Two perimeters cannot make a web at this size.**

That is the whole reason piece 6 breaks the project's 0.85 mm floor, and
`direction.md` carries the argument in full.
