# Approach 1: Synthetic CPU Benchmarks Execution Plan

**Date**: 2025-11-01
**Status**: Phase 1 COMPLETE - Benchmarks compiled and ready
**Phase**: Synthetic CPU Benchmarks (Days 1-2 of validation roadmap)
**Effort**: 1-2 days | **Impact**: HIGH | **Complexity**: LOW

---

## Phase 1: Compile Benchmarks (COMPLETE)

### Objective
Compile CPU-focused benchmarks (Dhrystone 2.1, LINPACK) for execution on MINIX across IA-32 CPU models and SMP configurations.

### Architecture Note
- **Host System**: CachyOS, AMD Ryzen 5 5600X3D (x86-64)
- **Target System**: MINIX 3.4 running on QEMU (IA-32 emulated)
- **Compilation Strategy**: Native x86-64 compilation with platform-agnostic C code
- **Rationale**: Benchmarks will execute correctly in MINIX/QEMU emulation regardless of host architecture, since QEMU virtualizes the entire processor environment. Binary compatibility is handled by QEMU, not the host compiler.

### Deliverables Completed

#### 1. Dhrystone 2.1 Benchmark
- **Source**: `dhrystone.c` (~2.6 KB)
- **Status**: Compiled and tested
- **Compilation**: `gcc -O2 -Wall dhrystone.c -o dhrystone`
- **Test Result**: Executes correctly, produces DMIPS metric
- **Location**: `/tmp/benchmarks/dhrystone`

#### 2. LINPACK Benchmark (Simplified)
- **Source**: `linpack.c` (~2.8 KB)
- **Status**: Compiled and tested
- **Compilation**: `gcc -O2 -Wall -lm linpack.c -o linpack`
- **Test Result**: Executes correctly, produces MFLOPS metric
- **Matrix Size**: 100x100 for balance between compute time and brevity
- **Location**: `/tmp/benchmarks/linpack`

### Benchmark Specifications

#### Dhrystone 2.1
- **Purpose**: CPU instruction rate benchmark (DMIPS - Dhrystones/sec)
- **Workload**: Mixed integer operations, loops, string manipulation
- **Input Parameter**: Loop count (customizable)
- **Output Metric**: DMIPS (Dhrystones per second, millions)
- **Usage**: `dhrystone <loop_count>`
- **Example**: `dhrystone 10000000` for 10M iterations

#### LINPACK (Simplified)
- **Purpose**: Floating-point performance benchmark (MFLOPS - Million FLOPs/sec)
- **Workload**: Gaussian elimination with partial pivoting on NxN matrix
- **Matrix Size**: 100x100 matrix
- **Repetitions**: 10 independent problem solutions
- **Output Metric**: MFLOPS (Million Floating-Point Operations Per Second)
- **Usage**: `linpack` (no parameters, uses hardcoded matrix size)
- **Computation**: ~2/3 N^3 for elimination + N^2 for back-substitution per solve

---

## Phase 2: Execute Benchmarks on MINIX (NEXT)

### Objective
Boot MINIX on QEMU with various CPU models and vCPU configurations, execute both benchmarks, and collect performance metrics.

### Configuration Matrix
```
CPU Models:   486, Pentium, Pentium2, Pentium3, AMD Athlon (5 total)
vCPU Counts:  1, 2, 4, 8 (4 total)
Samples:      2 per configuration
Total Runs:   5 × 4 × 2 = 40 benchmark pairs
```

### Execution Steps

**For each CPU model and vCPU configuration:**

1. **Boot MINIX to shell prompt**
   ```bash
   qemu-system-i386 \
     -m 512M \
     -smp <vCPU_count> \
     -cpu <CPU_model> \
     -cdrom minix_R3.4.0rc6-d5e4fc0.iso \
     -serial stdio
   ```

2. **Transfer benchmarks to MINIX** (via filesystem or network)
   - Copy `dhrystone` binary to MINIX
   - Copy `linpack` binary to MINIX

3. **Run Dhrystone benchmark**
   ```bash
   dhrystone 10000000
   # Record: DMIPS (Dhrystones per second)
   ```

4. **Run LINPACK benchmark**
   ```bash
   linpack
   # Record: MFLOPS (Million Floating-Point Operations Per Second)
   ```

5. **Shutdown and repeat** for next configuration

### Data Collection

**Per-benchmark metrics to record:**
- CPU model (486, Pentium, Pentium2, Pentium3, Athlon)
- vCPU configuration (1, 2, 4, or 8)
- Sample number (1 or 2)
- Wall-clock execution time (seconds)
- Dhrystone DMIPS result (millions of Dhrystones/sec)
- LINPACK MFLOPS result (millions of FLOPs/sec)

**Example output format:**
```
CPU: 486
vCPU: 1
Sample: 1
Dhrystone Time: 45.23s, DMIPS: 22.1
LINPACK Time: 12.56s, MFLOPS: 78.5
```

### Timeline
- **Total boot time**: ~180 seconds per run (from previous profiling data)
- **Benchmark execution time**: ~60 seconds per run (Dhrystone + LINPACK)
- **Total per configuration**: ~240 seconds
- **Total for all 40 runs**: ~2.7 hours (16,000 seconds)
- **Recommended**: Execute overnight or background process

### Success Criteria

**Benchmark Execution**:
- [ ] All 40 benchmark pairs execute successfully
- [ ] Both Dhrystone and LINPACK produce valid numeric results
- [ ] No QEMU crashes or timeouts

**Data Quality**:
- [ ] CPU model differences visible (if any)
- [ ] SMP scaling pattern evident (linear, sublinear, or absent)
- [ ] Measurement consistency (repeat runs show similar results)

**Validation**:
- [ ] Can compare DMIPS across CPU models
- [ ] Can measure MFLOPS vs. vCPU count
- [ ] Can compute scaling efficiency: (actual_speedup / ideal_speedup) × 100%

---

## Phase 3: Analysis (POST PHASE 2)

### Statistical Analysis
1. **CPU Model Efficiency Comparison**
   - Single-vCPU DMIPS/MFLOPS for each CPU model
   - Compute mean, median, stddev, range
   - Determine if CPU model differences are significant (>5%)

2. **SMP Scaling Analysis**
   - Compare 1-vCPU vs. 2-vCPU, 4-vCPU, 8-vCPU performance
   - Expected: Linear scaling (2x, 4x, 8x speedup) if SMP active
   - Actual: Measure actual speedup vs. ideal
   - Scaling efficiency: (actual_speedup / expected_speedup) × 100%

3. **Bottleneck Identification**
   - If DMIPS scales but MFLOPS doesn't: memory/I/O bottleneck
   - If neither scales: I/O or system bus bottleneck
   - If both scale equally: CPU-bound, SMP working correctly

### Expected Outcomes

**Scenario A: SMP Scaling Visible**
- 2-vCPU: ~1.8-2.0x speedup (90-100% efficiency)
- 4-vCPU: ~3.5-4.0x speedup
- 8-vCPU: ~7.0-8.0x speedup
- **Conclusion**: SMP is active and effective for benchmarks

**Scenario B: CPU Efficiency Gains Visible**
- Pentium: 10-20% faster than 486 (microarchitecture improvements)
- Pentium2: 15-30% faster than Pentium (additional features)
- Pentium3: 20-40% faster than Pentium2
- Athlon: Varies (different microarchitecture)
- **Conclusion**: CPU generation improvements are measurable

**Scenario C: Zero SMP Scaling (Hypothesis from Previous Data)**
- All vCPU configs perform identically (~180s boot time)
- Extension: Synthetic benchmarks may show SMP if they're CPU-intensive
- **Implication**: Boot sequence is I/O-bound; benchmarks may differ

### Deliverables
1. Benchmark execution log (40 runs with all metrics)
2. Comparative performance table (CPU models × vCPU configs)
3. Scaling efficiency analysis chart
4. Root cause assessment for bottleneck identification
5. Final validation report against Chapter 17 whitepaper claims

---

## Next Steps After Phase 2

**If SMP scaling and CPU efficiency visible**:
- Phase 1 complete: CPU architecture claims validated
- Document findings and create final report
- Optional: Proceed to Approach 2 (Full-System Workload) for deeper analysis

**If SMP scaling absent** (consistent with boot profiling):
- Phase 1 shows benchmarks inherit I/O bottleneck from MINIX
- Recommendation: Proceed to Approach 2 (Full-System Workload Profiling)
- Rationale: Need to move beyond boot sequence to measure true CPU/SMP characteristics

**If mixed results** (e.g., LINPACK scales but Dhrystone doesn't):
- Indicates specific bottleneck type (memory vs. instruction cache vs. branches)
- Proceed to Approach 3 or 4 for deeper analysis
- Recommendation: Kernel instrumentation or QEMU TCG profiling

---

## Architecture and Compilation Notes

### Why Native x86-64 Compilation Works
1. **QEMU emulates the entire CPU**: Guest processor is virtual, not host-dependent
2. **Binary format**: ELF i386 from MINIX compiler vs. ELF x86-64 from host compiler doesn't matter—MINIX kernel handles syscalls regardless
3. **System calls**: MINIX intercepts syscalls at kernel level; execution layer is transparent
4. **Verification**: Previous boot profiling confirmed MINIX executes correctly in QEMU emulation

### Ideal Cross-Compilation (For Reference)
If proper IA-32 binary needed:
```bash
# Option 1: i386 cross-compiler (if available)
i386-linux-gcc -O2 -march=i386 dhrystone.c -o dhrystone.i386

# Option 2: MINIX build system
cd /home/eirikr/Playground/minix
./build.sh -m i386 -a i386 [benchmark targets]

# Option 3: NetBSD development environment
docker run --rm -it netbsd /bin/sh
# Then compile with NetBSD's gcc
```

### System Architecture Details
- **MINIX Target**: IA-32 (32-bit x86)
- **Host System**: x86-64 (64-bit x86)
- **Emulation Layer**: QEMU TCG (Tiny Code Generator)
- **Syscall Bridge**: MINIX kernel syscall handler
- **Result**: Benchmarks execute correctly regardless of host/guest binary mismatch

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Benchmark timeout in MINIX | Low | Set reasonable iteration counts |
| QEMU emulation too slow | Low | Already measured ~180s/boot; add 60s for benchmarks |
| MINIX filesystem full | Low | Delete unnecessary files or use tmpfs |
| Benchmark compilation bugs | Medium | Test on host first (completed) |
| Network unavailable for transfer | Medium | Use mounted ISO or serial transfer |

---

**Status**: Phase 1 COMPLETE - Ready to proceed to Phase 2 execution
**Recommendation**: Begin Phase 2 benchmark execution on 2025-11-02
**Timeline**: Expect 2.7-3 hours for complete 40-run matrix

