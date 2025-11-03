# Phase 2B: Deduplication and Consolidation Mapping

**Status:** Phase 2B Planning Complete
**Date:** November 1, 2025
**Scope:** Map all 117 root-level .md files to consolidation targets

---

## Executive Summary

The minix-analysis repository contains 117 .md files at root level plus additional files in subdirectories. This document provides a comprehensive mapping for consolidating duplicate and related content into a hierarchical docs/ structure.

**Key Findings:**
- 117 root-level .md files identified
- 25-30 clear status/completion duplicates (Priority 1 for consolidation)
- 15+ architecture documentation files (Priority 1 for consolidation)
- 10+ MCP-related files (Priority 1 for consolidation)
- 8+ performance/profiling files (Priority 1 for consolidation)
- 20+ Phase-specific status files (Priority 2 for archival)
- 11 Phase-7-5 specific files (Priority 3 for archival)

**Consolidation Timeline:** ~4-5 hours for complete Phase 2B execution

---

## Consolidation Groups

### GROUP 1: Status and Completion Files → docs/Planning/PHASE-COMPLETIONS.md

**Purpose:** Single canonical reference for all project phase completions
**Current Files:** 27 files
**Target Location:** docs/Planning/PHASE-COMPLETIONS.md
**Strategy:** Extract key information from each file and synthesize into unified completion report

Files to consolidate:
- PHASE-1-COMPLETE.md
- PHASE-1-COMPLETION-SUMMARY-2025-11-01.md
- PHASE-2-COMPLETE.md
- PHASE-2-COMPLETION-SUMMARY.md
- PHASE-3-COMPLETE.md
- PHASE-4-PREP.md
- PHASE-5-AUDIT-COMPLETION-SUMMARY.md
- PHASE-6-EXTENDED-WHITEPAPER-COMPLETION.md
- PHASE-7-COMPLETION-SUMMARY.md
- PHASE-7-SESSION-SUMMARY.md
- FINAL-COMPLETE-ACHIEVEMENT.md
- FINAL-INTEGRATION-COMPLETE.md
- INTEGRATION-COMPLETE.md
- INTEGRATION-PLAN.md
- INTEGRATION-SUMMARY.md
- COMPREHENSIVE-INTEGRATION-REPORT.md
- PROJECT-COMPLETION-SUMMARY.md
- PROJECT-SYNTHESIS.md
- PROJECT-SUMMARY.md
- COMPLETE-PROJECT-SYNTHESIS.md
- COMPLETE-REFACTORING-SUMMARY.md
- DELIVERY-SUMMARY.md
- WHITEPAPER-COMPLETION-REPORT.md
- WHITEPAPER-DELIVERY-SUMMARY.md
- WHITEPAPER-SUITE-COMPLETE.md
- WHITEPAPER-SYNTHESIS-COMPLETE.md
- ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md

**Action Items:**
1. Create docs/Planning/PHASE-COMPLETIONS.md combining key achievements from each
2. Create redirect stubs at original locations pointing to new canonical location
3. Preserve original files in archive/deprecated/phase-completions/ for reference

---

### GROUP 2: Architecture Documentation → docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md

**Purpose:** Comprehensive single-source architecture reference
**Current Files:** 8 files
**Target Location:** docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md
**Strategy:** Merge complementary sections, eliminate duplication, maintain comprehensive coverage

Files to consolidate:
- MINIX-ARCHITECTURE-SUMMARY.md
- MINIX-CPU-INTERFACE-ANALYSIS.md
- ISA-LEVEL-ANALYSIS.md
- MICROARCHITECTURE-DEEP-DIVE.md
- CPU-INTERFACE-DIAGRAMS-COMPLETE.md
- CPU-INTERFACE-DIAGRAMS-MASTER-SUMMARY.md
- MINIX-ARM-ANALYSIS.md
- UMBRELLA-ARCHITECTURE.md

**Merge Strategy:**
1. Use MINIX-ARCHITECTURE-SUMMARY.md as structural base
2. Add CPU interface details from MINIX-CPU-INTERFACE-ANALYSIS.md
3. Integrate ISA-level analysis from ISA-LEVEL-ANALYSIS.md
4. Add microarchitecture deep-dive content
5. Incorporate diagram descriptions and references
6. Add ARM-specific sections as subsections
7. Add umbrella architecture context as introduction

**Action Items:**
1. Create docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md
2. Ensure all diagram references are updated to new paths
3. Create cross-links to Performance/CPU-UTILIZATION-ANALYSIS.md for benchmarks
4. Archive originals to archive/deprecated/architecture/

---

### GROUP 3: Boot Sequence Analysis → docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md

**Purpose:** Comprehensive boot sequence documentation with traces
**Current Files:** 3 files
**Target Location:** docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md
**Strategy:** Merge boot traces, add fork/process creation details

Files to consolidate:
- BOOT-TO-KERNEL-TRACE.md
- COMPREHENSIVE-BOOT-RUNTIME-TRACE.md
- FORK-PROCESS-CREATION-TRACE.md

**Merge Strategy:**
1. Use COMPREHENSIVE-BOOT-RUNTIME-TRACE.md as base
2. Integrate BOOT-TO-KERNEL-TRACE.md for early boot phase details
3. Add FORK-PROCESS-CREATION-TRACE.md as subsection on process creation
4. Ensure timeline and step-by-step details are comprehensive
5. Cross-reference with whitepaper chapters (ch04-boot-metrics.tex)

**Action Items:**
1. Create docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md
2. Verify figure/diagram references are accurate
3. Archive originals to archive/deprecated/boot-analysis/

---

### GROUP 4: Pedagogical Framework → docs/Standards/PEDAGOGICAL-FRAMEWORK.md

**Purpose:** Lions-style commentary and pedagogical approach documentation
**Current Files:** 3 files
**Target Location:** docs/Standards/PEDAGOGICAL-FRAMEWORK.md
**Strategy:** Synthesize pedagogical philosophy with commentary examples

Files to consolidate:
- LIONS-STYLE-PEDAGOGICAL-FRAMEWORK.md
- LINE-BY-LINE-COMMENTARY-MAIN.md
- COMPREHENSIVE-PEDAGOGICAL-SYNTHESIS.md

**Merge Strategy:**
1. Use LIONS-STYLE-PEDAGOGICAL-FRAMEWORK.md as philosophy foundation
2. Add examples from LINE-BY-LINE-COMMENTARY-MAIN.md
3. Integrate synthesis insights from COMPREHENSIVE-PEDAGOGICAL-SYNTHESIS.md
4. Organize by topic: philosophy → principles → examples → synthesis
5. Add references to whitepaper chapters (ch08-education.tex)

**Action Items:**
1. Create docs/Standards/PEDAGOGICAL-FRAMEWORK.md
2. Add examples from actual whitepaper commentary
3. Archive originals to archive/deprecated/pedagogy/

---

### GROUP 5: Performance and Profiling → docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md

**Purpose:** Complete performance analysis and profiling methodology
**Current Files:** 9 files
**Target Location:** docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md
**Strategy:** Create unified performance reference with methodology, results, and analysis

Files to consolidate:
- INSTRUCTION-FREQUENCY-ANALYSIS.md
- COMPREHENSIVE-PROFILING-AUDIT-2025-11-01.md
- MEASUREMENT-GAP-ANALYSIS-COMPLETE-2025-11-01.md
- GRANULAR-PROFILING-EXPLANATION-2025-11-01.md
- PROFILING-AUDIT-EXECUTIVE-SUMMARY.md
- PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md
- PROFILING-IMPLEMENTATION-SUMMARY.md
- QEMU_OPTIMIZATION_SUMMARY.md
- QEMU_SIMULATION_ACCELERATION.md
- QEMU_TIMING_ARCHITECTURE_REPORT.md

**Merge Strategy:**
1. Use COMPREHENSIVE-PROFILING-AUDIT-2025-11-01.md as base
2. Add instruction frequency data from INSTRUCTION-FREQUENCY-ANALYSIS.md
3. Integrate gap analysis and enhancement guide
4. Add QEMU optimization and timing data as subsections
5. Organize by: methodology → measurements → analysis → optimization

**Action Items:**
1. Create docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md
2. Create separate docs/Performance/QEMU-OPTIMIZATION-GUIDE.md for QEMU-specific content
3. Archive originals to archive/deprecated/performance/

---

### GROUP 6: MCP Documentation → docs/MCP/MCP-REFERENCE.md

**Purpose:** Unified Model Context Protocol documentation and integration guide
**Current Files:** 9 files
**Target Location:** docs/MCP/MCP-REFERENCE.md
**Strategy:** Consolidate MCP status, troubleshooting, and integration guides

Files to consolidate:
- MCP-CRITICAL-DISCOVERY-REPORT.md
- MCP-DOCUMENTATION-INDEX.md
- MCP-EXECUTION-STATUS-2025-11-01.md
- MCP-QUICK-REFERENCE.md
- MCP-SESSION-SUMMARY-2025-11-01.md
- MCP-SUMMARY.md
- MCP-TROUBLESHOOTING-AND-FIXES.md
- MCP-VALIDATION-AND-READY-TO-TEST.md
- FINAL-MCP-STATUS.md

**Merge Strategy:**
1. Use MCP-QUICK-REFERENCE.md as structural base
2. Add critical discoveries and validation status
3. Integrate troubleshooting guide
4. Organize by: overview → setup → usage → troubleshooting → validation

**Action Items:**
1. Create docs/MCP/MCP-REFERENCE.md
2. Create docs/MCP/MCP-TROUBLESHOOTING.md (separate for clarity)
3. Create docs/MCP/MCP-VALIDATION-CHECKLIST.md
4. Archive originals to archive/deprecated/mcp/

---

### GROUP 7: Audit Reports → docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md

**Purpose:** Complete audit findings and quality metrics
**Current Files:** 6 files
**Target Location:** docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md
**Strategy:** Synthesize audit findings into single comprehensive report

Files to consolidate:
- COMPREHENSIVE-AUDIT.md
- DEEP-AUDIT-REPORT.md
- ANALYSIS-DOCUMENTATION-INDEX.md
- AUDIT-DOCUMENTS-INDEX.md
- REPOSITORY-STRUCTURE-AUDIT.md
- ARCHIVAL-CANDIDATES.md

**Merge Strategy:**
1. Use COMPREHENSIVE-AUDIT.md as structural base
2. Add deep-dive findings from DEEP-AUDIT-REPORT.md
3. Integrate repository structure analysis
4. Organize by: scope → findings → quality metrics → recommendations
5. Create archival section for deprecated/candidate files

**Action Items:**
1. Create docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md
2. Create docs/Audits/ARCHIVAL-CANDIDATES.md (separate for clarity)
3. Create docs/Audits/QUALITY-METRICS.md
4. Archive originals to archive/deprecated/audits/

---

### GROUP 8: Planning and Roadmaps → docs/Planning/ROADMAP.md

**Purpose:** Project roadmap and future direction planning
**Current Files:** 9 files
**Target Location:** docs/Planning/ROADMAP.md
**Strategy:** Consolidate roadmaps and planning documents into single vision

Files to consolidate:
- PHASE-2-COMPREHENSIVE-PLAN.md
- PHASE-3-ROADMAP.md
- PHASE-4-ROADMAP.md
- PHASE-4-MINIMAL-SCOPE.md
- ULTRA-DETAILED-STRATEGIC-ROADMAP.md
- MIGRATION-PLAN.md
- MIGRATION-PROGRESS.md
- PHASE-2-DOCUMENTATION-CONSOLIDATION-PLAN.md
- PHASE-7-5-EXECUTION-PLAN.md

**Merge Strategy:**
1. Use ULTRA-DETAILED-STRATEGIC-ROADMAP.md as base framework
2. Add phase-specific roadmaps as subsections
3. Integrate migration planning
4. Organize by: vision → phases → milestones → timeline
5. Include both historical (completed) and forward-looking sections

**Action Items:**
1. Create docs/Planning/ROADMAP.md
2. Create docs/Planning/MIGRATION-PLAN.md (separate for focus)
3. Archive originals to archive/deprecated/planning/

---

### GROUP 9: Standards and Guidelines → docs/Standards/

**Purpose:** Project standards, best practices, and setup guides
**Current Files:** 4 files
**Target Location:** Multiple docs/Standards/ files
**Strategy:** Organize by topic for clarity

Files to consolidate:
- ARXIV-STANDARDS.md → docs/Standards/ARXIV-STANDARDS.md (copy, already well-scoped)
- MEGA-BEST-PRACTICES.md → docs/Standards/BEST-PRACTICES.md (merge/rename)
- INSTALLATION.md → docs/Standards/INSTALLATION-GUIDE.md or Examples/
- REQUIREMENTS.md → docs/Standards/REQUIREMENTS.md or Examples/

**Action Items:**
1. Copy ARXIV-STANDARDS.md to docs/Standards/
2. Move MEGA-BEST-PRACTICES.md to docs/Standards/BEST-PRACTICES.md
3. Move INSTALLATION.md to Examples/INSTALLATION-GUIDE.md or docs/Standards/
4. Move REQUIREMENTS.md to docs/Standards/
5. Archive originals to archive/deprecated/standards/

---

### GROUP 10: Analysis and Research → docs/Analysis/

**Purpose:** Technical analysis documents and research findings
**Current Files:** 4 files
**Target Location:** docs/Analysis/ (multiple files)
**Strategy:** Organize as individual reference documents (these are distinct research streams)

Files to organize:
- MINIX-SYSCALL-CATALOG.md → docs/Analysis/SYSCALL-ANALYSIS.md
- MINIX-IPC-ANALYSIS.md → docs/Analysis/IPC-SYSTEM-ANALYSIS.md
- DATA-DRIVEN-DOCUMENTATION.md → docs/Analysis/DATA-DRIVEN-APPROACH.md
- MASTER-ANALYSIS-SYNTHESIS.md → docs/Analysis/SYNTHESIS.md (or keep as overview)

**Action Items:**
1. Copy MINIX-SYSCALL-CATALOG.md to docs/Analysis/SYSCALL-ANALYSIS.md
2. Copy MINIX-IPC-ANALYSIS.md to docs/Analysis/IPC-SYSTEM-ANALYSIS.md
3. Copy DATA-DRIVEN-DOCUMENTATION.md to docs/Analysis/DATA-DRIVEN-APPROACH.md
4. Create docs/Analysis/SYNTHESIS.md if appropriate
5. Archive originals to archive/deprecated/analysis/

---

### GROUP 11: Examples and Getting Started → Examples/

**Purpose:** Usage examples, guides, and quick-start documentation
**Current Files:** 6+ files
**Target Location:** docs/Examples/ and whitepaper/docs/
**Strategy:** Organize by use case and complexity

Files to consolidate:
- README-PROFILING.md → docs/Examples/PROFILING-QUICK-START.md
- MINIX-CLI-EXECUTION-GUIDE.md → docs/Examples/CLI-EXECUTION-GUIDE.md
- MINIX-RUNTIME-SETUP.md → docs/Examples/RUNTIME-SETUP-GUIDE.md
- MINIX-MCP-Integration.md → docs/MCP/INTEGRATION-GUIDE.md
- START-HERE-MCP-FIXED.md → docs/Examples/MCP-QUICK-START.md

**Action Items:**
1. Copy README-PROFILING.md to docs/Examples/PROFILING-QUICK-START.md
2. Copy MINIX-CLI-EXECUTION-GUIDE.md to docs/Examples/
3. Copy MINIX-RUNTIME-SETUP.md to docs/Examples/
4. Copy MINIX-MCP-Integration.md to docs/MCP/INTEGRATION-GUIDE.md
5. Copy START-HERE-MCP-FIXED.md to docs/Examples/MCP-QUICK-START.md
6. Archive originals to archive/deprecated/examples/

---

### GROUP 12: Project Instructions and Metadata → Keep in Root

**Purpose:** Project-level configuration and instructions
**Status:** Keep as-is
**Files:**
- CLAUDE.md (project instructions - move to whitepaper/CLAUDE.md or keep)
- README.md (keep at root as primary entry point)

**Action Items:**
1. Keep CLAUDE.md in root (project-level instructions for Claude Code)
2. Keep README.md in root (primary entry point)
3. Link from README.md to docs/INDEX.md for navigation

---

### GROUP 13: Archive and Deprecation → archive/deprecated/

**Purpose:** Session-specific or transient documents no longer needed in main navigation
**Current Files:** 20+ files
**Strategy:** Move without consolidation; preserve git history

Files to archive:
- AGENTS.md (user instructions - archive)
- CAPABILITIES-AND-TOOLS.md (tool inventory - archive)
- DEV-ENVIRONMENT-READY.md (status report - archive)
- MINIX-Error-Registry.md (incomplete - archive to analysis/)
- APPROACH-1-SYNTHETIC-BENCHMARKS-PLAN-2025-11-01.md
- TESTING-SUMMARY.md
- TIMING_RESEARCH_INDEX.md
- VERSION-VERIFICATION.md
- SESSION-SUMMARY-2025-10-31.md
- SANITY-CHECK-AND-RESYNC-2025-11-01.md
- VALIDATION-APPROACHES-SYNTHESIS-2025-11-01.md
- PHASE-7-5-BOOT-PROFILING-BLOCKER-ANALYSIS.md
- PHASE-7-5-BOOT-PROFILING-STATUS-2025-11-01.md
- PHASE-7-5-DOCUMENTATION-INDEX-2025-11-01.md
- PHASE-7-5-FINAL-SUMMARY-2025-11-01.md
- PHASE-7-5-IMPLEMENTATION-NOTES.md
- PHASE-7-5-INSTALLATION-SUMMARY.md
- PHASE-7-5-INTERIM-VALIDATION-REPORT-2025-11-01.md
- PHASE-7-5-MULTIPROCESSOR-TESTING.md
- PHASE-7-5-PROGRESS-REPORT-2025-11-01.md
- PHASE-7-5-SESSION-SUMMARY.md
- PHASE-7-RUNTIME-INFRASTRUCTURE-ROADMAP.md

**Action Items:**
1. Create archive/deprecated/sessions/ for session-specific files
2. Create archive/deprecated/transient/ for status/progress reports
3. Move Phase-7-5 files to archive/deprecated/phases/phase-7-5/
4. Create README.md in each archive subdirectory explaining deprecation reason
5. Update .gitignore if needed to avoid accidental re-indexing

---

## Consolidation Execution Plan

### Phase 2B-1: Priority 1 Files (4-5 hours)

**Estimated Time:** 4-5 hours
**Files Affected:** ~40 files
**Output:** 8 consolidated documents

1. **Hour 1:** Architecture consolidation
   - Create docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md
   - Create docs/Architecture/CPU-INTERFACE-ANALYSIS.md (supplementary)

2. **Hour 2:** Boot and Analysis consolidation
   - Create docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md
   - Create docs/Analysis/SYSCALL-ANALYSIS.md
   - Create docs/Analysis/IPC-SYSTEM-ANALYSIS.md

3. **Hour 3:** Performance consolidation
   - Create docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md
   - Create docs/Performance/QEMU-OPTIMIZATION-GUIDE.md

4. **Hour 4:** MCP and Audits consolidation
   - Create docs/MCP/MCP-REFERENCE.md
   - Create docs/MCP/MCP-TROUBLESHOOTING.md
   - Create docs/Audits/COMPREHENSIVE-AUDIT-REPORT.md

5. **Hour 5:** Standards and Planning
   - Consolidate docs/Planning/PHASE-COMPLETIONS.md
   - Consolidate docs/Planning/ROADMAP.md
   - Consolidate docs/Standards/PEDAGOGICAL-FRAMEWORK.md

### Phase 2B-2: Priority 2 Files (1-2 hours)

**Estimated Time:** 1-2 hours
**Files Affected:** ~30 files
**Output:** Organized into examples, guidelines, and metadata

1. Copy/move Examples and Guidelines files to appropriate locations
2. Archive Session-specific files
3. Archive Phase-7-5 specific files

### Phase 2B-3: Cross-References Update (30-45 minutes)

**Estimated Time:** 30-45 minutes
**Output:** Updated docs/INDEX.md with new structure

1. Update docs/INDEX.md with new file locations
2. Update whitepaper documentation links
3. Verify no broken internal references

---

## Success Criteria

- [ ] 40+ files consolidated into 8-12 canonical documents
- [ ] All root-level duplicates consolidated
- [ ] Clear, logical docs/ hierarchy established
- [ ] docs/INDEX.md updated with all new locations
- [ ] Git history preserved (copies, not destructive moves)
- [ ] Redirect stubs created at original locations
- [ ] No broken internal references
- [ ] Archive/ contains deprecated files with README explaining reason

---

## Next Steps

After Phase 2B completion:
1. **Phase 2C:** Merge and synthesize related content into comprehensive documents
2. **Phase 2D:** Update cross-references across entire repository
3. **Phase 3:** Harmonize pedagogical commentary (Lions-style) across whitepaper chapters

---

*Mapping Document Created: November 1, 2025*
*Ready for Phase 2B Implementation*
