"""Engraving location codes into the underside of a bin."""
import cadquery as cq
import pytest
from cqgridfinity import GridfinityBox

from gridfinity_negatives.stamp import bottom_pads, engrave_code


def _underside(body):
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    return [f for f in shape.Faces()
            if f.normalAt().z < -0.99 and f.Center().z < 0.01][0]


def test_engraving_removes_material_without_changing_the_envelope():
    box = GridfinityBox(1, 1, 3).cq_obj
    before = box.vals()[0].Volume()
    bb_before = box.vals()[0].BoundingBox()

    body, size = engrave_code(box, "KWL1N1T")
    after = body.vals()[0].Volume()
    bb = body.vals()[0].BoundingBox()

    assert after < before, "nothing was engraved"
    assert body.vals()[0].isValid()
    for a, b in ((bb.xlen, bb_before.xlen), (bb.ylen, bb_before.ylen),
                 (bb.zlen, bb_before.zlen)):
        assert a == pytest.approx(b, abs=1e-6), "engraving changed the bin size"
    assert 2.0 < size <= 8.0


def test_text_is_mirrored_so_it_reads_when_turned_over():
    """The underside is read from below; unmirrored text reads backwards there.

    Compares the centroid of the material actually removed against the
    centroid of the same glyph unmirrored. They must sit on opposite sides of
    the pad centre. Uses an asymmetric glyph, since a symmetric one would
    pass whether or not the mirror was applied.
    """
    raw = cq.Workplane("XY").text("F", 8.0, 0.6, font="DejaVu Sans Mono",
                                  halign="center", valign="center")
    raw_cx = raw.vals()[0].Center().x
    assert abs(raw_cx) > 0.05, "glyph is not asymmetric enough to test a mirror"

    original = GridfinityBox(1, 1, 3).cq_obj
    body, size = engrave_code(original, "F")
    assert size == pytest.approx(8.0, abs=0.01), "size differs; centroids not comparable"

    removed = original.cut(body)          # the engraving itself, as a solid
    assert removed.vals(), "nothing was removed"
    cut_cx = removed.vals()[0].Center().x

    assert cut_cx == pytest.approx(-raw_cx, abs=0.02), (
        f"engraving centroid x={cut_cx:.3f}, unmirrored glyph x={raw_cx:.3f} -- "
        "expected opposite sides of the pad centre"
    )


def test_engraving_stays_inside_the_pad():
    body, _ = engrave_code(GridfinityBox(1, 1, 3).cq_obj, "KWL10N12T")
    face = _underside(body)
    pad = bottom_pads(GridfinityBox(1, 1, 3).cq_obj)[0]
    cx, cy, pw, ph = pad
    for w in list(face.Wires())[1:]:
        bb = w.BoundingBox()
        assert bb.xmin >= cx - pw / 2 and bb.xmax <= cx + pw / 2, "text ran off the pad"
        assert bb.ymin >= cy - ph / 2 and bb.ymax <= cy + ph / 2


@pytest.mark.parametrize("size,pads", [("1x1", 1), ("2x1", 2), ("2x2", 4)])
def test_one_pad_per_grid_unit(size, pads):
    lu, wu = (int(v) for v in size.split("x"))
    assert len(bottom_pads(GridfinityBox(lu, wu, 3).cq_obj)) == pads


def test_code_lands_on_a_single_pad_not_across_the_gap():
    """A 2x1 has two separate pads; text centred on the bin would span nothing."""
    body, _ = engrave_code(GridfinityBox(2, 1, 3).cq_obj, "KWL1N1T")
    face = _underside(body)
    inner = list(face.Wires())[1:]
    assert inner, "engraving missed the pad entirely"


def test_empty_code_is_refused():
    with pytest.raises(ValueError, match="empty code"):
        engrave_code(GridfinityBox(1, 1, 3).cq_obj, "   ")
