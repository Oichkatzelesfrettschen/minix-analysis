# MINIX 3.4 Boot Sequence and Process Creation Analysis

**Status:** Consolidated reference document (Phase 2B)
**Date:** November 1, 2025
**Scope:** Complete boot sequence, process creation, and process lifecycle
**Architecture:** i386 (32-bit x86)
**MINIX Version:** 3.4.0-RC6

---

## Executive Summary

This document provides a comprehensive trace of MINIX 3.4 operation from bootloader entry through complete system initialization and process lifecycle management. It covers:

- **Boot Sequence**: Bootloader → protected mode → kernel initialization
- **Process Creation**: Fork syscall mechanics and process table updates
- **Process Execution**: Exec syscall and address space transition
- **Context Switching**: Context preservation and process switching during fork
- **CPU State Transitions**: Ring level changes, privilege transitions, register state
- **Memory Address Space**: Virtual-to-physical mappings throughout boot

---

## Table of Contents

1. [Boot Sequence Overview](#boot-sequence-overview)
2. [Bootloader Entry and Setup](#bootloader-entry)
3. [Protected Mode Initialization](#protected-mode)
4. [Paging and Memory Setup](#paging-setup)
5. [Kernel Initialization](#kernel-initialization)
6. [First Process Scheduling](#first-process)
7. [Process Creation (Fork)](#process-creation)
8. [Process Execution (Exec)](#process-execution)
9. [Context Switching](#context-switching)
10. [Runtime and Scheduling](#runtime-scheduling)
11. [References and Appendices](#references)

---

## Boot Sequence Overview

The MINIX 3.4 boot sequence implements a **6-phase initialization** from bootloader to first user process:

```
Phase 0: Bootloader Entry (Real Mode)
    ↓
Phase 1: Protected Mode Transition (32-bit mode, low memory)
    ↓
Phase 2: Paging Enablement (virtual memory activation)
    ↓
Phase 3: Kernel Initialization (GDT/IDT/TSS setup)
    ↓
Phase 4: Subsystem Initialization (timer, interrupts)
    ↓
Phase 5: Process Scheduling (first process execution)
```

**Timeline**: ~100-500 milliseconds (depends on hardware, IO operations)
**Code Entry Points**: `head.S` → `pre_init()` → `cstart()` → `main()` → `switch_to_user()`

---

## Bootloader Entry

### Entry Point Location

**File**: `minix/kernel/arch/i386/head.S` (line 40)
**Environment**: Real mode, A20 gate enabled
**Input**: Multiboot-compliant bootloader (GRUB)

### Bootloader Protocol (Multiboot)

The bootloader (GRUB) provides:

**Multiboot Header** (in kernel binary):
```
magic:     0x1BADB002
flags:     0x00000003 (memory map required)
checksum:  -(magic + flags)
```

**Multiboot Information Structure** (at boot, EBX = pointer):
```
mbi.flags          (bit 0: memory field valid)
mbi.mem_lower      (conventional memory below 1MB)
mbi.mem_upper      (memory above 1MB in KB)
mbi.boot_device    (boot device ID)
mbi.cmdline        (command line pointer)
mbi.mods_count     (number of modules loaded)
mbi.mods_addr      (module list address)
```

### Real Mode to Protected Mode Transition

**Pre-Transition Checks**:
1. A20 gate verified (allows access above 1MB)
2. GDT prepared with kernel segments
3. IDT prepared (initially minimal)

**Transition Sequence** (mpx.S:40-80):
```
1. Disable interrupts: CLI
2. Load GDT: LGDT [gdt_pointer]
3. Set CR0.PE: MOV CR0, EAX; OR EAX, 1; MOV EAX, CR0
4. Far jump: JMP 0x08:protected_start  ; flush prefetch queue
5. Protected mode entered, CPL = 0
6. Load DS/ES/SS: MOV AX, 0x10; MOV DS, AX; etc.
```

**Register State After Transition**:
- EIP: Protected mode code address
- CR0: PE=1 (Protected mode enabled), PG=0 (Paging disabled yet)
- CPL: Ring 0 (kernel)
- Memory: Still physical addresses (paging not yet enabled)

---

## Protected Mode Initialization

### Phase 1: Pre-Init Low-Level Setup

**Entry Function**: `pre_init()` (pre_init.c)
**Responsibility**: Parse multiboot info, set up initial paging structures

**Multiboot Information Extraction**:
```c
// From multiboot info at boot
u32_t mem_lower = mbi->mem_lower;  // Memory below 1MB
u32_t mem_upper = mbi->mem_upper;  // Memory above 1MB (in KB)
u32_t boot_devices = mbi->boot_device;
```

**Initial Page Table Setup**:
1. **Identity Mapping** (kernel at 0x00000000): Maps physical memory 1:1
2. **High Half Mapping** (kernel at 0x80000000): Maps kernel to high memory
3. **Bootstrap Page Directory**: Temporary directory used during boot

**Key Data Structures Created**:
```c
// In pre_init.c
extern u32_t __phys_base;  // Physical load address
extern u32_t __virt_base;  // Virtual kernel base (0x80000000)

// Page directory entries for identity and high mapping
pde_t kernel_pagetable[1024];  // 4MB coverage
pde_t identity_pagetable[1024]; // Physical 1:1 mapping
```

**Critical Transition**:
- Before: Physical addresses used
- After: Kernel operates at 0x80000000 (virtual)
- Mapping maintained: low memory accessible via identity map

---

## Paging Setup

### Enabling Virtual Memory

**Code Location**: `minix/kernel/arch/i386/mpx.S` (after pre_init)
**Instruction Sequence**:

```asm
; Load page directory base (CR3)
MOV EAX, kernel_pagetable_phys  ; Physical address of page directory
MOV CR3, EAX

; Enable paging in CR0
MOV EAX, CR0
OR  EAX, 0x80000000            ; Set CR0.PG (bit 31)
MOV CR0, EAX                    ; PAGING ENABLED!

; Execute near jump to flush TLB and prefetch queue
JMP continue_in_high_memory

; continue_in_high_memory now executes at 0x80xxxxxx
```

**Memory Layout Before Paging**:
```
Physical Memory Layout:
0x00000000 ───┐ Real Mode IVT / BIOS Data
0x00001000    │ Bootloader
0x00010000    │ MINIX Kernel
0x001XXXXX ───┘ (typically < 1MB for bootloader)
```

**Memory Layout After Paging**:
```
Virtual Address Space:
0x00000000 ─── Identity mapped to physical 0x00000000 (still accessible)
0x80000000 ─── Kernel code/data (mapped from physical 0x00010000 area)
0x80100000 ─── Kernel BSS (uninitialized data)
```

### Two-Level Page Table Structure

MINIX uses standard Intel two-level page tables:

```
Linear Address (32-bit):
┌─────────┬─────────┬──────────┐
│PDE(10b) │PTE(10b) │Offset(12b)│  = 32 bits total
└─────────┴─────────┴──────────┘
   10 bits   10 bits    12 bits

Translation:
1. CR3 points to page directory (physical)
2. PDE[linear>>22] gives page table address
3. PTE[linear>>12 & 0x3FF] gives page frame
4. Page frame + (linear & 0xFFF) = physical address
```

**Page Table Entry (PTE) Format** (32-bit):
```
31          12   11 10 9 8 7  6  5  4  3  2  1  0
┌──────────────────┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
│   Page Frame    │AV│ D│ A│  │CD│WT│ U│ W│ P│
└──────────────────┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
AV=Available  D=Dirty  A=Accessed  CD=Cache Disable
WT=Write-Through  U=User  W=Writable  P=Present
```

---

## Kernel Initialization

### Phase 2: Kernel Setup (cstart)

**Entry Function**: `cstart()` (start.c)
**Responsibility**: Initialize GDT, IDT, TSS, and subsystems

### GDT (Global Descriptor Table) Setup

**GDT Structure**: Four main entries for MINIX

| Selector | DPL | Type | Base | Limit | Purpose |
|----------|-----|------|------|-------|---------|
| 0x00 | - | - | 0 | 0 | Null (required) |
| 0x08 | 0 | Code | 0 | 4GB | Kernel code |
| 0x10 | 0 | Data | 0 | 4GB | Kernel data |
| 0x18 | 3 | Code | 0 | 4GB | User code |
| 0x20 | 3 | Data | 0 | 4GB | User data |

**GDT Register** (GDTR):
```asm
LGDT [gdt_pointer]  ; Load GDT base and limit
```

### IDT (Interrupt Descriptor Table) Setup

256 interrupt/exception handlers:

| Vector | Type | Handler | CPL | Purpose |
|--------|------|---------|-----|---------|
| 0-31 | Exception | Hardware exception handlers | 0 | Faults, traps, aborts |
| 32-47 | IRQ | Interrupt handlers | 0 | Hardware interrupts (PIC) |
| 33 (0x21) | Syscall | `ipc_entry_softint_um` | 3 | User syscalls |
| 48+ | (undefined) | - | - | Reserved |

**IDT Entry Format** (8 bytes):

```
┌──────────┬─────────┬──────┬────┬──────────┐
│ Offset   │Segment  │Flags │Res │ Offset   │
│31-16,0-7 │15-0     │7-0   │3-0 │31-16,0-7 │
└──────────┴─────────┴──────┴────┴──────────┘

Flags: D=32-bit, DPL=privilege, P=present
```

### TSS (Task State Segment) Setup

**TSS Structure** (used for privilege transitions):

```c
struct tss {
    u32_t ts_backlink;      // Previous TSS (for task switches)
    u32_t ts_esp0;          // Ring 0 stack pointer (kernel stack)
    u32_t ts_ss0;           // Ring 0 stack segment
    u32_t ts_esp1;          // Ring 1 stack (unused)
    u32_t ts_ss1;           // Ring 1 stack segment
    u32_t ts_esp2;          // Ring 2 stack (unused)
    u32_t ts_ss2;           // Ring 2 stack segment
    // ... more fields ...
};
```

**TSS Purpose**: Contains kernel stack address (ts_esp0) used during privilege transitions:
- When user → kernel (interrupt/syscall), CPU reads ts_esp0
- Kernel stack location set here, used for context saves

---

## First Process Scheduling

### Phase 3: Kernel Main and Scheduling

**Entry Function**: `main()` (main.c)
**Sequence**:
1. Initialize kernel subsystems (timer, memory)
2. Enable interrupts
3. Call first scheduler decision
4. Switch to first process

### CPU State at First IRET

**Before IRET** (kernel context):
```
EIP = user_entry_point (e.g., init)
CS  = 0x1B (user code segment, DPL=3)
ESP = user_stack_initial
SS  = 0x23 (user data segment, DPL=3)
EFLAGS = 0x0202 (IF=1, VIF=1, interrupts enabled)
```

**IRET Instruction** (reverse of INT):
```asm
IRET    ; Pop EIP, CS, EFLAGS (and ESP, SS if ring change)
        ; Load from kernel stack
        ; Return to user mode (CPL changes from 0 to 3)
        ; Execute at user EIP
```

**After IRET** (user process running):
- CPL = 3 (user mode)
- Execution starts at user process entry point
- User stack active
- Kernel unreachable (protection enabled)

---

## Process Creation (Fork)

### Fork System Call Mechanics

**System Call Path**: User `fork()` → INT 0x21 → `do_ipc()` → `do_fork()`

### Phase 1: User-Kernel Transition (Syscall)

**User Code** (libc/fork.c):
```c
// Register setup for fork
MOV EAX, fork_syscall_number  // System call number
MOV EBX, 0                     // No parent_pid needed for fork
MOV ECX, 0                     // No other args
INT 0x21                       // Invoke syscall
```

**Kernel Syscall Handler** (`ipc_entry_softint_um`):
1. Hardware actions: Push SS, ESP, EFLAGS, CS, EIP
2. Kernel entry: Save remaining registers
3. Dispatch: Call `do_ipc(fork_syscall_number, ...)`

### Phase 2: Kernel Process Creation

**do_fork() Responsibilities**:

1. **Allocate Process Table Entry**:
   ```c
   proc_ptr = &proc[next_proc_slot];  // Find free slot
   proc->p_flags = 0;                 // Initialize
   proc->p_rts_flags = SUSPENDED;     // Start suspended
   ```

2. **Copy Parent's Context**:
   ```c
   // Copy parent's registers to child
   for (i = 0; i < NR_REGS; i++) {
       proc->p_reg[i] = parent->p_reg[i];
   }
   // Child's return register (EAX) = 0 (fork return value for child)
   proc->p_reg[REG_AX] = 0;
   // Parent's return register will be set to child's PID
   parent->p_reg[REG_AX] = child_pid;
   ```

3. **Copy Address Space** (via VM):
   ```c
   // Tell VM to duplicate parent's address space for child
   msg_t m;
   m.m_type = VM_FORK;
   m.VM_PM_PID = child_pid;
   m.VM_PM_MEMBASE = parent_memory_map;
   send(VM_SERVER, &m);  // IPC to VM server
   // VM responds with mapping confirmation
   ```

4. **Initialize Child Process**:
   ```c
   proc->p_pid = child_pid;
   proc->p_parent = parent_pid;
   proc->p_rts_flags = RUNNABLE;  // Mark ready to run
   ```

5. **Return Values**:
   - Parent: EAX = child_pid (return to parent after IRET)
   - Child: EAX = 0 (when first scheduled, sees EAX=0)

### Process Table State After Fork

Before fork:
```
proc[0] (init):  pid=1, children=[], memory at 0x00000000
proc[1] (free):  available
```

After fork:
```
proc[0] (init):  pid=1, children=[2], memory at 0x00000000
proc[1] (child): pid=2, parent=1, memory at 0x10000000 (VM-allocated copy)
```

---

## Process Execution (Exec)

### Exec System Call

**Purpose**: Replace process image with new program
**System Call**: `execve(path, argv, envp)`

### Exec Implementation

1. **Load New Binary**:
   ```c
   // Tell VM to load executable
   msg_t m;
   m.m_type = VM_EXEC;
   m.VM_PM_PATH = executable_path;  // e.g., "/bin/sh"
   send(VM_SERVER, &m);
   ```

2. **VM Server Maps Binary**:
   - Read ELF header
   - Parse sections (text, data, bss)
   - Map at virtual address 0x08048000 (standard user text base)
   - Create new page tables

3. **Update Process Table**:
   ```c
   // Process retains PID but new memory image
   proc->p_rts_flags = SUSPENDED;  // Suspend while loading
   // VM signals completion
   proc->p_rts_flags = RUNNABLE;   // Ready after exec
   ```

4. **Register Setup for New Image**:
   ```c
   // Reset registers for new process
   proc->p_reg[REG_AX] = 0;        // Return value
   proc->p_reg[REG_BX] = 0;
   proc->p_reg[REG_SP] = new_stack_pointer;
   proc->p_reg[REG_IP] = executable_entry_point;
   ```

---

## Context Switching

### Context Preservation During Fork

When a child process is first scheduled:

**Kernel Scheduler** (`sched()` → `switch_to_user()`):
```c
// Retrieve child process from proc table
proc_ptr = &proc[child_pid];

// Restore child's registers from save area
MOV ESP, proc->p_reg[REG_SP]    // Child stack
// ... restore other registers ...
MOV EAX, 0                       // Fork return value for child
```

**IRET to Child**:
```asm
IRET    ; Return to user mode
        ; Child executes with EAX=0 (sees itself as fork() returning 0)
```

### Context Switch Overhead

**Register Save** (~50 cycles):
- 8-12 general purpose registers saved
- Segment selectors, status registers

**TLB Invalidation** (~100-500 cycles):
- New CR3 loaded (page directory)
- TLB entries invalidated by hardware (implicit with CR3 write)
- TLB refilled on first accesses (cache miss penalty)

**Cache Warming** (~1000-5000 cycles):
- Child's code not in L1i cache (miss penalty)
- Data not in L1d cache
- Depends on code size and CPU cache size

**Total Context Switch**: ~1000-6000 CPU cycles
**Process ready for execution** after ~6-10 microseconds (worst case)

---

## Runtime and Scheduling

### Timer Interrupt Handling

**Timer Interrupt** (INT 0x20, 18.2 Hz or higher):

1. **Interrupt Entry** (`i8259.c` - PIC handler)
2. **Increment Tick Counter**
3. **Scheduler Activation** (`sched()`)
4. **Process Priority Decay** (reduce CPU credits)
5. **Load Balancing** (move processes between queues)

### Scheduler Decision Points

After timer interrupt:
```c
if (current_process->ticks_remaining > 0) {
    // Current process continues
    return;
} else {
    // Find next runnable process
    next = find_next_runnable();
    if (next != current) {
        switch_to_user(next);  // Context switch
    }
}
```

---

## References

### Source Code Locations

| Component | File | Lines |
|-----------|------|-------|
| Boot entry | `minix/kernel/arch/i386/head.S` | 40-100 |
| Pre-init | `minix/kernel/pre_init.c` | 1-150 |
| Page setup | `minix/kernel/arch/i386/mpx.S` | 100-200 |
| Kernel main | `minix/kernel/main.c` | 1-300 |
| GDT/IDT | `minix/kernel/arch/i386/protect.c` | 100-300 |
| Fork impl. | `minix/kernel/system/do_fork.c` | 1-250 |
| Exec impl. | `minix/kernel/system/do_exec.c` | 1-200 |
| Scheduler | `minix/kernel/proc.c` | sched(), switch_to_user() |

### Related Documentation

- [MINIX Architecture Complete](../Architecture/MINIX-ARCHITECTURE-COMPLETE.md) - Architecture overview
- [Syscall Analysis](SYSCALL-ANALYSIS.md) - System call catalog
- [IPC System Analysis](IPC-SYSTEM-ANALYSIS.md) - Message passing internals
- [Performance Analysis](../Performance/COMPREHENSIVE-PROFILING-GUIDE.md) - Timing measurements

### Further Reading

1. **Tanenbaum & Woodhull**, "Operating Systems Design and Implementation" (MINIX 3 Book)
2. **Intel 64 and IA-32 Architectures Manual** (Protected mode, paging, syscalls)
3. **x86 Assembly Language Reference** (Machine-level details)
4. **MINIX Source Code** (minix/kernel/ - primary reference)

---

## Appendix A: CPU Register State Reference

### At Various Boot Points

| Point | EIP | CR0 | CR3 | CPL | Paging |
|-------|-----|-----|-----|-----|--------|
| Bootloader | Physical | PE=1 | ? | 0 | Off |
| Protected mode | Physical | PE=1 | 0 | 0 | Off |
| Paging enabled | Virtual | PE=1 | Kernel | 0 | On |
| First user proc | Virtual | PE=1 | User | 3 | On |

---

## Document Metadata

**Consolidated From:**
- BOOT-TO-KERNEL-TRACE.md (detailed boot phases)
- COMPREHENSIVE-BOOT-RUNTIME-TRACE.md (comprehensive system trace)
- FORK-PROCESS-CREATION-TRACE.md (process creation details)

**Total Source**: ~2,500 lines
**Consolidated**: November 1, 2025
**Format**: Markdown with comprehensive sectioning
**Audience**: OS developers, researchers, students

---

*Last Updated: November 1, 2025*
*Status: Phase 2B Consolidation - Boot Sequence Analysis*
*Next Phase: Cross-reference updates and additional consolidations*
