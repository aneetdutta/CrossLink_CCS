# Figure 11(a): Question 4 (Q4) - Maximum User Velocity

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 11(a)** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 11(a)
- **Evaluation Scenario**: Q4: Max User Velocity

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **1.6 m/s** | `configs/q4_mobility_512_sumo_1-5_LB.yml` | Pedestrian walking velocity (~1.6 m/s) |
| **3.0 m/s** | `configs/q4_mobility_512_sumo_3_LB.yml` | Bicycle / jogger velocity (~3.0 m/s) |
| **5.0 m/s** | `configs/q4_mobility_512_sumo_5_LB.yml` | Urban transit / cycling velocity (~5.0 m/s) |
| **10.0 m/s** | `configs/q4_mobility_512_sumo_10_LB.yml` | Vehicular road speed (~10.0 m/s) |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make q4a
```

### Run from this Directory:
```bash
make
# or
make q4a
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_q4_mobility_ccs.pdf`
- **Visualization Script**: `python3 plot/q4_mobility.py`
