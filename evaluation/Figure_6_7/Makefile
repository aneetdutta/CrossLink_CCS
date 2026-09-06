# Makefile for Figure 6 & 7 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run q1 plot clean help

all: q1

help:
	@echo "Evaluation targets for Figure 6 & 7:"
	@echo "  make q1   - Run evaluation pipeline for Figure 6 & 7"
	@echo "  make plot  - Generate visualization figures"

q1:
	@echo "==> Running Figure 6 & 7 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_q1.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 plot/plot_q1.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
