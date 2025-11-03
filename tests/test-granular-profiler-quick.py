#!/usr/bin/env python3
"""
QUICK VALIDATION TEST for Phase 7.5 Granular Profiler
Tests: Serial logging, perf integration, strace integration, JSON output

Usage:
  python3 tests/test-granular-profiler-quick.py

Expected:
  - Single 486 x1 boot with granular metrics
  - 30+ metrics collected (cycles, cache, branches, syscalls, serial)
  - JSON output valid and comprehensive
  - Test completes in ~3 minutes
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

def test_granular_profiler():
    """Run quick validation of granular profiler"""
    
    print("=" * 80)
    print("GRANULAR PROFILER VALIDATION TEST - 486 x1 vCPU (quick)")
    print("=" * 80)
    print(f"[*] Start time: {datetime.now().isoformat()}")
    print()
    
    # Verify ISO exists
    iso_path = Path('/home/eirikr/Playground/minix-analysis/docker/minix_R3.4.0rc6-d5e4fc0.iso')
    if not iso_path.exists():
        print(f"[!] ISO not found: {iso_path}")
        return False
    
    print(f"[+] ISO verified: {iso_path}")
    
    # Create test output directory
    test_dir = Path('/home/eirikr/Playground/minix-analysis/measurements/test-granular-quick')
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"[+] Test output directory: {test_dir}")
    print()
    
    # Import the granular profiler
    sys.path.insert(0, str(Path('/home/eirikr/Playground/minix-analysis')))
    from measurements.phase_7_5_boot_profiler_granular import MinixBootProfilerGranular
    
    try:
        # Initialize profiler
        profiler = MinixBootProfilerGranular(str(iso_path))
        print()
        
        # Run single boot with granular metrics
        print("[PHASE 1] Running 486 x1 vCPU boot with granular metrics...")
        print("[*] Collecting: CPU cycles, instructions, cache misses, branch misses, context switches, serial output, syscalls")
        print()
        
        metrics = profiler.boot_minix_with_metrics('486', 1, timeout=180)
        
        print()
        print("=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        
        # Validate metrics collected
        checks = {
            'wall_clock_ms': metrics.get('wall_clock_ms', 0) > 0,
            'cpu_cycles': metrics.get('cpu_cycles', 0) > 0,
            'instructions': metrics.get('instructions', 0) > 0,
            'cache_misses': metrics.get('cache_misses', 0) > 0,
            'branch_misses': metrics.get('branch_misses', 0) > 0,
            'context_switches': metrics.get('context_switches', 0) > 0,
            'boot_phases': len(metrics.get('boot_phases', {})) > 0,
            'syscall_summary': len(metrics.get('syscall_summary', {})) > 0,
            'serial_output': len(metrics.get('serial_output', [])) > 0,
        }
        
        print("\nMetric Collection Status:")
        for check, result in checks.items():
            status = "[+] PASS" if result else "[!] FAIL"
            print(f"  {status}: {check}")
            if check in metrics and result:
                value = metrics[check]
                if isinstance(value, dict):
                    print(f"           -> {len(value)} items")
                elif isinstance(value, list):
                    print(f"           -> {len(value)} items")
                else:
                    print(f"           -> {value:,}")
        
        # Overall pass/fail
        all_passed = all(checks.values())
        print()
        print("=" * 80)
        if all_passed:
            print("[+] VALIDATION PASSED: All metrics collected successfully")
        else:
            print("[!] VALIDATION FAILED: Some metrics missing")
        print("=" * 80)
        
        # Save metrics to JSON
        output_file = test_dir / 'test-results.json'
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        print(f"\n[+] Results saved: {output_file}")
        print(f"[*] End time: {datetime.now().isoformat()}")
        
        return all_passed
        
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_granular_profiler()
    sys.exit(0 if success else 1)
