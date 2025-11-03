# MINIX 3.4.0-RC6 Architecture Summary

**Date**: 2025-10-30
**Project**: MINIX CPU Interface Analysis
**Architecture**: i386 (32-bit x86) and earm (32-bit ARM)

---

## Supported Architectures

MINIX 3.4.0-RC6 supports **two architectures**:

1. **i386** (32-bit x86): Primary architecture for x86 processors
2. **earm** (32-bit ARM): ARM embedded platform support

**NOT SUPPORTED**: x86-64 (long mode, 64-bit)

**Verification**: `/home/eirikr/Playground/minix/minix/kernel/arch/` contains only `i386/` and `earm/` subdirectories.

---

## i386 Register Set (32-bit)

### General Purpose Registers:
- **EAX**: Accumulator (return values, syscall params)
- **EBX**: Base register (syscall params)
- **ECX**: Counter (syscall params, **clobbered by SYSCALL instruction**)
- **EDX**: Data (syscall params, **receives ECX value before SYSCALL**)
- **ESI**: Source index (saved ESP during syscall)
- **EDI**: Destination index (syscall type: IPCVEC, KERVEC)
- **EBP**: Base pointer (process structure pointer in kernel)
- **ESP**: Stack pointer

### Control Registers:
- **CR0**: Protection enable, paging enable (I386_CR0_PE, I386_CR0_PG)
- **CR3**: Page directory base address (physical)
- **CR4**: Extensions (PSE, PAE, PGE, MCE)
- **EFLAGS**: Flags register

### Segment Registers:
- **CS**: Code segment
- **DS**: Data segment
- **SS**: Stack segment
- **ES/FS/GS**: Extra segments

---

## System Call Mechanisms (i386)

### 1. INT (Software Interrupt)

**Entry**: `ipc_entry_softint_um` (mpx.S:269)
**Vector**: INT 0x21 (IPC_VECTOR_UM)
**Registers**: EAX, EBX, ECX (syscall params)

**Hardware Actions**:
- Push SS, ESP, EFLAGS, CS, EIP (5 values, automatic)
- Load CS:EIP from IDT entry
- Set CPL=0

**Kernel Actions**:
- `SAVE_PROCESS_CTX(0, KTS_INT_UM)` - manual register save
- Call `do_ipc()`
- Return via `IRET`

**Performance**: ~1772 cycles (Skylake - benchmark, not MINIX-specific)

---

### 2. SYSENTER (Intel Fast Path)

**Entry**: `ipc_entry_sysenter` (mpx.S:220)
**Prerequisites**: Pentium II+, MSRs configured
**Registers**: EDI (call type), EAX, EBX, ECX (params), ESI (saved ESP), EDX (saved EIP)

**MSR Setup** (protect.c:183-187):
```c
ia32_msr_write(INTEL_MSR_SYSENTER_CS, 0, KERN_CS_SELECTOR);
ia32_msr_write(INTEL_MSR_SYSENTER_ESP, 0, t->sp0);  // TSS kernel stack
ia32_msr_write(INTEL_MSR_SYSENTER_EIP, 0, (u32_t) ipc_entry_sysenter);
```

**Hardware Actions**:
- Load CS from MSR (kernel code segment)
- Load ESP from MSR (kernel stack)
- Load EIP from MSR (entry point)
- Set CPL=0, disable interrupts
- **No automatic state save**

**Kernel Actions**:
- User must save ESP→ESI, EIP→EDX before SYSENTER
- Kernel saves ESI→SPREG, EDX→PCREG
- Shared path: `syscall_sysenter_common` (mpx.S:240)
- Return via `SYSEXIT` (EIP←EDX, ESP←ECX)

**Performance**: ~1305 cycles (Skylake - benchmark)

---

### 3. SYSCALL (AMD/Intel, 32-bit mode)

**Entry**: `ipc_entry_syscall_cpu#` (mpx.S:202, per-CPU variants 0-7)
**Prerequisites**: AMD K6+ or Intel (late), EFER.SCE enabled
**Registers**: EDI (call type), EAX, EBX, **ECX (clobbered!)**, EDX (receives ECX value), ESI (saved ESP)

**MSR Setup** (protect.c:190-203):
```c
ia32_msr_write(AMD_MSR_EFER, 0, ia32_msr_read(AMD_MSR_EFER, 0) | AMD_EFER_SCE);
// STAR MSR: bits [47:32] = kernel EIP, [63:48] = CS/SS selectors
ia32_msr_write(AMD_MSR_STAR, cpu, <configured per-CPU>);
```

**Hardware Actions** (32-bit SYSCALL):
- **ECX ← EIP** (return address - clobbers ECX!)
- Save EFLAGS internally (not to R11 like x86-64)
- Load EIP from STAR[47:32]
- Load CS/SS from STAR[63:48]
- Mask EFLAGS, set CPL=0

**Kernel Actions** (mpx.S:202-218):
```assembly
xchg %ecx, %edx              # Swap ECX↔EDX (restore params)
mov  k_percpu_stacks+4*cpu, %esi  # Load per-CPU stack
mov  (%esi), %ebp            # Get proc ptr from stack
movl $KTS_SYSCALL, P_KERN_TRAP_STYLE(%ebp)
xchg %esp, %esi              # Swap to kernel stack
jmp  syscall_sysenter_common
```

**Return Path** (mpx.S:414-432):
```assembly
mov PCREG(%ebp), %ecx   # Load return EIP → ECX
mov SPREG(%ebp), %esp   # Restore user stack
mov AXREG(%ebp), %eax   # Return values
sysret                  # 32-bit SYSRET: EIP←ECX, restore EFLAGS
```

**Performance**: ~1439 cycles (Skylake x86-64 benchmark - i386 may differ)

**Critical Difference from x86-64 SYSCALL**:
- i386: ECX ← EIP (32-bit), internal EFLAGS save
- x86-64: RCX ← RIP (64-bit), R11 ← RFLAGS
- i386: Uses STAR MSR bits [47:32] for EIP
- x86-64: Uses LSTAR MSR for RIP

---

## Memory Management (i386)

### Virtual Address Space

- **32-bit addressing**: 4 GB maximum address space (2^32)
- **User space**: 0x00000000 - 0xBFFFFFFF (3 GB typically)
- **Kernel space**: 0xC0000000 - 0xFFFFFFFF (1 GB typically)

### Paging Architecture

**Mode**: Standard 2-level paging with PSE (Page Size Extension) support

**Virtual Address Breakdown** (32-bit):
```
[31:22]  [21:12]  [11:0]
10 bits  10 bits  12 bits
PDE idx  PTE idx  Offset
```

**CR3 Register**:
- Points to Page Directory physical base address
- Written during context switch (triggers TLB flush)

**Page Directory (PD)**: Level 1
- 1024 entries (I386_VM_DIR_ENTRIES)
- Each entry: 32 bits
- Indexed by VA[31:22]
- Points to Page Table or 4 MB page (if PSE bit set)

**Page Table (PT)**: Level 2
- 1024 entries (I386_VM_PT_ENTRIES)
- Each entry: 32 bits
- Indexed by VA[21:12]
- Points to 4 KB physical page frame

**Page Sizes**:
- **4 KB** (I386_PAGE_SIZE): Standard page via PT
- **4 MB** (I386_BIG_PAGE_SIZE): Large page via PSE bit in PDE

**MINIX Configuration** (pg_utils.c:229-230):
```c
/* Our page table contains 4MB entries. */
cr4 |= I386_CR4_PSE;  // Enable Page Size Extension
```

### Page Directory Entry (PDE) Format (32 bits)

```
[31:12] Page table base address (20 bits) OR 4MB page frame if PS=1
[11:9]  Available for OS use
[8]     G - Global page (if CR4.PGE=1)
[7]     PS - Page Size (0=4KB, 1=4MB)
[6]     Reserved (0)
[5]     A - Accessed
[4]     PCD - Cache disable
[3]     PWT - Write-through
[2]     U/S - User/Supervisor
[1]     R/W - Read/Write
[0]     P - Present
```

**Key Constants** (vm.h):
```c
#define I386_VM_BIGPAGE      0x080    // 4MB page flag
#define I386_VM_DIR_ENTRIES  1024
#define I386_VM_DIR_ENT_SHIFT 22
```

### Page Table Entry (PTE) Format (32 bits)

```
[31:12] Physical frame address (20 bits, 4KB-aligned)
[11:9]  Available for OS
[8]     G - Global page
[7]     Reserved (0)
[6]     D - Dirty
[5]     A - Accessed
[4]     PCD - Cache disable
[3]     PWT - Write-through
[2]     U/S - User/Supervisor
[1]     R/W - Read/Write
[0]     P - Present
```

**Key Constants** (vm.h):
```c
#define I386_VM_PT_ENTRIES   1024
#define I386_VM_PT_ENT_SHIFT 12
#define I386_VM_PT_ENT_MASK  0x3FF
#define I386_VM_ADDR_MASK    0xFFFFF000  // 4KB page
#define I386_VM_ADDR_MASK_4MB 0xFFC00000 // 4MB page
```

### Address Translation Algorithm (2-level)

1. Extract PDE index: `i = VA[31:22]` (10 bits)
2. Read PDE: `PDE = *(CR3 + i*4)`
3. Check PDE.P (present bit)
4. If PDE.PS=1: **4 MB page**, PA = PDE[31:22] | VA[21:0]
5. Else: Extract PTE index: `j = VA[21:12]` (10 bits)
6. Read PTE: `PTE = *(PDE[31:12] + j*4)`
7. Check PTE.P (present bit)
8. Extract physical frame: `PFN = PTE[31:12]`
9. Combine with offset: `PA = PFN | VA[11:0]`

**TLB Optimization**:
- TLB hit: 1 cycle (translation cached)
- TLB miss: 200+ cycles (2 memory accesses: PD + PT lookup)
- TLB flush: Write CR3 or INVLPG instruction

### PAE Mode (Optional)

**Detection** (pg_utils.c:211-213):
```c
#ifdef PAE
    if(_cpufeature(_CPUF_I386_PAE) == 0)
        panic("kernel built with PAE support, CPU seems to lack PAE support?\n");
#endif
```

**PAE Characteristics** (if enabled):
- 3-level paging: PDPT → PD → PT
- 36-bit physical addressing (64 GB)
- 4 PDPT entries (VA[31:30])
- 512 PD/PT entries per table (9-bit indexing)
- PDE/PTE: 64 bits (expanded from 32 bits)

**MINIX Default**: PAE is **optional** compile-time flag, not default

---

## TLB (Translation Lookaside Buffer)

### Types
- **L1 DTLB**: Data TLB (first-level cache of translations)
- **L1 ITLB**: Instruction TLB (separate for code fetches)
- **L2 STLB**: Shared TLB (second-level, unified)

### Performance
- **Hit**: 1 cycle (cached translation)
- **Miss**: 200+ cycles (i386 2-level page walk)
- **Hit Rate**: >99% typical

### TLB Entry Format
```
Tag: Virtual Page Number (VPN)
PFN: Physical Frame Number
Flags: V (valid), G (global), D (dirty), U/S, R/W, X
```

### TLB Invalidation

**Global Flush** (mpx.S, pg_utils.c):
```c
write_cr3(phpagedir);  // Flushes all non-global entries
```

**Single Page** (via INVLPG):
```assembly
invlpg <linear-address>  // Flush single TLB entry
```

**Context Switch Cost**:
- Direct cost: Save regs (200) + CR3 write (100) + Restore regs (200) = **500 cycles**
- Indirect cost: TLB warmup (~100 misses × ~200 cycles/miss) = **~2000 cycles**
- **Total**: ~2500 cycles per context switch

**Mitigation Strategies**:
- **Global pages**: CR4.PGE=1, PTE.G=1 → not flushed on CR3 write
- **PCID**: Not available on i386 (x86-64 feature)
- **Large pages**: Fewer TLB entries needed (4 MB vs 4 KB)
- **Process affinity**: Reduce context switch frequency

---

## Key Source Files

### i386 Kernel Architecture

**`/home/eirikr/Playground/minix/minix/kernel/arch/i386/`**:
- **mpx.S**: Low-level entry/exit code, syscall handlers
- **protect.c**: GDT/IDT/TSS setup, MSR configuration, CPU feature detection
- **pg_utils.c**: Paging setup, CR3/CR4 management

**`/home/eirikr/Playground/minix/minix/kernel/arch/i386/include/`**:
- **archconst.h**: GDT layout, MSR addresses, trap styles, interrupt vectors
- **vm.h**: Paging constants (I386_VM_*, I386_CR0/CR4_*)

### Key Code Locations

**INT Entry**: mpx.S:265-300
```assembly
ENTRY(ipc_entry_softint_um)
    SAVE_PROCESS_CTX(0, KTS_INT_UM)
    jmp ipc_entry_common
```

**SYSENTER Entry**: mpx.S:220-260
```assembly
ENTRY(ipc_entry_sysenter)
    mov (%esp), %ebp  /* get proc from TSS.sp0 */
    movl $KTS_SYSENTER, P_KERN_TRAP_STYLE(%ebp)
    ...
    jmp syscall_sysenter_common
```

**SYSCALL Entry**: mpx.S:192-218
```assembly
#define ipc_entry_syscall_percpu(cpu)
ENTRY(ipc_entry_syscall_cpu ## cpu)
    xchg %ecx, %edx   /* ECX clobbered, swap with EDX */
    ...
```

**Common Path**: mpx.S:240
```assembly
syscall_sysenter_common:
    mov %esi, SPREG(%ebp)  /* save user ESP */
    mov %edx, PCREG(%ebp)  /* save return EIP */
    ...
    jmp ipc_entry_common
```

**IPC Handler**: mpx.S:273
```assembly
ENTRY(ipc_entry_common)
    push %ebp
    push %ebx
    push %eax
    push %ecx
    call _C_LABEL(context_stop)
    call _C_LABEL(do_ipc)
```

**MSR Setup**: protect.c:183-203
```c
/* SYSENTER */
if(minix_feature_flags & MKF_I386_INTEL_SYSENTER) {
    ia32_msr_write(INTEL_MSR_SYSENTER_CS, 0, KERN_CS_SELECTOR);
    ia32_msr_write(INTEL_MSR_SYSENTER_ESP, 0, t->sp0);
    ia32_msr_write(INTEL_MSR_SYSENTER_EIP, 0, (u32_t) ipc_entry_sysenter);
}

/* SYSCALL */
if(minix_feature_flags & MKF_I386_AMD_SYSCALL) {
    ia32_msr_write(AMD_MSR_EFER, 0, ... | AMD_EFER_SCE);
    /* Per-CPU STAR MSR setup */
}
```

**Paging Enable**: pg_utils.c:204-245
```c
void vm_enable_paging(void) {
    cr4 |= I386_CR4_PSE;  /* 4MB pages */
    write_cr4(cr4);
    cr0 |= I386_CR0_PG;   /* Enable paging */
    write_cr0(cr0);
    if(pgeok) cr4 |= I386_CR4_PGE;  /* Global pages */
}
```

---

## Critical Differences: i386 vs x86-64

| Feature | i386 (32-bit) | x86-64 (64-bit) |
|---------|---------------|-----------------|
| **Registers** | EAX, EBX, ECX, EDX, ESI, EDI, EBP, ESP | RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP + R8-R15 |
| **Address Size** | 32-bit (4 GB) | 64-bit (limited to 48-bit canonical, 256 TB) |
| **Paging Levels** | 2 (PD→PT) or 3 with PAE (PDPT→PD→PT) | 4 (PML4→PDPT→PD→PT) or 5 with LA57 |
| **Page Table Entries** | 32-bit (1024 per level) | 64-bit (512 per level, 9-bit index) |
| **SYSCALL ECX** | ECX ← EIP (clobbered, user saves to EDX) | RCX ← RIP (clobbered) |
| **SYSCALL Flags** | Internal save (restored by SYSRET) | R11 ← RFLAGS |
| **SYSCALL MSRs** | STAR (bits [47:32]=EIP, [63:48]=CS/SS) | LSTAR (64-bit RIP), STAR (CS/SS), FMASK |
| **SYSENTER/SYSEXIT** | Full support (EIP←EDX, ESP←ECX) | Exists but discouraged (use SYSCALL instead) |
| **CR3 Format** | 32-bit PD base (4KB-aligned) | 64-bit PML4 base (4KB-aligned, canonical) |
| **TLB Miss Cost** | ~200 cycles (2 memory accesses) | ~400 cycles (4 memory accesses) |
| **Large Pages** | 4 MB (PSE) | 2 MB (PD), 1 GB (PDPT) |

---

## Performance Summary

### System Call Costs (Skylake benchmarks - x86-64, not MINIX i386)

| Mechanism | Cycles | Notes |
|-----------|--------|-------|
| INT | ~1772 | Slowest, most portable |
| SYSENTER | ~1305 | Fastest on Intel |
| SYSCALL | ~1439 | Comparable to SYSENTER |

**Caveats**:
- These are **x86-64 Linux** measurements, not MINIX i386
- Spectre/Meltdown mitigations add ~10x overhead (pre-mitigation: ~70 cycles)
- Actual MINIX i386 performance may differ significantly

### Context Switch Costs

| Component | Cycles | Type |
|-----------|--------|------|
| Save registers | ~200 | Direct |
| Write CR3 (TLB flush) | ~100 | Direct |
| Restore registers | ~200 | Direct |
| **TLB warmup** | **~2000** | **Indirect (dominates)** |
| **Total** | **~2500** | |

**Real-World**: 2-5 µs @ 3 GHz (6000-15000 cycles including scheduler overhead)

---

## Recommendations for Phase 3 (MCP Integration)

1. **DeepWiki MCP**: Integrate for MINIX online documentation access
2. **Filesystem MCP**: Local MINIX codebase exploration via MCP
3. **Analysis MCP**: Expose Phase 1 Python tools (symbol extraction, call graph generation)
4. **Architecture Queries**: Create MCP tools for "What architecture?", "Show register set", etc.

## Recommendations for Phase 4 (Wiki Generation)

1. Generate wiki pages from this architecture summary
2. Auto-generate register reference tables
3. Create interactive syscall flow diagrams
4. Link wiki to actual MINIX source code locations

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Verified Against**: MINIX 3.4.0-RC6 source code (`/home/eirikr/Playground/minix/`)
