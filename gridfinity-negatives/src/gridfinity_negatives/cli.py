"""Command line front end."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
from cadquery import exporters as _exp


def cq_export(obj, path):
    _exp.export(obj, path)


from .calibrate import Mat, render_mat
from .config import DEFAULT_PRINTER, DEFAULTS, PRINTERS, Tuning
from .geometry import pocket_profile, straighten
from .codes import is_valid, parse as parse_code
from .drawer import build_baseplates, build_spacers, estimate_mass_g, plan as plan_drawer
from .model import BedTooSmall, BinSpec, PocketTooDeep, auto_spec, build, export
from .layout import load_items, pack
from .preview import render, render_drawer, render_layout
from .stamp import DEFAULT_DEPTH_MM, engrave_code
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
                       label_shelf=a.label, printer=PRINTERS[a.printer])
    else:
        spec = auto_spec(pocket, a.depth, t, magnet_holes=a.magnets,
                         keep_lip=not a.no_lip, label_shelf=a.label,
                         printer=PRINTERS[a.printer])
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

    if a.code:
        rc = _check_code(a.code)
        if rc:
            return rc
        result.body, csize = engrave_code(result.body, a.code)
        print(f"Engraved {a.code.upper()} underneath at {csize:.1f} mm")

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


def cmd_drawer(a: argparse.Namespace) -> int:
    printer = PRINTERS[a.printer]
    try:
        p = plan_drawer(a.width, a.depth, a.height, printer)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    dead = 100.0 * (1 - (p.units_x * 42.0 * p.units_y * 42.0)
                    / (p.drawer_w_mm * p.drawer_d_mm))
    print(f"Drawer   : {p.drawer_w_mm:.0f} x {p.drawer_d_mm:.0f} mm internal")
    print(f"Printer  : {printer.name} "
          f"({printer.max_units_x}x{printer.max_units_y} units per plate)")
    print(f"Grid     : {p.units_x} x {p.units_y} units "
          f"({p.units_x * 42 - 0.5:.1f} x {p.units_y * 42 - 0.5:.1f} mm), "
          f"{p.total_units} bin positions")
    print(f"Margins  : {p.margin_x_mm:.1f} mm each side, "
          f"{p.margin_y_mm:.1f} mm front and back ({dead:.0f}% of the floor unused)")
    print(f"Baseplate: {len(p.tiles)} tiles -- " + ", ".join(
        f"{q} x {lu}x{wu}" for (lu, wu), q in sorted(p.tile_counts.items(), reverse=True)))
    for n in p.notes:
        print(f"note     : {n}")

    if a.plan_only:
        return 0

    print()
    total = 0.0
    for path, qty, grams in build_baseplates(p, a.out, a.name, magnets=a.magnets):
        total += qty * grams
        print(f"wrote {path}  x{qty}  ~{grams:.0f} g each")
    sp = build_spacers(p, a.out, a.name)
    if sp:
        print(f"wrote {sp}")
    else:
        print(f"skipped spacers: margins under 4 mm are too fragile to print")
    print(f"baseplate filament: ~{total:.0f} g total (~${total / 1000 * 13.74:.2f} "
          f"in PETG Basic)")

    png = str(Path(a.out) / f"{a.name}-layout.png")
    render_drawer(p, png)
    print(f"wrote {png}")
    print()
    print("Measure twice. Print ONE tile and check it sits flat in the drawer "
          "before printing the rest.")
    return 0


def _check_code(code: str) -> int:
    """Echo a code back in words so a typo is caught before printing."""
    if code is None:
        return 0
    if not is_valid(code):
        print(f"error: {code!r} is not a valid location code.", file=sys.stderr)
        print("  Expected e.g. KWL1N1T -- room, wall, section, "
              "column number+direction, drawer number+T/B.", file=sys.stderr)
        return 2
    print(f"Code     : {code.upper()} = {parse_code(code).describe()}")
    return 0


def cmd_bin(a: argparse.Namespace) -> int:
    from cqgridfinity import GridfinityBox

    rc = _check_code(a.code)
    if rc:
        return rc

    try:
        lu, wu = (int(v) for v in a.size.lower().split("x"))
    except ValueError:
        print(f"error: --size wants LxW, e.g. 1x2 (got {a.size!r})", file=sys.stderr)
        return 2

    printer = PRINTERS[a.printer]
    if not printer.fits(lu, wu):
        print(f"error: {lu}x{wu} units is past the {printer.name}'s "
              f"{printer.max_units_x}x{printer.max_units_y}-unit bed.", file=sys.stderr)
        return 1

    box = GridfinityBox(
        lu, wu, a.height,
        holes=a.magnets, unsupported_holes=a.magnets,
        labels=a.label, scoops=a.scoop,
        length_div=a.length_div, width_div=a.width_div,
        no_lip=a.no_lip,
    )
    body = box.cq_obj
    if a.code:
        body, size = engrave_code(body, a.code, depth=a.code_depth)
        print(f"Engraved : {size:.1f} mm text, {a.code_depth} mm deep, "
              "underside, mirrored to read when turned over")

    grams = estimate_mass_g(body, infill=0.10)
    print(f"Bin      : {lu}x{wu}x{a.height}U "
          f"({lu * 42 - 0.5:.1f} x {wu * 42 - 0.5:.1f} x {a.height * 7 + 3.8:.1f} mm), "
          f"{box.max_height:.0f} mm usable depth")
    print(f"Filament : ~{grams:.0f} g each"
          + (f", ~{grams * a.count:.0f} g for {a.count}" if a.count > 1 else ""))

    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    stem = a.name or (f"{a.code.upper()}-" if a.code else "") + f"bin-{lu}x{wu}x{a.height}"
    path = d / f"{stem}.stl"
    cq_export(body, str(path))
    print(f"wrote {path}")
    if a.count > 1:
        print(f"  print {a.count} copies -- duplicate on the plate in the slicer")
    return 0


def cmd_layout(a: argparse.Namespace) -> int:
    rc = _check_code(a.code)
    if rc:
        return rc
    printer = PRINTERS[a.printer]
    try:
        p = plan_drawer(a.width, a.depth, a.height, printer)
        items = load_items(a.items)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not items:
        print("error: no items in the list", file=sys.stderr)
        return 1

    layout = pack(p, items, allow_rotation=not a.no_rotate)
    print(f"Drawer   : {p.drawer_w_mm:.0f} x {p.drawer_d_mm:.0f} mm, "
          f"{p.units_x} x {p.units_y} units, {p.total_units} positions")
    print(f"Placed   : {len(layout.placements)} bins, "
          f"{layout.used_units} units used, {layout.free_units} free")

    by_size: dict = {}
    for pl in layout.placements:
        key = (pl.length_u, pl.width_u, pl.item.height_units(), pl.item.name)
        by_size[key] = by_size.get(key, 0) + 1
    print()
    print(f"{'qty':>4}  {'bin':<10} {'height':<8} item")
    for (lu, wu, hu, name), qty in sorted(by_size.items(), key=lambda kv: -kv[1]):
        print(f"{qty:>4}  {lu}x{wu:<8} {hu}U{'':<5} {name}")

    unmeasured = {i.name for i in items if not i.measured}
    if unmeasured:
        print()
        print("warning: these sizes are PLACEHOLDERS, not measurements: "
              + ", ".join(sorted(unmeasured)))
        print("         do not print from this layout until they are measured.")
    if layout.unplaced:
        print()
        for i in layout.unplaced:
            lu, wu = i.footprint_units()
            print(f"unplaced: {i.name} needs {lu}x{wu} units -- no free block that size")

    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    png = str(d / f"{(a.code or 'drawer').upper()}-layout.png")
    render_layout(layout, png, code=(a.code or "").upper())
    print()
    print(f"wrote {png}")
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
        sp.add_argument("--printer", choices=sorted(PRINTERS), default="h2d",
                        help="machine whose bed limits the bin size")
        sp.add_argument("--code", help="location code to engrave underneath")
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

    d = sub.add_parser("drawer", help="plan a drawer and generate its baseplates")
    d.add_argument("--width", type=float, required=True,
                   help="internal clear width of the drawer in mm")
    d.add_argument("--depth", type=float, required=True,
                   help="internal clear depth of the drawer in mm")
    d.add_argument("--height", type=float, default=None,
                   help="internal clear height, to check bin headroom")
    d.add_argument("--printer", choices=sorted(PRINTERS), default="h2d")
    d.add_argument("--magnets", action="store_true",
                   help="add corner screw tabs to the baseplates")
    d.add_argument("--plan-only", action="store_true",
                   help="report the layout without generating any CAD")
    d.add_argument("--name", default="drawer", help="output filename stem")
    d.add_argument("--out", default="out", help="output directory")
    d.set_defaults(func=cmd_drawer)

    n = sub.add_parser("bin", help="generate a plain bin, optionally code-stamped")
    n.add_argument("--size", default="1x1", help="bin size in units, e.g. 1x2")
    n.add_argument("--height", type=int, default=3, help="height in units")
    n.add_argument("--code", help="location code to engrave underneath, e.g. KWL1N1T")
    n.add_argument("--code-depth", type=float, default=DEFAULT_DEPTH_MM)
    n.add_argument("--count", type=int, default=1, help="how many, for the estimate")
    n.add_argument("--magnets", action="store_true")
    n.add_argument("--label", action="store_true",
                   help="add the overhanging label shelf (clip-on holders avoid this)")
    n.add_argument("--scoop", action="store_true", help="finger scoop at one end")
    n.add_argument("--length-div", type=int, default=0, help="dividing walls along length")
    n.add_argument("--width-div", type=int, default=0, help="dividing walls along width")
    n.add_argument("--no-lip", action="store_true")
    n.add_argument("--printer", choices=sorted(PRINTERS), default="h2d")
    n.add_argument("--name", help="output filename stem")
    n.add_argument("--out", default="out")
    n.set_defaults(func=cmd_bin)

    ly = sub.add_parser("layout", help="pack measured items into a drawer and draw it")
    ly.add_argument("--width", type=float, required=True)
    ly.add_argument("--depth", type=float, required=True)
    ly.add_argument("--height", type=float, default=None)
    ly.add_argument("--items", required=True, help="YAML list of items and sizes")
    ly.add_argument("--code", help="drawer location code, for the title")
    ly.add_argument("--no-rotate", action="store_true",
                    help="do not turn items 90 degrees to make them fit")
    ly.add_argument("--printer", choices=sorted(PRINTERS), default="h2d")
    ly.add_argument("--out", default="out")
    ly.set_defaults(func=cmd_layout)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
