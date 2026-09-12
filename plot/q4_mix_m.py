from __future__ import annotations

from pathlib import Path
from typing import Final
import re
import warnings

import matplotlib.pyplot as plt
from matplotlib.ticker import (
    FixedLocator,
    LogFormatterMathtext,
    NullFormatter,
    PercentFormatter,
)
import numpy as np
import pandas as pd

from figure11_style import (
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

# Directory used by the original q4_mix.py script.
MIXZONE_CSV_DIR: Final[Path] = Path(
    "/home/aneet_wisec/usenix_2025/path-leakage/plot/q4_mix1"
)

OUTPUT_ROOT: Final[Path] = Path("output/images")
OUTPUT_PDF: Final[Path] = OUTPUT_ROOT / "privacy_leakage_q4_mix_m.pdf"
OUTPUT_PNG: Final[Path] = OUTPUT_ROOT / "privacy_leakage_q4_mix.png"

# The supplied CSVs use this column.
DURATION_COLUMN: Final[str] = "duration_seconds"

POPULATIONS: Final[tuple[int, ...]] = (512, 1024, 1536)
SOURCES: Final[tuple[str, ...]] = ("SUMO", "Synthetic")

# Show the two compact legend rows below panel (c):
#   row 1: population sizes in ascending order;
#   row 2: SUMO versus Synthetic encoding.
SHOW_LEGEND: Final[bool] = True

# Draw dashed synthetic curves first, then solid SUMO curves.
PLOT_ORDER: Final[list[tuple[int, str]]] = [
    (512, "Synthetic"),
    (1024, "Synthetic"),
    (1536, "Synthetic"),
    (1536, "SUMO"),
    (1024, "SUMO"),
    (512, "SUMO"),
]


# -----------------------------------------------------------------------------
# File discovery and data loading
# -----------------------------------------------------------------------------

def parse_csv_identity(path: Path) -> tuple[int, str]:
    """
    Infer population and mobility source from a filename.

    Accepted source tokens:
      - "sumo" -> SUMO
      - "graph" or "synthetic" -> Synthetic

    The filename must also contain exactly one of 512, 1024, or 1536.
    """
    stem = path.stem.lower()

    if "sumo" in stem:
        source = "SUMO"
    elif "graph" in stem or "synthetic" in stem:
        source = "Synthetic"
    else:
        raise ValueError(
            f"Cannot infer SUMO/Synthetic source from filename: {path.name}"
        )

    matches = [
        population
        for population in POPULATIONS
        if re.search(rf"(?<!\d){population}(?!\d)", stem)
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Cannot infer a unique population from filename: {path.name}"
        )

    return matches[0], source


def discover_csv_files() -> dict[tuple[int, str], Path]:
    """Discover the six q4 mix-zone CSV files."""
    if not MIXZONE_CSV_DIR.is_dir():
        raise FileNotFoundError(
            f"Mix-zone CSV directory does not exist: {MIXZONE_CSV_DIR}"
        )

    mapping: dict[tuple[int, str], Path] = {}

    for path in sorted(MIXZONE_CSV_DIR.glob("*.csv")):
        try:
            key = parse_csv_identity(path)
        except ValueError as exc:
            warnings.warn(str(exc), stacklevel=2)
            continue

        if key in mapping:
            raise RuntimeError(
                f"Multiple CSV files map to {key}:\n"
                f"  {mapping[key]}\n"
                f"  {path}"
            )

        mapping[key] = path

    expected = {
        (population, source)
        for population in POPULATIONS
        for source in SOURCES
    }
    missing = sorted(expected - set(mapping))

    if missing:
        formatted = "\n  ".join(
            f"{population}, {source}" for population, source in missing
        )
        raise FileNotFoundError(
            "Could not find all six mix-zone files. Missing:\n  "
            f"{formatted}\n"
            f"Discovered files: {[path.name for path in mapping.values()]}"
        )

    return mapping


def load_durations(path: Path) -> np.ndarray:
    """Load, validate, and prepare mix-zone durations for a log-scale plot."""
    frame = pd.read_csv(path)

    if DURATION_COLUMN not in frame.columns:
        raise KeyError(
            f"Column '{DURATION_COLUMN}' is missing from {path}. "
            f"Available columns: {list(frame.columns)}"
        )

    values = pd.to_numeric(
        frame[DURATION_COLUMN],
        errors="coerce",
    ).to_numpy(dtype=float)

    values = values[np.isfinite(values)]

    if values.size == 0:
        raise ValueError(f"No valid duration values found in {path}")

    if np.any(values < 0):
        raise ValueError(f"Negative mix-zone duration found in {path}")

    # A logarithmic axis cannot display zero. Preserve zero-duration samples at
    # the bottom by replacing them with half the smallest positive duration.
    positive = values[values > 0]

    if positive.size == 0:
        raise ValueError(f"All duration values are zero in {path}")

    if np.any(values == 0):
        floor = max(float(positive.min()) / 2.0, 1e-3)
        warnings.warn(
            f"Replacing zero durations in {path.name} with {floor:g} s "
            "for logarithmic plotting.",
            stacklevel=2,
        )
        values = np.where(values == 0, floor, values)

    return values


def percentile_axis(size: int) -> np.ndarray:
    """
    Return the empirical percentile rank used by the original plot.

    This is 100 times the ECDF value: 1/n, 2/n, ..., 1.
    """
    return 100.0 * np.arange(1, size + 1, dtype=float) / size


def marker_schedule(size: int, source: str) -> tuple[int, int]:
    """Use approximately five sparse markers and stagger the two sources."""
    step = max(1, size // 5)
    start_fraction = 0.15 if source == "SUMO" else 0.58
    start = min(size - 1, int(step * start_fraction))
    return start, step


def configure_log_ticks(ax: plt.Axes, all_values: np.ndarray) -> None:
    """Use at most a few readable decade ticks on the narrow CCS panel."""
    min_value = float(np.min(all_values))
    max_value = float(np.max(all_values))

    min_exp = int(np.floor(np.log10(min_value)))
    max_exp = int(np.ceil(np.log10(max_value)))

    if min_exp == max_exp:
        max_exp += 1

    ax.set_ylim(10.0 ** min_exp, 10.0 ** max_exp)

    # Even powers give compact labels such as 10^0, 10^2, and 10^4.
    exponents = [
        exponent
        for exponent in range(min_exp, max_exp + 1)
        if exponent % 2 == 0
    ]

    if not exponents:
        exponents = [min_exp, max_exp]
    else:
        # Keep the number of labels small in a 2.16-inch-wide panel.
        while len(exponents) > 4:
            exponents = exponents[::2]

    major_ticks = [10.0 ** exponent for exponent in exponents]
    ax.yaxis.set_major_locator(FixedLocator(major_ticks))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10.0))
    ax.yaxis.set_minor_formatter(NullFormatter())


# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------

def main() -> None:
    apply_ccs_style()

    csv_files = discover_csv_files()
    durations = {
        key: load_durations(path)
        for key, path in csv_files.items()
    }

    for key in sorted(durations, key=lambda item: (item[1], item[0])):
        values = durations[key]
        print(
            f"{key}: {csv_files[key].name}, "
            f"n={values.size}, "
            f"median={np.median(values):.2f} s"
        )

    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    for population, source in PLOT_ORDER:
        values = np.sort(durations[(population, source)])
        percentile = percentile_axis(values.size)

        population_style = POPULATION_STYLE[population]
        source_style = SOURCE_STYLE[source]

        color = str(population_style["color"])
        marker = str(population_style["marker"])
        filled = bool(source_style["filled"])

        ax.plot(
            percentile,
            values,
            color=color,
            linestyle=source_style["linestyle"],
            linewidth=float(source_style["linewidth"]),
            marker=marker,
            markevery=marker_schedule(values.size, source),
            markersize=2.8,
            markerfacecolor=color if filled else "white",
            markeredgecolor="white" if filled else color,
            markeredgewidth=0.68 if filled else 0.80,
            zorder=int(source_style["zorder"]),
        )

    ax.set_yscale("log")

    # Small endpoint padding prevents the 0% and 100% labels from being cut.
    ax.set_xlim(-3.0, 103.0)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.set_major_formatter(
        PercentFormatter(xmax=100, decimals=0)
    )

    configure_log_ticks(
        ax,
        np.concatenate(list(durations.values())),
    )

    ax.set_xlabel("User percentile", labelpad=2)
    ax.set_ylabel("Mix-zone duration (s)", labelpad=1.5)

    style_axis(ax)

    # Two compact semantic legends:
    #   - population size is encoded by color and marker shape;
    #   - mobility source is encoded by line style and marker fill.
    if SHOW_LEGEND:
        from matplotlib.lines import Line2D

        population_handles = [
            Line2D(
                [0],
                [0],
                color=str(POPULATION_STYLE[n]["color"]),
                marker=str(POPULATION_STYLE[n]["marker"]),
                linestyle="none",
                markerfacecolor=str(POPULATION_STYLE[n]["color"]),
                markeredgecolor="white",
                markeredgewidth=0.6,
                markersize=3.0,
                label=f"N={n}",
            )
            for n in POPULATIONS
        ]

        source_handles = [
            Line2D(
                [0],
                [0],
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
                [0],
                [0],
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

    # Identical canvas and margins to the mobility and density panels.
    set_panel_margins(fig)
    save_panel(fig, OUTPUT_PDF, OUTPUT_PNG)

    print(f"Saved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")

    plt.show()


if __name__ == "__main__":
    main()
