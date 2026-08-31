"""Generate a synthetic 'flatbed scan' of a combination spanner.

Stands in for a real scan so the pipeline can be exercised without a scanner.
Nominal length 152mm -- near enough a 13mm combination spanner.
"""
import cv2
import numpy as np

DPI = 400
PPM = DPI / 25.4


def spanner(length_mm=152.0, ring_od=26.0, open_w=19.0, shaft=9.5):
    canvas = np.full((int(210 * PPM), int(297 * PPM), 3), 242, np.uint8)
    cy = canvas.shape[0] // 2
    x0 = int((canvas.shape[1] - length_mm * PPM) / 2)

    def px(mm):
        return int(round(mm * PPM))

    # Shaft, tapered slightly toward the ring end.
    shaft_pts = np.array([
        [x0 + px(18), cy - px(shaft / 2)],
        [x0 + px(length_mm - 20), cy - px(shaft / 2 * 1.25)],
        [x0 + px(length_mm - 20), cy + px(shaft / 2 * 1.25)],
        [x0 + px(18), cy + px(shaft / 2)],
    ], np.int32)
    cv2.fillPoly(canvas, [shaft_pts], (28, 28, 28))

    # Ring end.
    cv2.circle(canvas, (x0 + px(length_mm - 15), cy), px(ring_od / 2), (28, 28, 28), -1)
    # Open end: a head with a slot cut out of it.
    cv2.ellipse(canvas, (x0 + px(15), cy), (px(15), px(open_w / 2)),
                0, 0, 360, (28, 28, 28), -1)
    cv2.rectangle(canvas, (x0 - px(2), cy - px(6.5)),
                  (x0 + px(13), cy + px(6.5)), (242, 242, 242), -1)
    return canvas


if __name__ == "__main__":
    img = spanner()
    cv2.imwrite("examples/spanner-scan.png", img)
    from PIL import Image
    im = Image.open("examples/spanner-scan.png")
    im.save("examples/spanner-scan.png", dpi=(DPI, DPI))
    print(f"examples/spanner-scan.png written at {DPI} dpi")
