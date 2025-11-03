# MINIX Analysis: Installation Requirements and Dependencies

**Version**: 1.1.0
**Last Updated**: 2025-10-30
**Maintainer**: Oaich (eirikr)
**Platform**: Linux (CachyOS/Arch preferred), macOS supported

---

## I. Executive Summary

This document specifies **complete installation requirements** for the MINIX Analysis umbrella project, covering all modules, shared infrastructure, build tools, and runtime dependencies.

**Quick Start for CachyOS/Arch**:
```bash
sudo pacman -S texlive-core texlive-latexextra python python-pip graphviz
git clone <repo-url> && cd minix-analysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```

---

## II. System Requirements

### A. Operating System

**Supported Platforms**:
1. **Linux** (PRIMARY)
   - CachyOS (recommended)
   - Arch Linux
   - Debian/Ubuntu (tested)
   - Fedora/RHEL (should work)

2. **macOS** (SECONDARY)
   - macOS 12+ (Monterey or later)
   - Homebrew required

**Unsupported**:
- Windows (WSL2 may work but not tested)

---

### B. Core System Dependencies

#### 1. LaTeX Distribution

**TeX Live 2023 or later** (REQUIRED)

**CachyOS/Arch**:
```bash
sudo pacman -S texlive-core texlive-bin texlive-latexextra texlive-pictures
```

**Ubuntu/Debian**:
```bash
sudo apt install texlive-full texlive-latex-extra texlive-pictures
```

**macOS (Homebrew)**:
```bash
brew install --cask mactex
# OR for minimal install:
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install collection-latexextra collection-pictures
```

**Verify Installation**:
```bash
pdflatex --version  # Should show TeX Live 2023 or later
```

**Required LaTeX Packages**:
- tikz (vector graphics)
- pgfplots (plotting)
- xcolor (color support)
- hyperref (PDF links)
- cleveref (smart references)
- amsmath, amssymb (mathematics)
- algorithm, algpseudocode (algorithms)
- booktabs (professional tables)
- listings (code listings)
- geometry (page layout)
- fontenc, inputenc (fonts and encoding)

---

#### 2. Python Environment

**Python 3.10 or later** (REQUIRED)

**CachyOS/Arch**:
```bash
sudo pacman -S python python-pip python-virtualenv
```

**Ubuntu/Debian**:
```bash
sudo apt install python3 python3-pip python3-venv
```

**macOS**:
```bash
brew install python@3.12
```

**Verify Installation**:
```bash
python --version  # Should show Python 3.10+
pip --version
```

---

#### 3. Build Tools

**Make** (REQUIRED)

**CachyOS/Arch**:
```bash
sudo pacman -S make
```

**Ubuntu/Debian**:
```bash
sudo apt install build-essential
```

**macOS**:
```bash
xcode-select --install  # Includes make
```

**Verify Installation**:
```bash
make --version  # Should show GNU Make 4.0+
```

---

#### 4. Git Version Control

**Git 2.30+** (REQUIRED)

**CachyOS/Arch**:
```bash
sudo pacman -S git
```

**Ubuntu/Debian**:
```bash
sudo apt install git
```

**macOS**:
```bash
brew install git
```

---

#### 5. Graphviz (Optional)

**For call graph visualization** (RECOMMENDED)

**CachyOS/Arch**:
```bash
sudo pacman -S graphviz
```

**Ubuntu/Debian**:
```bash
sudo apt install graphviz
```

**macOS**:
```bash
brew install graphviz
```

---

## III. Python Dependencies

### A. Root Project Dependencies

**File**: `requirements.txt` (root level)

```
# Core MCP dependencies
mcp>=0.9.0
anthropic>=0.39.0

# Documentation generation
mkdocs>=1.5.0
mkdocs-material>=9.4.0
mkdocs-mermaid2-plugin>=1.1.0

# Analysis tools
networkx>=3.2
matplotlib>=3.8.0
numpy>=1.26.0
pandas>=2.1.0

# Development tools
pytest>=7.4.0
black>=23.10.0
flake8>=6.1.0
mypy>=1.6.0

# Utilities
pyyaml>=6.0
toml>=0.10.2
click>=8.1.0
jinja2>=3.1.0
```

**Installation**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### B. Module-Specific Dependencies

#### 1. CPU Interface Module

**File**: `modules/cpu-interface/requirements.txt`

```
# Inherit from root
-r ../../requirements.txt

# CPU-specific analysis
capstone>=5.0.0      # Disassembly
pyelftools>=0.30     # ELF parsing
```

**Installation**:
```bash
pip install -r modules/cpu-interface/requirements.txt
```

---

#### 2. Boot Sequence Module

**File**: `modules/boot-sequence/requirements.txt`

```
# Inherit from root
-r ../../requirements.txt

# Boot analysis tools
pygraphviz>=1.11     # Graph visualization (requires graphviz)
pydot>=1.4.2         # DOT file generation
```

**Installation**:
```bash
pip install -r modules/boot-sequence/requirements.txt
```

---

## IV. Optional Dependencies

### A. Documentation Tools

**MkDocs Wiki Generation** (OPTIONAL)

Already included in `requirements.txt`, but additional plugins:

```bash
pip install mkdocs-redirects mkdocs-minify-plugin
```

---

### B. Development Tools

**Code Quality** (OPTIONAL but RECOMMENDED)

```bash
pip install pylint autopep8 isort pre-commit
```

**Shell Script Validation** (RECOMMENDED)

**CachyOS/Arch**:
```bash
sudo pacman -S shellcheck shfmt
```

**Ubuntu/Debian**:
```bash
sudo apt install shellcheck
# shfmt: download from https://github.com/mvdan/sh/releases
```

**macOS**:
```bash
brew install shellcheck shfmt
```

---

### C. MCP Testing

**For MCP server development** (OPTIONAL)

```bash
pip install mcp-server-test mcp-client
```

---

## V. MINIX Source Code (Optional)

**Required for**: Re-running boot sequence analysis tools

**Not required for**: Building papers, using MCP server, wiki generation

**Installation**:
```bash
git clone https://github.com/Stichting-MINIX-Research-Foundation/minix.git
export MINIX_SRC=/path/to/minix
```

**Note**: Boot analysis outputs are pre-generated and committed to repo

---

## VI. Installation Procedures

### A. Standard Installation (End Users)

```bash
# 1. Clone repository
git clone https://github.com/eirikr/minix-analysis.git
cd minix-analysis

# 2. Install system dependencies (Arch example)
sudo pacman -S texlive-core texlive-latexextra python graphviz

# 3. Create Python virtual environment
python -m venv .venv
source .venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Verify installation
make status

# 6. Build all modules
make all

# 7. (Optional) Install shared styles system-wide
sudo make install
```

---

### B. Developer Installation

**Includes dev tools, testing, and pre-commit hooks**

```bash
# Follow steps 1-4 from Standard Installation, then:

# 5. Install development dependencies
pip install -r requirements-dev.txt

# 6. Install pre-commit hooks
pre-commit install

# 7. Validate shell scripts
shellcheck -S error modules/*/pipeline/*.sh

# 8. Run tests
make test
```

---

### C. MCP Server Only

**For using the MINIX Analysis MCP tools without building papers**

```bash
# 1. Clone repository
git clone https://github.com/eirikr/minix-analysis.git
cd minix-analysis

# 2. Install Python dependencies only
python -m venv .venv
source .venv/bin/activate
pip install mcp anthropic

# 3. Start MCP server
cd mcp/servers/minix-analysis
python -m src.server
```

---

## VII. Verification Steps

### A. System Dependencies

```bash
# LaTeX
pdflatex --version | head -1

# Python
python --version

# Make
make --version | head -1

# Git
git --version

# Graphviz (optional)
dot -V
```

**Expected Output**:
```
pdfTeX 3.141592653-2.6-1.40.25 (TeX Live 2023)
Python 3.12.0
GNU Make 4.4.1
git version 2.43.0
dot - graphviz version 2.50.0
```

---

### B. Python Dependencies

```bash
# Activate virtualenv first
source .venv/bin/activate

# Verify core packages
python -c "import mcp; print(f'MCP: {mcp.__version__}')"
python -c "import mkdocs; print(f'MkDocs: {mkdocs.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
```

---

### C. Build System

```bash
# Test root Makefile
make help

# Test CPU module
make cpu 2>&1 | tee cpu-build.log

# Test Boot module
make boot 2>&1 | tee boot-build.log

# Check for errors
grep -i error cpu-build.log boot-build.log
```

---

### D. MCP Server

```bash
# Test server startup
cd mcp/servers/minix-analysis
timeout 5s python -m src.server || echo "Server started OK (timeout expected)"

# Test module imports
python -c "from modules.cpu_interface.mcp.cpu_data_loader import CPUDataLoader; print('CPU: OK')"
python -c "from modules.boot_sequence.mcp.boot_data_loader import BootDataLoader; print('Boot: OK')"
```

---

## VIII. Troubleshooting

### A. LaTeX Issues

**Problem**: `minix-styles.sty not found`

**Solutions**:
1. **Local use**: LaTeX files use relative paths (`../../shared/styles/minix-styles.sty`)
2. **System-wide**: Run `sudo make install` to install to `/usr/share/texmf/tex/latex/minix/`
3. **TEXINPUTS**: Set environment variable:
   ```bash
   export TEXINPUTS=.:./shared/styles//:$TEXINPUTS
   ```

---

**Problem**: `! Package xcolor Error: Undefined color 'phase1'`

**Solution**: Ensure LaTeX file has:
```latex
\usepackage{../../shared/styles/minix-colors}
```

---

### B. Python Import Errors

**Problem**: `ModuleNotFoundError: No module named 'shared'`

**Solutions**:
1. **Add to PYTHONPATH**:
   ```bash
   export PYTHONPATH=/path/to/minix-analysis:$PYTHONPATH
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

---

**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**: Install MCP:
```bash
pip install mcp
```

---

### C. Build Failures

**Problem**: `make: *** No rule to make target 'cpu'. Stop.`

**Solution**: Check that `modules/cpu-interface/Makefile` exists

---

**Problem**: `pdflatex: command not found`

**Solution**: Install TeX Live (see Section II.B.1)

---

### D. MCP Server Issues

**Problem**: Server won't start, import errors

**Solutions**:
1. Check PYTHONPATH includes project root
2. Verify module structure:
   ```bash
   ls modules/*/mcp/*.py
   ```
3. Check for syntax errors:
   ```bash
   python -m py_compile modules/*/mcp/*.py
   ```

---

## IX. Platform-Specific Notes

### A. CachyOS/Arch Linux

**Optimizations**:
- Use x86-64-v3 optimized packages where available
- TeX Live from repos is recent (2023+)
- Python 3.12+ in repos

**AUR Packages** (optional):
```bash
yay -S texlive-localmanager-git  # For easier TeX package management
```

---

### B. macOS

**Homebrew Caveats**:
- BasicTeX is minimal; full MacTeX recommended for this project
- Python from Homebrew may conflict with system Python
- Use `python3` and `pip3` explicitly

**Path Issues**:
```bash
# Add TeX Live to PATH (if using MacTeX)
export PATH="/Library/TeX/texbin:$PATH"
```

---

### C. Ubuntu/Debian

**Outdated Packages**:
- Ubuntu repos may have older TeX Live (2021)
- Consider installing TeX Live from upstream if necessary:
  ```bash
  wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
  tar xzf install-tl-unx.tar.gz
  cd install-tl-*
  sudo ./install-tl
  ```

---

## X. Minimal vs. Full Installation

### A. Minimal Installation (Papers Only)

**Use case**: Build PDFs, no MCP/wiki

**Requirements**:
- TeX Live (core + latexextra)
- Make
- Git

**Size**: ~1.5 GB (mostly TeX Live)

---

### B. Full Installation (All Features)

**Use case**: Development, MCP server, wiki generation, analysis tools

**Requirements**:
- All from Minimal
- Python 3.10+ with all dependencies
- Graphviz
- MINIX source (optional)

**Size**: ~2.5 GB (TeX Live + Python packages + MINIX source)

---

## XI. Dependency Versions (Tested Configurations)

### Configuration 1: CachyOS (2025-10-30)

```
OS: CachyOS (Arch Linux base)
Kernel: linux-cachyos 6.11.5
TeX Live: 2024.20241107
Python: 3.12.7
Make: 4.4.1
Git: 2.47.0
Graphviz: 12.2.0
```

**Status**: ✅ Fully tested and working

---

### Configuration 2: Ubuntu 24.04 LTS

```
OS: Ubuntu 24.04 LTS
TeX Live: 2023.20230311
Python: 3.12.3
Make: 4.3
Git: 2.43.0
Graphviz: 2.43.0
```

**Status**: ⚠️  Should work (not tested recently)

---

### Configuration 3: macOS 14 (Sonoma)

```
OS: macOS 14.7
TeX Live: 2024 (MacTeX)
Python: 3.12.6 (Homebrew)
Make: 3.81 (Xcode)
Git: 2.39.3
Graphviz: 12.1.2 (Homebrew)
```

**Status**: ⚠️  Should work (not tested recently)

---

## XII. Continuous Integration

**GitHub Actions** (planned):

```yaml
# .github/workflows/build.yml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install TeX Live
        run: sudo apt-get install -y texlive-full
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Build papers
        run: make all
      - name: Run tests
        run: make test
```

---

## XIII. Dependency Licenses

**System Tools**:
- TeX Live: Mix of free licenses (LaTeX Project Public License, etc.)
- Python: Python Software Foundation License
- Make: GNU GPL v3
- Git: GNU GPL v2
- Graphviz: Eclipse Public License

**Python Packages**:
- MCP: MIT License
- mkdocs: BSD License
- pandas/numpy: BSD License
- matplotlib: PSF License
- pytest: MIT License

**Project License**: MIT License (see root LICENSE file)

---

## XIV. Support and Resources

### Documentation
- **Root README**: `/README.md`
- **Architecture**: `/UMBRELLA-ARCHITECTURE.md`
- **Migration Plan**: `/MIGRATION-PLAN.md`
- **Audit Report**: `/DEEP-AUDIT-REPORT.md`
- **Capabilities**: `/CAPABILITIES-AND-TOOLS.md`

### Getting Help
1. Check `TROUBLESHOOTING.md` (if exists)
2. Review module-specific READMEs
3. Search GitHub issues
4. Create new issue with:
   - OS and version
   - Output of `make status`
   - Relevant error logs

### Contributing
See `CONTRIBUTING.md` for guidelines on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process

---

## XV. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-30 | Initial requirements documentation |
| 1.1.0 | 2025-10-30 | Added troubleshooting, platform notes, tested configs |

---

**AD ASTRA PER MATHEMATICA ET SCIENTIAM**

*Dependencies documented. Installation validated. Build system ready.*
