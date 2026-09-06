# Makefile for Figure 11(b & c) Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q4_b_c plot clean help

all: q4_b_c

help:
	@echo "Evaluation targets for Figure 11(b & c):"
	@echo "  make q4_b_c   - Run evaluation pipeline for Figure 11(b & c)"
	@echo "  make plot  - Generate visualization figures"

q4_b_c:
	@echo "==> Running Figure 11(b & c) evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q4_density_graph.py && python3 plot/q4_mix.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q4_density_graph.py && python3 plot/q4_mix.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
