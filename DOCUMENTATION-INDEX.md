# Complete Documentation Index
## minix-analysis Project

**Last Updated:** 2025-11-05  
**Total Documentation Files:** 339  
**Python Modules:** 71  
**GitHub Workflows:** 3

> **Navigation Tip:** Use Ctrl+F / Cmd+F to search this index quickly.

---

## Quick Start

**New to the project?** Start here:
1. [README.md](README.md) - Project overview and quick start
2. [REQUIREMENTS.md](REQUIREMENTS.md) - Installation and dependencies
3. [docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md](docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md) - NetBSD build environment
4. [docs/TEXPLOSION-QUICKSTART.md](docs/TEXPLOSION-QUICKSTART.md) - TeXplosion pipeline quick start

---

## Part I: Essential Documentation

### Core Project Documentation
- [README.md](README.md) - Project overview, architecture, quick start
- [REQUIREMENTS.md](REQUIREMENTS.md) - Complete dependency documentation
- [COMPREHENSIVE-REPOSITORY-AUDIT.md](COMPREHENSIVE-REPOSITORY-AUDIT.md) - Repository health assessment (82/100)
- [COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md](COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md) - Complete audit (339 docs, 71 Python files)

### Setup and Installation
- [REQUIREMENTS.md](REQUIREMENTS.md) - System requirements, Python packages, LaTeX, dependencies
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Installation procedures
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) - Setup completion summary

### Build Environments

#### NetBSD DevContainer (Primary Build Environment)
- [docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md](docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md) - Complete setup guide (11.5 KB)
- [docs/netbsd/NETBSD-IMAGES-RESEARCH.md](docs/netbsd/NETBSD-IMAGES-RESEARCH.md) - NetBSD 10.1 images and best practices (9.2 KB)
- [scripts/netbsd/README.md](scripts/netbsd/README.md) - NetBSD automation scripts

#### Docker and QEMU
- [docs/ISO_DOWNLOAD_WORKFLOW.md](docs/ISO_DOWNLOAD_WORKFLOW.md) - ISO acquisition workflow
- `.devcontainer/` - Complete DevContainer configuration

---

## Part II: CI/CD and Workflows

### TeXplosion Pipeline (Continuous Publication)
- [docs/TEXPLOSION-PIPELINE.md](docs/TEXPLOSION-PIPELINE.md) - Complete architecture guide
- [docs/TEXPLOSION-QUICKSTART.md](docs/TEXPLOSION-QUICKSTART.md) - Quick reference guide
- [docs/TEXPLOSION-FAQ.md](docs/TEXPLOSION-FAQ.md) - 50+ frequently asked questions
- [docs/TEXPLOSION-EXAMPLE.md](docs/TEXPLOSION-EXAMPLE.md) - End-to-end walkthrough
- [TEXPLOSION-SUMMARY.md](TEXPLOSION-SUMMARY.md) - Implementation summary
- `.github/workflows/texplosion-pages.yml` - Workflow definition

### GitHub Actions Workflows
1. **TeXplosion Pipeline** (`.github/workflows/texplosion-pages.yml`)
   - 5-stage LaTeX publication to GitHub Pages
   - Diagrams, MINIX build, LaTeX, pages, deploy
   
2. **Main CI/CD** (`.github/workflows/ci.yml`)
   - Lint, test, build validation
   - Dependency checking, documentation generation
   
3. **MINIX Build CI** (`.github/workflows/minix-ci.yml`)
   - QEMU environment, MINIX compilation
   - Boot testing, performance profiling

### CI/CD Documentation
- [CI-CD-VALIDATION-REPORT.md](CI-CD-VALIDATION-REPORT.md) - Production validation (92/100)
- [WORKFLOW_AUDIT_AND_SYNTHESIS.md](WORKFLOW_AUDIT_AND_SYNTHESIS.md) - Workflow analysis
- [INTEGRATION_TEST_REPORT.md](INTEGRATION_TEST_REPORT.md) - Integration testing

---

## Part III: Analysis and Profiling

### Analysis Tools Documentation

#### Source Code Analysis
- [docs/analysis/README.md](docs/analysis/README.md) - Analysis overview
- [docs/analysis/DATA-DRIVEN-APPROACH.md](docs/analysis/DATA-DRIVEN-APPROACH.md) - Data-driven methodology
- [docs/analysis/SYNTHESIS.md](docs/analysis/SYNTHESIS.md) - Analysis synthesis
- [docs/analysis/BOOT-SEQUENCE-ANALYSIS.md](docs/analysis/BOOT-SEQUENCE-ANALYSIS.md) - Boot sequence
- [docs/analysis/ERROR-ANALYSIS.md](docs/analysis/ERROR-ANALYSIS.md) - Error triage
- [docs/analysis/IPC-SYSTEM-ANALYSIS.md](docs/analysis/IPC-SYSTEM-ANALYSIS.md) - IPC analysis
- [docs/analysis/SYSCALL-ANALYSIS.md](docs/analysis/SYSCALL-ANALYSIS.md) - System calls

#### Boot Analysis
- [docs/boot-analysis/README.md](docs/boot-analysis/README.md) - Boot analysis overview
- [docs/boot-analysis/QUICK_START.md](docs/boot-analysis/QUICK_START.md) - Quick start guide
- [docs/boot-analysis/DEMO.md](docs/boot-analysis/DEMO.md) - Demo walkthrough
- [docs/boot-analysis/bsp_complete.md](docs/boot-analysis/bsp_complete.md) - BSP analysis
- [docs/boot-analysis/cstart_analysis.md](docs/boot-analysis/cstart_analysis.md) - cstart analysis
- [docs/boot-analysis/cstart_complete.md](docs/boot-analysis/cstart_complete.md) - cstart complete
- [docs/boot-analysis/kmain_complete.md](docs/boot-analysis/kmain_complete.md) - kmain analysis
- [docs/boot-analysis/proc_init_analysis.md](docs/boot-analysis/proc_init_analysis.md) - Process init
- [docs/boot-analysis/FINAL_SYNTHESIS_REPORT.md](docs/boot-analysis/FINAL_SYNTHESIS_REPORT.md) - Final synthesis
- [docs/boot-analysis/ULTIMATE_SYNTHESIS_COMPLETE.md](docs/boot-analysis/ULTIMATE_SYNTHESIS_COMPLETE.md) - Ultimate synthesis
- [docs/boot-analysis/ULTRA_DENSE_COMPLETION_REPORT.md](docs/boot-analysis/ULTRA_DENSE_COMPLETION_REPORT.md) - Completion report
- [docs/boot-analysis/ARXIV_WHITEPAPER_COMPLETE.md](docs/boot-analysis/ARXIV_WHITEPAPER_COMPLETE.md) - ArXiv whitepaper

#### Performance Analysis
- [docs/performance/README.md](docs/performance/README.md) - Performance overview
- [docs/performance/COMPREHENSIVE-PROFILING-GUIDE.md](docs/performance/COMPREHENSIVE-PROFILING-GUIDE.md) - Complete guide
- [docs/performance/BOOT-PROFILING-RESULTS.md](docs/performance/BOOT-PROFILING-RESULTS.md) - Boot profiling data
- [docs/performance/CPU-UTILIZATION-ANALYSIS.md](docs/performance/CPU-UTILIZATION-ANALYSIS.md) - CPU utilization
- [docs/performance/OPTIMIZATION-RECOMMENDATIONS.md](docs/performance/OPTIMIZATION-RECOMMENDATIONS.md) - Optimization tips

### Architecture Documentation
- [docs/architecture/README.md](docs/architecture/README.md) - Architecture overview
- [docs/architecture/MINIX-ARCHITECTURE-COMPLETE.md](docs/architecture/MINIX-ARCHITECTURE-COMPLETE.md) - Complete architecture
- [docs/architecture/BOOT-TIMELINE.md](docs/architecture/BOOT-TIMELINE.md) - Boot timeline
- [docs/architecture/CPU-INTERFACE-ANALYSIS.md](docs/architecture/CPU-INTERFACE-ANALYSIS.md) - CPU interface
- [docs/architecture/MEMORY-LAYOUT-ANALYSIS.md](docs/architecture/MEMORY-LAYOUT-ANALYSIS.md) - Memory layout

---

## Part IV: Testing and Quality Assurance

### Testing Framework
- [docs/testing/README.md](docs/testing/README.md) - Complete testing guide (11 KB)
  - Test categories: unit, integration, benchmark, property-based
  - Coverage requirements (target: 80%)
  - CI/CD integration
  - Best practices and troubleshooting
- `pytest.ini` - Pytest configuration
- `tests/` - Test suite (67 tests, 45 passing)

### Quality Automation
- [docs/quality/PRE-COMMIT.md](docs/quality/PRE-COMMIT.md) - Pre-commit hooks guide (5.9 KB)
- `.pre-commit-config.yaml` - 15+ automated quality checks
- `.yamllint` - YAML linting configuration
- `.bandit` - Security scanning configuration
- `scripts/validate-build.py` - Build validation (24/26 checks)
- `scripts/validate-texplosion-setup.py` - TeXplosion validation

### Audit Reports
- [docs/audits/README.md](docs/audits/README.md) - Audit overview
- [docs/audits/COMPREHENSIVE-AUDIT-REPORT.md](docs/audits/COMPREHENSIVE-AUDIT-REPORT.md) - Full audit
- [docs/audits/QUALITY-METRICS.md](docs/audits/QUALITY-METRICS.md) - Quality metrics
- [docs/audits/COMPLETENESS-CHECKLIST.md](docs/audits/COMPLETENESS-CHECKLIST.md) - Completeness check
- [docs/audits/ARCHIVAL-CANDIDATES.md](docs/audits/ARCHIVAL-CANDIDATES.md) - Archive candidates

---

## Part V: Examples and Guides

### Example Documentation
- [docs/examples/README.md](docs/examples/README.md) - Examples overview
- [docs/examples/INDEX.md](docs/examples/INDEX.md) - Examples index
- [docs/examples/CLI-EXECUTION-GUIDE.md](docs/examples/CLI-EXECUTION-GUIDE.md) - CLI usage
- [docs/examples/MCP-INTEGRATION-GUIDE.md](docs/examples/MCP-INTEGRATION-GUIDE.md) - MCP integration
- [docs/examples/MCP-QUICK-START.md](docs/examples/MCP-QUICK-START.md) - MCP quick start
- [docs/examples/PROFILING-QUICK-START.md](docs/examples/PROFILING-QUICK-START.md) - Profiling quick start
- [docs/examples/PROFILING-ENHANCEMENT-GUIDE.md](docs/examples/PROFILING-ENHANCEMENT-GUIDE.md) - Profiling enhancement
- [docs/examples/RUNTIME-SETUP-GUIDE.md](docs/examples/RUNTIME-SETUP-GUIDE.md) - Runtime setup
- [docs/examples/ORGANIZATION-STATUS-REPORT.md](docs/examples/ORGANIZATION-STATUS-REPORT.md) - Organization status

---

## Part VI: Standards and Best Practices

### Standards Documentation
- [docs/standards/README.md](docs/standards/README.md) - Standards overview
- [docs/standards/BEST-PRACTICES.md](docs/standards/BEST-PRACTICES.md) - Best practices
- [docs/standards/PEDAGOGICAL-FRAMEWORK.md](docs/standards/PEDAGOGICAL-FRAMEWORK.md) - Pedagogical framework
- [docs/standards/ARXIV-STANDARDS.md](docs/standards/ARXIV-STANDARDS.md) - ArXiv standards
- [docs/standards/LIONS-STYLE-WHITEPAPER-INTEGRATION.md](docs/standards/LIONS-STYLE-WHITEPAPER-INTEGRATION.md) - Lions style integration
- [docs/standards/LIONS-WHITEPAPER-DIAGRAM-TECHNIQUES.md](docs/standards/LIONS-WHITEPAPER-DIAGRAM-TECHNIQUES.md) - Diagram techniques
- [BEST_PRACTICES_AND_LESSONS.md](BEST_PRACTICES_AND_LESSONS.md) - Lessons learned

---

## Part VII: Planning and Roadmaps

### Planning Documentation
- [docs/planning/README.md](docs/planning/README.md) - Planning overview
- [docs/planning/ROADMAP.md](docs/planning/ROADMAP.md) - Project roadmap
- [docs/planning/MIGRATION-PLAN.md](docs/planning/MIGRATION-PLAN.md) - Migration plan
- [PHASE_4_ROADMAP_v0.2.0.md](PHASE_4_ROADMAP_v0.2.0.md) - Phase 4 roadmap

### Phase Documentation
- [docs/PHASE-3-COMPREHENSIVE-SUMMARY.md](docs/PHASE-3-COMPREHENSIVE-SUMMARY.md)
- [docs/PHASE-3E-WEEK-1-PLAN.md](docs/PHASE-3E-WEEK-1-PLAN.md)
- [docs/PHASE-3E-WEEK-1-REPORT.md](docs/PHASE-3E-WEEK-1-REPORT.md)
- [docs/PHASE-3E-WEEK-1-MONDAY-EXAMINATION.md](docs/PHASE-3E-WEEK-1-MONDAY-EXAMINATION.md)
- [docs/PHASE-3E-WEEK-1-TUESDAY-CONTEXT.md](docs/PHASE-3E-WEEK-1-TUESDAY-CONTEXT.md)
- [docs/PHASE-3E-WEEK-1-WEDNESDAY-GAPS.md](docs/PHASE-3E-WEEK-1-WEDNESDAY-GAPS.md)
- [docs/PHASE-3E-WEEK-1-THURSDAY-SKETCHES.md](docs/PHASE-3E-WEEK-1-THURSDAY-SKETCHES.md)
- [docs/PHASE-3F-COMPLETION-REPORT.md](docs/PHASE-3F-COMPLETION-REPORT.md)
- [docs/PHASE-4-PUBLICATION-PLAN.md](docs/PHASE-4-PUBLICATION-PLAN.md)
- [docs/PHASE-5-PILOTS-EXPANSION-PLAN.md](docs/PHASE-5-PILOTS-EXPANSION-PLAN.md)

---

## Part VIII: Agent and MCP Documentation

### Agent Instructions
- [docs/AGENTS.md](docs/AGENTS.md) - Agent coordination guidelines
- [docs/CLAUDE.md](docs/CLAUDE.md) - Claude-specific instructions (comprehensive, 300+ lines)
- [GEMINI.md](GEMINI.md) - Gemini operational log and analysis

### MCP (Model Context Protocol)
- [docs/mcp/README.md](docs/mcp/README.md) - MCP overview
- [docs/mcp/MCP-REFERENCE.md](docs/mcp/MCP-REFERENCE.md) - MCP reference
- [docs/MINIX-MCP-Integration.md](docs/MINIX-MCP-Integration.md) - MINIX MCP integration

### Operations Documentation
- [docs/operations/INDEX.md](docs/operations/INDEX.md) - Operations index

---

## Part IX: Whitepaper and Publication

### Whitepaper Documentation
- [docs/WHITEPAPER-VISION.md](docs/WHITEPAPER-VISION.md) - Whitepaper vision
- [docs/LIONS-PEDAGOGY-RESEARCH.md](docs/LIONS-PEDAGOGY-RESEARCH.md) - Lions pedagogy research
- `whitepaper/` - LaTeX whitepaper source
  - `chapters/` - Individual chapters
  - `figures-export/` - Exported figures
  - `src/` - LaTeX source files

### ArXiv Submission
- `scripts/create-arxiv-package.sh` - ArXiv packaging script (250+ lines)
- `arxiv-submission/` - ArXiv submission directory

---

## Part X: Historical and Archived Documentation

### Completion Reports
- [PROJECT_COMPLETION_SUMMARY.md](PROJECT_COMPLETION_SUMMARY.md)
- [SESSION-PHASE-3-FINAL-SUMMARY.md](SESSION-PHASE-3-FINAL-SUMMARY.md)
- [SESSION-SUMMARY-2025-11-01.md](SESSION-SUMMARY-2025-11-01.md)
- [GITHUB_PUSH_COMPLETION.md](GITHUB_PUSH_COMPLETION.md)
- [RECONCILIATION_REPORT.md](RECONCILIATION_REPORT.md)
- [SYNC_AND_RELEASE_SUMMARY.md](SYNC_AND_RELEASE_SUMMARY.md)

### Release Documentation
- [RELEASE_NOTES_v0.1.0.md](RELEASE_NOTES_v0.1.0.md)

### Archive (251 files)
- [archive/README.md](archive/README.md) - Archive index
- `archive/phase-reports/` - Phase completion reports (40 files)
- `archive/integration-reports/` - Integration reports (6 files)
- `archive/reference-materials/` - Reference materials (17 files)
- `archive/deprecated/mcp/` - Deprecated MCP docs (10 files)
- `archive/completion-reports/` - Historical completion reports (~100 files)
- `archive/misc/` - Miscellaneous archived content (~78 files)

---

## Part XI: Python Module Documentation

### Core Analysis Tools
- `tools/minix_source_analyzer.py` - Source code analysis
- `tools/isa_instruction_extractor.py` - ISA extraction
- `tools/analyze_syscalls.py` - System call analysis
- `tools/tikz_generator.py` - TikZ diagram generation
- `tools/triage-minix-errors.py` - Error triage
- `tools/analyze_arm.py` - ARM analysis

### Profiling Tools
- `tools/profiling/parse_perf_data.py` - Performance data parsing
- `tools/boot-analysis/` - Boot analysis tools
- `measurements/phase-7-5-boot-profiler-granular.py` - Granular profiler
- `measurements/phase-7-5-boot-profiler-optimized.py` - Optimized profiler
- `measurements/phase-7-5-boot-profiler-timing.py` - Timing profiler
- `measurements/phase-7-5-iso-boot-profiler.py` - ISO boot profiler

### Testing Tools
- `tools/testing/qemu_runner.py` - QEMU test runner
- `tools/testing/test_harness.py` - Test harness

### MCP Servers
- `mcp/servers/boot-profiler/server.py` - Boot profiler MCP server
- `mcp/servers/memory-monitor/server.py` - Memory monitor MCP server
- `mcp/servers/syscall-tracer/server.py` - Syscall tracer MCP server

### Analysis Modules
- `analysis/generators/tikz_converter.py` - TikZ converter
- `analysis/graphs/call_graph.py` - Call graph generator
- `analysis/parsers/symbol_extractor.py` - Symbol extractor

### Source Code Packages
- `src/minix_transport/` - MCP transport layer
- `src/os_analysis_toolkit/` - OS analysis toolkit

---

## Part XII: Additional Resources

### Wiki Documentation
- `wiki/api/` - API documentation
- `wiki/architecture/` - Architecture documentation
- `wiki/boot-sequence/` - Boot sequence documentation
- `wiki/build-system/` - Build system documentation
- `wiki/style-guide/` - Style guides

### Other Documentation
- [docs/INDEX.md](docs/INDEX.md) - Documentation index
- [docs/index.md](docs/index.md) - Index (lowercase)
- [docs/features.md](docs/features.md) - Features documentation
- [docs/gap_analysis.md](docs/gap_analysis.md) - Gap analysis
- [docs/minix_file_map.md](docs/minix_file_map.md) - MINIX file map
- [docs/overview.md](docs/overview.md) - Overview
- [docs/MINIX-Error-Registry.md](docs/MINIX-Error-Registry.md) - Error registry

---

## Quick Reference by Use Case

### "I want to build MINIX natively"
→ [docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md](docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md)

### "I want to analyze MINIX source code"
→ [docs/analysis/README.md](docs/analysis/README.md)

### "I want to profile MINIX boot performance"
→ [docs/performance/COMPREHENSIVE-PROFILING-GUIDE.md](docs/performance/COMPREHENSIVE-PROFILING-GUIDE.md)

### "I want to generate LaTeX documentation"
→ [docs/TEXPLOSION-QUICKSTART.md](docs/TEXPLOSION-QUICKSTART.md)

### "I want to run the test suite"
→ [docs/testing/README.md](docs/testing/README.md)

### "I want to contribute code"
→ [docs/CLAUDE.md](docs/CLAUDE.md) + [docs/quality/PRE-COMMIT.md](docs/quality/PRE-COMMIT.md)

### "I want to understand the architecture"
→ [docs/architecture/MINIX-ARCHITECTURE-COMPLETE.md](docs/architecture/MINIX-ARCHITECTURE-COMPLETE.md)

### "I want to fix CI/CD issues"
→ [CI-CD-VALIDATION-REPORT.md](CI-CD-VALIDATION-REPORT.md)

---

## Statistics

### Documentation Coverage
- **Total Markdown Files:** 339
- **Active Documentation:** ~120 files
- **Archived Documentation:** ~219 files
- **Root-Level Docs:** 18 files
- **docs/ Directory:** 88 files

### Code Coverage
- **Python Files:** 71
- **Analysis Tools:** 9 files
- **Tests:** 11 files
- **MCP Servers:** 3 files
- **Scripts:** 3 files

### Workflow Coverage
- **GitHub Actions:** 3 workflows
- **Pre-commit Hooks:** 15+ checks
- **Build Validations:** 24/26 passing

---

## Maintenance

**Document Owner:** Repository maintainers  
**Update Frequency:** Monthly or after major changes  
**Last Audit:** 2025-11-05  
**Next Audit:** 2025-12-05

**To update this index:**
```bash
# Run comprehensive audit
python3 scripts/audit-documentation.py

# Update this file
vim DOCUMENTATION-INDEX.md

# Commit changes
git commit -am "Update documentation index"
```

---

**Related Documentation:**
- [COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md](COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md) - Complete repository audit
- [COMPREHENSIVE-REPOSITORY-AUDIT.md](COMPREHENSIVE-REPOSITORY-AUDIT.md) - Repository health assessment
- [README.md](README.md) - Project overview

*AD ASTRA PER MATHEMATICA ET SCIENTIAM*
