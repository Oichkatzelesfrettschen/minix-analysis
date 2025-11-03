# MINIX Analysis Best Practices

**Version**: 1.0.0
**Date**: 2025-11-01
**Source**: Reorganized from MEGA-BEST-PRACTICES.md
**Purpose**: Unified practices, roadmaps, and knowledge atlas for MINIX 3.4.0-RC6 analysis

---

## 0. Project Snapshot & Metrics

- **Portfolio Scale**: 26,349 lines of documentation, 20+ curated artifacts, four reusable Python analysis tools, and machine-readable catalogs (e.g., `syscall_catalog.json`).
- **Coverage Achieved**: Boot sequence, process creation, syscall dispatch, IPC, memory management, interrupt handling, privilege transitions, and architecture variants verified against 100+ MINIX source files with ~40% kernel code footprint inspected line-by-line.
- **Diagram Suite**: Seven CPU interface diagrams plus five data-driven visuals (syscall table, process states, boot phases, IPC topology, memory regions) regenerated via automated pipelines.
- **Key Findings**:
  - Multiboot → Ring 3 transition documented across 12 CPU state snapshots; timer initialized at 1000 Hz for deterministic scheduling.
  - Fork/exec lifecycle traced end-to-end, confirming INT 0x30 entry, FPU context management, CR3 flush costs (~6400 cycles), and child RTS flag behavior.
  - 46 kernel syscalls catalogued with complexity metrics (2–49) and source file references; message passing defined via 56-byte envelopes and generation-aware endpoints.
  - ARM support mapped (10+ files) with privilege-mode comparisons and syscall differences captured alongside the canonical i386 path.
- **How to Consume**: Leadership skims this atlas + executive briefs (≈25 min), engineers deep dive via trace dossiers and diagrams, researchers pull JSON exports and benchmarking frameworks for reproducible studies.

---

## 1. Mission & Architectural Doctrine

- **Charter**: Deliver a production-grade knowledge system that dissects MINIX 3.4.0-RC6 from boot to userspace, spanning CPU interface, process lifecycle, memory management, IPC, benchmarks, and pedagogical framing.
- **Microkernel Reality**:
  - Kernel provides scheduling, IPC, low-level hardware drivers.
  - Userland servers (PM, VFS, RS, VM) run in Ring 3 and communicate via synchronous message passing (`sys_sendrec`, mailbox semantics).
  - Strict separation between policy (servers) and mechanism (kernel).
- **Supported Architectures**:
  - Canonical target: i386 32-bit; verify all diagrams, register tables, and syscall flows use EAX/EBX/ECX conventions.
  - ARM (earm) support documented separately; highlight deviations (vector table placement, banked registers) when relevant.
- **Three-Tier Repository Model**:
  1. **Tier 1** – Root orchestration (`Makefile`, pipelines, CI, agent guides).
  2. **Tier 2** – Domain modules (`modules/cpu-interface`, `modules/boot-sequence`, `modules/template`).
  3. **Tier 3** – Shared infrastructure (styles, MCP servers, reusable pipeline code, cross-module tests).
- **Outcome North Star**:
  - Accurate technical reconstruction validated by trace dossiers and diagrams.
  - Research-friendly deliverables (arXiv packages, whitepapers).
  - AI-assistant-ready knowledge surfaces (MCP endpoints, wiki, externalized JSON/graph data).

---

## 2. Temporal Roadmap & Phase Gates

| Phase | Status | Core Objectives | Exit Criteria | Key Sources |
| ----- | ------ | --------------- | ------------- | ----------- |
| Foundation (Phase 0) | ✅ | Rename repo, scaffold umbrella structure, mirror MINIX source, baseline tooling | Directory tree matches Tier model; backups captured; README aligned | Migration docs |
| Phase 1 – Core Infrastructure | ✅ | Build symbol extraction, call graphs, TikZ conversion, pipeline tests | Python tools validated; outputs stored under `analysis/` | Pipeline validation docs |
| Phase 2 – Enhanced Diagrams | ✅ | Generate syscall, paging, TLB, performance diagrams; correct architecture assumptions | Eight diagrams regenerated; architecture errata resolved | CPU interface analysis |
| Phase 2A–2E – Refinement & Publication | ✅ | Completion reports, benchmarking framework, comprehensive plan, arXiv packaging | Benchmark JSON available; arXiv package script validated | Phase completion reports |
| Phase 3 – Module Harmonization | 🔄 | Consolidate CPU/boot modules with shared styles, unify READMEs, migrate tests | Modules reference shared styles; redundant assets removed | Phase 3 roadmap |
| Phase 4 – Integration & Release | 🔮 | Final integration, MCP consolidation, publication-ready release | All make targets clean; whitepaper suite compiled | Phase 4 roadmap |

**Strategic Overlay**: Execute ALPHA (remove duplication) → BETA (build validation) → GAMMA (MCP fusion) → DELTA (testing/docs hardening) → EPSILON (final verification). Each sprint review should confirm the roadmap rung just completed and the next rung's blockers.

---

## 3. Repository & Knowledge Topology

- **Primary Surfaces**:
  - `docs/` & `documentation/`: Long-form manuals, deep dives, and supporting appendices.
  - `wiki/`: MkDocs-driven portal; treat `wiki/Home.md` as the navigation root; update `wiki/*/Overview.md` alongside module changes.
  - Root-level executive briefs for leadership visibility.
  - `whitepapers/`: Thematic essays on architecture rationale, pedagogy, testing strategy.
- **Generated Artifact Destinations**:
  - Diagrams → `diagrams/` (TikZ sources under `diagrams/tikz/`, compiled outputs named `*_diagram` or `*_report`).
  - Pipeline outputs & notebooks → `analysis-results/`.
  - Coverage → `htmlcov/`.
  - Logs & trace captures → `logs/`.
- **Shared Assets**:
  - Styles: `shared/styles/minix-styles.sty`, `minix-colors.sty`, `minix-arxiv.sty`, `STYLE-GUIDE.md`.
  - MCP infrastructure: `shared/mcp/` (servers, base classes, capability docs).
  - Pipeline utilities: `shared/pipeline/` (shell/Python scripts consumed by modules and CLI).

---

## 4. Core Technical Doctrine (Boot → Runtime)

### 4.1 Boot Sequence Summary
- **Phase 0 – Multiboot Entry**: `head.S` verifies magic, sets up a temporary 4 KB stack, and jumps into `pre_init` with the multiboot info structure; CPU state logged with CS=0x0010, paging disabled.
- **Phase 1 – Low-Level Setup**: `pre_init.c` parses multiboot payload (memory map, modules), initializes identity-mapped page tables, remaps the kernel to 0x80xxxxxx, and hands control back for a high-memory stack pivot.
- **Phase 2 – kmain Initialization**: `main.c` performs BSS sanity checks, copies boot parameters, initializes serial, calls `cstart()` to load GDT/IDT/TSS, acquires the big kernel lock, seeds the process table, configures programmable timers, and enables interrupts.
- **Phase 3 – First Scheduling & Interrupt Loop**: `switch_to_user` executes the first IRET into Ring 3. After ~10 ms the PIT triggers `hwint00` in `mpx.S`, which relies on `SAVE_PROCESS_CTX` to persist kernel state before resuming the run queue.
- **CPU Register Snapshots**: Trace dossiers capture six canonical register states (boot entry, post-`pre_init`, post-`cstart`, pre-user entry, timer interrupt, post-IRET) to validate emulator traces and instrumentation.

### 4.2 Process Lifecycle & Syscall Flow
- **Syscall Entry Matrix**: INT 0x30 (compatibility), SYSENTER (Intel fast path, ~40 cycles), and SYSCALL (AMD fast path, ~35 cycles) all supported; MINIX selects the optimal path based on CPUID/MSR capability checks, yielding up to 5.7× latency reduction over INT.
- **Fork Path**: User issues INT/SYSENTER → `mpx.S` saves full context → `sys_call` dispatches to `do_fork` → process table entry duplicated, FPU context saved, child endpoint regenerated, child flagged `RTS_VMINHIBIT` until scheduler activation.
- **Exec Path**: `do_exec` validates caller, populates `m_ptr`, calls `arch_proc_init` to install new EIP/ESP/ps_strings, and intentionally omits a reply because the image is replaced in place.
- **Context Switching Costs**: `contextswitch()` updates CR3 (flushes TLB ~6400 cycles unless global pages used), refreshes TSS.ESP0, restores segment and general registers, then returns via IRET/SYSEXIT/SYSRET depending on trap style.
- **Syscall Catalog Metrics**: 46 kernel syscalls across 35 files, complexity scores from 2 (lightweight) to 49 (`SYS_PRIVCTL`), JSON catalog available for automation (`analysis-results/syscall_catalog.json`).

### 4.3 IPC & Endpoint Mechanics
- **Message Frames**: Fixed 56-byte envelopes with 11 layout variants; grants enable safe copy semantics without exposing kernel buffers.
- **Operations**: `SEND`, `RECEIVE`, `SENDREC`, `NOTIFY`, and grant operations orchestrated via synchronous message passing; endpoints encode generation counters to prevent stale references.
- **Servers & Policy**: Core services (PM, VFS, RS, VM) execute in user space; kernel mediates IPC but enforces no policy, aligning with microkernel doctrine.
- **Timing Characteristics**: IPC latency and grant usage documented for benchmarking; use this section when profiling message-heavy workloads.

### 4.4 Memory & Paging Insights
- i386 two-level paging (Page Directory → Page Tables) with 4 KB pages and optional 4 MB PDE (PSE); address space split at 0x80000000 with kernel higher half mapping.
- CR3 reload semantics govern TLB flushes; tracers should account for global page optimizations and the cost of per-switch invalidations.
- Page faults (#PF vector 14) trigger kernel handlers that read CR2, forward to the VM server, and either resolve via mapping or deliver SIGSEGV; copy-on-write and demand paging leverage this pathway.

### 4.5 Hardware & Microarchitecture
- **Interrupt Fabric**: Legacy PIC (15 IRQs, I/O port EOIs) vs APIC (24+ IRQs, MMIO EOIs, SMP support) flows documented; APIC reduces latency ~25% and is mandatory for multi-core operation.
- **Timer & Frequency Assumptions**: PIT configured at 1000 Hz; maintain consistent tick sources when instrumenting or porting to alternative hardware.
- **Architecture Variants**: ARM pathway reroutes vector tables, leverages banked registers, and modifies syscall/exception entry; highlight these deltas when adapting tooling or diagrams beyond x86.

---

## 5. Module Operating Manuals

### 5.1 CPU Interface Module (`modules/cpu-interface`)
- **Deliverables**: Diagram suite, module README, docs mirroring root analysis.
- **Build Path**: `make cpu` (compiles LaTeX, updates diagrams); ensure LaTeX imports shared styles via relative paths.
- **Data Sources**: `analysis/` outputs, benchmarks from `benchmarks/`, wiki extracts.
- **Quality Bar**: Validate architecture assumptions against MINIX source tree at `$MINIX_ROOT/minix/kernel/arch/i386`.

### 5.2 Boot Sequence Module (`modules/boot-sequence`)
- **Deliverables**: Boot whitepaper, quick-start guide, TikZ boot diagrams.
- **Build Path**: `make boot`; confirm module README references umbrella structure.
- **Trace Discipline**: Keep seven-phase structure intact; update CPU state tables whenever kernel commit changes control flow.

### 5.3 Shared Infrastructure (`shared/`)
- **Styles**: Manage `minix-colors.sty`, `minix-arxiv.sty`; follow style guide for naming and palette governance.
- **MCP Servers**: Document capabilities; align CLI feature flags with server handlers.
  - Shared code lives under `shared/mcp/server/`, providing data accessors for both CPU and boot endpoints.
- **Pipelines**: Centralize Python/Bash helpers; modules should import rather than duplicate.

### 5.4 Formal Models & Benchmarking
- **Formal Verification**: Formal models document defines model scope; track specification coverage and proof status.
- **Benchmark Framework**: Use benchmarking framework to structure experiments; deposit JSON results in `analysis-results/benchmarks/`.

### 5.5 Whitepapers & Publications
- `whitepapers/*.md` provide thematic rationale; align with module outputs.
- Use whitepaper completion reports as closure checklists when updating LaTeX manuscripts.

---

## 6. Operational Runbooks & Checklists

### 6.1 Migration & Harmonization Tasks
1. Rename legacy repo to `minix-analysis`; confirm Tier directories exist.
2. Relocate LaTeX styles to `shared/styles/`; create color/arXiv packages; update module imports.
3. Move MCP servers into `shared/mcp/`; adjust import paths.
4. Refresh module READMEs to reference umbrella architecture.
5. Verify pipelines and tests post-move.

### 6.2 Pipeline Execution
1. Ensure `$MINIX_ROOT` points to `/home/eirikr/Playground/minix`.
2. Run `make pipeline` for full extraction → TikZ flow; capture runtime metrics in `logs/`.
3. For targeted CLI use, run `python -m os_analysis_toolkit.cli --source $MINIX_ROOT --output analysis-results/<name> [--parallel --workers 8]`.
4. Post-run, sync diagrams and docs; update relevant sections in this atlas and module docs.
5. **Data-Driven Diagram Stack**:
   - `minix_source_analyzer.py` parses 91 kernel files (19,659 LOC) and emits JSON.
   - `tikz_generator.py` transforms JSON into TikZ assets compiled via `pdflatex` into vector graphics.
   - Machine-readable outputs live in `diagrams/data/` and `diagrams/tikz-generated/`.

### 6.3 Release & Integration
1. Execute full build matrix: `make pipeline`, `make cpu`, `make boot`, `pytest`, `pytest -m benchmark`.
2. Refresh coverage and confirm `htmlcov/` published.
3. Generate whitepapers/arXiv packages via `scripts/create-arxiv-package.sh <module>`.
4. Update executive summaries and roadmap documents with release outcomes.
5. Tag release after ensuring documentation, diagrams, and MCP endpoints align.

---

## 7. Tooling, Automation & Environment

- **Make Targets**:
  - `make help` – discover curated commands.
  - `make pipeline` – E2E analysis.
  - `make cpu`, `make boot` – module-specific LaTeX builds.
- **Python CLI**:
  - `python -m os_analysis_toolkit.cli --source <path> --output <dir> [--parallel --workers 8]`.
  - Data queries: `--list-resources`, `--resource <name>`, `--syscall <name>`.
  - Summaries: `--kernel-summary [--top-syscalls N]`, `--boot-critical-path`.
- **Analysis Toolchain**:
  - `analyze_syscalls.py` – extracts and scores 46 kernel syscalls, exporting JSON for dashboards.
  - `analyze_ipc.py` – documents message layouts, grants, and endpoint usage patterns.
  - `generate_tikz_diagrams.py` / `tikz_generator.py` – convert structured data into LaTeX/TikZ.
  - `analyze_arm.py` – surfaces ARM-specific code paths.
- **Environment**:
  - Python 3.13, `pip install -r requirements.txt`.
  - LaTeX toolchain (TeX Live 2023) for publication parity.
  - Graphviz, `ctags`, `rg` for pipeline utilities.
- **Agents & Automation**:
  - Install `pre-commit` hooks; enforce `black`, `flake8`, `mypy`.
  - Agents must respect sandbox paths and update logs/tests transparently.

---

## 8. Testing, Benchmarking & Quality Gates

- **Pytest Strategy**:
  - Default command: `pytest`.
  - Rapid iterations: `pytest -m "not slow"`.
  - Benchmarking: `pytest -m benchmark` with outputs archived.
  - Integration with MINIX source: mark tests as `requires_minix`.
- **Coverage Discipline**:
  - Run `pytest --cov-report=html`; ensure `htmlcov/index.html` reflects new results.
  - Update coverage thresholds and highlight deltas in testing summary.
- **Pipeline Validation**:
  - Keep test scripts executable and up-to-date.
  - When pipelines change, refresh validation docs with run metadata.
- **Performance Baselines**:
  - Capture `min`, `max`, `stddev`, commit hash, tool versions.
  - Document anomalies and mitigations.

---

## 9. Documentation, Publication & Knowledge Sharing

- **Writing Standards**:
  - Use concise docstrings and PEP 484 type hints in code.
  - Maintain narrative structure: executive summary → context → deep dive → references.
  - For diagrams, follow `_report` / `_diagram` suffix conventions.
- **Wiki & Onboarding**:
  - Update wiki pages after major changes.
  - Reflect new tutorials or guides in docs.
- **ArXiv Standards** (see ARXIV-STANDARDS.md):
  - TeX Live 2023 compliance, root-level `main.tex`, sanitized filenames.
  - Include `.bbl`, not `.bib`; convert EPS to PDF; verify `pdflatex` logs clean.
  - Provide submission README noting compilation steps.
- **Whitepaper Suite**:
  - Use shared styles, color palettes, and `minix-arxiv.sty`.
  - Sync narrative with diagrams and benchmark data.
  - **Thematic Highlights**:
    - `01-WHY-MICROKERNEL-ARCHITECTURE.md` – articulates reliability/security rationale.
    - `02-WHY-PARALLEL-ANALYSIS-WORKS.md` – justifies multi-agent analysis pipelines.
    - `03-WHY-THIS-TESTING-STRATEGY.md` – defends the pytest regimen.
    - `04-WHY-PEDAGOGY-MATTERS.md` – frames the educational mission.
- **Pedagogical Layer** (see PEDAGOGICAL-FRAMEWORK.md):
  - Embrace progressive disclosure—beginner-friendly walkthroughs leading into line-by-line commentary.

---

## 10. Collaboration, Governance & Change Control

- **Commit Hygiene**:
  - Format: `<type>: <imperative>` (e.g., `docs: Harmonize boot trace narrative`).
  - Squash fixups prior to review; prefer rebasing to retain linear history.
- **Pull Requests**:
  - Include scope summary, affected modules, exact test commands with results, refreshed diagrams/screenshots.
  - Reference roadmap phase or issue IDs in the body.
- **Change Logging**:
  - Update strategic docs when plans shift.
  - Note environment changes to preserve onboarding clarity.
- **Agent Coordination**:
  - Follow agent-specific guides; log automation outputs under `logs/`.
  - When MCP endpoints evolve, refresh capability docs and CLI help.

---

## 11. Forward Synthesis Planner

**Progress Recap**:
- Unified documentation landscape now centered on this best practices guide with metrics, technical doctrine, operational runbooks, and governance summarized.
- CPU/boot trace dossiers, syscall catalogs, and data-driven diagram pipelines are fully harmonized.
- Strategic roadmaps captured with clear exit criteria; module manuals and QA practices consolidated for reproducibility.

**Near-Term Objectives (1–2 weeks)**:
- ✅ Completed: Removed module-level style duplicates, aligned LaTeX imports.
- ✅ Completed: Updated wiki landing page to point at documentation structure.
- ✅ Completed: Regenerated pipeline artifacts and reran pytest.
- ✅ Completed: Catalogued standalone Markdown assets for Phase 4 cleanup decisions.

**Mid-Term Objectives (Phase 3–4 execution window)**:
- Consolidate MCP servers under `shared/mcp/`, update capability docs.
- Extend automation to regenerate data-driven diagrams as part of `make pipeline`.
- Prepare publication bundles by aligning LaTeX manuscripts.
- Define regression test suites for benchmarks.

**Long-Term Vision (Post Phase 4)**:
- Establish continuous synthesis cadence: every major change triggers atlas updates, wiki rebuilds, pipeline runs.
- Develop onboarding curricula combining whitepapers, pedagogy guides, and interactive notebooks.
- Explore automation for MCP knowledge surfacing.

Progress toward each objective should be tracked with dates and owners; treat this as the active roadmap.

---

## 12. Source Document Concordance

| Source Documents | Integrated Here | Contribution |
| ---------------- | --------------- | ------------ |
| README.md, UMBRELLA-ARCHITECTURE.md | §1, §3 | Repository architecture, mission charter |
| MASTER-ANALYSIS-SYNTHESIS.md | §1, §2, §4 | Executive scope, phase deliverables |
| CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md | §0, §4.2, §4.5 | Portfolio metrics, diagram insights |
| Phase completion docs | §2, §5, §6 | Temporal roadmap, harmonization tasks |
| ULTRA-DETAILED-STRATEGIC-ROADMAP.md | §2, §10 | Strategic ladder, governance |
| BOOT-TO-KERNEL-TRACE.md | §4.1 | Boot sequence phases |
| MINIX-SYSCALL-CATALOG.md | §4.2 | Process lifecycle, syscall details |
| MINIX-CPU-INTERFACE-ANALYSIS.md | §4.4, §5.1 | CPU interface scope |
| AGENTS.md, CAPABILITIES-AND-TOOLS.md | §3, §7, §10 | Command suites, automation |
| TESTING-SUMMARY.md | §6.2, §8, §9 | Pipeline validation, QA |
| ARXIV-STANDARDS.md | §9 | Publication standards |
| LIONS-STYLE-PEDAGOGICAL-FRAMEWORK.md | §9 | Pedagogical approach |

---

## 13. Maintaining This Document

- Treat this document as the front door for contributors—update promptly after material changes.
- When legacy documents become outdated, either refresh them to match this guide or mark them as archival.
- Relocate superseded Markdown into `archive/` once their insights are captured here.
- Before each major release or roadmap milestone, review this guide to ensure every section reflects the current state.

> **Canonical Rule**: This best practices guide supersedes fragmented guidance. When conflicts arise, reconcile the source material and resynthesize the outcome here so the project continues to operate from a single, harmonized playbook.

---

*Last Updated: 2025-11-01*
*Source: /home/eirikr/Playground/minix-analysis/MEGA-BEST-PRACTICES.md*
