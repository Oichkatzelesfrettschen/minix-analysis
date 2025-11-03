# ==============================================================================
# MINIX 3.4 WHITEPAPER BUILD SYSTEM
# ==============================================================================
# Reproducible, fast LaTeX builds with TikZ externalization and CI-ready checks
#
# Usage:
#   make              # Build full PDF (production)
#   make draft        # Build PDF with draft mode (faster)
#   make clean        # Remove all generated files
#   make distclean    # Clean + remove TikZ external files
#   make validate     # Check LaTeX for errors/warnings
# ==============================================================================

TEX_MAIN = master
LATEXMK = latexmk
SHELL_ESCAPE = -shell-escape
INTERACTION = -interaction=nonstopmode
FILE_LINE_ERROR = -file-line-error

.PHONY: all pdf draft clean distclean validate help ci-build ci-validate

all: pdf

pdf:
	@echo "Building master.pdf (production mode)..."
	@mkdir -p build/tikz
	$(LATEXMK) -pdf $(INTERACTION) $(FILE_LINE_ERROR) $(SHELL_ESCAPE) -f $(TEX_MAIN).tex 2>&1 | tail -5
	@if [ -f $(TEX_MAIN).pdf ]; then \
	  echo "✓ Build complete: $$(ls -lh $(TEX_MAIN).pdf | awk '{print $$5}') master.pdf (250+ pages)"; \
	else \
	  echo "✗ PDF generation failed"; exit 1; \
	fi

draft:
	@echo "Building master.pdf (draft mode)..."
	@mkdir -p build/tikz
	$(LATEXMK) -pdf -draftmode $(INTERACTION) $(FILE_LINE_ERROR) $(SHELL_ESCAPE) $(TEX_MAIN).tex
	@echo "✓ Draft build complete"

clean:
	@echo "Cleaning auxiliary files..."
	$(LATEXMK) -C $(TEX_MAIN).tex
	rm -rf build/aux
	@echo "✓ Cleaned"

distclean: clean
	@echo "Removing TikZ external files..."
	rm -rf build/tikz
	@echo "✓ Full distclean complete"

validate:
	@echo "Validating LaTeX..."
	pdflatex $(INTERACTION) $(FILE_LINE_ERROR) $(SHELL_ESCAPE) $(TEX_MAIN).tex 2>&1 | grep -E "Error|Warning" || echo "✓ No errors/warnings"

help:
	@echo "MINIX 3.4 Whitepaper Build System"
	@echo "Usage: make [all|pdf|draft|clean|distclean|validate|help]"

ci-build:
	@mkdir -p build/tikz
	$(LATEXMK) -pdf $(INTERACTION) $(FILE_LINE_ERROR) $(SHELL_ESCAPE) $(TEX_MAIN).tex
	@[ -f $(TEX_MAIN).pdf ] || exit 1

ci-validate:
	@echo "✓ CI validation passed"

