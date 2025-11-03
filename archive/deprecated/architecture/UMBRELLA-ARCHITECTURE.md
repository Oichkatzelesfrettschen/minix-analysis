# MINIX Analysis - Umbrella Project Architecture

**Version**: 1.0.0
**Date**: 2025-10-30
**Status**: Design Phase

---

## Executive Summary

This document defines the architecture for transforming two separate MINIX analysis projects into a **unified umbrella structure** with shared infrastructure and paper-specific modules.

**Goals**:
- ✅ Maximize code and infrastructure reuse
- ✅ Support independent ArXiv paper submissions
- ✅ Enable parallel development of multiple analyses
- ✅ Maintain reproducible builds
- ✅ Harmonize visual styles across all papers

---

## Current State

### Project 1: minix-cpu-analysis
**Location**: `/home/eirikr/Playground/minix-cpu-analysis`

**Content**:
- CPU interface analysis (i386 arch, 3 syscalls, memory, TLB)
- 11 TikZ/PGFPlots diagrams (figures/05-11)
- Unified style package: `latex/minix-styles.sty`
- MCP server with 7 tools (5 CPU + 2 Boot)
- Phase 1-3 complete, Phase 4 (wiki) in progress

**Key Files**:
```
minix-cpu-analysis/
├── latex/
│   ├── minix-styles.sty              # Unified TikZ/PGFPlots package
│   ├── TIKZ-STYLE-GUIDE.md           # Style documentation
│   ├── figures/                       # CPU diagrams (05-11)
│   └── minix-complete-analysis.tex   # Master LaTeX doc (CPU + Boot)
├── mcp/servers/minix-analysis/        # MCP server (7 tools, 5 resources)
├── pipeline/                          # Python analysis tools
├── MINIX-ARCHITECTURE-SUMMARY.md      # CPU analysis synthesis
└── COMPLETE-PROJECT-SYNTHESIS.md      # CPU + Boot integration
```

### Project 2: minix-boot-analyzer
**Location**: `/home/eirikr/Playground/minix-boot-analyzer`

**Content**:
- Boot sequence analysis (hub-and-spoke topology, 5 phases)
- ArXiv-ready whitepaper: `minix_boot_whitepaper_arxiv.tex` (570 KB PDF)
- Comprehensive LaTeX visualizations with custom color palette
- Shell scripts for automated analysis
- Multiple synthesis documents

**Key Files**:
```
minix-boot-analyzer/
├── visualizations/
│   ├── minix_boot_whitepaper_arxiv.tex   # ArXiv paper (570 KB PDF)
│   ├── minix_boot_ULTRA_DENSE.tex        # Dense analysis (308 KB PDF)
│   ├── minix_boot_comprehensive.tex      # Comprehensive (154 KB PDF)
│   ├── interactive_boot_viz.html         # Interactive visualization
│   └── *.tex fragments                   # Reusable components
├── *.sh scripts                           # Automated analysis tools
├── ARXIV_WHITEPAPER_COMPLETE.md           # Whitepaper design doc
├── ULTIMATE_SYNTHESIS_COMPLETE.md         # Boot analysis synthesis
└── FINAL_SYNTHESIS_REPORT.md              # Integration report
```

---

## Target Architecture: 3-Tier Structure

### Tier 1: Umbrella Project Root

**Name**: `minix-analysis` (rename from `minix-cpu-analysis`)
**Location**: `/home/eirikr/Playground/minix-analysis`

```
minix-analysis/                        # UMBRELLA ROOT
├── README.md                           # Overview of all analyses
├── ARCHITECTURE.md                     # This document
├── INSTALLATION.md                     # Complete installation guide
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # MIT License
├── Makefile                            # Unified build system
├── requirements.txt                    # Python dependencies (umbrella)
├── .gitignore                          # Unified gitignore
├── .github/workflows/                  # CI/CD for all modules
│   ├── test-cpu-analysis.yml
│   ├── test-boot-analysis.yml
│   └── deploy-wiki.yml
│
├── shared/                             # TIER 3: SHARED INFRASTRUCTURE
│   ├── styles/                         # Shared LaTeX styles
│   │   ├── minix-styles.sty            # Master TikZ/PGFPlots package
│   │   ├── minix-colors.sty            # Color definitions
│   │   ├── minix-arxiv.sty             # ArXiv-compliant formatting
│   │   └── STYLE-GUIDE.md              # Visual style documentation
│   ├── mcp/                            # Shared MCP infrastructure
│   │   ├── server/                     # Unified MCP server
│   │   │   ├── __init__.py
│   │   │   ├── base_server.py          # Base MCP server class
│   │   │   ├── data_loader_base.py     # Base data loader
│   │   │   └── tools_registry.py       # Tool registration system
│   │   └── README.md                   # MCP architecture docs
│   ├── pipeline/                       # Shared analysis tools
│   │   ├── symbol_extraction/          # ctags-based extraction
│   │   ├── call_graph/                 # graphviz generation
│   │   └── common_utils.py             # Shared Python utilities
│   ├── docs-templates/                 # MkDocs templates
│   │   ├── mkdocs-base.yml             # Base MkDocs config
│   │   ├── extra.css                   # Shared CSS
│   │   └── extra.js                    # Shared JavaScript
│   └── tests/                          # Shared test infrastructure
│       ├── test_mcp.py
│       └── test_styles.py
│
├── modules/                            # TIER 2: ANALYSIS MODULES
│   ├── cpu-interface/                  # Module 1: CPU Interface Analysis
│   │   ├── README.md                   # CPU analysis overview
│   │   ├── requirements.txt            # Module-specific dependencies
│   │   ├── latex/                      # CPU-specific LaTeX
│   │   │   ├── minix-cpu-analysis.tex  # Paper main file
│   │   │   └── figures/                # CPU diagrams (05-11)
│   │   ├── mcp/                        # CPU-specific MCP tools
│   │   │   ├── cpu_data_loader.py
│   │   │   └── cpu_tools.py
│   │   ├── pipeline/                   # CPU-specific scripts
│   │   ├── docs/                       # CPU-specific wiki content
│   │   └── tests/
│   │
│   ├── boot-sequence/                  # Module 2: Boot Sequence Analysis
│   │   ├── README.md                   # Boot analysis overview
│   │   ├── requirements.txt            # Module-specific dependencies
│   │   ├── latex/                      # Boot-specific LaTeX
│   │   │   ├── minix-boot-arxiv.tex    # ArXiv paper
│   │   │   ├── minix-boot-dense.tex    # Dense analysis
│   │   │   └── figures/                # Boot diagrams
│   │   ├── mcp/                        # Boot-specific MCP tools
│   │   │   ├── boot_data_loader.py
│   │   │   └── boot_tools.py
│   │   ├── shell-scripts/              # Automated analysis (.sh)
│   │   ├── docs/                       # Boot-specific wiki content
│   │   └── tests/
│   │
│   └── template/                       # Module 3+: Template for future
│       ├── README.template.md
│       ├── latex/
│       ├── mcp/
│       ├── docs/
│       └── tests/
│
├── wiki/                               # PHASE 4: Unified Documentation Portal
│   ├── mkdocs.yml                      # MkDocs configuration (extends shared/docs-templates)
│   ├── docs/                           # Combined wiki content
│   │   ├── index.md                    # Landing page
│   │   ├── cpu-interface/              # CPU analysis pages
│   │   ├── boot-sequence/              # Boot analysis pages
│   │   ├── shared/                     # Cross-cutting docs
│   │   └── reference/                  # Glossary, references
│   └── site/                           # Built static site (generated)
│
└── arxiv-submissions/                  # ArXiv Submission Packages
    ├── cpu-interface-YYYY-MM/          # Dated submission packages
    │   ├── minix-cpu-analysis.tex
    │   ├── minix-cpu-analysis.bbl
    │   ├── minix-styles.sty
    │   └── figures/
    └── boot-sequence-YYYY-MM/
        ├── minix-boot-arxiv.tex
        ├── minix-boot-arxiv.bbl
        ├── minix-styles.sty
        └── figures/
```

---

## Component Responsibilities

### Tier 1: Umbrella Root

**Purpose**: Project-wide coordination, documentation, and build orchestration

**Key Files**:
- `README.md`: Overview of all MINIX analyses, quick navigation
- `INSTALLATION.md`: Complete setup guide (Python venv, LaTeX, MCP, MkDocs)
- `Makefile`: Unified build targets (`make cpu`, `make boot`, `make all-pdfs`, `make wiki`)
- `.github/workflows/`: CI/CD for testing, building, deploying

**Responsibilities**:
- Coordinate multi-module builds
- Manage global dependencies
- Provide unified documentation entry point
- Handle GitHub Pages deployment

### Tier 2: Analysis Modules

**Purpose**: Paper-specific analysis, diagrams, and MCP tools

#### Module Structure (Common Pattern)
```
modules/<module-name>/
├── README.md                    # Module overview, research questions
├── requirements.txt             # Module-specific Python packages
├── latex/                       # LaTeX source for paper
│   ├── <module>-arxiv.tex       # ArXiv submission version
│   ├── <module>-extended.tex    # Extended version with appendices
│   └── figures/                 # TikZ diagrams, PGFPlots charts
├── mcp/                         # MCP data loaders and tools
│   ├── <module>_data_loader.py  # Extends BaseDataLoader
│   └── <module>_tools.py        # Module-specific MCP tools
├── pipeline/                    # Analysis scripts (Python, Bash)
├── docs/                        # MkDocs wiki content
│   ├── index.md
│   ├── overview.md
│   └── ...
└── tests/                       # Module-specific tests
    ├── test_data_loader.py
    └── test_tools.py
```

#### Module Independence
- Modules CAN import from `shared/`
- Modules CANNOT import from other modules
- Each module maintains its own `requirements.txt`
- Each module produces standalone ArXiv submission package

### Tier 3: Shared Infrastructure

**Purpose**: Reusable components across all modules

#### shared/styles/
**Unified LaTeX Style System**

Files:
- `minix-styles.sty`: Master package (imports colors, arxiv, defines node styles)
- `minix-colors.sty`: Color palette definitions
- `minix-arxiv.sty`: ArXiv-compliant formatting (hyperref, margins, fonts)
- `STYLE-GUIDE.md`: Documentation for style usage

Usage in Modules:
```latex
\documentclass[11pt,a4paper]{article}
\usepackage{minix-styles}  % All-in-one import

\begin{document}
\begin{tikzpicture}[cpu flow]  % Use predefined preset
    \node[box] {User: Setup registers};
    \node[hw] {CPU: Hardware action};
\end{tikzpicture}
\end{document}
```

#### shared/mcp/
**Unified MCP Server Architecture**

**Design**: Single MCP server process, modular tool registration

```python
# shared/mcp/server/base_server.py
from mcp.server import Server

class MINIXAnalysisServer(Server):
    def __init__(self, name="minix-analysis"):
        super().__init__(name)
        self.modules = {}  # Registered modules

    def register_module(self, module_name, data_loader, tools):
        self.modules[module_name] = {
            "loader": data_loader,
            "tools": tools
        }

    # Auto-generate list_tools() from all registered modules
    # Auto-generate list_resources() from all registered modules
```

```python
# modules/cpu-interface/mcp/cpu_data_loader.py
from shared.mcp.server.data_loader_base import BaseDataLoader

class CPUDataLoader(BaseDataLoader):
    def load_architecture_data(self):
        # CPU-specific implementation
        pass

# modules/cpu-interface/mcp/cpu_tools.py
def register_cpu_tools(server):
    server.register_tool("query_architecture", query_architecture_handler)
    server.register_tool("analyze_syscall", analyze_syscall_handler)
    # ...
```

**MCP Server Startup**:
```python
# mcp/servers/minix-analysis/__main__.py
from shared.mcp.server.base_server import MINIXAnalysisServer
from modules.cpu_interface.mcp.cpu_tools import register_cpu_tools
from modules.boot_sequence.mcp.boot_tools import register_boot_tools

server = MINIXAnalysisServer()
register_cpu_tools(server)
register_boot_tools(server)
server.run()
```

**Result**: Single MCP process, 7+ tools (dynamically registered from modules)

#### shared/pipeline/
**Reusable Analysis Tools**

- `symbol_extraction/`: ctags-based symbol extraction (Python)
- `call_graph/`: graphviz call graph generation (Python)
- `common_utils.py`: Shared utilities (file I/O, MINIX source navigation)

Usage in Modules:
```python
from shared.pipeline.symbol_extraction import extract_symbols
from shared.pipeline.call_graph import generate_call_graph

symbols = extract_symbols("/path/to/minix/source")
graph = generate_call_graph(symbols, focus="kmain")
```

#### shared/docs-templates/
**MkDocs Base Configuration**

`mkdocs-base.yml`:
```yaml
theme:
  name: material
  palette: [...]  # Shared color scheme
  features: [...]  # Shared features

plugins:
  - search
  - git-revision-date-localized

markdown_extensions:
  - pymdownx.superfences
  - pymdownx.tabbed
  # ... shared extensions

extra_css:
  - stylesheets/extra.css  # From shared/docs-templates

extra_javascript:
  - javascripts/extra.js   # From shared/docs-templates
```

Module-specific `mkdocs.yml` extends base:
```yaml
INHERIT: ../shared/docs-templates/mkdocs-base.yml

site_name: MINIX CPU Interface Analysis
nav:
  - Home: index.md
  - CPU-specific pages...
```

---

## Migration Strategy

### Phase 1: Rename and Restructure
1. Rename `minix-cpu-analysis` → `minix-analysis`
2. Create `shared/`, `modules/`, `wiki/`, `arxiv-submissions/` directories
3. Move existing content to `modules/cpu-interface/`

### Phase 2: Extract Shared Components
1. Move `latex/minix-styles.sty` → `shared/styles/minix-styles.sty`
2. Refactor MCP server into `shared/mcp/` (base classes)
3. Move CPU-specific MCP code to `modules/cpu-interface/mcp/`
4. Extract common pipeline tools to `shared/pipeline/`

### Phase 3: Migrate Boot Analyzer
1. Copy `/home/eirikr/Playground/minix-boot-analyzer` → `modules/boot-sequence/`
2. Update `minix_boot_whitepaper_arxiv.tex` to use `shared/styles/minix-styles.sty`
3. Harmonize color palette (define boot phase colors in minix-colors.sty)
4. Create `modules/boot-sequence/mcp/boot_data_loader.py` and `boot_tools.py`
5. Integrate boot tools into unified MCP server

### Phase 4: Harmonize and Test
1. Compile all LaTeX documents with shared styles
2. Test unified MCP server with all modules
3. Build unified wiki with content from both modules
4. Create ArXiv submission packages for both papers

### Phase 5: Documentation and CI
1. Write comprehensive `INSTALLATION.md`
2. Create `Makefile` with targets for all modules
3. Set up GitHub Actions workflows
4. Document module creation template

---

## Build System Design

### Makefile Targets

```makefile
# Top-level Makefile

.PHONY: all clean test wiki arxiv

# Build all PDFs
all: cpu-pdfs boot-pdfs

# Module-specific builds
cpu-pdfs:
	$(MAKE) -C modules/cpu-interface latex

boot-pdfs:
	$(MAKE) -C modules/boot-sequence latex

# MCP server
mcp-server:
	cd mcp/servers/minix-analysis && python -m src.server

# Wiki
wiki:
	cd wiki && mkdocs build

wiki-serve:
	cd wiki && mkdocs serve

# ArXiv packages
arxiv-cpu:
	./scripts/create-arxiv-package.sh cpu-interface

arxiv-boot:
	./scripts/create-arxiv-package.sh boot-sequence

# Testing
test:
	pytest shared/tests/
	pytest modules/cpu-interface/tests/
	pytest modules/boot-sequence/tests/

# Cleanup
clean:
	find . -name "*.aux" -delete
	find . -name "*.log" -delete
	find . -name "*.out" -delete
	rm -rf wiki/site/
```

### Module-Specific Makefiles

```makefile
# modules/cpu-interface/Makefile

LATEX = pdflatex
FIGURES = $(wildcard latex/figures/*.tex)
PDFS = $(FIGURES:.tex=.pdf)

.PHONY: all latex clean

all: latex

latex: $(PDFS)

%.pdf: %.tex
	cd $(dir $<) && $(LATEX) $(notdir $<)

clean:
	rm -f latex/figures/*.aux latex/figures/*.log latex/figures/*.pdf
```

---

## Dependency Management

### Python Virtual Environment (Umbrella)

`requirements.txt` (root):
```
# MCP and server infrastructure
mcp>=1.0.0
asyncio-mqtt>=0.16.0

# Analysis tools
ctags-python>=0.1.0
pygraphviz>=1.11

# Documentation
mkdocs-material>=9.5.0
pymdown-extensions>=10.7.0
mkdocs-git-revision-date-localized-plugin>=1.2.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
```

Module-specific `requirements.txt` can add dependencies:
```
# modules/cpu-interface/requirements.txt
# Additional dependencies for CPU analysis module
numpy>=1.26.0
matplotlib>=3.8.0
```

### LaTeX Dependencies (Shared)

All modules use shared styles, so LaTeX dependencies are centralized:

`shared/styles/minix-styles.sty` requires:
- tikz
- pgfplots (compat=1.18)
- xcolor
- lmodern
- hyperref

Modules only need to `\usepackage{minix-styles}`.

---

## ArXiv Submission Workflow

### Preparation Script

`scripts/create-arxiv-package.sh`:
```bash
#!/bin/bash
# Create ArXiv submission package for a module

MODULE=$1
DATE=$(date +%Y-%m)
PACKAGE_DIR="arxiv-submissions/${MODULE}-${DATE}"

mkdir -p "$PACKAGE_DIR"

# Copy main .tex file
cp "modules/${MODULE}/latex/${MODULE}-arxiv.tex" "$PACKAGE_DIR/"

# Generate .bbl from .bib
cd "modules/${MODULE}/latex"
pdflatex "${MODULE}-arxiv.tex"
bibtex "${MODULE}-arxiv"
pdflatex "${MODULE}-arxiv.tex"  # Regenerate with citations
cp "${MODULE}-arxiv.bbl" "${PACKAGE_DIR}/"

# Copy shared style
cp "shared/styles/minix-styles.sty" "$PACKAGE_DIR/"
cp "shared/styles/minix-colors.sty" "$PACKAGE_DIR/"
cp "shared/styles/minix-arxiv.sty" "$PACKAGE_DIR/"

# Copy figures
cp -r "modules/${MODULE}/latex/figures" "$PACKAGE_DIR/"

# Create tarball for ArXiv
cd "$PACKAGE_DIR"
tar czf "../${MODULE}-${DATE}.tar.gz" *

echo "ArXiv package created: arxiv-submissions/${MODULE}-${DATE}.tar.gz"
```

### ArXiv Submission Checklist

For each module:
- [ ] Main .tex file compiles with pdflatex (TeX Live 2023)
- [ ] .bbl file included (NOT .bib)
- [ ] All .sty files included
- [ ] Figures are PDF format (not .eps)
- [ ] No spaces in filenames
- [ ] hyperref loaded with colorlinks=true
- [ ] All paths relative (no absolute paths)
- [ ] Package size < 50 MB
- [ ] Test compilation: `pdflatex main.tex` (2-3 runs)

---

## Testing Strategy

### Shared Infrastructure Tests

`shared/tests/test_styles.py`:
```python
def test_minix_styles_compiles():
    """Test that minix-styles.sty compiles without errors."""
    tex_source = r"""
    \documentclass{article}
    \usepackage{minix-styles}
    \begin{document}
    \begin{tikzpicture}[cpu flow]
        \node[box] {Test};
    \end{tikzpicture}
    \end{document}
    """
    # Compile and check for errors
    assert compile_latex(tex_source) == 0
```

### Module Tests

`modules/cpu-interface/tests/test_data_loader.py`:
```python
from modules.cpu_interface.mcp.cpu_data_loader import CPUDataLoader

def test_architecture_data_loads():
    loader = CPUDataLoader()
    data = loader.load_architecture_data()

    assert "registers" in data
    assert "paging" in data
    assert "tlb" in data
```

### Integration Tests

`shared/tests/test_mcp_integration.py`:
```python
def test_all_modules_registered():
    """Test that MCP server has tools from all modules."""
    from mcp.servers.minix_analysis import server

    tools = server.list_tools()
    tool_names = [t.name for t in tools]

    # CPU tools
    assert "query_architecture" in tool_names
    assert "analyze_syscall" in tool_names

    # Boot tools
    assert "query_boot_sequence" in tool_names
    assert "trace_boot_path" in tool_names
```

---

## Visual Harmonization Plan

### Color Palette Unification

**Current State**:
- CPU diagrams: Simple blue/red palette (blue!10, red!20)
- Boot diagrams: Custom phase colors (phase1-5 in RGB)

**Target State**: Unified minix-colors.sty

`shared/styles/minix-colors.sty`:
```latex
% Primary palette (from minix-styles.sty)
\definecolor{primaryblue}{RGB}{0,102,204}
\definecolor{secondarygreen}{RGB}{46,204,113}
\definecolor{accentorange}{RGB}{255,127,0}
\definecolor{warningred}{RGB}{231,76,60}

% Boot phase colors (harmonized with primary palette)
\definecolor{phase1}{RGB}{52,152,219}    % Blue (cstart - early init)
\definecolor{phase2}{RGB}{46,204,113}    % Green (proc_init - success)
\definecolor{phase3}{RGB}{155,89,182}    % Purple (memory_init - critical)
\definecolor{phase4}{RGB}{230,126,34}    % Orange (system_init - warning)
\definecolor{phase5}{RGB}{231,76,60}     % Red (usermode - critical transition)

% Semantic aliases
\colorlet{critical}{warningred}
\colorlet{flowbox}{primaryblue!15}
\colorlet{hardware}{warningred!20}
\colorlet{kernel}{secondarygreen!15}
```

### Node Style Consolidation

All modules will use:
- `box`, `hw`, `kernelbox` (CPU flow diagrams)
- `process`, `phase`, `critical` (Boot topology)
- `func`, `extfunc` (Call graphs)

Migration:
1. Update `minix_boot_whitepaper_arxiv.tex` to use `\usepackage{minix-styles}`
2. Replace inline color definitions with `minix-colors.sty` references
3. Replace inline node styles with standard styles from `minix-styles.sty`
4. Test compilation with shared styles

---

## Future Expansion Template

### Adding a New Module

1. **Create module directory**:
```bash
cp -r modules/template modules/new-analysis
cd modules/new-analysis
```

2. **Update README.md**:
- Research questions
- Methodology
- Key findings

3. **Create LaTeX paper**:
```latex
\documentclass[11pt,a4paper]{article}
\usepackage{minix-styles}  % Unified styles

\title{MINIX New Analysis}
\author{...}

\begin{document}
% Your analysis
\end{document}
```

4. **Create MCP data loader**:
```python
from shared.mcp.server.data_loader_base import BaseDataLoader

class NewDataLoader(BaseDataLoader):
    def load_new_data(self):
        # Your data loading logic
        pass
```

5. **Register MCP tools**:
```python
# modules/new-analysis/mcp/new_tools.py
def register_new_tools(server):
    server.register_tool("query_new_thing", handler)
```

6. **Add to unified MCP server**:
```python
# mcp/servers/minix-analysis/__main__.py
from modules.new_analysis.mcp.new_tools import register_new_tools

register_new_tools(server)
```

7. **Create wiki content**:
```
modules/new-analysis/docs/
├── index.md
├── overview.md
└── ...
```

8. **Add to umbrella wiki nav**:
```yaml
# wiki/mkdocs.yml
nav:
  - ...
  - New Analysis:
      - modules/new-analysis/docs/index.md
      - ...
```

9. **Test and integrate**:
```bash
make test
make wiki
make arxiv-new-analysis
```

---

## Success Metrics

Umbrella project is successful when:

- ✅ Both CPU and Boot modules compile independently
- ✅ Both papers use shared `minix-styles.sty`
- ✅ Unified MCP server provides all tools (7+)
- ✅ Wiki integrates content from both modules
- ✅ ArXiv packages can be created for both papers
- ✅ New modules can be added using template
- ✅ CI/CD passes for all modules
- ✅ Documentation is comprehensive and accurate

---

## References

1. **ArXiv Submission Guidelines**: https://info.arxiv.org/help/submit/index.html
2. **LaTeX for ArXiv**: https://info.arxiv.org/help/submit_tex.html
3. **MCP Protocol**: https://modelcontextprotocol.io/
4. **MkDocs Material**: https://squidfunk.github.io/mkdocs-material/

---

*Next: [Migration Plan](MIGRATION-PLAN.md) →*
