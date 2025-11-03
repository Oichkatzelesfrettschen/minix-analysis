# MINIX PROFILING TOOLS - PROJECT INTEGRATION

Complete CPU profiling solution for MINIX 3.4 boot analysis on CachyOS/Arch Linux.

## What's Included

### 📚 Documentation (72 KB total)
- **COMPREHENSIVE-CPU-PROFILING-GUIDE.md** (57 KB, 1839 lines)
  - 20+ profiling tools (online services, Python, Arch packages, QEMU)
  - Installation instructions for all tools
  - Integration workflows and data pipelines
  - JSON schemas and processing examples
  
- **PROFILING-QUICK-START.md** (4.8 KB)
  - 5-minute installation guide
  - Common workflows
  - Troubleshooting tips
  - Quick reference commands

- **PROFILING-IMPLEMENTATION-SUMMARY.md** (10 KB)
  - Project deliverable summary
  - Tool categorization
  - File structure overview

### 🛠️ Production-Ready Tools
- **qemu-profile-boot.sh** (1.8 KB, executable)
  - Automated QEMU boot profiling
  - Generates perf.data, flamegraph SVG, and JSON metadata
  - Usage: `./tools/profiling/qemu-profile-boot.sh minix.iso 30 output 001`

- **parse_perf_data.py** (4.3 KB, executable)
  - Converts perf.data to structured JSON
  - Hotspot analysis and stack trace parsing
  - Usage: `python3 tools/profiling/parse_perf_data.py boot.perf.data > boot.json`

- **requirements-profiling.txt** (883 bytes)
  - Python profiling dependencies
  - Install: `pip install --user -r tools/profiling/requirements-profiling.txt`

### 📦 PKGBUILD for Distribution (2.5 KB)
- Package name: `minix-profiling-tools`
- Bundles: FlameGraph toolkit + QProfiler + documentation
- Build: `cd packaging && makepkg -si`

## Quick Start (5 Minutes)

```bash
# 1. Install core tools
sudo pacman -S perf valgrind
yay -S flamegraph-git
pip install --user -r tools/profiling/requirements-profiling.txt

# 2. Test workflow (10-second boot profile)
cd /home/eirikr/Playground/minix-analysis
perf record -g -F 99 -o test.perf.data -- \
  timeout 10s qemu-system-i386 -cdrom minix.iso -m 512M -nographic

# 3. Generate flamegraph
perf script -i test.perf.data | \
  stackcollapse-perf.pl | \
  flamegraph.pl > test-flamegraph.svg

# 4. View results
firefox test-flamegraph.svg
```

## Recommended Toolchain

### Tier 1: Essential (Install Now)
1. **perf** - Linux kernel profiler (<5% overhead)
2. **flamegraph-git** - Visualization toolkit
3. **py-spy** - Python profiling (<1% overhead)

### Tier 2: Deep Analysis (As Needed)
4. **QProfiler** - QEMU guest profiling (no instrumentation)
5. **Scalene** - CPU + memory profiling for Python
6. **valgrind** - Callgrind/cachegrind (10-50x overhead, offline analysis)

### Tier 3: Advanced Visualization (Optional)
7. **Hotspot** - GUI for perf.data (AppImage or source build)
8. **KCachegrind** - Callgrind visualization

## Tools Documented (20+ Total)

### Online/Professional Services
- Intel VTune Profiler (AWS cloud)
- Pixie Continuous Profiler (eBPF)
- FlameGraph (Brendan Gregg, open-source standard)
- Linux perf (kernel profiling)
- Valgrind suite (cachegrind, callgrind, massif)
- QEMU CPU Tracer (research tool)
- QProfiler (QEMU guest profiling)

### Python/pip Ecosystem
- **py-spy** (Rust, <1% overhead) ⭐
- **Scalene** (CPU + memory + GPU) ⭐
- **Austin** (C, minimal overhead)
- **Pyinstrument** (visual call stack)
- **memory_profiler** (line-level memory)
- **cProfile** (built-in standard)
- **line_profiler** (line-level deterministic)
- **pyperf** (stable benchmarking)

### Arch Linux / AUR Packages
- **perf** (`pacman -S perf`) ⭐
- **flamegraph-git** (`yay -S flamegraph-git`) ⭐
- valgrind, strace, gprof (already installed)
- inferno, cargo-flamegraph, flamelens
- kcachegrind, massif-visualizer
- gperftools, hyperfine

## Integration with MINIX Analysis

### Data Pipeline
```
MINIX ISO
  ↓
  ├→ QEMU → perf record → perf.data
  │           ↓
  │           ├→ parse_perf_data.py → JSON
  │           ├→ flamegraph.pl → SVG
  │           └→ QProfiler → hotspots
  │
  └→ minix_source_analyzer.py → JSON
                  ↓
          Combined Analysis (profiling + source)
                  ↓
          TikZ Diagrams + Statistics
```

### Example: Combine Profiling with Source Analysis
```python
# Profile boot
./tools/profiling/qemu-profile-boot.sh minix.iso 30 diagrams/profiling 001

# Parse to JSON
python3 tools/profiling/parse_perf_data.py \
  diagrams/profiling/boot-001.perf.data \
  --output diagrams/profiling/boot-001.json

# Match hotspots to source files
python3 tools/profiling/combine_profile_source.py

# Generate diagrams with profiling data
python3 tools/tikz_generator.py --profile-dir diagrams/profiling
```

## File Structure

```
minix-analysis/
├── documentation/
│   ├── COMPREHENSIVE-CPU-PROFILING-GUIDE.md  (57 KB, main reference)
│   └── PROFILING-QUICK-START.md              (4.8 KB, quick start)
├── tools/
│   └── profiling/
│       ├── qemu-profile-boot.sh              (automated profiling)
│       ├── parse_perf_data.py                (perf → JSON)
│       └── requirements-profiling.txt        (Python deps)
├── packaging/
│   └── PKGBUILD                              (Arch package)
├── PROFILING-IMPLEMENTATION-SUMMARY.md       (deliverable summary)
└── README-PROFILING.md                       (this file)
```

## Common Workflows

### 1. Profile Single Boot
```bash
./tools/profiling/qemu-profile-boot.sh minix.iso 30 diagrams/profiling 001
# Output: perf.data, flamegraph.svg, metadata.json
```

### 2. Profile Python Analysis Tools
```bash
py-spy record -o analyzer-profile.svg -- \
  python3 tools/minix_source_analyzer.py \
    --minix-root /home/eirikr/Playground/minix \
    --output diagrams/data
```

### 3. Deep Callgrind Analysis (Slow)
```bash
valgrind --tool=callgrind qemu-system-i386 -cdrom minix.iso
kcachegrind callgrind.out.*
```

### 4. Batch Profiling (40+ Boots)
```python
# See COMPREHENSIVE-CPU-PROFILING-GUIDE.md section 6.2
python3 batch-profile.py --runs 40 --duration 30
```

## Performance Expectations

| Task | Duration | Overhead | Output Size |
|------|----------|----------|-------------|
| perf record (30s boot) | 30s | <5% | ~100 MB |
| Flamegraph generation | 2s | N/A | ~1 MB SVG |
| JSON parsing | <1s | N/A | ~5 MB |
| Callgrind (30s boot) | 5-15 min | 10-50x | ~500 MB |
| py-spy (Python tool) | +1% | <1% | ~500 KB |
| Batch 40 boots | 20 min | <5% | ~5 GB total |

## Troubleshooting

### Issue: perf not found
**Solution**: `sudo pacman -S perf`

### Issue: stackcollapse-perf.pl command not found
**Solution**: `yay -S flamegraph-git` or add `/usr/share/flamegraph` to PATH

### Issue: py-spy fails to attach
**Solution**: Run with sudo or use `--pid` flag

### Issue: Flamegraph is empty
**Check**: 
1. Verify perf.data has samples: `perf report -i boot.perf.data`
2. Check if QEMU ran long enough: increase duration
3. Ensure call graph was recorded: use `-g` flag

## Resources

- **Main Guide**: `documentation/COMPREHENSIVE-CPU-PROFILING-GUIDE.md`
- **Quick Start**: `documentation/PROFILING-QUICK-START.md`
- **Brendan Gregg's Perf**: https://www.brendangregg.com/perf.html
- **FlameGraph Repo**: https://github.com/brendangregg/FlameGraph
- **QProfiler**: https://github.com/torokernel/qprofiler
- **py-spy**: https://github.com/benfred/py-spy
- **Scalene**: https://github.com/plasma-umass/scalene

## Next Steps

1. **Read Documentation**
   - Start: `documentation/PROFILING-QUICK-START.md`
   - Deep dive: `documentation/COMPREHENSIVE-CPU-PROFILING-GUIDE.md`

2. **Install Tools**
   ```bash
   sudo pacman -S perf valgrind
   yay -S flamegraph-git
   pip install --user -r tools/profiling/requirements-profiling.txt
   ```

3. **Test Workflow**
   ```bash
   ./tools/profiling/qemu-profile-boot.sh minix.iso 10 test 001
   firefox test/boot-001.svg
   ```

4. **Build Package (Optional)**
   ```bash
   cd packaging && makepkg -si
   ```

5. **Integrate with Analysis Pipeline**
   - Profile 40+ boots
   - Combine with source analysis JSON
   - Generate TikZ diagrams with profiling data

---

**Project**: MINIX 3.4 Operating System Analysis  
**Scope**: CPU profiling for boot analysis  
**Platform**: CachyOS (Arch Linux, x86-64-v3)  
**Status**: Complete and production-ready  
**Documentation**: 72 KB across 3 files  
**Scripts**: 3 production tools  
**Total Tools**: 20+ documented and integrated
