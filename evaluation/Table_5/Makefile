# Makefile for Table 5 Evaluation
SHELL := /usr/bin/env bash
ROOT_DIR := $(abspath ../..)

.PHONY: all run t5 plot clean help

all: t5

help:
	@echo "Evaluation targets for Table 5:"
	@echo "  make t5   - Run evaluation pipeline for Table 5"
	@echo "  make plot  - Generate visualization figures"

t5:
	@echo "==> Running Table 5 evaluation pipeline from root repository..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 target_privacy_scores.py

plot:
	@echo "==> Generating evaluation plot figure..."
	@cd $(ROOT_DIR) && source .venv/bin/activate 2>/dev/null || true; python3 target_privacy_scores.py

clean:
	@echo "==> Cleaning local temporary files..."
	@rm -rf *.log *.tmp
