# Arm-junction tests, second set — 2026-10-09

A 2×2 on the flare, with the inset fixed at 12. Each was built by reloading
`params.py` from disk first, so every case starts from the committed
baseline and only the three numbers below differ — nothing carries over from
the case before it.

| | `ARM_BLEND` | `ARM_BLEND_REACH` | `ARM_ROOT_INSET` | Volume | Sockets |
| --- | --- | --- | --- | --- | --- |
| `test-arm-a.stl` | 1 | 1 | 12 | 764.358 cm³ | 109 |
| `test-arm-b.stl` | 1 | 4 | 12 | 764.369 cm³ | 109 |
| `test-arm-c.stl` | 3 | 1 | 12 | 764.358 cm³ | 109 |
| `test-arm-d.stl` | 3 | 4 | 12 | 764.395 cm³ | 109 |

Millimetres as given, not design numbers times `SCALE`. All four 233.4 mm
tall, watertight on reload, seam relaxation off (`ARM_SEAM_SWEEPS = 0`).

## These four are, in practice, the same model

Look at the volumes. **a and c are identical to the milligram and have the
same vertex count**, despite one having three times the other's flare. The
spread across all four is 0.04 cm³ on an 800 cm³ part — boolean noise.

The reason, measured on arm 0:

| | |
| --- | --- |
| Arm spine leaves the trunk wall at | **arc 14.0 mm** |
| Flare still above 0.05 mm at reach 1 | arc 0 – 1.8 mm |
| Flare still above 0.05 mm at reach 4 | arc 0 – 7.1 mm |

At an inset of 12 the arm's first 14 mm are inside the trunk, and a flare
with a reach of 1–4 mm has died long before that. It is buried. Neither
`ARM_BLEND` nor `ARM_BLEND_REACH` can reach the visible surface at this
inset, so the 2×2 has nothing to vary.

How far in the arm starts, against where it emerges:

| `ARM_ROOT_INSET` | spine leaves the wall at |
| --- | --- |
| 0 | 1.8 mm |
| 2 | 3.6 mm |
| 4 | 5.3 mm |
| 6 | 7.1 mm |
| 8.75 | 10.6 mm |
| 12 | 14.0 mm |

For the flare to show at all, `ARM_BLEND_REACH` has to be comparable with
that emergence distance, or the inset has to come down to meet it.

## What this means for the junction

An inset of 12 **is** the pure intersection — the arm arrives at full
diameter with full-depth grooves and simply stops at the trunk. That is what
the first set's `d` (blend 0, reach 0, inset 12) was, and all four of these
are the same thing by another route.

So the flare is settled: at this inset it does nothing. What is left is the
hard line on the underside, which is the boolean intersection curve and was
never the flare's doing. That needs either a light seam relaxation — far
weaker than the 30 sweeps tried before, enough to take the tangent break off
without touching the grooves — or a smaller inset so the flare has somewhere
to act.

The first set is in git history at `63edba7` if those are wanted back.
