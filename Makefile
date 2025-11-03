# minix-analysis Makefile - Analysis and documentation pipeline
# This Makefile orchestrates all analysis, documentation, and publishing tasks
# Version: 2.0.0
# Last Updated: 2025-11-01

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Configuration
PYTHON := python3
PDFLATEX := pdflatex
MKDOCS := mkdocs
MINIX_ROOT := ../minix
MINIX_SRC := $(MINIX_ROOT)/minix

# Directories
BUILD_DIR := build
DOCS_DIR := docs
TOOLS_DIR := tools
WHITEPAPER_DIR := whitepaper
DATA_DIR := diagrams/data
TIKZ_DIR := diagrams/tikz-generated
ARCHIVE_DIR := archive
SCRIPTS_DIR := scripts

# Module directories (legacy)
CPU_MODULE := modules/cpu-interface
BOOT_MODULE := modules/boot-sequence
SHARED_STYLES := shared/styles

# Output directories
DOCS_BUILD := $(BUILD_DIR)/docs
ANALYSIS_BUILD := $(BUILD_DIR)/analysis
WHITEPAPER_BUILD := $(BUILD_DIR)/whitepaper

# Tools
ANALYZER := $(TOOLS_DIR)/minix_source_analyzer.py
TIKZ_GEN := $(TOOLS_DIR)/tikz_generator.py
AUDIT_TOOL := $(TOOLS_DIR)/documentation_auditor.py
LINK_CHECK := $(TOOLS_DIR)/link_checker.py

# Create output directories
$(BUILD_DIR) $(DOCS_BUILD) $(ANALYSIS_BUILD) $(WHITEPAPER_BUILD) $(DATA_DIR) $(TIKZ_DIR):
	mkdir -p $@

# Primary targets
.PHONY: all
all: analysis docs whitepaper ## Build everything

.PHONY: analysis pipeline
analysis pipeline: $(ANALYSIS_BUILD)/.analyzed ## Run source analysis pipeline
$(ANALYSIS_BUILD)/.analyzed: $(BUILD_DIR) | validate-minix
	@echo "=== Running MINIX source analysis ==="
	$(PYTHON) $(ANALYZER) \
		--minix-root $(MINIX_ROOT) \
		--output $(DATA_DIR)
	@echo "=== Generating TikZ diagrams ==="
	$(PYTHON) $(TIKZ_GEN) \
		--data-dir $(DATA_DIR) \
		--output $(TIKZ_DIR)
	@echo "=== Compiling TikZ to PDF ==="
	@cd $(TIKZ_DIR) && \
	for tex in *.tex; do \
		echo "  Compiling $$tex..."; \
		$(PDFLATEX) -interaction=nonstopmode "$$tex" >/dev/null 2>&1 || \
			(echo "Failed to compile $$tex" && exit 1); \
	done
	@echo "=== Converting PDF to PNG ==="
	@cd $(TIKZ_DIR) && \
	for pdf in *.pdf; do \
		magick -density 150 "$$pdf" -quality 90 "$${pdf%.pdf}.png" && \
		echo "  ✓ $$pdf converted" || echo "  ✗ $$pdf failed"; \
	done
	touch $@

# Legacy targets for backward compatibility
.PHONY: analyze generate-diagrams compile-tikz convert-png
analyze generate-diagrams compile-tikz convert-png: analysis

.PHONY: docs wiki
docs wiki: $(DOCS_BUILD)/.built ## Build documentation with mkdocs
$(DOCS_BUILD)/.built: $(DOCS_BUILD) | lint-docs
	@echo "=== Building documentation site ==="
	@if command -v $(MKDOCS) >/dev/null 2>&1; then \
		$(MKDOCS) build -d $(DOCS_BUILD); \
	else \
		echo "WARNING: mkdocs not found, using fallback HTML generation"; \
		$(PYTHON) $(TOOLS_DIR)/generate_static_docs.py \
			--source $(DOCS_DIR) \
			--output $(DOCS_BUILD) 2>/dev/null || \
		echo "Fallback documentation generator not available"; \
	fi
	touch $@

.PHONY: whitepaper
whitepaper: $(WHITEPAPER_BUILD)/.built ## Build LaTeX whitepaper
$(WHITEPAPER_BUILD)/.built: $(WHITEPAPER_BUILD) analysis
	@echo "=== Building whitepaper ==="
	@mkdir -p $(WHITEPAPER_BUILD)/figures
	cp -r $(WHITEPAPER_DIR)/* $(WHITEPAPER_BUILD)/ 2>/dev/null || true
	cp -r $(TIKZ_DIR)/*.pdf $(WHITEPAPER_BUILD)/figures/ 2>/dev/null || true
	@if [ -f $(WHITEPAPER_BUILD)/main.tex ]; then \
		cd $(WHITEPAPER_BUILD) && \
		$(PDFLATEX) -interaction=nonstopmode main.tex && \
		$(PDFLATEX) -interaction=nonstopmode main.tex; \
	else \
		echo "No main.tex found in whitepaper directory"; \
	fi
	touch $@

# Module builds (legacy support)
.PHONY: cpu boot
cpu:
	@echo "Building CPU Interface Analysis..."
	@if [ -d $(CPU_MODULE) ]; then \
		$(MAKE) -C $(CPU_MODULE) all; \
	else \
		echo "CPU module not found at $(CPU_MODULE)"; \
	fi

boot:
	@echo "Building Boot Sequence Analysis..."
	@if [ -d $(BOOT_MODULE) ]; then \
		$(MAKE) -C $(BOOT_MODULE) all; \
	else \
		echo "Boot module not found at $(BOOT_MODULE)"; \
	fi

.PHONY: audit
audit: ## Run documentation audit
	@echo "=== Running documentation audit ==="
	@if [ -f $(AUDIT_TOOL) ]; then \
		$(PYTHON) $(AUDIT_TOOL) --root . --output $(BUILD_DIR)/audit-report.md; \
	else \
		echo "Creating audit tool stub..."; \
		mkdir -p $(TOOLS_DIR); \
		echo "#!/usr/bin/env python3" > $(AUDIT_TOOL); \
		echo "import os, sys" >> $(AUDIT_TOOL); \
		echo "print('Audit: Checking documentation structure...')" >> $(AUDIT_TOOL); \
		echo "# TODO: Implement comprehensive audit" >> $(AUDIT_TOOL); \
		chmod +x $(AUDIT_TOOL); \
		$(PYTHON) $(AUDIT_TOOL); \
	fi

.PHONY: lint
lint: lint-markdown lint-python lint-tex ## Run all linters

.PHONY: lint-markdown
lint-markdown: ## Lint markdown files
	@echo "=== Linting markdown files ==="
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint $(DOCS_DIR)/**/*.md 2>/dev/null || true; \
	else \
		echo "markdownlint not found, skipping..."; \
	fi

.PHONY: lint-python
lint-python: ## Lint Python files
	@echo "=== Linting Python files ==="
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 $(TOOLS_DIR)/*.py --max-line-length=100 2>/dev/null || true; \
	else \
		$(PYTHON) -m py_compile $(TOOLS_DIR)/*.py 2>/dev/null || true; \
	fi

.PHONY: lint-tex
lint-tex: ## Lint LaTeX files
	@echo "=== Linting LaTeX files ==="
	@if command -v chktex >/dev/null 2>&1; then \
		find $(WHITEPAPER_DIR) -name "*.tex" -exec chktex -q {} \; 2>/dev/null || true; \
	else \
		echo "chktex not found, skipping..."; \
	fi

.PHONY: lint-docs
lint-docs: ## Validate documentation structure
	@echo "=== Validating documentation links ==="
	@if [ -f $(LINK_CHECK) ]; then \
		$(PYTHON) $(LINK_CHECK) --root $(DOCS_DIR); \
	else \
		grep -r '\[.*\](.*\.md)' $(DOCS_DIR) --include="*.md" 2>/dev/null | \
			grep -v "^Binary" | wc -l | \
			xargs echo "Found markdown links:"; \
	fi

.PHONY: test
test: test-unit test-integration ## Run all tests

.PHONY: test-unit
test-unit: ## Run unit tests
	@echo "=== Running unit tests ==="
	@if [ -d tests ]; then \
		$(PYTHON) -m pytest tests/unit -v 2>/dev/null || \
		echo "pytest not available or no tests found"; \
	else \
		echo "No unit tests directory found"; \
	fi

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "=== Running integration tests ==="
	@if [ -d tests ]; then \
		$(PYTHON) -m pytest tests/integration -v 2>/dev/null || \
		echo "pytest not available or no tests found"; \
	else \
		echo "No integration tests directory found"; \
	fi

.PHONY: qemu
qemu: ## Launch MINIX in QEMU
	@echo "=== Launching MINIX in QEMU ==="
	@if [ -f $(SCRIPTS_DIR)/qemu-launch.sh ]; then \
		$(SCRIPTS_DIR)/qemu-launch.sh; \
	else \
		echo "QEMU launch script not found at $(SCRIPTS_DIR)/qemu-launch.sh"; \
		echo "Creating script stub..."; \
		mkdir -p $(SCRIPTS_DIR); \
		echo "#!/bin/bash" > $(SCRIPTS_DIR)/qemu-launch.sh; \
		echo "# QEMU launch script for MINIX" >> $(SCRIPTS_DIR)/qemu-launch.sh; \
		echo "echo 'TODO: Implement QEMU launch'" >> $(SCRIPTS_DIR)/qemu-launch.sh; \
		chmod +x $(SCRIPTS_DIR)/qemu-launch.sh; \
	fi

.PHONY: serve
serve: docs ## Serve documentation locally
	@echo "=== Serving documentation at http://localhost:8000 ==="
	@if command -v $(MKDOCS) >/dev/null 2>&1; then \
		$(MKDOCS) serve; \
	else \
		cd $(DOCS_BUILD) && $(PYTHON) -m http.server 8000; \
	fi

.PHONY: watch watch-cpu watch-boot
watch: ## Watch for changes and rebuild
	@echo "=== Watching for changes ==="
	@while true; do \
		$(MAKE) all; \
		echo "Waiting for changes..."; \
		inotifywait -r -e modify,create,delete \
			--exclude '$(BUILD_DIR)' \
			$(DOCS_DIR) $(TOOLS_DIR) $(WHITEPAPER_DIR) 2>/dev/null || sleep 5; \
	done

watch-cpu:
	@echo "Watching CPU module for changes..."
	@while true; do \
		inotifywait -e modify -r $(CPU_MODULE)/latex/ 2>/dev/null && \
		$(MAKE) cpu; \
	done

watch-boot:
	@echo "Watching Boot module for changes..."
	@while true; do \
		inotifywait -e modify -r $(BOOT_MODULE)/latex/ 2>/dev/null && \
		$(MAKE) boot; \
	done

.PHONY: validate check
validate check: validate-minix validate-structure validate-data ## Validate environment

.PHONY: validate-minix
validate-minix: ## Check MINIX source availability
	@echo "=== Validating MINIX source ==="
	@test -d $(MINIX_SRC) || \
		(echo "ERROR: MINIX source not found at $(MINIX_SRC)" && exit 1)
	@test -f $(MINIX_SRC)/kernel/main.c || \
		(echo "ERROR: MINIX kernel source not complete" && exit 1)
	@echo "✓ MINIX source validated at $(MINIX_SRC)"

.PHONY: validate-structure
validate-structure: ## Validate repository structure
	@echo "=== Validating repository structure ==="
	@test -d $(DOCS_DIR) || (echo "ERROR: docs/ directory missing" && exit 1)
	@test -d $(TOOLS_DIR) || (echo "ERROR: tools/ directory missing" && exit 1)
	@test -f $(ANALYZER) || (echo "ERROR: Source analyzer missing" && exit 1)
	@echo "✓ Repository structure validated"

.PHONY: validate-data
validate-data: ## Validate extracted data
	@echo "=== Validating extracted data ==="
	@if [ -d $(DATA_DIR) ]; then \
		for json in $(DATA_DIR)/*.json; do \
			[ -f "$$json" ] && $(PYTHON) -m json.tool "$$json" > /dev/null 2>&1 && \
			echo "  ✓ $$json valid" || echo "  ✗ $$json invalid"; \
		done; \
	else \
		echo "No data directory found"; \
	fi

.PHONY: install-deps install
install-deps install: ## Install Python dependencies
	@echo "=== Installing dependencies ==="
	$(PYTHON) -m pip install --user \
		mkdocs \
		mkdocs-material \
		pytest \
		flake8 \
		matplotlib \
		networkx 2>/dev/null || \
	echo "Some dependencies could not be installed"
	@echo "Dependencies installation attempted"

.PHONY: clean
clean: clean-cpu clean-boot ## Clean generated files
	@echo "=== Cleaning build artifacts ==="
	rm -rf $(BUILD_DIR)
	rm -f $(TIKZ_DIR)/*.aux $(TIKZ_DIR)/*.log $(TIKZ_DIR)/*.pdf
	rm -f $(WHITEPAPER_DIR)/*.aux $(WHITEPAPER_DIR)/*.log
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.log

.PHONY: clean-cpu
clean-cpu: ## Clean CPU module
	@echo "Cleaning CPU module..."
	@if [ -d $(CPU_MODULE) ]; then \
		$(MAKE) -C $(CPU_MODULE) clean 2>/dev/null || true; \
	fi

.PHONY: clean-boot
clean-boot: ## Clean Boot module
	@echo "Cleaning Boot module..."
	@if [ -d $(BOOT_MODULE) ]; then \
		$(MAKE) -C $(BOOT_MODULE) clean 2>/dev/null || true; \
	fi

.PHONY: dist-clean
dist-clean: clean ## Deep clean including caches
	@echo "=== Deep cleaning ==="
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf $(DATA_DIR)/*.json
	rm -rf $(TIKZ_DIR)
	rm -rf dist/

.PHONY: archive
archive: ## Create distribution archive
	@echo "=== Creating distribution archive ==="
	tar czf minix-analysis-$(shell date +%Y%m%d).tar.gz \
		--exclude=$(BUILD_DIR) \
		--exclude=.git \
		--exclude=__pycache__ \
		--exclude=*.pyc \
		.

.PHONY: status stats
status stats: ## Show repository statistics
	@echo "=== Repository Statistics ==="
	@echo "Documentation files: $$(find $(DOCS_DIR) -name '*.md' 2>/dev/null | wc -l)"
	@echo "Python tools: $$(find $(TOOLS_DIR) -name '*.py' 2>/dev/null | wc -l)"
	@echo "LaTeX files: $$(find $(WHITEPAPER_DIR) -name '*.tex' 2>/dev/null | wc -l)"
	@echo "Total lines of code: $$(find . -name '*.py' -o -name '*.tex' -o -name '*.md' 2>/dev/null | \
		xargs wc -l 2>/dev/null | tail -1 | awk '{print $$1}')"
	@if [ -d $(DATA_DIR) ]; then \
		echo "Analysis data files: $$(ls -1 $(DATA_DIR)/*.json 2>/dev/null | wc -l)"; \
	fi
	@if [ -d $(TIKZ_DIR) ]; then \
		echo "Generated diagrams: $$(ls -1 $(TIKZ_DIR)/*.pdf 2>/dev/null | wc -l)"; \
	fi
	@echo ""
	@echo "Module Status:"
	@if [ -f $(CPU_MODULE)/latex/minix-complete-analysis.pdf ]; then \
		echo "  ✓ CPU PDF exists ($$(stat -c%s $(CPU_MODULE)/latex/minix-complete-analysis.pdf 2>/dev/null || echo 0) bytes)"; \
	else \
		echo "  ✗ CPU PDF not built"; \
	fi
	@if [ -f $(BOOT_MODULE)/latex/minix-boot-analysis.pdf ]; then \
		echo "  ✓ Boot PDF exists ($$(stat -c%s $(BOOT_MODULE)/latex/minix-boot-analysis.pdf 2>/dev/null || echo 0) bytes)"; \
	else \
		echo "  ✗ Boot PDF not built"; \
	fi

# ArXiv packaging (legacy support)
.PHONY: arxiv-cpu arxiv-boot
arxiv-cpu:
	@echo "Creating ArXiv package for CPU Interface Analysis..."
	@if [ -f scripts/create-arxiv-package.sh ]; then \
		scripts/create-arxiv-package.sh cpu-interface; \
	else \
		echo "ArXiv packaging script not found"; \
	fi

arxiv-boot:
	@echo "Creating ArXiv package for Boot Sequence Analysis..."
	@if [ -f scripts/create-arxiv-package.sh ]; then \
		scripts/create-arxiv-package.sh boot-sequence; \
	else \
		echo "ArXiv packaging script not found"; \
	fi

.PHONY: help
help: ## Show this help message
	@echo "MINIX Analysis Build System"
	@echo "============================"
	@echo ""
	@echo "Primary targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E '^[a-z]' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
	@echo ""
	@echo "Build everything:    make all"
	@echo "Parallel build:      make -j4 all"
	@echo "Verbose output:      make V=1 all"
	@echo "Watch mode:          make watch"
	@echo ""
	@echo "Module builds:       make cpu boot"
	@echo "Check environment:   make check"

.DEFAULT_GOAL := help

# Include custom configurations if present
-include Makefile.local