# 🔗 CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/) [![Rust 1.70+](https://img.shields.io/badge/Rust-1.70+-000000.svg?logo=rust&logoColor=white)](https://www.rust-lang.org/) 


Official software artifact repository for the ACM CCS paper:
> **CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols**

This repository contains the artifact for CrossLink, a passive cross-protocol tracking framework that links temporary identifiers emitted by the same device over LTE, WiFi, and BLE. The artifact supports the simulation, tracing, reconstruction, and plotting pipeline used in the paper.

---

## Paper Overview

Smartphones simultaneously transmit temporary network identifiers over LTE, Wi-Fi, and BLE to facilitate network association and service discovery. Per-protocol identifier randomization assumes that privacy protections compose independently across protocols. **CrossLink** demonstrates that they do not: even under fully passive eavesdropping and noisy spatiotemporal localization, unsynchronized identifier rotations enable cross-protocol stitching of device trajectories over time.


> **Architecture & Configuration Guide**: The detailed modular architecture, repository structure, Rust/Python modules, and YAML configuration guide are documented in [**`ARCHITECTURE.md`**](ARCHITECTURE.md).

![Attack pipeline](design/approach.png)

---

## System Requirements

The artifact is designed to run on standard Linux hardware. Below are the recommended system configurations for quick testing vs. full evaluation.

| Requirement | Fast Smoke Test (32 Users) | Full Evaluation (512 Users) |
| :--- | :--- | :--- |
| **CPU** | 2 Cores (x86-64) | 8+ Cores (Intel Core i7 / AMD Ryzen 7 or server equivalent) |
| **RAM** | 4 GB | 16 GB minimum (32 GB recommended for large SUMO graphs) |
| **Storage** | 10 GB free space | 64 GB free space (SSD recommended) |
| **OS** | Linux (Ubuntu 22.04 LTS+ minimum) | Linux (Ubuntu 24.04 LTS tested; Ubuntu 22.04 LTS+ minimum) |
| **Software** | Python 3.10+, Rust 1.70+, SUMO 1.18+ | Python 3.10+, Rust 1.70+, SUMO 1.18+ |

---

## Software Setup & Installation

```bash
# Enter the CrossLink Directory

cd CrossLink_CCS
# Software setup and installation
make install

# Activate virtual environment
source .venv/bin/activate

# To clean build artifacts, compiled bytecode, and caches:
make clean
```

---

## Mobility Data Generation (20 compute minutes)

```bash
# Generate 512-user mobility traces (default)
make mobility_data
```

---

## Quick Start: Smoke Test (2 compute minutes)

Run a lightweight **32-user test** (`scenario_test_32_sumo_smoke.yml`) to verify complete end-to-end functionality of the repository:

```bash
make smoke_test
```



**Expected Outcome**: Successfully generates privacy score files in `output/data/scenario_test_32_smoke/` and plots verification figures in `output/images/privacy_leakage_scenario_test_32_sumo_smoke.pdf`.

---

## 512-User Execution Pipeline

To reproduce the main paper basline result with 512 users and full coverage , execute the full pipeline using the `configs/scenario_result_512_sumo_all1.yml` using the following command:

```bash
make baseline
```
**Expected Output**: output/data/scenario_result_512_sumo_all1/*.csv, output/images/privacy_leakage_scenario_result_512_sumo_all1.pdf and correct_linkings_by_mapping_protocol_scenario_result_512_sumo_all1.pdf (Figure 7)

The workflow consists of the following sequential stages:

```bash
# ------------------------------------------------------------------------------
# Stage 0: Environment Setup
# ------------------------------------------------------------------------------
source .venv/bin/activate
CONFIG=scenario_result_512_sumo_all1.yml
SCENARIO=$(basename "$CONFIG" .yml)

# ------------------------------------------------------------------------------
# Stage 1: Mobility Trajectory Filtering (20 compute minutes)
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t sumo
python3 main.py -c "$CONFIG" -t filter_users_polygon
python3 main.py -c "$CONFIG" -t filter_users_RI_Count

# ------------------------------------------------------------------------------
# Stage 2: User Data Generation (<1 compute minute)
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t generate_user_data

# ------------------------------------------------------------------------------
# Stage 3: Sniffer Data Generation (1 compute minute)
# ------------------------------------------------------------------------------
cd rust_code && cargo run --release -- "$SCENARIO" generate_sniffer_data && cd ..

# ------------------------------------------------------------------------------
# Stage 4: Aggregation (<1 compute minute)
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t aggregate_new

# ------------------------------------------------------------------------------
# Stage 5: Inter/Intra Mapping Candidate Construction (2 compute minutes)
# ------------------------------------------------------------------------------
cd rust_code && cargo run --release --features inter_map_disable_trim -- "$SCENARIO" inter_map && cd ..
cd rust_code && cargo run --release --features intra_map_disable_trim -- "$SCENARIO" intra_map && cd ..

# ------------------------------------------------------------------------------
# Stage 6: Inter/Intra Mapping Refinement (3 compute minutes)
# ------------------------------------------------------------------------------

python3 main.py -c "$CONFIG" -t refine_intramap
python3 main.py -c "$CONFIG" -t intra_filter

# ------------------------------------------------------------------------------
# Stage 7: Trace Reconstruction (40 compute minutes)
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t reconstruction

# ------------------------------------------------------------------------------
# Stage 7: Result Visualization (<1 compute minute)
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t plot
```

---

## Real-World Device Validity & Empirical Validation

To validate CrossLink's effectiveness on physical hardware, we evaluated the framework on **12 commodity devices** transmitting LTE and BLE packets in real-world environments.

### Dataset Files in `real_world/`:
- `lte_observations.csv`: Passive LTE sniffer captures.
- `ble_observations.csv`: Passive BLE advertisement captures.
- `anchors.csv`: Mix-zone entry/exit mappings.
- `ground_truth.csv`: True device identity mappings.

### Execution Steps:
```bash
# Run real-world device evaluation (via Makefile)
make validate_real_world
```

**Expected Output**: Produces `inter_links.csv` and `intra_links.csv` containing the mappings produced by CrossLink algorithm. The resulting plot is in `output/images/accuracy_identifier_linkings_real_ccs.pdf` 



## 🛠️ Troubleshooting FAQ

<details>
<summary><b>1. FileNotFoundError or Module Import Errors</b></summary>

- Always ensure Python commands are executed from the repository root or the folder containing `main.py`.
- If using Poetry, verify virtualenv activation with `poetry shell` or prefix commands with `poetry run`.
</details>

<details>
<summary><b>2. Cargo Execution & Argument Formatting</b></summary>

- Pass scenario names to Cargo **without** the `.yml` file extension (e.g., `scenario_result_512_sumo_all`).
- Execute Cargo commands from the directory containing `Cargo.toml`.
</details>

<details>
<summary><b>3. Memory Limits & Out-Of-Memory (OOM) Errors</b></summary>

- SUMO trajectory processing for 512 users can require 16–32 GB RAM.
- If RAM is limited, use pre-generated traces in `data/` or evaluate with 32/128 user configurations (`scenario_test_32_sumo_smoke.yml`).
</details>

<details>
<summary><b>4. Rust Compilation & Feature Flags</b></summary>

- Cargo commands utilize feature flags such as `--features inter_map_disable_trim`. Ensure clean builds with `cargo clean` if toolchain flags are modified.
</details>

---




## ⚖️ Ethics Note

This artifact is provided strictly for academic research, peer verification, and security analysis. The spatiotemporal linking techniques and tools described must not be deployed against unconsenting individuals or third-party device networks.
