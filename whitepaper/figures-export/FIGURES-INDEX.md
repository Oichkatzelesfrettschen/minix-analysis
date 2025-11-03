# MINIX Whitepaper Figures - Detailed Index

**Complete reference guide to all 22 figures with pedagogical context**

---

## CHAPTER 1: INTRODUCTION AND MOTIVATION

### Figure 1: Microkernel Architecture Overview
- **File**: `tikz-diagrams/fig-01-microkernel-architecture.png`
- **Page**: 18 | **DPI**: 300 | **Size**: 46 KB
- **Description**: MINIX 3.4 kernel vs. services architecture
- **What it Shows**: 
  - Minimal kernel core (95 KB) at center
  - User-space isolated services (FS, VM, drivers, network)
  - Message-based IPC between kernel and services
  - Fault isolation boundaries (dashed green lines)
- **Lions Pedagogy**: 
  - Question: Why isolate drivers in user space?
  - Answer: Demonstrates microkernel principle—fault in driver cannot crash kernel
  - Reveals reliability advantage over monolithic design
- **Used In**: Introduction establishing microkernel philosophy

---

## CHAPTER 2: FUNDAMENTALS

### Figure 2: Synchronous Message Passing Sequence
- **File**: `tikz-diagrams/fig-02-message-passing.png`
- **Page**: 29 | **DPI**: 300 | **Size**: 49 KB
- **Description**: IPC message passing sequence diagram
- **What it Shows**:
  - Process A sends message to kernel
  - Kernel blocks Process A (waiting for response)
  - Process B receives and processes message
  - Process B sends reply back through kernel
  - Process A resumes with reply
- **Lions Pedagogy**:
  - Question: Why synchronous (not asynchronous)?
  - Answer: Guarantees ordering, simplifies debugging, enforces isolation
  - Shows how architecture enforces determinism
- **Used In**: Chapter 2 explaining MINIX IPC model

### Figure 3: x86 Memory Layout and CPU State
- **File**: `tikz-diagrams/fig-03-memory-layout.png`
- **Page**: 32 | **DPI**: 300 | **Size**: 4.2 KB
- **Description**: Virtual address space layout and CPU structures
- **What it Shows**:
  - Virtual address range (0x00000000 to 0xFFFFFFFF)
  - Kernel memory at high addresses (0xFFFF0000+)
  - I/O memory mappings
  - Process-specific regions (heap, data, stack)
  - CPU structures (GDT, IDT, page tables, TSS)
- **Lions Pedagogy**:
  - Question: Why isolate memory ranges?
  - Answer: Hardware MMU enforces boundaries; architecture builds on this
  - Shows how x86 capabilities shape design decisions
- **Used In**: Chapter 2 explaining memory architecture

---

## CHAPTER 3: METHODOLOGY

### Figure 4: Data Pipeline Architecture
- **File**: `tikz-diagrams/fig-04-data-pipeline.png`
- **Page**: 42 | **DPI**: 300 | **Size**: 58 KB
- **Description**: Analysis data flow from boot execution to reporting
- **What it Shows**:
  - MINIX boot execution in QEMU
  - Serial log capture to file
  - Error triage and pattern matching
  - Metrics extraction (latency, throughput, memory)
  - Database storage (SQLite)
  - Final analysis and reporting outputs
- **Lions Pedagogy**:
  - Demonstrates how design claims are validated with measurements
  - Shows reproducible methodology underpinning all analysis
  - Grounds pedagogical claims in empirical data
- **Used In**: Chapter 3 explaining experimental methodology

### Figure 5: Experimental Workflow
- **File**: `tikz-diagrams/fig-05-workflow.png`
- **Page**: 45 | **DPI**: 300 | **Size**: 34 KB
- **Description**: Iteration cycle for validation
- **What it Shows**:
  - Setup phase (environment configuration)
  - Boot execution (QEMU simulation)
  - Analysis phase (data extraction and error detection)
  - Validation phase (verify consistency)
  - Iteration loop until consistent valid results
- **Lions Pedagogy**:
  - Shows disciplined experimental approach
  - Emphasizes reproducibility as foundation for pedagogical claims
  - Demonstrates how design wisdom is validated
- **Used In**: Chapter 3 explaining validation cycles

---

## CHAPTER 4: BOOT METRICS (PILOT 1 - DESIGN TOPOLOGY)

### Figure 6: Boot Phase Flowchart
- **File**: `tikz-diagrams/fig-06-boot-flowchart.png`
- **Page**: 55 | **DPI**: 300 | **Size**: 40 KB
- **Description**: MINIX 3.4 boot sequence 7-phase structure
- **What it Shows**:
  - Phase 0: Bootloader entry
  - Phases 1-2: Kernel initialization (protected mode, paging, interrupts)
  - Phase 3: Scheduler startup
  - Phases 4-6: User-space service startup (FS, drivers, shell)
  - Red highlighting for critical phases where errors commonly occur
- **Lions Pedagogy (PILOT 1)**:
  - **Question**: Why 7 phases, not 3 or 15?
  - **Alternatives Explored**:
    - Coarser (3 phases): Simpler, but hides dependencies
    - Finer (15 phases): Atomic failures, but testing explodes (2^15 combinations)
    - Seven phases: Information-theoretic sweet spot
  - **Hardware Grounding**: x86 state transitions (real-mode → protected mode → paging)
  - **Principle Synthesis**: Microkernel design—kernel completion vs. service startup
  - **Design Insight**: Phase boundaries enforce trust and isolation boundaries
- **Critical for Understanding**: Lions-style design explanation of boot topology
- **Used In**: Chapter 4 Section 1-2 (Boot Topology Pilot)

### Figure 7: CPU Register State During Boot Phases
- **File**: `pgfplots-charts/fig-07-cpu-registers.png`
- **Page**: 58 | **DPI**: 300 | **Size**: 55 KB
- **Description**: CPU register values across boot phases
- **What it Shows**:
  - General-purpose registers (EAX, EBX, ECX, EDX)
  - Stack pointer (ESP) progression
  - Instruction pointer (EIP) advancement
  - Control registers (CR0, CR3 changes) across phases
- **Measurement Purpose**: Validates that state transitions occur as expected
- **Used In**: Chapter 4 Section 2 (supporting measurements)

### Figure 8: Boot Phase Durations (Measured in QEMU)
- **File**: `pgfplots-charts/fig-08-boot-durations.png`
- **Page**: 60 | **DPI**: 300 | **Size**: 42 KB
- **Description**: Time spent in each of 7 boot phases
- **What it Shows**:
  - Phases 0-2 (kernel init): ~0.8-2.1 ms each
  - Phase 3 (scheduler): ~0.5 ms
  - Phases 4-6 (services): ~1-4 ms each
  - Kernel completion: ~9.2 ms total
- **Lions Pedagogy**: Demonstrates why kernel phases are tight (deterministic) vs. service phases (hardware-dependent)
- **Used In**: Chapter 4 Section 1 (Pilot 1 empirical grounding)

### Figure 9: Boot Sequence Timeline
- **File**: `tikz-diagrams/fig-09-boot-timeline.png`
- **Page**: 62 | **DPI**: 300 | **Size**: 41 KB
- **Description**: Boot timeline showing phase progression
- **What it Shows**:
  - Horizontal timeline from bootloader entry through shell ready
  - Phase markers at transitions
  - Critical path (dependency chain)
  - Total duration: 9-12 ms typical
- **Used In**: Chapter 4 Section 1 (Pilot 1 narrative)

### Figure 10: Memory Allocation During Boot
- **File**: `pgfplots-charts/fig-10-memory-allocation.png`
- **Page**: 65 | **DPI**: 300 | **Size**: 6.6 KB
- **Description**: Memory usage progression across boot phases
- **What it Shows**:
  - Initial state: minimal memory used
  - Phase 2: page table allocation
  - Phase 3: process table allocation
  - Phase 4-6: service memory allocation
  - Final state: ~8-12 MB total
- **Used In**: Chapter 4 Section 1 (supporting measurement)

### Figure 11: Detailed Boot Sequence Flowchart
- **File**: `tikz-diagrams/fig-11-boot-detailed.png`
- **Page**: 67 | **DPI**: 300 | **Size**: 53 KB
- **Description**: Detailed boot flowchart with decision points and error paths
- **What it Shows**:
  - Every initialization step
  - Decision points (success/failure branches)
  - Error recovery paths
  - Success and failure outcomes
- **Lions Pedagogy**: Shows how architecture enables error recovery through service isolation
- **Used In**: Chapter 4 Section 2 (detailed control flow)

### Figure 12: Boot Time Distribution
- **File**: `pgfplots-charts/fig-12-boot-distribution.png`
- **Page**: 70 | **DPI**: 300 | **Size**: 86 KB
- **Description**: Boot time distribution across 100+ runs
- **What it Shows**:
  - Histogram of boot times
  - Mean: 9.2 ms
  - Median: 9.1 ms
  - Range: 8.0-12.5 ms (2.5 ms variance)
  - Tight concentration showing deterministic behavior
- **Lions Pedagogy (PILOT 1 Conclusion)**:
  - Demonstrates that kernel-only boot is highly deterministic (tight variance)
  - Shows why 7-phase structure enables predictable behavior
  - Explains difference vs. full-system boot (50-200 ms, loose variance)
- **Used In**: Chapter 4 Section 3 (Pilot 1 Results)

---

## CHAPTER 5: ERROR ANALYSIS

### Figure 13: MINIX 3.4 Error Catalog (15-Error Registry)
- **File**: `pgfplots-charts/fig-13-error-catalog.png`
- **Page**: 82 | **DPI**: 300 | **Size**: 45 KB
- **Description**: 15 documented error types with frequency matrix
- **What it Shows**:
  - All 15 error codes (E001-E015)
  - Occurrence frequency in testing
  - Error severity indicators
  - Co-occurrence patterns (which errors happen together)
- **Used In**: Chapter 5 Section 1 (Error Catalog Overview)

### Figure 14: Error Detection Algorithm Flowchart
- **File**: `tikz-diagrams/fig-14-error-detection-algo.png`
- **Page**: 85 | **DPI**: 300 | **Size**: 50 KB
- **Description**: Automated error detection workflow
- **What it Shows**:
  - Log input
  - Regex pattern matching against 15 error types
  - Confidence scoring
  - Database storage
  - Escalation for high-confidence errors
- **Lions Pedagogy**: Shows how architecture principles enable automated error detection
- **Used In**: Chapter 5 Section 2 (Detection Algorithms)

### Figure 15: Error Detection Regex Patterns
- **File**: `pgfplots-charts/fig-15-error-regex.png`
- **Page**: 87 | **DPI**: 300 | **Size**: 63 KB
- **Description**: Regex pattern coverage for error detection
- **What it Shows**:
  - Each of 15 error types
  - Number of regex patterns per type
  - Pattern overlap and collisions
  - False positive/negative rates
- **Used In**: Chapter 5 Section 2 (Pattern Documentation)

### Figure 16: Error Frequency and Impact
- **File**: `pgfplots-charts/fig-16-error-frequency.png`
- **Page**: 89 | **DPI**: 300 | **Size**: 52 KB
- **Description**: Occurrence frequency vs. system impact
- **What it Shows**:
  - X-axis: Error type (E001-E015)
  - Y-axis: Frequency in 100+ test runs
  - Point size: Recovery difficulty
  - Color: Severity (recoverable → critical)
- **Lions Pedagogy**: Empirical validation that error distribution is non-uniform; architecture affects error patterns
- **Used In**: Chapter 5 Section 1 (Error Statistics)

### Figure 17: Error Causal Relationship Graph
- **File**: `tikz-diagrams/fig-17-error-graph.png`
- **Page**: 91 | **DPI**: 300 | **Size**: 49 KB
- **Description**: Directed graph showing error causality and co-occurrence
- **What it Shows**:
  - Nodes: 15 error types
  - Edges: Causal relationships (E001 can cause E003, etc.)
  - Edge thickness: co-occurrence frequency
  - Clusters: related error groups
- **Lions Pedagogy**: Demonstrates how system architecture creates predictable error patterns
- **Used In**: Chapter 5 Section 3 (Error Patterns and Relationships)

---

## CHAPTER 6: ARCHITECTURE (PILOT 2 - SYSCALL DESIGN)

### Figure 18: System Call Mechanism Selection
- **File**: `pgfplots-charts/fig-18-syscall-selection.png`
- **Page**: 102 | **DPI**: 300 | **Size**: 52 KB
- **Description**: CPU support for three syscall mechanisms
- **What it Shows**:
  - Hardware availability across generations
  - INT 0x80h: Universal (1974-2025, all x86)
  - SYSENTER: Intel-only (1997-present, Pentium Pro+)
  - SYSCALL: AMD (1998-present, AMD K6+) and modern Intel
- **Lions Pedagogy (PILOT 2 Foundation)**: Shows how CPU instruction set evolution forces design choices
- **Used In**: Chapter 6 Section 3 (Syscall Evolution Context)

### Figure 19: System Call Latency Comparison
- **File**: `pgfplots-charts/fig-19-syscall-latency.png`
- **Page**: 105 | **DPI**: 300 | **Size**: 45 KB
- **Description**: Syscall latency in CPU cycles for three mechanisms
- **What it Shows**:
  - INT 0x80h: 1772 cycles (baseline)
  - SYSENTER: 1305 cycles (-26%, fastest)
  - SYSCALL: 1439 cycles (-19%, middle ground)
  - Measurement environment: QEMU, dedicated CPU, deterministic
- **Lions Pedagogy (PILOT 2 Core)**:
  - **Question**: Why do three mechanisms coexist?
  - **Performance vs. Universality Trade-off**:
    - INT 0x80h: Universally available, reliable, but slow
    - SYSENTER: Fast on Intel, but unavailable on AMD (until recently)
    - SYSCALL: AMD's competitive response, now mainstream
  - **Hardware Grounding**: MSR-based entry points, automatic context save differences
  - **Design Principle**: MINIX supports all three, auto-detects fastest available
  - **Insight**: Operating systems evolve with CPU features; backward compatibility matters
- **Critical for Understanding**: Lions-style explanation of design trade-offs in syscall mechanisms
- **Used In**: Chapter 6 Section 3-4 (Syscall Latency Pilot)

### Figure 20: Complete MINIX 3.4 System Architecture
- **File**: `tikz-diagrams/fig-20-system-arch.png`
- **Page**: 107 | **DPI**: 300 | **Size**: 31 KB
- **Description**: Full system architecture showing kernel, services, and application layers
- **What it Shows**:
  - Kernel core (95 KB, central)
  - Kernel subsystems: memory manager, IPC, scheduler, interrupt handler
  - User-space services: file system, drivers, network
  - Applications layer at top
- **Used In**: Chapter 6 Section 1 (System Design Overview)

### Figure 21: Process and IPC Architecture
- **File**: `tikz-diagrams/fig-21-process-ipc.png`
- **Page**: 110 | **DPI**: 300 | **Size**: 45 KB
- **Description**: Process communication and kernel message routing
- **What it Shows**:
  - Independent process boxes (isolated)
  - Message queues between processes
  - Kernel routing role
  - IPC paths for common operations (file I/O, network, drivers)
- **Lions Pedagogy**: Shows how architecture enforces isolation through IPC boundaries
- **Used In**: Chapter 6 Section 2 (Process Architecture)

---

## CHAPTER 10: ERROR REFERENCE

### Figure 22: Error Detection and Recovery Flowchart
- **File**: `tikz-diagrams/fig-22-error-recovery.png`
- **Page**: 180 | **DPI**: 300 | **Size**: 67 KB
- **Description**: Complete error detection and recovery workflow
- **What it Shows**:
  - Error detection (log analysis, regex matching)
  - Classification into 15-error taxonomy
  - Recovery strategy selection:
    - Automatic (restart service)
    - Guided (requires admin action)
    - Manual (documentation provided)
    - Critical halt (system shutdown)
  - Recovery execution and verification
  - Logging and escalation on failure
- **Lions Pedagogy**: Demonstrates how microkernel design enables per-service recovery without system halt
- **Used In**: Chapter 10 (Error Reference and Recovery)

---

## SUMMARY BY PEDAGOGICAL PURPOSE

### Lions-Style Design Questions Addressed

| Question | Figure(s) | Chapter | Type |
|----------|-----------|---------|------|
| Why 7-phase boot structure? | fig-06, fig-09, fig-11, fig-12 | Ch 4 | PILOT 1 |
| Why 3 syscall mechanisms coexist? | fig-18, fig-19 | Ch 6 | PILOT 2 |
| Why synchronous IPC? | fig-02 | Ch 2 | Fundamental |
| Why isolate drivers in user space? | fig-01 | Ch 1 | Architectural |
| Why x86 memory layout matters? | fig-03 | Ch 2 | Hardware |
| Why error detection necessary? | fig-14, fig-17, fig-22 | Ch 5, 10 | Resilience |
| Why microkernel resilience? | fig-01, fig-22 | Ch 1, 10 | Principle |

### Figure Organization by Type

**Architecture & Design** (7 figures):
- fig-01: Microkernel overview
- fig-02: Message passing
- fig-03: Memory layout
- fig-20: System architecture
- fig-21: Process IPC
- fig-04: Data pipeline
- fig-05: Workflow

**Boot Analysis** (5 figures):
- fig-06: Phase structure
- fig-07: CPU state
- fig-08: Phase durations
- fig-09: Timeline
- fig-10: Memory allocation
- fig-11: Detailed flowchart
- fig-12: Distribution (7 total)

**Error Analysis** (5 figures):
- fig-13: Error catalog
- fig-14: Detection algorithm
- fig-15: Regex patterns
- fig-16: Frequency/impact
- fig-17: Causal graph
- fig-22: Recovery (6 total)

**Syscall Analysis** (2 figures):
- fig-18: Mechanism selection
- fig-19: Latency comparison

---

## Cross-References

### By Chapter

- **Chapter 1**: fig-01
- **Chapter 2**: fig-02, fig-03
- **Chapter 3**: fig-04, fig-05
- **Chapter 4**: fig-06, fig-07, fig-08, fig-09, fig-10, fig-11, fig-12
- **Chapter 5**: fig-13, fig-14, fig-15, fig-16, fig-17
- **Chapter 6**: fig-18, fig-19, fig-20, fig-21
- **Chapter 10**: fig-22

### By Topic

- **Microkernel Principles**: fig-01, fig-02, fig-21
- **Boot Sequence**: fig-06, fig-07, fig-08, fig-09, fig-10, fig-11, fig-12
- **Memory/Addressing**: fig-03, fig-10, fig-20
- **IPC/Messaging**: fig-02, fig-21
- **Error Handling**: fig-13, fig-14, fig-15, fig-16, fig-17, fig-22
- **Syscalls**: fig-18, fig-19
- **Data/Workflow**: fig-04, fig-05

---

**Index Updated**: November 2, 2025  
**Total Figures**: 22  
**Total Size**: 1.1 MB at 300 DPI PNG
