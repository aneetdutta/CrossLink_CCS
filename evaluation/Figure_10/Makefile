# Makefile for Figure 10 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q3 plot clean help

all: q3

help:
	@echo "Evaluation targets for Figure 10:"
	@echo "  make q3   - Run evaluation pipeline for Figure 10"
	@echo "  make plot  - Generate visualization figures"

q3:
	@echo "==> Running Figure 10 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q3_partial.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q3_partial.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
