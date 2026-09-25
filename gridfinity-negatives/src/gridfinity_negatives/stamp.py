"""Engraving a location code into the underside of a bin.

Bins within a drawer are interchangeable by design -- that is the point of a
grid. The cost of that is that a bin which leaves the drawer has nothing
saying where it came from. A code on the underside fixes it without spending
any of the bin's usable volume or its visible faces.

Engraved, never embossed. The underside is the first layer, printed against
the build plate: raised text there would have to be printed in mid-air.
Recessed text is simply an absence in the first few layers, which prints
cleanly and needs no supports.
"""

from __future__ import annotations

import cadquery as cq

DEFAULT_FONT = "DejaVu Sans Mono"
"""Monospace, so codes line up and 1/I and 0/O stay distinguishable."""

DEFAULT_DEPTH_MM = 0.6
"""Three layers at 0.2mm. Deep enough to read and to catch a pencil rub,
shallow enough not to matter structurally."""

PAD_MARGIN_MM = 3.0
"""Kept clear around the text, inside the 35.6mm underside pad."""


def bottom_pads(body: cq.Workplane) -> list[tuple[float, float, float, float]]:
    """Find the flat pads on the underside, one per grid unit.

    Returns (centre_x, centre_y, width, height) per pad, ordered front-left
    first so the code always lands in the same relative place.
    """
    shape = cq.Shape.cast(body.vals()[0].wrapped)
    pads = []
    for f in shape.Faces():
        if f.normalAt().z < -0.99 and f.Center().z < 0.01:
            bb = f.BoundingBox()
            pads.append((f.Center().x, f.Center().y, bb.xlen, bb.ylen))
    return sorted(pads, key=lambda p: (p[1], p[0]))


def _sized_text(
    code: str, depth: float, max_w: float, max_h: float, font: str
) -> tuple[cq.Workplane, float]:
    """Build the text solid, scaled to fit the pad.

    Measured rather than calculated from font metrics: the advance width of a
    'monospace' face is not reliably what the name implies, and a code running
    off the edge of the pad would be unreadable and unfixable after printing.
    """
    nominal = 10.0
    probe = cq.Workplane("XY").text(
        code, nominal, depth, font=font, halign="center", valign="center"
    )
    bb = probe.vals()[0].BoundingBox()
    scale = min(max_w / bb.xlen, max_h / bb.ylen, 1.0) * nominal
    size = min(scale, 8.0)
    if abs(size - nominal) < 1e-9:
        return probe, size
    return (
        cq.Workplane("XY").text(
            code, size, depth, font=font, halign="center", valign="center"
        ),
        size,
    )


def engrave_code(
    body: cq.Workplane,
    code: str,
    *,
    depth: float = DEFAULT_DEPTH_MM,
    font: str = DEFAULT_FONT,
    pad_index: int = 0,
) -> tuple[cq.Workplane, float]:
    """Cut ``code`` into the underside of ``body``.

    Returns the modified body and the text height actually used.

    The text is mirrored in X. Cut into a downward-facing surface, unmirrored
    text reads correctly only from inside the part; the person reading it has
    the bin turned over in their hand, looking at that face from below.
    """
    code = code.strip()
    if not code:
        raise ValueError("Cannot engrave an empty code.")

    pads = bottom_pads(body)
    if not pads:
        raise ValueError(
            "No flat underside found to engrave. A lite-style or vase-mode bin "
            "may not have one."
        )
    cx, cy, pw, ph = pads[min(pad_index, len(pads) - 1)]

    text, size = _sized_text(
        code, depth, pw - 2 * PAD_MARGIN_MM, ph - 2 * PAD_MARGIN_MM, font
    )
    # Mirror so it reads the right way round when the bin is turned over.
    mirrored = text.mirror("YZ")
    cutter = mirrored.translate((cx, cy, 0))
    return body.cut(cutter), size
