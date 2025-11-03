#!/bin/bash

# Phase 7.5 Validation Test
# Checks environment setup and profiler readiness

set -e

PROJECT_ROOT="/home/eirikr/Playground/minix-analysis"
ISO_PATH="${PROJECT_ROOT}/docker/minix_R3.4.0rc6-d5e4fc0.iso"
PROFILER="${PROJECT_ROOT}/phase-7-5-qemu-boot-profiler.py"
RESULTS_DIR="${PROJECT_ROOT}/measurements/phase-7-5-validation"

echo "=================================="
echo "Phase 7.5 Validation Test"
echo "=================================="
echo ""

# Check ISO file
echo "Checking ISO file..."
if [ -f "$ISO_PATH" ]; then
    SIZE=$(ls -lh "$ISO_PATH" | awk '{print $5}')
    echo "✓ ISO found: $ISO_PATH ($SIZE)"
else
    echo "✗ ISO not found: $ISO_PATH"
    exit 1
fi

# Check QEMU
echo ""
echo "Checking QEMU..."
if command -v qemu-system-i386 &> /dev/null; then
    QEMU_VERSION=$(qemu-system-i386 --version 2>/dev/null | head -1)
    echo "✓ QEMU found: $QEMU_VERSION"
else
    echo "✗ QEMU not found"
    exit 1
fi

# Check qemu-img
echo ""
echo "Checking qemu-img..."
if command -v qemu-img &> /dev/null; then
    echo "✓ qemu-img found"
else
    echo "✗ qemu-img not found"
    exit 1
fi

# Check profiler script
echo ""
echo "Checking profiler script..."
if [ -f "$PROFILER" ]; then
    echo "✓ Profiler script found: $PROFILER"
    # Verify syntax
    python3 -m py_compile "$PROFILER" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Profiler syntax is valid"
    else
        echo "✗ Profiler has syntax errors"
        python3 -m py_compile "$PROFILER"
        exit 1
    fi
else
    echo "✗ Profiler script not found: $PROFILER"
    exit 1
fi

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import subprocess, json, re, sys, time, pathlib, tempfile, argparse, statistics, datetime" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All Python modules available"
else
    echo "✗ Missing Python modules"
    exit 1
fi

# Create results directory
echo ""
echo "Creating results directory..."
mkdir -p "$RESULTS_DIR"
echo "✓ Results directory: $RESULTS_DIR"

# Test profiler help
echo ""
echo "Testing profiler help..."
python3 "$PROFILER" --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Profiler help works"
else
    echo "✗ Profiler help failed"
    exit 1
fi

# Show system info
echo ""
echo "=================================="
echo "System Information"
echo "=================================="
echo "Kernel: $(uname -r)"
echo "CPUs: $(nproc)"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "Disk: $(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $2, "free:", $4}')"
echo ""

# Show test parameters
echo "=================================="
echo "Phase 7.5 Test Parameters"
echo "=================================="
echo "ISO: $ISO_PATH"
echo "Profiler: $PROFILER"
echo "Results dir: $RESULTS_DIR"
echo "QEMU: $(which qemu-system-i386)"
echo ""

# Estimate test duration
echo "=================================="
echo "Test Duration Estimate"
echo "=================================="
echo "Quick validation (1 sample): ~15-20 minutes"
echo "Full test (5 samples): ~60-90 minutes"
echo ""

# Show test command
echo "=================================="
echo "Ready to Run Tests"
echo "=================================="
echo ""
echo "Quick validation (1 sample per CPU config):"
echo "  cd $PROJECT_ROOT"
echo "  python3 phase-7-5-qemu-boot-profiler.py \\"
echo "    --iso $ISO_PATH \\"
echo "    --output $RESULTS_DIR/quick \\"
echo "    --samples 1"
echo ""
echo "Full test (5 samples per CPU config):"
echo "  python3 phase-7-5-qemu-boot-profiler.py \\"
echo "    --iso $ISO_PATH \\"
echo "    --output $RESULTS_DIR/full \\"
echo "    --samples 5"
echo ""

echo "✓ All checks passed! System is ready for Phase 7.5 testing."
echo ""
