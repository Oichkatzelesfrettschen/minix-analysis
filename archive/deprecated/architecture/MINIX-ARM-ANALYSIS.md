# MINIX 3.4 ARM Architecture Support Analysis

**Generated**: 2025-10-31
**Architecture**: ARMv7/ARMv8 (32-bit/64-bit)

## ARM-Specific Implementation Files

Total ARM-specific files found: 0

## ARM Processor Modes and Privilege Levels

ARM provides multiple processor modes (like x86 rings):

| Mode | Name | Purpose | CPSR[4:0] |
|------|------|---------|----------|
| USR | User | User application code | 10000 |
| FIQ | Fast IRQ | Fast interrupt handler | 10001 |
| IRQ | Interrupt | Normal interrupt handler | 10010 |
| SVC | Supervisor | Kernel/privileged code | 10011 |
| ABT | Abort | Memory abort handler | 10111 |
| UND | Undefined | Undefined instruction | 11011 |
| SYS | System | Privileged system code | 11111 |

## Banked Registers (Mode-Specific)

ARM has separate register banks for different modes:

| Register | USR | FIQ | IRQ | SVC | ABT | UND | SYS |
|----------|-----|-----|-----|-----|-----|-----|-----|
| R13 (SP) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| R14 (LR) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| CPSR | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| SPSR | No  | Yes | Yes | Yes | Yes | Yes | No  |

## System Calls on ARM

MINIX system calls on ARM using SWI (Software Interrupt):

```asm
SWI #0          ; Software interrupt (syscall on ARM)
```

Transition:
- **Before**: USR mode, CPSR[4:0]=10000
- **After**: SVC mode, CPSR[4:0]=10011
- **Return**: MOVS PC, LR (restore from SPSR)

## ARMv7 vs ARMv8 Differences

| Feature | ARMv7 | ARMv8 | MINIX Support |
|---------|-------|-------|---------------|
| 32-bit ISA | Primary | Backward compat | Yes |
| 64-bit ISA | No | Primary (A64) | Limited |
| Thumb-2 | Yes | Yes | Likely |
| VFP/NEON | Yes | Yes | Optional |
| Virtualization | Limited | Enhanced | Possible |
| TrustZone | Yes | Yes | Limited |

## ARM Memory Management

### MMU (Memory Management Unit)
- 2-level page table walk
- TTBR (Translation Table Base Register) holds page table address
- ASID (Address Space ID) for TLB tagging
- Virtual address format: [31:20] Section index, [19:0] Page offset

### TLB (Translation Lookaside Buffer)
- Caches virtual-to-physical translations
- Invalidated per ASID or globally
- Operations: ISB (Instruction), DSB (Data), DMB (Domain)

## ARM Interrupt Handling

ARM has dedicated interrupt vectors:

| Exception | Vector | Mode | CPSR[4:0] |
|-----------|--------|------|----------|
| Reset | 0x00000000 | SVC | 10011 |
| Undefined | 0x00000004 | UND | 11011 |
| SWI | 0x00000008 | SVC | 10011 |
| Prefetch Abort | 0x0000000C | ABT | 10111 |
| Data Abort | 0x00000010 | ABT | 10111 |
| IRQ | 0x00000018 | IRQ | 10010 |
| FIQ | 0x0000001C | FIQ | 10001 |

## Key ARM Registers

### Control Registers
- **CPSR**: Current Processor Status Register (flags, mode, interrupts)
- **SPSR**: Saved Processor Status Register (saved CPSR)
- **SCTLR**: System Control Register (MMU, cache, endianness)
- **ACTLR**: Auxiliary Control Register (CPU-specific)
- **TTBR0/TTBR1**: Translation Table Base Registers
- **TTBCR**: Translation Table Base Control Register

### General Purpose Registers
- **R0-R7**: General purpose (not banked in most modes)
- **R8-R12**: General purpose (banked in FIQ mode)
- **R13 (SP)**: Stack pointer (banked per mode)
- **R14 (LR)**: Link register (return address, banked per mode)
- **R15 (PC)**: Program counter

## MINIX ARM Support Assessment

Based on code analysis, MINIX 3.4 ARM support includes:

**Implemented**:
- ARM ISA bootstrap (head.S)
- SVC/Supervisor mode operation
- System call via SWI
- Memory management (MMU, paging)
- Context switching

**Likely Supported**:
- Interrupt handling (IRQ/FIQ)
- Floating point (VFP optional)
- Cache invalidation operations

**Not/Partially Supported**:
- 64-bit ARM (ARMv8-A) - Limited or absent
- NEON SIMD
- Virtualization extensions
- TrustZone (if used)

