#!/usr/bin/env python3
"""Build every STL and every render for wire-tags.

    python3 build.py                        # the starter set, the coupon, renders
    python3 build.py --label SCANNER --diameter 5.2
    python3 build.py --coupon --diameter 3.5    # just a coupon, at that size
    python3 build.py --stl                  # STLs only
    python3 build.py --renders              # renders only
    python3 build.py --fast                 # half-res renders

Outputs land in stl/ and renders/. Both are regenerated from scratch and are
safe to delete.

Every tag is two files -- `<name>-body.stl` and `<name>-text.stl` -- modelled
in one coordinate system so they land on top of each other with no manual
positioning. print-guide.md says what to do with them.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

# The renderer is shared -- see ../3d-tools/direction.md. It is the only thing
# this project takes from outside its own folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import params as P
import tag as T
import render as R

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
RENDERS = HERE / "renders"

# Rendered in the pair print-guide.md recommends: PETG Basic reflex blue with
# PETG Basic white lettering. Both are on the shelf -- see ../filament.md.
BODY = (0.17, 0.34, 0.74)
TEXT = (0.94, 0.95, 0.96)
CABLE = (0.30, 0.31, 0.34)


def slug(label: str, d: float) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"{s}-{d:g}mm"


def cable_rod(p: dict, length: float = 0.0) -> trimesh.Trimesh:
    """A length of cable through the clips, for the renders only."""
    length = length or p["plate_l"] + 16.0
    m = trimesh.creation.cylinder(radius=p["cable_d"] / 2.0, height=length,
                                  sections=64)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    m.apply_translation((0.0, 0.0, p["z_cable"]))
    return m


# ------------------------------------------------------------------- output
def write(mesh: trimesh.Trimesh, name: str) -> None:
    STL.mkdir(exist_ok=True)
    mesh.export(STL / f"{name}.stl")
    print(f"  stl/{name}.stl  {len(mesh.faces):6d} faces  {mesh.volume:8.1f} mm3")


def build_stls(labels, coupon_d: float) -> None:
    if labels:
        print("tags")
    for label, d in labels:
        body, letters, p = T.build(d, label)
        n = slug(label, d)
        write(body, f"{n}-body")
        write(letters, f"{n}-text")
    # The coupon is only worth printing at the size you are about to use, so
    # it carries its diameter in the name and follows --diameter.
    print("fit coupon")
    body, info = T.coupon(coupon_d)
    write(body, f"fit-coupon-{coupon_d:g}mm")


# ------------------------------------------------------------------ renders
def _save(img, name: str) -> None:
    RENDERS.mkdir(exist_ok=True)
    img.save(RENDERS / name)
    print(f"  renders/{name}")


def r_tag(scale: float, label: str = "USB-C", d: float = None) -> None:
    body, letters, p = T.build(P.CABLE_D if d is None else d, label)
    rod = cable_rod(p)
    parts = [{"mesh": body, "color": BODY}, {"mesh": letters, "color": TEXT},
             {"mesh": rod, "color": CABLE}]
    cam = R.frame([body], azimuth_deg=65, elevation_deg=42, margin=1.02)
    _save(R.render(parts, width=int(1400 * scale), height=int(1000 * scale), **cam),
          "01-tag.png")

    # Seen from under the bed face, so the key light has to come from under
    # it too -- otherwise the one face this render exists for is in shadow.
    cam = R.frame([body], azimuth_deg=44, elevation_deg=-56, margin=1.0)
    _save(R.render(parts, width=int(1200 * scale), height=int(1000 * scale),
                   key_dir=(-0.45, -0.75, -0.95), fill_dir=(0.8, 0.35, -0.35),
                   **cam),
          "02-label-face.png")


def r_section(scale: float) -> None:
    """Across one clip, with the numbers that decide whether it works."""
    body, letters, p = T.build(P.CABLE_D, "USB-C")
    rod = cable_rod(p)
    w, h = int(1300 * scale), int(1000 * scale)
    parts = []
    for mesh, col in ((body, BODY), (rod, CABLE)):
        keep, cut = R.section(mesh, normal=(0, 1, 0), origin=(0, p["clip_y"], 0))
        if keep is not None and len(keep.faces):
            parts.append({"mesh": keep, "color": col})
        if cut is not None and len(cut.faces):
            parts.append({"mesh": cut, "color": R.tint(col)})

    zc, rb, ro = p["z_cable"], p["r_bore"], p["r_out"]
    target = (0.0, p["clip_y"], zc * 0.55)
    eye = R.orbit_eye(target, 400.0, -90.0, 0.0)
    oh = (2 * ro + 7.0)
    img = R.render(parts, eye=eye, target=target, up=(0, 0, 1),
                   width=w, height=h, ortho_height=oh)

    a = np.radians(P.MOUTH_TILT)
    anchors = np.array([
        [0.0, p["clip_y"], zc],                                   # bore
        [(rb + ro) / 2 * np.cos(a), p["clip_y"],
         zc + (rb + ro) / 2 * np.sin(a)],                          # mouth
        [-ro, p["clip_y"], zc],                                   # wall
        [-rb * 0.72, p["clip_y"], zc + rb * 0.80],                # bore roof
        [0.0, p["clip_y"], P.PLATE_T - P.SINK / 2],               # cradle
    ])
    px = R.screen_of(anchors, eye, target, w, h, up=(0, 0, 1), ortho_height=oh)
    gap = p["cable_d"] - p["mouth"]
    items = [
        {"text": f"bore {p['bore']:.2f} on a {p['cable_d']:.1f} cable",
         "px": px[0], "to": (w * 0.72, h * 0.44)},
        {"text": f"mouth {p['mouth']:.2f} at {P.MOUTH_TILT:.0f}deg,"
                 f" {gap:.2f} of snap", "px": px[1], "to": (w * 0.66, h * 0.16)},
        {"text": f"wall {p['wall']:.2f} = 4 perimeters",
         "px": px[2], "to": (w * 0.22, h * 0.30), "align": "right"},
        {"text": "bore roof on 45deg flanks",
         "px": px[3], "to": (w * 0.26, h * 0.10), "align": "right"},
        {"text": f"cradle {P.SINK:.2f} deep", "px": px[4],
         "to": (w * 0.74, h * 0.70)},
    ]
    _save(R.annotate(img, items, font_size=int(19 * scale)), "03-clip-section.png")


def r_sizes(scale: float) -> None:
    """The four bands end-on, which is the only view that shows the point.

    Seen in three-quarter they are four blue slabs; seen down the cable they
    are four different clips, and the cable each one is for is drawn in it.
    """
    parts, meshes, xs, plans = [], [], [], []
    x = 0.0
    for d, _ in P.FAMILY:
        body, letters, p = T.build(d, f"{d:g} MM")
        rod = cable_rod(p, length=p["plate_l"] + 10.0)
        dx = x + p["plate_w"] / 2.0
        for m, c in ((body, BODY), (letters, TEXT), (rod, CABLE)):
            m = m.copy()
            m.apply_translation((dx, 0.0, 0.0))
            parts.append({"mesh": m, "color": c})
            meshes.append(m)
        xs.append(dx)
        plans.append(p)
        x += p["plate_w"] + 5.0

    w, h = int(1500 * scale), int(620 * scale)
    lo, hi = R.bounds_of(meshes)
    target = (float((lo[0] + hi[0]) / 2), 0.0, float(hi[2] * 0.42))
    # From -Y, so model +X is screen right and the row reads small to large.
    eye = R.orbit_eye(target, 500.0, -90.0, 10.0)
    oh = float(hi[2]) * 2.9
    img = R.render(parts, eye=eye, target=target, up=(0, 0, 1),
                   width=w, height=h, ortho_height=oh)
    anchors = np.array([[dx, 0.0, p["z_cable"]] for dx, p in zip(xs, plans)])
    px = R.screen_of(anchors, eye, target, w, h, up=(0, 0, 1), ortho_height=oh)
    items = [{"text": f"{p['cable_d']:g} mm", "px": q,
              "to": (q[0] - 10 * scale, h * 0.84), "align": "right"}
             for q, p in zip(px, plans)]
    _save(R.annotate(img, items, font_size=int(20 * scale)), "04-sizes.png")


def r_coupon(scale: float, d: float = None) -> None:
    body, info = T.coupon(P.CABLE_D if d is None else d)
    parts = [{"mesh": body, "color": BODY}]
    w, h = int(1500 * scale), int(620 * scale)
    lo, hi = R.bounds_of([body])
    target = (0.0, 0.0, float(hi[2]) * 0.4)
    eye = R.orbit_eye(target, 500.0, -90.0, 58.0)   # -Y: the numbers read
    oh = float(hi[0] - lo[0]) * 1.04 * h / w
    _save(R.render(parts, eye=eye, target=target, up=(0, 0, 1),
                   width=w, height=h, ortho_height=oh), "05-fit-coupon.png")


def r_set(scale: float, labels) -> None:
    """The whole set from underneath, which is the side with the words on it."""
    built = [T.build(d, label) for label, d in labels]
    pw = max(p["plate_w"] for _, _, p in built)
    pl = max(p["plate_l"] for _, _, p in built)
    cols = 4
    parts = []
    for i, (body, letters, p) in enumerate(built):
        # Seen from below, screen-right is model -X, so lay the set out
        # backwards and it reads in order.
        dx = ((cols - 1) / 2.0 - (i % cols)) * (pw + 6.0)
        dy = (0.5 - i // cols) * (pl + 6.0)
        for m, c in ((body, BODY), (letters, TEXT)):
            m = m.copy()
            m.apply_translation((dx, dy, 0.0))
            parts.append({"mesh": m, "color": c})

    w, h = int(1300 * scale), int(900 * scale)
    span_x = cols * (pw + 6.0)
    span_y = 2 * (pl + 6.0)
    target = (0.0, 0.0, P.PLATE_T / 2.0)
    eye = R.orbit_eye(target, 600.0, -90.0, -88.0)
    oh = max(span_y, span_x * h / w) * 1.06
    _save(R.render(parts, eye=eye, target=target, up=(0, 1, 0),
                   width=w, height=h, ortho_height=oh,
                   key_dir=(-0.3, -0.5, -1.0), fill_dir=(0.6, 0.3, -0.5)),
          "06-starter-set.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label", help="build one tag with this word on it")
    ap.add_argument("--diameter", type=float, default=P.CABLE_D,
                    help="cable diameter in mm (default %(default)s)")
    ap.add_argument("--coupon", action="store_true",
                    help="the fit coupon on its own, at --diameter")
    ap.add_argument("--stl", action="store_true", help="STLs only")
    ap.add_argument("--renders", action="store_true", help="renders only")
    ap.add_argument("--fast", action="store_true", help="half-resolution renders")
    args = ap.parse_args()

    if args.coupon:
        labels = []
    elif args.label:
        labels = [(args.label.upper(), args.diameter)]
    else:
        labels = P.STARTER
    do_stl = args.stl or not args.renders
    do_png = args.renders or not args.stl
    scale = 0.5 if args.fast else 1.0

    t0 = time.time()
    if do_stl:
        build_stls(labels, args.diameter)
    if do_png:
        print("renders")
        r_coupon(scale, args.diameter)
        if labels:
            r_tag(scale, *labels[0][:1], labels[0][1])
            r_section(scale)
            r_sizes(scale)
            r_set(scale, labels)
    print(f"done in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
