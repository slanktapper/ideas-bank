#!/usr/bin/env python3
"""Assertions about the renderer itself.

    python3 test_render.py

render.py was written inside cantstop, where it was checked by looking at
the PNGs it produced. Shared, that is no longer good enough: a regression
here is a regression in every project that draws a part, and the project
that notices it may not be the project that caused it. These checks pin the
contract -- image size, determinism, colour fidelity, depth ordering,
perspective-correct depth, framing, sectioning -- so it can be verified
without a human eye on an image.

The depth check earns its keep. cantstop shipped a renderer that
interpolated z linearly in screen space, which is wrong under perspective,
and nothing in an 83-ring lattice was ever big enough to show it. It took a
57,000 mm2 slab face to make it visible. The check below reproduces it in
two triangles.
"""

from __future__ import annotations

import sys

import numpy as np
import trimesh

import render as R

FAILS: list[str] = []
CHECKS = 0

# Flat, unlit, un-edged: a face comes out as exactly its own colour, so a
# pixel can be compared against a number rather than squinted at.
FLAT = dict(ambient=1.0, key=0.0, fill=0.0, spec=0.0, edges=0.0,
            supersample=1)

RED = (0.8, 0.1, 0.1)
GREEN = (0.1, 0.7, 0.2)
BLUE = (0.15, 0.25, 0.8)


def check(label, ok, detail=""):
    global CHECKS
    CHECKS += 1
    mark = "ok  " if ok else "FAIL"
    print(f"  [{mark}] {label}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def shown(v):
    return tuple(int(x) for x in v)


def px(img):
    return np.asarray(img, dtype=np.uint8)


def as255(color):
    # The renderer does (rgb * 255).astype(uint8) -- a truncation, not a
    # round. 0.1 becomes 25, not 26. A test that rounds instead disagrees
    # with every face by one count and matches nothing.
    return (np.clip(np.asarray(color, dtype=float), 0, 1) * 255).astype(np.uint8)


def count_of(arr, color, tol=2):
    """How many pixels are (near enough) this colour."""
    return int((np.abs(arr.astype(int) - as255(color).astype(int))
                <= tol).all(axis=-1).sum())


def cube(size=20.0, at=(0.0, 0.0, 0.0)):
    m = trimesh.creation.box(extents=(size, size, size))
    m.apply_translation(at)
    return m


# ---------------------------------------------------------------------------

def image_checks():
    print("\nthe image that comes back")
    c = cube()
    cam = R.frame([c], azimuth_deg=35, elevation_deg=25)

    img = R.render([{"mesh": c, "color": RED}], width=240, height=180,
                   supersample=2, **cam)
    check("the image is exactly the size asked for, after supersampling",
          img.size == (240, 180), f"{img.size[0]} x {img.size[1]}")

    a = px(R.render([{"mesh": c, "color": RED}], width=160, height=120, **cam))
    b = px(R.render([{"mesh": c, "color": RED}], width=160, height=120, **cam))
    check("the same geometry renders byte-identically twice",
          np.array_equal(a, b), "deterministic, so PNGs can be committed")

    flat = px(R.render([{"mesh": c, "color": RED}], width=160, height=120,
                       **{**cam, **FLAT}))
    hits = count_of(flat, RED, tol=0)
    check("a lit-flat face comes out as exactly its own colour",
          hits > 0, f"{hits} pixels are exactly {shown(as255(RED))}")
    frac = hits / (160 * 120)
    check("the part fills a sensible share of a framed shot",
          0.15 < frac < 0.95, f"{frac * 100:.1f}% of the frame")

    bg = flat[0, 0]
    check("the background is a gradient, not part of the model",
          not np.array_equal(bg, as255(RED)) and flat[-1, 0].tolist()
          != flat[0, 0].tolist(),
          f"top {shown(bg)} -> bottom {shown(flat[-1, 0])}")


def depth_checks():
    print("\ndepth")
    near = cube(14.0, at=(0.0, 0.0, 0.0))
    far = cube(14.0, at=(0.0, 0.0, -40.0))
    eye = (0.0, 0.0, 120.0)
    img = px(R.render([{"mesh": far, "color": GREEN},
                       {"mesh": near, "color": RED}],
                      eye=eye, target=(0, 0, 0), width=140, height=140,
                      fov_deg=40, **FLAT))
    centre = img[70, 70]
    check("a near part hides a far one, whatever order they are passed in",
          np.array_equal(centre, as255(RED)) and count_of(img, GREEN) == 0,
          f"centre pixel {shown(centre)}, {count_of(img, GREEN)} green pixels")

    # THE 1/Z CHECK. Depth has to be interpolated as 1/z, not z: under
    # perspective, distance is not linear in screen space but its reciprocal
    # is. Interpolating z directly puts a triangle's interior at the
    # arithmetic mean of its vertex depths where the truth is the harmonic
    # mean, and the arithmetic mean is always the larger -- so a big flat
    # face is rendered systematically FARTHER away than it is, by an amount
    # that grows with the triangle. Anything sunk into that face then pokes
    # straight through it. cantstop shipped this bug; nothing in an 83-ring
    # lattice was big enough to show it, and a 57,000 mm2 slab face was.
    #
    # Checked the way a design is checked: sink a feature 1 mm into a large
    # face and it must stay hidden. With linear z it comes back in full, and
    # stays visible until it is 8 mm deep -- which is the size of the error
    # in millimetres on a face this big.
    plane = trimesh.Trimesh(
        vertices=[[-60, -60, 0], [60, -45, 0], [0, 60, 0]],
        faces=[[0, 1, 2]], process=False)

    def sunk(h):
        return trimesh.Trimesh(
            vertices=[[-8, -6, h], [10, -4, h], [1, 9, h]],
            faces=[[0, 1, 2]], process=False)

    cam = dict(eye=tuple(R.orbit_eye((0, 0, 0), 140, 40, 25)),
               target=(0, 0, 0), width=200, height=200, fov_deg=45)

    alone = px(R.render([{"mesh": sunk(-1.0), "color": GREEN}],
                        **cam, **FLAT))
    silhouette = count_of(alone, GREEN)
    check("the sunk feature is big enough on screen for this to mean "
          "anything", silhouette > 100, f"{silhouette} pixels on its own")

    behind = px(R.render([{"mesh": plane, "color": BLUE},
                          {"mesh": sunk(-1.0), "color": GREEN}],
                         **cam, **FLAT))
    showing = count_of(behind, GREEN)
    check("a feature sunk 1 mm into a large face stays behind it",
          showing == 0,
          f"{showing} of {silhouette} pixels show through "
          f"({showing / max(silhouette, 1) * 100:.0f}%)")

    # The positive control. A depth bias big enough to paper over the bug
    # above would also swallow a feature standing proud of the face, which
    # is just as wrong and much harder to spot.
    proud = px(R.render([{"mesh": plane, "color": BLUE},
                         {"mesh": sunk(1.0), "color": GREEN}],
                        **cam, **FLAT))
    visible = count_of(proud, GREEN)
    check("a feature standing 1 mm proud of a large face is not swallowed "
          "by it", visible > silhouette * 0.9,
          f"{visible} pixels visible against a {silhouette}-pixel "
          f"silhouette")


def camera_checks():
    print("\nthe camera")
    c = cube(20.0, at=(13.0, -7.0, 4.0))
    W, H = 200, 150

    for ortho in (False, True):
        cam = R.frame([c], azimuth_deg=-120, elevation_deg=40, ortho=ortho)
        scr = R.screen_of(c.vertices, width=W, height=H, **cam)
        inside = ((scr[:, 0] >= 0) & (scr[:, 0] < W)
                  & (scr[:, 1] >= 0) & (scr[:, 1] < H)).all()
        label = "orthographic" if ortho else "perspective"
        check(f"frame() fits the whole part in shot ({label})", bool(inside),
              f"x {scr[:, 0].min():.0f}..{scr[:, 0].max():.0f}, "
              f"y {scr[:, 1].min():.0f}..{scr[:, 1].max():.0f}")

    # screen_of has to agree with where render() actually drew, or an
    # annotation leader points at thin air.
    cam = R.frame([c], azimuth_deg=20, elevation_deg=70)
    img = px(R.render([{"mesh": c, "color": RED}], width=W, height=H,
                      **{**cam, **FLAT}))
    cx, cy = R.screen_of([c.centroid], width=W, height=H, **cam)[0]
    hit = img[int(round(cy)), int(round(cx))]
    check("screen_of lands on the pixels render() drew",
          np.array_equal(hit, as255(RED)),
          f"centroid projects to ({cx:.0f}, {cy:.0f}), pixel {shown(hit)}")

    tgt = (5.0, 5.0, 0.0)
    e = R.orbit_eye(tgt, 100.0, 0.0, 90.0)
    check("orbit_eye at 90 degrees elevation is straight overhead",
          abs(e[2] - 100.0) < 1e-9 and np.allclose(e[:2], tgt[:2]),
          f"eye {tuple(round(float(v), 3) for v in e)}")
    check("looking straight down still gives a usable camera",
          np.isfinite(R.look_at(e, tgt)).all(),
          "the degenerate up-vector is handled")

    lo, hi = R.bounds_of([cube(10.0, at=(0, 0, 0)), cube(10.0, at=(30, 0, 0))])
    check("bounds_of spans every mesh it is given",
          np.allclose(lo, (-5, -5, -5)) and np.allclose(hi, (35, 5, 5)),
          f"{tuple(round(float(v), 1) for v in lo)} .. "
          f"{tuple(round(float(v), 1) for v in hi)}")


def section_checks():
    print("\nsections and annotation")
    c = cube(20.0)
    body, caps = R.section(c, normal=(0, -1, 0), origin=(0, 0, 0))
    check("a section gives back both a body and its cut faces",
          len(body.faces) > 0 and len(caps.faces) > 0,
          f"{len(body.faces)} body triangles, {len(caps.faces)} cap")
    check("every cut face lies on the cutting plane",
          bool(np.abs(caps.triangles_center[:, 1]).max() < 1e-6),
          f"max off-plane {np.abs(caps.triangles_center[:, 1]).max():.2e} mm")
    check("the cut keeps the half of the solid the normal points at",
          body.bounds[1][1] < 1e-6 and body.bounds[0][1] > -10 - 1e-6,
          f"y spans {body.bounds[0][1]:.1f} .. {body.bounds[1][1]:.1f}, "
          f"normal (0, -1, 0)")
    check("the cut face is the full cross-section, no more",
          abs(float(caps.area) - 20.0 * 20.0) < 1e-6,
          f"{float(caps.area):.1f} mm2 against 400.0")

    t = R.tint(RED)
    check("tint lightens a colour without losing which colour it was",
          all(t[i] > RED[i] for i in range(3)) and max(t) == t[0],
          f"{tuple(round(float(v), 3) for v in t)} from {RED}")

    moved = R.placed(c, (5, 0, 0))
    check("placed() translates a copy and leaves the original alone",
          np.allclose(moved.centroid, (5, 0, 0))
          and np.allclose(c.centroid, (0, 0, 0)),
          "no accidental mutation of a cached mesh")

    cam = R.frame([c], azimuth_deg=35, elevation_deg=25)
    img = R.render([{"mesh": c, "color": RED}], width=200, height=150, **cam)
    before = px(img).copy()
    after = px(R.annotate(img, [{"text": "a face", "px": (100, 75),
                                 "to": (170, 20), "align": "right"}]))
    check("annotate draws a leader and a label onto a finished render",
          not np.array_equal(before, after),
          f"{int((before != after).any(axis=-1).sum())} pixels changed")


def main():
    print("render.py — shared rasteriser checks")
    image_checks()
    depth_checks()
    camera_checks()
    section_checks()

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
