from __future__ import annotations

from pathlib import Path
from typing import Final
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

NUM_TARGETS: Final[int] = 113
TOTAL_DURATION_SEC: Final[int] = 7200
SECONDS_PER_MINUTE: Final[int] = 60
MAX_DURATION_MIN: Final[float] = (
    TOTAL_DURATION_SEC / SECONDS_PER_MINUTE
)

DATA_ROOT: Final[Path] = Path("output/data")
OUTPUT_ROOT: Final[Path] = Path("output/images")
SCORE_COLUMN: Final[str] = "privacy_score"

OUTPUT_PDF: Final[Path] = (
    OUTPUT_ROOT / "privacy_leakage_duration_sf_m.pdf"
)
OUTPUT_PNG: Final[Path] = (
    OUTPUT_ROOT / "privacy_leakage_duration_sf.png"
)

FILES: dict[str, Path] = {
    "PATCH": DATA_ROOT / "matched_user_ids_patch.csv",
    "MOB": DATA_ROOT / "matched_user_ids_mob.csv",
    "RAND": DATA_ROOT / "matched_user_ids_rand.csv",
    "Full coverage": DATA_ROOT / "matched_user_ids_baseline.csv",
}


# -----------------------------------------------------------------------------
# Camera-ready style: same hierarchy as standardized Figure 6
# -----------------------------------------------------------------------------

# Generate directly at the final CCS single-column width.
# The height reserves room for the two-row bottom legend.
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
        "legend.columnspacing": 1.05,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

# Keep this deployment-color mapping identical in the other deployment plots.
STYLES: dict[str, dict[str, object]] = {
    "Full coverage": {
        "color": "#000000",
        "linestyle": "-",
        "linewidth": 1.95,
        "marker": "o",
        "marker_offset": 0,
        "zorder": 7,
    },
    "PATCH": {
        "color": "#0072B2",
        "linestyle": (0, (5.0, 1.7)),
        "linewidth": 1.35,
        "marker": "s",
        "marker_offset": 1,
        "zorder": 5,
    },
    "MOB": {
        "color": "#009E73",
        "linestyle": "-.",
        "linewidth": 1.35,
        "marker": "^",
        "marker_offset": 2,
        "zorder": 5,
    },
    "RAND": {
        "color": "#E69F00",
        "linestyle": (0, (2.5, 1.3)),
        "linewidth": 1.35,
        "marker": "D",
        "marker_offset": 3,
        "zorder": 5,
    },
}

# Draw the baseline last so it remains visible where curves overlap.
PLOT_ORDER: Final[list[str]] = [
    "RAND",
    "MOB",
    "PATCH",
    "Full coverage",
]

# Desired visible legend:
# Row 1: Full coverage, PATCH
# Row 2: MOB, RAND
#
# Matplotlib fills multi-column legends column-wise, so this internal order
# produces the desired row-wise appearance with ncol=2.
LEGEND_ORDER: Final[list[str]] = [
    "Full coverage",
    "MOB",
    "PATCH",
    "RAND",
]


# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------

def load_and_convert(path: Path) -> np.ndarray:
    """Load privacy leakage and convert it to tracking duration in minutes."""
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

    if scores.size != NUM_TARGETS:
        warnings.warn(
            f"{path} contains {scores.size} targets; "
            f"NUM_TARGETS is {NUM_TARGETS}.",
            stacklevel=2,
        )

    return scores * MAX_DURATION_MIN


def survival_curve(durations: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Return the empirical survival function S(t) = P(T >= t).

    The returned values are intended for a steps-pre plot. This preserves the
    inclusive interpretation "trackable for at least t minutes."
    """
    unique_durations = np.unique(np.sort(durations))

    thresholds = np.concatenate(([0.0], unique_durations))
    survival = np.array(
        [(durations >= threshold).mean() for threshold in thresholds],
        dtype=float,
    )

    # If no target reaches the full two-hour limit, extend the curve to the
    # right boundary at zero.
    if thresholds[-1] < MAX_DURATION_MIN:
        thresholds = np.append(thresholds, MAX_DURATION_MIN)
        survival = np.append(survival, 0.0)

    return thresholds, survival


def marker_schedule(
    number_of_points: int,
    offset_index: int,
) -> tuple[int, int]:
    """Place about five markers per curve and stagger overlapping curves."""
    step = max(1, number_of_points // 5)
    start = min(number_of_points - 1, offset_index * max(1, step // 4))
    return start, step


def print_summary(label: str, durations: np.ndarray) -> None:
    """Print descriptive and threshold statistics."""
    print(
        f"{label:<14} "
        f"mean={durations.mean():6.2f} min | "
        f"median={np.median(durations):6.2f} min | "
        f"min={durations.min():6.2f} | "
        f"max={durations.max():6.2f}"
    )

    for threshold in (30.0, 60.0, 90.0, 120.0):
        count = int(np.count_nonzero(durations >= threshold - 1e-9))
        print(
            f"  >= {threshold:>5.0f} min: "
            f"{count:>3}/{durations.size} "
            f"({count / durations.size:6.2%})"
        )


# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------

def main() -> None:
    durations_by_strategy = {
        label: load_and_convert(path)
        for label, path in FILES.items()
    }

    for label in ["PATCH", "MOB", "RAND", "Full coverage"]:
        print_summary(label, durations_by_strategy[label])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    handles_by_label: dict[str, mpl.lines.Line2D] = {}

    for label in PLOT_ORDER:
        x_values, y_values = survival_curve(
            durations_by_strategy[label]
        )
        style = STYLES[label]
        color = str(style["color"])

        (line,) = ax.plot(
            x_values,
            y_values,
            drawstyle="steps-pre",
            label=label,
            color=color,
            linestyle=style["linestyle"],
            linewidth=float(style["linewidth"]),
            marker=str(style["marker"]),
            markevery=marker_schedule(
                len(x_values),
                int(style["marker_offset"]),
            ),
            markersize=3.15,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=0.75,
            zorder=int(style["zorder"]),
        )
        handles_by_label[label] = line

    # Endpoint padding prevents the 0 and 120 tick labels from being clipped.
    ax.set_xlim(-3.0, MAX_DURATION_MIN + 3.0)
    ax.set_ylim(-0.015, 1.015)

    ax.set_xticks([0, 30, 60, 90, 120])
    ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])
    ax.yaxis.set_major_formatter(
        PercentFormatter(xmax=1.0, decimals=0)
    )

    ax.set_xlabel(
        "Post-event tracking duration (min)",
        labelpad=3,
    )
    ax.set_ylabel(
        "Trackable targets",
        labelpad=2,
    )

    # Same restrained grid and open frame used in Figure 6.
    ax.set_axisbelow(True)
    ax.grid(
        axis="y",
        color="0.87",
        linewidth=0.45,
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

    # Two-row bottom legend.
    fig.legend(
        [handles_by_label[label] for label in LEGEND_ORDER],
        LEGEND_ORDER,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.012),
        ncol=2,
        borderaxespad=0.0,
        labelspacing=0.42,
        numpoints=1,
    )

    # Fixed margins keep the physical output consistent with Figure 6.
    fig.subplots_adjust(
        left=0.195,
        right=0.975,
        bottom=0.285,
        top=0.975,
    )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Do not use bbox_inches="tight"; the legend is inside the fixed canvas.
    fig.savefig(OUTPUT_PDF)
    fig.savefig(OUTPUT_PNG, dpi=300)

    print(f"\nSaved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")

    # Comment this out when generating all figures in batch mode.
    plt.show()


if __name__ == "__main__":
    main()
