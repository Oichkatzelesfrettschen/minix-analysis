# Boot Sequence Analysis Module - Makefile
# Version: 1.0.0
# Last Updated: 2025-10-30

.PHONY: all clean test quick visualizations help

# Directories
LATEX_DIR := latex
DOCS_DIR := docs
VIZ_DIR := visualizations
STYLES_DIR := ../../shared/styles

# Main document
MAIN_TEX := $(LATEX_DIR)/minix-boot-analysis.tex
MAIN_PDF := $(LATEX_DIR)/minix-boot-analysis.pdf

# LaTeX compiler (use LuaLaTeX for Spline Sans fonts)
LATEX := lualatex
LATEX_FLAGS := -interaction=nonstopmode -halt-on-error
LATEX_ENV := TEXINPUTS=.:$(STYLES_DIR)/:

#=============================================================================
# HELP
#=============================================================================

help:
	@echo "Boot Sequence Analysis Module"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  all            - Build complete PDF (visualizations + document)"
	@echo "  quick          - Quick build (single pass, for iteration)"
	@echo "  visualizations - Generate all call graphs and topology diagrams"
	@echo "  test           - Validate LaTeX compilation and data integrity"
	@echo "  clean          - Remove all build artifacts"
	@echo "  help           - Show this message"

#=============================================================================
# BUILD TARGETS
#=============================================================================

all: visualizations $(MAIN_PDF)

$(MAIN_PDF): $(MAIN_TEX) visualizations
	@echo "Building complete Boot analysis PDF..."
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@echo "✓ PDF built successfully: $(MAIN_PDF)"

quick: $(MAIN_TEX)
	@echo "Quick build (single pass)..."
	@cd $(LATEX_DIR) && $(LATEX_ENV) $(LATEX) $(LATEX_FLAGS) $(notdir $(MAIN_TEX))
	@echo "✓ Quick build complete"

#=============================================================================
# VISUALIZATIONS
#=============================================================================

visualizations:
	@echo "Generating boot sequence visualizations..."
	@if [ -d "$(VIZ_DIR)" ] && [ -f "$(VIZ_DIR)/generate_all.py" ]; then \
		cd $(VIZ_DIR) && python3 generate_all.py && \
		echo "✓ Visualizations generated"; \
	else \
		echo "  No visualization generator found, skipping..."; \
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
	@echo "Validating boot sequence data..."
	@grep -q "Phase\|phase" $(DOCS_DIR)/FINAL_SYNTHESIS_REPORT.md && \
		echo "✓ Boot phase data present" || \
		echo "✗ Missing boot phase data"
	@grep -q "kmain\|kernel_main" $(DOCS_DIR)/FINAL_SYNTHESIS_REPORT.md && \
		echo "✓ Kernel entry point documented" || \
		echo "✗ Missing kernel entry documentation"

#=============================================================================
# CLEANING
#=============================================================================

clean:
	@echo "Cleaning Boot module build artifacts..."
	@cd $(LATEX_DIR) && rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk \
		*.synctex.gz *.pdf
	@if [ -d "$(VIZ_DIR)/output" ]; then \
		rm -rf $(VIZ_DIR)/output/*; \
	fi
	@echo "✓ Clean complete"

#=============================================================================
# ARXIV PREPARATION
#=============================================================================

arxiv:
	@echo "Preparing ArXiv submission package..."
	@mkdir -p ../../build/arxiv-boot
	@cp $(LATEX_DIR)/*.tex ../../build/arxiv-boot/
	@cp $(STYLES_DIR)/*.sty ../../build/arxiv-boot/
	@if [ -d "$(VIZ_DIR)/output" ]; then \
		cp -r $(VIZ_DIR)/output ../../build/arxiv-boot/figures/; \
	fi
	@echo "✓ ArXiv package created in ../../build/arxiv-boot/"
	@echo "  Next: Run pdflatex 3 times, then upload .tex + .bbl + figures/"
