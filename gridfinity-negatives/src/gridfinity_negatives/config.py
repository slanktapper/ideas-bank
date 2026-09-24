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
@dataclass(frozen=True)
class Printer:
    """A machine's usable single-nozzle print area.

    Kept as a table rather than a constant because this project was first
    written against an X2D that was never bought -- the H2D was. Hard-coding
    one machine's bed silently caps every part at the wrong size.
    """

    name: str
    bed_x_mm: float
    bed_y_mm: float

    @property
    def max_units_x(self) -> int:
        return int((self.bed_x_mm + 0.5) // GRID_PITCH_MM)

    @property
    def max_units_y(self) -> int:
        return int((self.bed_y_mm + 0.5) // GRID_PITCH_MM)

    def fits(self, length_u: int, width_u: int) -> bool:
        return length_u <= self.max_units_x and width_u <= self.max_units_y


PRINTERS = {
    # Single-nozzle usable area. The H2D's 350mm figure is total plate span,
    # not printable area, so it is deliberately not used here.
    "h2d": Printer("Bambu Lab H2D", 325.0, 320.0),
    "x2d": Printer("Bambu Lab X2D", 256.0, 256.0),
}

DEFAULT_PRINTER = PRINTERS["h2d"]
"""The machine actually in the workshop -- delivered week of 2026-09-21 MDT."""


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
