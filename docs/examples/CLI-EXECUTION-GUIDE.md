# MINIX Development Environment - Complete CLI Execution Guide

**Source**: MINIX-CLI-EXECUTION-GUIDE.md
**Date Organized**: 2025-11-01
**Purpose**: Step-by-step CLI commands for MINIX development environment setup and measurement
**Complexity Level**: ⭐⭐⭐ (Intermediate)
**Estimated Time**: 20-30 minutes

---

## Overview

This guide provides step-by-step CLI commands to:
1. Set up TAP networking for MINIX
2. Boot MINIX from ISO with interactive serial console
3. Configure MINIX networking internally
4. Compile and deploy measurement tools
5. Run syscall and memory profilers
6. Capture and export results

## Prerequisites Verification

Verify your system has all required tools:

```bash
# Check QEMU
which qemu-system-i386 && qemu-system-i386 --version | head -1

# Check socat (for serial console)
which socat && socat -V | head -1

# Check ISO exists
file /home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso

# Check dev environment
ls -lh /home/eirikr/Playground/minix-analysis/dev-environment/
```

Expected output: All commands return paths and versions without errors.

---

## Step 1: Navigate to Dev Environment

**Duration**: Immediate

Open a terminal and navigate to the development environment:

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
pwd  # Verify you're in the right directory
ls -la  # List all files
```

---

## Step 2: Set Up TAP Network (One-time per Session)

**Duration**: 2-3 minutes
**Requires**: `sudo` password entry

Execute the network setup script:

```bash
./setup-network.sh
```

**Script Actions:**
- Creates TAP interface `tap0`
- Assigns IP address `192.168.122.1/24`
- Enables IP forwarding
- Allows MINIX to reach 192.168.122.x via DHCP

**Verification** (wait for script to complete, then check):

```bash
ip link show tap0
ip addr show tap0 | grep "inet "
```

Expected: Interface shows "UP" and IP `192.168.122.1/24`

**Troubleshooting:**
- If "Device or resource busy": TAP already exists from previous session
- Clean up: `sudo ip tuntap del dev tap0 mode tap`
- Then run setup again

---

## Step 3: Start MINIX in Background

**Duration**: 2-3 minutes
**Requires**: ~512MB RAM, 2 vCPUs from host

In the same terminal, start MINIX:

```bash
./boot-minix-interactive.sh start
```

**What This Does:**
1. Creates serial socket at `/tmp/minix-serial.sock`
2. Launches QEMU with MINIX ISO
3. Attaches TAP interface for networking
4. Redirects serial output to log file
5. Returns to prompt (MINIX runs in background)

**Verify MINIX Started:**

```bash
./boot-minix-interactive.sh status
```

Expected output: Shows QEMU PID and memory usage

---

## Step 4: Monitor Boot Progress (Optional, in New Terminal)

**Duration**: 30-60 seconds
**In**: A **new terminal** in same directory

Watch MINIX boot in real-time:

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
./boot-minix-interactive.sh logs-live
```

Press `Ctrl+C` to stop watching (MINIX continues running).

**What to Look For:**
- Bootloader messages
- Kernel initialization
- Process startup
- Network interface detection
- Ready/login prompt

---

## Step 5: Connect to MINIX Serial Console

**Duration**: Interactive
**In**: A **third terminal** in same directory

Open interactive connection to MINIX:

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
./boot-minix-interactive.sh connect
```

**You are now in MINIX shell!**

Type commands as if you're in MINIX. Press `Ctrl+D` to disconnect (but MINIX keeps running).

**Example MINIX Commands to Try:**

```bash
# Show MINIX version
uname -a

# Check network interfaces
ifconfig

# Show current directory
pwd

# List files
ls /tmp

# Check system uptime
uptime
```

---

## Step 6: Configure MINIX Network (Within MINIX Shell)

**Duration**: 2-3 minutes
**Location**: MINIX serial console (from Step 5)

Since MINIX RC6 typically has auto-DHCP, try:

```bash
# Check if interface is up and has IP
ifconfig

# If no IP, enable interface with netconf
netconf
# Follow prompts: select NE2K card, choose DHCP
```

If DHCP doesn't work, configure static IP:

```bash
ifconfig de0 192.168.122.100
route add default 192.168.122.1
```

**Verify Network Connectivity:**

Test with HTTP request (QEMU DHCP doesn't support ping):

```bash
# Test DNS resolution
nslookup localhost

# Or check gateway is reachable
ifconfig de0  # Should show IP like 192.168.122.x
```

---

## Step 7: Compile Measurement Tools (Within MINIX)

**Duration**: 5-10 seconds
**Location**: MINIX serial console

The C source files are in `/tmp/`. Compile them:

```bash
# Compile syscall profiler
gcc -o syscall-profiler /tmp/minix-syscall-profiler.c

# Compile memory monitor
gcc -o memory-monitor /tmp/minix-memory-monitor.c

# Verify they compiled
ls -la syscall-profiler memory-monitor
```

Expected: Two executable files created.

**Troubleshooting:**
- If "gcc: command not found": Need to install build tools
  ```bash
  pkgin install gcc  # May need internet
  ```
- If "error: minix-syscall-profiler.c: No such file": Files in `/tmp/`
  ```bash
  ls /tmp/minix-*.c  # Verify source files exist
  ```

---

## Step 8: Run Syscall Profiler

**Duration**: 2-5 seconds
**Location**: MINIX serial console

Execute the profiler:

```bash
./syscall-profiler
```

**Expected Output:**
```
MINIX Syscall Profiler
======================

System information:
  Uptime: XXX seconds
  Processes: YYY
  UID: Z
  GID: Z

CPU times (in clock ticks):
  User: XXXX
  System: YYYY
  Child user: ZZZZ
  Child system: WWWW
  Elapsed: PPPP
```

**Capture to File:**

```bash
./syscall-profiler > /tmp/syscall-results.txt
cat /tmp/syscall-results.txt  # Verify content
```

---

## Step 9: Run Memory Monitor

**Duration**: 2-5 seconds
**Location**: MINIX serial console

Execute the memory monitor:

```bash
./memory-monitor
```

**Expected Output:**
```
MINIX Memory Monitor
====================

Memory info (if available)...

Process Information:
  PID: XXXX
  PPID: YYYY
  Working dir: /tmp
```

**Capture to File:**

```bash
./memory-monitor > /tmp/memory-results.txt
cat /tmp/memory-results.txt  # Verify content
```

---

## Step 10: Run Comprehensive Profiler Script

**Duration**: 10-30 seconds
**Location**: MINIX serial console

If you created the comprehensive profiler script, run it:

```bash
# Copy profiler script if not already in MINIX
cp /tmp/minix-cli-profiler.sh .
chmod +x minix-cli-profiler.sh

# Run all profiling
./minix-cli-profiler.sh all

# Or specific profiles
./minix-cli-profiler.sh syscalls
./minix-cli-profiler.sh memory
./minix-cli-profiler.sh network
./minix-cli-profiler.sh boot
```

**Output Location:**

Results saved to `/tmp/minix-measurements/`

```bash
ls -la /tmp/minix-measurements/
cat /tmp/minix-measurements/*.txt
```

---

## Step 11: Export Results to Host

**Duration**: 2-5 minutes
**Location**: MINIX serial console or new host terminal

### Option A: Via Serial Console (Easiest)

Copy text from MINIX terminal and save on host:

```bash
# In MINIX:
cat /tmp/syscall-results.txt
# Select all output and copy

# On host terminal:
cat > /tmp/minix-syscall-results.txt << 'EOF'
# Paste MINIX output here
EOF
```

### Option B: Via Network (If Configured)

```bash
# In MINIX:
# Start simple HTTP server or use nc to send data
(echo "HTTP/1.0 200 OK"; cat /tmp/syscall-results.txt) | nc -l 80 &

# On host:
curl http://192.168.122.x > /tmp/minix-syscall-results.txt
```

### Option C: Via File System Mount (If Supported)

Check if host filesystem accessible:

```bash
# In MINIX:
mount  # Shows mounted filesystems
ls /host  # Or check for shared mount point
```

---

## Step 12: Analyze Results on Host

**Duration**: 5-10 minutes
**Location**: Host terminal

Once results are on host, analyze them:

```bash
cd /tmp

# View syscall profiling results
cat minix-syscall-results.txt

# View memory profiling results
cat minix-memory-results.txt

# Compare multiple runs
diff minix-syscall-results-run1.txt minix-syscall-results-run2.txt

# Generate summary
echo "=== Profiling Summary ===" > minix-analysis-summary.txt
echo "" >> minix-analysis-summary.txt
echo "Syscall Data:" >> minix-analysis-summary.txt
head -20 minix-syscall-results.txt >> minix-analysis-summary.txt
echo "" >> minix-analysis-summary.txt
echo "Memory Data:" >> minix-analysis-summary.txt
head -20 minix-memory-results.txt >> minix-analysis-summary.txt

cat minix-analysis-summary.txt
```

---

## Step 13: Insert Results into SQLite Database

**Duration**: 5 minutes
**Location**: Host terminal

Store results for persistent tracking:

```bash
cd /home/eirikr/Playground/minix-analysis

# Create results table if not exists
sqlite3 measurements/minix-analysis.db << EOF
CREATE TABLE IF NOT EXISTS internal_measurements (
    id INTEGER PRIMARY KEY,
    measurement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    measurement_type TEXT,  -- 'syscall', 'memory', 'boot'
    metric_name TEXT,
    metric_value REAL,
    unit TEXT,
    notes TEXT
);

-- Insert syscall timing
INSERT INTO internal_measurements
  (measurement_type, metric_name, metric_value, unit, notes)
VALUES
  ('syscall', 'user_cpu_ticks', 1234, 'ticks', 'From profiler run'),
  ('syscall', 'system_cpu_ticks', 567, 'ticks', 'From profiler run'),
  ('memory', 'memory_available', 256, 'MB', 'From monitor run');

-- View results
SELECT * FROM internal_measurements ORDER BY measurement_date DESC LIMIT 10;
EOF

# Query results
sqlite3 measurements/minix-analysis.db \
  "SELECT measurement_type, metric_name, metric_value, unit FROM internal_measurements ORDER BY id DESC LIMIT 20;"
```

---

## Step 14: Shutdown MINIX Cleanly

**Duration**: 1-2 minutes
**Location**: MINIX serial console

Graceful shutdown:

```bash
# In MINIX console:
shutdown -h now

# Wait for shutdown message, then press Ctrl+D
```

Or force shutdown from host:

```bash
# On host terminal:
cd /home/eirikr/Playground/minix-analysis/dev-environment
./boot-minix-interactive.sh stop
```

---

## Complete Command Sequence (Copy-Paste Ready)

### Terminal 1: Setup and Boot

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
./setup-network.sh
./boot-minix-interactive.sh start
# MINIX is now running
```

### Terminal 2: Monitor Boot (Optional)

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
./boot-minix-interactive.sh logs-live
# Press Ctrl+C to stop (MINIX keeps running)
```

### Terminal 3: Connect to MINIX

```bash
cd /home/eirikr/Playground/minix-analysis/dev-environment
./boot-minix-interactive.sh connect
```

**Once connected to MINIX, execute:**

```bash
# Compile tools
gcc -o syscall-profiler /tmp/minix-syscall-profiler.c
gcc -o memory-monitor /tmp/minix-memory-monitor.c

# Run profilers
./syscall-profiler > /tmp/syscall-results.txt
./memory-monitor > /tmp/memory-results.txt

# View results
cat /tmp/syscall-results.txt
cat /tmp/memory-results.txt

# Shutdown
shutdown -h now
```

**Back on host, after MINIX shuts down:**

```bash
cd /tmp
# Results are in minix-interactive-TIMESTAMP.log files
ls -lh minix-interactive-*.log
# Extract measurement data as needed
```

---

## Troubleshooting Guide

### Network Setup Issues

**Problem**: "Device or resource busy" when running setup-network.sh
```bash
# Solution:
sudo ip tuntap del dev tap0 mode tap
./setup-network.sh  # Try again
```

**Problem**: MINIX can't reach host
```bash
# In MINIX, verify interface:
ifconfig de0
# Should show IP like 192.168.122.100

# Add route if needed:
route add default 192.168.122.1

# Test with pkgin (HTTP works, ping doesn't):
pkgin up
```

### Serial Console Issues

**Problem**: "Cannot connect to socket /tmp/minix-serial.sock"
```bash
# Solution: Restart MINIX
./boot-minix-interactive.sh stop
./boot-minix-interactive.sh start
sleep 2
./boot-minix-interactive.sh connect
```

**Problem**: No output in serial console
```bash
# Check boot log:
tail -100 minix-interactive-*.log

# Check MINIX process:
./boot-minix-interactive.sh status
```

### Compilation Issues

**Problem**: "gcc: command not found" in MINIX
```bash
# Solution: Install build tools
pkgin install gcc
# or
# Use pre-compiled binary if available
```

**Problem**: "No such file or directory" for syscall-profiler.c
```bash
# Verify source files exist:
ls /tmp/minix-*.c

# If missing, copy from host:
# (from host MINIX console)
cat /tmp/minix-syscall-profiler.c
# Copy output and paste into MINIX
```

---

## Best Practices (From Online Research)

1. **Use DHCP for Network Configuration**
   - MINIX RC3+ has netconf utility for easy setup
   - DHCP assigns 192.168.122.x addresses

2. **Test Network with HTTP**
   - QEMU user-mode doesn't support ICMP (ping fails)
   - Use `pkgin up` or HTTP requests to verify connectivity

3. **Use TAP for Meaningful Network Participation**
   - Preferred over user-mode networking
   - Allows bidirectional communication
   - Necessary for SSH, server access, etc.

4. **Serial Console for Measurement Collection**
   - Most reliable for capturing output
   - Works even if network fails
   - Use socat for persistent, bidirectional access

5. **TSC-Based Profiling**
   - MINIX supports Pentium TSC (Time-Stamp Counter)
   - More accurate than wall-clock for CPU measurements
   - Kernel has function to read TSC

6. **Process Tracing**
   - Use ptrace() interface (like strace)
   - Can monitor syscall frequencies
   - Useful for understanding workload patterns

---

## Next Steps

After completing measurement collection:

1. **Analyze Results**
   - Compare syscall profiles across runs
   - Identify hot paths and bottlenecks
   - Extract performance metrics

2. **Generate Reports**
   - Create summary statistics
   - Build performance charts (if visualization tools available)
   - Document findings

3. **Integrate with MCP**
   - Use GitHub MCP to create issues for anomalies
   - Use SQLite MCP to query measurements database
   - Automate issue creation for performance regressions

4. **Iterate**
   - Run multiple profiling sessions
   - Vary load conditions
   - Compare different MINIX configurations

---

## File Locations Summary

- **Dev Environment**: `/home/eirikr/Playground/minix-analysis/dev-environment/`
- **Boot Scripts**: `boot-minix-interactive.sh`, `boot-minix-dev.sh`, `boot-minix-iso.sh`
- **Network Setup**: `setup-network.sh`
- **ISO Image**: `/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso`
- **Measurement Tools**: `/tmp/minix-syscall-profiler.c`, `/tmp/minix-memory-monitor.c`
- **Profiler Script**: `/tmp/minix-cli-profiler.sh`
- **Results Database**: `/home/eirikr/Playground/minix-analysis/measurements/minix-analysis.db`

---

## See Also

- [Profiling Quick Start](PROFILING-QUICK-START.md) - CPU profiling tools setup
- [Runtime Setup Guide](RUNTIME-SETUP-GUIDE.md) - QEMU and Docker setup in detail
- [MCP Quick Start](MCP-QUICK-START.md) - Model Context Protocol integration
- [MCP Integration Guide](MCP-INTEGRATION-GUIDE.md) - Full MCP server integration

---

**Status**: Ready for Execution
**Last Updated**: 2025-11-01
**Estimated Completion**: 20-30 minutes from Step 1
