# Examples: Learning Paths and Practical Workflows

This section provides concrete learning paths and hands-on examples for understanding MINIX through different approaches: from quick starts to deep technical dives.

## Organization

Examples are organized by **learning style and time investment**, not by topic. Pick the path that matches your needs.

### Quick-Start Guides (15-30 minutes each)

| Guide | Goal | Audience |
|-------|------|----------|
| PROFILING-QUICK-START.md | Boot MINIX and collect profiling data | Anyone curious about MINIX internals |
| MCP-QUICK-START.md | Query analysis data using MCP tools | Researchers, tool users |
| CLI-EXECUTION-GUIDE.md | Run MINIX from command line | System administrators, students |

### Intermediate Workflows (1-2 hours each)

| Guide | Goal | Audience |
|-------|------|----------|
| RUNTIME-SETUP-GUIDE.md | Configure MINIX runtime environment | Developers, researchers |
| MCP-INTEGRATION-GUIDE.md | Integrate analysis into your tools | Tool builders, integrators |
| PROFILING-ENHANCEMENT-GUIDE.md | Extend profiling with custom measurements | Advanced users, contributors |

### Comprehensive References (4-8 hours each)

| Guide | Goal | Audience |
|-------|------|----------|
| INDEX.md | Complete reference of all examples | Everyone needing full documentation |
| ORGANIZATION-STATUS-REPORT.md | How examples are organized and why | Project maintainers, contributors |

## How to Use This Section

### Path 1: "I Have 15 Minutes"

1. **Read**: PROFILING-QUICK-START.md (first section only)
2. **Do**: Boot MINIX in QEMU using provided script
3. **See**: Real system behavior, not abstractions
4. **Next**: Architecture/README.md (understand what you saw)

**Time**: 15 minutes
**Outcome**: Hands-on experience with MINIX

### Path 2: "I Have an Hour"

1. **Read**: CLI-EXECUTION-GUIDE.md (complete)
2. **Do**: Set up MINIX runtime environment
3. **Read**: PROFILING-QUICK-START.md (first 30 minutes)
4. **Do**: Collect boot profiling data
5. **Read**: docs/analysis/BOOT-SEQUENCE-ANALYSIS.md (match data to theory)

**Time**: 60 minutes
**Outcome**: Understand boot sequence empirically

### Path 3: "I Have Half a Day (4 Hours)"

1. **Read**: MCP-QUICK-START.md (understand tooling)
2. **Setup**: MCP-INTEGRATION-GUIDE.md (configure tools)
3. **Read**: docs/architecture/README.md (understand components)
4. **Explore**: Use MCP tools to query analysis data
5. **Read**: docs/analysis/SYNTHESIS.md (how it all fits)

**Time**: 4 hours
**Outcome**: Full understanding of MINIX architecture with hands-on exploration

### Path 4: "I'm Doing Research (Full Day+)"

1. **Read**: ORGANIZATION-STATUS-REPORT.md (understand documentation structure)
2. **Read**: docs/audits/QUALITY-METRICS.md (verify completeness)
3. **Do**: PROFILING-ENHANCEMENT-GUIDE.md (collect original data)
4. **Read**: docs/analysis/ (all sections)
5. **Cross-reference**: MINIX source code directly
6. **Document**: Your findings using Lions-style approach

**Time**: 8+ hours
**Outcome**: Publication-ready analysis with verified measurements

## Learning by Interest

### I Want to Understand Boot Sequence

1. Start: PROFILING-QUICK-START.md (collect boot data)
2. Read: docs/analysis/BOOT-SEQUENCE-ANALYSIS.md (interpret data)
3. Deep dive: docs/architecture/BOOT-TIMELINE.md (phase-by-phase breakdown)
4. Cross-reference: MINIX source (lib/csu/ directory)

### I Want to Understand System Calls

1. Start: CLI-EXECUTION-GUIDE.md (run a simple program)
2. Read: docs/architecture/CPU-INTERFACE-ANALYSIS.md (how syscalls work)
3. Deep dive: docs/architecture/syscalls/ (three mechanisms)
4. Measure: docs/performance/CPU-UTILIZATION-ANALYSIS.md (syscall costs)
5. Verify: MINIX source (kernel/system/do_*.c files)

### I Want to Understand Memory Management

1. Start: docs/architecture/MEMORY-LAYOUT-ANALYSIS.md (overview)
2. Read: docs/architecture/memory/ (paging details)
3. Measure: docs/performance/ (TLB behavior)
4. Cross-reference: MINIX source (kernel/arch/i386/)

### I Want to Understand Process Management

1. Start: docs/architecture/README.md (architecture overview)
2. Read: docs/analysis/SYNTHESIS.md (how processes relate to other systems)
3. Deep dive: docs/architecture/PROCESS-MANAGEMENT.md
4. Verify: MINIX source (kernel/proc.h, kernel/proc.c)

## Practical Workflows

### Workflow 1: Verify a Claim

**You read**: "SYSENTER is fastest syscall"

**To verify**:
1. PROFILING-QUICK-START.md (set up measurement environment)
2. PROFILING-ENHANCEMENT-GUIDE.md (add syscall timing measurement)
3. Collect data and compare SYSENTER vs INT vs SYSCALL
4. Cross-reference: docs/architecture/SYSCALL-ARCHITECTURE.md

**Expected outcome**: Measurements confirm or refute claim

### Workflow 2: Extend Analysis for Publication

**You want**: Original MINIX measurements for your paper

**To implement**:
1. ORGANIZATION-STATUS-REPORT.md (understand what's already measured)
2. docs/audits/QUALITY-METRICS.md (identify gaps)
3. PROFILING-ENHANCEMENT-GUIDE.md (design new measurements)
4. Collect original data using MINIX QEMU environment
5. Document using Lions-style approach (see docs/standards/)

**Expected outcome**: Publication-ready measurements

### Workflow 3: Teach MINIX to Students

**You need**: Learning materials for OS course

**To create**:
1. Pick a topic: Boot sequence, memory management, or syscalls
2. PROFILING-QUICK-START.md (show students hands-on)
3. docs/architecture/ and docs/analysis/ (reading assignments)
4. PROFILING-ENHANCEMENT-GUIDE.md (advanced student project)

**Expected outcome**: Complete lesson plan with hands-on component

## Setup and Prerequisites

### Minimum Requirements

- Linux system (CachyOS recommended, Arch/Debian/Ubuntu okay)
- 4 GB RAM minimum (8 GB recommended)
- QEMU installed (qemu-system-i386)
- MINIX 3.4.0-RC6 ISO (provided in repo)
- Python 3.8+ (for data processing)

### Recommended Additional Tools

- Performance profiling tools (linux-tools, perf)
- TikZ/LaTeX (if generating diagrams)
- Git (for tracking changes)
- Docker (for reproducible environment)

### Setup Time

- Basic QEMU setup: 5 minutes
- Full profiling environment: 15-20 minutes
- Custom measurement tools: 30-45 minutes

See CLI-EXECUTION-GUIDE.md and RUNTIME-SETUP-GUIDE.md for detailed setup.

## File Structure

```
examples/
├── README.md                          (this file)
├── PROFILING-QUICK-START.md           (15 min: boot & profile)
├── MCP-QUICK-START.md                 (15 min: query data)
├── CLI-EXECUTION-GUIDE.md             (30 min: run MINIX)
├── RUNTIME-SETUP-GUIDE.md             (60 min: configure env)
├── MCP-INTEGRATION-GUIDE.md           (60 min: integrate tools)
├── PROFILING-ENHANCEMENT-GUIDE.md     (90 min: extend analysis)
├── INDEX.md                           (complete reference)
└── ORGANIZATION-STATUS-REPORT.md      (documentation meta)
```

## Connection to Other Sections

**Architecture** (docs/architecture/):
- Provides theoretical understanding for what examples demonstrate

**Analysis** (docs/analysis/):
- Explains what you're observing in hands-on examples

**Performance** (docs/performance/):
- Shows how to measure and analyze MINIX behavior

**Standards** (docs/standards/):
- Explains how to document your own findings

## Tips for Success

### Debugging QEMU Boot

If MINIX won't boot:
1. Check: scripts/qemu-launch.sh --help (usage)
2. Check: Disk image created successfully (4 GB qcow2)
3. Check: ISO file readable and valid
4. Try: --debug mode to see console output
5. Refer: CLI-EXECUTION-GUIDE.md (troubleshooting section)

### Interpreting Profiling Data

Profiling can be overwhelming. Use this approach:
1. Collect data (PROFILING-QUICK-START.md)
2. Filter to a specific component (e.g., boot phase)
3. Read analysis section about that component
4. Verify: Do measurements match expectations?
5. Investigate: Unexpected results → deep dive

### Contributing New Examples

Have a workflow that should be shared? Follow:
1. Document in Lions-style (explain why, then what)
2. Include timing estimates (how long does it take?)
3. List prerequisites (what's needed?)
4. Provide troubleshooting section
5. Add file to examples/INDEX.md

## Navigation

- [Return to docs/](../README.md)
- [Architecture Overview](../architecture/README.md) - Theory behind examples
- [Analysis Documents](../analysis/README.md) - Deeper explanations
- [Performance Measurements](../performance/README.md) - Data driving examples
- [Standards & Documentation](../standards/README.md) - How to extend examples

---

**Updated**: November 1, 2025
**Learning Paths**: 4 paths from 15 minutes to full day
**Workflows**: 3 practical applications documented
**Difficulty**: Beginner to Advanced
**Status**: Ready for educational and research use
