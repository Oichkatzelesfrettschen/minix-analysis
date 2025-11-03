# Architecture: MINIX 3.4.0-RC6 Hardware and Software Design

This section documents the complete architectural picture of MINIX: how hardware constraints shape software organization, why MINIX chose certain designs over alternatives, and how all pieces interconnect.

## What is Architecture?

In Lions' view, architecture is about **design trade-offs and constraints**. A system is not "good" or "bad" in abstract terms—it's optimal given specific constraints.

MINIX's constraints (circa 2012):
- **CPU**: i386 architecture (32-bit x86, not x86-64)
- **Philosophy**: Microkernel design (minimal kernel, maximum modularity)
- **Target**: Education and reliability, not performance

Given these constraints, MINIX's architectural decisions make sense.

## Organization

### Core Architecture Files

| File | Focus | Key Question |
|------|-------|--------------|
| MINIX-ARCHITECTURE-COMPLETE.md | Full system design | How does MINIX organize all its pieces? |
| CPU-INTERFACE-ANALYSIS.md | Processor interaction | How does user code call kernel functions? |
| MEMORY-LAYOUT-ANALYSIS.md | Address spaces and paging | How is memory protected and organized? |
| BOOT-TIMELINE.md | Initialization sequence | How does MINIX start from power-on? |
| SYSCALL-ARCHITECTURE.md | System call mechanisms | What are the three syscall paths? |
| INTERRUPT-HANDLING.md | Exception processing | How does MINIX respond to hardware events? |
| PROCESS-MANAGEMENT.md | Process abstraction | How does MINIX represent and manage processes? |

### Subdirectories

**i386/** - Processor-specific details
- Register usage and calling conventions
- Paging hardware (page tables, TLB)
- Privilege transitions

**memory/** - Virtual memory system
- Address translation
- Protection mechanisms
- TLB optimization

**syscalls/** - System call implementation
- Three mechanisms: INT, SYSENTER, SYSCALL
- Performance comparison
- Kernel entry points

**tlb/** - Translation Lookaside Buffer
- How TLB miss penalties affect performance
- TLB invalidation strategies

## How to Use This Section

### By Depth Level

**Level 1: Overview (30 minutes)**
- Read: MINIX-ARCHITECTURE-COMPLETE.md (section 1: Overview)
- Goal: Understand major components and their roles

**Level 2: Mechanisms (2-3 hours)**
- Read: CPU-INTERFACE-ANALYSIS.md (how user calls kernel)
- Read: MEMORY-LAYOUT-ANALYSIS.md (how memory is protected)
- Read: BOOT-TIMELINE.md (initialization order)
- Goal: Understand how hardware features are used

**Level 3: Implementation (half day)**
- Study: i386/ subdirectory (processor details)
- Study: syscalls/ subdirectory (specific mechanisms)
- Study: MINIX source code (cross-reference)
- Goal: Understand exact code implementations

**Level 4: Design Rationale (full day)**
- Compare: i386 alternatives (why not x86-64?)
- Analyze: Syscall performance (why SYSENTER is fastest)
- Evaluate: Memory layout (why this virtual address scheme?)
- Goal: Understand trade-offs and constraints

### By Use Case

**I'm porting MINIX to new hardware**
1. Start: MINIX-ARCHITECTURE-COMPLETE.md (what changes?)
2. Study: i386/ subdirectory (what's processor-specific?)
3. Deep dive: BOOT-TIMELINE.md (where does bootstrap happen?)
4. Reference: SYSCALL-ARCHITECTURE.md (what's the ABI?)

**I'm optimizing MINIX performance**
1. Start: CPU-INTERFACE-ANALYSIS.md (where time goes)
2. Study: syscalls/ (which mechanism is fastest?)
3. Analyze: MEMORY-LAYOUT-ANALYSIS.md (cache implications)
4. Reference: tlb/ (TLB optimization opportunities)

**I'm teaching OS design**
1. Follow Lions' approach: explain *why* then show *what*
2. Start: MINIX-ARCHITECTURE-COMPLETE.md (design rationale)
3. Show: i386/ details (concrete processor behavior)
4. Emphasize: Design trade-offs section (how decisions were made)

## Core Architectural Patterns

### Microkernel Design

MINIX is a **microkernel**: the kernel is small, and functionality lives in user-space servers.

**Why?** 
- Reliability: A bug in a driver or filesystem doesn't crash the system
- Security: Servers can't directly access hardware (everything mediated)
- Modularity: Servers can be updated without rebooting

**Trade-off**: Message passing overhead is higher than traditional monolithic kernels (Linux).

### Privilege Levels

x86 provides 4 privilege levels (rings 0-3):
- Ring 0: Kernel (full hardware access)
- Ring 3: User processes (restricted)

MINIX uses only rings 0 and 3. Ring 1-2 unused for simplicity.

**Why?** MINIX's model doesn't need intermediate privilege levels.

### Virtual Memory

MINIX uses **2-level page tables**:
- Page Directory (10 bits)
- Page Table (10 bits)
- Page Offset (12 bits)
- Total: 32-bit virtual addresses

Address: `[31:22 PDE index][21:12 PTE index][11:0 offset]`

**Why this structure?**
- 4 MB per process feasible with 4 KB pages
- Two-level design reduces memory overhead vs. flat page table
- i386 hardware supports this exactly

**Trade-off**: Single-level page tables would be faster but use more memory.

### System Call Mechanisms

Three syscall paths on i386:

| Method | Speed | Setup | Modern? |
|--------|-------|-------|---------|
| INT 0x21 | ~1772 cycles | None | Legacy |
| SYSENTER | ~1305 cycles | MSR setup | Pentium II+ |
| SYSCALL | ~1439 cycles | MSR setup | AMD/Intel |

MINIX supports all three for compatibility.

**Why?** Older CPUs lack SYSENTER/SYSCALL. Newer CPUs prefer them for speed.

## Connections to Other Sections

**Analysis** (docs/analysis/):
- Analysis shows *how* architecture manifests in code
- Architecture explains *why* those code patterns exist

**Performance** (docs/performance/):
- Architecture defines the search space for optimization
- Performance documents what optimizations are actually possible

**Boot Sequence** (docs/analysis/BOOT-SEQUENCE-ANALYSIS.md):
- Shows architecture in action during initialization
- Demonstrates how all components initialize

## Special Design Insights

### Why i386, Not x86-64?

MINIX 3.4.0-RC6 targets i386 (32-bit), not x86-64 (64-bit).

**Reasons:**
1. Simpler (32-bit addressing is enough for educational system)
2. Smaller code (less bloat for students to read)
3. Teaching focus (x86-64 unnecessary complexity)
4. Historical (MINIX predates modern 64-bit requirements)

**Trade-off**: Can't address > 4 GB memory, limited to 32-bit registers.

### TLB as Critical Path

The **Translation Lookaside Buffer** (TLB) is cached page table entries. TLB miss → memory access → ~200 cycle penalty.

MINIX optimization: Process pages laid out to minimize TLB misses (working set fits in DTLB).

This explains MINIX's memory layout choices.

## Key Questions Answered

**Q: Why does MINIX architecture differ from Linux?**
A: Different design goals. Linux optimizes for performance; MINIX for clarity. See MINIX-ARCHITECTURE-COMPLETE.md section 2 for comparison.

**Q: Can I understand MINIX without hardware knowledge?**
A: Partially. Architecture docs explain hardware at a conceptual level. For deep understanding, you need i386 knowledge. See i386/README.md.

**Q: How do I verify these claims?**
A: Read MINIX source code directly. All architecture files reference source file locations (e.g., kernel/arch/i386/). Consult i386 manuals for hardware details.

## Navigation

- [Return to docs/](../README.md)
- [Analysis: System Behavior](../analysis/README.md) - What actually happens at runtime
- [Performance: Measurements & Optimization](../performance/README.md) - Speed and efficiency
- [Processor Details](i386/README.md) - x86 specifics

---

**Updated**: November 1, 2025
**Style**: Lions Commentary (explain design trade-offs, not just code)
**Status**: Complete - Ready for Phase 3 harmonization
