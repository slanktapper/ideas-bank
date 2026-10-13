# wire-tags

**Status:** prototype — modelled and checked, nothing printed yet

## What it is

A printed tag that clips onto a cable and says what the cable is. The tag is a
flat plate with the name recessed into one face, and a C-clip at each end that
the cable snaps into. **The two clips face opposite ways**, so the cable
threads a shallow S through the tag: no single pull takes it off, and the tag
cannot rotate on the cable to hide its own label.

Everything is derived from one number. `plan(cable_d)` in `params.py` takes
the cable diameter and returns the bore, the mouth, the ride height, the plate
width and the plate length; `build.py --diameter 5.2 --label SCANNER` makes
that tag. There is no 4 mm tag with a bigger hole punched in it — a 7.5 mm tag
is a 7.5 mm tag all the way through.

## Why

Eight black cables behind a desk are eight identical black cables. Labels fall
off, printed shrink-wrap needs a heat gun, and a wrap of masking tape looks
like a wrap of masking tape. The thing that was wanted is a tag you can read
at arm's length, fit without unplugging anything, and take off again when the
cable is repurposed.

## Scope

**Does:**

- One tag, parametric on cable diameter and on the word written on it.
- A starter set of eight: `USB-C`, `USB-A`, `LIGHTNING`, `MICRO-B`, `HDMI`,
  `ETHERNET`, `LAPTOP`, `POWER`, each at a sensible diameter for that cable.
- Four documented size bands — 3.5, 4.5, 6.0 and 7.5 mm — covering thin charge
  leads through kettle leads.
- Two STLs per tag, body and lettering, in one coordinate system so the
  slicer puts them on top of each other with no manual positioning.
- A fit coupon: five clips stepping the asked-for diameter ±0.4 mm, each
  engraved with its step, because what a bore actually comes out at depends on
  the filament and nobody can calculate that.
- `test_fit.py`, 122 checks, including one that measures every downward-facing
  surface on the clip section and fails if anything would need support.

**Does not:**

- **Adjust.** Each tag is cut for one diameter. A tag that fits everything
  grips nothing, and the parametric build makes the right size cheap to get.
- **Wrap the cable completely.** It is a clip, not a sleeve. It will come off
  if you work at it, and that is the point — the alternative is cutting it off
  when the cable changes job.
- **Hold a paper or vinyl insert.** The word is in the part.
- **Carry more than a word.** 3.4 mm is the smallest lettering it will set,
  and at that size a sentence is unreadable anyway.
- **Mark which end is which.** Print two and put one at each end if that
  matters; nothing in the model knows about ends.

## How it works

Orientation is the print orientation, and every decision below came from it:
**X across the tag, Y along the cable, Z up off the bed.**

**The label face is the bed face.** Printed that way the lettering is a flat
first layer rather than a bridged ceiling, the 0.60 mm recess is the first
three layers so the filament change costs exactly one purge, and the clips
flex within their layers instead of trying to peel them apart.

**The clip outline is a D, not a circle.** Vertical flanks run from the plate
up to the cable centre and the dome sits on top of them. A circular clip
standing on the bed starts as a sliver and flares outward faster than FDM will
bridge; the flat flanks are what make it printable without support.

**The bore is an arch, not a hole.** It is a horizontal hole, so its roof is
carried on 45 degree flanks with a short flat left to bridge at the very top.

**The mouth is aimed 46 degrees above horizontal**, and that number is pinned
from both sides. Below 45 the underside of the upper lip overhangs more than
45 degrees and wants support. Much above 60 the mouth is pointing at the sky
and the tag lifts off. At 46 the lower lip reaches just past the cable's
widest point, so the cable is captured on roughly 270 degrees of its
circumference and has to be pushed down and sideways to get out.

**The snap is sized against the arm, not the eye.** The cable spreads the lips
by `cable - mouth`; `MOUTH_K` is set so that is about 12-15% of the cable
diameter. An earlier 0.74 asked for 21% and would have crazed a 1.6 mm PETG
arm on the second fit.

**Two grip ribs** stand 0.25 mm proud of the bore, opposite the mouth. They are
what stops the tag creeping along a cable it fits loosely; without them the
only thing holding station is friction on a 0.3 mm clearance.

**The cable nests 0.8 mm into the plate.** A ring that merely touches the plate
is joined to it along a tangent line, which is the weakest joint available.

## Stack

Python 3.10+, parametric CAD as code — the same toolchain as `cantstop`,
`cactus-pot` and `flattener`:

- `trimesh` + `manifold3d` for solids and booleans
- `shapely` for the 2D sections that get extruded, which is most of the part
- `matplotlib` for glyph outlines. The lettering module, `glyphs.py`, was
  written here rather than copied from `cactus-pot/pot/text3d.py`, so the two
  projects share no code and no font file. DejaVu Sans Bold ships inside
  matplotlib, so there is nothing to keep in version control.
- `../3d-tools/render.py` for the renders — the only thing this folder takes
  from outside itself.

## How to run

```bash
python3 -m pip install -r requirements.txt

python3 test_fit.py                              # 122 design checks
python3 build.py                                 # starter set + coupon + renders
python3 build.py --label SCANNER --diameter 5.2  # any other tag
python3 build.py --renders --fast                # half-res renders only
```

STLs land in `stl/`, renders in `renders/`. Both are regenerated from scratch
and safe to delete. `print-guide.md` says what to do with them.

## Open questions

- **`FIT` is a guess.** 0.30 mm on the bore is a starting value, not a
  measurement. The coupon exists to replace it and has not been printed yet.
- **Does the snap survive repeated fitting?** PETG should take 12-15% spread
  indefinitely; nothing has been cycled to find out.
- **Ribs or no ribs.** They may make a correctly sized tag a fight to fit. The
  coupon will say; `RIB = 0` turns them off.
- **Does the word want to run across the tag rather than along it?** Along is
  right for a cable you read at a distance, but a short word across a wider
  plate would read without turning your head.
- **Nothing says which end of the cable you are holding.** A left/right pair,
  or an arrow, would — but that is a second idea, not a change to this one.
