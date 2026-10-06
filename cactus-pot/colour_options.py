"""Three ways to print the cactus in Rob's three purples.

Rob has three purple PLAs and wants a cactus that reads as three colours
without looking like it was painted in stripes. The spines are a fourth
filament, silk silver -- they were a purple to begin with and vanished
against the body, which is in the notes under SILVER.

Real cacti do colour in three ways, and each of the schemes below copies one
of them. They are listed in order of what they cost to print, which is not
the same order as how good they look.

The pigment that makes a cactus purple is a betalain, and it is a stress
response rather than a fixed colour. Two facts from that matter here:

  * it concentrates at the edges of a pad and around the areoles, so a real
    purple cactus is darkest on its ridges and palest in its hollows; and
  * it deepens with cold and drought, so the oldest tissue low down and the
    newest growth at the tip are rarely the same colour.

Columnar cacti add a third: a glaucous bloom, a powdery wax that sits pale
over the whole stem and rubs off the crests where anything touches it, and a
collar of pale down around each areole.

Run: python3 colour_options.py
Writes renders/colour-a-*.png, -b-*, -c-*.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "3d-tools"))
import render as R                      # noqa: E402

import build                            # noqa: E402
import cactus as C                      # noqa: E402
import params as P                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(HERE, "renders")

# The three spools, as Bambu publishes them. Printed PLA reads a little
# darker and less saturated than the swatch, and the silk reads lighter than
# its hex because the sheen throws light back at you -- so treat these as the
# right *order* of three values rather than an exact preview.
INDIGO = (0x48, 0x29, 0x60)     # PLA Basic Indigo Purple 10701, #482960
PURPLE = (0x5E, 0x43, 0xB7)     # PLA Basic Purple 10700,       #5E43B7
SILK = (0x86, 0x71, 0xCB)       # PLA Silk+ Purple 13702,       #8671CB

# The spines. They were the third purple to begin with and disappeared --
# the lightest of three close purples, on a 1.9 mm needle, has nothing to
# read against. Silver is a value apart from all three, and pale spines on a
# dark body is what the real plants do. GEEETECH publish no hex for it, so
# this is a reading of their own product photo; a silk silver also throws
# back more light than any flat colour, so expect the print to read brighter
# than the render does.
SILVER = (0xC3, 0xC7, 0xCC)     # GEEETECH Metal Shine silk PLA, metallic silver


def norm(c):
    return tuple(v / 255.0 for v in c)


# ---------------------------------------------------------------------------
# splitting a mesh for the render
# ---------------------------------------------------------------------------
# None of this changes the model. It splits the finished mesh into groups of
# faces so each group can be drawn in its own colour, which is what the
# printer would be doing in a different way.

def split(mesh, mask):
    """Two meshes from one, by a per-face boolean."""
    return (mesh.submesh([np.flatnonzero(mask)], append=True),
            mesh.submesh([np.flatnonzero(~mask)], append=True))


def face_centres(mesh):
    return mesh.triangles.mean(axis=1)


def arm_distance(pts):
    """Distance from each point to the nearer arm's centreline."""
    best = np.full(len(pts), np.inf)
    for spec in P.ARMS:
        _, line, _ = C.arm_rings(spec)
        d = np.linalg.norm(pts[:, None, :] - line[None, :, :], axis=2).min(1)
        best = np.minimum(best, d)
    return best


def arm_crest(pts):
    """Which points sit on an arm's rib crest rather than in its hollow.

    The trunk's test is easy: it is a column about the z axis, so a point's
    radius can be compared against the mean radius at that height. An arm is
    a swept tube that bends and tapers, so there is no single axis to measure
    from. Each point is matched to the nearest station on the arm's spine
    instead, and its distance measured perpendicular to the spine there,
    against the mean radius of the ring at that station.

    This fades out on its own where it should. The ribs are scaled away into
    the root flare and the rounded tip, so near either end a point sits at
    the mean radius and nothing is called a crest -- which is what the arm
    actually looks like.
    """
    out = np.zeros(len(pts), dtype=bool)
    for spec in P.ARMS:
        rings, line, tang = C.arm_rings(spec)
        mean_r = np.linalg.norm(rings - line[:, None, :], axis=2).mean(1)
        d = np.linalg.norm(pts[:, None, :] - line[None, :, :], axis=2)
        i = d.argmin(1)
        rel = pts - line[i]
        along = np.einsum("ij,ij->i", rel, tang[i])
        perp = np.linalg.norm(rel - tang[i] * along[:, None], axis=1)
        near = d[np.arange(len(pts)), i] < 16.0
        out |= near & (perp - mean_r[i] > 0.15 * P.ARM_RIB_DEPTH)
    return out


# ---------------------------------------------------------------------------

def main():
    os.makedirs(RENDERS, exist_ok=True)
    body, sites = C.cactus()
    spikes = build._spikes_in(sites)
    c = face_centres(body)
    r = np.linalg.norm(c[:, :2], axis=1)

    def shot(name, parts, az=104, el=20, margin=1.02):
        # Flatter light than the green renders use. These three purples sit
        # close together in value, and the default key light costs more
        # contrast than the difference between two of them -- so a scheme
        # would look like one colour even when the print would not.
        cam = R.frame([p["mesh"] for p in parts], az, el, margin=margin)
        R.render(parts, ambient=0.62, key=0.42, fill=0.18, spec=0.22,
                 **cam).save(os.path.join(RENDERS, name))
        print("renders/" + name)

    # -- A. the crown colours up ------------------------------------------
    # The newest growth is at the tip and it is the part that colours hardest
    # under sun and cold. A filament swap is a hard line, so it is put where
    # the geometry already has one: the shoulder where the ribs fade out and
    # the crown begins. Below it the column, above it the cap.
    shoulder = P.TRUNK_H * P.RIB_FADE_TOP
    crown, column = split(body, c[:, 2] >= shoulder)
    shot("colour-a-crown.png",
         [{"mesh": column, "color": norm(INDIGO)},
          {"mesh": crown, "color": norm(PURPLE)},
          {"mesh": spikes, "color": norm(SILVER)}])
    print(f"  A: swap at z={shoulder:.0f} mm, "
          f"{100 * crown.area / body.area:.0f}% of the surface above it")

    # -- B. the ridges are darkest ----------------------------------------
    # What a purple cactus actually does: the pigment sits in the ridges and
    # the hollows stay pale. Needs the printer to change colour inside a
    # layer rather than between layers, so it is the expensive one.
    mean = C.trunk_mean_radius(c[:, 2])
    on_arm = arm_distance(c) < 16.0
    crest = np.where(on_arm, arm_crest(c), r - mean > 0.15 * P.RIB_DEPTH)
    ridge, hollow = split(body, crest)
    shot("colour-b-ridges.png",
         [{"mesh": hollow, "color": norm(SILK)},
          {"mesh": ridge, "color": norm(INDIGO)},
          {"mesh": spikes, "color": norm(SILVER)}])
    # The same split the other way up, and the one Rob picked. Botanically
    # it is the weaker claim -- the pigment really is in the ridges -- but a
    # ridge is the part the light lands on, so putting the dark colour there
    # cancels the shading that shows the ribs at all. Rendered both ways
    # because that is not something a swatch tells you.
    b2 = [{"mesh": hollow, "color": norm(INDIGO)},
          {"mesh": ridge, "color": norm(SILK)},
          {"mesh": spikes, "color": norm(SILVER)}]
    shot("colour-b2-ridges-lit.png", b2)
    shot("colour-b2-side.png", b2, az=118, el=4)
    shot("colour-b2-arm.png", b2, az=150, el=14, margin=0.62)
    print(f"  B: {100 * ridge.area / body.area:.0f}% of the surface is ridge, "
          f"{100 * (crest & on_arm).sum() / max(1, on_arm.sum()):.0f}% of the "
          f"arm faces are crest")

    # -- C. the arms are younger ------------------------------------------
    # An arm is years younger than the trunk it grew out of and does not
    # match it. Printed as separate parts they are three plain single-colour
    # prints, and the arms stop needing support into the bargain.
    arm, trunk = split(body, arm_distance(c) < 16.0)
    shot("colour-c-arms.png",
         [{"mesh": trunk, "color": norm(INDIGO)},
          {"mesh": arm, "color": norm(PURPLE)},
          {"mesh": spikes, "color": norm(SILVER)}])
    print(f"  C: {100 * arm.area / body.area:.0f}% of the surface is arm")


if __name__ == "__main__":
    main()
