# PHASE 7.5: Multi-Processor QEMU Testing & Real System Validation

**Date**: 2025-10-31  
**Status**: Specification & Planning  
**Scope**: QEMU-within-Docker multi-processor testing, real ISO validation, platform verification

================================================================================
EXECUTIVE SUMMARY
================================================================================

Phase 7.5 extends Phase 7 infrastructure by:
1. Using the actual MINIX RC6 ISO (`minix_R3.4.0rc6-d5e4fc0.iso`)
2. Testing QEMU-within-Docker with multiple CPU configurations
3. Validating i386 (x86 32-bit IA-32) and ARM native support
4. Cross-processor boot timing measurements
5. Real system validation against whitepaper claims

This phase bridges Phase 7 (infrastructure) and Phase 8 (MCP enhancements) by:
- Proving the Docker/QEMU containerization works with real MINIX
- Collecting baseline measurements across processor configurations
- Validating measurement tools against actual system behavior
- Establishing data collection for Chapter 17

================================================================================
PHASE 7.5 OBJECTIVES
================================================================================

### Primary Objectives

1. **ISO Validation**
   - Verify MINIX RC6 ISO integrity (SHA checksum)
   - Successfully boot MINIX i386 in QEMU within Docker
   - Test ARM MINIX if build available

2. **Multi-Processor Testing**
   - Test MINIX boot with 1, 2, 4, 8 vCPU configurations
   - Measure boot time variance across processor counts
   - Identify CPU scaling impacts on boot timeline

3. **Real System Measurements**
   - Collect actual boot timings from MINIX i386
   - Compare against whitepaper estimates (35-65ms)
   - Validate marker detection in real environment
   - Generate real measurement data

4. **Multi-Architecture Support**
   - Verify i386 (IA-32) support works correctly
   - Test ARM support (if build available)
   - Document processor family behavior
   - Create comparative analysis framework

5. **Data Collection for Phase 8**
   - Real boot measurements (10+ samples per config)
   - Syscall frequency baseline (from running MINIX)
   - Memory access patterns (page faults, cache behavior)
   - Performance characterization data

### Secondary Objectives

1. **Documentation**
   - Record all processor configurations tested
   - Document measurement accuracy
   - Create real-system baseline report

2. **Infrastructure Validation**
   - Verify Docker Compose orchestration works
   - Test volume persistence across runs
   - Validate measurement storage structure

3. **CLI Verification**
   - Test all CLI commands against real MINIX
   - Verify MCP server connectivity
   - Validate report generation

================================================================================
IMPLEMENTATION PLAN
================================================================================

## Step 1: ISO Verification

### SHA Checksum Validation
```bash
# Expected SHA-1 hash starts with: d5e4fc0
sha1sum /home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso

# Expected: d5e4fc0... minix_R3.4.0rc6-d5e4fc0.iso
```

### File Verification Checklist
- [ ] File exists and is readable
- [ ] File size reasonable (150-200 MB)
- [ ] SHA checksum matches
- [ ] ISO can be mounted (verify ISO structure)

---

## Step 2: Docker Build Preparation

### Dockerfile Modifications for Real ISO
Update `Dockerfile.i386` to use actual ISO:

```dockerfile
# Copy real MINIX ISO
COPY minix_R3.4.0rc6-d5e4fc0.iso /minix-runtime/minix.iso

# Create disk image from ISO
RUN qemu-img create -f qcow2 /minix-runtime/minix-i386.qcow2 2G

# Note: Actual installation via interactive QEMU session required
# Or pre-create disk image with OS already installed
```

### Build Commands
```bash
cd /home/eirikr/Playground/minix-analysis

# Build i386 image with real ISO
docker-compose build minix-i386

# Build MCP servers
docker-compose build mcp-boot-profiler
docker-compose build mcp-syscall-tracer
docker-compose build mcp-memory-monitor
```

---

## Step 3: Multi-Processor Configuration Testing

### Test Matrix (i386)

| Config | CPUs | Memory | KVM | Expected Boot Time |
|--------|------|--------|-----|-------------------|
| Single | 1    | 256MB  | Yes | Baseline (slower) |
| Dual   | 2    | 512MB  | Yes | Expected ~50-65ms |
| Quad   | 4    | 768MB  | Yes | Expected ~45-60ms |
| Octa   | 8    | 1GB    | Yes | Expected ~40-55ms |
| NoKVM  | 2    | 512MB  | No  | Expected ~100-200ms (TCG fallback) |

### Test Configuration YAML

Create `docker-compose.multi-processor.yml`:

```yaml
version: '3.9'

services:
  minix-i386-single:
    build:
      context: ./docker
      dockerfile: Dockerfile.i386
    container_name: minix-rc6-i386-1cpu
    cpus: '1'
    mem_limit: 256m
    # ... rest of config

  minix-i386-dual:
    cpus: '2'
    mem_limit: 512m
    container_name: minix-rc6-i386-2cpu
    # ...

  minix-i386-quad:
    cpus: '4'
    mem_limit: 768m
    container_name: minix-rc6-i386-4cpu
    # ...

  minix-i386-octa:
    cpus: '8'
    mem_limit: 1024m
    container_name: minix-rc6-i386-8cpu
    # ...
```

### Test Execution

```bash
# Launch single-CPU instance
docker-compose -f docker-compose.multi-processor.yml up -d minix-i386-single
python3 cli/minix-analysis-cli.py measure --metric boot --arch i386 --container minix-rc6-i386-1cpu

# Repeat for 2, 4, 8 CPUs
docker-compose -f docker-compose.multi-processor.yml down

# Collect results
ls -la measurements/i386/
```

---

## Step 4: Real System Measurements

### Boot Profiler Testing

```bash
# Test 1: Basic boot measurement
python3 docker/boot-profiler.py \
  --arch i386 \
  --container minix-rc6-i386 \
  --timeout 120

# Expected output: JSON report with boot markers
```

### Multiple Runs for Variance Analysis

```bash
# Run boot test 10 times, collect measurements
for i in {1..10}; do
  echo "Run $i..."
  python3 docker/boot-profiler.py --arch i386 --container minix-rc6-i386
  sleep 5
done

# Analyze variance
python3 -c "
import json
import glob
from pathlib import Path

measurements = []
for file in sorted(glob.glob('measurements/i386/boot-*.json'))[-10:]:
    with open(file) as f:
        data = json.load(f)
        measurements.append(data['total_time_ms'])

print(f'Samples: {len(measurements)}')
print(f'Min: {min(measurements):.1f}ms')
print(f'Max: {max(measurements):.1f}ms')
print(f'Mean: {sum(measurements)/len(measurements):.1f}ms')
print(f'Whitepaper: 35-65ms')
"
```

### Syscall Tracing from Real MINIX

```bash
# Start MINIX container
docker-compose up -d minix-i386

# SSH into MINIX (if SSH available)
ssh -p 2222 root@localhost

# Once inside MINIX, run strace on a process
strace -c /bin/ls

# Or monitor from host
docker exec minix-rc6-i386 strace -c /bin/ls
```

### Memory Monitoring

```bash
# Monitor memory events during boot
curl -X POST http://localhost:5003/monitor-memory \
  -H "Content-Type: application/json" \
  -d '{"duration": 60}'
```

---

## Step 5: Whitepaper Validation

### Comparison Script

Create `validate-whitepaper.py`:

```python
#!/usr/bin/env python3
import json
import glob
from pathlib import Path

# Load all measurements
measurements = {}
for arch in ['i386', 'arm']:
    arch_dir = Path(f'measurements/{arch}')
    if not arch_dir.exists():
        continue
    
    measurements[arch] = []
    for file in arch_dir.glob('boot-*.json'):
        with open(file) as f:
            data = json.load(f)
            if 'total_time_ms' in data:
                measurements[arch].append(data['total_time_ms'])

# Whitepaper estimates
estimates = {
    'i386': {'total': 65, 'kernel': 35},  # ms
    'arm': {'total': 56, 'kernel': 28},   # ms
}

# Analysis
for arch, times in measurements.items():
    if not times:
        continue
    
    mean = sum(times) / len(times)
    estimate = estimates[arch]['total']
    error = abs(mean - estimate) / estimate * 100
    
    status = 'VERIFIED' if error < 10 else 'PLAUSIBLE' if error < 20 else 'NEEDS_VALIDATION'
    
    print(f"\n{arch.upper()} WHITEPAPER VALIDATION")
    print(f"  Estimate: {estimate}ms")
    print(f"  Measured: {mean:.1f}ms")
    print(f"  Error: {error:.1f}%")
    print(f"  Status: {status}")
    print(f"  Samples: {len(times)}")
```

---

## Step 6: Data Aggregation for Chapter 17

### Measurement Summary Report

```bash
# Generate comprehensive report
python3 cli/minix-analysis-cli.py report --arch i386 --format json > phase-7-5-results.json

# Extract key metrics
python3 -c "
import json
with open('phase-7-5-results.json') as f:
    data = json.load(f)
    print('=== Phase 7.5 Results ===')
    print(f'Boot measurements: {data.get(\"measurement_count\", 0)}')
    print(f'Architecture: {data.get(\"architecture\")}')
    print(f'Latest boot: {data[\"measurements\"].get(\"latest_boot\", {})}')
"
```

---

## Step 7: ARM Testing (if available)

### ARM MINIX Build Check

```bash
# Check if ARM build is available
ls -la /home/eirikr/Playground/minix/minix/kernel/arch/arm/ || echo "ARM support not in this build"

# If available, test ARM variant
docker-compose up -d minix-arm
python3 docker/boot-profiler.py --arch arm --container minix-rc6-arm
```

### ARM Boot Marker Detection

Test the same 10 boot markers for ARM:
- multiboot_detected
- kernel_starts
- pre_init_phase
- kmain_phase
- cstart_phase
- process_init
- memory_init
- system_init
- scheduler_ready
- shell_prompt

================================================================================
SUCCESS CRITERIA
================================================================================

### Phase 7.5 Completion Checklist

- [ ] MINIX RC6 ISO downloaded (d5e4fc0 SHA verified)
- [ ] ISO file validates successfully
- [ ] Docker i386 image builds with real ISO
- [ ] MINIX boots in QEMU within Docker
- [ ] Boot profiler detects all 10 markers
- [ ] Measurements collected (10+ samples)
- [ ] Boot time within ±20% of whitepaper
- [ ] Multi-CPU configurations tested
- [ ] MCP servers connect to real MINIX
- [ ] CLI commands work against real instance
- [ ] Comparison report generated
- [ ] Data ready for Chapter 17

### Performance Targets

| Metric | Target | Success Criteria |
|--------|--------|-----------------|
| Boot Time (i386) | 35-65ms | Within range |
| Marker Detection | 10/10 | All markers found |
| Measurement Accuracy | ±5ms | Consistent samples |
| Multi-CPU Scaling | Linear | Clear performance trend |
| System Stability | 100% | No crashes in 10 runs |

### Data Quality

- [ ] All measurements have timestamps
- [ ] All measurements have boot markers
- [ ] JSON reports valid and complete
- [ ] Consistent directory structure
- [ ] Reproducible results across runs

================================================================================
TIMELINE
================================================================================

**Estimated Duration**: 2-3 hours

| Step | Task | Duration | Status |
|------|------|----------|--------|
| 1 | ISO Download & Verification | 30 min | In Progress |
| 2 | Docker Build | 15 min | Pending |
| 3 | Single Boot Test | 10 min | Pending |
| 4 | Multi-Processor Tests | 45 min | Pending |
| 5 | Real Measurements | 30 min | Pending |
| 6 | Validation Report | 20 min | Pending |
| 7 | ARM Testing (if available) | 20 min | Pending |

**Total**: ~2.5 hours for complete Phase 7.5

================================================================================
BLOCKERS AND MITIGATIONS
================================================================================

### Blocker 1: Docker KVM Access
**Issue**: KVM device not available in container
**Mitigation**: Fall back to TCG (QEMU software emulation, slower)
**Impact**: Boot time increases 2-3x, but still measurable

### Blocker 2: MINIX Installation
**Issue**: ISO boot doesn't automatically install to disk
**Mitigation**: 
- Pre-create disk image with MINIX already installed
- Or use interactive installation within container
- Or use existing MINIX installation from local system

### Blocker 3: ARM Build Not Available
**Issue**: MINIX RC6 may not have ARM support compiled
**Mitigation**: Focus on i386 testing, note ARM limitation in report

### Blocker 4: Network/SSH Issues
**Issue**: Can't SSH into MINIX container for advanced testing
**Mitigation**: Use docker exec and strace from host, or collect data via serial console

================================================================================
INTEGRATION WITH PHASE 8
================================================================================

Phase 7.5 outputs feed directly into Phase 8:

1. **Real Measurement Data**
   - Boot timing dataset (10+ samples, multiple CPU configs)
   - Baseline for performance comparison

2. **MCP Server Validation**
   - Prove all 24 endpoints work with real MINIX
   - Real syscall traces from running system
   - Real memory events during operation

3. **CLI Tool Validation**
   - All 7 CLI commands tested against real infrastructure
   - Error handling verified in production scenario
   - Report generation validated

4. **Chapter 17 Data**
   - Real boot times for whitepaper validation
   - Syscall frequency baseline
   - Memory behavior characterization
   - Multi-processor impact analysis

================================================================================
EXPECTED OUTPUTS
================================================================================

### Files Generated

```
measurements/i386/
├── boot-2025-10-31T21:50:00.json      # Single CPU run
├── boot-2025-10-31T21:55:00.json      # Dual CPU run
├── boot-2025-10-31T22:00:00.json      # Quad CPU run
├── boot-2025-10-31T22:05:00.json      # Octa CPU run
└── ...                                 # 10 total samples

phase-7-5-results.json                  # Aggregated results
phase-7-5-whitepaper-comparison.txt    # Validation report
```

### Data Summary Example

```
=== PHASE 7.5 RESULTS ===
Architecture: i386 (IA-32)
Processor Configs Tested: 5 (1, 2, 4, 8 CPU + TCG)
Total Boot Samples: 50
Total Test Duration: 2.5 hours

Boot Time Analysis:
  Single CPU (TCG):    145.3ms (10 samples)
  Dual CPU (KVM):      58.2ms (10 samples)
  Quad CPU (KVM):      52.1ms (10 samples)
  Octa CPU (KVM):      48.7ms (10 samples)
  2 CPU NoKVM (TCG):   162.1ms (10 samples)

Whitepaper Comparison:
  Estimated: 35-65ms
  Measured Mean: 52.4ms
  Error: 5.1%
  Status: VERIFIED

Boot Markers (all tests):
  ✓ multiboot_detected: 100% detection
  ✓ kernel_starts: 100% detection
  ✓ pre_init_phase: 100% detection
  ✓ kmain_phase: 100% detection
  ✓ cstart_phase: 100% detection
  ✓ process_init: 100% detection
  ✓ memory_init: 100% detection
  ✓ system_init: 100% detection
  ✓ scheduler_ready: 100% detection
  ✓ shell_prompt: 100% detection

Performance Scaling:
  1 CPU: 145.3ms (baseline, no SMP)
  2 CPU: 58.2ms (2.5x improvement)
  4 CPU: 52.1ms (2.8x improvement)
  8 CPU: 48.7ms (3.0x improvement)
  
Conclusion: Linear scaling on additional CPUs, clear performance improvement
```

================================================================================
DELIVERABLES
================================================================================

Phase 7.5 will deliver:

1. **Real Measurement Dataset**
   - 50+ boot timing samples
   - Multiple processor configurations
   - JSON reports for all runs

2. **Whitepaper Validation Report**
   - Boot timing vs. estimates
   - Error percentage calculation
   - Marker detection success rate

3. **Multi-Processor Analysis**
   - CPU scaling analysis
   - Performance impact quantification
   - Optimal CPU count recommendation

4. **Infrastructure Validation**
   - Proof of Docker Compose functionality
   - MCP server real-world testing
   - CLI tool operational validation

5. **Chapter 17 Baseline Data**
   - Real system measurements
   - Comparative analysis framework
   - Whitepaper claim validation

================================================================================
NEXT PHASE (8) PREPARATION
================================================================================

Phase 7.5 completes with:
- ✓ Proven Docker/QEMU containerization
- ✓ Real MINIX running in containers
- ✓ Actual boot measurements from real system
- ✓ All MCP servers tested against real instance
- ✓ Whitepaper validation framework established
- ✓ Data collection infrastructure proven
- ✓ Ready for Phase 8 enhancements

Phase 8 will use this data to:
- Implement enhanced MCP server features
- Add authentication and rate limiting
- Develop comparative analysis tools
- Write Chapter 17 with real data
- Create advanced reporting features

================================================================================
END OF PHASE 7.5 SPECIFICATION
================================================================================
