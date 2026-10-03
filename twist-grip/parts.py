"""The four printed parts, built from params.py and scroll.py.

Nothing here invents a dimension. If a number appears in this file it is
either a count of facets or a local construction offset that cannot be wrong
by more than it is obvious.

HOW IT GOES TOGETHER, bottom to top:

    ring      a flat annulus with the two spiral grooves in its top face and
              a fluted wall standing up round the outside. This is the part
              you twist, and it is the outermost thing on the object because
              it has to be reachable.
    jaw x2    ride on the ring's top face, in channels cut through the body
              plate. A pin under each one hangs down into a groove. The
              channel holds the jaw tangentially, the groove holds it
              radially, and the channel's lid stops it lifting and taking
              its pin out of the groove.
    body      the plate those channels are cut in, plus a skirt that drops
              down through the ring's bore and carries three lugs. The lugs
              hook under a lip inside the ring, which is what holds the
              whole stack together -- no screws, no snaps, nothing glued.

ASSEMBLY. Slide both jaws into their channels from outside. Bring the ring
up over the skirt with its lip notches over the lugs and the grooves' outer
ends under the pins, then twist. Once the pins are in the grooves the jaws
cannot come back out radially -- the cam is holding them -- and once the ring
is off the notches the body cannot lift off. It comes apart again at full
open, deliberately; see direction.md on making that harder.
"""

from __future__ import annotations

import math

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

import params as P
import scroll as S

FACETS = 256


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------

def _boolean(op, meshes):
    out = getattr(trimesh.boolean, op)(meshes, engine="manifold")
    if isinstance(out, list):
        out = out[0]
    return out


def cut(a, *bs):
    return _boolean("difference", [a, *bs])


def fuse(*meshes):
    return _boolean("union", list(meshes))


def keep_both(a, b):
    return _boolean("intersection", [a, b])


def tube(r_in: float, r_out: float, z0: float, z1: float, sections=FACETS):
    """An annular wall. r_in of 0 gives a plain cylinder."""
    h = z1 - z0
    m = (trimesh.creation.annulus(r_min=r_in, r_max=r_out, height=h,
                                  sections=sections)
         if r_in > 0 else
         trimesh.creation.cylinder(radius=r_out, height=h, sections=sections))
    m.apply_translation((0.0, 0.0, z0 + h / 2.0))
    return m


def bar(length, width, z0, z1, x0=0.0, angle_deg=0.0):
    """A rectangular bar lying along a radius, x0 at its inner end."""
    m = trimesh.creation.box(extents=(length, width, z1 - z0))
    m.apply_translation((x0 + length / 2.0, 0.0, (z0 + z1) / 2.0))
    if angle_deg:
        m.apply_transform(trimesh.transformations.rotation_matrix(
            math.radians(angle_deg), (0, 0, 1)))
    return m


def post(d, z0, z1, at_r=0.0, angle_deg=0.0, sections=64):
    m = trimesh.creation.cylinder(radius=d / 2.0, height=z1 - z0,
                                 sections=sections)
    a = math.radians(angle_deg)
    m.apply_translation((at_r * math.cos(a), at_r * math.sin(a),
                         (z0 + z1) / 2.0))
    return m


def sector(r_in, r_out, a0_deg, a1_deg, z0, z1, steps=48):
    """An annular wedge -- used for the lugs and their notches."""
    a = np.radians(np.linspace(a0_deg, a1_deg, steps))
    outer = [(r_out * math.cos(t), r_out * math.sin(t)) for t in a]
    inner = [(r_in * math.cos(t), r_in * math.sin(t)) for t in a[::-1]]
    m = trimesh.creation.extrude_polygon(Polygon(outer + inner), z1 - z0)
    m.apply_translation((0.0, 0.0, z0))
    return m


def from_polygon(poly, z0, z1):
    """Extrude a shapely polygon, or a MultiPolygon of several.

    The two grooves never touch -- that is the point of the half-turn
    sweep -- so their union comes back as a MultiPolygon and has to be
    extruded piece by piece.
    """
    geoms = list(getattr(poly, "geoms", [poly]))
    parts = []
    for g in geoms:
        m = trimesh.creation.extrude_polygon(g, z1 - z0)
        m.apply_translation((0.0, 0.0, z0))
        parts.append(m)
    return parts[0] if len(parts) == 1 else fuse(*parts)


def spun(mesh, angle_deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(angle_deg), (0, 0, 1)))
    return m


# ---------------------------------------------------------------------------
# the lugs and the notches they pass through
# ---------------------------------------------------------------------------
# The lugs stand on the skirt; the notches are the gaps in the ring's lip
# they drop through during assembly. One set of angles defines both, which
# is the only way they are guaranteed to line up.

NOTCH_ARC = P.LUG_ARC + 2 * P.NOTCH_SLACK      # 36 degrees


def body_lugs():
    """Three ledges on the skirt that hook under the ring's lip."""
    return fuse(*[
        sector(P.SKIRT_OD / 2 - 0.2, P.LUG_R_OUT,
               a - P.LUG_ARC / 2, a + P.LUG_ARC / 2,
               P.LUG_Z0, P.LUG_Z1)
        for a in P.LUG_ANGLES])


def ring_notches():
    """The gaps in the lip the lugs drop through, at the same three angles.

    One list of angles defines the lugs and the notches both, which is the
    only way they are guaranteed to line up. Because those angles are
    unevenly spaced (see params.py), the ring lines all three up only when it
    is at full open -- so in use the lugs are always under solid lip.
    """
    return fuse(*[
        sector(P.RING_ID / 2 - 0.5, P.LIP_R_OUT + 0.3,
               a - NOTCH_ARC / 2, a + NOTCH_ARC / 2,
               P.LIP_Z0 - 0.5, P.RING_T + 0.5)
        for a in P.LUG_ANGLES])


# ---------------------------------------------------------------------------
# the parts
# ---------------------------------------------------------------------------

def ring():
    """The twist ring: grooves in its face, flutes on its wall."""
    r_out = P.OVERALL_D / 2.0
    solid = tube(P.RING_ID / 2, r_out, P.Z_RING_0, P.Z_RING_TOP)

    # the wall you actually hold
    solid = fuse(solid, tube(P.WALL_ID / 2, r_out, P.Z_RING_0, P.WALL_H))

    # the pocket under the inner lip, which the lugs swing through
    solid = cut(solid, tube(P.RING_ID / 2 - 0.5, P.LIP_R_OUT,
                            P.Z_RING_0 - 0.5, P.LIP_Z0))

    solid = cut(solid, ring_notches())

    # the two spiral grooves
    solid = cut(solid, from_polygon(S.grooves_polygon(),
                                    P.Z_GROOVE_FLOOR, P.Z_RING_TOP + 1.0))

    # flutes, for grip
    flute_r = r_out + P.FLUTE_D / 2.0 - P.FLUTE_DEPTH
    solid = cut(solid, fuse(*[
        post(P.FLUTE_D, P.Z_RING_0 - 0.5, P.WALL_H + 0.5, at_r=flute_r,
             angle_deg=360.0 / P.FLUTE_COUNT * k, sections=24)
        for k in range(P.FLUTE_COUNT)]))
    return solid


def body():
    """The plate the jaws slide in, its skirt, and the lugs."""
    plate = tube(0.0, P.PLATE_OD / 2, P.Z_PLATE_0, P.Z_PLATE_TOP)
    solid = fuse(plate,
                 tube(P.SKIRT_ID / 2, P.SKIRT_OD / 2, P.SKIRT_Z0, P.Z_PLATE_0),
                 body_lugs())

    # the finger bore, all the way through
    solid = cut(solid, tube(0.0, P.BORE_D / 2,
                            P.SKIRT_Z0 - 1.0, P.Z_PLATE_TOP + 1.0))

    # the jaw channels. The two jaws are diametrically opposite, so one bar
    # through the middle cuts both. Wide below, narrow above: the step is the
    # lid that keeps a jaw down in its channel.
    reach = P.PLATE_OD / 2 + 2.0
    solid = cut(solid,
                bar(2 * reach, P.SLOT_W, P.Z_PLATE_0 - 0.5, P.Z_LID_0,
                    x0=-reach),
                bar(2 * reach, P.WINDOW_W, P.Z_LID_0, P.Z_PLATE_TOP + 0.5,
                    x0=-reach))
    return solid


def jaw(phi: float = 0.0, index: int = 0):
    """One jaw, placed for a given twist angle."""
    r_face = S.jaw_face_radius(phi)

    base = bar(P.JAW_L, P.JAW_W, P.Z_JAW_0, P.Z_JAW_0 + P.JAW_H)
    pad = bar(P.PAD_L, P.PAD_W, P.Z_JAW_0, P.Z_PAD_TOP)
    pin = post(P.PIN_D, P.Z_PIN_BASE, P.Z_JAW_0, at_r=P.PIN_OFFSET)
    solid = fuse(base, pad, pin)

    solid.apply_translation((r_face, 0.0, 0.0))
    return spun(solid, S.JAW_ANGLES[index])


# ---------------------------------------------------------------------------
# the assembly, for renders and for interference checks
# ---------------------------------------------------------------------------

def assembly(phi: float = 0.0):
    """Every part in the pose it is in at a given twist."""
    return [
        {"mesh": spun(ring(), phi), "color": P.COL_RING, "name": "ring"},
        {"mesh": body(), "color": P.COL_BODY, "name": "body"},
        *[{"mesh": jaw(phi, k), "color": P.COL_JAW, "name": f"jaw{k}"}
          for k in range(P.JAW_COUNT)],
    ]


def printable():
    """Each distinct part once, oriented as it should be printed.

    ring   grooves and wall upward -- every cavity opens to the sky
    body   top face DOWN, so the channel lid prints over a gap that is
           already there rather than bridging one, and the skirt points up
    jaw    pin upward, flat on its base
    """
    r = ring()

    b = body()
    b.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi, (1, 0, 0)))
    b.apply_translation((0.0, 0.0, -b.bounds[0][2]))

    j = jaw(0.0, 0)
    j.apply_translation((-S.jaw_face_radius(0.0), 0.0, 0.0))
    j.apply_translation((0.0, 0.0, -j.bounds[0][2]))

    return {"ring": r, "body": b, "jaw": j}


# ---------------------------------------------------------------------------
# the fit-test coupon
# ---------------------------------------------------------------------------

COUPON_ARC = 50.0          # degrees, centred on jaw 0


def coupon():
    """A wedge of the real object, for a 25-minute print instead of a 4-hour one.

    Every clearance in this design is a guess until something has come off
    the printer: the pin in its groove, the jaw in its channel, the lug under
    its lip, the ring on its skirt. All four of those meet within 25 degrees
    either side of jaw 0 -- which is also where a lug is -- so a wedge there
    tests the lot.

    Cut FROM the finished meshes rather than built to resemble them, so what
    gets printed is exactly what the real part would be: same walls, same
    groove floor, same lid, same overhangs. The wedge gives about 25 degrees
    of twist, enough to feel whether it binds.
    """
    wedge = sector(0.0, P.OVERALL_D, -COUPON_ARC / 2, COUPON_ARC / 2,
                   -2.0, P.WALL_H + 2.0)
    out = {
        "coupon-ring": keep_both(ring(), wedge),
        "coupon-body": keep_both(body(), wedge),
        "coupon-jaw": jaw(0.0, 0),
    }
    out["coupon-jaw"].apply_translation((-S.jaw_face_radius(0.0), 0.0, 0.0))
    return out
