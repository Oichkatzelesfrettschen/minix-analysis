# Archival Candidate Tracker

**Purpose**: Provide a living checklist for consolidating legacy Markdown assets now that `MEGA-BEST-PRACTICES.md` serves as the canonical knowledge base. Update this file as documents are merged, retired, or confirmed as long-term references.

---

## 1. Root Deliverables

| File | Current Role | Action |
| ---- | ------------ | ------ |
| `ANALYSIS-COMPLETE-EXECUTIVE-SUMMARY.md` | Executive snapshot summarising Phase 1 outputs | ✔ Retain (link from atlas §0) |
| `FINAL-INTEGRATION-COMPLETE.md`, `FINAL-COMPLETE-ACHIEVEMENT.md`, `DELIVERY-SUMMARY.md` | Release artifacts for final review | 🔄 Evaluate during Phase 4 release—archive once atlas release notes are authoritative |
| `MIGRATION-PLAN.md`, `MIGRATION-PROGRESS.md` | Historical plan + progress log | ✔ Retain as historical appendix; reference in atlas roadmap |
| `PROJECT-SYNTHESIS.md`, `MASTER-ANALYSIS-SYNTHESIS.md` | Long-form synthesis predating atlas | ⚠ Candidate for partial archival—verify unique analysis before folding into atlas appendices |
| `PIPELINE-VALIDATION-COMPLETE.md`, `TESTING-SUMMARY.md` | Running validation notes | ✔ Keep active; sync after each run |

---

## 2. Module Documentation

| Path | Current Role | Action |
| ---- | ------------ | ------ |
| `modules/cpu-interface/docs/*.md` | Mirrors of CPU analysis narratives | ✔ Retain as module-local mirrors (keep synced with atlas §5.1) |
| `modules/boot-sequence/docs/*.md` | Boot sequence documentation | ✔ Retain; ensure atlas references remain current |
| `modules/*/README.md` | Module quick-start guides | ✔ Keep; align tone/style with atlas |

---

## 3. Thematic Whitepapers

| File | Current Role | Action |
| ---- | ------------ | ------ |
| `whitepapers/01-WHY-MICROKERNEL-ARCHITECTURE.md` etc. | Pedagogical essays supporting the project | ✔ Retain; cross-link from atlas §9 |
| `WHITEPAPER-COMPLETION-REPORT.md`, `WHITEPAPER-SUITE-COMPLETE.md` | Publication status trackers | 🔄 Review during Phase 4 publication prep and collapse into single status sheet if practical |

---

## 4. Support Surfaces

| Path | Current Role | Action |
| ---- | ------------ | ------ |
| `wiki/*.md` | MkDocs-fronted portal | 🔄 Update API/Testing pages to reference shared MCP server + CLI (partial refresh complete) |
| `shared/styles/*.md` | Style guide references | ✔ Retain |
| `benchmarks/*.md`, `formal-models/*.md` | Benchmark & formal verification plans | ⚠ Confirm accuracy post-Phase 4; archive outdated frameworks |
| `arxiv-submission/*.md` | Packaging guides | ⚠ Fold into publication checklist during Phase 4 |

---

## 5. Legacy / Miscellaneous

| Item | Current Role | Action |
| ---- | ------------ | ------ |
| `archive/legacy/README-CPU-ANALYSIS-LEGACY.md` | Legacy README pre-umbrella | ✅ Archived (content reflected in atlas/module docs) |
| Files under `venv/`, `.pytest_cache/` | Environment artefacts | ➖ Ignore (not tracked) |
| External project summaries under repo root (`DEEP-AUDIT-REPORT.md`, etc.) | Historical documentation | ⚠ Review for unique analysis; move to `archive/` directory if superseded by atlas |

---

## Next Review

- **Owner**: Documentation lead (currently atlas maintainer)
- **Cadence**: Revisit during Phase 4 completion review or whenever new Markdown assets are introduced.
- **Process**:
  1. Identify duplicates or superseded content.
  2. Merge unique insights into the atlas.
  3. Move obsolete files to an `archive/` folder or remove if no longer needed (after stakeholder approval).
