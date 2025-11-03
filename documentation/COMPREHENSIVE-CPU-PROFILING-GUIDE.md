# COMPREHENSIVE CPU PROFILING GUIDE FOR MINIX ANALYSIS
# Document Version: 1.0 (2025-11-01)
# Scope: Complete profiling toolchain for MINIX boot analysis on CachyOS/Arch Linux

================================================================================
## TABLE OF CONTENTS
================================================================================

1. ONLINE/PROFESSIONAL PROFILING SERVICES
2. PYTHON/PIP ECOSYSTEM PROFILING TOOLS
3. ARCH LINUX / AUR PROFILING PACKAGES
4. QEMU-SPECIFIC PROFILING INTEGRATION
5. INTEGRATION APPROACHES AND WORKFLOWS
6. PRACTICAL RECOMMENDATIONS FOR MINIX
7. PACKAGING FOR THE PROJECT
8. PROCESSING PIPELINES AND DATA EXTRACTION

================================================================================
## 1. ONLINE/PROFESSIONAL PROFILING SERVICES
================================================================================

### 1.1 Cloud Platform Profiling Services

#### Intel VTune Profiler (AWS Integration)
- **Website**: https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html
- **Use Case**: Professional-grade profiling on AWS EC2 instances
- **Features**:
  - Web service mode for remote profiling
  - Hardware event sampling (PMU counters)
  - Hotspot detection and call graph analysis
  - Microarchitecture analysis
- **Pricing**: Free for development, paid for production use
- **MINIX Relevance**: Low (requires Intel hardware, cloud overhead)
- **Installation**: Download from Intel, requires registration

#### Pixie Continuous Profiler
- **Website**: https://px.dev/
- **Use Case**: eBPF-based continuous profiling for cloud applications
- **Features**:
  - Zero-instrumentation CPU profiling
  - Sub-1% overhead sampling profiler
  - Flamegraph visualization
  - Kubernetes integration
- **Pricing**: Open-source core, paid managed service
- **MINIX Relevance**: Low (designed for modern Linux, not MINIX 3.4)
- **Installation**: kubectl apply or self-hosted

#### Brendan Gregg's FlameGraph (Open Source Standard)
- **Website**: https://www.brendangregg.com/flamegraphs.html
- **Repository**: https://github.com/brendangregg/FlameGraph
- **Use Case**: De facto standard for CPU profile visualization
- **Features**:
  - Converts perf/DTrace output to SVG flamegraphs
  - Interactive visualization (zoom, search)
  - Memory, off-CPU, and differential flamegraphs
- **Pricing**: Free and open-source (CDDL/GPL)
- **MINIX Relevance**: HIGH (can visualize QEMU profiling data)
- **Installation**: `git clone` + Perl scripts

### 1.2 Academic/Open-Source Profiling Frameworks

#### Linux perf (perf_events)
- **Documentation**: https://perf.wiki.kernel.org/
- **Use Case**: Gold standard for Linux kernel/application profiling
- **Features**:
  - Hardware and software event sampling
  - Call graph recording (stack traces)
  - Kernel and user-space profiling
  - Low overhead (<5% typical)
- **MINIX Relevance**: HIGH (profile QEMU host, integrate with guest)
- **Installation**: `pacman -S perf` (linux-tools package)

#### Valgrind Cachegrind/Callgrind
- **Website**: https://valgrind.org/
- **Use Case**: Detailed cache simulation and call graph profiling
- **Features**:
  - Cache miss analysis (L1/L2/L3)
  - Instruction-level profiling
  - Call graph with cycle counts
  - KCachegrind visualization
- **Overhead**: 10-50x slowdown (deterministic, not sampling)
- **MINIX Relevance**: MEDIUM (can profile QEMU, high overhead)
- **Installation**: `pacman -S valgrind` (already installed)

#### QEMU CPU Tracer (QCT)
- **Paper**: "QEMU CPU Tracer – an Exact Profiling Tool" (ResearchGate)
- **Use Case**: Exact instruction-level tracing in QEMU
- **Features**:
  - Full trace of all CPU jumps
  - Supports both user-mode and system emulation
  - Exact (not statistical) profiling
- **Overhead**: 2x for sampling, 7x for full trace
- **MINIX Relevance**: HIGH (designed for OS boot analysis)
- **Installation**: Custom QEMU build (requires patch)

#### QProfiler
- **Repository**: https://github.com/torokernel/qprofiler
- **Use Case**: QEMU guest profiling via QMP (no guest instrumentation)
- **Features**:
  - Samples CPU registers from host
  - Identifies hotspot functions
  - No guest OS modifications needed
- **MINIX Relevance**: VERY HIGH (perfect for MINIX boot analysis)
- **Installation**: `git clone` + Python dependencies

================================================================================
## 2. PYTHON/PIP ECOSYSTEM PROFILING TOOLS
================================================================================

### 2.1 Sampling Profilers (Near-Zero Overhead)

#### py-spy (RECOMMENDED for production)
- **PyPI**: https://pypi.org/project/py-spy/
- **Install**: `pip install py-spy`
- **Language**: Rust (no Python overhead)
- **Overhead**: <1% typical
- **Features**:
  - Attach to running processes (no restart)
  - Flamegraph generation (`py-spy record --format flamegraph`)
  - Top-like real-time view (`py-spy top`)
  - Native (no GIL interference)
- **Use Case**: Profile minix_source_analyzer.py during boot data extraction
- **Example**:
  ```bash
  py-spy record -o profile.svg -- python3 tools/minix_source_analyzer.py
  py-spy record --format speedscope -o profile.speedscope -- python3 script.py
  ```

#### Austin (Minimal C Implementation)
- **PyPI**: https://pypi.org/project/austin-python/
- **Install**: `pip install austin-python` (also need `austin` binary)
- **Language**: Pure C (minimal dependencies)
- **Overhead**: <1% typical
- **Features**:
  - Sub-microsecond sampling
  - TUI for real-time monitoring
  - Flamegraph export
- **Use Case**: Lower-level profiling than py-spy
- **Example**:
  ```bash
  austin python3 script.py
  austin --format speedscope -o profile.speedscope python3 script.py
  ```

#### Pyinstrument (Visual Call Stack)
- **PyPI**: https://pypi.org/project/pyinstrument/
- **Install**: `pip install pyinstrument`
- **Overhead**: ~5-10%
- **Features**:
  - HTML output with interactive call tree
  - Shows percentage time per function
  - Clean visualization
- **Use Case**: Initial profiling to find hotspots
- **Example**:
  ```bash
  pyinstrument -o profile.html script.py
  python3 -m pyinstrument script.py
  ```

### 2.2 Comprehensive Profilers (CPU + Memory)

#### Scalene (RECOMMENDED for holistic analysis)
- **PyPI**: https://pypi.org/project/scalene/
- **Install**: `pip install scalene`
- **Overhead**: 10-20% typical
- **Features**:
  - **CPU profiling** (line-level granularity)
  - **Memory profiling** (allocations, leaks)
  - **GPU profiling** (CUDA, if applicable)
  - AI-powered optimization suggestions
  - HTML report with heatmaps
- **Use Case**: Deep analysis of TikZ generator memory usage
- **Example**:
  ```bash
  scalene tools/tikz_generator.py
  scalene --html --outfile report.html tools/minix_source_analyzer.py
  ```

#### memory_profiler (Line-Level Memory)
- **PyPI**: https://pypi.org/project/memory-profiler/
- **Install**: `pip install memory-profiler`
- **Features**:
  - Decorator-based profiling (`@profile`)
  - Line-by-line memory increments
  - Matplotlib visualization
- **Use Case**: Track JSON data size growth during parsing
- **Example**:
  ```python
  from memory_profiler import profile

  @profile
  def analyze_minix():
      # ... code ...
  ```

### 2.3 Deterministic Profilers (Call Graph Analysis)

#### cProfile (Built-in Standard)
- **Module**: `cProfile` (Python stdlib)
- **Install**: None (built-in)
- **Overhead**: 10-30%
- **Features**:
  - Function-level call counts and timings
  - Deterministic (every call tracked)
  - Export to pstats format
- **Use Case**: Baseline profiling, CI integration
- **Example**:
  ```bash
  python3 -m cProfile -o profile.pstats tools/minix_source_analyzer.py
  python3 -m pstats profile.pstats  # Interactive analysis
  ```

#### line_profiler (Line-Level Deterministic)
- **PyPI**: https://pypi.org/project/line-profiler/
- **Install**: `pip install line-profiler`
- **Features**:
  - Decorator-based (`@profile`)
  - Line-by-line timing
  - High overhead (only profile critical functions)
- **Use Case**: Optimize regex loops in source analyzer
- **Example**:
  ```python
  @profile
  def parse_syscalls(file_content):
      # ... line-level profiling ...
  ```

### 2.4 Flamegraph Generators

#### py-flame (Brendan Gregg Integration)
- **PyPI**: https://pypi.org/project/py-flame/
- **Install**: `pip install py-flame`
- **Features**:
  - Converts cProfile to flamegraph format
  - Integrates with FlameGraph toolkit
- **Example**:
  ```bash
  python3 -m cProfile -o profile.pstats script.py
  flameprof profile.pstats > flamegraph.svg
  ```

#### Pyflame (DEPRECATED but still useful)
- **AUR**: `yay -S python-pyflame` (if available)
- **Features**:
  - Attach to running Python processes
  - Generate flamegraphs
- **Status**: Unmaintained, use py-spy instead

### 2.5 QEMU/Perf Wrapper Libraries

#### perfplot (Perf Data Visualization)
- **PyPI**: https://pypi.org/project/perfplot/
- **Install**: `pip install perfplot`
- **Features**:
  - Benchmark multiple implementations
  - Matplotlib plotting
- **Use Case**: Compare regex vs tree-sitter for parsing

#### pyperf (Stable Benchmarking)
- **PyPI**: https://pypi.org/project/pyperf/
- **Install**: `pip install pyperf`
- **Features**:
  - Statistical benchmarking (warmup, multiple runs)
  - JSON output for reproducibility
- **Use Case**: Benchmark boot analysis pipeline stages

================================================================================
## 3. ARCH LINUX / AUR PROFILING PACKAGES
================================================================================

### 3.1 Core Profiling Tools (Official Repos)

#### perf (Linux Kernel Performance Tool)
- **Package**: `perf` (linux-tools)
- **Install**: `sudo pacman -S perf`
- **Repository**: extra
- **Description**: Linux kernel performance auditing tool
- **Key Commands**:
  ```bash
  perf record -g ./executable       # Record with call graph
  perf report                        # Interactive TUI
  perf script | flamegraph.pl > out.svg  # Flamegraph
  perf stat ./executable             # Hardware counter stats
  ```
- **MINIX Use Case**: Profile QEMU host performance
- **Integration**: `perf kvm` for guest/host profiling

#### valgrind (Memory Debugger + Profilers)
- **Package**: `valgrind`
- **Install**: Already installed (`3.25.1-3.1`)
- **Repository**: extra
- **Tools**:
  - **cachegrind**: Cache profiling
  - **callgrind**: Call graph + cache simulation
  - **massif**: Heap profiler
  - **memcheck**: Memory leak detector
- **Key Commands**:
  ```bash
  valgrind --tool=callgrind ./executable
  kcachegrind callgrind.out.<pid>   # Visualize

  valgrind --tool=cachegrind ./executable
  cg_annotate cachegrind.out.<pid>  # Cache miss analysis
  ```
- **Overhead**: 10-50x slowdown
- **MINIX Use Case**: Deep QEMU analysis (not for production)

#### strace (System Call Tracer)
- **Package**: `strace`
- **Install**: Already installed (`6.17-1.1`)
- **Features**:
  - Trace all system calls
  - Measure syscall latency
  - Filter by syscall type
- **Key Commands**:
  ```bash
  strace -c ./executable            # Summary statistics
  strace -T -o trace.log ./executable  # Timestamps
  strace -e trace=open,read ./exe   # Filter syscalls
  ```
- **MINIX Use Case**: Trace QEMU syscalls during boot

#### gprof (GNU Profiler)
- **Package**: `gprof` (binutils)
- **Install**: Already installed (part of binutils)
- **Features**:
  - Function-level profiling
  - Flat and call graph profiles
  - Requires recompilation with `-pg`
- **Key Commands**:
  ```bash
  gcc -pg -o executable source.c
  ./executable                      # Generates gmon.out
  gprof executable gmon.out > profile.txt
  ```
- **MINIX Use Case**: Profile custom QEMU builds

#### gperftools (Google Performance Tools)
- **Package**: `gperftools`
- **Install**: Already installed (`2.17.2-1.1`)
- **Features**:
  - CPU profiler (sampling-based)
  - Heap profiler
  - Heap checker (leak detection)
- **Key Commands**:
  ```bash
  LD_PRELOAD=/usr/lib/libprofiler.so CPUPROFILE=out.prof ./exe
  pprof --text ./exe out.prof
  pprof --svg ./exe out.prof > profile.svg
  ```
- **MINIX Use Case**: Profile C++ analysis tools (if written)

### 3.2 Visualization Tools (Official Repos)

#### massif-visualizer (Valgrind Heap Visualization)
- **Package**: `massif-visualizer`
- **Install**: `sudo pacman -S massif-visualizer`
- **Repository**: extra (KDE application)
- **Features**:
  - Graphical heap usage over time
  - Integration with Valgrind massif
- **Use Case**: Visualize QEMU memory growth during boot

### 3.3 Flamegraph Tools (AUR + Official)

#### flamegraph-git (Brendan Gregg's Scripts)
- **Package**: `flamegraph-git`
- **Install**: `yay -S flamegraph-git`
- **Repository**: AUR (+16 votes, 0.18 popularity)
- **Features**:
  - `stackcollapse-perf.pl` (convert perf output)
  - `flamegraph.pl` (generate SVG)
  - Differential flamegraphs (before/after comparison)
- **Use Case**: Visualize perf data from QEMU boot
- **Example**:
  ```bash
  perf record -g -F 99 ./qemu-system-i386 minix.iso
  perf script | stackcollapse-perf.pl | flamegraph.pl > boot.svg
  ```

#### inferno (Rust FlameGraph Port)
- **Package**: `inferno`
- **Install**: `sudo pacman -S inferno`
- **Repository**: extra, cachyos-extra-v3
- **Features**:
  - Faster than Perl version
  - Multi-threaded flamegraph generation
  - Compatible with perf output
- **Use Case**: Same as flamegraph, but faster for large datasets
- **Example**:
  ```bash
  perf script | inferno-collapse-perf > folded.txt
  inferno-flamegraph folded.txt > boot.svg
  ```

#### cargo-flamegraph (Rust-Specific)
- **Package**: `cargo-flamegraph`
- **Install**: `sudo pacman -S cargo-flamegraph`
- **Repository**: cachyos-extra-v3
- **Use Case**: Profile Rust components (if any in project)

#### flamelens (Terminal Flamegraph Viewer)
- **Package**: `flamelens`
- **Install**: `sudo pacman -S flamelens`
- **Repository**: cachyos-extra-v3
- **Features**:
  - TUI flamegraph viewer
  - Interactive navigation in terminal
- **Use Case**: Quick profiling review without browser

### 3.4 GUI Profiling Tools (AUR)

#### Hotspot (KDAB perf GUI) - NOT YET IN AUR
- **Expected Package**: `hotspot` or `hotspot-git`
- **Current Status**: NOT found in AUR search
- **Alternative Install**: AppImage or build from source
- **Repository**: https://github.com/KDAB/hotspot
- **Features**:
  - Modern Qt-based GUI for perf.data files
  - Timeline filtering by time/process/thread
  - Built-in flamegraph viewer
  - Launch perf from GUI
- **Installation (Manual)**:
  ```bash
  # AppImage method (easiest)
  wget https://github.com/KDAB/hotspot/releases/download/v1.5.0/hotspot-v1.5.0-x86_64.AppImage
  chmod +x hotspot-v1.5.0-x86_64.AppImage
  ./hotspot-v1.5.0-x86_64.AppImage

  # Or build from source
  git clone https://github.com/KDAB/hotspot.git
  cd hotspot
  mkdir build && cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
  make -j$(nproc)
  sudo make install
  ```
- **MINIX Use Case**: Interactive profiling of QEMU boot data

#### KCachegrind (Callgrind Visualizer)
- **Package**: `kcachegrind`
- **Install**: `sudo pacman -S kcachegrind`
- **Repository**: extra (KDE application)
- **Features**:
  - Visualize callgrind output
  - Call graph, source annotation
  - Comparative analysis (multiple runs)
- **Use Case**: Deep dive into QEMU call patterns

### 3.5 QEMU-Specific Packages (AUR)

#### qemu-git (Latest QEMU Development)
- **Package**: `qemu-git`
- **Install**: `yay -S qemu-git`
- **Repository**: AUR
- **Features**:
  - Latest QEMU features
  - Profiling hooks and tracing
- **Use Case**: Build with custom profiling patches

#### No MINIX-specific packages found in AUR
- **Search performed**: `minix`, `minix3`, `minix-tools`
- **Result**: No dedicated MINIX analysis tools in AUR
- **Opportunity**: Create `minix-analysis-tools` AUR package

================================================================================
## 4. QEMU-SPECIFIC PROFILING INTEGRATION
================================================================================

### 4.1 QEMU Tracing Framework

#### Built-in QEMU Tracing
- **Documentation**: https://wiki.qemu.org/Features/Tracing
- **Features**:
  - Light-weight event tracing at defined points
  - Enable/disable at runtime
  - Multiple backends (simple, ftrace, log, syslog)
- **Use Case**: Trace MINIX boot events in QEMU
- **Example**:
  ```bash
  # List available trace events
  qemu-system-i386 -trace help

  # Enable specific events
  qemu-system-i386 -trace "kvm_*" -cdrom minix.iso

  # Use ftrace backend
  qemu-system-i386 -trace "events=/tmp/trace-events" -cdrom minix.iso
  ```

### 4.2 perf kvm (Guest/Host Profiling)

#### perf kvm Integration
- **Documentation**: https://www.linux-kvm.org/page/Perf_events
- **Requirements**:
  - Guest kallsyms and modules files
  - Debug symbols for guest kernel
  - QEMU built with KVM support
- **Workflow**:
  ```bash
  # On host: record both host and guest events
  sudo perf kvm --host --guest -o perf.data record -a -g

  # Copy guest symbols from MINIX
  # (requires mounting MINIX filesystem or network transfer)
  mkdir -p ~/.debug/minix
  cp /path/to/minix/kallsyms ~/.debug/minix/
  cp /path/to/minix/modules ~/.debug/minix/

  # Analyze with guest symbol resolution
  perf kvm --guestmount ~/.debug/minix report
  ```
- **MINIX Challenge**: MINIX 3.4 may not export kallsyms easily
- **Solution**: Use QProfiler instead (no guest symbols needed)

### 4.3 QProfiler (Recommended for MINIX)

#### Installation and Setup
```bash
# Clone repository
cd /home/eirikr/Playground
git clone https://github.com/torokernel/qprofiler.git
cd qprofiler

# Install dependencies (if not already present)
pip install --user qmp  # QEMU Machine Protocol library

# QEMU must be started with QMP interface
qemu-system-i386 \
  -qmp tcp:localhost:4444,server,nowait \
  -cdrom /home/eirikr/Playground/minix-analysis/minix.iso \
  -enable-kvm -m 512M
```

#### Profiling Workflow
```bash
# Connect to QEMU and start profiling
python3 qprofiler.py --qmp localhost:4444 --duration 30 --interval 100

# Output: Function address histogram (most-used code regions)
# Post-process: Map addresses to MINIX symbols (requires disassembly)
```

#### Advantages for MINIX
- No guest instrumentation required
- Works without debug symbols (just addresses)
- Low overhead (sampling-based)
- Can profile boot loader and kernel init

### 4.4 QEMU CPU Tracer (QCT)

#### Research Paper Implementation
- **Paper**: "QEMU CPU Tracer – an Exact Profiling Tool" (2013)
- **Features**:
  - Full instruction-level trace
  - All jump/branch targets recorded
  - Exact (not statistical) profiling
- **Overhead**: 2x for sampling, 7x for full trace
- **Status**: Not actively maintained, may require porting to modern QEMU
- **Alternative**: Use QEMU TCG plugins (newer approach)

#### QEMU TCG Plugin Framework (Modern Approach)
- **Documentation**: https://qemu.readthedocs.io/en/latest/devel/tcg-plugins.html
- **Features**:
  - Custom instrumentation via plugins
  - Instruction count, memory access tracing
  - Built-in plugins: `execlog`, `hotpages`, `hotblocks`
- **Example**:
  ```bash
  qemu-system-i386 \
    -plugin contrib/plugins/libexeclog.so \
    -d plugin \
    -cdrom minix.iso
  ```
- **Use Case**: Identify hot code blocks during MINIX boot

### 4.5 Debugging QEMU with GDB + perf

#### Workflow for Deep Profiling
```bash
# Step 1: Build QEMU with debug symbols
git clone https://gitlab.com/qemu-project/qemu.git
cd qemu
./configure --enable-debug --enable-debug-info
make -j$(nproc)

# Step 2: Run under perf
perf record -g -F 99 ./build/qemu-system-i386 -cdrom minix.iso

# Step 3: Analyze with symbols
perf report --symfs ./build
perf script | flamegraph.pl > qemu-boot.svg
```

================================================================================
## 5. INTEGRATION APPROACHES AND WORKFLOWS
================================================================================

### 5.1 Wrapping perf Output in Python

#### Subprocess Integration
```python
import subprocess
import json
from pathlib import Path

def profile_qemu_boot(iso_path, duration=30):
    """Profile QEMU boot with perf and export to JSON."""

    # Start QEMU in background with perf
    perf_data = Path("boot.perf.data")
    qemu_cmd = [
        "qemu-system-i386",
        "-cdrom", str(iso_path),
        "-m", "512M",
        "-nographic"
    ]

    perf_cmd = [
        "perf", "record",
        "-o", str(perf_data),
        "-g",  # Call graph
        "-F", "99",  # 99 Hz sampling
        "--"
    ] + qemu_cmd

    print(f"Profiling QEMU boot for {duration} seconds...")
    proc = subprocess.Popen(perf_cmd)
    proc.wait(timeout=duration)
    proc.kill()

    # Export to JSON via perf script
    perf_script = subprocess.run(
        ["perf", "script", "-i", str(perf_data)],
        capture_output=True,
        text=True
    )

    # Parse stack traces (simplified)
    samples = []
    for line in perf_script.stdout.splitlines():
        if line.strip() and not line.startswith("#"):
            samples.append(line.strip())

    return {
        "duration": duration,
        "sample_count": len(samples),
        "raw_samples": samples[:100],  # First 100 samples
        "perf_data_file": str(perf_data)
    }

# Usage
result = profile_qemu_boot(
    iso_path="/home/eirikr/Playground/minix-analysis/minix.iso",
    duration=30
)
print(json.dumps(result, indent=2))
```

### 5.2 Integrating cachegrind with QEMU

#### Callgrind Profiling of QEMU
```bash
# Profile QEMU itself with callgrind
valgrind --tool=callgrind \
  --callgrind-out-file=qemu-boot.callgrind \
  qemu-system-i386 -cdrom minix.iso -nographic

# Visualize with kcachegrind
kcachegrind qemu-boot.callgrind

# Or convert to JSON for Python processing
callgrind_annotate --tree=both qemu-boot.callgrind > callgrind.txt
```

#### Python Parser for Callgrind Output
```python
import re
from pathlib import Path

def parse_callgrind_summary(callgrind_file):
    """Extract hotspot functions from callgrind output."""

    result = subprocess.run(
        ["callgrind_annotate", "--tree=both", str(callgrind_file)],
        capture_output=True,
        text=True
    )

    hotspots = []
    for line in result.stdout.splitlines():
        # Parse lines like: "1,234,567  10.5%  function_name"
        match = re.match(r'\s*([\d,]+)\s+(\d+\.\d+)%\s+(.+)', line)
        if match:
            ir_executed, percentage, function = match.groups()
            hotspots.append({
                "function": function.strip(),
                "ir_count": int(ir_executed.replace(",", "")),
                "percentage": float(percentage)
            })

    return sorted(hotspots, key=lambda x: x["percentage"], reverse=True)

# Usage
hotspots = parse_callgrind_summary("qemu-boot.callgrind")
print(f"Top 10 QEMU hotspots during boot:")
for i, hs in enumerate(hotspots[:10], 1):
    print(f"{i}. {hs['function']}: {hs['percentage']}%")
```

### 5.3 Using Hotspot GUI for Interactive Analysis

#### Workflow with Hotspot (once installed)
```bash
# Step 1: Record perf data
perf record -g -F 999 qemu-system-i386 -cdrom minix.iso

# Step 2: Open in Hotspot (GUI)
hotspot perf.data

# Hotspot provides:
# - Timeline view (zoom to specific boot phases)
# - Flamegraph view (interactive, searchable)
# - Call/Caller table (who called what)
# - Source annotation (if debug symbols available)
```

#### Exporting Hotspot Data for Python
```bash
# Hotspot can export to JSON (if feature available)
# Otherwise, use perf script as intermediary

perf script -i perf.data --fields comm,tid,time,event,ip,sym > perf-export.txt

# Python parser
import pandas as pd

def parse_perf_script(script_file):
    """Parse perf script output into DataFrame."""
    data = []
    with open(script_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 4:
                    data.append({
                        "command": parts[0],
                        "tid": int(parts[1]),
                        "time": float(parts[2].rstrip(":")),
                        "symbol": " ".join(parts[3:])
                    })
    return pd.DataFrame(data)

df = parse_perf_script("perf-export.txt")
print(df.groupby("symbol").size().sort_values(ascending=False).head(20))
```

### 5.4 Generating Flamegraphs from Boot Data

#### Complete Flamegraph Pipeline
```bash
#!/bin/bash
# flamegraph-boot.sh - Generate flamegraph from MINIX boot

ISO="/home/eirikr/Playground/minix-analysis/minix.iso"
DURATION=30
OUTPUT="diagrams/profiling/boot-flamegraph.svg"

# Step 1: Profile with perf
perf record -g -F 99 -o boot.perf.data -- \
  timeout ${DURATION}s qemu-system-i386 -cdrom "$ISO" -nographic

# Step 2: Generate flamegraph
perf script -i boot.perf.data | \
  /usr/share/flamegraph/stackcollapse-perf.pl | \
  /usr/share/flamegraph/flamegraph.pl --title "MINIX Boot (${DURATION}s)" > "$OUTPUT"

echo "Flamegraph saved to: $OUTPUT"
```

#### Python Wrapper with Metadata
```python
import subprocess
from pathlib import Path
import time

def generate_boot_flamegraph(iso_path, output_dir, duration=30, samples=99):
    """Generate flamegraph from QEMU boot and save metadata."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    perf_data = output_dir / f"boot-{timestamp}.perf.data"
    flamegraph_svg = output_dir / f"boot-{timestamp}.svg"

    # Step 1: perf record
    qemu_cmd = [
        "qemu-system-i386",
        "-cdrom", str(iso_path),
        "-m", "512M",
        "-nographic"
    ]

    perf_cmd = [
        "perf", "record",
        "-g",
        "-F", str(samples),
        "-o", str(perf_data),
        "--"
    ] + qemu_cmd

    print(f"Recording perf data for {duration}s...")
    proc = subprocess.Popen(perf_cmd)
    time.sleep(duration)
    proc.terminate()
    proc.wait()

    # Step 2: Generate flamegraph
    print("Generating flamegraph...")
    perf_script = subprocess.run(
        ["perf", "script", "-i", str(perf_data)],
        capture_output=True,
        text=True
    )

    collapse = subprocess.run(
        ["/usr/share/flamegraph/stackcollapse-perf.pl"],
        input=perf_script.stdout,
        capture_output=True,
        text=True
    )

    flamegraph = subprocess.run(
        ["/usr/share/flamegraph/flamegraph.pl",
         "--title", f"MINIX Boot ({duration}s)"],
        input=collapse.stdout,
        capture_output=True,
        text=True
    )

    flamegraph_svg.write_text(flamegraph.stdout)

    # Metadata
    metadata = {
        "timestamp": timestamp,
        "duration_seconds": duration,
        "sampling_frequency": samples,
        "iso_path": str(iso_path),
        "perf_data": str(perf_data),
        "flamegraph": str(flamegraph_svg),
        "sample_count": perf_script.stdout.count("\n")
    }

    (output_dir / f"boot-{timestamp}.json").write_text(
        json.dumps(metadata, indent=2)
    )

    print(f"Flamegraph: {flamegraph_svg}")
    print(f"Metadata: {output_dir}/boot-{timestamp}.json")
    return metadata
```

================================================================================
## 6. PRACTICAL RECOMMENDATIONS FOR MINIX
================================================================================

### 6.1 Best Tools for ISO Boot Profiling

#### Tier 1: Essential Tools (Install Immediately)
1. **perf** (`pacman -S perf`)
   - Industry standard, low overhead
   - Works with QEMU out of the box
   - **Use for**: Host-side profiling, QEMU overhead analysis

2. **flamegraph-git** (`yay -S flamegraph-git`)
   - Visualize perf output
   - Interactive SVG for exploration
   - **Use for**: Identifying boot hotspots visually

3. **py-spy** (`pip install py-spy`)
   - Profile Python analysis tools
   - Zero-overhead production profiling
   - **Use for**: Optimizing minix_source_analyzer.py

#### Tier 2: Deep Analysis Tools (Install as Needed)
4. **QProfiler** (manual install, https://github.com/torokernel/qprofiler)
   - Guest profiling without instrumentation
   - **Use for**: MINIX kernel hotspot identification

5. **Scalene** (`pip install scalene`)
   - CPU + memory profiling for Python
   - **Use for**: Full pipeline optimization

6. **valgrind/callgrind** (already installed)
   - Detailed call graph analysis
   - **Use for**: Offline deep-dive into QEMU behavior

#### Tier 3: Advanced Visualization (Optional)
7. **Hotspot** (AppImage or build from source)
   - GUI for perf.data exploration
   - **Use for**: Interactive timeline analysis

8. **KCachegrind** (`pacman -S kcachegrind`)
   - Visualize callgrind data
   - **Use for**: Cache miss analysis

### 6.2 Tools That Scale to 40+ Boot Samples

#### Recommended: Automated Batch Profiling
```python
# batch-profile.py - Profile multiple boots and aggregate
import subprocess
import json
from pathlib import Path

def profile_multiple_boots(iso_path, num_runs=40, duration=30):
    """Profile N boots and aggregate data."""

    output_dir = Path("diagrams/profiling/batch")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_metadata = []

    for run in range(1, num_runs + 1):
        print(f"\n=== Boot {run}/{num_runs} ===")

        perf_data = output_dir / f"boot-{run:03d}.perf.data"

        # Profile this boot
        qemu_cmd = [
            "qemu-system-i386",
            "-cdrom", str(iso_path),
            "-m", "512M",
            "-nographic"
        ]

        perf_cmd = [
            "perf", "record",
            "-g", "-F", "99",
            "-o", str(perf_data),
            "--"
        ] + qemu_cmd

        proc = subprocess.Popen(perf_cmd)
        proc.wait(timeout=duration)
        proc.kill()

        # Extract sample count
        perf_script = subprocess.run(
            ["perf", "script", "-i", str(perf_data)],
            capture_output=True,
            text=True
        )

        sample_count = perf_script.stdout.count("\n")

        metadata = {
            "run": run,
            "perf_data": str(perf_data),
            "sample_count": sample_count,
            "duration": duration
        }

        all_metadata.append(metadata)
        print(f"  Samples: {sample_count}")

    # Aggregate all perf data
    print("\n=== Merging all perf data ===")
    merged_perf = output_dir / "boot-merged.perf.data"

    subprocess.run([
        "perf", "buildid-list",
        "-o", str(merged_perf)
    ] + [str(m["perf_data"]) for m in all_metadata])

    # Generate aggregate flamegraph
    print("=== Generating aggregate flamegraph ===")
    perf_script = subprocess.run(
        ["perf", "script", "-i", str(merged_perf)],
        capture_output=True,
        text=True
    )

    collapse = subprocess.run(
        ["/usr/share/flamegraph/stackcollapse-perf.pl"],
        input=perf_script.stdout,
        capture_output=True,
        text=True
    )

    flamegraph = subprocess.run(
        ["/usr/share/flamegraph/flamegraph.pl",
         "--title", f"MINIX Boot Aggregate (N={num_runs})"],
        input=collapse.stdout,
        capture_output=True,
        text=True
    )

    flamegraph_path = output_dir / "boot-aggregate.svg"
    flamegraph_path.write_text(flamegraph.stdout)

    # Save metadata
    (output_dir / "batch-metadata.json").write_text(
        json.dumps(all_metadata, indent=2)
    )

    print(f"\nAggregate flamegraph: {flamegraph_path}")
    print(f"Total samples: {sum(m['sample_count'] for m in all_metadata)}")

    return all_metadata
```

#### Scaling Considerations
- **perf**: Handles millions of samples efficiently
- **flamegraph**: SVG size grows with unique stacks (typically <10 MB)
- **JSON storage**: ~1 KB per boot metadata entry
- **Total disk usage**: ~5 GB for 40 boots (perf.data ~100 MB each)

### 6.3 Tools with Best Python/JSON Integration

#### Recommended Data Pipeline
```
QEMU Boot → perf record → perf script → Python Parser → JSON → Analysis
```

#### Example: Full Integration
```python
# profiling_pipeline.py - Complete profiling and analysis

import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

class BootProfiler:
    def __init__(self, iso_path, output_dir="diagrams/profiling"):
        self.iso_path = Path(iso_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def record_boot(self, duration=30, run_id=1):
        """Record perf data for one boot."""
        perf_data = self.output_dir / f"boot-{run_id:03d}.perf.data"

        qemu_cmd = [
            "qemu-system-i386",
            "-cdrom", str(self.iso_path),
            "-m", "512M", "-nographic"
        ]

        perf_cmd = [
            "perf", "record", "-g", "-F", "99",
            "-o", str(perf_data), "--"
        ] + qemu_cmd

        proc = subprocess.Popen(perf_cmd)
        proc.wait(timeout=duration)
        proc.kill()

        return perf_data

    def parse_perf_data(self, perf_data):
        """Parse perf.data into structured JSON."""
        result = subprocess.run(
            ["perf", "script", "-i", str(perf_data)],
            capture_output=True, text=True
        )

        stacks = []
        current_stack = None

        for line in result.stdout.splitlines():
            if not line.strip() or line.startswith("#"):
                continue

            # Sample header: "qemu-system-i38 12345 123.456: cycles:"
            if re.match(r'^\S+\s+\d+', line):
                if current_stack:
                    stacks.append(current_stack)

                parts = line.split()
                current_stack = {
                    "command": parts[0],
                    "tid": int(parts[1]),
                    "time": float(parts[2].rstrip(":")),
                    "frames": []
                }
            else:
                # Stack frame: "    7fff12345678 symbol_name (/path/to/lib.so)"
                match = re.match(r'\s+([0-9a-f]+)\s+(.+)', line)
                if match and current_stack:
                    addr, symbol = match.groups()
                    current_stack["frames"].append({
                        "address": addr,
                        "symbol": symbol.strip()
                    })

        if current_stack:
            stacks.append(current_stack)

        return stacks

    def analyze_hotspots(self, stacks):
        """Identify hotspot functions from stacks."""
        function_counts = defaultdict(int)

        for stack in stacks:
            for frame in stack.get("frames", []):
                symbol = frame["symbol"]
                # Extract function name (before '(')
                func = symbol.split("(")[0].strip()
                function_counts[func] += 1

        total = sum(function_counts.values())
        hotspots = []

        for func, count in sorted(
            function_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]:  # Top 50
            hotspots.append({
                "function": func,
                "sample_count": count,
                "percentage": (count / total) * 100 if total > 0 else 0
            })

        return hotspots

    def profile_and_analyze(self, duration=30, run_id=1):
        """Complete workflow: record + parse + analyze."""
        print(f"Recording boot {run_id}...")
        perf_data = self.record_boot(duration, run_id)

        print("Parsing perf data...")
        stacks = self.parse_perf_data(perf_data)

        print("Analyzing hotspots...")
        hotspots = self.analyze_hotspots(stacks)

        # Save results
        json_path = self.output_dir / f"boot-{run_id:03d}.json"
        json_path.write_text(json.dumps({
            "run_id": run_id,
            "duration": duration,
            "stack_count": len(stacks),
            "hotspots": hotspots
        }, indent=2))

        print(f"Results saved to: {json_path}")
        print(f"\nTop 10 hotspots:")
        for i, hs in enumerate(hotspots[:10], 1):
            print(f"  {i}. {hs['function']}: "
                  f"{hs['percentage']:.2f}% "
                  f"({hs['sample_count']} samples)")

        return hotspots

# Usage
profiler = BootProfiler(
    iso_path="/home/eirikr/Playground/minix-analysis/minix.iso"
)
profiler.profile_and_analyze(duration=30, run_id=1)
```

### 6.4 Tools Already Installed on CachyOS

#### Currently Available (No Installation Needed)
- **valgrind** (3.25.1-3.1)
- **strace** (6.17-1.1)
- **gprof** (part of binutils)
- **gperftools** (2.17.2-1.1)
- **hyperfine** (1.19.0-1.1) - Benchmarking tool
- **libtraceevent** (1:1.8.4-1.1) - perf dependency
- **libtracefs** (1.8.2-2.1) - ftrace support

#### Need to Install
- **perf**: `sudo pacman -S perf`
- **flamegraph**: `yay -S flamegraph-git`
- **py-spy**: `pip install --user py-spy`
- **scalene**: `pip install --user scalene`
- **QProfiler**: Manual git clone

### 6.5 Custom Wrappers for QEMU Profiling

#### Recommended Wrapper Script
```bash
#!/bin/bash
# qemu-profile-boot.sh - One-command MINIX boot profiling

set -e

ISO="${1:-/home/eirikr/Playground/minix-analysis/minix.iso}"
DURATION="${2:-30}"
OUTPUT_DIR="${3:-diagrams/profiling}"
RUN_ID="${4:-$(date +%s)}"

mkdir -p "$OUTPUT_DIR"

PERF_DATA="$OUTPUT_DIR/boot-$RUN_ID.perf.data"
FLAMEGRAPH="$OUTPUT_DIR/boot-$RUN_ID.svg"
JSON="$OUTPUT_DIR/boot-$RUN_ID.json"

echo "=== MINIX Boot Profiling ==="
echo "ISO: $ISO"
echo "Duration: ${DURATION}s"
echo "Output: $OUTPUT_DIR"
echo ""

# Step 1: Profile with perf
echo "[1/3] Recording perf data..."
timeout "${DURATION}s" perf record \
  -g -F 99 \
  -o "$PERF_DATA" \
  -- qemu-system-i386 -cdrom "$ISO" -m 512M -nographic \
  || true  # Ignore timeout exit code

# Step 2: Generate flamegraph
echo "[2/3] Generating flamegraph..."
perf script -i "$PERF_DATA" | \
  /usr/share/flamegraph/stackcollapse-perf.pl | \
  /usr/share/flamegraph/flamegraph.pl \
    --title "MINIX Boot ($RUN_ID)" \
    > "$FLAMEGRAPH"

# Step 3: Extract metadata to JSON
echo "[3/3] Extracting metadata..."
SAMPLE_COUNT=$(perf script -i "$PERF_DATA" | wc -l)

cat > "$JSON" <<EOF
{
  "run_id": "$RUN_ID",
  "iso_path": "$ISO",
  "duration_seconds": $DURATION,
  "sample_count": $SAMPLE_COUNT,
  "perf_data": "$PERF_DATA",
  "flamegraph": "$FLAMEGRAPH"
}
EOF

echo ""
echo "=== Profiling Complete ==="
echo "Flamegraph: $FLAMEGRAPH"
echo "Metadata: $JSON"
echo "Samples: $SAMPLE_COUNT"
```

#### Make it executable
```bash
chmod +x tools/qemu-profile-boot.sh

# Usage
./tools/qemu-profile-boot.sh minix.iso 30 diagrams/profiling 001
```

================================================================================
## 7. PACKAGING FOR THE PROJECT
================================================================================

### 7.1 Create PKGBUILD for minix-profiling-tools

```bash
# File: /home/eirikr/Playground/minix-analysis/packaging/PKGBUILD

pkgname=minix-profiling-tools
pkgver=1.0.0
pkgrel=1
pkgdesc="Profiling toolchain for MINIX OS analysis (perf, flamegraph, wrappers)"
arch=('x86_64')
url="https://github.com/oaich/minix-analysis"
license=('MIT')
depends=(
  'perf'                # Linux perf tool
  'python'              # Python 3
  'qemu-system-x86'     # QEMU emulator
  'imagemagick'         # For diagram conversion
)
makedepends=(
  'git'
)
optdepends=(
  'valgrind: Deep profiling with cachegrind/callgrind'
  'kcachegrind: Visualize callgrind data'
  'python-py-spy: Low-overhead Python profiler'
  'python-scalene: CPU + memory profiler'
  'hotspot: GUI for perf data (manual install)'
)
source=(
  "flamegraph::git+https://github.com/brendangregg/FlameGraph.git"
  "qprofiler::git+https://github.com/torokernel/qprofiler.git"
  "qemu-profile-boot.sh"
  "batch-profile.py"
  "profiling_pipeline.py"
)
sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')

package() {
  # Install flamegraph scripts
  install -dm755 "$pkgdir/usr/share/flamegraph"
  install -Dm755 flamegraph/*.pl "$pkgdir/usr/share/flamegraph/"

  # Install QProfiler
  install -dm755 "$pkgdir/usr/share/qprofiler"
  cp -r qprofiler/* "$pkgdir/usr/share/qprofiler/"

  # Install wrapper scripts
  install -Dm755 qemu-profile-boot.sh "$pkgdir/usr/bin/qemu-profile-boot"
  install -Dm755 batch-profile.py "$pkgdir/usr/bin/minix-batch-profile"
  install -Dm755 profiling_pipeline.py "$pkgdir/usr/bin/minix-profile-pipeline"

  # Install documentation
  install -Dm644 "$srcdir/../COMPREHENSIVE-CPU-PROFILING-GUIDE.md" \
    "$pkgdir/usr/share/doc/$pkgname/README.md"
}
```

#### Build and Install
```bash
cd /home/eirikr/Playground/minix-analysis/packaging
makepkg -si
```

### 7.2 Document pip Install Commands

```bash
# File: tools/requirements-profiling.txt

# Sampling profilers (low overhead)
py-spy>=0.3.14           # Rust-based sampling profiler
austin-python>=1.7.0     # C-based sampling profiler
pyinstrument>=4.6.0      # Visual call stack profiler

# Comprehensive profilers
scalene>=1.5.0           # CPU + memory + GPU profiling
memory-profiler>=0.61.0  # Line-level memory profiling

# Deterministic profilers
line-profiler>=4.1.0     # Line-level CPU profiling

# Benchmarking
pyperf>=2.6.0            # Stable benchmarking framework
perfplot>=0.10.0         # Benchmark visualization

# Data processing
pandas>=2.0.0            # For perf data analysis
matplotlib>=3.7.0        # Plotting

# Optional: QEMU integration
# (QProfiler has no pip package, manual install)
```

#### Installation Command
```bash
cd /home/eirikr/Playground/minix-analysis
pip install --user -r tools/requirements-profiling.txt
```

### 7.3 Wrapper Scripts Integration

#### Create tools/profiling/ Directory
```bash
mkdir -p /home/eirikr/Playground/minix-analysis/tools/profiling
```

#### File Structure
```
tools/profiling/
├── qemu-profile-boot.sh      # Single boot profiling
├── batch-profile.py          # Multiple boot automation
├── profiling_pipeline.py     # Full Python pipeline
├── parse_perf_data.py        # perf.data → JSON converter
├── generate_flamegraph.sh    # Standalone flamegraph generator
└── aggregate_profiles.py     # Merge multiple perf.data files
```

### 7.4 Processing Pipelines Documentation

```python
# File: tools/profiling/parse_perf_data.py
"""
Parse perf.data files into structured JSON for analysis.

Usage:
    python3 parse_perf_data.py boot.perf.data > boot.json

Output format:
    {
      "metadata": {
        "perf_version": "6.17",
        "command": "qemu-system-i386",
        "total_samples": 12345
      },
      "stacks": [
        {
          "tid": 12345,
          "time": 123.456,
          "frames": [
            {"address": "0x7fff12345678", "symbol": "kvm_vcpu_ioctl"}
          ]
        }
      ],
      "hotspots": [
        {"function": "kvm_vcpu_ioctl", "samples": 500, "percentage": 4.05}
      ]
    }
"""

import subprocess
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

def parse_perf_data_to_json(perf_data_file):
    """Convert perf.data to structured JSON."""
    # [Implementation from section 6.3]
    pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    result = parse_perf_data_to_json(sys.argv[1])
    print(json.dumps(result, indent=2))
```

================================================================================
## 8. PROCESSING PIPELINES AND DATA EXTRACTION
================================================================================

### 8.1 Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MINIX Boot Analysis Pipeline              │
└─────────────────────────────────────────────────────────────┘

┌───────────┐
│ MINIX ISO │
└─────┬─────┘
      │
      ├─────────────────────────────────────────────────────┐
      │                                                     │
      v                                                     v
┌──────────────┐                                   ┌──────────────┐
│ QEMU Emulator│                                   │Source Analysis│
└──────┬───────┘                                   └──────┬───────┘
       │                                                  │
       v                                                  v
┌──────────────┐                                   ┌──────────────┐
│  perf record │                                   │JSON Extraction│
└──────┬───────┘                                   └──────┬───────┘
       │                                                  │
       v                                                  │
┌──────────────┐                                         │
│ perf.data    │                                         │
└──────┬───────┘                                         │
       │                                                  │
       ├────────────┬────────────┬─────────────┐         │
       │            │            │             │         │
       v            v            v             v         v
┌────────────┐ ┌────────┐ ┌────────────┐ ┌────────────────────┐
│perf script │ │flamegr.│ │ QProfiler  │ │Combined Analysis   │
│ → JSON     │ │→ SVG   │ │ → hotspots │ │(profiling + source)│
└──────┬─────┘ └────┬───┘ └──────┬─────┘ └─────────┬──────────┘
       │            │            │                  │
       └────────────┴────────────┴──────────────────┘
                           │
                           v
                  ┌────────────────┐
                  │Unified JSON DB │
                  └────────┬───────┘
                           │
                           v
                  ┌────────────────┐
                  │  TikZ Diagrams │
                  │  + Statistics  │
                  └────────────────┘
```

### 8.2 JSON Schema for Profiling Data

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MINIX Boot Profiling Data",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "run_id": {"type": "string"},
        "timestamp": {"type": "integer"},
        "iso_path": {"type": "string"},
        "duration_seconds": {"type": "number"},
        "qemu_version": {"type": "string"},
        "perf_version": {"type": "string"}
      }
    },
    "samples": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "time": {"type": "number"},
          "tid": {"type": "integer"},
          "cpu": {"type": "integer"},
          "event": {"type": "string"},
          "stack": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "address": {"type": "string"},
                "symbol": {"type": "string"},
                "module": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "hotspots": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "function": {"type": "string"},
          "module": {"type": "string"},
          "sample_count": {"type": "integer"},
          "percentage": {"type": "number"},
          "self_time": {"type": "number"},
          "total_time": {"type": "number"}
        }
      }
    },
    "timeline": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "time_bucket": {"type": "number"},
          "sample_count": {"type": "integer"},
          "top_function": {"type": "string"}
        }
      }
    }
  }
}
```

### 8.3 Example: Integrating Profiling with Source Analysis

```python
# File: tools/profiling/combine_profile_source.py
"""
Combine profiling data with source code analysis.

Matches hotspot functions from perf with MINIX source locations.
"""

import json
from pathlib import Path

def load_profiling_data(profile_json):
    """Load JSON from perf analysis."""
    with open(profile_json) as f:
        return json.load(f)

def load_source_analysis(source_json):
    """Load JSON from minix_source_analyzer.py."""
    with open(source_json) as f:
        return json.load(f)

def match_hotspots_to_source(profile_data, source_data):
    """Match profiled functions to source file locations."""

    hotspots = profile_data.get("hotspots", [])
    syscalls = source_data.get("syscalls", [])

    # Build function → file mapping from source analysis
    func_to_file = {}
    for sc in syscalls:
        func = sc["name"]
        file_path = sc["file"]
        func_to_file[func] = file_path

    # Annotate hotspots with source locations
    annotated = []
    for hs in hotspots:
        func = hs["function"]

        # Try to match (may need fuzzy matching)
        source_file = func_to_file.get(func, "unknown")

        annotated.append({
            **hs,
            "source_file": source_file,
            "matched": source_file != "unknown"
        })

    return annotated

def generate_combined_report(profile_json, source_json, output_json):
    """Create unified profiling + source analysis report."""

    profile = load_profiling_data(profile_json)
    source = load_source_analysis(source_json)

    hotspots = match_hotspots_to_source(profile, source)

    report = {
        "summary": {
            "total_samples": profile["metadata"]["total_samples"],
            "duration": profile["metadata"]["duration_seconds"],
            "hotspot_count": len(hotspots),
            "matched_count": sum(1 for h in hotspots if h["matched"])
        },
        "hotspots_with_source": hotspots,
        "syscall_frequency": analyze_syscall_frequency(hotspots, source)
    }

    with open(output_json, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Combined report: {output_json}")
    return report

def analyze_syscall_frequency(hotspots, source):
    """Determine which syscalls are hot during boot."""
    syscall_samples = {}

    for hs in hotspots:
        if hs["matched"]:
            # Extract syscall name (e.g., do_fork from kernel/system/do_fork.c)
            func = hs["function"]
            if func.startswith("do_"):
                syscall_samples[func] = hs["sample_count"]

    return sorted(
        [{"syscall": k, "samples": v} for k, v in syscall_samples.items()],
        key=lambda x: x["samples"],
        reverse=True
    )

# Usage
if __name__ == "__main__":
    generate_combined_report(
        profile_json="diagrams/profiling/boot-001.json",
        source_json="diagrams/data/syscalls.json",
        output_json="diagrams/profiling/combined-001.json"
    )
```

### 8.4 Automated Pipeline Script

```bash
#!/bin/bash
# File: tools/profiling/full-analysis-pipeline.sh
# Complete end-to-end MINIX analysis with profiling

set -e

ISO="/home/eirikr/Playground/minix-analysis/minix.iso"
MINIX_ROOT="/home/eirikr/Playground/minix"
OUTPUT_DIR="diagrams/profiling"
DATA_DIR="diagrams/data"

echo "=== MINIX Full Analysis Pipeline ==="
echo ""

# Step 1: Source code analysis
echo "[1/6] Analyzing MINIX source code..."
python3 tools/minix_source_analyzer.py \
  --minix-root "$MINIX_ROOT" \
  --output "$DATA_DIR"

# Step 2: Profile boot
echo "[2/6] Profiling QEMU boot..."
tools/profiling/qemu-profile-boot.sh "$ISO" 30 "$OUTPUT_DIR" 001

# Step 3: Parse perf data
echo "[3/6] Parsing perf data..."
python3 tools/profiling/parse_perf_data.py \
  "$OUTPUT_DIR/boot-001.perf.data" \
  > "$OUTPUT_DIR/boot-001.json"

# Step 4: Combine profiling + source
echo "[4/6] Combining profiling with source analysis..."
python3 tools/profiling/combine_profile_source.py

# Step 5: Generate diagrams
echo "[5/6] Generating TikZ diagrams..."
python3 tools/tikz_generator.py \
  --data-dir "$DATA_DIR" \
  --profile-dir "$OUTPUT_DIR" \
  --output diagrams/tikz-generated

# Step 6: Compile diagrams
echo "[6/6] Compiling diagrams to PDF..."
cd diagrams/tikz-generated
for tex in *.tex; do
  pdflatex -interaction=nonstopmode "$tex" > /dev/null 2>&1
  echo "  Compiled: $tex"
done

echo ""
echo "=== Pipeline Complete ==="
echo "Profiling data: $OUTPUT_DIR"
echo "Diagrams: diagrams/tikz-generated"
```

================================================================================
## APPENDIX: QUICK REFERENCE COMMANDS
================================================================================

### Essential Profiling Commands

```bash
# Install profiling tools
sudo pacman -S perf valgrind
yay -S flamegraph-git
pip install --user py-spy scalene

# Profile QEMU boot (30 seconds)
perf record -g -F 99 -o boot.perf.data -- \
  timeout 30s qemu-system-i386 -cdrom minix.iso -nographic

# Generate flamegraph
perf script -i boot.perf.data | \
  stackcollapse-perf.pl | \
  flamegraph.pl > boot.svg

# Profile Python analysis tool
py-spy record -o profile.svg -- python3 tools/minix_source_analyzer.py

# Deep callgrind analysis (slow)
valgrind --tool=callgrind qemu-system-i386 -cdrom minix.iso
kcachegrind callgrind.out.*

# Quick function hotspots
perf record -g ./program
perf report --stdio | head -50

# System call trace
strace -c qemu-system-i386 -cdrom minix.iso
```

### Data Processing Commands

```bash
# Parse perf.data to text
perf script -i boot.perf.data > boot-stacks.txt

# Extract hotspots (top 20 functions)
perf report --stdio -i boot.perf.data | grep -A 20 "Overhead"

# Export to JSON (custom script)
python3 tools/profiling/parse_perf_data.py boot.perf.data > boot.json

# Aggregate multiple perf files
perf buildid-list -o merged.perf.data boot-*.perf.data
```

================================================================================
## SUMMARY AND NEXT STEPS
================================================================================

### Recommended Immediate Actions

1. **Install Core Tools**
   ```bash
   sudo pacman -S perf
   yay -S flamegraph-git
   pip install --user py-spy scalene
   ```

2. **Test Basic Workflow**
   ```bash
   # Quick 10-second test
   perf record -g -F 99 -o test.perf.data -- \
     timeout 10s qemu-system-i386 -cdrom minix.iso -nographic

   perf script -i test.perf.data | \
     stackcollapse-perf.pl | \
     flamegraph.pl > test-flamegraph.svg

   # Open in browser
   firefox test-flamegraph.svg
   ```

3. **Set Up QProfiler**
   ```bash
   cd /home/eirikr/Playground
   git clone https://github.com/torokernel/qprofiler.git
   # Test with QEMU -qmp option
   ```

4. **Create PKGBUILD**
   ```bash
   mkdir -p /home/eirikr/Playground/minix-analysis/packaging
   # Copy PKGBUILD from section 7.1
   cd packaging && makepkg -si
   ```

5. **Integrate into Project**
   ```bash
   # Add to project repository
   mkdir -p tools/profiling
   # Add wrapper scripts from this guide
   chmod +x tools/profiling/*.sh
   ```

### Tool Selection Matrix

| Use Case | Recommended Tool | Installation | Overhead |
|----------|-----------------|--------------|----------|
| QEMU boot profiling | perf + flamegraph | pacman + AUR | <5% |
| Guest OS profiling | QProfiler | Manual git | ~2% |
| Python tool profiling | py-spy | pip | <1% |
| Deep analysis | valgrind/callgrind | pacman | 10-50x |
| Memory profiling | scalene | pip | 10-20% |
| Visualization | Hotspot (AppImage) | Manual | N/A |
| Batch profiling | Custom script | N/A | Depends |

### Documentation Locations

- **This Guide**: `/home/eirikr/Playground/minix-analysis/documentation/COMPREHENSIVE-CPU-PROFILING-GUIDE.md`
- **Scripts**: `/home/eirikr/Playground/minix-analysis/tools/profiling/`
- **PKGBUILD**: `/home/eirikr/Playground/minix-analysis/packaging/`
- **Profiling Output**: `/home/eirikr/Playground/minix-analysis/diagrams/profiling/`

================================================================================
END OF GUIDE
================================================================================
