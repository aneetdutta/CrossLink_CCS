# Figure 9: Question 2 (Q2) - Different Bounded Localization Errors

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 9** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 9
- **Evaluation Scenario**: Q2: Different bounded localization errors

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Low** | `configs/scenario_result_512_sumo_low.yml` | Low spatial localization error bounds |
| **Baseline** | `configs/scenario_result_512_sumo_all.yml` | Standard empirical localization error bounds |
| **High** | `configs/scenario_result_512_sumo_high.yml` | High spatial localization error bounds |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make q2_loc
```

### Run from this Directory:
```bash
make
# or
make q2_loc
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_q3_localization.pdf`
- **Visualization Script**: `python3 plot/q3_localization.py`
