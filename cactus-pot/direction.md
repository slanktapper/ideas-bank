# cactus-pot

**Status:** prototype

## What it is

A printed cactus that drops into a printed flower pot, with its spines printed
as a separate part and press-fitted into sockets on the body. The pot came from
a downloaded model (`reference/`); the cactus is rebuilt here as parametric
code, because the thing that was wrong with it — it read as a cartoon — is not
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

- The cactus body: ribbed trunk, two arms, areole pads, 108 spike sockets, and
  a spigot that drops into the socket in the pot's floor.
- The spike: one part, printed many times.
- A fit-test coupon that steps the socket diameter either side of nominal, so
  the press fit gets measured instead of guessed.
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
    python3 test_fit.py               # 23 checks; all have to pass

Every dimension lives in `params.py`. The two that matter most:

| | |
| --- | --- |
| `PRESS_FIT` | the *printed* interference, −0.06 mm. Negative is a bite. |
| `SPIKE_RIB_STEP` | 1 puts a pad on every rib, 2 on every other. 2 is 108 spikes. |

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

A new pot is being designed, so these numbers are what the cactus needs from
whatever pot it ends up in rather than facts about one mesh:

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
  hole the spike seats in, set `SOCKET_COMP` from it.
- **108 spikes is an evening.** `SPIKE_RIB_STEP` and `AREOLE_PITCH` are the
  dials; doubling the pitch halves the count. If seating them turns out to be
  tedious rather than pleasant, that is where it gets backed off.
- **No spines on the arm undersides.** `SPIKE_FLOOR_DEG` drops any socket that
  would be a hole in a roof. A real saguaro has them; a printer does not enjoy
  them.
- **Arm undersides want support.** 4% of the part faces down at more than 45°,
  all of it under the two arms. PETG interface layers under a PLA body give
  breakaway supports from filament already on the shelf — see
  `../available-tools.md`.
