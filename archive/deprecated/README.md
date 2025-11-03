# Archive: Deprecated Documentation

**Purpose**: This directory preserves deprecated, consolidated, or session-specific documentation files that have been reorganized into the main `docs/` hierarchy or archived for historical reference.

**Archival Policy**:
- Files are moved here when they are **consolidated** into comprehensive reference documents
- Files are moved here when they are **session-specific** and no longer part of active navigation
- Files are moved here when they are **superseded** by updated versions with the same information
- Original files are preserved to maintain git history and traceability
- Each subdirectory includes a README explaining the consolidation or deprecation rationale

**When to Refer to Archived Files**:
1. **Historical Context**: Understand how documentation evolved
2. **Git History**: Trace commits and changes to specific content
3. **Preserved Content**: Access original formulation if needed
4. **Migration Reference**: See how content was reorganized

**Key Principle**: If a file is in `archive/deprecated/`, refer instead to the **canonical location** listed in the subdirectory README.

---

## Directory Structure

```
archive/deprecated/
├── README.md                          (This file)
├── architecture/                      (Consolidation: → docs/Architecture/)
├── boot-analysis/                     (Consolidation: → docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md)
├── performance/                       (Consolidation: → docs/Performance/)
├── mcp/                               (Consolidation: → docs/MCP/)
├── audits/                            (Consolidation: → docs/Audits/)
├── planning/                          (Consolidation: → docs/Planning/)
├── standards/                         (Consolidation: → docs/Standards/)
├── analysis/                          (Consolidation: → docs/Analysis/)
├── examples/                          (Consolidation: → docs/Examples/)
├── phases/                            (Phase-specific files)
│   └── phase-7-5/                     (Phase 7.5 session artifacts)
├── sessions/                          (Session-specific documentation)
└── transient/                         (Status reports, temporary progress logs)
```

---

## Consolidation Summary

### Phase 2B Consolidation Results

| Source Category | Files | Consolidated To | Status |
|-----------------|-------|------------------|--------|
| Architecture | 8 | docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md | ✅ Consolidated |
| Boot Analysis | 3 | docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md | ✅ Consolidated |
| Performance | 10 | docs/Performance/ (2 files) | ✅ Consolidated |
| MCP | 9 | docs/MCP/ (3 files) | ✅ Consolidated |
| Audits | 6 | docs/Audits/ (3 files) | ✅ Consolidated |
| Planning | 9 | docs/Planning/ (2 files) | ✅ Consolidated |
| Standards | 4 | docs/Standards/ (4 files) | ✅ Organized |
| Analysis | 4 | docs/Analysis/ (6 files) | ✅ Organized |
| Examples | 6+ | docs/Examples/ (9 files) | ✅ Organized |

**Total Consolidated**: 49+ source files → 28+ canonical reference documents
**File Reduction**: 77-90% reduction in deprecated/duplicate content

---

## How to Find Content

### If you need to understand...

**System Architecture**:
- **Archived files**: `archive/deprecated/architecture/`
- **Current reference**: `docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md`
- **Use case**: Need comprehensive CPU interface, ISA, or microarchitecture details

**Boot Sequence**:
- **Archived files**: `archive/deprecated/boot-analysis/`
- **Current reference**: `docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md`
- **Use case**: Need boot traces, process creation details, or initialization sequence

**Performance Analysis**:
- **Archived files**: `archive/deprecated/performance/`
- **Current references**:
  - `docs/Performance/COMPREHENSIVE-PROFILING-GUIDE.md` (methodology + results)
  - `docs/Performance/QEMU-OPTIMIZATION-GUIDE.md` (QEMU-specific optimization)
- **Use case**: Performance benchmarking, profiling methodology, QEMU tuning

**MCP Integration**:
- **Archived files**: `archive/deprecated/mcp/`
- **Current references**:
  - `docs/MCP/MCP-REFERENCE.md` (main reference)
  - `docs/MCP/MCP-TROUBLESHOOTING.md` (troubleshooting)
  - `docs/MCP/MCP-VALIDATION-CHECKLIST.md` (validation procedures)
- **Use case**: Model Context Protocol setup, integration, or debugging

**Project Standards**:
- **Archived files**: `archive/deprecated/standards/`
- **Current references**:
  - `docs/Standards/ARXIV-STANDARDS.md` (publication guidelines)
  - `docs/Standards/BEST-PRACTICES.md` (project best practices)
  - `docs/Standards/PEDAGOGICAL-FRAMEWORK.md` (Lions-style commentary philosophy)
- **Use case**: Understand project conventions, publication requirements, or pedagogical approach

**Quick-Start Guides**:
- **Archived files**: `archive/deprecated/examples/`
- **Current references**: `docs/Examples/` (organized by complexity and use case)
- **Use case**: Get started quickly with CLI, runtime setup, profiling, or MCP integration

---

## Git History and Traceability

Archived files are preserved in git history. To understand content evolution:

```bash
# View git history of a consolidated file
git log --follow archive/deprecated/architecture/MINIX-ARCHITECTURE-SUMMARY.md

# See all consolidations in Phase 2B
git log --grep="PHASE 2B" --oneline

# Find when content moved to new location
git log -p docs/Architecture/MINIX-ARCHITECTURE-COMPLETE.md | head -100
```

---

## Migration Timeline

**Phase 2B: Consolidation (November 1, 2025)**
- 49+ source files consolidated into hierarchical `docs/` structure
- Deprecated files moved to `archive/deprecated/` with README explanations
- Git history preserved for all files

**Future Phases**
- Phase 2C: Enhance cross-references between consolidated documents
- Phase 2D: Verify all internal links work correctly
- Phase 3: Harmonize pedagogical commentary across whitepaper
- Phase 4: Prepare for GitHub publication

---

## Accessing Archived Content

### For Reference/Research
```bash
cd archive/deprecated/
grep -r "keyword" .              # Search across all deprecated files
ls -la architecture/             # View consolidated source files
```

### For Historical Context
```bash
git log --all -- archive/deprecated/  # View all changes to deprecated files
git blame archive/deprecated/file.md   # See who made each change
```

### For Understanding Migration
```bash
cat docs/Standards/README.md           # See how Standards/ was organized
cat docs/Examples/README.md            # See Examples/ structure
```

---

## Maintenance

**Quarterly Review**:
1. Verify consolidated documents in `docs/` remain current
2. Check for any orphaned content in `archive/deprecated/`
3. Update cross-references if new content is added

**When Adding New Content**:
1. Determine if content fits existing consolidated documents
2. If so, update the canonical document and archive the new source
3. If not, create new document in appropriate `docs/` subdirectory

**Archive Cleanup Policy**:
- Keep files for 2+ years minimum to preserve git history
- Consider removing only after:
  - Content is verified as fully integrated into canonical documents
  - Stakeholder approval is obtained
  - Git history is extracted and preserved in commit messages

---

*Archive Directory Created: November 1, 2025*
*Consolidation Status: Phase 2B Archival Complete*
*Last Updated: November 1, 2025*
