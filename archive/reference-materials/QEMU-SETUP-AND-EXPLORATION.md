================================================================================
QEMU SETUP AND MINIX EXPLORATION GUIDE
Comprehensive Guide to Running MINIX 3.4 RC6 in QEMU with Profiling
Generated: 2025-11-01
================================================================================

EXECUTIVE SUMMARY
================================================================================

This document provides comprehensive guidance for running MINIX 3.4 RC6 in QEMU,
including networking setup, boot sequence understanding, profiling integration,
and troubleshooting. The guide integrates with existing Phase 5-6 profiling work
to enable comprehensive performance analysis of the MINIX operating system.

Key Components:
- QEMU system emulator configuration for i386/x86
- TAP networking for host-guest communication
- Serial console for boot logging
- GDB stub for kernel debugging
- Integration with existing profiling framework

================================================================================
MINIX 3.4 RC6 OVERVIEW
================================================================================

Version: MINIX 3.4.0 RC6 (Release Candidate 6)
Architecture: x86 (32-bit)
Kernel Type: Microkernel with user-space servers
Key Features:
- Self-healing capabilities
- Live update of system components
- NetBSD userland compatibility
- POSIX compliance

System Requirements:
- CPU: i386 or higher (Pentium recommended)
- RAM: Minimum 64MB (256MB recommended)
- Disk: 2GB minimum
- Network: Optional (for package installation)

================================================================================
MINIX BOOT SEQUENCE
================================================================================

The MINIX 3.4 boot process follows this sequence:

1. BIOS/UEFI Initialization
   - Power-on self-test (POST)
   - Load Master Boot Record (MBR) from disk
   - Transfer control to boot loader

2. Boot Monitor (boot/boot)
   - MINIX custom boot loader
   - Loads kernel and initial modules
   - Sets up initial memory map
   - Passes control to kernel

3. Kernel Initialization (kernel/main.c)
   ```
   MINIX booting...
   Kernel: initializing memory
   Kernel: starting system task
   Kernel: starting clock task
   ```
   - Initialize segments and interrupts
   - Set up process table
   - Start SYSTEM task (privileged operations)
   - Start CLOCK task (timers and alarms)
   - Initialize IPC (Inter-Process Communication)

4. Service Manager (servers/rs)
   ```
   RS: starting reincarnation server
   RS: reading boot image table
   RS: starting kernel tasks
   ```
   - Reincarnation Server starts
   - Reads /etc/system.conf
   - Launches essential system servers

5. Process Manager (servers/pm)
   ```
   PM: process manager starting
   PM: initializing process table
   PM: system ready for multiuser mode
   ```
   - Initialize process management
   - Handle fork/exec/exit
   - Signal handling

6. Virtual File System (servers/vfs)
   ```
   VFS: virtual file system starting
   VFS: mounting root filesystem
   VFS: root filesystem is ext2
   ```
   - Mount root filesystem
   - Initialize file descriptors
   - Set up device mappings

7. Memory Manager (servers/vm)
   ```
   VM: virtual memory manager starting
   VM: initializing page tables
   VM: memory layout complete
   ```
   - Set up virtual memory
   - Handle page faults
   - Manage memory allocation

8. Device Drivers
   ```
   AHCI: found SATA controller
   E1000: Intel Ethernet controller detected
   AUDIO: no audio hardware found
   ```
   - Storage drivers (AHCI, IDE)
   - Network drivers (E1000, RTL8139)
   - Other hardware drivers

9. Network Stack (servers/inet)
   ```
   INET: network server starting
   INET: configuring loopback interface
   INET: waiting for network configuration
   ```
   - TCP/IP stack initialization
   - Configure network interfaces
   - Start DHCP client if configured

10. Init Process (servers/init)
    ```
    INIT: system initialization
    INIT: running /etc/rc
    INIT: entering multiuser mode
    ```
    - Read /etc/ttytab
    - Spawn getty processes
    - Execute /etc/rc startup script

11. Login Prompt
    ```
    MINIX 3.4.0 (Galileo) (tty00)

    login:
    ```

Expected Boot Time: 5-10 seconds in QEMU
Total Boot Messages: ~50-100 lines

================================================================================
QEMU CONFIGURATION
================================================================================

Basic QEMU Command:
```bash
qemu-system-i386 \
    -m 256M \
    -drive file=minix.img,format=raw,if=ide \
    -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
    -device e1000,netdev=net0 \
    -serial mon:stdio \
    -display vnc=:1
```

Parameters Explained:

-m 256M
  Allocate 256MB RAM (MINIX minimum is 64MB, 256MB recommended)

-drive file=minix.img,format=raw,if=ide
  Use minix.img as primary IDE disk
  format=raw for uncompressed disk image
  if=ide emulates IDE controller (MINIX compatible)

-netdev tap,id=net0,ifname=tap0,script=no,downscript=no
  Create TAP network backend
  id=net0: Network identifier
  ifname=tap0: TAP interface name on host
  script=no: Don't run ifup script
  downscript=no: Don't run ifdown script

-device e1000,netdev=net0
  Emulate Intel E1000 network card
  MINIX has good E1000 driver support

-serial mon:stdio
  Redirect serial port to stdio
  'mon:' enables QEMU monitor on Ctrl+A, C
  Captures boot messages for analysis

-display vnc=:1
  VNC server on port 5901
  Connect with: vncviewer localhost:1
  Alternative: -display gtk for local window

Advanced Options:

Enable GDB debugging:
  -s -S
  -s: GDB server on port 1234
  -S: Pause at startup, wait for GDB

Enable KVM acceleration (if available):
  -enable-kvm
  Note: Requires KVM support for i386 guest

Increase CPUs:
  -smp 2
  Note: MINIX 3.4 has limited SMP support

Add second disk:
  -drive file=data.img,format=raw,if=ide,index=1

USB support:
  -usb -device usb-mouse -device usb-kbd

Sound card:
  -soundhw ac97
  Note: MINIX audio support is limited

================================================================================
TAP NETWORKING SETUP
================================================================================

TAP (network tap) provides layer 2 network access between host and guest.

Host Setup (run as root):

1. Create TAP interface:
```bash
# Create tap0 interface
ip tuntap add dev tap0 mode tap user $USER

# Bring interface up
ip link set tap0 up

# Assign IP address to host side
ip addr add 10.0.0.1/24 dev tap0

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Add NAT for internet access (optional)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i tap0 -j ACCEPT
iptables -A FORWARD -o tap0 -j ACCEPT
```

2. Make setup persistent:
Create /etc/systemd/network/tap0.netdev:
```ini
[NetDev]
Name=tap0
Kind=tap

[Tap]
User=youruser
Group=yourgroup
```

Create /etc/systemd/network/tap0.network:
```ini
[Match]
Name=tap0

[Network]
Address=10.0.0.1/24
IPForward=yes
```

3. Bridge setup (alternative for multiple VMs):
```bash
# Create bridge
ip link add br0 type bridge
ip link set tap0 master br0
ip link set br0 up
ip addr add 10.0.0.1/24 dev br0
```

Guest Configuration (inside MINIX):

1. Check network interface:
```bash
ifconfig -a
# Should show e1000_0 or similar
```

2. Configure static IP:
```bash
# Edit /etc/inet.conf
echo "eth0 e1000_0 { default; };" > /etc/inet.conf

# Configure IP
ifconfig e1000_0 10.0.0.2 netmask 255.255.255.0

# Add default route
route add default 10.0.0.1

# Add DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

3. Test connectivity:
```bash
# Ping host
ping 10.0.0.1

# Ping internet (if NAT configured)
ping 8.8.8.8
```

4. Make configuration persistent:
Edit /etc/rc.net:
```bash
# Network configuration
ifconfig e1000_0 10.0.0.2 netmask 255.255.255.0
route add default 10.0.0.1
```

================================================================================
PROFILING INTEGRATION
================================================================================

Integration with Phase 5-6 Profiling Framework:

1. Kernel Profiling Setup:

Enable profiling in MINIX kernel:
```bash
# Inside MINIX source before building
cd /usr/src
make MKPROFILE=yes build
```

QEMU command with profiling output:
```bash
qemu-system-i386 \
    -m 256M \
    -drive file=minix.img,format=raw \
    -serial file:boot-profile.log \
    -monitor unix:qemu-monitor.sock,server,nowait \
    -trace events=trace-events.txt \
    -D qemu-trace.log
```

2. Trace Events Configuration:

Create trace-events.txt:
```
# CPU events
cpu_in
cpu_out
exec_tb

# Memory events
memory_region_ops_read
memory_region_ops_write

# Interrupt events
pic_interrupt
apic_deliver_irq
```

3. Profile Data Collection:

Boot profiling:
```bash
# Start QEMU with timestamped serial output
qemu-system-i386 ... -serial file:boot-$(date +%s).log

# Parse boot log for timing
grep -E "^[0-9]+\.[0-9]+" boot-*.log | \
    awk '{print $1, $2}' > boot-timeline.dat
```

System call profiling:
```bash
# Inside MINIX
sprofalyze -d /usr/src -o profile.txt
# Copy profile.txt to host via network or serial
```

Memory profiling:
```bash
# QEMU memory dump
(qemu) dump-guest-memory memory.dump
# Analyze with crash or gdb
```

4. Integration with Existing Tools:

Link to Phase 5 performance tools:
```python
# In tools/performance_analyzer.py
def parse_qemu_profile(logfile):
    """Parse QEMU profiling output"""
    with open(logfile) as f:
        events = []
        for line in f:
            if line.startswith('['):
                # Parse QEMU trace format
                timestamp, event, *args = line.strip().split()
                events.append({
                    'time': float(timestamp.strip('[]')),
                    'event': event,
                    'args': args
                })
    return events
```

Link to Phase 6 visualization:
```python
# Generate boot sequence diagram
def visualize_boot_sequence(events):
    """Create TikZ diagram of boot sequence"""
    # Group events by component
    # Generate timeline visualization
    # Export to tikz_generator.py format
```

================================================================================
COMMON ISSUES AND TROUBLESHOOTING
================================================================================

Issue 1: MINIX won't boot
Symptoms: Hangs at "Booting MINIX 3.4.0"
Causes & Solutions:
- Corrupted disk image: Re-download or rebuild MINIX image
- Insufficient memory: Increase -m to at least 128M
- Wrong disk interface: Use -drive if=ide, not virtio
- BIOS issue: Try with -bios /usr/share/qemu/bios.bin

Issue 2: Network not working
Symptoms: No network interface in MINIX
Causes & Solutions:
- Wrong NIC model: Use e1000 or rtl8139, not virtio
- TAP not configured: Check tap0 exists and is up
- Driver not loaded: Check 'service status' in MINIX
- Firewall blocking: Check iptables rules on host

Issue 3: Very slow performance
Symptoms: Boot takes > 1 minute
Causes & Solutions:
- No KVM: Enable with -enable-kvm if available
- Debug build: Use release build of MINIX
- Excessive logging: Reduce -d flags in QEMU
- I/O bottleneck: Use raw format, not qcow2

Issue 4: Can't connect to VNC
Symptoms: VNC viewer connection refused
Causes & Solutions:
- Wrong port: VNC :1 means port 5901, not 5900
- Firewall: Check if port is open
- Binding: Add -vnc 0.0.0.0:1 for all interfaces
- Alternative: Use -display gtk for local display

Issue 5: Serial console garbage
Symptoms: Unreadable characters on serial
Causes & Solutions:
- Wrong baud rate: MINIX uses 115200 by default
- Terminal emulation: Use 'screen /dev/pts/X 115200'
- Character encoding: Ensure UTF-8 or ASCII

Issue 6: Disk full during profiling
Symptoms: Can't write profile data
Causes & Solutions:
- Small disk image: Increase to 4GB minimum
- /tmp full: Clear temporary files
- Profile data too large: Reduce profiling duration
- Use network to transfer files instead

Issue 7: GDB can't connect
Symptoms: "Connection refused" from GDB
Causes & Solutions:
- QEMU not paused: Use -S to wait for GDB
- Wrong architecture: Use gdb for i386, not x86_64
- Port conflict: Check if 1234 is already used
- Symbol mismatch: Rebuild MINIX with -g flag

================================================================================
QEMU LAUNCH SCRIPT
================================================================================

Complete script for scripts/qemu-launch.sh:

```bash
#!/bin/bash
# QEMU launcher for MINIX 3.4 analysis
# Supports multiple configurations and profiling modes

set -e

# Configuration
MINIX_IMG="${MINIX_IMG:-../minix/minix.img}"
MEMORY="${MEMORY:-256M}"
CPUS="${CPUS:-1}"
VNC_DISPLAY="${VNC_DISPLAY:-1}"
TAP_IFACE="${TAP_IFACE:-tap0}"
PROFILE_DIR="${PROFILE_DIR:-build/profiling}"

# Parse arguments
MODE="normal"
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            MODE="debug"
            shift
            ;;
        --profile)
            MODE="profile"
            shift
            ;;
        --network)
            MODE="network"
            shift
            ;;
        --help)
            echo "Usage: $0 [--debug|--profile|--network]"
            echo "  --debug   : Enable GDB debugging"
            echo "  --profile : Enable profiling output"
            echo "  --network : Setup TAP networking"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check prerequisites
if [ ! -f "$MINIX_IMG" ]; then
    echo "ERROR: MINIX image not found at $MINIX_IMG"
    echo "Please build or download MINIX image first"
    exit 1
fi

# Create directories
mkdir -p "$PROFILE_DIR"
mkdir -p build/logs

# Setup TAP interface if requested
if [ "$MODE" = "network" ] || [ "$MODE" = "profile" ]; then
    echo "Setting up TAP network interface..."
    if ! ip link show $TAP_IFACE &>/dev/null; then
        echo "Creating $TAP_IFACE (requires sudo)..."
        sudo ip tuntap add dev $TAP_IFACE mode tap user $USER
        sudo ip link set $TAP_IFACE up
        sudo ip addr add 10.0.0.1/24 dev $TAP_IFACE

        # Enable forwarding and NAT
        sudo sysctl -w net.ipv4.ip_forward=1
        sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        sudo iptables -A FORWARD -i $TAP_IFACE -j ACCEPT
    else
        echo "TAP interface $TAP_IFACE already exists"
    fi

    NETWORK_ARGS="-netdev tap,id=net0,ifname=$TAP_IFACE,script=no,downscript=no"
    NETWORK_ARGS="$NETWORK_ARGS -device e1000,netdev=net0"
else
    NETWORK_ARGS=""
fi

# Build QEMU command
QEMU_CMD="qemu-system-i386"
QEMU_ARGS="-m $MEMORY"
QEMU_ARGS="$QEMU_ARGS -smp $CPUS"
QEMU_ARGS="$QEMU_ARGS -drive file=$MINIX_IMG,format=raw,if=ide"
QEMU_ARGS="$QEMU_ARGS $NETWORK_ARGS"

# Mode-specific configuration
case $MODE in
    debug)
        echo "Starting MINIX in debug mode..."
        echo "Connect GDB with: gdb -ex 'target remote :1234'"
        QEMU_ARGS="$QEMU_ARGS -s -S"
        QEMU_ARGS="$QEMU_ARGS -serial mon:stdio"
        QEMU_ARGS="$QEMU_ARGS -display gtk"
        ;;

    profile)
        echo "Starting MINIX with profiling..."
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        QEMU_ARGS="$QEMU_ARGS -serial file:$PROFILE_DIR/boot-$TIMESTAMP.log"
        QEMU_ARGS="$QEMU_ARGS -monitor unix:$PROFILE_DIR/monitor-$TIMESTAMP.sock,server,nowait"
        QEMU_ARGS="$QEMU_ARGS -display vnc=:$VNC_DISPLAY"

        # Create trace events file
        cat > $PROFILE_DIR/trace-events.txt <<EOF
# CPU events
cpu_in
cpu_out
exec_tb
exec_tb_exit

# Memory events
memory_region_ops_read
memory_region_ops_write

# Interrupt events
pic_interrupt
pic_ack
EOF
        QEMU_ARGS="$QEMU_ARGS -trace events=$PROFILE_DIR/trace-events.txt"
        QEMU_ARGS="$QEMU_ARGS -D $PROFILE_DIR/trace-$TIMESTAMP.log"

        echo "Profile data will be saved to: $PROFILE_DIR/"
        echo "Boot log: $PROFILE_DIR/boot-$TIMESTAMP.log"
        echo "Trace log: $PROFILE_DIR/trace-$TIMESTAMP.log"
        echo "Monitor socket: $PROFILE_DIR/monitor-$TIMESTAMP.sock"
        echo ""
        echo "Connect via VNC: vncviewer localhost:590$VNC_DISPLAY"
        ;;

    network)
        echo "Starting MINIX with networking..."
        echo "Host IP: 10.0.0.1"
        echo "Guest should use: 10.0.0.2"
        QEMU_ARGS="$QEMU_ARGS -serial mon:stdio"
        QEMU_ARGS="$QEMU_ARGS -display gtk"
        ;;

    *)
        echo "Starting MINIX (normal mode)..."
        QEMU_ARGS="$QEMU_ARGS -serial mon:stdio"
        QEMU_ARGS="$QEMU_ARGS -display gtk"
        ;;
esac

# Show full command
echo "Command: $QEMU_CMD $QEMU_ARGS"
echo ""

# Launch QEMU
exec $QEMU_CMD $QEMU_ARGS
```

Make script executable:
```bash
chmod +x scripts/qemu-launch.sh
```

================================================================================
INTEGRATION WITH EXISTING WORK
================================================================================

Phase 5 Integration (Performance Profiling):

1. Boot Performance Analysis:
   - Collect serial output timestamps
   - Parse boot messages for component initialization
   - Generate boot timeline visualization
   - Compare with theoretical microkernel boot sequence

2. System Call Profiling:
   - Use MINIX's built-in profiling (sprofalyze)
   - Collect system call traces via serial port
   - Analyze IPC message patterns
   - Generate call graph visualizations

3. Memory Usage Analysis:
   - Monitor memory allocation during boot
   - Track page fault patterns
   - Analyze memory fragmentation
   - Compare with monolithic kernel behavior

Phase 6 Integration (Whitepaper):

1. Empirical Data:
   - Add measured boot times to whitepaper
   - Include actual message passing overhead
   - Document driver initialization sequence
   - Provide performance comparison data

2. Architectural Validation:
   - Verify microkernel design claims
   - Measure isolation overhead
   - Document fault recovery behavior
   - Analyze live update performance

3. Visualization Enhancement:
   - Generate boot sequence diagrams from real data
   - Create IPC communication graphs
   - Produce memory layout visualizations
   - Build component dependency maps

================================================================================
NEXT STEPS
================================================================================

1. Immediate Tasks:
   - Test QEMU launch script with actual MINIX image
   - Verify TAP networking configuration
   - Collect initial boot profiling data
   - Generate first boot sequence diagram

2. Integration Tasks:
   - Connect profiling output to Python analyzers
   - Update TikZ generator for boot visualization
   - Add QEMU data to performance metrics
   - Create automated profiling pipeline

3. Documentation Tasks:
   - Add QEMU setup to main README
   - Create troubleshooting guide
   - Document profiling methodology
   - Update whitepaper with empirical data

4. Advanced Features:
   - Implement automated testing in QEMU
   - Add continuous profiling support
   - Create performance regression detection
   - Build comparative analysis framework

================================================================================
REFERENCES AND RESOURCES
================================================================================

Official Documentation:
- MINIX 3 Book: http://www.minix3.org/docs/
- QEMU Documentation: https://www.qemu.org/docs/
- Intel E1000 Specification (for driver debugging)

Community Resources:
- MINIX 3 Wiki: http://wiki.minix3.org/
- MINIX 3 Google Group: https://groups.google.com/g/minix3
- QEMU Mailing List Archives

Related Projects:
- MINIX 3 on GitHub: https://github.com/Stichting-MINIX-Research-Foundation/minix
- Educational OS projects using MINIX
- Microkernel performance studies

Tools and Utilities:
- sprofalyze: MINIX profiling analyzer
- qemu-img: Disk image manipulation
- gdb: Kernel debugging
- wireshark: Network traffic analysis

================================================================================
END OF QEMU SETUP AND EXPLORATION GUIDE
================================================================================