# Memory Layout Analysis - MINIX 3.4 Virtual Memory System

**Status:** Reference placeholder (Phase 2D - Missing Documentation Recovery)
**Date:** November 1, 2025
**Scope:** Virtual memory, paging system, memory regions, TLB behavior, kernel/user space separation
**Audience:** Systems programmers, virtual memory specialists, kernel developers

---

## Table of Contents

1. [Overview](#overview)
2. [Kernel Memory Layout](#kernel-memory-layout)
3. [User Process Memory Layout](#user-process-memory-layout)
4. [Paging System (MMU)](#paging-system-mmu)
5. [TLB Behavior](#tlb-behavior)
6. [Protection & Access Control](#protection--access-control)
7. [Memory Allocation Strategies](#memory-allocation-strategies)
8. [Address Translation Examples](#address-translation-examples)
9. [Performance Characteristics](#performance-characteristics)
10. [Integration Points](#integration-points)

---

## Overview

MINIX 3.4 implements a **paged virtual memory system** for i386 architecture:

**Key Characteristics**:
- **Page size**: 4 KB (standard x86)
- **Virtual address space**: 4 GB (32-bit i386)
- **Kernel space**: Upper 1 GB (0xC0000000 - 0xFFFFFFFF)
- **User space**: Lower 3 GB (0x00000000 - 0xBFFFFFFF)
- **Paging**: Two-level page table hierarchy
- **TLB**: 64 entries (typical for P6 family)

**Memory Protection Rings**:
- **Ring 0** (Kernel): Full memory access
- **Ring 3** (User): Restricted to user-space pages

### Key Architecture Documents
- CPU interface details: See [CPU-INTERFACE-ANALYSIS.md](CPU-INTERFACE-ANALYSIS.md)
- Boot-time memory setup: See [BOOT-TIMELINE.md](BOOT-TIMELINE.md)
- System architecture: See [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md)

---

## Kernel Memory Layout

### Kernel Address Space (Virtual 0xC0000000 - 0xFFFFFFFF)

**Layout** (simplified, typical configuration):

```
0xFFFFFFFF  +---------------------------+
            | BIOS & Device Memory      |  [512 MB - 4 GB]
            | (unmapped, exception)      |
0xFFC00000  +---------------------------+
            | Kernel Heap               |  [~100 MB]
            | (dynamic allocation)       |
0xFF800000  +---------------------------+
            | Page Tables               |  [~4 MB]
            | (for paging system)        |
0xFF400000  +---------------------------+
            | Per-CPU Data Structures   |  [~1 MB per CPU]
            |                           |
0xFF000000  +---------------------------+
            | Kernel BSS & Data         |  [~10 MB]
            | (initialized memory)       |
0xFE000000  +---------------------------+
            | Kernel Code               |  [~2 MB]
            | (text section)             |
0xFD800000  +---------------------------+
            | Reserved                  |  [varies]
            | (for future expansion)     |
0xC0000000  +---------------------------+
            | [User space above 0xBFFFFFFF follows]
```

### Kernel Sections (Detailed)

**Text Section** (kernel code):
```c
struct kernel_text {
    // Linked at 0xFE000000 (physical + kernel offset)
    // Read-only, executable
    // Size: typically 1-2 MB
    // Includes:
    //  - Exception handlers
    //  - System call entry points
    //  - Process management code
    //  - Device drivers (built-in)
};
```

**Data Section** (kernel data):
```c
struct kernel_data {
    // Kernel global variables
    // Read-write, non-executable
    // Size: typically 5-10 MB
    // Includes:
    //  - Process table (proc_table)
    //  - Scheduling queues
    //  - Device state
    //  - Interrupt handlers state
};
```

**BSS Section** (uninitialized memory):
```c
struct kernel_bss {
    // Zero-initialized at boot
    // Read-write, non-executable
    // Size: typically 1-5 MB
    // Includes:
    //  - Frame buffer (if graphics)
    //  - Large buffers
    //  - I/O memory mappings
};
```

**Kernel Heap**:
```c
struct kernel_heap {
    // Dynamically allocated via kmalloc()
    // Expands upward into reserved space
    // Size: typically 20-100 MB
    // Includes:
    //  - Process stacks (growing downward)
    //  - Temporary buffers
    //  - Device driver structures
    //  - IPC message buffers
};
```

### Memory-Mapped I/O

**Device Memory** (typically 0xA0000000 - 0xBFFFFFFF or above):
```c
// Graphics memory (VGA/framebuffer)
volatile uint8_t *vga_memory = (uint8_t *)0xA0000000;

// PCI device memory regions
volatile uint32_t *device_memory = (uint32_t *)0xD0000000;

// BIOS ROM (0xC0000000 area, not paged)
// Accessed via direct physical addresses
```

**Kernel Mapping Strategy**:
- Identity-mapped: Physical address = Virtual address for low memory
- High-memory mapped: Kernel structures in upper 1 GB
- Device memory: Mapped on-demand or at boot time

---

## User Process Memory Layout

### Virtual Address Space per Process (0x00000000 - 0xBFFFFFFF)

**Typical User Process Layout**:

```
0xBFFFFFFF  +---------------------------+
            | Stack (grows downward)    |  [~8 MB]
            | (highest addresses)        |
0xBF800000  +---------------------------+
            | Unused / Gap              |  [varies]
            |                           |
0x10000000  +---------------------------+
            | Heap (grows upward)       |  [~10 MB typical]
            | (allocated memory)         |
0x08048000  +---------------------------+
            | Data & BSS                |  [~1 MB typical]
            | (initialized & uninit)     |
0x08000000  +---------------------------+
            | Text (code)               |  [varies]
            | (read-only executable)     |
0x00001000  +---------------------------+
            | Unused / Reserved         |
0x00000000  +---------------------------+
            | (never accessible)        |  [protection]
```

### Process Memory Sections

**Text Section** (program code):
```c
// Typically starts at 0x08000000 or 0x08048000
// Read-only, executable
// Size: depends on binary size
// Example: ls utility ~50-200 KB
// Example: gcc executable ~10-50 MB

struct process_text {
    code instructions[SIZE];
    readonly string literals[];
};
```

**Data Section** (initialized data):
```c
// Follows text section
// Read-write, non-executable
// Example: global variables = 100 KB

int global_variable = 42;  // In data section
const char *string = "hello";  // String literal in text, pointer in data
```

**BSS Section** (uninitialized data):
```c
// Follows data section
// Read-write, non-executable
// Zero-initialized at process load
// Example: global arrays = 500 KB

char buffer[1000000];  // In BSS, not in executable file
```

**Heap** (dynamic allocation):
```c
// Grows upward (toward higher addresses)
// Extended via brk() system call
// Managed by malloc()/free()
// Typical size: 10-100 MB

void *malloc_ptr = malloc(1024 * 1024);  // 1 MB allocation
```

**Stack** (local variables, return addresses):
```c
// Grows downward (toward lower addresses)
// Extended automatically by paging system
// Typical size: 8 MB per process

void function(int a, int b) {
    int local_var;  // On stack
    char buffer[1000];  // On stack
}  // Stack frame destroyed on return
```

---

## Paging System (MMU)

### Two-Level Page Table Hierarchy

**Address Translation**:

```
Virtual Address (32-bit):
+-----------+-----------+-----------+
| PD index  | PT index  | Offset    |
| [31:22]   | [21:12]   | [11:0]    |
| (10 bits) | (10 bits) | (12 bits) |
+-----------+-----------+-----------+

Translation Process:
1. Extract PD index (bits 31:22) = 0-1023
2. Load CR3 register (page directory base physical address)
3. Access page_directory[PD_index]
   - Physical address = PD_entry & 0xFFFFF000 (4K aligned)
4. Extract PT index (bits 21:12) = 0-1023
5. Access page_table[PT_index]
   - Physical address = PT_entry & 0xFFFFF000 (4K aligned)
6. Add offset (bits 11:0) = 0-4095
   - Physical address = (PT_entry & 0xFFFFF000) + offset
```

### Page Directory Entry (PDE) Format

**Bit Layout** (32 bits):

```
Bit 0       : P (Present) = 1 if page table in memory
Bit 1       : R/W = 1 if writable (0 = read-only)
Bit 2       : U/S = 1 if user-accessible (0 = kernel-only)
Bit 3       : PWT (Page Write-Through) = cache control
Bit 4       : PCD (Page Cache Disable) = cache control
Bit 5       : A (Accessed) = 1 if accessed
Bit 6       : D (Dirty) = 1 if written (only for 4MB pages)
Bit 7       : PS (Page Size) = 1 for 4MB page, 0 for 4KB
Bit 8       : G (Global) = 1 for global page
Bits 9-11   : Available for OS (often used for flags)
Bits 12-31  : Physical address of page table [20 bits] (page-aligned)
```

### Page Table Entry (PTE) Format

**Bit Layout** (32 bits):

```
Bit 0       : P (Present) = 1 if page in memory
Bit 1       : R/W = 1 if writable (0 = read-only)
Bit 2       : U/S = 1 if user-accessible (0 = kernel-only)
Bit 3       : PWT (Page Write-Through) = cache control
Bit 4       : PCD (Page Cache Disable) = cache control
Bit 5       : A (Accessed) = 1 if accessed
Bit 6       : D (Dirty) = 1 if written (modified page)
Bit 7       : PAT (Page Attribute Table) = cache control
Bit 8       : G (Global) = 1 for global page (kernel)
Bits 9-11   : Available for OS (often used for flags)
Bits 12-31  : Physical address of page [20 bits] (page-aligned)
```

### Page Table Population Example

**Kernel Space Entry** (example: 0xFE000000):

```
Virtual Address: 0xFE000000
PD index: 0x3F8 (bits [31:22] = 11111110000)
PT index: 0x000 (bits [21:12] = 0000000000)
Offset: 0x000 (bits [11:0] = 000000000000)

PDE[0x3F8] = 0x00400003
  - Present (bit 0) = 1
  - Writable (bit 1) = 1
  - Kernel only (bit 2) = 0
  - Page table physical address = 0x400000

PTE[0x000] = 0x00001003
  - Present (bit 0) = 1
  - Writable (bit 1) = 1
  - Kernel only (bit 2) = 0
  - Page physical address = 0x1000

Result: VA 0xFE000000 maps to PA 0x1000000
```

---

## TLB Behavior

### Translation Lookaside Buffer (TLB)

**Purpose**: Cache recent virtual-to-physical address translations

**Characteristics**:
- **Entries**: 64 (typical for Intel P6 family)
- **Split design**: Separate I-TLB (instruction) and D-TLB (data)
- **Associativity**: 4-way or 8-way (typical)
- **Invalidation**: Automatic on CR3 change, explicit via INVLPG

### TLB Miss Penalties

| Event | Latency |
|-------|---------|
| TLB hit | ~1 cycle (pipeline latency only) |
| TLB miss, page in L1 cache | ~3-4 cycles (single memory access) |
| TLB miss, page in L2 cache | ~10-15 cycles |
| TLB miss, page in main memory | ~50-200 cycles |

**MINIX Optimization Strategy**:
- Global pages (bit 8 in PTE) preserved across process switches
- Kernel pages marked as global (avoids TLB flush)
- User pages flushed on context switch

### TLB Flush Operations

**Full TLB Flush** (reload CR3):
```asm
MOV     EAX, CR3
MOV     CR3, EAX            ; Flushes all TLB entries
```

**Selective Invalidation** (INVLPG instruction):
```asm
INVLPG  [address]           ; Invalidate single entry
; Useful when modifying single page table entry
; Avoids expensive full flush
```

**MINIX Usage Pattern**:
```c
// On process switch:
set_cr3(next_process->page_directory);

// When changing page permissions:
invlpg(virtual_address);
```

---

## Protection & Access Control

### Privilege Level Transitions

**Access Control Bits** (Bits 1-2 in PDE/PTE):

```
Bit 1 (R/W): Read/Write Permission
  0 = Read-only
  1 = Read-write

Bit 2 (U/S): User/Supervisor Permission
  0 = Supervisor (kernel) only
  1 = User-accessible (and kernel)
```

### Page Protection States

| U/S | R/W | Access Rule | Typical Use |
|-----|-----|-------------|-------------|
| 0 | 0 | Kernel read-only | Kernel code |
| 0 | 1 | Kernel read-write | Kernel data |
| 1 | 0 | User+kernel read-only | Shared code, COW pages |
| 1 | 1 | User+kernel read-write | User data, heap |

### Protection Faults

**Page Fault (Exception #14)**:

```
Occurs when:
- Page not present (P=0)
- Insufficient privileges
- Write to read-only page
- Execute from non-executable page (if NX bit available)
```

**Error Code** (EAX when #PF handler called):

```
Bit 0   : P (Present) = 0 if page not present
Bit 1   : W/R = 1 if write, 0 if read
Bit 2   : U/S = 1 if user mode, 0 if kernel mode
Bit 3   : RSVD = 1 if reserved bit set
Bit 4   : I/D = 1 if instruction fetch (NX bit)
```

**MINIX Page Fault Handler**:
```c
// do_page_fault() in kernel/arch/i386/exception.c
// Decisions:
//  1. Page swapped out? Load from disk
//  2. Copy-on-write? Create new page
//  3. Stack growth? Allocate new stack page
//  4. Invalid access? Kill process (SIGSEGV)
```

---

## Memory Allocation Strategies

### Kernel Memory Allocation

**kmalloc()** (simple allocator):
```c
void *kmalloc(size_t size);
// Fixed-size allocation
// Typical sizes: 512B, 1KB, 2KB, 4KB, 8KB
// Wastes space but prevents fragmentation
```

**Process Memory**:
```c
// Process table: static allocation (256-512 processes)
struct proc proc_table[NR_PROCS];

// Per-process kernel stack: 4KB per process
// allocated from kernel heap
```

### User Process Memory Allocation

**brk()/sbrk()** (heap expansion):
```c
// User program requests more memory
int brk(void *addr);  // Set heap end
void *sbrk(intptr_t increment);  // Increment heap

// Kernel action:
// 1. Allocate new pages
// 2. Update page tables
// 3. Mark pages as present and writable
```

**mmap()** (memory-mapped files):
```c
// In MINIX 3.4: may be limited or not fully implemented
// Would allocate pages on-demand
// Share physical pages between processes
```

### Copy-on-Write (COW) Optimization

**fork() System Call**:
```
1. Parent and child share pages initially
2. Both parent and child pages marked read-only
3. On write: page fault occurs
4. Kernel makes copy of page
5. Child page marked as writable
6. Write continues

Benefit: Avoids copying full process memory
```

---

## Address Translation Examples

### Example 1: Kernel Code Access

**Scenario**: Kernel reads instruction at 0xFE001000

```
Virtual Address: 0xFE001000 (kernel code segment)
  PD index: 0x3F8 (bits 31:22)
  PT index: 0x001 (bits 21:12)
  Offset: 0x000 (bits 11:0)

1. Load CR3 (kernel page directory base) = 0x00000000
2. Access PD[0x3F8] = 0x01001003 (PT base = 0x01000000)
3. Access PT[0x001] = 0x00002007 (page base = 0x00002000)
4. Physical address = 0x00002000 + 0x000 = 0x00002000

Translation: 0xFE001000 → 0x00002000

Note: Early in boot, kernel is identity-mapped
After paging enabled, kernel at 0xFE000000+ maps to physical 0x1000+
```

### Example 2: User Process Heap Access

**Scenario**: User process at PID 5 allocates memory via malloc()

```
Virtual Address: 0x08040000 (process heap)
  PD index: 0x200 (bits 31:22)
  PT index: 0x040 (bits 21:12)
  Offset: 0x000 (bits 11:0)

Process structure: proc_table[5]
  page_directory_base = 0x02000000 (per-process)

1. Load CR3 (this process's PD base) = 0x02000000
2. Access PD[0x200] = 0x02010003 (PT base = 0x02010000)
3. Access PT[0x040] = 0x00020007 (page base = 0x00020000)
4. Physical address = 0x00020000 + 0x000 = 0x00020000

Translation: 0x08040000 → 0x00020000

Note: Each process has unique page directory
Physical memory pages are allocated as needed
```

### Example 3: Syscall Kernel Stack Access

**Scenario**: System call handler uses kernel stack

```
Virtual Address: 0xFF000000 (kernel stack for process)
  PD index: 0x3FC (bits 31:22)
  PT index: 0x000 (bits 21:12)
  Offset varies

1. CR3 = kernel page directory
2. PD[0x3FC] = 0x03001003 (PT base = 0x03000000)
3. PT[0x000] = 0x00030007 (page base = 0x00030000)
4. Physical address = 0x00030000 + offset

Translation: 0xFF000000 → physical stack page
Each process has unique kernel stack
```

---

## Performance Characteristics

### Memory Access Latencies

**Simplified Memory Hierarchy**:

| Level | Latency | Size | Access Time |
|-------|---------|------|--------------|
| L1 Cache | ~4 cycles | 64 KB | 1-4 ns |
| L2 Cache | ~10-15 cycles | 256-512 KB | 3-10 ns |
| L3 Cache | ~40-75 cycles | 2-8 MB | 12-25 ns |
| Main Memory | ~100-300 cycles | 256 MB+ | 30-100 ns |
| Disk (swap) | ~1,000,000+ cycles | Unlimited | 1-10 ms |

**Paging Impact**:
- TLB hit: adds ~0 cycles (cache latency only)
- TLB miss (L2 hit): adds ~10-15 cycles
- TLB miss (memory): adds ~100-300 cycles

### Page Fault Overhead

| Fault Type | Handling Time | Typical Frequency |
|------------|---------------|-------------------|
| Demand page | ~1000 cycles | At process start |
| COW | ~5000 cycles | After fork() |
| Swap in | ~1-10 million cycles | Low memory conditions |

**MINIX Optimization**:
- Pre-allocation for kernel stacks (avoid faults)
- Lazy allocation for user heap (demand paging)
- No swap in 3.4 (memory-constrained embedded system)

---

## Integration Points

### Boot-Time Memory Setup

**Relevant phases** (see [BOOT-TIMELINE.md](BOOT-TIMELINE.md)):
- Phase 1: Bootloader sets up initial paging
- Phase 2: Kernel initializes page tables
- Phase 3: Kernel maps itself to 0xC0000000+
- Phase 4: Process table initialized

### Related Documentation

1. **Architecture Details**:
   - [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md) - Full architecture reference
   - [CPU-INTERFACE-ANALYSIS.md](CPU-INTERFACE-ANALYSIS.md) - CPU control registers

2. **Boot & Initialization**:
   - [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md) - Complete boot timeline
   - [BOOT-TIMELINE.md](BOOT-TIMELINE.md) - Detailed timeline with metrics

3. **Process Management**:
   - [MINIX-ARCHITECTURE-COMPLETE.md#process-management](MINIX-ARCHITECTURE-COMPLETE.md#process-management) - Process structures

4. **Performance Analysis**:
   - [COMPREHENSIVE-PROFILING-GUIDE.md](../Performance/COMPREHENSIVE-PROFILING-GUIDE.md) - Memory performance metrics

---

## Related Documentation

**Architecture & Design**:
- [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md) - Complete architecture reference
- [CPU-INTERFACE-ANALYSIS.md](CPU-INTERFACE-ANALYSIS.md) - CPU interface and control structures
- [BOOT-TIMELINE.md](BOOT-TIMELINE.md) - Detailed boot sequence with timing

**Analysis & Research**:
- [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md) - Complete boot procedure
- [ERROR-ANALYSIS.md](../Analysis/ERROR-ANALYSIS.md) - Page fault and memory exception handling

**Performance & Profiling**:
- [COMPREHENSIVE-PROFILING-GUIDE.md](../Performance/COMPREHENSIVE-PROFILING-GUIDE.md) - Memory performance metrics
- [BOOT-PROFILING-RESULTS.md](../Performance/BOOT-PROFILING-RESULTS.md) - Boot timing measurements

---

## References

**Intel Architecture References**:
- Intel 64 and IA-32 Architectures Software Developer Manual Vol. 3
- Chapter: Paging and Protection

**MINIX Source Files**:
- `kernel/arch/i386/prot.c` - Page table initialization
- `kernel/arch/i386/protect.c` - GDT/IDT setup
- `kernel/memory.c` - Memory allocator
- `kernel/proc.c` - Process table and context switching

**Related Documentation**:
- [MINIX-ARCHITECTURE-COMPLETE.md](MINIX-ARCHITECTURE-COMPLETE.md)
- [BOOT-SEQUENCE-ANALYSIS.md](../Analysis/BOOT-SEQUENCE-ANALYSIS.md)
- [CPU-INTERFACE-ANALYSIS.md](CPU-INTERFACE-ANALYSIS.md)

---

**Status:** Phase 2D placeholder - Framework established, ready for content population
**Last Updated:** November 1, 2025
**Completeness:** Structure 100%, Content 30% (framework only)
