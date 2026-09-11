from __future__ import annotations

from pathlib import Path
from typing import Final
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

NUM_USERS: Final[int] = 512
BASE_SCENARIO_NAME: Final[str] = f"scenario_result_{NUM_USERS}_sumo"

DATA_ROOT: Final[Path] = Path("output/data")
OUTPUT_ROOT: Final[Path] = Path("output/images")
SCORE_COLUMN: Final[str] = "privacy_score"

OUTPUT_PDF: Final[Path] = (
    OUTPUT_ROOT / f"privacy_leakage_q1_{NUM_USERS}_ccs_m.pdf"
)
OUTPUT_PNG: Final[Path] = (
    OUTPUT_ROOT / f"privacy_leakage_q1_{NUM_USERS}_ccs.png"
)

LP_SYMBOL: Final[str] = r"$LP_D$"

# Preserve the scenario-specific paths from your current script.
FILES: dict[str, Path] = {
    "BLE": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_BW1"
        / f"single_ble_{BASE_SCENARIO_NAME}_BW1.csv"
    ),
    "LTE": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_LW1"
        / f"single_lte_{BASE_SCENARIO_NAME}_LW1.csv"
    ),
    "WiFi": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_all1"
        / f"single_wifi_{BASE_SCENARIO_NAME}_all1.csv"
    ),
    "LTE+BLE": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_LB1"
        / f"multi_protocol_{BASE_SCENARIO_NAME}_LB1.csv"
    ),
    "LTE+WiFi": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_LW1"
        / f"multi_protocol_{BASE_SCENARIO_NAME}_LW1.csv"
    ),
    "BLE+WiFi": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_BW1"
        / f"multi_protocol_{BASE_SCENARIO_NAME}_BW1.csv"
    ),
    "LTE+BLE+WiFi": (
        DATA_ROOT
        / f"{BASE_SCENARIO_NAME}_all1"
        / f"multi_protocol_{BASE_SCENARIO_NAME}_all1.csv"
    ),
}


# -----------------------------------------------------------------------------
# Camera-ready visual style
# -----------------------------------------------------------------------------

# Generate directly at the final CCS single-column width. The extra height
# reserves space for the two bottom legend rows.
FIGURE_SIZE: Final[tuple[float, float]] = (3.35, 2.1)

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": [
            "Libertinus Serif",
            "Linux Libertine O",
            "DejaVu Serif",
        ],
        "mathtext.fontset": "stix",
        "font.size": 7.5,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "legend.fontsize": 6.2,
        "axes.linewidth": 0.65,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.solid_capstyle": "round",
        "lines.dash_capstyle": "round",
        "legend.frameon": False,
        "legend.handlelength": 2.2,
        "legend.handletextpad": 0.42,
        "legend.columnspacing": 0.70,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

# Sparse, hollow markers improve curve identification without reproducing the
# clutter of the earlier marker-heavy figure. Marker positions are staggered
# so near-overlapping curves do not place their markers on top of each other.
STYLES: dict[str, dict[str, object]] = {
    "LTE+BLE+WiFi": {
        "color": "#000000",
        "linestyle": "-",
        "linewidth": 1.95,
        "marker": "o",
        "markevery": (18, 105),
        "zorder": 7,
    },
    "LTE+BLE": {
        "color": "#CC79A7",
        "linestyle": (0, (5.0, 1.5)),
        "linewidth": 1.42,
        "marker": "P",
        "markevery": (60, 105),
        # Draw above the black line because these curves nearly overlap.
        "zorder": 8,
    },
        "BLE+WiFi": {
        "color": "#56B4E9",
        "linestyle": (0, (4.0, 1.6)),
        "linewidth": 1.28,
        "marker": "D",
        "markevery": (50, 105),
        "zorder": 5,
    },
    "BLE": {
        "color": "#0072B2",
        "linestyle": "--",
        "linewidth": 1.28,
        "marker": "s",
        "markevery": (8, 105),
        "zorder": 5,
    },
    
    "LTE+WiFi": {
        "color": "#D55E00",
        "linestyle": "-.",
        "linewidth": 1.28,
        "marker": "X",
        "markevery": (28, 105),
        "zorder": 4,
    },
   
    "LTE": {
        "color": "#E69F00",
        "linestyle": (0, (2.8, 1.4)),
        "linewidth": 1.22,
        "marker": "v",
        "markevery": (42, 105),
        "zorder": 3,
    },
    "WiFi": {
        "color": "#009E73",
        "linestyle": ":",
        "linewidth": 1.32,
        "marker": "^",
        "markevery": (74, 105),
        "zorder": 3,
    },
}

PLOT_ORDER: Final[list[str]] = [
    "WiFi",
    "LTE",
    "BLE",
    "LTE+WiFi",
    "BLE+WiFi",
    "LTE+BLE+WiFi",
    "LTE+BLE",
]

#MULTI_LEGEND_ORDER: Final[list[str]] = [
 #   "LTE+BLE+WiFi",
 #   "LTE+BLE",
 #   "LTE+WiFi",
 #   "BLE+WiFi",
#]
#SINGLE_LEGEND_ORDER: Final[list[str]] = ["BLE", "LTE", "WiFi"]
# Legend entries appear visually from left to right in this order:
# LTE+BLE+WiFi, LTE+BLE, BLE+WiFi, BLE,
# LTE+WiFi, LTE, WiFi
LEGEND_ROW_1: Final[list[str]] = [
    "LTE+BLE+WiFi",
    "LTE+BLE",
    "BLE+WiFi",
    "BLE",
]

LEGEND_ROW_2: Final[list[str]] = [
    "LTE+WiFi",
    "LTE",
    "WiFi",
]

LEGEND_ORDER: Final[list[str]] = LEGEND_ROW_1 + LEGEND_ROW_2

# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------

def load_scores(path: Path) -> np.ndarray:
    """Load and validate one privacy-score vector."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing input file: {path}")

    frame = pd.read_csv(path)

    if SCORE_COLUMN not in frame.columns:
        raise KeyError(
            f"Column '{SCORE_COLUMN}' is missing from {path}. "
            f"Available columns: {list(frame.columns)}"
        )

    scores = pd.to_numeric(
        frame[SCORE_COLUMN],
        errors="raise",
    ).to_numpy(dtype=float)

    if scores.size == 0:
        raise ValueError(f"No privacy scores found in {path}")

    if not np.all(np.isfinite(scores)):
        raise ValueError(f"NaN or infinite privacy scores found in {path}")

    if np.any(scores < -1e-9) or np.any(scores > 1.0 + 1e-9):
        raise ValueError(
            f"Privacy scores in {path} must lie in [0, 1]; "
            f"observed range: [{scores.min()}, {scores.max()}]"
        )

    scores = np.clip(scores, 0.0, 1.0)
    scores[np.isclose(scores, 0.0, atol=1e-9)] = 0.0
    scores[np.isclose(scores, 1.0, atol=1e-9)] = 1.0

    if scores.size != NUM_USERS:
        warnings.warn(
            f"{path} contains {scores.size} users; "
            f"NUM_USERS is {NUM_USERS}.",
            stacklevel=2,
        )

    return scores


def print_summary(label: str, scores: np.ndarray) -> None:
    """Print the threshold statistics used in the manuscript."""
    print(f"\n{label} (n={scores.size})")

    for threshold in (1.00, 0.95, 0.90, 0.80):
        if np.isclose(threshold, 1.0):
            mask = np.isclose(scores, 1.0, atol=1e-9)
            relation = "="
        else:
            mask = scores >= threshold - 1e-12
            relation = ">="

        count = int(mask.sum())
        print(
            f"  privacy_score {relation} {threshold:.2f}: "
            f"{count}/{scores.size} ({count / scores.size:.2%})"
        )


# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------

def main() -> None:
    results = {
        label: load_scores(path)
        for label, path in FILES.items()
    }

    #for label in MULTI_LEGEND_ORDER + SINGLE_LEGEND_ORDER:
     #   print_summary(label, results[label])
    for label in LEGEND_ORDER:
        print_summary(label, results[label])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    handles_by_label: dict[str, mpl.lines.Line2D] = {}

    for label in PLOT_ORDER:
        sorted_scores = np.sort(results[label])
        user_rank = np.arange(1, sorted_scores.size + 1)
        style = STYLES[label]
        color = str(style["color"])

        (line,) = ax.plot(
            user_rank,
            sorted_scores,
            label=label,
            color=color,
            linestyle=style["linestyle"],
            linewidth=float(style["linewidth"]),
            marker=str(style["marker"]),
            markevery=style["markevery"],
            markersize=3.15,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=0.75,
            zorder=int(style["zorder"]),
        )
        handles_by_label[label] = line

    # Add explicit horizontal padding so the endpoint curve and the "512"
    # tick label remain fully inside the axes at CCS single-column width.
    # A one-unit margin is too small because tick labels are centered on
    # their tick positions and therefore extend beyond the axes boundary.
    x_padding = 18
    ax.set_xlim(1 - x_padding, NUM_USERS + x_padding)
    ax.set_ylim(-0.015, 1.015)

    ax.set_xticks([1, 128, 256, 384, 512])
    ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])

    ax.set_xlabel(
        rf"User rank (ascending {LP_SYMBOL})",
        labelpad=3,
    )
    ax.set_ylabel(
        rf"Privacy leakage ({LP_SYMBOL})",
        labelpad=2,
    )

    # Horizontal guides only; vertical grid lines make the single-column plot
    # look crowded.
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
        length=2.5,
        width=0.6,
        pad=2,
    )

    # Keep protocol combinations grouped at the bottom.
    
    legend_row_1 = fig.legend(
        [handles_by_label[label] for label in LEGEND_ROW_1],
        LEGEND_ROW_1,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.058),
        ncol=4,
        borderaxespad=0.0,
        labelspacing=0.35,
        numpoints=1,
    )

    legend_row_2 = fig.legend(
        [handles_by_label[label] for label in LEGEND_ROW_2],
        LEGEND_ROW_2,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.004),
        ncol=3,
        borderaxespad=0.0,
        labelspacing=0.35,
        numpoints=1,
    )
    
    #multi_legend = fig.legend(
     #   [handles_by_label[label] for label in MULTI_LEGEND_ORDER],
      #  MULTI_LEGEND_ORDER,
       # loc="lower center",
        #bbox_to_anchor=(0.5, 0.058),
        #ncol=4,
        #borderaxespad=0.0,
        #labelspacing=0.35,
        #numpoints=1,
    #)

    #single_legend = fig.legend(
     #   [handles_by_label[label] for label in SINGLE_LEGEND_ORDER],
      #  SINGLE_LEGEND_ORDER,
       # loc="lower center",
        #bbox_to_anchor=(0.5, 0.004),
        #ncol=3,
        #borderaxespad=0.0,
        #labelspacing=0.35,
        #numpoints=1,
    #)

    # Fixed margins keep the physical size predictable and avoid clipping.
    fig.subplots_adjust(
        left=0.185,
        right=0.975,   # extra canvas space protects the final x-tick label
        bottom=0.338,
        top=0.975,
    )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Avoid bbox_inches="tight": both legends are already inside the canvas,
    # and fixed dimensions make the paper's figures visually consistent.
    fig.savefig(OUTPUT_PDF)
    fig.savefig(OUTPUT_PNG, dpi=300)

    print(f"\nSaved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")

    # Comment this out for non-interactive batch generation.
    plt.show()


if __name__ == "__main__":
    main()
