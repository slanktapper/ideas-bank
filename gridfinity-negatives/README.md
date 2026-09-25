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

## Start with the drawer

Nothing else can be sized until the drawer is measured. Use the **internal clear**
dimensions at the base, not the nominal size.

```bash
gfneg drawer --width 442 --depth 390 --height 95 --plan-only
```

```
Grid     : 10 x 9 units (419.5 x 377.5 mm), 90 bin positions
Margins  : 11.0 mm each side, 6.0 mm front and back (8% of the floor unused)
Baseplate: 4 tiles -- 2 x 5x5, 2 x 5x4
```

Drop `--plan-only` to write the baseplate STLs, the spacer set, and a layout PNG.

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
- a bin past the printer's bed — 7 × 7 units on the H2D, 6 × 6 on the X2D
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

## Grid alignment — always a corner, never the middle

**Every drawer's grid goes into the back-right corner.** This is a rule, not a
preference, and `back-right` is the default.

A centred grid has nothing to register against. There is no feature in a drawer
to measure a floating grid from, no way to place it accurately, and it drifts
the first time the drawer is opened hard. Pushed into a corner it has **two
drawer walls as datums**: it cannot be positioned wrongly and it cannot move.

It also changes what the leftover is good for. Centred, the slack splits into
four strips too narrow to use. In a corner it collects into **two strips** —
one down one side, one across the front — each twice as wide and each a
candidate for a spacer or a long thin item.

```
   centred: 4 useless strips        back-right: 2 usable strips
   ┌───────────────────┐            ┌───────────────────┐
   │ ░░░░░░░░░░░░░░░░░ │            │ ███████████████░░ │  ← flush, back wall
   │ ░ ███████████ ░░░ │            │ ███████████████░░ │
   │ ░ ███████████ ░░░ │            │ ███████████████░░ │
   │ ░░░░░░░░░░░░░░░░░ │            │ ░░░░░░░░░░░░░░░░░ │  ← all depth slack
   └───────────────────┘            └───────────────────┘
                                      ↑ all width slack   ↑ flush, right wall
```

`--align center` still exists for comparison, and says so in the notes, but
nothing should be printed against it.

## Gap gauges — standard for every drawer

A 42 mm pitch never divides a drawer evenly. What is left over decides whether
spacers fit, whether the grid slides, and sometimes whether another whole row
would fit. Measuring a 14 mm gap at the back of a loaded drawer with a tape is
guesswork, so **every drawer gets gauged before anything else is printed.**

A gauge is a small stick: a foot that butts flat against the baseplate's outer
edge, and an arm that reaches across the gap. **The longest one that still
drops in is the gap.**

```
    ┌────────────────────────┐  ← foot, butts against the baseplate edge
    │          ██            │     (26 mm wide, so it cannot skew)
    └──────────██────────────┘
               ██               ← arm: its length IS the measurement,
               ██                 read from the foot's contact face
               ▼ tip touches the drawer wall
```

Each is 26 × L × 3 mm, about 0.7 g. Three millimetres thick on purpose: the
baseplate edge is vertical for its full 4.75 mm, so a thinner gauge meets the
flat and cannot ride up a chamfer. The length is **engraved into the
underside**, mirrored to read when turned over, which is what makes them
reusable rather than disposable.

### The standard ladder: −3, −2, −1, 0, +1

Five sticks per gap, weighted **below** nominal.

| Offset | Why |
| --- | --- |
| −3, −2, −1 | A gauge shorter than the gap goes in and shows how much slack is left. Errors in a recorded drawer dimension tend to run generous, so the true gap is more often under nominal than over. |
| 0 | The nominal. |
| +1 | One step above is enough to confirm the upper bound. Anything longer than the gap simply will not go in, and tells you nothing beyond "smaller than this". |

A drawer needs **two ladders**, because the two dimensions leave different
remainders: one for the **width** gaps (left and right), one for the **depth**
gaps (front and back).

### The library — check before printing

A gauge is just a length. It does not care which drawer it came from, so a
14.5 mm stick serves every drawer that needs 14.5 mm. `gauge-library.yml`
lists the lengths that physically exist, and `gfneg gauge` consults it:

```bash
$ gfneg gauge --gap 14.5
Nominal gap : 14.5 mm
Ladder      : 11.5, 12.5, 13.5, 14.5, 15.5 mm   (standard -3 -2 -1 0 +1)
Already own : 12.5, 13.5, 14.5, 15.5 mm -- reuse these, do not print them again
                12.5 mm: KWL1N1T width ladder, 2026-09-25
To print    : 11.5 mm
```

Only the missing lengths are exported. After printing, record them so the next
drawer benefits:

```bash
gfneg gauge --gap 17 --register "KSL1W1T depth ladder"
```

`--all` forces the whole ladder out anyway; `--library` points at a different
file. A drawer whose ladder is entirely covered prints nothing and says so.

## Bins that meet a drawer wall

A drawer's leftover is never a whole grid unit, so closing it means bins that
are not standard sizes. `extended.py` welds a skirt to the outside of a normal
bin and punches the interior through, so the cavity is continuous:

```bash
gfneg bin --size 6x2 --height 5 --extend-left 38.5 --code KWL1N1T
gfneg bins --width 542.5 --depth 328.5 --items items-DRAWER.yml --code KWL1N1T
```

`bins` generates every bin in a layout at once, extensions and code stamps
included.

**The grid keeps its 42 mm pitch throughout.** Only the bins facing a wall are
odd, and only on that side — their grid base profile is untouched, so they
still seat in a baseplate normally. The skirt rests on the drawer floor, which
works because a baseplate is a frame and a bin passes through it to the floor
anyway; both halves of the bin sit on the same surface.

Three properties are tested, none of them visible from the bounding box:

1. **Outer size** is grid plus reach, and the part still sits on z = 0.
2. **The interior is one cavity, not two.** If the original wall survived, the
   skirt is dead space.
3. **The grid base pads survive**, so the bin still seats.

The wall inset is **measured from the bin, not taken from `wall_th`** — a bin
reporting `wall_th = 1.0` has a 2.1 mm usable inset, and building the skirt's
cavity from the wrong figure leaves a ridge at the joint.

## Printing a tiled baseplate

A baseplate for anything but a small drawer is wider than the bed, so it prints
as tiles. `gfneg drawer` splits the grid evenly and writes one STL per distinct
tile size.

**The tiles do not clip together.** cq-gridfinity baseplates have no interlock —
its `corner_tab_size` is for screw tabs, not for joining plates. Four things
hold a tiled grid in place, and the first is free:

1. **Bins straddling the seam.** Any bin wider than the tile boundary pins the
   two plates in plane once it is loaded. Worth checking where the seam falls:
   a seam no bin crosses is a seam that can open.
2. **Drawer walls plus spacers.** Filling the margins wedges the whole assembly
   so nothing can slide. `gfneg drawer` writes the spacer set.
3. **Screws into the drawer floor.** `GridfinityBaseplate(corner_screws=True)`
   adds countersunk corner tabs. The definitive fix, at the cost of holes.
4. **Double-sided tape under each tile.** No holes, very effective, and the
   usual answer for a drawer you may want to re-do later.

Gluing the tiles into one slab also works and is permanent. Third-party
click-lock designs (Clickfinity, CLICKbase) do interlock, but they replace
cq-gridfinity's baseplate rather than extending it.

**Print settings:** flat on the bed, 0.2 mm layers, 3 walls, 15–20% infill, no
supports. A large flat first layer is the one thing that can lift at the
corners — add a brim if it does.

## Tests

```bash
pytest -q      # 52 tests
```

The `test_model.py` contract tests pin down cq-gridfinity's coordinate system
and height convention. They exist because a silent change there would put
every pocket at the wrong depth with no other symptom.

## Licence note

Depends on `cq-gridfinity` (MIT) and CadQuery (Apache-2.0). Gridfinity itself
originates with Zack Freedman; see `../3dresearch/gridfinity.md` for the
licensing ambiguity, which matters only if you sell prints.
