# Makefile for Figure 3 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run ablation plot clean help

all: ablation

help:
	@echo "Evaluation targets for Figure 3:"
	@echo "  make ablation   - Run evaluation pipeline for Figure 3"
	@echo "  make plot  - Generate visualization figures"

ablation:
	@echo "==> Running Figure 3 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_abalation.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_abalation.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
