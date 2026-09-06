# Table 5: Effect of Error-Tolerance Choices

This directory contains reproduction instructions, scenario profiles, and execution targets for **Table 5** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Table 5
- **Evaluation Scenario**: Effect of error-tolerance choices

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Bounded (Baseline)** | `configs/scenario_result_512_sumo_all.yml` | Bounded localization error tolerance threshold |
| **Heavy-tail (baseline error tolerance)** | `configs/scenario_result_512_sumo_low.yml` | Heavy-tailed distribution with baseline error tolerance |
| **Heavy-tail (increased error tolerance)** | `configs/scenario_result_512_sumo_high.yml` | Heavy-tailed distribution with increased tolerance threshold |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make t5
```

### Run from this Directory:
```bash
make
# or
make t5
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/data/table_5_results.csv`
- **Visualization Script**: `python3 target_privacy_scores.py`
