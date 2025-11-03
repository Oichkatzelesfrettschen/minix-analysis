# MINIX 3.4 RC6 Automated Installation - Quick Start

## TL;DR

```bash
# Install pexpect if not available
pip3 install pexpect

# Run automated installation
cd /home/eirikr/Playground/minix-analysis/docker
./test_installation.sh

# Or manually
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix_installed.qcow2
```

## What This Does

1. Creates a 2GB QCOW2 disk image
2. Boots MINIX installer from ISO
3. Automatically answers all installation prompts:
   - Login as root
   - Start setup
   - Accept default keyboard (us-std)
   - Use automatic partitioning
   - Select full install
   - Accept default partition sizes
   - Wait for file copy (2-5 minutes)
   - Shutdown installer
4. Leaves you with a bootable MINIX disk image

## Installation Time

- **With KVM**: 2-5 minutes
- **Without KVM**: 10-20 minutes

## Requirements

- Python 3.6+
- pexpect (`pip3 install pexpect`)
- QEMU (`qemu-system-i386`)
- KVM support (optional, but highly recommended)

## Command Options

```bash
python3 minix_auto_install.py \
    --iso <path-to-iso> \        # Required: MINIX ISO file
    --disk <output-disk> \       # Required: Output disk image
    --size 2G \                  # Optional: Disk size (default: 2G)
    --memory 512M \              # Optional: RAM (default: 512M)
    --boot \                     # Optional: Boot after install
    --no-create                  # Optional: Use existing disk
```

## Usage Examples

### Basic Installation
```bash
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix.qcow2
```

### Installation with Larger Disk
```bash
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix_4gb.qcow2 \
    --size 4G \
    --memory 1G
```

### Install and Boot Immediately
```bash
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix.qcow2 \
    --boot
```

### Boot Existing Installation
```bash
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix_existing.qcow2 \
    --no-create \
    --boot
```

### Manual Boot (Alternative)
```bash
qemu-system-i386 \
    -m 512M \
    -hda minix.qcow2 \
    -serial stdio \
    -nographic \
    -enable-kvm
```

## Troubleshooting

### Installation Hangs
- Check that ISO path is correct
- Ensure QEMU is installed: `which qemu-system-i386`
- Try without KVM (remove `-enable-kvm` from script)
- Check output log for specific error

### Timeout During Installation
- File copy step can take 2-5 minutes
- Script has 300-second timeout for this step
- If still times out, increase timeout in script:
  ```python
  timeout=600  # 10 minutes
  ```

### pexpect Not Found
```bash
pip3 install pexpect
```

### QEMU Not Found
```bash
# On Arch/CachyOS
sudo pacman -S qemu-system-i386

# On Debian/Ubuntu
sudo apt install qemu-system-x86
```

### Installation Succeeds but Won't Boot
- Verify disk image: `qemu-img info minix.qcow2`
- Try booting with boot menu: add `-boot menu=on` to QEMU command
- Check installation log for errors

## Output Files

After successful installation:

- `minix_installed.qcow2` - Bootable MINIX disk image
- Installation log printed to stdout

## Next Steps

1. **Test Boot**: Boot installed system to verify
2. **Boot Profiling**: Use installed disk for automated boot profiling
3. **Integration**: Integrate with boot profiler pipeline

## Integration with Boot Profiler

```bash
#!/bin/bash
# Complete boot profiling pipeline

# Step 1: Automated installation
python3 minix_auto_install.py \
    --iso minix_R3.4.0rc6-d5e4fc0.iso \
    --disk minix_profile.qcow2

# Step 2: Boot profiling (10 iterations)
for i in {1..10}; do
    echo "Boot iteration $i"
    qemu-system-i386 \
        -m 512M \
        -hda minix_profile.qcow2 \
        -serial stdio \
        -nographic \
        -enable-kvm \
        > boot_log_$i.txt 2>&1
done

# Step 3: Analyze boot times
python3 analyze_boot_times.py boot_log_*.txt
```

## Advanced: Customizing Installation

Edit `minix_auto_install.py` to customize:

- Partition sizes (Step 10)
- Keyboard layout (Step 5)
- Ethernet configuration (Step 14)
- Post-install scripts

See `MINIX_INSTALLATION_AUTOMATION_GUIDE.md` for detailed documentation.

## Files in This Directory

- `minix_auto_install.py` - Main automation script
- `test_installation.sh` - Test/demo script
- `MINIX_INSTALLATION_AUTOMATION_GUIDE.md` - Complete documentation
- `QUICK_START.md` - This file
- `minix_R3.4.0rc6-d5e4fc0.iso` - MINIX installer ISO (604 MB)

## Support

For issues or questions:
1. Check `MINIX_INSTALLATION_AUTOMATION_GUIDE.md` for detailed troubleshooting
2. Review installation logs for specific errors
3. Enable debug logging in script for detailed output

## License

MIT License - Free to use and modify
