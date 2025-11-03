#!/usr/bin/env python3
"""
MINIX 3.4 IA-32 Boot Profiler - Direct ISO Boot
Phase 7.5: Real MINIX boot timing from ISO bootable image

Boots directly from MINIX ISO without installation, measures boot time
across CPU models and vCPU counts. ISO boots to shell prompt allowing
for real system measurements.
"""

import subprocess
import time
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics


class MinixISOBootProfiler:
    """Production boot profiler for MINIX IA-32 ISO direct boot"""

    # Boot markers with regex patterns (detecting boot sequence on serial output)
    BOOT_MARKERS = {
        'qemu_start': (r'QEMU|qemu', 'QEMU startup'),
        'kernel_start': (r'MINIX|Kernel|kernel|Booting', 'Kernel initialization'),
        'memory_init': (r'memory|Memory|RAM', 'Memory system init'),
        'device_init': (r'device|Device|driver', 'Device initialization'),
        'shell_prompt': (r'[$#>%]|login:|#|\$', 'Shell prompt or login'),
    }

    def __init__(self, iso_image: str):
        """
        Initialize profiler with ISO image
        
        Args:
            iso_image: Path to MINIX bootable ISO
        """
        self.iso_image = Path(iso_image)
        self.results_dir = Path('measurements/phase-7-5-real')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Verify ISO exists
        if not self.iso_image.exists():
            raise FileNotFoundError(f"ISO image not found: {self.iso_image}")

        print(f"[*] MINIX ISO Boot Profiler initialized")
        print(f"[*] ISO image: {self.iso_image}")
        print(f"[*] Results directory: {self.results_dir}")

    def boot_minix_from_iso(self, cpu_model: str, num_cpus: int, timeout: int = 180) -> Tuple[str, float]:
        """
        Boot MINIX from ISO and capture serial output
        
        Args:
            cpu_model: CPU model (486, pentium, pentium2, pentium3, athlon, etc.)
            num_cpus: Number of vCPUs (1, 2, 4, 8)
            timeout: Boot timeout in seconds
            
        Returns:
            (log_output, boot_time_ms)
        """
        log_file = self.results_dir / f'iso-boot-{cpu_model}-{num_cpus}cpu-{datetime.now().isoformat()}.log'

        # Build QEMU command for ISO boot (no disk needed, just ISO)
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

        print(f"[BOOT] {cpu_model:12} x{num_cpus} vCPU (ISO) -> {log_file.name}")

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
            print(f"[+] Boot time: {boot_time_ms:.0f}ms | Markers: {markers_found} | Log size: {len(log_output)} bytes")

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
        Profile single-CPU baseline (486 IA-32)
        
        Args:
            samples: Number of boot samples to collect
            
        Returns:
            Dictionary with statistics
        """
        print(f"\n[PHASE 1] Single-CPU Baseline (486 IA-32)")
        print(f"[*] Collecting {samples} samples...")

        boot_times = []
        for i in range(samples):
            log, boot_time = self.boot_minix_from_iso('486', 1, timeout=180)
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

    def profile_multiprocessor(self, cpu_models: List[str], cpu_counts: List[int], samples: int = 3) -> Dict:
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
                    log, boot_time = self.boot_minix_from_iso(cpu_model, num_cpus, timeout=180)
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
        """Calculate scaling efficiency metrics"""
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

    def save_results(self, results: Dict, filename: str = 'phase-7-5-iso-results.json'):
        """Save results to JSON"""
        output_file = self.results_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n[+] Results saved to {output_file}")
        return output_file

    def generate_report(self, results: Dict, scaling: Dict):
        """Generate human-readable report"""
        report_file = self.results_dir / 'ISO_BOOT_PROFILING_REPORT.txt'

        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MINIX 3.4 IA-32 Boot Profiling Report - ISO Direct Boot - Phase 7.5\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Report Generated: {datetime.now().isoformat()}\n")
            f.write(f"ISO Image: {self.iso_image}\n")
            f.write(f"Results Directory: {self.results_dir}\n\n")

            f.write("METHOD: Direct ISO boot (no disk installation required)\n")
            f.write("This profile measures boot time from MINIX ISO bootable image.\n\n")

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
            f.write("SYSTEM INFORMATION\n")
            f.write("-" * 80 + "\n")
            f.write("Architecture: IA-32 (x86 32-bit)\n")
            f.write("Boot Source: MINIX 3.4.0 RC6 Bootable ISO\n")
            f.write("QEMU Emulation: qemu-system-i386\n")
            f.write("Host KVM: Enabled (when available)\n")

        print(f"\n[+] Report saved to {report_file}")
        return report_file


def main():
    """Main profiling workflow"""

    # ISO path
    iso_image = '/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso'

    # Check if ISO exists
    if not Path(iso_image).exists():
        print(f"[!] ISO image not found: {iso_image}")
        print(f"[!] Please ensure MINIX ISO is available")
        import sys
        sys.exit(1)

    # Initialize profiler
    profiler = MinixISOBootProfiler(iso_image)

    # Run profiling phases
    print("\n" + "=" * 80)
    print("MINIX 3.4 IA-32 Boot Profiling - ISO Direct Boot")
    print("=" * 80)

    # Phase 1: Single-CPU baseline
    baseline_stats = profiler.profile_single_cpu(samples=3)

    # Phase 2: Multi-processor scaling
    cpu_models = ['486', 'pentium', 'pentium2', 'pentium3', 'athlon']
    cpu_counts = [1, 2, 4, 8]

    multi_results = profiler.profile_multiprocessor(cpu_models, cpu_counts, samples=2)

    # Phase 3: Calculate scaling efficiency
    scaling_metrics = profiler.calculate_scaling_efficiency(multi_results, baseline_cpus=1)

    # Phase 4: Save and report
    profiler.save_results({'baseline': baseline_stats, 'multiprocessor': multi_results}, 'phase-7-5-iso-results.json')
    profiler.save_results(scaling_metrics, 'iso-scaling-efficiency.json')
    profiler.generate_report(multi_results, scaling_metrics)

    print("\n" + "=" * 80)
    print("Profiling Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
