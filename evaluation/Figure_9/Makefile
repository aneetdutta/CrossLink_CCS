# Makefile for Figure 9 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q2_loc plot clean help

all: q2_loc

help:
	@echo "Evaluation targets for Figure 9:"
	@echo "  make q2_loc   - Run evaluation pipeline for Figure 9"
	@echo "  make plot  - Generate visualization figures"

q2_loc:
	@echo "==> Running Figure 9 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q3_localization.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q3_localization.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
