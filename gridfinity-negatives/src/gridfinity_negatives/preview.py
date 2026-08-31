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
