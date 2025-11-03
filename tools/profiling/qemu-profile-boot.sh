#!/bin/bash
# qemu-profile-boot.sh - One-command MINIX boot profiling
# Usage: ./qemu-profile-boot.sh [ISO] [DURATION] [OUTPUT_DIR] [RUN_ID]

set -e

ISO="${1:-/home/eirikr/Playground/minix-analysis/minix.iso}"
DURATION="${2:-30}"
OUTPUT_DIR="${3:-diagrams/profiling}"
RUN_ID="${4:-$(date +%s)}"

mkdir -p "$OUTPUT_DIR"

PERF_DATA="$OUTPUT_DIR/boot-$RUN_ID.perf.data"
FLAMEGRAPH="$OUTPUT_DIR/boot-$RUN_ID.svg"
JSON="$OUTPUT_DIR/boot-$RUN_ID.json"

echo "=== MINIX Boot Profiling ==="
echo "ISO: $ISO"
echo "Duration: ${DURATION}s"
echo "Output: $OUTPUT_DIR"
echo ""

# Step 1: Profile with perf
echo "[1/3] Recording perf data..."
timeout "${DURATION}s" perf record \
  -g -F 99 \
  -o "$PERF_DATA" \
  -- qemu-system-i386 -cdrom "$ISO" -m 512M -nographic \
  || true  # Ignore timeout exit code

# Step 2: Generate flamegraph (if flamegraph tools installed)
echo "[2/3] Generating flamegraph..."
if command -v stackcollapse-perf.pl &> /dev/null; then
  perf script -i "$PERF_DATA" | \
    stackcollapse-perf.pl | \
    flamegraph.pl \
      --title "MINIX Boot ($RUN_ID)" \
      > "$FLAMEGRAPH"
  echo "  Flamegraph: $FLAMEGRAPH"
else
  echo "  WARNING: flamegraph tools not found, skipping flamegraph generation"
  echo "  Install with: yay -S flamegraph-git"
  FLAMEGRAPH="(not generated)"
fi

# Step 3: Extract metadata to JSON
echo "[3/3] Extracting metadata..."
SAMPLE_COUNT=$(perf script -i "$PERF_DATA" | wc -l)

cat > "$JSON" <<EOF
{
  "run_id": "$RUN_ID",
  "iso_path": "$ISO",
  "duration_seconds": $DURATION,
  "sample_count": $SAMPLE_COUNT,
  "perf_data": "$PERF_DATA",
  "flamegraph": "$FLAMEGRAPH"
}
EOF

echo ""
echo "=== Profiling Complete ==="
echo "Perf data: $PERF_DATA"
echo "Flamegraph: $FLAMEGRAPH"
echo "Metadata: $JSON"
echo "Samples: $SAMPLE_COUNT"
