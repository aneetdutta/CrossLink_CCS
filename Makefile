.PHONY: all install clean smoke-test smoke_test mobility_data validate_real_world help

SHELL := /usr/bin/env bash
CONFIG ?= scenario_result_512_sumo_all.yml
SMOKE_CONFIG ?= scenario_test_32_sumo_smoke.yml
SMOKE_SCENARIO := scenario_test_32_sumo_smoke

all: help

help:
	@echo "CrossLink Makefile Targets:"
	@echo "  make install             - Run install.sh to setup environment, Rust binaries, and Python virtual environment"
	@echo "  make clean               - Clean Python bytecode, caches, Rust target binaries, and output logs"
	@echo "  make mobility_data       - Generate SUMO mobility traces (default CONFIG=$(CONFIG))"
	@echo "  make smoke_test          - Run complete end-to-end 32-user smoke test simulation"
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
	@cargo clean || true
	@echo "Cleaning temporary logs and data files..."
	@rm -rf data/*.csv logs/*.log output/data/*.csv

mobility_data:
	@echo "Generating SUMO mobility traces for config: $(CONFIG)..."
	@source .venv/bin/activate && python3 main.py -c $(CONFIG) -t sumo
	@source .venv/bin/activate && python3 main.py -c $(CONFIG) -t filter_users_polygon
	@source .venv/bin/activate && python3 main.py -c $(CONFIG) -t filter_users_RI_Count
	@echo "SUMO user mobility data generation completed."

smoke_test:
	@echo "Running end-to-end 32-user smoke test..."
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_polygon
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_RI_Count
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t generate_user_data
	@source .venv/bin/activate && cargo run --release -- $(SMOKE_SCENARIO) generate_sniffer_data
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t aggregate_new
	@source .venv/bin/activate && cargo run --release --features inter_map_disable_trim -- $(SMOKE_SCENARIO) inter_map
	@source .venv/bin/activate && cargo run --release --features intra_map_disable_trim -- $(SMOKE_SCENARIO) intra_map
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t refine_intramap
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t intra_filter
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t reconstruction
	@source .venv/bin/activate && python3 main.py -c $(SMOKE_CONFIG) -t plot
	@echo "Smoke test completed successfully."

validate_real_world:
	@echo "Running real-world device empirical validation..."
	@source .venv/bin/activate && cd real_world && python3 crosslink.py && python3 evaluate.py
	@echo "Real-world empirical validation completed successfully."
