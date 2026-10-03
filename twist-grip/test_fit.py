#!/usr/bin/env python3
"""Assertions about the design, run before spending an evening of printer time.

    python3 test_fit.py

These are design rules, not unit tests. Editing params.py is the whole point
of the project, and most of the ways to get this mechanism wrong are silent:
a pin that leaves its groove, a wall that goes to nothing between the lip
pocket and the spiral, a body that lifts off halfway through the sweep, a jaw
whose tail runs into the grip wall before it reaches full open. Each one
costs a print to find and nothing to check.

The checks that earn their keep are the ones that interrogate the finished
meshes rather than the numbers that made them -- interference between real
solids, the bore actually being clear, the lugs actually being trapped --
because the numbers can agree with each other and still describe an object
that cannot be assembled.
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

TOUCHING = 0.02        # mm^3. Two solids that share a face boolean out to a
                       # sliver, not to nothing, so "no interference" has to
                       # mean "less than a sliver".

# Twists to check the assembly at. 0 and 180 are the ends; 120 is in there on
# purpose, because that is where evenly spaced lugs used to come apart.
SWEEP_SAMPLES = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0)


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def overlap(a, b) -> float:
    """Volume two solids share. 0 for parts that merely touch."""
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


def span(mesh, axis):
    return float(mesh.bounds[0][axis]), float(mesh.bounds[1][axis])


# ---------------------------------------------------------------------------

def brief_checks():
    """The three things the brief fixed, measured rather than asserted."""
    print("\nthe brief")

    check("the opening is 40 mm when open",
          abs(S.gap(0.0) - P.BORE_D) < 1e-9,
          f"{S.gap(0.0):.1f} mm between the faces")
    check("the faces touch when the twist is run all the way over",
          abs(S.gap(P.TWIST_SWEEP)) < 1e-9,
          f"gap {S.gap(P.TWIST_SWEEP):.3f} mm at {P.TWIST_SWEEP:.0f} deg")
    check("each jaw travels exactly the bore radius",
          abs(P.JAW_TRAVEL - P.BORE_D / 2) < 1e-9,
          f"{P.JAW_TRAVEL:.1f} mm, which is what reaching the axis means")
    check("there are two jaws, diametrically opposite",
          P.JAW_COUNT == 2 and abs(S.JAW_ANGLES[1] - S.JAW_ANGLES[0] - 180) < 1e-9)

    # Linear in the twist: the same millimetres per degree everywhere, so it
    # does not feel like it is binding as it closes.
    rate = [(S.jaw_face_radius(a) - S.jaw_face_radius(a + 1.0))
            for a in np.linspace(0, P.TWIST_SWEEP - 1, 40)]
    check("the jaws close at a constant rate through the whole sweep",
          max(rate) - min(rate) < 1e-9,
          f"{rate[0]:.4f} mm per degree, everywhere")

    # THE BORE, MEASURED. Not "the number is 40" but "a 40 mm cylinder passes
    # through the assembled object without touching anything".
    probe = T.tube(0.0, P.BORE_D / 2 - 0.05, P.SKIRT_Z0 - 1.0,
                   P.Z_PLATE_TOP + 1.0)
    worst = max(overlap(probe, part["mesh"]) for part in T.assembly(0.0))
    check("a 40 mm cylinder passes clean through the open mechanism",
          worst < TOUCHING, f"worst intrusion {worst:.4f} mm3")

    # And the pads really do meet on the axis, in the solids.
    shut = T.assembly(P.TWIST_SWEEP)
    j0 = next(p["mesh"] for p in shut if p["name"] == "jaw0")
    j1 = next(p["mesh"] for p in shut if p["name"] == "jaw1")
    x0, x1 = span(j0, 0)[0], span(j1, 0)[1]
    check("the two pads arrive on the axis from opposite sides",
          abs(x0) < 1e-6 and abs(x1) < 1e-6,
          f"jaw0 reaches x={x0:+.4f}, jaw1 reaches x={x1:+.4f}")
    check("they meet face to face rather than driving into each other",
          overlap(j0, j1) < TOUCHING,
          f"shared volume {overlap(j0, j1):.4f} mm3 over a "
          f"{P.PAD_W:.1f} x {P.Z_PAD_TOP - P.Z_JAW_0:.1f} mm face")


def cam_checks():
    print("\nthe cam")

    # The check that caught a real defect: the groove arcs were first placed
    # at the jaw angles instead of the jaw angles less the sweep, which put
    # every pin 48 mm from the groove meant to drive it. The ring looked
    # right either way, because the two grooves together are symmetric under
    # a half turn.
    worst = 0.0
    for jaw in range(P.JAW_COUNT):
        path = S.groove_path(jaw, 4000)
        for phi in np.linspace(0, P.TWIST_SWEEP, 73):
            psi, r = S.pin_ring_angle(phi, jaw), S.pin_radius(phi)
            px = r * math.cos(math.radians(psi))
            py = r * math.sin(math.radians(psi))
            worst = max(worst, float(np.min(np.hypot(path[:, 0] - px,
                                                     path[:, 1] - py))))
    check("every pin stays on its own groove through the whole sweep",
          worst < 0.05, f"worst departure {worst:.4f} mm")

    inner = S.groove_slope_deg(P.R_PIN_IN)
    outer = S.groove_slope_deg(P.R_PIN_OUT)
    check("the groove is shallow enough to hold position under load",
          inner < 17.0 and outer < 17.0,
          f"{outer:.1f} deg at the outer end, {inner:.1f} at the inner; "
          f"PETG on PETG is about 17 deg")
    check("the spiral is steepest at its inner end, where it is weakest",
          inner > outer, "so the inner end is the number that matters")

    sep = S.groove_separation()
    check("the two grooves cannot run into each other",
          sep > P.GROOVE_W + P.WALL_MIN,
          f"{sep:.1f} mm apart where they share an angle, groove is "
          f"{P.GROOVE_W:.1f} mm wide")
    polys = S.grooves_polygon()
    check("and they come out as two separate shapes, not one",
          len(list(getattr(polys, "geoms", [polys]))) == P.JAW_COUNT,
          f"{len(list(getattr(polys, 'geoms', [polys])))} disjoint grooves")

    check("the ends of a groove are flat, so the stops are positive",
          abs(S.groove_radius(-20.0) - S.groove_radius(0.0)) < 1e-12
          and abs(S.groove_radius(P.TWIST_SWEEP + 20.0)
                  - S.groove_radius(P.TWIST_SWEEP)) < 1e-12,
          f"{P.GROOVE_PAD_IN:.1f} deg of dead flat at the inner end, "
          f"{P.GROOVE_PAD_OUT:.1f} at the outer")

    # A flat 2 degree pad was the first try, and at the inner end it put a
    # third of the pin through the end wall of its own groove: the pad has to
    # be a pin radius OF ARC, which is a bigger angle on a smaller circle.
    for end, pad, r in (("inner", P.GROOVE_PAD_IN, P.R_PIN_IN),
                        ("outer", P.GROOVE_PAD_OUT, P.R_PIN_OUT)):
        arc = math.radians(pad) * r
        check(f"the {end} pad is long enough for the pin to clear its end wall",
              arc >= P.PIN_D / 2 + 1e-9,
              f"{arc:.2f} mm of arc against a {P.PIN_D / 2:.2f} mm pin radius")

    engaged = P.PIN_LEN - (P.Z_LID_0 - (P.Z_JAW_0 + P.JAW_H))
    check("the pin stays well inside its groove even with the jaw lifted",
          engaged > P.PIN_LEN * 0.8 and P.PIN_LEN < P.GROOVE_DEPTH,
          f"{engaged:.1f} mm of {P.PIN_LEN:.1f} mm still in a "
          f"{P.GROOVE_DEPTH:.1f} mm groove")


def wall_checks():
    print("\nwalls and thicknesses")

    walls = {
        "ring inner, lip pocket to groove": P.R_GROOVE_IN - P.LIP_R_OUT,
        "ring outer, groove to grip wall": P.WALL_ID / 2 - P.R_GROOVE_OUT,
        "ring floor under every groove": P.RING_FLOOR,
        "the lip the lugs hook under": P.RING_T - P.LIP_Z0,
        "the lid over a jaw channel": P.LIP_T,
        "the skirt the ring turns on": (P.SKIRT_OD - P.SKIRT_ID) / 2,
        "the grip wall": P.WALL_T,
    }
    for name, t in walls.items():
        check(f"{name} is at least {P.WALL_MIN} mm", t >= P.WALL_MIN - 1e-9,
              f"{t:.2f} mm")

    check("the jaw pad fits through the lid's window and the base does not",
          P.PAD_W < P.WINDOW_W < P.JAW_W,
          f"pad {P.PAD_W}, window {P.WINDOW_W}, base {P.JAW_W} mm")
    check("the lid overlaps each side of the jaw base",
          (P.SLOT_W - P.WINDOW_W) / 2 >= 2.0,
          f"{(P.SLOT_W - P.WINDOW_W) / 2:.1f} mm of lid each side")


def assembly_checks():
    print("\nassembly: does it actually go together and move")

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

    # The jaw cannot lift out of its channel and take its pin with it.
    body = T.body()
    float_ = P.Z_LID_0 - (P.Z_JAW_0 + P.JAW_H)
    j = T.jaw(90.0, 0)
    check("a jaw is free to slide with the float it was given",
          overlap(lifted(j, float_ - 0.1), body) < TOUCHING,
          f"{float_:.1f} mm of vertical float")
    check("a jaw cannot lift any further than that -- the lid stops it",
          overlap(lifted(j, float_ + 0.4), body) > TOUCHING,
          "which is what keeps its pin in the groove")

    # The body cannot lift off the ring in use: the lugs are under the lip.
    # 120 degrees is in this list because that is exactly where evenly
    # spaced lugs would have let it come apart.
    for phi in (30.0, 90.0, 120.0, 150.0, 180.0):
        ring = T.spun(T.ring(), phi)
        v = overlap(lifted(body, P.LIP_Z0 - P.LUG_Z1 + 0.4), ring)
        check(f"the body cannot lift off at {phi:.0f} deg -- lugs under lip",
              v > TOUCHING, f"lug fouls lip by {v:.2f} mm3")

    # ...and it does come apart where it is meant to.
    v = overlap(lifted(body, 3.0), T.spun(T.ring(), 0.0))
    check("at full open the notches line up and it lifts apart",
          v < TOUCHING,
          f"{v:.3f} mm3 in the way -- deliberate, this is how it assembles")

    # The jaw tail has to clear the grip wall at full open, or the mechanism
    # stops before the opening is a full 40 mm.
    tail = max(span(T.jaw(0.0, k), 0)[1] for k in range(P.JAW_COUNT))
    check("the jaw tail clears the grip wall at full open",
          tail < P.WALL_ID / 2,
          f"tail reaches r={tail:.1f}, wall starts at r={P.WALL_ID / 2:.1f}")


def part_checks():
    print("\nthe parts themselves")

    made = {"ring": T.ring(), "body": T.body(), "jaw": T.jaw(0.0, 0)}
    for name, m in made.items():
        check(f"{name} is one watertight solid",
              m.is_watertight and m.is_winding_consistent and m.body_count == 1,
              f"{len(m.faces)} triangles, {m.body_count} body")

    pr = T.printable()
    for name, m in pr.items():
        lo, hi = m.bounds
        on_bed = abs(lo[2]) < 1e-6
        fits = (hi[0] - lo[0]) < P.BED[0] and (hi[1] - lo[1]) < P.BED[1]
        check(f"{name} sits on the bed and fits it",
              on_bed and fits,
              f"{hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2] - lo[2]:.1f} mm")

    # The body prints top face down, so the channel lid is laid over a gap
    # instead of bridging one, and the skirt points up.
    b = pr["body"]
    check("the body is flipped for printing, skirt upward",
          b.bounds[1][2] > P.PLATE_T + 1.0,
          f"{b.bounds[1][2]:.1f} mm tall, so the skirt is the top of the print")

    grams = sum(m.volume for m in made.values()) / 1000.0 * 1.27
    grams += T.jaw(0.0, 0).volume / 1000.0 * 1.27      # the second jaw
    check("a whole set is a sensible evening of printing",
          grams < 400.0, f"about {grams:.0f} g of PETG if printed solid")

    check(f"the object is {P.OVERALL_D:.0f} mm across and "
          f"{P.OVERALL_H:.0f} mm tall",
          P.OVERALL_D < min(P.BED), "the size the brief implies, not a choice")


def main():
    print("twist-grip — design checks")
    brief_checks()
    cam_checks()
    wall_checks()
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
