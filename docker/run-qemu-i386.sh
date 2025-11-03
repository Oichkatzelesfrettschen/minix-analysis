#!/bin/bash

# MINIX i386 QEMU Boot Profiler Script
# Launches MINIX in QEMU with measurement hooks
# Timestamps all boot events and saves to measurement directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOT_START=$(date +%s%3N)
BOOT_TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BOOT_LOG="/measurements/i386/boot-${BOOT_TIMESTAMP}.log"
QEMU_DEBUG="/measurements/i386/qemu-debug-${BOOT_TIMESTAMP}.log"
MEASUREMENTS_JSON="/measurements/i386/measurements-${BOOT_TIMESTAMP}.json"

mkdir -p /measurements/i386

echo "=========================================="
echo "MINIX i386 Boot Profiler"
echo "=========================================="
echo "Boot Start Time: ${BOOT_TIMESTAMP}"
echo "Boot Log: ${BOOT_LOG}"
echo "Measurements JSON: ${MEASUREMENTS_JSON}"
echo ""

# Detect QEMU mode (KVM or TCG)
if [ -e /dev/kvm ]; then
    ENABLE_KVM="-enable-kvm"
    QEMU_MODE="KVM"
else
    ENABLE_KVM=""
    QEMU_MODE="TCG (No KVM available)"
fi

echo "QEMU Mode: ${QEMU_MODE}"
echo ""

# Check for disk image
DISK_IMAGE="${SCRIPT_DIR}/minix-i386.qcow2"
if [ ! -f "${DISK_IMAGE}" ] && [ -f "${SCRIPT_DIR}/minix_R3.4.0-rc6.iso" ]; then
    echo "Creating disk image from ISO..."
    qemu-img create -f qcow2 "${DISK_IMAGE}" 2G

    echo "Installing MINIX to disk (this may take 5-10 minutes)..."
    timeout 600 qemu-system-i386 \
        -m 512M \
        -smp 2 \
        -cpu host \
        ${ENABLE_KVM} \
        -cdrom "${SCRIPT_DIR}/minix_R3.4.0-rc6.iso" \
        -hda "${DISK_IMAGE}" \
        -boot d \
        -serial file:"${BOOT_LOG}" \
        -display none \
        2>&1 | tee -a "${BOOT_LOG}" | head -100

    echo "Installation complete. Rebooting from disk..."
    sleep 2
fi

echo "Starting MINIX i386 QEMU instance..."
echo ""

# Main QEMU boot with measurement hooks
{
    echo "=== QEMU Boot Measurement ==="
    echo "Start Time: $(date)"
    echo "Boot Log: ${BOOT_LOG}"
    echo ""
} >> "${MEASUREMENTS_JSON}"

# Prepare measurement hook script
python3 << 'EOF' > /tmp/measure-boot.py
#!/usr/bin/env python3
import subprocess
import time
import re
import json
from datetime import datetime
from pathlib import Path

boot_start = time.time()
boot_markers = {}

# Tail the serial log and look for boot markers
proc = subprocess.Popen(
    ["tail", "-f", "/measurements/i386/boot-*.log"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1
)

marker_patterns = {
    'kernel_detect': r'MINIX.*booting',
    'pre_init_start': r'pre_init\(',
    'kmain_start': r'kmain\(',
    'cstart_detect': r'cstart\(',
    'scheduler_start': r'scheduler.*start|Starting scheduler',
    'shell_prompt': r'[$#%]'
}

for line in proc.stdout:
    elapsed = time.time() - boot_start

    for marker_name, pattern in marker_patterns.items():
        if marker_name not in boot_markers and re.search(pattern, line, re.IGNORECASE):
            boot_markers[marker_name] = elapsed
            print(f"✓ {marker_name}: {elapsed:.2f}s")

    if elapsed > 300:  # Timeout after 5 minutes
        break

proc.terminate()
proc.wait()

print("\nBoot markers detected:")
for marker, elapsed in sorted(boot_markers.items(), key=lambda x: x[1]):
    print(f"  {marker}: {elapsed:.2f}s")
EOF

# Launch QEMU with serial output to boot log
timeout 300 qemu-system-i386 \
    -m 512M \
    -smp 2 \
    -cpu host \
    ${ENABLE_KVM} \
    -hda "${DISK_IMAGE}" \
    -vnc 0.0.0.0:0 \
    -net nic,model=e1000 \
    -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::9000-:9000 \
    -serial file:"${BOOT_LOG}" \
    -trace enable=qemu_perf_* \
    -D "${QEMU_DEBUG}" \
    -display none \
    2>&1 | tee -a "${BOOT_LOG}" || true

# Post-boot analysis
echo ""
echo "=========================================="
echo "Boot Complete"
echo "=========================================="
BOOT_END=$(date +%s%3N)
BOOT_DURATION=$((BOOT_END - BOOT_START))

echo "Total Boot Time: ${BOOT_DURATION}ms ($(echo "scale=2; ${BOOT_DURATION}/1000" | bc)s)"
echo ""
echo "Boot Log: ${BOOT_LOG}"
echo "Debug Log: ${QEMU_DEBUG}"
echo ""

# Generate JSON measurement report
cat > "${MEASUREMENTS_JSON}" << JSONEOF
{
  "architecture": "i386",
  "boot_timestamp": "${BOOT_TIMESTAMP}",
  "boot_duration_ms": ${BOOT_DURATION},
  "qemu_mode": "${QEMU_MODE}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "disk_image": "${DISK_IMAGE}",
  "boot_log": "${BOOT_LOG}",
  "debug_log": "${QEMU_DEBUG}"
}
JSONEOF

echo "Measurements saved to: ${MEASUREMENTS_JSON}"
echo ""
echo "To view boot log:"
echo "  cat ${BOOT_LOG}"
echo ""
echo "To view QEMU debug log:"
echo "  less ${QEMU_DEBUG}"
