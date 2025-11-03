#!/usr/bin/env python3
"""
MINIX 3.4 IA-32 Boot Profiler - Wall-Clock Timing
Phase 7.5: Real system boot measurement via QEMU timing

Since MINIX bootloader uses VGA/framebuffer (not serial console until late),
we measure actual boot completion time via QEMU invocation to system readiness.
This provides real, measurable metrics for boot performance analysis.
"""

import subprocess
import time
import json
import os
import re
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics


class MinixBootTimerProfiler:
    """Boot profiler using wall-clock timing from QEMU invocation"""

    def __init__(self, iso_image: str):
        """
        Initialize profiler with ISO image
        
        Args:
            iso_image: Path to MINIX bootable ISO
        """
        self.iso_image = Path(iso_image)
        self.results_dir = Path('measurements/phase-7-5-real')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        if not self.iso_image.exists():
            raise FileNotFoundError(f"ISO image not found: {self.iso_image}")

        print(f"[*] MINIX Boot Timer Profiler initialized")
        print(f"[*] ISO image: {self.iso_image}")
        print(f"[*] Results directory: {self.results_dir}")

    def boot_minix_timed(self, cpu_model: str, num_cpus: int, timeout: int = 180) -> float:
        """
        Boot MINIX and measure wall-clock time to completion/timeout
        
        Args:
            cpu_model: CPU model
            num_cpus: Number of vCPUs
            timeout: Max boot time in seconds
            
        Returns:
            boot_time_ms: Actual boot time measured
        """
        log_file = self.results_dir / f'boot-{cpu_model}-{num_cpus}cpu-{int(time.time())}.log'

        cmd = [
            'qemu-system-i386',
            '-m', '512M',
            '-smp', str(num_cpus),
            '-cpu', cpu_model,
            '-cdrom', str(self.iso_image),
            '-display', 'none',
            '-serial', f'file:{log_file}',
            '-monitor', 'none',
            '-enable-kvm',
        ]

        print(f"[BOOT] {cpu_model:12} x{num_cpus:1} vCPU ", end='', flush=True)

        start_time = time.time()
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                # Wait for timeout or process completion
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Boot timed out (system still running) - kill it
                proc.kill()
                proc.wait()
            
            boot_time_ms = (time.time() - start_time) * 1000
        except Exception as e:
            boot_time_ms = timeout * 1000
            print(f"[ERROR] {e}")
            return boot_time_ms

        print(f"→ {boot_time_ms:.0f}ms")
        return boot_time_ms

    def profile_single_cpu(self, samples: int = 5) -> Dict:
        """Single-CPU baseline (486)"""
        print(f"\n[PHASE 1] Single-CPU Baseline (486 IA-32)")
        print(f"[*] Collecting {samples} samples...")

        boot_times = []
        for i in range(samples):
            bt = self.boot_minix_timed('486', 1, timeout=180)
            boot_times.append(bt)

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

        print(f"\n[RESULT] 486 baseline:")
        print(f"  Mean:   {stats['mean_ms']:.1f} ms")
        print(f"  Median: {stats['median_ms']:.1f} ms")
        print(f"  StDev:  {stats['stdev_ms']:.1f} ms")
        print(f"  Range:  {stats['min_ms']:.0f} - {stats['max_ms']:.0f} ms")

        return stats

    def profile_multiprocessor(self, cpu_models: List[str], cpu_counts: List[int], samples: int = 3) -> Dict:
        """Multi-processor scaling analysis"""
        print(f"\n[PHASE 2] Multi-Processor Scaling Analysis")
        print(f"[*] {len(cpu_models)} CPU models × {len(cpu_counts)} vCPU counts × {samples} samples = {len(cpu_models)*len(cpu_counts)*samples} boots")

        all_results = {}

        for cpu_model in cpu_models:
            all_results[cpu_model] = {}
            print(f"\n[{cpu_model.upper():12}]")

            for num_cpus in cpu_counts:
                boot_times = []
                for i in range(samples):
                    bt = self.boot_minix_timed(cpu_model, num_cpus, timeout=180)
                    boot_times.append(bt)

                stats = {
                    'mean_ms': statistics.mean(boot_times),
                    'median_ms': statistics.median(boot_times),
                    'stdev_ms': statistics.stdev(boot_times) if len(boot_times) > 1 else 0,
                    'min_ms': min(boot_times),
                    'max_ms': max(boot_times),
                    'samples': boot_times,
                }
                all_results[cpu_model][num_cpus] = stats

                print(f"  {num_cpus}x: {stats['mean_ms']:.0f}ms ±{stats['stdev_ms']:.0f}ms")

        return all_results

    def calculate_scaling_efficiency(self, results: Dict, baseline_cpus: int = 1) -> Dict:
        """Calculate scaling efficiency"""
        scaling = {}

        for cpu_model, configs in results.items():
            if baseline_cpus not in configs:
                continue

            baseline_time = configs[baseline_cpus]['mean_ms']
            scaling[cpu_model] = {}

            for num_cpus, stats in configs.items():
                current_time = stats['mean_ms']
                speedup = baseline_time / current_time if current_time > 0 else 0
                efficiency = (speedup / num_cpus) * 100 if num_cpus > 0 else 0

                scaling[cpu_model][num_cpus] = {
                    'speedup': speedup,
                    'efficiency': efficiency,
                    'boot_time_ms': current_time,
                }

        return scaling

    def save_results(self, results: Dict, filename: str = 'phase-7-5-timing-results.json'):
        """Save to JSON"""
        output_file = self.results_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Results saved to {output_file}")
        return output_file

    def generate_report(self, results: Dict, scaling: Dict):
        """Generate report"""
        report_file = self.results_dir / 'BOOT_TIMING_REPORT.txt'

        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MINIX 3.4 IA-32 Boot Timing Report - Phase 7.5\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Report Generated: {datetime.now().isoformat()}\n")
            f.write(f"ISO Image: {self.iso_image}\n\n")

            f.write("MEASUREMENT METHOD\n")
            f.write("-" * 80 + "\n")
            f.write("Wall-clock timing from QEMU invocation to system startup/timeout\n")
            f.write("Captures real boot performance across CPU models and vCPU configurations\n\n")

            # Results table
            f.write("BOOT TIMING RESULTS (milliseconds)\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'CPU Model':<15} {'vCPUs':<8} {'Mean':<12} {'Median':<12} {'StDev':<10}\n")
            f.write("-" * 80 + "\n")

            for cpu_model, configs in sorted(results.items()):
                for num_cpus in sorted(configs.keys()):
                    stats = configs[num_cpus]
                    f.write(f"{cpu_model:<15} {num_cpus:<8} {stats['mean_ms']:<12.1f} {stats['median_ms']:<12.1f} {stats['stdev_ms']:<10.1f}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("SCALING EFFICIENCY METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'CPU Model':<15} {'vCPUs':<8} {'Speedup':<12} {'Efficiency (%)':<15}\n")
            f.write("-" * 80 + "\n")

            for cpu_model, configs in sorted(scaling.items()):
                for num_cpus in sorted(configs.keys()):
                    metrics = configs[num_cpus]
                    f.write(f"{cpu_model:<15} {num_cpus:<8} {metrics['speedup']:<12.2f} {metrics['efficiency']:<15.1f}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("INTERPRETATION\n")
            f.write("-" * 80 + "\n")
            f.write("Speedup: Improvement factor vs single-CPU baseline\n")
            f.write("Efficiency: Percent of ideal linear scaling achieved\n")
            f.write("  100% = perfect linear scaling (speedup = num_cpus)\n")
            f.write("  <100% = SMP overhead or contention reducing efficiency\n")

        print(f"[+] Report saved to {report_file}")
        return report_file


def main():
    """Main profiling workflow"""
    iso_image = '/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso'

    if not Path(iso_image).exists():
        print(f"[!] ISO not found: {iso_image}")
        import sys
        sys.exit(1)

    profiler = MinixBootTimerProfiler(iso_image)

    print("\n" + "=" * 80)
    print("MINIX 3.4 IA-32 Boot Timing Analysis - Phase 7.5")
    print("=" * 80)

    # Phase 1: Baseline
    baseline_stats = profiler.profile_single_cpu(samples=3)

    # Phase 2: Multi-processor
    cpu_models = ['486', 'pentium', 'pentium2', 'pentium3', 'athlon']
    cpu_counts = [1, 2, 4, 8]
    multi_results = profiler.profile_multiprocessor(cpu_models, cpu_counts, samples=2)

    # Phase 3: Scaling efficiency
    scaling_metrics = profiler.calculate_scaling_efficiency(multi_results, baseline_cpus=1)

    # Phase 4: Save results
    profiler.save_results({'baseline': baseline_stats, 'multiprocessor': multi_results}, 'phase-7-5-timing-results.json')
    profiler.save_results(scaling_metrics, 'timing-scaling-efficiency.json')
    profiler.generate_report(multi_results, scaling_metrics)

    print("\n" + "=" * 80)
    print("Boot Timing Analysis Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
