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
	@source .venv/bin/activate && T1=$$(date +%s) && python3 main.py -c $(SMOKE_CONFIG) -t sumo && T2=$$(date +%s) && echo "⏱ Stage Time: $$(($$T2-$$T1))s"
	@echo "SUMO Mobility Data generation completed."

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
	@if [ -n "$(START)" ]; then \
		echo "🔄 Resuming execution from task / stage: $(START)"; \
	fi
	@echo "======================================================================"
	@source .venv/bin/activate && python3 -c 'import time; open("/tmp/crosslink_start.txt","w").write(str(time.time()))'
	@source .venv/bin/activate && \
	START_TASK="$(START)"; \
	ONLY="$(ONLY)"; \
	SKIPPING=0; \
	[ -n "$$START_TASK" ] && SKIPPING=1; \
	run_stage() { \
		local num="$$1"; \
		local title="$$2"; \
		local aliases="$$3"; \
		shift 3; \
		if [ "$$SKIPPING" = "1" ]; then \
			local match=0; \
			for a in $$num $$aliases; do \
				if [ "$$a" = "$$START_TASK" ]; then match=1; break; fi; \
			done; \
			if [ "$$match" = "1" ]; then \
				SKIPPING=0; \
			else \
				return 0; \
			fi; \
		fi; \
		echo ""; \
		echo "----------------------------------------------------------------------"; \
		echo "▶ [Stage $$num/10] $$title"; \
		local t1=$$(date +%s); \
		"$$@"; \
		local rc=$$?; \
		local t2=$$(date +%s); \
		if [ $$rc -ne 0 ]; then \
			echo "❌ Stage $$num ($$title) failed with exit code $$rc"; \
			exit $$rc; \
		fi; \
		echo "⏱ Stage Time: $$((t2-t1))s"; \
		if [ -n "$$ONLY" ]; then \
			echo "ℹ️ Ran single task ($$title). Exiting."; \
			exit 0; \
		fi; \
	}; \
	run_stage 0 "Preparing Scenario Data" "prep prepare scenario_data" \
		cp -f data/raw_user_data_$(CONFIG_SCENARIO).csv data/raw_user_data_$(SMOKE_SCENARIO).csv; \
	run_stage 1 "Mobility Filtering (Polygon)" "filter_users_polygon mobility_filtering filter" \
		python3 main.py -c $(SMOKE_CONFIG) -t filter_users_polygon; \
	run_stage 1 "Mobility Filtering (RI Count)" "filter_users_RI_Count filter_users_ri_count" \
		python3 main.py -c $(SMOKE_CONFIG) -t filter_users_RI_Count; \
	run_stage 2 "User Data Generation" "generate_user_data user_data" \
		python3 main.py -c $(SMOKE_CONFIG) -t generate_user_data; \
	run_stage 3 "Sniffer Data Generation" "generate_sniffer_data sniffer_data" \
		bash -c "cd rust_code && cargo run --release -- $(SMOKE_SCENARIO) generate_sniffer_data && cd .."; \
	run_stage 4 "Aggregation" "aggregate_new aggregate" \
		python3 main.py -c $(SMOKE_CONFIG) -t aggregate_new; \
	run_stage 5 "Inter-Protocol Mapping" "inter_map inter" \
		bash -c "cd rust_code && cargo run --release --features inter_map_disable_trim -- $(SMOKE_SCENARIO) inter_map && cd .."; \
	run_stage 6 "Intra-Protocol Mapping" "intra_map intra" \
		bash -c "cd rust_code && cargo run --release --features intra_map_disable_trim -- $(SMOKE_SCENARIO) intra_map && cd .."; \
	run_stage 7 "Refinement" "refine_intramap refine" \
		python3 main.py -c $(SMOKE_CONFIG) -t refine_intramap; \
	run_stage 8 "Filtering" "intra_filter" \
		python3 main.py -c $(SMOKE_CONFIG) -t intra_filter; \
	run_stage 9 "Reconstruction" "reconstruction recon" \
		python3 main.py -c $(SMOKE_CONFIG) -t reconstruction; \
	run_stage 10 "Result Visualization" "plot visualization" \
		python3 main.py -c $(SMOKE_CONFIG) -t plot; \
	if [ "$$SKIPPING" = "1" ]; then \
		echo "❌ Error: Unrecognized task or stage '$$START_TASK'."; \
		echo "Available tasks / stages to restart from:"; \
		echo "  0 or prep                   - Preparing Scenario Data"; \
		echo "  1 or filter_users_polygon   - Mobility Filtering (Polygon)"; \
		echo "       filter_users_RI_Count  - Mobility Filtering (RI Count)"; \
		echo "  2 or generate_user_data     - User Data Generation"; \
		echo "  3 or generate_sniffer_data  - Sniffer Data Generation"; \
		echo "  4 or aggregate_new          - Aggregation"; \
		echo "  5 or inter_map              - Inter-Protocol Mapping"; \
		echo "  6 or intra_map              - Intra-Protocol Mapping"; \
		echo "  7 or refine_intramap        - Refinement"; \
		echo "  8 or intra_filter           - Filtering"; \
		echo "  9 or reconstruction         - Reconstruction"; \
		echo "  10 or plot                  - Result Visualization"; \
		exit 1; \
	fi
	@echo ""
	@echo "======================================================================"
	@source .venv/bin/activate && python3 -c 'import time; t0=float(open("/tmp/crosslink_start.txt").read()); print(f"✅ Smoke Test Pipeline Finished in {time.time()-t0:.2f}s!")'
	@echo "======================================================================"

validate_real_world:
	@echo "Running real-world device empirical validation..."
	@source .venv/bin/activate && cd real_world && python3 crosslink.py && python3 evaluate.py && python3 plot_results.py
	@echo "Real-world empirical validation completed successfully."
