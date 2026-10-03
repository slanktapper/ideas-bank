"""The four printed parts, built from params.py and scroll.py.

Nothing here invents a dimension. If a number appears in this file it is a
facet count or a local construction offset.

HOW IT GOES TOGETHER, bottom to top:

    shell     a fluted tube with a scroll plate for a floor. The part you
              twist, and the outermost thing, because it has to be reachable.
              Three pegs stand on its rim.
    body      a tube inside it: 40 mm bore, two full-height slots, a skirt
              that drops into the shell's bore carrying three lugs, and a
              ring closing its top carrying three more.
    jaw x2    90 mm blades in those slots, with an arm at each end carrying a
              pin. The slot holds a blade sideways; the two pins hold it
              radially and drive it.
    cap       the second scroll plate, pegged to the shell so it turns with
              it, with the spiral cut straight through so you can watch the
              pins travel.

WHY TWO SCROLL PLATES. A 90 mm blade driven by one pin at one end is a drawer
pulled by one corner: the friction of a finger down its length acts about the
driven end and cocks it in its slot. Two plates turning together drive both
ends identically, and the couple never exists.

ASSEMBLY, all of it at full open, which is the only angle where both sets of
lugs line up with their notches:

    1. slide both jaws into the body's slots from outside;
    2. lower the body into the shell -- bottom lugs through the lip notches,
       bottom pins into the outer ends of the grooves;
    3. drop the cap on -- pegs into their holes, lip notches over the body's
       top lugs, top pins into the slots;
    4. twist.

From there the cam holds the jaws radially, the shell's lip holds the body
down, and the body's top ring holds the cap down. It comes apart again at
full open, deliberately, and nowhere else.
"""

from __future__ import annotations

import math

import numpy as np
import trimesh
from shapely.geometry import Polygon

import params as P
import scroll as S

FACETS = 256
NOTCH_ARC = P.LUG_ARC + 2 * P.NOTCH_SLACK      # 36 degrees


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------

def _boolean(op, meshes):
    out = getattr(trimesh.boolean, op)(meshes, engine="manifold")
    return out[0] if isinstance(out, list) else out


def cut(a, *bs):
    return _boolean("difference", [a, *bs])


def fuse(*meshes):
    return _boolean("union", list(meshes))


def keep_both(a, b):
    return _boolean("intersection", [a, b])


def tube(r_in, r_out, z0, z1, sections=FACETS):
    h = z1 - z0
    m = (trimesh.creation.annulus(r_min=r_in, r_max=r_out, height=h,
                                  sections=sections)
         if r_in > 0 else
         trimesh.creation.cylinder(radius=r_out, height=h, sections=sections))
    m.apply_translation((0.0, 0.0, z0 + h / 2.0))
    return m


def bar(length, width, z0, z1, x0=0.0, angle_deg=0.0):
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
    a = np.radians(np.linspace(a0_deg, a1_deg, steps))
    outer = [(r_out * math.cos(t), r_out * math.sin(t)) for t in a]
    inner = [(r_in * math.cos(t), r_in * math.sin(t)) for t in a[::-1]]
    m = trimesh.creation.extrude_polygon(Polygon(outer + inner), z1 - z0)
    m.apply_translation((0.0, 0.0, z0))
    return m


def from_polygon(poly, z0, z1):
    """Extrude a shapely polygon, or a MultiPolygon of several.

    The two grooves never touch -- that is the point of the half-turn
    sweep -- so their union is a MultiPolygon and extrudes piece by piece.
    """
    parts = []
    for g in list(getattr(poly, "geoms", [poly])):
        m = trimesh.creation.extrude_polygon(g, z1 - z0)
        m.apply_translation((0.0, 0.0, z0))
        parts.append(m)
    return parts[0] if len(parts) == 1 else fuse(*parts)


def solidify(mesh):
    """Drop the zero-volume shells a boolean can leave behind.

    Cutting a wedge out of a part slices exactly along faces that are
    already there, and manifold hands back the sliver as a second body. It
    weighs nothing and means nothing, but it is a degenerate shell in the
    STL, so it goes before the file is written.
    """
    pieces = [c for c in mesh.split(only_watertight=False)
              if abs(c.volume) > 1e-6]
    if len(pieces) <= 1:
        return pieces[0] if pieces else mesh
    return trimesh.util.concatenate(pieces)


def spun(mesh, angle_deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(angle_deg), (0, 0, 1)))
    return m


def flipped(mesh):
    """Turn a part over and stand it on the bed."""
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi, (1, 0, 0)))
    m.apply_translation((0.0, 0.0, -m.bounds[0][2]))
    return m


def notches(angles, r_in, r_out, z0, z1):
    return fuse(*[sector(r_in, r_out, a - NOTCH_ARC / 2, a + NOTCH_ARC / 2,
                         z0, z1) for a in angles])


def lugs(angles, r_in, r_out, z0, z1):
    return fuse(*[sector(r_in, r_out, a - P.LUG_ARC / 2, a + P.LUG_ARC / 2,
                         z0, z1) for a in angles])


# ---------------------------------------------------------------------------
# the parts
# ---------------------------------------------------------------------------

def shell(st=None):
    """Fluted tube, scroll plate for a floor, three pegs on the rim."""
    st = st or P.STACK
    r_out = P.OVERALL_D / 2.0

    solid = fuse(tube(P.RING_ID / 2, r_out, st.ring_0, st.ring_top),
                 tube(P.WALL_ID / 2, r_out, st.ring_0, st.wall_top))

    # the pocket under the inner lip, and the notches the body's lugs pass
    # through on the way in
    solid = cut(solid, tube(P.RING_ID / 2 - 0.5, P.LIP_R_OUT,
                            st.ring_0 - 0.5, P.LIP_Z0))
    solid = cut(solid, notches(P.LUG_ANGLES, P.RING_ID / 2 - 0.5,
                               P.LIP_R_OUT + 0.3, P.LIP_Z0 - 0.5,
                               st.ring_top + 0.5))

    # the spirals, blind in the floor
    solid = cut(solid, from_polygon(S.grooves_polygon(),
                                    st.groove_floor, st.ring_top + 1.0))

    # flutes for grip, the full height of the wall
    flute_r = r_out + P.FLUTE_D / 2.0 - P.FLUTE_DEPTH
    solid = cut(solid, fuse(*[
        post(P.FLUTE_D, st.ring_0 - 0.5, st.wall_top + 0.5, at_r=flute_r,
             angle_deg=360.0 / P.FLUTE_COUNT * k, sections=24)
        for k in range(P.FLUTE_COUNT)]))

    # the pegs the cap sits on. Three, on the same uneven angles as the lugs,
    # so the cap goes on exactly one way round and its spiral lines up with
    # this one.
    solid = fuse(solid, *[
        post(P.PEG_D, st.wall_top - 0.01, st.wall_top + P.PEG_H,
             at_r=P.PEG_R, angle_deg=a) for a in P.LUG_ANGLES])
    return solid


def body(st=None):
    """The inner tube: bore, two slots, a skirt below and a ring above.

    Three diameters up its height, and each one is forced. The skirt is thin
    enough to turn inside the shell's bore; the middle is thicker, because
    90 mm of unsupported tube is the one thing here that can flex, and its
    step at the shell's floor is the shoulder the whole body stands on; the
    neck at the top is thin again to let the cap's hook ring pass outside it.
    """
    st = st or P.STACK
    solid = fuse(
        tube(P.BORE_D / 2, P.SKIRT_OD / 2, st.ring_0, st.ring_top),
        tube(P.BORE_D / 2, P.BODY_ARC_R_OUT, st.ring_top, st.arc_top),
        tube(P.BORE_D / 2, P.SKIRT_OD / 2, st.arc_top, st.topring_0),
        tube(P.BORE_D / 2, P.SKIRT_OD / 2, st.topring_0, st.topring_1),
        lugs(P.LUG_ANGLES, P.SKIRT_OD / 2 - 0.2, P.LUG_R_OUT,
             st.lug_z0, st.lug_z1),
        # the top lugs the cap's hook catches under
        lugs(P.TOP_LUG_ANGLES, P.SKIRT_OD / 2 - 0.2, P.TOP_LUG_OUT,
             st.topring_0, st.topring_1))

    solid = cut(solid, tube(0.0, P.BORE_D / 2, st.ring_0 - 1.0,
                            st.topring_1 + 1.0))

    # The two slots stop at the top of the blades, so everything above is a
    # closed hoop tying the two arc walls together.
    reach = P.OVERALL_D
    solid = cut(solid, bar(2 * reach, P.SLOT_W, st.ring_top, st.arc_top,
                           x0=-reach))
    return solid


def cap(st=None):
    """The top scroll plate: spiral cut through, pegged to the shell.

    Its hook ring reaches in under the body's top lugs. That is what holds
    the cap down -- and the cap has to be held down, because a finger pulled
    out of a shut jaw drags the blades up against it.
    """
    st = st or P.STACK
    solid = tube(P.CAP_HOOK_R_IN, P.OVERALL_D / 2, st.cap_0, st.cap_top)

    # open the middle above the hook, so the body's top ring can sit in it
    solid = cut(solid, tube(P.CAP_HOOK_R_IN - 0.5, P.CAP_HOOK_R_OUT,
                            st.cap_hook_1, st.cap_top + 0.5))
    # notches the body's top lugs pass down through on the way together
    solid = cut(solid, notches(P.TOP_LUG_ANGLES, P.CAP_HOOK_R_IN - 0.5,
                               P.CAP_HOOK_R_OUT + 0.3, st.cap_0 - 0.5,
                               st.cap_hook_1 + 0.5))

    # the spiral, straight through, so the pins are visible travelling
    solid = cut(solid, from_polygon(S.grooves_polygon(),
                                    st.cap_0 - 0.5, st.cap_top + 0.5))
    solid = cut(solid, fuse(*[
        post(P.PEG_D + 2 * P.FIT_FREE, st.cap_0 - 0.5, st.cap_top + 0.5,
             at_r=P.PEG_R, angle_deg=a) for a in P.LUG_ANGLES]))
    return solid


def jaw(phi=0.0, index=0, st=None):
    """One blade, placed for a given twist.

    A face plate the height of the grip, an arm at each end carrying a pin,
    and a rib joining them. The rib is what stops the arms working as two
    independent cantilevers.
    """
    st = st or P.STACK
    r_face = S.jaw_face_radius(phi)

    solid = fuse(
        bar(P.FACE_T, P.JAW_W, st.jaw_0, st.jaw_top),
        bar(P.JAW_L, P.JAW_W, st.jaw_0, st.jaw_0 + P.ARM_H),
        bar(P.JAW_L, P.JAW_W, st.jaw_top - P.ARM_H, st.jaw_top),
        bar(P.JAW_L, P.RIB_W, st.jaw_0, st.jaw_top),
        post(P.PIN_D, st.pin_bot_0, st.jaw_0, at_r=P.PIN_OFFSET),
        post(P.PIN_D, st.jaw_top, st.pin_top_1, at_r=P.PIN_OFFSET))

    solid.apply_translation((r_face, 0.0, 0.0))
    return spun(solid, S.JAW_ANGLES[index])


# ---------------------------------------------------------------------------
# assemblies
# ---------------------------------------------------------------------------

def assembly(phi=0.0, st=None):
    """Every part in the pose it is in at a given twist."""
    st = st or P.STACK
    return [
        {"mesh": spun(shell(st), phi), "color": P.COL_SHELL, "name": "shell"},
        {"mesh": spun(cap(st), phi), "color": P.COL_CAP, "name": "cap"},
        {"mesh": body(st), "color": P.COL_BODY, "name": "body"},
        *[{"mesh": jaw(phi, k, st), "color": P.COL_JAW, "name": f"jaw{k}"}
          for k in range(P.JAW_COUNT)],
    ]


def printable(st=None):
    """Each distinct part once, oriented as it should be printed.

    shell  as modelled: every cavity opens to the sky
    body   as modelled: a tube standing on its skirt
    cap    turned over, so the pocket under its lip opens upward instead of
           overhanging 5 mm inward
    jaw    turned over. Upside down, the one face that bears on anything --
           the underside of the bottom arm, which rides on the shell's
           floor -- prints as a top surface, and the pin that runs in the
           shell's groove prints as a vertical cylinder. The support this
           needs lands under the TOP arm, which touches nothing.
    """
    st = st or P.STACK
    j = jaw(0.0, 0, st)
    j.apply_translation((-S.jaw_face_radius(0.0), 0.0, 0.0))
    return {"shell": shell(st), "body": body(st),
            "cap": flipped(cap(st)), "jaw": flipped(j)}


# ---------------------------------------------------------------------------
# the fit-test coupon
# ---------------------------------------------------------------------------

COUPON_ARC = 50.0
COUPON_GRIP = 25.0         # a short-grip version of the whole mechanism


def coupon():
    """A short, narrow wedge of the real object, to spend an hour instead of
    most of a day finding out whether the clearances are right.

    Everything that slides here is plastic on plastic at a clearance that is
    currently a guess. This is the same model with the grip shortened and a
    50 degree wedge taken out of it, cut FROM the finished meshes rather than
    built to resemble them, so the walls, the groove floor and every overhang
    are exactly what the real part would print.

    It carries every fit at once: pin in groove at both ends, blade in slot,
    lugs under both lips, body on the shell's bore.
    """
    st = P.stack(COUPON_GRIP)
    wedge = sector(0.0, P.OVERALL_D, -COUPON_ARC / 2, COUPON_ARC / 2,
                   -2.0, st.overall_h + 2.0)
    out = {
        "coupon-shell": solidify(keep_both(shell(st), wedge)),
        "coupon-body": solidify(keep_both(body(st), wedge)),
        "coupon-cap": flipped(solidify(keep_both(cap(st), wedge))),
        "coupon-jaw": flipped(jaw(0.0, 0, st)),
    }
    out["coupon-jaw"].apply_translation((-S.jaw_face_radius(0.0), 0.0, 0.0))
    return out
