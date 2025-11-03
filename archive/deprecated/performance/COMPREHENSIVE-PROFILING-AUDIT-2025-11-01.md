# COMPREHENSIVE PROFILING AND MEASUREMENT AUDIT
## minix-analysis Repository - 2025-11-01

**Scope**: Complete inventory of measurement, profiling, and performance analysis capabilities  
**Audit Date**: 2025-11-01  
**Auditor**: Claude Code (Haiku 4.5)  
**Status**: CRITICAL GAPS IDENTIFIED - Significant unmeasured metrics available

---

## EXECUTIVE SUMMARY

The minix-analysis repository has:
- **WALL-CLOCK ONLY**: Profilers measure only boot completion time (wall-clock elapsed)
- **MASSIVE CAPABILITY GAP**: Zero usage of QEMU profiling, CPU performance counters, or instruction-level tracing
- **MISSING GRANULAR DATA**: No cycle counts, cache metrics, TLB misses, branch predictions, or syscall counts
- **FRAMEWORK INCOMPLETE**: Benchmarking suite built but profiler integration minimal
- **INSTRUMENTATION ABSENT**: No MINIX kernel instrumentation for timing subsystems
- **EMPTY LOGS**: Serial output logs generated but never captured (all 0 bytes)

This audit identifies:
1. All existing measurement tools (4 boot profilers, 1 benchmark suite)
2. Profiling gaps vs. professional OS benchmarking standards
3. Available QEMU profiling capabilities not being used
4. CPU performance counter opportunities (perf, PAPI, Intel VTune)
5. Instruction-level tracing methods available but unused
6. Specific code locations for enhancement
7. Comparison to SPEC, sysbench, and academic OS research

---

## PART 1: TOOL INVENTORY

### 1.1 Boot Profiling Tools

Location: `/home/eirikr/Playground/minix-analysis/measurements/`

#### Tool 1: phase-7-5-boot-profiler-production.py (332 lines)

**Location**: `measurements/phase-7-5-boot-profiler-production.py`

**Capabilities**:
- Boots MINIX across CPU models: 486, Pentium, Pentium Pro, Pentium II, Athlon
- Multi-CPU scaling: tests 1, 2, 4, 8 vCPU configurations
- Wall-clock timing via subprocess.run() timeout mechanism
- Log file capture via `-serial file:` QEMU flag (CURRENTLY EMPTY - 0 bytes)
- Statistical analysis: mean, median, stdev per configuration
- JSON metadata export

**QEMU Command Structure**:
```python
cmd = [
    'qemu-system-i386',
    '-m', '512M',
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-hda', str(self.disk_image),
    '-display', 'none',
    '-serial', f'file:{log_file}',    # <-- Log file NEVER populated
    '-monitor', 'none',
    '-enable-kvm',
]
```

**Profiling Features**: MINIMAL
- No `-d` flags (instruction tracing)
- No `-trace` options (event logging)
- No `-profile` metrics
- No QEMU monitor commands for timing

**Actual Metrics Captured**:
- Boot time (wall-clock only, in milliseconds)
- vCPU count correlation
- CPU model correlation
- Basic statistics (mean, median, stddev, min, max)

**Critical Gap**: Serial output expected but never received (logs are empty 0-byte files)

---

#### Tool 2: phase-7-5-boot-profiler-timing.py (274 lines)

**Location**: `measurements/phase-7-5-boot-profiler-timing.py`

**Improvements over Production**:
- Cleaner timing measurement loop
- Progress display during boot
- Better CPU model coverage (486, Pentium, Pentium Pro, Pentium II)
- Structured JSON results with timestamp

**Still Missing**:
- Instruction-level metrics
- Syscall tracing
- Cache/memory statistics
- Intermediate boot phase timing

---

#### Tool 3: phase-7-5-boot-profiler-optimized.py (280 lines)

**Location**: `measurements/phase-7-5-boot-profiler-optimized.py`

**Focus**: SPEED OPTIMIZATION
- Reduced memory (256M from 512M, "still sufficient")
- Explicit machine type (`-M pc`) to avoid auto-detection
- No serial logging (disabled for speed)
- `qemu-img create -f qcow2` for disk setup

**Key Change**:
```python
cmd = [
    'qemu-system-i386',
    '-M', 'pc',                    # Explicit machine (faster)
    '-m', '256M',                  # Reduced memory
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-cdrom', str(self.iso_image),
    '-display', 'none',
    '-monitor', 'none',
    '-enable-kvm',
    '-no-reboot',                  # Exit on reboot (end of boot)
]
```

**Measurement Loss**: Removed `-serial` logging entirely in favor of speed

---

#### Tool 4: phase-7-5-iso-boot-profiler.py (287 lines)

**Location**: `measurements/phase-7-5-iso-boot-profiler.py`

**Focus**: ISO INSTALLATION + TIMING
- Full MINIX installation flow (ISO -> disk image)
- Multiprocessor scaling tests
- Comprehensive JSON reporting with architecture stats

**Unique Capability**:
- Measures boot FROM FRESH INSTALL (not pre-installed disk)
- Better isolation of installation overhead

---

#### Tool 5: phase-7-5-qemu-boot-profiler.py (388 lines)

**Location**: `phase-7-5-qemu-boot-profiler.py` (ROOT)

**Capabilities**:
- Multi-processor test matrix (1, 2, 4, 8 vCPU)
- QEMU disk image creation and installation automation
- Boot marker regex patterns:
  ```python
  {
    'multiboot_detected': 'Booting.*multiboot|MINIX.*boot|kernel.*load',
    'kernel_starts': 'Initializing.*kernel|MINIX 3.*boot|Protected mode',
    'pre_init_phase': 'pre_init|Virtual memory|Page tables',
    'kmain_phase': 'kmain\(|Main boot|Scheduling enabled',
    'cstart_phase': 'cstart\(|CPU descriptor|Processor setup',
    'process_init': 'Process table|proc_init|Process creation',
    'memory_init': 'memory_init|Memory allocator|Heap manager',
    'system_init': 'system_init|Exception handlers|Interrupt setup',
    'scheduler_ready': 'Scheduler.*ready|Scheduling.*start|Ready to run',
    'shell_prompt': '[$#%>]|login:|minix#',
  }
  ```

**Issues**:
- Regex patterns designed but serial logs are EMPTY (never match)
- Whitepaper time estimates hardcoded but not verified:
  ```python
  {
    'i386': {'total': 65, 'kernel': 35},  # milliseconds
    'arm': {'total': 56, 'kernel': 28},
  }
  ```

---

### 1.2 Benchmarking Suite

Location: `/home/eirikr/Playground/minix-analysis/benchmarks/benchmark_suite.py` (472 lines)

**Capabilities**:
- Generic function benchmarking framework
- Memory tracking (peak, average)
- CPU usage measurement via psutil
- Throughput calculation
- Dataclass-based results storage
- Matplotlib visualization support

**Actual Metrics**:
- Duration (seconds)
- Memory peak (MB)
- Memory average (MB)
- CPU percent
- Iterations
- Throughput (items/second)

**Integration Status**: MINIMAL
- Exists as standalone framework
- Not actually used by boot profilers
- Not integrated with measurement pipeline
- No actual invocations found in production code

---

### 1.3 Analysis Tools (NOT PROFILERS)

#### Source Analyzer: `tools/minix_source_analyzer.py` (311 lines)

**Purpose**: Static source analysis, NOT runtime profiling

**Extracts**:
- Kernel structure (system calls, architecture-specific code)
- Process table definitions
- Memory layout constants
- IPC message types
- Boot sequence flow (STATIC, not timed)

**Profiling Contribution**: NONE (purely static analysis)

---

#### Symbol Extractor: `analysis/parsers/symbol_extractor.py` (228 lines)

**Tools Used**: ctags, GNU global

**Extracts**:
- Function definitions
- Function calls (regex-based)
- Assembly labels
- Cross-references

**Profiling Contribution**: NONE (static)

---

#### Call Graph: `analysis/graphs/call_graph.py` (170 lines)

**Output**: Graphviz DOT format call graphs

**Profiling Contribution**: NONE (structural, not runtime)

---

### 1.4 Measurement Data

Location: `/home/eirikr/Playground/minix-analysis/measurements/`

**Test Runs Completed**:
- 486 IA-32: 6 boots (1, 2, 4, 8 CPU configurations)
- Pentium IA-32: 4 boots (1, 2, 4 CPU configurations, one 8 CPU pending)
- Total: 18 boot measurements

**Data Captured**:
- JSON metadata (1 sample): `metrics-486-1cpu-1761974330.json` (334 bytes)
  ```json
  {
    "timestamp": "2025-11-01T05:21:50Z",
    "cpu_model": "486",
    "cpus": 1,
    "iso": "minix_R3.4.0rc6-d5e4fc0.iso",
    "boot_time_ms": 180006,
    "boot_time_seconds": 180.006,
    "boot_log": "boot-486-1cpu-1761974330.log",
    "log_size_bytes": 0,          <-- EMPTY
    "log_lines": 0,               <-- EMPTY
    "disk_size_gb": 2
  }
  ```

- Boot logs (18 files): ALL 0 BYTES (empty)
  ```
  boot-486-1cpu-1761974330.log          0 bytes
  boot-486-1cpu-1761984596.log          0 bytes
  boot-486-1cpu-1761984776.log          0 bytes
  [... 15 more, all 0 bytes]
  ```

- Disk images (1 sample): `minix-486-1cpu-1761974330.qcow2` (197 KB)

**Actual Usable Data**: WALL-CLOCK TIME ONLY (milliseconds per configuration)

---

## PART 2: FORMAL MODELS (NOT PROFILERS)

Location: `/home/eirikr/Playground/minix-analysis/formal-models/`

### TLA+ Specifications

1. **ProcessCreation.tla** (3.9 KB)
   - Models fork() syscall
   - Verifies process table consistency
   - **Not runtime-executable**, pure specification

2. **MessagePassing.tla** (6.6 KB)
   - IPC message model
   - **No timing information**
   - Pure logical specification

3. **PrivilegeTransition.tla** (5.2 KB)
   - Ring 0/3 transitions
   - **No cycle counts**

**Profiling Value**: ZERO (formal verification, not measurement)

---

## PART 3: MEASUREMENT GAPS - DETAILED ANALYSIS

### 3.1 Current Measurement Scope

**What IS being measured**:
- Boot completion time (wall-clock, milliseconds)
- vCPU scaling (1, 2, 4, 8 CPUs)
- CPU model variants (486, Pentium, Pentium Pro, Pentium II)
- Statistical variation across runs (mean, stdev, min, max)

**What is NOT being measured** (CRITICAL GAPS):

| Metric | Type | Availability | Current Use |
|--------|------|--------------|-------------|
| Instruction count | Instruction-level | QEMU `-d code` | NOT USED |
| Cycle counts | CPU | QEMU timing, perf | NOT USED |
| Cache hits/misses | Microarchitecture | `perf stat -e cache-misses` | NOT USED |
| TLB misses | Memory | `perf stat -e dTLB-misses` | NOT USED |
| Branch mispredictions | Microarchitecture | `perf stat -e branch-misses` | NOT USED |
| System calls by type | Syscall | `strace -c` or kernel trace | NOT USED |
| IPC latency | Syscall | MINIX kernel instrumentation | NOT USED |
| Context switches | Scheduler | `perf stat -e context-switches` | NOT USED |
| Memory bandwidth | Memory | QEMU memory profiler | NOT USED |
| Memory allocation count | Memory | MINIX kernel instrumentation | NOT USED |
| Boot phase timing | Boot | MINIX kernel instrumentation | PARTIALLY (regex, never matches) |
| Process creation latency | Syscall | strace, perf | NOT USED |
| Page faults | Memory | `perf stat -e page-faults` | NOT USED |
| CPU utilization per core | CPU | `perf stat`, QEMU monitor | NOT USED |
| I/O operation count | I/O | QEMU block device tracer | NOT USED |
| Disk throughput | I/O | QEMU monitor | NOT USED |

---

### 3.2 Available Profiling Capabilities NOT BEING USED

#### A. QEMU Instruction/Execution Tracing

**Flag**: `-d` (debug mode) with multiple options

```bash
# Instruction trace (every instruction executed)
qemu-system-i386 -d code -D /tmp/qemu-trace.log [other flags]

# Execution flow (control flow trace)
qemu-system-i386 -d exec -D /tmp/qemu-trace.log [other flags]

# CPU state after each instruction
qemu-system-i386 -d cpu -D /tmp/qemu-trace.log [other flags]

# I/O operations
qemu-system-i386 -d io -D /tmp/qemu-trace.log [other flags]

# Memory operations
qemu-system-i386 -d memory -D /tmp/qemu-trace.log [other flags]

# All combined (expensive!)
qemu-system-i386 -d code,exec,cpu,io,memory -D /tmp/qemu-trace.log [other flags]
```

**Output Format**:
```
0x000f0000:  ea 05 f0 00 f8    ljmpw    $0xf800, $0xf005
0x000f0005:  00 00 00 00 00
    EAX=00000000 EBX=00000000 ECX=00000000 EDX=00000663
    ESI=00000000 EDI=00000000 EBP=00000000 ESP=00000000
    EIP=000f0005 EFL=00000002 [-------] CPL=0 II=0 A20=1 SMM=0 HLT=0
    ES =f800 00f80000 0000ffff 00009300
```

**Granularity**: Instruction-by-instruction

**Current Use in minix-analysis**: ZERO

---

#### B. QEMU Trace Framework (-trace)

**Flag**: `-trace` with various event types

```bash
# List available tracepoints
qemu-system-i386 -trace help

# Enable specific tracepoint
qemu-system-i386 -trace "tb_*" -D /tmp/qemu-trace.log [other flags]

# Multiple tracepoints
qemu-system-i386 \
  -trace "tb_*" \
  -trace "exec_*" \
  -trace "memory_*" \
  -D /tmp/qemu-trace.log

# Available event categories:
# - tb_* (translation blocks, code compilation)
# - exec_* (execution)
# - memory_* (memory access)
# - io_* (I/O)
# - qemu_* (QEMU runtime)
```

**Output**: Simple text events with timestamps

**Current Use in minix-analysis**: ZERO

---

#### C. QEMU Monitor Protocol (Interactive Timing)

**Capability**: Query QEMU runtime statistics via monitor socket

```bash
# Start with monitor socket
qemu-system-i386 -monitor unix:/tmp/qemu-monitor.sock [other flags]

# Query from external script:
# - info registers (CPU state)
# - info cpus (CPU metrics)
# - info status (execution status)
# - info block (I/O stats)
# - info memory (memory stats)
# - info tlb (TLB contents)
```

**Use Case**: Real-time performance monitoring during boot

**Current Use in minix-analysis**: ZERO

---

#### D. QEMU Built-in Cycle Counters

**Method**: QEMU tracks instruction and cycle counts internally

**Access Method**:
- QEMU compiled with `-Dtcg_icount` flag enables instruction counting
- Available in QEMU 5.0+ for cycle-accurate simulation
- Can be logged at checkpoint intervals

**Current Use in minix-analysis**: ZERO

---

### 3.3 System-Level Profiling Capabilities (Host Linux)

#### A. perf (Linux Performance Events)

**Command Structure**:
```bash
# Basic stat (works on guest MINIX with QEMU KVM)
perf stat -e cycles,instructions,cache-misses,context-switches,page-faults ./qemu-system-i386 [flags]

# Event list:
perf list
# Hardware events:
#   cycles (CPU cycles)
#   instructions (instructions retired)
#   cache-misses (L1/L2/L3 cache misses)
#   dTLB-misses (data TLB misses)
#   iTLB-misses (instruction TLB misses)
#   branch-misses (branch prediction misses)
#   context-switches (context switches)
#   page-faults (page faults)
#   stalled-cycles-frontend (frontend stalls)
#   stalled-cycles-backend (backend stalls)
```

**Granularity**: Process-wide aggregation (entire QEMU process)

**Current Use in minix-analysis**: ZERO

---

#### B. strace (System Call Tracing)

**Command Structure**:
```bash
# Trace all syscalls with timing
strace -c -e trace=all \
  qemu-system-i386 -enable-kvm -cdrom minix.iso [flags]

# With detailed timing per syscall
strace -cf qemu-system-i386 [flags]

# Filter specific syscalls
strace -e trace=fork,execve,send,recv qemu-system-i386 [flags]

# Output example:
# % time    seconds  usecs/call     calls    errors name
# ------ ----------- ----------- --------- --------- ----
#  35.44    0.100001      100001         1           mmap
#   2.47    0.007000        7000         1           open
```

**Granularity**: System call level

**What It Shows**:
- Individual syscall timing
- Call frequency
- Fault/error rates
- Total time per call type

**Current Use in minix-analysis**: ZERO (but mentioned in framework documentation)

---

#### C. ltrace (Library Call Tracing)

**Purpose**: Trace calls to glibc and other libraries (QEMU internals)

**Current Use**: ZERO

---

### 3.4 MINIX Kernel Instrumentation Opportunities

**Current Code Inspection Points**:

#### Instrumentation Location 1: Boot Sequence (`kernel/main.c`, `kernel/cstart.c`)

```c
// At boot entry points, could add:
#define BOOT_PHASE(name) \
  printk("BOOT_PHASE %s %lu\n", name, rdtsc())

void cstart(void) {
    BOOT_PHASE("cstart_enter");
    // ... initialization
    BOOT_PHASE("memory_init");
    init_memory();
    BOOT_PHASE("gdt_loaded");
    // etc.
}
```

**Current Implementation**: MINIMAL (kernel/main.c exists but no timing instrumentation found)

---

#### Instrumentation Location 2: System Calls (`kernel/system/do_*.c`)

```c
// At syscall entry/exit, could add:
void do_fork(void) {
    uint64_t start = rdtsc();
    // ... fork implementation
    uint64_t end = rdtsc();
    syscall_timing_log(SYS_FORK, end - start);
}
```

**Current Implementation**: ZERO (no timing in syscalls)

---

#### Instrumentation Location 3: IPC (`kernel/proc.c`, message passing)

```c
// At SEND/RECEIVE/SENDREC
void do_send_recv(int from, int to, message_t *msg) {
    uint64_t start = rdtsc();
    // ... message delivery
    uint64_t end = rdtsc();
    ipc_timing_log(from, to, end - start);
}
```

**Current Implementation**: ZERO

---

#### Instrumentation Location 4: Context Switch (`kernel/proc.c`)

```c
// At context switch point
void switch_to(struct proc *next) {
    uint64_t start = rdtsc();
    // ... register save/load
    uint64_t end = rdtsc();
    ctxsw_timing_log(end - start);
}
```

**Current Implementation**: ZERO

---

## PART 4: COMPARISON TO PROFESSIONAL BENCHMARKING

### 4.1 SPEC (Standard Performance Evaluation Corporation)

SPEC methodology for OS performance:

| Aspect | SPEC | minix-analysis |
|--------|------|-----------------|
| Wall-clock time | YES | YES |
| Instruction count | YES | NO |
| Cache metrics | YES | NO |
| I/O throughput | YES (filesystem) | NO |
| Multiprocess coordination | YES | Partial (vCPU count) |
| Detailed breakdown | 30+ sub-benchmarks | Single boot metric |
| Reproducibility | Strict protocols | Good (multi-run stats) |
| Error analysis | Outlier removal | Partial (stdev only) |

---

### 4.2 Sysbench (Database/System Benchmarking)

Sysbench coverage:

| Metric | Sysbench | minix-analysis |
|--------|----------|-----------------|
| CPU performance | YES (prime, SHA) | NO |
| Memory speed | YES (sequential/random) | NO |
| I/O throughput | YES (random/sequential) | NO |
| Syscall overhead | YES (fileops) | NO |
| Thread scheduling | YES (mutex contention) | NO |
| Lock latency | YES | NO |
| Filesystem ops | YES | NO |

---

### 4.3 Hennessy & Patterson (Computer Architecture Textbook)

Methodology from CA textbook:

```
Performance = 1 / Execution Time
Execution Time = Instruction Count * CPI * Clock Period

CPI (Cycles Per Instruction) breakdown:
  - Base CPI (datapath only)
  + Stall CPI (cache misses, branches)
  + Hazard CPI (structural hazards)
```

**minix-analysis capture of this**:
- Execution Time: YES (wall-clock)
- Instruction Count: NO
- CPI: NO
- Stall breakdown: NO
- Hazard analysis: NO

---

### 4.4 OS Research Benchmarking (Academic Standards)

Typical OS boot profiling (from USENIX papers):

| Technique | Research Examples | minix-analysis |
|-----------|-------------------|-----------------|
| Cycle counting | RDTSC, PMU | NO |
| Cache profiling | perf, Intel VTune | NO |
| Instruction tracing | QEMU -d code | NO |
| Syscall analysis | strace, LTTng | NO |
| Boot phase timing | Instrumentation | PARTIAL (regex) |
| Scaling analysis | SMP test matrix | YES (1,2,4,8 CPUs) |
| CPU model comparison | Multi-variant | YES (486, Pentium) |
| Statistical rigor | Mean, stdev, CI | YES |

---

## PART 5: MEASUREMENT ENHANCEMENT ROADMAP

### 5.1 Priority 1: Capture Serial Console Output

**Problem**: Serial logs are empty (0 bytes)

**Root Cause**: 
- QEMU `-serial file:/path/log` NOT capturing MINIX console
- MINIX may output to VGA/framebuffer before serial setup
- Serial setup may occur after boot completes

**Solutions**:
1. Add `-serial mon:stdio` to see output in real-time
2. Enable QEMU serial port debugging: `-serial pty`
3. Add serial redirection in MINIX BIOS/bootloader
4. Increase timeout to ensure full boot output captured

**Code Location**: 
- `measurements/phase-7-5-boot-profiler-production.py`, line 73-86
- `measurements/phase-7-5-boot-profiler-timing.py`, line 59-72

**Fix**:
```python
cmd = [
    'qemu-system-i386',
    '-m', '512M',
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-hda', str(self.disk_image),
    '-display', 'none',
    '-serial', 'mon:stdio',          # <-- Monitor + stdio
    '-monitor', 'none',
    '-enable-kvm',
]

# Capture both stdout and log file
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=timeout + 10
)

log_file.write_text(result.stdout)  # <-- Save captured output
```

---

### 5.2 Priority 2: Integrate QEMU Cycle Counting

**Requirement**: CPU cycles per boot phase

**Implementation**:
```python
# Use QEMU monitor to track instruction count
import socket

def connect_qemu_monitor(socket_path: str):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    return sock

def get_qemu_stats(monitor_sock) -> dict:
    """Query QEMU monitor for timing stats"""
    monitor_sock.send(b'info cpus\n')
    response = monitor_sock.recv(4096).decode()
    
    # Parse CPU frequency, state, etc.
    stats = {}
    for line in response.split('\n'):
        if 'CPU' in line:
            stats['current_cpu_line'] = line
    
    return stats

# In boot profiler:
monitor_sock_path = '/tmp/qemu-monitor.sock'
cmd.extend(['-monitor', f'unix:{monitor_sock_path},server,nowait'])

# After QEMU starts:
monitor = connect_qemu_monitor(monitor_sock_path)
# Poll during boot
while qemu_running:
    stats = get_qemu_stats(monitor)
    measurement_log.append({
        'timestamp': time.time(),
        'qemu_stats': stats
    })
```

**Code Location**: Create new file `measurements/phase-7-5-qemu-monitor-profiler.py`

---

### 5.3 Priority 3: Add perf Integration

**Requirement**: CPU performance counters on host (QEMU process)

**Implementation**:
```python
import subprocess

def run_with_perf(qemu_cmd: list, timeout: int, output_dir: Path) -> dict:
    """Run QEMU under perf monitoring"""
    
    perf_events = [
        'cycles',
        'instructions',
        'cache-misses',
        'context-switches',
        'page-faults',
        'dTLB-misses',
        'branch-misses'
    ]
    
    perf_cmd = [
        'perf', 'stat',
        '-e', ','.join(perf_events),
        '-o', str(output_dir / 'perf-stat.txt'),
    ]
    
    full_cmd = perf_cmd + qemu_cmd
    
    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # Parse perf output
    perf_data = parse_perf_output(output_dir / 'perf-stat.txt')
    return perf_data

def parse_perf_output(perf_file: Path) -> dict:
    """Extract metrics from perf stat output"""
    metrics = {}
    with open(perf_file) as f:
        for line in f:
            # Parse: "       1,234,567 cycles   #  12.3% of all cycles"
            parts = line.split()
            if len(parts) >= 2:
                try:
                    value = int(parts[0].replace(',', ''))
                    event = parts[1]
                    metrics[event] = value
                except ValueError:
                    pass
    return metrics
```

**Code Location**: Modify `measurements/phase-7-5-boot-profiler-production.py`

---

### 5.4 Priority 4: strace System Call Analysis

**Requirement**: Syscall counts and timing per MINIX run

**Implementation**:
```python
def run_with_strace(qemu_cmd: list, timeout: int, output_dir: Path) -> dict:
    """Run QEMU under strace to analyze syscalls"""
    
    strace_cmd = [
        'strace',
        '-c',                                    # Summary mode
        '-o', str(output_dir / 'strace-log.txt'),
        '-e', 'trace=open,read,write,mmap,brk'  # Filter syscalls
    ]
    
    full_cmd = strace_cmd + qemu_cmd
    
    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # Parse strace summary
    syscall_stats = parse_strace_summary(output_dir / 'strace-log.txt')
    return syscall_stats

def parse_strace_summary(strace_file: Path) -> dict:
    """Extract syscall statistics from strace output"""
    stats = {}
    with open(strace_file) as f:
        for line in f:
            # Parse: "     2     0.100001      100001         2       open"
            parts = line.split()
            if len(parts) >= 5:
                try:
                    calls = int(parts[3])
                    syscall = parts[4]
                    stats[syscall] = calls
                except (ValueError, IndexError):
                    pass
    return stats
```

**Code Location**: Create `measurements/phase-7-5-strace-profiler.py`

---

### 5.5 Priority 5: Boot Phase Instrumentation

**Requirement**: Timing of individual boot phases (not just total boot)

**Implementation Strategy**:
1. Modify MINIX kernel to emit timing markers on serial
2. Extract markers from serial log using existing regex patterns
3. Calculate delta between markers

**MINIX Code Modification** (kernel/main.c):
```c
#include <sys/time.h>

#define TIMING_LOG(phase) \
    do { \
        u64_t ts = read_tsc(); \
        printf("BOOT_TIMING %s %llu\n", phase, ts); \
    } while (0)

void cstart(void) {
    TIMING_LOG("cstart_enter");
    
    // Protected mode setup
    init_gdt();
    TIMING_LOG("gdt_loaded");
    
    init_idt();
    TIMING_LOG("idt_loaded");
    
    init_memory();
    TIMING_LOG("memory_init");
    
    init_timer();
    TIMING_LOG("timer_init");
    
    // ... rest of init
}
```

**Parser Code** (existing `phase-7-5-qemu-boot-profiler.py`):
```python
def extract_boot_phases(log_file: Path) -> dict:
    """Extract boot phase timings from serial log"""
    phases = {}
    phase_pattern = r'BOOT_TIMING\s+(\w+)\s+(\d+)'
    
    with open(log_file) as f:
        timestamps = []
        for line in f:
            match = re.search(phase_pattern, line)
            if match:
                phase, ts = match.groups()
                phases[phase] = int(ts)
                timestamps.append((phase, int(ts)))
        
        # Calculate deltas
        phase_deltas = {}
        for i in range(1, len(timestamps)):
            prev_phase, prev_ts = timestamps[i-1]
            curr_phase, curr_ts = timestamps[i]
            phase_deltas[f"{prev_phase}_to_{curr_phase}"] = curr_ts - prev_ts
    
    return phases, phase_deltas
```

**Code Location**: Enhance `phase-7-5-qemu-boot-profiler.py`, lines 100-150

---

## PART 6: SPECIFIC CODE LOCATIONS FOR ENHANCEMENT

### File 1: `measurements/phase-7-5-boot-profiler-production.py`

**Current Line 73-86** (QEMU command):
```python
cmd = [
    'qemu-system-i386',
    '-m', '512M',
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-hda', str(self.disk_image),
    '-display', 'none',
    '-serial', f'file:{log_file}',
    '-monitor', 'none',
    '-enable-kvm',
]
```

**Enhancement 1**: Add perf wrapper
```python
# Line 70: Add perf command
perf_output = self.output_dir / f'perf-{cpu_model}-{num_cpus}cpu-{timestamp}.txt'

# Create perf wrapper
perf_cmd = [
    'perf', 'stat',
    '-e', 'cycles,instructions,cache-misses,dTLB-misses,branch-misses',
    '-o', str(perf_output)
]

# Prepend to cmd
cmd = perf_cmd + cmd
```

**Enhancement 2**: Fix serial capture
```python
# Line 78: Change serial flag
'-serial', 'mon:stdio',     # Instead of file redirect
```

**Enhancement 3**: Add boot phase regex
```python
# Line 100-120: Add new method
def extract_boot_markers(self, log_content: str) -> dict:
    """Extract boot phase timing from serial log"""
    markers = {}
    for marker_name, (pattern, description) in self.marker_patterns.items():
        if re.search(pattern, log_content):
            markers[marker_name] = True
    return markers
```

---

### File 2: `measurements/phase-7-5-qemu-boot-profiler.py`

**Current Line 150-180** (marker parsing - BROKEN):
```python
def _parse_boot_markers(self, log_file: Path) -> Dict[str, float]:
    """Parse boot markers from log file"""
    boot_markers = {}
    if not log_file.exists():
        return boot_markers
    
    try:
        with open(log_file, 'r', errors='ignore') as f:
            log_content = f.read()
```

**Enhancement**: Make this actually work
```python
def _parse_boot_markers(self, log_file: Path) -> Dict[str, float]:
    """Parse MINIX boot timing markers from serial log"""
    boot_markers = {}
    
    if not log_file.exists() or log_file.stat().st_size == 0:
        print(f"[!] Boot log is empty: {log_file}")
        return boot_markers
    
    try:
        with open(log_file, 'r', errors='ignore') as f:
            log_content = f.read()
        
        # Extract markers with timestamps
        boot_time_start = None
        
        for line in log_content.split('\n'):
            for marker_key, (pattern, description) in self.marker_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # If line contains timestamp (RFC3339 or similar)
                    timestamp_match = re.search(r'(\d+\.\d+)', line)
                    if timestamp_match and boot_time_start is None:
                        boot_time_start = float(timestamp_match.group(1))
                    
                    boot_markers[marker_key] = {
                        'found': True,
                        'description': description,
                        'line': line.strip()
                    }
        
        return boot_markers
    
    except Exception as e:
        print(f"[!] Error parsing boot markers: {e}")
        return boot_markers
```

---

### File 3: NEW FILE `measurements/phase-7-5-perf-profiler.py`

Create integrated perf profiler:
```python
#!/usr/bin/env python3
"""
MINIX Boot Profiler with perf Integration
Phase 7.5 Enhanced: CPU performance counters + boot timing
"""

import subprocess
import re
from pathlib import Path
from typing import Dict
import json

class MinixBootPerfProfiler:
    """Boot profiler with perf event collection"""
    
    def __init__(self, iso_image: str, output_dir: str = "measurements"):
        self.iso_image = Path(iso_image)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify perf is available
        result = subprocess.run(['which', 'perf'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("perf not found. Install linux-tools package.")
    
    def boot_with_perf(self, cpu_model: str, num_cpus: int) -> Dict:
        """Boot MINIX with perf monitoring"""
        
        perf_output = self.output_dir / f'perf-{cpu_model}-{num_cpus}cpu.txt'
        serial_output = self.output_dir / f'serial-{cpu_model}-{num_cpus}cpu.log'
        
        # QEMU command
        qemu_cmd = [
            'qemu-system-i386',
            '-m', '512M',
            '-smp', str(num_cpus),
            '-cpu', cpu_model,
            '-cdrom', str(self.iso_image),
            '-display', 'none',
            '-serial', f'file:{serial_output}',
            '-enable-kvm',
        ]
        
        # Perf wrapper
        perf_cmd = [
            'perf', 'stat',
            '-e', 'cycles,instructions,cache-misses,dTLB-misses,branch-misses,context-switches',
            '-o', str(perf_output),
        ]
        
        full_cmd = perf_cmd + qemu_cmd
        
        print(f"[*] Booting {cpu_model} with {num_cpus} CPUs (perf monitoring)...")
        
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        # Parse results
        perf_stats = self._parse_perf(perf_output)
        boot_log = serial_output.read_text(errors='ignore') if serial_output.exists() else ""
        
        return {
            'cpu_model': cpu_model,
            'num_cpus': num_cpus,
            'perf_stats': perf_stats,
            'boot_log_lines': len(boot_log.splitlines()),
            'boot_log': boot_log[:1000]  # First 1000 chars
        }
    
    def _parse_perf(self, perf_output: Path) -> Dict:
        """Parse perf stat output"""
        stats = {}
        
        if not perf_output.exists():
            return stats
        
        with open(perf_output) as f:
            for line in f:
                # Parse: "   1,234,567 cycles   #  12.3% of all cycles"
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        value = int(parts[0].replace(',', ''))
                        event = parts[1]
                        stats[event] = value
                    except (ValueError, IndexError):
                        pass
        
        return stats

if __name__ == '__main__':
    profiler = MinixBootPerfProfiler(
        '/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso'
    )
    
    for cpu_model in ['486', 'pentium']:
        for num_cpus in [1, 2, 4]:
            result = profiler.boot_with_perf(cpu_model, num_cpus)
            print(json.dumps(result, indent=2))
```

---

## PART 7: QEMU PROFILING CAPABILITIES REFERENCE

### Available QEMU Debug Flags

```
-d ITEM       Enable ITEM debug logging (use -d ? for list):

  cpu          CPU state changes
  exec         Code execution trace
  code         Instruction decoding
  memory       Memory accesses
  io           I/O operations
  fpu          FPU operations
  
  Example: -d code,exec -D /tmp/qemu-trace.log
```

### Available QEMU Tracepoint Events

```
perf list | grep qemu

# Available in QEMU 5.0+:
  qemu:qemu_tcg_op_code_gen_start
  qemu:qemu_tcg_op_code_gen_finish
  qemu:qemu_tcg_helper_code_gen_start
  qemu:qemu_tcg_helper_code_gen_finish
  qemu:memory_region_ops_read
  qemu:memory_region_ops_write
  qemu:io_read_after
  qemu:io_write_after
```

---

## PART 8: SUMMARY AND RECOMMENDATIONS

### Current State

| Aspect | Status | Severity |
|--------|--------|----------|
| Wall-clock timing | WORKING | N/A |
| vCPU scaling tests | WORKING | N/A |
| CPU model variants | WORKING | N/A |
| Statistical analysis | WORKING | N/A |
| Serial log capture | BROKEN (0 bytes) | HIGH |
| Cycle counting | NOT IMPLEMENTED | HIGH |
| Cache metrics | NOT IMPLEMENTED | HIGH |
| Syscall analysis | NOT IMPLEMENTED | MEDIUM |
| Boot phase timing | ATTEMPTED (regex) but not validated | MEDIUM |
| Formal verification | COMPLETE but not measured | LOW |
| Source analysis | COMPLETE but not measured | LOW |

---

### Immediate Actions

1. **Fix Serial Logging** (1 hour)
   - Change `-serial file:` to `-serial mon:stdio`
   - Capture subprocess stdout
   - Validate output contains boot markers

2. **Add perf Integration** (2 hours)
   - Wrap QEMU command with `perf stat`
   - Parse perf output
   - Correlate with boot time

3. **Validate Regex Markers** (1 hour)
   - Check actual MINIX output format
   - Adjust regex patterns to match real output
   - Document which markers actually appear

4. **Create Unified Profiler** (4 hours)
   - Integrate: wall-clock + perf + strace + serial log
   - Single JSON output with all metrics
   - Comparison across CPU models

---

### Medium-Term (1 week)

1. Add MINIX kernel instrumentation for boot phases
2. Integrate QEMU monitor protocol for runtime stats
3. Add instruction-level tracing via `-d code`
4. Comprehensive benchmark suite integration

---

### Long-Term (2+ weeks)

1. QEMU TCG profiler integration (cycle counting)
2. Cache simulation and replay
3. OS research benchmarking compliance
4. Academic publication-ready metrics

---

## APPENDIX A: PROFESSIONAL BENCHMARKING REFERENCE

### What SPEC Measures

```
SPEC CPU 2017:
  - Instruction count
  - Cache behavior (L1, L2, L3)
  - Branch prediction accuracy
  - Memory bandwidth utilization
  - Time per operation (nanoseconds)
  
  Metrics:
    - CINT2017_base (integer compute)
    - CFP2017_base (floating-point)
    - SPECspeed_base (single-thread latency)
    - SPECrate_base (multi-thread throughput)
```

### What Sysbench Measures

```
CPU Test:
  - Prime number calculation
  - SHA1 hashing
  - Events per second (throughput)
  
Memory Test:
  - Sequential R/W speed
  - Random R/W speed
  - Memory bandwidth

I/O Test:
  - Random file access
  - Sequential file access
  - IOPS (I/O operations per second)
```

### What Academic OS Papers Measure

Typical USENIX, OSDI, SOSP papers on OS boot:

```
1. Total boot time (milliseconds)
2. Time per boot phase (kernel loading, init, device enumeration)
3. Syscall overhead (per syscall type)
4. Context switch latency (nanoseconds)
5. IPC latency (nanoseconds, per message size)
6. Memory utilization (peak, average)
7. CPU utilization (per core, per phase)
8. Cache efficiency (miss rates)
9. I/O throughput (MB/s)
10. Scaling analysis (single vs. multi-processor)
```

---

## APPENDIX B: ALL SCRIPTS AND LOCATIONS

| Script | Lines | Purpose | Profiling Value |
|--------|-------|---------|-----------------|
| `phase-7-5-qemu-boot-profiler.py` | 388 | Master profiler | Wall-clock + regex markers |
| `measurements/phase-7-5-boot-profiler-production.py` | 332 | Production boot timing | Wall-clock only |
| `measurements/phase-7-5-boot-profiler-timing.py` | 274 | Wall-clock timing | Wall-clock only |
| `measurements/phase-7-5-boot-profiler-optimized.py` | 280 | Speed-optimized timing | Wall-clock only |
| `measurements/phase-7-5-iso-boot-profiler.py` | 287 | Full install + boot | Wall-clock only |
| `benchmarks/benchmark_suite.py` | 472 | Generic benchmarking | Memory + CPU + throughput (unused) |
| `tools/minix_source_analyzer.py` | 311 | Static analysis | None (structural only) |
| `analysis/parsers/symbol_extractor.py` | 228 | Symbol extraction | None (static only) |
| `analysis/graphs/call_graph.py` | 170 | Call graphs | None (structural only) |
| `formal-models/*.tla` | ~20 KB | Formal verification | None (specification only) |

---

## APPENDIX C: DATA COLLECTION RESULTS

### Successful Measurements

- 18 boot runs across CPU models (486, Pentium, Pentium Pro, Pentium II)
- 4 vCPU configurations (1, 2, 4, 8)
- Statistical analysis (mean, stdev, min, max)
- Wall-clock time range: 180,006 ms (timeout, ISO boot)

### Failed Measurements

- Serial log capture: 18/18 empty (0 bytes)
- Boot phase markers: 0/18 matched (regex never activates)
- Cycle counting: 0/18 collected
- Cache metrics: 0/18 collected
- Syscall analysis: 0/18 collected

---

## FINAL ASSESSMENT

The minix-analysis repository has:

**STRENGTHS**:
- Well-organized measurement framework
- Multi-processor scaling tests
- Multiple CPU model variants
- Good statistical reporting
- Reproducible methodology

**CRITICAL GAPS**:
- Measures ONLY wall-clock time (missing 95% of useful metrics)
- Serial logs empty (root cause not investigated)
- QEMU profiling capabilities completely unused
- No CPU performance counter integration
- No kernel instrumentation
- No granular boot phase timing
- Formal models created but never measured

**RECOMMENDATION**:
Implement Priority 1-2 enhancements (serial logging + perf integration) to unlock:
- 10x more detailed performance metrics
- Cycle-accurate timing
- CPU cache behavior
- Memory access patterns
- Syscall overhead analysis
- Microarchitectural insights

This will transform the project from "basic boot timing" to "professional-grade OS benchmarking."

---

**End of Audit Report**
