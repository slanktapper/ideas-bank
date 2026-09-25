"""Bins built at an arbitrary outer size, so they meet a drawer wall.

A drawer's leftover is never a whole grid unit, so closing it needs bins that
are not standard sizes.

**Not by welding a block onto a stock bin.** That was the first attempt and it
was wrong in three ways at once: a Gridfinity bin has 3.75 mm rounded corners,
so a square block butted against one leaves the original corner fillets
stranded in the middle of a wall, kinks the side where block meets curve, and
gives the finished part square outer corners where every other bin is rounded.

Instead the bin is **built at its true size from the start**. cq-gridfinity
derives the whole shell from ``outer_l``/``outer_w`` -- the outer sketch, the
inner sketch, the corner radii and the stacking lip all follow -- while the
base pads are placed independently at ``grid_centres``. Overriding the former
and leaving the latter alone gives a bin of any size whose base still seats in
a standard baseplate.

    ├─ extension ─┤├──── grid cells ────┤
    ╭─────────────────────────────────╮     one rounded rectangle,
    │                                 │     one continuous wall,
    │    ╭───────────────────────╮    │     one lip all the way round
    │    ╰───────────────────────╯    │
    ╰──────┬────────┬────────┬────────╯
       solid│      ╰─ chamfered base pads, 42 mm pitch
       to the floor   (the extension has no baseplate under it)
"""

from __future__ import annotations

import cadquery as cq
from cqgridfinity import GridfinityBox
from cqgridfinity.constants import GR_BASE_HEIGHT, GR_TOL, GRU, GRU2
from cqgridfinity.gf_box import rounded_rect_sketch


class ExtensionError(ValueError):
    """The requested extension cannot be built."""


class ExtendedBox(GridfinityBox):
    """A Gridfinity bin whose footprint is larger than its grid.

    ``extend_left_mm`` and ``extend_front_mm`` add to the outer size on the
    -X and -Y sides only, so the grid cells stay where a baseplate expects
    them and the extra material lands against the drawer wall.
    """

    def __init__(self, length_u, width_u, height_u, *,
                 extend_left_mm: float = 0.0, extend_front_mm: float = 0.0,
                 **kwargs):
        if extend_left_mm < 0 or extend_front_mm < 0:
            raise ExtensionError("Extensions cannot be negative.")
        self._ext_l = float(extend_left_mm)
        self._ext_f = float(extend_front_mm)
        super().__init__(length_u, width_u, height_u, **kwargs)

    # --- the size the part is actually built at --------------------------
    @property
    def outer_l(self) -> float:
        return self.length_u * GRU - GR_TOL + self._ext_l

    @property
    def outer_w(self) -> float:
        return self.width_u * GRU - GR_TOL + self._ext_f

    # Shifting the centre by half the extension puts all the extra material
    # on the left and front, leaving the right and back edges on the grid.
    @property
    def half_l(self) -> float:
        return (self.length_u - 1) * GRU2 - self._ext_l / 2

    @property
    def half_w(self) -> float:
        return (self.width_u - 1) * GRU2 - self._ext_f / 2

    # --- the one thing the base class cannot know about ------------------
    def _skirt_base(self) -> cq.Workplane:
        """Fill the extension's footprint down to the drawer floor.

        Base pads exist only under grid cells, so without this the extension
        would hang 4.75 mm above the drawer floor. The grid cells are left
        alone: their chamfered pads are what seat the bin in a baseplate.
        """
        sketch = rounded_rect_sketch(self.outer_l, self.outer_w, self.outer_rad)
        full = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(GR_BASE_HEIGHT + 1.0)
            .translate((*self.half_dim, -GR_BASE_HEIGHT))
        )
        grid = (
            cq.Workplane("XY")
            .box(self.length_u * GRU - GR_TOL, self.width_u * GRU - GR_TOL,
                 3 * (GR_BASE_HEIGHT + 2))
            .translate(((self.length_u - 1) * GRU2,
                        (self.width_u - 1) * GRU2, 0))
        )
        return full.cut(grid)

    def render_shell(self, as_solid=False):
        shell = super().render_shell(as_solid=True)
        if self._ext_l or self._ext_f:
            shell = shell.union(self._skirt_base())
        if not as_solid:
            return shell.cut(self.interior_solid)
        return shell


def extended_bin(
    length_u: int,
    width_u: int,
    height_u: int,
    *,
    extend_left_mm: float = 0.0,
    extend_front_mm: float = 0.0,
    **box_kwargs,
) -> cq.Workplane:
    """A Gridfinity bin of any outer size, correctly structured throughout."""
    if box_kwargs.get("solid") and (extend_left_mm or extend_front_mm):
        raise ExtensionError("A solid bin has no cavity to extend.")
    if not (extend_left_mm or extend_front_mm):
        return GridfinityBox(length_u, width_u, height_u, **box_kwargs).cq_obj
    return ExtendedBox(
        length_u, width_u, height_u,
        extend_left_mm=extend_left_mm, extend_front_mm=extend_front_mm,
        **box_kwargs,
    ).cq_obj


def describe(length_u, width_u, height_u,
             extend_left_mm=0.0, extend_front_mm=0.0) -> str:
    """'6x2x5+38.5L' -- the label used in the layout and on filenames."""
    s = f"{length_u}x{width_u}x{height_u}"
    if extend_left_mm:
        s += f"+{extend_left_mm:g}L"
    if extend_front_mm:
        s += f"+{extend_front_mm:g}F"
    return s
