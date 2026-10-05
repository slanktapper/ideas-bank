# reference

The source model this project started from, and anything else that is an
input rather than something built here.

| File | What it is |
| --- | --- |
| `pot.stl` | the flower pot, as downloaded. Not modelled here; measured. |
| `cactus-original.stl` | the cactus as downloaded, kept for comparison |

Both are third-party meshes Rob supplied. They are here to be measured and
compared against, not edited — the cactus in `stl/` is built from scratch by
`build.py`, and shares no geometry with the original.

`python3 build.py --pot reference/pot.stl` prints the pot's measured bore and
checks it against `params.POT_BORE_D`.
