# Arm-junction tests, third set — 2026-10-09

| | `ARM_BLEND` | `ARM_BLEND_REACH` | `ARM_ROOT_INSET` | Volume | Sockets |
| --- | --- | --- | --- | --- | --- |
| `test-arm-a.stl` | 1 | 6 | 12 | 764.427 cm³ | 109 |
| `test-arm-b.stl` | 1 | 12 | 12 | 764.940 cm³ | 108 |
| `test-arm-c.stl` | 3 | 6 | 12 | 764.626 cm³ | 108 |
| `test-arm-d.stl` | 3 | 12 | 12 | 766.214 cm³ | 106 |

Millimetres as given, not design numbers times `SCALE`. All four 233.4 mm
tall and watertight on reload. Seam relaxation off (`ARM_SEAM_SWEEPS = 0`).
Each built after reloading `params.py` from disk, so none inherits anything
from the case before it.

Unlike the second set, these four are genuinely different: the arm's surface
sits 16.5, 16.7, 18.5 and 18.6 mm from its spine, and the volumes spread by
1.8 cm³.

Earlier sets are in git history — first at `63edba7`, second at `04a4c97`.
