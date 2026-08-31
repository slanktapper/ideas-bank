"""Cutting the pocket into a Gridfinity body.

The body comes from ``cq-gridfinity``, which owns the base profile, the
stacking lip and the magnet holes. This module owns only the subtraction.

Geometry contract with cq-gridfinity 0.5.7, established by measurement rather
than assumption (see ``tests/test_model.py``, which fails if it ever changes):

* the solid is centred on the origin in X and Y, and sits on z = 0;
* ``box.top_ref_height`` (== U * 7) is the main top surface;
* a rim stands 3.8mm proud of that, so the bounding box top is U * 7 + 3.8;
* ``box.max_height`` (== (U - 1) * 7) is how deep a pocket may safely go,
  the bottom unit being reserved for the base profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq
from cqgridfinity import GridfinityBox
from shapely.geometry import Polygon

from .config import DEFAULTS, MAX_UNITS_ON_BED, Tuning
from .geometry import centre_on, grid_units_for, height_units_for


class BedTooSmall(ValueError):
    """The requested bin does not fit on the printer."""


class PocketTooDeep(ValueError):
    """The requested depth would cut into the base profile."""


@dataclass
class BinSpec:
    """Everything needed to build one bin."""

    length_u: int
    width_u: int
    height_u: int
    depth_mm: float
    magnet_holes: bool = False
    keep_lip: bool = True
    label_shelf: bool = False

    def describe(self) -> str:
        return (
            f"{self.length_u}x{self.width_u}x{self.height_u}U "
            f"({self.length_u * 42 - 0.5:.1f} x {self.width_u * 42 - 0.5:.1f} x "
            f"{self.height_u * 7 + 3.8:.1f} mm), pocket {self.depth_mm:.1f} mm deep"
        )


@dataclass
class Build:
    body: cq.Workplane
    spec: BinSpec
    pocket: Polygon
    warnings: list[str] = field(default_factory=list)


def auto_spec(
    pocket: Polygon,
    depth_mm: float,
    tuning: Tuning = DEFAULTS,
    **kwargs,
) -> BinSpec:
    """Pick the smallest bin that holds this pocket at this depth."""
    length_u, width_u = grid_units_for(pocket, tuning)
    return BinSpec(
        length_u=length_u,
        width_u=width_u,
        height_u=height_units_for(depth_mm),
        depth_mm=depth_mm,
        **kwargs,
    )


def _extrude(poly: Polygon, z_bottom: float, height: float) -> cq.Workplane:
    """Extrude a shapely polygon, holes and all, into a CadQuery solid."""
    exterior = list(poly.exterior.coords)[:-1]
    solid = (
        cq.Workplane("XY")
        .polyline([(float(x), float(y)) for x, y in exterior])
        .close()
        .extrude(height)
    )
    for ring in poly.interiors:
        pts = list(ring.coords)[:-1]
        hole = (
            cq.Workplane("XY")
            .polyline([(float(x), float(y)) for x, y in pts])
            .close()
            .extrude(height)
        )
        solid = solid.cut(hole)
    return solid.translate((0, 0, z_bottom))


def build(pocket: Polygon, spec: BinSpec, tuning: Tuning = DEFAULTS) -> Build:
    """Make the bin and cut the pocket into it."""
    warnings: list[str] = []

    if max(spec.length_u, spec.width_u) > MAX_UNITS_ON_BED:
        raise BedTooSmall(
            f"{spec.length_u}x{spec.width_u} units is "
            f"{max(spec.length_u, spec.width_u) * 42 - 0.5:.0f} mm across, past the "
            f"X2D's {MAX_UNITS_ON_BED}-unit ({MAX_UNITS_ON_BED * 42 - 0.5:.0f} mm) "
            "bed. Split the tool across two bins, or print it on a machine with "
            "a larger bed."
        )

    box = GridfinityBox(
        spec.length_u,
        spec.width_u,
        spec.height_u,
        solid=True,
        holes=spec.magnet_holes,
        unsupported_holes=spec.magnet_holes,
        no_lip=not spec.keep_lip,
        labels=spec.label_shelf,
    )
    body = box.cq_obj

    usable = box.max_height
    if spec.depth_mm > usable + 1e-6:
        raise PocketTooDeep(
            f"A {spec.height_u}U bin gives {usable:.1f} mm of usable depth, but "
            f"{spec.depth_mm:.1f} mm was asked for. Use "
            f"{height_units_for(spec.depth_mm)}U instead."
        )
    if spec.depth_mm > usable - tuning.floor_mm:
        warnings.append(
            f"Pocket leaves under {tuning.floor_mm} mm of floor "
            f"({usable - spec.depth_mm:.1f} mm). Consider one more height unit."
        )

    top = box.top_ref_height
    bb = body.vals()[0].BoundingBox()
    z_bottom = top - spec.depth_mm
    # Cut from above the lip rim so the pocket is open at the top whether or
    # not the lip was kept.
    height = (bb.zmax + 1.0) - z_bottom

    centred = centre_on(pocket, 0.0, 0.0)
    cutter = _extrude(centred, z_bottom, height)
    return Build(body.cut(cutter), spec, centred, warnings)


def export(build_result: Build, stem: str, out_dir: str = "out") -> list[str]:
    """Write STL for slicing and STEP for later editing."""
    from pathlib import Path

    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    paths = []
    stl, step = d / f"{stem}.stl", d / f"{stem}.step"
    cq.exporters.export(build_result.body, str(stl))
    cq.exporters.export(build_result.body, str(step))
    paths.extend([str(stl), str(step)])
    return paths
