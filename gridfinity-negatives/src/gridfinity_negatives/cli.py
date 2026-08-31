"""Command line front end."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from .calibrate import Mat, render_mat
from .config import DEFAULTS, MAX_UNITS_ON_BED, Tuning
from .geometry import pocket_profile, straighten
from .model import BedTooSmall, BinSpec, PocketTooDeep, auto_spec, build, export
from .preview import render
from .trace import Trace, trace_photo, trace_scan


def _tuning(a: argparse.Namespace) -> Tuning:
    return Tuning(
        clearance_mm=a.clearance,
        simplify_mm=DEFAULTS.simplify_mm,
        floor_mm=DEFAULTS.floor_mm,
        wall_mm=a.wall,
        relief_radius_mm=a.relief_radius,
        min_feature_mm2=a.min_feature,
        photo_px_per_mm=DEFAULTS.photo_px_per_mm,
    )


def _do_trace(a: argparse.Namespace, t: Tuning) -> Trace:
    if a.photo:
        return trace_photo(a.image, Mat(), t)
    return trace_scan(a.image, a.dpi, t)


def cmd_mat(a: argparse.Namespace) -> int:
    mat = Mat()
    img = render_mat(mat, a.dpi)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), img)
    uw, uh = mat.usable_area_mm()
    print(f"Calibration mat written to {out}")
    print(f"  Mat {mat.width_mm:.0f} x {mat.height_mm:.0f} mm at {a.dpi} dpi")
    print(f"  Usable area between markers: {uw:.0f} x {uh:.0f} mm")
    print()
    print("  Print at 100% scale -- NOT 'fit to page'. Then measure the printed")
    print("  scale bar: if it is not exactly 100 mm, reprint. Every dimension")
    print("  derived from a photo inherits this error directly.")
    return 0


def cmd_trace(a: argparse.Namespace) -> int:
    t = _tuning(a)
    tr = _do_trace(a, t)
    w, h = tr.size_mm
    print(f"Source     : {tr.source}")
    print(f"Scale      : {tr.px_per_mm:.3f} px/mm")
    print(f"Tool bounds: {w:.1f} x {h:.1f} mm")
    print(f"Tool area  : {tr.outline.area:.0f} mm^2")
    if tr.extra:
        print(f"Also found : {len(tr.extra)} smaller shape(s), largest "
              f"{tr.extra[0].area:.0f} mm^2 -- raise --min-feature to ignore")
    pocket = pocket_profile(tr.outline, t, relief=a.relief)
    spec = auto_spec(pocket, a.depth, t)
    print(f"Would build: {spec.describe()}")
    return 0


def cmd_build(a: argparse.Namespace) -> int:
    t = _tuning(a)
    tr = _do_trace(a, t)
    outline = tr.outline

    if not a.no_straighten:
        outline, angle = straighten(outline)
        if abs(angle) > 0.05:
            print(f"Straightened trace by {angle:+.1f} deg")

    pocket = pocket_profile(outline, t, relief=a.relief)

    if a.size:
        try:
            lu, wu = (int(v) for v in a.size.lower().split("x"))
        except ValueError:
            print(f"error: --size wants LxW, e.g. 2x3 (got {a.size!r})", file=sys.stderr)
            return 2
        from .geometry import height_units_for

        spec = BinSpec(lu, wu, a.height or height_units_for(a.depth), a.depth,
                       magnet_holes=a.magnets, keep_lip=not a.no_lip,
                       label_shelf=a.label)
    else:
        spec = auto_spec(pocket, a.depth, t, magnet_holes=a.magnets,
                         keep_lip=not a.no_lip, label_shelf=a.label)
        if a.height:
            spec.height_u = a.height

    w, h = tr.size_mm
    print(f"Traced {w:.1f} x {h:.1f} mm from {tr.source}")
    print(f"Building {spec.describe()}")

    try:
        result = build(pocket, spec, t)
    except (BedTooSmall, PocketTooDeep) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for warning in result.warnings:
        print(f"warning: {warning}")

    stem = a.name or Path(a.image).stem
    paths = export(result, stem, a.out)
    for p in paths:
        print(f"wrote {p}")

    if not a.no_preview:
        png = str(Path(a.out) / f"{stem}-preview.png")
        render(outline, result.pocket, spec, png,
               title=f"{stem}: {spec.describe()}")
        print(f"wrote {png}")

    print()
    print("Print one before committing to a set: check the tool actually drops "
          "in, and that the base seats in a baseplate.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="gfneg",
        description="Turn a scan or photo of a tool into a Gridfinity bin "
                    "with the tool's negative cut into it.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mat", help="generate the printable calibration mat")
    m.add_argument("--out", default="calibration-mat.png")
    m.add_argument("--dpi", type=int, default=300)
    m.set_defaults(func=cmd_mat)

    def common(sp):
        sp.add_argument("image")
        sp.add_argument("--photo", action="store_true",
                        help="image is a phone photo on the calibration mat, "
                             "not a flatbed scan")
        sp.add_argument("--dpi", type=float, default=None,
                        help="scan resolution, if the file does not record it")
        sp.add_argument("--depth", type=float, default=12.0,
                        help="pocket depth in mm (default: 12)")
        sp.add_argument("--clearance", type=float, default=DEFAULTS.clearance_mm,
                        help=f"gap around the tool in mm "
                             f"(default: {DEFAULTS.clearance_mm})")
        sp.add_argument("--wall", type=float, default=DEFAULTS.wall_mm,
                        help="minimum material to the bin wall in mm")
        sp.add_argument("--relief", action="store_true",
                        help="add a finger scallop so the tool can be lifted out")
        sp.add_argument("--relief-radius", type=float,
                        default=DEFAULTS.relief_radius_mm)
        sp.add_argument("--min-feature", type=float,
                        default=DEFAULTS.min_feature_mm2,
                        help="ignore traced blobs smaller than this, in mm^2")

    t = sub.add_parser("trace", help="trace and report, without building CAD")
    common(t)
    t.set_defaults(func=cmd_trace)

    b = sub.add_parser("build", help="trace, cut the pocket, export STL and STEP")
    common(b)
    b.add_argument("--size", help="force bin size in units, e.g. 2x3")
    b.add_argument("--height", type=int, help="force height in units")
    b.add_argument("--magnets", action="store_true",
                   help="add 6x2mm magnet holes, printable without supports")
    b.add_argument("--label", action="store_true", help="add a label shelf")
    b.add_argument("--no-lip", action="store_true",
                   help="drop the stacking lip profile")
    b.add_argument("--no-straighten", action="store_true",
                   help="do not auto-rotate the trace square to the grid")
    b.add_argument("--no-preview", action="store_true")
    b.add_argument("--name", help="output filename stem")
    b.add_argument("--out", default="out", help="output directory")
    b.set_defaults(func=cmd_build)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
