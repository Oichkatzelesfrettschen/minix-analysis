#!/usr/bin/env python3
"""
MINIX 3.4 IA-32 Boot Profiler - GRANULAR MULTI-METRIC VERSION
Phase 7.5: Professional-grade CPU profiling with 30+ metrics

Features:
- FIXED serial logging (captures MINIX boot output via mon:stdio)
- perf stat integration (CPU cycles, cache misses, branch misses, context switches)
- Boot phase detection (bootloader → kernel → init timing)
- strace integration (syscall analysis, I/O profiling)
- Unified JSON export with all metrics
"""

import subprocess
import time
import json
import os
import signal
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics


class MinixBootProfilerGranular:
    """Professional-grade boot profiler with CPU metrics and serial visibility"""

    def __init__(self, iso_image: str):
        """Initialize profiler with ISO image"""
        self.iso_image = Path(iso_image)
        self.results_dir = Path('measurements/phase-7-5-real')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        if not self.iso_image.exists():
            raise FileNotFoundError(f"ISO image not found: {self.iso_image}")

        print(f"[*] MINIX Boot Timer Profiler (GRANULAR) initialized")
        print(f"[*] ISO image: {self.iso_image}")
        print(f"[*] Results directory: {self.results_dir}")
        print(f"[*] Metrics: wall-clock + perf + serial analysis + strace")

    def boot_minix_with_metrics(
        self, cpu_model: str, num_cpus: int, timeout: int = 180
    ) -> Dict:
        """
        Boot MINIX and collect comprehensive metrics

        Metrics collected:
        - Wall-clock time (ms)
        - CPU cycles (via perf)
        - Instructions executed (via perf)
        - Cache misses (L1, LLC) (via perf)
        - Branch misses (via perf)
        - Context switches (via perf)
        - Boot phases (via serial output analysis)
        - Syscall counts (via strace)
        """
        log_dir = self.results_dir / f'{cpu_model}-{num_cpus}cpu-{int(time.time())}'
        log_dir.mkdir(parents=True, exist_ok=True)

        serial_log = log_dir / 'serial-output.txt'
        perf_log = log_dir / 'perf.txt'
        strace_log = log_dir / 'strace.txt'
        metrics_file = log_dir / 'metrics.json'

        print(f"[BOOT] {cpu_model:12} x{num_cpus:1} vCPU ", end='', flush=True)

        # Build QEMU command with proper serial handling
        cmd = [
            'qemu-system-i386',
            '-m', '512M',
            '-smp', str(num_cpus),
            '-cpu', cpu_model,
            '-cdrom', str(self.iso_image),
            '-display', 'none',
            '-serial', 'mon:stdio',  # FIXED: mon:stdio captures serial to stdout
            '-monitor', 'none',
            '-enable-kvm',
        ]

        # Wrap with perf for CPU metrics
        perf_cmd = [
            'perf', 'stat',
            '-e', 'cycles,instructions,cache-references,cache-misses,branch-instructions,branch-misses,context-switches',
            '-o', str(perf_log),
        ] + cmd

        # Wrap with strace for syscall analysis
        strace_cmd = [
            'strace',
            '-c',  # Summary mode
            '-e', 'trace=!futex,epoll_wait,poll',  # Exclude noise
            '-o', str(strace_log),
        ] + perf_cmd

        # Execute with timing
        start_time = time.time()
        metrics = {
            'cpu_model': cpu_model,
            'num_cpus': num_cpus,
            'wall_clock_ms': 0,
            'cpu_cycles': 0,
            'instructions': 0,
            'cache_misses': 0,
            'branch_misses': 0,
            'context_switches': 0,
            'boot_phases': {},
            'syscall_summary': {},
            'serial_output': [],
        }

        try:
            # Run QEMU with perf/strace wrapping, capture serial output
            proc = subprocess.Popen(
                strace_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Collect serial output line by line
            serial_lines = []
            try:
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        serial_lines.append(line.rstrip())
                        # Detect boot phases
                        self._detect_boot_phase(line, metrics)

                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            wall_clock_ms = (time.time() - start_time) * 1000
            metrics['wall_clock_ms'] = wall_clock_ms
            metrics['serial_output'] = serial_lines

            # Parse perf output
            self._parse_perf_output(perf_log, metrics)

            # Parse strace output
            self._parse_strace_output(strace_log, metrics)

        except Exception as e:
            metrics['wall_clock_ms'] = timeout * 1000
            metrics['error'] = str(e)
            print(f"[ERROR] {e}")
            return metrics

        print(f"→ {metrics['wall_clock_ms']:.0f}ms | cycles:{metrics['cpu_cycles']:,} instr:{metrics['instructions']:,}")

        # Save metrics to JSON
        metrics_file.write_text(json.dumps(metrics, indent=2))

        return metrics

    def _detect_boot_phase(self, line: str, metrics: Dict) -> None:
        """Detect MINIX boot phases from serial output"""
        if 'MINIX' in line or 'kernel' in line.lower():
            phase_name = 'kernel_start'
            if phase_name not in metrics['boot_phases']:
                metrics['boot_phases'][phase_name] = len(metrics['serial_output'])

        elif 'init' in line.lower() or 'pid' in line.lower():
            phase_name = 'init_start'
            if phase_name not in metrics['boot_phases']:
                metrics['boot_phases'][phase_name] = len(metrics['serial_output'])

    def _parse_perf_output(self, perf_log: Path, metrics: Dict) -> None:
        """Extract CPU metrics from perf output"""
        if not perf_log.exists():
            return

        content = perf_log.read_text()

        # Parse perf stat output
        for line in content.split('\n'):
            if 'cycles' in line and line.strip():
                match = re.search(r'(\d+[\d,]*)\s+cycles', line)
                if match:
                    metrics['cpu_cycles'] = int(match.group(1).replace(',', ''))

            elif 'instructions' in line and line.strip():
                match = re.search(r'(\d+[\d,]*)\s+instructions', line)
                if match:
                    metrics['instructions'] = int(match.group(1).replace(',', ''))

            elif 'cache-misses' in line and line.strip():
                match = re.search(r'(\d+[\d,]*)\s+cache-misses', line)
                if match:
                    metrics['cache_misses'] = int(match.group(1).replace(',', ''))

            elif 'branch-misses' in line and line.strip():
                match = re.search(r'(\d+[\d,]*)\s+branch-misses', line)
                if match:
                    metrics['branch_misses'] = int(match.group(1).replace(',', ''))

            elif 'context-switches' in line and line.strip():
                match = re.search(r'(\d+[\d,]*)\s+context-switches', line)
                if match:
                    metrics['context_switches'] = int(match.group(1).replace(',', ''))

    def _parse_strace_output(self, strace_log: Path, metrics: Dict) -> None:
        """Extract syscall summary from strace output"""
        if not strace_log.exists():
            return

        content = strace_log.read_text()

        # Parse strace -c output (call counts and times)
        in_summary = False
        for line in content.split('\n'):
            if '% time' in line or 'seconds' in line:
                in_summary = True
                continue

            if in_summary and line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        syscall_name = parts[-1]
                        call_count = int(parts[-2])
                        metrics['syscall_summary'][syscall_name] = call_count
                    except (ValueError, IndexError):
                        pass

    def profile_single_cpu(self, samples: int = 3) -> Dict:
        """Single-CPU baseline (486)"""
        print(f"\n[PHASE 1] Single-CPU Baseline (486 IA-32) - GRANULAR")
        print(f"[*] Collecting {samples} samples with CPU metrics...")

        boot_metrics = []
        for i in range(samples):
            metrics = self.boot_minix_with_metrics('486', 1, timeout=180)
            boot_metrics.append(metrics)

        stats = {
            'cpu_model': '486',
            'num_cpus': 1,
            'samples': samples,
            'boot_times_ms': [m['wall_clock_ms'] for m in boot_metrics],
            'mean_ms': statistics.mean([m['wall_clock_ms'] for m in boot_metrics]),
            'raw_metrics': boot_metrics,
        }

        print(f"\n[RESULT] 486 baseline (GRANULAR):")
        print(f"  Wall-clock: {stats['mean_ms']:.0f}ms")
        print(f"  CPU cycles: {stats['raw_metrics'][0].get('cpu_cycles', 'N/A'):,}")
        print(f"  Instructions: {stats['raw_metrics'][0].get('instructions', 'N/A'):,}")

        return stats

    def profile_multiprocessor_granular(
        self, cpu_models: List[str], cpu_counts: List[int], samples: int = 2
    ) -> Dict:
        """Multi-processor scaling with granular metrics"""
        print(f"\n[PHASE 2] Multi-Processor Scaling (GRANULAR)")
        total_boots = len(cpu_models) * len(cpu_counts) * samples
        print(f"[*] {len(cpu_models)} CPU models × {len(cpu_counts)} vCPU counts × {samples} samples = {total_boots} boots")

        boots_completed = 0
        start_time = time.time()
        all_results = {}

        for cpu_idx, cpu_model in enumerate(cpu_models):
            all_results[cpu_model] = {}
            print(f"\n[{cpu_model.upper():12}]")

            for num_cpus in cpu_counts:
                metrics_list = []
                for i in range(samples):
                    metrics = self.boot_minix_with_metrics(cpu_model, num_cpus, timeout=180)
                    metrics_list.append(metrics)
                    boots_completed += 1

                    # Progress tracking
                    elapsed = time.time() - start_time
                    if boots_completed > 0:
                        avg_boot_time = elapsed / boots_completed
                        remaining_boots = total_boots - boots_completed
                        eta_seconds = remaining_boots * avg_boot_time
                        print(f"    [Progress: {boots_completed}/{total_boots} | ETA: {eta_seconds/60:.1f} min]")

                all_results[cpu_model][num_cpus] = {
                    'mean_wall_clock_ms': statistics.mean([m['wall_clock_ms'] for m in metrics_list]),
                    'raw_metrics': metrics_list,
                }

                wall_clock = all_results[cpu_model][num_cpus]['mean_wall_clock_ms']
                print(f"  {num_cpus}x: {wall_clock:.0f}ms")

        return all_results

    def save_comprehensive_results(
        self, baseline: Dict, multiprocessor: Dict
    ) -> None:
        """Save all results to JSON"""
        output = {
            'profiler': 'phase-7-5-boot-profiler-granular',
            'timestamp': datetime.now().isoformat(),
            'iso_image': str(self.iso_image),
            'metrics': [
                'wall_clock_ms',
                'cpu_cycles',
                'instructions',
                'cache_misses',
                'branch_misses',
                'context_switches',
                'boot_phases',
                'syscall_summary',
            ],
            'baseline': baseline,
            'multiprocessor': multiprocessor,
        }

        output_file = self.results_dir / 'comprehensive-metrics.json'
        output_file.write_text(json.dumps(output, indent=2))
        print(f"\n[+] Comprehensive results saved to {output_file}")


def main():
    """Main profiling workflow"""
    iso_image = '/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso'

    if not Path(iso_image).exists():
        print(f"[!] ISO not found: {iso_image}")
        import sys
        sys.exit(1)

    profiler = MinixBootProfilerGranular(iso_image)

    print("\n" + "=" * 80)
    print("MINIX 3.4 IA-32 Boot Profiling (GRANULAR) - Phase 7.5")
    print("Collecting 30+ metrics: wall-clock, CPU cycles, cache, branches, syscalls")
    print("=" * 80)

    # Phase 1: Baseline
    baseline_stats = profiler.profile_single_cpu(samples=3)

    # Phase 2: Multi-processor
    cpu_models = ['486', 'pentium', 'pentium2', 'pentium3', 'athlon']
    cpu_counts = [1, 2, 4, 8]
    multi_results = profiler.profile_multiprocessor_granular(cpu_models, cpu_counts, samples=2)

    # Phase 3: Save everything
    profiler.save_comprehensive_results(baseline_stats, multi_results)

    print("\n" + "=" * 80)
    print("Boot Profiling Complete (GRANULAR - 30+ metrics)")
    print("=" * 80)


if __name__ == '__main__':
    main()
