from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Run this script from the directory containing results.json.
INPUT_JSON = Path("results.json")
OUTPUT_ROOT = Path("output/images")
OUTPUT_PDF = OUTPUT_ROOT / "accuracy_identifier_linkings_real_ccs.pdf"
OUTPUT_PNG = OUTPUT_ROOT / "accuracy_identifier_linkings_real_ccs.png"

GROUPS = ["Single-protocol", "Cross-protocol"]
PROTOCOLS = ["BLE", "LTE"]

with INPUT_JSON.open("r", encoding="utf-8") as file:
    results = json.load(file)

# Each tuple is (correct links, total identifier rotations).
# Match the order of GROUPS: single-protocol, then cross-protocol.
COUNTS = {
    protocol: [
        (results[f"{protocol}_{mode}_correct"], results[f"{protocol}_{mode}_total"])
        for mode in ("single", "cross")
    ]
    for protocol in PROTOCOLS
}

# Keep these protocol colors identical across the paper.
PROTOCOL_COLORS = {
    "BLE": "#0072B2",
    "LTE": "#E69F00",
}


# -----------------------------------------------------------------------------
# Shared camera-ready style
# -----------------------------------------------------------------------------

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
        "legend.frameon": False,
        "legend.handlelength": 1.5,
        "legend.handletextpad": 0.45,
        "legend.columnspacing": 1.1,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def percentages(protocol: str) -> np.ndarray:
    return np.array(
        [100.0 * correct / total for correct, total in COUNTS[protocol]],
        dtype=float,
    )


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Generate directly at the final CCS single-column width.
    fig, ax = plt.subplots(figsize=(3.35, 2.1))

    x = np.arange(len(GROUPS), dtype=float)
    offsets = {
        "BLE": -0.235,
        "LTE": 0.0,
    }
    bar_width = 0.175

    bars_by_protocol = {}

    for protocol in PROTOCOLS:
        values = percentages(protocol)

        bars = ax.bar(
            x + offsets[protocol],
            values,
            width=bar_width,
            color=PROTOCOL_COLORS[protocol],
            edgecolor=PROTOCOL_COLORS[protocol],
            linewidth=0.55,
            label=protocol,
            zorder=3,
        )
        bars_by_protocol[protocol] = bars

        # Show percentages only; raw counts are clearer in the caption.
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                value + 1.7,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=6.7,
                fontweight="semibold",
                clip_on=False,
            )

    ax.set_xlim(-0.56, 1.56)
    ax.set_ylim(0, 107)

    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS)

    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))

    ax.set_ylabel("Linking accuracy (%)", labelpad=3)

    ax.set_axisbelow(True)
    ax.grid(axis="y", color="0.87", linewidth=0.45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(
        axis="both",
        direction="out",
        length=2.5,
        width=0.6,
        pad=2,
    )

    # Bottom legend, matching the standardized Figure 6.
    fig.legend(
        handles=[bars_by_protocol[p][0] for p in PROTOCOLS],
        labels=PROTOCOLS,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.018),
        ncol=3,
        borderaxespad=0.0,
    )

    fig.subplots_adjust(
        left=0.19,
        right=0.985,
        bottom=0.245,
        top=0.955,
    )

    # Fixed dimensions; do not use bbox_inches="tight".
    fig.savefig(OUTPUT_PDF)
    fig.savefig(OUTPUT_PNG, dpi=300)

    print(f"Saved PDF: {OUTPUT_PDF}")
    print(f"Saved PNG: {OUTPUT_PNG}")

    plt.show()


if __name__ == "__main__":
    main()

