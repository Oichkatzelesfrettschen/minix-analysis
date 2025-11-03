#!/bin/bash

# Direct MINIX QEMU Boot Test
# Captures real boot metrics with serial output to file

set -e

RESULTS_DIR="measurements/phase-7-5-direct"
mkdir -p "$RESULTS_DIR"

ISO_PATH="docker/minix_R3.4.0rc6-d5e4fc0.iso"
CPUS=${1:-1}

echo "=================================================="
echo "MINIX Direct QEMU Boot Test"
echo "=================================================="
echo "CPUs: $CPUS"
echo "ISO: $ISO_PATH"
echo ""

# Check ISO
if [ ! -f "$ISO_PATH" ]; then
    echo "ERROR: ISO not found"
    exit 1
fi

# Create disk image
DISK="$RESULTS_DIR/disk-${CPUS}cpu-$(date +%s).qcow2"
echo "Creating disk image: $DISK"
qemu-img create -f qcow2 "$DISK" 2G > /dev/null

# Boot log
BOOT_LOG="$RESULTS_DIR/boot-${CPUS}cpu-$(date +%s).log"
echo "Boot log: $BOOT_LOG"
echo ""

# Start timing
START=$(date +%s%N)

# Run QEMU with ISO installation
echo "Starting MINIX installation from ISO (this may take several minutes)..."
timeout 180 qemu-system-i386 \
    -m 512M \
    -smp "$CPUS" \
    -cpu qemu64 \
    -cdrom "$ISO_PATH" \
    -hda "$DISK" \
    -boot d \
    -display none \
    -nographic \
    -serial file:"$BOOT_LOG" \
    2>&1 || true

# End timing
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))  # Convert nanoseconds to milliseconds

echo ""
echo "Installation completed"
echo "Elapsed time: ${ELAPSED}ms ($(echo "scale=2; $ELAPSED / 1000" | bc)s)"
echo ""

# Analyze boot log
echo "=================================================="
echo "Boot Log Analysis"
echo "=================================================="
if [ -s "$BOOT_LOG" ]; then
    LOG_SIZE=$(wc -c < "$BOOT_LOG")
    LOG_LINES=$(wc -l < "$BOOT_LOG")
    echo "Log file size: $LOG_SIZE bytes"
    echo "Log lines: $LOG_LINES"
    echo ""
    echo "First 50 lines of boot log:"
    echo "---"
    head -50 "$BOOT_LOG"
    echo "---"
    echo ""
    echo "Last 50 lines of boot log:"
    echo "---"
    tail -50 "$BOOT_LOG"
    echo "---"
else
    echo "WARNING: Boot log is empty!"
fi

# Save metadata
cat > "$RESULTS_DIR/metadata-${CPUS}cpu-$(date +%s).json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cpus": $CPUS,
  "iso": "$ISO_PATH",
  "disk": "$DISK",
  "boot_log": "$BOOT_LOG",
  "boot_time_ms": $ELAPSED,
  "log_size_bytes": $(wc -c < "$BOOT_LOG" 2>/dev/null || echo 0),
  "log_lines": $(wc -l < "$BOOT_LOG" 2>/dev/null || echo 0)
}
EOF

echo "Metadata saved: $RESULTS_DIR/metadata-${CPUS}cpu-*.json"
