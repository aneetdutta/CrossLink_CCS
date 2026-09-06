# Makefile for Figure 12 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run eg_scen plot clean help

all: eg_scen

help:
	@echo "Evaluation targets for Figure 12:"
	@echo "  make eg_scen   - Run evaluation pipeline for Figure 12"
	@echo "  make plot  - Generate visualization figures"

eg_scen:
	@echo "==> Running Figure 12 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_targeted.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_targeted.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
