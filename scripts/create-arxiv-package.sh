#!/usr/bin/env sh
# ArXiv Package Creation Script for MINIX Analysis Modules
# Creates ArXiv-compliant submission packages from analysis modules
#
# Usage: ./create-arxiv-package.sh <module-name>
# Example: ./create-arxiv-package.sh boot-sequence

set -eu

module="${1:-}"

if [ -z "$module" ]; then
  echo "Usage: $0 <module-name>" >&2
  echo "" >&2
  echo "Available modules:" >&2
  echo "  cpu-interface" >&2
  echo "  boot-sequence" >&2
  echo "" >&2
  echo "Example: $0 boot-sequence" >&2
  exit 1
fi

# Verify module exists
module_dir="modules/$module"
if [ ! -d "$module_dir" ]; then
  echo "Error: Module not found: $module_dir" >&2
  exit 1
fi

# Create ArXiv submissions directory
mkdir -p arxiv-submissions

# Generate timestamp for package
timestamp=$(date +%Y%m%d-%H%M%S)
package_name="${module}-arxiv-${timestamp}"
package_dir="arxiv-submissions/$package_name"

echo "Creating ArXiv package: $package_name"
echo ""

# TODO: Full implementation
# This is a stub that will be enhanced with actual packaging logic
#
# Full implementation would:
# 1. Copy main LaTeX file(s) from modules/$module/latex/
# 2. Copy all required figures (PDF only, no .eps)
# 3. Copy shared style files (minix-*.sty)
# 4. Generate .bbl file from .bib (if bibliography exists)
# 5. Remove auxiliary files (.aux, .log, .out, etc.)
# 6. Create submission ZIP with correct structure
# 7. Validate ArXiv compliance (TeX Live 2023, colorlinks, etc.)
# 8. Generate submission README with compilation instructions

echo "Placeholder package directory: $package_dir"
echo ""
echo "TODO: Implement full ArXiv packaging"
echo "  - Copy LaTeX files from $module_dir/latex/"
echo "  - Include shared styles from shared/styles/"
echo "  - Generate .bbl from bibliography"
echo "  - Create submission ZIP"
echo "  - Validate ArXiv compliance"
echo ""
echo "For manual ArXiv submission:"
echo "  1. cd $module_dir/latex"
echo "  2. Compile: pdflatex + bibtex + pdflatex + pdflatex"
echo "  3. Copy .tex, .bbl, figures/*.pdf, and shared/styles/*.sty"
echo "  4. Create ZIP without directory structure"
echo "  5. Submit to ArXiv"
echo ""
echo "See ARXIV-STANDARDS.md for complete compliance checklist"

exit 0
