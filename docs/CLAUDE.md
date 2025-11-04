# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a comprehensive MINIX 3.4 operating system analysis repository that combines:
- Source code analysis tools that extract data from OS codebases
- Pedagogical documentation in the style of Lions' Commentary
- Data-driven diagram generation from source code
- Formal verification models (TLA+)
- Performance benchmarking frameworks
- LaTeX whitepaper materials for academic publication
- **MCP integration for automated Docker/GitHub workflow**
- **TeXplosion CI/CD pipeline for continuous publication to GitHub Pages**

## Current Repository Status (2025-11-04)

**Health Score:** 82/100 (Good)
- Structure: 95/100 ✅
- Documentation: 85/100 ✅
- Testing: Infrastructure complete, coverage in progress
- Build System: 90/100 ✅
- Quality Automation: 15+ pre-commit hooks ✅

## Critical Paths and Dependencies

```
MINIX Source: minix-source/
Analysis Root: /home/runner/work/minix-analysis/minix-analysis/
Python Tools: tools/minix_source_analyzer.py, tools/tikz_generator.py
Diagnostics: tools/triage-minix-errors.py
Launch Scripts: scripts/minix-qemu-launcher.sh, scripts/minix-boot-diagnostics.sh
Data Flow: Source → JSON (diagrams/data/) → TikZ → PDF/PNG
Error Registry: docs/MINIX-Error-Registry.md (15+ documented errors with solutions)
Whitepaper: whitepaper/MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

## Directory Structure

```
minix-analysis/
├── .github/workflows/        # CI/CD pipelines
│   ├── texplosion-pages.yml  # TeXplosion continuous publication
│   └── ci.yml                # Standard CI checks
├── whitepaper/               # LaTeX whitepaper (300+ pages)
├── diagrams/                 # TikZ diagrams and visualizations
├── tools/                    # Analysis tools
├── scripts/                  # Automation scripts
├── tests/                    # Test suite (pytest)
├── docs/                     # Documentation
│   ├── testing/              # Testing framework guides
│   ├── quality/              # Quality assurance docs
│   └── [other docs]
├── mcp/                      # MCP server implementations
├── archive/                  # Historical materials
└── requirements.txt          # Python dependencies
```

## TeXplosion Pipeline (NEW - 2025-11-04)

**What it is:** A 5-stage GitHub Actions pipeline that automatically compiles LaTeX whitepapers, generates diagrams, and deploys to GitHub Pages.

**Stages:**
1. Generate Diagrams (3-5 min) - TikZ/PGFPlots from analysis data
2. Build MINIX (60-90 min, optional) - QEMU/Docker compilation
3. Compile LaTeX (5-10 min) - 300+ page whitepaper
4. Build Pages (2-3 min) - MkDocs + landing page
5. Deploy (1-2 min) - GitHub Pages publication

**Documentation:**
- `docs/TEXPLOSION-PIPELINE.md` - Complete architecture
- `docs/TEXPLOSION-QUICKSTART.md` - Quick start guide
- `docs/TEXPLOSION-FAQ.md` - 50+ Q&A
- `docs/TEXPLOSION-EXAMPLE.md` - Full walkthrough

**Trigger:** Automatic on push to `main` when files in `whitepaper/`, `diagrams/`, `tools/`, or `docs/` change

## Quality Automation (NEW - 2025-11-04)

**Pre-commit Hooks:** 15+ automated checks
- Python: Black, Flake8, isort, MyPy, Bandit, pydocstyle
- Shell: shellcheck
- YAML: yamllint, syntax validation
- Markdown: markdownlint
- Security: Bandit, detect-secrets

**Setup:**
```bash
pip install pre-commit
pre-commit install
```

**Build Validation:**
```bash
python3 scripts/validate-build.py --quick  # Quick check
python3 scripts/validate-build.py          # Full validation
```

## Testing Framework (NEW - 2025-11-04)

**Configuration:** `pytest.ini`

**Test Categories:**
- `unit` - Unit tests (fast)
- `integration` - Integration tests
- `benchmark` - Performance tests
- `property` - Property-based tests
- `slow` - Tests >10 seconds

**Run tests:**
```bash
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest --cov=src         # With coverage
pytest -m "not slow"     # Skip slow tests
```

**Documentation:** `docs/testing/README.md`

## MCP Quick Start

**Enable Claude Code automation with MCP servers**:

```bash
# 1. Set credentials
export GITHUB_TOKEN="ghp_YourToken"
export DOCKER_HUB_USERNAME="your-id"
export DOCKER_HUB_TOKEN="your-token"

# 2. Start services
docker-compose -f docker-compose.enhanced.yml up -d

# 3. In Claude Code, test:
# "Can you list my Docker containers?"
```

**Available MCP Servers**:
- Docker: Control MINIX instances, fetch logs, monitor stats
- Docker Hub: Search images, version management
- GitHub: Create issues for errors, track diagnostics
- SQLite: Query boot measurements database
- Custom Boot Profiler: Multi-CPU testing and analysis

## Key Workflows

### 1. TeXplosion Workflow (Continuous Publication)

```bash
# Edit whitepaper or docs
vim whitepaper/ch01-introduction.tex

# Commit and push
git add whitepaper/ch01-introduction.tex
git commit -m "Update introduction"
git push origin main

# Pipeline automatically:
# - Generates diagrams
# - Compiles PDF
# - Builds documentation site
# - Deploys to GitHub Pages
# Result available at: username.github.io/minix-analysis/
```

### 2. Analysis Workflow

```bash
# Run source analysis
python3 tools/minix_source_analyzer.py --source minix-source/

# Generate TikZ diagrams
python3 tools/tikz_generator.py --data diagrams/data/ --output diagrams/tikz-generated/

# Diagrams automatically included in next TeXplosion build
```

### 3. Testing Workflow

```bash
# Run pre-commit checks
pre-commit run --all-files

# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 4. ArXiv Submission Workflow (NEW)

```bash
# Create ArXiv package
./scripts/create-arxiv-package.sh --whitepaper

# Review package
cd arxiv-submissions/<package-name>/

# Test compilation
pdflatex main.tex

# Submit ZIP to ArXiv
```

## Development Guidelines

### Quality Standards

1. **Warnings as Errors:** Treat all warnings as errors
2. **Testing Required:** All new code must have tests
3. **Documentation Required:** Update docs with code changes
4. **Pre-commit Checks:** Must pass before committing
5. **Build Validation:** Run `validate-build.py` before pushing

### Code Style

- **Python:** Black formatting (88 char line length)
- **Shell:** shellcheck compliant
- **LaTeX:** Follow whitepaper style conventions
- **Markdown:** markdownlint compliant

### Testing Requirements

- **Coverage Target:** 80%
- **Test Categories:** Use appropriate markers
- **Mock External Deps:** Use mocks for external services
- **Fast Tests:** Unit tests < 1 second

### Documentation Requirements

- **Every module:** Has README.md
- **Every function:** Has docstring
- **Every script:** Has usage comments
- **Every workflow:** Has documentation

## Common Tasks

### Add New Analysis Tool

1. Create tool in `tools/<name>.py`
2. Add tests in `tests/test_<name>.py`
3. Update `REQUIREMENTS.md` if new dependencies
4. Document in `docs/analysis/<name>.md`
5. Run pre-commit and tests
6. Update this file with new workflow

### Add New LaTeX Chapter

1. Create `whitepaper/chXX-<topic>.tex`
2. Add `\include{chXX-<topic>}` to main document
3. Test compilation locally
4. Push to trigger TeXplosion pipeline
5. Review deployed PDF on GitHub Pages

### Add New Test

1. Create test file `tests/test_<feature>.py`
2. Use appropriate markers (`@pytest.mark.unit`, etc.)
3. Follow naming conventions (`test_<function>_<scenario>`)
4. Run: `pytest tests/test_<feature>.py`
5. Check coverage: `pytest --cov=src`

### Fix Build Issues

1. Run validation: `python3 scripts/validate-build.py`
2. Check pre-commit: `pre-commit run --all-files`
3. Run tests: `pytest -v`
4. Check workflow logs in GitHub Actions
5. Review error messages and fix
6. Validate fix: `validate-build.py` again

## Important Files

### Configuration
- `pytest.ini` - Test configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.bandit` - Security scanning config
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Project overview
- `REQUIREMENTS.md` - Unified dependency documentation
- `COMPREHENSIVE-REPOSITORY-AUDIT.md` - Repository health analysis
- `docs/INDEX.md` - Documentation index

### Scripts
- `scripts/validate-build.py` - Build validation
- `scripts/validate-texplosion-setup.py` - TeXplosion validation
- `scripts/create-arxiv-package.sh` - ArXiv packaging
- `scripts/minix-qemu-launcher.sh` - MINIX launcher

### Workflows
- `.github/workflows/texplosion-pages.yml` - TeXplosion pipeline
- `.github/workflows/ci.yml` - Standard CI

## Troubleshooting

### TeXplosion Build Fails

1. Check workflow run in GitHub Actions
2. Download artifacts for logs
3. Validate LaTeX locally: `cd whitepaper && pdflatex main.tex`
4. Check diagram generation: `python3 tools/tikz_generator.py`
5. Review FAQ: `docs/TEXPLOSION-FAQ.md`

### Pre-commit Hooks Fail

1. Run manually: `pre-commit run --all-files`
2. Fix reported issues
3. For formatting: `black src/ tests/`
4. For imports: `isort src/ tests/`
5. For linting: Review and fix Flake8 errors

### Tests Fail

1. Run specific test: `pytest tests/test_<name>.py -v`
2. Check test logs for error messages
3. Run with debugging: `pytest -s -v`
4. Check fixtures in `tests/conftest.py`
5. Review test documentation: `docs/testing/README.md`

### Build Validation Fails

1. Run: `python3 scripts/validate-build.py`
2. Install missing dependencies
3. Fix configuration issues
4. Re-run validation
5. Check detailed output for specific failures

## Resources

### Documentation
- Full docs: `docs/INDEX.md`
- Testing guide: `docs/testing/README.md`
- Quality guide: `docs/quality/PRE-COMMIT.md`
- TeXplosion guide: `docs/TEXPLOSION-PIPELINE.md`

### External Links
- Repository: https://github.com/Oichkatzelesfrettschen/minix-analysis
- MINIX Project: https://minix3.org/
- GitHub Pages: (after first TeXplosion deployment)

## Agent Coordination

### Parallel Work
- Multiple agents can work on different modules simultaneously
- Use branches for major features
- Coordinate via GitHub issues and PRs
- Update documentation as you work

### Best Practices for Agents
1. Read this file completely before starting
2. Check `COMPREHENSIVE-REPOSITORY-AUDIT.md` for current state
3. Run `validate-build.py` before committing
4. Update relevant documentation
5. Add tests for new code
6. Follow systematic approach: Build → Test → Document → Validate

---

**Last Updated:** 2025-11-04
**Maintained By:** Project Team
**Status:** Production Ready

**AD ASTRA PER MATHEMATICA ET SCIENTIAM** ✨
- Custom Syscall Tracer: System call frequency analysis
- Custom Memory Monitor: Memory usage tracking

**Key Workflows**:
1. Start MINIX → Fetch boot log → Run error triage → Create GitHub issue
2. Multi-CPU test → Insert to SQLite → Query scaling efficiency
3. Detect error → Get solution from registry → Apply fix → Log to GitHub

See **MINIX-MCP-Integration.md** for complete guide.

## Building and Running Analysis Pipeline

### Complete Analysis Pipeline
```bash
# 1. Extract data from MINIX source
cd /home/eirikr/Playground/minix-analysis
python3 tools/minix_source_analyzer.py --minix-root /home/eirikr/Playground/minix --output diagrams/data

# 2. Generate TikZ diagrams from extracted data
python3 tools/tikz_generator.py --data-dir diagrams/data --output diagrams/tikz-generated

# 3. Compile TikZ to PDF
cd diagrams/tikz-generated
for tex in *.tex; do
    pdflatex -interaction=nonstopmode "$tex"
done

# 4. Convert PDF to PNG for web/documentation
for pdf in *.pdf; do
    magick -density 150 "$pdf" -quality 90 "${pdf%.pdf}.png"
done
```

### Quick MINIX Boot and Diagnostics

```bash
# Interactive launcher (auto-detects system)
./scripts/minix-qemu-launcher.sh

# Or direct commands:
./scripts/minix-qemu-launcher.sh install     # Install from ISO
./scripts/minix-qemu-launcher.sh boot        # Boot existing disk
./scripts/minix-qemu-launcher.sh diagnostics # System analysis

# Error diagnosis
python3 tools/triage-minix-errors.py measurements/i386/boot.log
```

## Architecture and Key Design Patterns

### Data Pipeline Architecture
The repository implements a three-stage pipeline:

1. **Extraction Stage** (`minix_source_analyzer.py`)
   - Parses C source files using regex patterns
   - Extracts: system calls, process states, memory regions, boot sequences
   - Outputs structured JSON to `diagrams/data/`

2. **Generation Stage** (`tikz_generator.py`)
   - Reads JSON data files
   - Generates TikZ LaTeX code programmatically
   - Handles special character escaping (underscores → spaces in math mode)

3. **Compilation Stage** (pdflatex + ImageMagick)
   - Compiles TikZ to vector PDF
   - Converts to raster PNG for embedding

### MCP Integration Architecture

Four-tier MCP system:

1. **MCP Servers** (Docker: docker-mcp, GitHub: gh-mcp, Hub: docker-hub-mcp)
   - Handle protocol and tool definitions
   - Provide standardized interfaces to Claude Code

2. **Docker Compose Services** (docker-compose.enhanced.yml)
   - Launch MCP servers in containers
   - Manage MINIX instances and analysis tools
   - Network isolation and resource control

3. **Error Diagnostics** (triage-minix-errors.py)
   - Automated error detection in boot logs
   - Pattern matching against MINIX-Error-Registry.md
   - Confidence scoring and recommendation ranking

4. **Smart Launchers** (minix-qemu-launcher.sh, minix-boot-diagnostics.sh)
   - Auto-detect system capabilities (CPU, RAM, KVM)
   - Select optimal QEMU parameters
   - Generate boot logs for analysis

### Key Technical Challenges and Solutions

**TikZ Special Characters**: The generator must escape underscores in function names but not in file paths. Solution: context-aware replacement in `tikz_generator.py`.

**Path Structure**: MINIX source has nested structure (`/minix/minix/kernel/`). The analyzer accounts for this extra nesting level.

**Boot Error Patterns**: 15+ common MINIX boot errors documented with symptoms, root causes, and solutions. Python triage tool uses regex patterns to detect and diagnose.

## Repository Organization (Current State)

```
minix-analysis/
├── tools/                           # Analysis tools
│   ├── minix_source_analyzer.py    # Extract data from MINIX source
│   ├── tikz_generator.py           # Generate diagrams
│   └── triage-minix-errors.py      # Error diagnosis (NEW)
├── scripts/                         # Automated helpers
│   ├── minix-boot-diagnostics.sh   # System capability detection (NEW)
│   ├── minix-qemu-launcher.sh      # Interactive QEMU launcher (NEW)
│   ├── mcp-docker-setup.sh         # MCP server installation (NEW)
│   └── minix-error-recovery.sh     # Error recovery automation (NEW)
├── diagrams/
│   ├── data/                # JSON extracted from source
│   ├── tikz/                # Hand-crafted diagrams
│   └── tikz-generated/      # Data-driven diagrams
├── mcp-servers/             # Custom MCP server implementations
│   ├── boot-profiler/       # Boot profiling MCP server
│   ├── syscall-tracer/      # Syscall analysis MCP server
│   └── memory-monitor/      # Memory monitoring MCP server
├── measurements/            # Boot profiling results
│   └── minix-analysis.db    # SQLite database of measurements
├── formal-models/           # TLA+ specifications
├── benchmarks/              # Performance analysis tools
├── docker-compose.enhanced.yml  # All services + MCP servers (NEW)
├── .mcp.json               # MCP server definitions (NEW)
├── MINIX-Error-Registry.md # 15+ errors with solutions (NEW)
├── MINIX-MCP-Integration.md # Complete MCP setup guide (NEW)
└── *.md                    # 47 documentation files + new additions
```

## Common Development Tasks

### Adding New Source Analysis
1. Extend `MinixAnalyzer` class in `minix_source_analyzer.py`
2. Add new extraction method following pattern:
   ```python
   def analyze_new_component(self):
       data = {"key": []}
       # Parse source files
       # Extract patterns
       return data
   ```
3. Export in `export_all_data()` method
4. Create corresponding TikZ generator method

### Creating New Diagram Types
1. Add generation method to `TikZGenerator` class
2. Follow naming pattern: `generate_*_tikz()`
3. Handle special characters (underscores, backslashes)
4. Add to `save_all_tikz_files()` dictionary

### Debugging TikZ Compilation Failures
```bash
# Check specific error
pdflatex diagram.tex  # Interactive mode shows exact line

# Common fixes:
# - Replace underscores in text mode
# - Escape backslashes in labels
# - Ensure math mode for subscripts
```

### Running MINIX Boot Tests with Error Diagnosis

```bash
# 1. Start launcher
./scripts/minix-qemu-launcher.sh boot

# 2. Monitor boot log
tail -f measurements/boot-*.log

# 3. Analyze errors
python3 tools/triage-minix-errors.py measurements/boot-*.log

# 4. View full registry
cat MINIX-Error-Registry.md | grep "^### Error"
```

## Testing and Validation

### Data Accuracy Verification
```bash
# Verify extracted metrics match reality
ls /home/eirikr/Playground/minix/minix/kernel/system/do_*.c | wc -l
# Should match syscall count in statistics.json
```

### Diagram Compilation Test
```bash
cd diagrams/tikz-generated
for tex in *.tex; do
    pdflatex -interaction=nonstopmode "$tex" > /dev/null 2>&1 && \
    echo "✓ $tex" || echo "✗ $tex"
done
```

### MINIX Boot Validation
```bash
# Run diagnostics
./scripts/minix-boot-diagnostics.sh

# Quick boot test
timeout 120 ./scripts/minix-qemu-launcher.sh boot

# Full error check
python3 tools/triage-minix-errors.py measurements/boot-*.log
```

### MCP Integration Tests
```bash
# Verify Docker MCP
docker-compose -f docker-compose.enhanced.yml ps

# Test error diagnosis pipeline
python3 tools/triage-minix-errors.py measurements/i386/boot.log --output /tmp/errors.json

# Query measurements
python3 -c "
import json
with open('/tmp/errors.json') as f:
    errors = json.load(f)
print(f'Errors detected: {len(errors[\"errors\"])}')"
```

## Planned Modularization

The repository is being reorganized into:
1. **os-analysis-toolkit/** - General OS analysis tools (reusable)
2. **minix-specific-tools/** - MINIX-specific analyzers and configs
3. **minix-whitepaper/** - LaTeX publication materials
4. **minix-pedagogical/** - Educational materials and exercises
5. **minix-mcp-integration/** - MCP servers and automation scripts

When implementing modularization:
- Preserve git history with `git mv`
- Update import paths in Python files
- Adjust relative paths in scripts
- Test full pipeline after each move

## Performance Considerations

- **Source Analysis**: ~20 seconds for full MINIX kernel (91 files, 19K lines)
- **TikZ Generation**: < 1 second for 5 diagrams
- **PDF Compilation**: ~2 seconds per diagram
- **PNG Conversion**: ~1 second per diagram at 150 DPI
- **Error Triage**: < 500ms for typical boot log (< 10MB)
- **Docker Container Startup**: < 5 seconds (with KVM) or < 30 seconds (without)

For large-scale analysis, consider:
- Caching JSON data (check timestamps)
- Parallel PDF compilation
- Batch PNG conversion
- Docker layer caching for faster builds

## Integration with MINIX Source

The tools assume MINIX source structure:
```
/home/eirikr/Playground/minix/
└── minix/               # Extra nesting level!
    ├── kernel/
    │   ├── system/      # System calls (do_*.c)
    │   └── proc.h       # Process definitions
    ├── servers/         # User-space servers
    └── include/         # Header files
```

Always verify paths when working with different MINIX versions or forks.

## Error Recovery

If analysis fails:
1. Check MINIX source path exists and is readable
2. Verify Python 3.6+ (for f-strings and Path)
3. Ensure pdflatex is installed (texlive-full recommended)
4. Confirm ImageMagick 7+ for PNG conversion

Common issues:
- **Empty JSON files**: Source path incorrect or permissions issue
- **TikZ compilation fails**: Special character escaping needed
- **PNG conversion fails**: Use `magick` not deprecated `convert`

### MINIX Boot Errors

Consult **MINIX-Error-Registry.md** for 15+ documented errors:

**Quick Lookup**:
- **E003**: CD9660 module load failure (use RC6+ ISO or build from source)
- **E002**: SeaBIOS hang (use `-cpu kvm32` instead of host)
- **E006**: IRQ check failed (configure NE2K IRQ 3, I/O 0x300)
- **E001**: Blank screen (add `-sdl` or use `-serial file:boot.log -nographic`)

**Automated Diagnosis**:
```bash
python3 tools/triage-minix-errors.py boot.log
# Shows: detected errors, confidence levels, recommended fixes
```

## Using MCP with Claude Code

### Enable MCP Servers

```bash
# Export credentials
export GITHUB_TOKEN="ghp_YourTokenHere"
export DOCKER_HUB_USERNAME="your-docker-username"
export DOCKER_HUB_TOKEN="dckr_YourTokenHere"

# Start services
docker-compose -f docker-compose.enhanced.yml up -d

# Verify status
docker-compose -f docker-compose.enhanced.yml ps
```

### Test MCP in Claude Code

```
Test Docker MCP: Can you list the containers currently running?

Test GitHub MCP: What issues are in the minix-analysis repository?

Test error diagnosis: Fetch the boot log from minix-rc6-i386 and 
analyze it for errors using the triage tool.
```

### Common MCP Workflows

**1. Boot and Diagnose**
```
1. Start minix-rc6-i386 container
2. Fetch boot log
3. Run error triage
4. Create GitHub issue if errors found
```

**2. Performance Analysis**
```
1. Boot with different CPU counts (1, 2, 4, 8)
2. Measure boot time for each
3. Insert to SQLite database
4. Query scaling efficiency
```

**3. Error Recovery**
```
1. Detect error in boot log (e.g., E006)
2. Look up solution in MINIX-Error-Registry.md
3. Modify docker-compose.yml with fix
4. Restart container
5. Verify success, log to GitHub
```

### See Also

- **MINIX-MCP-Integration.md** - Complete setup and reference
- **MINIX-Error-Registry.md** - 15+ error solutions
- **docker-compose.enhanced.yml** - All services configuration
- **.mcp.json** - MCP server definitions

## Next Steps for New Sessions

1. Read this entire CLAUDE.md
2. Enable MCP: `export GITHUB_TOKEN=... && docker-compose up -d`
3. Test in Claude Code: "List my Docker containers"
4. Run MINIX: `./scripts/minix-qemu-launcher.sh`
5. Diagnose errors: `python3 tools/triage-minix-errors.py measurements/boot-*.log`
6. Refer to error registry as needed
7. Use MCP to create GitHub issues and track progress
