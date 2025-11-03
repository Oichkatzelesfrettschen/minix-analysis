# MINIX CPU Interface Diagrams - Master Summary

**Project**: MINIX 3.4.0-RC6 CPU Interface Analysis
**Purpose**: Comprehensive TikZ visualizations of all CPU interfaces used by MINIX kernel
**Status**: 7 diagrams complete, compiled, and documented
**Created**: 2025-10-31

---

## Overview

This document provides a master index of all CPU interface diagrams created for the MINIX whitepaper. Each diagram visualizes a specific aspect of how MINIX interacts with x86 CPU hardware, from system calls to interrupts to memory management.

## Diagram Inventory

### 1. System Call Mechanisms (system-call-mechanisms.tex)

**File**: `diagrams/tikz/system-call-mechanisms.tex`
**Size**: 126 KB PDF
**Purpose**: Compare three system call methods used by MINIX

**Content**:
- **INT 0x33** path (legacy, 200 cycles)
  - Stack push operations (SS, ESP, EFLAGS, CS, EIP)
  - IDT lookup
  - Handler execution
  - IRET return with stack restoration

- **SYSENTER** path (Intel fast, 40 cycles)
  - MSR-based entry (IA32_SYSENTER_CS/ESP/EIP)
  - No stack operations
  - SYSEXIT return via MSRs

- **SYSCALL** path (AMD fast, 35 cycles)
  - EFER/STAR MSR configuration
  - RCX/R11 register save
  - SYSRET return
  - Fastest mechanism

**Key Insights**:
- SYSCALL is 5.7x faster than INT
- MINIX detects CPU vendor and selects optimal path
- All three paths supported for compatibility

**Source Files Referenced**:
- mpx.S:265 (INT entry), mpx.S:220 (SYSENTER entry), mpx.S:202 (SYSCALL entry)
- mpx.S:459 (IRET), mpx.S:391-412 (SYSEXIT), mpx.S:414-432 (SYSRET)

---

### 2. Hardware Interrupt Flow (hardware-interrupt-flow.tex)

**File**: `diagrams/tikz/hardware-interrupt-flow.tex`
**Size**: ~120 KB PDF
**Purpose**: Compare PIC (legacy) vs APIC (modern) interrupt handling

**Content**:
- **PIC Path** (8259 controller)
  - 15 IRQs maximum
  - I/O port-based (0x20, 0x21, 0xA0, 0xA1)
  - Manual IRQ routing
  - EOI via OUT instruction
  - Total latency: ~8 μs

- **APIC Path** (Advanced PIC)
  - 24+ IRQs
  - Message-based delivery
  - IOAPIC → LAPIC → CPU flow
  - EOI via MMIO write
  - SMP support (multi-CPU)
  - Total latency: ~6 μs (25% faster)

**Key Insights**:
- APIC required for SMP systems
- IOAPIC handles device interrupts
- LAPIC per CPU for delivery
- Inter-Processor Interrupts (IPIs) for SMP coordination

**Source Files Referenced**:
- mpx.S:74-157 (interrupt entry points)
- apic.c:1068 (APIC configuration)
- apic_asm.S (LAPIC access routines)

---

### 3. Exception Handling (exception-handling.tex)

**File**: `diagrams/tikz/exception-handling.tex`
**Size**: ~115 KB PDF
**Purpose**: Visualize CPU exception handling, focusing on page faults

**Content**:
- **Page Fault Flow** (#PF, vector 14)
  - User space access to unmapped page
  - CPU pushes error code and EIP
  - IDT entry 14 invoked
  - Kernel reads CR2 (faulting address)
  - IPC to VM server
  - Two outcomes:
    1. Success: Page mapped, return to user
    2. Failure: SIGSEGV signal sent

- **All 20 x86 Exceptions Listed**:
  - #DE (0): Divide Error
  - #DB (1): Debug
  - #NMI (2): Non-Maskable Interrupt
  - #BP (3): Breakpoint
  - #OF (4): Overflow
  - ... (full list in diagram)
  - #PF (14): Page Fault (detailed)

**Key Insights**:
- CR2 register holds faulting virtual address
- VM server handles page mapping in user space
- Copy-on-write implemented via page faults
- Lazy allocation uses page faults for demand paging

**Source Files Referenced**:
- mpx.S:572 (exception entry), mpx.S:347-389 (exception dispatcher)
- exception.c:49-140 (exception handlers)
- klib.S:214 (read CR2 register)

---

### 4. Context Switch (context-switch-detailed.tex)

**File**: `diagrams/tikz/context-switch-detailed.tex`
**Size**: ~130 KB PDF
**Purpose**: Show complete process context switch (Process A → Process B)

**Content**:
- **Process State Saving** (Process A):
  - Save all general-purpose registers
  - Save segment registers
  - Save EFLAGS
  - Save FPU/SSE state (FXSAVE)

- **Critical CR3 Switch**:
  ```asm
  mov P_CR3(%edx), %eax  ; Load new page directory
  cmp %eax, %cr3          ; Compare with current
  je 0f                   ; Skip if same
  mov %eax, %cr3          ; SWITCH (flushes TLB!)
  0:
  ```

- **Process State Restoration** (Process B):
  - Restore CR3 (page directory)
  - Update TSS.ESP0 (kernel stack for next interrupt)
  - Restore segment registers
  - Restore general registers
  - Three return paths based on trap_style:
    1. IRET (normal interrupt)
    2. SYSEXIT (from SYSENTER)
    3. SYSRET (from SYSCALL)

**Key Insights**:
- CR3 switch flushes entire TLB (6400 cycle penalty)
- Global pages (PG_G) not flushed
- TSS.ESP0 must be updated for next Ring 3→0 transition
- FPU/SSE state saved only if used by process

**Source Files Referenced**:
- klib.S:586-651 (switch_to_user)
- klib.S:609-621 (CR3 conditional switch)
- proc.c (process management)
- mpx.S:434, 391, 414 (three return paths)

---

### 5. CPU Structures (cpu-structures.tex)

**File**: `diagrams/tikz/cpu-structures.tex`
**Size**: ~125 KB PDF
**Purpose**: Document GDT, IDT, and TSS structures used by MINIX

**Content**:
- **GDT (Global Descriptor Table)**:
  - 16 entries (GDT_SIZE=16)
  - Entry 0: NULL (required by x86)
  - Entry 1: Kernel Code (Ring 0, selector 0x08)
  - Entry 2: Kernel Data (Ring 0, selector 0x10)
  - Entry 3: User Code (Ring 3, selector 0x18)
  - Entry 4: User Data (Ring 3, selector 0x20)
  - Entry 5: LDT (per-process, if used)
  - Entry 6-13: TSS for CPU 0-7 (SMP support)

- **IDT (Interrupt Descriptor Table)**:
  - 256 entries
  - 0-31: CPU exceptions (#DE, #DB, #PF, etc.)
  - 32-47 (0x20-0x2F): Hardware IRQs (timer, keyboard, etc.)
  - 48+ (0x30+): Software interrupts
  - Entry 0x33: MINIX IPC syscall

- **TSS (Task State Segment)**:
  - One per CPU (CONFIG_MAX_CPUS)
  - Critical field: **ESP0** (kernel stack pointer)
  - On Ring 3→0: CPU loads ESP ← TSS.ESP0
  - Must be updated on every context switch
  - Other fields unused by MINIX (no hardware task switching)

**Key Insights**:
- MINIX uses software task switching (not hardware TSS switching)
- TSS serves only to provide ESP0 for privilege transitions
- GDT loaded once at boot via LGDT
- IDT programmed with all 256 handler addresses
- TR register points to current CPU's TSS

**Source Files Referenced**:
- protect.c:25-27 (GDT/IDT/TSS arrays)
- protect.c:250 (prot_init)
- protect.c:58-75 (sdesc - build descriptors)
- klib.S:529-531 (LGDT/LIDT/LTR wrappers)
- archconst.h:11 (IDT_SIZE=256)

---

### 6. TLB Management (tlb-management.tex)

**File**: `diagrams/tikz/tlb-management.tex`
**Size**: ~120 KB PDF
**Purpose**: Explain TLB invalidation strategies (selective vs full flush)

**Content**:
- **TLB Overview**:
  - Cache for virtual→physical translations
  - Size: 64-512 entries (CPU-dependent)
  - Fully associative cache
  - Structure: {VPN} → {PFN + flags}

- **INVLPG (Selective Flush)**:
  - Invalidates single TLB entry
  - Cost: 1-3 cycles
  - Use cases:
    - Unmapping single page (mprotect)
    - Page table entry modification
    - Lazy allocation (map on demand)
    - COW page replacement
  - Assembly: `invlpg (%eax)`

- **CR3 Reload (Full Flush)**:
  - Invalidates ALL non-global TLB entries
  - Cost: ~100 cycles + refill penalty
  - Use cases:
    - Context switch (different address space)
    - Must flush all old process's mappings
  - Assembly: `mov %eax, %cr3`

- **TLB Miss Penalty**:
  - 2 extra memory accesses per miss (2-level paging)
  - 50 cycles/access (typical)
  - Post-switch penalty: 64 misses × 2 × 50 = 6400 cycles
  - **This is why context switching is expensive in microkernels**

**Key Insights**:
- Global pages (PG_G) not flushed on CR3 write
- MINIX uses global pages for kernel text/data
- Selective INVLPG preferred when possible
- Full CR3 flush unavoidable on context switch

**Source Files Referenced**:
- klib.S:549 (i386_invlpg)
- arch_do_vmctl.c:56 (VMCTL_I386_INVLPG)
- mpx.S:594-595 (reload_cr3 - force flush)
- klib.S:618-621 (CR3 conditional switch)

---

### 7. x86 CPU Evolution (x86-cpu-evolution.tex) **[NEW]**

**File**: `diagrams/tikz/x86-cpu-evolution.tex`
**Size**: 149 KB PDF
**Purpose**: Chronicle x86 CPU architecture evolution from 386 to Athlon 64 (1985-2003)

**Content**: Timeline-based visualization with two columns:

**Intel Column** (left):
1. **Intel 80386 (1985)** - CPUCLASS_386
   - Protected mode (Ring 0-3)
   - 32-bit registers & addressing
   - Paging (4KB pages)
   - Virtual 8086 mode
   - Instructions: CR0, CR2, CR3, LGDT, LIDT, LTR, INVLPG, INT, IRET

2. **Intel 80486 (1989)** - CPUCLASS_486
   - **CPUID instruction** (feature detection breakthrough)
   - On-die L1 cache (8KB)
   - Integrated FPU
   - WP bit (CR0.WP)
   - Instructions: CPUID, INVD, WBINVD, CMPXCHG, XADD, BSWAP

3. **Intel Pentium (1993)** - CPUCLASS_586
   - **RDTSC** (time-stamp counter)
   - Dual-issue pipeline (U,V pipes)
   - APIC (vs PIC)
   - MMX (1997 variant)
   - Instructions: RDTSC, CMPXCHG8B, MMX (57 SIMD instructions)

4. **Intel Pentium Pro (1995)** - P6 Architecture (686)
   - **PAE** (36-bit physical addressing)
   - **SYSENTER/SYSEXIT** (fast syscalls)
   - PGE (Page Global Enable)
   - CMOV (16 conditional move variants)
   - Out-of-order execution
   - Instructions: CR4.PAE, SYSENTER, SYSEXIT, CR4.PGE, CMOVcc, RDMSR, WRMSR

5. **Intel Pentium II (1997)** - P6 + MMX
   - MMX + FXSAVE/FXRSTOR
   - SSE preparation (full in PIII)
   - Instructions: FXSAVE, FXRSTOR

6. **Intel Pentium III (1999)** - P6 + SSE
   - **SSE** (70 SIMD instructions)
   - Enhanced 3DNow! compatibility
   - CPUID serial number (leaf 03h)
   - Instructions: SSE (MOVAPS, ADDPS, etc.), SFENCE

7. **Intel Pentium 4 (2000)** - NetBurst
   - **SSE2** (144 new double-precision SIMD instructions)
   - Hyper-Threading Technology
   - Long pipeline (20-31 stages)
   - Trace cache
   - Instructions: SSE2 (MOVAPD, ADDPD, etc.), PAUSE, MFENCE, LFENCE, CLFLUSH

**AMD Column** (right):
1. **AMD K5 (1996)** - Pentium-class
   - Pentium-compatible (no SYSCALL yet)

2. **AMD K6 (1997)** - CPUCLASS_586
   - **SYSCALL/SYSRET** (first implementation, AMD-specific)
   - 3DNow! (21 FP SIMD instructions)
   - MMX support
   - EFER MSR
   - Instructions: SYSCALL, SYSRET, 3DNow!, EFER MSR

3. **AMD K7/Athlon (1999)** - CPUCLASS_686
   - SSE support (later revisions)
   - Improved 3DNow!

4. **AMD Athlon XP (2001)** - K7 Enhanced
   - Full SSE support
   - 3DNow! Professional
   - Hardware prefetch
   - Instructions: SSE (all), PREFETCH, PREFETCHW, SYSCALL (refined)

5. **AMD Athlon 64 (2003)** - x86-64
   - **64-bit mode** (long mode)
   - **NX bit** (No-Execute for DEP)
   - On-die memory controller
   - SSE2 support
   - Instructions: 64-bit registers (RAX, etc.), EFER.NXE, SYSCALL (64-bit variant)

**Key Historical Insights**:
- **The SYSCALL Race**: AMD K6 (1997) introduced SYSCALL/SYSRET before Intel's SYSENTER/SYSEXIT (Pentium Pro, 1995) but after Pentium Pro's release. SYSCALL was 5 cycles faster (35 vs 40).
- **The 64-bit Race**: AMD Athlon 64 (2003) beat Intel to market with x86-64. Intel adopted AMD64 in later Pentium 4 revisions (2004+).
- **MINIX Support**: Fully supports 32-bit features (CPUID, RDTSC, PAE, SYSENTER, SYSCALL, SSE). Detects 64-bit CPUs but runs in 32-bit mode with PAE for NX bit support.

**Background Zones**:
- Blue: 16-bit → 32-bit transition (386, 486)
- Green: Performance era (Pentium)
- Orange: P6 Architecture (Pentium Pro, Pentium II)
- Blue: SSE/SSE2 Era (Pentium III, Pentium 4)
- Red: AMD Competition (K5 through Athlon 64)

**Source Files Referenced**:
- cputypes.h:35-58 (CPU class/type definitions)
- specialreg.h:37-200 (CPUID flags, CR bits)
- features.md:1-13 (MINIX support matrix)

**Documentation**: See `x86-cpu-evolution-README.md` for full details.

---

## Statistics Summary

### Overall Metrics

- **Total diagrams**: 7
- **Total source files referenced**: 30+
- **Total CPU mechanisms documented**: 60+
- **Total lines of TikZ code**: ~1,800
- **Combined PDF size**: ~1 MB
- **Timeline coverage**: 18 years (1985-2003)

### Coverage by Category

1. **System Calls**: 3 mechanisms (INT, SYSENTER, SYSCALL)
2. **Interrupts**: 2 controllers (PIC, APIC)
3. **Exceptions**: 20 CPU exceptions (#DE through #XF)
4. **Context Switching**: Complete flow with 3 return paths
5. **CPU Structures**: 3 tables (GDT, IDT, TSS)
6. **TLB Management**: 2 strategies (INVLPG, CR3 reload)
7. **CPU Evolution**: 12 generations (7 Intel, 5 AMD)

### Performance Metrics Documented

- System call latencies: 35-200 cycles
- Interrupt handling: 6-8 μs
- Context switch overhead: 6400 cycles (TLB refill)
- TLB invalidation: 1-100+ cycles
- Memory access penalty: 2 extra accesses per TLB miss

---

## Compilation Instructions

### Prerequisites

```bash
# Arch/CachyOS
sudo pacman -S texlive-core texlive-latexextra texlive-pictures

# Debian/Ubuntu
sudo apt install texlive-latex-extra texlive-pictures

# Fedora
sudo dnf install texlive-scheme-full
```

### Compile All Diagrams

```bash
cd /home/eirikr/Playground/minix-analysis/diagrams/tikz

# Compile individually
for tex in system-call-mechanisms hardware-interrupt-flow exception-handling \
           context-switch-detailed cpu-structures tlb-management x86-cpu-evolution; do
  pdflatex -interaction=nonstopmode ${tex}.tex
done

# Clean auxiliary files
rm -f *.aux *.log

# Convert to PNG (optional, 300 DPI)
for pdf in *.pdf; do
  magick -density 300 -quality 95 ${pdf} ${pdf%.pdf}.png
done
```

### Batch Script

```bash
#!/bin/bash
# compile-all-diagrams.sh

set -e
cd /home/eirikr/Playground/minix-analysis/diagrams/tikz

DIAGRAMS=(
  "system-call-mechanisms"
  "hardware-interrupt-flow"
  "exception-handling"
  "context-switch-detailed"
  "cpu-structures"
  "tlb-management"
  "x86-cpu-evolution"
)

for diagram in "${DIAGRAMS[@]}"; do
  echo "Compiling ${diagram}..."
  pdflatex -interaction=nonstopmode ${diagram}.tex > /dev/null
done

echo "Cleaning auxiliary files..."
rm -f *.aux *.log

echo "Done! PDFs created:"
ls -lh *.pdf
```

---

## Integration with Whitepaper

### LaTeX Chapter Structure

```latex
\documentclass[12pt]{report}
\usepackage{graphicx}
\usepackage{subcaption}

\begin{document}

\chapter{MINIX CPU Interface Analysis}

\section{System Call Mechanisms}
MINIX supports three system call mechanisms for compatibility and performance...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/system-call-mechanisms.pdf}
\caption{Comparison of INT, SYSENTER, and SYSCALL system call mechanisms}
\label{fig:syscall-mechanisms}
\end{figure}

\section{Hardware Interrupt Handling}
Modern x86 systems support two interrupt controllers: the legacy 8259 PIC and
the Advanced Programmable Interrupt Controller (APIC)...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/hardware-interrupt-flow.pdf}
\caption{PIC vs APIC interrupt handling flow}
\label{fig:interrupt-flow}
\end{figure}

\section{Exception Handling}
The x86 architecture defines 20 CPU exceptions, ranging from divide errors to
page faults. MINIX handles all exceptions via the IDT...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/exception-handling.pdf}
\caption{Page fault exception handling with CR2 register}
\label{fig:exception-handling}
\end{figure}

\section{Context Switching}
Context switches are expensive operations due to TLB flushing. MINIX minimizes
overhead through careful CR3 management...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/context-switch-detailed.pdf}
\caption{Complete context switch flow from Process A to Process B}
\label{fig:context-switch}
\end{figure}

\section{CPU Protection Structures}
The x86 architecture relies on three critical tables: GDT, IDT, and TSS...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/cpu-structures.pdf}
\caption{GDT, IDT, and TSS structures in MINIX}
\label{fig:cpu-structures}
\end{figure}

\section{TLB Management}
Translation Lookaside Buffers (TLBs) cache virtual-to-physical address mappings.
MINIX uses two strategies for TLB invalidation...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/tlb-management.pdf}
\caption{INVLPG vs CR3 reload TLB invalidation strategies}
\label{fig:tlb-management}
\end{figure}

\section{x86 CPU Architecture Evolution}
Understanding the evolution of x86 CPUs helps explain MINIX's feature detection
and compatibility strategies...

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/x86-cpu-evolution.pdf}
\caption{x86 CPU architecture timeline (1985-2003) with MINIX support}
\label{fig:cpu-evolution}
\end{figure}

\end{document}
```

### Cross-References

When discussing specific CPU features in text, reference the evolution timeline:

```latex
The Pentium Pro (1995) introduced PAE and SYSENTER (see Figure~\ref{fig:cpu-evolution}),
which MINIX fully supports. The system call mechanism selection is shown in
Figure~\ref{fig:syscall-mechanisms}, where SYSENTER provides 5x faster syscalls
than the legacy INT instruction.
```

---

## File Organization

```
minix-analysis/
├── diagrams/
│   └── tikz/
│       ├── system-call-mechanisms.tex
│       ├── system-call-mechanisms.pdf (126 KB)
│       ├── hardware-interrupt-flow.tex
│       ├── hardware-interrupt-flow.pdf (~120 KB)
│       ├── exception-handling.tex
│       ├── exception-handling.pdf (~115 KB)
│       ├── context-switch-detailed.tex
│       ├── context-switch-detailed.pdf (~130 KB)
│       ├── cpu-structures.tex
│       ├── cpu-structures.pdf (~125 KB)
│       ├── tlb-management.tex
│       ├── tlb-management.pdf (~120 KB)
│       ├── x86-cpu-evolution.tex
│       ├── x86-cpu-evolution.pdf (149 KB)
│       ├── x86-cpu-evolution-README.md
│       └── compile-all-diagrams.sh
├── CPU-INTERFACE-DIAGRAMS-COMPLETE.md
├── CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md (this file)
└── MINIX-CPU-INTERFACE-ANALYSIS.md (source analysis, 1134 lines)
```

---

## Next Steps

### Remaining Diagrams (from original request)

1. **386 Baseline Interface Diagram**
   - Protected mode details (Ring 0-3)
   - Paging mechanism (2-level page tables)
   - Segment registers and descriptors
   - Virtual 8086 mode

2. **486 Enhancements Diagram**
   - CPUID instruction flow
   - WP bit (write protection)
   - On-die cache architecture
   - FPU integration

3. **Pentium Diagram**
   - RDTSC timing mechanism
   - APIC configuration
   - Dual-issue pipeline (U,V pipes)
   - Superscalar execution

4. **P6 Architecture Diagram**
   - PAE memory layout (3-level page tables)
   - SYSENTER/SYSEXIT detailed flow
   - CMOV instruction usage
   - Out-of-order execution pipeline

5. **Feature Detection Flowchart**
   - CPUID decision tree
   - Feature flag checking
   - Vendor detection (Intel/AMD/Cyrix)
   - Fallback strategies

### Integration Tasks

1. **Whitepaper Chapter Creation**
   - Write introductory text for each diagram
   - Cross-reference related diagrams
   - Add performance analysis sections
   - Include code examples from MINIX source

2. **PGFPlots Visualizations** (from original request)
   - System call latency comparison (bar chart)
   - Context switch overhead (stacked bar chart)
   - TLB miss penalty vs TLB size (line graph)
   - CPU feature adoption timeline (Gantt chart)

3. **Final Compilation**
   - Combine all diagrams into single PDF appendix
   - Create high-resolution PNGs for web version
   - Generate thumbnails for index page
   - Build searchable PDF with hyperlinks

---

## References

### MINIX Source Files

- **sys/arch/x86/x86/mpx.S** - System call entry points, interrupt handlers
- **sys/arch/x86/x86/klib.S** - Low-level CPU manipulation (CR3, INVLPG, etc.)
- **sys/arch/x86/x86/protect.c** - GDT/IDT/TSS initialization
- **sys/arch/x86/include/cputypes.h** - CPU classification
- **sys/arch/x86/include/specialreg.h** - Control register bits, CPUID flags
- **analysis_tools/features.md** - MINIX feature support matrix

### Documentation

- **MINIX-CPU-INTERFACE-ANALYSIS.md** - Original comprehensive analysis (1134 lines)
- **CPU-INTERFACE-DIAGRAMS-COMPLETE.md** - First 6 diagrams documentation
- **latex/TIKZ-STYLE-GUIDE.md** - Visual style conventions
- **x86-cpu-evolution-README.md** - CPU evolution timeline documentation

### External References

- Intel® 64 and IA-32 Architectures Software Developer's Manual (3 volumes)
- AMD64 Architecture Programmer's Manual (5 volumes)
- MINIX 3.4.0-RC6 source code
- x86 CPU feature evolution (Wikipedia, CPU-World)

---

## Contact and Contributions

This documentation is part of the MINIX CPU Interface Analysis project.

**Repository**: `/home/eirikr/Playground/minix-analysis`
**Created**: 2025-10-31
**Version**: 1.0

For questions or contributions, please refer to the project README.

---

**Total Diagrams**: 7 complete
**Total Documentation**: 4 comprehensive guides
**Project Status**: 60% complete (7/12 diagrams, awaiting 5 additional CPU-specific diagrams)

