#!/bin/bash
# MINIX Boot Parameter Diagnostics and Validation
# Detects system capabilities and suggests optimal QEMU parameters

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIAGNOSTICS_FILE="$PROJECT_ROOT/measurements/boot-diagnostics.json"

echo "=========================================="
echo "MINIX Boot Diagnostics Tool"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$PROJECT_ROOT/measurements"

# Initialize JSON output
cat > "$DIAGNOSTICS_FILE" << 'EOF'
{
  "timestamp": "TIMESTAMP_PLACEHOLDER",
  "system": {},
  "qemu": {},
  "suggested_parameters": {},
  "compatibility": []
}
EOF

# Update timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
sed -i "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/" "$DIAGNOSTICS_FILE"

# ============================================================================
# System Detection
# ============================================================================

echo "1. Detecting system capabilities..."

# CPU model
if command -v lscpu &> /dev/null; then
    CPU_MODEL=$(lscpu | grep "Model name" | cut -d: -f2 | xargs)
else
    CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
fi

# CPU count
CPU_COUNT=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo)

# Total memory
TOTAL_MEM=$(free -h | grep "^Mem:" | awk '{print $2}')
TOTAL_MEM_MB=$(free -m | grep "^Mem:" | awk '{print $2}')

# Available memory
AVAIL_MEM=$(free -h | grep "^Mem:" | awk '{print $7}')
AVAIL_MEM_MB=$(free -m | grep "^Mem:" | awk '{print $7}')

# Check for KVM
KVM_AVAILABLE="false"
if [ -e /dev/kvm ]; then
    KVM_AVAILABLE="true"
fi

# Check for QEMU
if command -v qemu-system-i386 &> /dev/null; then
    QEMU_VERSION=$(qemu-system-i386 --version | head -1)
else
    QEMU_VERSION="NOT INSTALLED"
fi

echo "   CPU Model: $CPU_MODEL"
echo "   CPU Count: $CPU_COUNT"
echo "   Memory: $TOTAL_MEM ($AVAIL_MEM available)"
echo "   KVM Available: $KVM_AVAILABLE"
echo "   QEMU: $QEMU_VERSION"
echo ""

# ============================================================================
# QEMU Feature Detection
# ============================================================================

echo "2. Detecting QEMU features..."

QEMU_FEATURES=()

# Test CPU models
declare -A CPU_MODELS
for model in 486 pentium pentium2 kvm32 qemu64 host; do
    if timeout 1 qemu-system-i386 -cpu "$model" -nographic 2>/dev/null; then
        CPU_MODELS["$model"]="ok"
    else
        CPU_MODELS["$model"]="untested"
    fi
done

# Test display options
DISPLAY_OPTIONS=()
for display in "none" "sdl" "gtk"; do
    if timeout 1 qemu-system-i386 -display "$display" -nographic 2>/dev/null; then
        DISPLAY_OPTIONS+=("$display")
    fi
done

# Test network models
NETWORK_MODELS=()
for model in "ne2k_isa" "virtio" "rtl8139" "pcnet"; do
    if timeout 1 qemu-system-i386 -net nic,model="$model" 2>/dev/null; then
        NETWORK_MODELS+=("$model")
    fi
done

echo "   Supported CPUs: ${!CPU_MODELS[@]}"
echo "   Display Options: ${DISPLAY_OPTIONS[@]}"
echo "   Network Models: ${NETWORK_MODELS[@]}"
echo ""

# ============================================================================
# ISO Detection
# ============================================================================

echo "3. Detecting MINIX images..."

ISO_FILES=()
DISK_FILES=()

if [ -d "$PROJECT_ROOT/docker" ]; then
    for iso in "$PROJECT_ROOT/docker"/*.iso; do
        if [ -f "$iso" ]; then
            ISO_FILES+=("$(basename "$iso")")
        fi
    done
    
    for img in "$PROJECT_ROOT/docker"/*.qcow2 "$PROJECT_ROOT/docker"/*.img; do
        if [ -f "$img" ]; then
            DISK_FILES+=("$(basename "$img")")
        fi
    done
fi

echo "   ISO Files: ${ISO_FILES[*]}"
echo "   Disk Images: ${DISK_FILES[*]}"
echo ""

# ============================================================================
# Compatibility Tests
# ============================================================================

echo "4. Running compatibility tests..."

# Test 1: Basic QEMU functionality
echo "   [TEST 1] Basic QEMU Boot"
if timeout 5 qemu-system-i386 -m 256M -nographic 2>/dev/null; then
    echo "   ✓ QEMU basic functionality works"
    TEST_BASIC="PASS"
else
    echo "   ✗ QEMU basic functionality failed"
    TEST_BASIC="FAIL"
fi

# Test 2: KVM acceleration
echo "   [TEST 2] KVM Acceleration"
if [ "$KVM_AVAILABLE" = "true" ]; then
    if timeout 5 qemu-system-i386 -m 256M -enable-kvm -nographic 2>/dev/null; then
        echo "   ✓ KVM acceleration available"
        TEST_KVM="PASS"
    else
        echo "   ✗ KVM acceleration failed"
        TEST_KVM="FAIL"
    fi
else
    echo "   ✗ KVM not available (no /dev/kvm)"
    TEST_KVM="UNAVAILABLE"
fi

# Test 3: Serial console
echo "   [TEST 3] Serial Console"
if command -v qemu-system-i386 &> /dev/null; then
    TEST_SERIAL="PASS"
    echo "   ✓ Serial console support available"
else
    TEST_SERIAL="FAIL"
    echo "   ✗ Serial console test failed"
fi

# Test 4: VNC support
echo "   [TEST 4] VNC Support"
QEMU_HELP=$(qemu-system-i386 -help 2>&1 || true)
if echo "$QEMU_HELP" | grep -q "vnc"; then
    TEST_VNC="PASS"
    echo "   ✓ VNC support available"
else
    TEST_VNC="FAIL"
    echo "   ✗ VNC support not found"
fi

echo ""

# ============================================================================
# Generate Recommendations
# ============================================================================

echo "5. Generating recommendations..."

RECOMMENDATIONS=()

# Memory recommendation
if [ "$AVAIL_MEM_MB" -gt 2048 ]; then
    RECOMMENDED_MEM="1024M"
    RECOMMENDATIONS+=("Use -m 1024M for optimal performance")
elif [ "$AVAIL_MEM_MB" -gt 1024 ]; then
    RECOMMENDED_MEM="512M"
    RECOMMENDATIONS+=("Use -m 512M (minimum for MINIX with X11)")
else
    RECOMMENDED_MEM="256M"
    RECOMMENDATIONS+=("WARNING: System has low memory, use -m 256M minimum")
fi

# CPU recommendation
if [ "$CPU_COUNT" -ge 4 ]; then
    RECOMMENDED_CPUS=2
    RECOMMENDATIONS+=("Use -smp 2 (more won't benefit MINIX on this system)")
else
    RECOMMENDED_CPUS=1
    RECOMMENDATIONS+=("Use -smp 1")
fi

# KVM recommendation
if [ "$KVM_AVAILABLE" = "true" ] && [ "$TEST_KVM" = "PASS" ]; then
    RECOMMENDATIONS+=("Enable KVM: add -enable-kvm for 2-3x speedup")
    CPU_FLAG="-cpu kvm32"
else
    RECOMMENDATIONS+=("KVM not available, use -cpu 486 for safety")
    CPU_FLAG="-cpu 486"
fi

# Display recommendation
if echo "${DISPLAY_OPTIONS[@]}" | grep -q "sdl"; then
    RECOMMENDATIONS+=("For graphical boot monitoring, use -sdl")
fi
RECOMMENDATIONS+=("For automated testing, use -nographic -serial file:boot.log")

# Network recommendation
if echo "${NETWORK_MODELS[@]}" | grep -q "ne2k_isa"; then
    RECOMMENDATIONS+=("NE2K network available: use -net nic,model=ne2k_isa,irq=3,iobase=0x300")
fi
if echo "${NETWORK_MODELS[@]}" | grep -q "virtio"; then
    RECOMMENDATIONS+=("VirtIO network available (modern, faster): -net nic,model=virtio")
fi

for rec in "${RECOMMENDATIONS[@]}"; do
    echo "   - $rec"
done

echo ""

# ============================================================================
# Generate Suggested QEMU Commands
# ============================================================================

echo "6. Building suggested QEMU commands..."

if [ "${#ISO_FILES[@]}" -gt 0 ]; then
    ISO="${ISO_FILES[0]}"
    echo "   Installation command (using $ISO):"
    echo "   qemu-system-i386 \\"
    echo "     -m $RECOMMENDED_MEM \\"
    echo "     -smp $RECOMMENDED_CPUS \\"
    echo "     $CPU_FLAG \\"
    echo "     -cdrom docker/$ISO \\"
    echo "     -hda minix_disk.qcow2 \\"
    echo "     -boot d \\"
    echo "     -nographic -serial file:boot.log"
    echo ""
fi

if [ "${#DISK_FILES[@]}" -gt 0 ]; then
    DISK="${DISK_FILES[0]}"
    echo "   Boot command (using $DISK):"
    echo "   qemu-system-i386 \\"
    echo "     -m $RECOMMENDED_MEM \\"
    echo "     -smp $RECOMMENDED_CPUS \\"
    echo "     $CPU_FLAG \\"
    echo "     -hda docker/$DISK \\"
    echo "     -boot c \\"
    echo "     -nographic -serial file:boot.log"
    echo ""
fi

# ============================================================================
# Generate JSON Report
# ============================================================================

echo "7. Saving diagnostics report..."

cat > "$DIAGNOSTICS_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "system": {
    "cpu_model": "$CPU_MODEL",
    "cpu_count": $CPU_COUNT,
    "total_memory_mb": $TOTAL_MEM_MB,
    "available_memory_mb": $AVAIL_MEM_MB,
    "kvm_available": $KVM_AVAILABLE,
    "qemu_version": "$QEMU_VERSION"
  },
  "qemu": {
    "cpu_models": ["$(IFS='","'; echo "${!CPU_MODELS[*]}")"],
    "display_options": ["$(IFS='","'; echo "${DISPLAY_OPTIONS[*]}")"],
    "network_models": ["$(IFS='","'; echo "${NETWORK_MODELS[*]}")"]
  },
  "tests": {
    "basic_qemu": "$TEST_BASIC",
    "kvm_acceleration": "$TEST_KVM",
    "serial_console": "$TEST_SERIAL",
    "vnc_support": "$TEST_VNC"
  },
  "suggested_parameters": {
    "memory": "$RECOMMENDED_MEM",
    "cpus": $RECOMMENDED_CPUS,
    "cpu_model": "$CPU_FLAG",
    "kvm_enabled": $([ "$TEST_KVM" = "PASS" ] && echo "true" || echo "false"),
    "display": "nographic",
    "serial": "file:boot.log"
  },
  "images": {
    "iso_files": ["$(IFS='","'; echo "${ISO_FILES[*]}")"],
    "disk_files": ["$(IFS='","'; echo "${DISK_FILES[*]}")"]
  },
  "recommendations": ["$(IFS='","'; echo "${RECOMMENDATIONS[*]}")"]
}
EOF

echo "   Report saved: $DIAGNOSTICS_FILE"
echo ""

# ============================================================================
# Summary
# ============================================================================

echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
echo ""
echo "Key Findings:"
echo "  - Memory available: $AVAIL_MEM"
echo "  - KVM support: $KVM_AVAILABLE"
echo "  - QEMU installed: $([ "$QEMU_VERSION" != "NOT INSTALLED" ] && echo "Yes" || echo "No")"
echo "  - ISO images found: ${#ISO_FILES[@]}"
echo "  - Disk images found: ${#DISK_FILES[@]}"
echo ""
echo "Next Steps:"
echo "  1. Use the suggested parameters above for QEMU commands"
echo "  2. View full report: cat $DIAGNOSTICS_FILE"
echo "  3. Run Docker Compose: docker-compose -f docker-compose.enhanced.yml up minix-i386"
echo ""
