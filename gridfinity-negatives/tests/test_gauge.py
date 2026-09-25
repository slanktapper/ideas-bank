"""Gap gauges.

The whole tool is one promise: the part's reach equals the number written on
it. If that is off by a millimetre the gauge is worse than useless, because it
lies with authority.
"""
import cadquery as cq
import pytest

from gridfinity_negatives.gauge import (
    DEFAULT_GAUGE, GaugeSpec, gauge_set, make_gauge,
)


@pytest.mark.parametrize("length", [8.0, 12.5, 14.5, 17.0, 19.0, 34.0])
def test_reach_equals_the_stated_length(length):
    """Measured from the datum face to the arm tip, with nothing added."""
    bb = make_gauge(length).vals()[0].BoundingBox()
    assert bb.ylen == pytest.approx(length, abs=1e-6), (
        f"gauge marked {length} actually reaches {bb.ylen}"
    )
    assert bb.ymin == pytest.approx(0.0, abs=1e-6), "datum face is not at y=0"


def test_the_foot_is_inside_the_measured_length_not_added_to_it():
    """A foot that stuck out behind the datum would offset every reading."""
    g = make_gauge(14.5)
    bb = g.vals()[0].BoundingBox()
    assert bb.ylen == pytest.approx(14.5, abs=1e-6)
    assert bb.ylen > DEFAULT_GAUGE.foot_depth_mm


def test_gauge_is_thinner_than_the_baseplate_edge_it_registers_against():
    """4.75mm of baseplate edge is vertical; a taller gauge would ride up it."""
    bb = make_gauge(14.5).vals()[0].BoundingBox()
    assert bb.zlen < 4.75


def test_foot_is_wider_than_the_arm_so_it_cannot_skew():
    g = make_gauge(14.5)
    bb = g.vals()[0].BoundingBox()
    assert bb.xlen == pytest.approx(DEFAULT_GAUGE.foot_length_mm)
    assert DEFAULT_GAUGE.foot_length_mm > DEFAULT_GAUGE.arm_width_mm * 3


def test_length_is_engraved_not_embossed():
    """Raised text on the underside would print in mid-air."""
    spec = DEFAULT_GAUGE
    plain_vol = (spec.foot_length_mm * spec.foot_depth_mm * spec.thickness_mm
                 + spec.arm_width_mm * (14.5 - spec.foot_depth_mm) * spec.thickness_mm)
    actual = make_gauge(14.5).vals()[0].Volume()
    assert actual < plain_vol, "material was added, not removed"


def test_engraving_is_mirrored_to_read_when_turned_over():
    raw = cq.Workplane("XY").text("7", 3.0, 0.5, font="DejaVu Sans Mono",
                                  halign="center", valign="center")
    raw_cx = raw.vals()[0].Center().x
    assert abs(raw_cx) > 0.01, "glyph too symmetric to detect a mirror"

    spec = GaugeSpec(text_depth_mm=0.5)
    body = make_gauge(14.5, spec, label="7")
    plain = (cq.Workplane("XY")
             .box(spec.foot_length_mm, spec.foot_depth_mm, spec.thickness_mm,
                  centered=(True, False, False))
             .union(cq.Workplane("XY").box(spec.arm_width_mm, 14.5,
                                           spec.thickness_mm,
                                           centered=(True, False, False))))
    removed = plain.cut(body)
    assert removed.vals(), "nothing engraved"
    assert removed.vals()[0].Center().x == pytest.approx(-raw_cx, abs=0.3), (
        "engraving is not mirrored, so it reads backwards in the hand"
    )


def test_a_ladder_is_evenly_spaced_around_the_nominal():
    lengths = [L for L, _ in gauge_set(14.5)]
    assert lengths == [12.5, 13.5, 14.5, 15.5, 16.5]


def test_a_gauge_shorter_than_its_own_foot_is_refused():
    with pytest.raises(ValueError):
        make_gauge(3.0)


def test_each_gauge_is_a_valid_solid():
    for _, body in gauge_set(17.0):
        assert body.vals()[0].isValid()
