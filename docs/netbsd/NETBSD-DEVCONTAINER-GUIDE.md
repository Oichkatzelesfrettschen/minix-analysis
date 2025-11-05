# NetBSD i386 Build Environment for MINIX 3.4

## Overview

This devcontainer provides a **production-ready NetBSD 10.1 i386 environment** running in QEMU for building and testing MINIX 3.4.0RC6. It implements best practices from the NetBSD and QEMU communities for optimal performance and reliability.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  DevContainer (Ubuntu 22.04)                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  QEMU i386 Emulator                               │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  NetBSD 10.1 i386                           │  │  │
│  │  │  ┌───────────────────────────────────────┐  │  │  │
│  │  │  │  MINIX 3.4.0RC6 Build System          │  │  │  │
│  │  │  │  - build.sh (NetBSD cross-compiler)   │  │  │  │
│  │  │  │  - LLVM/Clang toolchain               │  │  │  │
│  │  │  │  - Release tools                      │  │  │  │
│  │  │  └───────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Key Features

✅ **NetBSD 10.1 i386** - Latest stable release (December 2024)  
✅ **KVM Acceleration** - Hardware virtualization when available  
✅ **Complete Build Environment** - All tools for MINIX compilation  
✅ **Port Forwarding** - SSH, VNC, serial console access  
✅ **Persistent Storage** - VM images and builds preserved  
✅ **Production Ready** - Based on community best practices  

## Quick Start

### Prerequisites

- Docker or Podman
- Visual Studio Code with Remote-Containers extension (optional)
- VNC client (for GUI access)
- At least 8GB RAM and 20GB free disk space

### 1. Build the DevContainer

```bash
# From repository root
cd .devcontainer
docker-compose build
```

### 2. Start the Environment

```bash
docker-compose up -d
docker exec -it minix-netbsd-builder bash
```

Or open in VS Code:
- Command Palette (Ctrl+Shift+P)
- "Remote-Containers: Open Folder in Container"
- Select repository root

### 3. Create NetBSD VM

```bash
# Inside the container
/opt/netbsd-scripts/create-vm.sh 20G netbsd-minix-builder
```

This creates a 20GB QCOW2 disk image for the NetBSD VM.

### 4. Start NetBSD VM

```bash
/opt/netbsd-scripts/start-netbsd.sh netbsd-minix-builder
```

The VM will boot from the NetBSD installation ISO.

### 5. Connect to VM

**Option A: VNC (Graphical)**
```bash
# On your host machine
vncviewer localhost:5900
```

**Option B: Serial Console (Text)**
```bash
# Inside the container
telnet localhost 9001
```

**Option C: SSH (After NetBSD installation)**
```bash
# Inside the container or host
ssh -p 2222 root@localhost
```

### 6. Install NetBSD

In the VNC or serial console:

1. Boot from ISO (automatic on first boot)
2. Select "Install NetBSD"
3. Choose language and keyboard
4. **Disk setup:**
   - Select `wd0` (entire disk)
   - Choose "Use entire disk"
   - Standard MBR partition table
   - Accept default partitioning
5. **Boot blocks:** Yes, install boot blocks
6. **Package sets:** Select at minimum:
   - `base` (required)
   - `comp` (compiler and development tools)
   - `etc` (configuration files)
   - `man` (manual pages)
   - `text` (text processing tools)
7. **Network configuration:**
   - Configure `vioif0` (virtio network)
   - Use DHCP
8. Set root password
9. Reboot when installation completes

### 7. Post-Installation Setup

SSH into the NetBSD VM:

```bash
ssh -p 2222 root@localhost
```

Inside NetBSD, install additional packages:

```bash
# Update package manager
pkgin update

# Install essential build tools
pkgin install git gmake bash

# Install MINIX dependencies
pkgin install groff texinfo gettext
```

### 8. Build MINIX 3.4

Still in the NetBSD VM:

```bash
# Create source directory
mkdir -p /usr/src
cd /usr/src

# Clone MINIX source (or mount from host via shared folder)
git clone git://git.minix3.org/minix minix
cd minix

# Build toolchain
sh build.sh -mi386 -O /builds tools

# Build MINIX distribution
sh build.sh -mi386 -O /builds distribution

# Create release image
sh build.sh -mi386 -O /builds release

# Build ISO image (optional)
cd releasetools
sh x86_hdimage.sh
```

Build artifacts will be in `/builds` directory.

## Environment Variables

Configure the environment via docker-compose.yml:

| Variable | Default | Description |
|----------|---------|-------------|
| `NETBSD_VERSION` | 10.1 | NetBSD release version |
| `NETBSD_ARCH` | i386 | Target architecture |
| `QEMU_MEMORY` | 2048 | VM RAM in MB |
| `QEMU_CPUS` | 4 | Number of virtual CPUs |
| `QEMU_ENABLE_KVM` | 1 | Enable KVM acceleration |
| `MINIX_SOURCE` | /workspace/minix-source | MINIX source path |
| `BUILD_OUTPUT` | /builds | Build output directory |
| `ARTIFACTS_DIR` | /artifacts | Artifacts directory |

## Directory Structure

```
/workspace/              # Repository root (mounted from host)
  ├── minix-source/      # MINIX 3.4 source code
  ├── .devcontainer/     # This devcontainer configuration
  └── ...

/vm/
  ├── images/            # VM disk images (persistent)
  ├── snapshots/         # VM snapshots
  └── logs/              # VM logs

/builds/                 # MINIX build outputs (persistent)
  ├── destdir.i386/      # Cross-compiled binaries
  ├── obj.i386/          # Object files
  └── tools/             # Build tools

/artifacts/              # Generated artifacts (persistent)
  ├── iso/               # Bootable ISO images
  └── analysis/          # Analysis results

/opt/
  ├── netbsd-images/     # NetBSD ISO files
  └── netbsd-scripts/    # Management scripts
```

## Networking

The devcontainer exposes these ports:

| Port | Protocol | Purpose |
|------|----------|---------|
| 5900 | VNC | NetBSD VM graphical console |
| 2222 | SSH | NetBSD VM SSH access |
| 55555 | TCP | QEMU monitor interface |
| 9001 | TCP | Serial console telnet |
| 8080 | HTTP | Analysis dashboard |

## Best Practices

### KVM Acceleration

For best performance, ensure KVM is available:

```bash
# Check KVM availability
ls -l /dev/kvm

# If missing, enable virtualization in BIOS
# and install KVM on host:
# sudo apt-get install qemu-kvm libvirt-daemon-system

# Verify KVM inside container
docker exec minix-netbsd-builder ls -l /dev/kvm
```

### VM Snapshots

Create snapshots before major changes:

```bash
# Inside container
qemu-img snapshot -c pre-build /vm/images/netbsd-minix-builder.qcow2

# List snapshots
qemu-img snapshot -l /vm/images/netbsd-minix-builder.qcow2

# Restore snapshot
qemu-img snapshot -a pre-build /vm/images/netbsd-minix-builder.qcow2
```

### Resource Allocation

Adjust based on your host system:

**For 16GB+ RAM hosts:**
```yaml
environment:
  - QEMU_MEMORY=4096
  - QEMU_CPUS=8
```

**For 8GB RAM hosts:**
```yaml
environment:
  - QEMU_MEMORY=2048
  - QEMU_CPUS=4
```

### Serial Console Debugging

The serial console is invaluable for debugging:

```bash
# Connect to serial console
telnet localhost 9001

# QEMU monitor (for VM control)
telnet localhost 55555

# Monitor commands
(qemu) info status
(qemu) info snapshots
(qemu) savevm snapshot-name
(qemu) loadvm snapshot-name
```

## Troubleshooting

### KVM Not Available

**Symptom:** VM runs very slowly

**Solution:**
```bash
# Check if KVM device is available
ls -l /dev/kvm

# If not, check host kernel modules
lsmod | grep kvm

# Load KVM module (on host)
sudo modprobe kvm_intel  # or kvm_amd
```

### Cannot Connect to VM

**Symptom:** VNC/SSH connection refused

**Solution:**
```bash
# Check if VM is running
ps aux | grep qemu

# Check port forwarding
netstat -tlnp | grep :5900
netstat -tlnp | grep :2222

# Restart VM
/opt/netbsd-scripts/start-netbsd.sh netbsd-minix-builder
```

### MINIX Build Failures

**Symptom:** build.sh fails with missing tools

**Solution:**
```bash
# Inside NetBSD VM
pkgin update
pkgin install gmake groff texinfo gettext

# Ensure compiler set is installed
ls /usr/bin/gcc

# If missing, reinstall NetBSD with 'comp' set
```

### Out of Disk Space

**Symptom:** VM reports no space

**Solution:**
```bash
# Check VM disk usage
ssh -p 2222 root@localhost df -h

# Resize VM disk (shut down VM first)
qemu-img resize /vm/images/netbsd-minix-builder.qcow2 +10G

# Inside NetBSD, resize filesystem
# (requires reboot and manual partition resizing)
```

## Advanced Usage

### Automated Installation

For automated NetBSD installation:

```bash
# Create expect script for automatic answers
cat > /tmp/netbsd-install.exp << 'EOF'
#!/usr/bin/expect
spawn /opt/netbsd-scripts/start-netbsd.sh
# Add automated installation responses
EOF

expect /tmp/netbsd-install.exp
```

### Cross-Mounting Host Directories

Mount host directories into NetBSD:

```bash
# Modify start-netbsd.sh to add:
# -virtfs local,path=/workspace/minix-source,mount_tag=host0,security_model=passthrough
```

Inside NetBSD:
```bash
mount -t 9p -o trans=virtio,version=9p2000.L host0 /mnt/host
```

### Performance Tuning

For faster builds:

```bash
# Use virtio for better I/O performance (already configured)
# Enable multi-core compilation in NetBSD
export MAKEFLAGS="-j $(sysctl -n hw.ncpu)"

# Build with parallel jobs
sh build.sh -mi386 -O /builds -j 8 distribution
```

## References

### NetBSD Official Documentation
- [NetBSD 10.1 Release](https://www.netbsd.org/releases/formal-10/NetBSD-10.1.html)
- [NetBSD Installation Guide](https://www.netbsd.org/docs/guide/en/chap-inst.html)
- [NetBSD Virtualization](https://www.netbsd.org/docs/guide/en/chap-virt.html)

### MINIX Documentation
- [MINIX 3 Wiki](https://wiki.minix3.org/)
- [Cross-compilation Guide](https://wiki.minix3.org/doku.php?id=developersguide:crosscompiling)
- [Build System](https://wiki.minix3.org/doku.php?id=developersguide:buildsystem)

### QEMU Documentation
- [QEMU User Documentation](https://www.qemu.org/docs/master/)
- [QEMU i386 System Emulation](https://www.qemu.org/docs/master/system/target-i386.html)
- [QEMU Monitor](https://www.qemu.org/docs/master/system/monitor.html)

### Community Resources
- [madworx/docker-netbsd](https://github.com/madworx/docker-netbsd) - QEMU NetBSD Docker images
- [DevContainers Spec](https://containers.dev/) - DevContainer specification
- [NetBSD Mailing Lists](https://www.netbsd.org/mailinglists/) - Community support

## FAQ

**Q: Can I use this on Windows/macOS?**  
A: Yes, via Docker Desktop with WSL2 (Windows) or Docker Desktop (macOS). KVM acceleration won't be available, so performance will be slower.

**Q: How much disk space do I need?**  
A: Minimum 20GB for VM + 10GB for builds = 30GB total recommended.

**Q: Can I run multiple VMs?**  
A: Yes, create additional VMs with different names and adjust port mappings in docker-compose.yml.

**Q: Is this suitable for production MINIX builds?**  
A: Yes, this follows NetBSD and MINIX best practices for reproducible builds.

**Q: Can I use a different NetBSD version?**  
A: Yes, modify `NETBSD_VERSION` in docker-compose.yml. Tested with 10.0 and 10.1.

## Support

For issues or questions:
1. Check this documentation first
2. Review NetBSD and MINIX official documentation
3. Check GitHub issues in the repository
4. Consult NetBSD mailing lists

## License

This devcontainer configuration is part of the minix-analysis project.
See repository LICENSE file for details.

---

**Created:** 2025-11-05  
**NetBSD Version:** 10.1  
**MINIX Target:** 3.4.0RC6  
**Status:** Production Ready ✅
