# 🔗 CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/) [![Rust 1.70+](https://img.shields.io/badge/Rust-1.70+-000000.svg?logo=rust&logoColor=white)](https://www.rust-lang.org/) [![Poetry 1.8.2](https://img.shields.io/badge/Poetry-1.8.2-60A5FA.svg?logo=poetry&logoColor=white)](https://python-poetry.org/)

Official software artifact repository for the ACM CCS paper:
> **CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols**

This artifact contains the experimental framework, Rust candidate linking engines, Python trace reconstruction tools, SUMO mobility generators, empirical datasets (12 commodity devices), and plotting scripts to reproduce all results in the paper.

---

## 📖 Paper Overview & Abstract

Smartphones simultaneously transmit temporary network identifiers over LTE, Wi-Fi, and BLE. Per-protocol identifier randomization assumes that privacy protections compose across protocols. **CrossLink** demonstrates that they do not: even under fully passive eavesdropping and noisy localization, unsynchronized identifier rotations enable cross-protocol stitching of device trajectories over time.

Key experimental findings *(draft version - to be modified)*:
- **Trajectory Reconstruction**: Reconstructs complete multi-protocol traces for **83% of users**, compared to **22%** for the best single-protocol baseline.
- **Partial Sniffer Coverage**: Strategic sniffer placement near LTE handover regions and mobile sniffers retains sufficient evidence to bridge observation gaps.

> 🏗️ **Architecture & Flow**: The system architecture, component module graph, and execution flow are documented in [**`ARCHITECTURE.md`**](ARCHITECTURE.md).

![Attack pipeline](design/approach.png)

---

## 🏆 Paper Claims & Verification Matrix

| Claim / Benchmark | Config File (`configs/`) | Commands | Target Figure / Output | Compute Time |
| :--- | :--- | :--- | :--- | :---: |
| **Claim 1: Multi-Protocol Tracking** (512 users across LTE/Wi-Fi/BLE) | `scenario_result_512_sumo_all.yml` | `sumo` $\to$ `generate_user_data` $\to$ `cargo` $\to$ `reconstruction` $\to$ `plot` | `output/images/<scenario>/privacy_leakage_*.pdf` | ~30–45 min |
| **Claim 2: Synced Randomization Defense** | `scenario_synced_randomization_512_all.yml` | `generate_user_data` $\to$ `cargo` $\to$ `plot_synced.py` | `plot/privacy_leakage_synced_*.pdf` | ~15–20 min |
| **Claim 3: Proximity / Mixing Countermeasure** | `scenario_proximity_512_sumo_all.yml` | `generate_user_data_proximity` $\to$ `cargo` $\to$ `plot_proximity.py` | `plot/privacy_leakage_proximity_*.pdf` | ~20–30 min |
| **Claim 4: Partial Sniffer Placement** | `scenario_partial_512_sumo_strategic.yml` | `cargo generate_sniffer_data` $\to$ `plot_partial.py` | `plot/privacy_leakage_partial_*.pdf` | ~15–25 min |
| **Claim 5: Sensitivity (Localization Noise & Mobility)** | `q3_localization_error_high.yml`, `q4_mobility_512_sumo_5_LB.yml` | `q3_localization.py`, `q4_mobility.py` | `plot/privacy_leakage_q3_*.pdf`, `plot/privacy_leakage_q4_*.pdf` | ~20–30 min |
| **Claim 6: Empirical Validation** (12 commodity devices) | `real_world/` | `cd real_world && python3 crosslink.py && python3 evaluate.py` | `real_world/inter_links.csv`, `real_world/intra_links.csv` | ~3–5 min |

---

## 🗂️ Repository Structure

```text
.
├── configs/                 # Scenario configuration YAML files
├── data/                    # User mobility traces, sniffer logs, and binary outputs
├── design/                  # Pipeline diagrams (approach.png, code_pipeline.pdf)
├── output/                  # Reconstructed device traces and PDF vector figures
├── plot/                    # Plotting scripts for paper figures
├── reconstruction/          # Single- and multi-protocol trace reconstruction algorithms
├── scenario/                # SUMO mobility spatial networks and OSM polygon bounds
├── simulation/              # SUMO and synthetic graph mobility generators
├── tracing_algorithm/       # Spatiotemporal link aggregation, refinement, & filtering
├── rust_code/               # High-performance Rust backend (sniffer logging, inter/intra mapping)
├── real_world/              # Empirical data & evaluation scripts for 12 commodity devices
├── main.py                  # CLI entry point for Python pipeline stages
└── pipeline.py              # Stage execution definitions consumed by main.py
```

---

## 🖥️ System Requirements

| Requirement | Fast Smoke Test (32 Users) | Full Evaluation (512 Users) |
| :--- | :--- | :--- |
| **CPU** | 2 Cores (x86-64) | 8+ Cores (Intel Core i7 / AMD Ryzen 7 or server equivalent) |
| **RAM** | 4 GB | 16 GB minimum (32 GB recommended for large SUMO graphs) |
| **Storage** | 10 GB free space | 64 GB free space (SSD recommended) |
| **OS** | Linux (Ubuntu 22.04 LTS+ minimum) | Linux (Ubuntu 24.04 LTS tested; Ubuntu 22.04 LTS+ minimum) |

---

## ⚙️ Software Setup & Installation

### 1. Python Environment (Poetry)

Install Python dependencies from the repository root:

```bash
# Install Poetry package manager
sudo apt install python3-poetry   # Alternative: pip3 install poetry

# Verify Poetry version (tested with Poetry 1.8.2)
poetry --version

# Install dependencies from pyproject.toml
poetry install

# Activate the Python virtual environment shell
poetry shell
```

> [!TIP]  
> Alternatively, prefix Python commands with `poetry run` instead of entering a Poetry shell. If you prefer `uv`, export dependencies to `requirements.txt` and execute via `uv`'s pip compatibility layer.

### 2. Rust Toolchain & Engine Compilation

Build/check the Rust implementation from the directory that contains `Cargo.toml`:

```bash
# Install Rustup toolchain and Rust packages
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Source environment configuration to load cargo package path (or open a new terminal)
source ~/.bashrc

# Build release binaries and dependencies
cargo build --release
```

---

## ⚡ Quick Start: 10-Minute Kick-the-Tires Stage

Run a lightweight 32-user smoke test (`scenario_test_32_sumo_smoke.yml`) to verify toolchain functionality (< 5 min compute, < 4 GB RAM):

```bash
cd code
CONFIG=scenario_test_32_sumo_smoke.yml
SCENARIO=$(basename "$CONFIG" .yml)

# 1. Verify pipeline options
python3 main.py -c "$CONFIG" -t help

# 2. Clean cache
python3 main.py -c "$CONFIG" -t clean_all

# 3. Run smoke test end-to-end
python3 main.py -c "$CONFIG" -t generate_user_data
cargo run --release -- "$SCENARIO" generate_sniffer_data
python3 main.py -c "$CONFIG" -t aggregate_new
cargo run --release --features inter_map_disable_trim -- "$SCENARIO" inter_map
cargo run --release --features intra_map_disable_trim -- "$SCENARIO" intra_map
python3 main.py -c "$CONFIG" -t refine_intramap
python3 main.py -c "$CONFIG" -t intra_filter
python3 main.py -c "$CONFIG" -t reconstruction
python3 main.py -c "$CONFIG" -t plot
```

**Expected Outcome**: Produces reconstructed traces in `output/data/` and figures in `output/images/scenario_test_32_sumo_smoke/`.

---

## 🏃 Step-by-Step Pipeline Execution

Full 512-user tracking evaluation (`scenario_result_512_sumo_all.yml`):

```bash
cd code
CONFIG=scenario_result_512_sumo_all.yml
SCENARIO=$(basename "$CONFIG" .yml)
```

### 1. Generate User Mobility Traces
```bash
python3 main.py -c "$CONFIG" -t sumo
python3 main.py -c "$CONFIG" -t filter_users_polygon
python3 main.py -c "$CONFIG" -t filter_users_RI_Count
```
*(Pre-generated traces are included in `data/`; Step 1 can be skipped if using provided data).*

### 2. Generate Protocol Transmissions
```bash
python3 main.py -c "$CONFIG" -t generate_user_data
```
For proximity mixing countermeasure:
```bash
python3 main.py -c "$CONFIG" -t generate_user_data_proximity
```

### 3. Generate Sniffer Observations (Rust)
```bash
# Static sniffer deployment
cargo run --release -- "$SCENARIO" generate_sniffer_data

# Mobile sniffer scenario (30 mobile sniffers)
cargo run --release -- "$SCENARIO" generate_sniffer_data_from_end_devices 30
```

### 4. Aggregate Sniffer Observations
```bash
python3 main.py -c "$CONFIG" -t aggregate_new
```

### 5. Candidate Mapping & Refinement
```bash
# Rust initial candidate mapping
cargo run --release --features inter_map_disable_trim -- "$SCENARIO" inter_map
cargo run --release --features intra_map_disable_trim -- "$SCENARIO" intra_map

# Python consistency refinement & filtering
python3 main.py -c "$CONFIG" -t refine_intramap
python3 main.py -c "$CONFIG" -t intra_filter
```

### 6. Reconstruct Traces & Quantify Privacy Leakage
```bash
python3 main.py -c "$CONFIG" -t reconstruction
```

### 7. Plot Figures
```bash
python3 main.py -c "$CONFIG" -t plot
```
Outputs PDF figures to `output/images/<scenario>/privacy_leakage_<scenario>.pdf`.

---

## 🔬 Real World Device Validity & Empirical Validation

The real world data are provided in two separate `.csv` files: `lte_observations.csv` and `ble_observations.csv` for **12 commodity devices**. The sniffer anchors and ground truths are provided in `anchors.csv` and `ground_truth.csv` respectively.

To run empirical linkability reconstruction and performance evaluation:

```bash
cd real_world

# 1. Run CrossLink inter-protocol & intra-protocol candidate linking
python3 crosslink.py
```
**Expected Output:** `inter_links.csv` and `intra_links.csv`

```bash
# 2. Evaluate linking accuracy and metrics against ground truth
python3 evaluate.py

# 3. Plot empirical result figures
python3 plot_results.py
```

---

## ⚙️ Configuration Guide

Key YAML options in `configs/`:

| Parameter Group | Key Parameters | Description |
| :--- | :--- | :--- |
| **Mobility** | `POLYGON_COORDS`, `USER_TIMESTEPS`, `mobility_factor` | Spatial bounds, timesteps, movement speed |
| **Scale** | `TOTAL_NUMBER_OF_USERS`, `ENABLE_USER_THRESHOLD` | Population size (32 to 512) |
| **Protocols** | `ENABLE_BLUETOOTH`, `ENABLE_WIFI`, `ENABLE_LTE` | Protocol layer toggles |
| **Transmissions** | `*_MIN_TRANSMIT`, `*_MAX_TRANSMIT` | Transmission packet interval bounds (seconds) |
| **Rotations** | `*_MIN_REFRESH`, `*_MAX_REFRESH` | Temporary identifier rotation bounds (seconds) |
| **Defenses** | `ENABLE_SYNCED_RANDOMIZATION`, `PROTOCOL_*_REFRESH` | Synchronized rotation defense settings |
| **Sniffer Bounds** | `BLUETOOTH_RANGE`, `WIFI_RANGE`, `LTE_RANGE` | Reception range per protocol (meters) |
| **Noise & Coverage**| `*_LOCALIZATION_ERROR`, `ENABLE_PARTIAL_COVERAGE` | Distance error noise and coverage topology |

---

## 🛠️ Troubleshooting FAQ

<details>
<summary><b>1. FileNotFoundError or Path Resolution Errors</b></summary>

- Execute Python commands from the directory containing `main.py`.
- Execute Cargo commands from the directory containing `Cargo.toml`.
</details>

<details>
<summary><b>2. Cargo Argument Formatting</b></summary>

- Pass scenario names to Cargo **without** the `.yml` extension (e.g. `scenario_result_512_sumo_all`).
</details>

<details>
<summary><b>3. Memory Constraints</b></summary>

- SUMO trajectory filtering for 512 users can require 16–32 GB RAM. Use pre-generated traces in `data/` or test with 32/128 user scenarios if RAM is constrained.
</details>

<details>
<summary><b>4. Poetry Environment</b></summary>

- If Poetry shell activation is skipped, prefix Python commands with `poetry run`.
</details>

---

## 📜 Citation & License

```bibtex
@inproceedings{crosslink2026ccs,
  title={{CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols}},
  author={Anonymous Authors},
  booktitle={Proceedings of the ACM SIGSAC Conference on Computer and Communications Security (CCS)},
  year={2026},
  publisher={ACM}
}
```

### Ethics Note
This artifact is provided for reproducible academic research and security evaluation. Methodology and code must not be used to track unauthorized third-party devices or individuals.
