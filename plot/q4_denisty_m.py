from __future__ import annotations

from pathlib import Path
from typing import Final
import warnings

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

from figure11_style import (
    LP_SYMBOL,
    PANEL_SIZE,
    POPULATION_STYLE,
    SOURCE_STYLE,
    apply_ccs_style,
    save_panel,
    set_panel_margins,
    style_axis,
)


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DATA_ROOT: Final[Path] = Path("output/data")
OUTPUT_ROOT: Final[Path] = Path("output/images")
SCORE_COLUMN: Final[str] = "privacy_score"

OUTPUT_PDF: Final[Path] = OUTPUT_ROOT / "privacy_leakage_q4_density_m.pdf"
OUTPUT_PNG: Final[Path] = OUTPUT_ROOT / "privacy_leakage_q4_density.png"

SCENARIOS: Final[dict[tuple[int, str], Path]] = {
    (512, "SUMO"): (
        DATA_ROOT
        / "scenario_exponential_512_sumo_LB"
        / "multi_protocol_scenario_exponential_512_sumo_LB.csv"
    ),
    (1024, "SUMO"): (
        DATA_ROOT
        / "scenario_exponential_1024_sumo_LB"
        / "multi_protocol_scenario_exponential_1024_sumo_LB.csv"
    ),
    (1536, "SUMO"): (
        DATA_ROOT
        / "scenario_exponential_1536_sumo_LB"
        / "multi_protocol_scenario_exponential_1536_sumo_LB.csv"
    ),
    (512, "Synthetic"): (
        DATA_ROOT
        / "scenario_exponential_512_graph_LB"
        / "multi_protocol_scenario_exponential_512_graph_LB.csv"
    ),
    (1024, "Synthetic"): (
        DATA_ROOT
        / "scenario_exponential_1024_graph_LB"
        / "multi_protocol_scenario_exponential_1024_graph_LB.csv"
    ),
    (1536, "Synthetic"): (
        DATA_ROOT
        / "scenario_exponential_1536_graph_LB"
        / "multi_protocol_scenario_exponential_1536_graph_LB.csv"
    ),
}

PLOT_ORDER: Final[list[tuple[int, str]]] = [
    (512, "Synthetic"),
    (1024, "Synthetic"),
    (1536, "Synthetic"),
    (1536, "SUMO"),
    (1024, "SUMO"),
    (512, "SUMO"),
]


def load_scores(path: Path, expected_users: int) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input file: {path}")

    frame = pd.read_csv(path)
    if SCORE_COLUMN not in frame.columns:
        raise KeyError(
            f"Column '{SCORE_COLUMN}' is missing from {path}; "
            f"available columns: {list(frame.columns)}"
        )

    values = pd.to_numeric(
        frame[SCORE_COLUMN], errors="raise"
    ).to_numpy(dtype=float)

    if not np.all(np.isfinite(values)):
        raise ValueError(f"Non-finite scores found in {path}")
    if np.any(values < -1e-9) or np.any(values > 1.0 + 1e-9):
        raise ValueError(f"Scores in {path} must lie in [0, 1]")

    values = np.clip(values, 0.0, 1.0)

    if values.size != expected_users:
        warnings.warn(
            f"{path} contains {values.size} users; "
            f"scenario indicates {expected_users}.",
            stacklevel=2,
        )

    return values


def marker_schedule(size: int, source: str) -> tuple[int, int]:
    step = max(1, size // 5)
    start = int(step * (0.15 if source == "SUMO" else 0.58))
    return min(start, size - 1), step


def main() -> None:
    apply_ccs_style()

    results = {
        key: load_scores(path, expected_users=key[0])
        for key, path in SCENARIOS.items()
    }

    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    for users, source in PLOT_ORDER:
        scores = np.sort(results[(users, source)])
        percentile = np.linspace(0.0, 100.0, scores.size)

        pop = POPULATION_STYLE[users]
        src = SOURCE_STYLE[source]
        color = str(pop["color"])
        filled = bool(src["filled"])

        ax.plot(
            percentile,
            scores,
            color=color,
            linestyle=src["linestyle"],
            linewidth=float(src["linewidth"]),
            marker=str(pop["marker"]),
            markevery=marker_schedule(scores.size, source),
            markersize=2.8,
            markerfacecolor=color if filled else "white",
            markeredgecolor="white" if filled else color,
            markeredgewidth=0.68 if filled else 0.78,
            zorder=int(src["zorder"]),
        )

    ax.set_xlim(-3, 103)
    ax.set_ylim(-0.015, 1.015)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.set_major_formatter(
        PercentFormatter(xmax=100, decimals=0)
    )
    ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])

    ax.set_xlabel("User percentile", labelpad=2)
    # The left panel already defines the shared privacy-leakage label.
    ax.set_ylabel("")

    style_axis(ax)

    population_handles = [
        Line2D(
            [0], [0],
            color=str(POPULATION_STYLE[n]["color"]),
            marker=str(POPULATION_STYLE[n]["marker"]),
            linestyle="none",
            markerfacecolor=str(POPULATION_STYLE[n]["color"]),
            markeredgecolor="white",
            markeredgewidth=0.6,
            markersize=3.0,
            label=f"N={n}",
        )
        for n in (512, 1024, 1536)
    ]
    source_handles = [
        Line2D(
            [0], [0],
            color="0.15",
            linestyle=SOURCE_STYLE["SUMO"]["linestyle"],
            linewidth=1.35,
            marker="o",
            markerfacecolor="0.15",
            markeredgecolor="white",
            markeredgewidth=0.55,
            markersize=3.0,
            label="SUMO",
        ),
        Line2D(
            [0], [0],
            color="0.15",
            linestyle=SOURCE_STYLE["Synthetic"]["linestyle"],
            linewidth=1.15,
            marker="o",
            markerfacecolor="white",
            markeredgecolor="0.15",
            markeredgewidth=0.75,
            markersize=3.0,
            label="Synthetic",
        ),
    ]

    # This legend applies to both panels (b) and (c).
    fig.legend(
        handles=population_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.055),
        ncol=3,
        borderaxespad=0.0,
        numpoints=1,
    )
    fig.legend(
        handles=source_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.008),
        ncol=2,
        borderaxespad=0.0,
        numpoints=1,
    )

    set_panel_margins(fig)
    save_panel(fig, OUTPUT_PDF, OUTPUT_PNG)

    print(f"Saved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")
    plt.show()


if __name__ == "__main__":
    main()
