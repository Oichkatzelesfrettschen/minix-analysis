# NetBSD Disk Images and QEMU Setup - Research Summary

## Latest NetBSD Releases (2024-2025)

### NetBSD 10.1 (Current Stable - December 2024)

**Official Image Downloads:**
- **Base URL:** https://iso.netbsd.org/pub/NetBSD/iso/10.1/
- **i386 ISO:** https://iso.netbsd.org/pub/NetBSD/iso/10.1/NetBSD-10.1-i386.iso
- **i386 Install Image:** https://iso.netbsd.org/pub/NetBSD/iso/10.1/NetBSD-10.1-i386-install.img.gz

**Daily Builds (Rolling Latest):**
- **Base URL:** https://nycdn.netbsd.org/pub/NetBSD-daily/netbsd-10/latest/images/
- Automatically updated with latest stable patches

### Key Features of NetBSD 10.1

✅ **Stable Release** - Production-ready (December 16, 2024)  
✅ **i386 Support** - Full support for 32-bit x86  
✅ **QEMU Compatible** - Tested with QEMU 5.0+  
✅ **Virtio Drivers** - Para-virtualized performance  
✅ **Active Development** - Regular security updates  

## QEMU Best Practices for NetBSD i386

### Hardware Virtualization (KVM)

**Linux Host:**
```bash
# Enable KVM
sudo modprobe kvm_intel  # or kvm_amd
sudo chmod 666 /dev/kvm  # or use proper group membership

# Verify
ls -l /dev/kvm
kvm-ok  # if available
```

**Docker Container:**
```yaml
devices:
  - /dev/kvm:/dev/kvm
cap_add:
  - SYS_ADMIN
privileged: true  # or specific capabilities
```

### QEMU Command Line (Recommended)

```bash
qemu-system-i386 \
  -enable-kvm \                      # Hardware acceleration
  -cpu host \                        # Pass through host CPU features
  -m 2048M \                         # 2GB RAM
  -smp 4 \                           # 4 CPUs
  -drive file=netbsd.qcow2,format=qcow2,if=virtio \  # Virtio disk
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \       # Port forwarding
  -device virtio-net-pci,netdev=net0 \               # Virtio network
  -vnc :0 \                          # VNC on port 5900
  -serial telnet:localhost:9001,server,nowait \      # Serial console
  -monitor telnet:localhost:55555,server,nowait \    # QEMU monitor
  -nographic \                       # No SDL/GTK window
  -cdrom NetBSD-10.1-i386.iso \      # Boot from ISO (first install)
  -boot d                            # Boot from CD
```

### Device Configuration

**Virtio (Recommended for Performance):**
- **Disk:** `if=virtio` - 2-3x faster than IDE
- **Network:** `virtio-net-pci` - Lower latency
- **Balloon:** `virtio-balloon-pci` - Memory management

**Legacy (Better Compatibility):**
- **Disk:** `if=ide` - Universal support
- **Network:** `e1000` - Intel gigabit emulation

### Networking Modes

**User Mode (NAT) - Default:**
```bash
-netdev user,id=net0,hostfwd=tcp::2222-:22
-device virtio-net-pci,netdev=net0
```
- No root required
- Port forwarding for SSH/services
- Limited to outbound connections

**Bridged Networking (Advanced):**
```bash
-netdev bridge,id=net0,br=br0
-device virtio-net-pci,netdev=net0
```
- Full network integration
- Requires host bridge setup
- Guest gets routable IP

**Tap Device (Custom):**
```bash
-netdev tap,id=net0,ifname=tap0,script=no,downscript=no
-device virtio-net-pci,netdev=net0
```
- Maximum flexibility
- Manual setup required

## Docker DevContainer Best Practices

### KVM Access in Container

**Method 1: Device Mapping**
```yaml
services:
  netbsd:
    devices:
      - /dev/kvm:/dev/kvm
    cap_add:
      - SYS_ADMIN
```

**Method 2: Group Membership**
```dockerfile
# In Dockerfile
RUN groupadd -g 107 kvm
RUN usermod -aG kvm developer

# In docker-compose.yml
group_add:
  - kvm
```

**Verification:**
```bash
# Inside container
ls -l /dev/kvm
# Should show: crw-rw---- 1 root kvm ...

# Test access
qemu-system-i386 -enable-kvm -version
```

### Volume Management

**Persistent VM Images:**
```yaml
volumes:
  - netbsd-images:/vm/images  # Named volume
  - ./builds:/builds          # Bind mount for easy access
```

**Performance Considerations:**
- Use named volumes for VM disks (better I/O)
- Use bind mounts for source code (easier editing)
- Avoid mounting large directories on Windows/macOS (slow)

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```

### Cross-Platform Support

**Linux:**
- Full KVM support
- Best performance
- /dev/kvm access

**Windows (WSL2):**
- Nested virtualization possible (Hyper-V required)
- Slower than Linux
- Enable: `bcdedit /set hypervisorlaunchtype auto`

**macOS (Docker Desktop):**
- No KVM (Apple Hypervisor used)
- QEMU software emulation
- Expect 3-5x slower builds

## MINIX 3.4 Cross-Compilation on NetBSD

### NetBSD as Build Host

**Why NetBSD for MINIX?**
- MINIX build system based on NetBSD build.sh
- Native toolchain compatibility
- Tested and documented workflow

**Required NetBSD Packages:**
```bash
# Inside NetBSD
pkgin update
pkgin install \
  git \
  gmake \
  groff \
  texinfo \
  gettext \
  gcc \
  binutils
```

### Build.sh Cross-Compilation

```bash
# Clone MINIX source
git clone git://git.minix3.org/minix
cd minix

# Build toolchain
sh build.sh -mi386 -O /builds tools

# Build distribution
sh build.sh -mi386 -O /builds distribution

# Create release
sh build.sh -mi386 -O /builds release

# Generate bootable image
cd releasetools
sh x86_hdimage.sh
```

**Build Options:**
- `-m MACHINE`: Target architecture (i386, amd64)
- `-O DESTDIR`: Output directory
- `-j N`: Parallel jobs
- `-U`: Unprivileged build

### Performance Tips

**Parallel Builds:**
```bash
# Use all CPU cores
NPROC=$(sysctl -n hw.ncpu)
sh build.sh -mi386 -O /builds -j $NPROC distribution
```

**Disk Performance:**
```bash
# Use tmpfs for object files (if enough RAM)
mount -t tmpfs tmpfs /builds/obj.i386
```

**Network Optimization:**
```bash
# If downloading packages
export PKG_PATH="https://cdn.netbsd.org/pub/pkgsrc/packages/NetBSD/i386/10.1/All"
```

## Image Management

### QCOW2 Format (Recommended)

**Create:**
```bash
qemu-img create -f qcow2 netbsd.qcow2 20G
```

**Resize:**
```bash
qemu-img resize netbsd.qcow2 +10G
```

**Snapshots:**
```bash
qemu-img snapshot -c snapshot1 netbsd.qcow2
qemu-img snapshot -l netbsd.qcow2
qemu-img snapshot -a snapshot1 netbsd.qcow2
qemu-img snapshot -d snapshot1 netbsd.qcow2
```

**Convert:**
```bash
qemu-img convert -f raw -O qcow2 netbsd.img netbsd.qcow2
```

### Automated Image Creation

**Community Tools:**
- [mkimg-netbsd](https://github.com/alarixnia/mkimg-netbsd) - Automated NetBSD image generation
- [packer-netbsd](https://github.com/search?q=packer+netbsd) - HashiCorp Packer templates

## Security Considerations

### Container Security

**Minimize Privileges:**
```yaml
# Instead of privileged: true
devices:
  - /dev/kvm:/dev/kvm
  - /dev/net/tun:/dev/net/tun
cap_add:
  - NET_ADMIN
  - SYS_ADMIN
security_opt:
  - apparmor:unconfined  # Only if needed
```

**User Namespaces:**
```yaml
userns_mode: "host"  # For KVM access
```

### Network Isolation

**Internal Network:**
```yaml
networks:
  netbsd-net:
    internal: true
```

**Firewall Rules:**
```bash
# Inside container
iptables -A INPUT -p tcp --dport 5900 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 5900 -j DROP
```

## References

### Official Documentation
1. [NetBSD 10.1 Release](https://www.netbsd.org/releases/formal-10/NetBSD-10.1.html)
2. [NetBSD Downloads](https://www.netbsd.org/releases/)
3. [QEMU NetBSD Guide](https://wiki.qemu.org/Hosts/BSD)
4. [NetBSD Virtualization](https://www.netbsd.org/docs/guide/en/chap-virt.html)

### Community Resources
5. [madworx/docker-netbsd](https://github.com/madworx/docker-netbsd)
6. [NetBSD Kernel Debugging with QEMU](https://wiki.netbsd.org/kernel_debugging_with_qemu/)
7. [Chris Pinnock's QEMU Guide](https://chrispinnock.com/stuff/emulation/)
8. [DevContainers Best Practices](https://github.com/orgs/devcontainers/discussions/149)

### MINIX Documentation
9. [MINIX Cross-compilation](https://wiki.minix3.org/doku.php?id=developersguide:crosscompiling)
10. [MINIX Build System](https://wiki.minix3.org/doku.php?id=developersguide:buildsystem)
11. [MINIX Release Tools](https://github.com/Stichting-MINIX-Research-Foundation/minix)

### Technical Papers
12. [QEMU KVM Performance](https://www.linux-kvm.org/page/Tuning_KVM)
13. [Virtio Specification](https://docs.oasis-open.org/virtio/virtio/v1.1/virtio-v1.1.html)

## Summary of Best Practices

### ✅ Do

1. **Use NetBSD 10.1** - Latest stable with i386 support
2. **Enable KVM** - 5-10x performance improvement
3. **Use Virtio drivers** - 2-3x I/O performance
4. **Named volumes for VMs** - Better Docker performance
5. **Snapshots before builds** - Easy rollback
6. **Port forwarding for SSH** - Secure access
7. **Serial console** - Debugging without VNC
8. **Resource limits** - Prevent host exhaustion

### ❌ Avoid

1. **Running without KVM on Linux** - Extremely slow
2. **IDE disk interface** - Much slower than virtio
3. **Privileged: true everywhere** - Security risk
4. **Large bind mounts on Windows/macOS** - Performance issues
5. **Building without snapshots** - Risk of data loss
6. **Exposing VNC publicly** - Security vulnerability

---

**Research Date:** 2025-11-05  
**NetBSD Version:** 10.1 (Stable)  
**QEMU Version:** 5.0+ recommended  
**Docker:** 20.10+ required  
**Status:** Production Ready ✅
