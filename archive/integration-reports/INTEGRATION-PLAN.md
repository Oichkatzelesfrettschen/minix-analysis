# MINIX CPU Analysis - Ultra-Integration Master Plan
**Version:** 1.0
**Date:** 2025-10-30
**Architect:** Claude Code + Multi-Agent Orchestration
**Status:** 🚀 Active Development

---

## Executive Summary

This plan integrates three major enhancements to the MINIX 3.4.0-RC6 analysis project:

- **Option A**: Enhanced publication-quality diagrams (call graphs, control flow, memory layout, performance plots)
- **Option B**: Python analysis tooling (DeepWiki-style: parsing, graphing, metrics, RAG/embeddings)
- **Option C**: MCP integration (DeepWiki MCP, filesystem MCP, custom analysis server)

**Design Principles:**
1. ✅ Harmonize with existing whitepaper structure
2. ✅ Arch/CachyOS native (PKGBUILD-first policy)
3. ✅ LaTeX-compatible outputs (TikZ/PGFPlots)
4. ✅ Reproducible builds (zero manual intervention)
5. ✅ Offline-capable (local analysis fallback)
6. ✅ Agent-driven automation

---

## Current State Inventory

### Existing Assets (Complete ✅)
```
minix-cpu-analysis/
├── Documentation (104 KB)
│   ├── MINIX-CPU-INTERFACE-ANALYSIS.md (39K) - 60+ CPU contact points
│   ├── ISA-LEVEL-ANALYSIS.md (21K) - INT/SYSENTER/SYSCALL specs
│   ├── MICROARCHITECTURE-DEEP-DIVE.md (44K) - µop breakdowns, TLB
│   ├── PROJECT-SUMMARY.md (13K)
│   └── README.md (14K)
├── Diagrams (690 KB)
│   ├── 01-system-call-flow.pdf (220K)
│   ├── 02-context-switch.pdf (253K)
│   └── 03-privilege-rings.pdf (217K)
└── Whitepaper (713 KB)
    └── MINIX-CPU-INTERFACE-WHITEPAPER.pdf (12 pages, ArXiv-ready)
```

### Gaps (To Be Implemented)
```
❌ Call graph visualizations (kernel function relationships)
❌ Control flow diagrams (INT/SYSENTER/SYSCALL execution paths)
❌ Memory layout diagrams (stack, heap, kernel segments)
❌ Performance plots (cycle counts, µop execution timing)
❌ Python analysis tools (parsers, metrics, graph generators)
❌ MCP server integration (DeepWiki, filesystem, custom)
❌ Automated documentation pipeline
❌ RAG/embeddings for Q&A
```

---

## Target Architecture

### Directory Structure (Post-Integration)
```
minix-cpu-analysis/
├── docs/
│   ├── wiki/                      # DeepWiki-style pages
│   │   ├── INDEX.md
│   │   ├── ARCHITECTURE.md
│   │   ├── SYSTEM-CALLS.md
│   │   ├── INTERRUPTS.md
│   │   └── MEMORY-MANAGEMENT.md
│   ├── MINIX-CPU-INTERFACE-ANALYSIS.md (existing)
│   ├── ISA-LEVEL-ANALYSIS.md (existing)
│   └── MICROARCHITECTURE-DEEP-DIVE.md (existing)
├── diagrams/
│   ├── 01-system-call-flow.{tex,pdf} (existing)
│   ├── 02-context-switch.{tex,pdf} (existing)
│   ├── 03-privilege-rings.{tex,pdf} (existing)
│   ├── 04-call-graph-kernel.{dot,tex,pdf}     # NEW
│   ├── 05-control-flow-int.{dot,tex,pdf}      # NEW
│   ├── 06-control-flow-sysenter.{dot,tex,pdf} # NEW
│   ├── 07-memory-layout.{tex,pdf}             # NEW
│   ├── 08-performance-cycles.{tex,pdf}        # NEW (PGFPlots)
│   └── 09-performance-uops.{tex,pdf}          # NEW (PGFPlots)
├── analysis/
│   ├── parsers/
│   │   ├── c_parser.py           # tree-sitter C parsing
│   │   ├── asm_parser.py         # NASM/GAS parsing
│   │   └── symbol_extractor.py  # ctags/global wrapper
│   ├── graphs/
│   │   ├── call_graph.py         # Function call relationships
│   │   ├── control_flow.py       # CFG extraction
│   │   └── data_flow.py          # DFG analysis (optional)
│   ├── metrics/
│   │   ├── complexity.py         # Cyclomatic complexity
│   │   ├── loc_counter.py        # Lines of code
│   │   └── dependency_depth.py   # Module coupling
│   ├── embeddings/
│   │   ├── code_embedder.py      # Generate embeddings
│   │   ├── vector_store.py       # SQLite-VSS/FAISS
│   │   └── rag_query.py          # Q&A over codebase
│   └── generators/
│       ├── dot_generator.py      # DOT graphs from analysis
│       ├── tikz_converter.py     # dot2tex wrapper
│       └── pgfplots_generator.py # Performance plots
├── mcp/
│   ├── servers/
│   │   ├── deepwiki_config.json  # DeepWiki MCP setup
│   │   ├── filesystem_config.json
│   │   └── analysis_server.py    # Custom MCP for analysis tools
│   └── clients/
│       └── claude_integration.sh # Setup script for Claude Code
├── build/
│   ├── Makefile.master          # Top-level orchestration
│   ├── Makefile.diagrams        # Diagram generation
│   ├── Makefile.analysis        # Python tool execution
│   └── Makefile.wiki            # Documentation generation
├── artifacts/
│   ├── graphs/                  # DOT files
│   ├── metrics/                 # CSV/JSON metrics
│   ├── embeddings/              # Vector DB
│   └── cache/                   # Build cache
├── latex/
│   ├── figures/                 # TikZ source
│   └── plots/                   # PGFPlots data
├── whitepaper/ (existing)
├── INTEGRATION-PLAN.md (this file)
└── PKGBUILD (optional: package entire stack)
```

---

## Technology Stack

### Core Tools (Arch Packages)
```bash
# Already installed or assumed
sudo pacman -S --needed \
  git ripgrep fd tree-sitter clang llvm \
  universal-ctags global graphviz plantuml \
  texlive-most biber python python-pip nodejs npm

# Additional for this project
sudo pacman -S --needed \
  python-tree-sitter python-pygraphviz \
  python-networkx python-matplotlib \
  python-numpy python-pandas dot2tex
```

### Python Ecosystem (PyPI)
```bash
python -m pip install --user \
  tree-sitter-c tree-sitter-cpp \
  pycparser lizard radon \
  faiss-cpu sentence-transformers \
  pygments jinja2 pyyaml
```

### Optional (Advanced Analysis)
```bash
# Joern (CPG analysis) - manual install
curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" | bash

# CodeQL - manual install (GitHub docs)
# Semgrep
paru -S semgrep-bin  # or pip install semgrep
```

---

## Phase Breakdown

### Phase 0: Planning and Validation ✅ (Current)
**Duration:** 1 hour
**Agent:** Plan (this document)

**Deliverables:**
- ✅ `INTEGRATION-PLAN.md` (this file)
- ✅ Directory structure designed
- ✅ Technology stack verified
- ⏳ Online claim verification (MCP endpoints, tool availability)

**Validation:**
```bash
# Verify Arch packages
pacman -Q tree-sitter graphviz dot2tex texlive-most

# Verify Python packages
python -c "import tree_sitter, networkx, matplotlib; print('OK')"

# Verify MINIX source
ls /home/eirikr/Playground/minix/minix/kernel/arch/i386/{mpx.S,klib.S,protect.c}
```

---

### Phase 1: Python Analysis Tooling
**Duration:** 4-6 hours
**Agents:** `polyglot-systems-architect`, `phd-software-engineer`

**Tasks:**
1. **Parser Development** (2 hours)
   - `c_parser.py`: Extract functions, calls, includes from C files
   - `asm_parser.py`: Extract labels, instructions, jumps from .S files
   - `symbol_extractor.py`: Wrap `ctags`/`global` for cross-references

2. **Graph Extraction** (2 hours)
   - `call_graph.py`: Build function call graph (who calls whom)
   - `control_flow.py`: Extract CFG for critical functions (INT entry, SYSENTER, SYSCALL)
   - Output: DOT format for Graphviz

3. **Metrics Collection** (1 hour)
   - `complexity.py`: Cyclomatic complexity via `lizard`
   - `loc_counter.py`: Lines of code per file/function
   - Output: CSV for analysis

4. **DOT → TikZ Pipeline** (1 hour)
   - `tikz_converter.py`: Wrapper for `dot2tex` with custom templates
   - Ensure LaTeX compatibility

**Deliverables:**
```
analysis/
├── parsers/
│   ├── __init__.py
│   ├── c_parser.py       # 150-200 lines
│   ├── asm_parser.py     # 100-150 lines
│   └── symbol_extractor.py # 80-100 lines
├── graphs/
│   ├── call_graph.py     # 200-250 lines
│   ├── control_flow.py   # 150-200 lines
│   └── graph_utils.py    # Shared DOT generation
├── metrics/
│   ├── complexity.py     # 100 lines
│   └── loc_counter.py    # 80 lines
└── generators/
    ├── dot_generator.py  # 120 lines
    └── tikz_converter.py # 100 lines
```

**Validation:**
```bash
# Test call graph extraction
python analysis/graphs/call_graph.py /home/eirikr/Playground/minix/minix/kernel/arch/i386/mpx.S \
  > artifacts/graphs/mpx_calls.dot

# Test DOT → TikZ conversion
python analysis/generators/tikz_converter.py artifacts/graphs/mpx_calls.dot \
  > latex/figures/04-call-graph-kernel.tex

# Compile to PDF
cd latex/figures && pdflatex 04-call-graph-kernel.tex
```

---

### Phase 2: Enhanced Diagrams (Call Graphs, Control Flow)
**Duration:** 3-4 hours
**Agents:** `tikz-whitepaper-synthesizer`, `polyglot-systems-architect`

**Tasks:**
1. **Call Graph: Kernel Core** (1.5 hours)
   - Input files: `mpx.S`, `klib.S`, `proc.c`, `protect.c`
   - Extract: All function definitions and calls
   - Generate: `04-call-graph-kernel.{dot,tex,pdf}`
   - Style: Hierarchical layout, color-coded by file

2. **Control Flow: INT Entry** (1 hour)
   - Focus: `ipc_entry_softint_orig` (mpx.S:265) → `do_ipc()`
   - Show: Assembly→C transition, register saves, stack operations
   - Generate: `05-control-flow-int.{dot,tex,pdf}`

3. **Control Flow: SYSENTER Entry** (1 hour)
   - Focus: `ipc_entry_sysenter` (mpx.S:220) → `do_ipc()`
   - Compare: Differences from INT path
   - Generate: `06-control-flow-sysenter.{dot,tex,pdf}`

4. **Memory Layout Diagram** (0.5 hour)
   - TikZ manual creation (not generated)
   - Show: User stack, kernel stack, heap, code segments
   - Address ranges from GDT/IDT analysis
   - Generate: `07-memory-layout.{tex,pdf}`

**Deliverables:**
```
diagrams/
├── 04-call-graph-kernel.{dot,tex,pdf}
├── 05-control-flow-int.{dot,tex,pdf}
├── 06-control-flow-sysenter.{dot,tex,pdf}
└── 07-memory-layout.{tex,pdf}
```

**Integration with Whitepaper:**
- Add new `\begin{figure*}` blocks in whitepaper
- Reference in sections 3 (System Calls) and 4 (Context Switching)
- Update captions with detailed descriptions

---

### Phase 3: Performance Plots (PGFPlots)
**Duration:** 2-3 hours
**Agents:** `tikz-whitepaper-synthesizer`

**Tasks:**
1. **Cycle Count Plot** (1.5 hours)
   - Data source: MICROARCHITECTURE-DEEP-DIVE.md (existing measurements)
   - X-axis: Mechanism (INT, SYSENTER, SYSCALL)
   - Y-axis: Cycles (entry, exit, total)
   - Style: Bar chart with error bars
   - Generate: `08-performance-cycles.{tex,pdf}`

2. **µop Execution Plot** (1 hour)
   - Data source: Same as above
   - Show: µop counts for each mechanism
   - Style: Stacked bar chart (different phases)
   - Generate: `09-performance-uops.{tex,pdf}`

**PGFPlots Template:**
```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
\begin{axis}[
    ybar,
    xlabel={Mechanism},
    ylabel={Cycles},
    symbolic x coords={INT, SYSENTER, SYSCALL},
    xtick=data,
    nodes near coords,
    legend pos=north west
]
\addplot coordinates {(INT,200) (SYSENTER,70) (SYSCALL,60)};
\addplot coordinates {(INT,50) (SYSENTER,15) (SYSCALL,12)};
\legend{Entry,Exit}
\end{axis}
\end{tikzpicture}
\end{document}
```

**Deliverables:**
```
diagrams/
├── 08-performance-cycles.{tex,pdf}
└── 09-performance-uops.{tex,pdf}

latex/plots/
├── cycles_data.csv
└── uops_data.csv
```

---

### Phase 4: MCP Integration
**Duration:** 3-4 hours
**Agents:** `multi-agent-orchestrator`, `phd-software-engineer`

**Tasks:**
1. **Verify MCP Endpoints** (0.5 hour)
   - Test DeepWiki MCP: `https://mcp.deepwiki.com/mcp`
   - Verify Figma/Canva endpoints (if applicable)
   - Document authentication requirements

2. **Add MCP Servers to Claude Code** (1 hour)
   ```bash
   # DeepWiki (public repos)
   claude mcp add --transport http deepwiki https://mcp.deepwiki.com/mcp

   # Filesystem (local analysis)
   claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /home/eirikr/Playground/minix-cpu-analysis
   ```

3. **Custom Analysis MCP Server** (2 hours)
   - Create `mcp/servers/analysis_server.py`
   - Expose Python tools as MCP tools:
     - `extract_call_graph(file_path)`
     - `compute_metrics(file_path)`
     - `generate_diagram(type, output_path)`
   - Follow MCP protocol spec

4. **Integration Testing** (0.5 hour)
   - Test Claude Code can invoke analysis tools
   - Verify filesystem access works
   - Document usage patterns

**Deliverables:**
```
mcp/
├── servers/
│   ├── analysis_server.py       # Custom MCP server
│   ├── deepwiki_config.json
│   └── filesystem_config.json
└── clients/
    ├── claude_setup.sh          # Automated MCP setup
    └── test_integration.py      # Validation script
```

---

### Phase 5: Documentation Generation (DeepWiki-Style)
**Duration:** 2-3 hours
**Agents:** `general-purpose`, `tikz-whitepaper-synthesizer`

**Tasks:**
1. **Wiki Structure** (1 hour)
   - Create `docs/wiki/INDEX.md` (navigation)
   - Generate module pages:
     - `SYSTEM-CALLS.md` (INT/SYSENTER/SYSCALL deep dive)
     - `INTERRUPTS.md` (IRQ handling)
     - `MEMORY-MANAGEMENT.md` (paging, TLB, CR3)
   - Link to source code (file:line references)

2. **Embeddings/RAG** (1.5 hours)
   - Generate embeddings for all `.md` and source files
   - Store in SQLite-VSS or FAISS
   - Create `analysis/embeddings/rag_query.py` for Q&A

3. **Automated Updates** (0.5 hour)
   - Create `build/Makefile.wiki`
   - Regenerate wiki on source changes
   - Update embeddings incrementally

**Deliverables:**
```
docs/wiki/
├── INDEX.md
├── ARCHITECTURE.md
├── SYSTEM-CALLS.md
├── INTERRUPTS.md
└── MEMORY-MANAGEMENT.md

analysis/embeddings/
├── code_embedder.py
├── vector_store.py (SQLite-VSS wrapper)
└── rag_query.py
```

---

### Phase 6: Unified Build System
**Duration:** 2 hours
**Agent:** `phd-software-engineer`

**Tasks:**
1. **Master Makefile** (1 hour)
   - `build/Makefile.master`: Orchestrate all phases
   - Targets:
     - `all`: Full rebuild (diagrams + analysis + wiki + whitepaper)
     - `diagrams`: Generate all figures
     - `analysis`: Run Python tools
     - `wiki`: Update documentation
     - `clean`: Remove artifacts
     - `distclean`: Full clean including cache

2. **Incremental Builds** (0.5 hour)
   - Use timestamps to avoid redundant work
   - Cache intermediate results

3. **Documentation** (0.5 hour)
   - `BUILD-GUIDE.md`: Step-by-step build instructions
   - `AGENT-USAGE.md`: How to use with Claude Code agents

**Deliverables:**
```
build/
├── Makefile.master
├── Makefile.diagrams
├── Makefile.analysis
└── Makefile.wiki

BUILD-GUIDE.md
AGENT-USAGE.md
```

**Example Master Makefile:**
```makefile
.PHONY: all diagrams analysis wiki whitepaper clean

all: diagrams analysis wiki whitepaper

diagrams:
	$(MAKE) -C diagrams -f ../build/Makefile.diagrams

analysis:
	$(MAKE) -f build/Makefile.analysis

wiki:
	$(MAKE) -f build/Makefile.wiki

whitepaper:
	$(MAKE) -C whitepaper

clean:
	rm -rf artifacts/graphs/* artifacts/metrics/*
	$(MAKE) -C diagrams clean
	$(MAKE) -C whitepaper clean
```

---

## Risk Analysis and Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **tree-sitter C parser incomplete** | Medium | High | Fallback to ctags/global; manual annotation |
| **DOT → TikZ conversion artifacts** | Low | Medium | Custom templates; manual TikZ cleanup |
| **MCP server auth issues** | Medium | Low | Use local filesystem MCP; skip DeepWiki if unavailable |
| **Performance plot data incomplete** | Low | Low | Use existing measurements from docs; estimate if needed |
| **Build system complexity** | Low | Medium | Extensive testing; clear documentation |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **MINIX source changes** | Low | High | Version pinning (commit d5e4fc0); detect changes |
| **LaTeX compilation failures** | Low | High | Extensive testing per diagram; include PDFs as fallback |
| **Python dependency hell** | Medium | Medium | Virtual environment; lock versions with `requirements.txt` |
| **Agent coordination failures** | Low | Medium | Manual fallback for critical tasks |

---

## Agent Assignment Matrix

| Phase | Primary Agent | Secondary Agent | Responsibility |
|-------|---------------|-----------------|----------------|
| 0. Planning | `Plan` | `Explore` | Architecture design, repo inventory |
| 1. Python Tooling | `polyglot-systems-architect` | `phd-software-engineer` | Parser/graph development |
| 2. Diagrams | `tikz-whitepaper-synthesizer` | `polyglot-systems-architect` | TikZ generation, DOT conversion |
| 3. Performance Plots | `tikz-whitepaper-synthesizer` | - | PGFPlots data visualization |
| 4. MCP Integration | `multi-agent-orchestrator` | `phd-software-engineer` | Server setup, protocol implementation |
| 5. Wiki Generation | `general-purpose` | `tikz-whitepaper-synthesizer` | Documentation, embeddings |
| 6. Build System | `phd-software-engineer` | - | Makefile orchestration |
| Testing | `general-purpose` | ALL | Integration validation |

---

## Success Criteria

### Phase-Level Validation

- ✅ **Phase 1**: Python tools extract call graph from `mpx.S` (verifiable DOT output)
- ✅ **Phase 2**: At least 4 new diagrams compile to PDF without errors
- ✅ **Phase 3**: Performance plots accurately reflect documented measurements
- ✅ **Phase 4**: Claude Code can invoke at least 2 MCP servers successfully
- ✅ **Phase 5**: Wiki pages auto-generate with source links
- ✅ **Phase 6**: `make all` builds entire system in < 5 minutes

### Final Integration Tests

1. **End-to-End Diagram Generation:**
   ```bash
   cd /home/eirikr/Playground/minix-cpu-analysis
   make clean && make diagrams
   ls diagrams/*.pdf | wc -l  # Should be 9 (3 existing + 6 new)
   ```

2. **Whitepaper Compilation:**
   ```bash
   cd whitepaper
   make clean && make all
   # Should compile with ZERO errors, include all 9 figures
   ```

3. **Python Analysis:**
   ```bash
   python analysis/graphs/call_graph.py /home/eirikr/Playground/minix/minix/kernel/arch/i386/mpx.S
   # Should output valid DOT graph
   ```

4. **MCP Server Health:**
   ```bash
   python mcp/servers/analysis_server.py --health-check
   # Should return: {"status": "healthy", "tools": 3}
   ```

5. **Wiki Q&A:**
   ```bash
   python analysis/embeddings/rag_query.py "How does SYSENTER work?"
   # Should return answer with source references
   ```

---

## Timeline

**Total Estimated Duration:** 18-24 hours (over 3-5 days with validation pauses)

```
Day 1: Planning + Python Tooling (Phases 0-1)  → 6 hours
Day 2: Diagrams + Performance Plots (Phases 2-3) → 7 hours
Day 3: MCP + Wiki + Build System (Phases 4-6)    → 7 hours
Day 4-5: Integration Testing + Refinement        → 2-4 hours
```

**Parallel Execution Opportunities:**
- Phases 2 & 3 can run concurrently (different agents)
- Phase 5 (wiki) can start after Phase 1 (parsers ready)
- Phase 6 (build) can be incrementally developed alongside others

---

## Next Steps (Immediate Actions)

1. **Validate Online Claims** (30 min)
   - Test DeepWiki MCP endpoint: `curl https://mcp.deepwiki.com/mcp`
   - Verify `dot2tex` installation: `dot2tex --version`
   - Check tree-sitter C bindings: `python -c "from tree_sitter_c import *"`

2. **Create Directory Structure** (10 min)
   ```bash
   mkdir -p analysis/{parsers,graphs,metrics,embeddings,generators}
   mkdir -p mcp/{servers,clients}
   mkdir -p build artifacts/{graphs,metrics,embeddings,cache}
   mkdir -p latex/{figures,plots}
   mkdir -p docs/wiki
   ```

3. **Install Python Dependencies** (20 min)
   ```bash
   python -m pip install --user tree-sitter tree-sitter-c \
     networkx pygraphviz lizard sentence-transformers faiss-cpu
   ```

4. **Launch Phase 1 Agents** (proceed to implementation)
   - Deploy `polyglot-systems-architect` for parser development
   - Deploy `phd-software-engineer` for graph extraction

---

## Appendix A: Technology Justifications

### Why tree-sitter over Clang AST?
- **Pro**: Language-agnostic, fast, incremental parsing
- **Con**: Simpler AST (no semantic analysis)
- **Decision**: Good enough for call graph extraction; Clang overkill

### Why dot2tex over manual TikZ?
- **Pro**: Automated graph→TikZ conversion
- **Con**: Less control over styling
- **Decision**: Use for complex graphs (call/control flow); manual TikZ for simple diagrams

### Why SQLite-VSS over ChromaDB/Pinecone?
- **Pro**: Lightweight, no external service, SQL-queryable
- **Con**: Less feature-rich than specialized vector DBs
- **Decision**: Offline-first requirement; extensibility not critical

### Why Custom MCP Server over Direct Python?
- **Pro**: Claude Code integration, standardized protocol
- **Con**: Additional complexity
- **Decision**: Future-proof; enables agent-driven workflows

---

## Appendix B: Alternative Approaches Considered

1. **Use Joern CPG instead of tree-sitter**
   - **Rejected**: Overkill for call graph extraction; steep learning curve
   - **Keep**: Document as future enhancement for dataflow analysis

2. **Generate diagrams with PlantUML instead of Graphviz**
   - **Rejected**: PlantUML less flexible for custom layouts
   - **Keep**: Good for UML-specific diagrams (future)

3. **Use ChatGPT API for embeddings instead of local models**
   - **Rejected**: Violates offline-first requirement
   - **Keep**: Document as cloud-enhanced option

4. **Package entire stack as single PKGBUILD**
   - **Deferred**: Implement after Phase 6 validation
   - **Reason**: Ensure stability before packaging

---

## Appendix C: Reference URLs (To Be Verified)

**MCP Servers:**
- DeepWiki: https://mcp.deepwiki.com/mcp (SSE: /sse)
- Figma: https://mcp.figma.com/mcp
- Filesystem: npm package `@modelcontextprotocol/server-filesystem`

**Documentation:**
- MCP Spec: https://modelcontextprotocol.io/
- DeepWiki Docs: https://docs.devin.ai/work-with-devin/deepwiki
- dot2tex Manual: https://mirrors.mit.edu/CTAN/graphics/dot2tex/dot2tex.pdf

**Source Code:**
- Joern: https://github.com/joernio/joern
- tree-sitter: https://tree-sitter.github.io/tree-sitter/
- DeepWiki Open (community): https://github.com/AsyncFuncAI/deepwiki-open

---

**END OF INTEGRATION PLAN**

*This document is a living blueprint. Update as implementation progresses.*
