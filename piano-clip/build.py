#!/usr/bin/env python3
"""Build the piano clip: checks, STLs, renders.

    python3 build.py

Writes nothing if a check fails, and exits non-zero. Everything dimensional
lives in params.py; this file is only geometry and argument.
"""

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "3d-tools"))
import render as R  # noqa: E402

import params as P  # noqa: E402

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
RENDERS = HERE / "renders"

FAILURES = []


def check(name, ok, detail=""):
    if not ok:
        FAILURES.append(f"{name}: {detail}")
    status = "ok  " if ok else "FAIL"
    print(f"  [{status}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

def extrude_yz(points_yz, x_len, x_centre=0.0):
    """Extrude a (y, z) profile along X.

    The profile is drawn in the plane of the piano's side view, which is how
    every shape here is easiest to reason about: the cabinet's stepped top,
    the blade's flare and its ribs are all side-view outlines.
    """
    poly = Polygon(points_yz)
    if not poly.is_valid:
        poly = poly.buffer(0)
    m = trimesh.creation.extrude_polygon(poly, height=x_len)
    # extrude_polygon works in XY extruded along Z; relabel (u, v, w) -> (x, y, z)
    v = m.vertices.copy()
    m.vertices = np.column_stack([v[:, 2], v[:, 0], v[:, 1]])
    m.fix_normals()
    m.apply_translation([x_centre - x_len / 2.0, 0.0, 0.0])
    return m


def box(dx, dy, dz, centre):
    m = trimesh.creation.box(extents=(dx, dy, dz))
    m.apply_translation(centre)
    return m


def union(meshes):
    return trimesh.boolean.union(meshes, engine="manifold")


# ---------------------------------------------------------------------------
# the piano's own numbers, in model space
# ---------------------------------------------------------------------------

D = P.s(P.DEPTH_REAL)
H = P.s(P.CASE_H_REAL)
W = P.MINI_W

Y_BACK = D / 2
Y_LID_FRONT = Y_BACK - P.s(P.LID_D_REAL)
Y_PANEL_FRONT = Y_LID_FRONT - P.s(P.PANEL_D_REAL)
Y_KEYS_FRONT = Y_PANEL_FRONT - P.s(P.KEYS_D_REAL)
Y_FRONT = -D / 2

Z_TOP = H
Z_PANEL = H - P.s(P.LID_DROP_REAL)
Z_KEYS = Z_PANEL - P.s(P.KEYS_DROP_REAL)

KEY_T = 0.80                       # white key band thickness
Z_RECESS = Z_KEYS - KEY_T          # floor the keys sit on
Z_SLIP = Z_KEYS - 0.20             # key slip, just under the key tops

KEYBED_W = P.s(P.KEYBED_W_REAL)
WHITE_W = P.s(P.WHITE_W_REAL)
KEYS_D = P.s(P.KEYS_D_REAL)
BLACK_D = KEYS_D * P.BLACK_LEN_FRAC
BLACK_RISE = 0.35


def sharps():
    """X centres of the 31 black keys, built from the note pattern itself.

    White key 0 is E1. Walking up from E the white notes cycle
    E F G A B C D with period 7, and a sharp sits above every white key
    except E and B. Generating them this way rather than listing 31 numbers
    means the count is a consequence of the keyboard, not an assertion about
    it -- and it comes out at 31, which is what the photograph showed.
    """
    x0 = -KEYBED_W / 2
    out = []
    for i in range(P.N_WHITE - 1):
        if i % 7 in (1, 2, 3, 5, 6):       # F G A  C D  -- not E, not B
            out.append(x0 + (i + 1) * WHITE_W)
    return out


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------

def cabinet():
    """The case: lid, control strip, key recess, key slip, front."""
    profile = [
        (Y_BACK, 0.0),
        (Y_BACK, Z_TOP),
        (Y_LID_FRONT, Z_TOP),
        (Y_LID_FRONT, Z_PANEL),
        (Y_PANEL_FRONT, Z_PANEL),
        (Y_PANEL_FRONT, Z_RECESS),
        (Y_KEYS_FRONT, Z_RECESS),
        (Y_KEYS_FRONT, Z_SLIP),
        (Y_FRONT, Z_SLIP),
        (Y_FRONT, 0.0),
    ]
    return extrude_yz(profile, W)


def white_band():
    """One solid white band, not 45 separate keys.

    At 1 mm per inch a white key is 0.93 mm wide, so the groove between two
    of them would be about 0.1 mm -- a quarter of a nozzle line. Cutting
    grooves that cannot print would only add facets. The keyboard reads as a
    keyboard from the black key grouping instead, which is what the eye uses
    anyway.
    """
    return box(KEYBED_W, KEYS_D, KEY_T,
               (0.0, (Y_PANEL_FRONT + Y_KEYS_FRONT) / 2, Z_RECESS + KEY_T / 2))


def black_keys():
    y_back_edge = Y_PANEL_FRONT
    yc = y_back_edge - BLACK_D / 2
    keys = [box(P.BLACK_W_MIN, BLACK_D, BLACK_RISE,
                (x, yc, Z_KEYS + BLACK_RISE / 2)) for x in sharps()]
    return union(keys)


def music_rest():
    """Smoked acrylic panel in its base trough, leaning back.

    The real panel is 4.5 mm of acrylic, which is 0.18 mm at this scale --
    less than half a nozzle line. It is printed at 1.20 mm, 6.8x over scale.
    That is the largest lie in the model and it is why the rest looks a
    little slab-like next to the photograph.
    """
    mw = P.s(P.MREST_W_REAL)
    mh = P.s(P.MREST_H_REAL)
    mt = P.MREST_T_MIN
    base_d = P.s(P.MREST_BASE_D_REAL)
    base_h = max(P.s(P.MREST_BASE_H_REAL), 0.80)
    y0 = P.s(P.MREST_Y_REAL)

    base = box(mw, base_d, base_h, (0.0, y0, Z_TOP + base_h / 2))

    panel = box(mw, mt, mh, (0.0, 0.0, mh / 2))
    tilt = trimesh.transformations.rotation_matrix(
        -math.radians(P.MREST_TILT_DEG), [1, 0, 0], [0, 0, 0])
    panel.apply_transform(tilt)
    panel.apply_translation([0.0, y0, Z_TOP + base_h])
    return union([base, panel])


def blade(sign, slot_gap=None, depth=None):
    """One spring blade. sign = -1 front, +1 back.

    Side-view outline, from the tip up the inner face and back down the
    outer. Three things are shaped into it:

      * a flare at the tip, so the mouth is wider than the music rest and
        the clip feeds itself on over the fabric rather than catching;
      * three ribs on the inner face, which are what actually touch -- the
        plain face is held clear so that SLOT_GAP means the gripping gap and
        not some other gap;
      * a thickened root, so the blade does not hinge on a sharp corner.
    """
    half = (P.SLOT_GAP if slot_gap is None else slot_gap) / 2
    grip = P.GRIP_DEPTH if depth is None else depth
    inner = sign * (half + P.RIB_H)          # plain inner face
    outer = sign * (half + P.RIB_H + P.LEG_T)
    root = sign * (half + P.RIB_H + P.LEG_T + P.LEG_ROOT_FILLET)
    z_tip = -grip
    z_flare = z_tip + P.LEG_FLARE_H
    z_root = -P.LEG_ROOT_FILLET * 2

    inner_tip = sign * (half + P.RIB_H + P.LEG_FLARE)
    outer_tip = sign * (half + P.RIB_H + P.LEG_FLARE + P.LEG_T)

    pts = [(inner_tip, z_tip), (inner, z_flare)]
    for i in range(P.RIB_COUNT):
        zc = z_flare + (i + 1) * (abs(z_flare) / (P.RIB_COUNT + 1))
        pts += [(inner, zc - P.RIB_D / 2),
                (sign * half, zc),
                (inner, zc + P.RIB_D / 2)]
    pts += [(inner, 0.0), (root, 0.0), (outer, z_root),
            (outer, z_flare), (outer_tip, z_tip)]

    if sign > 0:
        pts = pts[::-1]
    return extrude_yz(pts, P.LEG_W)


def coupon(preload, pips):
    """A fit coupon: the real grip, none of the piano.

    Full 44 mm blade width and the full 25 mm reach, because the clamping
    force scales with blade width and a narrow coupon would feel wrong in
    exactly the way that matters. What it drops is the cabinet, the keyboard
    and the music rest -- about three quarters of the print time and all of
    the colour changes.

    Pips on the spine count the coupon, lowest preload first, so three of
    them on the bench cannot be confused once they are off the plate.
    """
    gap = P.GRIPPED_T - 2 * preload
    spine_h = 4.0
    parts = [box(P.LEG_W, gap + 2 * (P.RIB_H + P.LEG_T + P.LEG_ROOT_FILLET),
                 spine_h, (0.0, 0.0, spine_h / 2)),
             blade(-1, slot_gap=gap), blade(+1, slot_gap=gap)]
    for i in range(pips):
        parts.append(trimesh.creation.cylinder(
            radius=0.9, height=1.2,
            transform=trimesh.transformations.translation_matrix(
                [-6.0 + i * 6.0, 0.0, spine_h + 0.4])))
    return union(parts), gap


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def run_checks(parts):
    print("\nchecks")
    body, white, black = parts["body"], parts["white"], parts["black"]
    allm = [body, white, black]

    # -- the piano it is a model of ----------------------------------------
    check("depth breakdown sums to the cabinet depth",
          abs(P.LID_D_REAL + P.PANEL_D_REAL + P.KEYS_D_REAL + P.SLIP_D_REAL
              - P.DEPTH_REAL) < 1e-6)
    check("45 white keys, 31 sharps, generated from the note pattern",
          len(sharps()) == P.N_BLACK == 31,
          f"{len(sharps())} sharps")

    groups = []
    xs = sharps()
    run = 1
    for a, b in zip(xs, xs[1:]):
        if b - a < WHITE_W * 1.5:
            run += 1
        else:
            groups.append(run)
            run = 1
    groups.append(run)
    check("sharps fall in the 3-2-3-2 pattern a piano actually has",
          groups == [3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 1],
          str(groups))

    check("key bed sits inside the cabinet with a cheek each side",
          0 < (W - KEYBED_W) / 2 < W * 0.1,
          f"cheek {(W - KEYBED_W) / 2:.2f} mm a side")

    # -- what the nozzle can do --------------------------------------------
    check("black keys are at least one nozzle line wide",
          P.BLACK_W_MIN >= P.MIN_FEATURE,
          f"{P.BLACK_W_MIN:.2f} mm, {P.BLACK_W_MIN / P.s(P.BLACK_W_REAL):.2f}x over scale")
    check("music rest is at least one nozzle line thick",
          P.MREST_T_MIN >= P.MIN_FEATURE,
          f"{P.MREST_T_MIN:.2f} mm, {P.MREST_T_MIN / P.s(P.MREST_T_REAL):.2f}x over scale")
    check("blade thickness is a whole number of perimeters",
          abs(round(P.LEG_T / 0.4) - P.LEG_T / 0.4) < 0.05,
          f"{P.LEG_T / 0.4:.1f} lines")

    # -- the clip as a spring ----------------------------------------------
    strain = 3 * P.LEG_T * P.PRELOAD / (2 * P.GRIP_DEPTH ** 2)
    inertia = P.LEG_W * P.LEG_T ** 3 / 12
    force = 3 * P.E_PLA * inertia * P.PRELOAD / P.GRIP_DEPTH ** 3
    check("blade strain stays under the long-term PLA limit",
          strain < P.STRAIN_LIMIT,
          f"{strain * 100:.3f} % against {P.STRAIN_LIMIT * 100:.1f} %")
    check("clamping force is enough for cloth without being a hand exercise",
          0.5 < force < 8.0,
          f"{force:.2f} N a blade, {2 * force:.2f} N to spread")
    yield_defl = 0.02 * 2 * P.GRIP_DEPTH ** 2 / (3 * P.LEG_T)
    check("blade survives being opened far past its working deflection",
          yield_defl > P.LEG_FLARE + P.PRELOAD + 2.0,
          f"yields at {yield_defl:.1f} mm, works at {P.PRELOAD:.1f} mm")

    # -- the clip against the thing it grips -------------------------------
    occupied = P.GRIPPED_T
    # The flare is measured from the plain inner face, which stands RIB_H
    # clear of the gripping gap -- so the mouth is wider than SLOT_GAP by the
    # ribs as well as the flare. Getting this wrong understated the mouth by
    # 0.7 mm; the sectioned profile is what caught it.
    mouth = P.SLOT_GAP + 2 * P.RIB_H + 2 * P.LEG_FLARE
    check("the mouth is wider than the measured stack, so it can start",
          mouth > occupied, f"mouth {mouth:.2f} vs {occupied:.2f} mm")
    check("the gap is narrower than the measured stack, so it grips",
          P.SLOT_GAP < occupied,
          f"gap {P.SLOT_GAP:.2f} vs {occupied:.2f} mm")
    check("the ribs are the narrowest point, so they are what grips",
          P.RIB_H > 0 and P.SLOT_GAP < P.SLOT_GAP + 2 * P.RIB_H < mouth,
          f"ribs {P.SLOT_GAP:.2f}, plain face {P.SLOT_GAP + 2 * P.RIB_H:.2f} mm")
    check("deflection in use is the preload it was designed for",
          abs((occupied - P.SLOT_GAP) / 2 - P.PRELOAD) < 1e-9)
    check("it reaches the depth Rob asked for",
          abs(P.GRIP_DEPTH - 25.0) < 1e-9)

    keel = P.SLOT_GAP + 2 * (P.RIB_H + P.LEG_T + P.LEG_ROOT_FILLET)
    check("the keel tucks under the cabinet instead of sticking out",
          keel < D, f"keel {keel:.2f} mm in a {D:.2f} mm cabinet")
    check("blades are narrower than the cabinet",
          P.LEG_W < W, f"{P.LEG_W} mm in {W} mm")

    # -- meshes -------------------------------------------------------------
    for name, m in parts.items():
        check(f"{name} mesh is watertight", m.is_watertight,
              f"{len(m.faces)} faces")
    check("no colour body overlaps another",
          _no_overlap(body, white) and _no_overlap(white, black)
          and _no_overlap(body, black))

    lo, hi = R.bounds_of(allm)
    size = hi - lo
    check("whole clip fits the H2D bed with room to spare",
          all(size < np.array([325, 320, 325])),
          f"{size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")
    return size


def _no_overlap(a, b):
    inter = trimesh.boolean.intersection([a, b], engine="manifold")
    return inter.is_empty or abs(inter.volume) < 1e-6


# ---------------------------------------------------------------------------

def main():
    print(f"piano-clip  --  1 mm per inch (1:{1 / P.SCALE:.1f})")
    print(f"  cabinet   {W:.1f} x {D:.1f} x {H:.1f} mm")
    print(f"  grip      {P.GRIP_DEPTH:.0f} mm deep, {P.SLOT_GAP:.2f} mm gap")

    body = union([cabinet(), music_rest(), blade(-1), blade(+1)])
    parts = {"body": body, "white": white_band(), "black": black_keys()}

    size = run_checks(parts)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed -- nothing written")
        for f in FAILURES:
            print("  -", f)
        return 1

    STL.mkdir(exist_ok=True)
    for name, m in parts.items():
        m.export(STL / f"piano-clip-{name}.stl")
    print(f"\nwrote {len(parts)} STLs to stl/")

    print("\nfit coupons -- print these first")
    for i, preload in enumerate(P.COUPON_PRELOADS):
        m, gap = coupon(preload, i + 1)
        m.export(STL / f"coupon-{i + 1}.stl")
        strain = 3 * P.LEG_T * preload / (2 * P.GRIP_DEPTH ** 2)
        force = (3 * P.E_PLA * (P.LEG_W * P.LEG_T ** 3 / 12)
                 * preload / P.GRIP_DEPTH ** 3)
        flag = "" if strain < P.STRAIN_LIMIT else "   <-- over the creep limit"
        print(f"  coupon-{i + 1}  {i + 1} pip{'s' if i else ' '}  "
              f"gap {gap:.2f} mm  preload {preload:.1f} mm  "
              f"{force:.2f} N a blade  strain {strain * 100:.3f} %{flag}")

    render_all(parts)
    print(f"overall {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, "
          f"{sum(m.volume for m in parts.values()) / 1000 * 1.24:.1f} g solid")
    return 0


def render_all(parts):
    RENDERS.mkdir(exist_ok=True)
    scene = [
        {"mesh": parts["body"], "color": P.COL_BODY},
        {"mesh": parts["white"], "color": P.COL_WHITE},
        {"mesh": parts["black"], "color": P.COL_BLACK},
    ]
    meshes = [p["mesh"] for p in scene]
    shots = [
        ("01-front", -90, 12),
        ("02-three-quarter", -55, 26),
        ("03-above", -90, 68),
        ("04-end", 0, 8),
        ("05-underneath", -70, -34),
    ]
    for name, az, el in shots:
        cam = R.frame(meshes, az, el, margin=1.06)
        img = R.render(scene, width=1400, height=1000, **cam)
        img.save(RENDERS / f"{name}.png")
        print(f"  rendered {name}.png")

    cpn = [{"mesh": coupon(p, i + 1)[0], "color": P.COL_BODY}
           for i, p in enumerate(P.COUPON_PRELOADS)]
    for i, c in enumerate(cpn):
        c["mesh"].apply_translation([0.0, (i - 1) * 22.0, 0.0])
    cam = R.frame([c["mesh"] for c in cpn], -58, 24, margin=1.04)
    R.render(cpn, width=1400, height=1000, **cam).save(
        RENDERS / "06-coupons.png")
    print("  rendered 06-coupons.png")


if __name__ == "__main__":
    sys.exit(main())
