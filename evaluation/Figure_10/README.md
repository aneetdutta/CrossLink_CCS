# Figure 10: Question 3 (Q3) - Difference RI and TI

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 10** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 10
- **Evaluation Scenario**: Q3: Difference RI and TI

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Low, Low** | `configs/scenario_q2_ri_low_ti_low.yml` | Low Rotation Interval (RI), Low Transmission Interval (TI) |
| **Low, High** | `configs/scenario_q2_ri_low_ti_high.yml` | Low Rotation Interval (RI), High Transmission Interval (TI) |
| **High, Low** | `configs/scenario_q2_ri_low_ti_same.yml` | High Rotation Interval (RI), Low Transmission Interval (TI) |
| **High, High** | `configs/scenario_q2_ri_same_ti_high.yml` | High Rotation Interval (RI), High Transmission Interval (TI) |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make q3
```

### Run from this Directory:
```bash
make
# or
make q3
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_scenario_q2_ri_low_ti_low.pdf`
- **Visualization Script**: `python3 plot/q3_partial.py`
