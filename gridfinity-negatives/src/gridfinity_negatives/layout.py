"""Packing real objects into a drawer's grid.

Takes measured item sizes, works out the bin each needs, and places them on
the drawer's grid so the arrangement can be looked at before it is printed.

Deliberately simple: shelf-packing, largest first. A drawer has tens of
positions, not thousands, and a layout you can understand and override beats
an optimal one you cannot.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from .config import DEFAULTS, GRID_PITCH_MM, Tuning
from .drawer import DrawerPlan
from .geometry import height_units_for


def numbered(layout) -> list[tuple[int, "Placement"]]:
    """Assign each bin a number, front to back then left to right.

    A stable number is easier to say than a cell range -- "bin 7" rather than
    "the 2x2 at F3:G4" -- and the order matches how you scan an open drawer.
    """
    ordered = sorted(layout.placements, key=lambda p: (p.y_u, p.x_u))
    return list(enumerate(ordered, start=1))


def cell_ref(x_u: int, y_u: int) -> str:
    """Spreadsheet-style reference for a grid position: column letter, row number.

    Columns run A.. from the left, rows 1.. from the front of the drawer, so a
    position can be named out loud -- "make C4 taller" -- without measuring.
    """
    letters = ""
    n = x_u
    while True:
        letters = chr(ord("A") + n % 26) + letters
        n = n // 26 - 1
        if n < 0:
            break
    return f"{letters}{y_u + 1}"


def parse_cell(ref: str) -> tuple[int, int]:
    """Inverse of :func:`cell_ref`. 'C4' -> (2, 3)."""
    ref = ref.strip().upper()
    i = 0
    while i < len(ref) and ref[i].isalpha():
        i += 1
    if i == 0 or i == len(ref):
        raise ValueError(f"{ref!r} is not a cell reference, e.g. C4")
    col = 0
    for ch in ref[:i]:
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col - 1, int(ref[i:]) - 1


def cell_range(x_u: int, y_u: int, length_u: int, width_u: int) -> str:
    """'A1' for a single unit, 'A1:E4' for a block."""
    if length_u == 1 and width_u == 1:
        return cell_ref(x_u, y_u)
    return f"{cell_ref(x_u, y_u)}:{cell_ref(x_u + length_u - 1, y_u + width_u - 1)}"


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
    bins: int | None = None
    """Explicit number of bins, overriding the calculation. For items split
    across several bins by purpose rather than by capacity."""
    extend_left_mm: float = 0.0
    """Millimetres the bin reaches past the grid on its left, into the gap.

    A drawer's leftover is never a whole unit, so a bin that should meet the
    wall has to be an odd size. The grid stays the standard 42 mm pitch; only
    this one bin is non-standard, and only on the side facing the wall."""
    extend_front_mm: float = 0.0
    """The same, towards the front of the drawer."""
    at: str | None = None
    """Explicit position, as a cell reference like "A6". Placed there before
    anything is auto-packed, so a stated layout is honoured exactly."""
    bin_size: str | None = None
    """Explicit bin footprint, "LxW", overriding all sizing.

    Needed for sparse objects. The volume model reasons from a bounding box,
    which is a fair description of a lighter and a poor one of a keychain --
    a ring, a fob and some keys are mostly air, so their box overstates them
    several times over and asks for an absurd bin."""
    measured: bool = True
    """False marks a placeholder, so a layout built on guesses says so."""
    note: str = ""

    @property
    def bins_needed(self) -> int:
        """Bins required to hold ``qty_max`` objects at ``per_bin`` each."""
        if self.bins is not None:
            return max(1, self.bins)
        if self.at:
            # An explicit position names one bin. Without this, qty_max would
            # conjure extra copies that all contend for the same cell.
            return 1
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
        if self.bins:
            total = math.ceil(total / self.bins)   # per-bin share
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
        if self.bin_size:
            try:
                lu, wu = (int(v) for v in self.bin_size.lower().split("x"))
            except ValueError as e:
                raise ValueError(
                    f"{self.name!r}: bin_size must be LxW, e.g. 2x1 "
                    f"(got {self.bin_size!r})"
                ) from e
            return max(1, lu), max(1, wu)
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

    def capacity(self, tuning: Tuning = DEFAULTS) -> int:
        """How many of this object fit, packed square to the bin.

        A stated bin size says nothing about how much goes in it, and the
        answer is routinely lower than the quantity held -- worth computing.

        But this is a LOWER BOUND, not the capacity. It counts a plain
        rectangular packing: across the width, along the depth, stacked in
        the height. It cannot see a diagonal fit, and long thin objects in
        particular often go in at an angle when they will not go in square.
        Treat a shortfall as "check it", not as "it will not fit".
        """
        lu, wu = self.footprint_units(tuning)
        # A bin reaching into the drawer's gap is genuinely longer, and that
        # length holds things. Ignoring it reported the BBQ bin as holding
        # nothing when it had 285 mm inside for a 272 mm lighter.
        iw = (lu * GRID_PITCH_MM - 0.5 - 2 * tuning.wall_mm
              + self.extend_left_mm)
        idp = (wu * GRID_PITCH_MM - 0.5 - 2 * tuning.wall_mm
               + self.extend_front_mm)
        ih = max(0.0, (self.height_units() - 1) * 7.0)

        best = 0
        for a, b in ((self.width_mm, self.depth_mm), (self.depth_mm, self.width_mm)):
            if a <= 0 or b <= 0:
                continue
            n = int(iw // a) * int(idp // b)
            if self.height_mm > 0:
                n *= max(1, int(ih // self.height_mm))
            best = max(best, n)
        return best

    def wanted(self) -> int:
        return self.qty_max if self.qty_max is not None else self.qty

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

    @property
    def extend_left_mm(self) -> float:
        return self.item.extend_left_mm

    @property
    def extend_front_mm(self) -> float:
        return self.item.extend_front_mm

    def outer_size_mm(self, pitch: float = GRID_PITCH_MM) -> tuple[float, float]:
        """Printed size: grid footprint plus whatever reaches into the gap."""
        return (self.length_u * pitch - 0.5 + self.extend_left_mm,
                self.width_u * pitch - 0.5 + self.extend_front_mm)

    def label_size(self) -> str:
        """'6x2' or '6sq+38.5' when it reaches into the gap."""
        base = f"{self.length_u}x{self.width_u}"
        bits = []
        if self.extend_left_mm:
            bits.append(f"+{self.extend_left_mm:g}L")
        if self.extend_front_mm:
            bits.append(f"+{self.extend_front_mm:g}F")
        return base + ("".join(bits) if bits else "")


@dataclass
class Layout:
    plan: DrawerPlan
    _grid: list | None = field(default=None, repr=False, compare=False)
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


def load_defaults(path: str | Path) -> dict:
    """Drawer-wide settings from the item file's ``defaults:`` block.

    ``bin_height_u`` lives here rather than on the command line so the value
    is recorded with the drawer it belongs to, and changing it is one edit
    that reaches every bin.
    """
    data = yaml.safe_load(Path(path).read_text()) or {}
    return data.get("defaults", {}) or {}


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
                bins=(int(row["bins"]) if row.get("bins") is not None else None),
                bin_size=(str(row["bin_size"]) if row.get("bin_size") else None),
                at=(str(row["at"]) if row.get("at") else None),
                extend_left_mm=float(row.get("extend_left_mm", 0.0)),
                extend_front_mm=float(row.get("extend_front_mm", 0.0)),
                measured=bool(row.get("measured", True)),
                note=str(row.get("note", "")),
            )
        )
    return items


def pack(
    plan: DrawerPlan, items: list[Item], tuning: Tuning = DEFAULTS,
    allow_rotation: bool = True, height_u: int | None = None,
) -> Layout:
    """Place items on the grid: stated positions first, then largest-first.

    Anything carrying ``at`` goes exactly where it says. The rest is packed
    largest first, because a big item that cannot find a home late wastes far
    more space than a small one.
    """
    grid = [[False] * plan.units_x for _ in range(plan.units_y)]
    layout = Layout(plan=plan)

    def free_at(x, y, lu, wu) -> bool:
        if x < 0 or y < 0 or x + lu > plan.units_x or y + wu > plan.units_y:
            return False
        return all(not grid[y + j][x + i] for j in range(wu) for i in range(lu))

    def occupy(x, y, lu, wu):
        for j in range(wu):
            for i in range(lu):
                grid[y + j][x + i] = True

    expanded: list[Item] = []
    for it in items:
        if height_u:
            it = replace(it, bin_height_u=height_u)
        for _ in range(it.bins_needed):
            expanded.append(it)

    # Stated positions first, so an explicit layout is never displaced.
    rest = []
    for it in expanded:
        if not it.at:
            rest.append(it)
            continue
        lu, wu = it.footprint_units(tuning)
        x, y = parse_cell(it.at)
        if free_at(x, y, lu, wu):
            occupy(x, y, lu, wu)
            layout.placements.append(Placement(it, x, y, lu, wu))
        else:
            layout.unplaced.append(it)

    rest.sort(
        key=lambda i: (i.footprint_units(tuning)[0] * i.footprint_units(tuning)[1],
                       max(i.footprint_units(tuning))),
        reverse=True,
    )
    for it in rest:
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
                        layout.placements.append(Placement(it, x, y, olu, owu, rot))
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        if not placed:
            layout.unplaced.append(it)

    layout._grid = grid
    return layout


def fill_remaining(
    layout: Layout, sizes: list[str], name: str = "Spare",
    height_u: int = 8, tuning: Tuning = DEFAULTS,
) -> Layout:
    """Tile whatever grid is still empty with general-purpose bins.

    Sizes are tried largest first, so the biggest bin that fits a gap wins and
    the offcuts stay small.
    """
    grid = getattr(layout, "_grid", None)
    if grid is None:
        raise ValueError("fill_remaining needs a layout produced by pack()")
    plan = layout.plan

    parsed = []
    for spec in sizes:
        lu, wu = (int(v) for v in spec.lower().split("x"))
        parsed.append((lu, wu))
    parsed.sort(key=lambda t: t[0] * t[1], reverse=True)

    def free_at(x, y, lu, wu) -> bool:
        if x + lu > plan.units_x or y + wu > plan.units_y:
            return False
        return all(not grid[y + j][x + i] for j in range(wu) for i in range(lu))

    changed = True
    while changed:
        changed = False
        for lu, wu in parsed:
            for orient in ({(lu, wu), (wu, lu)} if lu != wu else {(lu, wu)}):
                olu, owu = orient
                for y in range(plan.units_y):
                    for x in range(plan.units_x):
                        if free_at(x, y, olu, owu):
                            for j in range(owu):
                                for i in range(olu):
                                    grid[y + j][x + i] = True
                            layout.placements.append(
                                Placement(
                                    Item(name, 0, 0, 0, bin_size=f"{olu}x{owu}",
                                         bin_height_u=height_u),
                                    x, y, olu, owu,
                                )
                            )
                            changed = True
    return layout
