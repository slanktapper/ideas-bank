# 3d-tools

**Status:** working

## What it is

The one deliberately shared folder in this repository: project-agnostic
helpers for looking at a 3D part before it is printed. Right now that is
exactly one thing — `render.py`, a software rasteriser that turns a list of
meshes into a PNG with no GPU, no display and no system libraries.

It was written inside `cantstop`, where it earned its keep, and was extracted
here unchanged when a second project needed it.

## Why

Two reasons, and the second is the one that justifies breaking the
one-folder-per-idea rule.

The first is ordinary: `flattener` needs renders, `cantstop` already had a
renderer, and copying a few hundred lines to get it would mean two copies
drifting apart.

The second is that a renderer is not where a project's ideas live. Every
other folder here is an idea, and its code is a statement about that idea.
This is a tool: it knows nothing about dice, boards, finger traps or cams,
and it never should. Shared, it gets tested once — `test_render.py` —
instead of being eyeballed in each project's PNGs.

## Scope

**What it does.** Flat-shaded rasterising of `trimesh` meshes into a PIL
image, with a z-buffer, two lights, a specular term and a depth-discontinuity
edge pass. Cameras (`frame`, `orbit_eye`, `look_at`), projecting world points
to pixels so annotations can be anchored to real geometry (`screen_of`),
plane sections that hand back the cut faces separately so they can be tinted
(`section`, `tint`), and leader-line labels (`annotate`).

**What it deliberately does not do.**

- **Know anything about any project.** No parameters, no part names, no
  colours from a filament shelf. It takes `{"mesh": Trimesh, "color": rgb}`
  dicts and camera arguments. If a change here would need a project's
  vocabulary to explain, it belongs in that project.
- **Build geometry.** No primitives, no booleans, no CSG convenience. Each
  project models its own parts however it likes.
- **Slice, or talk to a printer.** No G-code, no 3MF, no bed layout.
- **Look pretty.** These renders exist to catch mistakes before filament is
  committed, not to sell anything. No shadows, no ambient occlusion, no
  anti-aliasing beyond supersampling.
- **Grow a plugin system.** It is one file. When a second genuinely shared
  tool appears it gets its own file beside this one, not a framework.

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
and `matplotlib` is optional — see `requirements.txt`, which says what each
one is for.

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
```

There is nothing to build. The checks are the only executable thing here;
everything else is imported by other projects.

## How a project uses it

This folder is a dependency of other folders, which is the thing `CLAUDE.md`
otherwise forbids. Keep the coupling to exactly this, at the top of whichever
module renders:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import render as R
```

The folder name is not a Python identifier, so it goes on `sys.path` rather
than being imported as a package. Two rules come with it:

- **The dependency runs one way only.** Projects import `3d-tools`.
  `3d-tools` imports nothing from any project, ever — that is what keeps it
  a tool rather than a coupling between two ideas.
- **A change here can break a project that is not in front of you.**
  `cantstop` commits its renders, so its full build is a regression test:
  run `python3 build.py` there and `git status` must come back clean. If a
  change is meant to alter output, say so in the commit and re-commit the
  PNGs deliberately.

## Open questions

- **Packaging.** The `sys.path` line is honest but crude. A
  `pip install -e 3d-tools` would be tidier and would need a real package
  name, since `3d-tools` is not importable. Not worth it for two consumers.
- **Near-plane clipping.** Worth adding the first time a camera genuinely
  needs to sit inside a part — a bore, say, which `flattener` has.
- **Vertex normals.** Would make curved surfaces readable at the cost of
  hiding facet count. If it is ever added it should be an argument that
  defaults to off, not a change of behaviour.
