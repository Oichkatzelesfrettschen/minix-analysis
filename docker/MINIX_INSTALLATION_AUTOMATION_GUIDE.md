# MINIX 3.4 RC6 Installation Automation Guide

## Executive Summary

This guide provides a complete automated installation solution for MINIX 3.4 RC6 on QEMU, enabling non-interactive boot profiling and analysis. The automation uses Python with pexpect to interact with the MINIX installer via serial console.

## Installation Sequence Overview

### Complete Prompt Flow (Extracted from MINIX 3.4 setup.sh)

```
1. Boot Message → Press ENTER
2. Login: root → Press ENTER (no password)
3. Type: setup → Press ENTER
4. Keyboard type? [us-std] → Press ENTER (or type keyboard map)
5. Expert mode? → Press ENTER (automatic mode)
6. Select drive → Press ENTER (first drive)
7. Region selection → Type region number
8. Confirm partition: "yes" or "no" → Type: yes
9. Full or (R)einstall? [R] → Press ENTER (full install)
10. Home partition size (MB)? → Press ENTER (accept default)
11. Home size OK? [Y] → Press ENTER
12. Block size? [4] → Press ENTER
13. Wait for file copy (automatic)
14. Ethernet configuration → Press ENTER (skip or configure)
15. Type: shutdown → Press ENTER
16. Remove CD, boot from disk
```

### Timing Estimates

- **Boot to login**: 15-30 seconds
- **Setup initialization**: 5-10 seconds
- **Disk partitioning**: 10-20 seconds
- **File copy**: 60-180 seconds (depends on disk speed)
- **Total installation**: 2-5 minutes

## Automation Strategy

### Approach 1: pexpect with Serial Console (RECOMMENDED)

This method uses QEMU's `-serial stdio` to redirect the serial console to stdin/stdout, allowing pexpect to interact with the installer.

**Advantages:**
- Reliable text-based interaction
- Easy to debug (see all prompts)
- Works with headless QEMU
- No VNC or graphics needed

**Disadvantages:**
- MINIX must be configured to use serial console
- Some boot messages may not appear on serial

### Approach 2: QEMU Monitor sendkey Commands

Use QEMU's monitor interface to inject keyboard events directly to the VM.

**Advantages:**
- Works with standard graphical boot
- No serial console configuration needed

**Disadvantages:**
- Timing-sensitive (hard to sync with prompts)
- Requires VNC or SDL to verify state
- Less reliable for long installations

### Approach 3: Hybrid (pexpect + Monitor)

Combine serial console for prompts with sendkey for special keys (arrow keys, function keys).

**Advantages:**
- Best of both worlds
- Can handle complex interactions

**Disadvantages:**
- More complex implementation
- Two channels to coordinate

## Implementation: pexpect Automation Script

### Complete Python Automation Script

```python
#!/usr/bin/env python3
"""
MINIX 3.4 RC6 Automated Installation Script
Automates the MINIX installation process using pexpect and QEMU serial console.
"""

import pexpect
import sys
import time
import argparse
from pathlib import Path

class MinixInstaller:
    def __init__(self, iso_path, disk_image, disk_size="2G", memory="512M", timeout=600):
        self.iso_path = iso_path
        self.disk_image = disk_image
        self.disk_size = disk_size
        self.memory = memory
        self.timeout = timeout
        self.child = None

    def create_disk_image(self):
        """Create a blank disk image for installation."""
        print(f"[*] Creating {self.disk_size} disk image: {self.disk_image}")
        import subprocess
        subprocess.run([
            "qemu-img", "create", "-f", "qcow2",
            self.disk_image, self.disk_size
        ], check=True)

    def start_qemu(self):
        """Start QEMU with serial console enabled."""
        cmd = [
            "qemu-system-i386",
            "-m", self.memory,
            "-cdrom", self.iso_path,
            "-hda", self.disk_image,
            "-boot", "d",  # Boot from CD-ROM first
            "-serial", "stdio",  # Redirect serial to stdio
            "-nographic",  # No graphical window
            "-enable-kvm",  # Use KVM acceleration if available
        ]

        print(f"[*] Starting QEMU: {' '.join(cmd)}")
        self.child = pexpect.spawn(" ".join(cmd), encoding='utf-8', timeout=self.timeout)
        self.child.logfile_read = sys.stdout  # Echo all output

    def wait_and_send(self, pattern, response, timeout=None):
        """Wait for a pattern and send a response."""
        if timeout is None:
            timeout = self.timeout
        print(f"[*] Waiting for: {pattern}")
        self.child.expect(pattern, timeout=timeout)
        time.sleep(0.5)  # Small delay to avoid overwhelming serial
        print(f"[*] Sending: {response}")
        self.child.sendline(response)
        time.sleep(0.5)

    def install(self):
        """Execute the complete MINIX installation sequence."""
        try:
            # Step 1: Wait for boot and login prompt
            print("\n[STEP 1] Waiting for login prompt...")
            self.wait_and_send(r'(?i)login:', 'root', timeout=60)

            # Step 2: No password required, press enter
            print("\n[STEP 2] Bypassing password (press enter)...")
            time.sleep(2)
            self.child.sendline('')

            # Step 3: Wait for shell prompt and start setup
            print("\n[STEP 3] Starting setup...")
            self.wait_and_send(r'#', 'setup', timeout=10)

            # Step 4: Initial setup prompt (press enter to continue)
            print("\n[STEP 4] Confirming setup start...")
            self.wait_and_send(r'Press ENTER to continue', '', timeout=10)

            # Step 5: Keyboard selection (accept default)
            print("\n[STEP 5] Selecting keyboard (us-std)...")
            self.wait_and_send(r'Keyboard type\?', '', timeout=10)

            # Step 6: Partition mode (automatic, not expert)
            print("\n[STEP 6] Selecting automatic partition mode...")
            self.wait_and_send(r'expert', '', timeout=10)

            # Step 7: Select first drive (if prompted)
            print("\n[STEP 7] Selecting first drive...")
            # This step may vary - might auto-detect single drive
            try:
                self.wait_and_send(r'(?i)select.*drive', '1', timeout=5)
            except pexpect.TIMEOUT:
                print("[*] Drive auto-detected, continuing...")

            # Step 8: Confirm partition destruction
            print("\n[STEP 8] Confirming partition selection...")
            self.wait_and_send(r'(?i)yes.*no', 'yes', timeout=10)

            # Step 9: Full install (not reinstall)
            print("\n[STEP 9] Selecting full install...")
            self.wait_and_send(r'Full or.*Reinstall', '', timeout=10)

            # Step 10: Accept default home partition size
            print("\n[STEP 10] Accepting default home partition size...")
            self.wait_and_send(r'How big.*home', '', timeout=10)

            # Step 11: Confirm home size
            print("\n[STEP 11] Confirming home partition size...")
            self.wait_and_send(r'Ok\?', '', timeout=10)

            # Step 12: Accept default block size
            print("\n[STEP 12] Accepting default block size...")
            self.wait_and_send(r'Block size', '', timeout=10)

            # Step 13: Wait for file copying to complete
            print("\n[STEP 13] Waiting for file copy (may take 2-3 minutes)...")
            self.wait_and_send(r'(?i)copy.*complete|(?i)installation.*complete', '', timeout=300)

            # Step 14: Skip ethernet configuration (or configure if needed)
            print("\n[STEP 14] Skipping ethernet configuration...")
            try:
                self.wait_and_send(r'(?i)ethernet', '', timeout=10)
            except pexpect.TIMEOUT:
                print("[*] No ethernet prompt, continuing...")

            # Step 15: Shutdown the system
            print("\n[STEP 15] Shutting down installer...")
            self.wait_and_send(r'#', 'shutdown', timeout=10)

            # Wait for shutdown to complete
            print("\n[*] Waiting for shutdown...")
            time.sleep(5)

            print("\n[SUCCESS] Installation completed successfully!")
            return True

        except pexpect.TIMEOUT as e:
            print(f"\n[ERROR] Timeout waiting for prompt: {e}")
            print(f"[DEBUG] Last output: {self.child.before}")
            return False
        except pexpect.EOF as e:
            print(f"\n[ERROR] Unexpected EOF: {e}")
            return False
        except Exception as e:
            print(f"\n[ERROR] Installation failed: {e}")
            return False
        finally:
            if self.child:
                self.child.close()

    def boot_installed_system(self):
        """Boot the installed MINIX system (without CD-ROM)."""
        cmd = [
            "qemu-system-i386",
            "-m", self.memory,
            "-hda", self.disk_image,
            "-boot", "c",  # Boot from hard disk
            "-serial", "stdio",
            "-nographic",
            "-enable-kvm",
        ]

        print(f"\n[*] Booting installed system: {' '.join(cmd)}")
        self.child = pexpect.spawn(" ".join(cmd), encoding='utf-8', timeout=self.timeout)
        self.child.logfile_read = sys.stdout

        # Wait for login prompt
        print("\n[*] Waiting for boot to complete...")
        self.child.expect(r'(?i)login:', timeout=120)
        print("\n[SUCCESS] System booted successfully!")

        # Login
        self.child.sendline('root')
        time.sleep(1)
        self.child.sendline('')  # No password

        # Interactive mode
        print("\n[*] Entering interactive mode. Press Ctrl+] to exit.")
        self.child.interact()

def main():
    parser = argparse.ArgumentParser(description="Automated MINIX 3.4 RC6 Installation")
    parser.add_argument("--iso", required=True, help="Path to MINIX ISO file")
    parser.add_argument("--disk", required=True, help="Path to output disk image")
    parser.add_argument("--size", default="2G", help="Disk size (default: 2G)")
    parser.add_argument("--memory", default="512M", help="RAM allocation (default: 512M)")
    parser.add_argument("--boot", action="store_true", help="Boot installed system after install")
    parser.add_argument("--no-create", action="store_true", help="Don't create disk (use existing)")

    args = parser.parse_args()

    # Verify ISO exists
    if not Path(args.iso).exists():
        print(f"[ERROR] ISO file not found: {args.iso}")
        sys.exit(1)

    # Create installer
    installer = MinixInstaller(
        iso_path=args.iso,
        disk_image=args.disk,
        disk_size=args.size,
        memory=args.memory
    )

    # Create disk image if needed
    if not args.no_create:
        installer.create_disk_image()

    # Start QEMU and install
    installer.start_qemu()
    success = installer.install()

    if not success:
        print("\n[ERROR] Installation failed!")
        sys.exit(1)

    # Boot installed system if requested
    if args.boot:
        print("\n[*] Proceeding to boot installed system...")
        time.sleep(2)
        installer.boot_installed_system()

if __name__ == "__main__":
    main()
```

### Usage Examples

```bash
# Basic installation
python3 minix_auto_install.py \
    --iso /home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix_installed.qcow2

# Installation with custom settings
python3 minix_auto_install.py \
    --iso minix.iso \
    --disk minix_4gb.qcow2 \
    --size 4G \
    --memory 1G \
    --boot

# Use existing disk (reinstall)
python3 minix_auto_install.py \
    --iso minix.iso \
    --disk existing_disk.qcow2 \
    --no-create \
    --boot
```

## Alternative: QEMU Monitor sendkey Method

### Using QEMU Monitor for Keyboard Automation

```python
#!/usr/bin/env python3
"""
MINIX Installation using QEMU Monitor sendkey commands
"""

import subprocess
import time
import socket

class QEMUMonitor:
    def __init__(self, monitor_socket="/tmp/qemu-monitor.sock"):
        self.socket_path = monitor_socket
        self.sock = None

    def connect(self):
        """Connect to QEMU monitor socket."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)
        # Read initial prompt
        self.sock.recv(1024)

    def send_command(self, cmd):
        """Send a command to QEMU monitor."""
        self.sock.sendall(f"{cmd}\n".encode())
        time.sleep(0.1)
        response = self.sock.recv(4096).decode()
        return response

    def sendkey(self, key, hold_time=0.1):
        """Send a single key press."""
        self.send_command(f"sendkey {key}")
        time.sleep(hold_time)

    def type_string(self, text, delay=0.1):
        """Type a string character by character."""
        for char in text:
            if char == ' ':
                self.sendkey('spc', delay)
            elif char.isupper():
                # Send shift + key
                self.sendkey(f"shift-{char.lower()}", delay)
            else:
                self.sendkey(char, delay)

def start_qemu_with_monitor(iso_path, disk_path, monitor_socket="/tmp/qemu-monitor.sock"):
    """Start QEMU with monitor enabled."""
    cmd = [
        "qemu-system-i386",
        "-m", "512M",
        "-cdrom", iso_path,
        "-hda", disk_path,
        "-boot", "d",
        "-monitor", f"unix:{monitor_socket},server,nowait",
        "-vnc", ":0",  # VNC for visual feedback
    ]

    proc = subprocess.Popen(cmd)
    time.sleep(5)  # Wait for QEMU to start
    return proc

def automate_with_sendkey(iso_path, disk_path):
    """Automate MINIX installation using sendkey."""
    monitor_socket = "/tmp/qemu-monitor.sock"

    # Start QEMU
    proc = start_qemu_with_monitor(iso_path, disk_path, monitor_socket)

    # Connect to monitor
    mon = QEMUMonitor(monitor_socket)
    mon.connect()

    # Wait for boot
    time.sleep(30)

    # Login as root
    mon.type_string("root")
    mon.sendkey("ret")  # Enter
    time.sleep(2)
    mon.sendkey("ret")  # No password

    # Start setup
    time.sleep(3)
    mon.type_string("setup")
    mon.sendkey("ret")

    # Continue with installation steps...
    # (Similar sequence to pexpect version)

    print("[*] Installation script running...")
    time.sleep(300)  # Wait for installation

    proc.wait()

# Usage
automate_with_sendkey(
    "/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso",
    "minix_installed.qcow2"
)
```

## QEMU Command Reference

### Installation Phase

```bash
# Create disk image
qemu-img create -f qcow2 minix_installed.qcow2 2G

# Run installer with serial console
qemu-system-i386 \
    -m 512M \
    -cdrom minix_R3.4.0rc6-d5e4fc0.iso \
    -hda minix_installed.qcow2 \
    -boot d \
    -serial stdio \
    -nographic \
    -enable-kvm

# Run installer with VNC and monitor
qemu-system-i386 \
    -m 512M \
    -cdrom minix_R3.4.0rc6-d5e4fc0.iso \
    -hda minix_installed.qcow2 \
    -boot d \
    -monitor unix:/tmp/qemu-monitor.sock,server,nowait \
    -vnc :0
```

### Boot Profiling Phase

```bash
# Boot installed system for profiling
qemu-system-i386 \
    -m 512M \
    -hda minix_installed.qcow2 \
    -boot c \
    -serial stdio \
    -nographic \
    -enable-kvm \
    -trace events=trace_events.txt  # Optional: trace boot events
```

## Troubleshooting

### Common Issues

**Issue 1: Serial console not working**
- Ensure MINIX is configured to use serial console (default in recent versions)
- Check QEMU output for errors
- Try increasing timeout values

**Issue 2: pexpect timeout during file copy**
- File copy can take 2-5 minutes depending on disk speed
- Increase timeout to 300+ seconds for this step
- Monitor progress via VNC in parallel

**Issue 3: Unexpected prompts or variations**
- MINIX setup script may vary between versions
- Add debug logging: `self.child.logfile_read = open('install.log', 'w')`
- Use more flexible regex patterns

**Issue 4: Installation succeeds but system won't boot**
- Verify disk image was created successfully: `qemu-img info minix_installed.qcow2`
- Try booting with `-boot menu=on` to select boot device
- Check GRUB/bootloader installation in setup logs

### Debug Mode

Enable verbose logging:

```python
# Add to MinixInstaller.__init__
self.debug_log = open('minix_install_debug.log', 'w')
self.child.logfile_read = self.debug_log
self.child.logfile_send = self.debug_log
```

## Integration with Boot Profiler

Once installation is automated, integrate with boot profiler:

```bash
#!/bin/bash
# complete_boot_profiling_pipeline.sh

ISO_PATH="/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso"
DISK_PATH="minix_profile_disk.qcow2"

# Step 1: Automated installation
python3 minix_auto_install.py \
    --iso "$ISO_PATH" \
    --disk "$DISK_PATH" \
    --size 2G \
    --memory 512M

# Step 2: Boot profiling
python3 boot_profiler.py \
    --disk "$DISK_PATH" \
    --output boot_profile.json \
    --iterations 10

# Step 3: Analysis
python3 analyze_boot_profile.py \
    --input boot_profile.json \
    --output boot_analysis_report.md
```

## Performance Considerations

- **KVM acceleration**: Essential for reasonable installation time (2-5 min vs 10-20 min)
- **Disk format**: qcow2 with lazy allocation is fastest for initial install
- **Memory allocation**: 512M minimum, 1G recommended for stability
- **Serial delay**: Add 0.5s delays between sendline() calls to avoid overwhelming MINIX

## Next Steps

1. Test the pexpect script on your system
2. Adjust timeouts and patterns based on actual installation behavior
3. Add error recovery (retry on timeout, skip optional steps)
4. Integrate with boot profiler workflow
5. Document any version-specific variations in setup prompts

## References

- MINIX 3 Installation Guide: https://wiki.minix3.org/doku.php?id=usersguide:doinginstallation
- MINIX setup.sh source: https://github.com/jncraton/minix3/blob/master/commands/scripts/setup.sh
- QEMU Monitor Protocol: https://en.wikibooks.org/wiki/QEMU/Monitor
- pexpect Documentation: https://pexpect.readthedocs.io/
