# MINIX Analysis Project - Requirements Documentation

**Version:** 1.0.0  
**Last Updated:** 2025-11-04  
**Status:** Production

---

## Overview

This document provides a comprehensive guide to all dependencies, requirements, and prerequisites for the MINIX Analysis project. It consolidates information from multiple `requirements.txt` files and provides context for each dependency.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Dependencies](#python-dependencies)
3. [LaTeX Requirements](#latex-requirements)
4. [Build Tools](#build-tools)
5. [Optional Components](#optional-components)
6. [Installation Guide](#installation-guide)
7. [Dependency Rationale](#dependency-rationale)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum System Specifications

- **OS:** Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+ (WSL2)
- **CPU:** 2+ cores (4+ recommended for QEMU builds)
- **RAM:** 4 GB minimum (8 GB+ recommended)
- **Disk:** 10 GB free space (50 GB+ for MINIX source builds)
- **Python:** 3.7+ (3.9+ recommended)

### Required System Packages

**Ubuntu/Debian:**
```bash
sudo apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-venv \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-pictures \
    texlive-fonts-recommended \
    imagemagick \
    ghostscript \
    latexmk
```

**macOS (via Homebrew):**
```bash
brew install \
    python@3.9 \
    texlive \
    imagemagick \
    ghostscript
```

**Windows (WSL2):**
Follow Ubuntu instructions within WSL2 environment.

---

## Python Dependencies

### Core Dependencies

**File:** `requirements.txt` (root)

#### Analysis and Visualization
```python
matplotlib>=3.7.0    # Plotting and visualization
pandas>=2.0.0        # Data analysis and manipulation
numpy>=1.24.0        # Numerical computing
plotly>=5.15.0       # Interactive visualizations
dash>=2.11.0         # Dashboard creation
```

**Rationale:** These packages form the foundation for MINIX source analysis, data extraction, and diagram generation.

#### Testing Framework
```python
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reporting
pytest-benchmark>=4.0.0 # Performance benchmarking
pytest-timeout>=2.1.0   # Test timeout management
pytest-xdist>=3.3.0     # Parallel test execution
hypothesis>=6.82.0      # Property-based testing
```

**Rationale:** Comprehensive testing infrastructure for quality assurance.

#### Development Tools
```python
black>=23.7.0        # Code formatting
flake8>=6.1.0        # Linting
mypy>=1.5.0          # Type checking
ipython>=8.14.0      # Interactive shell
ipdb>=0.13.13        # Debugger
pre-commit>=3.3.0    # Pre-commit hooks
```

**Rationale:** Ensures code quality and consistent development practices.

#### Documentation
```python
sphinx>=7.1.0              # Documentation generation
sphinx-rtd-theme>=1.3.0    # Read the Docs theme
mkdocs-material            # MkDocs Material theme
```

**Rationale:** Multiple documentation formats for different use cases.

#### System Monitoring
```python
psutil>=5.9.0        # System and process utilities
```

**Rationale:** Required for performance monitoring during MINIX builds.

### MCP Server Dependencies

#### Boot Profiler
**File:** `mcp/servers/boot-profiler/requirements.txt`

```python
mcp-core                # MCP protocol implementation
flask>=2.0.0            # Web framework
requests>=2.28.0        # HTTP library
pyyaml>=6.0             # YAML parsing
```

**Purpose:** Enables boot sequence profiling via MCP protocol.

#### Memory Monitor
**File:** `mcp/servers/memory-monitor/requirements.txt`

```python
mcp-core
psutil>=5.9.0
prometheus-client>=0.16.0
```

**Purpose:** Real-time memory monitoring during MINIX execution.

#### Syscall Tracer
**File:** `mcp/servers/syscall-tracer/requirements.txt`

```python
mcp-core
python-ptrace>=0.9.8
```

**Purpose:** System call tracing for kernel analysis.

### Profiling Tools
**File:** `tools/profiling/requirements-profiling.txt`

```python
py-spy>=0.3.14          # Sampling profiler
memory-profiler>=0.60.0 # Memory usage profiling
line-profiler>=4.0.0    # Line-by-line profiling
```

**Purpose:** Performance profiling for analysis tools.

---

## LaTeX Requirements

### Essential Packages

**Included in TexLive distributions:**

```
texlive-latex-base      # Core LaTeX
texlive-latex-extra     # Additional LaTeX packages
texlive-pictures        # TikZ and PGFPlots
texlive-fonts-recommended   # Standard fonts
texlive-fonts-extra     # Additional fonts
texlive-science         # Scientific packages
latexmk                 # Build automation
biber                   # Bibliography processor
```

### Required LaTeX Packages

**For Whitepaper Compilation:**
- `tikz` - Diagram creation
- `pgfplots` - Data plotting
- `amsmath` - Mathematical typesetting
- `graphicx` - Image inclusion
- `hyperref` - Hyperlinks and cross-references
- `cleveref` - Smart cross-referencing
- `booktabs` - Professional tables
- `listings` - Code listings
- `xcolor` - Color support
- `geometry` - Page layout

### Validation

Verify LaTeX installation:
```bash
pdflatex --version
latexmk --version
kpsewhich tikz.sty
kpsewhich pgfplots.sty
```

---

## Build Tools

### Required

```bash
git                 # Version control
make                # Build automation
docker              # Containerization (optional but recommended)
```

### Optional but Recommended

```bash
qemu-system-i386    # MINIX emulation
pdf2svg             # PDF to SVG conversion
imagemagick         # Image processing
yamllint            # YAML validation
shellcheck          # Shell script linting
```

---

## Optional Components

### For MINIX Building

```bash
docker              # Container runtime
qemu-system-i386    # i386 emulation
qemu-utils          # QEMU utilities
```

**Purpose:** Required only if building MINIX from source in emulation.

### For Advanced Analysis

```bash
graphviz            # Graph visualization
plantuml            # UML diagrams
mermaid-cli         # Mermaid diagram rendering
```

### For Documentation Development

```bash
mkdocs              # Documentation site generator
pandoc              # Document conversion
```

---

## Installation Guide

### Quick Start

**1. Clone Repository:**
```bash
git clone https://github.com/Oichkatzelesfrettschen/minix-analysis.git
cd minix-analysis
```

**2. Create Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Python Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Install System Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y texlive-full imagemagick

# macOS
brew install texlive imagemagick
```

**5. Validate Installation:**
```bash
python3 scripts/validate-texplosion-setup.py
```

### Component-Specific Installation

#### MCP Servers

```bash
# Install all MCP server dependencies
pip install -r mcp/servers/boot-profiler/requirements.txt
pip install -r mcp/servers/memory-monitor/requirements.txt
pip install -r mcp/servers/syscall-tracer/requirements.txt
```

#### Profiling Tools

```bash
pip install -r tools/profiling/requirements-profiling.txt
```

#### Development Tools

```bash
pip install pre-commit
pre-commit install
```

---

## Dependency Rationale

### Why These Specific Versions?

**matplotlib>=3.7.0**
- Required for modern subplot_mosaic functionality
- Improved TikZ export capabilities
- Better performance for large datasets

**pandas>=2.0.0**
- Native PyArrow integration for performance
- Improved string handling
- Copy-on-write optimizations

**pytest>=7.4.0**
- Native support for pyproject.toml
- Improved error messages
- Better plugin compatibility

**texlive-full vs. texlive-base**
- `texlive-full` recommended for complete LaTeX ecosystem
- `texlive-base` + specific packages acceptable for minimal installs
- Full install prevents package-not-found errors

### Version Pinning Strategy

**Philosophy:** Minimum version requirements with compatible releases

- **Core dependencies:** Pinned to major.minor (e.g., `>=3.7.0`)
- **Build tools:** Exact versions in CI/CD
- **Development tools:** Latest compatible versions
- **System packages:** Distribution-provided versions

**Why not exact pinning?**
- Allows security updates
- Reduces dependency conflicts
- Enables compatibility with other projects

**When to use exact pinning?**
- Production deployments
- CI/CD pipelines (for reproducibility)
- Known incompatibilities

---

## Dependency Tree

### Core Analysis Stack

```
minix-analysis
├── numpy (numerical foundation)
├── pandas (data structures)
│   └── numpy
├── matplotlib (visualization)
│   └── numpy
└── plotly (interactive viz)
```

### Testing Stack

```
pytest (test runner)
├── pytest-cov (coverage)
├── pytest-benchmark (performance)
├── pytest-timeout (timeouts)
└── pytest-xdist (parallelization)
```

### Documentation Stack

```
sphinx (docs)
├── sphinx-rtd-theme
└── recommonmark (Markdown support)

mkdocs-material (site)
├── mkdocs
└── pymdown-extensions
```

---

## Troubleshooting

### Common Issues

#### "Package not found" (LaTeX)

**Problem:** Missing LaTeX package during compilation

**Solutions:**
1. Install full TexLive: `sudo apt-get install texlive-full`
2. Find missing package: `kpsewhich <package>.sty`
3. Install specific collection: `sudo apt-get install texlive-<collection>`

#### "ImportError: No module named X" (Python)

**Problem:** Missing Python dependency

**Solutions:**
1. Activate virtual environment: `source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version` (must be 3.7+)

#### "ImageMagick policy error" (PDF conversion)

**Problem:** ImageMagick PDF policy restrictions

**Solution:**
```bash
sudo sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml
```

#### Docker permissions

**Problem:** "Permission denied" when running docker

**Solutions:**
1. Add user to docker group: `sudo usermod -aG docker $USER`
2. Logout and login for group changes to take effect
3. Or use `sudo` prefix for docker commands

### Version Conflicts

**Problem:** Incompatible package versions

**Diagnosis:**
```bash
pip check  # Shows conflicts
pip list --outdated  # Shows available updates
```

**Resolution:**
1. Update pip: `pip install --upgrade pip`
2. Create fresh venv
3. Install in order: core → testing → development
4. Use virtual environment isolation

### Platform-Specific Issues

**macOS M1/M2 (ARM):**
- Some packages may need Rosetta 2
- Use `arch -x86_64` prefix for x86 packages
- Consider native ARM builds when available

**Windows:**
- Use WSL2 for best compatibility
- Native Windows requires:
  - MikTeX instead of TexLive
  - Visual C++ Build Tools
  - Git for Windows

---

## Maintenance

### Regular Updates

**Monthly:**
```bash
pip list --outdated
pip install --upgrade pip setuptools wheel
```

**Quarterly:**
```bash
pip install --upgrade -r requirements.txt
```

**Before Major Releases:**
- Full dependency audit
- Test all components
- Update documentation

### Security Updates

**Monitor for vulnerabilities:**
```bash
pip install safety
safety check
```

**Update pinned versions:**
- Review CVE databases
- Test updates in development
- Deploy to production after validation

---

## Contributing

### Adding New Dependencies

**Process:**
1. Justify the dependency (document why it's needed)
2. Check for alternatives (prefer standard library when possible)
3. Add to appropriate requirements file
4. Update this document with rationale
5. Test installation on all supported platforms
6. Submit PR with updated requirements

**Guidelines:**
- Prefer well-maintained packages
- Check license compatibility
- Consider bundle size
- Evaluate performance impact

---

## Appendix A: Complete Requirements Files

### Root requirements.txt
```
# See current file for exact versions
matplotlib>=3.7.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
dash>=2.11.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-benchmark>=4.0.0
pytest-timeout>=2.1.0
pytest-xdist>=3.3.0
hypothesis>=6.82.0
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0
ipython>=8.14.0
ipdb>=0.13.13
pre-commit>=3.3.0
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0
psutil>=5.9.0
```

### Validation Command

```bash
# Verify all requirements are satisfied
python3 -c "
import sys
packages = ['matplotlib', 'pandas', 'numpy', 'pytest', 'sphinx']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f'Missing: {missing}')
    sys.exit(1)
else:
    print('All core packages installed!')
"
```

---

## Appendix B: Environment Variables

### Required

None - all configuration via files

### Optional

```bash
export MINIX_SOURCE_DIR=/path/to/minix    # Override MINIX source location
export LATEX_OUTPUT_DIR=/path/to/output   # LaTeX build output
export PYTEST_WORKERS=4                   # Parallel test workers
```

---

## Appendix C: Docker Requirements

### Dockerfile Dependencies

**Base Image:** `python:3.9-slim`

**Build Dependencies:**
```
build-essential
git
texlive-latex-base
texlive-latex-extra
imagemagick
```

**Runtime Dependencies:**
```
python3
git
texlive (minimal)
imagemagick
```

---

**Document Maintenance:**
- Review quarterly
- Update on dependency changes
- Validate all installation instructions
- Keep troubleshooting section current

**Contact:** See CONTRIBUTING.md for contribution guidelines

**License:** See LICENSE file for licensing information
