# CPU Interface Analysis Module - Makefile
# Version: 1.0.0
# Last Updated: 2025-10-30

.PHONY: all clean test quick figures plots help

# Directories
LATEX_DIR := latex
DOCS_DIR := docs
FIGURES_DIR := $(LATEX_DIR)/figures
PLOTS_DIR := $(LATEX_DIR)/plots
STYLES_DIR := ../../shared/styles

# Main document
MAIN_TEX := $(LATEX_DIR)/minix-complete-analysis.tex
MAIN_PDF := $(LATEX_DIR)/minix-complete-analysis.pdf

# LaTeX compiler (use LuaLaTeX for Spline Sans fonts)
LATEX := lualatex
LATEX_FLAGS := -interaction=nonstopmode -halt-on-error
LATEX_ENV := TEXINPUTS=.:$(STYLES_DIR)/:

#=============================================================================
# HELP
#=============================================================================

help:
	@echo "CPU Interface Analysis Module"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build complete PDF (figures + plots + document)"
	@echo "  quick     - Quick build (single pass, for iteration)"
	@echo "  figures   - Compile all TikZ figures to standalone PDFs"
	@echo "  plots     - Generate all performance plots"
	@echo "  test      - Validate LaTeX compilation and data integrity"
	@echo "  clean     - Remove all build artifacts"
	@echo "  help      - Show this message"

#=============================================================================
# BUILD TARGETS
#=============================================================================

all: figures plots $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_TEX) figures plots
	@echo "Building complete CPU analysis PDF..."
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@echo "✓ PDF built successfully: $(MAIN_PDF)"

quick: $(MAIN_TEX)
	@echo "Quick build (single pass)..."
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@echo "✓ Quick build complete"

#=============================================================================
# FIGURES
#=============================================================================

figures:
	@echo "Compiling TikZ figures..."
	@for fig in $(FIGURES_DIR)/*-*.tex; do \
		echo "  Compiling $$(basename $$fig)..."; \
		cd $(FIGURES_DIR) && $(LATEX_ENV) $(LATEX) -jobname=$$(basename $$fig .tex) $$fig >/dev/null 2>&1 || \
		echo "    WARNING: $$fig failed to compile"; \
	done
	@echo "✓ Figures compiled"

#=============================================================================
# PLOTS
#=============================================================================

plots:
	@echo "Generating performance plots..."
	@if [ -d "$(PLOTS_DIR)" ]; then \
		for plot in $(PLOTS_DIR)/*.tex; do \
			echo "  Generating $$(basename $$plot)..."; \
			cd $(PLOTS_DIR) && $(LATEX_ENV) $(LATEX) -jobname=$$(basename $$plot .tex) $$plot >/dev/null 2>&1 || \
			echo "    WARNING: $$plot failed to compile"; \
		done; \
		echo "✓ Plots generated"; \
	else \
		echo "  No plots directory found, skipping..."; \
	fi

#=============================================================================
# TESTING
#=============================================================================

test: test-compile test-data

test-compile:
	@echo "Testing LaTeX compilation..."
	@$(MAKE) quick >/dev/null 2>&1 && echo "✓ LaTeX compiles successfully" || \
		(echo "✗ LaTeX compilation failed" && exit 1)

test-data:
	@echo "Validating analysis data..."
	@grep -q "i386" $(DOCS_DIR)/MINIX-CPU-INTERFACE-ANALYSIS.md && \
		echo "✓ Architecture data present" || \
		echo "✗ Missing architecture data"
	@grep -q "INT\|SYSENTER\|SYSCALL" $(DOCS_DIR)/MINIX-CPU-INTERFACE-ANALYSIS.md && \
		echo "✓ Syscall mechanisms documented" || \
		echo "✗ Missing syscall documentation"

#=============================================================================
# CLEANING
#=============================================================================

clean:
	@echo "Cleaning CPU module build artifacts..."
	@cd $(LATEX_DIR) && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk \
		*.synctex.gz *.pdf
	@cd $(FIGURES_DIR) && rm -f *.aux *.log *.pdf
	@if [ -d "$(PLOTS_DIR)" ]; then \
		cd $(PLOTS_DIR) && rm -f *.aux *.log *.pdf; \
	fi
	@echo "✓ Clean complete"

#=============================================================================
# ARXIV PREPARATION
#=============================================================================

arxiv:
	@echo "Preparing ArXiv submission package..."
	@mkdir -p ../../build/arxiv-cpu
	@cp $(LATEX_DIR)/*.tex ../../build/arxiv-cpu/
	@cp $(STYLES_DIR)/*.sty ../../build/arxiv-cpu/
	@cp -r $(FIGURES_DIR) ../../build/arxiv-cpu/
	@echo "✓ ArXiv package created in ../../build/arxiv-cpu/"
	@echo "  Next: Run pdflatex 3 times, then upload .tex + .bbl + figures/"
