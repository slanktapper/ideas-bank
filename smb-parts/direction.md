# smb-parts

**Status:** idea

## What it is

Physical parts derived from the *Super Mario Bros.* (NES, 1985) level maps. The
source is Ian Albert's stitched full-level maps, all 50 files of which are now in
`maps/`: the 32 main levels from World 1-1 to World 8-4, 13 maps of the rooms off
them, and 5 whole-game wallpapers that are not level data. Measurements and the
source URL are in `maps-source.md`.

What gets *made* from them is not decided. This folder exists so the idea and its
source are recorded; the form is the next conversation.

## Why

Not yet stated. Rob opened the project with the map source and asked for setup only;
the motivation belongs here once it is given.

## Scope

**Undecided — a placeholder, not a commitment.** Nothing is ruled in or out yet.

Three candidate readings of "parts" were put to Rob on 2026-10-15 MDT. He chose none
of them and asked for the project to be set up instead, so all three are still live:

- **Level as wall panels** — a level sliced into print-bed-sized panels that key
  together into one long piece. The parts are the panels.
- **Element library** — the recognisable objects harvested from the maps (question
  block, brick, pipe, goomba, coin, flagpole, castle) as standalone parts: magnets,
  keychains, desk objects. The parts are the things *in* the levels.
- **Snap-together tile kit** — a baseplate plus per-tile pieces, assembled by hand
  into any level. The maps become build instructions and a tile bill-of-materials
  rather than fixed geometry.

## Stack

**None chosen.** Per `CLAUDE.md` the stack is picked inside the project rather than
assumed, and it cannot be picked sensibly before the form is. For reference, whatever
is chosen will likely need:

- an image reader, since the maps are GIFs with an indexed palette
- if parts are modelled: OpenSCAD, CadQuery or build123d, per `available-tools.md`
- if renders are wanted: `3d-tools/render.py` is the repo's shared renderer

`fetch-maps.sh` is bash and curl, and deliberately boring: it is plumbing for
getting the source images, not a vote on what the project is written in.

## How to run

Nothing to build yet. The one runnable thing is the map fetch:

```bash
cd smb-parts
./fetch-maps.sh --check    # verify and measure every GIF in maps/ (the default)
./fetch-maps.sh --fetch    # download the 32 main levels from ian-albert.com
```

`--check` is the one to run after dropping files into `maps/` by hand. It reads
whatever GIFs are actually there rather than assuming a filename list, so it copes
with the sub-area maps whose names are not known up front: it measures each one,
ticks off the 32 main levels, lists anything else it found, and rejects files that
are not really GIFs — a 404 page saved as `mario-3-2.gif` is caught, not counted.

`--fetch` only knows the 32 main levels and needs `ian-albert.com` to be reachable;
see `maps-source.md`. It is not the way to get the full set.

## Open questions

- **What is a "part"?** The three candidates under Scope. This is the one question
  that blocks everything else.
- **Scale.** Tile-to-millimetre is the decision that sizes everything, and it is now
  a question with real numbers behind it. The playfield is **14 tiles tall** (224 px),
  and levels run from 159.5 tiles (`4-3`) to 389.5 tiles (`8-1`). At 10 mm per tile
  that is a 140 mm tall strip between 1.6 m and 3.9 m long; at 5 mm, 70 mm tall and
  0.8–1.9 m. Either way the height fits the bed comfortably and the length is the
  thing to decide.
- **The 16 px grid does not divide the maps cleanly.** Only 6 of the 32 levels have a
  width that is a multiple of 16; 20 are half a tile over and 6 are 1 or 6 px over.
  Any slicing has to decide what happens to the leftover column rather than assume it
  away. See `maps-source.md`.
- **Material and colour.** From `filament.md` once the form is settled, not before.
  Worth knowing early: the SMB palette wants browns, reds, blues and greens, and the
  only green on the shelf is PLA Basic Mistletoe Green. Pipes are the obvious problem.
- **Does the cutter earn a place?** There are 30 sheets of 300 × 300 mm matte
  removable vinyl in red, black and orange. For flat level art that may beat printing
  it. Worth weighing when the form is chosen, not assumed away.
- **Distribution.** Printing Nintendo's assets for yourself is one thing; publishing
  model files is a separate question. Only matters if the project ever points outward.
