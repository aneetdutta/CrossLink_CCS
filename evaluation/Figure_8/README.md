# Figure 8: Question 2 (Q2a & Q2b) - Partial Sniffer Coverage

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 8** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 8
- **Evaluation Scenario**: Q2 a & Q2 b (Partial Coverage)

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Full Coverage (Baseline)** | `configs/scenario_result_512_sumo_all.yml` | 100% sniffer coverage across simulation area |
| **PATCH** | `configs/scenario_partial_512_sumo_LB.yml` | Patch deployment (clustered sniffer placement) |
| **MOB SPOT** | `configs/scenario_sumo_512_sumo_homob.yml` | Mobile sniffing nodes moving within network |
| **RAND** | `configs/scenario_sumo_512_sumo_horand.yml` | Randomized uniform sniffer placement |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make q2
```
```bash
make q2a
```
```bash
make q2b
```

### Run from this Directory:
```bash
make
# or
make q2
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_q2_512.pdf`
- **Visualization Script**: `python3 plot/q2.py`
