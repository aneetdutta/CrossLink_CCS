# Figure 3: Ablation Studies

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 3** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 3
- **Evaluation Scenario**: Ablation Studies

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **Baseline** | `configs/scenario_result_512_sumo_all.yml` | Full CrossLink pipeline with spatiotemporal uncertainty modeling |
| **No_Loc** | `configs/scenario_result_512_sumo_all_noloc.yml` | CrossLink without localization uncertainty modeling |
| **Nom_Loc** | `configs/scenario_result_512_sumo_all_nomloc.yml` | No mobility and no localization uncertainty modeling |
| **Nom** | `configs/scenario_result_512_sumo_all_nom.yml` | CrossLink without mobility trajectory modeling |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make ablation
```

### Run from this Directory:
```bash
make
# or
make ablation
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_scenario_result_512_sumo_all_nomloc.pdf`
- **Visualization Script**: `python3 plot/plot_abalation.py`
