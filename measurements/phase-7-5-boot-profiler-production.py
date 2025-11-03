#!/usr/bin/env python3
"""
MINIX 3.4 IA-32 Boot Profiler - Production Implementation
Phase 7.5: Real MINIX boot timing and performance analysis

Measures boot time across:
- CPU models: 486, Pentium, Pentium Pro, Pentium II, Athlon
- vCPU counts: 1, 2, 4, 8
- Multiple samples per configuration for statistical analysis
"""

import subprocess
import time
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics


class MinixBootProfiler:
    """Production boot profiler for MINIX IA-32 systems"""

    # Boot markers with regex patterns
    BOOT_MARKERS = {
        'qemu_start': (r'QEMU|qemu', 'QEMU startup'),
        'kernel_start': (r'MINIX|Kernel|kernel', 'Kernel initialization'),
        'memory_init': (r'memory|Memory', 'Memory system init'),
        'scheduler': (r'scheduler|Scheduler|schedule', 'Scheduler ready'),
        'shell_prompt': (r'[$#>%]|login:|#', 'Shell prompt or login'),
    }

    def __init__(self, disk_image: str, iso_image: Optional[str] = None):
        """
        Initialize profiler with disk image

        Args:
            disk_image: Path to MINIX disk image (qcow2)
            iso_image: Path to MINIX ISO (for installation)
        """
        self.disk_image = Path(disk_image)
        self.iso_image = Path(iso_image) if iso_image else None
        self.results_dir = Path('measurements/phase-7-5-real')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Verify disk image exists
        if not self.disk_image.exists():
            raise FileNotFoundError(f"Disk image not found: {self.disk_image}")

        print(f"[*] MINIX Boot Profiler initialized")
        print(f"[*] Disk image: {self.disk_image}")
        print(f"[*] Results directory: {self.results_dir}")

    def boot_minix(self, cpu_model: str, num_cpus: int, timeout: int = 120) -> Tuple[str, float]:
        """
        Boot MINIX and capture serial output

        Args:
            cpu_model: CPU model (486, pentium, pentium2, pentium3, athlon, etc.)
            num_cpus: Number of vCPUs (1, 2, 4, 8)
            timeout: Boot timeout in seconds

        Returns:
            (log_output, boot_time_ms)
        """
        log_file = self.results_dir / f'boot-{cpu_model}-{num_cpus}cpu-{datetime.now().isoformat()}.log'

        # Build QEMU command
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

        print(f"\n[BOOT] {cpu_model:12} x{num_cpus} vCPU -> {log_file.name}")

        start_time = time.time()
        try:
            result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            print(f"[!] Timeout after {timeout}s")
            boot_time_ms = timeout * 1000
        else:
            boot_time_ms = (time.time() - start_time) * 1000

        # Read and parse log
        if log_file.exists():
            with open(log_file, 'r', errors='ignore') as f:
                log_output = f.read()

            # Analyze boot markers
            markers_found = self._analyze_markers(log_output)
            print(f"[+] Boot time: {boot_time_ms:.0f}ms | Markers: {markers_found}")

            return log_output, boot_time_ms
        else:
            print(f"[!] Log file not created")
            return "", boot_time_ms

    def _analyze_markers(self, log_output: str) -> int:
        """Count detected boot markers in output"""
        markers_found = 0
        for pattern, desc in self.BOOT_MARKERS.values():
            if re.search(pattern, log_output, re.IGNORECASE):
                markers_found += 1
        return markers_found

    def profile_single_cpu(self, samples: int = 5) -> Dict:
        """
        Profile single-CPU baseline (486)

        Args:
            samples: Number of boot samples to collect

        Returns:
            Dictionary with statistics
        """
        print(f"\n[PHASE 1] Single-CPU Baseline (486)")
        print(f"[*] Collecting {samples} samples...")

        boot_times = []
        for i in range(samples):
            log, boot_time = self.boot_minix('486', 1, timeout=120)
            boot_times.append(boot_time)

        # Calculate statistics
        stats = {
            'cpu_model': '486',
            'num_cpus': 1,
            'samples': samples,
            'boot_times_ms': boot_times,
            'mean_ms': statistics.mean(boot_times),
            'median_ms': statistics.median(boot_times),
            'stdev_ms': statistics.stdev(boot_times) if len(boot_times) > 1 else 0,
            'min_ms': min(boot_times),
            'max_ms': max(boot_times),
        }

        print(f"\n[RESULT] Single-CPU Baseline:")
        print(f"  Mean:   {stats['mean_ms']:.1f} ms")
        print(f"  Median: {stats['median_ms']:.1f} ms")
        print(f"  StDev:  {stats['stdev_ms']:.1f} ms")
        print(f"  Range:  {stats['min_ms']:.1f} - {stats['max_ms']:.1f} ms")

        return stats

    def profile_multiprocessor(self, cpu_models: List[str], cpu_counts: List[int], samples: int = 5) -> Dict:
        """
        Profile multi-processor scaling across CPU models

        Args:
            cpu_models: List of CPU models to test
            cpu_counts: List of vCPU counts to test
            samples: Samples per configuration

        Returns:
            Dictionary with all results
        """
        print(f"\n[PHASE 2] Multi-Processor Scaling Analysis")
        print(f"[*] Testing {len(cpu_models)} CPU models x {len(cpu_counts)} vCPU configs x {samples} samples")
        print(f"[*] Total boots: {len(cpu_models) * len(cpu_counts) * samples}")

        all_results = {}

        for cpu_model in cpu_models:
            all_results[cpu_model] = {}

            for num_cpus in cpu_counts:
                print(f"\n[{cpu_model:12} @ {num_cpus} vCPU]")
                boot_times = []

                for i in range(samples):
                    log, boot_time = self.boot_minix(cpu_model, num_cpus, timeout=120)
                    boot_times.append(boot_time)

                # Statistics
                stats = {
                    'mean_ms': statistics.mean(boot_times),
                    'median_ms': statistics.median(boot_times),
                    'stdev_ms': statistics.stdev(boot_times) if len(boot_times) > 1 else 0,
                    'min_ms': min(boot_times),
                    'max_ms': max(boot_times),
                    'samples': boot_times,
                }

                all_results[cpu_model][num_cpus] = stats

                print(f"  Mean: {stats['mean_ms']:.1f}ms | Median: {stats['median_ms']:.1f}ms | StDev: {stats['stdev_ms']:.1f}ms")

        return all_results

    def calculate_scaling_efficiency(self, results: Dict, baseline_cpus: int = 1) -> Dict:
        """
        Calculate scaling efficiency metrics

        Args:
            results: Results dictionary from profile_multiprocessor
            baseline_cpus: Reference CPU count for scaling calculations

        Returns:
            Scaling efficiency metrics
        """
        scaling = {}

        for cpu_model, configs in results.items():
            if baseline_cpus not in configs:
                continue

            baseline_time = configs[baseline_cpus]['mean_ms']
            scaling[cpu_model] = {}

            for num_cpus, stats in configs.items():
                current_time = stats['mean_ms']
                speedup = baseline_time / current_time
                efficiency = (speedup / num_cpus) * 100

                scaling[cpu_model][num_cpus] = {
                    'speedup': speedup,
                    'efficiency': efficiency,
                    'boot_time_ms': current_time,
                }

        return scaling

    def save_results(self, results: Dict, filename: str = 'phase-7-5-results.json'):
        """Save results to JSON"""
        output_file = self.results_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n[+] Results saved to {output_file}")
        return output_file

    def generate_report(self, results: Dict, scaling: Dict):
        """Generate human-readable report"""
        report_file = self.results_dir / 'BOOT_PROFILING_REPORT.txt'

        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MINIX 3.4 IA-32 Boot Profiling Report - Phase 7.5\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Report Generated: {datetime.now().isoformat()}\n")
            f.write(f"Disk Image: {self.disk_image}\n")
            f.write(f"Results Directory: {self.results_dir}\n\n")

            # Multi-processor results
            f.write("MULTI-PROCESSOR BOOT TIMES\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'CPU Model':<15} {'vCPUs':<8} {'Mean (ms)':<12} {'Median (ms)':<12} {'StDev':<10}\n")
            f.write("-" * 80 + "\n")

            for cpu_model, configs in sorted(results.items()):
                for num_cpus in sorted(configs.keys()):
                    stats = configs[num_cpus]
                    f.write(f"{cpu_model:<15} {num_cpus:<8} {stats['mean_ms']:<12.1f} {stats['median_ms']:<12.1f} {stats['stdev_ms']:<10.1f}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("SCALING EFFICIENCY\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'CPU Model':<15} {'vCPUs':<8} {'Speedup':<12} {'Efficiency (%)':<15}\n")
            f.write("-" * 80 + "\n")

            for cpu_model, configs in sorted(scaling.items()):
                for num_cpus in sorted(configs.keys()):
                    metrics = configs[num_cpus]
                    f.write(f"{cpu_model:<15} {num_cpus:<8} {metrics['speedup']:<12.2f} {metrics['efficiency']:<15.1f}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("VALIDATION AGAINST WHITEPAPER\n")
            f.write("-" * 80 + "\n")
            f.write("Expected baseline (i386/486): ~65ms\n")
            f.write("This report provides real system measurements for Chapter 17 validation.\n")

        print(f"\n[+] Report saved to {report_file}")
        return report_file


def main():
    """Main profiling workflow"""

    # Default parameters
    disk_image = '/tmp/minix_final.qcow2'

    # Check if disk exists
    if not Path(disk_image).exists():
        print(f"[!] Disk image not found: {disk_image}")
        print(f"[!] Please run installation first")
        sys.exit(1)

    # Initialize profiler
    profiler = MinixBootProfiler(disk_image)

    # Run profiling phases
    print("\n" + "=" * 80)
    print("MINIX 3.4 IA-32 Boot Profiling - Production Run")
    print("=" * 80)

    # Phase 1: Single-CPU baseline
    baseline_stats = profiler.profile_single_cpu(samples=5)

    # Phase 2: Multi-processor scaling
    cpu_models = ['486', 'pentium', 'pentium2', 'pentium3', 'athlon']
    cpu_counts = [1, 2, 4, 8]

    multi_results = profiler.profile_multiprocessor(cpu_models, cpu_counts, samples=3)

    # Phase 3: Calculate scaling efficiency
    scaling_metrics = profiler.calculate_scaling_efficiency(multi_results, baseline_cpus=1)

    # Phase 4: Save and report
    profiler.save_results({'baseline': baseline_stats, 'multiprocessor': multi_results}, 'phase-7-5-results.json')
    profiler.save_results(scaling_metrics, 'scaling-efficiency.json')
    profiler.generate_report(multi_results, scaling_metrics)

    print("\n" + "=" * 80)
    print("Profiling Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
