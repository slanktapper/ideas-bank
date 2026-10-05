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

- The cactus body: ribbed trunk, two arms, areole pads, 81 spike sockets, and a
  spigot that drops into the pot.
- The spike: one part, printed many times.
- A fit-test coupon that steps the socket diameter either side of nominal, so
  the press fit gets measured instead of guessed.
- Renders, so the shape is judged before filament is spent.

**Does not:**

- Model the pot. The pot is an input, a mesh in `reference/`, and the only
  things read from it are the bore diameter and the soil line.
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
    python3 build.py --pot reference/pot.stl   # measure the pot's bore
    python3 test_fit.py               # 23 checks; all have to pass

Every dimension lives in `params.py`. The two that matter most:

| | |
| --- | --- |
| `PRESS_FIT` | the *printed* interference, −0.06 mm. Negative is a bite. |
| `SPIKE_RIB_STEP` | 1 puts a pad on every rib, 2 on every other. 2 is 81 spikes. |

## Open questions

- **The pot's real bore.** `POT_BORE_D` is provisional. `build.py --pot`
  measures the mesh and says whether it agrees; until that has been run against
  the real file, the spigot is a guess.
- **Does −0.06 hold?** It is the right number on paper and the coupon exists
  because paper is not the same as PETG at 240 °C. Print the coupon, find the
  hole the spike seats in, set `SOCKET_COMP` from it.
- **81 spikes is an evening.** `SPIKE_RIB_STEP = 1` doubles it. If seating them
  turns out to be tedious rather than pleasant, the dial goes the other way.
- **Arm undersides want support.** 3% of the part faces down at more than 45°,
  all of it under the two arms. PETG interface layers under a PLA body give
  breakaway supports from filament already on the shelf — see
  `../available-tools.md`.
