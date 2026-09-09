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
	@rm -rf data/*.csv logs/*.log output/data/*.csv

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
	@echo "🚀 Starting End-to-End 32-User Smoke Test Verification Pipeline"
	
	python3 main.py -c $(SMOKE_CONFIG) -t generate_user_data; \
	
	bash -c "cd rust_code && cargo run --release -- $(SMOKE_SCENARIO) generate_sniffer_data && cd .."; \
	
	python3 main.py -c $(SMOKE_CONFIG) -t aggregate_new; \
	
	bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- $(SMOKE_SCENARIO) inter_map && cd .."; 
	
	bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- $(SMOKE_SCENARIO) intra_map && cd .."; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t refine_intramap; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t intra_filter; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t reconstruction; 
	
	python3 main.py -c $(SMOKE_CONFIG) -t plot; \
	
	@echo ""
	@echo "======================================================================"
	@source .venv/bin/activate && python3 -c 'import time; t0=float(open("/tmp/crosslink_start.txt").read()); print(f"✅ Smoke Test Pipeline Finished in {time.time()-t0:.2f}s!")'
	@echo "Output saved in /output/data/$(SMOKE_SCENARIO)/*.csv"
	@echo "Plot saved in /output/images/$(SMOKE_SCENARIO).pdf" 

	@echo "======================================================================"

validate_real_world:
	@echo "Running real-world device empirical validation..."
	@source .venv/bin/activate && cd real_world && python3 crosslink.py && python3 evaluate.py && python3 plot_results.py
	@echo "Real-world empirical validation completed successfully."
	
abalation_study:
	@echo "Running abalation study..."
    
