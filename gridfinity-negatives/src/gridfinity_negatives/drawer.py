"""Planning a drawer: how many grid units fit, and how to print the baseplate.

This is the step that has to happen before any bin is worth printing. A 42mm
pitch almost never divides a drawer evenly, and a baseplate for anything but a
small drawer is wider than the bed, so it has to be tiled.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBaseplate, GridfinityDrawerSpacer

from .config import (
    BASE_PROFILE_MM, DEFAULT_PRINTER, GRID_PITCH_MM, HEIGHT_UNIT_MM, Printer,
)

LIP_RIM_MM = 3.8
"""How far the stacking lip stands proud of a bin's nominal U * 7 height."""

PETG_DENSITY_G_CM3 = 1.27
"""Bambu PETG Basic. PLA is 1.24, near enough the same for an estimate."""


@dataclass(frozen=True)
class Tile:
    """One printable piece of the baseplate."""

    length_u: int
    width_u: int
    origin_x_u: int
    origin_y_u: int

    @property
    def size_mm(self) -> tuple[float, float]:
        return (
            self.length_u * GRID_PITCH_MM - 0.5,
            self.width_u * GRID_PITCH_MM - 0.5,
        )


ALIGNMENTS = {
    "center": (0.5, 0.5),
    "front-left": (0.0, 0.0),
    "front-right": (1.0, 0.0),
    "back-left": (0.0, 1.0),
    "back-right": (1.0, 1.0),
    "top-right": (1.0, 1.0),   # alias: "top" of a plan view is the back
    "top-left": (0.0, 1.0),
}
"""Where the grid sits in the drawer, as a fraction of the leftover.

Corner alignment is the rule, not a preference. A centred grid has nothing
to register against: there is no way to position it accurately in a real
drawer, and it drifts the moment the drawer is opened. Pushed into a corner
it has two drawer walls as datums, it cannot move, and the slack collects
into two usable strips rather than four useless ones.

``center`` remains selectable for comparison, but nothing should be printed
against it."""

DEFAULT_ALIGN = "back-right"
"""Back wall and right wall. See ALIGNMENTS for why a corner, not the middle."""


@dataclass
class DrawerPlan:
    drawer_w_mm: float
    drawer_d_mm: float
    units_x: int
    units_y: int
    margin_x_mm: float
    margin_y_mm: float
    tiles: list[Tile]
    printer: Printer
    drawer_h_mm: float | None = None
    notes: list[str] = field(default_factory=list)
    align: str = DEFAULT_ALIGN

    @property
    def slack_x_mm(self) -> float:
        """Total unused width, however it is distributed."""
        return self.drawer_w_mm - self.units_x * GRID_PITCH_MM

    @property
    def slack_y_mm(self) -> float:
        return self.drawer_d_mm - self.units_y * GRID_PITCH_MM

    @property
    def gaps_mm(self) -> dict[str, float]:
        """The four gaps, named. A zero gap is an edge against a wall."""
        fx, fy = ALIGNMENTS[self.align]
        return {
            "left": self.slack_x_mm * fx,
            "right": self.slack_x_mm * (1 - fx),
            "front": self.slack_y_mm * fy,
            "back": self.slack_y_mm * (1 - fy),
        }

    @property
    def tile_counts(self) -> dict[tuple[int, int], int]:
        """Distinct tile sizes and how many of each to print."""
        counts: dict[tuple[int, int], int] = {}
        for t in self.tiles:
            key = (t.length_u, t.width_u)
            counts[key] = counts.get(key, 0) + 1
        return counts

    @property
    def total_units(self) -> int:
        return self.units_x * self.units_y


def split_span(total_u: int, max_u: int) -> list[int]:
    """Break a span of grid units into printable pieces, as evenly as possible.

    Evenly rather than greedily: a 10-unit span on a 7-unit bed becomes 5+5,
    not 7+3. Equal tiles print on the same plate, share one set of slicer
    settings, and leave no narrow offcut piece to warp.
    """
    if total_u <= max_u:
        return [total_u]
    n = math.ceil(total_u / max_u)
    base, extra = divmod(total_u, n)
    return [base + 1] * extra + [base] * (n - extra)


def plan(
    drawer_w_mm: float,
    drawer_d_mm: float,
    drawer_h_mm: float | None = None,
    printer: Printer = DEFAULT_PRINTER,
    align: str = DEFAULT_ALIGN,
) -> DrawerPlan:
    """Work out the grid, the margins and the baseplate tiling for a drawer.

    ``drawer_w_mm`` and ``drawer_d_mm`` are the *internal clear* dimensions at
    the base of the drawer, which are usually a few millimetres under the
    nominal size. Measure them; do not take them from a catalogue.
    """
    if drawer_w_mm <= 0 or drawer_d_mm <= 0:
        raise ValueError("Drawer dimensions must be positive.")

    units_x = int(drawer_w_mm // GRID_PITCH_MM)
    units_y = int(drawer_d_mm // GRID_PITCH_MM)
    if units_x < 1 or units_y < 1:
        raise ValueError(
            f"A {drawer_w_mm:.0f} x {drawer_d_mm:.0f} mm drawer does not fit a "
            f"single {GRID_PITCH_MM:.0f} mm grid unit. Gridfinity is the wrong "
            "system for a space this small."
        )

    if align not in ALIGNMENTS:
        raise ValueError(
            f"{align!r} is not an alignment. Choose from "
            f"{', '.join(sorted(ALIGNMENTS))}."
        )
    fx, fy = ALIGNMENTS[align]
    if align == "center":
        notes_center = True
    # margin_* is the grid's offset from the drawer's front-left corner.
    margin_x = (drawer_w_mm - units_x * GRID_PITCH_MM) * fx
    margin_y = (drawer_d_mm - units_y * GRID_PITCH_MM) * fy

    xs = split_span(units_x, printer.max_units_x)
    ys = split_span(units_y, printer.max_units_y)

    tiles: list[Tile] = []
    oy = 0
    for wy in ys:
        ox = 0
        for wx in xs:
            tiles.append(Tile(wx, wy, ox, oy))
            ox += wx
        oy += wy

    notes: list[str] = []
    if align == "center":
        notes.append(
            "Centred. There is nothing in a drawer to register a centred grid "
            "against, so it cannot be positioned accurately and will drift. "
            "Use a corner alignment."
        )
    # A margin can never exceed half a pitch -- the remainder is what floor
    # left behind. What is worth saying is when it is *close* to a full unit,
    # because then a small measuring error costs a whole row of bins.
    for axis, slack, units in (("width", drawer_w_mm - units_x * GRID_PITCH_MM,
                                units_x),
                               ("depth", drawer_d_mm - units_y * GRID_PITCH_MM,
                                units_y)):
        short_by = GRID_PITCH_MM - slack
        if short_by < 8.0:
            notes.append(
                f"The {axis} is only {short_by:.1f} mm short of fitting "
                f"{units + 1} units instead of {units}. Worth re-measuring at "
                "the base, and checking whether the drawer's own walls taper."
            )
    if drawer_h_mm is not None:
        # The baseplate is a frame, not a platform: a bin's base profile drops
        # through its socket to the drawer floor, so the baseplate adds nothing
        # to the stack. What does count is the 3.8mm lip rim standing proud of
        # the bin's nominal U * 7.
        tallest_u = int((drawer_h_mm - LIP_RIM_MM) // HEIGHT_UNIT_MM)
        if tallest_u < 1:
            notes.append(
                f"At {drawer_h_mm:.0f} mm there is not room for even a 1U bin "
                f"({HEIGHT_UNIT_MM + LIP_RIM_MM:.1f} mm tall). Check the height."
            )
        else:
            actual = tallest_u * HEIGHT_UNIT_MM + LIP_RIM_MM
            notes.append(
                f"{drawer_h_mm:.0f} mm of height takes a bin up to {tallest_u}U "
                f"({actual:.1f} mm tall including the lip), with "
                f"{drawer_h_mm - actual:.1f} mm to spare. Bins sit on the drawer "
                "floor -- the baseplate is a frame and adds no height."
            )
    return DrawerPlan(
        drawer_w_mm, drawer_d_mm, units_x, units_y,
        margin_x, margin_y, tiles, printer, drawer_h_mm, notes, align,
    )


def estimate_mass_g(solid: cq.Workplane, infill: float = 0.15,
                    density: float = PETG_DENSITY_G_CM3) -> float:
    """Rough printed mass of a solid model.

    A baseplate is mostly perimeter and top surface, so treating it as part
    solid and part infill is closer than assuming either extreme. This is an
    estimate for ordering filament, not a slicer.
    """
    volume_cm3 = solid.vals()[0].Volume() / 1000.0
    effective = 0.45 + 0.55 * infill
    return volume_cm3 * density * effective


def build_baseplates(
    plan_result: DrawerPlan,
    out_dir: str = "out",
    stem: str = "baseplate",
    magnets: bool = False,
) -> list[tuple[str, int, float]]:
    """Generate one STL per distinct tile size.

    Returns (path, quantity, estimated grams each).
    """
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    made = []
    for (lu, wu), qty in sorted(plan_result.tile_counts.items(), reverse=True):
        bp = GridfinityBaseplate(lu, wu, corner_screws=magnets)
        path = d / f"{stem}-{lu}x{wu}.stl"
        cq.exporters.export(bp.cq_obj, str(path))
        made.append((str(path), qty, estimate_mass_g(bp.cq_obj)))
    return made


def build_spacers(
    plan_result: DrawerPlan, out_dir: str = "out", stem: str = "spacer"
) -> str | None:
    """Generate the filler pieces that centre the grid in the drawer.

    Returns None when the margins are too small to be worth printing -- below
    about 4mm the pieces are more fragile than useful, and a strip of foam
    does the same job.
    """
    live = [g for g in plan_result.gaps_mm.values() if g > 0.01]
    if not live or min(live) < 4.0:
        return None
    sp = GridfinityDrawerSpacer(
        dr_width=plan_result.drawer_w_mm, dr_depth=plan_result.drawer_d_mm
    )
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{stem}-set.stl"
    cq.exporters.export(sp.render_full_set(), str(path))
    return str(path)
