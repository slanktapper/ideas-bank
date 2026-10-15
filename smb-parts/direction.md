# smb-parts

**Status:** idea

## What it is

Physical parts derived from the *Super Mario Bros.* (NES, 1985) level maps. The
source is Ian Albert's stitched full-level maps — one image per level, covering all
32 levels from World 1-1 to World 8-4. See `maps-source.md` for the URLs.

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
./fetch-maps.sh            # fetch any missing maps into maps/, then report dimensions
./fetch-maps.sh --report   # dimensions of what is already on disk
```

It is idempotent — a map already present is left alone — and it rejects anything
that is not a real GIF, so a 404 page served as `mario-3-2.gif` is not quietly
stored. It needs `ian-albert.com` to be reachable; see `maps-source.md`.

## Open questions

- **What is a "part"?** The three candidates under Scope. This is the one question
  that blocks everything else.
- **How the maps reach the repo.** This session's network policy denies
  `ian-albert.com` (403 at the egress proxy; the host does not resolve for the fetch
  tool either), so no map has been downloaded or measured. Routes: allow the domain
  in the environment's network settings, or commit the files by hand.
- **Real map dimensions are unknown.** SMB tiles are 16 × 16 px and a level is 15
  tiles tall, but no figure here has been measured against an actual file — see the
  warning in `maps-source.md`.
- **Scale.** Tile-to-millimetre is the decision that sizes everything. A level is
  roughly 200 tiles long, so the choice is between a wall-length piece and something
  that fits a shelf.
- **Material and colour.** From `filament.md` once the form is settled, not before.
  Worth knowing early: the SMB palette wants browns, reds, blues and greens, and the
  only green on the shelf is PLA Basic Mistletoe Green. Pipes are the obvious problem.
- **Does the cutter earn a place?** There are 30 sheets of 300 × 300 mm matte
  removable vinyl in red, black and orange. For flat level art that may beat printing
  it. Worth weighing when the form is chosen, not assumed away.
- **Distribution.** Printing Nintendo's assets for yourself is one thing; publishing
  model files is a separate question. Only matters if the project ever points outward.
