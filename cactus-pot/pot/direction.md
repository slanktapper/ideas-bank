# pot — the pot half of cactus-pot

**Status:** working

## What it is

The flower pot the cactus stands in: the *pebble pot*. A straight-sided
cylinder, Ø92 × 76 mm, with a rolled gold-coloured foot, a field of raised
stone-like cells above a scalloped dividing line, and a sunken cartouche on the
front carrying *Eleanor Shellstrop's File* in three lines.

It is built from code — a revolved profile, a relaxed Voronoi field unioned onto
it, and the lettering cut from real glyph outlines — so every number in it is a
constant at the top of `build.py` rather than a mesh someone pushed around.

The pot and the cactus are two halves of one object and they share this folder.
The cactus is the parent directory: `../direction.md`, `../build.py`,
`../params.py`. Neither half imports from the other; they meet at the mount,
which is written down below and in `../direction.md` under *The interface, as a
contract*.

## Why

Rob started from a downloaded pot with the name already on it. Two things were
wrong with it, in this order:

1. **The middle word was badly set** — baseline sagging 8.16 mm, wrapping 156.6°
   of the circumference against 94° and 52° for its neighbours. That was fixed
   in place; see `original-fix/`.
2. **The surface it sits on is not flat.** Fixing the word does not fix that, and
   a round pot this size cannot carry a flat panel at all — a 78 mm chord sinks
   21.6 mm, through the well. So the body was redrawn with the lettering on a
   patch of *bare cylinder of one radius*, where every line wraps the same amount
   and the longest line is 68 mm instead of 106.

The texture came second: Rob supplied a reference photo of a planter with a
silver crackle finish above a smooth gold base, split by a scalloped line. That
is what the stone field and the two-tone split are.

## Scope

**Does:**

- The pot body, in one piece: `stl/pebble-pot.stl`.
- The same pot split four ways by colour, for a four-filament print:
  `stl/colour/`. Gold body and grooves, silver stones, white cartouche, black
  letters.
- The same pot split at the scalloped line into two printable zones, so the base
  and the textured upper can go in different filaments with no multi-material
  on either part: `stl/pebble-pot-base.stl` and `stl/pebble-pot-upper.stl`.
- The mount the cactus needs — a blind Ø32.00 × 8.00 socket in the middle of the
  well floor, 21 mm below the rim.
- Renders, so the shape and the lettering are judged before filament is spent.

**Does not:**

- Model the cactus. That is the parent folder's job.
- Drain. The well is a blind 21 mm cavity sized for the cactus's spigot, not for
  soil. A planter version — deeper cavity, drain hole, no socket — is an open
  question, not a feature.
- Carry the original third-party mesh, or a derivative of it. See
  `original-fix/README.md`.

## Stack

Python 3.10+, `numpy` + `trimesh` with the `manifold3d` boolean engine, `shapely`
for the 2D work, `scipy` for the Voronoi field, `fontTools` for the glyph
outlines. Renders go through `../../3d-tools/render.py`. No GUI, no CAD
application.

The typeface ships with the project: Outfit Bold, SIL Open Font License, in
`font/`. `POT_FONT_DIR` overrides the directory if the name should be set in
something else.

    python3 -m pip install -r requirements.txt

## How to run

    python3 build.py                      # stl/pebble-pot.stl
    python3 split.py                      # the two printable zones
    python3 colours.py                    # stl/colour/, the four-filament split
    python3 shots.py                      # renders/
    python3 shots.py --colour             # the five-colour pot, every 120 deg
    python3 shots.py --photos             # renders/photos/, a full set to look at
    python3 shots.py --compare <old.stl>  # this pot beside the one we started from

The build is deterministic — the Voronoi field is seeded — so `build.py` on a
clean checkout reproduces `stl/pebble-pot.stl` byte for byte, and `split.py`
reproduces the other two.

Every dimension is a constant at the top of `build.py`. The ones that matter:

| | |
| --- | --- |
| `R`, `H` | 46.0, 76.0 — outer radius and height. The cactus is scaled to these. |
| `WELL_Z`, `SOCKET_D`, `SOCKET_H` | the mount: floor at 55.0, Ø32.0 × 8.0 blind socket. Changing any of these breaks the cactus. |
| `PAN_W`, `PAN_H`, `PAN_Z` | the cartouche, 78 × 37 mm, centred 48.5 up. |
| `BEAD_W` | the border round each stone: 1.89 mm, 1.8x the groove, so it fills every nominal gap solid. |
| `BAND_D` | the raised bottom: 0.575 mm proud, half the height of a stone. |
| `PAN_INSET`, `PAN_MARGIN` | 5.0 and 2.5 mm of clear panel around the text. The three lines are set at one size and the block is centred on its *inked* extent, so the top and bottom margins come out equal. |
| `CELL_H`, `GROOVE`, `N_CELLS` | the stone field: 1.15 proud, 1.05 gaps, 300 seeds. |

## Measured, not assumed

Off `stl/pebble-pot.stl` itself:

| | |
| --- | --- |
| Overall | **94.30 × 94.30 × 76.00 mm** |
| The body | Ø92.00 — the extra 2.30 is the stone cells standing 1.15 mm proud |
| Watertight | yes as built, 372 656 faces, 371 405 mm³ |
| Well floor | z = 55.00, so 21.00 below the rim |
| Socket | Ø32.00 × 8.00 deep, blind, on the axis |
| Inner wall | r = 42.80 straight, with a 4 mm fillet into the floor — 38.80 in the corner itself, open to 42.80 by z = 59 |
| Lettering | three lines, all at one cap height of 8.88 mm; widest line 68.0 mm, cut 1.0 mm deep into a panel sunk 0.5 mm |
| Text in the panel | z 32.50 to 64.50 in a panel of 30.00 to 67.00 — 2.50 mm clear above and below |

`../build.py --pot stl/pebble-pot.stl` is the cactus half reading those numbers
back and checking them against `../params.py`. It agrees: 27 of 27 fit checks
pass against this pot, with a worst gap of 14.9 mm between trunk and wall.

## The four colours

`colours.py` writes one watertight solid per filament instead of leaving the
colouring to the slicer, so the split lives in the geometry:

| File | Filament | What it is |
| --- | --- | --- |
| `01-gold-body.stl` | Silk gold PLA | The body, the foot, the inside, and the grooves between the stones |
| `02-silver-stones.stl` | Silk silver PLA | The 179 raised cells, as 179 separate closed bodies |
| `03-white-panel.stl` | Jade white PLA | The cartouche, 1.6 mm deep behind its face |
| `04-black-letters.stl` | Black PLA | The letters, filling the 1.0 mm engraving flush |
| `05-purple-borders.stl` | Silk+ purple PLA | A rounded border round every stone, and the raised bottom below the scalloped line |

Volumes: 333 422 + 21 926 + 3 903 + 540 + 12 154 mm³, which reconciles with the
371 945 mm³ of `build.body_unlettered()` to 0.1 mm³. The parts are disjoint by
construction: the wider borders bite about 18 mm³ off the stones' feet and
140 mm³ off their own overlaps, and those are cut away rather than left for two
filaments to argue over.

`stl/colour/` is not tracked: it is 55 MB, and `colours.py` regenerates it
exactly from the same seed. Load all four into the slicer at the
origin and assign a filament to each; they are disjoint, so nothing needs
painting by hand.

**This is a different object from `stl/pebble-pot.stl`.** There the name is a
void cut into the panel. Here it is filled, so the face is flush and the letters
read by colour rather than by shadow. The single-colour pot is unchanged.

### The borders

Every stone is outlined by a rounded bead that fills the groove around it. It
started at `GROOVE` wide, 1.050 mm, measured back off the built field as the
median and the minimum gap; each stone carried a quarter-round rising from
nothing at its foot to 0.525 mm at the middle of the groove, so two neighbours
met exactly and anything wider than nominal showed gold between them.

It is now 1.8x that, 1.89 mm. Each stone's quarter-round has a radius of
0.945 mm and reaches 0.925 mm out, which is most of the way across a nominal
groove, so neighbouring borders overlap instead of meeting: every nominal groove
is filled solid, the crown stands about 0.84 mm off the wall rather than
0.525 mm, and a wider-than-nominal gap gets a border 1.8x as wide instead of a
sliver of gold. The whole border network comes out as one connected solid of
5 442 mm³ -- it used to be 179 separate ones of 3 666 mm³ in total.

The stones still read as the raised thing: they stand 1.15 mm proud, so the
crown is about three quarters of their height.

Overlapping borders are unioned rather than concatenated, and the 18 mm³ where
the wider bead runs into a stone's foot is cut off the stone. Each quarter still
stops `BEAD_GAP` short of its own full extent, 0.02 mm, because two faces that
land exactly on each other make the pot stop being a volume on reload.

### The raised bottom

Everything below the scalloped line stands 0.575 mm proud of the wall -- half
the height of a stone -- in the same purple as the borders, so the line now
divides a raised purple base from the stone field above it rather than being
just a change of texture.

It is the pot's own profile grown 0.575 mm **along its normal**, not radially, so
the band stands the same height proud of the foot's roll as it does of the
straight wall; a radial offset would have thinned away to nothing where the foot
turns under. It is clipped at z = 0, so the pot still stands on the same 26 mm
flat and is still exactly 76.00 mm tall, and the overall 94.30 mm across is
unchanged because the band is well inside the stones' envelope. Volume
6 849 mm³.

Its skin bites `BAND_BITE` = 0.3 mm into the wall and runs `BAND_LAP` = 0.15 mm
up behind the stones' feet, for the same reason the beads stop short: a solid
that lands exactly on another leaves coincident faces, and the union stops being
a volume on reload. An overlap is safe where a touch is not.

The cutter that trims it to the scalloped line is built directly rather than
revolved, in `above_wave`: a ring at r = 18 and a ring at r = R + 8 both sit at
`wave(theta)`, so the surface between them -- the only part of it that cuts
anything -- is the wave itself.

It is swept, not stacked: `potlib.sweep_on_cylinder` runs the section along each
cell's outline and onto the wall in one pass, giving 179 watertight bodies with
no boolean. Stacking extruded level sets is not merely slower here, it does not
work at all -- the level sets of this shape are polygons with 179 holes, and they
do not extrude into closed solids.

Three of the five are watertight on reload. The gold body is closed as written
but has about 1 600 edges where it touches itself in the narrow grooves between
stones, which show up once a reader merges coincident vertices. Slicers handle
that; it is not a hole.

### What five colours costs

Worth knowing before the slicer is opened. Every colour on this pot spans most of
its height -- the stones run from z 13.6 to 74.6, the cartouche from 30 to 67,
the name from 32.5 to 64.5, and gold and purple are both everywhere now that the
bottom is raised in purple. So all but two layers carry several filaments:

| | |
| --- | --- |
| Layers at 0.2 mm | 380 |
| Layers carrying more than one colour | 378 |
| Filament changes | about 1 030 |
| Purge, at 0.35 to 0.9 g flushed a change | 360 to 930 g |
| The pot itself | 372 cm³, about 462 g |

So the waste is of the same order as the part, and could exceed it. That is not an
argument against doing it -- it is a print worth the filament if the look is
wanted -- but it should be a decision rather than a surprise. Flushing into infill
saves little here, because a pot this thin has almost none.

The two-tone split in `split.py` is the cheap end of the same idea: one change for
the whole print, because the colours are stacked rather than interleaved.

## Printing it

The two-zone split is the point of `split.py`: each half is a single colour, so
two filaments give the reference photo's look with no purging and no multi-colour
tool changes inside a part. Printed as one piece instead, `stl/pebble-pot.stl` is
fine — the split is about colour, not about overhangs.

The scalloped line is a horizontal join and will show as a seam. That is wanted
here; it is the dividing line in the reference.

## Open questions

- **A planter version.** Deeper cavity, a drain hole in the floor, no socket. It
  is a different mount, which is why it is not a flag on this build — the cactus
  would have nothing to sit in. Offered to Rob; not answered.
- **The stone field is a Voronoi diagram, not a crackle glaze.** It reads as
  pebbles rather than the fine crazing in the reference photo. Smaller cells with
  a narrower groove would get closer, at the cost of print time and of grooves
  too fine for a 0.4 mm nozzle to resolve. Not tried.
- **A square-sectioned variant was drawn and rejected.** It put the name on a
  genuinely flat face, but Rob chose the round body; the biggest lettering was
  worth more than the flat. Its code is not kept — the decision is written down
  here instead.
