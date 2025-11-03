#!/bin/bash

# Real MINIX IA-32 Boot Profiling
# Tests actual MINIX 3.4 RC6 on proper x86 CPU models (486, Pentium, PentiumPro, etc.)
# Captures real boot metrics from serial output

set -e

PROJECT_ROOT="/home/eirikr/Playground/minix-analysis"
ISO="${PROJECT_ROOT}/docker/minix_R3.4.0rc6-d5e4fc0.iso"
RESULTS="${PROJECT_ROOT}/measurements/phase-7-5-real"
mkdir -p "$RESULTS"

CPUS=${1:-1}
CPU_MODEL=${2:-"486"}  # 486, pentium, pentium2, pentium3, athlon, etc.

echo "=========================================="
echo "Real MINIX IA-32 Boot Test"
echo "=========================================="
echo "CPUs: $CPUS"
echo "CPU Model: $CPU_MODEL"
echo "ISO: $ISO"
echo ""

# Validate ISO
if [ ! -f "$ISO" ]; then
    echo "ERROR: ISO not found at $ISO"
    exit 1
fi

ISO_SIZE=$(stat -f%z "$ISO" 2>/dev/null || stat -c%s "$ISO" 2>/dev/null)
echo "ISO verified: $(echo "scale=1; $ISO_SIZE / 1024 / 1024" | bc) MB"
echo ""

# Create disk
TIMESTAMP=$(date +%s)
DISK="$RESULTS/minix-${CPU_MODEL}-${CPUS}cpu-${TIMESTAMP}.qcow2"
BOOT_LOG="$RESULTS/boot-${CPU_MODEL}-${CPUS}cpu-${TIMESTAMP}.log"
METRICS="$RESULTS/metrics-${CPU_MODEL}-${CPUS}cpu-${TIMESTAMP}.json"

echo "Creating disk image..."
qemu-img create -f qcow2 "$DISK" 2G > /dev/null 2>&1
echo "Disk: $(basename $DISK)"
echo "Boot log: $(basename $BOOT_LOG)"
echo ""

# Start measuring
START=$(date +%s%N)

echo "Booting MINIX from ISO (CPU model: $CPU_MODEL, $CPUS vCPU)..."
echo "==================================================================="
echo ""

# Boot with proper 32-bit x86 CPU model
timeout 180 qemu-system-i386 \
    -m 512M \
    -smp "$CPUS" \
    -cpu "$CPU_MODEL" \
    -cdrom "$ISO" \
    -hda "$DISK" \
    -boot d \
    -display none \
    -serial file:"$BOOT_LOG" \
    -monitor none \
    2>&1 || true

# End timing
END=$(date +%s%N)
BOOT_TIME_MS=$(( (END - START) / 1000000 ))

echo ""
echo "==================================================================="
echo ""
echo "Boot completed."
echo "Boot time: ${BOOT_TIME_MS}ms ($(echo "scale=2; $BOOT_TIME_MS / 1000" | bc)s)"
echo ""

# Analyze boot log
if [ -s "$BOOT_LOG" ]; then
    LOG_SIZE=$(stat -f%z "$BOOT_LOG" 2>/dev/null || stat -c%s "$BOOT_LOG" 2>/dev/null)
    LOG_LINES=$(wc -l < "$BOOT_LOG" 2>/dev/null || echo 0)

    echo "Boot log analysis:"
    echo "  Size: $LOG_SIZE bytes"
    echo "  Lines: $LOG_LINES"
    echo ""

    # Check for boot markers
    echo "Boot markers detected:"
    grep -i "kernel\|boot\|init\|running\|minix\|menu\|prompt\|login\|shell\|\$\|#" "$BOOT_LOG" 2>/dev/null | head -30 | sed 's/^/  /'

    echo ""
    echo "Last 20 lines of boot log:"
    echo "---"
    tail -20 "$BOOT_LOG"
    echo "---"
else
    echo "WARNING: Boot log is empty or does not exist"
    LOG_SIZE=0
    LOG_LINES=0
fi

# Save metrics
cat > "$METRICS" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cpu_model": "$CPU_MODEL",
  "cpus": $CPUS,
  "iso": "$(basename $ISO)",
  "boot_time_ms": $BOOT_TIME_MS,
  "boot_time_seconds": $(echo "scale=3; $BOOT_TIME_MS / 1000" | bc),
  "disk_image": "$(basename $DISK)",
  "boot_log": "$(basename $BOOT_LOG)",
  "log_size_bytes": $LOG_SIZE,
  "log_lines": $LOG_LINES,
  "disk_size_gb": 2
}
EOF

echo ""
echo "Results saved:"
echo "  Metrics: $METRICS"
echo "  Boot log: $BOOT_LOG"
echo "  Disk: $DISK"
echo ""

# Display metrics
echo "=========================================="
echo "Boot Metrics Summary"
echo "=========================================="
cat "$METRICS" | grep -v "^{" | grep -v "^}" | sed 's/[",]//g' | sed 's/^ */  /'
