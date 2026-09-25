"""Drawer planning: the step everything else depends on.

A wrong unit count here wastes a whole drawer's worth of printing, so the
tiling is checked for exact coverage rather than eyeballed from the preview.
"""
import pytest

from gridfinity_negatives.config import GRID_PITCH_MM, PRINTERS
from gridfinity_negatives.drawer import plan, split_span


@pytest.mark.parametrize("total,mx", [(1, 7), (7, 7), (8, 7), (10, 7),
                                      (13, 7), (15, 7), (22, 7), (6, 6)])
def test_split_span_covers_exactly_and_fits_the_bed(total, mx):
    parts = split_span(total, mx)
    assert sum(parts) == total, "tiling lost or gained units"
    assert all(1 <= p <= mx for p in parts), "a tile does not fit the bed"
    assert max(parts) - min(parts) <= 1, "tiles should be as even as possible"


def test_split_span_prefers_even_over_greedy():
    """10 units on a 7-unit bed is 5+5, not 7+3."""
    assert split_span(10, 7) == [5, 5]
    assert split_span(8, 7) == [4, 4]


@pytest.mark.parametrize("w,d,ux,uy", [
    (442, 390, 10, 9),
    (400, 300, 9, 7),
    (300, 225, 7, 5),
    (84, 42, 2, 1),
])
def test_unit_count_is_floor_of_the_pitch(w, d, ux, uy):
    p = plan(float(w), float(d))
    assert (p.units_x, p.units_y) == (ux, uy)


def test_the_default_is_a_corner_not_the_middle():
    """A centred grid has no datum in a drawer, so it cannot be positioned."""
    from gridfinity_negatives.drawer import DEFAULT_ALIGN
    assert DEFAULT_ALIGN == "back-right"
    p = plan(442.0, 390.0)
    assert p.align == "back-right"
    g = p.gaps_mm
    assert g["right"] == pytest.approx(0.0), "not flush against the right wall"
    assert g["back"] == pytest.approx(0.0), "not flush against the back wall"
    assert g["left"] == pytest.approx(p.slack_x_mm)
    assert g["front"] == pytest.approx(p.slack_y_mm)


def test_gaps_always_account_for_the_whole_drawer():
    """However it is aligned, gaps plus grid must reconstruct the drawer."""
    for align in ("center", "back-right", "front-left"):
        p = plan(442.0, 390.0, align=align)
        g = p.gaps_mm
        assert g["left"] + g["right"] + p.units_x * GRID_PITCH_MM == \
            pytest.approx(442.0)
        assert g["front"] + g["back"] + p.units_y * GRID_PITCH_MM == \
            pytest.approx(390.0)


def test_centring_is_allowed_but_warns():
    p = plan(442.0, 390.0, align="center")
    assert p.gaps_mm["left"] == pytest.approx(p.slack_x_mm / 2)
    assert any("cannot be positioned accurately" in n for n in p.notes), p.notes


def test_an_unknown_alignment_is_refused():
    with pytest.raises(ValueError, match="not an alignment"):
        plan(442.0, 390.0, align="somewhere")


def test_tiles_cover_the_grid_exactly_without_overlap():
    p = plan(560.0, 410.0)   # 13 x 9 units, needs tiling both ways
    covered = set()
    for t in p.tiles:
        for i in range(t.length_u):
            for j in range(t.width_u):
                cell = (t.origin_x_u + i, t.origin_y_u + j)
                assert cell not in covered, f"tiles overlap at {cell}"
                covered.add(cell)
    expected = {(i, j) for i in range(p.units_x) for j in range(p.units_y)}
    assert covered == expected, "tiles do not cover the grid exactly"


def test_h2d_allows_seven_units_where_the_x2d_allowed_six():
    """Regression: the bed was hard-coded to the X2D, which was never bought."""
    assert PRINTERS["h2d"].max_units_x == 7
    assert PRINTERS["h2d"].max_units_y == 7
    assert PRINTERS["x2d"].max_units_x == 6
    # A 7-unit span is one tile on the H2D and two on the X2D.
    assert len(plan(300.0, 300.0, printer=PRINTERS["h2d"]).tiles) == 1
    assert len(plan(300.0, 300.0, printer=PRINTERS["x2d"]).tiles) == 4


def test_drawer_too_small_for_one_unit_is_refused():
    with pytest.raises(ValueError, match="does not fit"):
        plan(40.0, 200.0)


def test_height_note_reports_the_largest_bin_that_fits():
    """95mm takes a 13U bin (94.8mm). The old formula said 12U."""
    p = plan(400.0, 300.0, drawer_h_mm=95.0)
    note = " ".join(p.notes)
    assert "up to 13U" in note, note


def test_headroom_note_states_the_baseplate_adds_nothing():
    p = plan(400.0, 300.0, drawer_h_mm=63.0)
    assert any("adds no height" in n for n in p.notes), p.notes


def test_near_miss_on_an_extra_unit_is_flagged():
    """A drawer 4mm short of another row should say so -- that is actionable."""
    # 10 units = 420mm; 458mm is 38mm of remainder, 4mm short of 11 units.
    p = plan(458.0, 300.0)
    assert p.units_x == 10
    assert any("short of fitting 11 units" in n for n in p.notes), p.notes


def test_comfortable_margin_is_not_flagged():
    p = plan(442.0, 390.0)      # 22mm and 12mm of remainder -- nowhere near
    assert not any("short of fitting" in n for n in p.notes), p.notes


def test_slack_can_never_reach_a_whole_pitch():
    """The leftover is a floor remainder, so another unit would always fit."""
    for w in range(60, 700, 7):
        p = plan(float(w), 300.0)
        assert 0 <= p.slack_x_mm < GRID_PITCH_MM
        assert p.gaps_mm["left"] + p.gaps_mm["right"] == pytest.approx(p.slack_x_mm)


@pytest.mark.parametrize("drawer_h,expect_u", [
    (63.0, 8),    # 8U = 59.8mm, fits
    (60.0, 8),    # 8U = 59.8mm, just fits -- the old formula said 7
    (53.0, 7),    # 7U = 52.8mm, fits -- the old formula said 6
    (24.0, 2),    # 2U = 17.8mm
    (101.0, 13),  # 13U = 94.8mm
])
def test_headroom_accounts_for_the_lip_not_the_baseplate(drawer_h, expect_u):
    """Regression: the note subtracted the baseplate and ignored the lip rim.

    A bin's base drops through the baseplate socket to the drawer floor, so
    the baseplate adds no height. What stands proud is the 3.8mm lip.
    """
    from gridfinity_negatives.drawer import LIP_RIM_MM

    p = plan(400.0, 300.0, drawer_h_mm=drawer_h)
    note = " ".join(p.notes)
    assert f"up to {expect_u}U" in note, note
    # And the bin it names must genuinely fit.
    assert expect_u * 7 + LIP_RIM_MM <= drawer_h
    # One more unit must genuinely not fit.
    assert (expect_u + 1) * 7 + LIP_RIM_MM > drawer_h


def test_drawer_too_shallow_for_any_bin_says_so():
    p = plan(400.0, 300.0, drawer_h_mm=9.0)
    assert any("not room for even a 1U" in n for n in p.notes), p.notes
