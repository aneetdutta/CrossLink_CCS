.PHONY: all install clean smoke-test smoke_test mobility_data validate_real_world help

SHELL := /usr/bin/env bash
CONFIG ?= scenario_result_512_sumo_all.yml
SMOKE_CONFIG = scenario_test_32_sumo_smoke.yml
SMOKE_SCENARIO := $(basename $(notdir $(SMOKE_CONFIG)))
CONFIG_SCENARIO := $(basename $(notdir $(CONFIG)))

all: help

help:
	@echo "CrossLink Makefile Targets:"
	@echo "  make install             - Run install.sh to setup environment, Rust binaries, and Python virtual environment"
	@echo "  make clean               - Clean Python bytecode, caches, Rust target binaries, and output logs"
	@echo "  make mobility_data       - Generate SUMO mobility traces (default CONFIG=$(CONFIG))"
	@echo "  make smoke_test [<task>] - Run smoke test (optionally resuming from <task> or stage number)"
	@echo "  make validate_real_world - Run empirical evaluation on 12 commodity real-world devices"

install:
	@chmod +x install.sh
	@./install.sh

clean:
	@echo "Cleaning Python bytecode and cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache .ruff_cache
	@echo "Cleaning Rust build artifacts..."
	@(cd rust_code && cargo clean && cd ..) || true
	@echo "Cleaning temporary logs and data files..."
	@rm -rf logs/*.log output/data/*.csv

mobility_data:
	@echo "Generating SUMO Mobility Data for config: $(SMOKE_CONFIG)..."
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t sumo && T2=$$(date +%s) && echo "Time elapsed: $$(($$T2-$$T1))s"
	@echo "SUMO Mobility Data generation completed."
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_polygon && T2=$$(date +%s) && echo "Time elapsed: $$(($$T2-$$T1))s"
	@echo "SUMO Mobility Data filtered inside polygon."
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_RI_Count && T2=$$(date +%s) && echo "Time elapsed: $$(($$T2-$$T1))s"
	@echo "SUMO Mobility Data Generation Completed."

# Allow restarting smoke_test from a specific task/stage: make smoke_test <task>
ifneq ($(filter smoke_test smoke-test,$(firstword $(MAKECMDGOALS))),)
  SMOKE_START := $(word 2,$(MAKECMDGOALS))
  ifneq ($(SMOKE_START),)
    $(eval $(SMOKE_START):;@:)
  endif
endif

START ?= $(SMOKE_START)

smoke-test: smoke_test
smoke_test:
	@echo "======================================================================"
	@echo "Starting End-to-End 32-User Smoke Test Verification Pipeline"
	
	python3 main.py -c $(SMOKE_CONFIG) -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- $(SMOKE_SCENARIO) generate_sniffer_data && cd .."; \
	
	python3 main.py -c $(SMOKE_CONFIG) -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- $(SMOKE_SCENARIO) inter_map && cd .."; 
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- $(SMOKE_SCENARIO) intra_map && cd .."; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t refine_intramap; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t intra_filter; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t reconstruction; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t plot; 
	
	@echo "======================================================================"
	@echo "✅ Smoke Test Pipeline Finished"
	@echo "Output saved in /output/data/$(SMOKE_SCENARIO)/*.csv"
	@echo "Plot saved in /output/images/privacy_leakage_$(SMOKE_SCENARIO).pdf" 

	@echo "======================================================================"

validate_real_world:
	@echo "Running real-world device empirical validation..."
	@source .venv/bin/activate && cd real_world && python3 crosslink.py && python3 evaluate.py && python3 plot_results.py
	@echo "Real-world empirical validation completed successfully."
        
baseline:
	@echo "Running Baseline Scenario with 512 users in Full Coverage"
	
	python3 main.py -c scenario_result_512_sumo_all1.yml -t sumo; \
	python3 main.py -c scenario_result_512_sumo_all1.yml -t filter_users_polygon; \
	python3 main.py -c scenario_result_512_sumo_all1.yml -t filter_users_RI_Count; \
	python3 main.py -c scenario_result_512_sumo_all1.yml -t generate_user_data; \
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_all1 generate_sniffer_data && cd .."; \
	python3 main.py -c scenario_result_512_sumo_all1.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_all1  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_all1 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all1.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_all1.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all1.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_all1.yml -t plot; \
	
	@echo "======================================================================"
	@echo "✅ Baseline Pipeline Finished"
	@echo "Output saved in /output/data/scenario_result_512_sumo_all1/*.csv"
	@echo "Plot saved in /output/images/privacy_leakage_scenario_result_512_sumo_all1.pdf"
	@echo "======================================================================"
	
	
q3:
	@echo "======================================================================"
	@echo "Running the experiments to answer research question 3:"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_all_512.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_all4_512.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_all5_512.csv"
	
	python3 main.py -c scenario_result_512_sumo_all.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_all generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_all  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_all intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_all.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all.yml -t reconstruction; \
	
	
	python3 main.py -c scenario_result_512_sumo_all4.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_all4 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all4.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_all4  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_all4 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all4.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_all4.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all4.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_all5.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_all5 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all5.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_all5  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_all5 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_all5.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_all5.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all5.yml -t reconstruction; \
	
	python3 plot/q3_m.py; \
	
	@echo "======================================================================"
	@echo "Q1 Finished"
	@echo "Output saved in /output/data/"
	@echo "Plot saved in /output/images/privacy_leakage_q3_512_ccs.pdf"
	@echo "Generated Figure 10 of the main paper"
	@echo "======================================================================"
				
				
q2_bounded_localization:
	@echo "Bounded Localization Error"
	
	
	
abalation_study:
	@echo "Running abalation study..."
	
	
	python3 main.py -c scenario_result_512_sumo_all_nom.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all_nom.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_all_nomloc.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all_nomloc.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_all_noloc.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_all_noloc.yml -t reconstruction; \
	
	python3 plot/plot_abalation_m.py; \
	
	@echo "======================================================================"
	@echo "Abalation study Finished"
	@echo "Output saved in /output/data/"
	@echo "Plot saved in /output/images/privacy_leakage_abalation_ccs_m.pdf"
	@echo "Generated Figure 3 of the main paper"
	@echo "======================================================================"
	
	
q1:
	@echo "======================================================================"
	@echo "Running the experiments to answer research question 1:"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_LW1_512.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_LB1_512.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_BW1_512.csv"
	
	python3 main.py -c scenario_result_512_sumo_LW1.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_LW1 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_LW1.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_LW1  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_LW1 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_LW1.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_LW1.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_LW1.yml -t reconstruction; \
	
	
	python3 main.py -c scenario_result_512_sumo_LB1.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_LB1 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_LB1.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_LB1  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_LB1 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_LB1.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_LB1.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_LB1.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_BW1.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_BW1 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_BW1.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_BW1  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_BW1 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_BW1.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_BW1.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_BW1.yml -t reconstruction; \
	
	python3 plot/plot_q1_m.py; \
	
	@echo "======================================================================"
	@echo "Q3 Finished"
	@echo "Output saved in /output/data/"
	@echo "Plot saved in /output/images/privacy_leakage_q3_512_ccs_m.pdf"
	@echo "Generated Figure 6 of the main paper"
	@echo "======================================================================"
	
	
q4_velocity:
	@echo "======================================================================"
	@echo "Running the experiments to answer research question 4 (velocity):"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_moving3.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_moving5.csv"
	
	bash -c "cp ./data/raw_user_data_scenario_result_512_sumo_all1_512.csv ./data/raw_user_data_scenario_result_512_sumo_moving10.csv"
	
	python3 main.py -c scenario_result_512_sumo_moving3.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_moving3 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving3.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_moving3  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_moving3 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving3.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_moving3.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_moving3.yml -t reconstruction; \
	
	
	python3 main.py -c scenario_result_512_sumo_moving5.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_moving5 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving5.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_moving5  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_moving5 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving5.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_moving5.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_moving5.yml -t reconstruction; \
	
	python3 main.py -c scenario_result_512_sumo_moving10.yml -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- scenario_result_512_sumo_moving10 generate_sniffer_data && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving10.yml -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- scenario_result_512_sumo_moving10  inter_map && cd .."; \
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- scenario_result_512_sumo_moving10 intra_map && cd .."; \
	
	python3 main.py -c scenario_result_512_sumo_moving10.yml -t refine_intramap; \
	
	python3 main.py -c scenario_result_512_sumo_moving10.yml -t intra_filter; \
	
	python3 main.py -c scenario_result_512_sumo_moving10.yml -t reconstruction; \
	
	python3 plot/plot_q1_m.py; \
	
	@echo "======================================================================"
	@echo "Q4 Velocity Finished"
	@echo "Output saved in /output/data/"
	@echo "Plot saved in /output/images/privacy_leakage_q4_mobility_ccs_m"
	@echo "Generated Figure 11 (a) of the main paper"
	@echo "======================================================================"




    
