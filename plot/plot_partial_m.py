from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

NUM_USERS = 512
MARKER_INTERVAL = 50

OUTPUT_FILE = Path(
    f"output/images/privacy_leakage_q3_{NUM_USERS}_partial_ccs.pdf"
)


# ============================================================
# Input CSV files
# ============================================================

# Panel (a): memoryless LTE identifier rotation
MEMORYLESS_FILES = {
    "PATCH": Path(
        "output/data/scenario_result_512_sumo_partial/"
        "multi_protocol_scenario_result_512_sumo_partial.csv"
    ),
    "MOB": Path(
        "output/data/scenario_partial_512_sumo_user1/"
        "multi_protocol_scenario_partial_512_sumo_user1.csv"
    ),
    "RAND": Path(
        "output/data/scenario_partial_512_sumo_timestrategic/"
        "multi_protocol_scenario_partial_512_sumo_timestrategic.csv"
    ),
    "FULL": Path(
        "output/data/scenario_result_512_sumo_all1/"
        "multi_protocol_scenario_result_512_sumo_all1.csv"
    ),
}


# Panel (b): handover-driven LTE identifier rotation
HANDOVER_FILES = {
    "PATCH": Path(
        "output/data/scenario_sumo_512_sumo_hopatch/"
        "multi_protocol_scenario_sumo_512_sumo_hopatch.csv"
    ),
    "MOB": Path(
        "output/data/scenario_sumo_512_sumo_homob/"
        "multi_protocol_scenario_sumo_512_sumo_homob.csv"
    ),
    "SPOT": Path(
        "output/data/scenario_partial_512_sumo_hostrategic/"
        "multi_protocol_scenario_partial_512_sumo_hostrategic.csv"
    ),
    "RAND": Path(
        "output/data/scenario_sumo_512_sumo_horand/"
        "multi_protocol_scenario_sumo_512_sumo_horand.csv"
    ),
    "FULL": Path(
        "output/data/scenario_sumo_512_sumo_hoall/"
        "multi_protocol_scenario_sumo_512_sumo_hoall.csv"
    ),
}


# ============================================================
# Curve styles
# ============================================================

SERIES_STYLE = {
    "PATCH": {
        "label": r"$\mathit{PATCH}$",
        "color": "#8da0cb",
        "marker": "s",
        "linestyle": "-",
    },
    "MOB": {
        "label": r"$\mathit{MOB}$",
        "color": "#fdc086",
        "marker": "v",
        "linestyle": "--",
    },
    "SPOT": {
        "label": r"$\mathit{SPOT}$",
        "color": "#d62728",
        "marker": "P",
        "linestyle": "-.",
    },
    "RAND": {
        "label": r"$\mathit{RAND}$",
        "color": "#9467bd",
        "marker": "*",
        "linestyle": ":",
    },
    "FULL": {
        "label": "Full Coverage (Baseline)",
        "color": "#000000",
        "marker": "o",
        "linestyle": "-",
    },
}

LEGEND_ORDER = [
    "FULL",
    "PATCH",
    "MOB",
    "SPOT",
    "RAND",
    
]


# ============================================================
# Load one result file
# ============================================================

def load_sorted_scores(csv_path: Path) -> np.ndarray:
   

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"CSV file does not exist:\n{csv_path}"
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

    # Correct only insignificant floating-point deviations.
    scores = np.clip(scores, 0.0, 1.0)

   

    return np.sort(scores)





# ============================================================
# Plot one panel
# ============================================================

def plot_panel(
    ax,
    panel_files,
    panel_title,
    panel_name,
):
    handles = {}

    # Draw full coverage last so the black baseline remains visible.
    plotting_order = [
        deployment
        for deployment in LEGEND_ORDER
        if deployment in panel_files and deployment != "FULL"
    ]

    if "FULL" in panel_files:
        plotting_order.append("FULL")

    for deployment in plotting_order:
        scores = load_sorted_scores(
            panel_files[deployment]
        )

      
        user_rank = np.arange(
            1,
            len(scores) + 1,
        )

        style = SERIES_STYLE[deployment]

        line, = ax.plot(
            user_rank,
            scores,
            label=style["label"],
            color=style["color"],
            linestyle=style["linestyle"],
            marker=style["marker"],
            markevery=MARKER_INTERVAL,
            linewidth=1.2 if deployment == "FULL" else 1.0,
            markersize=2.5,
            markeredgewidth=0.45,
            alpha=0.95,
            zorder=4 if deployment == "FULL" else 3,
        )

        handles[deployment] = line

        ax.set_title(
        panel_title,
        fontsize=7,
        pad=3,
    )

  
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

    ax.tick_params(
        axis="both",
        which="major",
        labelsize=6,
        length=2.2,
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

    return handles


# ============================================================
# Standardized CCS plot settings
# ============================================================

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,

    # Embed text cleanly in the vector PDF.
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "mathtext.fontset": "dejavusans",
})


# ============================================================
# Create both panels in one CCS column
# ============================================================

FIGURE_WIDTH_INCHES = 3.35
FIGURE_HEIGHT_INCHES = 2.1

fig, axes = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(
        FIGURE_WIDTH_INCHES,
        FIGURE_HEIGHT_INCHES,
    ),
    sharex=True,
    sharey=True,
)


memoryless_handles = plot_panel(
    ax=axes[0],
    panel_files=MEMORYLESS_FILES,
    panel_title="(a) Memoryless",
    panel_name="Memoryless",
)


handover_handles = plot_panel(
    ax=axes[1],
    panel_files=HANDOVER_FILES,
    panel_title="(b) Handover-driven",
    panel_name="Handover-driven",
)



axes[1].tick_params(
    axis="y",
    labelleft=False,
)


# ============================================================
# Shared legend
# ============================================================

# ============================================================
# Shared legend
# ============================================================

all_handles = {
    **memoryless_handles,
    **handover_handles,
}

LEGEND_ORDER = [
    "FULL",
    "PATCH",
    "MOB",
    "SPOT",
    "RAND",
]

legend_entries = [
    deployment
    for deployment in LEGEND_ORDER
    if deployment in all_handles
]

fig.legend(
    handles=[
        all_handles[deployment]
        for deployment in legend_entries
    ],
    labels=[
        SERIES_STYLE[deployment]["label"]
        for deployment in legend_entries
    ],
    loc="lower center",
    bbox_to_anchor=(0.5, 0.015),
    ncol=5,                 # One row preserves the requested order
    frameon=False,
    handlelength=1.45,
    handletextpad=0.25,
    columnspacing=0.55,
    borderaxespad=0.0,
)


# ============================================================
# Shared axis labels
# ============================================================

fig.text(
    0.57,
    0.245,
    r"User rank (ascending $LP_D$)",
    ha="center",
    va="center",
    fontsize=7,
)

fig.text(
    0.025,
    0.62,
    r"Privacy leakage ($LP_D$)",
    ha="center",
    va="center",
    rotation="vertical",
    fontsize=7,
)


fig.subplots_adjust(
    left=0.17,
    right=0.995,
    top=0.90,
    bottom=0.38,
    wspace=0.12,
)



OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fig.savefig(
    OUTPUT_FILE,
    format="pdf",
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.015,
)

print(
    f"\nSaved combined CCS figure to:\n"
    f"{OUTPUT_FILE.resolve()}"
)

plt.show()
plt.close(fig)
