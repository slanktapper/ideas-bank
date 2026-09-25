"""Packing real objects into a drawer's grid.

Takes measured item sizes, works out the bin each needs, and places them on
the drawer's grid so the arrangement can be looked at before it is printed.

Deliberately simple: shelf-packing, largest first. A drawer has tens of
positions, not thousands, and a layout you can understand and override beats
an optimal one you cannot.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import DEFAULTS, GRID_PITCH_MM, Tuning
from .drawer import DrawerPlan
from .geometry import height_units_for


@dataclass
class Item:
    """A measured object that needs somewhere to live."""

    name: str
    width_mm: float
    depth_mm: float
    height_mm: float = 0.0
    qty: int = 1
    """How many bins to allocate -- see ``per_bin`` for objects that share one."""
    per_bin: int = 1
    """How many objects go in a single bin. Loose small items share; a 272mm
    lighter does not."""
    qty_max: int | None = None
    """The most you ever hold. Bins are sized for this, not for today's count,
    because a bulk purchase that does not fit means reprinting the bin."""
    qty_typical: int | None = None
    loose: bool = False
    """True for small items tipped into a bin rather than laid out in rows.
    Sized by volume with a packing factor, not by a neat array -- ten lighters
    in a grid needs a far bigger bin than ten lighters in a heap."""
    packing_factor: float = 0.55
    """Fraction of a bin's volume loose irregular objects actually occupy."""
    bin_height_u: int | None = None
    """Bin height for a loose item. Deeper bins need less floor."""
    measured: bool = True
    """False marks a placeholder, so a layout built on guesses says so."""
    note: str = ""

    @property
    def bins_needed(self) -> int:
        """Bins required to hold ``qty_max`` objects at ``per_bin`` each."""
        if self.loose:
            return 1
        total = self.qty_max if self.qty_max is not None else self.qty
        return max(1, math.ceil(total / max(1, self.per_bin)))

    def _arrangements(self) -> list[tuple[int, int]]:
        """Ways to lay ``per_bin`` objects out inside one bin."""
        n = max(1, self.per_bin)
        return [(a, math.ceil(n / a)) for a in range(1, n + 1)]

    def _loose_footprint(self, tuning: Tuning) -> tuple[int, int]:
        """Smallest bin whose interior swallows the heap and one whole object."""
        total = self.qty_max if self.qty_max is not None else self.qty
        volume = self.width_mm * self.depth_mm * max(self.height_mm, 1.0) * total
        needed = volume / max(0.05, self.packing_factor)
        usable_depth = max(7.0, (self.height_units() - 1) * 7.0)
        floor_needed = needed / usable_depth

        best = None
        for lu in range(1, 13):
            for wu in range(1, 13):
                iw = lu * GRID_PITCH_MM - 0.5 - 2 * tuning.wall_mm
                idp = wu * GRID_PITCH_MM - 0.5 - 2 * tuning.wall_mm
                fits_one = (
                    (iw >= self.width_mm and idp >= self.depth_mm)
                    or (iw >= self.depth_mm and idp >= self.width_mm)
                )
                if not fits_one or iw * idp < floor_needed:
                    continue
                key = (lu * wu, abs(lu - wu))
                if best is None or key < best[0]:
                    best = (key, (lu, wu))
        return best[1] if best else (1, 1)

    def footprint_units(self, tuning: Tuning = DEFAULTS) -> tuple[int, int]:
        """Smallest bin, in grid units, holding this item's allocation.

        The objects need clearance each, plus the bin's walls once, and the
        usable width across n units is n * 42 - 0.5 less both walls.
        """
        if self.loose:
            return self._loose_footprint(tuning)
        best = None
        for across, deep in self._arrangements():
            spans = (
                self.width_mm * across + 2 * tuning.clearance_mm * across,
                self.depth_mm * deep + 2 * tuning.clearance_mm * deep,
            )
            units = tuple(
                max(1, math.ceil(round((sp + 2 * tuning.wall_mm + 0.5)
                                       / GRID_PITCH_MM, 6)))
                for sp in spans
            )
            key = (units[0] * units[1], abs(units[0] - units[1]))
            if best is None or key < best[0]:
                best = (key, units)
        return best[1]

    def height_units(self) -> int:
        if self.bin_height_u:
            return self.bin_height_u
        return height_units_for(self.height_mm) if self.height_mm else 2

    def qty_label(self) -> str:
        if self.qty_max is not None and self.qty_typical is not None:
            return f"{self.qty_typical}-{self.qty_max}"
        return str(self.qty_max if self.qty_max is not None else self.qty)


@dataclass
class Placement:
    item: Item
    x_u: int
    y_u: int
    length_u: int
    width_u: int
    rotated: bool = False


@dataclass
class Layout:
    plan: DrawerPlan
    placements: list[Placement] = field(default_factory=list)
    unplaced: list[Item] = field(default_factory=list)

    @property
    def used_units(self) -> int:
        return sum(p.length_u * p.width_u for p in self.placements)

    @property
    def free_units(self) -> int:
        return self.plan.total_units - self.used_units

    @property
    def all_measured(self) -> bool:
        return all(p.item.measured for p in self.placements)


def load_items(path: str | Path) -> list[Item]:
    """Read an item list from YAML.

    Each entry: name, size [W, D, H] in mm, plus optional per_bin, qty,
    qty_max, qty_typical, note, and ``measured: false`` to mark a guess.
    """
    data = yaml.safe_load(Path(path).read_text()) or {}
    items = []
    for row in data.get("items", []):
        size = row.get("size") or []
        if len(size) < 2:
            raise ValueError(
                f"{row.get('name', '?')!r} needs a size of at least [width, depth] in mm"
            )
        items.append(
            Item(
                name=row["name"],
                width_mm=float(size[0]),
                depth_mm=float(size[1]),
                height_mm=float(size[2]) if len(size) > 2 else 0.0,
                qty=int(row.get("qty", 1)),
                per_bin=int(row.get("per_bin", 1)),
                qty_max=(int(row["qty_max"]) if row.get("qty_max") is not None else None),
                qty_typical=(int(row["qty_typical"])
                             if row.get("qty_typical") is not None else None),
                loose=bool(row.get("loose", False)),
                packing_factor=float(row.get("packing_factor", 0.55)),
                bin_height_u=(int(row["bin_height_u"])
                              if row.get("bin_height_u") is not None else None),
                measured=bool(row.get("measured", True)),
                note=str(row.get("note", "")),
            )
        )
    return items


def pack(
    plan: DrawerPlan, items: list[Item], tuning: Tuning = DEFAULTS,
    allow_rotation: bool = True,
) -> Layout:
    """Place items on the grid, largest first, first fit.

    Largest first because a big item that cannot find a home late in the
    process wastes far more space than a small one.
    """
    grid = [[False] * plan.units_x for _ in range(plan.units_y)]

    expanded: list[Item] = []
    for it in items:
        for _ in range(it.bins_needed):
            expanded.append(it)
    expanded.sort(
        key=lambda i: (i.footprint_units(tuning)[0] * i.footprint_units(tuning)[1],
                       max(i.footprint_units(tuning))),
        reverse=True,
    )

    def free_at(x, y, lu, wu) -> bool:
        if x + lu > plan.units_x or y + wu > plan.units_y:
            return False
        return all(not grid[y + j][x + i] for j in range(wu) for i in range(lu))

    def occupy(x, y, lu, wu):
        for j in range(wu):
            for i in range(lu):
                grid[y + j][x + i] = True

    layout = Layout(plan=plan)
    for it in expanded:
        lu, wu = it.footprint_units(tuning)
        options = [(lu, wu, False)]
        if allow_rotation and lu != wu:
            options.append((wu, lu, True))

        placed = False
        for y in range(plan.units_y):
            for x in range(plan.units_x):
                for olu, owu, rot in options:
                    if free_at(x, y, olu, owu):
                        occupy(x, y, olu, owu)
                        layout.placements.append(
                            Placement(it, x, y, olu, owu, rot)
                        )
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        if not placed:
            layout.unplaced.append(it)
    return layout
