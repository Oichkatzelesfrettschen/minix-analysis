# Phase 7.5: QEMU-Based MINIX Boot Profiling
## Implementation Approach and Status

**Date**: 2025-10-31
**Objective**: Multi-processor boot performance characterization of MINIX 3.4 RC6
**Platform**: Native QEMU (no Docker dependency)

---

## Decision: Native QEMU Instead of Docker

### Rationale
- **Docker not installed** on this workstation (verified via `docker --version`)
- **QEMU available**: `qemu-system-i386` found at `/usr/bin/qemu-system-i386`
- **Performance benefit**: Direct QEMU boot avoids Docker overhead, provides more accurate profiling
- **Flexibility**: Can test with different hardware configurations (CPU models, RAM sizes)

### Trade-offs
| Aspect | Native QEMU | Docker |
|--------|-------------|--------|
| Boot overhead | None (direct) | ~1-2s container startup |
| Disk management | Explicit QCOW2 files | Managed by compose |
| CLI integration | Direct subprocess | Docker API required |
| Reproducibility | System-dependent QEMU | Containerized, more repeatable |

**Decision**: Proceed with native QEMU; achieves Phase 7.5 objectives with better accuracy.

---

## Deliverables Created

### 1. QEMU Boot Profiler (`phase-7-5-qemu-boot-profiler.py`)

**Purpose**: Comprehensive boot measurement across multi-processor configurations

**Class**: `QemuBootProfiler`
- **Methods**:
  - `verify_iso()`: Validate ISO file exists and is readable
  - `create_disk_image()`: Create QCOW2 for test run
  - `run_qemu_installation()`: Install MINIX from ISO (first run per CPU config)
  - `run_qemu_boot()`: Boot from disk and capture serial log
  - `_parse_boot_markers()`: Extract boot phases from serial output
  - `measure_boot_sample()`: Single boot measurement
  - `run_test_matrix()`: Complete multi-CPU testing
  - `generate_report()`: Format results for whitepaper
  - `save_results()`: Export JSON + text report

**Boot Markers** (10 phases):
```python
'multiboot_detected': Bootloader detects MINIX
'kernel_starts': Kernel initialization begins
'pre_init_phase': pre_init() executes (memory setup)
'kmain_phase': kmain() orchestration begins
'cstart_phase': cstart() CPU setup
'process_init': Process table initialization
'memory_init': Memory allocator initialization
'system_init': Exception/interrupt handlers
'scheduler_ready': Scheduler operational
'shell_prompt': Shell available for login
```

**Whitepaper Baseline** (milliseconds):
- i386: 65 ms total (estimate)
- ARM: 56 ms total (estimate)

**Test Matrix**:
```
CPU Counts: [1, 2, 4, 8] vCPU
Samples: Configurable (default 3 per config)
Total samples: 12 measurements
Expected duration: ~40-60 minutes for full matrix (5 samples each)
```

**Output Format**:
- JSON report: `phase-7-5-results-{timestamp}.json`
- Text report: `phase-7-5-report-{timestamp}.txt`
- Boot logs: `boot-{cpus}cpu-{timestamp}.log` (per measurement)
- Disk images: `minix-{cpus}cpu-{timestamp}.qcow2` (per CPU config)

---

## Test Execution Plan

### Phase 7.5a: Validation (Quick test)
```bash
cd /home/eirikr/Playground/minix-analysis
python3 phase-7-5-qemu-boot-profiler.py \
  --iso docker/minix_R3.4.0rc6-d5e4fc0.iso \
  --output measurements/phase-7-5 \
  --samples 1
```

**Expected output**:
- 1 boot sample per CPU config (1, 2, 4, 8)
- Duration: ~15-20 minutes
- Validates profiler works and produces measurable data

### Phase 7.5b: Production run (Full test)
```bash
python3 phase-7-5-qemu-boot-profiler.py \
  --iso docker/minix_R3.4.0rc6-d5e4fc0.iso \
  --output measurements/phase-7-5-final \
  --samples 5
```

**Expected output**:
- 5 boot samples per CPU config (20 total)
- Duration: ~60-90 minutes
- Sufficient statistical power for whitepaper validation
- Calculate mean, median, stdev per configuration

---

## Chapter 17 Data Preparation

### Whitepaper Integration Points

**Section 17.1: Real System Validation**
- Compare measured boot times vs. whitepaper estimates
- Calculate error percentages
- Determine "VERIFIED" (< 10%), "PLAUSIBLE" (10-20%), "NEEDS_VALIDATION" (> 20%)

**Section 17.2: Multi-Processor Scaling**
- Boot time vs. CPU count (1 → 2 → 4 → 8)
- Calculate speedup ratio: T(1 CPU) / T(N CPUs)
- Calculate efficiency: (speedup / N) * 100%
- Analyze overhead of multi-processor boot coordination

**Section 17.3: Boot Phase Breakdown** (if profiling captures phases)
- Time per major boot phase
- Identify bottlenecks
- Quantify kernel initialization overhead

**Section 17.4: System Characterization**
- Boot time vs. system load
- Repeatability analysis (standard deviation)
- Variance source identification

### Output Data for LaTeX
```
Chapter 17 Input Files:
  - measurements/phase-7-5-final/phase-7-5-results-*.json
  - measurements/phase-7-5-final/phase-7-5-report-*.txt
```

**JSON Structure for TikZ Diagram Generation**:
```json
{
  "cpu_1": {
    "cpus": 1,
    "statistics": {
      "mean_ms": 65,
      "stdev_ms": 3
    },
    "whitepaper_comparison": {
      "estimated_ms": 65,
      "error_percent": 0.0,
      "status": "VERIFIED"
    }
  },
  "cpu_2": { ... },
  "cpu_4": { ... },
  "cpu_8": { ... }
}
```

---

## Known Limitations

### 1. QEMU Emulation Accuracy
- QEMU may not perfectly reflect real hardware boot behavior
- TCG (CPU emulation) slower than KVM (if/when available)
- Single machine architecture (i386) - no ARM testing without ARM host

### 2. Boot Marker Detection
- Relies on serial log regex matching
- May miss markers if boot messages vary from expected
- Fallback: line-based timing estimation (~100ms per output line)

### 3. Time Resolution
- QEMU serial log timestamp resolution limited
- Sub-millisecond accuracy not achievable
- ±100ms uncertainty acceptable for whitepaper

### 4. Installation Time Not Measured
- First-boot MINIX installation takes 5-15 minutes
- Measured boots assume disk already prepared
- Installation time not included in boot timing

### 5. Test Duration
- Full test matrix (5 samples × 4 CPU configs) requires 60-90 minutes
- Blocking process (sequential QEMU runs)
- Can be parallelized if multiple CPU cores available

---

## Success Criteria

- [x] QEMU profiler script created and syntactically valid
- [ ] ISO file verified and accessible
- [ ] Single-CPU boot measurement completes successfully
- [ ] Multi-CPU test matrix produces measurements for all configs
- [ ] Measurements cluster within ±10% of whitepaper estimates
- [ ] Scaling analysis shows expected patterns (typically boot time varies inversely with CPU count)
- [ ] JSON + text reports generated
- [ ] Chapter 17 data prepared for LaTeX integration

---

## Integration with Phase 8

### Phase 8 Enhancements (Planned)
1. **MCP Server Integration**: Expose QEMU profiler as MCP service (HTTP API)
2. **Real-time Dashboard**: Live boot progress visualization
3. **Comparative Analysis**: i386 vs ARM (if ARM artifacts available)
4. **Statistical Analysis**: Multi-run variance, confidence intervals
5. **Optimization Feedback**: Identify and document boot bottlenecks

### Phase 8 Data Dependencies
- Phase 7.5 JSON outputs become input for Phase 8 analysis tools
- Boot marker data enables timeline visualizations
- Multi-CPU scaling data informs performance optimization recommendations

---

## File Manifest

```
/home/eirikr/Playground/minix-analysis/
├── phase-7-5-qemu-boot-profiler.py          [NEW] QEMU boot profiler (520 lines)
├── docker/
│   └── minix_R3.4.0rc6-d5e4fc0.iso          [EXISTING] MINIX ISO (633 MB)
├── measurements/
│   └── phase-7-5/
│       ├── boot-1cpu-*.log                   [OUTPUT] Serial logs
│       ├── minix-1cpu-*.qcow2                [OUTPUT] Disk images
│       ├── phase-7-5-results-*.json          [OUTPUT] Raw data
│       └── phase-7-5-report-*.txt            [OUTPUT] Human-readable report
└── PHASE-7-5-IMPLEMENTATION-NOTES.md         [NEW] This document
```

---

## Next Steps

1. **Validate Profiler** (Immediate)
   ```bash
   python3 phase-7-5-qemu-boot-profiler.py --iso docker/minix_R3.4.0rc6-d5e4fc0.iso --samples 1
   ```

2. **Run Full Test Matrix** (Once validation passes)
   ```bash
   python3 phase-7-5-qemu-boot-profiler.py --iso docker/minix_R3.4.0rc6-d5e4fc0.iso --samples 5
   ```

3. **Analyze Results** (Post-execution)
   - Review JSON output for data quality
   - Compare measured vs. estimated boot times
   - Generate whitepaper figures

4. **Write Chapter 17** (Using Phase 7.5 data)
   - Whitepaper Real System Validation section
   - Include timing tables, scaling graphs, bottleneck analysis

5. **Proceed to Phase 8** (Based on Phase 7.5 findings)
   - Enhance CLI with comparative analysis
   - Develop MCP server for CI/CD integration
   - Create performance optimization recommendations

---

## Appendix: QEMU Command Reference

### Basic Boot Measurement
```bash
qemu-system-i386 \
  -m 512M \
  -smp 2 \
  -cpu host \
  -hda disk.qcow2 \
  -serial file:boot.log \
  -display none \
  -nographic
```

### With Network
```bash
qemu-system-i386 \
  -m 512M \
  -smp 2 \
  -cpu host \
  -hda disk.qcow2 \
  -net nic,model=e1000 \
  -net user \
  -serial file:boot.log \
  -display none
```

### With VNC (for interactive testing)
```bash
qemu-system-i386 \
  -m 512M \
  -smp 2 \
  -cpu host \
  -hda disk.qcow2 \
  -vnc 0.0.0.0:0 \
  -serial file:boot.log \
  -monitor stdio
```

### CPU Model Variations
- `-cpu host`: Use host CPU (best performance)
- `-cpu qemu64`: Generic x86-64 (emulated, slower)
- `-cpu Penryn`: Specific Intel model
- `-cpu Nehalem`: Sandy Bridge era
- `-cpu EPYC`: AMD EPYC model

### Performance Options
- `-enable-kvm`: Use KVM acceleration (if available)
- `-accel tcg`: Software CPU emulation (always available)
- `-accel kvm,tcg`: Try KVM first, fallback to TCG

---

*End of Phase 7.5 Implementation Notes*
