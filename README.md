# 🔗 CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/) [![Rust 1.70+](https://img.shields.io/badge/Rust-1.70+-000000.svg?logo=rust&logoColor=white)](https://www.rust-lang.org/) [![Poetry 1.8.2](https://img.shields.io/badge/Poetry-1.8.2-60A5FA.svg?logo=poetry&logoColor=white)](https://python-poetry.org/)


Official software artifact repository for the ACM CCS paper:
> **CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols**

This repository contains the artifact for CrossLink, a passive cross-protocol tracking framework that links temporary identifiers emitted by the same device over LTE, WiFi, and BLE. The artifact supports the simulation, tracing, reconstruction, and plotting pipeline used in the paper.

---

## 📖 Paper Overview

Smartphones simultaneously transmit temporary network identifiers over LTE, Wi-Fi, and BLE to facilitate network association and service discovery. Per-protocol identifier randomization assumes that privacy protections compose independently across protocols. **CrossLink** demonstrates that they do not: even under fully passive eavesdropping and noisy spatiotemporal localization, unsynchronized identifier rotations enable cross-protocol stitching of device trajectories over time.


> 🏗️ **Architecture & Configuration Guide**: The detailed modular architecture, repository structure, Rust/Python modules, and YAML configuration guide are documented in [**`ARCHITECTURE.md`**](ARCHITECTURE.md).

![Attack pipeline](design/approach.png)

---

## 🖥️ System Requirements

The artifact is designed to run on standard Linux hardware. Below are the recommended system configurations for quick testing vs. full evaluation.

| Requirement | Fast Smoke Test (32 Users) | Full Evaluation (512 Users) |
| :--- | :--- | :--- |
| **CPU** | 2 Cores (x86-64) | 8+ Cores (Intel Core i7 / AMD Ryzen 7 or server equivalent) |
| **RAM** | 4 GB | 16 GB minimum (32 GB recommended for large SUMO graphs) |
| **Storage** | 10 GB free space | 64 GB free space (SSD recommended) |
| **OS** | Linux (Ubuntu 22.04 LTS+ minimum) | Linux (Ubuntu 24.04 LTS tested; Ubuntu 22.04 LTS+ minimum) |
| **Software** | Python 3.10+, Rust 1.70+, SUMO 1.18+ | Python 3.10+, Rust 1.70+, SUMO 1.18+ |

---

## ⚙️ Software Setup & Installation

```bash
# Software setup and installation
make install

# Activate virtual environment
source .venv/bin/activate

# To clean build artifacts, compiled bytecode, and caches:
make clean
```

---

## 🚗 Mobility Data Generation

```bash
# Generate 512-user mobility traces (default)
make mobility_data
```

---

## ⚡ Quick Start: Smoke Test

Run a lightweight **32-user test** (`scenario_test_32_sumo_smoke.yml`) to verify complete end-to-end toolchain functionality:

```bash
make smoke_test
```

**Expected Outcome**: Successfully generates reconstructed traces in `output/data/` and plots verification figures in `output/images/scenario_test_32_sumo_smoke/`.

---

## 512-User Execution Pipeline

To reproduce the main paper results across 512 users, execute the full pipeline using `configs/scenario_result_512_sumo_all.yml`. The workflow consists of the following sequential stages:

```bash
# ------------------------------------------------------------------------------
# Stage 0: Environment Setup
# ------------------------------------------------------------------------------
source .venv/bin/activate
CONFIG=scenario_result_512_sumo_all.yml
SCENARIO=$(basename "$CONFIG" .yml)

# ------------------------------------------------------------------------------
# Stage 1: Mobility Trajectory Filtering
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t filter_users_polygon
python3 main.py -c "$CONFIG" -t filter_users_RI_Count

# ------------------------------------------------------------------------------
# Stage 2: User Data Generation
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t generate_user_data

# (Optional) Proximity mixing countermeasure run
python3 main.py -c "$CONFIG" -t generate_user_data_proximity

# ------------------------------------------------------------------------------
# Stage 3: Sniffer Data Generation
# ------------------------------------------------------------------------------
cargo run --release -- "$SCENARIO" generate_sniffer_data

# (Optional) Mobile sniffer scenario (e.g., 30 mobile sniffing nodes)
cargo run --release -- "$SCENARIO" generate_sniffer_data_from_end_devices 30

# ------------------------------------------------------------------------------
# Stage 4: Aggregation
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t aggregate_new

# ------------------------------------------------------------------------------
# Stage 5: Inter/Intra Mapping & Refinement
# ------------------------------------------------------------------------------
cargo run --release --features inter_map_disable_trim -- "$SCENARIO" inter_map
cargo run --release --features intra_map_disable_trim -- "$SCENARIO" intra_map

python3 main.py -c "$CONFIG" -t refine_intramap
python3 main.py -c "$CONFIG" -t intra_filter

# ------------------------------------------------------------------------------
# Stage 6: Trace Reconstruction
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t reconstruction

# ------------------------------------------------------------------------------
# Stage 7: Result Visualization
# ------------------------------------------------------------------------------
python3 main.py -c "$CONFIG" -t plot
```

---

## 🔬 Real-World Device Validity & Empirical Validation

To validate CrossLink's effectiveness on physical hardware, we evaluated the framework on **12 commodity devices** transmitting LTE and BLE packets in real-world environments.

### Dataset Files in `real_world/`:
- `lte_observations.csv`: Passive LTE sniffer captures.
- `ble_observations.csv`: Passive BLE advertisement captures.
- `anchors.csv`: Physical sniffer location coordinates.
- `ground_truth.csv`: True device identity mappings.

### Execution Steps:
```bash
# Run real-world device evaluation (via Makefile)
make validate_real_world
```

**Expected Output**: Produces `inter_links.csv` and `intra_links.csv` detailing predicted cross-protocol device associations, alongside evaluation metrics.

---

## 🏆 Experimental Evaluation & Verification Matrix

This matrix maps each figure and claim in the paper directly to its corresponding configuration, execution commands, target outputs, and estimated compute runtime:

<table>
  <thead>
    <tr>
      <th align="left">Paper Reference</th>
      <th align="left">Evaluation Scenario</th>
      <th align="left">Configurations</th>
      <th colspan="2" align="left">Commands</th>
      <th align="left">Results</th>
      <th align="center">Compute Time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Figure 3</b></td>
      <td>Ablation Studies</td>
      <td>• Baseline<br>• No_Loc<br>• Nom_Loc<br>• Nom</td>
      <td colspan="2">make ablation</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td><b>Figure 6 & 7</b></td>
      <td>Q1</td>
      <td>• Baseline<br>• LB1<br>• BW1<br>• LW1</td>
      <td colspan="2">make q1</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td rowspan="2"><b>Figure 8</b></td>
      <td>Q2 a (Partial Coverage)</td>
      <td rowspan="2">• Full Coverage (Baseline)<br>• PATCH<br>• MOB SPOT<br>• RAND</td>
      <td>make q2a</td>
      <td rowspan="2">make q2</td>
      <td rowspan="2"></td>
      <td rowspan="2" align="center"></td>
    </tr>
    <tr>
      <td>Q2 b (Partial Coverage)</td>
      <td>make q2b</td>
    </tr>
    <tr>
      <td><b>Table 5</b></td>
      <td>Effect of error-tolerance choices</td>
      <td>• Bounded (Baseline)<br>• Heavy-tail (baseline error tolerance)<br>• Heavy-tail (increased error tolerance)</td>
      <td colspan="2">make t5</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td><b>Figure 9</b></td>
      <td>Q2: Different bounded localization errors</td>
      <td>• Low<br>• Baseline<br>• High</td>
      <td colspan="2">make q2_loc</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td><b>Figure 10</b></td>
      <td>Q3: Difference RI and TI</td>
      <td>• Low, Low<br>• Low, High<br>• High, Low<br>• High, High</td>
      <td colspan="2">make q3</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td><b>Figure 11(a)</b></td>
      <td>Q4: Max User Velocity</td>
      <td>• 1.6<br>• 3<br>• 5<br>• 10</td>
      <td colspan="2">make q4a</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td rowspan="2"><b>Figure 11(b & c)</b></td>
      <td>Q4: User density</td>
      <td rowspan="2">• N=512<br>• N=1024<br>• N=1536<br>• SUMO Synthetic</td>
      <td>make q4_user_den</td>
      <td rowspan="2">make_q4_b_c</td>
      <td rowspan="2"></td>
      <td rowspan="2" align="center"></td>
    </tr>
    <tr>
      <td>Q4: Mix-zone duration</td>
      <td>make q4_mix_dur</td>
    </tr>
    <tr>
      <td><b>Figure 12</b></td>
      <td>Example scenario: Tracking duration</td>
      <td>• Full coverage<br>• MOB<br>• PATCH<br>• RAND</td>
      <td colspan="2">make eg_scen</td>
      <td></td>
      <td align="center"></td>
    </tr>
    <tr>
      <td><b>Figure 13</b></td>
      <td>countermeasure</td>
      <td>• No sync (baseline)<br>• Sync 180 s<br>• Sync 600 s<br>• Perfect mixing<br>• Sync</td>
      <td colspan="2">make cm</td>
      <td></td>
      <td align="center"></td>
    </tr>
  </tbody>
</table>

---

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

## 📜 Citation & License

If you use CrossLink in your research, please cite our paper:

```bibtex
@inproceedings{crosslink2026ccs,
  title={{CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols}},
  author={Anonymous Authors},
  booktitle={Proceedings of the ACM SIGSAC Conference on Computer and Communications Security (CCS)},
  year={2026},
  publisher={ACM}
}
```

This software artifact is released under the **MIT License**.

---

## ⚖️ Ethics Note

This artifact is provided strictly for academic research, peer verification, and security analysis. The spatiotemporal linking techniques and tools described must not be deployed against unconsenting individuals or third-party device networks.
