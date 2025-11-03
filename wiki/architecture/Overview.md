# Architecture Overview

**MINIX 3.4.0-RC6 i386 CPU Interface Analysis**

---

## Introduction

This module provides comprehensive analysis of how the MINIX 3 microkernel interfaces with the Intel i386 CPU architecture at the lowest level. It identifies every contact point where the kernel directly manipulates CPU state, including privileged instructions, register access, and hardware structures.

---

## Key Findings

### CPU Contact Points
- **7 major categories** with 50+ specific interface locations
- **Privilege Levels**: Ring 0 (kernel) and Ring 3 (user/servers)
- **System Call Mechanisms**: Three distinct paths (INT, SYSENTER, SYSCALL)
- **Context Switch Complexity**: ~200 lines of assembly handling CPU state transitions

### System Call Performance
- **SYSENTER**: 1305 cycles (fastest)
- **INT 0x80**: 1772 cycles (26% slower)
- **SYSCALL**: 1439 cycles (10% slower than SYSENTER)

### Memory Management
- **2-level paging**: 4KB pages with 1024-entry PDE/PTE
- **TLB Architecture**: 32-entry data TLB, 32-entry instruction TLB
- **TLB Miss Cost**: 200+ cycles vs 1-cycle hits
- **Context Switch**: 3000-5000 cycles with TLB flush overhead

---

## System Call Mechanisms

### 1. INT 0x80 (Legacy Path)

**Entry Points**:
- `ipc_entry_softint_orig` (mpx.S:265) - Original trap gate
- `ipc_entry_softint_um` (mpx.S:269) - User-mapped variant

**CPU Instructions**:
- Entry: `INT 0x33`
- Exit: `IRET`

**Hardware Actions**:
1. CPU pushes SS, ESP, EFLAGS, CS, EIP onto kernel stack
2. Loads kernel CS:EIP from IDT entry
3. Switches to kernel stack (from TSS.ESP0)

**Performance**: 1772 cycles (slowest due to microcode overhead)

### 2. SYSENTER (Intel Fast System Call)

**Entry Point**:
- `ipc_entry_sysenter` (mpx.S:220)

**CPU Instructions**:
- Entry: `SYSENTER`
- Exit: `SYSEXIT` (mpx.S:412)

**Special Requirements**:
- MSRs pre-configured: IA32_SYSENTER_CS, IA32_SYSENTER_ESP, IA32_SYSENTER_EIP
- NO automatic state save (userland saves context)
- ESP loaded from TSS.ESP0 via MSR

**Register Convention**:
- ESI = return ESP
- EDX = return EIP

**Performance**: 1305 cycles (fastest, 26% faster than INT)

### 3. SYSCALL (AMD Fast System Call)

**Entry Points**:
- `ipc_entry_syscall_cpu0` through `ipc_entry_syscall_cpu7`
- Per-CPU entry (8 separate entry points)

**CPU Instructions**:
- Entry: `SYSCALL`
- Exit: `SYSRET` (mpx.S:432)

**Register Convention**:
- ECX ↔ EDX swap (roles reversed vs. SYSENTER)
- ECX contains return EIP (for SYSRET)
- ESP restored manually

**Performance**: 1439 cycles (10% slower than SYSENTER)

---

## Memory Management

### Page Table Structure

**2-Level Hierarchy**:
```
CR3 → Page Directory (1024 entries)
        ↓
      Page Table (1024 entries)
        ↓
      Physical Page (4KB)
```

**Page Directory Entry (PDE)**:
- Bits 31-12: Physical base address of page table
- Bit 7: Page size (0 = 4KB, 1 = 4MB)
- Bit 6: Dirty (written to)
- Bit 5: Accessed
- Bit 2: User/Supervisor
- Bit 1: Read/Write
- Bit 0: Present

**Page Table Entry (PTE)**:
- Same structure as PDE
- Points to 4KB physical page

### TLB Architecture

**Data TLB**:
- 32 entries (4-way set associative on Pentium)
- Caches virtual → physical mappings
- Invalidated on CR3 write (context switch)

**Instruction TLB**:
- 32 entries (separate from data TLB)
- Caches code page mappings

**Performance Impact**:
- TLB hit: 1 cycle
- TLB miss: 200+ cycles (page table walk)

### Context Switch Cost

**Total**: 3000-5000 cycles

**Breakdown**:
1. Save process context: ~200 cycles
2. TLB flush (CR3 write): ~1000 cycles
3. Load new context: ~200 cycles
4. Pipeline refill: ~500 cycles
5. TLB warmup: ~1000-2000 cycles

---

## Interrupt Handling

### Hardware Interrupts

**Master PIC (IRQ 0-7)**:
- hwint00: Clock timer (PIT)
- hwint01: Keyboard
- hwint02: Cascade to slave PIC
- hwint03-04: Serial ports
- hwint05-07: Parallel, FDD, etc.

**Slave PIC (IRQ 8-15)**:
- hwint08: RTC
- hwint09: Redirected IRQ2
- hwint13: FPU exception
- hwint14-15: IDE controllers

**Entry Mechanism**:
1. Hardware raises IRQ line
2. PIC signals CPU via INTR pin
3. CPU vectors to `hwintXX` entry in IDT
4. Assembly macro saves context
5. C handler `irq_handle(irq)` processes interrupt
6. Send EOI to PIC (OUT to port 0x20/0xA0)
7. Jump to `switch_to_user`

### APIC (Advanced Programmable Interrupt Controller)

**Features**:
- Per-CPU local APIC
- I/O APIC for multi-CPU systems
- Message-based interrupt delivery
- Support for 240+ interrupt vectors

**Files**:
- `minix/kernel/arch/i386/apic.c` (32KB)
- `minix/kernel/arch/i386/apic_asm.S` (12KB)

---

## Diagrams

This module includes 11 TikZ diagrams:

1. **System Call Flow** (INT, SYSENTER, SYSCALL)
2. **Page Table Hierarchy** (CR3 → PD → PT → Page)
3. **TLB Architecture** (Data/Instruction TLBs)
4. **Context Switch Timeline** (Process A → B)
5. **Interrupt Handling** (PIC → CPU → Handler)
6. **Memory Layout** (Kernel/User address spaces)
7. **Privilege Rings** (Ring 0-3)
8. **CPU State Save/Restore** (Register preservation)
9. **Performance Comparison** (Syscall mechanisms)
10. **TLB Miss Penalty** (Hit vs Miss)
11. **Context Switch Cost** (Component breakdown)

All diagrams available in CVD-safe variants (protanopia, deuteranopia, tritanopia, monochromacy).

---

## Source Files

### Assembly Entry Points
- `minix/kernel/arch/i386/mpx.S` - System call entry/exit
- `minix/kernel/arch/i386/apic_asm.S` - APIC handlers

### C Implementation
- `minix/kernel/arch/i386/arch_system.c` - System call implementation
- `minix/kernel/arch/i386/memory.c` - Paging and TLB management
- `minix/kernel/arch/i386/apic.c` - APIC configuration

### Headers
- `minix/kernel/arch/i386/sconst.h` - Context save macros
- `minix/kernel/arch/i386/include/vm.h` - Memory management constants

---

## Research Applications

### Use Cases
1. **OS Course Labs**: Understanding x86 privilege levels and system calls
2. **Security Research**: Analyzing kernel/user transitions and attack surfaces
3. **Performance Tuning**: Selecting optimal syscall mechanism for workload
4. **Microkernel Design**: Studying minimal kernel contact points

### Academic References
- Tanenbaum & Woodhull: *Operating Systems: Design and Implementation*
- Intel: *IA-32 Intel Architecture Software Developer's Manual*
- AMD: *AMD64 Architecture Programmer's Manual*

---

## Related Documentation

- [Full CPU Interface Paper](../modules/cpu-interface/docs/MINIX-CPU-INTERFACE-ANALYSIS.md)
- [ISA-Level Analysis](../modules/cpu-interface/docs/ISA-LEVEL-ANALYSIS.md)
- [Style Guide](../style-guide/Overview.md)
- [MCP Server API](../api/MCP-Servers.md)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Architecture**: i386 (32-bit)
