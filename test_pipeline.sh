#!/usr/bin/env bash
#
# Test Pipeline: MINIX Code → Symbols → Call Graph → TikZ → PDF
#

set -euo pipefail

MINIX_ROOT="/home/eirikr/Playground/minix/minix/kernel/arch/i386"
OUTPUT_DIR="/home/eirikr/Playground/minix-cpu-analysis/artifacts"

echo "🔍 Testing MINIX CPU Analysis Pipeline"
echo "======================================="
echo

# Step 1: Extract symbols and calls
echo "Step 1: Extracting symbols from MINIX kernel (mpx.S, klib.S, protect.c)..."
python analysis/parsers/symbol_extractor.py \
    "$MINIX_ROOT" \
    -d "." \
    -o "$OUTPUT_DIR/symbols_kernel.json"

echo
echo "Step 2: Generating call graph (DOT format)..."
python analysis/graphs/call_graph.py \
    "$OUTPUT_DIR/symbols_kernel.json" \
    -o "$OUTPUT_DIR/graphs/kernel_call_graph.dot" \
    -f "mpx.S" "klib.S" "protect.c" \
    -t "MINIX Kernel Call Graph (mpx.S + klib.S + protect.c)" \
    --stats

echo
echo "Step 3: Converting DOT → TikZ..."
python analysis/generators/tikz_converter.py \
    "$OUTPUT_DIR/graphs/kernel_call_graph.dot" \
    -o "latex/figures/04-call-graph-kernel.tex" \
    --prog dot

echo
echo "Step 4: Compiling TikZ → PDF..."
python analysis/generators/tikz_converter.py \
    "$OUTPUT_DIR/graphs/kernel_call_graph.dot" \
    -o "diagrams/04-call-graph-kernel.pdf" \
    --pdf \
    --prog dot

echo
echo "✅ Pipeline test complete!"
echo
echo "Generated files:"
ls -lh "$OUTPUT_DIR/symbols_kernel.json" 2>/dev/null || true
ls -lh "$OUTPUT_DIR/graphs/kernel_call_graph.dot" 2>/dev/null || true
ls -lh "latex/figures/04-call-graph-kernel.tex" 2>/dev/null || true
ls -lh "diagrams/04-call-graph-kernel.pdf" 2>/dev/null || true
echo
echo "View the PDF with: evince diagrams/04-call-graph-kernel.pdf"
