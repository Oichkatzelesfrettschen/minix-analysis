# Phase 7.5: MINIX Boot Profiling - Blocker Analysis and Solution

**Date**: 2025-10-31
**Status**: IN PROGRESS - MINIX Source Build Initiated
**Blocker**: Interactive Installer ISO Requires Serial Console Configuration

## Problem Summary

The MINIX 3.4.0 RC6 ISO (`minix_R3.4.0rc6-d5e4fc0.iso`) is an **interactive installer** that:
1. Does NOT output to serial console during boot
2. Requires keyboard input from user for installation prompts
3. Cannot be used directly for automated/headless boot profiling

### Testing Evidence

**Test 1: QEMU with `-serial file:` redirection**
- Command: `qemu-system-i386 -serial file:boot.log ...`
- Result: Boot log file created but remained empty (0 bytes)
- Conclusion: No serial output from MINIX

**Test 2: QEMU with `-serial stdio` (direct stdout)**
- Command: `timeout 45 qemu-system-i386 -serial stdio ...`
- Result: No output to stdout/stderr, only timeout signal
- Conclusion: MINIX not producing any serial output during boot/installation

## Root Cause Analysis

The ISO image is a pre-built installation medium designed for interactive use. It:
1. May be waiting for user input at installer prompts
2. Does not have serial console enabled in boot configuration
3. Uses BIOS/firmware display mode, not serial-based console

## Solution: Build MINIX from Source

The official MINIX repository contains the complete build system which:
1. Compiles MINIX from source code
2. Uses `releasetools/x86_hdimage.sh` to create a bootable disk image
3. **Importantly**: Generates boot.cfg with serial console explicitly enabled

### Key Finding from x86_hdimage.sh

Line 51 of `/home/eirikr/Playground/minix/releasetools/x86_hdimage.sh`:
```bash
menu=Start MINIX 3 ALIX:load_mods /boot/minix_default/mod*;multiboot /boot/minix_default/kernel rootdevname=c0d0p0 console=tty00 consdev=com0 ata_no_dma=1
```

This shows the **correct boot parameters for serial console**:
- `console=tty00` - Route console to serial terminal 0
- `consdev=com0` - Set console device to COM0 (serial port)

## Implemented Solution

**MINIX Source Build (In Progress)**

Initiated full MINIX source compilation:
```bash
cd /home/eirikr/Playground/minix
./build.sh -m i386 -a i386 build distribution
```

**Build Process**:
1. Compiles i386 architecture tools and cross-compiler
2. Builds complete MINIX system from source
3. Creates distribution packages
4. (Next step) Generate disk image using `x86_hdimage.sh`

**Estimated Duration**: 30-60 minutes (system-dependent)

**Expected Output**: `minix_x86.img` - A bootable disk image with:
- Serial console fully configured
- 2GB size (optimized for QEMU)
- Kernel, modules, and full filesystem
- Ready for repeated boot profiling

## Boot Profiling Strategy (Post-Build)

Once disk image is available:

### Phase 1: Single CPU Baseline (486)
```bash
timeout 120 qemu-system-i386 \
    -m 512M \
    -smp 1 \
    -cpu 486 \
    -hda minix_x86.img \
    -display none \
    -serial file:boot-486-1cpu.log \
    -monitor none
```

Expected output:
- Kernel boot messages to serial console
- Boot markers: multiboot detected → kernel initialization → shell prompt
- Real boot time measurement (not 180s timeout like ISO)

### Phase 2: Multi-CPU Scaling Tests
- Test with 1, 2, 4, 8 vCPU configurations
- Test with CPU models: 486, Pentium, Pentium Pro, Pentium II, Athlon
- Collect 5 samples per configuration
- Analyze scaling efficiency and SMP coordination

### Phase 3: Data Analysis
- Measure actual boot time per configuration
- Calculate scaling factors: T(2)/T(1), T(4)/T(1), T(8)/T(1)
- Identify SMP coordination overhead
- Validate against whitepaper estimates (expected ~65ms for i386)

### Phase 4: Chapter 17 Report
- Real system validation data
- Performance scaling charts
- Comparison to theoretical estimates
- Impact analysis on microkernel design

## MINIX Build Artifacts

When build completes, key files will be available:

**Build Output Directory**: `obj.i386/` (if build.sh creates one)
**Distribution Directory**: `releasedir/` (typical for NetBSD-based build.sh)
**Disk Image**: `releasetools/minix_x86.img` or similar
**Cross-tools**: Compiled i386 toolchain for building kernel modules

## QEMU Boot Command (For Disk Image)

Once disk image is created, boot it with:
```bash
qemu-system-i386 \
    -m 512M \
    -smp $CPUS \
    -cpu $CPU_MODEL \
    -hda minix_x86.img \
    -display none \
    -serial file:boot.log \
    -monitor none \
    2>&1 || true
```

This will:
1. Boot the pre-installed MINIX system
2. Capture all serial output to `boot.log`
3. Reach shell prompt (not stop at installer)
4. Allow measurement of true boot time

## Online Resources Consulted

1. **MINIX 3 Wiki** - Official running on QEMU guide
   - URL: https://wiki.minix3.org/doku.php?id=usersguide:runningonqemu
   - Key: Serial console configuration details

2. **QEMU Documentation**
   - x86 System Emulator documentation
   - Boot index and device ordering

3. **MINIX Repository**
   - `/home/eirikr/Playground/minix/releasetools/x86_hdimage.sh`
   - `/home/eirikr/Playground/minix/build.sh`
   - Complete build infrastructure from NetBSD

4. **Wikibooks - MINIX 3 on QEMU**
   - QEMU command examples and parameters

## Timeline

- **T+0 (2025-10-31 05:25)**: Build initiated
- **T+30-60 min**: Build completion (estimate)
- **T+90-120 min**: Disk image generation and first boot test
- **T+120-180 min**: Complete single-CPU test matrix
- **T+180-240 min**: Multi-CPU testing (1,2,4,8 vCPU across CPU models)
- **T+240-300 min**: Data analysis and Chapter 17 report generation

## Recovery Plan (If Build Fails)

If MINIX build fails due to missing dependencies:

1. Check build log: `cat /tmp/minix-build.log`
2. Identify missing packages
3. Install via pacman: `pacman -S package-name`
4. Retry build with: `./build.sh -m i386 -a i386 build distribution`

Alternative approach if build system has issues:
- Manually compile kernel and modules
- Extract filesystem from ISO
- Create minimal disk image with proper boot config

## Success Criteria

✅ MINIX source compiles successfully
✅ Disk image created with correct boot parameters
✅ Single boot reaches shell prompt with serial output visible
⬜ Real boot time measured (target: ~65ms baseline)
⬜ Multi-CPU scaling data collected
⬜ Chapter 17 validation report generated

---

**Status**: Build in progress (background PID: 857e33)
Monitor with: `tail -f /tmp/minix-build.log`
