# smb-parts

**Status:** prototype

## What it is

A Mario frieze that caps the retainer bar on the front of a floating shelf.
One rail is one shelf: two printed panels of 160.02 mm butting into 320.04 mm,
the exact length of the shelf, carrying pixel art lifted straight out of the
real *Super Mario Bros.* level maps — no redrawing, no invented pixels.

Three shelves is about three feet, which is where the original brief lands.

The maps are the source: all 50 files are in `maps/`, being the 32 main levels
from World 1-1 to World 8-4, 13 maps of the rooms off them, and 5 whole-game
wallpapers that are not level data. `maps-source.md` has the measurements.

## Why

Rob wanted something long and thin to stand in front of his shelves. The game's
own art is already pixel-perfect and already in the repo, so the frieze is a
crop of the real thing rather than an illustration of it.

## Scope

**What it does.** Takes a rectangular crop from the maps per shelf, cuts it
into two printed panels, builds each as a cap that grips the shelf's retainer
bar, and stands the art 1.2 mm proud of the front face. Exports both a
single-solid STL per panel and a per-colour split for multi-material. Renders
the lot so it can be checked before filament.

**What it deliberately does not do.**

- **Redraw anything.** A vignette is a crop: a map, a tile column, a band. If
  it is not in the GIF it is not on the rail.
- **Fit a whole level.** A shelf at a printable pixel is 26 tiles, and the
  shortest level is 159. This is one scene per shelf, not a level.
- **Carry the sky as geometry.** Background pixels are not raised; the cap
  shows through, so the sky is whatever colour the body is printed in.
- **Attach to furniture.** It pushes onto the retainer bar and lifts off. No
  screws, no adhesive, no modification to the shelf.
- **Span shelves.** One rail is one shelf. A continuous run across separate
  floating shelves is not a thing this builds.
- **Grow a tile library or a level editor.** Crops are specified by numbers in
  `vignettes.py`. Moving a vignette is editing one integer.

## The shelf, and what it forces

Rob's shelf is pressed sheet 4 mm thick, 12.6 in long and 3.95 in deep, with
the front edge turned **up** into a retainer bar; the front elevation is
0.79 in (20.07 mm), so the bar stands 16.07 mm above the floor.

**There is nothing to clip over.** An earlier version of this project assumed
a wooden board and built a U that gripped an 18 mm edge; that part has no
shelf to fit. The rail now caps the bar: a 4.4 mm slot drops over it, an inner
leg runs 12 mm down the back, and the face hangs outside, covering the whole
20 mm front elevation with 1.5 mm to spare. It costs 9.3 mm of shelf depth.

**And a rail cannot span shelves.** 320 mm is not three feet; three of these
are. Floating shelves are separate objects with gaps between them, so one rail
is one shelf and the length comes from printing several.

**The art is still a two-tile band.** The maps are 14 tiles tall, and 25 mm of
a whole playfield is 0.112 mm a game pixel — about a third of the nozzle. Two
tiles is what fits: the row things stand on, plus the ground under it. Bands
11–12 of the 14, because band 13 and most of 12 are ground mass while band 11
holds a goomba's body, a pipe's foot and the castle doorway.

What changed is that the tile size now falls out of the shelf instead of being
chosen. Twenty-six tiles span 320.04 mm, so a tile is 12.31 mm, a game pixel is
0.77 mm, and the art is **24.62 mm** tall — within half a millimetre of the
25 Rob asked for, and 26 halves cleanly into two 13-tile panels.

## Stack

Python, matching every other 3D project here: `trimesh` with `manifold3d` for
booleans, `shapely` to collapse pixel runs into polygons before extruding, and
`../3d-tools/render.py` for the renders. Pillow reads the GIFs.

- `params.py` — every dimension. Nothing else hard-codes a size.
- `vignettes.py` — which crop of which map goes on which shelf.
- `parts.py` — the channel and the art bodies.
- `build.py` — STLs into `stl/`, renders into `renders/`.
- `coupons.py` — the fit ladder and art sample, plus the 3 x 5 pixel font
  that labels them. Test gear, not product.
- `test_fit.py` — the assertions that have to hold before printing.

## How to run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_fit.py      # must pass
.venv/bin/python build.py --test  # the 8 g fit ladder -- print this first
.venv/bin/python build.py         # --stl / --renders / --fast
```

`print-guide.md` has orientation, settings and the filament reality.

## Open questions

- **One dimension on the drawing is read, not measured.** The 0.79 in is taken
  as underside-of-floor to top-of-bar, which makes the bar 16.07 mm proud. If
  it is instead the bar's rise above the floor, the face stops about 2.5 mm
  short of the shelf's underside — it still grips, but there is a visible gap.
  A caliper from floor-top to bar-top settles it, and so does any coupon from
  the fit ladder: push one on and see whether the face passes the underside.
- ~~**The slot clearance is a guess.**~~ **Settled 2026-10-23 MDT.** Rob
  printed the fit ladder and the 4.2 mm rung gripped, so `FIT` is 0.2 and
  the panels are built to a measured number rather than an assumed one.
  Open only in one respect: 4.2 was the tightest rung on the ladder, and a
  5 mm coupon is not a 160 mm panel. If the first real panel binds, 0.3.
- **How many shelves there are.** The rail is per shelf and four vignettes
  exist; Rob prints the ones he wants. Three is the three feet.
- **Two colours do not exist and four more are missing entirely.** The
  overworld shelves lose the light green of the bushes and an olive detail;
  the underground shelf has no teal, no pale cyan and no navy on the shelf at
  all. See the table in `print-guide.md`.
- **Only the coupons have been printed.** The slot is now a measured number;
  everything else — the grip over a full panel, whether the art reads at
  0.77 mm, the half-lap — is still mesh arithmetic.
- **Which scenes.** The current four are an arc through 1-1 with a dip into
  1-2. Forty-five other maps are sitting in `maps/` unused.
- **The cutter is untouched.** 30 sheets of 300 x 300 mm vinyl in red, black
  and orange are on hand, and a flat decal on a shelf front is exactly what a
  blade cutter is for. It was never weighed against printing this.
