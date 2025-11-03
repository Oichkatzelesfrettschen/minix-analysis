# MINIX Analysis – Unified Practices, Roadmaps, and Knowledge Atlas

**Purpose**: Collapse the dozens of Markdown artifacts in this repository into a single authoritative playbook. Everything needed to orient, plan, execute, verify, publish, and govern MINIX 3.4.0-RC6 analysis work now lives here. When a legacy document diverges from this compendium, update the original and resynchronize this atlas to preserve coherence.

---

## 0. Project Snapshot & Metrics

- **Portfolio Scale** (*ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md*): 26,349 lines of documentation, 20+ curated artifacts, four reusable Python analysis tools, and machine-readable catalogs (e.g., `syscall_catalog.json`).
- **Coverage Achieved**: Boot sequence, process creation, syscall dispatch, IPC, memory management, interrupt handling, privilege transitions, and architecture variants verified against 100+ MINIX source files with ~40 % kernel code footprint inspected line-by-line.
- **Diagram Suite** (*CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md*): Seven CPU interface diagrams plus five data-driven visuals (syscall table, process states, boot phases, IPC topology, memory regions) regenerated via automated pipelines.
- **Key Findings**:
  - Multiboot → Ring 3 transition documented across 12 CPU state snapshots; timer initialized at 1000 Hz for deterministic scheduling.
  - Fork/exec lifecycle traced end-to-end, confirming INT 0x30 entry, FPU context management, CR3 flush costs (~6400 cycles), and child RTS flag behavior.
  - 46 kernel syscalls catalogued with complexity metrics (2–49) and source file references; message passing defined via 56-byte envelopes and generation-aware endpoints.
  - ARM support mapped (10+ files) with privilege-mode comparisons and syscall differences captured alongside the canonical i386 path.
- **How to Consume**: Leadership skims this atlas + executive briefs (≈25 min), engineers deep dive via trace dossiers and diagrams, researchers pull JSON exports and benchmarking frameworks for reproducible studies.

---

## 1. Mission & Architectural Doctrine

- **Charter** (*README.md*, *MASTER-ANALYSIS-SYNTHESIS.md*, *UMBRELLA-ARCHITECTURE.md*): Deliver a production-grade knowledge system that dissects MINIX 3.4.0-RC6 from boot to userspace, spanning CPU interface, process lifecycle, memory management, IPC, benchmarks, and pedagogical framing.
- **Microkernel Reality** (*MINIX-ARCHITECTURE-SUMMARY.md*):
  - Kernel provides scheduling, IPC, low-level hardware drivers.
  - Userland servers (PM, VFS, RS, VM) run in Ring 3 and communicate via synchronous message passing (`sys_sendrec`, mailbox semantics).
  - Strict separation between policy (servers) and mechanism (kernel).
- **Supported Architectures** (*MINIX-CPU-INTERFACE-ANALYSIS.md*, *MINIX-ARM-ANALYSIS.md*):
  - Canonical target: i386 32-bit; verify all diagrams, register tables, and syscall flows use EAX/EBX/ECX conventions.
  - ARM (earm) support documented separately; highlight deviations (vector table placement, banked registers) when relevant.
- **Three-Tier Repository Model** (*README.md*, *REPOSITORY-STRUCTURE-AUDIT.md*):
  1. **Tier 1** – Root orchestration (`Makefile`, pipelines, CI, agent guides).
  2. **Tier 2** – Domain modules (`modules/cpu-interface`, `modules/boot-sequence`, `modules/template`).
  3. **Tier 3** – Shared infrastructure (styles, MCP servers, reusable pipeline code, cross-module tests).
- **Outcome North Star** (*COMPLETE-PROJECT-SYNTHESIS.md*, *COMPREHENSIVE-PEDAGOGICAL-SYNTHESIS.md*):
  - Accurate technical reconstruction validated by trace dossiers and diagrams.
  - Research-friendly deliverables (arXiv packages, whitepapers).
  - AI-assistant‑ready knowledge surfaces (MCP endpoints, wiki, externalized JSON/graph data).

---

## 2. Temporal Roadmap & Phase Gates

| Phase | Status | Core Objectives | Exit Criteria | Key Sources |
| ----- | ------ | --------------- | ------------- | ----------- |
| Foundation (Phase 0) | ✅ | Rename repo, scaffold umbrella structure, mirror MINIX source, baseline tooling | Directory tree matches Tier model; backups captured; README aligned | *MIGRATION-PLAN.md*, *PROJECT-SYNTHESIS.md* |
| Phase 1 – Core Infrastructure | ✅ | Build symbol extraction, call graphs, TikZ conversion, pipeline tests | `symbol_extractor.py`, `call_graph.py`, `tikz_converter.py`, `test_pipeline.sh` green; outputs stored under `analysis/` | *PHASE-1-COMPLETE.md*, *PIPELINE-VALIDATION-COMPLETE.md* |
| Phase 2 – Enhanced Diagrams | ✅ | Generate syscall, paging, TLB, performance diagrams; correct architecture assumptions | Eight diagrams regenerated; architecture errata resolved; documentation mirrors i386 reality | *PHASE-2-COMPLETE.md*, *MINIX-CPU-INTERFACE-ANALYSIS.md*, *MASTER-ANALYSIS-SYNTHESIS.md* |
| Phase 2A–2E – Refinement & Publication | ✅ | Completion reports, benchmarking framework, comprehensive plan, arXiv packaging | Benchmark JSON in `analysis-results/benchmarks/`; arXiv package script output validated; plan filed | *PHASE-2A-COMPLETION-REPORT.md*, *benchmarks/PHASE-2C-PERFORMANCE-BENCHMARKING-FRAMEWORK.md*, *arxiv-submission/PHASE-2E-ARXIV-SUBMISSION-PACKAGE.md* |
| Phase 3 – Module Harmonization | 🔄 | Consolidate CPU/boot modules with shared styles, unify READMEs, migrate tests | Modules reference shared styles; redundant assets removed; wiki sections updated | *PHASE-3-ROADMAP.md*, *MIGRATION-PROGRESS.md* |
| Phase 4 – Integration & Release | 🔮 | Final integration, MCP consolidation, publication-ready release | `make pipeline`, `make cpu`, `make boot` clean; whitepaper suite compiled; release notes authored | *PHASE-4-ROADMAP.md*, *FINAL-INTEGRATION-COMPLETE.md*, *FINAL-COMPLETE-ACHIEVEMENT.md* |

**Strategic Overlay** (*ULTRA-DETAILED-STRATEGIC-ROADMAP.md*): Execute ALPHA (remove duplication) → BETA (build validation) → GAMMA (MCP fusion) → DELTA (testing/docs hardening) → EPSILON (final verification). Each sprint review should confirm the roadmap rung just completed and the next rung’s blockers.

---

## 3. Repository & Knowledge Topology

- **Primary Surfaces**:
  - `docs/` & `documentation/`: Long-form manuals, deep dives, and supporting appendices.
  - `wiki/`: MkDocs-driven portal; treat `wiki/Home.md` as the navigation root; update `wiki/*/Overview.md` alongside module changes.
  - Root-level executive briefs (*ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md*, *FINAL-COMPLETE-ACHIEVEMENT.md*, *DELIVERY-SUMMARY.md*) for leadership visibility.
  - `whitepapers/`: Thematic essays on architecture rationale, pedagogy, testing strategy (e.g., *01-WHY-MICROKERNEL-ARCHITECTURE.md*, *03-WHY-THIS-TESTING-STRATEGY.md*).
- **Generated Artifact Destinations** (*AGENTS.md*, *DATA-DRIVEN-DOCUMENTATION.md*):
  - Diagrams → `diagrams/` (TikZ sources under `diagrams/tikz/`, compiled outputs named `*_diagram` or `*_report`).
  - Pipeline outputs & notebooks → `analysis-results/`.
  - Coverage → `htmlcov/`; summary pointer recorded in *TESTING-SUMMARY.md*.
  - Logs & trace captures → `logs/`.
- **Shared Assets**:
  - Styles: `shared/styles/minix-styles.sty`, `minix-colors.sty`, `minix-arxiv.sty`, `STYLE-GUIDE.md`.
  - MCP infrastructure: `shared/mcp/` (servers, base classes, capability docs mirrored in *CAPABILITIES-AND-TOOLS.md*).
  - Pipeline utilities: `shared/pipeline/` (shell/Python scripts consumed by modules and CLI).

---

## 4. Core Technical Doctrine (Boot → Runtime)

### 4.1 Boot Sequence Summary (*BOOT-TO-KERNEL-TRACE.md*, *COMPREHENSIVE-BOOT-RUNTIME-TRACE.md*)
- **Phase 0 – Multiboot Entry**: `head.S` verifies magic, sets up a temporary 4 KB stack, and jumps into `pre_init` with the multiboot info structure; CPU state logged with CS=0x0010, paging disabled.
- **Phase 1 – Low-Level Setup**: `pre_init.c` parses multiboot payload (memory map, modules), initializes identity-mapped page tables, remaps the kernel to 0x80xxxxxx, and hands control back for a high-memory stack pivot.
- **Phase 2 – kmain Initialization**: `main.c` performs BSS sanity checks, copies boot parameters, initializes serial, calls `cstart()` to load GDT/IDT/TSS, acquires the big kernel lock, seeds the process table, configures programmable timers, and enables interrupts.
- **Phase 3 – First Scheduling & Interrupt Loop**: `switch_to_user` executes the first IRET into Ring 3. After ~10 ms the PIT triggers `hwint00` in `mpx.S`, which relies on `SAVE_PROCESS_CTX` to persist kernel state before resuming the run queue.
- **CPU Register Snapshots**: Trace dossiers capture six canonical register states (boot entry, post-`pre_init`, post-`cstart`, pre-user entry, timer interrupt, post-IRET) to validate emulator traces and instrumentation.

### 4.2 Process Lifecycle & Syscall Flow (*FORK-PROCESS-CREATION-TRACE.md*, *MINIX-SYSCALL-CATALOG.md*, *CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md*)
- **Syscall Entry Matrix**: INT 0x30 (compatibility), SYSENTER (Intel fast path, ~40 cycles), and SYSCALL (AMD fast path, ~35 cycles) all supported; MINIX selects the optimal path based on CPUID/MSR capability checks, yielding up to 5.7× latency reduction over INT.
- **Fork Path**: User issues INT/SYSENTER → `mpx.S` saves full context → `sys_call` dispatches to `do_fork` → process table entry duplicated, FPU context saved, child endpoint regenerated, child flagged `RTS_VMINHIBIT` until scheduler activation.
- **Exec Path**: `do_exec` validates caller, populates `m_ptr`, calls `arch_proc_init` to install new EIP/ESP/ps_strings, and intentionally omits a reply because the image is replaced in place.
- **Context Switching Costs**: `contextswitch()` updates CR3 (flushes TLB ~6400 cycles unless global pages used), refreshes TSS.ESP0, restores segment and general registers, then returns via IRET/SYSEXIT/SYSRET depending on trap style.
- **Syscall Catalog Metrics**: 46 kernel syscalls across 35 files, complexity scores from 2 (lightweight) to 49 (`SYS_PRIVCTL`), JSON catalog available for automation (`analysis-results/syscall_catalog.json`).

### 4.3 IPC & Endpoint Mechanics (*ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md*, *MINIX-SYSCALL-CATALOG.md*)
- **Message Frames**: Fixed 56-byte envelopes with 11 layout variants; grants enable safe copy semantics without exposing kernel buffers.
- **Operations**: `SEND`, `RECEIVE`, `SENDREC`, `NOTIFY`, and grant operations orchestrated via synchronous message passing; endpoints encode generation counters to prevent stale references.
- **Servers & Policy**: Core services (PM, VFS, RS, VM) execute in user space; kernel mediates IPC but enforces no policy, aligning with microkernel doctrine.
- **Timing Characteristics**: IPC latency and grant usage documented for benchmarking; use this section when profiling message-heavy workloads.

### 4.4 Memory & Paging Insights (*ISA-LEVEL-ANALYSIS.md*, *MICROARCHITECTURE-DEEP-DIVE.md*)
- i386 two-level paging (Page Directory → Page Tables) with 4 KB pages and optional 4 MB PDE (PSE); address space split at 0x80000000 with kernel higher half mapping.
- CR3 reload semantics govern TLB flushes; tracers should account for global page optimizations and the cost of per-switch invalidations.
- Page faults (#PF vector 14) trigger kernel handlers that read CR2, forward to the VM server, and either resolve via mapping or deliver SIGSEGV; copy-on-write and demand paging leverage this pathway.

### 4.5 Hardware & Microarchitecture (*CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md*, *MICROARCHITECTURE-DEEP-DIVE.md*, *MINIX-ARM-ANALYSIS.md*)
- **Interrupt Fabric**: Legacy PIC (15 IRQs, I/O port EOIs) vs APIC (24+ IRQs, MMIO EOIs, SMP support) flows documented; APIC reduces latency ~25 % and is mandatory for multi-core operation.
- **Timer & Frequency Assumptions**: PIT configured at 1000 Hz; maintain consistent tick sources when instrumenting or porting to alternative hardware.
- **Architecture Variants**: ARM pathway reroutes vector tables, leverages banked registers, and modifies syscall/exception entry; highlight these deltas when adapting tooling or diagrams beyond x86.

---

## 5. Module Operating Manuals

### 5.1 CPU Interface Module (`modules/cpu-interface`)
- **Deliverables**: Diagram suite (`CPU-INTERFACE-DIAGRAMS-COMPLETE.md`), module README, docs mirroring root analysis.
- **Build Path**: `make cpu` (compiles LaTeX, updates diagrams); ensure LaTeX imports shared styles via relative paths (`../../shared/styles/minix-styles`).
- **Data Sources**: `analysis/` outputs, benchmarks from `benchmarks/`, wiki extracts.
- **Quality Bar**: Validate architecture assumptions against MINIX source tree at `$MINIX_ROOT/minix/kernel/arch/i386`.

### 5.2 Boot Sequence Module (`modules/boot-sequence`)
- **Deliverables**: Boot whitepaper (`docs/FINAL_SYNTHESIS_REPORT.md`), quick-start guide, TikZ boot diagrams (`diagrams/tikz/MINIX-BOOT-SEQUENCE-COMPLETE-GUIDE.md`).
- **Build Path**: `make boot`; confirm module README references umbrella structure (per roadmap ALPHA tasks).
- **Trace Discipline**: Keep seven-phase structure intact; update CPU state tables whenever kernel commit changes control flow.

### 5.3 Shared Infrastructure (`shared/`)
- **Styles**: Manage `minix-colors.sty`, `minix-arxiv.sty`; follow *shared/styles/STYLE-GUIDE.md* for naming and palette governance.
- **MCP Servers**: Document capabilities in *CAPABILITIES-AND-TOOLS.md*; align CLI feature flags with server handlers.
  - Shared code lives under `shared/mcp/server/` (`MinixDataLoader`, `MinixAnalysisServer`), providing data accessors for both CPU and boot endpoints. Extend or wrap this module when adding transport layers.
- **Pipelines**: Centralize Python/Bash helpers; modules should import rather than duplicate (flag duplication in roadmap DELTA audits).

### 5.4 Formal Models & Benchmarking
- **Formal Verification**: *formal-models/PHASE-2B-FORMAL-VERIFICATION-FRAMEWORK.md* defines model scope; track specification coverage and proof status here.
- **Benchmark Framework**: Use *benchmarks/PHASE-2C-PERFORMANCE-BENCHMARKING-FRAMEWORK.md* to structure experiments; deposit JSON results in `analysis-results/benchmarks/`.

### 5.5 Whitepapers & Publications
- `whitepapers/*.md` provide thematic rationale; align with module outputs.
- *WHITEPAPER-COMPLETION-REPORT.md* and *WHITEPAPER-SUITE-COMPLETE.md* enumerate deliverables; use them as closure checklists when updating latex manuscripts under `modules/*/latex/`.

---

## 6. Operational Runbooks & Checklists

### 6.1 Migration & Harmonization Tasks (*MIGRATION-PLAN.md*, *MIGRATION-PROGRESS.md*)
1. Rename legacy repo to `minix-analysis`; confirm Tier directories exist.
2. Relocate LaTeX styles to `shared/styles/`; create color/arXiv packages; update module imports.
3. Move MCP servers into `shared/mcp/`; adjust import paths.
4. Refresh module READMEs to reference umbrella architecture.
5. Verify pipelines and tests post-move (`test_pipeline.sh`, targeted `pytest` runs).

### 6.2 Pipeline Execution (*PIPELINE-VALIDATION-COMPLETE.md*, *DATA-DRIVEN-DOCUMENTATION.md*)
1. Ensure `$MINIX_ROOT` points to `/home/eirikr/Playground/minix`.
2. Run `make pipeline` for full extraction → TikZ flow; capture runtime metrics in `logs/`.
3. For targeted CLI use, run `python -m os_analysis_toolkit.cli --source $MINIX_ROOT --output analysis-results/<name> [--parallel --workers 8]`.
4. Post-run, sync diagrams and docs; update relevant sections in this atlas and module docs.
5. **Data-Driven Diagram Stack**:
   - `minix_source_analyzer.py` parses 91 kernel files (19,659 LOC) and emits JSON (`kernel_structure.json`, `process_table.json`, `memory_layout.json`, `ipc_system.json`, `boot_sequence.json`, `statistics.json`).
   - `tikz_generator.py` transforms JSON into TikZ assets (`syscall-table`, `process-states`, `boot-sequence-data`, `ipc-architecture`, `memory-regions`) compiled via `pdflatex` into vector graphics.
   - Machine-readable outputs live in `diagrams/data/` and `diagrams/tikz-generated/`, ensuring every visual is traceable back to source analysis.

### 6.3 Release & Integration (*FINAL-INTEGRATION-COMPLETE.md*, *FINAL-COMPLETE-ACHIEVEMENT.md*)
1. Execute full build matrix: `make pipeline`, `make cpu`, `make boot`, `pytest`, `pytest -m benchmark`.
2. Refresh coverage (`pytest --cov-report=html`) and confirm `htmlcov/` published.
3. Generate whitepapers/arXiv packages via `scripts/create-arxiv-package.sh <module>`.
4. Update executive summaries and roadmap documents with release outcomes.
5. Tag release after ensuring documentation, diagrams, and MCP endpoints align.

---

## 7. Tooling, Automation & Environment

- **Make Targets** (*README.md*, *AGENTS.md*):
  - `make help` – discover curated commands.
  - `make pipeline` – E2E analysis.
  - `make cpu`, `make boot` – module-specific LaTeX builds.
- **Python CLI** (*CAPABILITIES-AND-TOOLS.md*, *CLAUDE.md*):
  - `python -m os_analysis_toolkit.cli --source <path> --output <dir> [--parallel --workers 8]`.
  - Ensure CLI flags align with documented capabilities (dashboard generation, trace extraction).
  - Data queries: `python -m os_analysis_toolkit.cli --list-resources`, `--resource <name>` (with optional `--boot-aspect`) and `--syscall <name>` now surface pipeline JSON via the shared MCP server layer (`--data-dir` override available).
  - Summaries: `--kernel-summary [--top-syscalls N]` emits top syscall stats, while `--boot-critical-path` prints the critical boot sequence timeline—ideal for quick status reports.
- **Analysis Toolchain** (*ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md*, *DATA-DRIVEN-DOCUMENTATION.md*):
  - `analyze_syscalls.py` – extracts and scores 46 kernel syscalls, exporting JSON for dashboards.
  - `analyze_ipc.py` – documents message layouts, grants, and endpoint usage patterns.
  - `generate_tikz_diagrams.py` / `tikz_generator.py` – convert structured data into LaTeX/TikZ for publication-ready diagrams.
  - `analyze_arm.py` – surfaces ARM-specific code paths, privilege transitions, and syscall differences.
  - `modules/cpu-interface/pipeline/run_cpu_analysis.sh` – CLI wrapper for CPU-focused runs (`MINIX_ROOT`, `OUTPUT_DIR`, `WORKERS` aware).
  - `modules/cpu-interface/pipeline/render_syscall_summary.py` – summarises `kernel_structure.json` into concise syscall counts/top lists for dashboards.
- **Environment** (*INSTALLATION.md*, *VERSION-VERIFICATION.md*):
  - Python 3.13, `pip install -r requirements.txt`.
  - LaTeX toolchain (TeX Live 2023) for publication parity.
  - Graphviz, `ctags`, `rg` for pipeline utilities.
- **Agents & Automation** (*AGENTS.md*, *CLAUDE.md*):
  - Install `pre-commit` hooks; enforce `black`, `flake8`, `mypy`.
  - Agents must respect sandbox paths and update logs/tests transparently.

---

## 8. Testing, Benchmarking & Quality Gates

- **Pytest Strategy** (*AGENTS.md*, *PROFESSIONAL-TEST-SUITE-COMPLETE.md*, *TESTING-SUMMARY.md*):
  - Default command: `pytest`.
  - Rapid iterations: `pytest -m "not slow"`.
  - Benchmarking: `pytest -m benchmark` with outputs archived in `analysis-results/benchmarks/`.
  - Integration with MINIX source: mark tests requiring actual MINIX checkout as `requires_minix`.
  - Module-specific smoke tests: `pytest tests/modules/test_cpu_pipeline.py` validates CPU pipeline helpers (uses benchmark fixture due to global `--benchmark-only` configuration).
- **Coverage Discipline**:
  - Run `pytest --cov-report=html`; ensure `htmlcov/index.html` reflects new results.
  - Update coverage thresholds and highlight deltas in *TESTING-SUMMARY.md*.
- **Pipeline Validation**:
  - Keep `test_pipeline.sh` and `test_complete_pipeline.py` executable and up-to-date.
  - When pipelines change, refresh *PIPELINE-VALIDATION-COMPLETE.md* with run metadata.
- **Performance Baselines** (*benchmarks/PHASE-2C-PERFORMANCE-BENCHMARKING-FRAMEWORK.md*):
  - Capture `min`, `max`, `stddev`, commit hash, tool versions.
  - Document anomalies and mitigations in this atlas and benchmarking framework doc.

---

## 9. Documentation, Publication & Knowledge Sharing

- **Writing Standards** (*AGENTS.md*, *DATA-DRIVEN-DOCUMENTATION.md*):
  - Use concise docstrings and PEP 484 type hints in code.
  - Maintain narrative structure: executive summary → context → deep dive → references (mirroring *COMPREHENSIVE-BOOT-RUNTIME-TRACE.md*).
  - For diagrams, follow `_report` / `_diagram` suffix conventions.
- **Wiki & Onboarding**:
  - Update `wiki/Home.md`, `wiki/boot-sequence/Overview.md`, `wiki/style-guide/Overview.md` after major changes.
  - Reflect new tutorials or guides in `docs/overview.md`, `docs/index.md`.
- **ArXiv Standards** (*ARXIV-STANDARDS.md*):
  - TeX Live 2023 compliance, root-level `main.tex`, sanitized filenames.
  - Include `.bbl`, not `.bib`; convert EPS to PDF; verify `pdflatex` logs clean.
  - Provide submission README noting compilation steps.
- **Whitepaper Suite** (*WHITEPAPER-COMPLETION-REPORT.md*, *WHITEPAPER-SUITE-COMPLETE.md*):
  - Use shared styles, color palettes, and `minix-arxiv.sty`.
  - Sync narrative with diagrams and benchmark data; cross-reference figure filenames.
  - **Thematic Highlights**:
    - `whitepapers/01-WHY-MICROKERNEL-ARCHITECTURE.md` – articulates reliability/security rationale for MINIX’s microkernel split and the historical trade-offs vs monolithic kernels.
    - `whitepapers/02-WHY-PARALLEL-ANALYSIS-WORKS.md` – justifies multi-agent, multi-stage analysis pipelines for scale and verification depth.
    - `whitepapers/03-WHY-THIS-TESTING-STRATEGY.md` – defends the marker-driven pytest regimen, coverage expectations, and benchmarking cadence.
    - `whitepapers/04-WHY-PEDAGOGY-MATTERS.md` – frames the educational mission, from progressive disclosure to line-by-line commentary.
- **Pedagogical Layer** (*LIONS-STYLE-PEDAGOGICAL-FRAMEWORK.md*):
  - Embrace progressive disclosure—beginner-friendly walkthroughs leading into line-by-line commentary.
  - Maintain `LINE-BY-LINE-COMMENTARY-MAIN.md` for granular analysis; summarize major insights here.

---

## 10. Collaboration, Governance & Change Control

- **Commit Hygiene** (*AGENTS.md*):
  - Format: `<type>: <imperative>` (e.g., `docs: Harmonize boot trace narrative`).
  - Squash fixups prior to review; prefer rebasing to retain linear history.
- **Pull Requests** (*DELIVERY-SUMMARY.md*, *FINAL-INTEGRATION-COMPLETE.md*):
  - Include scope summary, affected modules, exact test commands with results, refreshed diagrams/screenshots.
  - Reference roadmap phase or issue IDs in the body.
- **Change Logging**:
  - Update strategic docs (*ULTRA-DETAILED-STRATEGIC-ROADMAP.md*, *MIGRATION-PROGRESS.md*, *INTEGRATION-SUMMARY.md*) when plans shift.
  - Note environment changes in *INSTALLATION.md* to preserve onboarding clarity.
- **Agent Coordination**:
  - Follow agent-specific guides (*CLAUDE.md*, *AGENTS.md*); log automation outputs under `logs/`.
  - When MCP endpoints evolve, refresh *CAPABILITIES-AND-TOOLS.md* and CLI help.

---

## 11. Forward Synthesis Planner

**Progress Recap**:
- Unified documentation landscape now centered on this atlas with metrics, technical doctrine, operational runbooks, and governance summarized from 60+ source files.
- CPU/boot trace dossiers, syscall catalogs, and data-driven diagram pipelines are fully harmonized; README and tooling references point at the atlas.
- Strategic roadmaps (Phase 0–4) captured with clear exit criteria; module manuals and QA practices consolidated for reproducibility.

**Near-Term Objectives (1–2 weeks)**:
- ✅ *Completed:* Removed module-level style duplicates, aligned LaTeX imports with `shared/styles/`, and refreshed CPU/boot module READMEs.
- ✅ *Completed:* Updated wiki landing page to point at this atlas and reflect current structure/navigation.
- ✅ *Completed:* Regenerated pipeline artifacts and reran `pytest` (plugin restored; suite executes with environment-guarded skips). Testing summaries updated.
- ✅ *Completed:* Catalogued standalone Markdown assets in `ARCHIVAL-CANDIDATES.md`, flagging root deliverables, whitepapers, module docs, and legacy items for Phase 4 cleanup decisions.

**Mid-Term Objectives (Phase 3–4 execution window)**:
- Consolidate MCP servers under `shared/mcp/`, update capability docs, and verify CLI parity with documented endpoints. *(See `PHASE-4-PREP.md` §2)*
- Extend automation to regenerate data-driven diagrams and syscall catalogs as part of `make pipeline`, producing signed artifacts for review. *(See `PHASE-4-PREP.md` §1 & §4)*
- Prepare publication bundles by aligning LaTeX manuscripts with `minix-arxiv.sty`, refreshing figure references, and staging arXiv submissions per *ARXIV-STANDARDS.md*. *(See `PHASE-4-PREP.md` §3)*
- Define regression test suites for benchmarks (baseline JSON + acceptance thresholds) to gate integration merges. *(See `PHASE-4-PREP.md` §4)*

**Long-Term Vision (Post Phase 4)**:
- Establish continuous synthesis cadence: every major change triggers atlas updates, wiki rebuilds, pipeline runs, and artifact snapshots.
- Develop onboarding curricula combining whitepapers, pedagogy guides, and interactive notebooks derived from the atlas.
- Explore automation for MCP knowledge surfacing (auto-generated cards, query summaries) to keep AI assistants aligned with the latest analysis.

Progress toward each objective should be checked into this planner with dates and owners; treat it as the active roadmap while legacy phase documents serve as historical context.

---

## 12. Source Document Concordance

| Source Markdown | Integrated Here | Contribution |
| ---------------- | --------------- | ------------ |
| *README.md*, *UMBRELLA-ARCHITECTURE.md* | §1, §3 | Repository architecture, mission charter |
| *MASTER-ANALYSIS-SYNTHESIS.md*, *PROJECT-SYNTHESIS.md* | §1, §2, §4 | Executive scope, phase deliverables, boot/process insights |
| *ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md*, *CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md* | §0, §4.2, §4.5 | Portfolio metrics, syscall/interrupt diagram insights, hardware comparisons |
| *PHASE-1/2/3/4* docs, *MIGRATION-PLAN.md*, *MIGRATION-PROGRESS.md* | §2, §5, §6 | Temporal roadmap, harmonization tasks |
| *ULTRA-DETAILED-STRATEGIC-ROADMAP.md* | §2, §10 | Strategic ladder, governance checkpoints |
| *BOOT-TO-KERNEL-TRACE.md*, *COMPREHENSIVE-BOOT-RUNTIME-TRACE.md* | §4.1 | Boot sequence phases, CPU state tables |
| *FORK-PROCESS-CREATION-TRACE.md*, *MINIX-SYSCALL-CATALOG.md* | §4.2 | Process lifecycle, syscall details |
| *MINIX-CPU-INTERFACE-ANALYSIS.md*, *MICROARCHITECTURE-DEEP-DIVE.md*, *ISA-LEVEL-ANALYSIS.md* | §4.4, §5.1 | CPU interface scope, memory hierarchy |
| *MINIX-ARM-ANALYSIS.md* | §1, §4.5 | ARM deviations |
| *AGENTS.md*, *CAPABILITIES-AND-TOOLS.md*, *CLAUDE.md* | §3, §7, §10 | Command suites, automation policies |
| *DATA-DRIVEN-DOCUMENTATION.md*, *TESTING-SUMMARY.md*, *PROFESSIONAL-TEST-SUITE-COMPLETE.md* | §6.2, §8, §9 | Pipeline validation, QA practices |
| *ARXIV-STANDARDS.md*, *WHITEPAPER-COMPLETION-REPORT.md*, *WHITEPAPER-SUITE-COMPLETE.md* | §9 | Publication standards |
| *LIONS-STYLE-PEDAGOGICAL-FRAMEWORK.md*, *LINE-BY-LINE-COMMENTARY-MAIN.md* | §9 | Pedagogical approach |
| *ARCHIVAL-CANDIDATES.md* | §11 | Document consolidation tracker |
| *PHASE-4-PREP.md* | §11, §2 | Phase 4 execution checklist |
| `modules/*/docs/*.md`, `whitepapers/*.md`, `wiki/*.md` | §3, §5, §9 | Surface-specific instructions |

---

## 13. Maintaining the Atlas

- Treat this document as the front door for contributors—update promptly after material changes.
- When legacy documents become outdated, either refresh them to match this atlas or mark them as archival with a pointer here.
- Relocate superseded Markdown into `archive/` (see `archive/README.md`) once their insights are captured here; track actions in `ARCHIVAL-CANDIDATES.md`.
- Before each major release or roadmap milestone, review this atlas to ensure every section reflects the current state of tooling, documentation, and strategy.

> **Canonical Rule**: This atlas supersedes fragmented guidance. When conflicts arise, reconcile the source material and resynthesize the outcome here so the project continues to operate from a single, harmonized playbook.
