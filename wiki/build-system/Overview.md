# Build System Overview

**MINIX Analysis Unified Build Infrastructure**

---

## Introduction

The MINIX Analysis project uses a unified GNU Make build system with three-tier architecture: Root Makefile for orchestration, module-specific Makefiles for individual papers, and shared style infrastructure for consistent typography and diagrams.

---

## Architecture

### Three-Tier Build System

```
Root Makefile (Tier 1)
    ↓
Module Makefiles (Tier 2)
    ↓
Shared Styles (Tier 3)
```

**Tier 1**: Root coordination (`/minix-analysis/Makefile`)
- Orchestrates multi-module builds
- System-wide style installation
- Global testing and cleanup
- ArXiv package generation

**Tier 2**: Module-specific builds
- `modules/cpu-interface/Makefile`
- `modules/boot-sequence/Makefile`
- Independent compilation
- Module-specific targets

**Tier 3**: Shared infrastructure
- `shared/styles/*.sty` (LaTeX style files)
- `shared/pipeline/` (Analysis automation)
- `shared/tests/` (Common test utilities)

---

## Root Makefile

### Location
`/home/eirikr/Playground/minix-analysis/Makefile`

### Core Targets

**Build Targets**:
```bash
make cpu              # Build CPU Interface Analysis paper
make boot             # Build Boot Sequence Analysis paper
make all              # Build all papers
```

**Package Targets**:
```bash
make arxiv-cpu        # Create ArXiv submission package for CPU paper
make arxiv-boot       # Create ArXiv submission package for Boot paper
```

**Maintenance Targets**:
```bash
make clean            # Remove all build artifacts
make test             # Run all tests (LaTeX + Python)
make install          # Install shared styles system-wide
```

**Utility Targets**:
```bash
make help             # Show available targets
make status           # Show build status of all modules
```

### Installation

**System-wide style installation**:
```bash
sudo make install
```

**What gets installed**:
```
/usr/share/texmf/tex/latex/minix/
├── minix-colors.sty         # Base color palette
├── minix-colors-cvd.sty     # Colorblind-safe variants
├── minix-arxiv.sty          # ArXiv compliance + Spline Sans
└── minix-styles.sty         # TikZ/PGFPlots styles
```

**Post-install**:
```bash
sudo texhash            # Update TeX package database
kpsewhich minix-colors.sty   # Verify installation
```

---

## CPU Interface Module

### Location
`/home/eirikr/Playground/minix-analysis/modules/cpu-interface/Makefile`

### Build Targets

**Full Build**:
```bash
make all              # Complete build (figures + plots + paper)
```

**Component Builds**:
```bash
make figures          # Build TikZ diagrams (11 PDFs)
make plots            # Build PGFPlots performance charts
make paper            # Build main paper PDF only
```

**Quick Iteration**:
```bash
make quick            # Single-pass build (no reruns)
```

**Testing**:
```bash
make test             # Verify LaTeX compilation
make check            # Run all quality checks
```

**Maintenance**:
```bash
make clean            # Remove build artifacts
make arxiv            # Create ArXiv submission package
```

### Build Process

**Standard Build** (`make all`):
1. Compile standalone diagrams (`.tex` → `.pdf`)
2. Generate performance plots (PGFPlots)
3. Build main paper (LuaLaTeX, 3 passes)
4. Verify all references resolved

**Quick Build** (`make quick`):
1. Skip figure regeneration
2. Single LuaLaTeX pass
3. ~30 seconds vs ~3 minutes for full build

### LaTeX Engine

**Required**: LuaLaTeX (for Spline Sans fonts)

**Compilation Command**:
```bash
TEXINPUTS=.:../../shared/styles//: lualatex \
    -interaction=nonstopmode \
    -halt-on-error \
    paper.tex
```

**Environment Variables**:
- `TEXINPUTS`: LaTeX search path for shared styles
- `-interaction=nonstopmode`: Batch mode (no user prompts)
- `-halt-on-error`: Fail fast on compilation errors

---

## Boot Sequence Module

### Location
`/home/eirikr/Playground/minix-analysis/modules/boot-sequence/Makefile`

### Build Targets

**Full Build**:
```bash
make all              # Complete build (visualizations + paper)
```

**Component Builds**:
```bash
make visualizations   # Generate Python call graph diagrams
make paper            # Build main paper PDF only
```

**Quick Iteration**:
```bash
make quick            # Single-pass build
```

**Testing**:
```bash
make test             # Verify compilation
make validate         # Check call graph data integrity
```

**Maintenance**:
```bash
make clean            # Remove build artifacts
make arxiv            # Create ArXiv submission package
```

### Visualization Pipeline

**Python Tools**:
```bash
cd visualizations/
python generate_topology.py     # Create hub-and-spoke diagram
python generate_callgraph.py    # Create depth hierarchy
python generate_phases.py       # Create phase partitioning
```

**Output**:
- `topology.pdf` - Hub-and-spoke layout
- `callgraph-depth.pdf` - Layered tree
- `phases.pdf` - Color-coded by phase

**Dependencies**:
- Python 3.10+
- NetworkX (graph construction)
- Matplotlib (diagram rendering)

---

## ArXiv Submission Packages

### Structure

**CPU Interface Package**:
```
arxiv-cpu-interface-YYYY-MM-DD/
├── paper.tex                    # Main paper
├── paper.bbl                    # Compiled bibliography
├── minix-colors.sty             # Bundled styles
├── minix-colors-cvd.sty
├── minix-arxiv.sty
├── minix-styles.sty
├── figures/                     # All diagrams
│   ├── 05-syscall-int-flow.pdf
│   ├── 06-syscall-sysenter-flow.pdf
│   └── ... (11 total)
└── README-arxiv.txt             # Submission notes
```

**Boot Sequence Package**:
```
arxiv-boot-sequence-YYYY-MM-DD/
├── paper.tex
├── paper.bbl
├── minix-*.sty                  # Bundled styles (4 files)
├── visualizations/              # Call graph diagrams
│   ├── topology.pdf
│   ├── callgraph-depth.pdf
│   └── phases.pdf
└── README-arxiv.txt
```

### Generation

**Automated**:
```bash
make arxiv-cpu                   # CPU package
make arxiv-boot                  # Boot package
```

**Manual** (from root):
```bash
./scripts/create-arxiv-package.sh cpu-interface
./scripts/create-arxiv-package.sh boot-sequence
```

**Output Location**: `arxiv-packages/`

### Verification

**Check package contents**:
```bash
cd arxiv-cpu-interface-2025-10-30/
lualatex paper.tex               # Must compile standalone
```

**ArXiv Compliance**:
- ✅ All figures included (no external dependencies)
- ✅ Bibliography compiled (.bbl, not .bib)
- ✅ Styles bundled (no system package dependencies)
- ✅ Hyperref configured (colorlinks=true)

---

## Build Configuration

### TEXINPUTS Search Path

**Purpose**: Allow LaTeX to find shared styles from module directories

**Method 1** (Makefile):
```makefile
TEXINPUTS=.:../../shared/styles//: lualatex paper.tex
```

**Method 2** (LaTeX source):
```latex
\makeatletter
\def\input@path{{../../shared/styles/}}
\makeatother
```

**Method 3** (Environment):
```bash
export TEXINPUTS=../../shared/styles//:
make paper
```

### Compiler Flags

**LuaLaTeX**:
```bash
lualatex \
    -interaction=nonstopmode \    # No user prompts
    -halt-on-error \              # Fail immediately on error
    -output-directory=build \     # Place aux files in build/
    paper.tex
```

**Python**:
```bash
python -B generate_topology.py   # -B: Don't write .pyc files
```

---

## Testing

### LaTeX Compilation Tests

**Quick Test**:
```bash
make test                        # From root
cd modules/cpu-interface && make test
cd modules/boot-sequence && make test
```

**What's Tested**:
1. All `.tex` files compile without errors
2. All figures exist and are included
3. Bibliography resolves correctly
4. Cross-references valid

### Python Tests

**Visualization Tests**:
```bash
cd modules/boot-sequence/visualizations/
pytest test_topology.py -v
```

**What's Tested**:
1. Call graph data integrity
2. NetworkX graph construction
3. Matplotlib rendering (no exceptions)

---

## Performance

### Build Times

**CPU Interface Module**:
- Full build: ~3 minutes (11 diagrams + 3 LaTeX passes)
- Quick build: ~30 seconds (single pass)
- Figures only: ~1 minute (parallel compilation)

**Boot Sequence Module**:
- Full build: ~2 minutes (3 visualizations + 3 LaTeX passes)
- Quick build: ~25 seconds (single pass)
- Visualizations only: ~45 seconds

### Optimization Tips

**Parallel Builds**:
```bash
make -j4 figures                 # Use 4 cores for figure compilation
```

**Incremental Builds**:
```bash
make quick                       # Skip unchanged components
```

**Watch Mode** (requires inotify-tools):
```bash
make watch-cpu                   # Auto-rebuild on file changes
```

---

## Troubleshooting

### Error: "File `minix-colors.sty' not found"

**Cause**: TEXINPUTS not configured or styles not installed

**Solution 1** (Makefile already configures this):
```bash
cd modules/cpu-interface && make all
```

**Solution 2** (Manual build):
```bash
TEXINPUTS=.:../../shared/styles//: lualatex paper.tex
```

**Solution 3** (System install):
```bash
cd /home/eirikr/Playground/minix-analysis
sudo make install
```

### Error: "I can't find file `Spline Sans'"

**Cause**: Fonts not installed

**Solution**:
```bash
wget "https://fonts.google.com/download?family=Spline%20Sans"
unzip SplineSans.zip -d ~/.fonts/SplineSans/
fc-cache -fv
```

### Error: "Undefined control sequence \cvdsetup"

**Cause**: minix-colors-cvd.sty not loaded

**Solution**:
```latex
\usepackage{minix-colors-cvd}   % Add before using CVD commands
```

### Warning: "Label(s) may have changed. Rerun to get cross-references right."

**Cause**: Multiple LaTeX passes needed

**Solution**: Run `make all` instead of `make quick` (or manually run lualatex 3 times)

---

## Related Documentation

- [Style Guide](../style-guide/Overview.md)
- [Installation Guide](../../INSTALLATION.md)
- [Integration Report](../../INTEGRATION-COMPLETE.md)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Build System**: GNU Make 4.0+
**LaTeX Engine**: LuaLaTeX (TeX Live 2023+)
