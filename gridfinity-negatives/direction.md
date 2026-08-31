# gridfinity-negatives

**Status:** prototype

## What it is
A command-line tool that turns a picture of a hand tool into a Gridfinity bin
with that tool's shape cut into it. Scan a spanner on a flatbed, or photograph
it on a printed calibration mat, and it traces the outline, grows it by a
clearance, works out the smallest bin that holds it, cuts the pocket, and
writes STL and STEP.

It does not reimplement Gridfinity. The bin body — base profile, stacking lip,
magnet holes, label shelf — comes from `cq-gridfinity`. This project owns only
the half that library does not do: getting a tool's outline out of an image and
subtracting it from the bin.

## Why
Gridfinity solves *containers*. It does not solve *fitted* storage — the
tool-shaped pocket that makes a missing tool obvious at a glance. Doing that by
hand means a CAD session per tool, which nobody sustains past the third one.
Existing online services (ToolTrace, TracetoForge) do this, but they are hosted,
paid, and send photos of your workshop to someone else's server. This runs
locally, scripts, and batches.

See `../3dresearch/gridfinity.md` for the standard itself and why it was adopted.

## Scope
What this does:

- Trace a tool outline from a flatbed scan (scale from DPI) or a phone photo
  on an ArUco calibration mat (scale from fiducials + homography).
- Offset by a clearance, simplify, optionally add a finger-relief notch.
- Auto-size the bin in grid units and height units, or take a forced size.
- Cut the pocket and export STL (slicing) and STEP (later editing).
- Render a preview PNG before anything is printed.

What this deliberately does not do:

- **Not a Gridfinity implementation.** The body is `cq-gridfinity`'s. If bins
  do not seat in a baseplate, that is a slicer or tolerance issue, not this.
- **Not parametric pockets from primitives** — no "ten circles for sockets"
  spec file. Image-derived outlines only, for now. See open questions.
- Not a GUI, not a web service, not a slicer. It emits files.
- Not multi-tool layout. One tool per bin; arranging several is manual.

## Stack
Python 3.9–3.12, pip + venv.

- **CadQuery 2.8** (OCCT kernel) — solid modelling, STL/STEP export.
- **cq-gridfinity 0.5.7** — the Gridfinity body. MIT.
- **OpenCV (contrib, headless) 5.0** — thresholding, contours, ArUco.
- **shapely 2.1** — offsetting, simplification, the pocket profile.
- **matplotlib** — preview rendering.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
pytest                                   # 30 tests, ~15s

# Flatbed scan: scale comes from the file's DPI
gfneg trace scan.png --depth 12          # report only, no CAD
gfneg build scan.png --depth 12 --relief --magnets

# Phone photo: print the mat first, at 100% scale
gfneg mat --out calibration-mat.png
gfneg build photo.jpg --photo --depth 14 --relief
```

Outputs land in `out/`: `<name>.stl`, `<name>.step`, `<name>-preview.png`.

If a CadQuery wheel misbehaves on your machine, conda is the better-tested
path for the OCCT dependency chain: `conda install -c conda-forge cadquery`,
then `pip install -e .` for the rest.

## Print notes
PETG Basic, 3 walls, 0.2 mm layers, 10–15% infill — per `../3dresearch/materials.md`.
Bins print base-down, no supports; `--magnets` uses cq-gridfinity's unsupported
hole style so the slicer bridges them.

**Print one before committing to a set.** Check the tool drops in without
fighting, and that the base seats in a baseplate. PETG runs slightly looser
than PLA; adjust `--clearance` rather than scaling the model.

## Open questions
- **What clearance is actually right?** 0.4 mm is a considered guess, not a
  measured value. It needs a printed test ladder (0.2/0.3/0.4/0.5) in PETG on
  the X2D before the default can be trusted.
- **Parametric pockets** — sockets, driver bits and hex keys are circles on a
  pitch and need no camera at all. Deliberately left out of v1; likely the
  single highest-value addition.
- **Multi-tool bins.** One pocket per bin today. Packing several tools into one
  bin needs a layout step and a way to say which tools share a bin.
- **Through-holes.** `RETR_EXTERNAL` fills the ring of a spanner rather than
  leaving a locating pillar. Deliberate — pillars are fragile — but the
  opposite choice is defensible and should be a flag.
- **Second nozzle.** Body and pocket export as one solid. Separate bodies would
  let the X2D print a contrasting-colour pocket floor. Not attempted yet.
