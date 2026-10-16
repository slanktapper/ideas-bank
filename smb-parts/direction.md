# smb-parts

**Status:** prototype

## What it is

A Mario frieze that clips onto the front edge of a shelf. Four printed panels
of 225 mm butt together into a 900 mm (2.95 ft) rail, 25 mm tall, carrying
pixel art lifted straight out of the real *Super Mario Bros.* level maps — no
redrawing, no invented pixels.

The maps are the source: all 50 files are in `maps/`, being the 32 main levels
from World 1-1 to World 8-4, 13 maps of the rooms off them, and 5 whole-game
wallpapers that are not level data. `maps-source.md` has the measurements.

## Why

Rob wanted something long and thin to stand in front of his shelves. The game's
own art is already pixel-perfect and already in the repo, so the frieze is a
crop of the real thing rather than an illustration of it.

## Scope

**What it does.** Takes four rectangular crops from the maps, builds each as a
U-channel that hooks over a shelf board, and stands the art 1.2 mm proud of the
front face. Exports both a single-solid STL per panel and a per-colour split
for multi-material. Renders the lot so it can be checked before filament.

**What it deliberately does not do.**

- **Redraw anything.** A vignette is a crop: a map, a tile column, a band. If
  it is not in the GIF it is not on the rail.
- **Fit a whole level.** Three feet at a printable pixel is about 72 tiles, and
  the shortest level is 159. This is scenes, not a level.
- **Carry the sky as geometry.** Background pixels are not raised; the channel
  shows through, so the sky is whatever colour the body is printed in.
- **Attach to furniture.** It clips on and lifts off. No screws, no adhesive.
- **Grow a tile library or a level editor.** Crops are specified by numbers in
  `vignettes.py`. Moving a vignette is editing one integer.

## The 25 mm, and what it forces

Rob asked for 25 mm tall. The maps are 14 tiles tall, so 25 mm of a whole
playfield is 1.79 mm a tile and 0.112 mm a game pixel — about a third of the
nozzle, and not printable. The art is therefore a **two-tile band**: the row
things stand on, plus the ground under it. That gives 12.5 mm a tile and
0.78 mm a pixel, just under two bead widths.

Bands 11–12 of the 14 are the window. Band 13 and most of 12 are ground mass;
band 11 is where a goomba's body, a pipe's foot and the castle doorway are. A
window at 12–13 would be two rows of identical ground blocks.

## Stack

Python, matching every other 3D project here: `trimesh` with `manifold3d` for
booleans, `shapely` to collapse pixel runs into polygons before extruding, and
`../3d-tools/render.py` for the renders. Pillow reads the GIFs.

- `params.py` — every dimension. Nothing else hard-codes a size.
- `vignettes.py` — which crop of which map goes on which panel.
- `parts.py` — the channel and the art bodies.
- `build.py` — STLs into `stl/`, renders into `renders/`.
- `test_fit.py` — the assertions that have to hold before printing.

## How to run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_fit.py      # must pass
.venv/bin/python build.py         # --stl / --renders / --fast
```

`print-guide.md` has orientation, settings and the filament reality.

## Open questions

- **`SHELF_T` is a guess.** 18 mm, never measured. It is the one number in the
  project with nothing behind it, and the whole clip depends on it. A board
  over about 20 mm needs `FACE_H` raised past 25 mm; `test_fit.py` says so.
- **Two colours do not exist and four more are missing entirely.** The
  overworld panels lose the light green of the bushes and an olive detail; the
  underground panel has no teal, no pale cyan and no navy on the shelf at all.
  See the table in `print-guide.md`. Either print that panel in one colour or
  order filament.
- **Nothing has been printed.** Every number here is from the mesh, not from a
  part in hand. The slot fit in particular is a calculation, not a test print.
- **Which four scenes.** The current set is an arc through 1-1 with a dip into
  1-2. Forty-five other maps are sitting in `maps/` unused.
- **The cutter is untouched.** 30 sheets of 300 × 300 mm vinyl in red, black
  and orange are on hand. Flat Mario art on a shelf edge is exactly what a
  blade cutter is for, and it was not weighed against printing this.
