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

from functools import lru_cache

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


def deepest_inset(body: cq.Workplane, floor_z: float, ztop: float,
                  samples: int = 10) -> tuple[float, float]:
    """How far the bin's walls reach inward at their narrowest point.

    The wall is not a straight vertical face. The stacking lip is a stepped
    profile occupying the top few millimetres, and it reaches further inward
    than the plain wall does -- 2.6 mm against 2.1 mm on a stock bin.

    Cutting the skirt's cavity to the plain inset therefore leaves a thin
    ledge of surviving lip running along the joint, which reads as a stray
    shelf in a slicer. So the cavity is cut to the narrowest point found over
    the bin's whole height, measured rather than assumed.
    """
    bb = body.vals()[0].BoundingBox()
    left = front = 0.0
    # The lip lives in the top few millimetres, so sample there densely and
    # the plain wall below it sparsely. Sectioning is the expensive part.
    lip_band = min(8.0, (ztop - floor_z) * 0.5)
    heights = [floor_z + (ztop - lip_band - floor_z) * (i + 0.5) / 3
               for i in range(3)]
    heights += [ztop - lip_band + lip_band * (i + 0.5) / (samples - 3)
                for i in range(samples - 3)]
    for z in heights:
        try:
            faces = body.section(z).faces().vals()
        except Exception:
            continue
        for f in faces:
            wires = sorted(f.Wires(),
                           key=lambda w: w.BoundingBox().DiagonalLength,
                           reverse=True)
            if len(wires) < 2:
                continue
            inner = wires[1].BoundingBox()
            left = max(left, inner.xmin - bb.xmin)
            front = max(front, inner.ymin - bb.ymin)
    return left, front


@lru_cache(maxsize=64)
def _bin_profile(length_u: int, width_u: int, height_u: int,
                 kw: tuple) -> tuple[float, float, float, float]:
    """Cache the measurements for a given bin size.

    Sampling twenty sections costs about a second, and a drawer's worth of
    bins repeats the same few sizes. Returns floor z, wall inset, and the
    deepest left/front inset.
    """
    body = GridfinityBox(length_u, width_u, height_u, **dict(kw)).cq_obj
    floor_z, inset = interior_of(body)
    ztop = body.vals()[0].BoundingBox().zmax
    left, front = deepest_inset(body, floor_z, ztop)
    return floor_z, inset, left, front


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
    ztop = bb.zmax
    # The lip reaches further in than the plain wall; cut to the narrowest
    # point or a ledge of surviving lip is left along the joint.
    floor_z, inset, lip_left, lip_front = _bin_profile(
        length_u, width_u, height_u, tuple(sorted(box_kwargs.items()))
    )
    cut_left = max(inset, lip_left)
    cut_front = max(inset, lip_front)

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
    y1 = bb.ymax - cut_front
    x0 = bb.xmin - extend_left_mm + inset
    x1 = bb.xmax - cut_left
    depth = ztop - floor_z + 1.0

    if extend_left_mm:
        body = body.cut(_block(
            x0, y0, floor_z,
            (bb.xmin + cut_left) - x0, y1 - y0, depth,
        ))
    if extend_front_mm:
        body = body.cut(_block(
            x0, y0, floor_z,
            x1 - x0, (bb.ymin + cut_front) - y0, depth,
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
