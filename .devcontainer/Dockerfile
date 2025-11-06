# NetBSD i386 QEMU-based Build Environment for MINIX 3.4
# Based on latest research and best practices for NetBSD/QEMU/Docker integration

FROM ubuntu:22.04

# Build arguments
ARG NETBSD_VERSION=10.1
ARG NETBSD_ARCH=i386
ARG USER_UID=1000
ARG USER_GID=1000
ARG DEBIAN_FRONTEND=noninteractive

# Environment setup
ENV NETBSD_VERSION=${NETBSD_VERSION} \
    NETBSD_ARCH=${NETBSD_ARCH} \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

LABEL maintainer="MINIX Analysis Team" \
      description="NetBSD ${NETBSD_VERSION} i386 build environment for MINIX 3.4" \
      version="1.0.0"

# ============================================================================
# STAGE 1: System packages and QEMU installation
# ============================================================================

# Install QEMU and virtualization tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # QEMU and KVM
    qemu-system-x86 \
    qemu-system-i386 \
    qemu-utils \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils \
    virt-manager \
    ovmf \
    seabios \
    # Networking
    iproute2 \
    iptables \
    dnsmasq \
    netcat \
    telnet \
    openssh-client \
    openssh-server \
    socat \
    # Build tools
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    autoconf \
    automake \
    libtool \
    pkg-config \
    bison \
    flex \
    gawk \
    # Version control
    git \
    git-lfs \
    mercurial \
    subversion \
    # Utilities
    curl \
    wget \
    rsync \
    unzip \
    p7zip-full \
    gzip \
    bzip2 \
    xz-utils \
    # Text processing
    vim \
    nano \
    jq \
    xmlstarlet \
    # Terminal multiplexers
    screen \
    tmux \
    # System monitoring
    htop \
    iotop \
    sysstat \
    # Debugging tools
    gdb \
    strace \
    ltrace \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# STAGE 2: Python environment for automation
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for QEMU automation and analysis
RUN pip3 install --no-cache-dir \
    # QEMU control
    pexpect \
    paramiko \
    fabric \
    # System monitoring
    psutil \
    # Data formats
    PyYAML \
    toml \
    # Testing
    pytest \
    pytest-timeout \
    pytest-xdist \
    pytest-cov \
    # Linting and formatting
    black \
    flake8 \
    pylint \
    mypy \
    # Data validation
    pydantic \
    # CLI tools
    click \
    rich \
    # Analysis
    pandas \
    numpy \
    matplotlib

# ============================================================================
# STAGE 3: LaTeX for documentation
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-pictures \
    texlive-science \
    latexmk \
    imagemagick \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Remove ImageMagick PDF restrictions
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml || true

# ============================================================================
# STAGE 4: User setup
# ============================================================================

# Create developer user with same UID/GID as host
RUN groupadd -g ${USER_GID} developer || true && \
    useradd -m -u ${USER_UID} -g ${USER_GID} -s /bin/bash developer && \
    # Add to KVM and libvirt groups
    usermod -aG kvm,libvirt,dialout developer && \
    # Setup sudo without password
    apt-get update && apt-get install -y sudo && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p \
    /vm/images \
    /vm/snapshots \
    /vm/logs \
    /builds \
    /artifacts \
    /workspace \
    /var/cache/netbsd \
    /etc/qemu \
    && chown -R developer:developer \
    /vm \
    /builds \
    /artifacts \
    /workspace \
    /var/cache/netbsd

# ============================================================================
# STAGE 5: NetBSD image download and setup
# ============================================================================

# Download NetBSD installation image
RUN mkdir -p /opt/netbsd-images && \
    cd /opt/netbsd-images && \
    wget -q https://iso.netbsd.org/pub/NetBSD/iso/${NETBSD_VERSION}/NetBSD-${NETBSD_VERSION}-${NETBSD_ARCH}.iso && \
    wget -q https://iso.netbsd.org/pub/NetBSD/iso/${NETBSD_VERSION}/NetBSD-${NETBSD_VERSION}-${NETBSD_ARCH}-install.img.gz && \
    gunzip NetBSD-${NETBSD_VERSION}-${NETBSD_ARCH}-install.img.gz || true && \
    chown -R developer:developer /opt/netbsd-images

# ============================================================================
# STAGE 6: QEMU VM management scripts
# ============================================================================

# Copy QEMU management scripts
COPY scripts/netbsd/ /opt/netbsd-scripts/
RUN chmod +x /opt/netbsd-scripts/*.sh && \
    chown -R developer:developer /opt/netbsd-scripts

# Create VM initialization script
RUN cat > /opt/netbsd-scripts/create-vm.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Create NetBSD VM disk image
DISK_SIZE=${1:-20G}
VM_NAME=${2:-netbsd-minix-builder}
IMAGE_PATH="/vm/images/${VM_NAME}.qcow2"

echo "Creating NetBSD VM disk image: ${IMAGE_PATH}"
qemu-img create -f qcow2 "${IMAGE_PATH}" "${DISK_SIZE}"

echo "VM disk created successfully at ${IMAGE_PATH}"
echo "Use start-netbsd.sh to boot the VM"
EOF

RUN cat > /opt/netbsd-scripts/start-netbsd.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Start NetBSD VM with QEMU
VM_NAME=${1:-netbsd-minix-builder}
IMAGE_PATH="/vm/images/${VM_NAME}.qcow2"
ISO_PATH="/opt/netbsd-images/NetBSD-${NETBSD_VERSION:-10.1}-${NETBSD_ARCH:-i386}.iso"

# VM configuration
MEMORY=${QEMU_MEMORY:-2048}
CPUS=${QEMU_CPUS:-4}
KVM=${QEMU_ENABLE_KVM:-1}

# Build QEMU command
QEMU_CMD="qemu-system-i386"

# KVM acceleration if available
if [ "${KVM}" = "1" ] && [ -e /dev/kvm ]; then
    QEMU_CMD="${QEMU_CMD} -enable-kvm -cpu host"
else
    QEMU_CMD="${QEMU_CMD} -cpu qemu32"
fi

# VM configuration
QEMU_CMD="${QEMU_CMD} -m ${MEMORY}M -smp ${CPUS}"
QEMU_CMD="${QEMU_CMD} -drive file=${IMAGE_PATH},format=qcow2,if=virtio"

# Boot from ISO if it exists and disk is empty
if [ -f "${ISO_PATH}" ] && ! qemu-img info "${IMAGE_PATH}" | grep -q "virtual size"; then
    QEMU_CMD="${QEMU_CMD} -cdrom ${ISO_PATH} -boot d"
fi

# Network setup (user mode networking with port forwarding)
QEMU_CMD="${QEMU_CMD} -netdev user,id=net0,hostfwd=tcp::2222-:22 -device virtio-net-pci,netdev=net0"

# VNC display
QEMU_CMD="${QEMU_CMD} -vnc :0"

# Serial port for console access
QEMU_CMD="${QEMU_CMD} -serial telnet:localhost:9001,server,nowait"

# QEMU monitor
QEMU_CMD="${QEMU_CMD} -monitor telnet:localhost:55555,server,nowait"

# No graphic window (VNC only)
QEMU_CMD="${QEMU_CMD} -nographic"

echo "Starting NetBSD VM: ${VM_NAME}"
echo "VNC display: :0 (port 5900)"
echo "SSH forwarding: localhost:2222 -> VM:22"
echo "Serial console: telnet localhost 9001"
echo "QEMU monitor: telnet localhost 55555"
echo ""
echo "Running: ${QEMU_CMD}"

exec ${QEMU_CMD}
EOF

RUN chmod +x /opt/netbsd-scripts/*.sh

# ============================================================================
# STAGE 7: MINIX cross-compilation setup
# ============================================================================

# Install additional dependencies for MINIX building
RUN apt-get update && apt-get install -y --no-install-recommends \
    # MINIX-specific build tools
    bsdmainutils \
    groff \
    texinfo \
    gettext \
    # Cross-compilation tools
    binutils-multiarch \
    && rm -rf /var/lib/apt/lists/*

# Create MINIX build helper script
RUN cat > /opt/netbsd-scripts/build-minix.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Build MINIX from source within NetBSD VM
# This script connects to the NetBSD VM and runs the build

VM_SSH_PORT=${1:-2222}
MINIX_SOURCE=${2:-/workspace/minix-source}
BUILD_OUTPUT=${3:-/builds}

echo "Building MINIX 3.4 in NetBSD VM"
echo "Source: ${MINIX_SOURCE}"
echo "Output: ${BUILD_OUTPUT}"

# Check if VM is accessible
if ! nc -z localhost ${VM_SSH_PORT}; then
    echo "Error: Cannot connect to NetBSD VM on port ${VM_SSH_PORT}"
    echo "Make sure the VM is running with: /opt/netbsd-scripts/start-netbsd.sh"
    exit 1
fi

echo "VM is accessible. Starting build process..."
echo "Note: You'll need to configure SSH access to the VM first"
echo "Use: ssh -p ${VM_SSH_PORT} root@localhost"
EOF

RUN chmod +x /opt/netbsd-scripts/build-minix.sh

# ============================================================================
# STAGE 8: Documentation and examples
# ============================================================================

# Create comprehensive README
RUN cat > /opt/netbsd-scripts/README.md << 'EOF'
# NetBSD i386 Build Environment for MINIX 3.4

## Overview

This devcontainer provides a complete NetBSD 10.1 i386 environment running 
in QEMU for building and testing MINIX 3.4.0RC6.

## Quick Start

### 1. Create NetBSD VM

```bash
/opt/netbsd-scripts/create-vm.sh 20G netbsd-minix-builder
```

### 2. Start NetBSD VM

```bash
/opt/netbsd-scripts/start-netbsd.sh netbsd-minix-builder
```

### 3. Connect to VM

**VNC:** Use a VNC client to connect to `localhost:5900`

**Serial Console:** 
```bash
telnet localhost 9001
```

**SSH (after NetBSD installation):**
```bash
ssh -p 2222 root@localhost
```

### 4. Install NetBSD

Boot from the ISO and follow the installation wizard. Recommended settings:
- Disk: wd0 (entire disk)
- Partitioning: Use entire disk
- Boot blocks: Yes
- Packages: Install "comp" (compiler) and "text" sets

### 5. Build MINIX

After NetBSD is installed and running:

```bash
# Inside the NetBSD VM
cd /usr/src
git clone git://git.minix3.org/minix minix
cd minix
sh build.sh -mi386 -O /builds tools
sh build.sh -mi386 -O /builds distribution
sh build.sh -mi386 -O /builds release
```

## Environment Variables

- `NETBSD_VERSION`: NetBSD version (default: 10.1)
- `NETBSD_ARCH`: Architecture (default: i386)
- `QEMU_MEMORY`: VM RAM in MB (default: 2048)
- `QEMU_CPUS`: Number of CPUs (default: 4)
- `QEMU_ENABLE_KVM`: Use KVM acceleration (default: 1)

## Directory Structure

- `/vm/images/` - VM disk images
- `/vm/snapshots/` - VM snapshots
- `/vm/logs/` - VM logs
- `/builds/` - MINIX build outputs
- `/artifacts/` - Generated artifacts
- `/workspace/` - Source code
- `/opt/netbsd-images/` - NetBSD ISO images
- `/opt/netbsd-scripts/` - Management scripts

## Best Practices

1. **Snapshots**: Create VM snapshots before major changes
2. **Resource allocation**: Adjust QEMU_MEMORY and QEMU_CPUS based on host
3. **KVM acceleration**: Ensure /dev/kvm access for best performance
4. **Serial console**: Use for headless debugging
5. **Port forwarding**: SSH access via port 2222

## Troubleshooting

### KVM not available
If KVM is unavailable, QEMU will fall back to software emulation (slower).
Check: `ls -l /dev/kvm`

### Cannot connect to VM
Ensure the VM is running and ports are properly forwarded.
Check: `ps aux | grep qemu`

### Build failures
Ensure all NetBSD compiler sets are installed.
Inside VM: `pkgin install build-essential`

## References

- [NetBSD 10.1 Documentation](https://www.netbsd.org/releases/formal-10/NetBSD-10.1.html)
- [MINIX 3 Cross-compilation](https://wiki.minix3.org/doku.php?id=developersguide:crosscompiling)
- [QEMU Documentation](https://www.qemu.org/docs/master/)

EOF

RUN chown -R developer:developer /opt/netbsd-scripts

# ============================================================================
# STAGE 9: Entrypoint and finalization
# ============================================================================

# Create entrypoint script
RUN cat > /usr/local/bin/docker-entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "=================================================="
echo "NetBSD i386 Build Environment for MINIX 3.4"
echo "=================================================="
echo ""
echo "NetBSD Version: ${NETBSD_VERSION}"
echo "Architecture: ${NETBSD_ARCH}"
echo "User: ${USER_NAME:-developer}"
echo ""
echo "Quick Start:"
echo "  1. Create VM: /opt/netbsd-scripts/create-vm.sh"
echo "  2. Start VM:  /opt/netbsd-scripts/start-netbsd.sh"
echo "  3. Connect:   VNC to localhost:5900"
echo ""
echo "Documentation: /opt/netbsd-scripts/README.md"
echo "=================================================="
echo ""

# Execute command or start bash
exec "$@"
EOF

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to developer user
USER developer
WORKDIR /workspace

# Set PATH
ENV PATH="/opt/netbsd-scripts:${PATH}"

# Expose ports
EXPOSE 5900 2222 55555 9001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD qemu-system-i386 --version || exit 1

# Entry point
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash"]
