# gridfinity-negatives

Turn a scan or photo of a tool into a Gridfinity bin with the tool's negative
cut into it.

```
scan / photo ──► trace outline ──► offset by clearance ──► + finger relief
                                                                  │
                    GridfinityBox(solid) ────── cut ──────────────┘
                      (cq-gridfinity)            │
                                                 ▼
                                      STL · STEP · preview PNG
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .

gfneg build examples/spanner-scan.png --depth 12 --relief --magnets --name spanner
```

```
Traced 145.5 x 25.9 mm from scan @ 400 dpi
Building 4x1x3U (167.5 x 41.5 x 24.8 mm), pocket 12.0 mm deep
wrote out/spanner.stl
wrote out/spanner.step
wrote out/spanner-preview.png
```

## The two capture paths

**Flatbed scan** — the accuracy benchmark. The scanner knows its own DPI and
looks straight down, so scale is exact and there is nothing to calibrate. Lay
the tool on the glass, close the lid, scan. If the file does not record its
resolution, pass `--dpi`; the tool refuses to guess.

**Phone photo** — for tools too big for the glass. Print the calibration mat
at **100% scale** (not "fit to page"), lay the tool inside the markers, and
photograph roughly overhead. Four ArUco fiducials at known positions give a
homography that removes perspective and fixes the scale.

```bash
gfneg mat --out calibration-mat.png     # A4, 144 x 231 mm usable
gfneg build photo.jpg --photo --depth 14
```

Measure the printed scale bar before first use. A mat printed at 97% makes
every tool 3% too small, and nothing downstream can detect that.

## What it refuses to do

Silent wrongness costs a print; an error costs nothing. So it errors on:

- a scan with no recorded DPI and no `--dpi` — scale would be a guess
- a photo missing any of the four markers — scale would be a guess
- a tool running past the mat's usable area — the trace would be clipped and
  confidently too small
- a blank or featureless image — otherwise the background traces as one
  enormous "tool"
- a bin wider than 6 units — past the X2D's 256 mm bed
- a pocket deeper than `(U-1) x 7` mm — it names the height that would work

## Options that matter

| Flag | Default | Notes |
| --- | --- | --- |
| `--depth` | 12 mm | How deep the pocket goes. Drives bin height. |
| `--clearance` | 0.4 mm | Gap around the tool. 0.25 snug, 0.6 for gloves. |
| `--relief` | off | Thumb notch, centred on the outline edge at the tool's waist. |
| `--magnets` | off | 6x2 mm holes, printable without supports. |
| `--size` | auto | Force units, e.g. `2x3`. Otherwise smallest that fits. |
| `--no-straighten` | off | Keep the trace's original rotation. |

## Tests

```bash
pytest -q      # 30 tests
```

The `test_model.py` contract tests pin down cq-gridfinity's coordinate system
and height convention. They exist because a silent change there would put
every pocket at the wrong depth with no other symptom.

## Licence note

Depends on `cq-gridfinity` (MIT) and CadQuery (Apache-2.0). Gridfinity itself
originates with Zack Freedman; see `../3dresearch/gridfinity.md` for the
licensing ambiguity, which matters only if you sell prints.
