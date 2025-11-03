# MINIX Analysis - Migration Plan

**Version**: 1.0.0
**Date**: 2025-10-30
**Status**: Ready for Execution

---

## Overview

This document provides a **step-by-step migration plan** to transform the current two-repository structure into the unified umbrella architecture defined in `UMBRELLA-ARCHITECTURE.md`.

**Timeline**: 2-4 hours (sequential execution)
**Risk Level**: LOW (all existing work preserved, reversible)

---

## Pre-Migration Checklist

Before starting, verify:

- [ ] Current directory: `/home/eirikr/Playground/minix-cpu-analysis`
- [ ] Git repository is clean (`git status`)
- [ ] All tests pass (`python mcp/servers/minix-analysis/test_boot_integration.py`)
- [ ] LaTeX compiles (`cd latex/figures && pdflatex 05-syscall-int-flow.tex`)
- [ ] Backup created: `tar czf ../minix-cpu-analysis-backup-$(date +%Y%m%d).tar.gz .`

---

## Migration Phases

### Phase 1: Rename and Create Structure (15 min)

**Goal**: Rename project and create umbrella directory structure

#### Step 1.1: Rename Project Root

```bash
cd /home/eirikr/Playground
mv minix-cpu-analysis minix-analysis
cd minix-analysis
```

#### Step 1.2: Create Tier 1 Directories

```bash
# Create umbrella structure
mkdir -p shared/{styles,mcp/server,pipeline,docs-templates,tests}
mkdir -p modules/{cpu-interface,boot-sequence,template}
mkdir -p wiki/docs
mkdir -p arxiv-submissions
mkdir -p scripts
```

#### Step 1.3: Verification

```bash
tree -L 2 -d  # Should show new structure
```

**Expected Output**:
```
.
├── shared
│   ├── styles
│   ├── mcp
│   ├── pipeline
│   ├── docs-templates
│   └── tests
├── modules
│   ├── cpu-interface
│   ├── boot-sequence
│   └── template
├── wiki
│   └── docs
├── arxiv-submissions
└── scripts
```

---

### Phase 2: Extract Shared Styles (20 min)

**Goal**: Move LaTeX styles to shared location and create color/arxiv packages

#### Step 2.1: Move Master Style Package

```bash
# Move minix-styles.sty to shared
mv latex/minix-styles.sty shared/styles/
mv latex/TIKZ-STYLE-GUIDE.md shared/styles/STYLE-GUIDE.md
```

#### Step 2.2: Create minix-colors.sty

```bash
cat > shared/styles/minix-colors.sty << 'EOF'
% minix-colors.sty
% Unified color palette for all MINIX analysis papers
% Version: 1.0.0
% Date: 2025-10-30

\ProvidesPackage{minix-colors}[2025/10/30 v1.0 MINIX Analysis Color Palette]

% Require xcolor
\RequirePackage{xcolor}

% Primary Palette (from minix-styles.sty)
\definecolor{primaryblue}{RGB}{0,102,204}
\definecolor{secondarygreen}{RGB}{46,204,113}
\definecolor{accentorange}{RGB}{255,127,0}
\definecolor{warningred}{RGB}{231,76,60}

% Supporting Colors
\definecolor{lightgray}{RGB}{236,240,241}
\definecolor{darkgray}{RGB}{52,73,94}
\definecolor{mediumgray}{RGB}{149,165,166}

% Boot Phase Colors (harmonized with primary palette)
\definecolor{phase1}{RGB}{52,152,219}    % Blue - Early Init (cstart)
\definecolor{phase2}{RGB}{46,204,113}    % Green - Process Init (proc_init)
\definecolor{phase3}{RGB}{155,89,182}    % Purple - Memory Init (memory_init)
\definecolor{phase4}{RGB}{230,126,34}    % Orange - System Init (system_init)
\definecolor{phase5}{RGB}{231,76,60}     % Red - Usermode (bsp_finish_booting)

% Semantic Color Aliases
\colorlet{critical}{warningred}
\colorlet{flowbox}{primaryblue!15}
\colorlet{hardware}{warningred!20}
\colorlet{kernel}{secondarygreen!15}
\colorlet{background}{lightgray!50}

% Legacy Compatibility (CPU diagrams)
\colorlet{cpubox}{blue!10}
\colorlet{hwbox}{red!20}
\colorlet{annotation}{yellow!30}

\endinput
EOF
```

#### Step 2.3: Create minix-arxiv.sty

```bash
cat > shared/styles/minix-arxiv.sty << 'EOF'
% minix-arxiv.sty
% ArXiv-compliant formatting for MINIX analysis papers
% Version: 1.0.0
% Date: 2025-10-30
% Conforms to: TeX Live 2023 + ArXiv guidelines

\ProvidesPackage{minix-arxiv}[2025/10/30 v1.0 MINIX ArXiv Formatting]

% Geometry (ArXiv prefers 1-inch margins)
\RequirePackage[margin=1in]{geometry}

% Fonts
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{lmodern}

% Hyperref (ArXiv requirement: colorlinks=true)
\RequirePackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue,
    pdfauthor={},
    pdftitle={},
    pdfsubject={Operating Systems, MINIX, Microkernel},
    pdfkeywords={MINIX, i386, boot sequence, syscalls, microkernel}
}

% cleveref (must load after hyperref)
\RequirePackage{cleveref}

% Common packages for academic papers
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{booktabs}      % Professional tables
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}
\RequirePackage{listings}      % Code listings
\RequirePackage{float}

% Listings style for C code
\lstdefinestyle{minixcode}{
    language=C,
    basicstyle=\ttfamily\footnotesize,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{green!60!black}\itshape,
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    stepnumber=1,
    numbersep=8pt,
    showstringspaces=false,
    breaklines=true,
    frame=single,
    rulecolor=\color{black!30},
    backgroundcolor=\color{gray!5},
    captionpos=b,
    escapeinside={(*@}{@*)},
    morekeywords={assert,register}
}

\endinput
EOF
```

#### Step 2.4: Update minix-styles.sty to Use New Packages

```bash
# Edit shared/styles/minix-styles.sty
# At the top, after \ProvidesPackage, add:
# \RequirePackage{minix-colors}
# \RequirePackage{minix-arxiv}
```

**Manual edit** (first 10 lines of `shared/styles/minix-styles.sty`):
```latex
\ProvidesPackage{minix-styles}[2025/10/30 v1.0 MINIX Analysis TikZ/PGFPlots Styles]

% Load color palette
\RequirePackage{minix-colors}

% Load ArXiv formatting (optional, for papers)
% \RequirePackage{minix-arxiv}  % Uncomment for ArXiv submissions

\RequirePackage{tikz}
\RequirePackage{pgfplots}
% ... rest of file
```

#### Step 2.5: Test Shared Styles

```bash
# Create test document
cat > /tmp/test-shared-styles.tex << 'EOF'
\documentclass{article}
\usepackage{shared/styles/minix-styles}
\begin{document}
\begin{tikzpicture}[cpu flow]
    \node[box] {Test Box};
    \node[hw] at (0,-1) {Test HW};
\end{tikzpicture}
\end{document}
EOF

cd /tmp
pdflatex test-shared-styles.tex
```

**Expected**: PDF generated without errors

---

### Phase 3: Migrate CPU Interface Module (30 min)

**Goal**: Move CPU analysis content to `modules/cpu-interface/`

#### Step 3.1: Create Module Structure

```bash
cd /home/eirikr/Playground/minix-analysis

mkdir -p modules/cpu-interface/{latex/figures,mcp,pipeline,docs,tests}
```

#### Step 3.2: Move CPU LaTeX Content

```bash
# Move figures
cp -r latex/figures/*.tex modules/cpu-interface/latex/figures/
cp -r latex/figures/*.pdf modules/cpu-interface/latex/figures/

# Create main paper file
cp latex/minix-complete-analysis.tex modules/cpu-interface/latex/minix-cpu-analysis.tex
```

#### Step 3.3: Update LaTeX Imports in CPU Module

Edit `modules/cpu-interface/latex/minix-cpu-analysis.tex`:

```latex
% OLD:
% \usepackage{tikz}
% \usepackage{pgfplots}
% ... inline styles ...

% NEW:
\usepackage{../../shared/styles/minix-styles}  % Relative path to shared styles
```

#### Step 3.4: Move MCP CPU Components

```bash
# Move current MCP server to module
cp -r mcp/servers/minix-analysis/src modules/cpu-interface/mcp/
cp mcp/servers/minix-analysis/pyproject.toml modules/cpu-interface/
cp mcp/servers/minix-analysis/README.md modules/cpu-interface/mcp/
```

#### Step 3.5: Move Pipeline Scripts

```bash
# Move CPU-specific pipeline scripts
mkdir -p modules/cpu-interface/pipeline
cp -r pipeline/* modules/cpu-interface/pipeline/
```

#### Step 3.6: Create Module README

```bash
cat > modules/cpu-interface/README.md << 'EOF'
# MINIX CPU Interface Analysis

**Module**: CPU Interface Analysis
**Paper**: System Call Mechanisms and Memory Management in MINIX 3.4.0-RC6

## Overview

This module analyzes the MINIX i386 CPU interface, focusing on:
- Three system call mechanisms (INT, SYSENTER, SYSCALL)
- 2-level paging architecture
- TLB operation and performance
- Context switch costs

## Key Findings

- ✅ i386 architecture confirmed (NOT x86-64)
- ✅ SYSENTER is fastest syscall (1305 cycles, 26% speedup vs INT)
- ✅ 2-level paging: Page Directory → Page Table
- ✅ TLB miss penalty: ~200 cycles

## Contents

- `latex/`: LaTeX source for CPU analysis paper
  - `minix-cpu-analysis.tex`: Main paper
  - `figures/`: TikZ diagrams (05-11)
- `mcp/`: MCP server components (CPU data loader, tools)
- `pipeline/`: Analysis scripts (symbol extraction, call graphs)
- `docs/`: Wiki content for CPU analysis
- `tests/`: Module-specific tests

## Build

```bash
# Compile all diagrams
cd latex/figures
for file in *.tex; do pdflatex "$file"; done

# Compile main paper
cd ../
pdflatex minix-cpu-analysis.tex
bibtex minix-cpu-analysis
pdflatex minix-cpu-analysis.tex
pdflatex minix-cpu-analysis.tex
```

## Test

```bash
pytest tests/
```

## MCP Tools

This module provides:
- `query_architecture` - i386 architecture queries
- `analyze_syscall` - Syscall mechanism details
- `query_performance` - Performance metrics
- `compare_mechanisms` - Side-by-side comparison
- `explain_diagram` - Diagram explanations

## Dependencies

See `requirements.txt` for Python dependencies.

LaTeX requirements:
- TeX Live 2023 or later
- minix-styles.sty (from shared/styles/)
- TikZ, PGFPlots packages

## References

1. Intel IA-32 Architecture Software Developer's Manual
2. AMD64 Architecture Programmer's Manual
3. MINIX 3 Source Code (GitHub)
EOF
```

---

### Phase 4: Migrate Boot Sequence Module (45 min)

**Goal**: Copy boot analyzer content and harmonize with shared styles

#### Step 4.1: Copy Boot Analyzer Repository

```bash
cd /home/eirikr/Playground/minix-analysis

# Copy entire boot analyzer to module
cp -r /home/eirikr/Playground/minix-boot-analyzer/* modules/boot-sequence/

# Organize structure
cd modules/boot-sequence
mkdir -p latex/figures mcp/src pipeline docs tests
```

#### Step 4.2: Reorganize Boot LaTeX

```bash
cd /home/eirikr/Playground/minix-analysis/modules/boot-sequence

# Move LaTeX files
mv visualizations/minix_boot_whitepaper_arxiv.tex latex/minix-boot-arxiv.tex
mv visualizations/minix_boot_ULTRA_DENSE.tex latex/minix-boot-dense.tex
mv visualizations/minix_boot_comprehensive.tex latex/minix-boot-comprehensive.tex

# Move figure components
mv visualizations/*.tex latex/figures/
mv visualizations/*.pdf latex/figures/

# Keep interactive viz
mv visualizations/interactive_boot_viz.html docs/

# Clean up
rmdir visualizations 2>/dev/null || true
```

#### Step 4.3: Harmonize Boot LaTeX with Shared Styles

Edit `modules/boot-sequence/latex/minix-boot-arxiv.tex`:

**Find and replace**:
```latex
% OLD:
\definecolor{phase1}{RGB}{52,152,219}
\definecolor{phase2}{RGB}{46,204,113}
% ... etc

\usepackage{tikz}
\usepackage{pgfplots}

% NEW:
\usepackage{../../shared/styles/minix-styles}
\usepackage{../../shared/styles/minix-colors}
\usepackage{../../shared/styles/minix-arxiv}

% Phase colors are now in minix-colors.sty - remove local definitions
```

**Test compilation**:
```bash
cd modules/boot-sequence/latex
pdflatex minix-boot-arxiv.tex
```

**Expected**: Should compile with shared styles, colors match original

#### Step 4.4: Extract Boot MCP Components

Create `modules/boot-sequence/mcp/boot_data_loader.py`:

```python
"""Boot Sequence Data Loader for MCP Server"""

from typing import Dict, Any
from pathlib import Path

class BootDataLoader:
    """Loads boot sequence analysis data for MCP tools."""

    def __init__(self):
        self.module_root = Path(__file__).parent.parent
        self._boot_data = None

    def load_boot_sequence_data(self) -> Dict[str, Any]:
        """Load complete boot sequence analysis."""
        if self._boot_data is not None:
            return self._boot_data

        # Load from synthesis documents
        # (Copy logic from current MCP data_loader.py)

        self._boot_data = {
            "topology": {
                "type": "Hub-and-Spoke (Star Network)",
                "central_hub": "kmain()",
                "hub_degree": 34,
                # ... full topology data
            },
            "boot_phases": {
                "phase1": { "name": "Early C Initialization", "function": "cstart()", ... },
                "phase2": { "name": "Process Table Init", "function": "proc_init()", ... },
                # ... all 5 phases
            },
            "critical_path": { "estimated_time": "85-100ms", ... },
            "metrics": { "total_functions_traced": 34, ... },
            "infinite_loop_myth": { "truth": "NO loop in kmain()", ... }
        }

        return self._boot_data
```

Create `modules/boot-sequence/mcp/boot_tools.py`:

```python
"""Boot Sequence MCP Tools"""

from typing import List, Any
from mcp.types import Tool, TextContent
import json

def register_boot_tools(server):
    """Register boot sequence tools with MCP server."""

    @server.list_tools()
    async def list_boot_tools() -> List[Tool]:
        return [
            Tool(
                name="query_boot_sequence",
                description="Query MINIX boot sequence (topology, phases, metrics)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "aspect": {
                            "type": "string",
                            "enum": ["topology", "phases", "critical_path", "metrics", "infinite_loop", "all"],
                            "default": "all"
                        }
                    }
                }
            ),
            Tool(
                name="trace_boot_path",
                description="Trace boot phase or critical path",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "phase": {
                            "type": "string",
                            "enum": ["phase1", "phase2", "phase3", "phase4", "phase5", "critical_path"]
                        }
                    },
                    "required": ["phase"]
                }
            )
        ]

    # Register tool handlers (copy from current server.py)
```

#### Step 4.5: Move Shell Scripts to Pipeline

```bash
cd /home/eirikr/Playground/minix-analysis/modules/boot-sequence

# Move scripts
mkdir -p pipeline/shell-scripts
mv *.sh pipeline/shell-scripts/

# Make executable
chmod +x pipeline/shell-scripts/*.sh
```

#### Step 4.6: Create Boot Module README

```bash
cat > modules/boot-sequence/README.md << 'EOF'
# MINIX Boot Sequence Analysis

**Module**: Boot Sequence Analysis
**Paper**: Exhaustive Analysis of the MINIX-3 Kernel Boot Sequence

## Overview

This module provides a line-by-line decomposition of the MINIX boot sequence from `kmain()` to userspace, analyzing:
- Hub-and-spoke topology (kmain() degree 34)
- 5-phase initialization process
- Critical path analysis (85-100ms)
- Infinite loop myth debunking

## Key Findings

- ✅ Hub-and-spoke topology, NOT linear/sequential
- ✅ Directed Acyclic Graph (DAG) - no cycles
- ✅ 5 phases: cstart → proc_init → memory_init → system_init → bsp_finish_booting
- ✅ NO infinite loop - switch_to_user() never returns
- ✅ 34 functions traced, 8 source files analyzed

## Contents

- `latex/`: LaTeX papers (ArXiv, dense, comprehensive)
- `mcp/`: MCP server components (boot data loader, tools)
- `pipeline/shell-scripts/`: Automated analysis scripts
- `docs/`: Wiki content for boot analysis
- `tests/`: Module-specific tests

## Build

```bash
# Compile ArXiv paper
cd latex
pdflatex minix-boot-arxiv.tex
bibtex minix-boot-arxiv
pdflatex minix-boot-arxiv.tex
pdflatex minix-boot-arxiv.tex
```

## MCP Tools

This module provides:
- `query_boot_sequence` - Topology, phases, metrics
- `trace_boot_path` - Critical path and phase tracing

## Dependencies

See `requirements.txt` for Python dependencies.

LaTeX requirements:
- TeX Live 2023 or later
- minix-styles.sty (from shared/styles/)
- TikZ, PGFPlots, algorithm packages
EOF
```

---

### Phase 5: Consolidate MCP Server (30 min)

**Goal**: Create unified MCP server that registers modules

#### Step 5.1: Create Shared MCP Base Classes

`shared/mcp/server/base_server.py`:
```python
"""Base MCP Server for MINIX Analysis"""

from mcp.server import Server
from typing import Dict, Any

class MINIXAnalysisServer(Server):
    """Unified MCP server for all MINIX analysis modules."""

    def __init__(self, name="minix-analysis"):
        super().__init__(name)
        self.modules = {}

    def register_module(self, module_name: str, loader, tools_func):
        """Register an analysis module with the server."""
        self.modules[module_name] = {
            "loader": loader,
            "tools": tools_func
        }
        print(f"Registered module: {module_name}")
```

`shared/mcp/server/data_loader_base.py`:
```python
"""Base Data Loader for Analysis Modules"""

from abc import ABC, abstractmethod
from pathlib import Path

class BaseDataLoader(ABC):
    """Base class for module-specific data loaders."""

    def __init__(self, module_root: Path):
        self.module_root = module_root

    @abstractmethod
    def load_data(self):
        """Load module-specific data."""
        pass
```

#### Step 5.2: Create Unified MCP Server Entry Point

`mcp/servers/minix-analysis/__main__.py`:
```python
"""Unified MINIX Analysis MCP Server"""

import asyncio
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.mcp.server.base_server import MINIXAnalysisServer
from modules.cpu_interface.mcp.cpu_tools import register_cpu_tools
from modules.boot_sequence.mcp.boot_tools import register_boot_tools

async def main():
    server = MINIXAnalysisServer("minix-analysis")

    # Register CPU module
    register_cpu_tools(server)

    # Register Boot module
    register_boot_tools(server)

    # Run server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Phase 6: Create Shared Build System (20 min)

#### Step 6.1: Root Makefile

Create `/home/eirikr/Playground/minix-analysis/Makefile`:

```makefile
.PHONY: all clean test wiki arxiv help

# Default target
all: cpu-pdfs boot-pdfs

help:
	@echo "MINIX Analysis - Unified Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all             - Build all PDFs (CPU + Boot)"
	@echo "  cpu-pdfs        - Build CPU analysis diagrams and paper"
	@echo "  boot-pdfs       - Build boot sequence papers"
	@echo "  wiki            - Build MkDocs wiki"
	@echo "  wiki-serve      - Serve wiki locally (http://localhost:8000)"
	@echo "  test            - Run all tests"
	@echo "  arxiv-cpu       - Create ArXiv package for CPU paper"
	@echo "  arxiv-boot      - Create ArXiv package for Boot paper"
	@echo "  clean           - Remove build artifacts"

# CPU Interface Module
cpu-pdfs:
	@echo "Building CPU analysis diagrams..."
	$(MAKE) -C modules/cpu-interface/latex/figures
	@echo "Building CPU paper..."
	cd modules/cpu-interface/latex && pdflatex minix-cpu-analysis.tex

# Boot Sequence Module
boot-pdfs:
	@echo "Building boot sequence papers..."
	cd modules/boot-sequence/latex && pdflatex minix-boot-arxiv.tex
	cd modules/boot-sequence/latex && pdflatex minix-boot-dense.tex

# Wiki
wiki:
	@echo "Building unified wiki..."
	cd wiki && mkdocs build

wiki-serve:
	cd wiki && mkdocs serve

# Testing
test:
	@echo "Running tests..."
	pytest shared/tests/ -v
	pytest modules/cpu-interface/tests/ -v
	pytest modules/boot-sequence/tests/ -v

# ArXiv Submissions
arxiv-cpu:
	@echo "Creating ArXiv package for CPU analysis..."
	./scripts/create-arxiv-package.sh cpu-interface

arxiv-boot:
	@echo "Creating ArXiv package for Boot sequence..."
	./scripts/create-arxiv-package.sh boot-sequence

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -name "*.aux" -delete
	find . -name "*.log" -delete
	find . -name "*.out" -delete
	find . -name "*.toc" -delete
	find . -name "*.idx" -delete
	rm -rf wiki/site/
	@echo "Clean complete."
```

#### Step 6.2: Module-Specific Makefiles

`modules/cpu-interface/latex/figures/Makefile`:
```makefile
LATEX = pdflatex
SOURCES = $(wildcard *.tex)
PDFS = $(SOURCES:.tex=.pdf)

all: $(PDFS)

%.pdf: %.tex
	$(LATEX) -interaction=nonstopmode $<

clean:
	rm -f *.aux *.log *.pdf
```

---

### Phase 7: Documentation and Testing (30 min)

#### Step 7.1: Create INSTALLATION.md

```bash
cat > INSTALLATION.md << 'EOF'
# MINIX Analysis - Installation Guide

## Prerequisites

### System Requirements
- Linux (Arch/CachyOS preferred) or macOS
- Python 3.10 or later
- TeX Live 2023 or later
- Git

### Package Managers
- **Arch/CachyOS**: `pacman`
- **macOS**: `brew`
- **Debian/Ubuntu**: `apt`

## Step-by-Step Installation

### 1. Clone Repository

```bash
git clone https://github.com/eirikr/minix-analysis.git
cd minix-analysis
```

### 2. Install LaTeX

**Arch/CachyOS**:
```bash
sudo pacman -S texlive-core texlive-bin texlive-latexextra
```

**macOS**:
```bash
brew install --cask mactex
```

**Ubuntu/Debian**:
```bash
sudo apt install texlive-full
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install umbrella dependencies
pip install -r requirements.txt

# Install module-specific dependencies
pip install -r modules/cpu-interface/requirements.txt
pip install -r modules/boot-sequence/requirements.txt
```

### 4. Verify Installation

```bash
# Test LaTeX
make cpu-pdfs

# Test MCP server
cd mcp/servers/minix-analysis
python -m src.server &
# Should start without errors

# Test wiki
make wiki
```

## Module-Specific Setup

### CPU Interface Module

No additional setup required.

### Boot Sequence Module

Shell scripts require MINIX source code:
```bash
# Clone MINIX (optional, for re-running analysis)
git clone https://github.com/Stichting-MINIX-Research-Foundation/minix.git
export MINIX_SRC=/path/to/minix
```

## Troubleshooting

### LaTeX Errors

**Problem**: `minix-styles.sty not found`
**Solution**: Ensure `shared/styles/` is in LaTeX search path or use relative imports

### Python Import Errors

**Problem**: `ModuleNotFoundError: No module named 'shared'`
**Solution**: Install in development mode:
```bash
pip install -e .
```

### MCP Server Won't Start

**Problem**: Tool registration errors
**Solution**: Check that all module data loaders are importable:
```bash
python -c "from modules.cpu_interface.mcp.cpu_data_loader import CPUDataLoader"
```

## Next Steps

- Read [Architecture Documentation](UMBRELLA-ARCHITECTURE.md)
- Build diagrams: `make all`
- Start wiki: `make wiki-serve`
- Run tests: `make test`
EOF
```

#### Step 7.2: Create Root README.md

```bash
cat > README.md << 'EOF'
# MINIX Analysis

**Comprehensive documentation and analysis of the MINIX 3.4.0-RC6 operating system**

[![Documentation](https://img.shields.io/badge/docs-wiki-blue)](https://eirikr.github.io/minix-analysis/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Overview

This project provides **in-depth analysis** of MINIX across multiple dimensions:

1. **CPU Interface Analysis** - System call mechanisms, memory management, i386 architecture
2. **Boot Sequence Analysis** - Kernel initialization, topology, critical path

**Key Features**:
- 📄 **ArXiv-ready whitepapers** for each analysis
- 🎨 **Unified visual style system** (TikZ/PGFPlots)
- 🔧 **MCP integration** - 7+ interactive query tools
- 📚 **Comprehensive wiki** - MkDocs Material documentation
- 🧪 **Reproducible builds** - Makefile-based automation

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/eirikr/minix-analysis.git
cd minix-analysis

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build all PDFs
make all

# View wiki
make wiki-serve
# Visit http://localhost:8000
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

---

## Project Structure

```
minix-analysis/                     # Umbrella project root
├── modules/                        # Analysis modules (papers)
│   ├── cpu-interface/              # CPU analysis
│   └── boot-sequence/              # Boot sequence analysis
├── shared/                         # Shared infrastructure
│   ├── styles/                     # LaTeX style packages
│   ├── mcp/                        # MCP server base
│   └── pipeline/                   # Analysis tools
├── wiki/                           # Unified documentation portal
└── arxiv-submissions/              # ArXiv submission packages
```

See [UMBRELLA-ARCHITECTURE.md](UMBRELLA-ARCHITECTURE.md) for complete architecture.

---

## Documentation

- **Wiki**: [https://eirikr.github.io/minix-analysis/](https://eirikr.github.io/minix-analysis/)
- **CPU Analysis**: [modules/cpu-interface/README.md](modules/cpu-interface/README.md)
- **Boot Analysis**: [modules/boot-sequence/README.md](modules/boot-sequence/README.md)
- **Architecture**: [UMBRELLA-ARCHITECTURE.md](UMBRELLA-ARCHITECTURE.md)
- **Installation**: [INSTALLATION.md](INSTALLATION.md)

---

## Key Findings

### CPU Interface
- ✅ i386 architecture confirmed (NOT x86-64)
- ✅ SYSENTER fastest syscall: 1305 cycles (26% speedup vs INT)
- ✅ 2-level paging: PD → PT (4 KB pages)
- ✅ TLB miss penalty: ~200 cycles

### Boot Sequence
- ✅ Hub-and-spoke topology: kmain() degree 34
- ✅ 5-phase initialization: 85-100ms total
- ✅ NO infinite loop in kmain()
- ✅ Directed Acyclic Graph (DAG) structure

---

## Build Targets

```bash
make all            # Build all PDFs
make cpu-pdfs       # CPU analysis diagrams + paper
make boot-pdfs      # Boot sequence papers
make wiki           # Build documentation
make test           # Run all tests
make arxiv-cpu      # Create ArXiv package (CPU)
make arxiv-boot     # Create ArXiv package (Boot)
make clean          # Remove build artifacts
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE)

**MINIX** is a trademark of Vrije Universiteit Amsterdam.

---

## References

1. **MINIX Project**: [minix3.org](https://www.minix3.org/)
2. **MINIX Source**: [GitHub](https://github.com/Stichting-MINIX-Research-Foundation/minix)
3. **Tanenbaum & Woodhull**: *Operating Systems: Design and Implementation*

---

*Understanding operating systems, one syscall at a time.*
EOF
```

---

## Post-Migration Verification

After completing all phases, verify:

### 1. Directory Structure

```bash
tree -L 2 -d
```

**Expected**: Umbrella structure matches UMBRELLA-ARCHITECTURE.md

### 2. LaTeX Compilation

```bash
# CPU diagrams
make cpu-pdfs
ls modules/cpu-interface/latex/figures/*.pdf

# Boot papers
make boot-pdfs
ls modules/boot-sequence/latex/*.pdf
```

**Expected**: All PDFs generated without errors

### 3. Shared Styles

```bash
grep -r "minix-styles" modules/*/latex/*.tex
```

**Expected**: All module LaTeX files use shared styles

### 4. MCP Server

```bash
cd mcp/servers/minix-analysis
python -c "from modules.cpu_interface.mcp.cpu_data_loader import CPUDataLoader; print('CPU: OK')"
python -c "from modules.boot_sequence.mcp.boot_data_loader import BootDataLoader; print('Boot: OK')"
```

**Expected**: Both imports succeed

### 5. Wiki Build

```bash
make wiki
ls -lh wiki/site/index.html
```

**Expected**: Static site generated successfully

---

## Rollback Plan

If migration fails, restore from backup:

```bash
cd /home/eirikr/Playground
rm -rf minix-analysis
tar xzf minix-cpu-analysis-backup-YYYYMMDD.tar.gz
mv minix-cpu-analysis minix-analysis
```

---

## Timeline Summary

| Phase | Task | Duration | Cumulative |
|-------|------|----------|------------|
| 1 | Rename and create structure | 15 min | 15 min |
| 2 | Extract shared styles | 20 min | 35 min |
| 3 | Migrate CPU module | 30 min | 1h 5min |
| 4 | Migrate Boot module | 45 min | 1h 50min |
| 5 | Consolidate MCP server | 30 min | 2h 20min |
| 6 | Create build system | 20 min | 2h 40min |
| 7 | Documentation and testing | 30 min | 3h 10min |

**Total**: ~3-4 hours (including testing and verification)

---

*Next: Execute migration phases sequentially*
