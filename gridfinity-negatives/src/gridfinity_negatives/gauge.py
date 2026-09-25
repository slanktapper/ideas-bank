"""Gap gauges: printed feeler sticks for measuring what a tape cannot.

A drawer's usable width is rarely the number on a spec sheet, and the gap
left over by the 42 mm pitch is what decides whether spacers fit. Measuring a
14 mm gap at the back of a loaded drawer with a tape is guesswork.

So: a set of sticks at known lengths. The foot butts flat against the
baseplate's outer edge, the arm reaches across the gap. The longest one that
still drops in is the gap, to the nearest millimetre, with no measuring at all.

    ┌────────────────────────┐  ← foot, butts against the baseplate edge
    │          ██            │
    │          ██            │
               ██               ← arm, length is the measurement
               ██
               ██
               ▼ tip touches the drawer wall

Read from the datum face -- the foot's contact face -- to the arm tip. The
foot's own depth is inside that length, not added to it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

import yaml

from .stamp import DEFAULT_FONT

STANDARD_DELTAS: tuple[float, ...] = (-3.0, -2.0, -1.0, 0.0, 1.0)
"""The standard ladder, as offsets from nominal.

Weighted below nominal on purpose. A gauge longer than the gap will not go in
at all and tells you only "smaller than this", while a shorter one goes in and
tells you how much slack is left. Errors in a recorded drawer dimension also
tend to run generous, so the true gap is more often under nominal than over.
One step above is enough to confirm the upper bound."""

LIBRARY_FILE = "gauge-library.yml"
"""Lengths that physically exist. Gauges are reusable across drawers -- a
14.5 mm stick does not care which drawer it came from -- so the library is
consulted before anything is printed again."""


@dataclass(frozen=True)
class GaugeSpec:
    """Proportions of a gap gauge. Small: these are consumables."""

    thickness_mm: float = 3.0
    """Lies flat on the drawer floor, well under the baseplate's 4.75 mm, so
    the foot meets the vertical part of the edge rather than a chamfer."""
    arm_width_mm: float = 6.0
    foot_length_mm: float = 26.0
    foot_depth_mm: float = 5.0
    """How far the foot reaches into the gap. Inside the measured length."""
    text_depth_mm: float = 0.5
    min_length_mm: float = 6.0


DEFAULT_GAUGE = GaugeSpec()


def make_gauge(
    length_mm: float, spec: GaugeSpec = DEFAULT_GAUGE, label: str | None = None
) -> cq.Workplane:
    """One gauge stick of the given length, labelled underneath.

    ``length_mm`` is measured from the datum face to the arm tip -- the whole
    point of the tool, so it is the part's extent in Y and nothing is added to
    it.
    """
    if length_mm < spec.min_length_mm:
        raise ValueError(
            f"{length_mm} mm is shorter than the {spec.foot_depth_mm} mm foot "
            "plus a usable arm; a gauge this short would not register."
        )
    if length_mm <= spec.foot_depth_mm:
        raise ValueError(
            f"{length_mm} mm does not clear the {spec.foot_depth_mm} mm foot."
        )

    # Datum face on y = 0; everything grows in +y, into the gap.
    foot = (
        cq.Workplane("XY")
        .box(spec.foot_length_mm, spec.foot_depth_mm, spec.thickness_mm,
             centered=(True, False, False))
    )
    arm = (
        cq.Workplane("XY")
        .box(spec.arm_width_mm, length_mm, spec.thickness_mm,
             centered=(True, False, False))
    )
    body = foot.union(arm)

    text = label if label is not None else _format_length(length_mm)
    return _engrave_underside(body, text, spec)


def _format_length(length_mm: float) -> str:
    return f"{length_mm:g}"


def _engrave_underside(
    body: cq.Workplane, text: str, spec: GaugeSpec
) -> cq.Workplane:
    """Cut the length into the bottom face, mirrored so it reads turned over.

    On the foot, which is the only part wide enough to hold it.
    """
    max_w = spec.foot_length_mm - 4.0
    max_h = spec.foot_depth_mm - 1.2

    nominal = 10.0
    probe = cq.Workplane("XY").text(
        text, nominal, spec.text_depth_mm, font=DEFAULT_FONT,
        halign="center", valign="center",
    )
    bb = probe.vals()[0].BoundingBox()
    size = min(max_w / bb.xlen, max_h / bb.ylen, 1.0) * nominal

    glyphs = cq.Workplane("XY").text(
        text, size, spec.text_depth_mm, font=DEFAULT_FONT,
        halign="center", valign="center",
    )
    cutter = glyphs.mirror("YZ").translate((0.0, spec.foot_depth_mm / 2.0, 0.0))
    return body.cut(cutter)


def gauge_set(
    exact_mm: float,
    deltas: tuple[float, ...] = STANDARD_DELTAS,
    spec: GaugeSpec = DEFAULT_GAUGE,
) -> list[tuple[float, cq.Workplane]]:
    """A ladder of gauges around a nominal gap."""
    out = []
    for d in deltas:
        length = round(exact_mm + d, 3)
        out.append((length, make_gauge(length, spec)))
    return out


def export_set(
    exact_mm: float, out_dir: str, prefix: str,
    deltas: tuple[float, ...] = STANDARD_DELTAS,
    spec: GaugeSpec = DEFAULT_GAUGE,
    only: set[float] | None = None,
) -> list[str]:
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    paths = []
    for length, body in gauge_set(exact_mm, deltas, spec):
        if only is not None and length not in only:
            continue
        p = d / f"{prefix}-{_format_length(length).replace('.', 'p')}mm.stl"
        cq.exporters.export(body, str(p))
        paths.append(str(p))
    return paths


# --- the physical library --------------------------------------------------

def ladder(exact_mm: float,
           deltas: tuple[float, ...] = STANDARD_DELTAS) -> list[float]:
    """The lengths a nominal gap calls for."""
    return [round(exact_mm + d, 3) for d in deltas]


def load_library(path: str | Path = LIBRARY_FILE) -> dict[float, str]:
    """Lengths already printed, mapped to a note about where they came from."""
    f = Path(path)
    if not f.exists():
        return {}
    data = yaml.safe_load(f.read_text()) or {}
    out: dict[float, str] = {}
    for row in data.get("gauges", []):
        if isinstance(row, dict):
            out[float(row["length"])] = str(row.get("note", ""))
        else:
            out[float(row)] = ""
    return out


def save_library(lib: dict[float, str], path: str | Path = LIBRARY_FILE) -> None:
    rows = [{"length": L, "note": lib[L]} for L in sorted(lib)]
    header = (
        "# Gap gauges that physically exist.\n"
        "# A gauge is just a length -- it is reusable across every drawer, so\n"
        "# check here before printing. Managed by `gfneg gauge`.\n"
    )
    Path(path).write_text(header + yaml.safe_dump({"gauges": rows},
                                                  sort_keys=False))


def check_ladder(exact_mm: float, path: str | Path = LIBRARY_FILE,
                 deltas: tuple[float, ...] = STANDARD_DELTAS
                 ) -> tuple[list[float], list[float]]:
    """Split a ladder into what is already owned and what must be printed."""
    lib = load_library(path)
    want = ladder(exact_mm, deltas)
    have = [L for L in want if L in lib]
    need = [L for L in want if L not in lib]
    return have, need
