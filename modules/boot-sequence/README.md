# MINIX Boot Sequence Analysis

**Module**: Boot Sequence Analysis
**Paper**: Exhaustive Analysis of the MINIX-3 Kernel Boot Sequence
**Status**: Complete ✅

---

## Overview

This module provides a **line-by-line decomposition** of the MINIX boot sequence from `kmain()` to userspace transition, aligned with the umbrella guidance captured in `MEGA-BEST-PRACTICES.md`. Analysis covers:

- **Hub-and-spoke topology** (kmain() degree 34)
- **5-phase initialization process** (85-100ms total)
- **Critical path analysis**
- **Infinite loop myth debunking**

---

## Key Findings

- ✅ **Hub-and-spoke topology**, NOT linear/sequential
- ✅ **Directed Acyclic Graph (DAG)** - no cycles
- ✅ **5 phases**: cstart → proc_init → memory_init → system_init → bsp_finish_booting
- ✅ **NO infinite loop** - switch_to_user() never returns
- ✅ **34 functions traced**, 8 source files analyzed

---

## Contents

```
boot-sequence/
├── latex/              # LaTeX papers
│   ├── minix_boot_whitepaper_arxiv.tex    # ArXiv submission
│   ├── minix_boot_ULTRA_DENSE.tex         # Dense reference
│   ├── minix_boot_comprehensive.tex       # Full analysis
│   ├── figures/                           # TikZ diagrams
│   └── plots/                             # Data plots
├── mcp/                # MCP server components
│   ├── boot_data_loader.py                # Data loader
│   └── boot_tools.py                      # MCP tools
├── pipeline/           # Analysis scripts
│   ├── trace_boot_sequence.sh             # Boot tracer
│   ├── deep_dive.sh                       # Function analyzer
│   ├── extract_functions.sh               # Call extractor
│   ├── find_definition.sh                 # Definition finder
│   ├── generate_dot_graph.sh              # Graph generator
│   └── analyze_graph_structure.sh         # Graph analyzer
├── docs/               # Wiki content
├── tests/              # Module tests
├── Makefile            # Build system
└── README.md           # This file
```

---

## Build

### Compile Papers

```bash
cd latex

# ArXiv paper
pdflatex minix_boot_whitepaper_arxiv.tex
bibtex minix_boot_whitepaper_arxiv
pdflatex minix_boot_whitepaper_arxiv.tex
pdflatex minix_boot_whitepaper_arxiv.tex

# Ultra-dense reference
pdflatex minix_boot_ULTRA_DENSE.tex

# Comprehensive analysis
pdflatex minix_boot_comprehensive.tex
```

All manuscripts import the shared style suite in `shared/styles/` (`minix-arxiv.sty`, `minix-styles.sty`, `minix-colors.sty`); update those centrally for global typography or color tweaks.

### Use Makefile

```bash
# From module root
make all          # Build all papers
make clean        # Remove build artifacts
make help         # Show available targets
```

### From Project Root

```bash
cd /home/eirikr/Playground/minix-analysis
make boot         # Build boot module
```

---

## Analysis Tools

### Shell Scripts (POSIX-compliant)

All scripts require MINIX source code:

```bash
export MINIX_SRC=/path/to/minix
```

#### 1. **trace_boot_sequence.sh** - Boot Sequence Tracer

Traces all function calls from `kmain()` through the boot sequence.

**Usage**:
```bash
./pipeline/trace_boot_sequence.sh $MINIX_SRC 3
```

**Output**:
- `boot_trace_output/call_graph.txt` - Complete call graph
- `boot_trace_output/functions_summary.txt` - Statistics

#### 2. **deep_dive.sh** - Deep Function Analyzer

Extracts complete information about a function (docs, source, calls).

**Usage**:
```bash
./pipeline/deep_dive.sh $MINIX_SRC kmain output.md
```

#### 3. **extract_functions.sh** - Function Call Extractor

Extracts all function calls from a specific function.

**Usage**:
```bash
./pipeline/extract_functions.sh $MINIX_SRC/minix/kernel/main.c kmain
```

#### 4. **find_definition.sh** - Function Definition Finder

Searches for function definitions across the source tree.

**Usage**:
```bash
./pipeline/find_definition.sh $MINIX_SRC proc_init
```

#### 5. **generate_dot_graph.sh** - DOT Graph Generator

Creates Graphviz DOT files for call graph visualization.

**Usage**:
```bash
./pipeline/generate_dot_graph.sh < call_graph.txt > boot.dot
dot -Tpdf boot.dot -o boot.pdf
```

#### 6. **analyze_graph_structure.sh** - Graph Analyzer

Analyzes topology, metrics, and structure of the call graph.

**Usage**:
```bash
./pipeline/analyze_graph_structure.sh call_graph.txt
```

---

## MCP Tools

This module provides MCP server tools for interactive querying:

### Available Tools

1. **`query_boot_sequence`**
   - Query topology, phases, critical path, metrics
   - Aspects: `topology`, `phases`, `critical_path`, `metrics`, `infinite_loop`, `all`

2. **`trace_boot_phase`**
   - Get detailed information about a specific boot phase
   - Phases: `phase1` through `phase5`

### Usage

Start the unified MCP server:

```bash
cd /home/eirikr/Playground/minix-analysis/mcp/servers/minix-analysis
python __main__.py
```

Then use MCP client to call tools (see MCP documentation).

---

## Dependencies

### LaTeX (Required)

- TeX Live 2023 or later
- Packages: tikz, pgfplots, algorithm, booktabs, hyperref, etc.
- Shared styles from `../../shared/styles/`

### Shell Scripts (Optional)

- POSIX sh (bash, dash, zsh compatible)
- Standard UNIX tools: awk, grep, sed, find, sort, uniq
- MINIX source code (optional, analysis outputs already included)

### Python/MCP (Optional)

For MCP server functionality:
- Python 3.10+
- MCP package
- See `../../REQUIREMENTS.md` for details

---

## Key Discoveries

### 1. Hub-and-Spoke Topology

`kmain()` acts as a **central hub** with degree 34, orchestrating initialization through direct function calls. This is NOT a linear sequence.

### 2. Five Boot Phases

1. **Phase 1: Early C Initialization** (`cstart`)
   - Protection, clock, interrupts, architecture setup

2. **Phase 2: Process Table Initialization** (`proc_init`)
   - Clear process table, set up kernel tasks, idle process

3. **Phase 3: Memory Management Initialization** (`memory_init`)
   - Physical memory detection, page allocator setup

4. **Phase 4: System Services Initialization** (`system_init`)
   - System call handlers, IPC mechanism

5. **Phase 5: Usermode Transition** (`bsp_finish_booting`)
   - CPU identification, timer, FPU, **switch to usermode**

### 3. No Infinite Loop

**Myth**: "kmain() has an infinite loop"
**Reality**: `switch_to_user()` **never returns** (marked `NOT_REACHABLE`)

After boot, the kernel only runs on interrupts/syscalls. There is no loop in `kmain()`.

### 4. Directed Acyclic Graph

The call graph is a **DAG** with no cycles. Initialization is strictly ordered.

---

## Testing

```bash
# From module root
make test

# Or from project root
cd /home/eirikr/Playground/minix-analysis
make test-boot
```

---

## References

1. **MINIX Source**: [github.com/Stichting-MINIX-Research-Foundation/minix](https://github.com/Stichting-MINIX-Research-Foundation/minix)
2. **Tanenbaum & Woodhull**: *Operating Systems: Design and Implementation*
3. **Project Wiki**: `../../wiki/boot-sequence/`

---

## Integration

This module is part of the **MINIX Analysis Umbrella Project**.

- **Root**: `/home/eirikr/Playground/minix-analysis`
- **Shared Styles**: `../../shared/styles/`
- **Shared MCP**: `../../shared/mcp/`
- **Unified Build**: `../../Makefile`

See `../../README.md` for complete project documentation.

---

## Contributing

See `../../CONTRIBUTING.md` for guidelines on:
- Code style (POSIX shell compliance)
- Testing requirements
- Documentation standards
- Pull request process

---

## License

MIT License - see `../../LICENSE`

**MINIX** is a trademark of Vrije Universiteit Amsterdam.

---

**Last Updated**: 2025-10-30
**Author**: Oaich (eirikr)
**Status**: Production Ready ✅

*Understanding operating systems, one syscall at a time.*
