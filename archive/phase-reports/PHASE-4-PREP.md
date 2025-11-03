# Phase 4 Preparation Playbook

**Objective**: Stage the repository for Phase 4 (“Integration & Release”) by front-loading the work required on pipelines, MCP consolidation, and publication deliverables. Treat this as an operational checklist; update progress in `MEGA-BEST-PRACTICES.md` as items close.

---

## 1. CPU Module Enhancements

| Task | Owner | Target | Notes |
| ---- | ----- | ------ | ----- |
| Populate `modules/cpu-interface/pipeline/` with reusable helpers | CPU module lead | Week 1 | ✅ Initial scripts added (`run_cpu_analysis.sh`, `render_syscall_summary.py`); extend with additional helpers as new needs emerge |
| Add pytest coverage under `modules/cpu-interface/tests/` | QA lead | Week 1 | ✅ Baseline tests in `tests/modules/test_cpu_pipeline.py`; expand once MINIX fixtures available |
| Define benchmark scenarios for syscall/context-switch metrics | Performance lead | Week 2 | Integrate with existing `analysis-results/benchmarks/` workflow |

---

## 2. MCP Consolidation

| Task | Owner | Target | Notes |
| ---- | ----- | ------ | ----- |
| Relocate per-module MCP code into `shared/mcp/` | MCP maintainer | Week 1 | 🚧 Shared loader/server scaffolding added under `shared/mcp/server`; next, hook into CLI/transport and remove module stubs |
| Update `CAPABILITIES-AND-TOOLS.md` and CLI help to match new endpoints | Docs lead | Week 1 | ✅ Documented shared layer + CLI commands in capabilities guide and atlas |
| Add regression tests for consolidated MCP server | QA lead | Week 2 | ✅ Initial unit + CLI smoke tests in `tests/modules/test_mcp_server.py`; extend with integration coverage post-transport |

---

## 3. Publication Readiness

| Task | Owner | Target | Notes |
| ---- | ----- | ------ | ----- |
| Validate LaTeX manuscripts against `minix-arxiv.sty` after recent style updates | Publications lead | Week 1 | Run `make cpu`, `make boot`, fix warnings |
| Refresh arXiv packaging scripts (`scripts/create-arxiv-package.sh`) | Build engineer | Week 2 | Ensure new diagrams/data included |
| Produce release notes that mirror atlas highlights | Docs lead | Week 2 | Derive from `MEGA-BEST-PRACTICES.md` §0–§2 |

---

## 4. Testing & Automation

| Task | Owner | Target | Notes |
| ---- | ----- | ------ | ----- |
| Determine which pytest skips can be lifted with MINIX fixtures | QA lead | Week 1 | Document prerequisites in `TESTING-SUMMARY.md` |
| Integrate pipeline run into CI (once available) | Automation lead | Week 2 | Capture artifacts as build outputs |
| Establish benchmark acceptance thresholds | Performance lead | Week 2 | Compare against historical JSON data |

---

## 5. Documentation Sync

| Task | Owner | Target | Notes |
| ---- | ----- | ------ | ----- |
| Cross-link new Phase 4 assets in `MEGA-BEST-PRACTICES.md` | Docs lead | Ongoing | Keep planner accurate |
| Update wiki navigation for new scripts/tests as they land | Wiki maintainer | Ongoing | Add how-to guides under `wiki/build-system` or module pages |
| Maintain `ARCHIVAL-CANDIDATES.md` with decisions | Documentation lead | Ongoing | Archive or merge legacy docs post Phase 4 |

---

## Tracking

- Use issue tracker / PR labels to map each table entry to actionable tasks.
- Update this playbook (or close it out) when Phase 4 completes; move residual items into Phase 5 planning documents.
