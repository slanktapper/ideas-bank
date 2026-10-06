#!/usr/bin/env python3
"""Build every STL and every render for flattener.

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
# thing flattener takes from outside its own folder.
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
    items.update(T.fit_comb())
    items["jaw-flat"] = T.jaw_flat()       # the alternative to jaw.stl
    items["comb-dowels"] = T.dowel_comb()  # the press-fit comb
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
        # A caller can name the direction instead. Features on the axis --
        # two blade faces meeting on it -- have no direction from the centre
        # of the shot to take, and two that nearly share one put their
        # labels on top of each other.
        dx, dy = it.get("dir", (float(x) - cx, float(y) - cy))
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


def render_down_the_bore(phi: float, name: str, fast: bool):
    """Straight down the axis, into the hole, which is how you meet it.

    Hand-aimed rather than framed automatically: frame() fits the bounding
    sphere, and from overhead that pushes the camera back until the object
    is a small disc in the middle. Here the rim just fills the frame, so the
    bore does too.

    Lit flatter than the other shots on purpose. Looking down a 100 mm tube
    at a default key light from above, everything past the first 20 mm is
    black, and the blades are the point of the picture.
    """
    w, h, ss = _size(fast)
    st = P.STACK
    ps = T.assembly(phi)

    dist = 190.0
    half = P.OVERALL_D / 2 * 1.04
    fov = 2.0 * math.degrees(math.atan(half / dist))
    cam = {"eye": (0.0, 0.0, st.cap_top + dist), "target": (0.0, 0.0, 0.0),
           "fov_deg": fov}
    img = R.render(ps, width=w, height=h, supersample=ss,
                   ambient=0.66, key=0.40, fill=0.30, spec=0.10, edges=0.42,
                   **cam)
    if fast:
        _save(img, name)
        return

    r_face = S.jaw_face_radius(phi)
    mid = st.jaw_0 + P.GRIP_L * 0.5
    _callouts(img, cam, w, h, [
        {"at": (r_face + 0.2, 0.0, mid), "dir": (1, 0), "push": 0.20 * w,
         "text": f"blade: {P.JAW_W:.0f} mm wide, {P.GRIP_L:.0f} mm deep"},
        {"at": (-(r_face + 0.2), 0.0, mid), "dir": (-1, 0), "push": 0.20 * w,
         "text": f"gap {S.gap(phi):.0f} mm"},
        {"at": (0.0, -P.BORE_D / 2, mid), "dir": (0, 1), "push": 0.16 * h,
         "text": f"{P.BORE_D:.0f} mm bore"},
    ])
    _save(img, name)


def render_ratchet(phi: float, name: str, fast: bool):
    """The clicker, close up: the toothed collar and the post inside it."""
    w, h, ss = _size(fast)
    st = P.STACK
    ps = [{"mesh": T.spun(T.cap(), phi), "color": (0.62, 0.65, 0.70)},
          {"mesh": T.body(), "color": P.COL_BODY}]
    # Low, so the post is seen standing proud of the collar rather than
    # straight down into it.
    cam = {"eye": (46.0, -62.0, st.post_top + 10.0),
           "target": (0.0, 0.0, st.collar_0 + 2.0), "fov_deg": 40.0}
    img = R.render(ps, width=w, height=h, supersample=ss, edges=0.5, **cam)
    if fast:
        _save(img, name)
        return

    a = math.radians(P.PAWL_ANGLE)
    _callouts(img, cam, w, h, [
        {"at": (P.NOSE_R * math.cos(a), P.NOSE_R * math.sin(a),
                (st.nose_0 + st.nose_1) / 2), "dir": (1, 0), "push": 0.26 * w,
         "text": f"nose in a valley — {S.click_deg():.0f}° a click"},
        {"at": (P.POST_R_IN * math.cos(a), P.POST_R_IN * math.sin(a),
                st.post_top - P.PAD_T / 2), "dir": (-1, 0), "push": 0.24 * w,
         "text": "press here to release"},
        {"at": (P.COLLAR_R_OUT * math.cos(math.radians(140)),
                P.COLLAR_R_OUT * math.sin(math.radians(140)),
                (st.collar_0 + st.collar_1) / 2), "dir": (0, 1),
         "push": 0.20 * h,
         "text": f"{P.RATCHET_TEETH} teeth, on the cap"},
    ])
    _save(img, name)


def render_comb(name: str, fast: bool):
    """The fit comb — the first thing to print."""
    w, h, ss = _size(fast)
    cb = T.fit_comb()
    g = cb["comb-grooves"].copy()
    sp = cb["comb-springs"].copy()
    pin = cb["comb-pin"].copy()
    sp.apply_translation((2.0, -30.0, 0.0))
    pin.apply_translation((78.0, -24.0, 0.0))
    ps = [{"mesh": g, "color": (0.32, 0.36, 0.42)},
          {"mesh": sp, "color": P.COL_JAW},
          {"mesh": pin, "color": P.COL_BODY}]
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=-68, elevation_deg=46,
                  margin=1.06)
    _save(R.render(ps, width=w, height=h, supersample=ss, **cam), name)


# Presentation lighting. The default is lit for CATCHING MISTAKES -- a low
# ambient throws every facet into relief -- but it multiplies each colour by
# about 0.7, which turns a milky pink into mauve and a black part into a
# silhouette with no form in it. These shots are for looking at the object,
# so: more ambient, and keep the edge pass to give the black part its shape.
SHOW = dict(ambient=0.74, key=0.34, fill=0.20, spec=0.12, edges=0.46)

PART_COLOURS = {"shell": P.COL_SHELL, "body": P.COL_BODY,
                "cap": P.COL_CAP, "jaw": P.COL_JAW}

PART_VIEWS = {"shell": (34, 26), "body": (34, 18), "cap": (34, 30),
              "jaw": (28, 20)}


def _assembled_parts(phi=0.0):
    """Each part once, in the pose it has in the object."""
    st = P.STACK
    j = T.jaw(phi, 0)
    return {"shell": T.spun(T.shell(st), phi), "body": T.body(st),
            "cap": T.spun(T.cap(st), phi), "jaw": j}


def render_portrait(key: str, name: str, fast: bool):
    """One part on its own, in the orientation it sits in the object."""
    w, h, ss = _size(fast)
    m = _assembled_parts()[key]
    az, el = PART_VIEWS[key]
    cam = R.frame([m], azimuth_deg=az, elevation_deg=el, margin=1.03)
    _save(R.render([{"mesh": m, "color": PART_COLOURS[key]}],
                   width=w, height=h, supersample=ss, **SHOW, **cam), name)


def render_body_end(end: str, name: str, fast: bool):
    """The body's top or bottom end, close up and named.

    DRAWN IN GREY, not the body's black. Flat shading multiplies a colour by
    a factor under 1, so a black part comes back black whatever the light
    does -- no lugs, no boss, no post, just a silhouette. The assembly shots
    carry the real colour; this one has to be legible.

    Framed on a slab of the part rather than the whole of it: the camera is
    aimed with a cropped copy, but the whole body is drawn, so the end fills
    the shot without anything looking cut off.
    """
    w, h, ss = _size(fast)
    st = P.STACK
    body = T.body()
    top = end == "top"
    z0, z1 = ((st.topring_0 - 10.0, st.post_top) if top
              else (st.ring_0, st.ring_top + 10.0))
    proxy = T.keep_both(body, T.tube(0.0, P.OVERALL_D, z0, z1))
    cam = R.frame([proxy], azimuth_deg=40,
                  elevation_deg=52 if top else -52, margin=1.06)
    img = R.render([{"mesh": body, "color": (0.60, 0.62, 0.66)}],
                   width=w, height=h, supersample=ss, ambient=0.5, key=0.5,
                   fill=0.26, spec=0.2, edges=0.55, **cam)
    if fast:
        _save(img, name)
        return

    def at(r, deg, z):
        a = math.radians(deg)
        return (r * math.cos(a), r * math.sin(a), z)

    if top:
        items = [
            {"at": at(P.TOP_LUG_OUT, P.TOP_LUG_ANGLES[0],
                      (st.topring_0 + st.topring_1) / 2), "dir": (1, 0),
             "text": "top lugs (3) — the cap's hook catches under these"},
            {"at": at(P.POST_R_OUT, P.PAWL_ANGLE, st.post_top - P.PAD_T / 2),
             "dir": (-1, 0), "text": "pawl post, and the pad you press"},
            {"at": at(P.BORE_D / 2, 150.0, st.topring_1), "dir": (0, 1),
             "text": f"{P.BORE_D:.0f} mm bore, straight through"},
        ]
    else:
        items = [
            {"at": at(P.LUG_R_OUT, P.LUG_ANGLES[1],
                      (st.lug_z0 + st.lug_z1) / 2), "dir": (1, 0),
             "text": "bottom lugs (3) — hook under the shell's lip"},
            {"at": at(P.SKIRT_OD / 2, 200.0, P.RING_T / 2), "dir": (-1, 0),
             "text": "skirt — this is what turns in the shell's bore"},
            {"at": at(P.BODY_ARC_R_OUT, 90.0, P.RING_T + 6.0), "dir": (0, 1),
             "text": "the step here is the shoulder it stands on"},
        ]
    _callouts(img, cam, w, h, items)
    _save(img, name)


def render_exploded(name: str, fast: bool):
    """The four parts pulled apart along the axis, in assembly order."""
    w, h, ss = _size(fast)
    parts = _assembled_parts()
    # Far enough that each part visibly clears the one below it. At half
    # this, the body still sits down inside the shell and the picture reads
    # as an assembled object with a floating lid.
    lift = {"shell": 0.0, "body": 126.0, "jaw": 126.0, "cap": 258.0}
    out_r = {"jaw": 60.0}
    ps = []
    for key in ("shell", "body", "jaw", "cap"):
        for k in range(2 if key == "jaw" else 1):
            m = (T.jaw(0.0, k) if key == "jaw" else parts[key]).copy()
            a = math.radians(S.JAW_ANGLES[k]) if key == "jaw" else 0.0
            dr = out_r.get(key, 0.0)
            m.apply_translation((dr * math.cos(a), dr * math.sin(a),
                                 lift[key]))
            ps.append({"mesh": m, "color": PART_COLOURS[key]})
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=36, elevation_deg=14,
                  margin=1.01)
    _save(R.render(ps, width=int(w * 0.72), height=int(h * 1.55),
                   supersample=ss, **SHOW, **cam), name)


def render_together(phi: float, name: str, fast: bool):
    """The same four parts, assembled, same colours, same light."""
    w, h, ss = _size(fast)
    ps = [{"mesh": m, "color": PART_COLOURS[k]}
          for k, m in _assembled_parts(phi).items()]
    ps += [{"mesh": T.jaw(phi, 1), "color": P.COL_JAW}]
    cam = R.frame([p["mesh"] for p in ps], azimuth_deg=36, elevation_deg=20,
                  margin=1.03)
    _save(R.render(ps, width=w, height=h, supersample=ss, **SHOW, **cam),
          name)


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
        render_down_the_bore(0.0, "09-down-the-bore-open.png", a.fast)
        render_down_the_bore(S.phi_for_gap(17.0),
                             "10-down-the-bore-on-a-finger.png", a.fast)
        render_down_the_bore(P.TWIST_SWEEP, "11-down-the-bore-shut.png",
                             a.fast)
        render_ratchet(0.0, "12-ratchet.png", a.fast)
        render_comb("13-fit-comb.png", a.fast)
        for key in ("shell", "body", "cap", "jaw"):
            render_portrait(key, f"2{list(PART_COLOURS).index(key)}-part-{key}.png", a.fast)
        render_exploded("24-exploded.png", a.fast)
        render_together(0.0, "25-together-open.png", a.fast)
        render_together(P.TWIST_SWEEP, "26-together-shut.png",
                        a.fast)
        render_body_end("top", "27-body-top.png", a.fast)
        render_body_end("bottom", "28-body-bottom.png", a.fast)

    print("\n" + "-" * 78)
    print(S.summary())
    print("-" * 78)
    if grams:
        # Name the parts of the mechanism rather than excluding the test
        # pieces: every time a new test piece is added, a filter that works
        # by exclusion quietly starts counting it as part of the set.
        MECHANISM = ("shell", "body", "cap", "jaw")
        whole = sum(g for n, g in grams if n in MECHANISM)
        whole += next(g for n, g in grams if n == "jaw")      # the second jaw
        print(f"a whole mechanism: ring + body + 2 jaws, about {whole:.0f} g "
              f"of PETG printed solid")
        print(f"the fit coupon:    "
              f"{sum(g for n, g in grams if n.startswith('coupon')):.0f} g")
        print(f"the fit comb:      "
              f"{sum(g for n, g in grams if n.startswith('comb')):.0f} g "
              f"— print this one first")
    print(f"{P.OVERALL_D:.0f} mm across, {P.STACK.overall_h:.0f} mm tall; "
          f"bed is {P.BED[0]:.0f} x {P.BED[1]:.0f} mm")
    print(f"\ndone in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
