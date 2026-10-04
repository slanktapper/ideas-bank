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


def ratchet_ring(st):
    """The toothed collar on top of the cap.

    A sawtooth: over each tooth the surface ramps outward from the crest to
    the valley, then drops back to the crest at a radial wall. Which way
    that lets it turn is worth deriving rather than guessing.

    The post is fixed, so in the COLLAR's own frame it travels backwards as
    the shell turns to close. Going backwards along this profile the nose
    rides gently outward up a ramp, then falls off a wall into the next
    valley -- that is the click, and it is free. Going the other way the
    nose meets that wall head on and stops. Closing is backwards along the
    profile, so closing clicks and opening locks.
    """
    from shapely.geometry import Polygon

    pitch = 360.0 / P.RATCHET_TEETH
    inner = []
    for i in range(P.RATCHET_TEETH):
        for f in np.linspace(0.0, 1.0, 40, endpoint=False):
            psi = (i + f) * pitch
            a, r = math.radians(psi), S.tooth_radius(psi)
            inner.append((r * math.cos(a), r * math.sin(a)))
    outer = [(P.COLLAR_R_OUT * math.cos(math.radians(d)),
              P.COLLAR_R_OUT * math.sin(math.radians(d)))
             for d in np.linspace(0, 360, 361)[:-1]]
    return from_polygon(Polygon(outer, [inner[::-1]]), st.collar_0, st.collar_1)


def pawl_post(st):
    """The springy post on the body, its nose, and the pad you press.

    One cantilever. Press the pad inward, the nose comes off the teeth, and
    the shell twists back freely. It stands on a boss on the body's top
    ring, so it prints standing up with everything else.
    """
    post = bar(P.POST_R_OUT - P.POST_R_IN, P.POST_W, st.topring_1,
               st.post_top, x0=P.POST_R_IN)
    nose = bar(P.NOSE_R - P.POST_R_OUT + 0.2, P.NOSE_W, st.nose_0, st.nose_1,
               x0=P.POST_R_OUT - 0.2)
    pad = bar(P.POST_R_OUT - P.POST_R_IN, P.PAD_W,
              st.post_top - P.PAD_T, st.post_top, x0=P.POST_R_IN)
    boss = sector(P.SKIRT_OD / 2 - 0.2, P.POST_BOSS_R_OUT,
                  -P.POST_BOSS_ARC / 2, P.POST_BOSS_ARC / 2,
                  st.topring_0, st.topring_1)
    return spun(fuse(post, nose, pad, boss), P.PAWL_ANGLE)


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


def body(st=None, with_post=True):
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
             st.topring_0, st.topring_1),
        *([pawl_post(st)] if with_post else []))

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

    # the ratchet collar, standing on the cap's top face
    solid = fuse(solid, ratchet_ring(st))
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

    # Trim the tail to an arc about the axis, as it would be at full open.
    # A wide blade's square corners reach further out than its end does and
    # would otherwise clip the shell wall. Cutting it here rather than in
    # the assembled frame means the trim travels inward with the blade.
    solid = keep_both(solid, post(
        2 * P.JAW_TAIL_R_MAX, st.pin_bot_0 - 1.0, st.pin_top_1 + 1.0,
        at_r=P.BORE_D / 2, angle_deg=180.0, sections=FACETS))

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

# Wide enough to take in a slot WALL, not just the slot. A 26 mm blade's
# slot is 84 degrees of the bore on its own, so a narrow wedge centred on it
# contains no slot wall at all -- and a coupon with nothing to hold the
# blade sideways tests nothing, and falls into two pieces besides.
COUPON_ARC = 120.0
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


# ---------------------------------------------------------------------------
# the fit comb: the cheapest print that settles the guessed numbers
# ---------------------------------------------------------------------------
# Two numbers in params.py are guesses that only a printer can settle, and
# both of them are expensive to get wrong in a 77 g coupon, let alone a 374 g
# set:
#
#   FIT_SLIDE  -- the clearance everything slides on. Too tight and the
#                 mechanism binds; too loose and it rattles.
#   the pawl post's thickness -- which sets the click force, and goes as the
#                 CUBE of nothing else changing.
#
# So print these first. A few grams, a few minutes, and they turn both
# guesses into measurements before any of the real geometry is committed.

COMB_CLEARANCES = (0.25, 0.30, 0.35, 0.40, 0.45)
COMB_POST_T = (0.8, 0.9, 1.0, 1.1)
COMB_TICK = 1.2


def _comb_ticks(n, x, y, z0, z1, pitch=2.6):
    """n notches, so a cell can be identified without reading anything."""
    return fuse(*[
        trimesh.creation.box(extents=(COMB_TICK, 2.4, z1 - z0 + 1.0),
                             transform=trimesh.transformations.translation_matrix(
                                 (x + k * pitch, y, (z0 + z1) / 2)))
        for k in range(n)])


def comb_grooves():
    """Five arcs of the real spiral, cut at five clearances.

    Taken from the INNER end of the spiral, where it curves most tightly and
    a round pin in a swept slot binds soonest. A straight test slot would
    pass at a clearance the real groove fails at.
    """
    pts = []
    for t in np.linspace(0.0, 45.0, 120):
        r = P.R_PIN_IN + P.JAW_TRAVEL * t / P.TWIST_SWEEP
        a = math.radians(t)
        pts.append((r * math.cos(a), r * math.sin(a)))
    pts = np.asarray(pts)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    cell_w, cell_h = (hi[0] - lo[0]) + 9.0, (hi[1] - lo[1]) + 9.0

    plate = trimesh.creation.box(
        extents=(cell_w * len(COMB_CLEARANCES), cell_h, P.RING_T))
    plate.apply_translation((cell_w * len(COMB_CLEARANCES) / 2, cell_h / 2,
                             P.RING_T / 2))

    from shapely.geometry import LineString
    cuts = []
    for i, clear in enumerate(COMB_CLEARANCES):
        shifted = pts - lo + np.array([i * cell_w + 4.5, 4.5])
        poly = LineString(shifted).buffer(
            (P.PIN_D + 2 * clear) / 2, cap_style=2, join_style=2, resolution=16)
        cuts.append(from_polygon(poly, P.RING_FLOOR, P.RING_T + 1.0))
        cuts.append(_comb_ticks(i + 1, i * cell_w + 3.0, 1.2,
                                P.RING_T - 1.0, P.RING_T))
    return cut(plate, fuse(*cuts))


def comb_pin():
    """The real pin, on something to hold it by."""
    knob = post(12.0, 0.0, 5.0)
    pin = post(P.PIN_D, 5.0, 5.0 + P.PIN_LEN)
    return fuse(knob, pin)


def comb_springs():
    """Four pawl posts at four thicknesses, each with a stop 0.8 mm away.

    Press each one until it meets its stop -- that is exactly the deflection
    a tooth asks for -- and keep the one that feels like a firm click rather
    than a vague one or a wall. Then put its thickness into params.py as
    POST_R_OUT - POST_R_IN.
    """
    st = P.STACK
    h = st.post_top - st.topring_1
    nose_0 = st.nose_0 - st.topring_1
    base_t = 4.0
    pitch = 16.0

    parts_ = [trimesh.creation.box(extents=(pitch * len(COMB_POST_T), 22.0,
                                            base_t))]
    parts_[0].apply_translation((pitch * len(COMB_POST_T) / 2, 11.0,
                                 base_t / 2))
    for i, t in enumerate(COMB_POST_T):
        x = i * pitch + pitch / 2
        col = trimesh.creation.box(extents=(t, P.POST_W, h))
        col.apply_translation((x, 8.0, base_t + h / 2))
        nose = trimesh.creation.box(
            extents=(t + (P.NOSE_R - P.POST_R_OUT), P.NOSE_W, P.NOSE_H))
        nose.apply_translation((x + (P.NOSE_R - P.POST_R_OUT) / 2, 8.0,
                                base_t + (nose_0 + P.NOSE_H / 2)))
        # the stop: a wall exactly one tooth's depth from the post's face
        stop = trimesh.creation.box(extents=(3.0, 8.0, nose_0 + P.NOSE_H))
        stop.apply_translation((x - t / 2 - P.RATCHET_DEPTH - 1.5, 8.0,
                                base_t + (nose_0 + P.NOSE_H) / 2))
        parts_ += [col, nose, stop]
    solid = fuse(*parts_)
    return cut(solid, fuse(*[_comb_ticks(i + 1, i * pitch + 2.0, 19.0,
                                         base_t - 1.0, base_t)
                             for i in range(len(COMB_POST_T))]))


def fit_comb():
    return {"comb-grooves": comb_grooves(),
            "comb-pin": comb_pin(),
            "comb-springs": comb_springs()}


# ---------------------------------------------------------------------------
# the flat-printing blade, and its dowels
# ---------------------------------------------------------------------------

def _teardrop(d, z0, z1, at_r):
    """A hole that prints cleanly with its axis horizontal.

    Circle, with the sector facing the print's "up" replaced by a 45 degree
    peak. Lying flat, the blade's socket axis is horizontal and the roof of a
    plain round hole droops into the bore; a peak over it is self-supporting,
    and a round dowel never touches it.

    Drawn as ONE closed outline rather than a circle unioned with a triangle.
    The triangle of the textbook teardrop meets the circle at exactly two
    points, and a union that touches rather than overlaps pinches the polygon
    there -- it extrudes to something that is not a solid, and every boolean
    after it fails with "not all meshes are volumes".
    """
    from shapely.geometry import Polygon

    r = d / 2.0
    pts = [(r * math.cos(a), r * math.sin(a))
           for a in np.radians(np.linspace(45.0, 315.0, 64))]
    pts.append((r * math.sqrt(2.0), 0.0))          # the 45 degree peak
    m = from_polygon(Polygon(pts), z0, z1)
    m.apply_translation((at_r, 0.0, 0.0))
    return m


def jaw_socketed(phi=0.0, index=0, st=None):
    """The blade with blind sockets where the pins were."""
    st = st or P.STACK
    solid = fuse(
        bar(P.FACE_T, P.JAW_W, st.jaw_0, st.jaw_top),
        bar(P.JAW_L, P.JAW_W, st.jaw_0, st.jaw_0 + P.ARM_H),
        bar(P.JAW_L, P.JAW_W, st.jaw_top - P.ARM_H, st.jaw_top),
        bar(P.JAW_L, P.RIB_W, st.jaw_0, st.jaw_top))
    solid = keep_both(solid, post(
        2 * P.JAW_TAIL_R_MAX, st.jaw_0 - 1.0, st.jaw_top + 1.0,
        at_r=P.BORE_D / 2, angle_deg=180.0, sections=FACETS))
    solid = cut(solid,
                _teardrop(P.PIN_D, st.jaw_0 - 0.01,
                          st.jaw_0 + P.SOCKET_DEPTH, P.PIN_OFFSET),
                _teardrop(P.PIN_D, st.jaw_top - P.SOCKET_DEPTH,
                          st.jaw_top + 0.01, P.PIN_OFFSET))
    solid.apply_translation((S.jaw_face_radius(phi), 0.0, 0.0))
    return spun(solid, S.JAW_ANGLES[index])


def dowel():
    """One pin, printed standing up: the most accurate thing a printer makes.

    Bottoms out in its blind socket, so the 4.3 mm that stands proud is set
    by the geometry rather than by how hard it was pressed.
    """
    return post(P.PIN_D, 0.0, P.DOWEL_L, sections=96)


def jaw_flat():
    """The blade laid on its face, with its dowels beside it on one plate.

    Flat, the rib and both arms rise straight off the face plate, so the
    whole blade prints without a scrap of support. The face that lands on
    the build plate is the one that touches a finger.
    """
    st = P.STACK
    blade = jaw_socketed(0.0, 0, st)
    blade.apply_translation((-S.jaw_face_radius(0.0), 0.0, 0.0))
    blade.apply_transform(trimesh.transformations.rotation_matrix(
        -math.pi / 2, (0, 1, 0)))
    blade.apply_translation((0.0, 0.0, -blade.bounds[0][2]))
    blade.apply_translation((-blade.bounds[0][0], -blade.centroid[1], 0.0))

    pins = []
    x = blade.bounds[1][0] + 9.0
    for k in range(P.JAW_COUNT + P.DOWEL_SPARES):
        d = dowel()
        d.apply_translation((x + k * (P.PIN_D + 5.0), 0.0, 0.0))
        pins.append(d)
    return trimesh.util.concatenate([blade, *pins])


# ---------------------------------------------------------------------------
# the dowel comb
# ---------------------------------------------------------------------------

DOWEL_COMB_PITCH = 13.0
DOWEL_COMB_CENTRE = 7.0        # socket axis, above the bed


def _teardrop_sideways(d, length, x, z):
    """A teardrop socket lying on its side, peak upward.

    The socket has to be printed the way the real one is -- axis horizontal,
    roof bridging over the bore -- because that orientation is the whole
    reason it is a teardrop and the whole reason its printed size is not its
    drawn size. A socket test printed with the axis vertical would come out
    round, fit perfectly, and tell you nothing.
    """
    from shapely.geometry import Polygon

    r = d / 2.0
    # The arc covers the 270 degrees AWAY from the peak, so the apex closes
    # it between the two ends. Run it the other way and the apex connects
    # across the middle: a self-intersecting outline that extrudes to
    # something that is not a solid.
    pts = [(r * math.cos(a), r * math.sin(a))
           for a in np.radians(np.linspace(135.0, 405.0, 64))]
    pts.append((0.0, r * math.sqrt(2.0)))          # peak, toward +y
    m = trimesh.creation.extrude_polygon(Polygon(pts), length)
    # +90 about x: the extrusion axis turns into -y, and the peak turns up
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    m.apply_translation((x, length, z))
    return m


def dowel_comb():
    """Five dowels either side of nominal, and five real sockets for them.

    The block reproduces the arm's section around a socket exactly: the same
    5 mm blind depth, the same 1 mm of floor behind it, and the same ~1 mm of
    material over the teardrop's peak. What it does NOT reproduce is the
    29 mm of blade below the socket, which costs plastic and changes nothing
    about how a horizontal hole prints.
    """
    r = P.PIN_D / 2.0
    height = DOWEL_COMB_CENTRE + r * math.sqrt(2.0) + 0.96
    depth = P.SOCKET_DEPTH + 1.0                   # 5 mm socket, 1 mm floor
    width = DOWEL_COMB_PITCH * len(P.DOWEL_TEST_D)

    block = trimesh.creation.box(extents=(width, depth, height))
    block.apply_translation((width / 2, depth / 2, height / 2))

    cuts, pins = [], []
    for i, d in enumerate(P.DOWEL_TEST_D):
        x = i * DOWEL_COMB_PITCH + DOWEL_COMB_PITCH / 2
        # every socket is the DESIGN size; it is the dowels that vary
        cuts.append(_teardrop_sideways(P.PIN_D, P.SOCKET_DEPTH + 0.01, x,
                                       DOWEL_COMB_CENTRE))
        cuts.append(_comb_ticks(i + 1, x - 3.0, depth - 1.4,
                                height - 1.0, height))

        pin = post(d, 0.0, P.DOWEL_L, sections=96)
        pin.apply_translation((x, depth + 11.0, 0.0))
        # dimples on the top face, counting the size
        marks = [post(0.9, P.DOWEL_L - 0.6, P.DOWEL_L + 0.5,
                      at_r=1.45, angle_deg=90.0 + k * 40.0, sections=16)
                 for k in range(i + 1)]
        for m in marks:
            m.apply_translation((x, depth + 11.0, 0.0))
        pins.append(cut(pin, fuse(*marks)) if marks else pin)

    return trimesh.util.concatenate([cut(block, fuse(*cuts)), *pins])
