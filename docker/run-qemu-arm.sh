#!/bin/bash

# MINIX ARM QEMU Boot Profiler Script
# Placeholder - needs ARM MINIX artifacts (kernel, rootfs, device tree)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOT_TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BOOT_LOG="/measurements/arm/boot-${BOOT_TIMESTAMP}.log"

mkdir -p /measurements/arm

echo "=========================================="
echo "MINIX ARM Boot Profiler"
echo "=========================================="
echo "Boot Start Time: ${BOOT_TIMESTAMP}"
echo ""

# Check for required ARM MINIX artifacts
if [ ! -f "${SCRIPT_DIR}/minix-arm-kernel" ] || [ ! -f "${SCRIPT_DIR}/minix-arm-rootfs.img" ]; then
    echo "ERROR: ARM MINIX artifacts not found."
    echo ""
    echo "Required files:"
    echo "  ${SCRIPT_DIR}/minix-arm-kernel"
    echo "  ${SCRIPT_DIR}/minix-arm-rootfs.img"
    echo "  ${SCRIPT_DIR}/minix-arm.dtb (device tree, optional)"
    echo ""
    echo "To build ARM MINIX:"
    echo "  git clone https://github.com/Minix3/minix.git"
    echo "  cd minix && git checkout 3.4.0-rc6"
    echo "  ./configure --host=arm-linux && make"
    echo ""
    exit 1
fi

echo "Found ARM MINIX artifacts."
echo "Boot Log: ${BOOT_LOG}"
echo ""

# Detect KVM availability
if [ -e /dev/kvm ]; then
    ENABLE_KVM="-enable-kvm"
    QEMU_MODE="KVM"
else
    ENABLE_KVM=""
    QEMU_MODE="TCG (No KVM available)"
fi

echo "QEMU Mode: ${QEMU_MODE}"
echo ""

# Device tree file (if available)
DTB_FILE=""
if [ -f "${SCRIPT_DIR}/minix-arm.dtb" ]; then
    DTB_FILE="-dtb ${SCRIPT_DIR}/minix-arm.dtb"
    echo "Using device tree: ${DTB_FILE}"
fi

echo "Starting MINIX ARM QEMU instance..."
echo ""

# Launch QEMU ARM
timeout 120 qemu-system-arm \
    -m 512M \
    -smp 2 \
    -cpu cortex-a9 \
    ${DTB_FILE} \
    -kernel "${SCRIPT_DIR}/minix-arm-kernel" \
    -drive if=sd,format=raw,file="${SCRIPT_DIR}/minix-arm-rootfs.img" \
    -vnc 0.0.0.0:1 \
    -net nic,model=lan9118 \
    -net user \
    -serial file:"${BOOT_LOG}" \
    -display none \
    2>&1 | tee -a "${BOOT_LOG}" || true

echo ""
echo "=========================================="
echo "Boot Complete"
echo "=========================================="
echo "Boot Log: ${BOOT_LOG}"
echo ""
echo "To view boot log:"
echo "  cat ${BOOT_LOG}"
