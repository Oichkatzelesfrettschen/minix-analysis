# MINIX 3.4.0-RC6 ISO Acquisition Guide

## Issue

The MINIX 3.4.0-rc6 ISO is not available as a pre-built download from GitHub releases.

## Solution Options

### Option 1: Build MINIX from Source (Recommended)

```bash
# Clone MINIX repository
git clone https://github.com/Minix3/minix.git
cd minix

# Checkout RC6 tag
git checkout 3.4.0-rc6

# Configure for i386
./configure --host=i386-pc-linux

# Build MINIX
make

# Create ISO (if build scripts support it)
make iso  # or similar target
```

### Option 2: Download Pre-built ISO from Alternative Sources

Check MINIX project documentation for mirror sites or pre-built binary distributions:
- https://minix3.org (official website)
- MINIX mailing lists or forums
- Academic repositories

### Option 3: Use Docker Volume to Mount Existing Installation

If MINIX is already installed on your system:

```bash
docker run -v /path/to/minix/installation:/minix-runtime \
  minix-rc6-i386
```

## Building MINIX i386 ISO

Once you have the ISO, place it here:
```
/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0-rc6.iso
```

Then rebuild the Docker image:
```bash
cd /home/eirikr/Playground/minix-analysis
docker-compose build minix-i386
```

## Alternative: Use Existing MINIX Installation

The `run-qemu-i386.sh` script can boot from an existing qcow2 disk image if you have one from a previous MINIX installation.

## Next Steps

1. Obtain the ISO using one of the methods above
2. Place in `./docker/minix_R3.4.0-rc6.iso`
3. Run Docker build: `docker-compose build minix-i386`
4. Launch container: `docker-compose up minix-i386`

## Testing Without ISO

The boot profiler CLI tool and measurement framework can be tested with:
```bash
python3 /home/eirikr/Playground/minix-analysis/docker/boot-profiler.py --help
```

MCP servers can be implemented and tested independently of having a running MINIX instance.
