# Intel 80486 CPU Enhancements Diagram (1989)

## Overview

This TikZ diagram documents the key architectural enhancements introduced in the Intel 80486 processor (1989) that distinguish it from the 386 baseline. The 486 was the first x86 CPU with runtime feature detection (CPUID) and on-die cache, marking a significant evolution in x86 architecture.

**Purpose**: Document 486-specific features with precise MINIX source code references showing actual implementation and usage.

**Coverage**: 6 major 486 innovations: CPUID instruction, CR0.WP bit, on-die cache control, CMPXCHG, XADD, and BSWAP instructions.

## Diagram Structure

### Layout

The diagram is organized into 6 sections arranged in a 3x2 grid:

- **Top Row (Y=16-18)**:
  - **Left (X=1-7)**: CPUID instruction flow and feature detection
  - **Center (X=8-12)**: CR0.WP bit (Write Protect in Ring 0)
  - **Right (X=14-18)**: Cache control (WBINVD, INVLPG)

- **Bottom Row (Y=3-7)**:
  - **Left (X=1-7)**: CMPXCHG (compare and exchange) atomic operation
  - **Center (X=8-12)**: XADD (exchange and add) atomic operation
  - **Right (X=14-18)**: BSWAP (byte swap) endianness conversion

### Color Coding

Following MINIX style guide:

- **Primary Blue** (`primaryblue`): CPUID feature detection
- **Accent Orange** (`accentorange`): CR0.WP bit (critical kernel protection)
- **Secondary Green** (`secondarygreen`): Instructions and MINIX implementation notes
- **Warning Red** (`warningred`): Decision points in flowcharts
- **Light Gray** (`lightgray`): Code examples and atomic instruction backgrounds

## 486 Enhancements Detailed

### 1. CPUID Instruction (Left Column)

**Historical Significance**: First CPU feature detection mechanism in x86 history. Before CPUID, software had to guess CPU capabilities based on family/model, leading to compatibility issues.

**Detection Flow**:
```
1. Check EFLAGS.ID bit (bit 21)
   - Try to toggle ID bit
   - If toggles: CPUID supported
   - If stuck: 386 (no CPUID)

2. Execute CPUID with EAX=1
   - Opcode: 0x0f 0xa2
   - Returns: EDX = feature flags

3. Check feature bits:
   - bit 0: FPU (on-chip floating point)
   - bit 4: TSC (time stamp counter)
   - bit 8: CX8 (CMPXCHG8B instruction)
   - bit 9: APIC (on-chip APIC)
```

**MINIX Implementation** (klib.S:664-670):
```asm
; Detect CPUID support
pushf
pop %eax
mov %eax, %ebx
and $0x200000, %eax  ; Check ID bit (bit 21)
je 0f                ; No CPUID support
mov $0x1, %eax
.byte 0x0f, 0xa2     ; CPUID opcode
mov %edx, %eax       ; Feature flags to EAX
ret
0: xor %eax, %eax    ; Return 0 (no CPUID)
ret
```

**MINIX Source Files**:
- specialreg.h:122-157 - CPUID feature flag definitions
- klib.S:664-670 - CPUID implementation in assembly

**Why Important**: Enabled robust feature detection without relying on CPU family/model guessing. This allowed MINIX to detect RDTSC, APIC, PAE, SSE, and other features at runtime.

### 2. CR0.WP Bit (Center Column)

**Historical Significance**: First x86 hardware mechanism to enforce read-only memory protection in Ring 0 (kernel mode). Before WP, kernel bugs could silently corrupt read-only data.

**CR0 Register Layout**:
```
31-17: (other control bits)
  16 : WP (Write Protect)
15-1 : (other control bits)
   0 : PE (Protected mode Enable)
```

**Behavior**:
- **WP = 0**: Ring 0 can write to read-only pages (386 behavior)
- **WP = 1**: Ring 0 must respect read-only page protection (486+ behavior)

**MINIX Implementation** (pg_utils.c:230-245):
```c
// Enable PSE (Page Size Extension)
cr4 |= I386_CR4_PSE;
write_cr4(cr4);

/* First enable paging */
cr0 |= I386_CR0_PG;
write_cr0(cr0);

/* Then enable WP bit (486+ feature) */
cr0 |= I386_CR0_WP;  // <-- WP bit set
write_cr0(cr0);

/* Enable PGE (Page Global Enable) if supported */
if(pgeok)
    cr4 |= I386_CR4_PGE;
write_cr4(cr4);
```

**MINIX Source Files**:
- pg_utils.c:237 - WP bit enablement after paging setup
- memory.c:257 - WP bit usage in memory initialization

**Use Case**: Prevents kernel from accidentally writing to `.rodata` section, string literals, or other read-only kernel data. Critical for kernel stability.

**Example Scenario**:
```
Without WP (386):
  Kernel bug: strcpy(kernel_string_literal, user_input);
  Result: Silent corruption, undefined behavior

With WP (486+):
  Same bug: strcpy(kernel_string_literal, user_input);
  Result: Page fault, kernel panic (debuggable)
```

### 3. Cache Control (Right Column)

**Historical Significance**: First x86 CPU with on-die cache (8KB unified L1). Required new instructions for cache management.

**On-Die Cache**:
- Size: 8KB unified (instructions + data)
- Type: Write-through
- Lines: 128 lines × 64 bytes (4-way set associative)

**Cache Instructions**:

**WBINVD** (Write-Back and Invalidate):
```c
void wbinvd(void);  // cpufunc.h:74

// Effect:
1. Write all dirty cache lines to RAM
2. Invalidate entire cache
3. Used before: DMA operations, cache coherency in SMP
```

**INVLPG** (Invalidate TLB Entry):
```asm
invlpg <virtual_address>  // cpufunc.h:55

// Effect:
1. Invalidate TLB entry for specific virtual address
2. Much faster than CR3 reload (full TLB flush)

// Example:
invlpg(0xC0000000);  // Invalidate single page
```

**MINIX Implementation**:
- Uses INVLPG for single-page TLB invalidation (faster than CR3 flush)
- Uses WBINVD before hardware reset or cache-sensitive operations
- Prefers INVLPG over full TLB flush for performance

**Performance Comparison**:
```
Full TLB flush (CR3 reload):  ~500 cycles
INVLPG (single page):         ~30 cycles
Benefit: 16× faster for single-page invalidation
```

### 4. CMPXCHG - Compare and Exchange (Bottom Left)

**Historical Significance**: First atomic compare-and-swap instruction in x86. Foundation for lock-free data structures and synchronization primitives.

**Operation**:
```asm
CMPXCHG <dest>, <src>

Pseudocode:
  if (EAX == dest) {
      ZF = 1;
      dest = src;
  } else {
      ZF = 0;
      EAX = dest;
  }

Atomic: Yes (when prefixed with LOCK)
```

**MINIX Implementation** (atomic.S:80-93):
```asm
; atomic_and_32_nv - atomic AND with return value
_atomic_and_32_nv:
    movl 4(%esp), %edx      ; Load address
    movl (%edx), %eax       ; Load current value
0:
    movl %eax, %ecx         ; Copy to ECX
    andl 8(%esp), %ecx      ; Compute new value
    lock
    cmpxchgl %ecx, (%edx)   ; Atomic compare-exchange
    jnz 1f                  ; Retry if failed
    movl %ecx, %eax         ; Return new value
    ret
1:
    jmp 0b                  ; Retry loop
```

**Use Cases**:
- Lock-free queues
- Reference counting
- Spinlock implementation
- Memory allocator atomic operations

### 5. XADD - Exchange and Add (Bottom Center)

**Historical Significance**: Simplified atomic increment/decrement operations. Before XADD, atomic add required LOCK ADD (which didn't return old value) or CMPXCHG loop.

**Operation**:
```asm
XADD <dest>, <src>

Pseudocode:
  temp = dest;
  dest = dest + src;
  src = temp;

Atomic: Yes (when prefixed with LOCK)
```

**MINIX Implementation** (atomic.S:62-70):
```asm
; atomic_add_32_nv - atomic ADD with return value
_atomic_add_32_nv:
    movl 4(%esp), %edx      ; Load address
    movl 8(%esp), %eax      ; Load increment value
    movl %eax, %ecx         ; Save increment
    lock
    xaddl %eax, (%edx)      ; Atomic exchange-and-add
    addl %ecx, %eax         ; Compute new value
    ret                     ; Return new value
```

**Use Cases**:
- Atomic counters (reference counts, statistics)
- Lock-free data structure indices
- Sequence number generation

**Performance**: Single instruction vs. CMPXCHG loop (3-5 instructions)

### 6. BSWAP - Byte Swap (Bottom Right)

**Historical Significance**: First dedicated endianness conversion instruction. Before BSWAP, byte swapping required multiple ROL/ROR or XOR operations.

**Operation**:
```asm
BSWAP <reg32>

Example:
  Input:  0x12345678
  Output: 0x78563412

Effect: Reverse byte order in 32-bit register
Cycles: 1 (vs. 4-6 cycles with manual swap)
```

**MINIX Implementation** (byte_swap.h:42-49):
```c
static __inline uint32_t
__byte_swap_u32_variable(uint32_t x)
{
    __asm volatile (
        "bswap %1"
        : "=r" (x)
        : "0" (x));
    return (x);
}
```

**Use Cases**:
- Network byte order conversion (htonl, ntohl)
- File format parsing (reading big-endian data on little-endian CPU)
- Cryptographic operations

**Performance**:
```
Manual swap (386):
  mov eax, input
  rol ax, 8          ; Swap low word
  rol eax, 16        ; Swap halves
  rol ax, 8          ; Swap high word
  Total: 4 instructions

BSWAP (486+):
  bswap eax          ; 1 instruction
  Total: 1 instruction
```

## Background Zones

Visual zones help distinguish feature categories:

1. **CPUID Section** (primaryblue!5): Feature detection mechanism
2. **WP Bit Section** (accentorange!5): Kernel memory protection
3. **Cache Section** (secondarygreen!5): On-die cache control
4. **Atomic Instructions** (lightgray): Three atomic operation boxes

## Source File References

The diagram includes precise source code references:

- **specialreg.h:122-157** - CPUID feature flag definitions (CPUID_FPU, CPUID_TSC, etc.)
- **klib.S:664-670** - CPUID detection implementation in assembly
- **pg_utils.c:230-245** - CR0.WP bit enablement during paging setup
- **cpufunc.h:74** - WBINVD cache flush function declaration
- **cpufunc.h:55** - INVLPG TLB invalidation function
- **atomic.S:67-142** - CMPXCHG and XADD usage in atomic operations
- **byte_swap.h:42-49** - BSWAP inline assembly for endianness conversion

## Compilation

### Prerequisites

```bash
sudo pacman -S texlive-core texlive-latexextra texlive-pictures
```

### Build Commands

```bash
# Compile to PDF
pdflatex i486-enhancements.tex

# Convert to high-resolution PNG (300 DPI)
magick -density 300 -quality 95 i486-enhancements.pdf i486-enhancements.png

# Clean build artifacts
rm -f i486-enhancements.aux i486-enhancements.log
```

### Output Files

- **i486-enhancements.pdf** - Vector PDF (155 KB)
- **i486-enhancements.png** - Raster PNG (if converted)

## Integration with Whitepaper

### LaTeX Integration

```latex
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Intel 80486 Enhancements}

Figure~\ref{fig:i486-enhancements} shows the architectural enhancements
introduced in the Intel 80486 processor (1989), including CPUID instruction,
WP bit, on-die cache, and new atomic instructions.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{diagrams/tikz/i486-enhancements.pdf}
\caption{Intel 80486 CPU Enhancements (1989)}
\label{fig:i486-enhancements}
\end{figure}

Key innovations:
\begin{itemize}
\item \textbf{CPUID}: First runtime CPU feature detection mechanism
\item \textbf{CR0.WP}: Write protection in Ring 0 for kernel memory safety
\item \textbf{8KB L1 Cache}: First on-die cache with WBINVD/INVLPG control
\item \textbf{Atomic Instructions}: CMPXCHG, XADD for lock-free programming
\item \textbf{BSWAP}: Single-instruction endianness conversion
\end{itemize}

\end{document}
```

### Markdown Integration

```markdown
## Intel 80486 CPU Enhancements

![i486 Enhancements](diagrams/tikz/i486-enhancements.png)

*Figure: Intel 80486 architectural enhancements (1989), showing CPUID feature
detection, CR0.WP bit for kernel protection, cache control, and new atomic
instructions (CMPXCHG, XADD, BSWAP). All features fully supported by MINIX 3.4.0.*
```

## Statistics

- **Features documented**: 6 major 486 enhancements
- **Instructions covered**: CPUID, WBINVD, INVLPG, CMPXCHG, XADD, BSWAP
- **Source files referenced**: 6 (specialreg.h, klib.S, pg_utils.c, cpufunc.h, atomic.S, byte_swap.h)
- **Code examples**: 6 (assembly + C implementations)
- **Diagram size**: 288 lines of TikZ code
- **PDF output**: 155 KB

## Performance Impact

The 486 enhancements provided significant performance improvements:

| Feature | 386 Approach | 486 Approach | Speedup |
|---------|--------------|--------------|---------|
| CPU detection | Family/model guessing | CPUID instruction | Reliable vs. error-prone |
| TLB invalidation | CR3 reload (~500 cycles) | INVLPG (~30 cycles) | 16× faster |
| Atomic increment | LOCK ADD (no return) | XADD (1 instruction) | Simplified, faster |
| Endian swap | 4 instructions | BSWAP (1 instruction) | 4× faster |
| Kernel protection | None (bugs corrupt data) | CR0.WP (page fault) | Debuggable crashes |

## Related Diagrams

This diagram complements other MINIX CPU interface visualizations:

1. **i386-baseline-architecture.tex** - 386 foundation (protected mode, paging, segmentation)
2. **x86-cpu-evolution.tex** - CPU timeline from 386 through Pentium 4 and Athlon 64
3. **system-call-mechanisms.tex** - INT/SYSENTER/SYSCALL comparison
4. **hardware-interrupt-flow.tex** - PIC vs APIC interrupt handling
5. **context-switch-detailed.tex** - Process switching with CR3 and segment registers
6. **cpu-structures.tex** - GDT/IDT/TSS architecture

## Future Extensions

Potential additions to document later CPU generations:

1. **Pentium diagram**: RDTSC, APIC, dual-issue pipeline, MMX
2. **Pentium Pro diagram**: PAE (3-level paging), SYSENTER/SYSEXIT, CMOV, out-of-order execution
3. **Pentium III diagram**: SSE instructions, SFENCE, serial number
4. **Pentium 4 diagram**: SSE2, Hyper-Threading, long pipeline

## Historical Context

### Why CPUID Was Revolutionary

Before CPUID (pre-486), software had to guess CPU features:
```c
// 386-era code (unreliable)
if (cpu_family == 3) {
    // Assume 386: no FPU, no TSC
} else if (cpu_family == 4) {
    // Assume 486: has FPU, may have TSC?
} else if (cpu_family == 5) {
    // Assume Pentium: has TSC, may have APIC?
}
```

With CPUID (486+):
```c
// 486+ code (reliable)
cpuid_features = get_cpuid_features();
if (cpuid_features & CPUID_TSC) {
    use_rdtsc();  // Confirmed TSC support
}
if (cpuid_features & CPUID_APIC) {
    use_apic();   // Confirmed APIC support
}
```

### Why WP Bit Was Critical

Real-world kernel bug prevented by WP bit:
```c
// Kernel code (hypothetical bug)
const char *kernel_version = "MINIX 3.4.0";  // In .rodata

void buggy_function(const char *input) {
    // Bug: accidentally writing to read-only string
    strcpy(kernel_version, input);  // WRONG!

    // Without WP (386):
    //   Silent corruption, undefined behavior, system instability

    // With WP (486+):
    //   Page fault immediately, kernel panic with stack trace
    //   Developer can fix bug quickly
}
```

## References

- Intel 80486 Programmer's Reference Manual (1989)
- Intel Architecture Software Developer's Manual, Volume 2 (Instruction Set Reference)
- MINIX 3.4.0-RC6 source code (sys/arch/i386/, minix/kernel/arch/i386/)
- NetBSD source code (atomic operations, byte swapping utilities)

## License

This diagram is part of the MINIX CPU Interface Analysis project and follows the same licensing as MINIX documentation (BSD-style).

---

**Created**: 2025-10-31
**Last Updated**: 2025-10-31
**Version**: 1.0
**Author**: Generated for MINIX analysis whitepaper
**Compiled**: 155 KB PDF
**Source Lines**: 288 lines of TikZ code
