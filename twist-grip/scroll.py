"""The scroll: how twisting the ring moves the jaws.

A scroll chuck in two jaws. The ring carries two Archimedean spiral grooves;
a pin under each jaw rides one of them; the jaw itself can only move radially
because its channel in the body plate holds it. Turn the ring and the groove
walks the pin in or out.

WHY THE SWEEP IS HALF A TURN. The jaws sit 180 degrees apart, so as the ring
turns through phi each pin moves backwards through the ring's own frame by
phi. Over a sweep of exactly 180 degrees, jaw 1's pin covers ring angles
[180, 0] while jaw 0's covers [360, 180] -- the two halves of the face, with
no overlap at all. Both grooves are then the same spiral arc, one placed at
0 and one at 180, and they can never collide because wherever they share an
angle they are a full 20 mm apart in radius.

Any other sweep gives two spirals that overlap in angle and have to be
interleaved with the radial separation that falls out of the arithmetic:
20 * 180 / sweep millimetres. At 360 degrees that is 10 mm -- still fine, but
a full turn of a ring is not one wrist movement. Below 180 it grows past the
20 mm band the travel itself needs, so the ring gets bigger for no gain.

SIGNS. phi is the twist, 0 open and TWIST_SWEEP shut. Positive ring angles
are anticlockwise seen from above, the same sense as phi.
"""

from __future__ import annotations

import math

import numpy as np

import params as P

# Where the jaws sit, as absolute angles. Two jaws, so diametrically opposed.
JAW_ANGLES = tuple(180.0 * k for k in range(P.JAW_COUNT))


def groove_offset(jaw: int) -> float:
    """Where jaw k's groove arc is placed on the ring's face.

    Worth deriving rather than guessing, because guessing it wrong puts a
    pin 48 mm from the groove meant to drive it and the ring still looks
    right -- the two grooves together are symmetric under a half turn, so
    the SOLID is identical either way and only the kinematics disagree.

    The arc is parameterised from shut to open: r(t) = R_PIN_IN at t=0 and
    R_PIN_OUT at t=TWIST_SWEEP. A pin is at radius pin_radius(phi), which is
    R_PIN_OUT when phi=0, so t = TWIST_SWEEP - phi. The pin's angle in the
    ring's frame is JAW_ANGLES[k] - phi. Setting those equal:

        psi = t + (JAW_ANGLES[k] - TWIST_SWEEP)

    so the arc is offset by JAW_ANGLES[k] - TWIST_SWEEP, not by JAW_ANGLES[k].
    test_fit.py checks the pin against its own groove over the whole sweep.
    """
    return JAW_ANGLES[jaw] - P.TWIST_SWEEP


# ---------------------------------------------------------------------------
# kinematics
# ---------------------------------------------------------------------------

def fraction(phi: float) -> float:
    """How far through its travel the mechanism is, 0 open and 1 shut."""
    return phi / P.TWIST_SWEEP


def jaw_face_radius(phi: float) -> float:
    """Where a jaw's contact face is, as a radius from the axis.

    BORE_D/2 when open -- flush with the bore, so the opening is a clean
    circle -- and 0 when shut, which is the two faces meeting on the axis.
    """
    return (P.BORE_D / 2.0) * (1.0 - fraction(phi))


def pin_radius(phi: float) -> float:
    """Where that jaw's pin is. The face plus the fixed offset behind it."""
    return jaw_face_radius(phi) + P.PIN_OFFSET


def gap(phi: float) -> float:
    """The clear distance between the two jaw faces."""
    return 2.0 * jaw_face_radius(phi)


def phi_for_gap(g: float) -> float:
    """The twist that leaves a given gap -- what a finger of that width meets."""
    return P.TWIST_SWEEP * (1.0 - g / P.BORE_D)


def pin_ring_angle(phi: float, jaw: int) -> float:
    """A pin's position in the ring's own frame, in degrees.

    The ring turns under a pin that is fixed in angle, so in ring
    coordinates the pin runs backwards.
    """
    return JAW_ANGLES[jaw] - phi


# ---------------------------------------------------------------------------
# the groove
# ---------------------------------------------------------------------------

def groove_radius(t: float) -> float:
    """The spiral itself: radius at the groove's own angle t, in degrees.

    Linear in angle -- an Archimedean spiral -- so the jaw moves at a
    constant rate per degree of twist. Any other spiral would make the
    closing speed change as you turn it, which feels like something binding.

    Outside [0, TWIST_SWEEP] it flattens into the end pads, which is what
    makes the stops positive instead of a wedge the pin can jam into.
    """
    return P.R_PIN_IN + P.JAW_TRAVEL * min(max(t, 0.0), P.TWIST_SWEEP) / P.TWIST_SWEEP


def groove_slope_deg(r: float) -> float:
    """The angle of the groove wall against the direction of travel.

    This is the number that decides whether the thing holds. The pin is
    pushed along a wall climbing at this angle; friction holds if
    tan(slope) < mu. PETG on PETG is about 0.3 dry, so anything under about
    17 degrees is self-locking: press on a jaw and the ring does not unwind.
    The spiral is steepest at its inner end, where r is smallest.
    """
    dr_dtheta = P.JAW_TRAVEL / math.radians(P.TWIST_SWEEP)   # mm per radian
    return math.degrees(math.atan2(dr_dtheta, r))


def groove_path(jaw: int, n: int = 240) -> np.ndarray:
    """The groove's centreline for one jaw, as (n, 2) points in ring xy.

    Includes the flat end pads, so the returned path is a little longer than
    the sweep at both ends.
    """
    t0, t1 = -P.GROOVE_PAD_IN, P.TWIST_SWEEP + P.GROOVE_PAD_OUT
    ts = np.linspace(t0, t1, n)
    offset = groove_offset(jaw)
    pts = []
    for t in ts:
        r = groove_radius(t)
        a = math.radians(t + offset)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return np.asarray(pts)


def groove_polygon(jaw: int, n: int = 240):
    """The groove as a 2D shape: its centreline given a width.

    Flat caps, so each end is a wall square to the path -- a pin running
    onto it stops dead rather than riding up a rounded corner.
    """
    from shapely.geometry import LineString

    return LineString(groove_path(jaw, n)).buffer(
        P.GROOVE_W / 2.0, cap_style=2, join_style=2, resolution=16)


def grooves_polygon(n: int = 240):
    """Both grooves, as one shape to subtract from the ring's face."""
    from shapely.ops import unary_union

    return unary_union([groove_polygon(k, n) for k in range(P.JAW_COUNT)])


# ---------------------------------------------------------------------------
# the ratchet
# ---------------------------------------------------------------------------

def tooth_radius(psi_deg: float) -> float:
    """The collar's inner surface, at an angle in the collar's own frame.

    A sawtooth with a flat bottom: within each tooth the surface ramps
    outward from the crest to the valley, runs flat for a quarter of the
    pitch -- which is where the nose rests -- then drops back to the crest
    at a radial wall.

    The post is fixed, so in the collar's frame it travels BACKWARDS as the
    shell turns to close. Backwards along this profile the surface closes in
    on the nose gently -- deflecting the post -- and then jumps away at each
    boundary, which is the click. Forwards, that same boundary is a wall
    arriving head on, and nothing rides over it. So closing clicks and
    opening locks, which is the way round a clamp wants.
    """
    pitch = 360.0 / P.RATCHET_TEETH
    # Phased so a valley sits under the post whenever the twist is a whole
    # number of clicks -- which is the only place it ever comes to rest.
    phase = P.PAWL_ANGLE - (1.0 - P.RATCHET_FLAT / 2.0) * pitch
    f = ((psi_deg - phase) % pitch) / pitch
    if f >= 1.0 - P.RATCHET_FLAT:
        return P.COLLAR_R_ROOT
    rise = f / (1.0 - P.RATCHET_FLAT)
    return P.COLLAR_R_CREST + (P.COLLAR_R_ROOT - P.COLLAR_R_CREST) * rise


def click_deg() -> float:
    return 360.0 / P.RATCHET_TEETH


def click_mm() -> float:
    """How much a jaw moves between one click and the next."""
    return click_deg() * P.JAW_TRAVEL / P.TWIST_SWEEP


# ---------------------------------------------------------------------------
# what the cam does to the ring's size
# ---------------------------------------------------------------------------

def groove_separation() -> float:
    """Radial distance between the two grooves where they share an angle.

    20 * 180 / sweep, from the arithmetic in this module's docstring. It has
    to stay above GROOVE_W or the two grooves would run into each other.
    """
    return P.JAW_TRAVEL * 180.0 / P.TWIST_SWEEP


def summary() -> str:
    lines = [
        f"sweep              {P.TWIST_SWEEP:.0f} deg, open -> shut",
        f"travel per jaw     {P.JAW_TRAVEL:.1f} mm   "
        f"(gap {gap(0):.1f} -> {gap(P.TWIST_SWEEP):.1f} mm)",
        f"pin band           r {P.R_PIN_IN:.1f} -> {P.R_PIN_OUT:.1f} mm",
        f"spiral             {P.JAW_TRAVEL / P.TWIST_SWEEP * 180:.1f} mm "
        f"per half turn",
        f"groove slope       {groove_slope_deg(P.R_PIN_OUT):.1f} deg at the "
        f"outer end, {groove_slope_deg(P.R_PIN_IN):.1f} deg at the inner",
        f"groove separation  {groove_separation():.1f} mm "
        f"(groove is {P.GROOVE_W:.1f} mm wide)",
        f"a 17 mm finger     meets the jaws at "
        f"{phi_for_gap(17.0):.0f} deg of twist",
    ]
    return "\n".join("  " + ln for ln in lines)


if __name__ == "__main__":
    print("twist-grip scroll\n")
    print(summary())
