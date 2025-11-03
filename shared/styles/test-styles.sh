#!/usr/bin/env sh
# Shared Style System Test Script
# Validates that all LaTeX style files are present and correct
#
# Usage: ./test-styles.sh

set -eu

echo "==========================================="
echo " MINIX Analysis - Style System Validation"
echo "==========================================="
echo ""

# Get script directory
styles_dir="$(cd "$(dirname "$0")" && pwd)"

echo "Style directory: $styles_dir"
echo ""

# Check all required style files exist
echo "Checking style files..."
all_exist=true

for style in minix-styles.sty minix-colors.sty minix-colors-cvd.sty minix-arxiv.sty; do
  if [ -f "$styles_dir/$style" ]; then
    size=$(wc -c < "$styles_dir/$style")
    echo "  ✅ $style (${size} bytes)"
  else
    echo "  ❌ MISSING: $style" >&2
    all_exist=false
  fi
done

if [ "$all_exist" = false ]; then
  echo ""
  echo "❌ Some style files are missing"
  exit 1
fi

echo ""
echo "Checking for duplicate styles in modules..."

# Check that modules don't have duplicate style files
project_root="$(dirname "$(dirname "$styles_dir")")"
duplicates_found=false

for module_latex in "$project_root"/modules/*/latex; do
  if [ -d "$module_latex" ]; then
    module_name=$(basename "$(dirname "$module_latex")")
    for style in minix-styles.sty minix-colors.sty minix-arxiv.sty; do
      if [ -f "$module_latex/$style" ]; then
        echo "  ❌ Duplicate in $module_name/latex/$style" >&2
        duplicates_found=true
      fi
    done
  fi
done

if [ "$duplicates_found" = true ]; then
  echo ""
  echo "❌ Found duplicate style files in modules"
  echo "   Modules should use shared styles: ../../shared/styles/"
  exit 1
else
  echo "  ✅ No duplicates found in module directories"
fi

echo ""
echo "Additional validations TODO:"
echo "  - Test LaTeX compilation of each .sty file"
echo "  - Verify color definitions are consistent"
echo "  - Validate ArXiv compliance"
echo "  - Check TikZ style compatibility"
echo ""
echo "✅ Basic style system checks passed"
exit 0
