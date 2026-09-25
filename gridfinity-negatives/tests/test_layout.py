"""Packing measured items into a drawer."""
import pytest

from gridfinity_negatives.drawer import plan
from gridfinity_negatives.layout import Item, load_items, pack

KWL1N1T = plan(542.5, 328.5, 63.0)   # 12 x 7 units, measured 2026-09-25


def test_footprint_covers_the_object_plus_clearance_and_walls():
    """A 272mm lighter needs 7 units: 6 units is 252mm, which is too short."""
    assert Item("bbq", 272, 43, 24).footprint_units() == (7, 2)
    assert 6 * 42 < 272 + 2 * 0.4 + 2 * 2.4 <= 7 * 42


def test_sharing_a_bin_beats_one_bin_each():
    """Four 272mm lighters in one bin use fewer units than four bins."""
    alone = Item("bbq", 272, 43, 24, per_bin=1, qty_max=4)
    shared = Item("bbq", 272, 43, 24, per_bin=4, qty_max=4)
    a = alone.footprint_units()
    sh = shared.footprint_units()
    assert a[0] * a[1] * alone.bins_needed > sh[0] * sh[1] * shared.bins_needed


def test_bins_are_sized_for_the_maximum_not_todays_count():
    """Bulk buying is the normal case; a bin sized for 1 fails when 4 arrive."""
    it = Item("bbq", 272, 43, 24, per_bin=2, qty_typical=1, qty_max=4)
    assert it.bins_needed == 2, "sized for today rather than the bulk purchase"
    assert it.qty_label() == "1-4"


def test_loose_items_are_sized_by_volume_not_by_a_neat_array():
    """Ten lighters in a heap need far less bin than ten in rows."""
    array = Item("bic", 81, 24, 12, per_bin=10, qty_max=10)
    heap = Item("bic", 81, 24, 12, qty_max=10, loose=True, bin_height_u=8)
    a, h = array.footprint_units(), heap.footprint_units()
    assert h[0] * h[1] < a[0] * a[1], "loose sizing gained nothing"
    assert heap.bins_needed == 1


def test_a_loose_bin_still_fits_one_whole_object():
    """Volume alone would allow a bin too short for a single lighter."""
    it = Item("bic", 81, 24, 12, qty_max=2, loose=True, bin_height_u=8)
    lu, wu = it.footprint_units()
    interior = sorted([lu * 42 - 0.5 - 4.8, wu * 42 - 0.5 - 4.8])
    assert interior[1] >= 81, "bin is too short for one lighter"


def test_packing_never_overlaps_and_stays_in_bounds():
    items = load_items("items-KWL1N1T.yml")
    layout = pack(KWL1N1T, items)
    seen = set()
    for p in layout.placements:
        assert p.x_u >= 0 and p.y_u >= 0
        assert p.x_u + p.length_u <= KWL1N1T.units_x
        assert p.y_u + p.width_u <= KWL1N1T.units_y
        for i in range(p.length_u):
            for j in range(p.width_u):
                cell = (p.x_u + i, p.y_u + j)
                assert cell not in seen, f"two bins overlap at {cell}"
                seen.add(cell)
    assert len(seen) == layout.used_units


def test_the_directed_layout_places_everything():
    """The stated arrangement fits with no overflow."""
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    assert not layout.unplaced, [i.name for i in layout.unplaced]


def test_unmeasured_items_mark_the_whole_layout():
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"))
    assert not layout.all_measured, (
        "Bic and small GPS are assumed sizes; the layout must say so"
    )


def test_oversized_item_is_reported_not_silently_dropped():
    big = Item("beam", 900, 300, 20)
    layout = pack(KWL1N1T, [big])
    assert layout.unplaced and layout.unplaced[0].name == "beam"


def test_item_without_a_size_is_rejected(tmp_path):
    f = tmp_path / "bad.yml"
    f.write_text("items:\n  - name: mystery\n")
    with pytest.raises(ValueError, match="size of at least"):
        load_items(f)


# --- grid references -------------------------------------------------------

@pytest.mark.parametrize("x,y,ref", [
    (0, 0, "A1"), (2, 3, "C4"), (11, 6, "L7"), (25, 0, "Z1"), (26, 0, "AA1"),
])
def test_cell_ref_round_trips(x, y, ref):
    from gridfinity_negatives.layout import cell_ref, parse_cell
    assert cell_ref(x, y) == ref
    assert parse_cell(ref) == (x, y)


def test_cell_range_collapses_a_single_unit():
    from gridfinity_negatives.layout import cell_range
    assert cell_range(0, 0, 1, 1) == "A1"
    assert cell_range(0, 0, 7, 5) == "A1:G5"


@pytest.mark.parametrize("bad", ["", "4", "C", "::"])
def test_bad_cell_reference_is_rejected(bad):
    from gridfinity_negatives.layout import parse_cell
    with pytest.raises(ValueError, match="cell reference"):
        parse_cell(bad)


def test_explicit_bin_size_overrides_every_other_model():
    """Sparse objects need a stated bin; a bounding box badly overstates them."""
    keychain = Item("keys", 80, 38, 14, bin_size="2x1", bins=6, qty_max=18)
    assert keychain.footprint_units() == (2, 1)
    assert keychain.bins_needed == 6


def test_malformed_bin_size_is_rejected():
    with pytest.raises(ValueError, match="bin_size must be LxW"):
        Item("x", 10, 10, 10, bin_size="big").footprint_units()


def test_overflow_is_reported_rather_than_quietly_dropped():
    """An item with nowhere to go must surface, not vanish."""
    layout = pack(KWL1N1T, [Item("beam", 900, 300, 20)])
    assert layout.unplaced, "overflow vanished"
    assert layout.used_units <= KWL1N1T.total_units


# --- stated placement and fill ---------------------------------------------

def test_an_item_with_at_goes_exactly_there():
    from gridfinity_negatives.layout import cell_range
    it = Item("bbq", 272, 43, 24, bin_size="7x2", at="A6")
    layout = pack(KWL1N1T, [it])
    assert len(layout.placements) == 1
    p = layout.placements[0]
    assert cell_range(p.x_u, p.y_u, p.length_u, p.width_u) == "A6:G7"


def test_at_means_one_bin_not_one_per_item():
    """Regression: qty_max conjured extra copies that fought for the same cell."""
    it = Item("bbq", 272, 43, 24, bin_size="7x2", at="A6", qty_max=4)
    assert it.bins_needed == 1
    layout = pack(KWL1N1T, [it])
    assert not layout.unplaced, "phantom copies contended for the stated cell"


def test_stated_positions_are_never_displaced_by_packing():
    """A big auto-packed item must not take a cell that was asked for."""
    stated = Item("gps", 167, 75, 40, bin_size="5x2", at="H6")
    greedy = Item("big", 400, 250, 20)
    layout = pack(KWL1N1T, [greedy, stated])
    placed = {p.item.name: (p.x_u, p.y_u) for p in layout.placements}
    assert placed.get("gps") == (7, 5), "the stated position was taken"


def test_a_stated_position_off_the_grid_is_reported():
    it = Item("x", 10, 10, 10, bin_size="2x2", at="L7")   # runs off the edge
    layout = pack(KWL1N1T, [it])
    assert layout.unplaced


def test_fill_leaves_no_gap_it_could_have_filled():
    from gridfinity_negatives.layout import fill_remaining
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    fill_remaining(layout, ["2x2", "1x3", "1x2"], height_u=8)
    assert layout.free_units == 0, f"{layout.free_units} units left unfilled"


def test_fill_never_overlaps_what_was_already_placed():
    from gridfinity_negatives.layout import fill_remaining
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    fill_remaining(layout, ["2x2", "1x3", "1x2"], height_u=8)
    seen = set()
    for p in layout.placements:
        for i in range(p.length_u):
            for j in range(p.width_u):
                cell = (p.x_u + i, p.y_u + j)
                assert cell not in seen, f"overlap at {cell}"
                seen.add(cell)
    assert len(seen) == KWL1N1T.total_units


def test_forcing_a_height_applies_to_every_bin():
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    assert {p.item.height_units() for p in layout.placements} == {8}


def test_an_8U_bin_clears_the_63mm_drawer():
    """8U is 59.8mm with the lip; a 9U at 66.8mm would foul the drawer."""
    assert 8 * 7 + 3.8 <= 63.0
    assert 9 * 7 + 3.8 > 63.0


# --- capacity --------------------------------------------------------------

def test_capacity_counts_what_actually_fits():
    """A 7x2 at 8U takes two 272mm lighters: one across, two stacked."""
    it = Item("bbq", 272, 43, 24, bin_size="7x2", bin_height_u=8)
    assert it.capacity() == 2


def test_capacity_is_zero_when_the_object_is_longer_than_the_bin():
    """An 84mm object cannot go in a 2x2, whose interior is 78.7mm square."""
    it = Item("acc", 84, 75, 40, bin_size="2x2", bin_height_u=8)
    assert it.capacity() == 0
    assert Item("acc", 84, 75, 40, bin_size="3x2", bin_height_u=8).capacity() >= 1


def test_capacity_uses_the_better_of_the_two_orientations():
    it = Item("thin", 30, 200, 10, bin_size="6x1", bin_height_u=8)
    assert it.capacity() >= 1, "turning the object 90 degrees was not considered"


def test_capacity_accounts_for_stacking_in_the_height():
    shallow = Item("x", 60, 60, 24, bin_size="2x2", bin_height_u=3)
    deep = Item("x", 60, 60, 24, bin_size="2x2", bin_height_u=8)
    assert deep.capacity() > shallow.capacity()


# --- drawer-wide defaults --------------------------------------------------

def test_bin_height_is_declared_in_the_item_file():
    """It belongs with the drawer, not in a flag someone has to remember."""
    from gridfinity_negatives.layout import load_defaults
    d = load_defaults("items-KWL1N1T.yml")
    assert d.get("bin_height_u") == 8
    assert d.get("bin_height_provisional") is True, (
        "the height is not yet confirmed against the drawer; say so"
    )


def test_every_bin_takes_the_declared_height_including_spares():
    """One height for the whole drawer -- auto-filled bins included."""
    from gridfinity_negatives.layout import fill_remaining, load_defaults
    d = load_defaults("items-KWL1N1T.yml")
    h = d["bin_height_u"]
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=h)
    fill_remaining(layout, ["2x2", "1x3", "1x2"], height_u=h)
    heights = {p.item.height_units() for p in layout.placements}
    assert heights == {h}, f"mixed heights in one drawer: {sorted(heights)}"


def test_changing_the_declared_height_reaches_every_bin():
    from gridfinity_negatives.layout import fill_remaining
    for h in (3, 5, 8):
        layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=h)
        fill_remaining(layout, ["2x2", "1x3", "1x2"], height_u=h)
        assert {p.item.height_units() for p in layout.placements} == {h}


def test_missing_defaults_block_is_not_an_error(tmp_path):
    from gridfinity_negatives.layout import load_defaults
    f = tmp_path / "x.yml"
    f.write_text("items: []\n")
    assert load_defaults(f) == {}


def test_gps_and_flashlight_are_swapped():
    """GPS to A4:E5, flashlights to the back at H6:L7."""
    from gridfinity_negatives.layout import cell_range
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    at = {p.item.name: cell_range(p.x_u, p.y_u, p.length_u, p.width_u)
          for p in layout.placements if p.item.name in ("GPS", "Flashlight")}
    assert at["GPS"] == "A4:E5"
    assert at["Flashlight"] == "H6:L7"


# --- the directed arrangement ----------------------------------------------

def test_the_front_row_is_entirely_one_unit_deep():
    """Row 1 bins get extended over the front gap once it is measured, so
    every bin touching row 1 must be exactly one unit deep."""
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    front = [p for p in layout.placements if p.y_u == 0]
    assert len(front) == 4
    for p in front:
        assert p.width_u == 1, (
            f"bin at x={p.x_u} is {p.width_u} deep; it cannot absorb the gap"
        )
    assert sum(p.length_u for p in front) == KWL1N1T.units_x, (
        "the front row does not span the drawer"
    )


def test_the_arrangement_tiles_the_grid_exactly():
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    seen = set()
    for p in layout.placements:
        for i in range(p.length_u):
            for j in range(p.width_u):
                cell = (p.x_u + i, p.y_u + j)
                assert cell not in seen, f"overlap at {cell}"
                seen.add(cell)
    assert len(seen) == KWL1N1T.total_units
    assert not layout.unplaced


def test_named_items_sit_where_they_were_placed():
    from gridfinity_negatives.layout import cell_range
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"), height_u=8)
    at = {}
    for p in layout.placements:
        at.setdefault(p.item.name, []).append(
            cell_range(p.x_u, p.y_u, p.length_u, p.width_u))
    assert at["Bic lighter"] == ["J2:L3"], "Bic did not rotate into J2:L3"
    assert at["GPS"] == ["A4:E5"]
    assert at["Flashlight"] == ["H6:L7"]
    assert at["BBQ lighter"] == ["A6:F7"], "BBQ should be 6 wide now"
    assert sorted(at["Accessories"]) == ["A2:C3", "F4:I5", "J4:L5"]


def test_every_bin_is_explicitly_placed():
    """Nothing is auto-packed, so the arrangement cannot drift on a re-run."""
    items = load_items("items-KWL1N1T.yml")
    assert all(i.at for i in items), "an item has no stated position"


def test_the_merged_accessories_bin_clears_an_84mm_item():
    """The old 2x2 was 78.7mm inside and could not take it; a 4x2 can."""
    items = {(" ".join([i.name, i.at or ""])).strip(): i
             for i in load_items("items-KWL1N1T.yml")}
    merged = items["Accessories F4"]
    assert merged.bin_size == "4x2"
    lu, wu = merged.footprint_units()
    interior_long = lu * 42 - 0.5 - 4.8
    assert interior_long >= merged.width_mm, (
        f"{interior_long:.1f} mm inside cannot take an "
        f"{merged.width_mm:.0f} mm accessory"
    )
    assert merged.capacity() >= 1


# --- bins that reach into the drawer's gap ---------------------------------

def test_capacity_counts_the_reach_into_the_gap():
    """Regression: a 6x2 + 38.5mm bin reported holding nothing.

    capacity() measured the grid footprint only, so a 272mm lighter did not
    fit a bin with 285mm inside it.
    """
    extended = Item("bbq", 272, 43, 24, bin_size="6x2", bin_height_u=8,
                    extend_left_mm=38.5)
    plain = Item("bbq", 272, 43, 24, bin_size="6x2", bin_height_u=8)
    assert plain.capacity() == 0, "the grid footprint alone really is too short"
    assert extended.capacity() >= 1, "the reach into the gap was ignored"


def test_outer_size_includes_the_extension():
    p = pack(plan(542.5, 328.5, 63.0),
             load_items("items-KWL1N1T.yml"), height_u=8)
    by_name = {pl.item.name: pl for pl in p.placements}
    w, h = by_name["BBQ lighter"].outer_size_mm()
    assert w == pytest.approx(6 * 42 - 0.5 + 38.5)
    assert h == pytest.approx(2 * 42 - 0.5)


def test_extended_bins_reach_the_drawer_walls_exactly():
    """An extension equal to the gap must land flush, not over or short."""
    dp = plan(542.5, 328.5, 63.0)
    layout = pack(dp, load_items("items-KWL1N1T.yml"), height_u=8)
    gaps = dp.gaps_mm
    for pl in layout.placements:
        if pl.extend_left_mm:
            assert pl.x_u == 0, "only a column-A bin can reach the left wall"
            assert pl.extend_left_mm == pytest.approx(gaps["left"])
        if pl.extend_front_mm:
            assert pl.y_u == 0, "only a row-1 bin can reach the front"
            assert pl.extend_front_mm == pytest.approx(gaps["front"])


def test_the_whole_front_row_reaches_the_drawer_front():
    dp = plan(542.5, 328.5, 63.0)
    layout = pack(dp, load_items("items-KWL1N1T.yml"), height_u=8)
    front = [p for p in layout.placements if p.y_u == 0]
    assert front and all(p.extend_front_mm > 0 for p in front), (
        "a front-row bin was left short of the drawer front"
    )


def test_the_left_gap_is_left_alone_except_for_the_bbq_bin():
    """Only rows 6-7 close the left gap; rows 1-5 keep it, as directed."""
    dp = plan(542.5, 328.5, 63.0)
    layout = pack(dp, load_items("items-KWL1N1T.yml"), height_u=8)
    reaching = [p for p in layout.placements if p.extend_left_mm > 0]
    assert len(reaching) == 1
    assert reaching[0].item.name == "BBQ lighter"
