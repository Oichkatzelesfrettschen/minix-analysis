# MINIX Analysis Tool Suite - PKGBUILDs

Arch/CachyOS package definitions for MINIX boot and kernel CPU analysis.

## Packages

### minix-analysis-tools (Meta-package)

**Purpose**: Unified tool suite aggregating disassemblers, debuggers, profilers

**Dependencies**:
- binutils (objdump, nm, readelf, addr2line)
- gdb (GNU debugger)
- graphviz (graph visualization)
- gnu-cflow (call flow analysis)
- cscope (source indexing)
- ctags (tag generation)
- python with pandas, matplotlib, networkx

**Installation**:
```bash
pikaur -U PKGBUILD-minix-analysis-tools
```

**Verification**:
```bash
objdump --version
gdb --version
cflow --help
python -c "import pandas; import matplotlib; import networkx"
```

### minix-boot-tracer

**Purpose**: Kernel-mode tracing for boot sequence and CPU transitions

**Key Tools**:
- perf (Linux performance profiling)
- trace-cmd (kernel event tracing)
- ftrace (function tracer)

**Requirements**: linux-tools, linux-headers

**Installation**:
```bash
pikaur -U PKGBUILD-minix-boot-tracer
```

**Usage**:
```bash
# Record boot sequence events
trace-cmd record -e sched_process_fork,sched_switch -o boot.dat <minix-binary>

# Decode trace
trace-cmd report -i boot.dat > boot_trace.txt
```

### minix-asm-analyzer

**Purpose**: Specialized assembly analysis for CPU state transitions

**Key Tools**:
- objdump with disassembly optimizations
- llvm-objdump (alternative)
- readelf (ELF analysis)
- addr2line (address-to-source mapping)
- capstone (disassembly library)

**Installation**:
```bash
pikaur -U PKGBUILD-minix-asm-analyzer
```

**Wrapper Commands**:
- minix-disasm <kernel> [section]
- minix-symbols <kernel>
- minix-addr2line <kernel> <address>

## Build All

```bash
# Build all three packages
cd $(dirname $(readlink -f "$0"))

pikaur -U PKGBUILD-minix-analysis-tools
pikaur -U PKGBUILD-minix-boot-tracer
pikaur -U PKGBUILD-minix-asm-analyzer

# Verify all installed
pacman -Q minix-analysis-tools minix-boot-tracer minix-asm-analyzer
```

## Manual Build (if pikaur unavailable)

```bash
# Using makepkg
cd $(dirname $(readlink -f "$0"))

for pkgbuild in PKGBUILD-*; do
  cp "$pkgbuild" PKGBUILD
  makepkg -si
done
```

## Tool Inventory

### Static Analysis (No Runtime Required)

Disassembly:
  objdump -d kernel.elf > kernel.asm
  llvm-objdump -d kernel.elf

Symbol Analysis:
  nm -C kernel.elf
  readelf -s kernel.elf
  readelf -h kernel.elf (headers)
  readelf -S kernel.elf (sections)

Call Graph:
  cflow --depth=10 kernel.c | dot -Tpng > call_graph.png

Address Mapping:
  addr2line -e kernel.elf 0x80000000

### Dynamic Analysis (Requires Runtime System)

Kernel Tracing:
  perf record -e cycles,instructions -o boot.perf <minix>
  perf report -i boot.perf

Function Tracing:
  trace-cmd record -e function -o trace.dat <minix>
  trace-cmd report -i trace.dat

Debugging:
  gdb -ex "file kernel.elf" -ex "target remote :1234"

## Usage Workflow

### Phase 1: Extract Kernel
```bash
# From MINIX source or binary
objdump -d minix > minix.asm
nm -C minix > minix.symbols
readelf -S minix > minix.sections
```

### Phase 2: Analyze Boot Entry
```bash
# Find kmain entry point
grep -n "<kmain>:" minix.asm

# Trace first 100 instructions from kmain
objdump -S minix | grep -A 100 "kmain"

# Resolve addresses
addr2line -e minix 0x80001000
```

### Phase 3: Build Call Graph
```bash
# Generate call flow from source
cflow -b minix/kernel/main.c | dot -Tpng > main_calls.png

# Or from object file (requires debug symbols)
objdump --debugging minix | grep DW_TAG_subprogram
```

### Phase 4: Context Switch Analysis
```bash
# Find context switch code
grep -n "switch_to_user\|restore\|SAVE_PROCESS_CTX" minix.asm

# Analyze privilege transitions
grep -n "iret\|sysret\|sysexit" minix.asm
```

### Phase 5: CPU Interaction Trace
```bash
# System call entry points
grep -n "ipc_entry_softint\|ipc_entry_sysenter\|ipc_entry_syscall" minix.asm

# Interrupt handlers
grep -n "hwint[0-9]" minix.asm

# Task switch
grep -n "TASK_SWITCH\|SAVE_PROCESS_CTX" minix.asm
```

## Critical Assembly Patterns

Boot Sequence (head.S):
  - Multiboot header (offset 0x0)
  - Stack setup
  - GDT/IDT loading
  - Protected mode enable
  - Jump to kmain

Kernel Entry (kmain):
  - Process table initialization
  - Memory setup
  - Interrupt vector configuration
  - First process scheduling

Context Switch (mpx.S):
  - SAVE_PROCESS_CTX macro
  - Register restoration
  - IRET/SYSRET to user mode

System Calls (ipc_entry_*):
  - INT 0x33 (legacy)
  - SYSENTER (Intel fast syscall)
  - SYSCALL (AMD fast syscall)

## Documentation

See tool-specific docs:
- minix-analysis-tools: /usr/share/doc/minix-analysis-tools/TOOLS.txt
- minix-boot-tracer: /usr/share/doc/minix-boot-tracer/BOOT-TRACING.txt
- minix-asm-analyzer: /usr/share/doc/minix-asm-analyzer/ASM-ANALYSIS-GUIDE.txt

## Verification Commands

```bash
# All tools present
minix-disasm --help 2>&1 | head -1
minix-symbols --help 2>&1 | head -1
minix-boot-trace --help 2>&1 | head -1

# Python libraries
python -c "import capstone; from capstone import x86; print('capstone OK')"
python -c "import pandas; import networkx; import matplotlib; print('analysis OK')"

# System tools
objdump --version | head -1
gdb --version | head -1
readelf --version | head -1
cflow --version | head -1
```

## Next Steps

1. Build all packages: `make -C .. all`
2. Install with pikaur: `pikaur -U PKGBUILD-*`
3. Start analysis: See DEEP-AUDIT-REPORT.md and MINIX-CPU-INTERFACE-ANALYSIS.md
4. Read assembly: `minix-disasm minix.elf | less`
5. Trace boot: Use pipeline scripts in modules/boot-sequence/pipeline/
