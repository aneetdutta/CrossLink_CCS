from __future__ import annotations

from pathlib import Path
from typing import Final
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figure11_style import (
    LP_SYMBOL,
    PANEL_SIZE,
    apply_ccs_style,
    save_panel,
    set_panel_margins,
    style_axis,
)


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

NUM_USERS: Final[int] = 512
BASE_SCENARIO: Final[str] = f"scenario_result_{NUM_USERS}_sumo"

DATA_ROOT: Final[Path] = Path("output/data")
OUTPUT_ROOT: Final[Path] = Path("output/images")
SCORE_COLUMN: Final[str] = "privacy_score"

OUTPUT_PDF: Final[Path] = (
    OUTPUT_ROOT / "privacy_leakage_q4_mobility_ccs_m.pdf"
)
OUTPUT_PNG: Final[Path] = (
    OUTPUT_ROOT / "privacy_leakage_q4_mobility_ccs_m.png"
)

SERIES: Final[dict[float, dict[str, object]]] = {
    1.6: {
        "path": (
            DATA_ROOT
            / f"{BASE_SCENARIO}_all1"
            / f"multi_protocol_{BASE_SCENARIO}_all1.csv"
        ),
        "color": "#000000",
        "linestyle": "-",
        "linewidth": 1.75,
        "marker": "o",
        "markevery": (16, 112),
        "zorder": 7,
    },
    3.0: {
        "path": (
            DATA_ROOT
            / f"{BASE_SCENARIO}_moving3"
            / f"multi_protocol_{BASE_SCENARIO}_moving3.csv"
        ),
        "color": "#0072B2",
        "linestyle": (0, (5.0, 2.0)),
        "linewidth": 1.18,
        "marker": "s",
        "markevery": (40, 112),
        "zorder": 5,
    },
    5.0: {
        "path": (
            DATA_ROOT
            / f"{BASE_SCENARIO}_moving5"
            / f"multi_protocol_{BASE_SCENARIO}_moving5.csv"
        ),
        "color": "#CC79A7",
        "linestyle": "-.",
        "linewidth": 1.18,
        "marker": "^",
        "markevery": (66, 112),
        "zorder": 5,
    },
    10.0: {
        "path": (
            DATA_ROOT
            / f"{BASE_SCENARIO}_moving10"
            / f"multi_protocol_{BASE_SCENARIO}_moving10.csv"
        ),
        "color": "#E69F00",
        "linestyle": (0, (2.4, 1.35)),
        "linewidth": 1.18,
        "marker": "D",
        "markevery": (90, 112),
        "zorder": 5,
    },
}

PLOT_ORDER: Final[list[float]] = [10.0, 5.0, 3.0, 1.6]
LEGEND_ORDER: Final[list[float]] = [1.6, 3.0, 5.0, 10.0]


def load_scores(path: Path) -> np.ndarray:
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

    if values.size != NUM_USERS:
        warnings.warn(
            f"{path} contains {values.size} users; expected {NUM_USERS}.",
            stacklevel=2,
        )

    return values


def main() -> None:
    apply_ccs_style()

    results = {
        speed: load_scores(Path(spec["path"]))
        for speed, spec in SERIES.items()
    }

    fig, ax = plt.subplots(figsize=PANEL_SIZE)
    handles = {}

    for speed in PLOT_ORDER:
        scores = np.sort(results[speed])
        ranks = np.arange(1, scores.size + 1)
        spec = SERIES[speed]
        color = str(spec["color"])

        (line,) = ax.plot(
            ranks,
            scores,
            color=color,
            linestyle=spec["linestyle"],
            linewidth=float(spec["linewidth"]),
            marker=str(spec["marker"]),
            markevery=spec["markevery"],
            markersize=2.75,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=0.68,
            zorder=int(spec["zorder"]),
        )
        handles[speed] = line

    # Endpoint padding prevents 1 and 512 from being clipped.
    ax.set_xlim(-17, 530)
    ax.set_ylim(-0.015, 1.015)
    ax.set_xticks([1, 128, 256, 384, 512])
    ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])

    # Keep panel-axis labels short; the main caption explains the sorting.
    ax.set_xlabel("User rank", labelpad=2)
    ax.set_ylabel(rf"Privacy leakage ({LP_SYMBOL})", labelpad=1.5)

    style_axis(ax)

    fig.legend(
        [handles[s] for s in LEGEND_ORDER],
        ["1.6", "3", "5", "10"],
        title=r"$V_{\max}$ (m/s)",
        title_fontsize=5.6,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.020),
        ncol=4,
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
