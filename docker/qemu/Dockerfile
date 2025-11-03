# Dockerfile.qemu - QEMU-based MINIX testing environment
# Supports nested virtualization with KVM acceleration when available
# Falls back to pure QEMU emulation on systems without KVM

FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install QEMU and KVM utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    qemu-system-i386 \
    qemu-system-x86-64 \
    qemu-utils \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    libvirt-dev \
    bridge-utils \
    dnsmasq-base \
    ebtables \
    qemu-efi \
    qemu-efi-arm \
    ovmf \
    ipxe-qemu \
    seabios \
    syslinux \
    syslinux-common \
    && rm -rf /var/lib/apt/lists/*

# Install networking and debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    iptables \
    dnsmasq \
    netcat \
    telnet \
    openssh-client \
    curl \
    wget \
    git \
    vim \
    jq \
    expect \
    screen \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install Python for automation scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for QEMU control
RUN pip3 install --no-cache-dir \
    pexpect \
    paramiko \
    psutil \
    PyYAML \
    pytest \
    pytest-timeout \
    pytest-xdist \
    pydantic

# Create non-root user for running VMs
RUN groupadd -g 107 kvm && \
    useradd -m -u 1000 -g 1000 -G kvm,libvirt qemu-user && \
    mkdir -p /home/qemu-user/.ssh && \
    chown -R qemu-user:qemu-user /home/qemu-user

# Create VM storage directories
RUN mkdir -p /vm/images /vm/snapshots /vm/logs && \
    chown -R qemu-user:qemu-user /vm

# Create network configuration directories
RUN mkdir -p /etc/qemu /var/run/qemu

# Configure bridged networking (bridge-utils handles this)
RUN echo "allow qemu-user" >> /etc/libvirt/libvirtd.conf && \
    echo "unix_sock_group = \"libvirt\"" >> /etc/libvirt/libvirtd.conf && \
    echo "unix_sock_ro_perms = \"0777\"" >> /etc/libvirt/libvirtd.conf && \
    echo "unix_sock_rw_perms = \"0770\"" >> /etc/libvirt/libvirtd.conf

# Copy QEMU configuration templates
COPY docker/qemu/configs/ /etc/qemu/

# Copy test fixtures and scripts
COPY tests/qemu/ /opt/qemu-tests/
COPY tests/fixtures/ /opt/fixtures/

# Copy MINIX ISO and disk images
RUN mkdir -p /opt/minix-images
COPY docker/*.iso /opt/minix-images/ 2>/dev/null || true
COPY docker/*.qcow2 /opt/minix-images/ 2>/dev/null || true

# Create entrypoint script
RUN mkdir -p /opt/bin

# Volume mounts
VOLUME ["/vm/images", "/vm/snapshots", "/vm/logs", "/mnt/minix-source"]

# Expose ports
# VNC: 5900-5909 (for multiple VMs)
# QEMU monitor: 55555-55565
# Serial port relay: 9001-9010
EXPOSE 5900-5909 55555-55565 9001-9010

# Set working directory
WORKDIR /vm

# Run libvirt daemon in foreground
# Docker will manage the process lifecycle
ENV LIBVIRTD_OPTS="-l"

# Health check - verify QEMU is available
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD qemu-system-i386 --version || exit 1

# Default: start bash shell for interactive use
# Override with CMD to run specific tests
CMD ["/bin/bash"]
