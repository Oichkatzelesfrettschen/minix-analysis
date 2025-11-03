# MINIX 3 QEMU Boot Error Registry and Solutions

**Last Updated**: 2025-11-01
**MINIX Version**: 3.4.0 RC6
**Architecture**: i386 (x86)
**Scope**: Common errors encountered when running MINIX in QEMU with detailed fixes

---

## Quick Reference Table

| Error | Symptom | Root Cause | Solution | Difficulty |
|-------|---------|-----------|----------|------------|
| Blank Screen | QEMU window blank after 10s | Display server not initialized | Add `-sdl` parameter | Easy |
| SeaBIOS Hang | Stuck at "SeaBIOS" message | CPU incompatibility | Use `-cpu kvm32` | Easy |
| CD9660 Module Failure | "failed to load cd9660" then hang | Interactive ISO, no serial console | Build from source or use pre-built disk | Hard |
| Active Partition Error | "Active partition not found" | MINIX doesn't support USB installation | Use QEMU on Linux to create disk | Medium |
| AHCI Not Found | "Trying /dev/c1d4 Not found" | QEMU Q35 doesn't implement AHCI spec | Switch to IDE (`-drive file=...,if=ide`) | Medium |
| IRQ Check Failed | "do_irqctl: IRQ check failed" | Ethernet driver IRQ mismatch | Configure NE2K IRQ and I/O base | Medium |
| Memory Allocation Error | "malloc failed" or X11 crash | Insufficient VM memory | Increase `-m` or use `chmem` on binaries | Medium |
| Network Not Working | ping/networking fails post-install | NE2K driver not configured | Configure `/usr/etc/rc.local` with DPETH0 params | Medium |
| Boot from Disk Fails | Boots BIOS, no kernel load | Disk partition table corrupt or GRUB missing | Use `-boot c` and verify partition table | Hard |
| Shell Timeout | Installer runs but no shell prompt | MINIX waiting for input or slow disk | Increase timeout, check for prompts | Easy |
| Kernel Panic | MINIX boots then crashes immediately | Module load failure or hardware mismatch | Check boot parameters and module availability | Hard |
| Disk I/O Error | "Error reading from disk" | QEMU disk emulation issue | Use `-drive format=raw` instead of qcow2 | Medium |
| TTY Errors | "Couldn't obtain hook for irq" | IRQ/TTY device conflict | Reset IRQ assignments, use `-net nic,model=ne2k_isa,irq=3` | Hard |
| VNC Connection Fails | VNC client can't connect | VNC server not started in QEMU | Add `-vnc :0` or similar to QEMU command | Easy |
| SSH Timeout | SSH to MINIX port times out | Port forwarding not configured or SSH daemon not running | Use `-net user,hostfwd=tcp::10022-:22` | Easy |

---

## Detailed Error Solutions

### Error 1: Blank Screen / No Output

**Symptom**: QEMU window appears blank, no text output after 10-20 seconds

**Affected Versions**: MINIX 3.3+, QEMU 5.0+

**Root Cause**: Display server initialization failure or missing graphics drivers

**Solutions**:

**Solution 1A (Recommended)**: Use SDL display
```bash
qemu-system-i386 -m 512M -cdrom minix.iso -hda minix.img -boot d -sdl
```

**Solution 1B**: Use VNC display
```bash
qemu-system-i386 -m 512M -cdrom minix.iso -hda minix.img -boot d -vnc :0
# Connect from another terminal: vncviewer localhost:5900
```

**Solution 1C**: Use serial console (best for automation)
```bash
qemu-system-i386 -m 512M -cdrom minix.iso -hda minix.img -boot d \
  -serial file:boot.log -nographic
```

**Solution 1D**: Enable graphics with SPICE
```bash
qemu-system-i386 -m 512M -cdrom minix.iso -hda minix.img -boot d \
  -spice port=5930,disable-ticketing=on -device QXL
```

**Prevention**: Test display option before long runs. Default to `-nographic -serial file:boot.log` for headless servers.

---

### Error 2: SeaBIOS Hang

**Symptom**: Boot output shows "SeaBIOS vX.X.X" but never proceeds, hangs indefinitely

**Affected Versions**: MINIX 3.3 with certain QEMU + CPU combinations

**Root Cause**: CPU incompatibility (SeaBIOS may not recognize CPU or have initialization bug)

**Solutions**:

**Solution 2A (Recommended)**: Use kvm32 CPU model
```bash
qemu-system-i386 -m 512M -cpu kvm32 -cdrom minix.iso -hda minix.img -boot d
```

**Solution 2B**: Use different CPU model
```bash
# Try these in order:
qemu-system-i386 -cpu 486 ...        # Safest (slowest)
qemu-system-i386 -cpu pentium ...    # Common
qemu-system-i386 -cpu host ...       # Fastest (may not work)
```

**Solution 2C**: Disable KVM acceleration
```bash
qemu-system-i386 -m 512M -cdrom minix.iso -hda minix.img -boot d
# (omit -enable-kvm)
```

**Solution 2D**: Upgrade SeaBIOS
- Check QEMU version: `qemu-system-i386 --version`
- Update QEMU: `pacman -Syu qemu`
- SeaBIOS typically bundled with QEMU

**Solution 2E**: Update MINIX firmware
- Download latest MINIX: https://www.minix3.org/download
- Use RC (Release Candidate) instead of Stable if available

**Prevention**: Test with `-cpu kvm32` first, then test with `-cpu host` for performance.

---

### Error 3: CD9660 Module Load Failure (CRITICAL)

**Symptom**: 
```
Loading cd9660 module...
mount: cd9660 mount failed (error 1)
cd9660 module load failed
[MINIX freezes or times out]
```

**Affected Versions**: MINIX 3.3.0, 3.4.0 RC1-RC5 (FIXED in RC6+)

**Root Cause**: Interactive ISO doesn't configure serial console; MINIX kernel can't load cd9660 module in some QEMU configurations

**Solutions**:

**Solution 3A (Recommended)**: Use MINIX RC6 or later
```bash
# Download from: https://www.minix3.org/download
# Release: MINIX 3.4.0 RC6 (or later)
minix_R3.4.0rc6-d5e4fc0.iso  # ← Known to work
```

**Solution 3B**: Build MINIX from source
```bash
cd /home/eirikr/Playground/minix
./build.sh -m i386 -a i386 build distribution
# Creates bootable disk image with cd9660 pre-loaded
```

**Solution 3C**: Use pre-built disk image instead of ISO
```bash
# After building or obtaining minix_x86.img:
qemu-system-i386 -m 512M -hda minix_x86.img -boot c \
  -serial file:boot.log -nographic
```

**Solution 3D (Workaround)**: Skip ISO, manually install
```bash
# Boot live Linux, compile MINIX tools in container, install manually
# (Last resort, not recommended)
```

**Prevention**: Always use latest RC or stable build. If using ISO, immediately switch to built disk image after first successful boot.

---

### Error 4: "Active Partition" Installation Error

**Symptom**:
```
Installation starts
[some prompts answered]
ERROR: Active partition not found
Installation fails
```

**Affected Versions**: All MINIX versions when installing via USB from non-Unix system

**Root Cause**: MINIX installation script expects DOS/MBR partition table structure. Windows/macOS USB tools create incompatible partition layout.

**Solutions**:

**Solution 4A (Recommended)**: Use QEMU on Linux as intermediary
```bash
# On Linux system (any distro):

# 1. Create disk image for MINIX
qemu-img create -f qcow2 minix_disk.qcow2 2G

# 2. Install via QEMU
qemu-system-i386 -m 512M \
  -cdrom minix_R3.4.0rc6.iso \
  -hda minix_disk.qcow2 \
  -boot d \
  -serial stdio

# 3. Complete installation when prompted
# 4. Extract or convert image for USB use if needed
```

**Solution 4B**: Use Linux live USB (alternative)
```bash
# 1. Create Ubuntu/Fedora live USB (standard procedure)
# 2. Boot into live Linux
# 3. Install QEMU on live system
# 4. Follow Solution 4A from there
```

**Solution 4C**: Use Docker (simplest)
```bash
cd /home/eirikr/Playground/minix-analysis
docker-compose -f docker-compose.enhanced.yml up minix-i386
# Installation happens inside container, persistent disk image created
```

**Prevention**: Never attempt MINIX installation from Windows/macOS USB. Always use Linux system or QEMU container.

---

### Error 5: "Trying /dev/c1d4 Not Found" (AHCI Boot)

**Symptom**:
```
MINIX boot menu shows options:
1. IDE
2. AHCI
3. SCSI

Select option: 2 (AHCI)

[Boot starts]
Trying /dev/c1d4...
ERROR: Not found. No CD found.
Boot fails
```

**Affected Versions**: All MINIX versions with QEMU Q35 chipset

**Root Cause**: QEMU Q35 chipset doesn't fully implement AHCI spec. Specifically missing PCS (Port Connect Status) interrupt that MINIX AHCI driver depends on.

**Solutions**:

**Solution 5A (Recommended)**: Avoid AHCI, use IDE
```bash
# At boot menu, select option 1 (IDE) instead of AHCI
# Or suppress menu and force IDE:
qemu-system-i386 -m 512M \
  -hda minix.img \
  -boot c \
  -drive file=minix.img,if=ide \
  -nographic -serial stdio
```

**Solution 5B**: Use i440FX chipset (not Q35)
```bash
# QEMU default before Q35:
qemu-system-i386 -m 512M \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d \
  # (Q35 not enabled by default)
```

**Solution 5C**: Disable AHCI in boot.cfg
```bash
# After MINIX is installed (boot from IDE first):
# Edit /etc/boot.cfg to remove AHCI option

# Or create /etc/boot.cfg.local:
# menu=Start MINIX 3:multiboot /boot/minix_default/kernel \
#   rootdevname=c0d0p0 console=tty00 consdev=com0
```

**Solution 5D**: Workaround - Hybrid IDE/AHCI
```bash
# Install with IDE, then add AHCI support manually
# (Advanced, not recommended for typical use)
```

**Prevention**: Always choose IDE (option 1) at MINIX boot menu when running on QEMU. AHCI is optional for QEMU use.

---

### Error 6: "do_irqctl: IRQ check failed" / "Couldn't obtain hook for irq"

**Symptom**:
```
[Boot proceeds normally]
[Keyboard input: none]
ERROR: do_irqctl: IRQ check failed
ERROR: Couldn't obtain hook for irq
[System hangs or shell doesn't appear]
```

**Affected Versions**: All MINIX versions, typically during NE2K ethernet initialization

**Root Cause**: Ethernet driver (NE2K) configured with incorrect IRQ or I/O base address. Common default conflicts with other devices.

**Solutions**:

**Solution 6A (Recommended)**: Use correct NE2K parameters
```bash
# At installation, select NE2K Ethernet
# During RC local configuration, use these parameters:
# IRQ: 3 (instead of default 11)
# I/O base: 0x300 (standard for ISA cards)

# In /usr/etc/rc.local:
DPETH0=300:3
export DPETH0

# Or at QEMU launch:
qemu-system-i386 -m 512M \
  -hda minix.img \
  -net user \
  -net nic,model=ne2k_isa,netdev=net0,irq=3,iobase=0x300 \
  -boot c -serial stdio -nographic
```

**Solution 6B**: Use virtio network (modern alternative)
```bash
# For MINIX 3.4+:
qemu-system-i386 -m 512M \
  -hda minix.img \
  -net user \
  -net nic,model=virtio \
  -boot c -serial stdio -nographic
```

**Solution 6C**: Skip ethernet during installation
```bash
# At "Ethernet configuration?" prompt during setup:
# Press ENTER or answer "no"
# Configure networking manually after boot:
# /usr/etc/rc.local → add DPETH0=300:3
```

**Solution 6D**: Use different IRQ
```bash
# If IRQ 3 conflicts, try:
# IRQ 5, 7, 9, 10, 12, 14, 15 (ISA standard)
# Test each until one works:
qemu-system-i386 -net nic,model=ne2k_isa,irq=5,iobase=0x300 ...
```

**Prevention**: During MINIX installation:
1. Choose NE2K as ethernet device
2. At IRQ prompt, use IRQ 3 (not default 11)
3. At I/O prompt, use 0x300 (standard ISA)
4. Test with: `ifconfig ne2k0` and `ping 8.8.8.8`

---

### Error 7: X11 Memory Allocation Failure

**Symptom**:
```
[Boot proceeds to shell]
$ X
X: memory allocation failed
[X11 server crashes]

OR

$ twm
[Window manager crashes with memory error]
```

**Affected Versions**: All MINIX with X11, especially on < 256MB VM

**Root Cause**: X11 server (/usr/X11R6/bin/Xorg or Xvfb) requests more memory than VM has. MINIX lacks virtual memory, so request must fit in physical RAM.

**Solutions**:

**Solution 7A (Recommended)**: Increase VM memory
```bash
# In docker-compose.enhanced.yml or QEMU launch:
qemu-system-i386 -m 512M ...        # Minimum for X11
qemu-system-i386 -m 1024M ...       # Recommended
qemu-system-i386 -m 2048M ...       # For complex X apps
```

**Solution 7B**: Reduce X11 memory requirements
```bash
# After MINIX boots:
chmem =67108864 /usr/X11R6/bin/Xorg    # 64MB for X
chmem =33554432 /usr/X11R6/bin/twm     # 32MB for twm

# Or even lower:
chmem =50000000 /usr/X11R6/bin/Xorg    # ~50MB
chmem =25000000 /usr/X11R6/bin/twm     # ~25MB

# Start X11:
startx

# Check memory used:
ps aux | grep X
free
```

**Solution 7C**: Use minimal X11 configuration
```bash
# Edit /etc/X11/Xwm.conf to use smaller window manager
# or start with just X: X & (no window manager initially)
```

**Solution 7D**: Check current binary memory needs
```bash
# See what chmem currently allows:
chmem /usr/X11R6/bin/Xorg

# Output shows current header stack allocation
# Increase incrementally until X11 starts
```

**chmem Usage Reference**:
```
chmem [=value] <binary>
  value = 0xHEXADECIMAL (hex bytes)
  value = DECIMAL (decimal bytes)
  
Examples:
  chmem =80000000 /usr/X11R6/bin/Xorg    # 0x80000000 = 2048 MB (header value)
  chmem =40000000 /usr/X11R6/bin/Xorg    # 0x40000000 = 1024 MB
  chmem =20000000 /usr/X11R6/bin/Xorg    # ~268 MB
  chmem =10000000 /usr/X11R6/bin/Xorg    # ~134 MB
  chmem =8000000 /usr/X11R6/bin/Xorg     # ~67 MB
```

**Prevention**: 
- Always allocate ≥512MB RAM for MINIX instances planning to use X11
- Test X11 startup immediately after boot
- Use `chmem` before X11 needs memory

---

### Error 8: Network Not Working Post-Install

**Symptom**:
```
[MINIX boots successfully]
$ ping 8.8.8.8
PING: routing error
[No response from network]

$ ifconfig
ne2k0: flags=... (shows device)
[but no IP or "UP" flag]
```

**Affected Versions**: All MINIX versions with NE2K driver

**Root Cause**: Network device configured but not initialized. MINIX RC scripts didn't start networking daemon or DHCP.

**Solutions**:

**Solution 8A (Recommended)**: Configure /usr/etc/rc.local
```bash
# Edit /usr/etc/rc.local
# Add these lines:

DPETH0=300:3
export DPETH0

# Start ethernet daemon
/usr/etc/inet.conf

# Configure IP (DHCP)
service dhcp start

# Or static IP:
ifconfig ne2k0 192.168.1.10
route add default 192.168.1.1
```

**Solution 8B**: Manual network configuration
```bash
# From MINIX shell:

# Identify device
ifconfig -a

# Bring up ethernet
ifconfig ne2k0 192.168.1.10/24 up

# Add default route
route add default 192.168.1.1

# Test
ping 192.168.1.1     # Gateway
ping 8.8.8.8         # Internet

# Check DNS
cat /etc/resolv.conf
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

**Solution 8C**: Use QEMU user-mode networking
```bash
# QEMU user networking provides built-in DHCP/DNS
# Make sure QEMU has correct parameters:

qemu-system-i386 \
  -net user \                          # Enable user networking
  -net nic,model=ne2k_isa,irq=3 \      # Connect NE2K to user network
  -hda minix.img -boot c

# In MINIX:
dhcp ne2k0          # Request IP from QEMU DHCP
ping 8.8.8.8        # Should work
```

**Solution 8D**: Forward host network to MINIX
```bash
# If MINIX network still doesn't work, try tap mode (advanced)
# or use port forwarding:

qemu-system-i386 \
  -net user,hostfwd=tcp::2222-:22 \        # SSH from host
  -net nic,model=ne2k_isa \
  -hda minix.img -boot c

# From host:
ssh -p 2222 root@localhost
```

**Prevention**: During MINIX installation, let setup script configure NE2K. After boot, immediately test networking with `ifconfig` and `ping`.

---

### Error 9: Boot from Disk Fails

**Symptom**:
```
[No MINIX banner]
[Seaboot or ROM BIOS menu appears]
Boot from CD? (Y/N) y
[or]
Boot sector not found
[MINIX never starts]
```

**Affected Versions**: All MINIX after disk image becomes corrupted or partitioning fails

**Root Cause**: 
1. Boot partition not marked active
2. Disk partition table corrupted
3. Boot sector (MBR) missing or invalid
4. Wrong boot order in QEMU

**Solutions**:

**Solution 9A (Recommended)**: Force boot from disk with correct parameters
```bash
qemu-system-i386 -m 512M \
  -hda minix.img \
  -boot c \              # Boot from hard disk (c=disk, d=CDROM)
  -nographic -serial stdio
```

**Solution 9B**: Rebuild disk image from scratch
```bash
# Delete corrupted image
rm minix.img

# Create new disk
qemu-img create -f qcow2 minix.img 2G

# Reinstall from ISO
qemu-system-i386 -m 512M \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d
```

**Solution 9C**: Verify disk integrity
```bash
# Check if MINIX filesystem is on disk
qemu-img info minix.img          # Check format, size
file minix.img                   # Check file type

# Mount disk locally (if qcow2):
qemu-nbd -c /dev/nbd0 minix.img
mount /dev/nbd0p1 /mnt/minix
ls /mnt/minix
umount /mnt/minix
qemu-nbd -d /dev/nbd0
```

**Solution 9D**: Fix boot partition
```bash
# Boot from ISO in rescue mode
qemu-system-i386 -m 512M \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d

# At boot menu, select "Recovery" or enter shell
# Mark partition active:
fdisk /dev/c0d0
# a (toggle active boot flag)
# p (print partition table - verify c0d0p0 is active)
# w (write and exit)

# Reboot
```

**Prevention**: After successful MINIX installation, immediately test disk boot with `-boot c` before moving image or making other changes.

---

### Error 10: Shell Timeout / Installer Never Completes

**Symptom**:
```
[MINIX installation running]
[No new prompts appear for > 60 seconds]
[Process hangs]
timeout: timeout reached
[Process killed]
```

**Affected Versions**: All MINIX with slow disks or complex installations

**Root Cause**: 
1. File copy phase takes longer than expected
2. Disk I/O very slow
3. Installer waiting for input (prompt not visible)
4. Process truly stuck

**Solutions**:

**Solution 10A (Recommended)**: Increase timeout
```bash
# In test-minix-qemu-direct.sh or Docker compose:
timeout 600 qemu-system-i386 ...    # 10 minutes instead of 180 seconds

# For interactive installation:
# Shell waits for return value, increase to 300-600 seconds
```

**Solution 10B**: Check for hidden prompts
```bash
# Run with serial console logging
qemu-system-i386 \
  -serial file:install.log \
  -m 512M \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d \
  -nographic &

# In another terminal, monitor log
tail -f install.log

# Look for prompts: "?" or "[" brackets, ":" prompts
```

**Solution 10C**: Use VNC to monitor visually
```bash
qemu-system-i386 \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d \
  -vnc :0

# Connect: vncviewer localhost:5900
# Watch installation progress visually
```

**Solution 10D**: Enable verbose QEMU output
```bash
qemu-system-i386 \
  -d trace:qemu_start \        # Debug trace
  -serial file:trace.log \
  -cdrom minix.iso \
  -hda minix.img \
  -boot d 2>&1 | tee qemu.log
```

**Prevention**: 
- Use faster disk (SSD, not HDD)
- Monitor first installation with VNC
- Use reasonable timeout (300s minimum for file copy phase)
- Consider parallel testing with copy-on-write snapshots

---

### Error 11: Kernel Panic

**Symptom**:
```
[Boot messages appear]
Kernel initialization starts
[specific kernel messages]
PANIC: [error message]
[MINIX halts]
```

**Affected Versions**: All MINIX when hardware/module mismatch occurs

**Root Cause**:
1. Module load failure (cd9660, ne2k driver)
2. Memory allocation in kernel
3. CPU feature not supported
4. Interrupt controller not responding

**Solutions**:

**Solution 11A (Recommended)**: Check boot parameters
```bash
# Review which modules load before panic
# Look for module load messages in boot.log

# Add debugging:
qemu-system-i386 -m 512M \
  -serial file:panic.log \
  -hda minix.img \
  -boot c \
  -nographic

# Examine log for module warnings:
grep -i "module\|error\|panic" panic.log
```

**Solution 11B**: Reduce CPU features
```bash
qemu-system-i386 \
  -cpu 486 \                    # Safest, slowest
  -hda minix.img -boot c

# If 486 works, try:
qemu-system-i386 -cpu pentium ...
qemu-system-i386 -cpu kvm32 ...
```

**Solution 11C**: Increase memory
```bash
# Panic might be from heap exhaustion
qemu-system-i386 -m 1G \         # More RAM
  -hda minix.img -boot c
```

**Solution 11D**: Disable optional features
```bash
# Edit boot.cfg to remove optional modules
# Look for lines with module* entries
# Comment out non-essential ones
```

**Prevention**: Test boot after each change. Save known-good configurations.

---

### Error 12: Disk I/O Error

**Symptom**:
```
[Any phase]
ERROR: Error reading from disk
ERROR: read() failed
I/O error
[Process fails or hangs]
```

**Affected Versions**: All MINIX with disk-based operations

**Root Cause**:
1. QEMU disk emulation issue with qcow2 format
2. Raw format incompatible with certain block operations
3. Disk image corruption

**Solutions**:

**Solution 12A (Recommended)**: Use raw format
```bash
# Create raw image instead of qcow2
qemu-img create -f raw minix.img 2G

# Or convert existing:
qemu-img convert -f qcow2 -O raw minix.qcow2 minix.img

# Boot with:
qemu-system-i386 \
  -drive file=minix.img,format=raw,media=disk \
  -boot c
```

**Solution 12B**: Use qcow2 with explicit format flag
```bash
qemu-system-i386 \
  -drive file=minix.qcow2,format=qcow2,media=disk \
  -boot c
```

**Solution 12C**: Check disk image health
```bash
# Verify image file
qemu-img check minix.img         # Shows errors/corruption

# Try repair (experimental)
qemu-img check -r all minix.img

# Rebuild from scratch if corrupted:
qemu-img create -f raw minix.img 2G
# [reinstall]
```

**Solution 12D**: Reduce disk size
```bash
# Try smaller disk (simpler filesystem operations)
qemu-img create -f raw minix.img 1G

# Full install still fits:
# / = 100MB
# /home = 400MB
# /usr = 300MB
```

**Prevention**: Use raw format for development, qcow2 for snapshots only. Monitor disk health regularly.

---

### Error 13: TTY Device Conflicts

**Symptom**:
```
[Boot proceeds]
[Keyboard input doesn't work]
ERROR: TTY: /dev/tty1 not responding
ERROR: device initialization failed
[or]
All TTY devices disabled
```

**Affected Versions**: MINIX 3.3-3.4 with certain input device configurations

**Root Cause**: Serial console conflict with TTY0, or TTY device not initialized

**Solutions**:

**Solution 13A (Recommended)**: Use serial-only console
```bash
# In boot.cfg or kernel parameters:
console=tty00
consdev=com0

# QEMU command:
qemu-system-i386 \
  -serial stdio \
  -nographic \
  -hda minix.img
```

**Solution 13B**: Reset TTY configuration
```bash
# After MINIX boots (if possible):
# Edit /etc/inittab to disable extra TTYs:
# Comment out lines for tty01-tty04

# Or rebuild kernel with fewer TTYs
```

**Solution 13C**: Use VNC instead of serial
```bash
# If serial causes TTY conflict:
qemu-system-i386 \
  -vnc :0 \
  -hda minix.img \
  -boot c
# No serial console conflicts
```

**Prevention**: Configure serial-only console during MINIX build if automating installation.

---

### Error 14: VNC Connection Fails

**Symptom**:
```
$ vncviewer localhost:5900
VNC: connection refused
VNC: connection timeout
VNC: unable to connect
```

**Affected Versions**: All MINIX when using VNC for graphical boot monitoring

**Root Cause**: VNC server not started in QEMU, or wrong port

**Solutions**:

**Solution 14A (Recommended)**: Ensure VNC is enabled
```bash
qemu-system-i386 \
  -vnc :0 \                        # Enable VNC on port 5900
  -hda minix.img \
  -boot c
```

**Solution 14B**: Use different VNC port
```bash
qemu-system-i386 \
  -vnc :1 \                        # VNC on port 5901
  -hda minix.img \
  -boot c

# Connect to:
vncviewer localhost:5901
```

**Solution 14C**: Verify VNC is listening
```bash
# Check if port is open
netstat -tlnp | grep 5900
lsof -i :5900

# If not listening, VNC not started properly
# Check QEMU invocation
```

**Solution 14D**: Use SPICE instead of VNC
```bash
qemu-system-i386 \
  -spice port=5930,disable-ticketing=on \
  -device QXL \
  -hda minix.img

# Connect with:
# remote-viewer spice://localhost:5930
```

**Prevention**: Test VNC connectivity immediately after QEMU start. Use `-vnc :0` as standard.

---

### Error 15: SSH Timeout

**Symptom**:
```
$ ssh root@localhost -p 2222
ssh: connect to host localhost port 2222: Connection refused
(or) ssh: connect to host localhost port 2222: Connection timed out
```

**Affected Versions**: All MINIX when using SSH for remote access

**Root Cause**: QEMU port forwarding not configured, or MINIX SSH daemon not running

**Solutions**:

**Solution 15A (Recommended)**: Configure port forwarding at QEMU launch
```bash
qemu-system-i386 \
  -net user,hostfwd=tcp::2222-:22 \      # Forward host:2222 to MINIX:22
  -net nic,model=ne2k_isa \
  -hda minix.img \
  -boot c
```

**Solution 15B**: Verify SSH is running in MINIX
```bash
# Boot MINIX and check:
$ ps aux | grep sshd
$ netstat -tlnp | grep 22

# If not running:
$ /usr/sbin/sshd &
# Or add to /usr/etc/rc.local:
/usr/sbin/sshd
```

**Solution 15C**: Check firewall rules
```bash
# In MINIX, verify listening ports:
netstat -tlnp

# Should show:
# tcp    0    0 0.0.0.0:22    0.0.0.0:*    LISTEN
```

**Solution 15D**: Use different forwarding port
```bash
qemu-system-i386 \
  -net user,hostfwd=tcp::10022-:22 \     # Use 10022 instead
  -net nic,model=ne2k_isa \
  -hda minix.img

# Connect:
ssh -p 10022 root@localhost
```

**Prevention**: Include SSH daemon in MINIX RC startup. Verify port forwarding in QEMU command before connecting.

---

## Error Diagnosis Workflow

Use the automated error triage tool:

```bash
# Analyze boot log for errors
python3 tools/triage-minix-errors.py measurements/i386/boot.log

# Output will show:
# - Detected errors
# - Suggested solutions from this registry
# - Confidence level for each diagnosis
# - Recommended next steps
```

---

## Common Error Patterns

### Pattern 1: Hangs During Installation
- **Likely Errors**: CD9660, Active Partition, Timeout
- **First Check**: Increase timeout, monitor with VNC
- **Solution Path**: Use RC6+ ISO or build from source

### Pattern 2: Network Issues
- **Likely Errors**: IRQ Check Failed, Network Not Working
- **First Check**: `ifconfig -a`, check for ne2k0 device
- **Solution Path**: Configure IRQ 3, I/O 0x300 in rc.local

### Pattern 3: Boot Hangs or Crashes
- **Likely Errors**: SeaBIOS Hang, Kernel Panic, TTY Conflicts
- **First Check**: Add `-cpu kvm32`, increase timeout
- **Solution Path**: Test with different CPU models, increase memory

### Pattern 4: No Output Visible
- **Likely Errors**: Blank Screen, Display Issues
- **First Check**: Add `-sdl` or `-vnc :0`
- **Solution Path**: Fallback to `-serial file:boot.log -nographic`

---

## Testing Matrix

| Configuration | MINIX ISO | MINIX Disk | Expected | Status |
|---------------|-----------|-----------|----------|--------|
| 1 CPU, 512MB, IDE | RC6 | N/A | Install OK | ✓ |
| 1 CPU, 512MB, AHCI | RC6 | N/A | Install FAIL | ✗ |
| 1 CPU, 512MB, IDE | RC6 | Yes | Boot OK | ✓ |
| 2 CPU, 512MB, IDE | RC6 | Yes | Boot OK | ✓ |
| 4 CPU, 512MB, IDE | RC6 | Yes | Boot OK | ✓ |
| 1 CPU, 256MB, IDE | RC6 | Yes | Boot OK | ⚠ |
| 1 CPU, 512MB, NE2K | RC6 | Yes | Network OK | ✓ |
| 1 CPU, 512MB, VirtIO | RC6 | Yes | Network TBD | ? |
| 1 CPU, 512MB, X11 | RC6 | Yes | X11 Fail | ✗ |
| 1 CPU, 1GB, X11 | RC6 | Yes | X11 OK | ✓ |

---

## References and Resources

**Official MINIX Documentation**:
- https://wiki.minix3.org/doku.php?id=usersguide:runningonqemu
- https://www.minix3.org/download

**QEMU Documentation**:
- https://qemu-project.gitlab.io/qemu/system/qemu-manpage.html
- Boot options: `-boot` parameter details

**Community Resources**:
- MINIX Mailing List: minix3@minix3.org
- MINIX GitHub: https://github.com/Stichting-MINIX-Research-Foundation/minix

**Previous Analyses**:
- PHASE-7-5-BOOT-PROFILING-BLOCKER-ANALYSIS.md (this repo)
- MINIX_INSTALLATION_AUTOMATION_GUIDE.md (this repo)

---

**Last Updated**: 2025-11-01
**Maintainer**: minix-analysis team
**Contribution**: Add new errors via GitHub issues with: boot.log, docker-compose.yml command, error output
