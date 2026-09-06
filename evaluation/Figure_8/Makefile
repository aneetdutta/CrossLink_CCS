# Makefile for Figure 8 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q2 plot clean help

all: q2

help:
	@echo "Evaluation targets for Figure 8:"
	@echo "  make q2   - Run evaluation pipeline for Figure 8"
	@echo "  make plot  - Generate visualization figures"

q2:
	@echo "==> Running Figure 8 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q2.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/q2.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
