"""Image in, tool outline out.

Two front doors -- ``trace_scan`` for a flatbed scan and ``trace_photo`` for a
phone photo on the calibration mat -- which converge on the same contour
extraction as soon as the image has a known, uniform millimetre scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from shapely.geometry import Polygon

from .calibrate import Mat, rectify
from .config import DEFAULTS, Tuning
from .geometry import polygons_from_contours

BACKGROUND_AREA_FRACTION = 0.85
"""A traced blob larger than this share of the frame is the background."""


@dataclass
class Trace:
    """A traced outline and how it was obtained."""

    outline: Polygon
    px_per_mm: float
    source: str
    extra: list[Polygon]
    """Other blobs found, largest first. Usually specks; occasionally a
    second tool, which is why they are kept rather than dropped."""

    @property
    def size_mm(self) -> tuple[float, float]:
        minx, miny, maxx, maxy = self.outline.bounds
        return (maxx - minx, maxy - miny)


def read_dpi(path: str | Path) -> float | None:
    """Pull the scanning resolution out of the file, if it recorded one."""
    try:
        from PIL import Image

        with Image.open(path) as im:
            dpi = im.info.get("dpi")
    except Exception:
        return None
    if not dpi:
        return None
    x = float(dpi[0])
    # Some scanners write a nonsense 1 or 72; treat those as absent.
    return x if x > 100 else None


def _binarise(gray: np.ndarray) -> np.ndarray:
    """Separate tool from background, working out the polarity ourselves.

    The border of the image is assumed to be background -- true for a tool
    laid in the middle of a platen or a mat.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    border = np.concatenate(
        [blurred[0, :], blurred[-1, :], blurred[:, 0], blurred[:, -1]]
    )
    h, w = blurred.shape
    centre = blurred[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]

    dark_on_light = float(border.mean()) > float(centre.mean())
    flag = cv2.THRESH_BINARY_INV if dark_on_light else cv2.THRESH_BINARY
    _, mask = cv2.threshold(blurred, 0, 255, flag | cv2.THRESH_OTSU)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def _contours_to_mm(
    mask: np.ndarray, px_per_mm: float, tuning: Tuning
) -> list[Polygon]:
    """Find outlines and convert pixel coordinates to CAD millimetres.

    ``RETR_EXTERNAL`` deliberately ignores holes inside a tool: the ring of a
    spanner becomes solid pocket floor rather than a thin pillar that would
    snap off.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height_px, width_px = mask.shape[:2]
    rings = []
    for c in contours:
        pts = c.reshape(-1, 2).astype(float)
        # Image y runs down the page; CAD y runs up it.
        xy = np.column_stack([pts[:, 0] / px_per_mm,
                              (height_px - pts[:, 1]) / px_per_mm])
        rings.append(xy)
    polys = polygons_from_contours(rings, tuning.min_feature_mm2)

    # A featureless image thresholds into one blob covering everything. That
    # is the background, not a tool, and building a bin from it would produce
    # something enormous and silently wrong.
    frame_mm2 = (height_px / px_per_mm) * (width_px / px_per_mm)
    return [p for p in polys if p.area < BACKGROUND_AREA_FRACTION * frame_mm2]


def trace_scan(
    path: str | Path, dpi: float | None = None, tuning: Tuning = DEFAULTS
) -> Trace:
    """Trace a flatbed scan, where scale comes straight from the DPI."""
    path = Path(path)
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    resolved = dpi or read_dpi(path)
    if not resolved:
        raise ValueError(
            f"{path.name} does not record a scanning resolution, so its scale is "
            "unknown. Pass --dpi with the value you scanned at."
        )
    px_per_mm = resolved / 25.4

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    polys = _contours_to_mm(_binarise(gray), px_per_mm, tuning)
    if not polys:
        raise ValueError(
            "Nothing found in the scan. Check the tool contrasts with the "
            "background -- a dark tool on a closed white lid works best."
        )
    return Trace(polys[0], px_per_mm, f"scan @ {resolved:g} dpi", polys[1:])


def trace_photo(
    path: str | Path, mat: Mat | None = None, tuning: Tuning = DEFAULTS
) -> Trace:
    """Trace a photo of a tool sitting on the printed calibration mat."""
    path = Path(path)
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    mat = mat or Mat()
    px_per_mm = tuning.photo_px_per_mm
    flat = rectify(image, mat, px_per_mm)

    # Crop inside the markers so the fiducials are not traced as tools.
    inset = int(round((mat.margin_mm + mat.marker_mm + 2.0) * px_per_mm))
    cropped = flat[inset:-inset, inset:-inset]
    if cropped.size == 0:
        raise ValueError("Calibration mat is too small for its own markers.")

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    polys = _contours_to_mm(_binarise(gray), px_per_mm, tuning)
    if not polys:
        raise ValueError(
            "Nothing found between the markers. Put the tool inside the mat's "
            "inner area, and avoid shadows across it."
        )

    _reject_if_clipped(polys[0], cropped.shape, px_per_mm, mat)
    return Trace(polys[0], px_per_mm, "photo on calibration mat", polys[1:])


def _reject_if_clipped(
    poly: Polygon, shape: tuple[int, ...], px_per_mm: float, mat: Mat
) -> None:
    """Refuse a tool that runs past the mat's usable area.

    A tool larger than the space between the markers gets cut off by the crop,
    and the trace then reports the crop's size with total confidence. Silently
    returning a shape that is too short is the worst outcome available, so
    this is an error rather than a warning.
    """
    edge_mm = 1.0
    frame_w = shape[1] / px_per_mm
    frame_h = shape[0] / px_per_mm
    minx, miny, maxx, maxy = poly.bounds
    if (
        minx <= edge_mm
        or miny <= edge_mm
        or maxx >= frame_w - edge_mm
        or maxy >= frame_h - edge_mm
    ):
        uw, uh = mat.usable_area_mm()
        raise ValueError(
            f"The tool runs past the mat's usable area ({uw:.0f} x {uh:.0f} mm), "
            f"so the trace would be clipped and silently too small. Use a larger "
            f"mat, or scan the tool on a flatbed instead."
        )
