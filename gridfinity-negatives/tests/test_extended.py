"""Bins built at an arbitrary outer size.

These exist because the first implementation welded a square block onto a
stock bin, which left the original 3.75 mm corner fillets stranded mid-wall,
kinked the side where block met curve, and gave the part square outer corners.
The tests below are the shape of that failure, turned into assertions.
"""
import cadquery as cq
import pytest
from cqgridfinity import GridfinityBox

from gridfinity_negatives.extended import (
    ExtendedBox, ExtensionError, describe, extended_bin,
)
from gridfinity_negatives.stamp import bottom_pads

CASES = [(3, 1, 38.5, 34.5), (6, 2, 38.5, 0.0), (4, 1, 0.0, 34.5),
         (1, 2, 38.5, 0.0), (2, 2, 38.5, 0.0)]


def _shape(body):
    return cq.Shape.cast(body.vals()[0].wrapped)


def _corner_radii(shape):
    """Radii of the cylindrical faces at the outer corners."""
    bb = shape.BoundingBox()
    out = []
    for f in shape.Faces():
        if f.geomType() != "CYLINDER":
            continue
        r = f._geomAdaptor().Cylinder().Radius()
        c = f.Center()
        at_corner = ((abs(c.x - bb.xmin) < 6 or abs(c.x - bb.xmax) < 6)
                     and (abs(c.y - bb.ymin) < 6 or abs(c.y - bb.ymax) < 6))
        if at_corner and r > 2:
            out.append(round(r, 3))
    return sorted(out)


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_outer_size_is_grid_plus_extension(lu, wu, el, ef):
    bb = extended_bin(lu, wu, 5, extend_left_mm=el,
                      extend_front_mm=ef).vals()[0].BoundingBox()
    assert bb.xlen == pytest.approx(lu * 42 - 0.5 + el, abs=0.01)
    assert bb.ylen == pytest.approx(wu * 42 - 0.5 + ef, abs=0.01)
    assert bb.zlen == pytest.approx(5 * 7 + 3.8, abs=0.01)
    assert bb.zmin == pytest.approx(0.0, abs=1e-6), "must sit on the drawer floor"


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_the_corners_are_rounded_exactly_as_a_stock_bin(lu, wu, el, ef):
    """The weld left square outer corners. Built at size, all four are round."""
    stock = _corner_radii(_shape(GridfinityBox(lu, wu, 5).cq_obj))
    ext = _corner_radii(_shape(extended_bin(lu, wu, 5, extend_left_mm=el,
                                            extend_front_mm=ef)))
    assert ext == stock, f"corner profile differs from stock: {ext} vs {stock}"
    assert 3.75 in ext, "the 3.75 mm outer corner radius is missing"


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_the_wall_is_one_continuous_loop(lu, wu, el, ef):
    """A welded seam shows as extra wires in section. There must be two:
    the outer wall and the cavity, and nothing else."""
    body = extended_bin(lu, wu, 5, extend_left_mm=el, extend_front_mm=ef)
    wires = sum(len(f.Wires()) for f in body.section(20.0).faces().vals())
    assert wires == 2, f"{wires} wires at mid-height; expected outer + cavity"


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_no_stranded_ledge_anywhere_up_the_wall(lu, wu, el, ef):
    """The stock bin's corner fillets used to survive inside the new wall."""
    shape = _shape(extended_bin(lu, wu, 5, extend_left_mm=el, extend_front_mm=ef))
    ztop = shape.BoundingBox().zmax
    strays = [f for f in shape.Faces()
              if f.normalAt().z > 0.99 and 7.5 < f.Center().z < ztop - 0.05]
    assert not strays, (
        "horizontal ledge(s) mid-wall at z="
        + ", ".join(f"{f.Center().z:.2f}" for f in strays)
    )


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_the_lip_runs_all_the_way_round(lu, wu, el, ef):
    body = extended_bin(lu, wu, 5, extend_left_mm=el, extend_front_mm=ef)
    wires = sum(len(f.Wires()) for f in body.section(37.0).faces().vals())
    assert wires == 2, f"{wires} wires through the lip; it does not close"


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_base_pads_stay_on_the_grid_so_the_bin_still_seats(lu, wu, el, ef):
    """The chamfered pads must remain at 42 mm pitch and unchanged in size."""
    stock = {(round(w, 1), round(h, 1))
             for _, _, w, h in bottom_pads(GridfinityBox(lu, wu, 5).cq_obj)}
    pads = bottom_pads(extended_bin(lu, wu, 5, extend_left_mm=el,
                                    extend_front_mm=ef))
    grid_pads = [p for p in pads if (round(p[2], 1), round(p[3], 1)) in stock]
    assert len(grid_pads) == lu * wu, "a grid base pad was lost or resized"
    # and they are still on the 42 mm pitch
    xs = sorted({round(p[0], 2) for p in grid_pads})
    for a, b in zip(xs, xs[1:]):
        assert b - a == pytest.approx(42.0, abs=0.01), "pad pitch is not 42 mm"


def test_the_extension_is_solid_down_to_the_drawer_floor():
    """Base pads exist only under grid cells; the skirt needs its own floor."""
    body = extended_bin(3, 1, 5, extend_left_mm=38.5)
    sec = body.section(1.0)
    assert sec.faces().vals(), "nothing at z=1; the skirt would hang in the air"
    bb = cq.Shape.cast(body.vals()[0].wrapped).BoundingBox()
    xs = [f.BoundingBox().xmin for f in sec.faces().vals()]
    assert min(xs) == pytest.approx(bb.xmin, abs=0.01), (
        "the skirt does not reach the floor at its outer edge"
    )


@pytest.mark.parametrize("lu,wu,el,ef", CASES)
def test_the_result_is_a_valid_solid(lu, wu, el, ef):
    s = extended_bin(lu, wu, 5, extend_left_mm=el, extend_front_mm=ef).vals()[0]
    assert s.isValid() and s.Volume() > 0


def test_no_extension_gives_exactly_a_stock_bin():
    a = extended_bin(2, 2, 5).vals()[0].Volume()
    b = GridfinityBox(2, 2, 5).cq_obj.vals()[0].Volume()
    assert a == pytest.approx(b)


def test_extending_adds_material():
    plain = GridfinityBox(3, 2, 5).cq_obj.vals()[0].Volume()
    ext = extended_bin(3, 2, 5, extend_left_mm=38.5).vals()[0].Volume()
    assert ext > plain


def test_a_solid_bin_cannot_be_extended():
    with pytest.raises(ExtensionError, match="no cavity"):
        extended_bin(2, 2, 5, extend_left_mm=10, solid=True)


def test_negative_extension_is_refused():
    with pytest.raises(ExtensionError, match="negative"):
        ExtendedBox(2, 2, 5, extend_left_mm=-5)


def test_the_extension_lands_on_the_left_and_front_only():
    """The extra material must be on the wall sides, not shared out evenly.

    Both bins are centred on their own bounding box, so absolute coordinates
    say nothing. What matters is where the grid pads sit relative to each
    edge: unchanged on the right and back, pushed in by the extension on the
    left and front.
    """
    def gaps(body):
        bb = body.vals()[0].BoundingBox()
        # Grid pads only: an extended bin also has the skirt's floor, whose
        # footprint is the whole part and would swamp the measurement.
        pads = [p for p in bottom_pads(body)
                if abs(p[2] - 35.6) < 0.2 and abs(p[3] - 35.6) < 0.2]
        assert pads, "no grid base pads found"
        left = min(x - w / 2 for x, _, w, _ in pads) - bb.xmin
        right = bb.xmax - max(x + w / 2 for x, _, w, _ in pads)
        front = min(y - h / 2 for _, y, _, h in pads) - bb.ymin
        back = bb.ymax - max(y + h / 2 for _, y, _, h in pads)
        return left, right, front, back

    sl, sr, sf, sb = gaps(GridfinityBox(3, 2, 5).cq_obj)
    el, er, ef, eb = gaps(extended_bin(3, 2, 5, extend_left_mm=38.5,
                                       extend_front_mm=34.5))
    assert er == pytest.approx(sr, abs=0.01), "the right edge moved off the grid"
    assert eb == pytest.approx(sb, abs=0.01), "the back edge moved off the grid"
    assert el - sl == pytest.approx(38.5, abs=0.01)
    assert ef - sf == pytest.approx(34.5, abs=0.01)


def test_describe_matches_the_layout_label():
    assert describe(6, 2, 5, 38.5, 0) == "6x2x5+38.5L"
    assert describe(3, 1, 5, 38.5, 34.5) == "3x1x5+38.5L+34.5F"
    assert describe(2, 2, 5) == "2x2x5"
