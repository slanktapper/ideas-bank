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


def test_the_real_drawer_contents_fit():
    layout = pack(KWL1N1T, load_items("items-KWL1N1T.yml"))
    assert not layout.unplaced, [i.name for i in layout.unplaced]
    assert layout.used_units <= KWL1N1T.total_units
    assert layout.free_units >= 0


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
