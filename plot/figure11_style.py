from __future__ import annotations

from pathlib import Path
from typing import Final

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure


# Final physical size of each panel in the three-panel CCS figure.
# Three panels at 0.315\textwidth fit safely in one figure* row.
PANEL_SIZE: Final[tuple[float, float]] = (2.16, 1.8)

LP_SYMBOL: Final[str] = r"$LP_D$"

# Keep the same population encoding in the density and mix-zone panels.
POPULATION_STYLE: Final[dict[int, dict[str, str]]] = {
    512: {"color": "#000000", "marker": "o"},
    1024: {"color": "#0072B2", "marker": "s"},
    1536: {"color": "#CC79A7", "marker": "^"},
}

# Encode source redundantly:
#   SUMO      = solid line + filled marker
#   Synthetic = dashed line + hollow marker
SOURCE_STYLE: Final[dict[str, dict[str, object]]] = {
    "SUMO": {
        "linestyle": "-",
        "linewidth": 1.42,
        "filled": True,
        "zorder": 6,
    },
    "Synthetic": {
        "linestyle": (0, (5.5, 2.0)),
        "linewidth": 1.15,
        "filled": False,
        "zorder": 4,
    },
}


def apply_ccs_style() -> None:
    """Apply one typography and line system to all Figure 11 panels."""
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": [
                "Libertinus Serif",
                "Linux Libertine O",
                "DejaVu Serif",
            ],
            "mathtext.fontset": "stix",
            "font.size": 7.2,
            "axes.labelsize": 7.6,
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.6,
            "legend.fontsize": 5.4,
            "axes.linewidth": 0.62,
            "xtick.major.width": 0.58,
            "ytick.major.width": 0.58,
            "xtick.major.size": 2.4,
            "ytick.major.size": 2.4,
            "lines.solid_capstyle": "round",
            "lines.dash_capstyle": "round",
            "legend.frameon": False,
            "legend.handlelength": 1.75,
            "legend.handletextpad": 0.35,
            "legend.columnspacing": 0.62,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def style_axis(ax: Axes) -> None:
    """Apply identical axes, grid, and tick styling."""
    ax.set_axisbelow(True)
    ax.grid(
    True,
    which="major",
    linewidth=0.3,
    alpha=0.55,
    zorder=0,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(
        axis="both",
        direction="out",
        length=2.4,
        width=0.58,
        pad=1.8,
    )


def set_panel_margins(fig: Figure) -> None:
    """Use identical canvas margins for all three panel PDFs."""
    fig.subplots_adjust(
        left=0.215,
        right=0.970,
        bottom=0.305,
        top=0.970,
    )


def save_panel(fig: Figure, pdf_path: Path, png_path: Path) -> None:
    """Save with a fixed canvas; never recrop panels independently."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=300)
