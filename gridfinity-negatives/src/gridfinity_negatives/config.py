"""Constants and tunable defaults.

Gridfinity dimensions are from the published specification; see
``3dresearch/gridfinity.md`` in this repository for the sourcing. They are
fixed by the standard and must not be "tuned" -- if bins do not seat in a
baseplate, adjust horizontal expansion in the slicer, or ``Tuning.clearance``
here for the pocket, but never these.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- The standard. Do not edit. ------------------------------------------
GRID_PITCH_MM = 42.0
"""Centre-to-centre spacing of grid units."""

HEIGHT_UNIT_MM = 7.0
"""One 'U' of height. Note this includes the base profile."""

BIN_FOOTPRINT_MM = 41.5
"""Outer size of one bin unit: 42 less 0.5mm total clearance."""

BASE_PROFILE_MM = 4.75
"""Height of the 0.8 / 1.8 / 2.15 chamfer stack under every bin."""

# --- Printer envelope ----------------------------------------------------
X2D_BED_MM = 256.0
"""Bambu Lab X2D usable bed, single nozzle. 235mm on the second nozzle."""

MAX_UNITS_ON_BED = int(X2D_BED_MM // GRID_PITCH_MM)  # 6


@dataclass(frozen=True)
class Tuning:
    """Everything you might legitimately want to change.

    The defaults are deliberately conservative: a pocket that is slightly
    too loose is annoying, a pocket that is too tight is scrap.
    """

    clearance_mm: float = 0.4
    """Outward offset from the traced outline to the pocket wall.

    0.4mm suits PETG printed on a well-tuned machine and a tool you want to
    drop in without aiming. Drop to ~0.25 for a snug hold, raise to ~0.6 for
    gloved hands or a tool you grab in a hurry.
    """

    simplify_mm: float = 0.15
    """Douglas-Peucker tolerance on the traced outline.

    Traced contours carry one vertex per pixel, which makes the CAD boolean
    crawl and the STL enormous. 0.15mm is below what an FDM printer can
    resolve, so this costs nothing visible.
    """

    floor_mm: float = 1.6
    """Material left under the deepest pocket. 8 layers at 0.2mm."""

    wall_mm: float = 2.4
    """Minimum material between a pocket and the outside of the bin."""

    relief_radius_mm: float = 9.0
    """Radius of the finger-relief scallop. About a fingertip."""

    min_feature_mm2: float = 25.0
    """Traced blobs smaller than this are discarded as specks."""

    photo_px_per_mm: float = 8.0
    """Resolution the rectified photo is resampled to. ~200 DPI."""


DEFAULTS = Tuning()
