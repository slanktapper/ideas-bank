"""Bins that reach past the grid to meet a drawer wall.

Three properties matter and none is visible from the bounding box alone: the
part is the right size, its interior is one cavity rather than two, and its
grid base profile is untouched so it still seats in a baseplate.
"""
import cadquery as cq
import pytest
from cqgridfinity import GridfinityBox

from gridfinity_negatives.extended import (
    ExtensionError, describe, extended_bin, interior_of,
)
from gridfinity_negatives.stamp import bottom_pads


@pytest.mark.parametrize("lu,wu,el,ef", [
    (3, 1, 38.5, 34.5), (6, 2, 38.5, 0.0), (4, 1, 0.0, 34.5),
    (1, 2, 38.5, 0.0), (2, 2, 38.5, 0.0),
])
def test_outer_size_is_grid_plus_reach(lu, wu, el, ef):
    bb = extended_bin(lu, wu, 5, extend_left_mm=el,
                      extend_front_mm=ef).vals()[0].BoundingBox()
    assert bb.xlen == pytest.approx(lu * 42 - 0.5 + el, abs=0.01)
    assert bb.ylen == pytest.approx(wu * 42 - 0.5 + ef, abs=0.01)
    assert bb.zlen == pytest.approx(5 * 7 + 3.8, abs=0.01)
    assert bb.zmin == pytest.approx(0.0, abs=1e-6), "must sit on the drawer floor"


def test_the_interior_is_one_cavity_not_two():
    """The skirt is useless if the original wall still divides it off."""
    body = extended_bin(3, 1, 5, extend_left_mm=38.5, extend_front_mm=34.5)
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    floor_z, _ = interior_of(GridfinityBox(3, 1, 5).cq_obj)
    floors = [f for f in shape.Faces()
              if f.normalAt().z > 0.99 and abs(f.Center().z - floor_z) < 0.01]
    assert len(floors) == 1, f"{len(floors)} separate pockets; the wall survived"

    bb = shape.BoundingBox()
    expected = (bb.xlen - 2 * 2.1) * (bb.ylen - 2 * 2.1)
    assert floors[0].Area() == pytest.approx(expected, rel=0.01)


def test_the_grid_base_profile_survives():
    """The bin must still seat in a baseplate, so its grid pads are untouched."""
    plain = bottom_pads(GridfinityBox(3, 1, 5).cq_obj)
    ext = bottom_pads(extended_bin(3, 1, 5, extend_left_mm=38.5))
    plain_pads = {(round(x, 1), round(w, 1)) for x, _, w, _ in plain}
    ext_pads = {(round(x, 1), round(w, 1)) for x, _, w, _ in ext}
    assert plain_pads <= ext_pads, "a grid base pad was destroyed by the skirt"
    assert len(ext) == len(plain) + 1, "expected one extra pad under the skirt"


def test_the_result_is_a_valid_watertight_solid():
    for el, ef in ((38.5, 0.0), (0.0, 34.5), (38.5, 34.5)):
        s = extended_bin(3, 2, 5, extend_left_mm=el,
                         extend_front_mm=ef).vals()[0]
        assert s.isValid()
        assert s.Volume() > 0


def test_extending_adds_material_rather_than_removing_it():
    plain = GridfinityBox(3, 2, 5).cq_obj.vals()[0].Volume()
    ext = extended_bin(3, 2, 5, extend_left_mm=38.5).vals()[0].Volume()
    assert ext > plain


def test_no_extension_returns_a_plain_bin():
    a = extended_bin(2, 2, 5).vals()[0].Volume()
    b = GridfinityBox(2, 2, 5).cq_obj.vals()[0].Volume()
    assert a == pytest.approx(b)


def test_a_solid_bin_cannot_be_extended():
    with pytest.raises(ExtensionError, match="no cavity"):
        extended_bin(2, 2, 5, extend_left_mm=10, solid=True)


def test_negative_extension_is_refused():
    with pytest.raises(ExtensionError, match="negative"):
        extended_bin(2, 2, 5, extend_left_mm=-5)


def test_interior_inset_is_measured_not_assumed():
    """wall_th reads 1.0 but the usable inset is 2.1; building the skirt's
    cavity from wall_th would leave a ridge at the joint."""
    box = GridfinityBox(3, 2, 5)
    _, inset = interior_of(box.cq_obj)
    assert inset == pytest.approx(2.1, abs=0.05)
    assert inset != pytest.approx(box.wall_th, abs=0.05)


def test_describe_matches_the_layout_label():
    assert describe(6, 2, 5, 38.5, 0) == "6x2x5+38.5L"
    assert describe(3, 1, 5, 38.5, 34.5) == "3x1x5+38.5L+34.5F"
    assert describe(2, 2, 5) == "2x2x5"


def test_no_stray_ledge_survives_from_the_stacking_lip():
    """Regression: a 0.5 mm shelf was left running along the joint.

    The lip is a stepped profile reaching 2.6 mm inward, while the plain wall
    inset is 2.1 mm. Cutting the cavity to 2.1 left a sliver of lip behind,
    which in a slicer reads as a stray label shelf.
    """
    from gridfinity_negatives.extended import deepest_inset

    body = extended_bin(3, 1, 5, extend_left_mm=38.5, extend_front_mm=34.5)
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    floor_z, _ = interior_of(GridfinityBox(3, 1, 5).cq_obj)
    ztop = shape.BoundingBox().zmax

    strays = [f for f in shape.Faces()
              if f.normalAt().z > 0.99
              and floor_z + 0.5 < f.Center().z < ztop - 0.05]
    assert not strays, (
        f"{len(strays)} horizontal ledge(s) between the floor and the rim, at z="
        + ", ".join(f"{f.Center().z:.2f}" for f in strays)
    )


def test_the_lip_reaches_further_in_than_the_plain_wall():
    """The fact that made the ledge possible; pinned so it is not forgotten."""
    from gridfinity_negatives.extended import deepest_inset
    plain = GridfinityBox(3, 1, 5).cq_obj
    floor_z, inset = interior_of(plain)
    ztop = plain.vals()[0].BoundingBox().zmax
    left, front = deepest_inset(plain, floor_z, ztop)
    assert left > inset, "the lip no longer reaches past the wall inset"
    assert left == pytest.approx(2.6, abs=0.1)


@pytest.mark.parametrize("lu,wu,el,ef", [(2, 2, 38.5, 0.0), (1, 2, 38.5, 0.0),
                                         (4, 1, 0.0, 34.5)])
def test_every_extended_shape_is_ledge_free(lu, wu, el, ef):
    body = extended_bin(lu, wu, 5, extend_left_mm=el, extend_front_mm=ef)
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    floor_z, _ = interior_of(GridfinityBox(lu, wu, 5).cq_obj)
    ztop = shape.BoundingBox().zmax
    strays = [f for f in shape.Faces()
              if f.normalAt().z > 0.99
              and floor_z + 0.5 < f.Center().z < ztop - 0.05]
    assert not strays, f"ledge in {lu}x{wu}+{el}L+{ef}F"
