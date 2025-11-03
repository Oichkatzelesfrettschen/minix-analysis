#!/usr/bin/env python3
"""
MINIX Analysis Unified CLI Interface
Provides comprehensive command-line interface for Docker/QEMU infrastructure,
MCP server integration, and automated measurements.

Main Commands:
  launch    - Start MINIX containers
  stop      - Stop MINIX containers
  measure   - Run boot/syscall/memory measurements
  status    - Show container and measurement status
  compare   - Compare measurements against whitepaper
  report    - Generate analysis reports
  dashboard - Start real-time monitoring dashboard
"""

import argparse
import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, Optional

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
MEASUREMENTS_DIR = PROJECT_ROOT / "measurements"
MCP_SERVERS = {
    'boot-profiler': 'http://localhost:5001',
    'syscall-tracer': 'http://localhost:5002',
    'memory-monitor': 'http://localhost:5003',
}

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_status(msg: str, status: str = "INFO"):
    """Print status message with color coding"""
    colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "ERROR": Colors.RED,
        "WARNING": Colors.YELLOW,
    }
    color = colors.get(status, Colors.RESET)
    print(f"{color}[{status}]{Colors.RESET} {msg}")


def check_docker():
    """Verify Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        print_status("Docker not found. Please install Docker.", "ERROR")
        return False
    except Exception as e:
        print_status(f"Docker check failed: {e}", "ERROR")
        return False


def check_docker_compose():
    """Verify Docker Compose is installed"""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        print_status("Docker Compose not found. Please install Docker Compose.", "ERROR")
        return False


# CLI Command Implementations

def cmd_launch(args):
    """Launch MINIX containers"""
    if not check_docker() or not check_docker_compose():
        sys.exit(1)
    
    arch = args.arch or "i386"
    detach = not args.foreground
    
    print_status(f"Launching {arch} MINIX containers...", "INFO")
    
    if arch == "both":
        services = ["minix-i386", "minix-arm"]
    elif arch == "arm":
        services = ["minix-arm"]
    else:
        services = ["minix-i386"]
    
    cmd = ["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up"]
    if detach:
        cmd.append("-d")
    cmd.extend(services)
    
    try:
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        if result.returncode == 0:
            print_status(f"Containers launched successfully", "SUCCESS")
            if detach:
                print_status(f"Monitor logs: docker-compose -f {DOCKER_COMPOSE_FILE} logs -f", "INFO")
        else:
            print_status("Container launch failed", "ERROR")
            sys.exit(1)
    except Exception as e:
        print_status(f"Error launching containers: {e}", "ERROR")
        sys.exit(1)


def cmd_stop(args):
    """Stop MINIX containers"""
    print_status("Stopping containers...", "INFO")
    
    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "down"],
            cwd=str(PROJECT_ROOT)
        )
        if result.returncode == 0:
            print_status("Containers stopped", "SUCCESS")
        else:
            print_status("Container stop failed", "ERROR")
            sys.exit(1)
    except Exception as e:
        print_status(f"Error stopping containers: {e}", "ERROR")
        sys.exit(1)


def cmd_measure(args):
    """Run measurements"""
    metric = args.metric or "boot"
    arch = args.arch or "i386"
    duration = args.duration or 60
    
    print_status(f"Running {metric} measurement for {arch}...", "INFO")
    
    if metric == "boot":
        cmd_measure_boot(arch)
    elif metric == "syscalls":
        cmd_measure_syscalls(arch, duration)
    elif metric == "memory":
        cmd_measure_memory(arch, duration)
    else:
        print_status(f"Unknown metric: {metric}", "ERROR")
        sys.exit(1)


def cmd_measure_boot(arch: str):
    """Measure boot time"""
    container_map = {"i386": "minix-rc6-i386", "arm": "minix-rc6-arm"}
    container = container_map.get(arch)
    
    if not container:
        print_status(f"Unknown architecture: {arch}", "ERROR")
        sys.exit(1)
    
    try:
        # Use boot profiler CLI directly
        boot_profiler = PROJECT_ROOT / "docker" / "boot-profiler.py"
        cmd = [
            "python3", str(boot_profiler),
            "--container", container,
            "--arch", arch,
            "--timeout", "120"
        ]
        
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        
        if result.returncode == 0:
            print_status(f"Boot measurement complete for {arch}", "SUCCESS")
        else:
            print_status(f"Boot measurement failed", "ERROR")
            sys.exit(1)
    except Exception as e:
        print_status(f"Error measuring boot: {e}", "ERROR")
        sys.exit(1)


def cmd_measure_syscalls(arch: str, duration: int):
    """Measure syscalls"""
    mcp_url = MCP_SERVERS.get('syscall-tracer')
    
    if not mcp_url:
        print_status("Syscall Tracer MCP server not configured", "ERROR")
        sys.exit(1)
    
    try:
        response = requests.post(
            f"{mcp_url}/trace-syscalls",
            json={"duration": duration, "save_report": True},
            timeout=duration + 30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Traced {data.get('total_syscalls', 0)} syscalls in {arch}", "SUCCESS")
        else:
            print_status(f"Syscall tracing failed: {response.text}", "ERROR")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_status(
            f"Cannot connect to Syscall Tracer MCP server ({mcp_url}). "
            "Ensure Docker Compose is running with MCP servers.",
            "ERROR"
        )
        sys.exit(1)
    except Exception as e:
        print_status(f"Error measuring syscalls: {e}", "ERROR")
        sys.exit(1)


def cmd_measure_memory(arch: str, duration: int):
    """Measure memory behavior"""
    mcp_url = MCP_SERVERS.get('memory-monitor')
    
    if not mcp_url:
        print_status("Memory Monitor MCP server not configured", "ERROR")
        sys.exit(1)
    
    try:
        response = requests.post(
            f"{mcp_url}/monitor-memory",
            json={"duration": duration, "save_report": True},
            timeout=duration + 30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Memory monitoring complete for {arch}: {data.get('total_events', 0)} events", "SUCCESS")
        else:
            print_status(f"Memory monitoring failed: {response.text}", "ERROR")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_status(
            f"Cannot connect to Memory Monitor MCP server ({mcp_url}). "
            "Ensure Docker Compose is running with MCP servers.",
            "ERROR"
        )
        sys.exit(1)
    except Exception as e:
        print_status(f"Error measuring memory: {e}", "ERROR")
        sys.exit(1)


def cmd_status(args):
    """Show status of containers and measurements"""
    print_status("Container Status:", "INFO")
    print()
    
    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "ps"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print_status(f"Error getting container status: {e}", "ERROR")
        return
    
    print_status("Measurement Status:", "INFO")
    print()
    
    # Count measurements
    for arch in ['i386', 'arm']:
        arch_dir = MEASUREMENTS_DIR / arch
        if arch_dir.exists():
            boot_measurements = list(arch_dir.glob("boot-*.json"))
            print(f"  {arch}: {len(boot_measurements)} boot measurements")


def cmd_compare(args):
    """Compare measurements against whitepaper"""
    metric = args.metric or "boot"
    arch = args.arch or "i386"
    
    print_status(f"Comparing {metric} measurements to whitepaper estimates...", "INFO")
    
    if metric == "boot":
        cmd_compare_boot(arch)
    else:
        print_status(f"Comparison not implemented for {metric}", "WARNING")


def cmd_compare_boot(arch: str):
    """Compare boot measurements to whitepaper"""
    mcp_url = MCP_SERVERS.get('boot-profiler')
    
    if not mcp_url:
        print_status("Boot Profiler MCP server not available", "WARNING")
        return
    
    try:
        # Get statistics
        response = requests.get(f"{mcp_url}/statistics/{arch}", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            
            print()
            print(f"{Colors.BOLD}Boot Time Comparison ({arch}){Colors.RESET}")
            print("-" * 60)
            print(f"  Whitepaper estimate:   {stats['whitepaper_estimate_ms']:.1f} ms")
            print(f"  Measured average:      {stats['mean_ms']:.1f} ms")
            print(f"  Error:                 {stats['whitepaper_error_percent']:.1f}%")
            print(f"  Samples:               {stats['sample_count']}")
            print()
            print(f"  Min:  {stats['min_ms']:.1f} ms")
            print(f"  Max:  {stats['max_ms']:.1f} ms")
            print(f"  Median: {stats['median_ms']:.1f} ms")
            print(f"  StdDev: {stats['stdev_ms']:.1f} ms")
            print()
            
            error = stats['whitepaper_error_percent']
            if error < 10:
                status = f"{Colors.GREEN}VERIFIED{Colors.RESET}"
            elif error < 20:
                status = f"{Colors.YELLOW}PLAUSIBLE{Colors.RESET}"
            else:
                status = f"{Colors.RED}NEEDS_VALIDATION{Colors.RESET}"
            
            print(f"  Status: {status}")
    except requests.exceptions.ConnectionError:
        print_status(
            "Cannot connect to Boot Profiler MCP server. "
            "Run: docker-compose up mcp-boot-profiler",
            "WARNING"
        )
    except Exception as e:
        print_status(f"Error comparing measurements: {e}", "WARNING")


def cmd_report(args):
    """Generate analysis report"""
    arch = args.arch or "i386"
    output_format = args.format or "text"
    
    print_status(f"Generating {output_format} report for {arch}...", "INFO")
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "architecture": arch,
        "measurements": {}
    }
    
    # Collect boot measurements
    arch_dir = MEASUREMENTS_DIR / arch
    if arch_dir.exists():
        boot_files = list(arch_dir.glob("boot-*.json"))
        report_data["measurements"]["boot_count"] = len(boot_files)
        
        if boot_files:
            with open(boot_files[-1]) as f:
                report_data["measurements"]["latest_boot"] = json.load(f)
    
    # Generate output
    if output_format == "text":
        print()
        print(Colors.BOLD + "MINIX Analysis Report" + Colors.RESET)
        print("=" * 60)
        print(json.dumps(report_data, indent=2))
    elif output_format == "json":
        report_file = MEASUREMENTS_DIR / f"report-{arch}-{datetime.now().isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print_status(f"Report saved to {report_file}", "SUCCESS")
    
    print()
    print_status("Report generation complete", "SUCCESS")


def cmd_dashboard(args):
    """Start real-time monitoring dashboard"""
    print_status("Dashboard functionality coming in Phase 9", "INFO")
    print_status("For now, use: docker-compose logs -f", "INFO")


# Main CLI setup
def main():
    parser = argparse.ArgumentParser(
        description="MINIX Analysis Suite - Docker/QEMU Integration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch i386 MINIX container
  minix-analysis-cli launch --arch i386

  # Stop containers
  minix-analysis-cli stop

  # Measure boot time
  minix-analysis-cli measure --metric boot --arch i386

  # Trace syscalls for 30 seconds
  minix-analysis-cli measure --metric syscalls --duration 30

  # Monitor memory behavior
  minix-analysis-cli measure --metric memory --duration 60

  # Compare measurements to whitepaper
  minix-analysis-cli compare --metric boot --arch i386

  # Generate report
  minix-analysis-cli report --arch i386 --format json

  # Show status
  minix-analysis-cli status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Launch command
    launch_parser = subparsers.add_parser('launch', help='Launch MINIX containers')
    launch_parser.add_argument('--arch', choices=['i386', 'arm', 'both'], default='i386',
                               help='Architecture to launch')
    launch_parser.add_argument('--foreground', action='store_true',
                               help='Run in foreground (not detached)')
    launch_parser.set_defaults(func=cmd_launch)
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop MINIX containers')
    stop_parser.set_defaults(func=cmd_stop)
    
    # Measure command
    measure_parser = subparsers.add_parser('measure', help='Run measurements')
    measure_parser.add_argument('--metric', choices=['boot', 'syscalls', 'memory'],
                                help='Measurement type')
    measure_parser.add_argument('--arch', choices=['i386', 'arm'], default='i386',
                                help='Architecture to measure')
    measure_parser.add_argument('--duration', type=int,
                                help='Duration in seconds (for syscalls/memory)')
    measure_parser.set_defaults(func=cmd_measure)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=cmd_status)
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare to whitepaper')
    compare_parser.add_argument('--metric', choices=['boot', 'syscalls', 'memory'],
                                help='Metric to compare')
    compare_parser.add_argument('--arch', choices=['i386', 'arm'], default='i386',
                                help='Architecture')
    compare_parser.set_defaults(func=cmd_compare)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--arch', choices=['i386', 'arm'], default='i386',
                               help='Architecture')
    report_parser.add_argument('--format', choices=['text', 'json', 'html'], default='text',
                               help='Report format')
    report_parser.set_defaults(func=cmd_report)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start monitoring dashboard')
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_status("Interrupted by user", "INFO")
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
