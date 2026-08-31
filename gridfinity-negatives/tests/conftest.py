import numpy as np
import cv2
import pytest


def synthetic_tool(width_mm, height_mm, dpi, canvas_mm=(210, 297)):
    """A dark 'tool' of exact known size on a light background, as a scan would see it."""
    ppm = dpi / 25.4
    W = int(canvas_mm[0] * ppm)
    H = int(canvas_mm[1] * ppm)
    img = np.full((H, W, 3), 245, np.uint8)
    w = int(round(width_mm * ppm))
    h = int(round(height_mm * ppm))
    x0 = (W - w) // 2
    y0 = (H - h) // 2
    cv2.rectangle(img, (x0, y0), (x0 + w - 1, y0 + h - 1), (30, 30, 30), -1)
    return img


@pytest.fixture
def scan_factory(tmp_path):
    def make(width_mm=120.0, height_mm=28.0, dpi=300, name="tool.png"):
        img = synthetic_tool(width_mm, height_mm, dpi)
        path = tmp_path / name
        cv2.imwrite(str(path), img)
        return path, dpi
    return make
