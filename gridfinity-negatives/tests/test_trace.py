"""The scale must survive the round trip. Everything else is decoration."""
import pytest
from gridfinity_negatives.trace import trace_scan


@pytest.mark.parametrize("w,h,dpi", [
    (120.0, 28.0, 300),
    (60.0, 60.0, 600),
    (33.5, 14.2, 400),
])
def test_traced_size_matches_reality(scan_factory, w, h, dpi):
    path, actual_dpi = scan_factory(w, h, dpi)
    tr = trace_scan(path, dpi=actual_dpi)
    tw, th = tr.size_mm
    # One pixel of tolerance at the scan resolution, plus a little for
    # the morphological clean-up.
    tol = 3 * 25.4 / dpi + 0.15
    assert tw == pytest.approx(w, abs=tol), f"width {tw} vs {w}"
    assert th == pytest.approx(h, abs=tol), f"height {th} vs {h}"


def test_missing_dpi_is_an_error_not_a_guess(scan_factory):
    path, _ = scan_factory()
    import cv2
    img = cv2.imread(str(path))
    stripped = path.parent / "nodpi.jpg"
    cv2.imwrite(str(stripped), img)
    with pytest.raises(ValueError, match="scanning resolution"):
        trace_scan(stripped, dpi=None)


def test_blank_scan_reports_clearly(tmp_path):
    import numpy as np, cv2
    blank = np.full((600, 600, 3), 245, np.uint8)
    p = tmp_path / "blank.png"
    cv2.imwrite(str(p), blank)
    with pytest.raises(ValueError, match="Nothing found"):
        trace_scan(p, dpi=300)
