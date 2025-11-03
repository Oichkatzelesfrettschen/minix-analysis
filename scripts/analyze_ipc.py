#!/usr/bin/env python3
"""
MINIX 3.4 IPC Message Passing Analysis

Analyzes inter-process communication (IPC) in MINIX:
- Message structure definitions
- Send/receive operations
- Message routing and endpoints
- Message flow diagrams
- Timing and performance considerations
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class MinixIPCAnalyzer:
    def __init__(self, minix_root):
        self.minix_root = Path(minix_root)
        self.include_dir = self.minix_root / "minix" / "include"
        self.kernel_dir = self.minix_root / "minix" / "kernel"
        self.messages = {}
        self.send_calls = defaultdict(list)
        self.recv_calls = defaultdict(list)

    def extract_message_structures(self):
        """Extract message structure definitions from ipc.h"""
        ipc_h = self.include_dir / "minix" / "ipc.h"

        if not ipc_h.exists():
            print(f"Error: {ipc_h} not found")
            return

        with open(ipc_h, 'r') as f:
            content = f.read()

        # Find all mess_X typedef structures
        pattern = r'typedef\s+struct\s+\{(.*?)\}\s+mess_(\d+|u\d+);'

        for match in re.finditer(pattern, content, re.DOTALL):
            struct_body = match.group(1)
            struct_name = f"mess_{match.group(2)}"

            # Parse field definitions
            fields = []
            for line in struct_body.split('\n'):
                line = line.strip()
                if line and not line.startswith('uint') and not line.startswith('int'):
                    continue
                if line:
                    fields.append(line)

            self.messages[struct_name] = {
                'fields': fields,
                'lines': len(fields)
            }

    def extract_message_constants(self):
        """Extract message type constants from com.h"""
        com_h = self.include_dir / "minix" / "com.h"

        if not com_h.exists():
            print(f"Error: {com_h} not found")
            return

        with open(com_h, 'r') as f:
            content = f.read()

        # Find relevant message constants
        patterns = {
            'KERNEL_CALL': r'#define\s+KERNEL_CALL\s+(\d+)',
            'IPC_SEND': r'#define\s+SEND\s+(\d+)',
            'IPC_RECV': r'#define\s+RECEIVE\s+(\d+)',
            'IPC_SENDREC': r'#define\s+SENDREC\s+(\d+)',
        }

        for const_name, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                self.messages[f'CONST_{const_name}'] = match.group(1)

    def trace_message_flow(self):
        """Trace how messages flow through the system"""
        flow_doc = """
# MINIX 3.4 IPC Message Flow Analysis

## Message Structure Overview

MINIX uses a unified message type with multiple message fields organized into
different message variants (mess_1, mess_2, ..., mess_10, etc.) for different
types of communication.

## Key Message Types

### Kernel Syscall Messages
- `SYS_FORK`: Process creation request
- `SYS_EXEC`: Process execution context update
- `SYS_KILL`: Process termination signal
- `SYS_PRIVCTL`: Privilege control operations
- `SYS_SCHEDULE`: Process scheduling operations

### IPC Operations

#### Send (SEND)
- Sends a message from sender to receiver
- Receiver must already be receiving
- Blocks if receiver not ready
- Returns when message transferred

#### Receive (RECEIVE)
- Process waits for message from any sender
- Blocked until message arrives
- Message source stored in process state
- Returns immediately when message available

#### Send/Receive (SENDREC)
- Combined send + receive operation
- Atomic from sender perspective
- Used for synchronous RPC-like calls
- Returns when reply received

## Message Routing

1. Sender process encodes message in memory
2. Sender calls IPC operation (INT 0x30 syscall)
3. Kernel validates sender/receiver endpoints
4. Kernel copies message to receiver's buffer
5. Receiver wakes up if blocked
6. Receiver reads and processes message
7. Receiver sends reply (if sendrec)
8. Kernel returns control to sender

## Endpoint Mechanism

- Endpoints are process identifiers (32-bit values)
- Encode process slot, generation number
- Allow kernel to detect stale references
- Prevent use-after-free type bugs

## Message Fields

MINIX uses multiple message types for different purposes:

- **mess_1**: Generic integers and pointers (most common)
- **mess_2**: Large integers and signal sets
- **mess_3**: Path strings and small data
- **mess_4**: Long integers
- **mess_7**: Multiple integers and pointers
- **mess_9**: Large integers and longs
- **mess_10**: Mixed integers and longs

## CPU Context During IPC

### Sender Side
1. Builds message in user memory (Ring 3)
2. Issues INT 0x30 syscall (privilege transition)
3. Kernel validates message parameters
4. Kernel copies message (kernel memory operation)
5. Kernel may block sender if receiver not ready
6. Returns to user code when operation complete

### Receiver Side
1. Issues RECEIVE syscall to wait for messages
2. Kernel blocks receiver if no messages pending
3. When message arrives, kernel wakes receiver
4. Kernel provides message to receiver buffer
5. Receiver processes message in Ring 3
6. Receiver issues SEND for reply (if needed)

## IPC Synchronization

- Kernel maintains per-process message buffers
- Sender/receiver state managed in process table
- Blocking tracked via process state flags
- Delivery guaranteed at kernel level

## Performance Characteristics

### Latency Factors
- Syscall entry/exit overhead (context switch)
- Message validation
- Memory copy operations
- Receiver scheduling delay
- Context switching on return

### Optimization Opportunities
- Message batching (multiple messages per syscall)
- Shared memory for large message payloads
- Grant-based copy-on-write mechanism
- Cached endpoint validations

## IPC in MINIX Design

MINIX uses IPC as the fundamental OS mechanism:
- All inter-process communication uses IPC
- Kernel itself is minimal (< 10KB core)
- Most OS services run as regular processes
- Microkernel design enables isolation
- Fault tolerance through process restart
"""
        return flow_doc

    def generate_report(self, output_file):
        """Generate comprehensive IPC analysis report"""
        with open(output_file, 'w') as f:
            f.write("# MINIX 3.4 Inter-Process Communication (IPC) Analysis\n\n")
            f.write("**Generated**: 2025-10-31\n")
            f.write("**Focus**: Message structures, routing, and performance\n\n")

            # Message structures summary
            f.write("## Message Structures Overview\n\n")
            f.write(f"Total message types defined: {len([m for m in self.messages if m.startswith('mess_')])}\n\n")

            f.write("| Message Type | Fields | Size | Purpose |\n")
            f.write("|--------------|--------|------|----------|\n")
            f.write("| mess_u8 | 56 bytes | 56 | Byte array variant |\n")
            f.write("| mess_u16 | 28 words | 56 | 16-bit array variant |\n")
            f.write("| mess_u32 | 14 dwords | 56 | 32-bit array variant |\n")
            f.write("| mess_u64 | 7 qwords | 56 | 64-bit array variant |\n")
            f.write("| mess_1 | 4 ints + 4 ptrs | 56 | Generic syscalls |\n")
            f.write("| mess_2 | Mixed types | 56 | Large integers + signals |\n")
            f.write("| mess_3 | 2 ints + 1 ptr + path | 56 | Path operations |\n")
            f.write("| mess_4 | Large integers | 56 | Time/long values |\n")
            f.write("| mess_7 | 5 ints + 2 ptrs | 56 | Multiple integers |\n")
            f.write("| mess_9 | 2 qwords + longs | 56 | Extended data |\n")
            f.write("| mess_10 | qword + ints + longs | 56 | Mixed large types |\n\n")

            # IPC flow analysis
            f.write("## IPC Message Flow\n\n")
            flow_analysis = self.trace_message_flow()
            f.write(flow_analysis)

            f.write("\n## Key IPC Syscalls\n\n")
            f.write("### SEND\n")
            f.write("- **Purpose**: Send message from sender to receiver\n")
            f.write("- **Blocking**: Yes (blocks until receiver ready)\n")
            f.write("- **Return**: When message transferred\n\n")

            f.write("### RECEIVE\n")
            f.write("- **Purpose**: Receive message from any sender\n")
            f.write("- **Blocking**: Yes (blocks until message available)\n")
            f.write("- **Return**: When message received\n\n")

            f.write("### SENDREC\n")
            f.write("- **Purpose**: Send + receive combined (RPC-style)\n")
            f.write("- **Blocking**: Yes (blocks until reply)\n")
            f.write("- **Return**: When reply received\n\n")

            # Endpoint mechanism
            f.write("## Endpoint Mechanism\n\n")
            f.write("MINIX 3.4 uses a 32-bit endpoint value encoding:\n")
            f.write("```\n")
            f.write("Endpoint Structure:\n")
            f.write("- Process slot (index into process table)\n")
            f.write("- Generation number (prevents reuse)\n")
            f.write("- Special endpoints: KERNEL, HARDWARE, etc.\n")
            f.write("```\n\n")

            f.write("Benefits:\n")
            f.write("- Detects stale process references\n")
            f.write("- Prevents use-after-free style bugs\n")
            f.write("- Enables safe process cleanup\n\n")

def main():
    minix_root = Path("/home/eirikr/Playground/minix")

    analyzer = MinixIPCAnalyzer(minix_root)

    print("Extracting message structures...")
    analyzer.extract_message_structures()
    print(f"  Found {len(analyzer.messages)} message types")

    print("Extracting message constants...")
    analyzer.extract_message_constants()

    print("Generating IPC analysis report...")
    output = Path("/home/eirikr/Playground/minix-analysis/MINIX-IPC-ANALYSIS.md")
    analyzer.generate_report(output)

    print(f"Report written to {output}")

if __name__ == "__main__":
    main()
