"""The tag itself: a plate with a C-clip at each end, and the clips opposed.

Orientation is the print orientation and nothing else, because every decision
below was made by it:

    X   across the tag        Y   along the cable        Z   up off the bed

The label face is the **bed face**, Z = 0.  Printed that way the lettering is
a flat, glass-smooth first layer instead of a bridged ceiling, the 0.60 mm of
second filament is the first three layers so the colour change costs one
purge, and the clips flex within their layers rather than trying to peel them
apart.

Two shapes carry the whole part and both are sections in XZ, extruded along
the cable:

* `outer_section` is a **D**, not a circle -- vertical flanks from the plate
  up to the cable centre, domed above it.  A plain circular clip sitting on
  the bed starts as a sliver and flares outwards faster than FDM will bridge;
  the flat flanks are what make it printable without support.
* `bore_section` is a **truncated teardrop**: the bore is a horizontal hole,
  so 45 degree flanks carry its roof most of the way up and the last
  `BRIDGE` mm is left flat to bridge.  A full teardrop would come to a point
  and leave too little wall under the dome.

The mouth is aimed `MOUTH_TILT` above horizontal rather than straight out
sideways.  That is what turns the lower lip from a shoulder into a jaw: the
cable has to be pushed down as well as in, so nothing short of that motion
gets it out again.
"""
from __future__ import annotations
import numpy as np, trimesh
from shapely.geometry import Point, Polygon, box as sbox
from shapely.affinity import rotate as srotate, translate as stranslate
from shapely.ops import unary_union

import params as P
import glyphs

SEG = 96
EPS = 1e-6


# ----------------------------------------------------------------- 2D pieces
def _arch(r: float, cz: float, flat: float) -> Polygon:
    """A circle with 45 degree flanks over it, truncated to a flat roof.

    `flat` is the width of the bridge left at the top.  Set it to 0 and this
    is the usual teardrop, which comes to a point and wastes wall.
    """
    c = Point(0.0, cz).buffer(r, SEG)
    k = r / np.sqrt(2.0)
    half = min(flat / 2.0, k)
    top = cz + k + (k - half)
    roof = Polygon([(-k, cz), (-k, cz + k), (-half, top), (half, top),
                    (k, cz + k), (k, cz)])
    return unary_union([c, roof])


def outer_section(p: dict) -> Polygon:
    """The clip's outside: flat flanks to the cable centre, domed over it."""
    ro, zc = p["r_out"], p["z_cable"]
    return unary_union([Point(0.0, zc).buffer(ro, SEG), sbox(-ro, 0.0, ro, zc)])


def bore_section(p: dict) -> Polygon:
    return _arch(p["r_bore"], p["z_cable"], P.BRIDGE)


def mouth_section(p: dict, facing: float) -> Polygon:
    """The slot the cable snaps through, with a 45 degree lead-in on the lips.

    `facing` is +1 for a mouth opening towards +X, -1 towards -X.  That sign
    is the whole idea of the tag: the two clips get opposite signs, so the
    cable threads a shallow S and no single pull takes the tag off.
    """
    m, ro, lead, zc = p["mouth"] / 2.0, p["r_out"], P.LEAD, p["z_cable"]
    far = ro * 1.6
    slot = Polygon([
        (0.0, -m), (ro - lead, -m), (ro, -(m + lead)), (far, -(m + lead)),
        (far, m + lead), (ro, m + lead), (ro - lead, m), (0.0, m),
    ])
    a = P.MOUTH_TILT if facing > 0 else 180.0 - P.MOUTH_TILT
    return stranslate(srotate(slot, a, origin=(0, 0)), 0.0, zc)


def ribs_section(p: dict, facing: float):
    """Two bumps standing proud of the bore, so the tag cannot creep along."""
    if P.RIB <= 0:
        return None
    d = p["r_bore"] + P.RIB_R - P.RIB
    mouth_a = P.MOUTH_TILT if facing > 0 else 180.0 - P.MOUTH_TILT
    out = []
    for s in (1.0, -1.0):
        a = np.radians(mouth_a + s * P.RIB_DEG)
        out.append(Point(d * np.cos(a), p["z_cable"] + d * np.sin(a)).buffer(P.RIB_R, 32))
    return unary_union(out)


# ----------------------------------------------------------------- 2D -> 3D
def _clean(poly):
    """Drop the near-duplicate vertices a shapely union leaves behind.

    Without this the triangulator emits slivers and the extrusion comes back
    not watertight, which manifold then refuses to boolean.
    """
    g = poly.simplify(1e-6)
    return g if not g.is_empty else poly


def prism(poly, y0: float, y1: float) -> trimesh.Trimesh:
    """Extrude an XZ section along the cable, from y0 to y1."""
    geoms = [_clean(g) for g in getattr(poly, "geoms", [poly])]
    parts = [trimesh.creation.extrude_polygon(g, y1 - y0, engine="earcut")
             for g in geoms if g.area > 1e-9]
    m = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    m.apply_translation((0.0, y1, 0.0))     # +90 about X sends the extrusion to -Y
    return m


def flat(poly, z0: float, h: float) -> trimesh.Trimesh:
    """Extrude an XY outline upwards -- used for the lettering only."""
    geoms = [_clean(g) for g in getattr(poly, "geoms", [poly])]
    parts = [trimesh.creation.extrude_polygon(g, h, engine="earcut")
             for g in geoms if g.area > 1e-9]
    m = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    m.apply_translation((0.0, 0.0, z0))
    return m


def _plate(p: dict) -> trimesh.Trimesh:
    w, l, t = p["plate_w"], p["plate_l"], p["plate_t"]
    m = trimesh.creation.box((w, l, t))
    m.apply_translation((0.0, 0.0, t / 2.0))
    return m


# -------------------------------------------------------------------- parts
def set_text(p: dict):
    """Lay the label out, shrinking it only as far as it has to go."""
    cap = p["cap_h"]
    room = p["plate_l"] - 2 * (P.CLIP_H + P.CLIP_GAP) - 2 * P.EDGE
    geom, length, height = glyphs.outline(p["label"], cap, P.TRACK, mirror=True)
    while length > room and cap > P.CAP_MIN:
        cap = max(P.CAP_MIN, cap - 0.1)
        geom, length, height = glyphs.outline(p["label"], cap, P.TRACK, mirror=True)
    if length > room:                      # still too long: squeeze the word
        from shapely.affinity import scale as sscale
        geom = sscale(geom, 1.0, room / length, origin=(0, 0, 0))
        length = room
    return geom, length, height, cap


def build(cable_d: float = P.CABLE_D, label: str = "USB-C"):
    """One tag, as (body, letters, plan).  Both meshes share an origin."""
    p = P.plan(cable_d, label, glyphs.measure(label, P.CAP_H, P.TRACK))
    text, t_len, t_h, cap = set_text(p)
    p["text_len"], p["text_cap"] = t_len, cap

    cy, ch = p["clip_y"], p["clip_h"]
    spans = [(+cy - ch / 2, +cy + ch / 2, +1.0),      # +Y clip, mouth to +X
             (-cy - ch / 2, -cy + ch / 2, -1.0)]      # -Y clip, mouth to -X

    body = _plate(p)
    for y0, y1, facing in spans:
        body = trimesh.boolean.union([body, prism(outer_section(p), y0, y1)])
    for y0, y1, facing in spans:
        cut = [prism(bore_section(p), y0 - EPS, y1 + EPS),
               prism(mouth_section(p, facing), y0 - EPS, y1 + EPS)]
        body = trimesh.boolean.difference([body, *cut])
    for y0, y1, facing in spans:
        r = ribs_section(p, facing)
        if r is not None:
            body = trimesh.boolean.union([body, prism(r, y0, y1)])

    letters = flat(text, 0.0, p["text_h"])
    body = trimesh.boolean.difference([body, flat(text, -EPS, p["text_h"] + EPS)])
    return body, letters, p


# ------------------------------------------------------------------- coupon
def coupon(cable_d: float = P.CABLE_D, steps=P.COUPON_STEPS):
    """Five clips either side of nominal, each engraved with its step.

    FDM holes print undersize and by an amount that depends on the filament,
    the nozzle and how fast the clip's little perimeters are run.  `FIT` is a
    guess at that; this is how the guess gets corrected.  Push the real cable
    into each station, find the one that snaps home and holds, and build the
    tags at `--diameter cable + step`.

    Each station is a whole `plan()`, not a bore scaled in isolation -- the
    mouth, the wall and the ride height move with it, exactly as they would
    on a real tag, so what the coupon proves is a tag and not a hole.

    Unlike a tag, its numbers are engraved into the **top** face and in one
    colour: you read them while you are pushing cables in, not afterwards,
    and a fit test is not the place to also be testing a filament change.
    """
    plans = [P.plan(cable_d + d, f"{d:+.1f}") for d in steps]
    pitch = max(16.0, 2 * max(q["r_out"] for q in plans) + 8.0)
    width = pitch * len(plans)
    depth = P.CLIP_H + 2 * P.CLIP_GAP + P.COUPON_CAP + 2 * P.EDGE
    t = P.PLATE_T

    body = trimesh.creation.box((width, depth, t))
    body.apply_translation((0.0, 0.0, t / 2.0))

    y_clip = depth / 2.0 - P.CLIP_GAP - P.CLIP_H / 2.0
    y0, y1 = y_clip - P.CLIP_H / 2.0, y_clip + P.CLIP_H / 2.0
    y_text = -depth / 2.0 + P.EDGE + P.COUPON_CAP / 2.0

    text = None
    for i, (q, d) in enumerate(zip(plans, steps)):
        x = (i - (len(plans) - 1) / 2.0) * pitch
        # Alternate which way the mouth faces, so one coupon tests both hands.
        facing = 1.0 if i % 2 == 0 else -1.0
        body = trimesh.boolean.union(
            [body, prism(stranslate(outer_section(q), x, 0.0), y0, y1)])
        body = trimesh.boolean.difference([
            body,
            prism(stranslate(bore_section(q), x, 0.0), y0 - EPS, y1 + EPS),
            prism(stranslate(mouth_section(q, facing), x, 0.0), y0 - EPS, y1 + EPS),
        ])
        r = ribs_section(q, facing)
        if r is not None:
            body = trimesh.boolean.union(
                [body, prism(stranslate(r, x, 0.0), y0, y1)])

        g, _, _ = glyphs.outline(f"{d:+.1f}", P.COUPON_CAP, mirror=False,
                                 along_y=False)
        g = stranslate(g, x, y_text)
        text = g if text is None else unary_union([text, g])

    body = trimesh.boolean.difference(
        [body, flat(text, t - P.TEXT_H, P.TEXT_H + EPS)])
    info = {"cable_d": cable_d, "steps": tuple(steps), "pitch": pitch,
            "plate_w": width, "plate_l": depth, "plans": plans}
    return body, info
