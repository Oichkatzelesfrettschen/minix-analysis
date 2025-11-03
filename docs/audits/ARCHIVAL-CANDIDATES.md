# Archival Candidates and Deprecation Guide

**Status:** Consolidated reference document (Phase 2B)
**Date:** November 1, 2025
**Scope:** Living checklist for file consolidation, archival decisions, and deprecation management
**Audience:** Documentation managers, project architects, maintainers

---

## Executive Summary

This document provides a systematic approach to managing legacy documentation, deprecated components, and consolidation decisions as the MINIX analysis project evolves. It serves as the authoritative reference for:

1. **File Status Tracking**: Which files are active, retained, archived, or deprecated
2. **Consolidation Decisions**: Rationale for merging, retaining, or archiving files
3. **Migration Timeline**: When files should be evaluated and moved
4. **Stakeholder Communication**: Clear guidance on file lifecycle management

This is a **living document** - update as files are consolidated, archived, or new patterns emerge.

---

## Table of Contents

1. [Root-Level Deliverables](#root-level-deliverables)
2. [Module Documentation](#module-documentation)
3. [Thematic Whitepapers](#thematic-whitepapers)
4. [Support Infrastructure](#support-infrastructure)
5. [Phase-Specific Files](#phase-specific-files)
6. [Analysis and Research](#analysis-and-research)
7. [Legacy and Miscellaneous](#legacy-and-miscellaneous)
8. [Archival Process](#archival-process)
9. [Status Legend](#status-legend)
10. [Next Review Cycle](#next-review-cycle)

---

## Root-Level Deliverables

### Executive Summaries and Release Artifacts

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md` | Executive snapshot of Phase 1 outputs | ✔ Active | Retain; cross-link from docs/INDEX.md | Ongoing |
| `FINAL-INTEGRATION-COMPLETE.md` | Release artifact for final review | 🔄 Evaluate | Archive after Phase 4 release notes finalized | Phase 4 |
| `FINAL-COMPLETE-ACHIEVEMENT.md` | Achievement summary document | 🔄 Evaluate | Archive after Phase 4 release notes finalized | Phase 4 |
| `DELIVERY-SUMMARY.md` | Project delivery status | 🔄 Evaluate | Archive after Phase 4 release notes finalized | Phase 4 |

**Rationale**:
- Executive summaries provide quick reference for project status
- Release artifacts become historical once publication is complete
- Phase 4 release notes will supersede individual achievement documents
- Retain brief summaries, archive verbose phase-specific narratives

### Planning and Migration Documents

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `MIGRATION-PLAN.md` | Phases 1-7 systematic roadmap | ✔ Active | Retain as historical reference; keep updated | Ongoing |
| `MIGRATION-PROGRESS.md` | Running log of migration execution | ✔ Active | Keep synced; archive old entries monthly | Ongoing |
| `PHASE-2B-PROGRESS-REPORT.md` | Detailed Phase 2B tracking | ✔ Active | Retain during Phase 2B; archive at completion | Phase 2C |
| `PHASE-2B-DEDUPLICATION-MAPPING.md` | Strategic consolidation plan | ✔ Active | Retain as reference during consolidation | Phase 2C |

**Rationale**:
- Migration documents guide future work
- Progress reports valuable for understanding execution
- Archive completed phase reports as new phases begin
- Keep active planning documents current and accessible

### Synthesis and Integration Documents

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `PROJECT-SYNTHESIS.md` | Long-form synthesis predating atlas | ⚠ Evaluate | Verify unique analysis; fold into appendices if superseded | Phase 3 |
| `MASTER-ANALYSIS-SYNTHESIS.md` | Master integration document | ⚠ Evaluate | Verify unique insights; consolidate into docs/ structure | Phase 3 |

**Rationale**:
- Early synthesis documents may contain unique insights
- Some content will be superseded by consolidated docs/
- Extract and preserve genuinely novel analysis
- Archive bulk documents after extraction

---

## Module Documentation

### Module-Specific Directories

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `modules/boot-sequence/docs/*.md` | Boot sequence module documentation | ✔ Active | Keep synced with docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md | Ongoing |
| `modules/cpu-interface/docs/*.md` | CPU interface module documentation | ✔ Active | Keep synced with docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md | Ongoing |
| `modules/*/README.md` | Module quick-start guides | ✔ Active | Keep; ensure tone/style aligns with umbrella architecture | Ongoing |
| `modules/*/CHANGELOG.md` | Per-module change tracking | ✔ Active | Keep; maintain independently from root changelog | Ongoing |

**Rationale**:
- Module-local docs provide quick context for developers
- Mirror main docs in both locations to reduce navigation overhead
- Module READMEs are entry points for new contributors
- Changelog tracking at module level aids maintenance

### Module Implementation Files

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `modules/*/latex/*.tex` | LaTeX source for module content | ✔ Active | Retain; organize by theme (boot, cpu, etc.) | Ongoing |
| `modules/*/tests/` | Module-specific tests | ✔ Active | Create if missing; maintain alongside code | Ongoing |
| `modules/*/Makefile` | Per-module build automation | ✔ Active | Verify functionality; document targets | Ongoing |

**Rationale**:
- LaTeX documents are core research output
- Test infrastructure essential for quality
- Makefiles enable independent module building

---

## Thematic Whitepapers

### Pedagogical Essays and Frameworks

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `whitepapers/01-WHY-MICROKERNEL-ARCHITECTURE.md` | Foundational essay on microkernel design | ✔ Active | Retain; cross-link from docs/Standards/ | Ongoing |
| `whitepapers/02-MINIX-3-4-OVERVIEW.md` | MINIX 3.4 system overview | ✔ Active | Retain; reference from docs/INDEX.md | Ongoing |
| `whitepapers/*.md` | Other thematic pedagogical essays | ✔ Active | Retain in whitepapers/; reference from main docs | Ongoing |

**Rationale**:
- Thematic essays provide educational context
- Pedagogical framework essential for Lions-style commentary
- Retain all essays but organize with clear cross-references
- Consider converting to LaTeX chapters for final publication

### Publication Status Tracking

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `WHITEPAPER-COMPLETION-REPORT.md` | Publication readiness summary | 🔄 Evaluate | Collapse into single Phase 4 status document | Phase 4 |
| `WHITEPAPER-SUITE-COMPLETE.md` | Completion status tracker | 🔄 Evaluate | Merge into Phase 4 publication checklist | Phase 4 |
| `ARXIV-STANDARDS.md` | arXiv submission requirements | ✔ Active | Keep; reference during Phase 4 | Ongoing |

**Rationale**:
- Multiple status documents create confusion
- Phase 4 will have single authoritative status
- arXiv requirements remain constant; keep as reference
- Archive detailed completion reports after publication

---

## Support Infrastructure

### Build and Style System

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `shared/styles/*.sty` | LaTeX style packages (minix-styles, minix-colors, etc.) | ✔ Active | Retain; version control carefully | Ongoing |
| `shared/styles/*.md` | Style documentation | ✔ Active | Keep; ensure accuracy with .sty files | Ongoing |
| `shared/pipeline/` | Shared analysis tools | ✔ Active | Maintain; document dependencies | Ongoing |
| `shared/mcp/` | MCP server infrastructure | ✔ Active | Develop; integrate with modules | Ongoing |

**Rationale**:
- Shared infrastructure is core to project health
- Style consistency essential for publication
- Shared tools reduce duplication
- Maintain these as living components

### Wiki and Documentation Portals

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `wiki/*.md` | MkDocs documentation portal | 🔄 Evaluate | Update API/testing pages; remove outdated content | Phase 3 |
| `docs/INDEX.md` | Master documentation index | ✔ Active | Maintain as primary navigation hub | Ongoing |
| `docs/*/README.md` | Directory-level guides | ✔ Active | Create; help users navigate structure | Phase 2D |

**Rationale**:
- Wiki provides accessible documentation
- INDEX.md is authoritative starting point
- Directory READMEs guide exploration
- Systematically update as structure evolves

### Benchmark and Formal Verification

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `benchmarks/*.md` | Benchmark planning documents | ⚠ Evaluate | Verify accuracy post-Phase 4; archive outdated plans | Phase 4 |
| `benchmarks/*.py` | Benchmark implementation | ✔ Active | Maintain; integrate with CI/CD | Ongoing |
| `formal-models/*.tla+` | TLA+ specifications | ✔ Active | Maintain; document verification procedures | Ongoing |
| `formal-models/*.md` | Formal model documentation | ⚠ Evaluate | Confirm accuracy; update with results | Phase 4 |

**Rationale**:
- Benchmark code is active; documentation may be stale
- TLA+ specs require careful maintenance
- Archive old benchmark plans after results gathered
- Retain formal models as reference

### Publication Artifacts

| Path | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `arxiv-submissions/*.md` | arXiv submission packaging guides | ⚠ Evaluate | Fold into Phase 4 publication checklist | Phase 4 |
| `arxiv-submissions/` | Final arXiv package | ✔ Active | Create during Phase 4 | Phase 4 |

**Rationale**:
- arXiv guides provide reusable templates
- Final package lives in dedicated directory
- Archive submission iteration history

---

## Phase-Specific Files

### Phase Completion Reports

| File | Status | Action | Timeline |
|------|--------|--------|----------|
| `PHASE-1-COMPLETION-REPORT.md` | ✔ Historical | Archive to archive/phase-reports/ | Phase 2C |
| `PHASE-2-DOCUMENTATION-CONSOLIDATION-PLAN.md` | ✔ Historical | Archive to archive/phase-reports/ | Phase 2D |
| `PHASE-5-AUDIT-COMPLETION-SUMMARY.md` | ✔ Historical | Archive to archive/phase-reports/ | Phase 3 |
| `PHASE-7-5-DOCUMENTATION-INDEX-2025-11-01.md` | ✔ Historical | Archive to archive/phase-reports/ | Phase 3 |

**Archival Strategy**:
- Move completed phase reports to `archive/phase-reports/`
- Create `archive/phase-reports/README.md` explaining historical context
- Keep index of phase reports for reference
- Link to relevant phase reports from main docs

---

## Analysis and Research

### Audit Documents

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `COMPREHENSIVE-AUDIT.md` | Whitepaper verification + repository audit | ↗️ CONSOLIDATED | Moved to docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md | Phase 2B |
| `DEEP-AUDIT-REPORT.md` | Module structure assessment | ↗️ CONSOLIDATED | Merged into docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md | Phase 2B |
| `REPOSITORY-STRUCTURE-AUDIT.md` | Modularization strategy | ↗️ CONSOLIDATED | Merged into docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md | Phase 2B |

**Archival Schedule**:
1. **Phase 2B** (Current): Create consolidated docs/Audits/ documents
2. **Phase 2C**: Create redirect stubs at original locations
3. **Phase 3**: Move original files to archive/audits/deprecated/
4. **Phase 4**: Final cleanup and publication

### Analysis Indices

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `ANALYSIS-DOCUMENTATION-INDEX.md` | Analysis docs directory | ↗️ CONSOLIDATED | Merged into docs/Audits/QUALITY-METRICS.md | Phase 2B |
| `AUDIT-DOCUMENTS-INDEX.md` | Profiling audit index | ↗️ CONSOLIDATED | Merged into docs/Audits/QUALITY-METRICS.md | Phase 2B |

**Rationale**:
- Indices are navigation aids; consolidate with canonical references
- Quality metrics become authoritative reference
- Archive index files after consolidation

### Research Documents

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `INSTRUCTION-FREQUENCY-ANALYSIS.md` | Instruction frequency data | ↗️ CONSOLIDATED | Merged into docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md | Phase 2B |
| `PROFILING-AUDIT-EXECUTIVE-SUMMARY.md` | Performance measurement audit | ↗️ CONSOLIDATED | Merged into docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md | Phase 2B |
| Various other profiling/measurement docs | Performance analysis | ↗️ CONSOLIDATED | All merged into docs/Performance/ | Phase 2B |

---

## Legacy and Miscellaneous

### Legacy Pre-Umbrella Files

| File | Current Role | Status | Action | Timeline |
|------|--------------|--------|--------|----------|
| `archive/legacy/README-CPU-ANALYSIS-LEGACY.md` | Legacy README (pre-umbrella) | ✅ Archived | Keep in archive; reference only | N/A |
| Files in `archive/deprecated/` | Superseded components | ✅ Archived | Keep with explanatory README | N/A |

**Archival Structure**:
```
archive/
├── deprecated/
│   ├── README.md  # Explanation of deprecation
│   ├── phase-reports/
│   ├── old-tools/
│   └── obsolete-docs/
├── legacy/
│   ├── README.md  # Historical context
│   └── pre-umbrella-docs/
└── inactive-research/
    ├── README.md
    └── discontinued-projects/
```

### Environment and Build Artifacts

| Item | Status | Action |
|------|--------|--------|
| `venv/`, `.venv/` | Ignored (local environment) | Do not commit; add to .gitignore |
| `.pytest_cache/`, `.mypy_cache/` | Ignored (build cache) | Do not commit; add to .gitignore |
| `*.pyc`, `__pycache__/` | Ignored (compiled Python) | Do not commit; add to .gitignore |
| `build/`, `dist/`, `*.egg-info/` | Ignored (build outputs) | Do not commit; add to .gitignore |

**Rationale**:
- Environment artifacts are user-specific
- Cache files are regenerated
- Compiled objects unnecessary in git
- Keep .gitignore strict and comprehensive

---

## Archival Process

### Decision Tree

```
File Status → Active Consolidation?
              ↓
         YES → Consolidate into docs/
              ↓
              Move original → archive/with-stub
              ↓
              Update cross-references
              ↓
              (Complete)

         NO → Long-term Reference?
              ↓
         YES → Retain in root or docs/
              ↓
              Verify accuracy
              ↓
              Link from INDEX.md
              ↓
              Review quarterly
              ↓
              (Complete)

         NO → Phase-Specific?
              ↓
         YES → Move → archive/phase-reports/
              ↓
              Create explanatory README
              ↓
              Link from historical index
              ↓
              (Complete)

         NO → Delete or Archive?
              ↓
         Review with stakeholders
              ↓
              Decision on deletion vs. archival
              ↓
              Document decision
              ↓
              (Complete)
```

### Implementation Steps

**Step 1: Identify Candidates**
- Run audit to identify duplicates and superseded content
- Cross-reference with consolidation mapping
- Categorize by type (phase-specific, research, legacy, etc.)

**Step 2: Create Consolidated Versions**
- Read source files thoroughly
- Extract unique content
- Create consolidated document in new location
- Verify completeness against sources

**Step 3: Create Redirect Stubs**
- Leave minimal file at original location
- Explain where content moved
- Provide timestamp of move
- Include link to new location

**Step 4: Update Cross-References**
- Find all references to moved files
- Update links to point to new location
- Test links to verify they work
- Document changes

**Step 5: Move Original Files**
- Create archive/subdirectory for file type
- Move original file with redirect stub replaced
- Update .gitignore if needed
- Verify git history preserved

**Step 6: Archive Maintenance**
- Create archive/*/README.md explaining contents
- Keep .gitignore entries
- Link from main docs/INDEX.md for reference
- Schedule periodic review

### Archival Checklist

- [ ] Consolidation completed (if applicable)
- [ ] Unique content extracted
- [ ] Redundant content identified for removal
- [ ] New location created
- [ ] Cross-references identified
- [ ] Links updated
- [ ] Redirect stubs created (or file moved)
- [ ] Archive directory created
- [ ] README written for archive directory
- [ ] Git commit with clear message
- [ ] Stakeholder notification (if major change)
- [ ] Verification and testing completed

---

## Status Legend

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✔ | Active and current | Keep; maintain; refer regularly |
| 🔄 | Under evaluation | Decide during specified phase |
| ⚠ | Evaluate for archival | Verify content before archiving |
| ↗️ | Recently consolidated | Stub or move to archive pending |
| ✅ | Archived | Keep for reference; historical only |
| ➖ | Ignore (not tracked) | Outside version control scope |

---

## Next Review Cycle

### Review Schedule

**Frequency**: Monthly during active development, quarterly when stable

**Owner**: Documentation lead / Architecture team

**Process**:
1. Audit for new candidates (files added since last review)
2. Evaluate files in "🔄 Evaluate" status
3. Consolidate completed phase reports
4. Update this document with decisions
5. Execute archival for approved candidates
6. Report status in monthly meeting

### Phase-Based Reviews

| Phase | Review Focus | Timeline |
|-------|-------------|----------|
| Phase 2B | Consolidation progress | Weekly |
| Phase 2C | Synthesis and cross-references | Daily |
| Phase 2D | Final verification | Daily |
| Phase 3 | Pedagogical harmonization | Monthly |
| Phase 4 | Publication preparation | Monthly |

### Upcoming Decision Points

**Phase 2C (Synthesis)**:
- Final decision on FINAL-*.md files (archive or keep?)
- Evaluation of PROJECT-SYNTHESIS.md content (extract or archive?)
- Archive of completed phase reports

**Phase 3 (Pedagogy)**:
- Migration of whitepapers to LaTeX chapters (or keep as reference?)
- Consolidation of framework documents
- Archive of planning documents

**Phase 4 (Publication)**:
- Archive of benchmarking plans (post-results)
- Final status document consolidation
- Archival of submission guides
- Publication readiness checkpoint

---

## Related Documents

- [PHASE-2B-DEDUPLICATION-MAPPING.md](../PHASE-2B-DEDUPLICATION-MAPPING.md) - Strategic consolidation plan
- [PHASE-2B-PROGRESS-REPORT.md](../PHASE-2B-PROGRESS-REPORT.md) - Consolidation execution status
- [docs/INDEX.md](../docs/INDEX.md) - Master documentation index
- [MIGRATION-PLAN.md](../MIGRATION-PLAN.md) - Overall project roadmap

---

**Generated**: November 1, 2025
**Consolidated From**: ARCHIVAL-CANDIDATES.md
**Status**: Living document - update regularly as files are consolidated/archived
**Last Updated**: November 1, 2025
**Next Review**: November 8, 2025 (weekly during Phase 2B)
