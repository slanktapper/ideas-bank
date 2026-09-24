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


def test_margins_are_split_evenly_and_account_for_everything():
    p = plan(442.0, 390.0)
    assert p.margin_x_mm == pytest.approx((442 - 10 * 42) / 2)
    assert p.margin_y_mm == pytest.approx((390 - 9 * 42) / 2)
    # Margins plus grid must reconstruct the drawer exactly.
    assert 2 * p.margin_x_mm + p.units_x * GRID_PITCH_MM == pytest.approx(442.0)
    assert 2 * p.margin_y_mm + p.units_y * GRID_PITCH_MM == pytest.approx(390.0)


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
    p = plan(400.0, 300.0, drawer_h_mm=95.0)
    note = " ".join(p.notes)
    assert "12U" in note, note


def test_shallow_drawer_warns_about_headroom():
    p = plan(400.0, 300.0, drawer_h_mm=16.0)
    assert any("closes over" in n for n in p.notes)


def test_near_miss_on_an_extra_unit_is_flagged():
    """A drawer 4mm short of another row should say so -- that is actionable."""
    # 10 units = 420mm; 458mm is 38mm of remainder, 4mm short of 11 units.
    p = plan(458.0, 300.0)
    assert p.units_x == 10
    assert any("short of fitting 11 units" in n for n in p.notes), p.notes


def test_comfortable_margin_is_not_flagged():
    p = plan(442.0, 390.0)      # 22mm and 12mm of remainder -- nowhere near
    assert not any("short of fitting" in n for n in p.notes), p.notes


def test_margin_can_never_exceed_half_a_pitch():
    """Guards the invariant that made the old warning dead code."""
    for w in range(60, 700, 7):
        p = plan(float(w), 300.0)
        assert 0 <= p.margin_x_mm < GRID_PITCH_MM / 2
