"""A photo taken at an angle must still measure correctly.

The whole point of the mat is that scale survives perspective. If it does
not, every dimension downstream is wrong and nothing warns you.
"""
import cv2
import numpy as np
import pytest

from gridfinity_negatives.calibrate import Mat, render_mat, rectify
from gridfinity_negatives.trace import trace_photo


def _photo_of_mat(tmp_path, tool_mm=(90.0, 26.0), skew=True, dpi=200):
    """Render the mat, lay a synthetic tool on it, then warp it like a camera would."""
    mat = Mat()
    page = render_mat(mat, dpi)
    page = cv2.cvtColor(page, cv2.COLOR_GRAY2BGR)
    ppm = dpi / 25.4

    H, W = page.shape[:2]
    tw, th = int(tool_mm[0] * ppm), int(tool_mm[1] * ppm)
    x0, y0 = (W - tw) // 2, (H - th) // 2
    cv2.rectangle(page, (x0, y0), (x0 + tw - 1, y0 + th - 1), (25, 25, 25), -1)

    if skew:
        src = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
        dst = np.float32([[W * 0.06, H * 0.03], [W * 0.97, H * 0.10],
                          [W * 0.91, H * 0.96], [W * 0.02, H * 0.88]])
        page = cv2.warpPerspective(page, cv2.getPerspectiveTransform(src, dst), (W, H),
                                   borderValue=(255, 255, 255))
    p = tmp_path / "photo.png"
    cv2.imwrite(str(p), page)
    return p, mat


def test_markers_survive_render_and_detect(tmp_path):
    p, mat = _photo_of_mat(tmp_path, skew=False)
    img = cv2.imread(str(p))
    flat = rectify(img, mat, 8.0)
    assert flat.shape[0] == pytest.approx(mat.height_mm * 8.0, abs=2)
    assert flat.shape[1] == pytest.approx(mat.width_mm * 8.0, abs=2)


@pytest.mark.parametrize("tool", [(90.0, 26.0), (130.0, 55.0)])
def test_skewed_photo_recovers_true_size(tmp_path, tool):
    p, _ = _photo_of_mat(tmp_path, tool_mm=tool, skew=True)
    tr = trace_photo(p)
    w, h = tr.size_mm
    # A perspective round trip through resampling; 1.5mm is honest tolerance.
    assert w == pytest.approx(tool[0], abs=1.5), f"width {w:.2f} vs {tool[0]}"
    assert h == pytest.approx(tool[1], abs=1.5), f"height {h:.2f} vs {tool[1]}"


def test_missing_markers_refuses_rather_than_guesses(tmp_path):
    blank = np.full((800, 600, 3), 250, np.uint8)
    p = tmp_path / "nomarkers.png"
    cv2.imwrite(str(p), blank)
    with pytest.raises(LookupError, match="markers"):
        trace_photo(p)


def test_oversized_tool_refuses_rather_than_clipping(tmp_path):
    """A tool bigger than the mat must error, not return a too-small trace."""
    p, _ = _photo_of_mat(tmp_path, tool_mm=(190.0, 60.0), skew=False)
    with pytest.raises(ValueError, match="past the mat"):
        trace_photo(p)


def test_usable_area_is_reported_honestly():
    mat = Mat()
    uw, uh = mat.usable_area_mm()
    assert uw == pytest.approx(mat.width_mm - 2 * (mat.margin_mm + mat.marker_mm))
    assert uh == pytest.approx(mat.height_mm - 2 * (mat.margin_mm + mat.marker_mm))
