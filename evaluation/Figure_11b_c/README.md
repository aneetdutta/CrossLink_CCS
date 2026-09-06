# Figure 11(b & c): Question 4 (Q4) - User Density & Mix-Zone Duration

This directory contains reproduction instructions, scenario profiles, and execution targets for **Figure 11(b & c)** of the CrossLink paper.

---

## 📖 Scenario Overview

- **Paper Reference**: Figure 11(b & c)
- **Evaluation Scenario**: Q4: User density & Q4: Mix-zone duration

This evaluation investigates tracking reconstruction performance and privacy leakage bounds under the corresponding experimental configurations.

---

## ⚙️ Configurations

| Configuration | Profile File | Description |
| :--- | :--- | :--- |
| **N=512** | `configs/scenario_exponential_512_sumo_LB.yml` | Device population density N=512 |
| **N=1024** | `configs/scenario_exponential_1024_sumo_LB.yml` | Device population density N=1024 |
| **N=1536** | `configs/scenario_exponential_1536_sumo_LB.yml` | Device population density N=1536 |
| **SUMO Synthetic** | `configs/scenario_exponential_512_graph_LB.yml` | Synthetic network topology graph baseline |

---

## 🚀 Execution & Reproduction Commands

### Run from Root Repository:
```bash
make_q4_b_c
```
```bash
make q4_user_den
```
```bash
make q4_mix_dur
```

### Run from this Directory:
```bash
make
# or
make q4_b_c
```

---

## 📊 Target Outputs & Plots

- **Target Output Figure / Dataset**: `output/images/privacy_leakage_q4_density.pdf, output/images/privacy_leakage_q4_mix1.pdf`
- **Visualization Script**: `python3 plot/q4_density_graph.py && python3 plot/q4_mix.py`
