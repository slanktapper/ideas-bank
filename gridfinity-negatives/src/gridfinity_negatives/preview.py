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
