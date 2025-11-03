# Archive: Examples & Getting Started Sources

**Status**: Organized into `docs/Examples/` (9+ canonical documents)

**Consolidation Date**: November 1, 2025

---

## Why This Content Was Archived

These 6+ source files contained quick-start guides, setup instructions, and usage examples organized by complexity and use case. They have been organized into a carefully structured progressive learning path with 9 documents:

1. **Quick-start guides**: PROFILING-QUICK-START.md, MCP-QUICK-START.md (5-15 minutes)
2. **Usage guides**: CLI-EXECUTION-GUIDE.md, RUNTIME-SETUP-GUIDE.md (20-60 minutes)
3. **Advanced guides**: MCP-INTEGRATION-GUIDE.md, PROFILING-ENHANCEMENT-GUIDE.md (45 minutes - 8 hours)
4. **Navigation**: README.md (overview), INDEX.md (quick reference)
5. **Status**: ORGANIZATION-STATUS-REPORT.md (task summary)

**Original Files** (6+ total, 140 KB):
1. `README-PROFILING.md` - Profiling quick start
2. `MINIX-CLI-EXECUTION-GUIDE.md` - CLI usage guide
3. `MINIX-RUNTIME-SETUP.md` - Runtime environment setup
4. `START-HERE-MCP-FIXED.md` - MCP quick start
5. `MINIX-MCP-Integration.md` - MCP full integration
6. `PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md` - Advanced profiling
7. (Additional supporting files)

---

## Consolidation Methodology

### Step 1: Content Analysis by Complexity
Categorized guides by:
- **Time to Complete**: 5 min, 10 min, 20 min, 30 min, 60 min, 8 hours
- **Prerequisite Knowledge**: Beginner, Intermediate, Advanced
- **Technical Scope**: Quick-start, standard, comprehensive
- **Use Case**: Profiling, MCP integration, CLI usage, runtime setup

### Step 2: Progressive Learning Path Design
Organized guides sequentially:
- **Tier 1 (Beginner, 5-15 min)**: PROFILING-QUICK-START.md, MCP-QUICK-START.md
- **Tier 2 (Intermediate, 20-30 min)**: CLI-EXECUTION-GUIDE.md
- **Tier 3 (Advanced, 30-60 min)**: RUNTIME-SETUP-GUIDE.md, MCP-INTEGRATION-GUIDE.md
- **Tier 4 (Expert, 6-8 hours)**: PROFILING-ENHANCEMENT-GUIDE.md

### Step 3: Navigation Structure
Created multiple access paths:
- **By Complexity**: Beginner → Intermediate → Advanced
- **By Use Case**: Profiling, MCP, CLI, Runtime Setup
- **By Time**: 5-min, 20-min, 60-min, 8-hour guides
- **Quick Reference**: INDEX.md for quick lookup

### Step 4: Practical Workflow Documentation
Captured four common workflows:
1. **Setup & Installation** (RUNTIME-SETUP-GUIDE.md)
2. **Quick Profiling** (PROFILING-QUICK-START.md)
3. **MCP Integration** (MCP-QUICK-START.md → MCP-INTEGRATION-GUIDE.md)
4. **Advanced Customization** (PROFILING-ENHANCEMENT-GUIDE.md)

---

## Result

**Organized Documents** (in `docs/Examples/`):

### Quick-Start Guides (5-15 minutes)
1. **PROFILING-QUICK-START.md** (8.9 KB, ⭐⭐ Beginner)
   - Get first profiling results in 5-15 minutes
   - Prerequisites: Boot MINIX in QEMU
   - Output: Console profiling data
   - Goal: Understand what's available

2. **MCP-QUICK-START.md** (8.6 KB, ⭐⭐ Beginner)
   - Get MCP working in 5-10 minutes
   - Prerequisites: Claude Code, .mcp.json template
   - Output: MCP server connection working
   - Goal: Test basic MCP functionality

### Standard Guides (20-60 minutes)
3. **CLI-EXECUTION-GUIDE.md** (15 KB, ⭐⭐⭐ Intermediate)
   - Complete command-line workflow (20-30 minutes)
   - Prerequisites: MINIX source and analysis tools
   - Coverage: Analysis pipeline overview, key commands, output interpretation
   - Goal: Execute full analysis from command line

4. **RUNTIME-SETUP-GUIDE.md** (17 KB, ⭐⭐⭐⭐ Advanced)
   - QEMU and Docker environment setup (30-60 minutes)
   - Prerequisites: QEMU or Docker installation
   - Coverage: Configuration, optimization, validation
   - Goal: Optimized runtime environment

### Advanced Guides (45 minutes - 8 hours)
5. **MCP-INTEGRATION-GUIDE.md** (19 KB, ⭐⭐⭐⭐ Advanced)
   - Full MCP server integration (45-90 minutes)
   - Prerequisites: MCP basics, Claude Code setup
   - Coverage: Complete integration from setup to validation
   - Goal: Production-ready MCP configuration

6. **PROFILING-ENHANCEMENT-GUIDE.md** (19 KB, ⭐⭐⭐⭐ Advanced)
   - Add granular metrics to boot profiler (6-8 hours)
   - Prerequisites: Python knowledge, MINIX source understanding
   - Coverage: Profiling implementation, testing, validation
   - Goal: Custom profiling measurements

### Navigation & Reference
7. **README.md** (11 KB)
   - Comprehensive navigation hub
   - 3 learning paths (student, developer, researcher)
   - 4 practical workflows with time estimates
   - Multiple access methods
   - Integration points with other documentation

8. **INDEX.md** (10 KB)
   - Quick reference table of all guides
   - Filter by: complexity, time, topic, skill level
   - Hyperlinks to each guide
   - Glossary of common terms

9. **ORGANIZATION-STATUS-REPORT.md** (12 KB)
   - Task completion summary
   - File migration statistics
   - Organization methodology
   - Quality verification results

---

## Learning Paths Documented

### Path 1: Student Learning (2-3 hours total)
1. Start with PROFILING-QUICK-START.md (15 min) - see what's available
2. Read CLI-EXECUTION-GUIDE.md (20 min) - understand workflow
3. Study docs/Analysis/BOOT-SEQUENCE-ANALYSIS.md (30 min) - learn system
4. Try PROFILING-ENHANCEMENT-GUIDE.md sections (1-2 hours) - hands-on
5. Reference docs/Architecture/ as needed

### Path 2: Developer Quick Start (1 hour)
1. Skim README.md (5 min)
2. Follow CLI-EXECUTION-GUIDE.md (20 min)
3. Setup runtime with RUNTIME-SETUP-GUIDE.md (30 min)
4. Bookmark INDEX.md for future reference

### Path 3: Researcher Deep Dive (4-6 hours)
1. Read all quick-start guides (20 min)
2. Complete all standard guides (1 hour)
3. Work through PROFILING-ENHANCEMENT-GUIDE.md (6-8 hours, can split)
4. Cross-reference with analysis documents
5. Design custom research approach

### Path 4: MCP Integration Journey (1.5-2 hours)
1. Start with MCP-QUICK-START.md (10 min)
2. Follow MCP-INTEGRATION-GUIDE.md (45-90 min)
3. Validate with docs/MCP/MCP-VALIDATION-CHECKLIST.md (15 min)

---

## Practical Workflows Documented

### Workflow 1: Boot & Setup (30-60 min)
```
MINIX source downloaded
    ↓
RUNTIME-SETUP-GUIDE.md [30 min]
    ↓
QEMU environment ready
    ↓
CLI-EXECUTION-GUIDE.md [20 min]
    ↓
Analysis pipeline working
```

### Workflow 2: Quick Profiling (15 min)
```
MINIX running in QEMU
    ↓
PROFILING-QUICK-START.md [10 min]
    ↓
First profiling results in console
    ↓
Interpretation guide included
```

### Workflow 3: MCP Integration (1.5-2 hours)
```
Claude Code installed
    ↓
MCP-QUICK-START.md [10 min] ← Basic connectivity check
    ↓
MCP-INTEGRATION-GUIDE.md [45-90 min] ← Full setup
    ↓
MCP-VALIDATION-CHECKLIST.md [15 min] ← Verification
    ↓
Production-ready MCP
```

### Workflow 4: Advanced Customization (6-8 hours)
```
Profiling-QUICK-START.md complete
    ↓
PROFILING-ENHANCEMENT-GUIDE.md [6-8 hours]
    ↓
Custom measurement implemented
    ↓
Results integrated into pipeline
```

---

## Complexity Levels Explained

### Level 1 (⭐⭐ Beginner)
- No prerequisites beyond basic environment
- Simple commands with expected output
- 5-15 minutes to complete
- Good for: Understanding what's available

### Level 2 (⭐⭐⭐ Intermediate)
- Requires basic familiarity with previous level
- Some configuration needed
- 20-30 minutes to complete
- Good for: Using standard workflows

### Level 3 (⭐⭐⭐⭐ Advanced)
- Requires intermediate familiarity + technical knowledge
- Significant configuration or customization
- 30-60 minutes to complete
- Good for: Production setup or advanced usage

### Level 4 (⭐⭐⭐⭐ Expert)
- Requires advanced technical skills
- Involves coding and testing
- 6-8 hours to complete
- Good for: Research and custom development

---

## When to Refer to Archived Files

### Scenario 1: Review Original Quick Start
```bash
cat archive/deprecated/examples/README-PROFILING.md
```
Original profiling quick start before organization.

### Scenario 2: Study CLI Execution Details
```bash
cat archive/deprecated/examples/MINIX-CLI-EXECUTION-GUIDE.md
```
Original comprehensive CLI guide.

### Scenario 3: Understand Runtime Setup
```bash
cat archive/deprecated/examples/MINIX-RUNTIME-SETUP.md
```
Original detailed runtime setup guide.

### Scenario 4: MCP Integration Reference
```bash
cat archive/deprecated/examples/MINIX-MCP-Integration.md
```
Original MCP integration documentation.

### Scenario 5: Profiling Enhancement Details
```bash
cat archive/deprecated/examples/PROFILING-ENHANCEMENT-IMPLEMENTATION-GUIDE.md
```
Original comprehensive enhancement guide.

---

## Integration with Other Documentation

**Related Quick-Start Guides**:
- `docs/MCP/MCP-QUICK-START.md` - Alternative MCP quick start (from root level)
- `docs/Examples/` - All examples in organized form

**Integration Points**:
- Setup → RUNTIME-SETUP-GUIDE.md
- CLI Usage → CLI-EXECUTION-GUIDE.md
- Profiling → PROFILING-QUICK-START.md or PROFILING-ENHANCEMENT-GUIDE.md
- MCP → MCP-QUICK-START.md → MCP-INTEGRATION-GUIDE.md
- Troubleshooting → docs/MCP/MCP-TROUBLESHOOTING.md

---

## Metadata

- **Organization Type**: Progressive learning structure (6+ files → 9 organized documents)
- **Content Loss**: None - all practical examples preserved and well-organized
- **Organization Rationale**: Progressive complexity allows quick start for beginners, depth for advanced users
- **Audience Diversity**: Beginner, developer, researcher, and advanced user paths all supported
- **Validation Status**: ✅ All guides tested (November 1, 2025)
- **Update Frequency**: As tools and processes change; quick-starts updated quarterly
- **Next Action**: Add to docs/Examples/ and link from primary documentation

---

*Archive Created: November 1, 2025*
*Source Files Preserved: 6+ files, 140 KB*
*Canonical Locations*:
- *docs/Examples/PROFILING-QUICK-START.md*
- *docs/Examples/MCP-QUICK-START.md*
- *docs/Examples/CLI-EXECUTION-GUIDE.md*
- *docs/Examples/RUNTIME-SETUP-GUIDE.md*
- *docs/Examples/MCP-INTEGRATION-GUIDE.md*
- *docs/Examples/PROFILING-ENHANCEMENT-GUIDE.md*
- *docs/Examples/README.md*
- *docs/Examples/INDEX.md*
- *docs/Examples/ORGANIZATION-STATUS-REPORT.md*
