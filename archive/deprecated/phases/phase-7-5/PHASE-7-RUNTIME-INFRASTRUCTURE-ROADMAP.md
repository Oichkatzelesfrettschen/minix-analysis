# PHASE 7-10: RUNTIME INFRASTRUCTURE & AUTOMATED ANALYSIS ROADMAP

**Date**: 2025-10-31
**Status**: Planning Phase (Ready for Granular Implementation)
**Scope**: Docker/QEMU integration, MCP tool development, CLI automation, iterative testing

================================================================================
EXECUTIVE SUMMARY
================================================================================

This roadmap integrates the Docker/QEMU runtime solutions with novel MCP tools to create
an automated analysis pipeline that can:

1. Launch MINIX instances (i386 and ARM) in Docker/QEMU
2. Instrument running MINIX with tracing tools
3. Measure real boot times, syscall latencies, memory patterns
4. Validate whitepaper claims against actual system behavior
5. Automate data collection and comparison
6. Provide interactive CLI interfaces for exploration

**Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                    MINIX Analysis Suite                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  MINIX i386    │  │  MINIX ARM     │  │  Analysis    │  │
│  │  (Docker/QEMU) │  │  (Docker/QEMU) │  │  Control     │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│        ↓                    ↓                     ↓          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          MCP Server Layer (Novel Tools)             │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │ Boot Profiler│  │ Syscall Trace│  ┌──────────┐ │  │
│  │  │ MCP Server   │  │ MCP Server   │  │ Memory   │ │  │
│  │  └──────────────┘  └──────────────┘  │ Monitor  │ │  │
│  │                                       │ MCP Srv  │ │  │
│  └───────────────────────────────────────┴──────────┘  │  │
│                           ↓                             │  │
│  ┌──────────────────────────────────────────────────┐  │  │
│  │      Claude Code CLI Integration Layer           │  │  │
│  │  - Interactive QEMU launcher                    │  │  │
│  │  - Real-time measurement dashboard              │  │  │
│  │  - Automated comparison engine                  │  │  │
│  └──────────────────────────────────────────────────┘  │  │
└──────────────────────────────────────────────────────────────┘
```

================================================================================
PHASE 7: DOCKER/QEMU INFRASTRUCTURE SETUP (1 Week)
================================================================================

## 7.1: QEMU in Docker Containerization

### 7.1.1: i386 MINIX Docker Image

**File**: `/home/eirikr/Playground/minix-analysis/docker/Dockerfile.i386`

```dockerfile
FROM ubuntu:22.04

# Install QEMU and dependencies
RUN apt-get update && apt-get install -y \
    qemu-system-x86 \
    qemu-utils \
    curl \
    wget \
    openssh-client \
    socat \
    netcat \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Create MINIX working directory
WORKDIR /minix-runtime

# Copy MINIX ISO (will be mounted at build time)
COPY minix_R3.4.0-rc6.iso /minix-runtime/

# Create disk image
RUN qemu-img create -f qcow2 minix-i386.qcow2 2G

# QEMU boot script with measurement hooks
COPY ./run-qemu-i386.sh /minix-runtime/
RUN chmod +x /minix-runtime/run-qemu-i386.sh

# Expose monitoring ports
EXPOSE 5900 2222 9000

ENTRYPOINT ["/minix-runtime/run-qemu-i386.sh"]
```

**Boot Script**: `/home/eirikr/Playground/minix-analysis/docker/run-qemu-i386.sh`

```bash
#!/bin/bash

# Start QEMU i386 with measurement hooks
# Log boot sequence to timestamped file
BOOT_LOG="/minix-runtime/boot-$(date +%s).log"

exec qemu-system-i386 \
  -m 512M \
  -smp 2 \
  -cpu host \
  -enable-kvm \
  -hda /minix-runtime/minix-i386.qcow2 \
  -vnc 0.0.0.0:0 \
  -net nic,model=e1000 \
  -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::9000-:9000 \
  -trace enable=qemu_perf_* \
  -D /minix-runtime/qemu-debug.log \
  -serial file:${BOOT_LOG} \
  2>&1 | tee /minix-runtime/qemu-console.log
```

### 7.1.2: ARM MINIX Docker Image

**File**: `/home/eirikr/Playground/minix-analysis/docker/Dockerfile.arm`

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    qemu-system-arm \
    qemu-utils \
    curl \
    wget \
    openssh-client \
    socat \
    netcat \
    strace \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /minix-runtime

# For ARM, we may need to build from source or use pre-built kernel/rootfs
# This is a placeholder for ARM image setup
COPY ./run-qemu-arm.sh /minix-runtime/
RUN chmod +x /minix-runtime/run-qemu-arm.sh

EXPOSE 5900 2222 9000

ENTRYPOINT ["/minix-runtime/run-qemu-arm.sh"]
```

### 7.1.3: Docker Compose Orchestration

**File**: `/home/eirikr/Playground/minix-analysis/docker-compose.yml`

```yaml
version: '3.9'

services:
  # i386 MINIX instance
  minix-i386:
    build:
      context: ./docker
      dockerfile: Dockerfile.i386
    container_name: minix-rc6-i386
    privileged: true
    devices:
      - /dev/kvm:/dev/kvm
    ports:
      - "5900:5900"  # VNC
      - "2222:2222"  # SSH
      - "9000:9000"  # Analysis port
    volumes:
      - ./data/minix-i386:/minix-runtime
      - ./measurements/i386:/measurements
    environment:
      - DISPLAY=:0
      - QEMU_CPU=host
    networks:
      - minix-net

  # ARM MINIX instance (requires ARM build)
  minix-arm:
    build:
      context: ./docker
      dockerfile: Dockerfile.arm
    container_name: minix-rc6-arm
    privileged: true
    devices:
      - /dev/kvm:/dev/kvm
    ports:
      - "5901:5900"  # VNC (offset)
      - "2223:2222"  # SSH (offset)
      - "9001:9000"  # Analysis port (offset)
    volumes:
      - ./data/minix-arm:/minix-runtime
      - ./measurements/arm:/measurements
    environment:
      - QEMU_CPU=host
    networks:
      - minix-net
    depends_on:
      - minix-i386  # Sequential startup

  # MCP Boot Profiler server
  mcp-boot-profiler:
    build:
      context: ./mcp-servers/boot-profiler
      dockerfile: Dockerfile
    container_name: mcp-boot-profiler
    ports:
      - "5001:5000"
    volumes:
      - ./measurements:/measurements
      - ./data:/data
    networks:
      - minix-net
    depends_on:
      - minix-i386
      - minix-arm

  # MCP Syscall Tracer server
  mcp-syscall-tracer:
    build:
      context: ./mcp-servers/syscall-tracer
      dockerfile: Dockerfile
    container_name: mcp-syscall-tracer
    ports:
      - "5002:5000"
    volumes:
      - ./measurements:/measurements
      - ./data:/data
    networks:
      - minix-net
    depends_on:
      - minix-i386

  # MCP Memory Monitor server
  mcp-memory-monitor:
    build:
      context: ./mcp-servers/memory-monitor
      dockerfile: Dockerfile
    container_name: mcp-memory-monitor
    ports:
      - "5003:5000"
    volumes:
      - ./measurements:/measurements
      - ./data:/data
    networks:
      - minix-net
    depends_on:
      - minix-i386

networks:
  minix-net:
    driver: bridge

volumes:
  minix-i386-data:
  minix-arm-data:
  measurements:
```

### 7.1.4: Build and Launch Sequence

**Build Steps**:

```bash
# 1. Download MINIX RC6 ISO
cd /home/eirikr/Playground/minix-analysis
wget https://github.com/Minix3/minix/releases/download/3.4.0-rc6/minix_R3.4.0-rc6.iso \
  -O docker/minix_R3.4.0-rc6.iso

# 2. Build Docker images
docker-compose build minix-i386
docker-compose build minix-arm

# 3. Launch infrastructure
docker-compose up -d minix-i386
docker-compose logs -f minix-i386

# 4. Monitor boot
tail -f measurements/i386/boot-*.log
```

---

## 7.2: CLI Boot Profiler Tool

**File**: `/home/eirikr/Playground/minix-analysis/tools/boot-profiler-cli.py`

```python
#!/usr/bin/env python3
"""
Boot Profiler CLI Tool
Measures MINIX boot timeline in Docker/QEMU container
"""

import subprocess
import time
import json
import re
from pathlib import Path
from datetime import datetime

class BootProfiler:
    def __init__(self, container_name, arch="i386"):
        self.container_name = container_name
        self.arch = arch
        self.measurements = {}
        self.start_time = None

    def start_container(self):
        """Start MINIX container"""
        print(f"Starting {self.arch} container: {self.container_name}")
        self.start_time = time.time()

        result = subprocess.run(
            ["docker", "start", self.container_name],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False

        self.measurements['container_start'] = time.time() - self.start_time
        return True

    def wait_for_boot(self, timeout=120):
        """Monitor container for boot completion markers"""
        markers = {
            'multiboot_detected': r'Booting from.*multiboot',
            'pre_init_start': r'pre_init\(\)',
            'kmain_start': r'kmain\(\)',
            'scheduler_ready': r'scheduler.*ready|Scheduling',
            'shell_prompt': r'\$|#'
        }

        found = {}

        for i in range(timeout):
            logs = subprocess.run(
                ["docker", "logs", "--tail=50", self.container_name],
                capture_output=True,
                text=True
            ).stdout

            for marker_name, pattern in markers.items():
                if marker_name not in found and re.search(pattern, logs):
                    found[marker_name] = time.time() - self.start_time
                    print(f"✓ {marker_name}: {found[marker_name]:.2f}s")

            if len(found) == len(markers):
                break

            time.sleep(1)

        self.measurements.update(found)
        return len(found) == len(markers)

    def extract_kernel_metrics(self):
        """Extract kernel-specific timing from boot output"""
        logs = subprocess.run(
            ["docker", "logs", self.container_name],
            capture_output=True,
            text=True
        ).stdout

        # Parse kmain execution metrics
        if 'kernel init' in logs.lower():
            # Extract timing from kernel output
            kernel_time_match = re.search(r'kernel.*init.*(\d+)ms', logs)
            if kernel_time_match:
                self.measurements['kernel_init_ms'] = int(kernel_time_match.group(1))

        return self.measurements

    def generate_report(self):
        """Generate boot timeline report"""
        print("\n" + "="*60)
        print(f"BOOT TIMELINE REPORT - {self.arch.upper()}")
        print("="*60)

        for marker, elapsed in sorted(self.measurements.items(), key=lambda x: x[1]):
            print(f"{marker:.<40} {elapsed:>6.2f}s")

        if 'scheduler_ready' in self.measurements:
            total = self.measurements['scheduler_ready']
            print(f"\nTOTAL BOOT TIME: {total:.2f}s ({total*1000:.0f}ms)")

        # Save to JSON
        report_file = Path(f"measurements/{self.arch}/boot-report-{datetime.now().isoformat()}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(self.measurements, f, indent=2)

        print(f"\nReport saved: {report_file}")
        return self.measurements

def main():
    import argparse

    parser = argparse.ArgumentParser(description='MINIX Boot Profiler')
    parser.add_argument('--arch', choices=['i386', 'arm'], default='i386')
    parser.add_argument('--container', default='minix-rc6-i386')
    parser.add_argument('--timeout', type=int, default=120)

    args = parser.parse_args()

    profiler = BootProfiler(args.container, args.arch)

    if profiler.start_container():
        if profiler.wait_for_boot(timeout=args.timeout):
            profiler.extract_kernel_metrics()
            profiler.generate_report()
        else:
            print("Boot timeout - partial results available")
    else:
        print("Failed to start container")

if __name__ == '__main__':
    main()
```

---

## 7.3: Directory Structure

```
/home/eirikr/Playground/minix-analysis/
├── docker/
│   ├── Dockerfile.i386
│   ├── Dockerfile.arm
│   ├── run-qemu-i386.sh
│   ├── run-qemu-arm.sh
│   └── minix_R3.4.0-rc6.iso  [Downloaded]
├── docker-compose.yml
├── mcp-servers/
│   ├── boot-profiler/
│   │   ├── Dockerfile
│   │   ├── server.py
│   │   └── requirements.txt
│   ├── syscall-tracer/
│   │   ├── Dockerfile
│   │   ├── server.py
│   │   └── requirements.txt
│   └── memory-monitor/
│       ├── Dockerfile
│       ├── server.py
│       └── requirements.txt
├── tools/
│   ├── boot-profiler-cli.py
│   ├── syscall-tracer-cli.py
│   └── memory-monitor-cli.py
├── measurements/
│   ├── i386/
│   └── arm/
└── data/
    ├── minix-i386/
    └── minix-arm/
```

================================================================================
PHASE 8: NOVEL MCP SERVERS (1.5 Weeks)
================================================================================

## 8.1: Boot Profiler MCP Server

**File**: `/home/eirikr/Playground/minix-analysis/mcp-servers/boot-profiler/server.py`

```python
#!/usr/bin/env python3
"""
MCP Boot Profiler Server
Provides real-time boot measurement and comparison
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from mcp.server import Server

app = Server()

@app.call("measure_boot_i386")
def measure_boot_i386():
    """Measure i386 MINIX boot timeline"""
    container = "minix-rc6-i386"

    measurements = {
        'timestamp': datetime.now().isoformat(),
        'arch': 'i386',
        'container': container,
        'phases': {}
    }

    # Phase 1: QEMU startup
    start = time.time()
    subprocess.run(["docker", "start", container], check=True)
    measurements['phases']['qemu_startup'] = time.time() - start

    # Phase 2: Wait for kernel messages
    for i in range(120):
        logs = subprocess.run(
            ["docker", "logs", "--tail=100", container],
            capture_output=True,
            text=True
        ).stdout

        if 'MINIX booting' in logs:
            measurements['phases']['kernel_detection'] = i
            break

        time.sleep(1)

    # Phase 3: Parse kernel init time (if available in logs)
    if 'kernel init' in logs.lower():
        measurements['phases']['kernel_init'] = extract_timing(logs)

    # Save measurement
    meas_dir = Path("/measurements/i386")
    meas_dir.mkdir(parents=True, exist_ok=True)

    with open(meas_dir / f"boot-{datetime.now().isoformat()}.json", 'w') as f:
        json.dump(measurements, f, indent=2)

    return measurements

@app.call("compare_boot_times")
def compare_boot_times():
    """Compare measured boot times against whitepaper estimates"""

    measurements = []
    for arch_dir in Path("/measurements").glob("*/boot-*.json"):
        with open(arch_dir) as f:
            measurements.append(json.load(f))

    # Whitepaper estimates
    estimates = {
        'i386': {'kernel_init': 35, 'total': 65},
        'arm': {'kernel_init': 28, 'total': 56}
    }

    comparison = {}
    for meas in measurements:
        arch = meas['arch']
        total = meas['phases'].get('kernel_init', 0)
        estimate = estimates.get(arch, {})

        comparison[arch] = {
            'measured': total,
            'estimated': estimate.get('total', 0),
            'error_percent': abs(total - estimate.get('total', 0)) / estimate.get('total', 1) * 100
        }

    return comparison

def extract_timing(logs):
    """Extract timing from kernel boot logs"""
    # Implementation depends on actual MINIX boot output format
    import re
    match = re.search(r'kernel.*init.*(\d+)ms', logs)
    return int(match.group(1)) if match else 0

# Standard MCP endpoint
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

## 8.2: Syscall Tracer MCP Server

**Purpose**: Real-time syscall frequency and latency measurement

```python
# Pseudocode for syscall tracing
@app.call("trace_syscalls")
def trace_syscalls(duration_seconds=60):
    """
    Trace syscalls in running MINIX instance
    Uses: ssh into MINIX, run strace on kernel processes
    """
    syscall_stats = {}

    # SSH into MINIX (port 2222)
    # Run: strace -c -p <pid>
    # Parse output, collect frequencies

    return syscall_stats

@app.call("measure_syscall_latency")
def measure_syscall_latency(syscall_type="getpid"):
    """
    Measure specific syscall latency
    syscall_type: int80h, sysenter, syscall (i386 only)
    """
    latencies = {
        'syscall': syscall_type,
        'samples': [],
        'min': 0,
        'max': 0,
        'mean': 0
    }

    # Implementation uses perf/performance counters
    # Or custom kernel module

    return latencies
```

## 8.3: Memory Monitor MCP Server

**Purpose**: Real-time memory access pattern monitoring

```python
@app.call("monitor_memory_access")
def monitor_memory_access():
    """Monitor page faults, TLB behavior during boot"""

    memory_stats = {
        'page_faults': 0,
        'tlb_misses': 0,
        'cache_misses': 0,
        'memory_bandwidth': 0
    }

    # Implementation:
    # - Use perf events (page-faults, cache-misses)
    # - Parse /proc/vmstat if available
    # - Correlate with execution timeline

    return memory_stats
```

================================================================================
PHASE 9: CLI INTEGRATION & AUTOMATION (2 Weeks)
================================================================================

## 9.1: Unified CLI Interface

**File**: `/home/eirikr/Playground/minix-analysis/cli/minix-analysis-cli.py`

```bash
#!/usr/bin/env python3

COMMANDS:

minix-analysis-cli launch --arch i386 --image-size 2GB
  → Start MINIX container with specified config

minix-analysis-cli measure --arch i386 --metric boot
  → Run boot profiler, collect measurements

minix-analysis-cli measure --arch i386 --metric syscalls --duration 60
  → Trace syscalls for 60 seconds

minix-analysis-cli compare --metric boot
  → Compare all measured boot times vs whitepaper estimates

minix-analysis-cli dashboard
  → Start real-time monitoring dashboard

minix-analysis-cli report --arch i386 --output html
  → Generate comprehensive report with charts
```

## 9.2: Automated Measurement Pipeline

```python
def automated_measurement_suite():
    """
    Run complete measurement battery:
    1. Boot profiling (i386 and ARM)
    2. Syscall tracing (i386)
    3. Context switch measurement
    4. TLB/cache behavior
    5. Generate comparison report
    """

    results = {
        'boot': measure_boot(),
        'syscalls': measure_syscalls(),
        'context_switch': measure_context_switch(),
        'memory': measure_memory_patterns(),
        'comparison': compare_all_against_whitepaper()
    }

    return results
```

================================================================================
PHASE 10: VALIDATION & PUBLICATION (2 Weeks)
================================================================================

## 10.1: Comprehensive Validation

```python
class WhitepaperValidator:
    def validate_claim(self, chapter, claim, measured_value):
        """
        Validate individual whitepaper claims
        Returns: verified, plausible, or needs_measurement
        """
        pass

    def generate_validation_table(self):
        """
        Generate table showing:
        - Claim from whitepaper
        - Measured value
        - Error percentage
        - Verification status
        """
        pass
```

## 10.2: Extended Whitepaper with Real Data

Create **Chapter 17: Real System Validation**
- Measured boot timelines (i386 and ARM)
- Actual syscall latencies
- Real context switch timings
- Memory access patterns
- Comparison vs. whitepaper estimates

## 10.3: Publication & Documentation

- ArXiv submission format
- Supplementary data repository
- Analysis tools package
- Docker compose setup for reproducibility

================================================================================
IMPLEMENTATION SCHEDULE
================================================================================

```
WEEK 1 (Phase 7): Docker/QEMU Infrastructure
├─ 7.1: Dockerfile creation (2 days)
├─ 7.2: Docker Compose orchestration (2 days)
├─ 7.3: Boot profiler CLI tool (2 days)
└─ 7.4: Testing and debugging (1 day)

WEEK 2-3 (Phase 8): MCP Server Development
├─ 8.1: Boot Profiler MCP (4 days)
├─ 8.2: Syscall Tracer MCP (4 days)
├─ 8.3: Memory Monitor MCP (4 days)
└─ 8.4: Integration testing (2 days)

WEEK 4-5 (Phase 9): CLI Integration
├─ 9.1: Unified CLI interface (3 days)
├─ 9.2: Automated pipeline (3 days)
├─ 9.3: Dashboard development (4 days)
└─ 9.4: Performance tuning (2 days)

WEEK 6-7 (Phase 10): Validation & Publication
├─ 10.1: Run full measurement suite (3 days)
├─ 10.2: Write Chapter 17 (validation data) (3 days)
├─ 10.3: Generate final reports (2 days)
└─ 10.4: ArXiv preparation (2 days)
```

**Total Timeline**: 7 weeks (iterative, with 2-3 week parallel overlap possible)

================================================================================
SUCCESS CRITERIA
================================================================================

**Phase 7**:
- [ ] Docker images build successfully
- [ ] MINIX boots in containers (both i386 and ARM)
- [ ] Boot profiler CLI produces timing measurements
- [ ] Measurements within ±20% of whitepaper estimates

**Phase 8**:
- [ ] MCP servers start and respond to commands
- [ ] Boot Profiler MCP measures within ±10% of CLI tool
- [ ] Syscall tracer captures real syscall frequencies
- [ ] Memory monitor detects page faults and TLB behavior

**Phase 9**:
- [ ] Unified CLI launches measurements with single command
- [ ] Automated pipeline completes in < 5 minutes
- [ ] Dashboard displays real-time boot progress
- [ ] Reports generate in multiple formats (JSON, HTML, PDF)

**Phase 10**:
- [ ] Validation table shows 85%+ of claims verified/plausible
- [ ] Chapter 17 with real data passes LaTeX compilation
- [ ] Extended whitepaper ready for ArXiv
- [ ] All source code and tools publicly available

================================================================================
RISK MITIGATION
================================================================================

**Risk 1**: QEMU/Docker/KVM nested virtualization not available
- **Mitigation**: Fall back to non-KVM QEMU (slower but functional)
- **Fallback**: Run QEMU on bare metal if available

**Risk 2**: MINIX ARM build not available for RC6
- **Mitigation**: Build ARM support from source or use latest version
- **Alternative**: Focus on i386 initially, ARM as Phase 8.2

**Risk 3**: MCP server development complexity
- **Mitigation**: Start with simple HTTP API, upgrade to full MCP later
- **Incremental**: Implement one MCP server at a time

**Risk 4**: Real system measurements don't match whitepaper
- **Mitigation**: Document discrepancies, explain in validation section
- **Opportunity**: Identify optimization opportunities from delta

================================================================================
DELIVERABLES SUMMARY
================================================================================

**Phase 7**: Docker/QEMU infrastructure
- Dockerfiles (i386, ARM)
- Docker Compose orchestration
- Boot profiler CLI tool
- 3-5 successful boot measurements

**Phase 8**: MCP Servers
- Boot Profiler MCP server
- Syscall Tracer MCP server
- Memory Monitor MCP server
- 3 MCP endpoints with working integration

**Phase 9**: CLI Integration
- Unified CLI with 10+ commands
- Automated measurement pipeline
- Real-time dashboard
- Report generation (JSON, HTML, PDF)

**Phase 10**: Validation & Publication
- Chapter 17 (Real System Validation)
- Comprehensive measurement database
- Whitepaper validation table (85%+ verified)
- ArXiv-ready extended whitepaper

