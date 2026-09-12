from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

NUM_USERS = 512
MARKER_INTERVAL = 50
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"

OUTPUT_FILE = Path(
    f"output/images/privacy_leakage_q2_{NUM_USERS}_ccs.pdf"
)


# ============================================================
# Experimental configurations
# ============================================================

CONFIGURATIONS = [
    {
        "label": (
            "LTE RI: 7 min, BLE RI: 7–15 min\n"
            "LTE TI: 3 s, BLE TI: 5 s (baseline)"
        ),
        "short_name": "Baseline",
        "path": Path(
            f"output/data/{BASE_SCENARIO_NAME}_all1/"
            f"multi_protocol_{BASE_SCENARIO_NAME}_all1.csv"
        ),
        "color": "#000000",
        "marker": "o",
        "linestyle": "-",
    },
    {
        "label": (
            "LTE RI: 4 min, BLE RI: 3–5 min\n"
            "LTE TI: 3 s, BLE TI: 5 s"
        ),
        "short_name": "Shorter RI",
        "path": Path(
            f"output/data/{BASE_SCENARIO_NAME}_all/"
            f"multi_protocol_{BASE_SCENARIO_NAME}_all.csv"
        ),
        "color": "#e7298a",
        "marker": "^",
        "linestyle": "--",
    },
    {
        "label": (
            "LTE RI: 7 min, BLE RI: 7–15 min\n"
            "LTE TI: 10 s, BLE TI: 10 s"
        ),
        "short_name": "Longer TI",
        "path": Path(
            f"output/data/{BASE_SCENARIO_NAME}_all5/"
            f"multi_protocol_{BASE_SCENARIO_NAME}_all5.csv"
        ),
        "color": "#fdc086",
        "marker": "D",
        "linestyle": "-.",
    },
    {
        "label": (
            "LTE RI: 4 min, BLE RI: 3–5 min\n"
            "LTE TI: 10 s, BLE TI: 10 s"
        ),
        "short_name": "Shorter RI and longer TI",
        "path": Path(
            f"output/data/{BASE_SCENARIO_NAME}_all4/"
            f"multi_protocol_{BASE_SCENARIO_NAME}_all4.csv"
        ),
        "color": "#66a61e",
        "marker": "s",
        "linestyle": ":",
    },
]


# ============================================================
# Load one CSV
# ============================================================

def load_sorted_scores(csv_path: Path) -> np.ndarray:
    """
    Load and sort privacy scores.

    This function does not pad, truncate, or add users.
    """

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Input CSV does not exist:\n{csv_path}"
        )

    df = pd.read_csv(csv_path)

    if "privacy_score" not in df.columns:
        raise KeyError(
            f"{csv_path} does not contain a 'privacy_score' column.\n"
            f"Available columns: {list(df.columns)}"
        )

    scores = pd.to_numeric(
        df["privacy_score"],
        errors="raise",
    ).to_numpy(dtype=float)

    if len(scores) == 0:
        raise ValueError(
            f"{csv_path} contains no privacy scores."
        )

    if not np.all(np.isfinite(scores)):
        invalid_count = int(
            np.count_nonzero(~np.isfinite(scores))
        )

        raise ValueError(
            f"{csv_path} contains {invalid_count} invalid values."
        )

    tolerance = 1e-9

    if (
        np.any(scores < -tolerance)
        or np.any(scores > 1.0 + tolerance)
    ):
        raise ValueError(
            f"{csv_path} contains privacy scores outside [0, 1]. "
            f"Observed range: [{scores.min()}, {scores.max()}]"
        )

    if len(scores) != NUM_USERS:
        print(
            f"Note: {csv_path.name} contains {len(scores)} rows. "
            f"The curve will run from rank 1 to rank {len(scores)} "
            "without padding."
        )

    return np.sort(scores)


# ============================================================
# Print statistics
# ============================================================

def print_summary(
    configuration_name: str,
    scores: np.ndarray,
) -> None:

    count_full = int(
        np.count_nonzero(
            np.isclose(
                scores,
                1.0,
                rtol=0.0,
                atol=1e-9,
            )
        )
    )

    count_095 = int(np.count_nonzero(scores >= 0.95))
    count_090 = int(np.count_nonzero(scores >= 0.90))
    count_080 = int(np.count_nonzero(scores >= 0.80))

    print(f"\n{configuration_name}")

    print(
        f"  LP_D = 1.00: {count_full}/{NUM_USERS} "
        f"({100.0 * count_full / NUM_USERS:.2f}%)"
    )

    print(
        f"  LP_D >= 0.95: {count_095}/{NUM_USERS} "
        f"({100.0 * count_095 / NUM_USERS:.2f}%)"
    )

    print(
        f"  LP_D >= 0.90: {count_090}/{NUM_USERS} "
        f"({100.0 * count_090 / NUM_USERS:.2f}%)"
    )

    print(
        f"  LP_D >= 0.80: {count_080}/{NUM_USERS} "
        f"({100.0 * count_080 / NUM_USERS:.2f}%)"
    )


# ============================================================
# Standardized CCS style
# ============================================================

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 7,

    "axes.labelsize": 8,
    "axes.titlesize": 8,

    "xtick.labelsize": 7,
    "ytick.labelsize": 7,

    # Slightly smaller because every legend entry contains
    # two complete lines of parameter values.
    "legend.fontsize": 5.6,

    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,

    # Embed text properly in vector PDF output.
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "mathtext.fontset": "dejavusans",
})


# ============================================================
# Create the figure
# ============================================================

# Extra height provides room for the full numeric legend.
fig, ax = plt.subplots(
    figsize=(3.3, 2.35)
)


for configuration in CONFIGURATIONS:
    scores = load_sorted_scores(
        configuration["path"]
    )

    print_summary(
        configuration["short_name"],
        scores,
    )

    # Every curve begins at rank 1.
    # No zeros or additional users are inserted.
    user_rank = np.arange(
        1,
        len(scores) + 1,
    )

    ax.plot(
        user_rank,
        scores,

        label=configuration["label"],

        color=configuration["color"],
        marker=configuration["marker"],
        linestyle=configuration["linestyle"],

        markevery=MARKER_INTERVAL,
        markersize=2.8,
        markeredgewidth=0.5,

        linewidth=1.2
        if configuration["short_name"] == "Baseline"
        else 1.0,

        alpha=0.95,

        # Draw the baseline above overlapping curves.
        zorder=4
        if configuration["short_name"] == "Baseline"
        else 3,
    )


# ============================================================
# Axes: match Figure 6
# ============================================================

# Add the same visual margin around ranks 1 and 512.
# The first actual data point remains x = 1.
x_margin = 0.05 * (NUM_USERS - 1)

ax.set_xlim(
    1 - x_margin,
    NUM_USERS + x_margin,
)

ax.set_ylim(
    0.0,
    1.02,
)

ax.set_xticks([
    1,
    128,
    256,
    384,
    512,
])

ax.set_yticks([
    0.00,
    0.25,
    0.50,
    0.75,
    1.00,
])

ax.set_xlabel(
    r"User rank (ascending $LP_D$)"
)

ax.set_ylabel(
    r"Privacy leakage ($LP_D$)"
)

ax.tick_params(
    axis="both",
    which="major",
    length=2.5,
    width=0.5,
    pad=1.5,
)

ax.grid(
    True,
    which="major",
    linewidth=0.3,
    alpha=0.55,
    zorder=0,
)

for spine in ax.spines.values():
    spine.set_linewidth(0.6)


# ============================================================
# Full numeric legend below the plot
# ============================================================

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.27),

    # Two entries per row. Each entry itself has two text lines.
    ncol=2,

    frameon=False,

    handlelength=1.8,
    handletextpad=0.4,
    columnspacing=0.8,
    labelspacing=0.9,
    borderaxespad=0.0,
)


# Reserve enough space for the two-row, two-line legend.
fig.subplots_adjust(
    left=0.17,
    right=0.995,
    top=0.98,
    bottom=0.50,
)


# ============================================================
# Save
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fig.savefig(
    OUTPUT_FILE,
    format="pdf",
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.02,
)

print(
    f"\nSaved standardized figure to:\n"
    f"{OUTPUT_FILE.resolve()}"
)

plt.show()
plt.close(fig)
