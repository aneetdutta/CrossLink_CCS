# Makefile for Figure 11(a) Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q4a plot clean help

all: q4a

help:
	@echo "Evaluation targets for Figure 11(a):"
	@echo "  make q4a   - Run evaluation pipeline for Figure 11(a)"
	@echo "  make plot  - Generate visualization figures"

q4a:
	@echo "==> Running Figure 11(a) evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q4_mobility.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q4_mobility.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
