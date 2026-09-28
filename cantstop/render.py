"""A small software rasteriser, so renders need no GPU and no display.

The container this project is developed in has no OpenGL, and the usual
headless options (pyrender/OSMesa, pyglet under xvfb) are a pile of system
dependencies that break the moment the base image moves. Rasterising into a
numpy z-buffer instead is about a hundred lines, has no dependencies beyond
numpy and pillow, and is entirely deterministic -- the same geometry gives a
byte-identical PNG on any machine.

Flat shading with two lights and a depth-discontinuity edge pass. That last
bit matters more than it sounds: a wireframe lattice viewed head-on turns
into visual mush without edges, and the whole point of these renders is to
see whether the lattice is right before committing filament to it.
"""

from __future__ import annotations

import numpy as np
import trimesh
from PIL import Image


# ---------------------------------------------------------------------------
# camera
# ---------------------------------------------------------------------------

def look_at(eye, target, up=(0.0, 0.0, 1.0)) -> np.ndarray:
    eye = np.asarray(eye, dtype=float)
    target = np.asarray(target, dtype=float)
    up = np.asarray(up, dtype=float)

    fwd = target - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, up)
    n = np.linalg.norm(right)
    if n < 1e-9:                       # looking straight down: pick a new up
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(fwd, up)
        n = np.linalg.norm(right)
    right /= n
    true_up = np.cross(right, fwd)

    m = np.eye(4)
    m[0, :3], m[1, :3], m[2, :3] = right, true_up, -fwd
    m[:3, 3] = -m[:3, :3] @ eye
    return m


def _project(pts_cam, width, height, fov_deg, ortho_height):
    """Camera space -> screen pixels + a normalised depth in [0, 1)."""
    aspect = width / height
    z = -pts_cam[:, 2]                                 # distance in front
    if ortho_height is not None:
        sx = pts_cam[:, 0] / (ortho_height * 0.5 * aspect)
        sy = pts_cam[:, 1] / (ortho_height * 0.5)
    else:
        f = 1.0 / np.tan(np.radians(fov_deg) * 0.5)
        safe = np.maximum(z, 1e-6)
        sx = (pts_cam[:, 0] * f / aspect) / safe
        sy = (pts_cam[:, 1] * f) / safe
    px = (sx * 0.5 + 0.5) * width
    py = (0.5 - sy * 0.5) * height
    return np.column_stack([px, py]), z


# ---------------------------------------------------------------------------
# the rasteriser
# ---------------------------------------------------------------------------

def render(parts, eye, target, width=1500, height=1100, up=(0, 0, 1),
           fov_deg=32.0, ortho_height=None, supersample=2,
           bg_top=(0.97, 0.97, 0.98), bg_bottom=(0.84, 0.86, 0.90),
           key_dir=(-0.45, -0.75, 0.95), fill_dir=(0.8, 0.35, 0.35),
           ambient=0.34, key=0.66, fill=0.24, spec=0.30, shininess=22.0,
           edges=0.55):
    """Render a list of {"mesh": Trimesh, "color": (r,g,b) 0..1} dicts."""
    W, H = int(width * supersample), int(height * supersample)

    verts, tris, cols = [], [], []
    for p in parts:
        m = p["mesh"]
        off = sum(len(v) for v in verts)
        verts.append(np.asarray(m.vertices, dtype=np.float64))
        tris.append(np.asarray(m.faces, dtype=np.int64) + off)
        c = np.asarray(p["color"], dtype=np.float64)
        cols.append(np.tile(c, (len(m.faces), 1)))
    V = np.vstack(verts)
    F = np.vstack(tris)
    C = np.vstack(cols)

    # --- world -> camera --------------------------------------------------
    M = look_at(eye, target, up)
    Vc = (M[:3, :3] @ V.T).T + M[:3, 3]
    screen, depth = _project(Vc, W, H, fov_deg, ortho_height)

    s = screen[F]                                   # (n, 3, 2)
    d = depth[F]                                    # (n, 3)

    # --- cull -------------------------------------------------------------
    area = ((s[:, 1, 0] - s[:, 0, 0]) * (s[:, 2, 1] - s[:, 0, 1]) -
            (s[:, 2, 0] - s[:, 0, 0]) * (s[:, 1, 1] - s[:, 0, 1]))
    keep = area < -1e-9                             # front-facing (y is down)
    keep &= (d > 1e-6).all(axis=1)                  # fully in front of the eye
    keep &= (s[:, :, 0].max(axis=1) >= 0) & (s[:, :, 0].min(axis=1) < W)
    keep &= (s[:, :, 1].max(axis=1) >= 0) & (s[:, :, 1].min(axis=1) < H)

    idx = np.nonzero(keep)[0]
    s, d, area = s[idx], d[idx], area[idx]

    # Depth is interpolated as 1/z, not z. Under perspective, distance is NOT
    # linear in screen space -- 1/distance is -- so interpolating z directly
    # puts a triangle's interior at the wrong depth, by an amount that grows
    # with the triangle. Two coplanar neighbours of different sizes then
    # disagree about where the surface they share actually is, and the
    # z-buffer flickers between them in wedges radiating from their vertices.
    # The lattice never showed it: nothing in it was bigger than a strut. A
    # slab's top face is one 57,000 mm2 sheet and it showed immediately.
    di = 1.0 / d

    # --- shading (flat, per face, in world space) -------------------------
    p0, p1, p2 = V[F[idx, 0]], V[F[idx, 1]], V[F[idx, 2]]
    nrm = np.cross(p1 - p0, p2 - p0)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = nrm / np.maximum(ln, 1e-12)

    def _unit(v):
        v = np.asarray(v, dtype=float)
        return v / np.linalg.norm(v)

    shade = (ambient
             + key * np.clip(nrm @ _unit(key_dir), 0, 1)
             + fill * np.clip(nrm @ _unit(fill_dir), 0, 1))
    face_rgb = C[idx] * shade[:, None]

    # A Blinn-Phong highlight, with the view direction taken as constant
    # across the frame. Crude, but without it black filament renders as a
    # silhouette and the whole point of the lattice shots is lost.
    if spec > 0:
        view = _unit(np.asarray(eye, dtype=float) - np.asarray(target, dtype=float))
        half = _unit(_unit(key_dir) + view)
        face_rgb = face_rgb + spec * np.clip(nrm @ half, 0, 1)[:, None] ** shininess
    face_rgb = np.clip(face_rgb, 0, 1)

    # --- background gradient ---------------------------------------------
    ramp = np.linspace(0, 1, H)[:, None]
    img = (np.asarray(bg_top) * (1 - ramp) + np.asarray(bg_bottom) * ramp)
    img = np.repeat(img[:, None, :], W, axis=1)
    zbuf = np.full((H, W), np.inf)

    # --- scanline loop ----------------------------------------------------
    x0s = np.clip(np.floor(s[:, :, 0].min(axis=1)).astype(int), 0, W - 1)
    x1s = np.clip(np.ceil(s[:, :, 0].max(axis=1)).astype(int), 0, W - 1)
    y0s = np.clip(np.floor(s[:, :, 1].min(axis=1)).astype(int), 0, H - 1)
    y1s = np.clip(np.ceil(s[:, :, 1].max(axis=1)).astype(int), 0, H - 1)

    for k in range(len(s)):
        x0, x1, y0, y1 = x0s[k], x1s[k], y0s[k], y1s[k]
        if x1 < x0 or y1 < y0:
            continue
        xs = np.arange(x0, x1 + 1) + 0.5
        ys = np.arange(y0, y1 + 1) + 0.5
        gx, gy = np.meshgrid(xs, ys)

        (ax, ay), (bx, by), (cx, cy) = s[k]
        inv = 1.0 / area[k]
        l0 = ((bx - gx) * (cy - gy) - (cx - gx) * (by - gy)) * inv
        l1 = ((cx - gx) * (ay - gy) - (ax - gx) * (cy - gy)) * inv
        l2 = 1.0 - l0 - l1

        inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not inside.any():
            continue
        z = 1.0 / (l0 * di[k, 0] + l1 * di[k, 1] + l2 * di[k, 2])
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        hit = inside & (z < sub)
        if not hit.any():
            continue
        sub[hit] = z[hit]
        img[y0:y1 + 1, x0:x1 + 1][hit] = face_rgb[k]

    # --- edges from depth discontinuity ----------------------------------
    if edges > 0:
        z = np.where(np.isfinite(zbuf), zbuf, np.nan)
        gy_, gx_ = np.gradient(z)
        g = np.nan_to_num(np.hypot(gx_, gy_))
        scale = np.nanpercentile(g[g > 0], 88) if (g > 0).any() else 1.0
        e = np.clip(g / max(scale, 1e-9), 0, 1) ** 0.7
        img *= (1.0 - edges * e)[:, :, None]

    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if supersample > 1:
        out = out.resize((width, height), Image.LANCZOS)
    return out


# ---------------------------------------------------------------------------
# convenience
# ---------------------------------------------------------------------------

def placed(mesh: trimesh.Trimesh, xyz) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_translation(xyz)
    return m


def orbit_eye(target, radius, azimuth_deg, elevation_deg):
    a, e = np.radians(azimuth_deg), np.radians(elevation_deg)
    return np.asarray(target, dtype=float) + radius * np.array([
        np.cos(e) * np.cos(a),
        np.cos(e) * np.sin(a),
        np.sin(e),
    ])


def bounds_of(meshes):
    lo = np.min([m.bounds[0] for m in meshes], axis=0)
    hi = np.max([m.bounds[1] for m in meshes], axis=0)
    return lo, hi


def frame(meshes, azimuth_deg, elevation_deg, fov_deg=32.0,
          margin=1.0, ortho=False):
    """Work out a camera that frames everything, from a viewing direction.

    Uses the bounding sphere rather than the projected silhouette -- slightly
    loose, but it can never clip the model, which is the property that matters
    when the render is standing in for a part you have not printed yet.
    Returns a kwargs dict to splat into render().
    """
    lo, hi = bounds_of(meshes)
    target = (lo + hi) * 0.5
    radius = float(np.linalg.norm(hi - lo)) * 0.5 * margin
    if ortho:
        return {
            "eye": orbit_eye(target, radius * 4.0, azimuth_deg, elevation_deg),
            "target": tuple(target),
            "ortho_height": radius * 2.0,
        }
    dist = radius / np.sin(np.radians(fov_deg) * 0.5)
    return {
        "eye": orbit_eye(target, dist, azimuth_deg, elevation_deg),
        "target": tuple(target),
        "fov_deg": fov_deg,
    }


def section(mesh, normal, origin):
    """Cut a mesh with a plane and hand back (body, cut_faces) separately.

    Splitting the capped faces out lets the cut surface be rendered in a
    different colour, which is the difference between a section drawing you
    can read and a lump of one colour.
    """
    cut = trimesh.intersections.slice_mesh_plane(
        mesh, plane_normal=np.asarray(normal, dtype=float),
        plane_origin=np.asarray(origin, dtype=float), cap=True)
    n = np.asarray(normal, dtype=float)
    n /= np.linalg.norm(n)
    fn = cut.face_normals
    centroids = cut.triangles_center
    on_plane = np.abs((centroids - np.asarray(origin, dtype=float)) @ n) < 1e-6
    aligned = (fn @ n) < -0.999
    is_cap = on_plane & aligned
    body = cut.submesh([~is_cap], append=True, repair=False)
    caps = cut.submesh([is_cap], append=True, repair=False)
    return body, caps


def screen_of(points, eye, target, width, height, up=(0, 0, 1),
              fov_deg=32.0, ortho_height=None):
    """Project world points to pixel coordinates using render()'s camera.

    Lets annotations be anchored to real geometry -- a leader line pointing at
    "the socket" actually points at the socket, whatever the camera does.
    """
    pts = np.atleast_2d(np.asarray(points, dtype=float))
    M = look_at(eye, target, up)
    cam = (M[:3, :3] @ pts.T).T + M[:3, 3]
    px, _ = _project(cam, width, height, fov_deg, ortho_height)
    return px


def tint(color, k=0.38):
    """A lighter wash of a colour, for section-cut surfaces.

    Cut faces in a uniform grey make a sectioned assembly unreadable -- every
    part looks like the same part. Tinting each cut with its own colour keeps
    the parts legible while still reading as 'this is a cut'.
    """
    c = np.asarray(color, dtype=float)
    return tuple(c * (1 - k) + k)


def annotate(img, items, font_size=15, color=(26, 30, 40), leader=(90, 100, 118)):
    """Draw leader lines and labels onto a finished render.

    `items` are dicts: {"text", "px" (anchor pixel), "to" (label pixel),
    "align": "left"|"right"}.
    """
    from PIL import ImageDraw, ImageFont
    from matplotlib import font_manager

    try:
        path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
        font = ImageFont.truetype(path, font_size)
    except Exception:
        font = ImageFont.load_default()

    d = ImageDraw.Draw(img)
    for it in items:
        ax, ay = it["px"]
        bx, by = it["to"]
        d.line([(ax, ay), (bx, by)], fill=leader, width=2)
        r = 3
        d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=leader)
        anchor = "rm" if it.get("align", "left") == "right" else "lm"
        pad = 7 if anchor == "lm" else -7
        d.text((bx + pad, by), it["text"], font=font, fill=color, anchor=anchor)
    return img
