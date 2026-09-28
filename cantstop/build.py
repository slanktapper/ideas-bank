#!/usr/bin/env python3
"""Build every STL and every test render for cantstop.

    python3 build.py              # everything
    python3 build.py --stl        # STLs only
    python3 build.py --renders    # renders only
    python3 build.py --fast       # quarter-res renders, coarse facets

Outputs land in stl/ and renders/. Both directories are regenerated from
scratch, so they are safe to delete at any time.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

import board as B
import params as P
import render as R
import solids as S

HERE = Path(__file__).parent
STL_DIR = HERE / "stl"
RENDER_DIR = HERE / "renders"

# Colours chosen to match filament actually on the shelf -- see
# ../available-tools.md. The renders are a shopping list as much as a preview.
C_BOARD   = (0.760, 0.130, 0.130)   # PLA Basic, red -- see note in
C_NUMERAL = (0.930, 0.940, 0.920)   # PLA Basic, jade white   print-guide.md
C_CUT     = (0.620, 0.640, 0.680)   # section-cut surfaces
C_PLAYERS = [
    (0.800, 0.140, 0.140),          # PLA Basic, red
    (0.920, 0.930, 0.900),          # PLA Basic, jade white
    (0.360, 0.270, 0.600),          # PLA Basic, indigo purple
    (0.130, 0.380, 0.780),          # PLA Basic, blue
]
C_RUNNER  = (0.970, 0.800, 0.100)   # PETG Basic, yellow

DENSITY = {"PLA": 1.24, "PETG": 1.27}   # g/cm^3
LAYER, LINE, WALLS, SKINS = P.LAYER_H, 0.42, 3, 3


def _slab_filament(area: float, peri: float, n_posts: int) -> float:
    """cm3 of filament a slab of this plan shape eats: walls, skins, infill.

    A lattice is nearly all perimeter, so quoting it at 100% infill is close
    to the truth. A slab is not: its skins are a fixed 94 g over the full
    octagon however thick it is, and everything between them is set by the
    infill. Quoting a slab at 100% would overstate it by a factor of three.
    """
    core = max(P.SLAB_T - 2 * SKINS * LAYER, 0.0)
    posts = n_posts * np.pi * (P.POST_D / 2) ** 2 * P.POST_H
    return (peri * WALLS * LINE * P.SLAB_T
            + 2 * SKINS * LAYER * area
            + core * area * P.SLAB_INFILL
            + posts) / 1000.0


def _plan(poly) -> tuple[float, float]:
    """(area, perimeter) of a closed plan polygon."""
    p = np.asarray(poly, dtype=float)
    x, y = p[:, 0], p[:, 1]
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    peri = sum(float(np.linalg.norm(p[(j + 1) % len(p)] - p[j]))
               for j in range(len(p)))
    return area, peri


def slab_filament() -> float:
    return _slab_filament(*_plan(B.octagon()), len(B.all_cells()))


def stub_filament() -> float:
    """Same model, over the stub's own plan: the octagon clipped to its box."""
    from shapely.geometry import Polygon, box as _box

    (x0, y0), (x1, y1) = B.stub_box()
    plan = Polygon([tuple(p) for p in B.octagon()]).intersection(
        _box(x0, y0, x1, y1))
    return _slab_filament(plan.area, plan.length, len(B.stub_cells()))


# ---------------------------------------------------------------------------
# placement
# ---------------------------------------------------------------------------

# A piece seats when its shoulder lands on the collar rim, not when its pin
# bottoms out -- the socket is cut deeper than the pin is long precisely so
# that this is true. Stack height is therefore exact and repeatable.
SEAT_Z = B.seat_z()


def place(mesh, col: int, row: int, level: int = 0, below=()):
    """Drop a piece into cell (column 2..12, row 0-based), stacked `level` high.

    `below` lists the body heights of the pieces already in the cell, so a
    marker landing on top of a taller runner still seats correctly.
    """
    i = P.COLUMNS.index(col)
    x, y = B.cell_xy(i, row)
    z = SEAT_Z + sum(below[:level])
    return R.placed(mesh, (x, y, z))


# ---------------------------------------------------------------------------
# STL export
# ---------------------------------------------------------------------------

def export_stls(verbose=True):
    STL_DIR.mkdir(exist_ok=True)
    rows = []

    def save(mesh, name, material, note, cm3=None):
        path = STL_DIR / name
        mesh.export(path)
        cm3 = mesh.volume / 1000.0 if cm3 is None else cm3
        rows.append((name, mesh.is_watertight, len(mesh.faces), cm3,
                     cm3 * DENSITY[material], note))
        if verbose:
            print(f"  wrote {name}")

    if verbose:
        print("building board ...")
    board_body = B.build_board(verbose=verbose)
    numerals = B.build_board(numerals_only=True)

    slab = P.BOARD_STYLE == "slab"
    note = (f"{P.SLAB_T:.0f} mm slab at {P.SLAB_INFILL:.0%} infill; "
            f"load with numerals" if slab else "two-colour: load with numerals")
    save(board_body, "board-body.stl", "PLA", note,
         cm3=slab_filament() - numerals.volume / 1000.0 if slab else None)
    save(numerals, "board-numerals.stl", "PLA",
         "two-colour: numbers, title, lip cap and the alternate post tops")

    if verbose:
        print("building pieces ...")
    pieces = [B.build_player_piece(s) for s in P.PLAYER_STYLES]
    marker = pieces[0]
    runner = B.build_runner()
    for k, (style, m) in enumerate(zip(P.PLAYER_STYLES, pieces), start=1):
        save(m, f"piece-{style}.stl", "PLA", f"player {k}: one {style}")
    save(runner, "piece-runner.stl", "PLA", "one neutral runner")
    for lab, style, m in zip(P.PLAYER_LABELS, P.PLAYER_STYLES, pieces):
        save(B.build_plate(m, P.MARKERS_PER_PLAYER),
             f"game-pieces-{lab}.stl", "PLA",
             f"player {lab}: {P.MARKERS_PER_PLAYER} {style}s, one per column")
    save(B.build_plate(runner, P.RUNNERS), "plate-runners-x3.stl",
         "PLA", f"the shared runners ({P.RUNNERS})")

    save(B.build_fit_coupon(), "fit-test-coupon.stl", "PLA",
         "PRINT THIS FIRST -- bore fit check")

    # The test print: a corner of the real board, plus enough pieces to seat
    # one and stack another on it.
    if verbose:
        print("cutting the board stub ...")
    stub_body = B.build_board_stub(board_body)
    stub_nums = B.build_board_stub(numerals)
    cols = "/".join(str(c) for c in P.STUB_COLUMNS)
    save(stub_body, "stub-board-body.stl", "PLA",
         f"TEST PRINT -- real board corner, columns {cols}; load with "
         f"stub-board-numerals",
         cm3=stub_filament() - stub_nums.volume / 1000.0 if slab else None)
    save(stub_nums, "stub-board-numerals.stl", "PLA",
         "TEST PRINT -- the digits and their slice of each post")
    # one of each of the first STUB_PIECES shapes, so the test print checks
    # that a piece of one shape stacks on a piece of another
    spacing = 2 * P.PEG_MAX_R + 4.0
    want = P.PLAYER_STYLES[:P.STUB_PIECES]
    save(trimesh.util.concatenate(
             [R.placed(m, (k * spacing, 0, 0))
              for k, m in enumerate(pieces[:P.STUB_PIECES])]),
         f"stub-pieces-x{len(want)}.stl", "PLA",
         "TEST PRINT -- one of each: " + ", ".join(want)
         + " -- to seat and to stack")

    return (board_body, numerals, pieces, runner, stub_body, stub_nums, rows)


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def export_renders(board_body, numerals, pieces, runner, stub_body,
                   stub_nums, fast=False, verbose=True):
    marker = pieces[0]
    RENDER_DIR.mkdir(exist_ok=True)
    W, H = (760, 560) if fast else (1520, 1120)
    ss = 1 if fast else 2

    def shot(name, parts, **kw):
        t = time.time()
        img = R.render(parts, width=W, height=H, supersample=ss, **kw)
        img.save(RENDER_DIR / name)
        if verbose:
            print(f"  {name}  ({time.time() - t:.1f}s)")

    # Render the two-colour pair rather than the fused board: the column
    # numbers are unreadable as black-on-black, and this is what the AMS
    # would actually produce.
    bd = {"mesh": board_body, "color": C_BOARD}
    # The digits are inlaid dead flush, so their top faces and the box's sit
    # at exactly the same depth and the z-buffer cannot break the tie -- it
    # speckles. Lift them a hundredth of a millimetre FOR THE RENDER ONLY;
    # the exported mesh stays flush.
    nm = {"mesh": R.placed(numerals, (0, 0, 0.01)), "color": C_NUMERAL}
    board_all = [bd, nm]

    # 1 -- the whole board, three-quarter view from the players' side
    shot("01-board-iso.png", board_all,
         **R.frame([board_body], azimuth_deg=-90, elevation_deg=42, margin=0.70))

    # 2 -- straight down, orthographic: the ladder as a player reads it
    shot("02-board-plan.png", board_all,
         **R.frame([board_body], azimuth_deg=-90, elevation_deg=89.9,
                   margin=0.82, ortho=True),
         key_dir=(-0.3, -0.5, 1.0), edges=0.40)

    # 3 -- close on the summits of 5 / 6 / 7: the engraved numbers, the posts
    #      standing in the middle of them, and pieces seated on the surface
    sx, sy = B.summit(4)
    detail = list(board_all) + [
        {"mesh": place(marker, 7, P.ROWS[5] - 1), "color": C_PLAYERS[0]},
        {"mesh": place(marker, 6, P.ROWS[4] - 1), "color": C_PLAYERS[3]},
        {"mesh": place(marker, 5, P.ROWS[3] - 2), "color": C_PLAYERS[1]},
    ]
    shot("03-surface-detail.png", detail,
         eye=R.orbit_eye((sx + 14, sy + 14, 3), 205, -74, 34),
         target=(sx + 14, sy + 12, 4), fov_deg=32, edges=0.6)

    # 4 -- the two piece types, and a marker cut in half
    half_body, half_cap = R.section(marker, (0, 1, 0), (0, 0, 0))
    grp = [
        {"mesh": R.placed(marker, (-16, 0, 0)), "color": C_PLAYERS[0]},
        {"mesh": R.placed(runner, (0, 0, 0)), "color": C_RUNNER},
        {"mesh": R.placed(half_body, (16, 0, 0)), "color": C_PLAYERS[3]},
        {"mesh": R.placed(half_cap, (16, 0, 0)), "color": R.tint(C_PLAYERS[3])},
    ]
    cam4 = R.frame([p["mesh"] for p in grp], azimuth_deg=-88,
                   elevation_deg=14, margin=0.78)
    img4 = R.render(grp, width=W, height=H, supersample=ss, **cam4)
    anchors = R.screen_of([(-16, 0, 3), (0, 0, 3), (16, 0, 3)],
                          width=W, height=H, **cam4)
    R.annotate(img4, [
        dict(text=f"marker \u2014 {P.MARKERS_PER_PLAYER} per player, "
                  f"{P.PLAYERS} colours",
             px=tuple(anchors[0]), to=(0.05 * W, 0.84 * H), align="left"),
        dict(text=f"runner \u2014 {P.RUNNERS} shared, banded and taller",
             px=tuple(anchors[1]), to=(0.33 * W, 0.93 * H), align="left"),
        dict(text="the same marker, sectioned",
             px=tuple(anchors[2]), to=(0.66 * W, 0.84 * H), align="left"),
    ], font_size=max(13, int(0.016 * W)))
    img4.save(RENDER_DIR / "04-piece-anatomy.png")
    if verbose:
        print("  04-piece-anatomy.png")

    # 5 -- THE ONE THAT MATTERS: a collar, sectioned, with three pieces
    #      stacked on it. If the post/socket interface is wrong, it is wrong
    #      here and it costs nothing to find out.
    if P.BOARD_STYLE == "slab":
        collar = S.union_all([
            S.rounded_plate(0.0, 0.0, 44.0, 22.0, P.SLAB_T, 2.0),
            B._post(0.0, 0.0, P.SLAB_T),
        ])
    else:
        collar = B.build_cell(0.0, 0.0)
    rail = (S.strut((-19, 0), (19, 0), P.STRUT_W, P.STRUT_H)
            if P.BOARD_STYLE != "slab" else None)
    # Fuse before cutting. Sectioned separately they leave two cut faces on
    # the same plane, which z-fights into speckle exactly where the render
    # needs to be clearest.
    board_bit = S.union_all([c for c in (collar, rail) if c is not None])
    stack_parts = []
    heights = [P.PEG_BODY_H, P.PEG_BODY_H, P.RUNNER_BODY_H]
    for lvl, (mesh, col) in enumerate([(marker, C_PLAYERS[0]),
                                       (marker, C_PLAYERS[1]),
                                       (runner, C_RUNNER)]):
        z = SEAT_Z + sum(heights[:lvl])
        stack_parts.append((R.placed(mesh, (0, 0, z)), col))
    cut_scene = []
    for m, c in [(board_bit, C_BOARD)] + stack_parts:
        b, cp = R.section(m, (0, 1, 0), (0, 0, 0))
        if len(b.faces):
            cut_scene.append({"mesh": b, "color": c})
        if len(cp.faces):
            cut_scene.append({"mesh": cp, "color": R.tint(c)})
    # A true section elevation: orthographic, dead level, so the render can
    # be read off like a drawing instead of interpreted like a photograph.
    cam5 = R.frame([p["mesh"] for p in cut_scene], azimuth_deg=-90,
                   elevation_deg=0.0, margin=1.15, ortho=True)
    img5 = R.render(cut_scene, width=W, height=H, supersample=ss, **cam5)
    _annotate_stack(img5, cam5, W, H)
    img5.save(RENDER_DIR / "05-stacking-section.png")
    if verbose:
        print("  05-stacking-section.png")

    # 6 -- a plausible mid-game board, including two stacked cells
    scene = list(board_all)
    # banked markers: (column, row, player)
    banked = [(2, 1, 0), (4, 3, 1), (5, 2, 0), (6, 5, 2), (7, 4, 1),
              (7, 6, 3), (8, 2, 0), (9, 5, 3), (10, 1, 2), (11, 2, 1),
              (12, 1, 3), (3, 2, 2), (6, 8, 0), (5, 6, 3)]
    for col, row, pl in banked:
        scene.append({"mesh": place(pieces[pl], col, row),
                      "color": C_PLAYERS[pl]})
    # contested cells: player A stacked on player B
    for col, row, a, b in [(6, 5, 3, 2), (7, 4, 0, 1)]:
        scene.append({"mesh": place(pieces[a], col, row, 1, (P.PEG_BODY_H,)),
                      "color": C_PLAYERS[a]})
    # the three runners, mid-turn, one of them riding on a banked marker
    scene.append({"mesh": place(runner, 7, 7), "color": C_RUNNER})
    scene.append({"mesh": place(runner, 5, 3), "color": C_RUNNER})
    scene.append({"mesh": place(runner, 8, 2, 1, (P.PEG_BODY_H,)),
                  "color": C_RUNNER})
    # two columns claimed outright: a piece sitting on the number itself
    scene.append({"mesh": place(pieces[1], 2, P.ROWS[0] - 1),
                  "color": C_PLAYERS[1]})
    scene.append({"mesh": place(pieces[3], 11, P.ROWS[9] - 1),
                  "color": C_PLAYERS[3]})
    shot("06-assembly.png", scene,
         **R.frame([board_body], azimuth_deg=-84, elevation_deg=38, margin=0.73))

    # 7 -- THE TEST PRINT: the stub, with one piece seated and one stacked on
    #      it. This is the ~30 g, ~40 minute version of the whole board, so
    #      it is the render worth looking at before anything is printed.
    # Taken from the stub itself, not named, so the shot follows STUB_COLUMNS
    # wherever it is pointed. Both pieces go on ONE plain post: a piece on a
    # summit hides that column's number, and leaving the other plain post
    # bare is the only way to see whether its cap is the colour it should be.
    plain = [(i, r) for i, r in B.stub_cells() if not B.is_summit(i, r)]
    col, row = P.COLUMNS[plain[-1][0]], plain[-1][1]
    stack = place(marker, col, row, 1, (P.PEG_BODY_H,))
    stub = [{"mesh": stub_body, "color": C_BOARD},
            {"mesh": R.placed(stub_nums, (0, 0, 0.01)), "color": C_NUMERAL},
            {"mesh": place(marker, col, row), "color": C_PLAYERS[1]},
            {"mesh": stack, "color": C_PLAYERS[0]}]
    shot("07-test-print.png", stub,
         **R.frame([stub_body, stack], azimuth_deg=-95, elevation_deg=30,
                   margin=0.72))

    # 8 -- bed fit, drawn rather than rendered
    _bed_fit_diagram(board_body)
    if verbose:
        print("  08-bed-fit.png")


def _annotate_stack(img, cam, W, H):
    """Label the one interface the whole design hangs on."""
    z0 = SEAT_Z                                    # base piece sits on the pad
    z_top1 = z0 + P.PEG_BODY_H                     # top face of the base piece
    L, Rg = 0.30 * W, 0.70 * W

    items = [
        dict(at=(0.0, 0, B.seat_z() + P.POST_H * 0.5),
             to=(L, 0.90 * H), align="right",
             text=f"board post \u00d8{P.POST_D:.2f} \u00d7 {P.POST_H:.2f}"),
        dict(at=(P.PAD_OD / 2 - 2.0, 0, B.seat_z()),
             to=(Rg, 0.90 * H), align="left",
             text="skirt seats on the %s face"
                  % ("plate" if P.BOARD_STYLE == "slab" else "pad")),
        dict(at=(P.PEG_SOCKET_D / 2 - 0.4, 0, z0 + P.PEG_SOCKET_DEPTH * 0.45),
             to=(L, 0.66 * H), align="right",
             text=f"socket \u00d8{P.PEG_SOCKET_D:.2f} \u00d7 "
                  f"{P.PEG_SOCKET_DEPTH:.2f} deep"),
        dict(at=(0.8, 0, z0 + P.PEG_SOCKET_DEPTH + P.PEG_SOCKET_D * 0.35),
             to=(L, 0.44 * H), align="right",
             text=("45\u00b0 cone roof \u2014 no bridging"
                   if B.socket_bridge() < 1e-9 else
                   f"45\u00b0 cone roof, {B.socket_bridge():.1f} mm bridged")),
        dict(at=(P.PEG_BODY_PROFILE[0][0], 0, z_top1),
             to=(Rg, 0.62 * H), align="left",
             text=f"stack pitch {P.PEG_BODY_H:.2f} mm"),
        dict(at=(0.0, 0, z_top1 + P.PEG_BODY_H + P.PEG_POST_H * 0.5),
             to=(Rg, 0.40 * H), align="left",
             text=f"piece post \u00d8{P.PEG_POST_D:.2f} \u00d7 "
                  f"{P.PEG_POST_H:.2f}"),
        dict(at=(0.0, 0, z0 + 2 * P.PEG_BODY_H + P.RUNNER_BODY_H * 0.6),
             to=(L, 0.14 * H), align="right",
             text="runner rides on top"),
    ]
    pts = R.screen_of([i["at"] for i in items], width=W, height=H, **cam)
    R.annotate(img, [
        dict(text=i["text"], px=tuple(p), to=i["to"], align=i["align"])
        for i, p in zip(items, pts)
    ], font_size=max(13, int(0.016 * W)))


def _bed_fit_diagram(board_full):
    """Plan schematic of the board on the bed.

    Drawn from the strut, cell and shield lists rather than from the mesh: a
    dot scatter of 50k vertices looks like noise, whereas the lattice drawn as
    lines and rings is something you can read a dimension off. On a slab there
    is no lattice and no pad, so what is worth drawing is different: the
    outline, the band the raised lip occupies, and where the posts stand.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon
    from matplotlib.collections import LineCollection

    lo, hi = board_full.bounds
    w, h = hi[0] - lo[0], hi[1] - lo[1]
    ox, oy = (P.BED_X_DUAL - w) / 2 - lo[0], (P.BED_Y_DUAL - h) / 2 - lo[1]

    fig, ax = plt.subplots(figsize=(8.2, 8.2), dpi=170)
    ax.add_patch(Rectangle((0, 0), P.BED_X, P.BED_Y, facecolor="#e5e9f0",
                           edgecolor="#d8dee9", lw=1.0, zorder=0))
    ax.add_patch(Rectangle((0, 0), P.BED_X_DUAL, P.BED_Y_DUAL,
                           facecolor="#eceff4", edgecolor="#4c566a", lw=1.6,
                           zorder=0))
    ax.add_patch(Polygon([(x + ox, y + oy) for x, y in B.octagon()],
                         closed=True, facecolor="#e5e9f0", edgecolor="#4c566a",
                         lw=1.0, zorder=1))

    slab = P.BOARD_STYLE == "slab"

    if slab:
        # the inside edge of the raised lip, drawn the way slab_plate() makes
        # it: the outline scaled about its centre
        poly = np.asarray(B.octagon(), dtype=float)
        ctr = B.octagon_centre()
        k = ((max(abs(poly - ctr).max(axis=1)) - P.RIM_W)
             / max(abs(poly - ctr).max(axis=1)))
        ax.add_patch(Polygon([(x + ox, y + oy)
                              for x, y in (poly - ctr) * k + ctr],
                             closed=True, facecolor="#eceff4",
                             edgecolor="#4c566a", lw=0.8, ls=":", zorder=2))
    else:
        segs, widths = [], []
        for p0, p1, sw, _sh, _kind in B.final_struts():
            segs.append([(p0[0] + ox, p0[1] + oy), (p1[0] + ox, p1[1] + oy)])
            widths.append(sw * 1.4)
        ax.add_collection(LineCollection(segs, linewidths=widths,
                                         colors="#3b4252", zorder=2))

    for i in range(len(P.ROWS)):
        sx, sy = B.shield_xy(i)
        if not slab:
            ax.add_patch(Rectangle((sx + ox - P.PLAQUE_W / 2,
                                    sy + oy - P.PLAQUE_H / 2),
                                   P.PLAQUE_W, P.PLAQUE_H, facecolor="#3b4252",
                                   edgecolor="none", zorder=3))
        ax.text(sx + ox, sy + oy, str(P.COLUMNS[i]),
                color="#eceff4" if slab else "#d08770", ha="center",
                va="center", fontsize=6 if slab else 7, weight="bold",
                zorder=6)

    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        if not slab:
            ax.add_patch(Circle((cx + ox, cy + oy), P.PAD_OD / 2,
                                facecolor="#3b4252", edgecolor="none", zorder=4))
        ax.add_patch(Circle((cx + ox, cy + oy), P.POST_D / 2,
                            facecolor="#3b4252" if slab else "#eceff4",
                            edgecolor="none", zorder=5))

    bx, by = lo[0] + ox, lo[1] + oy
    ax.add_patch(Rectangle((bx, by), w, h, facecolor="none",
                           edgecolor="#5e81ac", lw=1.2, ls="--", zorder=7))
    ax.annotate("", (bx, by - 13), (bx + w, by - 13),
                arrowprops=dict(arrowstyle="<->", color="#bf616a", lw=1.4))
    ax.text(bx + w / 2, by - 22, f"{w:.0f} mm", ha="center", color="#bf616a",
            fontsize=11, weight="bold")
    ax.annotate("", (bx - 13, by), (bx - 13, by + h),
                arrowprops=dict(arrowstyle="<->", color="#bf616a", lw=1.4))
    ax.text(bx - 20, by + h / 2, f"{h:.0f} mm", va="center", rotation=90,
            color="#bf616a", fontsize=11, weight="bold")

    ax.set_xlim(-42, P.BED_X + 16)
    ax.set_ylim(-42, P.BED_Y + 26)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"Board on the H2D bed (DUAL nozzle — the board is two filaments)\n"
        f"{w:.0f} x {h:.0f} mm in a {P.BED_X_DUAL:.0f} x {P.BED_Y_DUAL:.0f} mm"
        f" envelope  —  {P.BED_X_DUAL - w:.0f} mm spare in X, "
        f"{P.BED_Y_DUAL - h:.0f} mm in Y",
        fontsize=12, color="#2e3440", pad=14)
    fig.tight_layout()
    fig.savefig(RENDER_DIR / "08-bed-fit.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------

def print_report(rows, board_body):
    lo, hi = board_body.bounds
    print()
    print(f"{'file':<26}{'solid':>6}{'tris':>8}{'cm3':>9}{'grams':>8}  note")
    print("-" * 96)
    for name, wt, nf, cm3, g, note in rows:
        print(f"{name:<26}{('yes' if wt else 'NO'):>6}{nf:>8}{cm3:>9.1f}{g:>8.1f}  {note}")
    print("-" * 96)
    # By NAME, not by row index. Indexed, this silently followed whatever
    # order export_stls() happened to save things in -- and when a file was
    # added it started billing the set for 44 runners and 3 marker plates.
    g = {name: grams for name, _wt, _nf, _cm3, grams, _note in rows}
    total = (g["board-body.stl"] + g["board-numerals.stl"]
             + sum(g[f"piece-{s}.stl"] for s in P.PLAYER_STYLES)
               * P.MARKERS_PER_PLAYER
             + g["piece-runner.stl"] * P.RUNNERS)
    how = (f"board at {100*P.SLAB_INFILL:.0f}% infill, pieces solid"
           if P.BOARD_STYLE == "slab" else "100% infill")
    print(f"full set, {how}: ~{total:.0f} g "
          f"(1 board + {P.MARKERS_PER_PLAYER} each of "
          f"{'/'.join(P.PLAYER_STYLES)} + {P.RUNNERS} runners)")
    print(f"board envelope: {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f} mm "
          f"(dual-nozzle bed {P.BED_X_DUAL:.0f} x {P.BED_Y_DUAL:.0f} x "
          f"{P.BED_Z:.0f}; {P.BED_X_DUAL-(hi[0]-lo[0]):.0f} spare in X, "
          f"{P.BED_Y_DUAL-(hi[1]-lo[1]):.0f} in Y)")
    print(f"cells: {sum(P.ROWS)}   columns: {len(P.COLUMNS)}   ladder: {P.ROWS}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stl", action="store_true", help="STLs only")
    ap.add_argument("--renders", action="store_true", help="renders only")
    ap.add_argument("--fast", action="store_true", help="quick low-res renders")
    a = ap.parse_args(argv)
    do_stl = a.stl or not a.renders
    do_ren = a.renders or not a.stl

    t0 = time.time()
    (board_body, numerals, pieces, runner,
     stub_body, stub_nums, rows) = export_stls(verbose=do_stl)
    if do_ren:
        print("rendering ...")
        export_renders(board_body, numerals, pieces, runner, stub_body,
                       stub_nums, fast=a.fast)
    if do_stl:
        print_report(rows, board_body)
    print(f"\ndone in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
