# NetBSD Management Scripts

This directory contains scripts for managing the NetBSD i386 build environment.

## Scripts (Generated in Docker Image)

The following scripts are automatically created when building the DevContainer:

- **create-vm.sh** - Create a new NetBSD VM disk image
- **start-netbsd.sh** - Start the NetBSD VM with QEMU
- **build-minix.sh** - Helper for building MINIX in the VM
- **README.md** - Comprehensive documentation

## Usage

These scripts are available in `/opt/netbsd-scripts/` inside the DevContainer.

See `.devcontainer/Dockerfile` for script definitions and `docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md` for complete documentation.
