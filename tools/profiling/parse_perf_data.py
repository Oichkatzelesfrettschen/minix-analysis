#!/usr/bin/env python3
"""
Parse perf.data files into structured JSON for analysis.

Usage:
    python3 parse_perf_data.py boot.perf.data > boot.json
    python3 parse_perf_data.py boot.perf.data --output boot.json

Output format:
    {
      "metadata": {
        "perf_version": "6.17",
        "command": "qemu-system-i386",
        "total_samples": 12345
      },
      "stacks": [
        {
          "tid": 12345,
          "time": 123.456,
          "frames": [
            {"address": "0x7fff12345678", "symbol": "kvm_vcpu_ioctl"}
          ]
        }
      ],
      "hotspots": [
        {"function": "kvm_vcpu_ioctl", "samples": 500, "percentage": 4.05}
      ]
    }
"""

import subprocess
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

def parse_perf_data_to_json(perf_data_file):
    """Convert perf.data to structured JSON."""

    perf_data_file = Path(perf_data_file)
    if not perf_data_file.exists():
        raise FileNotFoundError(f"Perf data file not found: {perf_data_file}")

    # Run perf script to extract stack traces
    result = subprocess.run(
        ["perf", "script", "-i", str(perf_data_file)],
        capture_output=True,
        text=True,
        check=True
    )

    stacks = []
    current_stack = None

    for line in result.stdout.splitlines():
        if not line.strip() or line.startswith("#"):
            continue

        # Sample header: "qemu-system-i38 12345 123.456: cycles:"
        if re.match(r'^\S+\s+\d+', line):
            if current_stack:
                stacks.append(current_stack)

            parts = line.split()
            try:
                current_stack = {
                    "command": parts[0],
                    "tid": int(parts[1]),
                    "time": float(parts[2].rstrip(":")),
                    "frames": []
                }
            except (IndexError, ValueError):
                current_stack = None
        else:
            # Stack frame: "    7fff12345678 symbol_name (/path/to/lib.so)"
            match = re.match(r'\s+([0-9a-f]+)\s+(.+)', line)
            if match and current_stack:
                addr, symbol = match.groups()
                current_stack["frames"].append({
                    "address": addr,
                    "symbol": symbol.strip()
                })

    if current_stack:
        stacks.append(current_stack)

    # Analyze hotspots
    function_counts = defaultdict(int)

    for stack in stacks:
        for frame in stack.get("frames", []):
            symbol = frame["symbol"]
            # Extract function name (before '(')
            func = symbol.split("(")[0].strip()
            function_counts[func] += 1

    total = sum(function_counts.values())
    hotspots = []

    for func, count in sorted(
        function_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:100]:  # Top 100
        hotspots.append({
            "function": func,
            "sample_count": count,
            "percentage": (count / total) * 100 if total > 0 else 0
        })

    # Metadata
    commands = set(s["command"] for s in stacks)

    return {
        "metadata": {
            "perf_data_file": str(perf_data_file),
            "total_samples": len(stacks),
            "commands": list(commands)
        },
        "stacks": stacks[:1000],  # First 1000 stacks (full data can be huge)
        "hotspots": hotspots
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("perf_data", help="Path to perf.data file")
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")

    args = parser.parse_args()

    try:
        result = parse_perf_data_to_json(args.perf_data)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"JSON output written to: {args.output}", file=sys.stderr)
        else:
            print(json.dumps(result, indent=2))

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: perf script failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
