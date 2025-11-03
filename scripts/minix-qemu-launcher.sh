#!/bin/bash
# Intelligent MINIX QEMU Launcher
# Auto-detects system capabilities and selects optimal parameters
# Supports both installation from ISO and booting from disk image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"
MEASUREMENTS_DIR="$PROJECT_ROOT/measurements"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "${GREEN}[*]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# ============================================================================
# Parameter Detection
# ============================================================================

detect_system() {
    print_step "Detecting system capabilities..."
    
    # Memory detection
    TOTAL_MEM_MB=$(free -m | grep "^Mem:" | awk '{print $2}')
    AVAIL_MEM_MB=$(free -m | grep "^Mem:" | awk '{print $7}')
    
    # CPU detection
    CPU_COUNT=$(nproc)
    
    # KVM detection
    if [ -e /dev/kvm ]; then
        KVM_AVAILABLE=true
        KVM_FLAG="-enable-kvm"
    else
        KVM_AVAILABLE=false
        KVM_FLAG=""
    fi
    
    # QEMU detection
    if ! command -v qemu-system-i386 &> /dev/null; then
        print_error "QEMU not installed. Install with: pacman -S qemu"
        exit 1
    fi
    
    print_step "System: Memory=${AVAIL_MEM_MB}MB, CPUs=$CPU_COUNT, KVM=$KVM_AVAILABLE"
}

select_parameters() {
    print_step "Selecting optimal parameters..."
    
    # Memory: Use 512MB minimum for MINIX (1GB for X11)
    if [ "$AVAIL_MEM_MB" -gt 2048 ]; then
        QEMU_MEMORY="1024M"
    elif [ "$AVAIL_MEM_MB" -gt 1024 ]; then
        QEMU_MEMORY="512M"
    else
        print_warning "Low memory available (${AVAIL_MEM_MB}MB), using 256M (may be slow)"
        QEMU_MEMORY="256M"
    fi
    
    # CPUs: MINIX SMP support limited, use 1-2
    QEMU_CPUS=1
    
    # CPU model
    if [ "$KVM_AVAILABLE" = true ]; then
        QEMU_CPU="kvm32"
    else
        QEMU_CPU="486"  # Safest for non-KVM
    fi
    
    print_step "Parameters: Memory=$QEMU_MEMORY, CPUs=$QEMU_CPUS, CPU=$QEMU_CPU"
}

# ============================================================================
# Image Detection and Validation
# ============================================================================

find_iso() {
    local iso_file=""
    
    # Priority order
    for candidate in \
        "$DOCKER_DIR/minix_R3.4.0rc6-d5e4fc0.iso" \
        "$DOCKER_DIR/minix_R3.4.0-rc6.iso" \
        "$DOCKER_DIR"/minix*.iso; do
        if [ -f "$candidate" ]; then
            iso_file="$candidate"
            break
        fi
    done
    
    if [ -z "$iso_file" ]; then
        print_error "No MINIX ISO found in $DOCKER_DIR"
        print_error "Download from: https://www.minix3.org/download"
        return 1
    fi
    
    echo "$iso_file"
}

find_disk() {
    local disk_file=""
    
    # Priority order (prefer raw over qcow2)
    for candidate in \
        "$DOCKER_DIR/minix_installed.img" \
        "$DOCKER_DIR/minix.img" \
        "$DOCKER_DIR/minix_installed.qcow2" \
        "$DOCKER_DIR"/minix*.qcow2 \
        "$DOCKER_DIR"/minix*.img; do
        if [ -f "$candidate" ]; then
            disk_file="$candidate"
            break
        fi
    done
    
    echo "$disk_file"
}

validate_image() {
    local image="$1"
    
    if [ ! -f "$image" ]; then
        print_error "Image not found: $image"
        return 1
    fi
    
    local size=$(du -h "$image" | cut -f1)
    print_step "Image: $(basename "$image") ($size)"
    
    # Validate ISO or disk
    if [[ "$image" == *.iso ]]; then
        # Basic ISO validation
        if ! file "$image" | grep -q "ISO 9660"; then
            print_warning "Image may not be valid ISO: $(file "$image")"
        fi
    fi
    
    return 0
}

# ============================================================================
# QEMU Command Building
# ============================================================================

build_qemu_cmd() {
    local mode="$1"  # "install" or "boot"
    local iso="$2"
    local disk="$3"
    
    local cmd="qemu-system-i386"
    
    # Memory and CPU
    cmd="$cmd -m $QEMU_MEMORY"
    cmd="$cmd -smp $QEMU_CPUS"
    cmd="$cmd -cpu $QEMU_CPU"
    
    # KVM if available
    if [ "$KVM_AVAILABLE" = true ]; then
        cmd="$cmd -enable-kvm"
    fi
    
    # Display
    cmd="$cmd -nographic"
    
    # Serial console for boot log
    mkdir -p "$MEASUREMENTS_DIR"
    local boot_log="$MEASUREMENTS_DIR/boot-$(date +%s).log"
    cmd="$cmd -serial file:$boot_log"
    
    # Mode-specific parameters
    if [ "$mode" = "install" ]; then
        # Installation: boot from ISO
        cmd="$cmd -cdrom $iso"
        cmd="$cmd -hda $disk"
        cmd="$cmd -boot d"
        cmd="$cmd -vnc :0" # Add VNC for interactive installation
    elif [ "$mode" = "boot" ]; then
        # Boot: load from disk
        cmd="$cmd -hda $disk"
        cmd="$cmd -boot c"
    fi
    
    # Network
    cmd="$cmd -device ne2k_isa,irq=3,iobase=0x300,netdev=net0 -netdev user,id=net0,hostfwd=tcp::2222-:22"
    
    # Monitor
    cmd="$cmd -monitor none"
    
    echo "$cmd"
    echo "$boot_log"  # Also echo boot log path for reference
}

# ============================================================================
# Interactive Mode
# ============================================================================

interactive_mode() {
    print_header "MINIX QEMU Launcher - Interactive Mode"
    
    detect_system
    select_parameters
    
    echo ""
    echo "Select operation:"
    echo "  1. Install MINIX from ISO"
    echo "  2. Boot installed MINIX"
    echo "  3. Boot with graphical monitoring (VNC)"
    echo "  4. Show boot diagnostics"
    echo ""
    read -p "Choice [1-4]: " choice
    
    case "$choice" in
        1)
            iso=$(find_iso) || exit 1
            disk="$DOCKER_DIR/minix_installed_$(date +%s).qcow2"
            
            print_header "MINIX Installation Mode"
            validate_image "$iso" || exit 1
            
            # Create disk image
            print_step "Creating disk image: $disk"
            qemu-img create -f qcow2 "$disk" 2G
            
            # Build and run QEMU
            print_step "Launching QEMU for installation..."
            cmd=$(build_qemu_cmd "install" "$iso" "$disk")
            boot_log=${cmd##*$'\n'}
            cmd=${cmd%%$'\n'*}
            
            echo ""
            echo "QEMU Command:"
            echo "$cmd"
            echo ""
            read -p "Press ENTER to start installation, Ctrl+C to cancel"
            
            eval "$cmd"
            
            echo ""
            print_step "Installation complete!"
            print_step "Boot log saved to: $boot_log"
            print_step "Next, run: ./minix-qemu-launcher.sh boot"
            ;;
            
        2)
            disk=$(find_disk)
            if [ -z "$disk" ]; then
                print_error "No MINIX disk image found"
                print_error "Run installation first: ./minix-qemu-launcher.sh install"
                exit 1
            fi
            
            print_header "MINIX Boot Mode"
            validate_image "$disk" || exit 1
            
            print_step "Launching QEMU for boot..."
            cmd=$(build_qemu_cmd "boot" "" "$disk")
            boot_log=${cmd##*$'\n'}
            cmd=${cmd%%$'\n'*}
            
            echo ""
            echo "QEMU Command:"
            echo "$cmd"
            echo ""
            read -p "Press ENTER to boot, Ctrl+C to cancel"
            
            eval "$cmd"
            
            print_step "Boot log saved to: $boot_log"
            ;;
            
        3)
            disk=$(find_disk)
            if [ -z "$disk" ]; then
                print_error "No MINIX disk image found"
                exit 1
            fi
            
            print_header "MINIX Boot Mode (with VNC)"
            validate_image "$disk" || exit 1
            
            print_step "Starting QEMU with VNC..."
            cmd="qemu-system-i386 -m $QEMU_MEMORY -smp $QEMU_CPUS -cpu $QEMU_CPU"
            [ "$KVM_AVAILABLE" = true ] && cmd="$cmd -enable-kvm"
            cmd="$cmd -hda $disk -boot c"
            cmd="$cmd -vnc :0"
            
            echo "QEMU Command:"
            echo "$cmd"
            echo ""
            echo "Connect with: vncviewer localhost:5900"
            echo ""
            
            eval "$cmd"
            ;;
            
        4)
            print_header "Boot Diagnostics"
            "$SCRIPT_DIR/minix-boot-diagnostics.sh"
            ;;
            
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# ============================================================================
# Command-Line Mode
# ============================================================================

cli_mode() {
    detect_system
    select_parameters
    
    local mode="$1"
    
    case "$mode" in
        install)
            iso=$(find_iso) || exit 1
            disk="$DOCKER_DIR/minix_fresh_install.qcow2"
            
            print_header "Creating MINIX Disk Image"
            print_step "ISO: $(basename "$iso")"
            print_step "Disk: $(basename "$disk")"
            
            cmd=$(build_qemu_cmd "install" "$iso" "$disk")
            boot_log=${cmd##*$'\n'}
            cmd=${cmd%%$'\n'*}
            
            print_header "Launching MINIX Installation"
            echo "$cmd"
            echo ""
            echo "Connect with VNC viewer to localhost:5900"
            eval "$cmd"
            
            print_step "Installation complete: $disk"
            ;;
            
        boot)
            disk=$(find_disk)
            [ -z "$disk" ] && { print_error "No disk image found"; exit 1; }
            
            print_header "Booting MINIX"
            validate_image "$disk" || exit 1
            
            cmd=$(build_qemu_cmd "boot" "" "$disk")
            boot_log=${cmd##*$'\n'}
            cmd=${cmd%%$'\n'*}
            
            echo "$cmd"
            echo ""
            eval "$cmd"
            
            print_step "Boot log: $boot_log"
            ;;
            
        vnc)
            disk=$(find_disk)
            [ -z "$disk" ] && { print_error "No disk image found"; exit 1; }
            
            print_header "Booting MINIX (VNC)"
            validate_image "$disk" || exit 1
            
            cmd="qemu-system-i386 -m $QEMU_MEMORY -smp $QEMU_CPUS -cpu $QEMU_CPU"
            [ "$KVM_AVAILABLE" = true ] && cmd="$cmd -enable-kvm"
            cmd="$cmd -hda $disk -boot c -vnc :0"
            
            print_step "VNC available at: localhost:5900"
            echo "$cmd"
            eval "$cmd"
            ;;
            
        diagnostics|diag)
            "$SCRIPT_DIR/minix-boot-diagnostics.sh"
            ;;
            
        *)
            print_error "Unknown mode: $mode"
            show_help
            exit 1
            ;;
    esac
}

show_help() {
    cat << EOF
MINIX QEMU Launcher - Intelligent Boot Helper

Usage:
  $0                     # Interactive mode
  $0 install             # Install MINIX from ISO
  $0 boot                # Boot installed MINIX
  $0 vnc                 # Boot with VNC graphical display
  $0 diagnostics         # Run system diagnostics
  $0 help                # Show this help

Examples:
  # Interactive guided mode
  ./minix-qemu-launcher.sh

  # Automated installation
  ./minix-qemu-launcher.sh install

  # Boot with monitoring
  ./minix-qemu-launcher.sh boot

  # Visual boot with VNC
  ./minix-qemu-launcher.sh vnc
  # Then in another terminal: vncviewer localhost:5900

Features:
  - Auto-detects system RAM and CPU capabilities
  - Selects optimal QEMU parameters (memory, CPU model, KVM)
  - Finds MINIX ISO and disk images automatically
  - Captures boot logs for analysis
  - Configures networking (SSH port 2222)
  - Supports both installation and boot modes

Requirements:
  - QEMU (install: pacman -S qemu)
  - MINIX ISO or pre-installed disk image
  - Linux system with at least 512MB available RAM

Boot Logs:
  All boot logs saved to: measurements/boot-TIMESTAMP.log

Next Steps After Installation:
  1. Boot: ./minix-qemu-launcher.sh boot
  2. SSH: ssh -p 2222 root@localhost
  3. Diagnose errors: python3 tools/triage-minix-errors.py measurements/boot-*.log
EOF
}

# ============================================================================
# Main
# ============================================================================

if [ $# -eq 0 ]; then
    interactive_mode
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
else
    cli_mode "$@"
fi
