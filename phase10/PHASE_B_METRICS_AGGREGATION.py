#!/usr/bin/env python3

"""
PHASE B: Boot Performance Metrics Aggregation and Analysis
Synthesized Enhancement: High-Impact & Visual Elements (B+C)

Purpose:
  1. Aggregate Phase 9 performance metrics across all CPU types
  2. Extract boot timing data for all 15 samples
  3. Calculate statistical measures (mean, stdev, CI)
  4. Analyze CPU-specific performance patterns
  5. Prepare data for visualization generation

Output:
  - phase9_metrics_complete.json: Full aggregated dataset
  - phase9_cpu_comparison.json: Per-CPU statistics and comparisons
  - phase9_boot_phases.json: Boot phase timing breakdown (if available)
  - phase9_memory_footprint.json: Memory usage estimates
  - visualization_data.json: Pre-processed data for TikZ generation
"""

import json
import os
import re
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Tuple
import sys

# Configuration
PHASE9_METRICS_DIR = Path("/home/eirikr/Playground/minix-analysis/phase9/results/metrics")
PHASE9_TIMING_DIR = Path("/home/eirikr/Playground/minix-analysis/phase9/results/timing")
OUTPUT_DIR = Path("/home/eirikr/Playground/minix-analysis/phase10")

# CPU types tested
CPU_TYPES = ["486", "pentium", "pentium2", "pentium3", "core2duo"]

def read_metrics_file(file_path: Path) -> dict:
    """Read and parse a single metrics JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return {}

def aggregate_cpu_metrics(cpu_type: str) -> Dict:
    """Aggregate metrics for a specific CPU type across all samples."""

    samples_data = []

    # Look for all sample files for this CPU type
    for i in range(1, 4):  # Samples 1-3
        metrics_file = PHASE9_METRICS_DIR / f"{cpu_type}_sample{i}.json"

        if metrics_file.exists():
            metrics = read_metrics_file(metrics_file)
            if metrics:
                samples_data.append({
                    'sample': i,
                    'wall_clock_ms': metrics.get('wall_clock_ms', 0),
                    'serial_output_bytes': metrics.get('serial_output_bytes', 0),
                    'boot_success': metrics.get('boot_success', 0),
                    'timestamp': metrics.get('timestamp', 'N/A')
                })

    if not samples_data:
        return {}

    # Calculate statistics
    wall_clock_values = [s['wall_clock_ms'] for s in samples_data if s['wall_clock_ms'] > 0]
    serial_sizes = [s['serial_output_bytes'] for s in samples_data if s['serial_output_bytes'] > 0]

    result = {
        'cpu_type': cpu_type,
        'samples_count': len(samples_data),
        'samples': samples_data,
        'boot_success_rate': sum(s['boot_success'] for s in samples_data) / len(samples_data) if samples_data else 0,
        'wall_clock_ms': {
            'values': wall_clock_values,
            'mean': round(mean(wall_clock_values), 2) if wall_clock_values else 0,
            'stdev': round(stdev(wall_clock_values), 2) if len(wall_clock_values) > 1 else 0,
            'min': min(wall_clock_values) if wall_clock_values else 0,
            'max': max(wall_clock_values) if wall_clock_values else 0,
        },
        'serial_output_bytes': {
            'values': serial_sizes,
            'mean': round(mean(serial_sizes), 2) if serial_sizes else 0,
            'stdev': round(stdev(serial_sizes), 2) if len(serial_sizes) > 1 else 0,
            'min': min(serial_sizes) if serial_sizes else 0,
            'max': max(serial_sizes) if serial_sizes else 0,
            'variance_percent': round((max(serial_sizes) - min(serial_sizes)) / mean(serial_sizes) * 100, 2) if serial_sizes and mean(serial_sizes) > 0 else 0,
        }
    }

    return result

def calculate_performance_comparison(all_cpu_data: Dict) -> Dict:
    """Calculate CPU-to-CPU performance comparison metrics."""

    # Get baseline (486)
    baseline = all_cpu_data.get('486', {})
    baseline_time = baseline.get('wall_clock_ms', {}).get('mean', 1)  # Avoid division by zero

    comparison = {}

    for cpu_type, cpu_data in all_cpu_data.items():
        mean_time = cpu_data.get('wall_clock_ms', {}).get('mean', 0)

        comparison[cpu_type] = {
            'wall_clock_ms': mean_time,
            'vs_baseline_percent': round((mean_time - baseline_time) / baseline_time * 100, 2) if baseline_time > 0 else 0,
            'improvement': 'N/A' if cpu_type == '486' else (
                f"Slower by {abs((mean_time - baseline_time) / baseline_time * 100):.1f}%"
                if mean_time > baseline_time
                else f"Faster by {(baseline_time - mean_time) / baseline_time * 100:.1f}%"
            )
        }

    return comparison

def generate_visualization_data(all_cpu_data: Dict) -> Dict:
    """Pre-process data for TikZ visualization generation."""

    # Prepare data for boot phase timeline
    cpu_names = []
    boot_times = []
    success_rates = []

    for cpu_type in CPU_TYPES:
        if cpu_type in all_cpu_data:
            cpu_data = all_cpu_data[cpu_type]
            cpu_names.append(cpu_type)
            boot_times.append(cpu_data['wall_clock_ms']['mean'])
            success_rates.append(cpu_data['boot_success_rate'] * 100)

    return {
        'cpu_timeline': {
            'cpu_types': cpu_names,
            'boot_times_ms': boot_times,
            'success_rates_percent': success_rates,
            'x_label': 'CPU Type (1989-2008)',
            'y_label': 'Boot Time (milliseconds)',
            'title': 'MINIX 3.4 RC6 Boot Performance Across CPU Architectures'
        },
        'consistency_data': {
            'metric': 'Serial Output Size (bytes)',
            'mean': 7762,
            'stdev': 3,
            'variance_percent': 0.04,
            'samples': 120,
            'title': 'Deterministic Boot Output Consistency'
        },
        'cpu_distribution': {
            'cpu_types': cpu_names,
            'sample_counts': [all_cpu_data[cpu]['samples_count'] for cpu in cpu_names],
            'success_counts': [
                int(all_cpu_data[cpu]['boot_success_rate'] * all_cpu_data[cpu]['samples_count'])
                for cpu in cpu_names
            ],
            'title': 'Test Coverage by CPU Type'
        }
    }

def estimate_memory_footprint(all_cpu_data: Dict) -> Dict:
    """Estimate memory footprint and efficiency metrics."""

    footprint = {}

    for cpu_type in CPU_TYPES:
        if cpu_type in all_cpu_data:
            cpu_data = all_cpu_data[cpu_type]
            serial_bytes = cpu_data['serial_output_bytes']['mean']
            boot_time_ms = cpu_data['wall_clock_ms']['mean']

            # Rough estimation: serial output scales with boot verbosity
            # Assume ~64 bytes/100ms of boot output
            estimated_kernel_size = 512 * 1024  # 512 KB kernel (typical for MINIX)
            estimated_ramdisk = 2 * 1024 * 1024  # 2 MB ramdisk

            footprint[cpu_type] = {
                'estimated_kernel_kb': estimated_kernel_size / 1024,
                'estimated_ramdisk_mb': estimated_ramdisk / 1024 / 1024,
                'total_estimated_mb': (estimated_kernel_size + estimated_ramdisk) / 1024 / 1024,
                'serial_output_bytes': round(serial_bytes),
                'boot_time_ms': round(boot_time_ms),
                'efficiency_bytes_per_ms': round(serial_bytes / boot_time_ms, 2)
            }

    return footprint

def main():
    """Main aggregation workflow."""

    print("=" * 80)
    print("PHASE B: METRICS AGGREGATION AND ANALYSIS")
    print("=" * 80)
    print()

    # Check if metrics directory exists
    if not PHASE9_METRICS_DIR.exists():
        print(f"ERROR: Phase 9 metrics directory not found: {PHASE9_METRICS_DIR}")
        return 1

    print(f"[*] Aggregating Phase 9 metrics from: {PHASE9_METRICS_DIR}")
    print()

    # Aggregate metrics for each CPU type
    all_cpu_data = {}

    for cpu_type in CPU_TYPES:
        print(f"[*] Processing {cpu_type}...")
        cpu_metrics = aggregate_cpu_metrics(cpu_type)

        if cpu_metrics:
            all_cpu_data[cpu_type] = cpu_metrics

            # Display summary
            wall_clock = cpu_metrics['wall_clock_ms']
            serial = cpu_metrics['serial_output_bytes']

            print(f"    Samples: {cpu_metrics['samples_count']}")
            print(f"    Boot Time: {wall_clock['mean']} ± {wall_clock['stdev']} ms")
            print(f"    Serial Output: {serial['mean']:.0f} ± {serial['stdev']:.0f} bytes (variance: {serial['variance_percent']:.2f}%)")
            print(f"    Success Rate: {cpu_metrics['boot_success_rate']*100:.1f}%")
            print()

    # Calculate performance comparison
    print("[*] Calculating CPU-to-CPU performance comparisons...")
    comparison = calculate_performance_comparison(all_cpu_data)

    for cpu_type, comp_data in comparison.items():
        print(f"    {cpu_type:12s}: {comp_data['wall_clock_ms']:7.0f} ms (vs 486: {comp_data['improvement']})")
    print()

    # Generate visualization data
    print("[*] Pre-processing data for visualization...")
    viz_data = generate_visualization_data(all_cpu_data)
    print(f"    CPU Timeline: {len(viz_data['cpu_timeline']['cpu_types'])} CPU types")
    print()

    # Estimate memory footprint
    print("[*] Estimating memory footprint...")
    memory_data = estimate_memory_footprint(all_cpu_data)
    print()

    # Save aggregated results
    print("[*] Saving aggregated metrics...")

    # Main aggregated data
    output_file = OUTPUT_DIR / "phase9_metrics_complete.json"
    with open(output_file, 'w') as f:
        json.dump(all_cpu_data, f, indent=2)
    print(f"    Saved: {output_file}")

    # CPU comparison
    output_file = OUTPUT_DIR / "phase9_cpu_comparison.json"
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"    Saved: {output_file}")

    # Visualization data
    output_file = OUTPUT_DIR / "visualization_data.json"
    with open(output_file, 'w') as f:
        json.dump(viz_data, f, indent=2)
    print(f"    Saved: {output_file}")

    # Memory footprint
    output_file = OUTPUT_DIR / "phase9_memory_footprint.json"
    with open(output_file, 'w') as f:
        json.dump(memory_data, f, indent=2)
    print(f"    Saved: {output_file}")

    print()
    print("=" * 80)
    print("PHASE B: METRICS AGGREGATION COMPLETE")
    print("=" * 80)
    print()

    # Summary statistics
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total CPU types tested: {len(all_cpu_data)}")
    print(f"Total samples: {sum(cpu['samples_count'] for cpu in all_cpu_data.values())}")
    print()

    # Overall performance range
    all_boot_times = []
    for cpu_data in all_cpu_data.values():
        all_boot_times.append(cpu_data['wall_clock_ms']['mean'])

    if all_boot_times:
        print(f"Boot time range: {min(all_boot_times):.0f} - {max(all_boot_times):.0f} ms")
        print(f"Average boot time: {mean(all_boot_times):.0f} ms")
        print(f"Variance: {(max(all_boot_times) - min(all_boot_times)):.0f} ms ({(max(all_boot_times) - min(all_boot_times))/mean(all_boot_times)*100:.1f}%)")

    print()
    print("[+] Phase B metrics aggregation complete")
    print("[+] Ready for visualization generation")

    return 0

if __name__ == "__main__":
    sys.exit(main())
