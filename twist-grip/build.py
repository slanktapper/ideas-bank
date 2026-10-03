#!/usr/bin/env python3
"""Build every STL and every render for twist-grip.

    python3 build.py              # everything
    python3 build.py --stl        # STLs only
    python3 build.py --renders    # renders only
    python3 build.py --fast       # quarter-res renders

Outputs land in stl/ and renders/. Both are regenerated from scratch and are
safe to delete.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

# The renderer is shared -- see ../3d-tools/direction.md. This is the only
# thing twist-grip takes from outside its own folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))

import params as P
import parts as T
import render as R
import scroll as S

HERE = Path(__file__).parent
STL_DIR = HERE / "stl"
RENDER_DIR = HERE / "renders"


# ---------------------------------------------------------------------------
# STLs
# ---------------------------------------------------------------------------

def write_stls() -> list[tuple[str, float]]:
    STL_DIR.mkdir(exist_ok=True)
    for old in STL_DIR.glob("*.stl"):
        old.unlink()

    out = []
    items = dict(T.printable())
    items.update(T.coupon())
    for name, mesh in items.items():
        m = mesh.copy()
        m.apply_translation((0.0, 0.0, -m.bounds[0][2]))      # sit on the bed
        path = STL_DIR / f"{name}.stl"
        m.export(path)
        out.append((name, m.volume / 1000.0 * 1.27))          # grams of PETG
        print(f"  {path.name:20s} {len(m.faces):6d} tris  "
              f"{m.bounds[1][0] - m.bounds[0][0]:5.1f} x "
              f"{m.bounds[1][1] - m.bounds[0][1]:5.1f} x "
              f"{m.bounds[1][2] - m.bounds[0][2]:5.1f} mm")
    return out


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def _size(fast: bool):
    return (420, 320, 1) if fast else (1400, 1050, 2)


def _save(img, name):
    RENDER_DIR.mkdir(exist_ok=True)
    img.save(RENDER_DIR / name)
    print(f"  renders/{name}")



def _callouts(img, cam, w, h, items):
    """Label features, pushing each label outward from the middle of the shot.

    Leaders aimed at fixed corners cross the picture and each other, and
    labels placed by hand land on the part. Taking the direction from the
    centre of the image to the feature and walking out along it puts every
    label in the margin, on the side its feature is on, with a short leader.
    """
    px = R.screen_of([it["at"] for it in items], width=w, height=h, **cam)
    cx, cy = w / 2.0, h / 2.0
    notes = []
    for (x, y), it in zip(px, items):
        dx, dy = float(x) - cx, float(y) - cy
        n = math.hypot(dx, dy) or 1.0
        push = it.get("push", 0.30 * min(w, h))
        tx, ty = float(x) + dx / n * push, float(y) + dy / n * push

        # Keep the TEXT inside the frame, not just the point it hangs off.
        # Clamping the leader endpoint alone still runs a long label off the
        # edge, because the words are drawn outward from it.
        run = 7.9 * len(it["text"]) + 26.0
        left = dx >= 0
        tx = min(tx, w - run) if left else max(tx, run)
        notes.append({
            "text": it["text"],
            "px": (float(x), float(y)),
            "to": (min(max(tx, 24.0), w - 24.0), min(max(ty, 34.0), h - 34.0)),
            "align": "left" if left else "right",
        })
    R.annotate(img, notes)


def render_assembly(phi: float, name: str, fast: bool, az=38, el=34):
    w, h, ss = _size(fast)
    ps = T.assembly(phi)
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=az, elevation_deg=el,
                  margin=1.04)
    _save(R.render(ps, width=w, height=h, supersample=ss, **cam), name)


def render_mechanism(phi: float, name: str, fast: bool):
    """The shell and the blades, with the body and cap left off.

    A DRAWING, not a preview: the shell is drawn grey because the filament
    is black, and a black floor lit from above hides the very spirals this
    view exists to check.
    """
    w, h, ss = _size(fast)
    ps = [{"mesh": T.spun(T.shell(), phi), "color": (0.70, 0.72, 0.76)},
          *[{"mesh": T.jaw(phi, k), "color": P.COL_JAW}
            for k in range(P.JAW_COUNT)]]
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=90, elevation_deg=46,
                  margin=1.04)
    img = R.render(ps, width=w, height=h, supersample=ss, edges=0.5, **cam)
    if fast:
        _save(img, name)
        return

    st = P.STACK

    def at(r, deg, z=P.RING_T):
        a = math.radians(deg)
        return (r * math.cos(a), r * math.sin(a), z)

    _callouts(img, cam, w, h, [
        {"at": at(S.pin_radius(phi), S.JAW_ANGLES[0]),
         "text": f"pin in its groove, r = {S.pin_radius(phi):.0f} mm"},
        {"at": at(P.OVERALL_D / 2, 232, st.wall_top * 0.55),
         "text": "fluted wall — the part you twist"},
        {"at": at(max(S.jaw_face_radius(phi), 1.0), 300.0,
                  st.jaw_0 + P.GRIP_L * 0.5),
         "text": f"{P.GRIP_L:.0f} mm blade, gap {S.gap(phi):.0f} mm"},
    ])
    _save(img, name)


def render_section(phi: float, name: str, fast: bool):
    """A cut through the jaw axis: the stack-up, and what holds it together."""
    w, h, ss = _size(fast)
    ps = []
    for part in T.assembly(phi):
        body, caps = R.section(part["mesh"], normal=(0, -1, 0),
                               origin=(0, 0, 0))
        if len(body.faces):
            ps.append({"mesh": body, "color": part["color"]})
        if len(caps.faces):
            ps.append({"mesh": caps, "color": R.tint(part["color"])})

    # The cut keeps the half at negative y and its faces look toward +y, so
    # the camera has to be on the +y side. From the other side you get a
    # tidy render of the outside of the part and no section at all.
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=90, elevation_deg=14,
                  margin=1.04)
    img = R.render(ps, width=w, height=h, supersample=ss, **cam)
    if fast:
        _save(img, name)
        return

    st = P.STACK
    _callouts(img, cam, w, h, [
        {"at": (S.pin_radius(phi), 0.0, (st.pin_bot_0 + st.jaw_0) / 2),
         "text": "bottom pin, in the shell's floor"},
        {"at": (S.pin_radius(phi), 0.0, (st.jaw_top + st.pin_top_1) / 2),
         "text": "top pin, in the cap — both ends driven together"},
        {"at": (-P.LUG_R_OUT, 0.0, (st.lug_z0 + st.lug_z1) / 2),
         "text": "lug under the shell's lip"},
        {"at": (-(S.jaw_face_radius(phi) + 1.0), 0.0,
                st.jaw_0 + P.GRIP_L * 0.5),
         "text": f"{P.GRIP_L:.0f} mm of grip, {S.gap(phi):.0f} mm apart here"},
    ])
    _save(img, name)


def render_parts(name: str, fast: bool):
    """The four printed parts, as they are oriented on the bed."""
    w, h, ss = _size(fast)
    pr = T.printable()
    colours = {"shell": P.COL_SHELL, "body": P.COL_BODY,
               "cap": P.COL_CAP, "jaw": P.COL_JAW}
    ps, x = [], 0.0
    for key in ("shell", "body", "cap", "jaw"):
        m = pr[key].copy()
        wide = m.bounds[1][0] - m.bounds[0][0]
        m.apply_translation((x - m.bounds[0][0], -m.centroid[1], 0.0))
        ps.append({"mesh": m, "color": colours[key]})
        x += wide + 12.0
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-62, elevation_deg=52,
                  margin=1.06)
    _save(R.render(ps, width=w, height=h, supersample=ss, **cam), name)


def render_coupon(name: str, fast: bool):
    w, h, ss = _size(fast)
    cp = T.coupon()
    ps = [{"mesh": cp["coupon-shell"], "color": P.COL_SHELL},
          {"mesh": cp["coupon-body"], "color": P.COL_BODY},
          {"mesh": cp["coupon-jaw"], "color": P.COL_JAW}]
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=24, elevation_deg=30,
                  margin=1.08)
    _save(R.render(ps, width=w, height=h, supersample=ss, **cam), name)


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", action="store_true")
    ap.add_argument("--renders", action="store_true")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args(argv)
    do_stl = a.stl or not a.renders
    do_ren = a.renders or not a.stl

    t0 = time.time()
    grams = []
    if do_stl:
        print("STLs")
        grams = write_stls()

    if do_ren:
        print("renders")
        render_assembly(0.0, "01-open.png", a.fast, az=38, el=22)
        render_assembly(P.TWIST_SWEEP, "02-shut.png", a.fast, az=38, el=22)
        render_mechanism(0.0, "03-mechanism-open.png", a.fast)
        render_mechanism(P.TWIST_SWEEP, "04-mechanism-shut.png", a.fast)
        render_section(S.phi_for_gap(17.0), "05-section-on-a-finger.png", a.fast)
        render_section(P.TWIST_SWEEP, "06-section-shut.png", a.fast)
        render_parts("07-printed-parts.png", a.fast)
        render_coupon("08-fit-coupon.png", a.fast)

    print("\n" + "-" * 78)
    print(S.summary())
    print("-" * 78)
    if grams:
        whole = sum(g for n, g in grams if not n.startswith("coupon"))
        whole += next(g for n, g in grams if n == "jaw")      # the second jaw
        print(f"a whole mechanism: ring + body + 2 jaws, about {whole:.0f} g "
              f"of PETG printed solid")
        print(f"the fit coupon:    "
              f"{sum(g for n, g in grams if n.startswith('coupon')):.0f} g")
    print(f"{P.OVERALL_D:.0f} mm across, {P.STACK.overall_h:.0f} mm tall; "
          f"bed is {P.BED[0]:.0f} x {P.BED[1]:.0f} mm")
    print(f"\ndone in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
