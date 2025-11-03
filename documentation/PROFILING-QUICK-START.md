# MINIX PROFILING QUICK START GUIDE

Quick reference for getting started with CPU profiling for MINIX boot analysis.

## Installation (5 Minutes)

```bash
# 1. Install core profiling tools (Arch/CachyOS)
sudo pacman -S perf valgrind

# 2. Install flamegraph toolkit (AUR)
yay -S flamegraph-git

# 3. Install Python profiling tools
pip install --user -r tools/profiling/requirements-profiling.txt

# 4. Optional: Install QProfiler for guest profiling
cd /home/eirikr/Playground
git clone https://github.com/torokernel/qprofiler.git
```

## Quick Test (2 Minutes)

```bash
# Profile a 10-second QEMU boot
cd /home/eirikr/Playground/minix-analysis

perf record -g -F 99 -o test.perf.data -- \
  timeout 10s qemu-system-i386 -cdrom minix.iso -m 512M -nographic

# Generate flamegraph
perf script -i test.perf.data | \
  stackcollapse-perf.pl | \
  flamegraph.pl > test-flamegraph.svg

# Open in browser
firefox test-flamegraph.svg
```

## Common Workflows

### 1. Profile MINIX Boot (Automated)

```bash
# Uses wrapper script
./tools/profiling/qemu-profile-boot.sh minix.iso 30 diagrams/profiling 001

# Output:
#   diagrams/profiling/boot-001.perf.data
#   diagrams/profiling/boot-001.svg (flamegraph)
#   diagrams/profiling/boot-001.json (metadata)
```

### 2. Profile Python Analysis Tools

```bash
# Profile minix_source_analyzer.py
py-spy record -o analyzer-profile.svg -- \
  python3 tools/minix_source_analyzer.py \
    --minix-root /home/eirikr/Playground/minix \
    --output diagrams/data

# View flamegraph
firefox analyzer-profile.svg
```

### 3. Deep Analysis with Callgrind

```bash
# WARNING: Very slow (10-50x overhead)
valgrind --tool=callgrind \
  --callgrind-out-file=qemu-boot.callgrind \
  qemu-system-i386 -cdrom minix.iso -nographic

# Visualize with GUI
kcachegrind qemu-boot.callgrind
```

### 4. Parse perf Data to JSON

```bash
# Convert perf.data to JSON for Python processing
python3 tools/profiling/parse_perf_data.py \
  diagrams/profiling/boot-001.perf.data \
  --output diagrams/profiling/boot-001-parsed.json

# View top 10 hotspots
jq '.hotspots[:10]' diagrams/profiling/boot-001-parsed.json
```

## Tool Selection Matrix

| Task | Tool | Overhead | Install |
|------|------|----------|---------|
| QEMU boot profiling | perf | <5% | `pacman -S perf` |
| Flamegraph visualization | flamegraph.pl | N/A | `yay -S flamegraph-git` |
| Python tool profiling | py-spy | <1% | `pip install py-spy` |
| Deep call graph analysis | valgrind | 10-50x | Already installed |
| Memory profiling | scalene | 10-20% | `pip install scalene` |
| Guest OS profiling | QProfiler | ~2% | Manual git clone |

## Interpreting Results

### Flamegraph Basics
- **Width**: Proportion of total samples (time spent)
- **Height**: Call stack depth
- **Color**: Random (no semantic meaning in standard flamegraphs)
- **Interactive**: Click to zoom, search by function name

### perf report (TUI)
```bash
perf report -i boot.perf.data
# Navigate with arrow keys, press 'a' to annotate assembly
```

### JSON Output Structure
```json
{
  "metadata": {
    "total_samples": 12345,
    "commands": ["qemu-system-i386"]
  },
  "hotspots": [
    {
      "function": "kvm_vcpu_ioctl",
      "sample_count": 500,
      "percentage": 4.05
    }
  ]
}
```

## Common Issues

### Issue: perf not found
**Solution**: `sudo pacman -S perf`

### Issue: stackcollapse-perf.pl command not found
**Solution**: `yay -S flamegraph-git` or add `/usr/share/flamegraph` to PATH

### Issue: py-spy fails to attach
**Solution**: Run with sudo: `sudo py-spy record -o profile.svg --pid <PID>`

### Issue: QEMU doesn't profile guest OS
**Solution**: Use QProfiler or perf kvm (requires guest symbols)

## Next Steps

1. **Read Full Guide**: `documentation/COMPREHENSIVE-CPU-PROFILING-GUIDE.md`
2. **Install Package**: `cd packaging && makepkg -si`
3. **Batch Profiling**: Run 40+ boots with automated script
4. **Combine with Source Analysis**: Integrate profiling data with source code locations

## Resources

- **Brendan Gregg's Perf Examples**: https://www.brendangregg.com/perf.html
- **FlameGraph Documentation**: https://github.com/brendangregg/FlameGraph
- **perf Tutorial**: https://perf.wiki.kernel.org/
- **QProfiler Repository**: https://github.com/torokernel/qprofiler
- **py-spy Documentation**: https://github.com/benfred/py-spy

## Quick Reference Card

```bash
# Record
perf record -g -F 99 -o out.perf.data -- <command>

# Report (TUI)
perf report -i out.perf.data

# Export to text
perf script -i out.perf.data > out.txt

# Flamegraph
perf script -i out.perf.data | stackcollapse-perf.pl | flamegraph.pl > out.svg

# Python profiling
py-spy record -o profile.svg -- python3 script.py

# System call trace
strace -c <command>

# Deep analysis
valgrind --tool=callgrind <command>
kcachegrind callgrind.out.*
```
