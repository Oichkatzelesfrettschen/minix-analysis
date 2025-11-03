# MINIX 3.4 Boot and Kernel Analysis - Documentation Index

**Version**: 1.0.0
**Date**: 2025-10-31
**Complete**: YES (All phases documented)
**Total Pages**: 2600+ lines of detailed analysis

---

## QUICK START

### For the Impatient (10 minutes)

1. Read **COMPREHENSIVE-BOOT-RUNTIME-TRACE.md**: Executive Summary + Part I
   - Overview of boot sequence
   - Process creation overview
   - CPU state transitions at high level

2. Open a terminal and explore:
   ```bash
   cd /home/eirikr/Playground/minix-analysis
   
   # Disassemble MINIX kernel
   objdump -d /path/to/minix > kernel.asm
   
   # Find boot entry point
   grep -n "^[0-9a-f]* <MINIX>:" kernel.asm
   
   # Extract kmain
   grep -n "^[0-9a-f]* <kmain>:" kernel.asm
   ```

### For Serious Analysis (1-2 hours)

1. Read **BOOT-TO-KERNEL-TRACE.md** (Full)
2. Read **FORK-PROCESS-CREATION-TRACE.md** (Full)
3. Read **COMPREHENSIVE-BOOT-RUNTIME-TRACE.md** (All appendices)
4. Cross-reference with MINIX source code
5. Use analysis tools to verify traces

---

## DOCUMENTATION STRUCTURE

### Three Main Trace Documents

#### 1. BOOT-TO-KERNEL-TRACE.md
**995 lines | 7 major phases**

**Coverage**:
- Phase 0: Multiboot bootloader entry
- Phase 1: Pre-init low-level setup (memory, paging)
- Phase 2: Kernel initialization (GDT, IDT, TSS, timers)
- Phase 3: Process scheduling and context switching

**Key Content**:
- Multiboot header and magic numbers
- Memory mapping (1:1 to paged)
- Protected mode entry
- Interrupt vector setup
- Timer initialization
- First process scheduling
- CPU register state at each transition

**Critical Insights**:
- Why pre_init runs at physical addresses before paging
- How kernel gets remapped from 0x00100000 to 0x80000000
- Exact sequence of GDT/IDT/TSS loading
- How first process enters Ring 3 via IRET

**Reading Path**:
1. Start with PHASE 0 (bootloader entry)
2. Follow through PHASE 3 (first IRET to user)
3. Study CPU register state sections for each phase
4. Cross-reference with head.S and pre_init.c

**Best For**:
- Understanding system initialization
- Learning memory management in real hardware
- CPU privilege level transitions
- Interrupt vector setup

---

#### 2. FORK-PROCESS-CREATION-TRACE.md
**974 lines | 7 major sections**

**Coverage**:
- Section 1: Fork syscall entry (INT 0x30)
- Section 2: Context save and syscall dispatch
- Section 3: Fork implementation (do_fork)
- Section 4: Return from syscall
- Section 5: CPU context switching during fork
- Section 6: Exec syscall sequence
- Section 7: CPU context state summary

**Key Content**:
- INT instruction and CPU automatic behavior
- SAVE_PROCESS_CTX macro expansion
- Process table structure and copying
- Endpoint generation and uniqueness
- Child process customization
- Privilege level handling
- FPU state management
- Memory page table setup
- Exec register updates

**Critical Insights**:
- Why child gets EAX=0 while parent gets PID
- How process table enables context switching
- Why child blocks on RTS_VMINHIBIT
- How exec changes EIP without syscall entry

**Reading Path**:
1. Start with SECTION 1 (syscall entry)
2. Follow SECTION 2 (context save)
3. Deep dive SECTION 3 (fork implementation)
4. Study SECTION 5 (CPU context switching)
5. Compare SECTION 6 (exec) to understand complete process lifecycle

**Best For**:
- Understanding process creation
- Learning context saving mechanisms
- CPU register state per process
- System call dispatch
- Process table manipulation

---

#### 3. COMPREHENSIVE-BOOT-RUNTIME-TRACE.md
**636 lines | Synthesis document**

**Coverage**:
- Executive summary
- Complete execution timeline
- Interrupt handling details
- System call dispatch
- Process scheduling
- CPU register reference (Appendix A)
- Memory layout reference (Appendix B)
- Code location reference (Appendix C)

**Key Content**:
- Unified timeline of fork() + exec()
- Timer interrupt sequence
- Run queue scheduling algorithm
- CPU register mapping (EAX, EBX, etc)
- Memory layout (user vs kernel)
- Page table structure
- Critical source code locations

**Critical Insights**:
- How everything fits together (synthesis)
- Complete example: parent forks child, child execs /bin/ls
- Exactly when processes are RUNNABLE/BLOCKED
- Where to find critical code in MINIX source

**Reading Path**:
1. Start with Executive Summary
2. Study Part I (overview of boot)
3. Study Part II (overview of process management)
4. Study Part III (runtime operation)
5. Use Appendices as reference during source code exploration

**Best For**:
- Refresher after reading detailed traces
- Cross-referencing multiple concepts
- Understanding complete system operation
- Finding critical code locations

---

### Supporting Documentation

#### CAPABILITIES-AND-TOOLS.md
**Status**: Exists (see minix-analysis root)
**Purpose**: Documents analysis tools and capabilities
**Content**:
- Available analysis tools
- When to use each tool
- MCP server capabilities
- Integration with tools

#### tools/pkgbuilds/ Directory
**Status**: Complete
**Content**:
- PKGBUILD-minix-analysis-tools (meta-package)
- PKGBUILD-minix-boot-tracer (kernel tracing)
- PKGBUILD-minix-asm-analyzer (assembly analysis)
- README.md (tool usage guide)

**Installation**:
```bash
cd /home/eirikr/Playground/minix-analysis/tools/pkgbuilds
pikaur -U PKGBUILD-minix-*
```

**After Installation**:
```bash
# Disassemble kernel
minix-disasm /path/to/minix.elf > kernel.asm

# Extract symbols
minix-symbols /path/to/minix.elf

# Resolve addresses
minix-addr2line /path/to/minix.elf 0x80000000
```

---

## HOW TO USE THESE DOCUMENTS

### Scenario 1: Understanding Boot Sequence

**Goal**: Understand how MINIX goes from bootloader to first user process

**Steps**:
1. Read BOOT-TO-KERNEL-TRACE.md PHASE 0-3
2. Look up source code references (head.S line numbers)
3. Use minix-disasm to extract assembly
4. Compare assembly with trace document
5. Verify CPU states match expectations

**Expected Understanding**:
- Bootloader provides protected mode
- Pre-init enables paging and remaps kernel
- cstart() initializes GDT/IDT/TSS
- kmain() creates process table
- Timer enabled, first process scheduled
- IRET switches to Ring 3

---

### Scenario 2: Tracing fork() Execution

**Goal**: Understand exactly what happens when a process calls fork()

**Steps**:
1. Read FORK-PROCESS-CREATION-TRACE.md SECTION 1-4
2. Find do_fork() in minix/kernel/system/do_fork.c
3. Follow code path with trace document
4. Note which fields change (EAX, endpoint, RTS_flags)
5. Verify child creation by examining process table

**Expected Understanding**:
- INT 0x30 enters kernel automatically
- SAVE_PROCESS_CTX saves all registers
- do_fork() copies parent to child
- Child EAX=0, parent EAX=pid
- Child blocked until VM sets up memory
- Return via IRET

---

### Scenario 3: Understanding Context Switches

**Goal**: Understand how CPU switches between processes

**Steps**:
1. Read COMPREHENSIVE-BOOT-RUNTIME-TRACE.md PART III
2. Read FORK-PROCESS-CREATION-TRACE.md SECTION 5
3. Study process table structure (proc.h)
4. Trace hwint00 handler in mpx.S
5. Follow pick_proc() scheduling logic

**Expected Understanding**:
- Interrupt saves full CPU context
- pick_proc() selects next runnable process
- RESTORE_GP_REGS restores registers
- IRET restores privilege level
- Context completely isolated per process

---

### Scenario 4: Analyzing Boot Trace

**Goal**: Create custom boot analysis using provided tools

**Steps**:
```bash
# Extract kernel assembly
objdump -d minix.elf > kernel_full.asm

# Find entry point
grep "<MINIX>:" kernel_full.asm

# Extract head.S section
objdump -S minix.elf | grep -A 50 "head.S"

# Find boot functions
grep -n "multiboot_init\|pre_init\|kmain\|cstart" kernel_full.asm

# Disassemble specific function
objdump -S minix.elf | sed -n '/<kmain>/,/^$/p'

# Find all interrupt handlers
grep "hwint[0-9][0-9]*>:" kernel_full.asm

# Extract all system calls
grep "ipc_entry" kernel_full.asm
```

**Cross-Reference with Traces**:
- BOOT-TO-KERNEL-TRACE.md tells you what each section does
- COMPREHENSIVE-BOOT-RUNTIME-TRACE.md APPENDIX C shows file locations
- Assembly output validates trace accuracy

---

## UNDERSTANDING CPU STATE AT CRITICAL POINTS

### The Magic of IRET

**Before IRET**:
```
Kernel stack contains (bottom to top):
[ESP+0]:   EIP (user instruction)
[ESP+4]:   CS (user code selector)
[ESP+8]:   EFLAGS (with IF=1)
```

**IRET Instruction**:
```asm
iret              ; CPU executes this
```

**CPU Automatic Actions**:
1. Pop EIP from [ESP+0]
2. Pop CS from [ESP+4]
3. Pop EFLAGS from [ESP+8]
4. Check privilege level in CS
5. If privilege level changed: also pop ESP, SS
6. Load segment registers from descriptor table
7. Jump to EIP with new privilege level

**After IRET**:
```
CPU State:
EIP:    User instruction pointer (from stack)
CS:     User code selector (0x1b, DPL=3)
EFLAGS: User flags (IF=1)
DS/ES:  User data selectors (0x23)
SS:     User stack selector (0x23)
ESP:    User stack pointer
```

**This One Instruction Performs**:
- Privilege level change (Ring 0 -> Ring 3)
- Stack switch (kernel -> user)
- Register reload (segment registers)
- Control transfer (to user code)

---

## KEY DISCOVERIES IN TRACES

### Discovery 1: Low Memory to High Memory Transition

**The Problem**: Kernel is compiled for virtual address 0x80000000, but bootloader loads it at 0x00100000

**The Solution**:
1. Enable paging with both mappings active
2. Run pre_init() at low address (still works due to 1:1 mapping)
3. Jump to high address (using high address in call instruction)
4. Continue at high address via page table

**Critical**: No TLB flush needed because both mappings exist before jumping

---

### Discovery 2: Process vs Fork

**Without Fork**:
- Process creation requires: allocate memory, build page tables, load executable, set up stacks
- Complex manual process (done by VM server)

**With Fork**:
- One atomic operation: copy parent process table entry
- Child inherits: all registers, memory mappings, open files
- Child only needs: new memory for stack (via copy-on-write)

**Result**: Fork is extremely fast (microseconds vs milliseconds)

---

### Discovery 3: Ring 3 to Ring 0 Transitions

**User Process Issues INT**:
- CPU atomically checks EFLAGS.IF
- CPU atomically saves context (EIP, CS, EFLAGS)
- CPU atomically loads kernel stack and code
- CPU atomically disables interrupts (EFLAGS.IF = 0)

**No Software Needed**:
- Kernel handler doesn't need to check privilege
- Context already saved by hardware
- Stack already switched by hardware
- Interrupts already disabled by hardware

**Result**: INT/IRET is very efficient (30-50 CPU cycles)

---

### Discovery 4: Process Table as Universal Context Storage

**Why Process Table Works**:
- Every process has exactly one entry in process table
- All CPU registers stored in process table entry
- Switching processes = restore registers from different entry
- No separate stacks needed per process (kernel has separate stack)

**Benefits**:
- Centralized, cacheable storage
- Fast context switches (L1 cache hit)
- Easy debugging (inspect process table)
- Simple memory management

---

## VERIFICATION CHECKLIST

After reading traces, verify understanding:

- [ ] Bootloader entry point in head.S
- [ ] Why paging enabled before kmain
- [ ] GDT/IDT/TSS locations in memory
- [ ] Timer interrupt handler entry point
- [ ] First process IRET sequence
- [ ] Fork syscall entry point (INT 0x30)
- [ ] do_fork location and basic logic
- [ ] Child vs parent return value (EAX)
- [ ] Process table structure and layout
- [ ] pick_proc scheduling algorithm
- [ ] Context save macro (SAVE_PROCESS_CTX)
- [ ] Register restoration sequence
- [ ] Ring 3 -> Ring 0 transition via INT
- [ ] Ring 0 -> Ring 3 transition via IRET
- [ ] Privilege level checks in GDT/IDT

**If you can answer all 15 questions from memory**: You understand MINIX architecture

---

## RECOMMENDED READING ORDER

### Option A: Linear (Beginner)
1. COMPREHENSIVE-BOOT-RUNTIME-TRACE.md (Executive Summary + Part I)
2. BOOT-TO-KERNEL-TRACE.md (PHASE 0 only)
3. BOOT-TO-KERNEL-TRACE.md (complete)
4. FORK-PROCESS-CREATION-TRACE.md (SECTION 1-2 only)
5. FORK-PROCESS-CREATION-TRACE.md (complete)
6. COMPREHENSIVE-BOOT-RUNTIME-TRACE.md (PART IV + Appendices)

### Option B: Thematic (Intermediate)
1. Boot: BOOT-TO-KERNEL-TRACE.md (complete)
2. Processes: FORK-PROCESS-CREATION-TRACE.md (complete)
3. Synthesis: COMPREHENSIVE-BOOT-RUNTIME-TRACE.md (complete)

### Option C: Focused (Advanced)
1. Pick relevant section from trace documents
2. Read COMPREHENSIVE-BOOT-RUNTIME-TRACE.md for context
3. Cross-reference with source code
4. Use analysis tools to verify

---

## NEXT STEPS

### Short Term (This Session)
- [ ] Read at least one complete trace document
- [ ] Use analysis tools on MINIX kernel
- [ ] Verify CPU register values in traces

### Medium Term (This Week)
- [ ] Read all three trace documents
- [ ] Cross-reference with MINIX source code
- [ ] Identify interesting optimizations
- [ ] Build custom analysis scripts

### Long Term (This Month)
- [ ] Create whitepaper with figures
- [ ] Submit to arXiv or conference
- [ ] Add system call analysis
- [ ] Add IPC message tracing
- [ ] Performance benchmarking

---

## DOCUMENT STATISTICS

| Document | Lines | Sections | Code Refs |
|----------|-------|----------|-----------|
| BOOT-TO-KERNEL-TRACE.md | 995 | 15 | 100+ |
| FORK-PROCESS-CREATION-TRACE.md | 974 | 14 | 80+ |
| COMPREHENSIVE-BOOT-RUNTIME-TRACE.md | 636 | 14 | 60+ |
| **Total** | **2605** | **43** | **240+** |

---

## AUTHORSHIP AND LICENSING

**Analysis**: Oaich (eirikr@local)
**Date**: 2025-10-31
**MINIX Version**: 3.4.0-RC6
**Architecture**: x86 (i386 32-bit)

**License**:
- Trace documents: MIT License
- MINIX source: BSD-style (Vrije Universiteit)
- Analysis tools: MIT License

**Source Code References**:
All source code references point to MINIX git repository.

---

## CONTACT AND FEEDBACK

For questions or corrections:
1. Verify claim against MINIX source code
2. Check against corresponding section in traces
3. Consult COMPREHENSIVE-BOOT-RUNTIME-TRACE.md Appendix C for code locations
4. File issue with specific line numbers and corrections

---

**END OF INDEX**

Ready to understand MINIX at the deepest CPU level. Happy reading!
