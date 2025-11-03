# Standards: Documentation and Contribution Guidelines

This section documents the standards, guidelines, and best practices for contributing to the MINIX analysis project. Use these to ensure your work maintains consistency with the Lions-style pedagogy and professional quality standards.

## Project Standards

### Writing Standards

#### Lions-Style Commentary

Our documentation follows the Lions Commentary approach:

1. **Explain Design Rationale First**
   - Start with "why" (constraints, trade-offs)
   - Then explain "what" (code, structure)
   - Finally show "how" (mechanisms, details)

   Example (Wrong):
   ```
   MINIX uses 2-level page tables with PDE (10 bits) and PTE (10 bits).
   ```

   Example (Right):
   ```
   MINIX must balance memory usage against lookup speed. A single-level 
   page table for 4GB address space would need 1M entries (~4MB). Two 
   levels reduce this to max 4MB per process. MINIX uses:
   - PDE: 10 bits (1024 entries, 4MB per level)
   - PTE: 10 bits (1024 entries, 4MB per level)
   - Offset: 12 bits (4KB pages)
   ```

2. **Acknowledge Difficulty**
   - Don't pretend everything is simple
   - Use phrase: "You are not expected to understand X yet"
   - Reference where full explanation exists

   Example:
   ```
   Context switching involves saving the CPU state and flushing the TLB.
   You are not expected to understand TLB invalidation strategies yet; 
   see docs/architecture/tlb/README.md for details.
   ```

3. **Multiple Entry Points**
   - Allow readers to enter at different levels
   - Provide section headers for quick scanning
   - Link to related concepts

   Example:
   ```
   ## Boot Sequence (30 seconds overview)
   MINIX boots in 5 phases: loader → kernel → memory → drivers → servers.

   ## Boot Timeline (10 minutes detailed)
   [Detailed phase breakdown]

   ## Boot Code Walkthrough (1 hour deep dive)
   [Line-by-line source code analysis]
   ```

4. **Integrate Context**
   - Explain hardware constraints that drive design
   - Show alternatives that were rejected
   - Justify each design decision

   Example:
   ```
   Why not use flat page tables?
   - Would need 1M entries for 4GB address space
   - Each entry ~8 bytes = 8MB overhead per process
   - With 2-level hierarchy, max 4MB per process
   - Trade-off: Slightly slower (2 memory accesses instead of 1) for huge savings
   ```

#### Structure and Organization

**Heading Hierarchy**:
```
# Section (major topic)
## Subsection (concept)
### Implementation Detail (code/mechanism)
#### Use Case (when to apply)
```

**Paragraph Style**:
- Opening sentence: Answer the question
- Supporting paragraphs: Explain why/how
- Conclusion: Summary of key insight

Example:
```
MINIX uses message passing for inter-process communication.

Message passing means processes send structured data to each other
rather than sharing memory. Why this design?

1. Security: Processes can't directly access each other's memory
2. Reliability: A crash in one server doesn't corrupt another's data
3. Modularity: Servers can be replaced without recompiling others

Trade-off: Message copying overhead (not zero-copy). Acceptable because
IPC isn't on the critical path for most applications.
```

### Content Standards

#### Completeness

Every major component needs three levels:

**Level 1: What** (5 minutes)
- What is this component?
- What problem does it solve?
- When would I care?

**Level 2: How** (30 minutes)
- How does it work?
- What are the main algorithms?
- What data structures are used?

**Level 3: Why** (1+ hour)
- Why was this design chosen?
- What are the trade-offs?
- What are the alternatives?

Example: System Calls
```
## What: System Calls (5 min)
User programs invoke kernel services through system calls. MINIX supports
34 different syscalls (GETPID, READ, WRITE, etc.).

## How: Three Mechanisms (30 min)
MINIX supports three syscall paths:
1. INT 0x21 - interrupt gate (legacy)
2. SYSENTER - fast entry (modern)
3. SYSCALL - AMD/Intel variant

[Technical details, code references, measurements]

## Why: Design Rationale (1+ hour)
Why three mechanisms?
- Hardware evolution: Old CPUs lack SYSENTER/SYSCALL
- Performance: SYSENTER 27% faster than INT
- Compatibility: Support multiple CPU generations

Chosen trade-off: Support all three. Why not just use fastest?
Because MINIX targets embedded/old systems where SYSENTER unavailable.
```

#### Accuracy

**Verification Requirements**:
- All claims must be verifiable against MINIX source code
- Performance measurements must be reproducible
- Architectural decisions must be documented with rationale

**Format for Verification**:
```
Claim: SYSENTER is faster than INT 0x21
Evidence: docs/architecture/SYSCALL-ARCHITECTURE.md
Measurement: SYSENTER ~1305 cycles, INT ~1772 cycles
Source: kernel/system/minix_call.S (line 45-67)
Verification: Can be reproduced with: perf record ./syscall_benchmark
```

#### Consistency

**Cross-Reference Style**:
```
Consistent ✓:
- [See Boot Sequence Analysis](../analysis/BOOT-SEQUENCE-ANALYSIS.md)
- [Architecture: CPU Interface](../architecture/CPU-INTERFACE-ANALYSIS.md)
- [Performance Data](../performance/#syscall-timing)

Inconsistent ✗:
- See boot analysis
- Check out the CPU architecture section
- Performance stuff is in performance/
```

**Terminology**:
- Define terms on first use: "The Translation Lookaside Buffer (TLB) is..."
- Use consistent names: "page directory entry" not "PD entry" or "PDE entry"
- Link to glossary for domain-specific terms

### Technical Standards

#### Code References

All code references must include:
- File path (relative to MINIX root)
- Line numbers (if available)
- Context (why this code matters)

Example (Good):
```
Context switching implemented in kernel/arch/i386/switch.S:101-145.
The function save_state() saves CPU registers before context switch.
This is called before TLB invalidation (why? See memory layout analysis).
```

Example (Bad):
```
See kernel code for details.
```

#### Diagrams

Diagrams must be:
- Generated from data (not hand-drawn)
- Reproducible (tools + data provided)
- Referenced in text
- Labeled clearly

Example:
```
See Figure 3: Boot Timeline (generated by tools/tikz_generator.py
from data/boot-phases.json, shows 5 phases with timing)
```

#### Performance Claims

All performance measurements must include:
- Tool used (perf, strace, timing, etc.)
- Hardware (QEMU i386, CPU model)
- Command line (exact invocation)
- Multiple runs (at least 3, show variance)
- Source of truth (where measurement code lives)

Example (Good):
```
Syscall latency: SYSENTER ~1305 cycles

Measured with: perf record -e cycles ./syscall_test
Platform: QEMU i386, Pentium Pro
Runs: 10, mean ± stddev = 1305 ± 15 cycles
Source: tools/syscall_benchmark.c lines 45-89
Reproducible: Yes (data in benchmarks/syscall-timing.csv)
```

## Contribution Process

### For Documentation Updates

1. **Create branch**: `git checkout -b docs/update-name`

2. **Identify file**: Which docs/ section needs updating?

3. **Check standards**: Does update follow Lions-style?
   - [ ] Explains rationale (why)
   - [ ] Acknowledges difficulty
   - [ ] Multiple entry points
   - [ ] Integrates context

4. **Verify accuracy**: Is every claim verifiable?
   - [ ] Source code references provided
   - [ ] Performance measurements reproducible
   - [ ] Cross-references validated

5. **Update cross-references**: Do other docs need links?
   - [ ] Check docs/INDEX.md
   - [ ] Update related files
   - [ ] Verify links work

6. **Commit and test**: Build locally first
   ```bash
   make docs        # Build documentation
   make test        # Run tests
   git diff         # Review changes
   ```

7. **Create PR**: Push and create pull request with:
   - [ ] Clear description of changes
   - [ ] Which Lions techniques applied
   - [ ] Verification checklist completed
   - [ ] Cross-reference updates listed

8. **Peer review**: Wait for approval before merge

### For New Content (New Files)

1. **Plan structure**: Follow docs/ hierarchy
   ```
   docs/topic/NEW-FILE.md         (new content)
   docs/topic/README.md           (update to include new file)
   docs/INDEX.md                  (add to index)
   ```

2. **Follow template**: Start with provided structure
   ```markdown
   # Topic: Brief Description

   ## What is [topic]? (5 min)
   [Elevator pitch]

   ## How does it work? (30 min)
   [Detailed explanation with examples]

   ## Why this design? (1+ hour)
   [Rationale and trade-offs]

   ## Related Content
   [Links to related sections]
   ```

3. **Lions-style checklist**:
   - [ ] Explain rationale before mechanism
   - [ ] Acknowledge what's difficult
   - [ ] Provide multiple entry points
   - [ ] Integrate hardware/historical context

4. **Quality checklist**:
   - [ ] Zero broken cross-references
   - [ ] All code references verified
   - [ ] Performance measurements reproducible
   - [ ] Grammar and spelling checked

5. **Integration**: Ensure new file is:
   - [ ] Listed in parent README.md
   - [ ] Added to docs/INDEX.md
   - [ ] Referenced from related docs
   - [ ] Built successfully (make docs)

## Peer Review Checklist

When reviewing contributions, verify:

**Content Quality**:
- [ ] Uses Lions-style (rationale first, mechanism second)
- [ ] Appropriate depth for target audience
- [ ] All claims verified or marked "TBD"
- [ ] No duplicated content (check archive/)

**Technical Accuracy**:
- [ ] Code references correct and verified
- [ ] Performance measurements reproducible
- [ ] Architecture diagrams accurate
- [ ] No contradictions with other docs

**Cross-Reference Integrity**:
- [ ] All internal links work
- [ ] External links point to correct resources
- [ ] No orphaned sections
- [ ] docs/INDEX.md updated

**Lions-Style Compliance**:
- [ ] Design rationale explained
- [ ] Hardware context provided
- [ ] Difficulty acknowledged
- [ ] Alternatives mentioned

**Professional Standards**:
- [ ] Heading hierarchy correct
- [ ] Consistent terminology
- [ ] Proper markdown formatting
- [ ] No typos or grammar errors

## Standards Reference

### File Naming

```
Canonical documents (consolidated): UPPERCASE-HYPHENATED.md
Quick guides: lowercase-hyphenated.md
README files: README.md (always lowercase)
Archive files: Original-Naming-Preserved.md
```

### Directory Structure

```
docs/
├── analysis/          (system behavior analysis)
├── architecture/      (design and structure)
├── audits/           (quality assurance)
├── examples/         (learning paths)
├── mcp/              (tool integration)
├── performance/      (measurement and optimization)
├── planning/         (roadmap and strategy)
└── standards/        (this section, guidelines)
```

### Markdown Style

- Use ATX headings (`#`, `##`, not underlines)
- Use backticks for code (`variable`, `function()`)
- Use code blocks with language tags (```c, ```python)
- Use tables for structured data
- Use lists (unordered `-`, ordered `1.`) appropriately

### Terminology Glossary

- **Syscall**: System call (user → kernel)
- **TLB**: Translation Lookaside Buffer (cache)
- **PDE**: Page Directory Entry (paging)
- **PTE**: Page Table Entry (paging)
- **Context switch**: Save/restore process state
- **Microkernel**: Minimal kernel architecture
- **IPC**: Inter-Process Communication
- **DTLB**: Data TLB (hardware cache)
- **ITLB**: Instruction TLB (hardware cache)

### Reference Format

**Internal reference** (cross-document):
```markdown
[See Architecture Overview](../architecture/README.md)
[Syscall Timing Data](../performance/CPU-UTILIZATION-ANALYSIS.md#syscall-timing)
```

**External reference** (MINIX source):
```markdown
[Context switching code](file:///home/eirikr/Playground/minix/minix/kernel/arch/i386/switch.S#L101)
See kernel/system/do_getpid.c (line 15-25)
```

**Performance reference**:
```markdown
Measured with perf: `perf record -e cycles ./benchmark`
Results: [Performance data](../performance/syscall-timing.csv)
```

## Tools and Infrastructure

### Required Tools

- Text editor (VS Code, vim, Emacs)
- Git (version control)
- Python 3.8+ (for data processing)
- LaTeX/TikZ (for diagrams, optional)

### Build System

```bash
make docs        # Build documentation (mkdocs build)
make test        # Run validation tests
make audit       # Run quality audits
make clean       # Clean build artifacts
```

### MkDocs Configuration

Documentation uses MkDocs with Material theme:
- `mkdocs.yml`: Site configuration
- `docs/`: Content directory
- Build: `mkdocs build` → `site/`

See `mkdocs.yml` for full configuration.

## Quality Metrics

Contributions should meet:

- **Coverage**: 90%+ of identified components documented
- **Accuracy**: 100% of claims verified (or marked "TBD")
- **Cross-references**: 100% of links working
- **Lions compliance**: 90%+ sections follow Lions-style
- **Readability**: Flesch-Kincaid Grade 10-12 level

## Change Management

Major changes (affecting project scope, timeline, or standards) require:

1. Document proposal (rationale, impact, effort)
2. Stakeholder notification
3. Decision point (approve/reject/revise)
4. Execution plan
5. Progress tracking
6. Lessons learned documentation

See ROADMAP.md for approval process.

## Connection to Other Sections

**Architecture** (docs/architecture/):
- These standards explain how to document architecture

**Analysis** (docs/analysis/):
- These standards explain how to document analysis findings

**Planning** (docs/planning/):
- These standards are applied during planned phases

**Examples** (docs/examples/):
- These standards guide creation of example workflows

## Navigation

- [Return to docs/](../README.md)
- [Architecture: Design Standards](../architecture/README.md) - How to document design
- [Analysis: Research Standards](../analysis/README.md) - How to document findings
- [Planning: Process Standards](../planning/README.md) - How to plan work
- [Contributing Guide](CONTRIBUTING.md) - Detailed contribution process

---

**Updated**: November 1, 2025
**Status**: Standards finalized, ready for Phase 3 execution
**Lions-Style**: Full framework documented and exemplified
**Quality Gates**: All standards defined and measurable
**Version**: 1.0
