# Profiling Enhancement Implementation Guide

**Source**: PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md
**Date Organized**: 2025-11-01
**Purpose**: Quick start guide for adding granular metrics to boot profiler
**Complexity Level**: ⭐⭐⭐⭐ (Advanced - Python + bash + regex)
**Estimated Time**: 6-8 hours for all improvements

---

## Quick Start: Adding Granular Metrics to Boot Profiler

**Estimated Implementation Time**: 6-8 hours for all improvements  
**Difficulty**: Intermediate (Python + bash + regex)  
**Impact**: 10x more measurement data (from wall-clock only to comprehensive profiling)

---

## QUICK REFERENCE: What to Implement

| Priority | Task | Time | Impact | Difficulty |
|----------|------|------|--------|------------|
| 1 | Fix serial logging (mon:stdio) | 30 min | BLOCKER | Easy |
| 2 | Add perf integration | 1 hr | HIGH | Easy |
| 3 | Fix/validate boot marker regex | 30 min | MEDIUM | Easy |
| 4 | Add strace syscall counting | 1 hr | MEDIUM | Easy |
| 5 | QEMU monitor protocol | 2 hrs | MEDIUM | Medium |
| 6 | Unified results JSON | 1 hr | HIGH | Easy |

---

## TASK 1: Fix Serial Logging (30 minutes)

**File**: `measurements/phase-7-5-boot-profiler-production.py`

**Problem**: Serial logs are 0 bytes because `-serial file:` doesn't work as expected with MINIX

**Solution**: Use `-serial mon:stdio` and capture subprocess output

### Step 1a: Find the QEMU command (line 73-86)

```python
cmd = [
    'qemu-system-i386',
    '-m', '512M',
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-hda', str(self.disk_image),
    '-display', 'none',
    '-serial', f'file:{log_file}',    # <-- BROKEN
    '-monitor', 'none',
    '-enable-kvm',
]
```

### Step 1b: Replace with stdout capture

```python
cmd = [
    'qemu-system-i386',
    '-m', '512M',
    '-smp', str(num_cpus),
    '-cpu', cpu_model,
    '-hda', str(self.disk_image),
    '-display', 'none',
    '-serial', 'mon:stdio',           # <-- FIXED: capture to stdout
    '-monitor', 'none',
    '-enable-kvm',
]
```

### Step 1c: Capture the output (around line 100-110)

**Before**:
```python
try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout + 10
    )

    boot_time = time.time() - boot_start

    # Parse log file for boot markers
    boot_markers = self._parse_boot_markers(boot_log_path)

    return True, boot_time, boot_markers
```

**After**:
```python
try:
    result = subprocess.run(
        cmd,
        capture_output=True,    # Captures stdout
        text=True,
        timeout=timeout + 10
    )

    boot_time = time.time() - boot_start
    
    # Write captured output to log file
    boot_log_path.write_text(result.stdout, encoding='utf-8')
    
    # Parse log file for boot markers
    boot_markers = self._parse_boot_markers(boot_log_path)

    return True, boot_time, boot_markers
```

### Step 1d: Verify it worked

```bash
# After running profiler, check log file size
ls -lh measurements/phase-7-5-real/boot-*.log

# Should show > 0 bytes (previously all 0 bytes)
# Example: -rw-r--r-- 1 user group 12K Nov  1 12:34 boot-486-1cpu-1234567890.log

# Check content
head -50 measurements/phase-7-5-real/boot-486-1cpu-*.log | less
```

---

## TASK 2: Add perf Integration (1 hour)

**File**: Modify `measurements/phase-7-5-boot-profiler-production.py` OR create new file `measurements/phase-7-5-perf-profiler.py`

**Goal**: Wrap QEMU with `perf stat` to collect CPU performance counters

### Step 2a: Add perf command wrapper (new method in class)

```python
def _build_perf_command(self, qemu_cmd: List[str], output_file: Path) -> List[str]:
    """Wrap QEMU command with perf monitoring"""
    
    perf_events = [
        'cycles',                # CPU cycles executed
        'instructions',          # Instructions retired
        'cache-misses',          # L1 + L2 + L3 cache misses
        'dTLB-misses',          # Data TLB misses
        'iTLB-misses',          # Instruction TLB misses
        'branch-misses',         # Branch prediction misses
        'context-switches',      # Context switches
        'page-faults',           # Page faults (major + minor)
        'stalled-cycles-backend' # Backend pipeline stalls
    ]
    
    perf_cmd = [
        'perf', 'stat',
        '-e', ','.join(perf_events),
        '-o', str(output_file),  # Output file
        '--append',              # Don't overwrite
    ]
    
    return perf_cmd + qemu_cmd
```

### Step 2b: Modify boot_minix() to use perf (around line 90)

**Before**:
```python
def boot_minix(self, cpu_model: str, num_cpus: int, timeout: int = 120):
    log_file = self.results_dir / f'boot-{cpu_model}-{num_cpus}cpu-{timestamp}.log'
    
    cmd = [
        'qemu-system-i386',
        # ... rest of command
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
```

**After**:
```python
def boot_minix(self, cpu_model: str, num_cpus: int, timeout: int = 120):
    timestamp = datetime.now().isoformat()
    log_file = self.results_dir / f'boot-{cpu_model}-{num_cpus}cpu-{timestamp}.log'
    perf_file = self.results_dir / f'perf-{cpu_model}-{num_cpus}cpu-{timestamp}.txt'
    
    cmd = [
        'qemu-system-i386',
        # ... rest of command
    ]
    
    # Wrap with perf monitoring
    cmd = self._build_perf_command(cmd, perf_file)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    
    # Write serial output
    log_file.write_text(result.stdout, encoding='utf-8')
    
    # Parse perf results
    perf_stats = self._parse_perf_output(perf_file)
    
    return log_output, boot_time_ms, perf_stats
```

### Step 2c: Add perf parser (new method)

```python
def _parse_perf_output(self, perf_file: Path) -> Dict[str, int]:
    """Parse perf stat output and extract event counts"""
    
    stats = {}
    
    if not perf_file.exists():
        print(f"[!] perf output file not found: {perf_file}")
        return stats
    
    try:
        with open(perf_file, 'r') as f:
            for line in f:
                # Format: "   1,234,567 cycles   #  12.3% of all cycles"
                parts = line.split()
                
                if len(parts) >= 2:
                    try:
                        # Extract numeric value (remove commas)
                        value_str = parts[0].replace(',', '')
                        value = int(value_str)
                        
                        # Extract event name
                        event = parts[1]
                        
                        # Store
                        stats[event] = value
                        
                    except (ValueError, IndexError):
                        # Skip lines that don't match pattern
                        pass
    
    except Exception as e:
        print(f"[!] Error parsing perf output: {e}")
    
    return stats
```

### Step 2d: Update results structure

Modify return value and storage to include perf stats:

```python
# In boot_minix() return statement
return {
    'log_output': log_output,
    'boot_time_ms': boot_time_ms,
    'boot_time_sec': boot_time_ms / 1000,
    'perf_stats': perf_stats,
    'perf_stats_human': self._format_perf_stats(perf_stats)
}

# Add formatting method
def _format_perf_stats(self, stats: Dict[str, int]) -> str:
    """Format perf stats for human readability"""
    lines = []
    for event, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {event:20} {count:15,}")
    return '\n'.join(lines)
```

---

## TASK 3: Fix Boot Marker Regex (30 minutes)

**File**: `phase-7-5-qemu-boot-profiler.py` (root directory)

**Problem**: Regex patterns defined but never validated against actual MINIX output

**Solution**: Test patterns, capture real output, refine patterns

### Step 3a: First, capture REAL output (one-time)

```bash
cd /home/eirikr/Playground/minix-analysis

# Run one boot with fixed serial logging
python3 measurements/phase-7-5-boot-profiler-production.py \
  --iso docker/minix_R3.4.0rc6-d5e4fc0.iso \
  --samples 1

# Check what we actually got
cat measurements/phase-7-5-real/boot-486-1cpu-*.log | head -100
```

### Step 3b: Update marker patterns based on real output

**Current patterns** (in `phase-7-5-qemu-boot-profiler.py`, line 37-49):

```python
self.marker_patterns = {
    'multiboot_detected': (r'Booting.*multiboot|MINIX.*boot|kernel.*load', 'Multiboot detected'),
    'kernel_starts': (r'Initializing.*kernel|MINIX 3.*boot|Protected mode', 'Kernel initialization'),
    'pre_init_phase': (r'pre_init|Virtual memory|Page tables', 'pre_init() phase'),
    'kmain_phase': (r'kmain\(|Main boot|Scheduling enabled', 'kmain() orchestration'),
    # ... etc
}
```

**Adjust patterns based on actual MINIX output**:

```python
# Example: if MINIX actually outputs "Boot: kernel loaded at 0x100000"
# Change pattern from 'kernel.*load' to 'Boot:.*kernel'

self.marker_patterns = {
    'multiboot': (r'QEMU|MINIX boot|multiboot', 'Bootloader entry'),
    'kernel_load': (r'kernel loaded|Loading kernel|protect mode', 'Kernel loading'),
    'boot_complete': (r'startup|Ready|login:|shell', 'Boot completion'),
    # ... etc
}
```

### Step 3c: Add validation test

Create small test script `test_boot_markers.py`:

```python
#!/usr/bin/env python3
import re
from pathlib import Path

# Get latest boot log
boot_logs = sorted(Path('measurements/phase-7-5-real').glob('boot-*.log'))
if not boot_logs:
    print("No boot logs found")
    exit(1)

latest_log = boot_logs[-1]
print(f"Testing patterns against: {latest_log.name}\n")

log_content = latest_log.read_text()
print(f"Log size: {len(log_content)} bytes\n")

# Define patterns to test
patterns = {
    'multiboot': r'QEMU|MINIX boot|multiboot',
    'kernel_load': r'kernel loaded|Loading kernel|protect mode',
    'boot_complete': r'startup|Ready|login:|shell',
}

# Test each pattern
print("Pattern test results:")
print("-" * 60)

for pattern_name, pattern in patterns.items():
    matches = re.findall(pattern, log_content, re.IGNORECASE)
    print(f"{pattern_name:20} {'MATCH' if matches else 'NO MATCH':8}  ({len(matches)} occurrences)")
    
    if matches:
        print(f"  Examples: {matches[:3]}")
    print()

# Show first 500 chars of log for inspection
print("\nFirst 500 characters of log:")
print("-" * 60)
print(log_content[:500])
```

Run it:
```bash
python3 test_boot_markers.py
```

Use output to refine patterns.

---

## TASK 4: Add strace Syscall Counting (1 hour)

**File**: Create new `measurements/phase-7-5-strace-profiler.py`

**Goal**: Capture syscall counts and per-syscall timing

### Step 4a: Create new profiler class

```python
#!/usr/bin/env python3
"""
MINIX Boot Profiler with strace Integration
Captures system call frequency and timing
"""

import subprocess
from pathlib import Path
from typing import Dict
import re
import json
from datetime import datetime


class MinixBootStraceProfiler:
    """Boot profiler with strace syscall analysis"""
    
    def __init__(self, iso_image: str, output_dir: str = "measurements"):
        self.iso_image = Path(iso_image)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify strace is available
        result = subprocess.run(['which', 'strace'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("strace not found. Install strace package.")
    
    def boot_with_strace(self, cpu_model: str, num_cpus: int, timeout: int = 180) -> Dict:
        """Boot MINIX with strace syscall monitoring"""
        
        timestamp = datetime.now().isoformat()
        strace_file = self.output_dir / f'strace-{cpu_model}-{num_cpus}cpu-{timestamp}.txt'
        serial_file = self.output_dir / f'serial-{cpu_model}-{num_cpus}cpu-{timestamp}.log'
        
        # QEMU command
        qemu_cmd = [
            'qemu-system-i386',
            '-m', '512M',
            '-smp', str(num_cpus),
            '-cpu', cpu_model,
            '-cdrom', str(self.iso_image),
            '-display', 'none',
            '-serial', 'mon:stdio',
            '-enable-kvm',
        ]
        
        # strace wrapper
        strace_cmd = [
            'strace',
            '-c',                                    # Summary mode
            '-o', str(strace_file),                 # Output file
            '-e', 'trace=open,read,write,mmap,fork,execve,send,recv',  # Filter syscalls
        ]
        
        full_cmd = strace_cmd + qemu_cmd
        
        print(f"[*] Booting {cpu_model} x{num_cpus} with strace monitoring...")
        
        start_time = subprocess.time.time()
        
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            boot_time_sec = subprocess.time.time() - start_time
            
            # Write serial output
            serial_file.write_text(result.stdout, encoding='utf-8')
            
        except subprocess.TimeoutExpired:
            boot_time_sec = timeout
            print(f"[!] Timeout after {timeout}s")
        
        # Parse strace results
        syscall_stats = self._parse_strace_summary(strace_file)
        
        return {
            'cpu_model': cpu_model,
            'num_cpus': num_cpus,
            'boot_time_sec': boot_time_sec,
            'syscall_stats': syscall_stats,
            'serial_log_lines': len(serial_file.read_text().splitlines()) if serial_file.exists() else 0
        }
    
    def _parse_strace_summary(self, strace_file: Path) -> Dict[str, Dict]:
        """Parse strace -c summary output"""
        
        stats = {}
        
        if not strace_file.exists():
            return stats
        
        with open(strace_file) as f:
            in_summary = False
            
            for line in f:
                # Look for summary table header
                if '% time' in line or '-----' in line:
                    in_summary = True
                    continue
                
                if not in_summary or not line.strip():
                    continue
                
                # Parse summary line
                # Format: "  35.44    0.100001      100001         1           mmap"
                parts = line.split()
                
                if len(parts) >= 5:
                    try:
                        percent_time = float(parts[0])
                        seconds = float(parts[1])
                        usecs_per_call = float(parts[2])
                        calls = int(parts[3])
                        syscall = parts[4]
                        
                        stats[syscall] = {
                            'percent_time': percent_time,
                            'total_time_sec': seconds,
                            'usecs_per_call': usecs_per_call,
                            'call_count': calls,
                        }
                    
                    except (ValueError, IndexError):
                        pass
        
        return stats


def main():
    profiler = MinixBootStraceProfiler(
        '/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso',
        'measurements/phase-7-5-strace'
    )
    
    # Run tests
    for cpu_model in ['486']:
        for num_cpus in [1]:
            result = profiler.boot_with_strace(cpu_model, num_cpus)
            
            print(f"\n{cpu_model} x{num_cpus} CPU Results:")
            print(f"  Boot time: {result['boot_time_sec']:.1f} seconds")
            print(f"  Syscall count: {len(result['syscall_stats'])}")
            print(f"  Top syscalls:")
            
            for syscall, stats in sorted(
                result['syscall_stats'].items(),
                key=lambda x: x[1]['call_count'],
                reverse=True
            )[:5]:
                print(f"    {syscall:15} {stats['call_count']:6} calls  {stats['percent_time']:5.1f}% time")


if __name__ == '__main__':
    main()
```

---

## TASK 5: Unified Results JSON (1 hour)

**File**: Modify main profiler to export unified JSON with all metrics

### Step 5a: Create results aggregator

```python
def aggregate_results(self) -> Dict:
    """Aggregate all measurements into single JSON"""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'measurements': []
    }
    
    # For each boot test, collect all metrics
    for cpu_model in ['486', 'pentium']:
        for num_cpus in [1, 2, 4]:
            measurement = {
                'cpu_model': cpu_model,
                'num_cpus': num_cpus,
                'boot_time_ms': self.boot_times[(cpu_model, num_cpus)],
                'perf_stats': self.perf_data.get((cpu_model, num_cpus), {}),
                'boot_markers': self.boot_markers.get((cpu_model, num_cpus), {}),
                'syscall_stats': self.syscall_data.get((cpu_model, num_cpus), {}),
            }
            
            results['measurements'].append(measurement)
    
    return results
```

### Step 5b: Save to JSON

```python
def save_results(self, results: Dict):
    """Save aggregated results to JSON file"""
    
    output_file = self.output_dir / f'measurements-{datetime.now().isoformat()}.json'
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"[+] Results saved to {output_file}")
    
    return output_file
```

---

## VALIDATION CHECKLIST

After implementing changes, verify:

- [ ] Serial logs now contain output (check file size > 0)
- [ ] perf stat output files created and parsed
- [ ] Boot marker regex matches appear in logs
- [ ] strace summary shows syscall counts
- [ ] Unified JSON output contains all metrics
- [ ] Results directory has proper timestamped files
- [ ] No subprocess timeouts during normal boot
- [ ] Boot time measurements remain consistent

---

## TESTING COMMANDS

```bash
# Test Serial Logging Fix
python3 measurements/phase-7-5-boot-profiler-production.py \
  --iso docker/minix_R3.4.0rc6-d5e4fc0.iso --samples 1

# Check output
ls -lh measurements/phase-7-5-real/boot-*.log | head
# Should show files with size > 0 bytes

# Test perf Integration
python3 measurements/phase-7-5-perf-profiler.py

# Check perf output
ls -lh measurements/phase-7-5-real/perf-*.txt | head
cat measurements/phase-7-5-real/perf-*.txt

# Test Boot Marker Regex
python3 test_boot_markers.py

# Verify Results JSON
cat measurements/phase-7-5-results/measurements-*.json | python3 -m json.tool
```

---

## TROUBLESHOOTING

### Problem: "perf not found"
**Solution**:
```bash
pacman -S linux-tools
# or: apt install linux-tools-common
```

### Problem: "strace not found"
**Solution**:
```bash
pacman -S strace
```

### Problem: Serial logs still empty after change
**Solution**:
- Add `print()` statements to debug
- Check if MINIX outputs anything at all (may hang at VGA)
- Try `-nographic` flag in addition to `-display none`
- Check QEMU version (use `-version`)

### Problem: perf permission denied
**Solution**:
```bash
# Either: enable unprivileged perf
echo 1 | sudo tee /proc/sys/kernel/perf_event_paranoid

# Or: use sudo
sudo python3 measurements/phase-7-5-perf-profiler.py
```

---

**Implementation Guide Complete - Ready for coding!**
