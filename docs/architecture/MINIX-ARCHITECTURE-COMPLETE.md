# MINIX 3.4 Complete Architecture Reference

**Status:** Consolidated reference document (Phase 2B)
**Date:** November 1, 2025
**Scope:** Comprehensive architecture documentation synthesized from 8 source files
**Audience:** Developers, researchers, students of operating systems

---

## Table of Contents

1. [Supported Architectures](#supported-architectures)
2. [i386 Architecture (32-bit x86)](#i386-architecture)
3. [ARM Architecture (earm)](#arm-architecture)
4. [System Call Mechanisms](#system-call-mechanisms)
5. [Microarchitecture Deep Dive](#microarchitecture-deep-dive)
6. [CPU Interface Analysis](#cpu-interface-analysis)
7. [ISA-Level Analysis](#isa-level-analysis)
8. [Umbrell Architecture Overview](#umbrella-architecture-overview)
9. [Visual Diagrams](#visual-diagrams)
10. [References](#references)

---

## Supported Architectures

MINIX 3.4.0-RC6 supports **two primary architectures**:

### 1. i386 (32-bit x86)
- **Primary architecture** for x86 processors
- Target platform: Intel Pentium II and later, AMD Athlon
- Kernel code: `/minix/kernel/arch/i386/`
- Full register set and syscall mechanism support

### 2. earm (32-bit ARM)
- **Embedded ARM support**
- Target: ARM Cortex-A cores
- Kernel code: `/minix/kernel/arch/earm/`
- Optimized for embedded systems

### NOT Supported
- **x86-64 (long mode, 64-bit)** - Not implemented in MINIX 3.4
- ARM THUMB mode - Not supported
- x86 real mode operations beyond boot - Not supported

**Verification**: Architecture directories at `/minix/kernel/arch/` contain only `i386/` and `earm/` subdirectories, confirming no x86-64 support in this release.

---

## i386 Architecture

### Register Set (32-bit)

#### General Purpose Registers

| Register | Primary Use | Syscall Role | Notes |
|----------|-------------|--------------|-------|
| **EAX** | Accumulator | Return values, syscall params | Result from system calls |
| **EBX** | Base register | Syscall params | Argument register |
| **ECX** | Counter | Syscall params | **Clobbered by SYSCALL instruction** |
| **EDX** | Data | Syscall params | Receives ECX value before SYSCALL |
| **ESI** | Source index | Saved ESP during syscall | User stack preservation |
| **EDI** | Destination index | Syscall type (IPCVEC, KERVEC) | Identifies syscall class |
| **EBP** | Base pointer | Process structure pointer in kernel | Links to PCB |
| **ESP** | Stack pointer | Kernel stack during syscall | Managed by syscall mechanism |

#### Control Registers

| Register | Purpose | Key Bits |
|----------|---------|----------|
| **CR0** | Protection & paging | PE (Protected Mode), PG (Paging) |
| **CR2** | Page fault address | Linear address causing #PF |
| **CR3** | Page directory base | Physical address of page directory |
| **CR4** | Extensions | PSE, PAE, PGE, MCE |
| **EFLAGS** | Condition flags | IF (interrupt), ZF, CF, OF |

#### Segment Registers

| Segment | Purpose |
|---------|---------|
| **CS** | Code segment (kernel=0x08, user=0x1b) |
| **DS/SS** | Data and stack segments |
| **ES/FS/GS** | Extra segments (task-local storage) |

### System Call Mechanisms (i386)

MINIX 3.4 i386 uses **three distinct syscall entry mechanisms**, optimized for different processor generations:

#### 1. INT (Software Interrupt) - Universal Path

**Entry Point**: `ipc_entry_softint_um` (mpx.S:269)
**Vector**: INT 0x21 (IPC_VECTOR_UM = 33)
**Compatibility**: All x86 processors (286+)

**Register Convention**:
- EAX: System call number / first parameter
- EBX, ECX: Additional parameters
- EDI: Call type indicator

**Hardware Actions** (automatic):
1. Push SS, ESP, EFLAGS, CS, EIP (5 values pushed automatically)
2. Load CS:EIP from IDT entry (interrupt gate)
3. Set CPL (Current Privilege Level) = 0

**Kernel Actions** (manual):
1. Execute `SAVE_PROCESS_CTX(0, KTS_INT_UM)` - save remaining registers
2. Call `do_ipc()` system call handler
3. Return via `IRET` instruction

**Performance**: ~1772 CPU cycles (Skylake benchmark baseline)
**Advantages**: Universal compatibility, simple semantics
**Disadvantages**: Slower than modern mechanisms, many context switches

#### 2. SYSENTER (Intel Fast Path) - Optimized for Pentium II+

**Entry Point**: `ipc_entry_sysenter` (mpx.S:220)
**Prerequisites**:
- Processor: Pentium II or later (IA32_SYSENTER_CS MSR)
- Kernel: Must initialize three MSRs

**MSR Setup** (protect.c:183-187):
```c
ia32_msr_write(INTEL_MSR_SYSENTER_CS,  0, KERN_CS_SELECTOR);     // Kernel CS
ia32_msr_write(INTEL_MSR_SYSENTER_ESP, 0, t->sp0);               // Kernel stack
ia32_msr_write(INTEL_MSR_SYSENTER_EIP, 0, ipc_entry_sysenter);  // Entry EIP
```

**Register Convention**:
- EDI: Syscall type (IPCVEC or KERVEC)
- EAX, EBX, ECX: Parameters (must preserve EDX for return)
- **User must manually save ESP→ESI, EIP→EDX** before instruction

**Hardware Actions** (automatic, no stack operations):
1. Load CS from SYSENTER_CS MSR (kernel code segment)
2. Load ESP from SYSENTER_ESP MSR (kernel stack pointer)
3. Load EIP from SYSENTER_EIP MSR (entry point address)
4. Set CPL = 0, disable interrupts (IF = 0)
5. **No automatic state save - user responsibility**

**Kernel Actions**:
1. Recover user ESP from ESI register
2. Recover user EIP from EDX register
3. Save to kernel process table
4. Execute syscall handler
5. Return via `SYSEXIT` instruction (restores EIP←EDX, ESP←ECX)

**Performance**: ~1305 CPU cycles (Skylake benchmark)
**Advantages**: Fast, minimal context operations, newer processors
**Disadvantages**: Manual state save requirement, limited to Pentium II+

#### 3. SYSCALL (AMD/Intel, 32-bit)

**Entry Point**: `ipc_entry_syscall` (mpx.S:...)
**Prerequisites**:
- Processor: AMD Athlon/Opteron, newer Intel (Pentium 4+)
- Kernel: Initialize IA32_LSTAR MSR (AMD SYSCALL/SYSRET)

**Register Convention**:
- Similar to SYSENTER but architecture-specific

**Performance**: Comparable to SYSENTER (~1300 cycles)
**Advantages**: AMD optimization, consistent with x86-64 (when ported)
**Disadvantages**: Only on newer AMD/Intel processors

### Syscall Handler Flow

All three mechanisms converge to common handler:

```
User Application
        ↓
    [INT/SYSENTER/SYSCALL instruction]
        ↓
    Kernel entry routine saves state
        ↓
    do_ipc() dispatcher
        ↓
    System call implementation (send, receive, notify, etc.)
        ↓
    Return to user via IRET/SYSEXIT/SYSRET
```

---

## ARM Architecture (earm)

### MINIX ARM Support

MINIX 3.4 provides ARM embedded support with:

**Target Processors**: ARM Cortex-A (32-bit ARMv7)
**Kernel Location**: `/minix/kernel/arch/earm/`
**Boot Path**: ARM-specific bootloader → kernel initialization
**Memory Model**: Protected memory with translation lookaside buffer (TLB)

### ARM System Call Mechanism

ARM uses **Software Interrupt (SWI/SVC)** for system calls:

**Instruction**: SWI #0 (Software Interrupt)
**Privilege Level**: User mode → Supervisor mode transition
**Handler**: ARM supervisor mode entry

**Register Convention**:
- R0: First syscall parameter / return value
- R1-R3: Additional parameters
- R4-R7: Saved by caller
- R12 (IP): Call type indicator

### Memory Architecture

ARM implementation uses standard ARM MMU features:
- Page table walk (hierarchical)
- TLB caching
- Large/small page support

---

## Microarchitecture Deep Dive

### CPU Pipeline Architecture

MINIX 3.4 is optimized for modern superscalar processors with:

**Pipeline Characteristics**:
- Out-of-order execution support
- Branch prediction
- Instruction-level parallelism (ILP) up to 4-way
- Modern cache hierarchies (L1i, L1d, L2, L3)

### Context Switch Overhead

**Current Measurement** (x86_64 baseline, estimated for i386):
- Full context save: ~50-100 CPU cycles
- TLB invalidation: ~100-500 cycles (variable by CPU generation)
- Cache cold penalty: ~1000+ cycles on re-entry

**Optimization Strategies**:
1. Lazy context switching (postpone non-critical saves)
2. TLB shootdown optimization (batch invalidations)
3. Cache warming (predictive preload)

### Branch Prediction Impact

Modern processors like Skylake include:
- Dynamic branch prediction (2K-4K entry BTB)
- Speculative execution (with speculative state restoration)
- Branch target buffer (BTB) for frequent jump targets

MINIX syscall paths benefit from:
- Predictable branch patterns (syscall dispatcher is deterministic)
- BTB entries for common syscalls
- Return stack buffer (RSB) for nested calls

### Cache Architecture

**Typical Skylake (Reference)**:
- L1i cache: 32 KB, 8-way set associative
- L1d cache: 32 KB, 8-way set associative, 64-byte line
- L2 cache: 256 KB, 4-way, per-core
- L3 cache: 8-16 MB, shared across cores

MINIX kernel code characteristics:
- Small kernel (~95 KB) - fits in L1 with room
- Frequently accessed syscall paths - hot in cache
- Process switching causes L1i reloading

---

## CPU Interface Analysis

### Interface Design Principles

The MINIX CPU interface (mpx.S, protect.c) implements:

1. **Privilege Separation**: Ring-based privilege (CPL 0=kernel, CPL 3=user)
2. **State Management**: Explicit register save/restore
3. **Interrupt Handling**: IDT-based exception handling
4. **Memory Protection**: Paging-based virtual memory

### Protection Rings and Privilege Levels

| Ring | Level | Mode | Access | MINIX Use |
|------|-------|------|--------|-----------|
| **0** | CPL 0 | Supervisor | All | Kernel code |
| **1-2** | CPL 1-2 | Used rarely | Limited | Device drivers |
| **3** | CPL 3 | User | User-only | User processes |

### Segmentation vs Paging

MINIX uses **minimal segmentation** and **pure paging**:

**Segmentation**:
- Only 4 GDT entries: kernel CS, kernel DS, user CS, user DS
- Flat memory model (segment base = 0, limit = 4GB)
- Effectively disabled in favor of paging

**Paging**:
- Two-level page tables (PDE, PTE)
- 4 KB pages (standard)
- Per-process page directory
- Kernel page directory shared across all processes (higher half mapping)

### Interrupt and Exception Handling

IDT (Interrupt Descriptor Table) maps 256 vectors:

| Vector | Type | Handler | Purpose |
|--------|------|---------|---------|
| 0-31 | Exceptions | Hardware handlers | Faults (#PF, #GP, etc.) |
| 32-47 | IRQ | PIC handlers | Devices (timer, keyboard, etc.) |
| 33 (0x21) | Syscall INT | `ipc_entry_softint_um` | User syscalls |
| 48+ | Reserved | - | Unused in MINIX |

---

## ISA-Level Analysis

### Instruction Distribution in MINIX Kernel

Based on analysis of 91 kernel files (19,000 LOC):

**Most Frequent Instructions**:
1. `MOV` - Register/memory operations (18-22% of instructions)
2. `CALL/RET` - Function calls (12-15%)
3. `ADD/SUB` - Arithmetic (8-10%)
4. `TEST/CMP` - Comparisons (8-10%)
5. `JMP/Jcc` - Branches (7-9%)
6. `PUSH/POP` - Stack operations (5-7%)
7. `LEA` - Address calculation (4-6%)
8. `XOR` - Bitwise operations (3-5%)

**Characteristics**:
- MOV-heavy (typical for modern C-compiled code)
- Frequent function calls (modular design)
- Moderate branching (straightforward control flow)

### System Call Instruction Paths

**INT 0x21 path** (most common):
```
User: INT 0x21               ; Syscall entry
  ↓
Hardware: Push return address
  ↓
Kernel: SAVE_PROCESS_CTX     ; Save registers (20-30 instructions)
  ↓
  CALL do_ipc                ; Branch to handler
  ↓
  Handler executes (10-100 instructions depending on syscall)
  ↓
  IRET                       ; Restore and return
```

**SYSENTER path** (fast):
```
User: SYSENTER                ; Fast entry
  ↓
Kernel: Minimal register save  ; 3-5 instructions
  ↓
  CALL do_ipc                ; Handler
  ↓
  SYSEXIT                    ; Fast return
```

---

## Umbrella Architecture Overview

The MINIX microkernel architecture is a **vertically integrated system** with:

### Architectural Layers

```
┌─────────────────────────────────┐
│   User Applications             │  CPL 3
├─────────────────────────────────┤
│   User-Space Services           │  CPL 3
│  (VM, FS, NET, DEVICE DRIVERS)  │
├─────────────────────────────────┤
│   Microkernel (IPC, Sched)      │  CPL 0  ← Only 95 KB!
├─────────────────────────────────┤
│   CPU Interface & Hardware      │  CPL 0
└─────────────────────────────────┘
```

### Microkernel Responsibilities (95 KB)

The MINIX kernel handles **only**:
- Process scheduling (CFS-like)
- Interprocess Communication (IPC/message passing)
- Memory protection (paging)
- Interrupt handling

### User-Space Services

All other OS functionality runs in user-space:
- **VM** (Virtual Memory manager): Paging, memory allocation
- **FS** (File System): Block device abstraction, file operations
- **NET** (Network stack): Protocol implementation
- **Device drivers**: Hardware abstraction
- **System services**: Time, resources, process management

### Advantages of This Architecture

1. **Microkernel is simpler** → fewer bugs, easier to verify
2. **Isolation** → driver crash doesn't crash kernel
3. **Security** → reduced attack surface
4. **Modularity** → swap components (filesystems, network stacks)

### Challenges and Trade-offs

1. **Context switching overhead** → More frequent user-kernel transitions
2. **Message passing latency** → Slower than monolithic syscalls
3. **Complexity in user-space** → Distributed logic harder to debug
4. **IPC bottle-neck** → Heavy IPC workload reduces scalability

---

## Visual Diagrams

### Figure 1: Memory Hierarchy and Addressing

(Refer to CPU-INTERFACE-DIAGRAMS-COMPLETE.md for visual representation)

**Virtual Address → Physical Address translation**:
```
User Virtual Address Space (0x00000000 - 0x7FFFFFFF)
  ↓ (Page table walk via CR3)
Kernel Page Tables (kept in upper half)
  ↓
Physical Memory (mapped by BIOS/kernel)
```

### Figure 2: System Call Flow Diagram

(Refer to CPU-INTERFACE-DIAGRAMS-COMPLETE.md)

**User → Kernel transition**:
```
1. User code executes INT 0x21
2. Hardware switches CPL and loads handler
3. Kernel entry routine saves user state
4. System call handler executes
5. IRET restores user state and returns
```

### Figure 3: Process and Memory Layout

(Refer to CPU-INTERFACE-DIAGRAMS-COMPLETE.md)

**Per-process address space**:
```
Kernel Space (Upper half, shared)    0x80000000 - 0xFFFFFFFF
Shared kernel code and data
  ↓
Kernel page directory base (CR3)
  ↓
User Space (Lower half, per-process) 0x00000000 - 0x7FFFFFFF
User code, data, heap, stack
```

---

## Detailed CPU Diagram References

For comprehensive CPU interface diagrams, see:
- `CPU-INTERFACE-DIAGRAMS-COMPLETE.md` - Professional TikZ diagrams
- `CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md` - Diagram explanations
- `whitepaper/diagrams/` - LaTeX compiled versions

---

## References

### Source Code References

- **Boot sequence**: `minix/kernel/arch/i386/mpx.S` (assembly entry)
- **Protection mechanisms**: `minix/kernel/arch/i386/protect.c` (CPU setup)
- **Syscall dispatcher**: `minix/kernel/system/do_ipc.c` (IPC handler)
- **Memory management**: `minix/kernel/arch/i386/memory.c` (paging setup)

### Related Documentation

- [MINIX Syscall Catalog](../Analysis/SYSCALL-ANALYSIS.md)
- [IPC System Analysis](../Analysis/IPC-SYSTEM-ANALYSIS.md)
- [Boot Sequence Analysis](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)
- [Performance Analysis](../Performance/COMPREHENSIVE-PROFILING-GUIDE.md)

### Further Reading

1. **Intel 64 and IA-32 Architectures Software Developer's Manual** (Intel)
2. **AMD64 Architecture Programmer's Manual** (AMD)
3. **ARM Architecture Reference Manual ARMv7** (ARM)
4. **MINIX 3 Book** by Andrew Tanenbaum (O'Reilly)
5. **Linux Kernel Documentation** (for comparison)

---

## Document Metadata

**Consolidated From:**
- MINIX-ARCHITECTURE-SUMMARY.md (476 lines)
- MINIX-CPU-INTERFACE-ANALYSIS.md (1,133 lines)
- ISA-LEVEL-ANALYSIS.md (852 lines)
- MICROARCHITECTURE-DEEP-DIVE.md (1,276 lines)
- CPU-INTERFACE-DIAGRAMS-COMPLETE.md (753 lines)
- CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md (704 lines)
- MINIX-ARM-ANALYSIS.md (124 lines)
- UMBRELLA-ARCHITECTURE.md (788 lines)

**Total Source**: 6,106 lines
**Consolidated**: November 1, 2025
**Format**: Markdown with comprehensive sectioning
**Audience**: Developers, researchers, students of OS architecture

---

*Last Updated: November 1, 2025*
*Status: Phase 2B Consolidation - Architecture Documentation*
*Next Phase: Cross-reference updates and additional consolidations*
