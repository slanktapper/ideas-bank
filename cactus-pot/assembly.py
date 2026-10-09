"""The finished object: both halves, in the filaments they will be printed in.

    python3 assembly.py          # renders/assembly-*.png

Everything else in this project renders one half or one question. `build.py`
draws the geometry in a flat green and a flat clay because those shots are
for judging silhouette, ribs and socket placement, and colour would only get
in the way. `colour_options.py` chose the cactus's scheme. `pot/shots.py
--colour` shows the pot's. Nothing put the two together, so there was no
picture of the thing itself -- which is the one picture worth having before
a day of printing.

The pot arrives as meshes, not as code: `pot/colours.py` writes its four
colour bodies to `pot/stl/colour/` and this reads them from there. That is
the same arrangement `build.py` already has with `POT_STL`, and it is what
keeps the two halves from importing each other.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "3d-tools"))
import render as R                                      # noqa: E402

import build                                            # noqa: E402
import cactus as C                                      # noqa: E402
import colour_options as CO                             # noqa: E402
import params as P                                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(HERE, "renders")

# The pot's four filaments. Copied rather than imported: pot/shots.py holds
# the same four, and the two halves of this project do not import from each
# other. They are render colours, not geometry -- nothing fits or fails on
# them -- so a copy costs nothing and a cross-half import would cost the one
# rule the split is built on.
COCOA = (0.44, 0.31, 0.20)      # PLA Basic cocoa brown
SILVER_SILK = (0.78, 0.80, 0.84)    # GEEETECH silk silver, the stones
JADE_WHITE = (0.94, 0.95, 0.93)     # the cartouche the name sits in
BLACK = (0.09, 0.09, 0.10)          # the letters
POT_PARTS = ("01-cocoa-body", "02-silver-stones",
             "03-white-panel", "04-black-letters")
POT_COLOUR_DIR = os.path.join(HERE, "pot", "stl", "colour")

# Flat light, for the reason colour_options.py gives: the body is two purples
# a single value apart, and a hard key light costs more contrast than the
# difference between them, so a scheme that would read on the bench looks
# like one colour in the render.
LIGHT = dict(ambient=0.58, key=0.46, fill=0.22, spec=0.22)

# The cactus's seating angle in the pot, and the only free number here. Its
# spigot is round, so the cactus can go into the socket at any rotation --
# which means the render gets to choose one rather than inherit it.
#
# The two constraints point in opposite directions. The pot's name faces
# az=0 and is only readable from there. The cactus's arms bear 28 and 214
# degrees and read worst from near either of those, which is why build.py
# shoots the bare cactus from 104. Turning the camera cannot satisfy both.
# Turning the cactus can: -104 degrees puts the arms where a camera at the
# pot's front sees across both of them, and the name stays square on.
SEAT_DEG = -104.0

# The parts-laid-out shot spreads the three printed parts along x, so the
# camera has to look across that axis. Shooting it from the front (az=0)
# looks straight down the row and piles all three on top of each other.
LAID_OUT_AZ = 270.0


def _z_rotate(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(deg), [0, 0, 1]))
    return m


def pot_colour_parts(floor):
    """The pot's four bodies, dropped so its cavity floor sits at z=0.

    z=0 is the cactus's soil line, so this is the same translation build.py
    uses for the single-colour assembly -- the two halves meet at the floor,
    not at the rim.
    """
    missing = [n for n in POT_PARTS
               if not os.path.exists(os.path.join(POT_COLOUR_DIR, f"{n}.stl"))]
    if missing:
        raise SystemExit(
            "the pot's colour bodies are a build product and are not in the\n"
            "repository (pot/.gitignore says so -- they are ~55 MB).\n"
            "    cd pot && python3 colours.py\n"
            "missing: " + ", ".join(missing))
    out = []
    for name, colour in zip(POT_PARTS, (COCOA, SILVER_SILK,
                                        JADE_WHITE, BLACK)):
        mesh = trimesh.load(os.path.join(POT_COLOUR_DIR, f"{name}.stl"),
                            force="mesh")
        mesh.apply_translation([0.0, 0.0, -floor])
        out.append({"mesh": mesh, "color": colour})
    return out


def cactus_colour_parts(seat_deg=0.0):
    """The cactus in scheme B2: silk purple crests, indigo hollows.

    The crest test is colour_options.py's, which is where it was worked out
    and argued over. Repeating it here would be two copies of a rule that
    has already been wrong once.
    """
    body, sites = C.cactus()
    spikes = build._spikes_in(sites)

    c = CO.face_centres(body)
    r = np.linalg.norm(c[:, :2], axis=1)
    mean = C.trunk_mean_radius(c[:, 2])
    # CO.on_arm_mask, not a distance against a hardcoded number: the arms
    # outgrew the old 16.0 at the 25% scale and their roots were being
    # coloured by the trunk's rule.
    on_arm = CO.on_arm_mask(c)
    crest = np.where(on_arm, CO.arm_crest(c), r - mean > 0.15 * P.RIB_DEPTH)
    ridge, hollow = CO.split(body, crest)

    return [{"mesh": _z_rotate(hollow, seat_deg), "color": CO.norm(CO.INDIGO)},
            {"mesh": _z_rotate(ridge, seat_deg), "color": CO.norm(CO.SILK)},
            {"mesh": _z_rotate(spikes, seat_deg), "color": CO.norm(CO.SILVER)}]


def shot(name, parts, az, el, margin=1.02, frame_on=None, **kw):
    """Render `parts`, framing on `frame_on` when the two differ.

    Framing on something smaller than what is drawn is how you get a detail
    shot: the rest is still rendered, it just runs out of the frame.
    """
    cam = R.frame(frame_on or [p["mesh"] for p in parts], az, el,
                  margin=margin)
    img = R.render(parts, width=1500, height=1150, supersample=2,
                   **{**LIGHT, **kw}, **cam)
    img.save(os.path.join(RENDERS, name))
    print("renders/" + name)


def laid_out(pot, cactus, gap=34.0):
    """The three printed parts side by side, standing on one plane.

    This is the print inventory rather than the object: the pot as it comes
    off the plate, the cactus body with its sockets still empty, and a plate
    of spikes. The cactus is shown bare on purpose -- 110 holes is what the
    part actually looks like at the moment you pick it up, and it is the
    last chance to notice that the spacing is wrong.
    """
    def width(parts):
        lo = min(p["mesh"].bounds[0][0] for p in parts)
        hi = max(p["mesh"].bounds[1][0] for p in parts)
        return lo, hi

    out = []
    x = 0.0
    # The pot is turned to face the camera. Laid out along x and shot from
    # LAID_OUT_AZ the camera looks along +y, so the face it sees is -y, and
    # the name is modelled on +x -- without this the cartouche is edge-on and
    # the one part of the pot anybody reads is the part you cannot see.
    for parts, spin in ((pot, -90.0), (cactus, 0.0)):
        parts = [{"mesh": _z_rotate(p["mesh"], spin), "color": p["color"]}
                 for p in parts]
        lo, hi = width(parts)
        for p in parts:
            m = p["mesh"].copy()
            m.apply_translation([x - lo, 0.0, 0.0])
            out.append({"mesh": m, "color": p["color"]})
        x += (hi - lo) + gap

    # The plate is left exactly as it is exported: flat, spikes up, which is
    # how it comes off the bed. Standing it on edge was tried and is worse --
    # it points 72 needles at the lens and they read as a grid of dots.
    plate = C.spike_plate()
    plate.apply_translation([x - plate.bounds[0][0],
                             0.0, -plate.bounds[0][2]])
    out.append({"mesh": plate, "color": CO.norm(CO.SILVER)})
    return out


def main():
    os.makedirs(RENDERS, exist_ok=True)

    path = os.path.join(HERE, P.POT_STL)
    if not os.path.exists(path):
        raise SystemExit(f"no pot mesh at {P.POT_STL} -- run pot/build.py")
    _, floor = build.measure_pot(path)

    pot = pot_colour_parts(floor)
    seated = cactus_colour_parts(SEAT_DEG)
    bare = cactus_colour_parts(0.0)[:2]      # no spikes, no seating turn

    # The object, from the pot's front, with the cactus turned to suit.
    shot("assembly-01-front.png", pot + seated, 0, 10)
    shot("assembly-02-three-quarter.png", pot + seated, 34, 16)
    # Low and close on the pot, because the name and the stones are the half
    # of this object that a render at full height throws away.
    #
    # Framed on the pot's own meshes rather than on the assembly with a small
    # margin. R.frame sizes itself from the bounding sphere of what it is
    # given, and given the whole object that sphere is 187 mm of cactus: a
    # margin small enough to fill the frame with the pot centres on the
    # trunk instead and crops the name off the bottom. Framing the pot and
    # letting the cactus run out of the top is the shot that was wanted.
    shot("assembly-03-name.png", pot + seated, 0, 6,
         frame_on=[p["mesh"] for p in pot], margin=1.12)

    shot("assembly-04-parts.png", laid_out(pot, bare),
         LAID_OUT_AZ, 12, margin=1.04)

    print(f"seated at {SEAT_DEG:+.0f}°, arms now bearing "
          + ", ".join(f"{(s['bearing'] + SEAT_DEG) % 360:.0f}°"
                      for s in P.ARMS))


if __name__ == "__main__":
    main()
