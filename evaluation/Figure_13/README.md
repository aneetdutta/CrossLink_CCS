# Figure 13: Countermeasures Evaluation

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 13** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 13
- **Evaluation Scenario**: Countermeasures

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **No sync (baseline)** | `configs/scenario_result_512_sumo_all.yml` | Standard unsynchronized identifier rotation |
| **Sync 180 s** | `configs/scenario_synced_randomization_512_LB.yml` | Synchronized identifier rotation with 180s interval |
| **Sync 600 s** | `configs/scenario_synced_randomization_512_all.yml` | Synchronized identifier rotation with 600s interval |
| **Perfect mixing** | `configs/scenario_proximity_512_sumo_all.yml` | Simulated perfect spatiotemporal mix-zone behavior |
| **Sync** | `configs/synchronized_low_ti.yml` | Synchronized rotation protocol evaluation |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make cm
```

### Run from this Directory:
```bash
make
# or
make cm
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_scenario_synced_randomization_512_LB.pdf`
- **Visualization Script**: `python3 plot/countermeasure.py`
