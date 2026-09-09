# CrossLink Architecture & Configuration Guide

This document provides a detailed technical overview of the system architecture, component modules, algorithmic workflow, and configuration options for **CrossLink**, a passive cross-protocol tracking framework linking temporary identifiers emitted across LTE, Wi-Fi, and BLE.

---

## 🗂️ Repository Structure

```text
.
├── configs/                 # Scenario configuration YAML files (32 to 512 users)
├── data/                    # User mobility traces, sniffer logs, and ground truth data
├── design/                  # Pipeline architectural diagrams (approach.png, code_pipeline.pdf)
├── output/                  # Reconstructed device traces and generated PDF vector figures
├── plot/                    # Plotting scripts for paper figures and evaluation charts
├── reconstruction/          # Single- and multi-protocol trace reconstruction algorithms
├── scenario/                # SUMO mobility spatial networks and OSM polygon bounds
├── simulation/              # SUMO and synthetic graph mobility generators
├── tracing_algorithm/       # Spatiotemporal link aggregation, refinement, & filtering
├── rust_code/               # High-performance Rust backend (sniffer logging, inter/intra mapping)
├── real_world/              # Empirical dataset & evaluation scripts for 12 commodity devices
├── main.py                  # CLI entry point for Python pipeline stages
├── pipeline.py              # Pipeline stage execution definitions consumed by main.py
└── ARCHITECTURE.md          # Architectural specification and module interaction reference
```

---

## Configuration Guide

All evaluation parameters and scenario profiles are centrally controlled via YAML configuration files located in `configs/`.

### Parameter Specification Reference

| Parameter Group | Key Parameters | Description |
| :--- | :--- | :--- |
| **Mobility** | `POLYGON_COORDS`, `USER_TIMESTEPS`, `mobility_factor` | Geographic bounding polygon coordinates, simulation duration, and movement speed factor |
| **Scale** | `TOTAL_NUMBER_OF_USERS`, `ENABLE_USER_THRESHOLD` | Target user population size ($N = 32 \dots 512$) and filtering flags |
| **Protocols** | `ENABLE_BLUETOOTH`, `ENABLE_WIFI`, `ENABLE_LTE` | Boolean flags toggling individual radio protocol evaluation layers |
| **Transmissions** | `*_MIN_TRANSMIT`, `*_MAX_TRANSMIT` | Min/max transmission interval bounds (in seconds) per protocol |
| **Rotations** | `*_MIN_REFRESH`, `*_MAX_REFRESH` | Min/max temporary identifier rotation interval bounds (in seconds) |
| **Defenses** | `ENABLE_SYNCED_RANDOMIZATION`, `PROTOCOL_*_REFRESH` | Synchronized multi-protocol identifier rotation parameters |
| **Sniffer Bounds** | `BLUETOOTH_RANGE`, `WIFI_RANGE`, `LTE_RANGE` | Maximum physical sniffer reception radius (meters) per protocol |
| **Noise & Coverage**| `*_LOCALIZATION_ERROR`, `ENABLE_PARTIAL_COVERAGE` | Spatiotemporal distance localization noise standard deviation ($\sigma$) and partial placement flags |

---

## Architectural Design Diagrams

The design directory includes additional reference diagrams:
- **`design/approach.png`**: High-level attack pipeline model.
- **`design/code_pipeline.pdf`**: Detailed module and control-flow layout.

