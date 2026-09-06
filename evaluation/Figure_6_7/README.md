# Figures 6 & 7: Question 1 (Q1) - Impact of Radio Protocol Combinations

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 6 & 7** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 6 & 7
- **Evaluation Scenario**: Q1 (Impact of Radio Protocols)

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Baseline** | `configs/scenario_result_512_sumo_all.yml` | Full multi-protocol tracking (LTE + BLE + Wi-Fi) |
| **LB1** | `configs/scenario_result_512_sumo_LB1.yml` | Two-protocol tracking: LTE + BLE |
| **BW1** | `configs/scenario_result_512_sumo_BW1.yml` | Two-protocol tracking: BLE + Wi-Fi |
| **LW1** | `configs/scenario_result_512_sumo_LW1.yml` | Two-protocol tracking: LTE + Wi-Fi |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make q1
```

### Run from this Directory:
```bash
make
# or
make q1
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_q1_512_band.pdf`
- **Visualization Script**: `python3 plot/plot_q1.py`
