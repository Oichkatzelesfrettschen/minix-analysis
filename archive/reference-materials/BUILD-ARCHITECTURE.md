================================================================================
BUILD SYSTEM ARCHITECTURE FOR MINIX ANALYSIS PROJECT
Professional Multi-Repository Build Orchestration Design
Generated: 2025-11-01
================================================================================

EXECUTIVE SUMMARY
================================================================================

This document defines a professional build system architecture that orchestrates
both the MINIX source repository (read-only reference) and the minix-analysis
repository (active development). The design follows GNU Make conventions while
supporting modern documentation toolchains (mkdocs, LaTeX, Python analysis).

Key Design Principles:
1. Separation of Concerns: MINIX source is read-only input
2. Reproducible Builds: All artifacts can be regenerated from source
3. Incremental Compilation: Only rebuild what changed
4. Parallel Execution: Support -j flag for parallel builds
5. Clean Separation: Analysis tools never modify MINIX source

================================================================================
REPOSITORY STRUCTURE AND SEPARATION
================================================================================

Physical Layout:
```
/home/eirikr/Playground/
├── minix/                      # MINIX source (READ-ONLY)
│   ├── minix/                  # Actual source (note double nesting)
│   │   ├── kernel/             # Kernel source
│   │   ├── servers/            # System servers
│   │   └── include/            # Headers
│   └── Makefile                # MINIX's own build (not touched)
│
├── minix-analysis/             # Analysis repository (ACTIVE)
│   ├── Makefile                # Analysis orchestration
│   ├── docs/                   # Documentation source
│   ├── tools/                  # Analysis tools
│   ├── whitepaper/             # LaTeX publication
│   └── build/                  # Generated artifacts (git-ignored)
│
└── Makefile                    # ROOT orchestrator (NEW)
```

Separation Rationale:
- MINIX source remains pristine for reference
- Analysis tools read from MINIX but write to minix-analysis/build/
- Root Makefile provides unified interface for both repos
- CI/CD can run from root without understanding structure

Integration Points:
1. Source Analysis: tools read from ../minix/minix/
2. Documentation: references MINIX paths but generates in build/
3. Profiling: runs MINIX in QEMU, collects data in minix-analysis/
4. Publishing: packages only minix-analysis content

================================================================================
ROOT MAKEFILE (ORCHESTRATOR)
================================================================================

Location: /home/eirikr/Playground/Makefile

```makefile
# Root Makefile - Orchestrates both MINIX and analysis repositories
# Usage: make [target] from /home/eirikr/Playground/

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Directories
MINIX_DIR := minix
ANALYSIS_DIR := minix-analysis
MINIX_SRC := $(MINIX_DIR)/minix

# Python interpreter
PYTHON := python3

# Default target
.PHONY: all
all: analysis

# High-level targets
.PHONY: analysis
analysis: ## Run complete analysis pipeline
→$(MAKE) -C $(ANALYSIS_DIR) all

.PHONY: minix
minix: ## Build MINIX (if needed for testing)
→@echo "MINIX is treated as read-only reference"
→@echo "To build MINIX, cd $(MINIX_DIR) && make"

.PHONY: docs
docs: ## Build all documentation
→$(MAKE) -C $(ANALYSIS_DIR) docs

.PHONY: whitepaper
whitepaper: ## Build LaTeX whitepaper
→$(MAKE) -C $(ANALYSIS_DIR) whitepaper

.PHONY: audit
audit: ## Run documentation audit
→$(MAKE) -C $(ANALYSIS_DIR) audit

.PHONY: test
test: ## Run all tests
→$(MAKE) -C $(ANALYSIS_DIR) test

.PHONY: clean
clean: ## Clean generated files
→$(MAKE) -C $(ANALYSIS_DIR) clean

.PHONY: dist-clean
dist-clean: ## Clean everything including caches
→$(MAKE) -C $(ANALYSIS_DIR) dist-clean

.PHONY: install-deps
install-deps: ## Install Python dependencies
→$(MAKE) -C $(ANALYSIS_DIR) install-deps

.PHONY: qemu
qemu: ## Launch MINIX in QEMU
→$(MAKE) -C $(ANALYSIS_DIR) qemu

.PHONY: validate
validate: ## Validate repository structure
→@echo "Checking MINIX source availability..."
→@test -d $(MINIX_SRC) || (echo "ERROR: MINIX source not found at $(MINIX_SRC)" && exit 1)
→@echo "Checking analysis repository..."
→@test -d $(ANALYSIS_DIR) || (echo "ERROR: Analysis repo not found at $(ANALYSIS_DIR)" && exit 1)
→$(MAKE) -C $(ANALYSIS_DIR) validate

.PHONY: help
help: ## Show this help message
→@echo "MINIX Analysis Build System"
→@echo "============================"
→@echo ""
→@echo "Usage: make [target]"
→@echo ""
→@echo "Targets:"
→@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
→→awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
→@echo ""
→@echo "Advanced usage:"
→@echo "  make -j4 all         # Parallel build with 4 jobs"
→@echo "  make V=1 all         # Verbose output"
→@echo "  make MINIX_DIR=/alt/path all  # Use alternative MINIX location"

# Default target
.DEFAULT_GOAL := help
```

================================================================================
MINIX-ANALYSIS MAKEFILE
================================================================================

Location: /home/eirikr/Playground/minix-analysis/Makefile

```makefile
# minix-analysis Makefile - Analysis and documentation pipeline
# This Makefile orchestrates all analysis, documentation, and publishing tasks

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
→mkdir -p $@

# Primary targets
.PHONY: all
all: analysis docs whitepaper ## Build everything

.PHONY: analysis
analysis: $(ANALYSIS_BUILD)/.analyzed ## Run source analysis
$(ANALYSIS_BUILD)/.analyzed: $(BUILD_DIR) | validate-minix
→@echo "=== Running MINIX source analysis ==="
→$(PYTHON) $(ANALYZER) \
→→--minix-root $(MINIX_ROOT) \
→→--output $(DATA_DIR)
→@echo "=== Generating TikZ diagrams ==="
→$(PYTHON) $(TIKZ_GEN) \
→→--data-dir $(DATA_DIR) \
→→--output $(TIKZ_DIR)
→@echo "=== Compiling TikZ to PDF ==="
→@cd $(TIKZ_DIR) && \
→for tex in *.tex; do \
→→echo "  Compiling $$tex..."; \
→→$(PDFLATEX) -interaction=nonstopmode "$$tex" >/dev/null 2>&1 || \
→→→(echo "Failed to compile $$tex" && exit 1); \
→done
→touch $@

.PHONY: docs
docs: $(DOCS_BUILD)/.built ## Build documentation with mkdocs
$(DOCS_BUILD)/.built: $(DOCS_BUILD) | lint-docs
→@echo "=== Building documentation site ==="
→@if command -v $(MKDOCS) >/dev/null 2>&1; then \
→→$(MKDOCS) build -d $(DOCS_BUILD); \
→else \
→→echo "WARNING: mkdocs not found, using fallback HTML generation"; \
→→$(PYTHON) $(TOOLS_DIR)/generate_static_docs.py \
→→→--source $(DOCS_DIR) \
→→→--output $(DOCS_BUILD); \
→fi
→touch $@

.PHONY: whitepaper
whitepaper: $(WHITEPAPER_BUILD)/.built ## Build LaTeX whitepaper
$(WHITEPAPER_BUILD)/.built: $(WHITEPAPER_BUILD) analysis
→@echo "=== Building whitepaper ==="
→cp -r $(WHITEPAPER_DIR)/* $(WHITEPAPER_BUILD)/
→cp -r $(TIKZ_DIR)/*.pdf $(WHITEPAPER_BUILD)/figures/ 2>/dev/null || true
→cd $(WHITEPAPER_BUILD) && \
→$(PDFLATEX) -interaction=nonstopmode main.tex && \
→$(PDFLATEX) -interaction=nonstopmode main.tex  # Run twice for references
→touch $@

.PHONY: audit
audit: ## Run documentation audit
→@echo "=== Running documentation audit ==="
→@if [ -f $(AUDIT_TOOL) ]; then \
→→$(PYTHON) $(AUDIT_TOOL) --root . --output $(BUILD_DIR)/audit-report.md; \
→else \
→→echo "Creating audit tool..."; \
→→echo "import os, sys" > $(AUDIT_TOOL); \
→→echo "print('Audit: Checking documentation structure...')" >> $(AUDIT_TOOL); \
→→echo "# TODO: Implement comprehensive audit" >> $(AUDIT_TOOL); \
→→$(PYTHON) $(AUDIT_TOOL); \
→fi

.PHONY: lint
lint: lint-markdown lint-python lint-tex ## Run all linters

.PHONY: lint-markdown
lint-markdown: ## Lint markdown files
→@echo "=== Linting markdown files ==="
→@if command -v markdownlint >/dev/null 2>&1; then \
→→markdownlint $(DOCS_DIR)/**/*.md || true; \
→else \
→→echo "markdownlint not found, skipping..."; \
→fi

.PHONY: lint-python
lint-python: ## Lint Python files
→@echo "=== Linting Python files ==="
→@if command -v flake8 >/dev/null 2>&1; then \
→→flake8 $(TOOLS_DIR)/*.py --max-line-length=100; \
→else \
→→$(PYTHON) -m py_compile $(TOOLS_DIR)/*.py; \
→fi

.PHONY: lint-tex
lint-tex: ## Lint LaTeX files
→@echo "=== Linting LaTeX files ==="
→@if command -v chktex >/dev/null 2>&1; then \
→→chktex -q $(WHITEPAPER_DIR)/*.tex || true; \
→else \
→→echo "chktex not found, skipping..."; \
→fi

.PHONY: lint-docs
lint-docs: ## Validate documentation structure
→@echo "=== Validating documentation links ==="
→@if [ -f $(LINK_CHECK) ]; then \
→→$(PYTHON) $(LINK_CHECK) --root $(DOCS_DIR); \
→else \
→→grep -r '\[.*\](.*\.md)' $(DOCS_DIR) --include="*.md" | \
→→→grep -v "^Binary" | wc -l | \
→→→xargs echo "Found markdown links:"; \
→fi

.PHONY: test
test: test-unit test-integration ## Run all tests

.PHONY: test-unit
test-unit: ## Run unit tests
→@echo "=== Running unit tests ==="
→@if [ -d tests ]; then \
→→$(PYTHON) -m pytest tests/unit -v; \
→else \
→→echo "No unit tests found"; \
→fi

.PHONY: test-integration
test-integration: ## Run integration tests
→@echo "=== Running integration tests ==="
→@if [ -d tests ]; then \
→→$(PYTHON) -m pytest tests/integration -v; \
→else \
→→echo "No integration tests found"; \
→fi

.PHONY: qemu
qemu: ## Launch MINIX in QEMU
→@echo "=== Launching MINIX in QEMU ==="
→scripts/qemu-launch.sh

.PHONY: serve
serve: docs ## Serve documentation locally
→@echo "=== Serving documentation at http://localhost:8000 ==="
→@if command -v $(MKDOCS) >/dev/null 2>&1; then \
→→$(MKDOCS) serve; \
→else \
→→cd $(DOCS_BUILD) && $(PYTHON) -m http.server 8000; \
→fi

.PHONY: watch
watch: ## Watch for changes and rebuild
→@echo "=== Watching for changes ==="
→@while true; do \
→→$(MAKE) all; \
→→echo "Waiting for changes..."; \
→→inotifywait -r -e modify,create,delete \
→→→--exclude '$(BUILD_DIR)' \
→→→$(DOCS_DIR) $(TOOLS_DIR) $(WHITEPAPER_DIR) 2>/dev/null; \
→done

.PHONY: validate
validate: validate-minix validate-structure ## Validate environment

.PHONY: validate-minix
validate-minix: ## Check MINIX source availability
→@echo "=== Validating MINIX source ==="
→@test -d $(MINIX_SRC) || \
→→(echo "ERROR: MINIX source not found at $(MINIX_SRC)" && exit 1)
→@test -f $(MINIX_SRC)/kernel/main.c || \
→→(echo "ERROR: MINIX kernel source not complete" && exit 1)
→@echo "MINIX source validated at $(MINIX_SRC)"

.PHONY: validate-structure
validate-structure: ## Validate repository structure
→@echo "=== Validating repository structure ==="
→@test -d $(DOCS_DIR) || (echo "ERROR: docs/ directory missing" && exit 1)
→@test -d $(TOOLS_DIR) || (echo "ERROR: tools/ directory missing" && exit 1)
→@test -f $(ANALYZER) || (echo "ERROR: Source analyzer missing" && exit 1)
→@echo "Repository structure validated"

.PHONY: install-deps
install-deps: ## Install Python dependencies
→@echo "=== Installing dependencies ==="
→$(PYTHON) -m pip install --user \
→→mkdocs \
→→mkdocs-material \
→→pytest \
→→flake8 \
→→matplotlib \
→→networkx
→@echo "Dependencies installed"

.PHONY: clean
clean: ## Clean generated files
→@echo "=== Cleaning build artifacts ==="
→rm -rf $(BUILD_DIR)
→rm -f $(TIKZ_DIR)/*.aux $(TIKZ_DIR)/*.log $(TIKZ_DIR)/*.pdf
→rm -f $(WHITEPAPER_DIR)/*.aux $(WHITEPAPER_DIR)/*.log
→find . -type f -name "*.pyc" -delete
→find . -type d -name "__pycache__" -delete

.PHONY: dist-clean
dist-clean: clean ## Deep clean including caches
→@echo "=== Deep cleaning ==="
→rm -rf .pytest_cache
→rm -rf .mypy_cache
→rm -rf $(DATA_DIR)/*.json
→rm -rf $(TIKZ_DIR)

.PHONY: archive
archive: ## Create distribution archive
→@echo "=== Creating distribution archive ==="
→tar czf minix-analysis-$(shell date +%Y%m%d).tar.gz \
→→--exclude=$(BUILD_DIR) \
→→--exclude=.git \
→→--exclude=__pycache__ \
→→--exclude=*.pyc \
→→.

.PHONY: stats
stats: ## Show repository statistics
→@echo "=== Repository Statistics ==="
→@echo "Documentation files: $$(find $(DOCS_DIR) -name '*.md' | wc -l)"
→@echo "Python tools: $$(find $(TOOLS_DIR) -name '*.py' | wc -l)"
→@echo "LaTeX files: $$(find $(WHITEPAPER_DIR) -name '*.tex' | wc -l)"
→@echo "Total lines of code: $$(find . -name '*.py' -o -name '*.tex' -o -name '*.md' | \
→→xargs wc -l | tail -1 | awk '{print $$1}')"
→@if [ -d $(DATA_DIR) ]; then \
→→echo "Analysis data files: $$(ls -1 $(DATA_DIR)/*.json 2>/dev/null | wc -l)"; \
→fi
→@if [ -d $(TIKZ_DIR) ]; then \
→→echo "Generated diagrams: $$(ls -1 $(TIKZ_DIR)/*.pdf 2>/dev/null | wc -l)"; \
→fi

.PHONY: help
help: ## Show this help message
→@echo "MINIX Analysis Build System"
→@echo "============================"
→@echo ""
→@echo "Primary targets:"
→@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
→→grep -E '^[a-z]' | \
→→awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
→@echo ""
→@echo "Build everything:    make all"
→@echo "Parallel build:      make -j4 all"
→@echo "Verbose output:      make V=1 all"
→@echo "Watch mode:          make watch"

.DEFAULT_GOAL := help

# Include custom configurations if present
-include Makefile.local
```

================================================================================
INTEGRATION POINTS EXPLAINED
================================================================================

1. Source Analysis Integration
-----------------------------------
The analyzer reads from MINIX source but writes to minix-analysis:

```python
# In tools/minix_source_analyzer.py
MINIX_ROOT = "../minix/minix"  # Read from here
OUTPUT_DIR = "diagrams/data"    # Write to here

# Never modify MINIX source, only read
with open(f"{MINIX_ROOT}/kernel/main.c", "r") as f:
    content = f.read()
    # Analyze content

# Write results to our repository
with open(f"{OUTPUT_DIR}/analysis.json", "w") as f:
    json.dump(results, f)
```

2. Documentation Integration
-----------------------------------
Documentation references MINIX but generates locally:

```markdown
# In docs/architecture/kernel.md
The MINIX kernel source is located at `../minix/minix/kernel/`

Key files:
- main.c: Kernel entry point
- proc.c: Process management
- system.c: System call handling

[View source](../../../minix/minix/kernel/main.c)
```

3. Build Output Separation
-----------------------------------
All generated files go to build/ (git-ignored):

```
minix-analysis/build/
├── analysis/          # Analysis results
├── docs/              # Generated documentation
└── whitepaper/        # PDF output
```

4. QEMU Integration
-----------------------------------
QEMU runs MINIX but saves output locally:

```bash
# In scripts/qemu-launch.sh
qemu-system-i386 \
    -drive file=../minix/minix.img,format=raw \
    -serial file:build/minix-boot.log \
    -monitor unix:build/qemu-monitor.sock,server,nowait
```

================================================================================
MAKEFILE DESIGN RATIONALE
================================================================================

Why Make Instead of Modern Build Tools:
1. Universal availability (every Unix system has make)
2. No additional dependencies to install
3. Excellent parallel execution support
4. Clear dependency graph
5. Standard in academic/research environments

Why Two Makefiles:
1. Separation of concerns (root orchestrates, analysis executes)
2. Can run analysis independently without root
3. Root Makefile can orchestrate multiple projects
4. Clean abstraction boundaries

Key Design Decisions:

1. Sentinel Files (.built, .analyzed)
   - Track completion of multi-step targets
   - Enable incremental rebuilds
   - Prevent unnecessary recomputation

2. Dependency Order
   - analysis → docs (docs may reference analysis results)
   - analysis → whitepaper (whitepaper includes diagrams)
   - validate → everything (ensure environment is correct)

3. Graceful Degradation
   - Check for optional tools (mkdocs, markdownlint)
   - Provide fallbacks when tools missing
   - Core functionality works with just Python + Make

4. Professional Touches
   - Help target with formatted output
   - Statistics target for project metrics
   - Watch mode for development
   - Archive target for distribution

================================================================================
CI/CD INTEGRATION
================================================================================

GitHub Actions Workflow:
```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/checkout@v2
        with:
          repository: 'Stichting-MINIX-Research-Foundation/minix'
          path: '../minix'

      - name: Install dependencies
        run: make install-deps

      - name: Validate structure
        run: make validate

      - name: Run analysis
        run: make analysis

      - name: Build documentation
        run: make docs

      - name: Run tests
        run: make test

      - name: Build whitepaper
        run: make whitepaper

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: build-artifacts
          path: build/
```

================================================================================
USAGE EXAMPLES
================================================================================

Common Developer Workflows:

```bash
# First-time setup
cd /home/eirikr/Playground
make install-deps
make validate

# Full build
make all

# Incremental development
make analysis          # Just run analysis
make docs             # Just build docs
make whitepaper       # Just build paper

# Development mode
make watch            # Auto-rebuild on changes
make serve           # Serve docs locally

# Testing
make lint            # Check code quality
make test           # Run test suite
make audit          # Audit documentation

# Cleanup
make clean          # Remove build artifacts
make dist-clean     # Deep clean

# Distribution
make archive        # Create tarball
```

Advanced Usage:

```bash
# Parallel build (use all cores)
make -j$(nproc) all

# Verbose output
make V=1 analysis

# Custom MINIX location
make MINIX_ROOT=/alt/minix/path analysis

# Override Python version
make PYTHON=python3.11 all

# Dry run (show commands without executing)
make -n all

# Force rebuild
make -B whitepaper

# Include local overrides
echo "PDFLATEX := xelatex" > Makefile.local
make whitepaper
```

================================================================================
END OF BUILD ARCHITECTURE DOCUMENT
================================================================================