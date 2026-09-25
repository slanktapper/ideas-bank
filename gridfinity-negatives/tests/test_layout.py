"""Packing measured items into a drawer."""
import pytest

from gridfinity_negatives.drawer import plan
from gridfinity_negatives.layout import Item, load_items, pack

KWL1N1T = plan(533.0, 328.0, 63.0)   # 12 x 7 units


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


def test_the_drawer_is_over_capacity_with_the_keychains_added():
    """84 units available, ~89 wanted. Recorded so the shortfall is tracked."""
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"))
    shortfall = sum(i.footprint_units()[0] * i.footprint_units()[1]
                    for i in layout.unplaced)
    assert shortfall > 0, "expected an overflow; the item list may have changed"
    assert layout.used_units + shortfall > KWL1N1T.total_units


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
    """The real drawer is over capacity; that must be visible, not silent."""
    items = load_items("items-KWL1N1T.yml")
    layout = pack(KWL1N1T, items)
    assert layout.unplaced, "overflow vanished -- check the item list"
    assert layout.used_units <= KWL1N1T.total_units
