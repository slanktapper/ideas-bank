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
C_BOARD   = (0.185, 0.195, 0.220)   # PETG Basic, black
C_NUMERAL = (0.950, 0.450, 0.080)   # PETG Basic, orange
C_CUT     = (0.620, 0.640, 0.680)   # section-cut surfaces
C_PLAYERS = [
    (0.800, 0.140, 0.140),          # PLA Basic, red
    (0.920, 0.930, 0.900),          # PLA Basic, jade white
    (0.360, 0.270, 0.600),          # PLA Basic, indigo purple
    (0.130, 0.380, 0.780),          # PLA Basic, blue
]
C_RUNNER  = (0.970, 0.800, 0.100)   # PETG Basic, yellow

DENSITY = {"PLA": 1.24, "PETG": 1.27}   # g/cm^3


# ---------------------------------------------------------------------------
# placement
# ---------------------------------------------------------------------------

# A piece seats when its shoulder lands on the collar rim, not when its pin
# bottoms out -- the socket is cut deeper than the pin is long precisely so
# that this is true. Stack height is therefore exact and repeatable.
SEAT_Z = P.COLLAR_H - P.PEG_PIN_H


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

    def save(mesh, name, material, note):
        path = STL_DIR / name
        mesh.export(path)
        cm3 = mesh.volume / 1000.0
        rows.append((name, mesh.is_watertight, len(mesh.faces), cm3,
                     cm3 * DENSITY[material], note))
        if verbose:
            print(f"  wrote {name}")

    if verbose:
        print("building board ...")
    board_full = B.build_board(with_numerals=True, verbose=verbose)
    board_body = B.build_board(with_numerals=False)
    numerals = B.build_board(numerals_only=True)

    save(board_full, "board.stl", "PETG", "single colour, digits fused in")
    save(board_body, "board-body.stl", "PETG", "two-colour: load with numerals")
    save(numerals, "board-numerals.stl", "PETG", "two-colour: second material")

    if verbose:
        print("building pieces ...")
    marker = B.build_marker()
    runner = B.build_runner()
    save(marker, "piece-marker.stl", "PLA", "one player marker")
    save(runner, "piece-runner.stl", "PLA", "one neutral runner")
    save(B.build_plate(marker, P.MARKERS_PER_PLAYER), "plate-markers-x11.stl",
         "PLA", f"one player's set ({P.MARKERS_PER_PLAYER})")
    save(B.build_plate(runner, P.RUNNERS), "plate-runners-x3.stl",
         "PLA", f"the shared runners ({P.RUNNERS})")

    save(B.build_fit_coupon(), "fit-test-coupon.stl", "PLA",
         "PRINT THIS FIRST -- bore fit check")

    return board_full, board_body, numerals, marker, runner, rows


# ---------------------------------------------------------------------------
# renders
# ---------------------------------------------------------------------------

def export_renders(board_body, numerals, marker, runner, fast=False, verbose=True):
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
    nm = {"mesh": numerals, "color": C_NUMERAL}
    board_all = [bd, nm]

    # 1 -- the whole board, three-quarter view from the players' side
    shot("01-board-iso.png", board_all,
         **R.frame([board_body], azimuth_deg=-90, elevation_deg=42, margin=0.70))

    # 2 -- straight down, orthographic: the ladder, and that the lattice is open
    shot("02-board-plan.png", board_all,
         **R.frame([board_body], azimuth_deg=-90, elevation_deg=89.9,
                   margin=0.82, ortho=True),
         key_dir=(-0.3, -0.5, 1.0), edges=0.40)

    # 3 -- close on the foot of columns 6/7/8: collars, struts, diagonals,
    #      plaques, and how the lattice welds into the rings
    shot("03-lattice-detail.png", board_all,
         eye=R.orbit_eye((88, 4, 4), 145, -72, 30), target=(88, 4, 2),
         fov_deg=30, edges=0.6)

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
    #      stacked in it. If the pin/socket interface is wrong, it is wrong
    #      here and it costs nothing to find out.
    collar = S.tube(0, 0, P.COLLAR_OD / 2, P.COLLAR_BORE / 2, 0, P.COLLAR_H,
                    segs=P.COLLAR_SEGS, top_chamfer=P.COLLAR_CHAMFER)
    rail = S.strut((-17, 0), (17, 0), P.STRUT_W, P.STRUT_H)
    # Fuse before cutting. Sectioned separately they leave two cut faces on
    # the same plane, which z-fights into speckle exactly where the render
    # needs to be clearest.
    board_bit = S.union_all([collar, rail])
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
        scene.append({"mesh": place(marker, col, row), "color": C_PLAYERS[pl]})
    # contested cells: player A stacked on player B
    for col, row, a, b in [(6, 5, 3, 2), (7, 4, 0, 1)]:
        scene.append({"mesh": place(marker, col, row, 1, (P.PEG_BODY_H,)),
                      "color": C_PLAYERS[a]})
    # the three runners, mid-turn, one of them riding on a banked marker
    scene.append({"mesh": place(runner, 7, 7), "color": C_RUNNER})
    scene.append({"mesh": place(runner, 5, 3), "color": C_RUNNER})
    scene.append({"mesh": place(runner, 8, 2, 1, (P.PEG_BODY_H,)),
                  "color": C_RUNNER})
    shot("06-assembly.png", scene,
         **R.frame([board_body], azimuth_deg=-84, elevation_deg=38, margin=0.73))

    # 7 -- bed fit, drawn rather than rendered
    _bed_fit_diagram(board_body)
    if verbose:
        print("  07-bed-fit.png")


def _annotate_stack(img, cam, W, H):
    """Label the one interface the whole design hangs on."""
    z0 = SEAT_Z                                   # base piece origin
    z_top1 = z0 + P.PEG_PIN_H + P.PEG_BODY_H      # top face of the base piece
    L, Rg = 0.30 * W, 0.70 * W

    items = [
        dict(at=(P.COLLAR_BORE / 2, 0, P.COLLAR_H * 0.30),
             to=(L, 0.93 * H), align="right",
             text=f"collar bore \u00d8{P.COLLAR_BORE:.2f}, through"),
        dict(at=(0.0, 0, z0 + P.PEG_PIN_H * 0.55),
             to=(Rg, 0.87 * H), align="left",
             text=f"pin \u00d8{P.PEG_PIN_D:.2f} \u00d7 {P.PEG_PIN_H:.2f} long"),
        dict(at=(5.2, 0, P.COLLAR_H),
             to=(Rg, 0.72 * H), align="left",
             text="shoulder seats on the rim"),
        dict(at=(2.0, 0, z_top1 - P.PEG_SOCKET_DEPTH * 0.5),
             to=(L, 0.46 * H), align="right",
             text=f"socket \u00d8{P.PEG_SOCKET_D:.2f} \u00d7 {P.PEG_SOCKET_DEPTH:.2f} deep"),
        dict(at=(5.6, 0, z_top1),
             to=(Rg, 0.50 * H), align="left",
             text=f"stack pitch {P.PEG_BODY_H:.2f} mm"),
        dict(at=(0.0, 0, z0 + P.PEG_PIN_H + 2 * P.PEG_BODY_H + 6.0),
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

    Drawn from the strut and cell lists rather than from the mesh: a dot
    scatter of 50k vertices looks like noise, whereas the lattice drawn as
    lines and rings is something you can actually read a dimension off.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    from matplotlib.collections import LineCollection

    lo, hi = board_full.bounds
    w, h = hi[0] - lo[0], hi[1] - lo[1]
    ox, oy = (P.BED_X - w) / 2 - lo[0], (P.BED_Y - h) / 2 - lo[1]

    fig, ax = plt.subplots(figsize=(8.2, 8.2), dpi=170)
    ax.add_patch(Rectangle((0, 0), P.BED_X, P.BED_Y, facecolor="#eceff4",
                           edgecolor="#4c566a", lw=1.6, zorder=0))

    segs, widths = [], []
    for p0, p1, sw, _sh, _kind in B.final_struts():
        segs.append([(p0[0] + ox, p0[1] + oy), (p1[0] + ox, p1[1] + oy)])
        widths.append(sw * 1.5)
    ax.add_collection(LineCollection(segs, linewidths=widths,
                                     colors="#3b4252", zorder=2))

    for i, r in B.all_cells():
        cx, cy = B.cell_xy(i, r)
        ax.add_patch(Circle((cx + ox, cy + oy), P.COLLAR_OD / 2,
                            facecolor="#3b4252", edgecolor="none", zorder=3))
        ax.add_patch(Circle((cx + ox, cy + oy), P.COLLAR_BORE / 2,
                            facecolor="#eceff4", edgecolor="none", zorder=4))

    for i, num in enumerate(P.COLUMNS):
        cx, _ = B.cell_xy(i, 0)
        ax.add_patch(Rectangle((cx + ox - P.PLAQUE_W / 2,
                                P.PLAQUE_DY + oy - P.PLAQUE_H / 2),
                               P.PLAQUE_W, P.PLAQUE_H, facecolor="#3b4252",
                               edgecolor="none", zorder=3))
        ax.text(cx + ox, P.PLAQUE_DY + oy, str(num), color="#d08770",
                ha="center", va="center", fontsize=8, weight="bold", zorder=5)

    bx, by = lo[0] + ox, lo[1] + oy
    ax.add_patch(Rectangle((bx, by), w, h, facecolor="none",
                           edgecolor="#5e81ac", lw=1.2, ls="--", zorder=6))
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
        f"Board on the H2D bed (single nozzle)\n"
        f"{w:.0f} x {h:.0f} mm in a {P.BED_X:.0f} x {P.BED_Y:.0f} mm envelope"
        f"  —  {P.BED_X - w:.0f} mm spare in X, {P.BED_Y - h:.0f} mm in Y",
        fontsize=12, color="#2e3440", pad=14)
    fig.tight_layout()
    fig.savefig(RENDER_DIR / "07-bed-fit.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------

def print_report(rows, board_full):
    lo, hi = board_full.bounds
    print()
    print(f"{'file':<26}{'solid':>6}{'tris':>8}{'cm3':>9}{'grams':>8}  note")
    print("-" * 96)
    for name, wt, nf, cm3, g, note in rows:
        print(f"{name:<26}{('yes' if wt else 'NO'):>6}{nf:>8}{cm3:>9.1f}{g:>8.1f}  {note}")
    print("-" * 96)
    total = (rows[0][4]
             + rows[4][4] * P.PLAYERS * P.MARKERS_PER_PLAYER
             + rows[5][4] * P.RUNNERS)
    print(f"full set, 100% infill: ~{total:.0f} g "
          f"(1 board + {P.PLAYERS}x{P.MARKERS_PER_PLAYER} markers "
          f"+ {P.RUNNERS} runners)")
    print(f"board envelope: {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f} mm "
          f"(bed {P.BED_X:.0f} x {P.BED_Y:.0f} x {P.BED_Z:.0f})")
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
    board_full, board_body, numerals, marker, runner, rows = export_stls(verbose=do_stl)
    if do_ren:
        print("rendering ...")
        export_renders(board_body, numerals, marker, runner, fast=a.fast)
    if do_stl:
        print_report(rows, board_full)
    print(f"\ndone in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
