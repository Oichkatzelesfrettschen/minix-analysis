#!/usr/bin/env python3
"""
MINIX Source Code Analyzer
Extracts structural data from MINIX source for diagram generation
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter

class MinixAnalyzer:
    def __init__(self, minix_root="/home/eirikr/Playground/minix"):
        self.minix_root = Path(minix_root)
        # MINIX has an extra 'minix' subdirectory
        self.kernel_dir = self.minix_root / "minix" / "kernel"
        self.servers_dir = self.minix_root / "minix" / "servers"
        self.include_dir = self.minix_root / "minix" / "include"

    def analyze_kernel_structure(self):
        """Extract kernel component structure"""
        structure = {
            "kernel_core": [],
            "system_calls": [],
            "arch_specific": {},
            "interrupt_handlers": [],
            "message_types": []
        }

        # Analyze kernel/system directory for system calls
        sys_dir = self.kernel_dir / "system"
        if sys_dir.exists():
            for f in sys_dir.glob("do_*.c"):
                syscall = f.stem.replace("do_", "")
                with open(f, 'r') as file:
                    lines = file.readlines()
                    # Extract function signature
                    for i, line in enumerate(lines):
                        if f"do_{syscall}" in line and "(" in line:
                            # Get full function signature
                            sig = line.strip()
                            j = i + 1
                            while j < len(lines) and "{" not in sig:
                                sig += " " + lines[j].strip()
                                j += 1
                            structure["system_calls"].append({
                                "name": syscall,
                                "file": str(f.relative_to(self.minix_root)),
                                "signature": sig,
                                "line_count": len(lines)
                            })
                            break

        # Analyze architecture-specific code
        arch_dir = self.kernel_dir / "arch" / "i386"
        if arch_dir.exists():
            for f in arch_dir.glob("*.c"):
                with open(f, 'r') as file:
                    content = file.read()
                    functions = re.findall(r'^\w+\s+(\w+)\s*\([^)]*\)\s*{', content, re.MULTILINE)
                    structure["arch_specific"][f.stem] = {
                        "functions": functions,
                        "lines": len(content.splitlines()),
                        "file": str(f.relative_to(self.minix_root))
                    }

        # Find interrupt handlers
        if (self.kernel_dir / "proc.c").exists():
            with open(self.kernel_dir / "proc.c", 'r') as f:
                content = f.read()
                # Look for interrupt handler patterns
                handlers = re.findall(r'(handle_\w+|do_\w+|irq_\w+)', content)
                structure["interrupt_handlers"] = list(set(handlers))

        # Extract message types from headers
        msg_header = self.include_dir / "minix" / "com.h"
        if msg_header.exists():
            with open(msg_header, 'r') as f:
                content = f.read()
                # Find message type definitions
                msg_types = re.findall(r'#define\s+(\w+)\s+\d+.*?/\*\s*(.*?)\s*\*/', content)
                structure["message_types"] = [
                    {"type": t[0], "description": t[1]} for t in msg_types
                ]

        return structure

    def analyze_process_table(self):
        """Extract process table structure from proc.h"""
        proc_data = {
            "process_states": [],
            "process_fields": [],
            "max_processes": None,
            "scheduling_queues": []
        }

        proc_h = self.kernel_dir / "proc.h"
        if proc_h.exists():
            with open(proc_h, 'r') as f:
                content = f.read()

                # Find process structure definition
                proc_struct = re.search(r'struct proc\s*{(.*?)};', content, re.DOTALL)
                if proc_struct:
                    fields = re.findall(r'^\s*(\w+)\s+(\w+)(?:\[.*?\])?;', proc_struct.group(1), re.MULTILINE)
                    proc_data["process_fields"] = [
                        {"type": f[0], "name": f[1]} for f in fields
                    ]

                # Find process states
                states = re.findall(r'#define\s+(RTS_\w+)\s+.*?/\*\s*(.*?)\s*\*/', content)
                proc_data["process_states"] = [
                    {"state": s[0], "description": s[1]} for s in states
                ]

                # Find max processes
                max_proc = re.search(r'#define\s+NR_PROCS\s+(\d+)', content)
                if max_proc:
                    proc_data["max_processes"] = int(max_proc.group(1))

                # Find scheduling queues
                queues = re.findall(r'#define\s+(.*?_Q)\s+(\d+)', content)
                proc_data["scheduling_queues"] = [
                    {"queue": q[0], "priority": int(q[1])} for q in queues
                ]

        return proc_data

    def analyze_memory_layout(self):
        """Extract memory layout from source"""
        memory_data = {
            "segments": [],
            "memory_regions": [],
            "page_size": None,
            "kernel_base": None
        }

        # Check memory-related headers
        const_h = self.include_dir / "minix" / "const.h"
        if const_h.exists():
            with open(const_h, 'r') as f:
                content = f.read()

                # Find page size
                page = re.search(r'#define\s+PAGE_SIZE\s+(\w+)', content)
                if page:
                    memory_data["page_size"] = page.group(1)

                # Find kernel base address
                kernel_base = re.search(r'#define\s+KERNEL_TEXT\s+(\w+)', content)
                if kernel_base:
                    memory_data["kernel_base"] = kernel_base.group(1)

        # Analyze VM server for memory regions
        vm_dir = self.servers_dir / "vm"
        if vm_dir.exists():
            for f in vm_dir.glob("*.c"):
                with open(f, 'r') as file:
                    content = file.read()
                    # Look for memory region definitions
                    regions = re.findall(r'(REGION_\w+|VR_\w+)', content)
                    memory_data["memory_regions"].extend(list(set(regions)))

        return memory_data

    def analyze_ipc_system(self):
        """Extract IPC system details"""
        ipc_data = {
            "message_size": None,
            "message_types": [],
            "ipc_functions": [],
            "endpoints": []
        }

        # Find message structure size
        ipc_h = self.include_dir / "minix" / "ipc.h"
        if ipc_h.exists():
            with open(ipc_h, 'r') as f:
                content = f.read()

                # Find message structure
                msg_struct = re.search(r'typedef struct\s*{(.*?)}\s*message;', content, re.DOTALL)
                if msg_struct:
                    # Count fields to estimate size
                    fields = re.findall(r'^\s*\w+\s+\w+', msg_struct.group(1), re.MULTILINE)
                    ipc_data["message_size"] = f"{len(fields) * 4} bytes (estimated)"

                # Find IPC function declarations
                funcs = re.findall(r'_PROTOTYPE\s*\(\s*(\w+),', content)
                ipc_data["ipc_functions"] = funcs

        # Find endpoint definitions
        com_h = self.include_dir / "minix" / "com.h"
        if com_h.exists():
            with open(com_h, 'r') as f:
                content = f.read()
                endpoints = re.findall(r'#define\s+(.*?_PROC_NR)\s+(\d+)', content)
                ipc_data["endpoints"] = [
                    {"name": e[0], "number": int(e[1])} for e in endpoints
                ]

        return ipc_data

    def analyze_boot_sequence(self):
        """Extract boot sequence from main.c and start.c"""
        boot_data = {
            "boot_stages": [],
            "initialization_functions": [],
            "boot_modules": []
        }

        # Analyze main.c
        main_c = self.kernel_dir / "main.c"
        if main_c.exists():
            with open(main_c, 'r') as f:
                content = f.read()

                # Find kmain function and trace calls
                kmain = re.search(r'void\s+kmain\s*\([^)]*\)\s*{(.*?)\n}', content, re.DOTALL)
                if kmain:
                    # Extract function calls in order
                    calls = re.findall(r'(\w+)\s*\([^)]*\);', kmain.group(1))
                    boot_data["boot_stages"] = [c for c in calls if not c.startswith("printf")]

                # Find initialization functions
                init_funcs = re.findall(r'PRIVATE\s+void\s+(\w+_init)\s*\(', content)
                boot_data["initialization_functions"] = init_funcs

        return boot_data

    def generate_statistics(self):
        """Generate overall statistics"""
        stats = {
            "kernel_files": 0,
            "kernel_lines": 0,
            "server_count": 0,
            "total_syscalls": 0,
            "driver_count": 0
        }

        # Count kernel files and lines
        for f in self.kernel_dir.rglob("*.c"):
            stats["kernel_files"] += 1
            with open(f, 'r') as file:
                stats["kernel_lines"] += len(file.readlines())

        # Count servers
        if self.servers_dir.exists():
            stats["server_count"] = len([d for d in self.servers_dir.iterdir() if d.is_dir()])

        # Count drivers
        drivers_dir = self.minix_root / "minix" / "drivers"
        if drivers_dir.exists():
            stats["driver_count"] = len([d for d in drivers_dir.iterdir() if d.is_dir()])

        # Count system calls
        sys_dir = self.kernel_dir / "system"
        if sys_dir.exists():
            stats["total_syscalls"] = len(list(sys_dir.glob("do_*.c")))

        return stats

    def export_all_data(self, output_dir="data"):
        """Export all analyzed data to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print("Analyzing kernel structure...")
        kernel_data = self.analyze_kernel_structure()
        with open(output_path / "kernel_structure.json", 'w') as f:
            json.dump(kernel_data, f, indent=2)

        print("Analyzing process table...")
        process_data = self.analyze_process_table()
        with open(output_path / "process_table.json", 'w') as f:
            json.dump(process_data, f, indent=2)

        print("Analyzing memory layout...")
        memory_data = self.analyze_memory_layout()
        with open(output_path / "memory_layout.json", 'w') as f:
            json.dump(memory_data, f, indent=2)

        print("Analyzing IPC system...")
        ipc_data = self.analyze_ipc_system()
        with open(output_path / "ipc_system.json", 'w') as f:
            json.dump(ipc_data, f, indent=2)

        print("Analyzing boot sequence...")
        boot_data = self.analyze_boot_sequence()
        with open(output_path / "boot_sequence.json", 'w') as f:
            json.dump(boot_data, f, indent=2)

        print("Generating statistics...")
        stats = self.generate_statistics()
        with open(output_path / "statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\nAll data exported to {output_path}/")
        return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze MINIX source code")
    parser.add_argument("--minix-root", default="/home/eirikr/Playground/minix",
                      help="Path to MINIX source tree")
    parser.add_argument("--output", default="data",
                      help="Output directory for data files")
    args = parser.parse_args()

    analyzer = MinixAnalyzer(args.minix_root)
    analyzer.export_all_data(args.output)