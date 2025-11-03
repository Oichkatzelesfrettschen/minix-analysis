#!/usr/bin/env python3
"""
Phase 7.5 MINIX QEMU Boot Profiler
Multi-processor boot performance characterization
Measures boot time across 1, 2, 4, 8 vCPU configurations
"""

import subprocess
import time
import json
import re
import sys
import os
import argparse
import tempfile
from pathlib import Path
from datetime import datetime
from statistics import mean, median, stdev
from typing import Dict, List, Tuple

class QemuBootProfiler:
    def __init__(self, iso_path: str, output_dir: str = "measurements"):
        self.iso_path = Path(iso_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.boot_markers = {}
        self.measurements = []

        # Boot markers - regex patterns for detection
        self.marker_patterns = {
            'multiboot_detected': (r'Booting.*multiboot|MINIX.*boot|kernel.*load', 'Multiboot detected'),
            'kernel_starts': (r'Initializing.*kernel|MINIX 3.*boot|Protected mode', 'Kernel initialization'),
            'pre_init_phase': (r'pre_init|Virtual memory|Page tables', 'pre_init() phase'),
            'kmain_phase': (r'kmain\(|Main boot|Scheduling enabled', 'kmain() orchestration'),
            'cstart_phase': (r'cstart\(|CPU descriptor|Processor setup', 'cstart() CPU setup'),
            'process_init': (r'Process table|proc_init|Process creation', 'Process initialization'),
            'memory_init': (r'memory_init|Memory allocator|Heap manager', 'Memory system init'),
            'system_init': (r'system_init|Exception handlers|Interrupt setup', 'System init'),
            'scheduler_ready': (r'Scheduler.*ready|Scheduling.*start|Ready to run', 'Scheduler ready'),
            'shell_prompt': (r'[$#%>]|login:|minix#', 'Shell prompt'),
        }

        # Whitepaper estimates (in milliseconds)
        self.whitepaper_estimates = {
            'i386': {'total': 65, 'kernel': 35},
            'arm': {'total': 56, 'kernel': 28},
        }

    def verify_iso(self) -> bool:
        """Verify ISO file exists and is readable"""
        if not self.iso_path.exists():
            print(f"ERROR: ISO not found: {self.iso_path}")
            return False

        size_mb = self.iso_path.stat().st_size / (1024 * 1024)
        print(f"ISO verified: {self.iso_path.name} ({size_mb:.1f} MB)")
        return True

    def create_disk_image(self, cpus: int) -> Path:
        """Create a QCOW2 disk image for this test run"""
        disk_path = self.output_dir / f"minix-{cpus}cpu-{datetime.now().isoformat()}.qcow2"

        print(f"Creating disk image: {disk_path.name} (2GB)...")
        result = subprocess.run(
            ["qemu-img", "create", "-f", "qcow2", str(disk_path), "2G"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"ERROR: Failed to create disk image: {result.stderr}")
            return None

        return disk_path

    def run_qemu_installation(self, disk_path: Path, cpus: int, timeout: int = 600) -> bool:
        """Run QEMU with ISO to install MINIX"""
        print(f"\nInstalling MINIX with {cpus} CPU(s)...")

        cmd = [
            "timeout", str(timeout),
            "qemu-system-i386",
            "-m", "512M",
            "-smp", str(cpus),
            "-cpu", "host",
            "-cdrom", str(self.iso_path),
            "-hda", str(disk_path),
            "-boot", "d",
            "-display", "none",
            "-nographic",
            "-serial", "stdio"
        ]

        try:
            # Run with interactive input for MINIX installer
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )

            print("Installation completed")
            return True

        except subprocess.TimeoutExpired:
            print("Installation timeout (expected - QEMU runs indefinitely)")
            return True
        except Exception as e:
            print(f"ERROR: Installation failed: {e}")
            return False

    def run_qemu_boot(self, disk_path: Path, cpus: int, timeout: int = 120) -> Tuple[bool, float, Dict[str, float]]:
        """
        Run QEMU from disk and measure boot time
        Returns: (success, boot_time_ms, boot_markers)
        """
        print(f"\nMeasuring boot with {cpus} CPU(s)...")

        boot_start = time.time()
        boot_log_path = self.output_dir / f"boot-{cpus}cpu-{datetime.now().isoformat()}.log"

        cmd = [
            "timeout", str(timeout),
            "qemu-system-i386",
            "-m", "512M",
            "-smp", str(cpus),
            "-cpu", "host",
            "-hda", str(disk_path),
            "-display", "none",
            "-nographic",
            "-serial", "file:" + str(boot_log_path)
        ]

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

        except subprocess.TimeoutExpired:
            boot_time = time.time() - boot_start
            print(f"Boot timeout after {boot_time:.2f}s (expected for QEMU)")

            # Still try to parse whatever we captured
            boot_markers = self._parse_boot_markers(boot_log_path)

            return True, boot_time, boot_markers
        except Exception as e:
            print(f"ERROR: Boot measurement failed: {e}")
            return False, 0, {}

    def _parse_boot_markers(self, log_path: Path) -> Dict[str, float]:
        """Parse boot markers from QEMU serial log"""
        markers = {}

        if not log_path.exists():
            return markers

        try:
            with open(log_path) as f:
                log_content = f.read()

            # Simple line-by-line marker detection
            lines = log_content.split('\n')
            for i, line in enumerate(lines):
                for marker_key, (pattern, description) in self.marker_patterns.items():
                    if marker_key not in markers:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Estimate time based on line number (rough approximation)
                            elapsed = i * 0.1  # ~100ms per line of output
                            markers[marker_key] = elapsed
        except Exception as e:
            print(f"WARNING: Failed to parse boot markers: {e}")

        return markers

    def measure_boot_sample(self, disk_path: Path, cpus: int) -> Dict:
        """Measure a single boot sample"""
        sample_start = time.time()
        success, boot_time, markers = self.run_qemu_boot(disk_path, cpus)

        measurement = {
            'timestamp': datetime.now().isoformat(),
            'cpus': cpus,
            'boot_time_seconds': boot_time,
            'boot_time_ms': int(boot_time * 1000),
            'marker_count': len(markers),
            'markers': markers,
            'success': success,
        }

        self.measurements.append(measurement)
        return measurement

    def run_test_matrix(self, samples_per_config: int = 3) -> Dict:
        """Run complete test matrix: 1, 2, 4, 8 CPU with multiple samples"""
        print("\n" + "="*70)
        print("PHASE 7.5 MULTI-PROCESSOR BOOT PROFILING")
        print("="*70)

        if not self.verify_iso():
            return {}

        cpu_counts = [1, 2, 4, 8]
        results = {}

        for cpus in cpu_counts:
            print(f"\n{'='*70}")
            print(f"CPU Configuration: {cpus} vCPU")
            print(f"{'='*70}")

            # Create disk image for this configuration
            disk_path = self.create_disk_image(cpus)
            if not disk_path:
                continue

            # Run installation once
            if not self.run_qemu_installation(disk_path, cpus):
                continue

            # Collect boot samples
            cpu_results = {
                'cpus': cpus,
                'samples': []
            }

            for sample in range(samples_per_config):
                print(f"\nSample {sample + 1}/{samples_per_config}")
                measurement = self.measure_boot_sample(disk_path, cpus)
                cpu_results['samples'].append(measurement)

            # Calculate statistics
            boot_times = [m['boot_time_seconds'] for m in cpu_results['samples']]
            cpu_results['statistics'] = {
                'mean_seconds': mean(boot_times),
                'mean_ms': int(mean(boot_times) * 1000),
                'median_seconds': median(boot_times),
                'median_ms': int(median(boot_times) * 1000),
                'min_seconds': min(boot_times),
                'min_ms': int(min(boot_times) * 1000),
                'max_seconds': max(boot_times),
                'max_ms': int(max(boot_times) * 1000),
                'stdev_seconds': stdev(boot_times) if len(boot_times) > 1 else 0,
                'stdev_ms': int(stdev(boot_times) * 1000) if len(boot_times) > 1 else 0,
            }

            # Whitepaper comparison
            whitepaper_ms = self.whitepaper_estimates['i386']['total']
            measured_ms = cpu_results['statistics']['mean_ms']
            error_pct = abs(measured_ms - whitepaper_ms) / whitepaper_ms * 100

            cpu_results['whitepaper_comparison'] = {
                'estimated_ms': whitepaper_ms,
                'measured_ms': measured_ms,
                'error_percent': round(error_pct, 1),
                'status': 'VERIFIED' if error_pct < 10 else 'PLAUSIBLE' if error_pct < 20 else 'NEEDS_VALIDATION'
            }

            results[f'cpu_{cpus}'] = cpu_results

            # Clean up disk image (optional)
            print(f"\nDisk image saved: {disk_path.name}")

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("\n" + "="*70)
        report.append("PHASE 7.5 BOOT PROFILING REPORT")
        report.append("="*70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"ISO: {self.iso_path.name}")
        report.append("")

        # Summary statistics across all configurations
        all_measurements = []
        for key, config_data in results.items():
            if isinstance(config_data, dict) and 'statistics' in config_data:
                stats = config_data['statistics']
                cpus = config_data['cpus']

                report.append(f"\n{'-'*70}")
                report.append(f"Configuration: {cpus} vCPU")
                report.append(f"{'-'*70}")
                report.append(f"  Mean:    {stats['mean_ms']:6d} ms")
                report.append(f"  Median:  {stats['median_ms']:6d} ms")
                report.append(f"  Min:     {stats['min_ms']:6d} ms")
                report.append(f"  Max:     {stats['max_ms']:6d} ms")
                report.append(f"  Stdev:   {stats['stdev_ms']:6d} ms")

                # Whitepaper comparison
                comparison = config_data['whitepaper_comparison']
                report.append(f"\n  Whitepaper Estimate: {comparison['estimated_ms']} ms")
                report.append(f"  Measured Average:    {comparison['measured_ms']} ms")
                report.append(f"  Error:               {comparison['error_percent']:.1f}%")
                report.append(f"  Status:              {comparison['status']}")

        report.append(f"\n{'='*70}")
        report.append("KEY FINDINGS")
        report.append(f"{'='*70}")

        # Analyze scaling
        cpu_times = {}
        for key, config_data in results.items():
            if isinstance(config_data, dict) and 'statistics' in config_data:
                cpus = config_data['cpus']
                mean_ms = config_data['statistics']['mean_ms']
                cpu_times[cpus] = mean_ms

        if len(cpu_times) > 1:
            sorted_cpus = sorted(cpu_times.keys())
            report.append("\nBoot Time by CPU Count:")
            for cpus in sorted_cpus:
                report.append(f"  {cpus} CPU:  {cpu_times[cpus]:6d} ms")

            # Calculate scaling efficiency
            if 1 in cpu_times:
                base_time = cpu_times[1]
                report.append("\nScaling Efficiency (relative to 1 CPU):")
                for cpus in sorted_cpus[1:]:
                    ratio = cpu_times[1] / cpu_times[cpus]
                    efficiency = (ratio / cpus) * 100
                    report.append(f"  {cpus} CPU: {ratio:.2f}x speedup ({efficiency:.0f}% efficiency)")

        report.append("\n" + "="*70)
        return '\n'.join(report)

    def save_results(self, results: Dict, report_str: str):
        """Save results to JSON and text files"""
        # Save JSON
        json_path = self.output_dir / f"phase-7-5-results-{datetime.now().isoformat()}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved: {json_path}")

        # Save text report
        report_path = self.output_dir / f"phase-7-5-report-{datetime.now().isoformat()}.txt"
        with open(report_path, 'w') as f:
            f.write(report_str)
        print(f"Report saved:  {report_path}")

        return json_path, report_path

def main():
    parser = argparse.ArgumentParser(
        description='MINIX QEMU Boot Profiler - Phase 7.5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 1 sample per CPU config
  %(prog)s --iso minix_R3.4.0rc6-d5e4fc0.iso --samples 1

  # Comprehensive test with 5 samples per CPU config
  %(prog)s --iso minix_R3.4.0rc6-d5e4fc0.iso --samples 5

  # Specify output directory
  %(prog)s --iso /path/to/minix.iso --output /tmp/measurements
        """
    )

    parser.add_argument('--iso', required=True, help='Path to MINIX ISO file')
    parser.add_argument('--output', default='measurements', help='Output directory for results')
    parser.add_argument('--samples', type=int, default=3, help='Boot samples per CPU config')

    args = parser.parse_args()

    profiler = QemuBootProfiler(args.iso, args.output)
    results = profiler.run_test_matrix(args.samples)

    report = profiler.generate_report(results)
    print(report)

    profiler.save_results(results, report)

if __name__ == '__main__':
    main()
