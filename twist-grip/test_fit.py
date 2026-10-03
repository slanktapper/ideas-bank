#!/usr/bin/env python3
"""Assertions about the design, run before spending a day of printer time.

    python3 test_fit.py

These are design rules, not unit tests. Editing params.py is the whole point
of the project, and most of the ways to get this mechanism wrong are silent:
a pin that leaves its groove, a wall that goes to nothing, a body that lifts
off halfway through the sweep, a cap that will go on three ways round when
only one of them is right.

The checks that earn their keep interrogate the finished meshes rather than
the numbers that made them -- interference between real solids, the bore
actually being clear, the lugs actually being trapped -- because the numbers
can agree with each other and still describe an object that cannot be
assembled.
"""

from __future__ import annotations

import math
import sys

import numpy as np
import trimesh

import params as P
import parts as T
import scroll as S

FAILS: list[str] = []
CHECKS = 0

TOUCHING = 0.05        # mm^3. Solids that share a face boolean out to a
                       # sliver, so "no interference" means "under a sliver".

# 120 is in this list on purpose: it is where evenly spaced lugs used to let
# the body lift straight off.
# All whole numbers of clicks. Between clicks the pawl is riding a ramp and
# IS pressing on a tooth -- that is what a spring does -- so a static model
# of a half-click position shows an overlap that is the mechanism working,
# not a fault. Resting positions are the ones that have to be clean.
SWEEP_SAMPLES = (0.0, 40.0, 90.0, 120.0, 180.0)


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def overlap(a, b) -> float:
    try:
        inter = trimesh.boolean.intersection([a, b], engine="manifold")
    except Exception:
        return 0.0
    if isinstance(inter, list):
        inter = inter[0] if inter else None
    if inter is None or len(inter.faces) == 0:
        return 0.0
    return abs(float(inter.volume))


def lifted(mesh, dz):
    m = mesh.copy()
    m.apply_translation((0.0, 0.0, dz))
    return m


# ---------------------------------------------------------------------------

def brief_checks():
    print("\nthe brief")
    st = P.STACK

    check("the opening is 40 mm when open",
          abs(S.gap(0.0) - P.BORE_D) < 1e-9,
          f"{S.gap(0.0):.1f} mm between the faces")
    check("the faces touch when the twist is run all the way over",
          abs(S.gap(P.TWIST_SWEEP)) < 1e-9,
          f"gap {S.gap(P.TWIST_SWEEP):.3f} mm at {P.TWIST_SWEEP:.0f} deg")
    check("each jaw travels exactly the bore radius",
          abs(P.JAW_TRAVEL - P.BORE_D / 2) < 1e-9, f"{P.JAW_TRAVEL:.1f} mm")

    # THE 90 MM GRIP, measured on the solid rather than taken from the
    # parameter: the face plate is the part that touches a finger.
    j = T.jaw(0.0, 0)
    face = T.keep_both(j, T.bar(P.FACE_T - 0.2, P.JAW_W + 1,
                                -10, st.overall_h + 10,
                                x0=S.jaw_face_radius(0.0) + 0.1))
    lo, hi = face.bounds
    check("the jaws grip 90 mm of finger",
          abs((hi[2] - lo[2]) - P.GRIP_L) < 0.01,
          f"contact face is {hi[2] - lo[2]:.1f} mm tall, "
          f"{P.JAW_W:.0f} mm wide")

    # A 40 mm cylinder has to pass through the WHOLE object now, cap included.
    probe = T.tube(0.0, P.BORE_D / 2 - 0.05, st.ring_0 - 1.0,
                   st.overall_h + 1.0)
    worst = max(overlap(probe, part["mesh"]) for part in T.assembly(0.0))
    check("a 40 mm cylinder passes clean through the whole open object",
          worst < TOUCHING, f"worst intrusion {worst:.4f} mm3 over "
          f"{st.overall_h:.0f} mm of height")

    shut = T.assembly(P.TWIST_SWEEP)
    j0 = next(p["mesh"] for p in shut if p["name"] == "jaw0")
    j1 = next(p["mesh"] for p in shut if p["name"] == "jaw1")
    check("the two faces arrive on the axis from opposite sides",
          abs(j0.bounds[0][0]) < 1e-6 and abs(j1.bounds[1][0]) < 1e-6,
          f"jaw0 reaches x={j0.bounds[0][0]:+.4f}, "
          f"jaw1 reaches x={j1.bounds[1][0]:+.4f}")
    check("they meet face to face rather than driving into each other",
          overlap(j0, j1) < TOUCHING,
          f"over a {P.JAW_W:.0f} x {P.GRIP_L:.0f} mm face")


def cam_checks():
    print("\nthe cam, at both ends of the blade")
    st = P.STACK

    worst = 0.0
    for jaw in range(P.JAW_COUNT):
        path = S.groove_path(jaw, 4000)
        for phi in np.linspace(0, P.TWIST_SWEEP, 73):
            psi, r = S.pin_ring_angle(phi, jaw), S.pin_radius(phi)
            px, py = r * math.cos(math.radians(psi)), r * math.sin(math.radians(psi))
            worst = max(worst, float(np.min(np.hypot(path[:, 0] - px,
                                                     path[:, 1] - py))))
    check("every pin stays on its own groove through the whole sweep",
          worst < 0.05, f"worst departure {worst:.4f} mm")

    # Both plates carry the SAME spiral, and a jaw's two pins are on one
    # axis, so whatever is true of the bottom pin is true of the top one.
    # That is what makes the drive symmetric; check it on the solid.
    # Sliced INSIDE the pins, not flush with their ends. A cut taken exactly
    # on a face leaves zero-volume slivers in the boolean, and .centroid is
    # area-weighted, so the slivers drag the answer tens of millimetres off
    # while the volume stays exactly right.
    j = T.jaw(90.0, 0)
    bot = T.keep_both(j, T.tube(0, P.OVERALL_D, st.pin_bot_0 + 0.2,
                                st.jaw_0 - 0.2))
    top = T.keep_both(j, T.tube(0, P.OVERALL_D, st.jaw_top + 0.2,
                                st.pin_top_1 - 0.2))
    cb, ct = bot.center_mass, top.center_mass
    check("a jaw's two pins are on one vertical axis",
          abs(cb[0] - ct[0]) < 1e-6 and abs(cb[1] - ct[1]) < 1e-6
          and abs(math.hypot(*cb[:2]) - S.pin_radius(90.0)) < 1e-6,
          f"both at r={math.hypot(*cb[:2]):.2f} mm, where the cam says "
          f"{S.pin_radius(90.0):.2f} — so the two plates drive the blade "
          f"identically")

    inner, outer = (S.groove_slope_deg(P.R_PIN_IN),
                    S.groove_slope_deg(P.R_PIN_OUT))
    check("the groove is shallow enough to hold position under load",
          inner < 17.0 and outer < 17.0,
          f"{outer:.1f} deg at the outer end, {inner:.1f} at the inner; "
          f"PETG on PETG is about 17 deg")
    check("the two grooves cannot run into each other",
          S.groove_separation() > P.GROOVE_W + P.WALL_MIN,
          f"{S.groove_separation():.1f} mm apart where they share an angle")
    for end, pad, r in (("inner", P.GROOVE_PAD_IN, P.R_PIN_IN),
                        ("outer", P.GROOVE_PAD_OUT, P.R_PIN_OUT)):
        arc = math.radians(pad) * r
        check(f"the {end} groove pad lets the pin clear its end wall",
              arc >= P.PIN_D / 2 + 1e-9,
              f"{arc:.2f} mm of arc against a {P.PIN_D / 2:.2f} mm pin radius")


def wall_checks():
    print("\nwalls and thicknesses")
    for name, t in {
        "ring inner, lip pocket to groove": P.R_GROOVE_IN - P.LIP_R_OUT,
        "shell floor under every groove": P.RING_FLOOR,
        "the lip the body's lugs hook under": P.RING_T - P.LIP_Z0,
        "the body tube": P.BODY_WALL,
        "the shell wall": P.WALL_T,
        "the cap's hook ring": P.CAP_HOOK_R_OUT - P.CAP_HOOK_R_IN,
        "cap hook to the spiral": P.R_GROOVE_IN - P.CAP_HOOK_R_OUT,
        "the body's top ring": P.TOPRING_T,
        "the jaw's face plate": P.FACE_T,
        "the jaw's rib": P.RIB_W,
    }.items():
        check(f"{name} is at least {P.WALL_MIN} mm", t >= P.WALL_MIN - 1e-9,
              f"{t:.2f} mm")

    check("the shell clears the jaw tails at full open",
          P.WALL_ID / 2 > P.JAW_TAIL_R_MAX,
          f"tail reaches r={P.JAW_TAIL_R_MAX:.1f}, wall starts at "
          f"r={P.WALL_ID / 2:.1f}")
    check("the cap never narrows the bore",
          2 * P.CAP_HOOK_R_IN >= P.BORE_D,
          f"cap opening {2 * P.CAP_HOOK_R_IN:.1f} mm")

    # The slots are the big hole in the body, and 26 mm wide ones take 84
    # degrees out of it at the bore. What keeps the tube a tube is that they
    # stop short at both ends: the skirt below them and the neck above are
    # closed rings, and both lug sets sit on those rather than on the slotted
    # part. Check the ends, and check what is left between the slots.
    st = P.STACK
    check("the slots stop below the neck, so the top stays a closed hoop",
          st.arc_top <= st.topring_0 and st.topring_0 > st.arc_top,
          f"slots end at z={st.arc_top:.1f}, the top ring starts at "
          f"{st.topring_0:.1f}")
    check("and stop above the skirt, which is a closed ring too",
          P.STACK.ring_top > 0.0,
          f"slots start at z={st.ring_top:.1f}, above the skirt's full height")

    arc = 180.0 - 2 * math.degrees(math.asin(P.SLOT_W / 2 / (P.BORE_D / 2)))
    check("what is left between the slots is a wall, not a strap",
          arc > 60.0,
          f"{arc:.0f} deg of arc each side at the bore, "
          f"{P.BODY_WALL:.1f} mm thick")

    # A flat face on a round bore is tangent to it, so the corners sit
    # further out than the middle. They have to stay inside the slot.
    corner = math.hypot(P.BORE_D / 2, P.JAW_W / 2)
    check("the corners of a full-open blade stay inside its slot",
          P.JAW_W / 2 < P.SLOT_W / 2 and corner < P.BODY_ARC_R_OUT,
          f"corner reaches r={corner:.2f}, slot half-width "
          f"{P.SLOT_W / 2:.2f}, tube OD r={P.BODY_ARC_R_OUT:.2f}")


def keying_checks():
    print("\nkeying: one way round, and only one")

    # Both lug sets and the pegs share one uneven pattern. For any of them to
    # line up twice, some rotation would have to map the set onto itself.
    for name, angles in (("the body's bottom lugs", P.LUG_ANGLES),
                         ("the body's top lugs", P.TOP_LUG_ANGLES),
                         ("the cap's pegs", P.LUG_ANGLES)):
        hits = [d for d in range(1, 360)
                if all(min(abs(((a + d - b + 180) % 360) - 180)
                           for b in angles) < 1e-6 for a in angles)]
        check(f"{name} line up at exactly one rotation",
              hits == [], f"no turn but zero maps the set onto itself"
              if not hits else f"also at {hits} deg")

    gaps = sorted(round((angles := P.LUG_ANGLES)[(i + 1) % 3] - angles[i]) % 360
                  for i in range(3))
    check("...because the three gaps are all different",
          len(set(gaps)) == 3, f"{gaps} degrees")


def ratchet_checks():
    print("\nthe ratchet")
    st = P.STACK

    check("a click is a small turn, and there are plenty of them",
          3.0 < S.click_deg() < 15.0 and P.TWIST_SWEEP / S.click_deg() > 12,
          f"{S.click_deg():.1f} deg a click = {S.click_mm():.2f} mm of jaw "
          f"travel, {P.TWIST_SWEEP / S.click_deg():.0f} clicks over the sweep")

    # WHICH WAY IT LOCKS, derived from the profile rather than assumed.
    # Walking the post along the surface in each direction: one way the
    # radius only ever eases away gradually or jumps outward (it rides over);
    # the other way it jumps INWARD, which is a wall arriving head on.
    pitch = S.click_deg()
    psis = np.linspace(0.0, 3 * pitch, 4000)
    rs = np.array([S.tooth_radius(x) for x in psis])
    steps = np.diff(rs)
    jumps = steps[np.abs(steps) > P.RATCHET_DEPTH * 0.5]
    check("opening meets a wall: the surface jumps inward that way",
          len(jumps) == 3 and bool((jumps < 0).all()),
          f"{len(jumps)} walls in 3 teeth, each {jumps.mean():+.2f} mm")
    flat = np.sum(np.abs(rs - P.COLLAR_R_ROOT) < 1e-9) / len(rs)
    check("each tooth has a flat valley for the nose to rest in",
          abs(flat - P.RATCHET_FLAT) < 0.02,
          f"{flat * 100:.0f}% of each tooth is flat bottom")
    check("closing rides over: backwards, the same step is outward",
          bool((-jumps > 0).all())
          and abs(float(-jumps.mean()) - P.RATCHET_DEPTH) < 0.05,
          f"{-jumps.mean():+.2f} mm of snap, which is the click")
    check("and between the walls it is a gentle ramp",
          float(np.abs(steps[np.abs(steps) <= P.RATCHET_DEPTH * 0.5]).max())
          < 0.01,
          "no step a nose could catch on")

    # The nose has to sit in a valley and be stopped by a crest.
    check("the nose sits in a valley with a crest to stop it",
          P.COLLAR_R_CREST < P.NOSE_R < P.COLLAR_R_ROOT,
          f"nose tip r={P.NOSE_R}, valley {P.COLLAR_R_ROOT}, crest "
          f"{P.COLLAR_R_CREST} — {P.NOSE_R - P.COLLAR_R_CREST:.2f} mm of bite")
    check("only the nose ever touches a tooth",
          P.POST_R_OUT < P.COLLAR_R_CREST,
          f"the post itself stops at r={P.POST_R_OUT}, "
          f"{P.COLLAR_R_CREST - P.POST_R_OUT:.2f} mm clear of the crests")
    check("pressing the pad far enough frees it",
          P.NOSE_R - P.COLLAR_R_CREST < 1.2,
          f"{P.NOSE_R - P.COLLAR_R_CREST:.2f} mm of press to clear the teeth")
    check("the pad is clear of the collar, so it can be pressed",
          st.post_top - P.PAD_T > st.collar_1,
          f"pad at z {st.post_top - P.PAD_T:.1f}..{st.post_top:.1f}, collar "
          f"tops out at {st.collar_1:.1f}")
    check("the ratchet never narrows the bore",
          P.COLLAR_R_CREST > P.BORE_D / 2 and P.POST_R_IN > P.BORE_D / 2,
          f"nothing inside r={min(P.COLLAR_R_CREST, P.POST_R_IN):.1f}")

    # The post is a spring, so it has to be free to move. Press the POST,
    # not the body: shoving the whole body sideways proves nothing except
    # that a body off its axis fouls the shell.
    post = T.pawl_post(st)
    inward = (math.cos(math.radians(P.PAWL_ANGLE + 180)),
              math.sin(math.radians(P.PAWL_ANGLE + 180)))
    free = True
    for phi in (0.0, 45.0, 90.0, 135.0, 180.0):
        moved = post.copy()
        moved.apply_translation((inward[0] * 0.9, inward[1] * 0.9, 0.0))
        if overlap(moved, T.spun(T.cap(), phi)) > TOUCHING:
            free = False
    check("the post has room to be pressed, at every twist",
          free, "0.9 mm inward clears the teeth at five angles")
    check("and at rest it is not fighting the teeth",
          overlap(post, T.cap()) < TOUCHING,
          "the nose sits in a flat valley, not part-way up a ramp")


def assembly_checks():
    print("\nassembly: does it go together, and move")
    st = P.STACK

    for phi in SWEEP_SAMPLES:
        ps = T.assembly(phi)
        worst, pair = 0.0, ""
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                v = overlap(ps[i]["mesh"], ps[j]["mesh"])
                if v > worst:
                    worst, pair = v, f"{ps[i]['name']}/{ps[j]['name']}"
        check(f"nothing fouls anything at {phi:.0f} deg of twist",
              worst < TOUCHING,
              f"worst {worst:.4f} mm3" + (f" ({pair})" if worst else ""))

    shell90, cap90, b = T.spun(T.shell(), 90.0), T.spun(T.cap(), 90.0), T.body()

    # The body cannot lift out of the shell: bottom lugs under the lip.
    rise = P.LIP_Z0 - st.lug_z1
    check("the body cannot lift out of the shell in use",
          overlap(lifted(b, rise + 0.4), shell90) > TOUCHING,
          f"it has {rise:.1f} mm of float, then the lugs meet the lip")

    # The cap cannot lift off: its hook ring is UNDER the body's top lugs.
    # Putting that hook above them instead holds nothing, which is what the
    # first version of this design did -- lifting the cap simply moved it
    # further from the thing meant to stop it.
    cap_rise = st.topring_0 - st.cap_hook_1
    check("the cap cannot lift off in use",
          overlap(lifted(cap90, cap_rise + 0.4), b) > TOUCHING,
          f"{cap_rise:.1f} mm of float, then its hook meets the body's top "
          f"lugs — and the body is held down by the shell")
    check("...and the cap is free to turn before it gets there",
          overlap(lifted(cap90, cap_rise - 0.15), b) < TOUCHING,
          "nothing rubbing in normal use")

    # ...and all of it comes apart where it is meant to.
    # Without the pawl post: taking it apart means pressing the release, and
    # the check is about the lugs and notches, not the ratchet.
    b_free = T.body(with_post=False)
    at_open = (overlap(lifted(b_free, 4.0), T.shell())
               + overlap(lifted(T.cap(), 4.0), b_free))
    check("at full open the notches line up and it lifts apart",
          at_open < TOUCHING,
          f"{at_open:.3f} mm3 in the way — deliberate, this is how it "
          f"assembles")

    # The blade's real outer radius, measured on the solid. A rectangle's
    # corners reach further than its end does, and at 26 mm wide that was
    # 1.5 mm past the shell wall until the tail was trimmed to an arc.
    jo = T.jaw(0.0, 0)
    r_max = float(np.max(np.hypot(jo.vertices[:, 0], jo.vertices[:, 1])))
    check("no corner of a full-open blade reaches the shell wall",
          r_max < P.WALL_ID / 2,
          f"widest point r={r_max:.2f}, wall starts at {P.WALL_ID / 2:.2f} "
          f"(a square tail would have been "
          f"{math.hypot(P.JAW_TAIL_R_MAX, P.JAW_W / 2):.2f})")

    # A blade held at one end only would cock. Both pins have to be engaged.
    j = T.jaw(90.0, 0)
    bot_in = overlap(T.tube(0, P.OVERALL_D, st.groove_floor, st.jaw_0), j)
    top_in = overlap(T.tube(0, P.OVERALL_D, st.jaw_top, st.cap_top), j)
    check("both ends of a blade reach into their plates",
          bot_in > 50.0 and top_in > 50.0,
          f"{bot_in:.0f} mm3 of pin below, {top_in:.0f} above")


def part_checks():
    print("\nthe parts themselves")
    made = {"shell": T.shell(), "body": T.body(), "cap": T.cap(),
            "jaw": T.jaw(0.0, 0)}
    for name, m in made.items():
        check(f"{name} is one watertight solid",
              m.is_watertight and m.is_winding_consistent and m.body_count == 1,
              f"{len(m.faces)} triangles, {m.body_count} body")

    for name, m in T.printable().items():
        lo, hi = m.bounds
        check(f"{name} sits on the bed and fits it",
              abs(lo[2]) < 1e-6 and (hi[0] - lo[0]) < P.BED[0]
              and (hi[1] - lo[1]) < P.BED[1],
              f"{hi[0] - lo[0]:.0f} x {hi[1] - lo[1]:.0f} x "
              f"{hi[2] - lo[2]:.0f} mm")

    for name, m in T.coupon().items():
        check(f"{name} is a sane test piece",
              m.is_watertight and m.body_count == 1
              and (m.bounds[1][2] - m.bounds[0][2]) < P.GRIP_L,
              f"{m.volume / 1000 * 1.27:.0f} g, "
              f"{m.bounds[1][2] - m.bounds[0][2]:.0f} mm tall")

    grams = (sum(m.volume for m in made.values())
             + made["jaw"].volume) / 1000.0 * 1.27
    check("a whole set is a day of printing, not a week",
          grams < 500.0, f"about {grams:.0f} g of PETG if printed solid")
    check(f"the object is {P.OVERALL_D:.0f} mm across and "
          f"{P.STACK.overall_h:.0f} mm tall",
          P.OVERALL_D < min(P.BED) and P.STACK.overall_h < 325.0,
          "the size the brief implies, not a choice")


def main():
    print("twist-grip — design checks")
    brief_checks()
    cam_checks()
    wall_checks()
    keying_checks()
    ratchet_checks()
    assembly_checks()
    part_checks()
    print()
    if FAILS:
        print(f"{len(FAILS)} of {CHECKS} checks FAILED:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print(f"all {CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
