#!/bin/bash
# Test script for MINIX automated installation
# This script demonstrates the complete workflow

set -e

# Configuration
ISO_PATH="/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso"
DISK_PATH="/home/eirikr/Playground/minix-analysis/docker/minix_test_install.qcow2"
DISK_SIZE="2G"
MEMORY="512M"

echo "==================================================================="
echo "MINIX 3.4 RC6 Automated Installation Test"
echo "==================================================================="
echo ""
echo "Configuration:"
echo "  ISO:    $ISO_PATH"
echo "  Disk:   $DISK_PATH"
echo "  Size:   $DISK_SIZE"
echo "  Memory: $MEMORY"
echo ""

# Verify ISO exists
if [ ! -f "$ISO_PATH" ]; then
    echo "[ERROR] ISO file not found: $ISO_PATH"
    exit 1
fi

# Check if pexpect is installed
if ! python3 -c "import pexpect" 2>/dev/null; then
    echo "[ERROR] pexpect is not installed. Installing..."
    pip3 install pexpect
fi

# Remove old disk if exists (clean test)
if [ -f "$DISK_PATH" ]; then
    echo "[*] Removing old disk image..."
    rm -f "$DISK_PATH"
fi

echo ""
echo "==================================================================="
echo "Starting automated installation..."
echo "==================================================================="
echo ""

# Run installation
python3 /home/eirikr/Playground/minix-analysis/docker/minix_auto_install.py \
    --iso "$ISO_PATH" \
    --disk "$DISK_PATH" \
    --size "$DISK_SIZE" \
    --memory "$MEMORY"

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================================================="
    echo "Installation completed successfully!"
    echo "==================================================================="
    echo ""
    echo "Disk image created: $DISK_PATH"
    echo "Size: $(du -h "$DISK_PATH" | cut -f1)"
    echo ""
    echo "To boot the installed system:"
    echo "  python3 minix_auto_install.py --iso $ISO_PATH --disk $DISK_PATH --boot --no-create"
    echo ""
    echo "Or manually with QEMU:"
    echo "  qemu-system-i386 -m 512M -hda $DISK_PATH -serial stdio -nographic -enable-kvm"
else
    echo ""
    echo "[ERROR] Installation failed!"
    exit 1
fi
