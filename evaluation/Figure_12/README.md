# Figure 12: Example Scenario - Tracking Duration

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 12** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 12
- **Evaluation Scenario**: Example scenario: Tracking duration

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Full coverage** | `configs/scenario_result_512_sumo_all.yml` | Continuous coverage tracking duration |
| **MOB** | `configs/scenario_sumo_512_sumo_homob.yml` | Tracking duration under mobile sniffing nodes |
| **PATCH** | `configs/scenario_sumo_512_sumo_hopatch.yml` | Tracking duration across spatial patches |
| **RAND** | `configs/scenario_sumo_512_sumo_horand.yml` | Tracking duration under randomized placement |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make eg_scen
```

### Run from this Directory:
```bash
make
# or
make eg_scen
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_targeted_ccs.pdf`
- **Visualization Script**: `python3 plot/plot_targeted.py`
