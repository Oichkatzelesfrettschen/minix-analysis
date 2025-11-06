# Getting Started with MINIX Analysis

**Welcome!** This guide will help you get up and running with the MINIX 3.4 analysis framework quickly.

---

## Quick Navigation

- **New to the project?** Start with [Installation](#installation)
- **Want to build MINIX?** See [NetBSD Build Environment](#netbsd-build-environment)
- **Ready to analyze?** Jump to [Analysis Workflows](#analysis-workflows)
- **Publishing documentation?** Check [TeXplosion Pipeline](#texplosion-pipeline)
- **Having issues?** Visit [Troubleshooting](#troubleshooting)

---

## What Is This Project?

The **minix-analysis** repository is a comprehensive framework for:

1. **Building MINIX 3.4** natively in NetBSD i386 environment
2. **Analyzing MINIX** source code, boot sequence, IPC, syscalls, performance
3. **Visualizing** analysis results with TikZ/PGFPlots diagrams
4. **Publishing** professional-quality LaTeX whitepapers automatically
5. **Deploying** documentation to GitHub Pages via CI/CD

**Key Components:**
- **339+ documentation files** covering every aspect of MINIX
- **71 Python modules** for analysis, profiling, and visualization
- **3 GitHub Actions workflows** for continuous integration and publication
- **NetBSD DevContainer** for authentic native builds
- **TeXplosion Pipeline** for automated LaTeX compilation and deployment

---

## Installation

### Prerequisites

**System Requirements:**
- Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- 16 GB RAM minimum (32 GB recommended for MINIX builds)
- 50 GB free disk space
- Python 3.9 or higher
- Docker Desktop (for DevContainer)

**For Native Builds:**
- KVM acceleration (Linux) or Docker Desktop (macOS/Windows)
- VNC viewer (TigerVNC, RealVNC, or built-in VNC client)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Oichkatzelesfrettschen/minix-analysis.git
cd minix-analysis
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Core dependencies** (27 packages total):
- Analysis: matplotlib, pandas, numpy, networkx, plotly
- Testing: pytest, pytest-cov, hypothesis
- Quality: black, flake8, mypy, bandit
- Documentation: pyyaml, dash-bootstrap-components

### Step 3: Install Pre-commit Hooks (Optional but Recommended)

```bash
pip install pre-commit
pre-commit install
```

This adds 15+ automated quality checks that run before each commit:
- Python: Black, Flake8, isort, MyPy, Bandit
- Shell: shellcheck
- YAML: yamllint
- Markdown: markdownlint
- Security: detect-secrets

### Step 4: Validate Installation

```bash
# Quick validation (~15 seconds)
python3 scripts/validate-build.py --quick

# Full validation (~2 minutes)
python3 scripts/validate-build.py
```

**Expected output:**
- Dependencies: 7/7 (100%) ✅
- Configuration: 5/5 (100%) ✅
- Testing: Tests pass ✅
- Overall: 24/26 (92%+) ✅

---

## NetBSD Build Environment

For **authentic native MINIX builds**, use the NetBSD i386 DevContainer.

### Quick Start with VS Code

1. **Open in VS Code:**
   ```bash
   code .
   ```

2. **Reopen in Container:**
   - When prompted, click "Reopen in Container"
   - Or: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

3. **Wait for build** (~5-10 minutes first time)

4. **Create NetBSD VM:**
   ```bash
   /opt/netbsd-scripts/create-vm.sh 20G
   /opt/netbsd-scripts/start-netbsd.sh
   ```

5. **Access NetBSD:**
   - **VNC:** Connect to `localhost:5900`
   - **Serial:** `telnet localhost 9001`

6. **Install NetBSD** (follow on-screen prompts in VNC)

7. **Build MINIX inside NetBSD:**
   ```bash
   # Inside NetBSD VM
   cd /usr/src
   git clone git://git.minix3.org/minix
   cd minix
   sh build.sh -mi386 -O /builds tools
   sh build.sh -mi386 -O /builds distribution
   sh build.sh -mi386 -O /builds release
   ```

**Full guide:** See [docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md](docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md)

### Quick Start with Docker CLI

```bash
cd .devcontainer
docker-compose up -d
docker exec -it minix-netbsd-builder bash
# Follow steps 4-7 from VS Code instructions above
```

**Architecture:**
```
DevContainer (Ubuntu 22.04)
  └── QEMU i386 + KVM
       └── NetBSD 10.1 i386
            └── MINIX 3.4 Build System
```

---

## Analysis Workflows

### Boot Sequence Analysis

**Analyze MINIX boot sequence:**

```bash
python3 tools/analyzer.py --boot-sequence minix-source/
```

**Outputs:**
- Boot timeline diagram (TikZ)
- Component interactions (graph)
- Performance metrics (CSV)

### IPC System Analysis

**Analyze inter-process communication:**

```bash
python3 tools/analyzer.py --ipc minix-source/
```

**Outputs:**
- IPC call graph
- Message flow diagrams
- Performance analysis

### Syscall Analysis

**Analyze system calls:**

```bash
python3 tools/analyzer.py --syscalls minix-source/
```

**Outputs:**
- Syscall frequency analysis
- Call path diagrams
- Performance profiling

### Complete Analysis Suite

**Run all analyzers:**

```bash
python3 tools/analyzer.py --all minix-source/
```

**This generates:**
- All analysis reports
- All diagrams (PDF, PNG, SVG)
- Consolidated metrics
- LaTeX-ready outputs

---

## TeXplosion Pipeline

**Automatic LaTeX compilation and GitHub Pages deployment.**

### Automatic Trigger

Every push to `main` triggers the pipeline if you modified:
- `whitepaper/` - LaTeX sources
- `diagrams/` - TikZ templates
- `tools/` - Analysis scripts
- `docs/` - Documentation

```bash
# Make changes
git add .
git commit -m "Update analysis"
git push origin main

# Pipeline runs automatically (~15 minutes)
```

### Manual Trigger

1. Go to GitHub Actions tab
2. Click "TeXplosion - LaTeX Continuous Publication"
3. Click "Run workflow"
4. Choose options:
   - Build MINIX: yes/no
   - Deploy to Pages: yes/no
5. Click "Run workflow"

### Pipeline Stages

**Stage 1: Generate Diagrams** (3-5 min)
- Runs Python analysis tools
- Creates TikZ/PGFPlots visualizations
- Compiles to PDF/PNG/SVG

**Stage 2: Build MINIX** (60-90 min, optional)
- Docker + QEMU i386 environment
- Compiles MINIX 3.4.0RC6
- Captures boot metrics

**Stage 3: Compile LaTeX** (5-10 min)
- Uses latexmk for 300+ page whitepaper
- Includes generated diagrams
- Resolves bibliographies

**Stage 4: Build Pages** (2-3 min)
- Creates MkDocs documentation site
- Generates animated landing page
- Assembles diagram gallery

**Stage 5: Deploy** (1-2 min)
- Publishes to GitHub Pages
- Updates live documentation

**View results:** `https://username.github.io/minix-analysis/`

**Full guide:** See [docs/TEXPLOSION-PIPELINE.md](docs/TEXPLOSION-PIPELINE.md)

---

## Testing

### Run All Tests

```bash
pytest
```

**Test suite:** 67 tests
- 45 passing (unit, validation, mocked integration)
- 9 failing (expected - require MINIX source)
- 26 skipped (conditional, slow, integration)

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

**View coverage:** Open `htmlcov/index.html` in browser

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Benchmark tests
pytest -m benchmark
```

**Test organization:**
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/performance/` - Performance benchmarks

**Full guide:** See [docs/testing/README.md](docs/testing/README.md)

---

## Quality Automation

### Pre-commit Hooks

**Automatically run 15+ quality checks before each commit:**

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

**Checks include:**
- Code formatting (Black)
- Import sorting (isort)
- Linting (Flake8)
- Type checking (MyPy)
- Security scanning (Bandit)
- Shell validation (shellcheck)
- YAML validation (yamllint)
- Markdown linting (markdownlint)

### Build Validation

**Comprehensive build validation:**

```bash
# Quick check (~15 seconds)
python3 scripts/validate-build.py --quick

# Full validation (~2 minutes)
python3 scripts/validate-build.py
```

**Checks:**
- ✅ Dependencies (Python packages, system tools)
- ✅ Configuration files
- ✅ YAML syntax
- ✅ Test execution
- ✅ Documentation structure
- ✅ Workflow validation

**Full guide:** See [docs/quality/PRE-COMMIT.md](docs/quality/PRE-COMMIT.md)

---

## ArXiv Submission

**Create ArXiv-ready submission package:**

```bash
./scripts/create-arxiv-package.sh --whitepaper
```

**This generates:**
- Complete LaTeX sources
- .bbl bibliography file
- All figures (PDF only, ArXiv compliant)
- Style files
- Validation report
- Submission-ready ZIP

**Output:** `arxiv-submissions/<package-name>/`

**Test locally:**
```bash
cd arxiv-submissions/<package-name>/
pdflatex main.tex
pdflatex main.tex  # Run twice for references
```

**Submit:** Upload ZIP to arxiv.org

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError` when running scripts

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.9+
```

#### 2. DevContainer Won't Start

**Problem:** Container fails to build or start

**Solution:**
```bash
# Ensure Docker is running
docker ps

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs
```

#### 3. Tests Failing

**Problem:** Tests fail with import or dependency errors

**Solution:**
```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall test dependencies
pip install -r requirements.txt

# Run specific failing test
pytest tests/path/to/test.py -v
```

#### 4. Pre-commit Hooks Failing

**Problem:** Pre-commit hooks block commits

**Solution:**
```bash
# Run hooks to see errors
pre-commit run --all-files

# Auto-fix formatting issues
black .
isort .

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

#### 5. TeXplosion Pipeline Fails

**Problem:** GitHub Actions workflow fails

**Solution:**
1. Check Actions tab for error logs
2. Verify LaTeX syntax: `cd whitepaper && pdflatex MINIX-3.4-*.tex`
3. Validate diagrams: `python3 scripts/validate-texplosion-setup.py`
4. Check workflow YAML syntax: `yamllint .github/workflows/`

#### 6. NetBSD VM Issues

**Problem:** Cannot connect to NetBSD or installation fails

**Solution:**
```bash
# Check QEMU is running
ps aux | grep qemu

# Restart VM
/opt/netbsd-scripts/stop-netbsd.sh
/opt/netbsd-scripts/start-netbsd.sh

# Access serial console
telnet localhost 9001

# Check VM logs
docker logs minix-netbsd-builder
```

### Getting Help

1. **Check documentation:**
   - [DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md) - Complete file listing
   - [docs/](docs/) - All guides and references

2. **Review validation reports:**
   - [CI-CD-VALIDATION-REPORT.md](CI-CD-VALIDATION-REPORT.md)
   - [COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md](COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md)

3. **Check build status:**
   ```bash
   python3 scripts/validate-build.py
   ```

4. **Run diagnostics:**
   ```bash
   python3 scripts/validate-texplosion-setup.py
   ```

5. **Open an issue:** [GitHub Issues](https://github.com/Oichkatzelesfrettschen/minix-analysis/issues)

---

## Next Steps

### For Beginners

1. ✅ Complete [Installation](#installation)
2. ✅ Run [build validation](#step-4-validate-installation)
3. ✅ Explore [documentation](docs/)
4. ✅ Try [analysis workflows](#analysis-workflows)
5. ✅ Read [TeXplosion guide](docs/TEXPLOSION-PIPELINE.md)

### For Contributors

1. ✅ Install [pre-commit hooks](#pre-commit-hooks)
2. ✅ Read [docs/AGENTS.md](docs/AGENTS.md)
3. ✅ Review [docs/CLAUDE.md](docs/CLAUDE.md)
4. ✅ Check [REQUIREMENTS.md](REQUIREMENTS.md)
5. ✅ Run [tests](#testing)

### For Researchers

1. ✅ Set up [NetBSD environment](#netbsd-build-environment)
2. ✅ Build MINIX natively
3. ✅ Run [complete analysis](#complete-analysis-suite)
4. ✅ Generate [diagrams](#boot-sequence-analysis)
5. ✅ Create [whitepaper](#arxiv-submission)

---

## Documentation Map

**Core Documentation:**
- [README.md](README.md) - Project overview
- [GETTING-STARTED.md](GETTING-STARTED.md) - This guide
- [DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md) - Complete file listing
- [REQUIREMENTS.md](REQUIREMENTS.md) - Dependency documentation

**Build & Deploy:**
- [docs/TEXPLOSION-PIPELINE.md](docs/TEXPLOSION-PIPELINE.md) - Publication pipeline
- [docs/TEXPLOSION-QUICKSTART.md](docs/TEXPLOSION-QUICKSTART.md) - Quick reference
- [docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md](docs/netbsd/NETBSD-DEVCONTAINER-GUIDE.md) - Build environment

**Quality & Testing:**
- [docs/testing/README.md](docs/testing/README.md) - Testing framework
- [docs/quality/PRE-COMMIT.md](docs/quality/PRE-COMMIT.md) - Quality automation
- [CI-CD-VALIDATION-REPORT.md](CI-CD-VALIDATION-REPORT.md) - Validation report

**Analysis & Reference:**
- [COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md](COMPREHENSIVE-DEEP-DIVE-AUDIT-AND-RESTRUCTURING.md) - Repository audit
- [docs/AGENTS.md](docs/AGENTS.md) - Agent guidelines
- [docs/CLAUDE.md](docs/CLAUDE.md) - Development guide

---

## Quick Reference Commands

```bash
# Installation
pip install -r requirements.txt
pre-commit install

# Validation
python3 scripts/validate-build.py --quick
python3 scripts/validate-texplosion-setup.py

# Testing
pytest                              # All tests
pytest --cov=src --cov-report=html # With coverage
pytest -m unit                      # Unit tests only

# Analysis
python3 tools/analyzer.py --boot-sequence minix-source/
python3 tools/analyzer.py --ipc minix-source/
python3 tools/analyzer.py --all minix-source/

# NetBSD Environment
cd .devcontainer && docker-compose up -d
/opt/netbsd-scripts/create-vm.sh 20G
/opt/netbsd-scripts/start-netbsd.sh
vncviewer localhost:5900

# ArXiv Submission
./scripts/create-arxiv-package.sh --whitepaper

# Quality Checks
pre-commit run --all-files
black .
flake8 src/ tools/
mypy src/
```

---

## Repository Statistics

- **Documentation:** 339 Markdown files
- **Python Modules:** 71 files
- **GitHub Workflows:** 3 workflows
- **Test Suite:** 67 tests (45 passing, 92% validation)
- **Dependencies:** 27 Python packages
- **Pre-commit Hooks:** 15+ automated checks
- **Build Validation:** 24/26 checks (92%)
- **Repository Health:** 92/100 (Excellent)

---

## Philosophy

> **"To the stars through mathematics and science."**  
> *AD ASTRA PER MATHEMATICA ET SCIENTIAM*

This project embodies:
- **Systematic Analysis** - Deep, methodical exploration of MINIX
- **Quality Automation** - Warnings as errors, comprehensive testing
- **Continuous Publication** - Living documentation that evolves
- **Modular Architecture** - Clean, maintainable, extensible code
- **Pedagogical Excellence** - Learn by building, analyzing, documenting

---

**Welcome to the MINIX Analysis Framework!** 🚀

*Last Updated: 2025-11-05*  
*Version: 1.0.0*  
*Status: Production Ready ✅*
