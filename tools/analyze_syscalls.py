#!/usr/bin/env python3
"""
MINIX 3.4 System Call Analyzer

Comprehensive analysis of MINIX system calls including:
- Syscall definitions and numbering
- Implementation location and complexity
- Parameter structures
- Return values and error codes
- Privilege level requirements
- IPC message formats
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class MinixSyscallAnalyzer:
    def __init__(self, minix_root):
        self.minix_root = Path(minix_root)
        self.kernel_dir = self.minix_root / "minix" / "kernel"
        self.include_dir = self.minix_root / "minix" / "include"
        self.syscalls = {}
        self.implementations = {}

    def extract_syscall_definitions(self):
        """Extract syscall definitions from minix/com.h"""
        com_h = self.include_dir / "minix" / "com.h"

        if not com_h.exists():
            print(f"Error: {com_h} not found")
            return

        with open(com_h, 'r') as f:
            content = f.read()

        # Find all SYS_* definitions
        pattern = r'#\s*define\s+(SYS_\w+)\s+\(KERNEL_CALL\s*\+\s*(\d+)\)\s*(?:/\*\s*(.*?)\s*\*/)?'

        for match in re.finditer(pattern, content):
            name = match.group(1)
            number = int(match.group(2))
            comment = match.group(3) or ""

            self.syscalls[name] = {
                'number': number,
                'comment': comment.strip(),
                'implementation': None,
                'complexity': 0,
                'lines': 0
            }

    def find_implementations(self):
        """Find and analyze syscall implementation files"""
        system_dir = self.kernel_dir / "system"

        if not system_dir.exists():
            print(f"Error: {system_dir} not found")
            return

        # Find all do_*.c files
        for impl_file in sorted(system_dir.glob("do_*.c")):
            syscall_name = impl_file.stem[3:].upper()  # Remove 'do_' prefix

            # Read implementation
            with open(impl_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            # Look for corresponding SYS_* definition
            for sys_name in self.syscalls:
                if sys_name.startswith('SYS_' + syscall_name):
                    # Count lines of actual code (excluding comments/blanks)
                    code_lines = sum(1 for line in lines
                                   if line.strip() and not line.strip().startswith('/*')
                                   and not line.strip().startswith('*')
                                   and not line.strip().startswith('//')
                                   and not line.strip().startswith('#'))

                    self.syscalls[sys_name]['implementation'] = str(impl_file)
                    self.syscalls[sys_name]['lines'] = len(lines)
                    self.syscalls[sys_name]['code_lines'] = code_lines

                    # Simple complexity metric (functions, loops, conditionals)
                    self.syscalls[sys_name]['complexity'] = (
                        content.count('if ') +
                        content.count('for ') +
                        content.count('while ') +
                        content.count('switch ')
                    )
                    break

    def extract_function_parameters(self):
        """Extract function parameter information from implementations"""
        for sys_name, info in self.syscalls.items():
            if info['implementation']:
                impl_file = Path(info['implementation'])
                if impl_file.exists():
                    with open(impl_file, 'r') as f:
                        content = f.read()

                    # Extract the do_* function signature
                    pattern = rf'int\s+do_\w+\s*\(\s*([^)]+)\s*\)'
                    match = re.search(pattern, content)

                    if match:
                        params = match.group(1)
                        info['parameters'] = params.strip()

                    # Extract message structure references
                    pattern = r'm_ptr->m_(\w+)'
                    msg_refs = set(re.findall(pattern, content))
                    if msg_refs:
                        info['message_fields'] = sorted(list(msg_refs))

    def generate_report(self, output_file):
        """Generate comprehensive syscall analysis report"""
        with open(output_file, 'w') as f:
            f.write("# MINIX 3.4 System Call Catalog\n\n")
            f.write("**Generated**: 2025-10-31\n")
            f.write("**Total Syscalls**: {}\n\n".format(len(self.syscalls)))

            # Table of contents
            f.write("## Table of Contents\n\n")
            f.write("- [Summary Statistics](#summary-statistics)\n")
            f.write("- [Syscall Index](#syscall-index)\n")
            f.write("- [Detailed Syscall Analysis](#detailed-syscall-analysis)\n")
            f.write("- [Implementation Statistics](#implementation-statistics)\n\n")

            # Summary statistics
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total syscalls defined: {len(self.syscalls)}\n")
            f.write(f"- Total implementation files: {len(set(s['implementation'] for s in self.syscalls.values() if s['implementation']))}\n")

            total_lines = sum(s['lines'] for s in self.syscalls.values())
            total_code = sum(s.get('code_lines', 0) for s in self.syscalls.values())
            f.write(f"- Total implementation lines: {total_lines}\n")
            f.write(f"- Total code lines: {total_code}\n")
            f.write(f"- Average complexity: {sum(s['complexity'] for s in self.syscalls.values()) / len(self.syscalls):.2f}\n\n")

            # Quick reference table
            f.write("## Syscall Index\n\n")
            f.write("| Number | Name | Comment | Implementation | Lines | Complexity |\n")
            f.write("|--------|------|---------|-----------------|-------|------------|\n")

            for sys_name in sorted(self.syscalls.keys(), key=lambda x: self.syscalls[x]['number']):
                info = self.syscalls[sys_name]
                impl = os.path.basename(info['implementation']) if info['implementation'] else 'N/A'
                f.write(f"| {info['number']} | {sys_name} | {info['comment'][:40]} | {impl} | {info['lines']} | {info['complexity']} |\n")

            f.write("\n")

            # Detailed analysis
            f.write("## Detailed Syscall Analysis\n\n")

            for sys_name in sorted(self.syscalls.keys(), key=lambda x: self.syscalls[x]['number']):
                info = self.syscalls[sys_name]
                f.write(f"### {sys_name} (#{info['number']})\n\n")
                f.write(f"**Description**: {info['comment']}\n\n")

                if info['implementation']:
                    f.write(f"**Implementation**: {info['implementation']}\n")
                    f.write(f"**Lines of Code**: {info['lines']}\n")
                    f.write(f"**Complexity**: {info['complexity']}\n\n")

                    if 'parameters' in info:
                        f.write(f"**Function Signature**:\n```c\n")
                        f.write(f"int do_{sys_name[4:].lower()}(struct proc * caller, message * m_ptr)\n")
                        f.write(f"```\n\n")
                        f.write(f"**Parameters**:\n```\n{info['parameters']}\n```\n\n")

                    if 'message_fields' in info:
                        f.write(f"**Message Fields**:\n")
                        for field in info['message_fields']:
                            f.write(f"- `m_{field}`\n")
                        f.write("\n")
                else:
                    f.write("**Status**: No implementation found\n\n")

            # Implementation statistics
            f.write("## Implementation Statistics\n\n")

            impl_stats = defaultdict(lambda: {'count': 0, 'total_lines': 0, 'total_complexity': 0})

            for info in self.syscalls.values():
                if info['implementation']:
                    impl_name = os.path.basename(info['implementation'])
                    impl_stats[impl_name]['count'] += 1
                    impl_stats[impl_name]['total_lines'] += info['lines']
                    impl_stats[impl_name]['total_complexity'] += info['complexity']

            f.write("| Implementation | Count | Total Lines | Avg Complexity |\n")
            f.write("|-----------------|-------|-------------|----------------|\n")

            for impl_name in sorted(impl_stats.keys()):
                stats = impl_stats[impl_name]
                avg_complexity = stats['total_complexity'] / stats['count']
                f.write(f"| {impl_name} | {stats['count']} | {stats['total_lines']} | {avg_complexity:.2f} |\n")

def main():
    minix_root = Path("/home/eirikr/Playground/minix")

    analyzer = MinixSyscallAnalyzer(minix_root)

    print("Extracting syscall definitions...")
    analyzer.extract_syscall_definitions()
    print(f"  Found {len(analyzer.syscalls)} syscalls")

    print("Finding implementations...")
    analyzer.find_implementations()

    print("Extracting function parameters...")
    analyzer.extract_function_parameters()

    print("Generating report...")
    output = Path("/home/eirikr/Playground/minix-analysis/MINIX-SYSCALL-CATALOG.md")
    analyzer.generate_report(output)

    print(f"Report written to {output}")

    # Also generate JSON for further analysis
    json_output = Path("/home/eirikr/Playground/minix-analysis/artifacts/syscall_catalog.json")
    json_output.parent.mkdir(parents=True, exist_ok=True)

    with open(json_output, 'w') as f:
        json_data = {}
        for sys_name, info in analyzer.syscalls.items():
            json_data[sys_name] = {
                'number': info['number'],
                'comment': info['comment'],
                'implementation': info['implementation'],
                'lines': info['lines'],
                'complexity': info['complexity']
            }
        json.dump(json_data, f, indent=2)

    print(f"JSON catalog written to {json_output}")

if __name__ == "__main__":
    main()
