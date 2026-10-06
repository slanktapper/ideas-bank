# cactus-pot

**Status:** prototype

## What it is

A printed cactus that drops into a printed flower pot, with its spines printed
as a separate part and press-fitted into sockets on the body. Both halves are
parametric code: the cactus here, the pot in `pot/` — see
[pot/direction.md](pot/direction.md). The cactus was rebuilt rather than edited
because the thing that was wrong with it — it read as a cartoon — is not
something you can edit out of a mesh.

## Why

The original cactus is a smooth capsule with cone spikes modelled into it. Two
separate problems:

- **It reads as a toy.** A real columnar cactus is ribbed from soil to crown,
  tapers, leans slightly, and carries its spines on raised pads along the rib
  crests. A smooth tube with spikes stuck on it is a cucumber with pins in it.
- **Spines printed as part of the body cannot be sharp.** Modelled onto a
  vertical part they are horizontal cantilevers: they need support, they print
  furry, and they come out blunt. Printed separately, standing point-up on
  their own pins, every layer is smaller than the one below and the taper comes
  out clean.

Splitting them also buys colour — spines in white or pale yellow against a
green body, with no multi-material printing on the big part at all.

## Scope

**Does:**

- The cactus body: ribbed trunk, two arms, areole pads, 110 spike sockets, and
  a spigot that drops into the socket in the pot's floor.
- The spike: one part, printed many times.
- A fit-test coupon that steps the socket diameter either side of nominal —
  with each step engraved beside its hole, so the answer can be read off the
  part instead of counted from an end — and a wedge of the real trunk that
  proves the joint on the curved ribbed wall it actually lives on.
- Renders, so the shape is judged before filament is spent.

**Does not:**

- Model the pot. The pot is an input, a mesh, and the only things read from it
  are the socket, the floor and the rim.
- Glue anything. The joint is an interference fit; if it ends up loose, the fix
  is a different socket diameter, not adhesive.
- Try to be botanically exact. It is a saguaro in silhouette, not a specimen.

## Stack

Python 3.10+, `numpy` + `trimesh` with the `manifold3d` boolean engine, the
same combination `cantstop` uses. Renders go through `../3d-tools/render.py`.
No GUI, no CAD application, no OpenSCAD.

    python3 -m pip install -r requirements.txt

## How to run

    python3 build.py                  # stl/ and renders/
    python3 build.py --stl            # just the printable files
    python3 build.py --renders        # just the pictures
    python3 build.py --pot <pot.stl>  # measure the pot, and render it seated
    python3 test_fit.py               # 26 checks; all have to pass
    python3 test_fit.py --pot <stl>   # 27, the last one against a real pot

Every dimension lives in `params.py`. The two that matter most:

| | |
| --- | --- |
| `PRESS_FIT` | the *printed* interference, −0.06 mm. Negative is a bite. |
| `AREOLE_MIN_SEP` | how close two pads may get: 14.5 mm on the trunk, 11.0 on an arm. It is what sets the spike count — 110 — because pads are drawn until the part will not take another. |

## The pot, measured

Measured off the real mesh with `build.py --pot`, not guessed:

| | |
| --- | --- |
| Pot | Ø92.2 × 76.0 mm |
| Cavity floor | 21.0 mm below the rim |
| Socket in that floor | **Ø32.00 × 8.00 deep** |
| Cavity wall, at the floor | r 40.6 |

So the cactus stands on the floor, 21 mm of it hidden inside the pot, with a
Ø31.30 spigot in the Ø32.00 socket and 13.7 mm of air to the pot's wall. Its
trunk is Ø52–55 and it is 175 mm tall, 147 of which is above the rim — the
assembly stands about 223 mm. `test_fit.py` checks all four of those numbers
against `params.py`, and `build.py --pot` fails loudly if the pot changes.

### The interface, as a contract

These numbers are what the cactus needs from whatever pot it ends up in rather
than facts about one mesh. **The pebble pot is the chosen one** — a round body
with a stone texture, picked over a square-sectioned variant that was drawn at
the same time. Both carried the same mount and the cactus fits either; the
square one is not what ships. The pebble pot keeps all four numbers, so the
cactus fits it unchanged:

    python3 build.py --pot <pebble-pot.stl>
    socket Ø32.00 x 8.00 deep, floor 21.00 below a rim at z=76.00,
    inner wall r=39.37 at its tightest -- params agree with this pot

That 39.37 is the narrowest the sampler finds over the heights it walks, not the
wall's true minimum. The wall is straight at r=42.80 and filleted into the
floor, so the real minimum is **38.80**, in the corner itself, opening to 42.80
by 4 mm up. It costs nothing here, because the cactus's base flare makes the
cactus narrowest exactly where the pot is tightest.
`test_fit.py --pot <stl>` measures both profiles over the 21 mm the cactus is
down inside the pot and reports the worst gap, which is **14.9 mm**, 20 mm up
— not down in the corner at all.


- **A blind socket in the middle of the inner floor**, concentric with the
  pot's axis. Blind matters: a drainage hole straight through the floor is a
  different mount and would need a different base on the cactus.
- **Deeper than the spigot**, so the cactus seats on the floor and not in the
  hole. Any diameter works; `POT_BORE_D` follows it and the spigot is sized
  from it with `SPIGOT_CLEAR` per side.
- **A cavity wall far enough out** that the trunk clears it — `POT_INNER_R`
  against `TRUNK_R_BASE + RIB_DEPTH`, checked in `test_fit.py`.
- **A known floor-to-rim height**, because `AREOLE_Z_MIN` has to stay above it
  or the pot's rim fouls the lowest spines going in.

The cactus is scaled to the pot rather than the other way round, so a pot that
changes size much from Ø92 × 76 should take the cactus's proportions with it.

## Open questions

- **Does −0.06 hold?** It is the right number on paper and the coupon exists
  because paper is not the same as PETG at 240 °C. Print the coupon, find the
  hole the spike seats in, and add that hole's engraved number to
  `SOCKET_COMP`. The ladder steps by `COUPON_STEP`, which is set equal to
  `PRESS_FIT` on purpose: one hole either side of the winner is a whole press
  fit away, so the answer is one hole rather than a region.

  The engraving is seven-segment characters built from boxes in `cactus.py`,
  not type. The pot half of this project sets real glyph outlines and that
  machinery is deliberately not reached for: the two halves do not import
  from each other, and what a gauge needs is a stroke a 0.4 nozzle can cut
  and a counter it can leave standing, which is a different problem from
  setting a name on a pot. The binding number is the counter inside an 8 —
  `COUPON_MARK_W` and `COUPON_MARK_H` are sized around it, and `test_fit.py`
  checks it, because a stroke too fat for its box engraves an 8 as a filled
  pit that still looks like a number.
- **The spines must not read as rows, and must not read as columns.** They did
  both, and the second one is why the trunk's layout no longer has ribs in it.

  The rows came from a fixed 2.1 mm step from one rib to the next: with evenly
  spaced pads the eye joined them into rings and a spiral. That was replaced by
  drawing each rib's starting height at random and rejecting it until no rib
  sat level with its neighbour and no four ribs marched in step. It fixed the
  rows and left the columns untouched, because a pad still belonged to a rib —
  so every rib carrying pads was a vertical line of them, and with pads on
  every other rib the trunk wore eight stripes. Letting a pad wander a few
  degrees off its own crest was built and measured and is not enough: ±3.8° is
  ±1.8 mm against the 11.3 mm gap to the next rib, so the line only wobbles.

  So a trunk pad does not belong to a rib any more. A crest and a height are
  drawn together, every rib in the draw, and the pad is kept only if it clears
  every pad already placed by `AREOLE_MIN_SEP` and does not make three evenly
  spaced pads up one crest. The draw runs until the trunk will not take
  another. Nothing decides in advance how many pads a rib gets, which is the
  thing that stops them being columns — the ribs now carry between 1 and 6
  each. Pads are still *on* crests, because that is where an areole grows and
  where a socket has a flat top to be bored into. Both arms are drawn the same
  way, with their own spacing — they had lines of their own down each crest,
  which is what Rob was looking at when he said the body and both sides had
  them.

  `test_fit.py` checks all of it on the finished sites rather than on the
  numbers that made them: the spacing, that all 15 ribs are used, that no three
  pads up a rib are evenly spaced, and that the wander keeps every pad on its
  crest.
- **110 spikes is an evening.** `AREOLE_MIN_SEP` and `ARM_AREOLE_MIN_SEP` are
  the dials now, and they are the honest ones: spacing is the thing with a
  physical meaning and the count follows from it. Raising the trunk's to 16 mm
  drops it to about 55 pads. If seating them turns out to be tedious rather
  than pleasant, that is where it gets backed off.
- **No spines on the arm undersides.** `SPIKE_FLOOR_DEG` drops any socket that
  would be a hole in a roof. A real saguaro has them; a printer does not enjoy
  them.
- **Arm undersides want support.** 4% of the part faces down at more than 45°,
  all of it under the two arms. PETG interface layers under a PLA body give
  breakaway supports from filament already on the shelf — see
  `../available-tools.md`.
