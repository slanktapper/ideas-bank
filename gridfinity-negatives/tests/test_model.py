"""Guards on the geometry contract with cq-gridfinity.

These assertions are not testing our code so much as pinning down someone
else's. If cq-gridfinity changes its coordinate system or height convention
in an upgrade, every pocket silently lands at the wrong depth. Better to
fail here than to find out on the print bed.
"""
import pytest
from cqgridfinity import GridfinityBox
from shapely.geometry import box as shapely_box

from gridfinity_negatives.config import BASE_PROFILE_MM, GRID_PITCH_MM
from gridfinity_negatives.geometry import pocket_profile
from gridfinity_negatives.model import (
    BedTooSmall, BinSpec, PocketTooDeep, auto_spec, build, export,
)


@pytest.mark.parametrize("u", [2, 3, 6])
def test_cqgridfinity_height_convention(u):
    b = GridfinityBox(1, 1, u, solid=True)
    bb = b.cq_obj.vals()[0].BoundingBox()
    assert b.top_ref_height == pytest.approx(u * 7.0), "main top surface moved"
    assert bb.zmax == pytest.approx(u * 7.0 + 3.8, abs=0.01), "lip rim height moved"
    assert b.max_height == pytest.approx((u - 1) * 7.0), "usable depth rule moved"
    assert bb.zmin == pytest.approx(0.0), "body no longer sits on z=0"


@pytest.mark.parametrize("lu,wu", [(1, 1), (2, 3)])
def test_body_is_centred_on_origin(lu, wu):
    bb = GridfinityBox(lu, wu, 3, solid=True).cq_obj.vals()[0].BoundingBox()
    assert bb.xmin == pytest.approx(-(lu * GRID_PITCH_MM - 0.5) / 2, abs=0.01)
    assert bb.xmax == pytest.approx((lu * GRID_PITCH_MM - 0.5) / 2, abs=0.01)
    assert bb.ymin == pytest.approx(-(wu * GRID_PITCH_MM - 0.5) / 2, abs=0.01)


def test_pocket_removes_the_volume_it_should():
    """Depth is right if the material removed matches area x depth."""
    pocket = pocket_profile(shapely_box(0, 0, 60, 20), relief=False)
    spec = auto_spec(pocket, depth_mm=10.0)
    result = build(pocket, spec)

    uncut = GridfinityBox(spec.length_u, spec.width_u, spec.height_u,
                          solid=True).cq_obj.vals()[0].Volume()
    cut = result.body.vals()[0].Volume()
    removed = uncut - cut
    expected = pocket.area * spec.depth_mm
    assert removed == pytest.approx(expected, rel=0.02), (
        f"removed {removed:.0f} mm^3, expected {expected:.0f} mm^3 -- "
        "pocket depth or placement is wrong"
    )


def test_pocket_floor_is_left_intact():
    """The cut must not reach through into the base profile."""
    pocket = pocket_profile(shapely_box(0, 0, 30, 30), relief=False)
    spec = BinSpec(2, 2, 4, depth_mm=21.0)   # 4U gives 21mm usable
    result = build(pocket, spec)
    bb = result.body.vals()[0].BoundingBox()
    assert bb.zmin == pytest.approx(0.0), "cut broke through the bottom"
    floor = spec.height_u * 7.0 - spec.depth_mm
    assert floor >= BASE_PROFILE_MM - 1e-6


def test_auto_spec_picks_the_smallest_bin_that_fits():
    pocket = pocket_profile(shapely_box(0, 0, 100, 30), relief=False)
    spec = auto_spec(pocket, depth_mm=12.0)
    assert (spec.length_u, spec.width_u) == (3, 1)
    assert spec.height_u == 3          # (3-1)*7 = 14mm usable >= 12
    assert spec.depth_mm == 12.0


def test_too_deep_names_the_size_that_would_work():
    pocket = pocket_profile(shapely_box(0, 0, 30, 30), relief=False)
    with pytest.raises(PocketTooDeep, match="4U"):
        build(pocket, BinSpec(2, 2, 2, depth_mm=20.0))


def test_oversized_bin_is_refused_with_the_bed_limit():
    pocket = pocket_profile(shapely_box(0, 0, 300, 30), relief=False)
    spec = auto_spec(pocket, depth_mm=10.0)
    assert spec.length_u > 6
    with pytest.raises(BedTooSmall, match="bed"):
        build(pocket, spec)


def test_shallow_floor_warns_but_still_builds():
    pocket = pocket_profile(shapely_box(0, 0, 30, 30), relief=False)
    result = build(pocket, BinSpec(2, 2, 3, depth_mm=13.5))  # usable 14
    assert result.warnings and "floor" in result.warnings[0]


def test_export_writes_both_formats(tmp_path):
    pocket = pocket_profile(shapely_box(0, 0, 40, 20), relief=False)
    result = build(pocket, auto_spec(pocket, depth_mm=8.0))
    paths = export(result, "unit-test", str(tmp_path))
    assert len(paths) == 2
    for p in paths:
        assert (tmp_path / p.rsplit("/", 1)[-1]).stat().st_size > 1000


def test_relief_enlarges_the_pocket():
    plain = pocket_profile(shapely_box(0, 0, 60, 20), relief=False)
    scalloped = pocket_profile(shapely_box(0, 0, 60, 20), relief=True)
    assert scalloped.area > plain.area


def test_relief_actually_reaches_outside_the_tool():
    """A scallop that stays inside the outline is not a finger relief.

    Regression: centring on the pole of inaccessibility put the circle wholly
    inside anything fatter than its own radius, so --relief did nothing.
    """
    from gridfinity_negatives.config import DEFAULTS

    # A spanner-like shape: slim shaft, fat round end larger than the scallop.
    from shapely.geometry import Point as P
    from shapely.ops import unary_union
    tool = unary_union([shapely_box(0, -5, 120, 5), P(120, 0).buffer(14)])

    plain = pocket_profile(tool, relief=False)
    scalloped = pocket_profile(tool, relief=True)

    grew = scalloped.area - plain.area
    half_disc = 3.14159 * DEFAULTS.relief_radius_mm ** 2 / 2
    assert grew > 0.5 * half_disc, (
        f"relief only added {grew:.1f} mm^2; it is landing inside the outline"
    )
