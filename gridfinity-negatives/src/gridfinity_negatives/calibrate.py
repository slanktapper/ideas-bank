"""The printable calibration mat, and using it to un-warp a phone photo.

A flatbed scan needs none of this: the scanner already knows its own DPI and
looks straight down. A photo knows neither, so we give it four fiducials at
known positions and solve for the transform between them.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_IDS = (0, 1, 2, 3)  # top-left, top-right, bottom-right, bottom-left


@dataclass(frozen=True)
class Mat:
    """A printable calibration mat.

    ``width_mm`` / ``height_mm`` are the mat's overall size. Markers sit with
    their outer corners inset by ``margin_mm`` from the mat edge, so the
    distance between opposing marker outer corners is a known quantity and
    that is what fixes the scale.
    """

    width_mm: float = 210.0   # A4 portrait
    height_mm: float = 297.0
    margin_mm: float = 8.0
    marker_mm: float = 25.0

    @property
    def corners_mm(self) -> np.ndarray:
        """Outer corner of each marker, in mat coordinates, in marker order.

        Origin is the mat's top-left, +x right, +y down -- image convention,
        converted to CAD convention later.
        """
        m, s = self.margin_mm, self.marker_mm
        w, h = self.width_mm, self.height_mm
        return np.array(
            [
                [m, m],                  # id 0 top-left, its top-left corner
                [w - m, m],              # id 1 top-right, its top-right corner
                [w - m, h - m],          # id 2 bottom-right corner
                [m, h - m],              # id 3 bottom-left corner
            ],
            dtype=np.float32,
        )

    def usable_area_mm(self) -> tuple[float, float]:
        """Space between the markers, where the tool should be placed."""
        return (
            self.width_mm - 2 * (self.margin_mm + self.marker_mm),
            self.height_mm - 2 * (self.margin_mm + self.marker_mm),
        )


def render_mat(mat: Mat, dpi: int = 300) -> np.ndarray:
    """Draw the mat as a printable image.

    Print this at 100% scale -- "fit to page" will silently rescale it and
    every measurement taken from it will be wrong by that factor.
    """
    px_per_mm = dpi / 25.4
    w = int(round(mat.width_mm * px_per_mm))
    h = int(round(mat.height_mm * px_per_mm))
    canvas = np.full((h, w), 255, dtype=np.uint8)

    d = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    side = int(round(mat.marker_mm * px_per_mm))
    m = int(round(mat.margin_mm * px_per_mm))

    placements = {
        0: (m, m),
        1: (w - m - side, m),
        2: (w - m - side, h - m - side),
        3: (m, h - m - side),
    }
    for mid, (x, y) in placements.items():
        img = cv2.aruco.generateImageMarker(d, mid, side)
        canvas[y : y + side, x : x + side] = img

    # A scale bar, so a mis-scaled printout is obvious to the eye.
    bar_y = h - int(round((mat.margin_mm + mat.marker_mm + 8) * px_per_mm))
    x0 = int(round((mat.margin_mm + mat.marker_mm + 5) * px_per_mm))
    for i in range(11):
        x = x0 + int(round(i * 10 * px_per_mm))
        tall = int(round((4 if i % 5 == 0 else 2.5) * px_per_mm))
        cv2.line(canvas, (x, bar_y), (x, bar_y - tall), 0, max(1, int(px_per_mm / 3)))
    cv2.line(canvas, (x0, bar_y), (x0 + int(round(100 * px_per_mm)), bar_y), 0,
             max(1, int(px_per_mm / 3)))
    cv2.putText(canvas, "100 mm - measure me before use", (x0, bar_y + int(6 * px_per_mm)),
                cv2.FONT_HERSHEY_SIMPLEX, px_per_mm / 9, 0, max(1, int(px_per_mm / 4)),
                cv2.LINE_AA)
    return canvas


def rectify(image: np.ndarray, mat: Mat, px_per_mm: float) -> np.ndarray:
    """Flatten a photo of the mat into a square-on, metric-scaled image.

    Returns an image where one pixel is exactly ``1 / px_per_mm`` mm in both
    axes, covering the whole mat.

    Raises ``LookupError`` if the four markers are not all visible -- better
    to say so than to hand back a silently wrong scale.
    """
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(ARUCO_DICT), cv2.aruco.DetectorParameters()
    )
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        raise LookupError(
            "No calibration markers found. Is the whole mat in frame, in focus, "
            "and reasonably lit?"
        )
    found = {int(i) for i in ids.flatten()}
    missing = sorted(set(MARKER_IDS) - found)
    if missing:
        raise LookupError(
            f"Calibration markers {missing} not visible -- all four are needed. "
            f"Found {sorted(found)}."
        )

    by_id = {int(i): c.reshape(4, 2) for i, c in zip(ids.flatten(), corners)}
    # detectMarkers returns corners clockwise from the marker's top-left, so
    # for marker n the outer corner of the mat is its own corner n.
    src = np.array([by_id[mid][idx] for idx, mid in enumerate(MARKER_IDS)],
                   dtype=np.float32)
    dst = (mat.corners_mm * px_per_mm).astype(np.float32)

    h = cv2.getPerspectiveTransform(src, dst)
    size = (int(round(mat.width_mm * px_per_mm)), int(round(mat.height_mm * px_per_mm)))
    return cv2.warpPerspective(image, h, size, flags=cv2.INTER_CUBIC)
