#!/usr/bin/env python3
"""Build every STL and every render for the smb-parts shelf rail.

    python3 build.py              # everything
    python3 build.py --stl        # STLs only
    python3 build.py --renders    # renders only
    python3 build.py --fast       # half-res renders

Outputs land in stl/ and renders/. Both are regenerated from scratch and are
safe to delete.

TWO WAYS TO PRINT, so two sets of STLs:

  stl/panel-N.stl          the whole panel as one solid. Print in one colour;
                           the art reads as relief in raking light.
  stl/colour/panel-N-*.stl the same panel split into the channel plus one body
                           per NES colour. Load them together in the slicer,
                           assign a filament to each, and the art comes out in
                           colour. Same geometry, same place -- they are the
                           one solid, cut up.
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

import params as P
import parts as T
import render as R
import vignettes as V

HERE = Path(__file__).parent
STL_DIR = HERE / "stl"
COLOUR_DIR = STL_DIR / "colour"
RENDER_DIR = HERE / "renders"

CHANNEL_COLOUR = (0.17, 0.18, 0.21)        # the body, in black PLA


def _rgb(c):
    return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)


def build_all():
    """[(vignette, whole, body, {colour: mesh})] for the whole rail."""
    out = []
    for i, vig in enumerate(V.RAIL):
        whole, body, art = T.panel(vig, first=(i == 0), last=(i == len(V.RAIL) - 1))
        out.append((vig, whole, body, art))
    return out


# ---------------------------------------------------------------------------
# STLs
# ---------------------------------------------------------------------------

def write_stls(built):
    STL_DIR.mkdir(exist_ok=True)
    COLOUR_DIR.mkdir(exist_ok=True)
    for old in list(STL_DIR.glob("*.stl")) + list(COLOUR_DIR.glob("*.stl")):
        old.unlink()

    rows = []
    for i, (vig, whole, body, art) in enumerate(built, start=1):
        name = "panel-%d-%s" % (i, vig.key)
        whole.export(STL_DIR / (name + ".stl"))
        rows.append((name + ".stl", whole.volume, whole.is_watertight))
        body.export(COLOUR_DIR / (name + "-channel.stl"))
        for colour, mesh in art.items():
            hexc = "%02x%02x%02x" % colour
            mesh.export(COLOUR_DIR / ("%s-%s.stl" % (name, hexc)))
    return rows


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def _parts_for(vig, body, art, offset=(0.0, 0.0, 0.0)):
    ps = [{"mesh": T_placed(body, offset), "color": CHANNEL_COLOUR}]
    for colour, mesh in art.items():
        ps.append({"mesh": T_placed(mesh, offset), "color": _rgb(colour)})
    return ps


def T_placed(mesh, offset):
    m = mesh.copy()
    m.apply_translation(offset)
    return m


def _save(img, name):
    RENDER_DIR.mkdir(exist_ok=True)
    img.save(RENDER_DIR / name)
    print("  renders/%s" % name)


def render_panels(built, ss, w, h):
    """The four panels stacked, head on -- what the art actually looks like."""
    ps = []
    step = P.FACE_H + 7.0
    for i, (vig, whole, body, art) in enumerate(built):
        z = (len(built) - 1 - i) * step
        ps += _parts_for(vig, body, art, offset=(0.0, 0.0, z))
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-90, elevation_deg=0,
                  margin=1.02, ortho=True)
    img = R.render(ps, width=w, height=h, supersample=ss, edges=0.45, **cam)
    _save(img, "rail-panels.png")


def render_full(built, ss, w, h):
    """The whole 900 mm as it hangs, end to end."""
    ps = []
    for i, (vig, whole, body, art) in enumerate(built):
        ps += _parts_for(vig, body, art, offset=(i * P.PANEL_L, 0.0, 0.0))
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-90, elevation_deg=0,
                  margin=1.01, ortho=True)
    img = R.render(ps, width=w, height=int(h * 0.20), supersample=ss,
                   edges=0.35, **cam)
    _save(img, "rail-full.png")


def render_three_quarter(built, ss, w, h):
    """One panel from in front and above, so the channel reads as a channel."""
    vig, whole, body, art = built[1]
    ps = _parts_for(vig, body, art)
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-58, elevation_deg=24,
                  margin=1.05)
    img = R.render(ps, width=w, height=h, supersample=ss, edges=0.5, **cam)
    _save(img, "panel-three-quarter.png")


def render_clip(built, ss, w, h):
    """Section through the channel with a shelf board in it."""
    vig, whole, body, art = built[1]
    board = trimesh.creation.box(extents=(120.0, 90.0, P.SHELF_T))
    board.apply_translation((60.0, P.FACE_T + 45.0, P.LEG_T + P.GAP / 2.0))

    ps = []
    for mesh, colour in ((whole, CHANNEL_COLOUR), (board, (0.74, 0.62, 0.45))):
        b, caps = R.section(mesh, normal=(-1.0, 0.0, 0.0), origin=(40.0, 0.0, 0.0))
        if len(b.faces):
            ps.append({"mesh": b, "color": colour})
        if len(caps.faces):
            ps.append({"mesh": caps, "color": R.tint(colour)})
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-34, elevation_deg=16,
                  margin=1.12)
    img = R.render(ps, width=w, height=h, supersample=ss, **cam)

    notes = [
        ((0.0, -P.RELIEF, P.FACE_H * 0.62), "art stands %.1f mm proud" % P.RELIEF),
        ((40.0, P.FACE_T + P.LEG_D * 0.5, P.LEG_T + P.GAP / 2.0),
         "%.1f mm slot: %.0f mm board + %.1f fit" % (P.GAP, P.SHELF_T, P.FIT)),
        ((40.0, P.FACE_T + P.LEG_D, P.FACE_H - P.LEG_T / 2.0),
         "leg %.1f mm thick, %.0f mm deep" % (P.LEG_T, P.LEG_D)),
    ]
    px = R.screen_of([n[0] for n in notes], width=w, height=h, **cam)
    items = []
    for (anchor, text), p in zip(notes, px):
        x, y = float(p[0]), float(p[1])
        left = x < w * 0.5
        tx = 26.0 if left else w - 26.0
        ty = min(max(y, 34.0), h - 34.0)
        items.append({"text": text, "px": (x, y), "to": (tx, ty),
                      "align": "left" if left else "right"})
    R.annotate(img, items)
    _save(img, "clip-section.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", action="store_true")
    ap.add_argument("--renders", action="store_true")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    do_stl = a.stl or not (a.stl or a.renders)
    do_ren = a.renders or not (a.stl or a.renders)

    t = time.time()
    print("building %d panels ..." % P.PANELS)
    built = build_all()
    print("  %.1fs" % (time.time() - t))

    if do_stl:
        print("STLs:")
        for name, vol, tight in write_stls(built):
            print("  stl/%-28s %8.0f mm3  watertight=%s" % (name, vol, tight))

    if do_ren:
        print("renders:")
        ss = 1 if a.fast else 2
        w, h = (1100, 820) if a.fast else (1500, 1100)
        render_panels(built, ss, w, h)
        render_full(built, ss, w * 2, h)
        render_three_quarter(built, ss, w, h)
        render_clip(built, ss, w, h)

    print("done in %.1fs" % (time.time() - t))


if __name__ == "__main__":
    main()
