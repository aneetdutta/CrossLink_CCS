.PHONY: all install clean smoke-test smoke_test mobility_data validate_real_world help

SHELL := /usr/bin/env bash
CONFIG ?= scenario_result_512_sumo_all.yml
SMOKE_CONFIG ?= scenario_test_32_sumo_smoke.yml
SMOKE_SCENARIO := $(basename $(notdir $(SMOKE_CONFIG)))
CONFIG_SCENARIO := $(basename $(notdir $(CONFIG)))

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
	@echo "Generating SUMO Mobility Data for config: $(SMOKE_CONFIG)..."
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t sumo && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo "SUMO Mobility Data generation completed."

smoke_test:
	@echo "======================================================================"
	@echo "🚀 Starting End-to-End 32-User Smoke Test Verification Pipeline"
	@echo "======================================================================"
	@source .venv/bin/activate && python3 -c 'import time; open("/tmp/crosslink_start.txt","w").write(str(time.time()))'
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 0/10] Preparing Scenario Data"
	@echo "Copying data/raw_user_data_$(CONFIG_SCENARIO).csv -> data/raw_user_data_$(SMOKE_SCENARIO).csv..."
	@cp -f data/raw_user_data_$(CONFIG_SCENARIO).csv data/raw_user_data_$(SMOKE_SCENARIO).csv
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 1/10] Mobility Filtering"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_polygon && python3 main.py -c $(SMOKE_CONFIG) -t filter_users_RI_Count && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 2/10] User Data Generation"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t generate_user_data && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s" && echo "📊 Dataset Files: $$(ls -1 output/data/$(SMOKE_SCENARIO)*/*.csv 2>/dev/null | wc -l)"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 3/10] Sniffer Data Generation"
	@source .venv/bin/activate && T1=$$(date +%s) && cargo run --release -- $(SMOKE_SCENARIO) generate_sniffer_data && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 4/10] Aggregation"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t aggregate_new && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 5/10] Inter-Protocol Mapping"
	@source .venv/bin/activate && T1=$$(date +%s) && cargo run --release --features inter_map_disable_trim -- $(SMOKE_SCENARIO) inter_map && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 6/10] Intra-Protocol Mapping"
	@source .venv/bin/activate && T1=$$(date +%s) && cargo run --release --features intra_map_disable_trim -- $(SMOKE_SCENARIO) intra_map && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 7/10] Refinement"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t refine_intramap && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 8/10] Filtering"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t intra_filter && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 9/10] Reconstruction"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t reconstruction && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s" && python3 -c "import pandas as pd; df=pd.read_csv('output/data/$(SMOKE_SCENARIO)_all/multi_protocol_$(SMOKE_SCENARIO)_all.csv'); print(f'📊 Reconstructed Users: {len(df)} | Mean Privacy Leakage: {df[\"privacy_score\"].mean():.4f}')" 2>/dev/null || true
	@echo ""
	@echo "----------------------------------------------------------------------"
	@echo "▶ [Stage 10/10] Result Visualization"
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t plot && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s" && echo "📊 Generated PDF Figure: $$(ls -h output/images/privacy_leakage_*.pdf 2>/dev/null | head -n 1)"
	@echo ""
	@echo "======================================================================"
	@source .venv/bin/activate && python3 -c 'import time; t0=float(open("/tmp/crosslink_start.txt").read()); print(f"✅ Smoke Test Completed Successfully in {time.time()-t0:.2f}s!")'
	@echo "======================================================================"

validate_real_world:
	@echo "Running real-world device empirical validation..."
	@source .venv/bin/activate && cd real_world && python3 crosslink.py && python3 evaluate.py && python3 plot_results.py
	@echo "Real-world empirical validation completed successfully."
