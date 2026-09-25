"""A picture of what is about to be printed.

Cheap insurance: a 200ms PNG catches a mis-scaled trace or a pocket crowding
the bin wall before a 40 minute print does.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.geometry import Polygon

from .config import GRID_PITCH_MM
from .model import BinSpec


def _ring(ax, poly: Polygon, **kw):
    x, y = poly.exterior.xy
    ax.plot(x, y, **kw)
    for interior in poly.interiors:
        ix, iy = interior.xy
        ax.plot(ix, iy, **kw)


def render(
    outline: Polygon,
    pocket: Polygon,
    spec: BinSpec,
    path: str,
    title: str = "",
) -> str:
    """Draw the bin footprint, grid, traced tool and finished pocket."""
    w = spec.length_u * GRID_PITCH_MM - 0.5
    h = spec.width_u * GRID_PITCH_MM - 0.5

    fig, ax = plt.subplots(figsize=(max(4, w / 25), max(4, h / 25)))
    ax.add_patch(
        Rectangle((-w / 2, -h / 2), w, h, facecolor="#eef1f5",
                  edgecolor="#43506b", linewidth=1.6, zorder=0)
    )
    for i in range(1, spec.length_u):
        x = -w / 2 + i * GRID_PITCH_MM
        ax.plot([x, x], [-h / 2, h / 2], color="#b6c0d0", lw=0.8, zorder=1)
    for i in range(1, spec.width_u):
        y = -h / 2 + i * GRID_PITCH_MM
        ax.plot([-w / 2, w / 2], [y, y], color="#b6c0d0", lw=0.8, zorder=1)

    _ring(ax, pocket, color="#c2410c", lw=2.0, zorder=3)
    ax.fill(*pocket.exterior.xy, color="#fdba74", alpha=0.45, zorder=2)

    # The tool itself, centred the same way the pocket was.
    from .geometry import centre_on

    minx, miny, maxx, maxy = pocket.bounds
    shifted = centre_on(outline, (minx + maxx) / 2, (miny + maxy) / 2)
    _ring(ax, shifted, color="#1e3a5f", lw=1.3, ls="--", zorder=4)

    ax.set_aspect("equal")
    ax.set_xlim(-w / 2 - 6, w / 2 + 6)
    ax.set_ylim(-h / 2 - 6, h / 2 + 6)
    ax.set_xlabel("mm")
    ax.set_title(title or spec.describe(), fontsize=9)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def render_drawer(plan_result, path: str) -> str:
    """Draw the drawer, the grid that fits, the baseplate tiles and the margins."""
    from .config import GRID_PITCH_MM

    W, D = plan_result.drawer_w_mm, plan_result.drawer_d_mm
    mx, my = plan_result.margin_x_mm, plan_result.margin_y_mm

    fig, ax = plt.subplots(figsize=(max(5, W / 55), max(4, D / 55)))

    # The drawer itself.
    ax.add_patch(Rectangle((0, 0), W, D, facecolor="#f6f7f9",
                           edgecolor="#2d3748", lw=2.0, zorder=0))
    # Dead space, shaded.
    ax.add_patch(Rectangle((0, 0), W, D, facecolor="#fde2e2", zorder=1))
    ax.add_patch(Rectangle((mx, my), plan_result.units_x * GRID_PITCH_MM,
                           plan_result.units_y * GRID_PITCH_MM,
                           facecolor="#eef1f5", edgecolor="none", zorder=2))

    # Grid lines.
    for i in range(plan_result.units_x + 1):
        x = mx + i * GRID_PITCH_MM
        ax.plot([x, x], [my, my + plan_result.units_y * GRID_PITCH_MM],
                color="#c3ccd9", lw=0.7, zorder=3)
    for j in range(plan_result.units_y + 1):
        y = my + j * GRID_PITCH_MM
        ax.plot([mx, mx + plan_result.units_x * GRID_PITCH_MM], [y, y],
                color="#c3ccd9", lw=0.7, zorder=3)

    # Tile boundaries, drawn heavier -- these are the separate prints.
    palette = ["#1e3a5f", "#c2410c", "#166534", "#6b21a8",
               "#9a3412", "#0f766e", "#7c2d12", "#3730a3"]
    for n, t in enumerate(plan_result.tiles):
        x = mx + t.origin_x_u * GRID_PITCH_MM
        y = my + t.origin_y_u * GRID_PITCH_MM
        w = t.length_u * GRID_PITCH_MM
        h = t.width_u * GRID_PITCH_MM
        ax.add_patch(Rectangle((x + 0.6, y + 0.6), w - 1.2, h - 1.2,
                               facecolor="none", edgecolor=palette[n % len(palette)],
                               lw=2.2, zorder=4))
        ax.text(x + w / 2, y + h / 2, f"{t.length_u}x{t.width_u}",
                ha="center", va="center", fontsize=11, zorder=5,
                color=palette[n % len(palette)], fontweight="bold")

    ax.set_aspect("equal")
    ax.set_xlim(-12, W + 12)
    ax.set_ylim(-12, D + 12)
    ax.set_xlabel("mm")
    ax.set_title(
        f"{W:.0f} x {D:.0f} mm drawer -> {plan_result.units_x} x "
        f"{plan_result.units_y} units, {len(plan_result.tiles)} baseplate tiles\n"
        f"margins {mx:.1f} mm sides / {my:.1f} mm front-back (shaded)",
        fontsize=9,
    )
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def render_layout(layout, path: str, title: str = "", code: str = "") -> str:
    """Top-down view of a packed drawer, on grid references rather than mm.

    Positions are named A1, C4, A1:G5 so a change can be asked for out loud
    without anyone measuring anything.
    """
    from .config import GRID_PITCH_MM
    from .layout import cell_range

    plan_result = layout.plan
    W, D = plan_result.drawer_w_mm, plan_result.drawer_d_mm
    mx, my = plan_result.margin_x_mm, plan_result.margin_y_mm
    ux, uy = plan_result.units_x, plan_result.units_y

    fig, ax = plt.subplots(figsize=(max(8, W / 38), max(7, D / 38) + 0.9))
    ax.add_patch(Rectangle((0, 0), W, D, facecolor="#fdeaea",
                           edgecolor="#2d3748", lw=2.2, zorder=0))
    ax.add_patch(Rectangle((mx, my), ux * GRID_PITCH_MM, uy * GRID_PITCH_MM,
                           facecolor="#f2f4f7", edgecolor="none", zorder=1))

    for i in range(ux + 1):
        x = mx + i * GRID_PITCH_MM
        ax.plot([x, x], [my, my + uy * GRID_PITCH_MM],
                color="#cfd6e0", lw=0.6, zorder=2)
    for j in range(uy + 1):
        y = my + j * GRID_PITCH_MM
        ax.plot([mx, mx + ux * GRID_PITCH_MM], [y, y],
                color="#cfd6e0", lw=0.6, zorder=2)

    palette = ["#1e3a5f", "#c2410c", "#166534", "#6b21a8", "#0f766e",
               "#9a3412", "#3730a3", "#854d0e", "#9f1239", "#155e75"]

    # Total capacity per item, so a shortfall is judged across all its bins.
    per_item_cap: dict[str, int] = {}
    per_item_wanted: dict[str, int] = {}
    for pl in layout.placements:
        if pl.item.width_mm > 0:
            per_item_cap[pl.item.name] = (
                per_item_cap.get(pl.item.name, 0) + pl.item.capacity())
            per_item_wanted[pl.item.name] = pl.item.wanted()
    for name in list(per_item_wanted):
        if per_item_cap.get(name, 0) >= per_item_wanted[name]:
            per_item_wanted.pop(name)

    seen: dict[str, str] = {}
    for p in layout.placements:
        colour = seen.setdefault(p.item.name, palette[len(seen) % len(palette)])
        x = mx + p.x_u * GRID_PITCH_MM + 1.2
        y = my + p.y_u * GRID_PITCH_MM + 1.2
        w = p.length_u * GRID_PITCH_MM - 2.4
        h = p.width_u * GRID_PITCH_MM - 2.4
        ax.add_patch(Rectangle((x, y), w, h, facecolor=colour, alpha=0.20,
                               edgecolor=colour, lw=1.8, zorder=3))
        label = p.item.name if p.item.measured else f"{p.item.name} ?"
        ref = cell_range(p.x_u, p.y_u, p.length_u, p.width_u)
        # Flag a bin that holds less than is owned -- the single most useful
        # thing to see on a layout, and invisible from footprint alone.
        short = ""
        if p.item.width_mm > 0:
            cap = p.item.capacity()
            want = per_item_wanted.get(p.item.name, 0)
            if cap < want:
                short = f"holds {cap} of {want}"
        if short:
            ax.add_patch(Rectangle((x, y), w, h, facecolor="none",
                                   edgecolor="#b91c1c", lw=2.6, ls=(0, (4, 2)),
                                   zorder=5))
        fs = max(5.5, min(9.5, w / (0.60 * max(7, len(label)))))
        ax.text(x + w / 2, y + h / 2 + (4.5 if h > 30 else 0), label,
                ha="center", va="center", fontsize=fs, color=colour,
                fontweight="bold", zorder=4)
        if h > 30:
            ax.text(x + w / 2, y + h / 2 - 5.5, ref, ha="center", va="center",
                    fontsize=max(6, fs - 1.5), color=colour, zorder=4,
                    fontweight="bold", alpha=0.95)
            ax.text(x + w / 2, y + h / 2 - 15,
                    f"{p.length_u}x{p.width_u} · {p.item.height_units()}U"
                    + ("  rot" if p.rotated else ""),
                    ha="center", va="center", fontsize=6.5,
                    color=colour, alpha=0.75, zorder=4)
        else:
            ax.text(x + w / 2, y + h / 2 - 7, ref, ha="center", va="center",
                    fontsize=6.5, color=colour, alpha=0.95, zorder=4)
        if short:
            ax.text(x + w / 2, y + 4.5, short, ha="center", va="bottom",
                    fontsize=6.8, color="#b91c1c", fontweight="bold", zorder=6)

    # Grid references in place of millimetres.
    ax.set_xticks([mx + (i + 0.5) * GRID_PITCH_MM for i in range(ux)])
    ax.set_xticklabels([chr(ord("A") + i) for i in range(ux)], fontsize=9,
                       fontweight="bold", color="#43506b")
    ax.set_yticks([my + (j + 0.5) * GRID_PITCH_MM for j in range(uy)])
    ax.set_yticklabels([str(j + 1) for j in range(uy)], fontsize=9,
                       fontweight="bold", color="#43506b")
    ax.tick_params(length=0)
    ax.set_xlabel("column  ·  row 1 is the front of the drawer", fontsize=8,
                  color="#5a6678")

    interior = GRID_PITCH_MM - 0.5 - 2 * 2.4
    legend = (
        f"1 square = 42 × 42 mm pitch   ·   bin outside {GRID_PITCH_MM - 0.5:.1f} mm "
        f"per unit   ·   usable inside ≈ {interior:.1f} mm per unit\n"
        f"height 1U = 7 mm (usable depth = (U−1) × 7)   ·   drawer "
        f"{W:.0f} × {D:.0f}"
        + (f" × {plan_result.drawer_h_mm:.0f}" if plan_result.drawer_h_mm else "")
        + f" mm   ·   margins {mx:.1f} mm sides / {my:.1f} mm front-back (pink)"
    )
    ax.text(0.5, -0.085, legend, transform=ax.transAxes, ha="center", va="top",
            fontsize=7.8, color="#43506b",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f2f4f7",
                      edgecolor="#cfd6e0", linewidth=0.8))

    if layout.unplaced:
        short = {}
        for i in layout.unplaced:
            lu, wu = i.footprint_units()
            short[i.name] = short.get(i.name, 0) + 1
        lines = ", ".join(f"{n} x{q}" for n, q in sorted(short.items()))
        need = sum(i.footprint_units()[0] * i.footprint_units()[1]
                   for i in layout.unplaced)
        ax.text(0.5, 1.004,
                f"DOES NOT FIT — {len(layout.unplaced)} bins unplaced "
                f"({lines}), needing {need} more units",
                transform=ax.transAxes, ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#b91c1c", zorder=10,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee2e2",
                          edgecolor="#b91c1c", linewidth=1.2))

    ax.set_aspect("equal")
    ax.set_xlim(-14, W + 14)
    ax.set_ylim(-14, D + 14)
    head = title or (f"{code} — " if code else "")
    ax.set_title(
        f"{head}{ux} × {uy} units, {len(layout.placements)} bins, "
        f"{layout.free_units} of {plan_result.total_units} units free"
        + ("" if layout.all_measured else
           "\nCONTAINS UNMEASURED PLACEHOLDER SIZES — marked ?"),
        fontsize=11,
        color="#1f2933" if layout.all_measured else "#b91c1c",
        pad=32 if layout.unplaced else 10,
    )
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path
