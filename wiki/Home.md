# MINIX Analysis Project Wiki

**Welcome to the documentation portal for the MINIX 3.4.0-RC6 analysis umbrella project.** Start with the root compendium (`MEGA-BEST-PRACTICES.md`) for mission context, phase roadmap, and consolidated best practices; this wiki surfaces focused guides and module primers.

---

## Quick Navigation

- [Architecture Overview](architecture/Overview.md) – CPU interface findings and diagrams.
- [Boot Sequence](boot-sequence/Overview.md) – Phase-by-phase boot trace and visualisations.
- [Build System](build-system/Overview.md) – Make targets and automation layout.
- [Style Guide](style-guide/Overview.md) – Shared LaTeX/TikZ conventions and accessibility tips.
- [API Reference](api/MCP-Servers.md) – MCP capabilities (Phase 5 consolidation target).
- [Contributing](Contributing.md) – Collaboration guidelines.
- [Testing](Testing.md) – Pytest philosophy, markers, and coverage expectations.

Module documentation is mirrored from `modules/<name>/docs/`; refer to the compendium for the authoritative roadmap and synthesis.

---

## Project Structure

```
minix-analysis/                 # Tier 1 – umbrella root
├── shared/                     # Tier 3 – reusable infrastructure
│   ├── styles/                 # LaTeX/TikZ styles (minix-*.sty, STYLE-GUIDE.md)
│   ├── pipeline/               # Shared analysis helpers
│   └── tests/                  # Cross-module testing utilities
├── modules/                    # Tier 2 – domain modules
│   ├── cpu-interface/          # CPU interface analysis (docs, latex, mcp, pipeline, tests)
│   └── boot-sequence/          # Boot sequence analysis (docs, latex, mcp, pipeline, tests)
├── docs/, documentation/       # Long-form references
├── wiki/                       # This portal (MkDocs-friendly Markdown)
├── diagrams/, analysis-results/ # Generated diagrams and data artefacts
└── Makefile                    # Root build orchestration
```

Shared LaTeX packages (minix-arxiv/minix-styles/minix-colors) live under `shared/styles/`; update them centrally to propagate typography and colour changes across modules.

---

## Getting Started

1. Review `MEGA-BEST-PRACTICES.md` for mission, roadmap, and operational doctrine.
2. Install prerequisites noted in `INSTALLATION.md` (Python 3.13 environment, TeX Live 2023, Graphviz, ripgrep, etc.).
3. Build the artefacts you need:
   ```bash
   make pipeline          # Run symbol extraction → graphing → TikZ generation
   make cpu               # Compile CPU interface manuscripts
   make boot              # Compile boot sequence manuscripts
   make arxiv-cpu         # Package CPU paper for arXiv submission
   make arxiv-boot        # Package boot paper for arXiv submission
   ```
4. Run tests as appropriate:
   ```bash
   pytest                 # Full test suite (markers configured in pytest.ini)
   pytest -m "not slow"   # Quick iteration
   pytest -m benchmark    # Performance baselines (archives JSON in analysis-results/benchmarks/)
   ```

---

## Module Snapshots

### CPU Interface (modules/cpu-interface)
- Focus: Syscall entry paths (INT/SYSENTER/SYSCALL), interrupt/exception handling, context switching, paging, and micro-architectural performance.
- Deliverables: `MINIX-CPU-INTERFACE-ANALYSIS.md`, `ISA-LEVEL-ANALYSIS.md`, `MICROARCHITECTURE-DEEP-DIVE.md`, 11 TikZ diagrams (`CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md`).
- Status: Phase 3 harmonisation complete; pipeline/tests expansion scheduled for Phase 4, MCP integration in Phase 5.

### Boot Sequence (modules/boot-sequence)
- Focus: Multiboot hand-off through `switch_to_user()`, five-phase boot timeline, hub-and-spoke topology, and state transition analysis.
- Deliverables: `FINAL_SYNTHESIS_REPORT.md`, `ARXIV_WHITEPAPER_COMPLETE.md`, `QUICK_START.md`, TikZ diagram suite regenerated via shared styles.
- Status: Documentation and LaTeX fully aligned with shared infrastructure; module scripts and tests maintained under `pipeline/` and `tests/`.

---

## Style & Accessibility Highlights

- Colour palettes, typography, and ArXiv compliance are enforced via `shared/styles/`. Use `minix-colors-cvd.sty` variants for colour-vision deficiency friendly diagrams.
- Refer to `shared/styles/STYLE-GUIDE.md` and `latex/TIKZ-STYLE-GUIDE.md` for TikZ conventions, code listing presets, and diagram naming rules.
- Documentation guidelines (docstrings, tone, formatting) are centralised in `AGENTS.md` and the compendium.

---

## Roadmap & Automation

- Phase progress, strategic objectives, and upcoming tasks are tracked in the “Forward Synthesis Planner” section of `MEGA-BEST-PRACTICES.md`.
- MCP consolidation and richer automation (auto-regenerated diagrams, knowledge surfacing) are scheduled for Phases 4–5; watch `CAPABILITIES-AND-TOOLS.md` for updates.
- When in doubt about priorities or process, treat the compendium as the single source of truth and update both it and the relevant wiki/module files in lock-step.
