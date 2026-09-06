# Makefile for Figure 13 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run cm plot clean help

all: cm

help:
	@echo "Evaluation targets for Figure 13:"
	@echo "  make cm   - Run evaluation pipeline for Figure 13"
	@echo "  make plot  - Generate visualization figures"

cm:
	@echo "==> Running Figure 13 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/countermeasure.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/countermeasure.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
