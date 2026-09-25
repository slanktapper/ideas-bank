"""Bins that reach past the grid to meet a drawer wall.

A drawer's leftover is never a whole grid unit, so closing it means a few bins
that are not standard sizes. The grid keeps its 42 mm pitch throughout; only
the bins facing a wall are odd, and only on the side that faces it.

The construction is a skirt welded to the outside of a standard bin, with the
interior punched through so the cavity is continuous:

    ├── skirt ──┤├──────── standard bin ────────┤
    ┌───────────┬───────────────────────────────┐
    │           │                               │  ← wall punched through,
    │   .................................       │    so it is one cavity
    │   :                                :      │
    └───┴────────────────────────────────┴──────┘
        └ floor continues at the same height

The skirt sits on the drawer floor, not on the baseplate -- there is no
baseplate out there. That works because a Gridfinity baseplate is a frame and
a bin passes through it to the floor anyway, so both halves of the bin rest on
the same surface.
"""

from __future__ import annotations

import cadquery as cq
from cqgridfinity import GridfinityBox


class ExtensionError(ValueError):
    """The requested extension cannot be built."""


def _block(x, y, z, dx, dy, dz) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(dx, dy, dz, centered=False)
        .translate((x, y, z))
    )


def interior_of(body: cq.Workplane) -> tuple[float, float]:
    """Measure a bin's interior floor height and its wall inset.

    Measured rather than taken from ``wall_th``: the usable inset is 2.1 mm on
    a bin whose wall_th reads 1.0, because the outer profile is not a plain
    vertical wall. Building the skirt's cavity from the wrong number would
    leave a ridge where the two halves meet.
    """
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    bb = shape.BoundingBox()
    floors = [
        f for f in shape.Faces()
        if f.normalAt().z > 0.99 and f.Center().z < bb.zmax - 1e-6
    ]
    if not floors:
        raise ExtensionError(
            "No interior floor found. A solid or vase-mode bin cannot be "
            "extended this way."
        )
    floor = max(floors, key=lambda f: f.Area())
    fb = floor.BoundingBox()
    inset = min(fb.xmin - bb.xmin, fb.ymin - bb.ymin)
    return floor.Center().z, inset


def extended_bin(
    length_u: int,
    width_u: int,
    height_u: int,
    *,
    extend_left_mm: float = 0.0,
    extend_front_mm: float = 0.0,
    **box_kwargs,
) -> cq.Workplane:
    """A Gridfinity bin with a skirt reaching left and/or forward.

    ``extend_left_mm`` and ``extend_front_mm`` are the distances to the drawer
    walls, i.e. the gaps the grid leaves over. The bin's grid footprint and its
    base profile are untouched, so it still seats in a baseplate normally.
    """
    if extend_left_mm < 0 or extend_front_mm < 0:
        raise ExtensionError("Extensions cannot be negative.")
    if box_kwargs.get("solid"):
        raise ExtensionError("A solid bin has no cavity to extend.")

    box = GridfinityBox(length_u, width_u, height_u, **box_kwargs)
    body = box.cq_obj
    if not (extend_left_mm or extend_front_mm):
        return body

    bb = body.vals()[0].BoundingBox()
    floor_z, inset = interior_of(body)
    ztop = bb.zmax

    # --- outer skirts, full height, sitting on the drawer floor -----------
    if extend_left_mm:
        body = body.union(_block(
            bb.xmin - extend_left_mm, bb.ymin - extend_front_mm, 0.0,
            extend_left_mm, bb.ylen + extend_front_mm, ztop,
        ))
    if extend_front_mm:
        body = body.union(_block(
            bb.xmin, bb.ymin - extend_front_mm, 0.0,
            bb.xlen, extend_front_mm, ztop,
        ))

    # --- punch the cavity through, so it is one continuous interior -------
    # Each strip reaches `inset` past the original wall, removing it.
    y0 = bb.ymin - extend_front_mm + inset
    y1 = bb.ymax - inset
    x0 = bb.xmin - extend_left_mm + inset
    x1 = bb.xmax - inset
    depth = ztop - floor_z + 1.0

    if extend_left_mm:
        body = body.cut(_block(
            x0, y0, floor_z,
            (bb.xmin + inset) - x0, y1 - y0, depth,
        ))
    if extend_front_mm:
        body = body.cut(_block(
            x0, y0, floor_z,
            x1 - x0, (bb.ymin + inset) - y0, depth,
        ))
    return body


def describe(length_u, width_u, height_u,
             extend_left_mm=0.0, extend_front_mm=0.0) -> str:
    """'6x2+38.5L' -- the label used in the layout and on filenames."""
    s = f"{length_u}x{width_u}x{height_u}"
    if extend_left_mm:
        s += f"+{extend_left_mm:g}L"
    if extend_front_mm:
        s += f"+{extend_front_mm:g}F"
    return s
