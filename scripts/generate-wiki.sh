#!/usr/bin/env sh
# Wiki Generation Script for MINIX Analysis Project
# Builds the unified documentation wiki using MkDocs
#
# Usage: ./generate-wiki.sh
# Output: wiki/site/ (static HTML)

set -eu

echo "====================================="
echo " MINIX Analysis - Wiki Generation"
echo "====================================="
echo ""

# Check if mkdocs is installed
if ! command -v mkdocs >/dev/null 2>&1; then
  echo "⚠️  MkDocs not installed"
  echo ""
  echo "To install MkDocs:"
  echo "  pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin"
  echo ""
  echo "Or install all project dependencies:"
  echo "  pip install -r requirements.txt"
  echo ""
  echo "Wiki generation skipped (non-fatal)"
  exit 0
fi

# Verify wiki directory exists
if [ ! -d "wiki" ]; then
  echo "❌ Error: wiki/ directory not found" >&2
  echo "   Current directory: $(pwd)" >&2
  exit 1
fi

# Build wiki
echo "Building wiki with MkDocs..."
cd wiki

if mkdocs build; then
  echo ""
  echo "✅ Wiki built successfully"
  echo "   Output: wiki/site/"
  echo ""
  echo "To serve locally:"
  echo "   cd wiki && mkdocs serve"
  echo "   Then visit: http://localhost:8000"
  echo ""
  echo "To deploy to GitHub Pages:"
  echo "   cd wiki && mkdocs gh-deploy"
else
  echo ""
  echo "❌ Wiki build failed"
  echo "   Check mkdocs.yml configuration"
  exit 1
fi
