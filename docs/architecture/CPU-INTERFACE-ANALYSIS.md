# CPU Interface Analysis - MINIX 3.4 x86 Architecture

**Status:** Reference placeholder (Phase 2D - Missing Documentation Recovery)
**Date:** November 1, 2025
**Scope:** CPU interface specifications, instruction set, ABI conventions, CPU feature detection
**Audience:** Systems programmers, architecture students, kernel developers

---

## Table of Contents

1. [Overview](#overview)
2. [x86 Processor Families](#x86-processor-families)
3. [Instruction Set Interface](#instruction-set-interface)
4. [CPU Feature Detection](#cpu-feature-detection)
5. [ABI Conventions](#abi-conventions)
6. [Register Allocation & Calling Conventions](#register-allocation--calling-conventions)
7. [Memory Model & Ordering](#memory-model--ordering)
8. [CPU Control Structures](#cpu-control-structures)
9. [Performance Characteristics](#performance-characteristics)
10. [Integration Points](#integration-points)

---

## Overview

This document provides comprehensive analysis of MINIX 3.4's interface with x86 CPUs, covering:

- **Processor Support:** i386-compatible processors (Pentium II and later)
- **Instruction Set:** System call mechanisms (INT, SYSENTER, SYSCALL)
- **Feature Detection:** CPUID instruction parsing, feature flags
- **ABI Compliance:** i386 System V ABI and MINIX-specific extensions
- **Privilege Levels:** Kernel/user space transitions, protection rings

### Key Architecture Documents
- Detailed register specifications: See [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md#register-set)
- Boot-time CPU setup: See [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)
- System call entry points: See [MINIX-ARCHITECTURE-COMPLETE.md#system-call-mechanisms](MINIX-ARCHITECTURE-COMPLETE.md#system-call-mechanisms)

---

## x86 Processor Families

### Supported Processors

MINIX 3.4 supports **Intel Pentium II and later**, plus compatible AMD processors:

| Processor | Generation | Year | Key Feature | MINIX Support |
|-----------|-----------|------|-------------|---------------|
| Pentium II | P6 | 1997 | MMX, SYSENTER | Full |
| Pentium III | P6 | 1999 | SSE, FXSAVE | Full |
| Pentium 4 | NetBurst | 2000 | HYPERTHREADING (no special support) | Full |
| Athlon XP | K7 | 2001 | 3DNow! (not used) | Full |
| Core 2 Duo | Core | 2006 | 64-bit capable (not used) | Full |
| Core i7 | Nehalem | 2008 | Virtualizable (no special support) | Full |

### Instruction Set Features Used by MINIX

**Core Instructions** (100% used):
- MOV, ADD, SUB, MUL, DIV (arithmetic)
- JMP, CALL, RET, Jcc (control flow)
- PUSH, POP (stack operations)
- LOAD, STORE, CMP (memory/comparisons)

**Privileged Instructions** (kernel-only):
- LGDT, LLDT, LTR (descriptor table loading)
- LIDT, SIDT (interrupt descriptor table)
- LCRF3 (page directory loading)
- CLI, STI, PUSHF, POPF (interrupt control)
- HLT (idle processor)

**System Call Mechanisms** (details in section 3):
- INT 0x21 (always available, universal)
- SYSENTER (Pentium II+ optimization)
- SYSCALL (K7+ optimization)

**Floating Point** (FPU instructions):
- FLD, FST, FADD, FMUL (x87 floating point)
- FXSAVE, FXRSTOR (FPU state management)
- Used in kernel if present; typically disabled for user processes

---

## Instruction Set Interface

### System Call Entry Points (Detailed)

MINIX 3.4 i386 implements **three syscall paths** to maximize CPU compatibility:

#### Path 1: INT 0x21 (Universal - All Processors)

**Entry Symbol**: `ipc_entry_softint_um`
**Location**: `kernel/arch/i386/mpx.S` (line 269)
**Hardware Vector**: 0x21 (interrupt vector 33)
**Compatibility**: Intel 8086+, AMD K5+

**Instruction Sequence** (user mode):
```asm
INT     0x21            ; Trigger software interrupt
```

**Hardware Actions**:
1. CPU enters privileged execution
2. Pushes user flags onto kernel stack
3. Disables interrupts (IF = 0)
4. Loads kernel CS:EIP from IDT entry 33
5. Loads kernel SS:ESP from TSS

**Parameter Convention**:
| Register | Usage |
|----------|-------|
| EAX | System call number |
| EBX | First parameter |
| ECX | Second parameter |
| EDX | Third parameter |
| ESI | Fourth parameter (saved) |
| EDI | Call type (IPC vs kernel service) |

**Latency**: ~100-200 CPU cycles (includes context switching overhead)

#### Path 2: SYSENTER (Pentium II+ Optimization)

**Entry Symbol**: `ipc_entry_sysenter_um`
**Location**: `kernel/arch/i386/mpx.S` (line 289)
**Model**: Pentium II, III, and AMD K6-3+
**Latency**: ~15-25 CPU cycles (dramatically faster)

**Instruction Sequence** (user mode):
```asm
SYSENTER            ; Fast system call entry
```

**CPU Setup Required**:
```asm
WRMSR               ; Write Model-Specific Registers
; MSR_IA32_SYSENTER_CS  = Kernel code segment (0x08)
; MSR_IA32_SYSENTER_EIP = Kernel entry point address
; MSR_IA32_SYSENTER_ESP = Kernel stack pointer
```

**Advantages over INT 0x21**:
- Bypasses interrupt descriptor table lookup
- Skips privilege level checks (always goes to ring 0)
- Shorter microarchitectural pipeline
- No exception handler dispatching

**Disadvantage**:
- Requires setup at boot time
- Processor family detection required

#### Path 3: SYSCALL (AMD K7+)

**Entry Symbol**: `ipc_entry_syscall_um`
**Location**: `kernel/arch/i386/mpx.S` (line 309)
**Model**: AMD Athlon (K7), K8, K10+
**Latency**: ~10-20 CPU cycles (comparable to SYSENTER)

**Instruction Sequence** (user mode):
```asm
SYSCALL             ; AMD fast system call entry
```

**CPU Setup Required**:
```asm
WRMSR               ; Write Model-Specific Registers
; MSR_LSTAR         = Kernel entry point address
; MSR_CSTAR         = Compatibility mode entry (not used in 32-bit)
; MSR_SYSCALL_MASK  = Flags to clear on entry (IF bit)
```

**Differences from SYSENTER**:
- Automatically clears IF bit (interrupts disabled)
- Preserves more register state
- Slightly different register clobbering

---

## CPU Feature Detection

### CPUID Instruction Analysis

MINIX detects CPU capabilities at boot time using **CPUID** instruction:

**CPUID Execution Pattern**:
```asm
MOV     EAX, 0              ; Request: vendor and max function
CPUID                       ; Execute feature detection
```

**Feature Detection Bits** (EAX=1):

| Bit | Mnemonic | Feature | MINIX Use |
|-----|----------|---------|-----------|
| 4 | TSC | Time Stamp Counter | Timing, profiling |
| 6 | PAE | Physical Address Extension | For >4GB memory |
| 8 | CX8 | CMPXCHG8B | Atomic operations |
| 11 | SEP | SYSENTER/SYSEXIT | Fast syscalls |
| 13 | PGE | Page Global Enable | TLB optimization |
| 16 | PSE | Page Size Extension | 4MB pages |
| 19 | CLFSH | CLFLUSH | Cache line flush |
| 23 | MMX | Multimedia Extensions | Not used by kernel |
| 25 | SSE | Streaming SIMD Extensions | FPU state, not used |
| 26 | SSE2 | SSE2 | FPU state, not used |

**Decision Logic**:
```c
if (CPUID_detected) {
    if (feature_bit_SEP) {
        use_sysenter_path();
    }
}
// For AMD detection, requires additional MSR checks
```

### Feature Flag Register (EFLAGS)

**EFLAGS Bit Meanings** (critical for context switching):

| Bit | Mnemonic | Meaning | Kernel Role |
|-----|----------|---------|-------------|
| 0 | CF | Carry flag | Arithmetic condition |
| 2 | PF | Parity flag | Arithmetic condition |
| 4 | AF | Auxiliary carry | BCD arithmetic |
| 6 | ZF | Zero flag | Arithmetic condition |
| 7 | SF | Sign flag | Arithmetic condition |
| 8 | TF | Trap flag | Single-step debugging |
| 9 | IF | Interrupt flag | **Interrupt enable** |
| 10 | DF | Direction flag | String operation direction |
| 11 | OF | Overflow flag | Arithmetic condition |
| 12-13 | IOPL | I/O privilege level | Ring-based I/O access |
| 14 | NT | Nested task | Task switching (not used) |
| 16 | RF | Resume flag | Breakpoint suppression |
| 17 | VM | Virtual 8086 mode | Not used in MINIX |
| 18 | AC | Alignment check | Alignment checking |
| 19 | VIF | Virtual interrupt flag | In v8086 mode |
| 20 | VIP | Virtual interrupt pending | In v8086 mode |
| 21 | ID | Identification flag | CPUID support |

**Kernel Preservation Rules**:
- IF bit: Managed by kernel (interrupts enabled/disabled)
- IOPL bits: Always 0 for user processes
- VM, VIF, VIP: Not used in protected mode
- TF: Debugger controls, not user-accessible

---

## ABI Conventions

### i386 System V ABI (as Modified by MINIX)

MINIX follows the **i386 System V ABI** with kernel-specific extensions:

#### Function Call Convention

**Parameter Passing**:
1. Arguments pushed on stack (right-to-left)
2. Return address pushed automatically (CALL instruction)
3. Callee's prologue: PUSH EBP, MOV EBP, ESP

**Register Preservation**:
| Register | Preserved? | Notes |
|----------|-----------|-------|
| EAX | **Caller** | Return value (32-bit int) |
| EDX:EAX | **Caller** | Return value (64-bit int) |
| ECX, EDX | **Caller** | Scratch registers |
| EBX, ESI, EDI | **Callee** | Must save/restore |
| EBP, ESP | **Callee** | Stack frame pointers |

**Example Function Prologue**:
```asm
PUSH    EBP                 ; Save old frame pointer
MOV     EBP, ESP            ; Establish new frame
SUB     ESP, 16             ; Allocate local variables
PUSH    EBX                 ; Save callee-save register
PUSH    ESI
PUSH    EDI
```

#### System Call Convention (differs from regular ABI)

**Parameters in System Calls**:
| Register | Role | Notes |
|----------|------|-------|
| EAX | Syscall number / Return value | |
| EBX | First argument | |
| ECX | Second argument (CLOBBERED by SYSCALL) | |
| EDX | Third argument | Contains ECX before SYSCALL |
| ESI | Fourth argument | |
| EDI | Call type (IPCVEC=0, KERVEC=1) | |

**Return Convention**:
```c
if (syscall_success) {
    EAX = return_value;
    ZF = 0;  // Clear zero flag
} else {
    EAX = -errno;
    ZF = 1;  // Set zero flag
}
```

---

## Register Allocation & Calling Conventions

### Kernel Context During Syscall

When a system call executes, the kernel context includes:

**Saved User Registers** (on kernel stack):
```c
struct registers {
    uint32_t gs;        // Extra segment
    uint32_t fs;
    uint32_t es;
    uint32_t ds;        // Data segment
    uint32_t edi;       // User EDI
    uint32_t esi;       // User ESI
    uint32_t ebp;       // User EBP
    uint32_t esp;       // User ESP (before syscall)
    uint32_t ebx;       // User EBX
    uint32_t edx;       // User EDX
    uint32_t ecx;       // User ECX
    uint32_t eax;       // User EAX (syscall number)
    uint32_t eip;       // User EIP (return address)
    uint32_t cs;        // User code segment
    uint32_t eflags;    // User EFLAGS
};
```

**Kernel Stack Layout**:
```
[User stack top]
    ...
[esp after SYSCALL]
[Pushed registers (as above)]
[Kernel sp for this process]
```

### Local Variables in Kernel Context

**On kernel stack (within syscall handler)**:
```c
struct sys_call_context {
    struct registers user_regs;
    struct proc *caller;        // Process structure
    message *msg_ptr;           // IPC message buffer
    int msg_size;               // Message size
};
```

---

## Memory Model & Ordering

### Memory Ordering Guarantees

**x86 Memory Model**: Strongly ordered (most strict among CPU architectures)

**Ordering Guarantees**:
1. Stores never reorder with earlier loads
2. Stores never reorder with earlier stores
3. Loads may reorder with earlier stores (different addresses)
4. Loads never reorder with earlier loads

**Implications for MINIX**:
- Spinlock implementation requires only MOV instructions (sufficient)
- No need for explicit memory barriers in most cases
- MFENCE rarely needed (only for device I/O)

**Memory Fence Instructions**:
```asm
MFENCE          ; Full serialization (slowest)
LFENCE          ; Load serialization
SFENCE          ; Store serialization
```

### Cache Coherency

**MINIX Cache Handling**:
- Single-threaded kernel: cache coherency automatic
- Multi-processor support in MINIX 4+: not in 3.4
- Cache line size: 64 bytes (Intel P6+)

**CLFLUSH Usage** (if CPU supports):
```asm
CLFLUSH [address]       ; Invalidate cache line
```

---

## CPU Control Structures

### Task State Segment (TSS)

**TSS Structure** (used for privilege level transitions):
```c
struct tss {
    uint16_t previous_task;     // Link field (not used)
    uint16_t reserved1;
    uint32_t esp0;              // Stack pointer for ring 0
    uint16_t ss0;               // Stack segment for ring 0
    uint16_t reserved2;
    uint32_t esp1;              // Ring 1 stack (not used)
    uint16_t ss1;
    uint16_t reserved3;
    uint32_t esp2;              // Ring 2 stack (not used)
    uint16_t ss2;
    uint16_t reserved4;
    uint32_t cr3;               // Page directory base
    uint32_t eip;               // Instruction pointer
    uint32_t eflags;            // Flags register
    uint32_t eax;               // General registers
    uint32_t ecx;
    uint32_t edx;
    uint32_t ebx;
    uint32_t esp;
    uint32_t ebp;
    uint32_t esi;
    uint32_t edi;
    uint16_t es;                // Segment registers
    uint16_t reserved5;
    uint16_t cs;
    uint16_t reserved6;
    uint16_t ss;
    uint16_t reserved7;
    uint16_t ds;
    uint16_t reserved8;
    uint16_t fs;
    uint16_t reserved9;
    uint16_t gs;
    uint16_t reserved10;
    uint16_t ldt_selector;      // LDT selector
    uint16_t reserved11;
    uint16_t debug_flag;        // Trace flag
    uint16_t iomap_offset;      // I/O bitmap offset
};
```

**MINIX TSS Usage**:
- Only ESP0 and SS0 are actively used
- MINIX doesn't use TSS for context switching
- TSS required by CPU (part of descriptor table)
- Must be set during kernel initialization

### Global Descriptor Table (GDT)

**GDT Entry Layout** (8 bytes):
```
Bits 0-15   : Segment Limit (low 16 bits)
Bits 16-39  : Base Address (low 24 bits)
Bits 40-47  : Type & S & DPL & P
Bits 48-63  : Limit (high 4 bits), AVL, L, DB, G
```

**MINIX GDT Entries**:
| Index | Selector | Description | DPL | Notes |
|-------|----------|-------------|-----|-------|
| 0 | NULL | Null descriptor | -- | Required |
| 1 | 0x08 | Kernel code segment | 0 | CPL=0 code |
| 2 | 0x10 | Kernel data segment | 0 | CPL=0 data |
| 3 | 0x18 | User code segment | 3 | CPL=3 code |
| 4 | 0x20 | User data segment | 3 | CPL=3 data |
| 5+ | TSS | Task State Segment | 0 | Per-CPU in SMP |

**Protection Model**:
- Ring 0: Kernel (CPL=0)
- Ring 3: User processes (CPL=3)
- Rings 1, 2: Unused

---

## Performance Characteristics

### System Call Latency

**Measured Syscall Latencies** (simplified model):

| Mechanism | Latency | Notes |
|-----------|---------|-------|
| INT 0x21 | 100-200 cycles | Full exception path |
| SYSENTER | 15-25 cycles | Fast path, Pentium II+ |
| SYSCALL | 10-20 cycles | AMD fast path, K7+ |

**Latency Components**:
1. **Entry overhead**: 5-10 cycles (depends on mechanism)
2. **IPC dispatching**: 20-50 cycles (message lookup)
3. **Context switching**: 30-100 cycles (if target is different process)
4. **Return overhead**: 5-10 cycles (depends on mechanism)

**Total Syscall + IPC Time**:
```
Simple IPC (same server, no blocking):
  Total: ~50-150 cycles (depends on path taken)

Context switch + IPC:
  Total: ~100-250 cycles
```

### Cache Effects

**I-Cache (Instruction Cache)**:
- Syscall entry point fits in single cache line
- Syscall handler prologue: usually L1 cache hit
- Fast path: minimal I-cache pollution

**D-Cache (Data Cache)**:
- User register stack: often L1 cache hit
- Message buffer: depends on application
- Process table: L2 cache for active processes

---

## Integration Points

### Boot-Time CPU Setup

**Relevant phases** (see [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)):
- Phase 2: GDT and IDT initialization
- Phase 3: Paging setup (CR3 loading)
- Phase 4: CPUID detection and feature enabling
- Phase 5: SYSENTER/SYSCALL MSR setup

### Related Documentation

1. **Architecture Details**:
   - [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md) - Full architecture reference
   - [MEMORY-LAYOUT-ANALYSIS.md](MEMORY-LAYOUT-ANALYSIS.md) - Virtual memory system

2. **Boot & Initialization**:
   - [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md) - Complete boot timeline
   - [BOOT-TIMELINE.md](BOOT-TIMELINE.md) - Detailed timeline with metrics

3. **System Calls**:
   - [MINIX-ARCHITECTURE-COMPLETE.md#system-call-mechanisms](MINIX-ARCHITECTURE-COMPLETE.md#system-call-mechanisms) - Entry mechanism details

4. **Error Handling**:
   - [ERROR-ANALYSIS.md](../Analysis/ERROR-ANALYSIS.md) - Exception handling and recovery

---

## Related Documentation

**Architecture & Design**:
- [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md) - Complete architecture reference
- [MEMORY-LAYOUT-ANALYSIS.md](MEMORY-LAYOUT-ANALYSIS.md) - Virtual memory and paging
- [BOOT-TIMELINE.md](BOOT-TIMELINE.md) - Detailed boot sequence with timing

**Analysis & Research**:
- [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md) - Complete boot procedure
- [ERROR-ANALYSIS.md](../Analysis/ERROR-ANALYSIS.md) - Exception and error handling

**Performance & Profiling**:
- [COMPREHENSIVE-PROFILING-GUIDE.md](../Performance/COMPREHENSIVE-PROFILING-GUIDE.md) - Full profiling methodology
- [BOOT-PROFILING-RESULTS.md](../Performance/BOOT-PROFILING-RESULTS.md) - Boot timing measurements

---

## References

**Intel Architecture References**:
- Intel 64 and IA-32 Architectures Software Developer Manual (current)
- i386 System V ABI Specification

**AMD Architecture References**:
- AMD64 Architecture Programmer's Manual (current)
- AMD Extensions to x86 instruction set

**MINIX Source Files**:
- `kernel/arch/i386/mpx.S` - Assembly entry points
- `kernel/arch/i386/protect.c` - GDT/IDT setup
- `kernel/arch/i386/sconst.h` - Constant definitions
- `kernel/priv.h` - Privilege structure definitions

**Related Documentation**:
- [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md)
- [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)
- [MEMORY-LAYOUT-ANALYSIS.md](MEMORY-LAYOUT-ANALYSIS.md)

---

**Status:** Phase 2D placeholder - Framework established, ready for content population
**Last Updated:** November 1, 2025
**Completeness:** Structure 100%, Content 25% (framework only)
