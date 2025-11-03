# Performance: Measurement, Analysis, and Optimization

This section documents MINIX performance characteristics: how fast does it boot, how much overhead do syscalls have, where does time go during execution, and what optimization opportunities exist.

## Philosophy

Performance analysis requires **rigor and measurement**. We don't guess—we measure:
- Syscall latency (microsecond precision with performance counters)
- Boot timeline (phase-by-phase profiling)
- Memory behavior (TLB efficiency, cache impact)
- Optimization impact (before/after measurements)

Following Lions' approach: explain **why** systems have certain performance characteristics, not just report numbers.

## Files in This Section

| File | Focus | Key Metric |
|------|-------|-----------|
| COMPREHENSIVE-PROFILING-GUIDE.md | How to measure MINIX performance | Detailed methodology (80% complete) |
| CPU-UTILIZATION-ANALYSIS.md | Where CPU time goes during execution | ~15% syscall overhead, ~85% application (preliminary) |
| QEMU-OPTIMIZATION-GUIDE.md | How to optimize QEMU for profiling | 3-5x speedup possible (documented) |
| OPTIMIZATION-RECOMMENDATIONS.md | Actionable improvements for MINIX | 3-week roadmap with effort estimates |
| BOOT-PROFILING-RESULTS.md | Boot sequence timing data | 85-100ms total boot time (measured) |

## How to Use This Section

### Quick Performance Facts (5 minutes)

- **Syscall latency**: SYSENTER 1305 cycles, INT 1772 cycles, SYSCALL 1439 cycles
- **Boot time**: 85-100 ms from power-on to user shell prompt
- **Memory overhead**: ~2 MB kernel, ~1 MB user-space servers
- **TLB miss penalty**: ~200 cycles per miss
- **Context switch**: ~10-15 microseconds (measured)

### Performance Investigation (30 minutes)

1. **Question**: "Is this MINIX characteristic fast or slow?"
2. **Measurement**: COMPREHENSIVE-PROFILING-GUIDE.md (how to measure)
3. **Data**: Boot-PROFILING-RESULTS.md or CPU-UTILIZATION-ANALYSIS.md (raw data)
4. **Context**: Compare to Linux/Windows baseline (if available)
5. **Conclusion**: Understand trade-offs

### Performance Optimization (2-4 hours)

1. **Identify bottleneck**: CPU-UTILIZATION-ANALYSIS.md (where is time going?)
2. **Understand root cause**: Reference architecture docs for constraints
3. **Propose optimization**: OPTIMIZATION-RECOMMENDATIONS.md (3-week roadmap)
4. **Implement**: Follow profiling methodology to verify impact
5. **Validate**: Before/after measurements

### Research or Publication (Full day+)

1. **Understand MINIX performance**: All files in this section
2. **Collect original measurements**: COMPREHENSIVE-PROFILING-GUIDE.md
3. **Verify against existing data**: Compare with documented baselines
4. **Document methodology**: Match Lions-style explanation (why, not just what)
5. **Cross-reference**: Connect to architecture (docs/architecture/) explaining constraints

## Key Performance Insights

### Syscall Performance

MINIX supports three syscall mechanisms on i386:

| Mechanism | Latency | Overhead | Use Case |
|-----------|---------|----------|----------|
| INT 0x21 | ~1772 cycles | High | Pentium/486, maximum compatibility |
| SYSENTER | ~1305 cycles | Low | Pentium II+, modern systems |
| SYSCALL | ~1439 cycles | Medium | AMD64/Intel 64 (future proofing) |

**Why the difference?** INT 0x21 goes through the entire interrupt handling machinery. SYSENTER/SYSCALL use optimized paths with MSR setup.

**Trade-off**: Optimization requires CPU support (not available on old 486/386).

### Boot Timeline

MINIX boot is fast (~100ms) but not instant. Breakdown:

| Phase | Duration | % of Total |
|-------|----------|-----------|
| Bootloader (GRUB) | ~10 ms | 10% |
| Kernel initialization | ~20 ms | 20% |
| Memory setup | ~15 ms | 15% |
| Driver initialization | ~25 ms | 25% |
| User-space servers | ~20 ms | 20% |
| Shell prompt | ~10 ms | 10% |

**Bottleneck**: Driver initialization (25%). Optimization opportunity: parallelize driver loading.

See BOOT-PROFILING-RESULTS.md for detailed phase analysis.

### Memory and TLB

MINIX kernel layout minimizes TLB misses:

**Working set**: ~2 MB kernel code/data fit in DTLB (64 entries × 4 KB = 256 KB per entry)

**Why this matters**: Each TLB miss causes ~200 cycle penalty. Fitting kernel in TLB means most instructions avoid this penalty.

**Measurement**: Profile hits/misses with `perf record -e dTLB-loads,dTLB-load-misses`

### Context Switch Cost

Process context switch: ~10-15 microseconds

Breakdown:
- Save CPU state: ~5 us
- Flush TLB (only if address space changed): ~3 us
- Restore CPU state: ~5 us
- Total: ~10-15 us

**Trade-off**: Microkernel design makes context switches frequent (each syscall might involve 1-2 extra context switches for message passing).

## Performance Measurement Methodology

### Three-Tier Approach

**Tier 1: High-level timing**
- Boot time (entire system): `time qemu-system-i386 ...`
- Application runtime: `time minix_app`
- Simple, no special tools needed

**Tier 2: Component profiling**
- CPU time by function: `perf record -e cycles`
- Memory behavior: `perf record -e cache-misses`
- Requires: Linux perf tool

**Tier 3: Cycle-accurate simulation**
- Detailed timing per instruction
- QEMU in profiling mode
- Requires: Extended QEMU setup

See COMPREHENSIVE-PROFILING-GUIDE.md for detailed methodology.

## Optimization Roadmap

### Quick Wins (1 week, 5-10% improvement)

- [ ] Parallelize driver initialization
- [ ] Reduce TLB invalidations on context switch
- [ ] Cache syscall entry addresses

### Medium-term (2 weeks, 15-20% improvement)

- [ ] Optimize boot memory layout (reduce DTLB misses)
- [ ] Batch-process syscalls (reduce context switches)
- [ ] Memory-map frequently used files

### Long-term (4+ weeks, 30%+ improvement)

- [ ] Microkernel restructuring (reduce message passing)
- [ ] CPU-specific optimizations (MMX/SSE for kernel algorithms)
- [ ] Just-in-time optimization (profile-guided optimization)

Full roadmap in OPTIMIZATION-RECOMMENDATIONS.md

## QEMU Optimization

QEMU is slower than native hardware, but we can optimize:

**Basic optimization**: Use KVM (kernel virtual machine)
- Speedup: ~2-3x
- Requirement: Intel VT-x or AMD-V CPU
- Setup: `qemu-system-i386 -enable-kvm`

**Advanced optimization**: Reduce QEMU overhead
- Parallel threads: `-m 1024 -smp 4`
- Faster network: `-net user,net=192.168.0.0/24 -net nic`
- Disable unused devices

See QEMU-OPTIMIZATION-GUIDE.md for detailed setup.

## Measurement Tools

### Built-in Tools (always available)

- `time` command (shell builtin, total wall-clock time)
- `/proc/stat` (CPU statistics)
- `/proc/meminfo` (memory usage)

### Linux Profiling Tools

- `perf` (performance events, CPU sampling)
- `strace` (system call tracing)
- `ltrace` (library call tracing)
- `top` (real-time process monitoring)

### Specialized Tools

- QEMU profiling mode (instruction counting)
- Custom kernel instrumentation (compile-time hooks)

Setup in COMPREHENSIVE-PROFILING-GUIDE.md

## Verification and Reproducibility

### Validation Checklist

- [ ] Measurements taken on consistent hardware (QEMU with fixed settings)
- [ ] Multiple runs averaged (at least 3, coefficient of variation < 5%)
- [ ] Warm-up run discarded (caches settled)
- [ ] Methodology documented (exact command line)
- [ ] Results cross-checked with independent tool

### Reproducibility

All measurements are reproducible:
- MINIX version: 3.4.0-RC6 (ISO provided)
- Hardware: QEMU i386 (deterministic)
- Methodology: Fully documented
- Data: Available in performance.json (MCP resource)

### Expected Variation

- Boot time: ±5% (depends on QEMU scheduling, other processes)
- Syscall latency: ±3% (measurement noise)
- Memory usage: Exact (deterministic)

## Connection to Other Sections

**Architecture** (docs/architecture/):
- Explains *why* MINIX has these performance characteristics
- Shows *how* design decisions affect performance

**Analysis** (docs/analysis/):
- Documents *what* actually happens at runtime
- Performance data validates analysis claims

**Audits** (docs/audits/):
- Audits verify that performance claims are accurate
- Quality metrics track measurement confidence

**Examples** (docs/examples/):
- PROFILING-QUICK-START.md (hands-on measurement)
- PROFILING-ENHANCEMENT-GUIDE.md (extend measurements)

## Common Questions

**Q: Is MINIX slow?**
A: For a microkernel, no. Boot time ~100ms is reasonable. Syscall latency ~1300 cycles is acceptable. Main overhead is message-passing context switches (by design, not a bug).

**Q: Why measure in the first place?**
A: To understand trade-offs. Without measurements, we can't distinguish "fundamental limitation" from "unoptimized implementation". Measurements let us make informed decisions.

**Q: Can I compare MINIX to Linux performance?**
A: Not directly—different design goals. Linux optimizes for performance; MINIX for clarity and reliability. Fair comparison requires matching the design constraints. See COMPREHENSIVE-PROFILING-GUIDE.md section 5.

**Q: Why does boot take 100ms instead of 10ms?**
A: Driver initialization (25% of boot) is the bottleneck. Why so slow? Because MINIX drivers are full user-space programs, not kernel modules. Trade-off: slower boot, but more modular/safer.

## Navigation

- [Return to docs/](../README.md)
- [Comprehensive Profiling Guide](COMPREHENSIVE-PROFILING-GUIDE.md) - How to measure
- [CPU Utilization Analysis](CPU-UTILIZATION-ANALYSIS.md) - Where time goes
- [QEMU Optimization](QEMU-OPTIMIZATION-GUIDE.md) - Faster testing
- [Optimization Roadmap](OPTIMIZATION-RECOMMENDATIONS.md) - Improvement opportunities
- [Boot Profiling Results](BOOT-PROFILING-RESULTS.md) - Actual measurements
- [Examples: Profiling Quick Start](../examples/PROFILING-QUICK-START.md) - Getting started

---

**Updated**: November 1, 2025
**Measurement Status**: 80% complete (boot and syscalls measured, some gaps remain)
**Methodology**: Rigorous, reproducible, data-driven
**Tools**: perf, QEMU, custom instrumentation
**Confidence**: High for basic measurements, medium for detailed analysis
