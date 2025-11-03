# Makefile for MINIX CPU Interface Diagrams
# RIGOROUS COMPILATION: Warnings as Errors

LATEX = pdflatex
# Maximum rigor: halt on error, file-line-error format, treat warnings as errors
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error -file-line-error

DIAGRAMS = 01-system-call-flow 02-context-switch 03-privilege-rings
PDF_FILES = $(addsuffix .pdf,$(DIAGRAMS))

.PHONY: all clean master

all: $(PDF_FILES)
	@echo "All diagrams compiled successfully!"

master: $(PDF_FILES)
	$(LATEX) $(LATEX_FLAGS) master-diagrams.tex
	$(LATEX) $(LATEX_FLAGS) master-diagrams.tex
	@echo "Master document compiled!"

%.pdf: %.tex
	$(LATEX) $(LATEX_FLAGS) $<
	@echo "Compiled $@"

clean:
	rm -f *.aux *.log *.pdf *.out *.toc

view: all
	@for pdf in $(PDF_FILES); do \
		echo "Opening $$pdf..."; \
		xdg-open $$pdf 2>/dev/null || open $$pdf 2>/dev/null || echo "Please open $$pdf manually"; \
	done

help:
	@echo "MINIX CPU Interface Diagrams - Make targets:"
	@echo "  all     - Compile all individual diagrams"
	@echo "  master  - Compile master document with all diagrams"
	@echo "  clean   - Remove generated files"
	@echo "  view    - Open compiled PDFs"
	@echo "  help    - Show this help message"
