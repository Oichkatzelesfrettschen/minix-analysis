#!/bin/bash
################################################################################
# MINIX 3.4 RC6 QEMU Launcher Script
# Purpose: Launch MINIX in QEMU with proper networking and logging
# Usage: ./scripts/qemu-launch.sh [--help|--install|--normal|--debug|--profile]
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MINIX_ISO="${PROJECT_ROOT}/../minix/minix_R3.4.0rc6-d5e4fc0.iso"
MINIX_DISK="/tmp/minix-qemu.qcow2"
LOG_DIR="${PROJECT_ROOT}/qemu-logs"
PROFILE_DIR="${PROJECT_ROOT}/qemu-profiles"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure directories exist
mkdir -p "$LOG_DIR" "$PROFILE_DIR"

################################################################################
# Helper Functions
################################################################################

print_help() {
    cat << 'EOF'
MINIX 3.4 RC6 QEMU Launcher

Usage: ./scripts/qemu-launch.sh [MODE]

Modes:
  --help        Show this help message
  --install     Create new MINIX disk and install system
  --normal      Boot MINIX in normal mode (default)
  --debug       Boot with debug output enabled
  --profile     Boot with profiling enabled
  --network     Boot with TAP networking

Examples:
  ./scripts/qemu-launch.sh --install     # First time setup
  ./scripts/qemu-launch.sh               # Normal boot
  ./scripts/qemu-launch.sh --profile     # With profiling

Requirements:
  - qemu-system-i386 installed
  - MINIX ISO at: ../minix/minix_R3.4.0rc6-d5e4fc0.iso
  - ~4GB free disk space for MINIX image

Notes:
  - TAP networking requires sudo setup (see QEMU-SETUP-AND-EXPLORATION.md)
  - Serial output logged to qemu-logs/
  - Boot time approximately 7-10 seconds
EOF
}

verify_prerequisites() {
    echo -e "${YELLOW}Verifying prerequisites...${NC}"
    
    # Check QEMU
    if ! command -v qemu-system-i386 &> /dev/null; then
        echo -e "${RED}ERROR: qemu-system-i386 not found${NC}"
        echo "Install with: pacman -S qemu"
        exit 1
    fi
    
    # Check ISO
    if [ ! -f "$MINIX_ISO" ]; then
        echo -e "${RED}ERROR: MINIX ISO not found at $MINIX_ISO${NC}"
        echo "Expected location: /home/eirikr/Playground/minix/minix_R3.4.0rc6-d5e4fc0.iso"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites verified${NC}"
}

create_disk() {
    if [ -f "$MINIX_DISK" ]; then
        echo -e "${YELLOW}Disk image exists at $MINIX_DISK${NC}"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        rm "$MINIX_DISK"
    fi
    
    echo -e "${YELLOW}Creating MINIX disk image (4GB qcow2)...${NC}"
    qemu-img create -f qcow2 "$MINIX_DISK" 4G
    echo -e "${GREEN}✓ Disk created at $MINIX_DISK${NC}"
}

launch_normal() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local logfile="${LOG_DIR}/qemu-normal-${timestamp}.log"
    
    echo -e "${GREEN}Launching MINIX in normal mode...${NC}"
    echo "Serial output: $logfile"
    echo ""
    echo "Boot sequence:"
    echo "  1. Press ENTER to select 'Regular MINIX 3'"
    echo "  2. Follow installation prompts"
    echo "  3. Create 'agents' user (optional)"
    echo "  4. System boots into shell"
    echo ""
    echo "To exit: Press Ctrl-A then X (or Ctrl-C)"
    echo ""
    
    qemu-system-i386 \
        -m 1024M \
        -cdrom "$MINIX_ISO" \
        -drive file="$MINIX_DISK",format=qcow2 \
        -nographic \
        -boot d \
        -serial stdio 2>&1 | tee "$logfile"
    
    echo -e "${GREEN}Session complete. Log saved to $logfile${NC}"
}

launch_debug() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local logfile="${LOG_DIR}/qemu-debug-${timestamp}.log"
    
    echo -e "${GREEN}Launching MINIX in debug mode...${NC}"
    echo "Serial output: $logfile"
    
    qemu-system-i386 \
        -m 1024M \
        -cdrom "$MINIX_ISO" \
        -drive file="$MINIX_DISK",format=qcow2 \
        -nographic \
        -boot d \
        -serial stdio \
        -d int,mmu,cpu_reset 2>&1 | tee "$logfile"
    
    echo -e "${GREEN}Session complete. Log saved to $logfile${NC}"
}

launch_profile() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local logfile="${PROFILE_DIR}/qemu-profile-${timestamp}.log"
    
    echo -e "${GREEN}Launching MINIX with profiling enabled...${NC}"
    echo "Profile output: $logfile"
    echo ""
    echo "Profiling will:"
    echo "  1. Measure boot time phases"
    echo "  2. Profile syscall overhead"
    echo "  3. Track CPU utilization"
    echo "  4. Record instruction frequency"
    echo ""
    
    qemu-system-i386 \
        -m 1024M \
        -cdrom "$MINIX_ISO" \
        -drive file="$MINIX_DISK",format=qcow2 \
        -nographic \
        -boot d \
        -serial stdio 2>&1 | tee "$logfile"
    
    echo -e "${GREEN}Profile data saved to $logfile${NC}"
}

launch_network() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local logfile="${LOG_DIR}/qemu-network-${timestamp}.log"
    
    echo -e "${YELLOW}Network mode requires TAP interface setup${NC}"
    echo "Prerequisites:"
    echo "  sudo ip tuntap add dev tap0 mode tap user $(whoami)"
    echo "  sudo ip addr add 10.0.2.2/24 dev tap0"
    echo "  sudo ip link set tap0 up"
    echo ""
    
    # Check if tap0 exists
    if ! ip link show tap0 &> /dev/null; then
        echo -e "${RED}ERROR: tap0 interface not found${NC}"
        echo "Run prerequisite commands above first"
        exit 1
    fi
    
    echo -e "${GREEN}Launching MINIX with network...${NC}"
    echo "Serial output: $logfile"
    echo "Network: tap0 (10.0.2.x)"
    echo ""
    
    qemu-system-i386 \
        -m 1024M \
        -cdrom "$MINIX_ISO" \
        -drive file="$MINIX_DISK",format=qcow2 \
        -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
        -device rtl8139,netdev=net0 \
        -nographic \
        -boot d \
        -serial stdio 2>&1 | tee "$logfile"
    
    echo -e "${GREEN}Session complete. Log saved to $logfile${NC}"
}

################################################################################
# Main
################################################################################

main() {
    local mode="${1:---normal}"
    
    case "$mode" in
        --help)
            print_help
            exit 0
            ;;
        --install)
            verify_prerequisites
            create_disk
            launch_normal
            ;;
        --normal)
            verify_prerequisites
            if [ ! -f "$MINIX_DISK" ]; then
                echo -e "${YELLOW}Disk not found. Creating...${NC}"
                create_disk
            fi
            launch_normal
            ;;
        --debug)
            verify_prerequisites
            if [ ! -f "$MINIX_DISK" ]; then
                echo -e "${YELLOW}Disk not found. Creating...${NC}"
                create_disk
            fi
            launch_debug
            ;;
        --profile)
            verify_prerequisites
            if [ ! -f "$MINIX_DISK" ]; then
                echo -e "${YELLOW}Disk not found. Creating...${NC}"
                create_disk
            fi
            launch_profile
            ;;
        --network)
            verify_prerequisites
            if [ ! -f "$MINIX_DISK" ]; then
                echo -e "${YELLOW}Disk not found. Creating...${NC}"
                create_disk
            fi
            launch_network
            ;;
        *)
            echo -e "${RED}Unknown mode: $mode${NC}"
            print_help
            exit 1
            ;;
    esac
}

# Ensure script is executable
chmod +x "$0"

# Run main function
main "$@"
