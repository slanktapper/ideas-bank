# 3d-tools

**Status:** working

## What it is

The one deliberately shared folder in this repository: project-agnostic
helpers for the parts of printing a part that are the same whatever is being
printed. There are two, and each is one file:

- **`render.py`** — a software rasteriser that turns a list of meshes into a
  PNG with no GPU, no display and no system libraries.
- **`text3d.py`** — glyph outlines straight from a TTF as shapely polygons,
  so lettering on a part is exact at any size instead of traced off a raster.
  The typeface it defaults to lives in `font/`.

Both arrived the same way. `render.py` was written inside `cantstop`, where
it earned its keep, and was extracted here unchanged when `flattener` needed
it. `text3d.py` was written inside `cactus-pot` for the name on the pot, and
was extracted here when `filament-labels` needed the same lettering.

That is the only route into this folder: a second project wants something a
first project already has, and the thing turns out not to be about either
idea. Nothing is put here speculatively.

## Why

Two reasons, and the second is the one that justifies breaking the
one-folder-per-idea rule.

The first is ordinary: `flattener` needed renders and `cantstop` already had
a renderer; `filament-labels` needed lettering and `cactus-pot` already had
it. Copying a few hundred lines to get either would mean two copies drifting
apart.

The second is that neither a renderer nor a font loader is where a project's
ideas live. Every other folder here is an idea, and its code is a statement
about that idea. These are tools: they know nothing about dice, boards,
finger traps, cams, cactuses or filament bins, and they never should. Shared,
they get tested once — `test_render.py` and `test_text3d.py` — instead of
being eyeballed in each project's PNGs and prints.

The test files are the real reason the sharing is safe. The pot sets three
lines of mixed case at 9.6 mm on a curved panel; the labels set one word of
caps at 18 mm on a flat one. Without checks that pin the contract, a change
that suits one would quietly ruin the other, and the project that noticed
would not be the project that caused it.

## Scope

**What `render.py` does.** Flat-shaded rasterising of `trimesh` meshes into a
PIL image, with a z-buffer, two lights, a specular term and a
depth-discontinuity edge pass. Cameras (`frame`, `orbit_eye`, `look_at`),
projecting world points to pixels so annotations can be anchored to real
geometry (`screen_of`), plane sections that hand back the cut faces separately
so they can be tinted (`section`, `tint`), and leader-line labels
(`annotate`).

**What `text3d.py` does.** One line of text as a shapely geometry, with the
baseline at y=0 and the cap height given in millimetres (`Face.line`), and a
block of lines set to one common size and centred on its inked extent
(`fit_lines`). Beziers are flattened here rather than by a rasteriser, so the
polygons stay exact at any size, and counters come back as holes rather than
filled blobs. `Face(font_dir=...)` or `TEXT3D_FONT_DIR` points it at a
typeface other than the one in `font/`.

**What it deliberately does not do.**

- **Know anything about any project.** No parameters, no part names, no
  colours from a filament shelf. It takes `{"mesh": Trimesh, "color": rgb}`
  dicts and camera arguments. If a change here would need a project's
  vocabulary to explain, it belongs in that project.
- **Build 3D geometry.** No primitives, no booleans, no CSG convenience, no
  solids of any kind. Each project models its own parts however it likes.

  `text3d.py` is the near miss worth being precise about, because it looks
  like an exception and is not. It returns **2D** polygons — an outline of a
  typeface, which is what a typeface is. Extruding that outline, sinking it
  into a face, cutting a pocket for it, or picking a clearance for an inlay
  is the calling project's work, and belongs there: the depth of a letter is
  a decision about a part, and every project makes it differently. The pot
  bends its lettering onto a cylinder; the labels inlay theirs flush in a
  flat face. Neither of those belongs here.
- **Slice, or talk to a printer.** No G-code, no 3MF, no bed layout.
- **Look pretty.** These renders exist to catch mistakes before filament is
  committed, not to sell anything. No shadows, no ambient occlusion, no
  anti-aliasing beyond supersampling.
- **Grow a plugin system.** It is two files, and that is how it grows: a
  third genuinely shared tool gets its own file beside them, with its own
  test file, not a framework, not a package layout, not a registry. Nothing
  in here imports anything else in here.

It also has two known limits, left alone on purpose:

- **No near-plane clipping.** A triangle with any vertex behind the eye is
  culled whole. Put the camera outside the model and this never shows; put it
  inside and large triangles vanish silently.
- **Flat shading only.** There are no vertex normals, so a cylinder reads as
  facets. For a fit check that is a feature — you can count the facets the
  mesh actually has.

## Stack

Python 3.10+, `numpy` and `pillow` for the raster, `trimesh` for the meshes.
`scipy`, `shapely` and `mapbox_earcut` are pulled in by `section()` alone,
`fontTools` by `text3d.py` alone, and `matplotlib` is optional — see
`requirements.txt`, which says what each one is for.

`shapely` is wanted by both files, for unrelated reasons: capping a section
cut and doing polygon algebra on glyph rings. That is a coincidence, not a
shared layer.

No GUI, no OpenGL, no system packages. The containers these projects are
developed in have no display, and the usual headless renderers
(pyrender/OSMesa, pyglet under xvfb) are a stack of system libraries that
break whenever the base image moves. A numpy z-buffer has none of that and
is deterministic: the same geometry gives a byte-identical PNG on any
machine, which is what makes committing the PNGs worthwhile.

## How to run

```bash
cd 3d-tools
python3 -m pip install -r requirements.txt
python3 test_render.py      # 22 checks, about 3 seconds
python3 test_text3d.py      # 20 checks, about 2 seconds
```

There is nothing to build. The checks are the only executable thing here;
everything else is imported by other projects. One test file per tool, and
neither imports the other.

## How a project uses it

This folder is a dependency of other folders, which is the thing `CLAUDE.md`
otherwise forbids. Keep the coupling to exactly this, at the top of whichever
module renders:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import render as R
import text3d as T
```

Import only the tool that is actually used — `cantstop` and `flattener` want
`render`, `cactus-pot` and `filament-labels` want both. A project nested one
level deeper, as `cactus-pot/pot` is, needs one more `.parent`.

The folder name is not a Python identifier, so it goes on `sys.path` rather
than being imported as a package. Two rules come with it:

- **The dependency runs one way only.** Projects import `3d-tools`.
  `3d-tools` imports nothing from any project, ever — that is what keeps it
  a tool rather than a coupling between two ideas.
- **A change here can break a project that is not in front of you.** Two
  projects commit deterministic output, so their builds are the regression
  test for this folder:

  ```bash
  cd cantstop       && python3 build.py    # renders
  cd cactus-pot/pot && python3 build.py    # stl/pebble-pot.stl, and the lettering
  ```

  The pot one is what guards `text3d.py`: its STL is reproducible byte for
  byte, and the three lines of the name are cut into it, so a change in glyph
  flattening shows up as a changed file rather than as a surprise on the next
  print. If a change is meant to alter output, say so in the commit and
  re-commit the artefacts deliberately.

  **Trust the STLs, and check the PNGs against a second run rather than
  against the commit.** `git status` coming back clean was the original test
  and it no longer holds on a current container: as of 2026-10-14 MDT,
  `cactus-pot/pot/shots.py` redraws all four of its default renders with most
  pixels moved by a value of one, and `cantstop`'s matplotlib-drawn
  `08-bed-fit.png` redraws too, while every STL and every other `cantstop`
  render still matches. None of that is a change in geometry. It reproduces on
  an untouched checkout of the same commit, so it is the library versions
  underneath, not the code. Before blaming a change here for a changed PNG,
  build the same thing on a pristine worktree of HEAD and see whether it moves
  there as well.

## Open questions

- **Packaging.** The `sys.path` line is honest but crude. A
  `pip install -e 3d-tools` would be tidier and would need a real package
  name, since `3d-tools` is not importable. Still not obviously worth it,
  but the count that made it easy to dismiss has gone from two consumers to
  four.
- **Near-plane clipping.** Worth adding the first time a camera genuinely
  needs to sit inside a part — a bore, say, which `flattener` has.
- **Vertex normals.** Would make curved surfaces readable at the cost of
  hiding facet count. If it is ever added it should be an argument that
  defaults to off, not a change of behaviour.
- **The font in `font/`.** One typeface, Outfit Bold, now shared by two
  projects rather than shipped with one. That is the right call while they
  agree on the face; the first project that wants a different one passes
  `font_dir=` and keeps its own TTF, and this folder does not become a font
  library.
- **Kerning.** `Face` reads the legacy `kern` table and Outfit has none, so
  every pair is set on its advance width alone. Nothing printed so far has
  suffered for it at these sizes. Reading `GPOS` is the fix if a face ever
  does need it.
