# Arm-junction tests, 2026-10-09

Four whole cactuses that differ only in how the arm meets the trunk. Built to
settle a complaint Rob made looking up at the model from below: the arm read
as a separate piece, and the arm's grooves *faded* as they approached the
trunk instead of simply intersecting it.

| | `ARM_BLEND` | `ARM_BLEND_REACH` | `ARM_ROOT_INSET` | Sockets |
| --- | --- | --- | --- | --- |
| `test-arm-a.stl` | 1 | 5 | 8.75 (unchanged) | 109 |
| `test-arm-b.stl` | 5 | 10 | 8.75 (unchanged) | 105 |
| `test-arm-c.stl` | 1 | 1 | 12 | 109 |
| `test-arm-d.stl` | 0 | 0 | 12 | 109 |

Millimetres as given, not design numbers times `SCALE`. All four are 233.4 mm
tall and reload watertight.

**The seam relaxation is off in all four** (`ARM_SEAM_SWEEPS = 0`). It smooths
a 43.75 mm ball around each arm root with 30 Laplacian sweeps, which would
have flattened most of the difference between these and gone on erasing the
grooves at the seam — the thing being judged. These show what the flare alone
does.

What they showed:

- **d** is the one that answers the complaint. No flare at all, so the arm
  arrives at full diameter with full-depth grooves and simply stops at the
  intersection. **c** is nearly the same.
- **b** still wears a sleeve: the root swells into an unribbed cone before
  the grooves begin. It also loses four spines — the fatter root swallows
  pad sites, which then drop out as buried.
- **The hard line on the underside survives in all four, d included.** The
  flare never caused it; the boolean intersection does. No value of these
  three numbers removes it.

These are a decision aid, not parts. Nothing builds them — they were made by
overriding the three parameters and re-running `cactus()`. Once the junction
is settled, the winning numbers go into `params.py` and this folder can go.
