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
    OUTPUT_ROOT / "privacy_leakage_countermeasure_ccs_m.pdf"
)
OUTPUT_PNG: Final[Path] = (
    OUTPUT_ROOT / "privacy_leakage_countermeasure_ccs.png"
)

LP_SYMBOL: Final[str] = r"$LP_D$"

# All paths are relative to the CrossLink project root. This replaces the
# mixture of absolute and relative paths in the original script.
SERIES: dict[str, dict[str, object]] = {
    "No sync": {
        "path": (
            DATA_ROOT
            / f"{BASE_SCENARIO_NAME}_all1"
            / f"multi_protocol_{BASE_SCENARIO_NAME}_all1.csv"
        ),
        "legend_label": "No sync (baseline)",
        "color": "#000000",
        "linestyle": "-",
        "linewidth": 1.95,
        "marker": "o",
        "markevery": (18, 105),
        "zorder": 9,
    },
    "Sync 180 s": {
        "path": (
            DATA_ROOT
            / "synchronized_high_ti"
            / "multi_protocol_synchronized_high_ti.csv"
        ),
        "legend_label": "Sync 180 s",
        "color": "#CC79A7",
        "linestyle": (0, (5.0, 1.5)),
        "linewidth": 1.35,
        "marker": "P",
        "markevery": (42, 105),
        "zorder": 6,
    },
    "Sync 300 s": {
        "path": (
            DATA_ROOT
            / "synchronized_low_ti"
            / "multi_protocol_synchronized_low_ti.csv"
        ),
        "legend_label": "Sync 300 s",
        "color": "#56B4E9",
        "linestyle": "-.",
        "linewidth": 1.35,
        "marker": "^",
        "markevery": (64, 105),
        "zorder": 6,
    },
    "Sync 600 s": {
        "path": (
            DATA_ROOT
            / "scenario_synced_randomization_512_all"
            / "multi_protocol_scenario_synced_randomization_512_all.csv"
        ),
        "legend_label": "Sync 600 s",
        "color": "#D55E00",
        "linestyle": (0, (2.6, 1.3)),
        "linewidth": 1.35,
        "marker": "D",
        "markevery": (86, 105),
        "zorder": 6,
    },
    "Perfect mixing": {
        "path": (
            DATA_ROOT
            / "scenario_proximity_512_sumo_new"
            / "multi_protocol_scenario_proximity_512_sumo_new.csv"
        ),
        "legend_label": "Perfect mixing",
        "color": "#6A3D9A",
        "linestyle": (0, (1.3, 1.4)),
        "linewidth": 1.55,
        "marker": "X",
        "markevery": (30, 105),
        "zorder": 8,
    },
    "BLE": {
        "path": (
            DATA_ROOT
            / "scenario_proximity_512_sumo_new"
            / "single_ble_scenario_proximity_512_sumo_new.csv"
        ),
        "legend_label": "BLE",
        "color": "#0072B2",
        "linestyle": (0, (5.0, 2.0)),
        "linewidth": 1.18,
        "marker": "s",
        "markevery": (10, 105),
        "zorder": 4,
    },
    "LTE": {
        "path": (
            DATA_ROOT
            / "scenario_proximity_512_sumo_new"
            / "single_lte_scenario_proximity_512_sumo_new.csv"
        ),
        "legend_label": "LTE",
        "color": "#E69F00",
        "linestyle": (0, (3.0, 1.4)),
        "linewidth": 1.18,
        "marker": "v",
        "markevery": (52, 105),
        "zorder": 4,
    },
    "WiFi": {
        "path": (
            DATA_ROOT
            / "scenario_proximity_512_sumo_new"
            / "single_wifi_scenario_proximity_512_sumo_new.csv"
        ),
        "legend_label": "WiFi",
        "color": "#009E73",
        "linestyle": ":",
        "linewidth": 1.25,
        "marker": "h",
        "markevery": (78, 105),
        "zorder": 4,
    },
}

# Draw the thinner contextual curves first. Draw the baseline and perfect-mixing
# curves last so they remain visible where curves overlap.
PLOT_ORDER: Final[list[str]] = [
    "WiFi",
    "LTE",
    "BLE",
    "Sync 600 s",
    "Sync 300 s",
    "Sync 180 s",
    "Perfect mixing",
    "No sync",
]

# Desired visible order:
# Row 1: No sync, Sync 180 s, Sync 300 s
# Row 2: Sync 600 s, Perfect mixing
#
# Matplotlib fills multi-column legends column-wise, so the internal order
# below is chosen to produce the desired row-wise appearance with ncol=3.
COUNTERMEASURE_LEGEND_ORDER: Final[list[str]] = [
    "No sync",          # Column 1, row 1
    "Sync 180 s",       # Column 1, row 2

    "Sync 600 s",       # Column 2, row 1
    "Perfect mixing",   # Column 2, row 2

    "Sync 300 s",       # Column 3, row 1
]

SINGLE_PROTOCOL_LEGEND_ORDER: Final[list[str]] = ["BLE", "LTE", "WiFi"]


# -----------------------------------------------------------------------------
# Camera-ready style: same visual system as standardized Figure 6
# -----------------------------------------------------------------------------

# Generated directly at the final CCS single-column width. The extra height
# reserves space for the three compact legend rows below the x-axis.
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
        "legend.fontsize": 5.9,
        "axes.linewidth": 0.65,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.solid_capstyle": "round",
        "lines.dash_capstyle": "round",
        "legend.frameon": False,
        "legend.handlelength": 2.1,
        "legend.handletextpad": 0.40,
        "legend.columnspacing": 0.72,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


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
        label: load_scores(Path(spec["path"]))
        for label, spec in SERIES.items()
    }

    summary_order = [
        "No sync",
        "Sync 180 s",
        "Sync 300 s",
        "Sync 600 s",
        "Perfect mixing",
        "BLE",
        "LTE",
        "WiFi",
    ]
    for label in summary_order:
        print_summary(str(SERIES[label]["legend_label"]), results[label])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    handles_by_label: dict[str, mpl.lines.Line2D] = {}

    for label in PLOT_ORDER:
        sorted_scores = np.sort(results[label])
        user_rank = np.arange(1, sorted_scores.size + 1)
        style = SERIES[label]
        color = str(style["color"])

        (line,) = ax.plot(
            user_rank,
            sorted_scores,
            label=str(style["legend_label"]),
            color=color,
            linestyle=style["linestyle"],
            linewidth=float(style["linewidth"]),
            marker=str(style["marker"]),
            markevery=style["markevery"],
            markersize=3.05,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=0.72,
            zorder=int(style["zorder"]),
        )
        handles_by_label[label] = line

    # Match Figure 6 and protect the endpoint and the "512" tick from clipping.
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

    # Same restrained grid and open frame used in Figure 6.
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

    # Countermeasure legend: two rows. The internal handle order is selected
    # to display the labels in the logical order documented above.
    countermeasure_legend = fig.legend(
        [handles_by_label[label] for label in COUNTERMEASURE_LEGEND_ORDER],
        [
            str(SERIES[label]["legend_label"])
            for label in COUNTERMEASURE_LEGEND_ORDER
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.058),
        ncol=3,
        borderaxespad=0.0,
        labelspacing=0.42,
        numpoints=1,
    )

    # Single-protocol baselines: one separate row.
    single_protocol_legend = fig.legend(
        [
            handles_by_label[label]
            for label in SINGLE_PROTOCOL_LEGEND_ORDER
        ],
        [
            str(SERIES[label]["legend_label"])
            for label in SINGLE_PROTOCOL_LEGEND_ORDER
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.006),
        ncol=3,
        borderaxespad=0.0,
        labelspacing=0.35,
        numpoints=1,
    )

    # Fixed margins keep the plot physically consistent with Figure 6 and
    # reserve enough space for the legends without clipping the axis labels.
    fig.subplots_adjust(
        left=0.185,
        right=0.975,
        bottom=0.355,
        top=0.975,
    )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Do not use bbox_inches="tight": both legends are inside the fixed canvas,
    # and fixed dimensions keep font scaling consistent across the paper.
    fig.savefig(OUTPUT_PDF)
    fig.savefig(OUTPUT_PNG, dpi=300)

    print(f"\nSaved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")

    # Comment this out when generating all figures in batch mode.
    plt.show()


if __name__ == "__main__":
    main()
