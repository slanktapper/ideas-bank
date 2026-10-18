#!/usr/bin/env python3
"""Build every STL and every render for the smb-parts shelf rail.

    python3 build.py              # everything
    python3 build.py --stl        # STLs only
    python3 build.py --renders    # renders only
    python3 build.py --fast       # half-res renders

Outputs land in stl/ and renders/. Both are regenerated from scratch and are
safe to delete.

ONE VIGNETTE IS ONE SHELF, cut into two printed panels of 160 mm. Print the
pair for each shelf you want to dress; three shelves is about three feet.

TWO WAYS TO PRINT, so two sets of STLs:

  stl/shelf-KEY-N.stl        the whole panel as one solid. One colour; the
                             art reads as relief in raking light.
  stl/colour/shelf-KEY-N-*   the same panel split into the cap plus one body
                             per NES colour. Load them together in the slicer
                             and assign a filament to each.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

# The renderer is shared -- see ../3d-tools/direction.md. This is the only
# thing smb-parts takes from outside its own folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import coupons as C
import params as P
import parts as T
import render as R
import vignettes as V

HERE = Path(__file__).parent
STL_DIR = HERE / "stl"
COLOUR_DIR = STL_DIR / "colour"
RENDER_DIR = HERE / "renders"
TEST_DIR = STL_DIR / "test"

CAP_COLOUR = (0.17, 0.18, 0.21)            # the body, in black PLA
SHELF_COLOUR = (0.78, 0.79, 0.81)          # the shelf proxy, in grey


def _rgb(c):
    return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)


def build_all():
    """[(vignette, idx, whole, body, {colour: mesh})] for every panel."""
    out = []
    for vig in V.RAIL:
        for idx in range(P.PANELS_PER_SHELF):
            whole, body, art = T.panel(vig, idx)
            out.append((vig, idx, whole, body, art))
    return out


def shelf_proxy(length):
    """The floor and retainer bar of Rob's shelf, where the rail expects them."""
    bar_top = P.FACE_H - P.WEB_T
    floor_top = bar_top - P.BAR_RISE
    bar = trimesh.creation.box(extents=(length, P.MAT_T, P.BAR_RISE))
    bar.apply_translation((length / 2, P.FACE_T + P.MAT_T / 2,
                           floor_top + P.BAR_RISE / 2))
    depth = 60.0                                  # just enough to read as a shelf
    floor = trimesh.creation.box(extents=(length, depth, P.MAT_T))
    floor.apply_translation((length / 2, P.FACE_T + depth / 2,
                             floor_top - P.MAT_T / 2))
    return trimesh.boolean.union([bar, floor])


# ---------------------------------------------------------------------------
# STLs
# ---------------------------------------------------------------------------

def write_stls(built):
    STL_DIR.mkdir(exist_ok=True)
    COLOUR_DIR.mkdir(exist_ok=True)
    for old in list(STL_DIR.glob("*.stl")) + list(COLOUR_DIR.glob("*.stl")):
        old.unlink()
    rows = []
    for vig, idx, whole, body, art in built:
        name = "shelf-%s-%d" % (vig.key, idx + 1)
        whole.export(STL_DIR / (name + ".stl"))
        rows.append((name, whole.volume, whole.is_watertight))
        body.export(COLOUR_DIR / (name + "-cap.stl"))
        for colour, mesh in art.items():
            mesh.export(COLOUR_DIR / ("%s-%02x%02x%02x.stl" % ((name,) + colour)))
    return rows


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def _placed(mesh, offset):
    m = mesh.copy()
    m.apply_translation(offset)
    return m


def _parts_for(body, art, offset=(0.0, 0.0, 0.0)):
    ps = [{"mesh": _placed(body, offset), "color": CAP_COLOUR}]
    for colour, mesh in art.items():
        ps.append({"mesh": _placed(mesh, offset), "color": _rgb(colour)})
    return ps


def _save(img, name):
    RENDER_DIR.mkdir(exist_ok=True)
    img.save(RENDER_DIR / name)
    print("  renders/%s" % name)


def render_shelves(built, ss, w, h):
    """Every shelf's art, assembled from its two panels, stacked."""
    ps = []
    step = P.FACE_H + 7.0
    for i, vig in enumerate(V.RAIL):
        z = (len(V.RAIL) - 1 - i) * step
        for _, idx, _, body, art in [b for b in built if b[0] is vig]:
            ps += _parts_for(body, art, (idx * P.PANEL_L, 0.0, z))
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-90, elevation_deg=0,
                  margin=1.02, ortho=True)
    _save(R.render(ps, width=w, height=h, supersample=ss, edges=0.45, **cam),
          "shelves.png")


def render_on_shelf(built, ss, w, h):
    """One shelf dressed, from in front and above, with the shelf under it."""
    vig = V.RAIL[1]
    ps = []
    for _, idx, _, body, art in [b for b in built if b[0] is vig]:
        ps += _parts_for(body, art, (idx * P.PANEL_L, 0.0, 0.0))
    ps.append({"mesh": shelf_proxy(P.SHELF_L), "color": SHELF_COLOUR})
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-62, elevation_deg=22,
                  margin=1.04)
    _save(R.render(ps, width=w, height=h, supersample=ss, edges=0.5, **cam),
          "on-shelf.png")


def render_clip(built, ss, w, h):
    """Section through the cap sitting on the retainer bar."""
    vig, idx, whole, body, art = built[2]
    shelf = shelf_proxy(80.0)
    ps = []
    for mesh, colour in ((whole, CAP_COLOUR), (shelf, SHELF_COLOUR)):
        b, caps = R.section(mesh, normal=(-1.0, 0.0, 0.0), origin=(40.0, 0.0, 0.0))
        if len(b.faces):
            ps.append({"mesh": b, "color": colour})
        if len(caps.faces):
            ps.append({"mesh": caps, "color": R.tint(colour)})
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-36, elevation_deg=15,
                  margin=1.15)
    img = R.render(ps, width=w, height=h, supersample=ss, **cam)

    bar_top = P.FACE_H - P.WEB_T
    notes = [
        ((0.0, -P.RELIEF, P.FACE_H * 0.55), "art %.1f mm proud, %.1f mm tall"
         % (P.RELIEF, P.FACE_H)),
        ((40.0, P.FACE_T + P.SLOT / 2.0, bar_top - P.GRIP / 2.0),
         "%.1f mm slot over the 4 mm bar" % P.SLOT),
        ((40.0, P.DEPTH, bar_top - P.GRIP),
         "inner leg %.0f mm down the bar" % P.GRIP),
        ((40.0, P.FACE_T, 1.0), "hangs %.1f mm below the shelf"
         % (bar_top - P.BAR_RISE - P.MAT_T)),
    ]
    px = R.screen_of([n[0] for n in notes], width=w, height=h, **cam)
    items = []
    for (anchor, text), p in zip(notes, px):
        x, y = float(p[0]), float(p[1])
        left = x < w * 0.5
        items.append({"text": text, "px": (x, y),
                      "to": (26.0 if left else w - 26.0,
                             min(max(y, 34.0), h - 34.0)),
                      "align": "left" if left else "right"})
    R.annotate(img, items)
    _save(img, "clip-section.png")


def write_test_stls():
    """The fit ladder and the art sample -- print these before the real thing."""
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    for old in TEST_DIR.glob("*.stl"):
        old.unlink()
    rows = []
    comb, total = C.fit_ladder()
    comb.export(TEST_DIR / "fit-ladder.stl")
    rows.append(("fit-ladder.stl", comb.volume,
                 "%d coupons, %.0f mm" % (len(P.COUPON_SLOTS), total)))
    vig = V.RAIL[1]
    sample, t0 = C.art_sample(vig)
    sample.export(TEST_DIR / "art-sample.stl")
    rows.append(("art-sample.stl", sample.volume,
                 "%s, tiles %d-%d" % (vig.key, t0, t0 + 1)))
    return rows


def render_test(ss, w, h):
    """The fit ladder, head on, so the embossed slot numbers can be read."""
    _, plain, numbers, _ = C.fit_ladder(split=True)
    ps = [{"mesh": plain, "color": CAP_COLOUR},
          {"mesh": numbers, "color": (0.98, 0.78, 0.16)}]
    cam = R.frame([plain], azimuth_deg=-90, elevation_deg=0, margin=1.04,
                  ortho=True)
    _save(R.render(ps, width=w, height=h, supersample=ss, edges=0.5, **cam),
          "fit-ladder.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", action="store_true")
    ap.add_argument("--renders", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--test", action="store_true",
                    help="only the fit ladder and art sample")
    a = ap.parse_args()
    if a.test:
        print("test pieces:")
        for name, vol, note in write_test_stls():
            print("  stl/test/%-18s %7.0f mm3 = %4.1f g  (%s)"
                  % (name, vol, vol / 1000 * 1.24, note))
        render_test(1 if a.fast else 2, *((1100, 820) if a.fast else (1500, 1100)))
        return

    do_stl = a.stl or not (a.stl or a.renders)
    do_ren = a.renders or not (a.stl or a.renders)

    t = time.time()
    print("building %d shelves x %d panels ..." % (len(V.RAIL), P.PANELS_PER_SHELF))
    built = build_all()
    print("  %.1fs" % (time.time() - t))

    if do_stl:
        print("test pieces:")
        for name, vol, note in write_test_stls():
            print("  stl/test/%-18s %7.0f mm3 = %4.1f g  (%s)"
                  % (name, vol, vol / 1000 * 1.24, note))
        print("STLs:")
        for name, vol, tight in write_stls(built):
            print("  stl/%-24s %8.0f mm3  watertight=%s" % (name + ".stl", vol, tight))

    if do_ren:
        print("renders:")
        ss = 1 if a.fast else 2
        w, h = (1100, 820) if a.fast else (1500, 1100)
        render_shelves(built, ss, w, h)
        render_on_shelf(built, ss, w, h)
        render_clip(built, ss, w, h)
        render_test(ss, w, h)

    print("done in %.1fs" % (time.time() - t))


if __name__ == "__main__":
    main()
