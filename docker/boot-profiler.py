#!/usr/bin/env python3
"""
Boot Profiler Tool for MINIX Analysis
Measures MINIX boot timeline from Docker/QEMU instances
"""

import subprocess
import time
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class BootProfiler:
    def __init__(self, container_name=None, arch="i386", timeout=120):
        self.container_name = container_name
        self.arch = arch
        self.timeout = timeout
        self.measurements = {}
        self.start_time = None
        self.boot_markers = {}

    def start_container(self):
        """Start MINIX Docker container"""
        if not self.container_name:
            print("ERROR: No container name specified")
            return False

        print(f"Starting container: {self.container_name}")
        self.start_time = time.time()

        try:
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False

            print("✓ Container started")
            return True
        except FileNotFoundError:
            print("ERROR: Docker not found. Please install Docker or use --no-container mode")
            return False
        except subprocess.TimeoutExpired:
            print("ERROR: Container start timeout")
            return False
        except Exception as e:
            print(f"ERROR: Failed to start container: {e}")
            return False

    def wait_for_boot_markers(self):
        """Monitor container logs for boot markers"""
        markers = {
            'multiboot_detected': (r'Booting.*multiboot|MINIX.*boot', 'Multiboot detected'),
            'kernel_starts': (r'Initializing.*kernel|MINIX 3', 'Kernel initialization'),
            'pre_init_phase': (r'pre_init|Virtual memory', 'pre_init() phase'),
            'kmain_phase': (r'kmain\(|Main boot hub', 'kmain() orchestration'),
            'cstart_phase': (r'cstart\(|CPU descriptor', 'cstart() CPU setup'),
            'process_init': (r'Process table|proc_init', 'Process initialization'),
            'memory_init': (r'memory_init|Memory allocator', 'Memory system init'),
            'system_init': (r'system_init|Exception handlers', 'System init'),
            'scheduler_ready': (r'Scheduler.*ready|Scheduling|Ready to run', 'Scheduler ready'),
            'shell_prompt': (r'[$#%>]|login:', 'Shell prompt'),
        }

        print("\nWaiting for boot markers (timeout: {}s)...".format(self.timeout))

        start_time = time.time()

        for i in range(self.timeout):
            try:
                if self.container_name:
                    # Container mode
                    result = subprocess.run(
                        ["docker", "logs", "--tail=200", self.container_name],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logs = result.stdout
                else:
                    # File mode - read from boot log
                    log_file = list(Path("/measurements").rglob("boot-*.log"))
                    if log_file:
                        with open(log_file[-1]) as f:
                            logs = f.read()
                    else:
                        logs = ""

                # Check for markers
                for marker_key, (pattern, description) in markers.items():
                    if marker_key not in self.boot_markers:
                        if re.search(pattern, logs, re.IGNORECASE | re.MULTILINE):
                            elapsed = time.time() - start_time
                            self.boot_markers[marker_key] = elapsed
                            print(f"✓ {description}: {elapsed:6.2f}s")

                # Exit if all markers found
                if len(self.boot_markers) >= 7:  # At least 7 markers expected
                    break

                time.sleep(1)

            except subprocess.TimeoutExpired:
                print("WARNING: Log retrieval timeout")
                continue
            except Exception as e:
                print(f"WARNING: {e}")
                continue

        elapsed = time.time() - start_time
        print(f"\nBoot detection complete: {elapsed:.2f}s")

        return len(self.boot_markers) >= 5  # Minimum markers for success

    def extract_kernel_metrics(self):
        """Extract additional kernel metrics from logs"""
        try:
            if self.container_name:
                result = subprocess.run(
                    ["docker", "logs", self.container_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                logs = result.stdout
            else:
                log_files = list(Path("/measurements").rglob("boot-*.log"))
                if not log_files:
                    return {}

                with open(log_files[-1]) as f:
                    logs = f.read()

            metrics = {}

            # Parse timing information from logs
            if 'kernel init' in logs.lower():
                match = re.search(r'kernel.*?init.*?(\d+)\s*ms', logs, re.IGNORECASE)
                if match:
                    metrics['kernel_init_ms'] = int(match.group(1))

            # Parse process count
            match = re.search(r'(\d+)\s*processes?', logs, re.IGNORECASE)
            if match:
                metrics['process_count'] = int(match.group(1))

            # Parse CPU info
            if 'CPU' in logs or 'cpu' in logs:
                match = re.search(r'CPU.*?(\d+)\s*MHz', logs, re.IGNORECASE)
                if match:
                    metrics['cpu_mhz'] = int(match.group(1))

            return metrics
        except Exception as e:
            print(f"WARNING: Could not extract metrics: {e}")
            return {}

    def generate_report(self):
        """Generate formatted boot timeline report"""
        print("\n" + "="*70)
        print(f"BOOT TIMELINE REPORT - {self.arch.upper()}")
        print("="*70)

        if not self.boot_markers:
            print("ERROR: No boot markers found")
            return {}

        # Sort by elapsed time
        sorted_markers = sorted(self.boot_markers.items(), key=lambda x: x[1])

        for marker_key, elapsed in sorted_markers:
            print(f"  {marker_key:<25} {elapsed:>8.2f}s")

        if sorted_markers:
            total_time = sorted_markers[-1][1]
            total_ms = int(total_time * 1000)
            print("-"*70)
            print(f"TOTAL BOOT TIME: {total_time:.2f}s ({total_ms}ms)")

        print("="*70)
        print()

        return dict(sorted_markers)

    def compare_with_whitepaper(self):
        """Compare measurements with whitepaper estimates"""
        estimates = {
            'i386': {'total': 65, 'kernel': 35},
            'arm': {'total': 56, 'kernel': 28},
        }

        if not self.boot_markers:
            return {}

        total_time = list(self.boot_markers.values())[-1] * 1000  # Convert to ms

        arch_estimate = estimates.get(self.arch, {})

        comparison = {
            'architecture': self.arch,
            'measured_ms': int(total_time),
            'estimated_ms': arch_estimate.get('total', 0),
        }

        if arch_estimate.get('total'):
            error = abs(total_time - arch_estimate['total']) / arch_estimate['total'] * 100
            comparison['error_percent'] = round(error, 1)
            comparison['status'] = 'VERIFIED' if error < 20 else 'NEEDS_VALIDATION'

        return comparison

    def save_json_report(self, output_dir="/measurements"):
        """Save measurement data as JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'architecture': self.arch,
            'container': self.container_name,
            'boot_markers': self.boot_markers,
            'whitepaper_comparison': self.compare_with_whitepaper(),
        }

        output_path = Path(output_dir) / self.arch
        output_path.mkdir(parents=True, exist_ok=True)

        report_file = output_path / f"boot-report-{datetime.now().isoformat()}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved: {report_file}")
        return report_file

def main():
    parser = argparse.ArgumentParser(
        description='MINIX Boot Profiler - Measure boot timeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Profile running Docker container
  %(prog)s --container minix-rc6-i386 --arch i386

  # Profile with custom timeout
  %(prog)s --container minix-rc6-i386 --timeout 180

  # Show help for more options
  %(prog)s --help
        """
    )

    parser.add_argument(
        '--container',
        help='Docker container name (if omitted, reads from boot log files)',
        default=None
    )
    parser.add_argument(
        '--arch',
        choices=['i386', 'arm'],
        default='i386',
        help='Architecture (default: i386)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=120,
        help='Boot timeout in seconds (default: 120)'
    )
    parser.add_argument(
        '--output-dir',
        default='/measurements',
        help='Output directory for reports (default: /measurements)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save JSON report'
    )

    args = parser.parse_args()

    profiler = BootProfiler(
        container_name=args.container,
        arch=args.arch,
        timeout=args.timeout
    )

    # If container specified, start it
    if args.container:
        if not profiler.start_container():
            sys.exit(1)

    # Wait for boot markers
    success = profiler.wait_for_boot_markers()

    # Generate report
    profiler.generate_report()

    # Compare with whitepaper
    comparison = profiler.compare_with_whitepaper()
    if comparison:
        print("\nWhitepaper Comparison:")
        print(f"  Measured: {comparison.get('measured_ms', 'N/A')}ms")
        print(f"  Estimated: {comparison.get('estimated_ms', 'N/A')}ms")
        if 'error_percent' in comparison:
            print(f"  Error: {comparison['error_percent']:.1f}%")
            print(f"  Status: {comparison.get('status', 'N/A')}")

    # Save report
    if not args.no_save:
        profiler.save_json_report(args.output_dir)

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
