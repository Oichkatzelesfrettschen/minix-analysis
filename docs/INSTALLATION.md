# MINIX Analysis - Installation Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-30
**Target**: MINIX 3.4.0-RC6 on i386 architecture

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Font Installation](#font-installation)
3. [LaTeX Environment](#latex-environment)
4. [Building the Papers](#building-the-papers)
5. [MCP Servers](#mcp-servers)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Operating System
- **Recommended**: Linux (Arch/CachyOS, Ubuntu 22.04+, Fedora 38+)
- **Supported**: macOS 12+, Windows 10/11 (WSL2)

### Core Dependencies

**LaTeX Distribution** (TeX Live 2023 or later):
```bash
# Arch Linux / CachyOS
sudo pacman -S texlive-most texlive-binextra

# Ubuntu / Debian
sudo apt install texlive-full

# macOS (via MacTeX)
brew install --cask mactex

# Fedora
sudo dnf install texlive-scheme-full
```

**Python** (3.10 or later):
```bash
# Arch Linux / CachyOS
sudo pacman -S python python-pip

# Ubuntu / Debian
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python@3.11

# Fedora
sudo dnf install python3 python3-pip
```

**Build Tools**:
```bash
# Arch Linux / CachyOS
sudo pacman -S make

# Ubuntu / Debian
sudo apt install build-essential

# macOS (via Xcode Command Line Tools)
xcode-select --install

# Fedora
sudo dnf groupinstall "Development Tools"
```

---

## Font Installation

The papers use **Spline Sans** and **Spline Sans Mono** from Google Fonts for clean, modern typography.

###Step 1: Download Fonts

```bash
# Create fonts directory
mkdir -p ~/.fonts/SplineSans
mkdir -p ~/.fonts/SplineSansMono

# Download Spline Sans
wget -O /tmp/SplineSans.zip "https://fonts.google.com/download?family=Spline%20Sans"
unzip /tmp/SplineSans.zip -d ~/.fonts/SplineSans/

# Download Spline Sans Mono
wget -O /tmp/SplineSansMono.zip "https://fonts.google.com/download?family=Spline%20Sans%20Mono"
unzip /tmp/SplineSansMono.zip -d ~/.fonts/SplineSansMono/

# Refresh font cache
fc-cache -fv
```

### Step 2: Verify Installation

```bash
fc-list | grep "Spline Sans"
```

Expected output:
```
/home/user/.fonts/SplineSans/SplineSans-Regular.ttf: Spline Sans:style=Regular
/home/user/.fonts/SplineSans/SplineSans-Bold.ttf: Spline Sans:style=Bold
/home/user/.fonts/SplineSansMono/SplineSansMono-Regular.ttf: Spline Sans Mono:style=Regular
...
```

---

## LaTeX Environment

### Install Shared Styles (System-wide)

```bash
cd /home/eirikr/Playground/minix-analysis
sudo make install
```

This installs:
- `minix-colors.sty` - Base color palette
- `minix-colors-cvd.sty` - Colorblind-safe variants
- `minix-arxiv.sty` - ArXiv compliance + Spline Sans fonts
- `minix-styles.sty` - TikZ/PGFPlots diagram styles

### Alternative: Local Installation (Per-Project)

```bash
# Set TEXINPUTS environment variable
export TEXINPUTS=./shared/styles//:

# Or use symlinks
cd modules/cpu-interface/latex/
ln -s ../../../shared/styles/*.sty .
```

### Verify LaTeX Installation

```bash
kpsewhich minix-colors.sty
kpsewhich minix-arxiv.sty
```

Expected output:
```
/usr/share/texmf/tex/latex/minix/minix-colors.sty
/usr/share/texmf/tex/latex/minix/minix-arxiv.sty
```

---

## Building the Papers

### Quick Start

```bash
cd /home/eirikr/Playground/minix-analysis

# Build CPU interface paper
make cpu

# Build boot sequence paper
make boot

# Build both
make cpu boot
```

### Module-Specific Builds

**CPU Interface Analysis**:
```bash
cd modules/cpu-interface
make all              # Full build (figures + plots + PDF)
make quick            # Single-pass build (fast iteration)
make figures          # Compile TikZ diagrams only
make clean            # Remove build artifacts
```

**Boot Sequence Analysis**:
```bash
cd modules/boot-sequence
make all              # Full build (visualizations + PDF)
make quick            # Single-pass build
make visualizations   # Generate call graphs
make clean            # Remove build artifacts
```

### ArXiv Submission Packages

```bash
# From root directory
make arxiv-cpu        # Creates build/arxiv-cpu/
make arxiv-boot       # Creates build/arxiv-boot/
```

### Build Output Locations

- **CPU Paper**: `modules/cpu-interface/latex/minix-complete-analysis.pdf`
- **Boot Paper**: `modules/boot-sequence/latex/minix-boot-analysis.pdf`
- **ArXiv Packages**: `build/arxiv-*/`

---

## MCP Servers

The MCP (Model Context Protocol) servers expose MINIX analysis data to AI assistants like Claude Code.

### Installation

```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt

# Install servers in development mode
cd servers/minix-analysis
pip install -e ".[dev]"

cd ../minix-filesystem
pip install -e ".[dev]"
```

### Configuration (Claude Code)

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "minix-analysis": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/servers/minix-analysis",
      "env": {
        "MINIX_DATA_PATH": "/home/eirikr/Playground/minix-analysis"
      }
    },
    "minix-filesystem": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/servers/minix-filesystem",
      "env": {
        "MINIX_SOURCE_ROOT": "/home/eirikr/Playground/minix"
      }
    }
  }
}
```

### Testing MCP Servers

```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
source venv/bin/activate
pytest -v
```

Expected: **39 tests pass (100% success rate)**

---

## Troubleshooting

### LaTeX Compilation Errors

**Error**: `! LaTeX Error: File 'minix-colors.sty' not found.`

**Solution**:
```bash
# Check if styles are installed
kpsewhich minix-colors.sty

# If not found, install system-wide
cd /home/eirikr/Playground/minix-analysis
sudo make install

# OR set TEXINPUTS
export TEXINPUTS=../../shared/styles//:
```

---

**Error**: `! Package fontspec Error: The font "Spline Sans" cannot be found.`

**Solution**:
```bash
# Reinstall fonts
fc-cache -fv

# Verify installation
fc-list | grep "Spline Sans"

# If still not found, re-download fonts (see Font Installation section)
```

---

**Error**: `! LaTeX Error: Command '\luatexversion' is undefined.`

**Solution**: You're using `pdflatex` instead of `lualatex`. Update your build command:
```bash
# Use lualatex explicitly
lualatex minix-complete-analysis.tex

# Or via Makefile (already configured)
make all
```

---

### MCP Server Issues

**Issue**: Tests fail with `MINIX_DATA_PATH` errors

**Solution**:
```bash
# Ensure environment variables are set
export MINIX_DATA_PATH="/home/eirikr/Playground/minix-analysis"
export MINIX_SOURCE_ROOT="/home/eirikr/Playground/minix"

# Run tests again
pytest -v
```

---

**Issue**: Import errors when running servers

**Solution**:
```bash
# Reinstall in development mode
cd servers/minix-analysis
pip install -e ".[dev]"

# Verify installation
python -c "import src.server; print('OK')"
```

---

### Build Performance

**Issue**: LaTeX compilation is slow

**Solutions**:
1. **Use quick build for iteration**:
   ```bash
   make quick  # Single pass, no figures rebuild
   ```

2. **Compile figures separately**:
   ```bash
   make figures  # One-time compilation
   make quick    # Fast iterations
   ```

3. **Enable draft mode** (edit `.tex` file):
   ```latex
   \documentclass[draft]{article}  % Faster, placeholder graphics
   ```

---

### Colorblind-Safe Diagrams

**Enabling CVD Mode**:

Edit your `.tex` file:
```latex
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]  % or deutan|tritan|mono
\cvdapplyplotstyles

\begin{tikzpicture}
\begin{axis}[cvdaxis]
  \addplot[color=cvdBlue700, mark=*] {data};
\end{axis}
\end{tikzpicture}
```

**Available Variants**:
- `default` - Standard MINIX colors
- `protan` - Protanopia (red-blind)
- `deutan` - Deuteranopia (green-blind)
- `tritan` - Tritanopia (blue-blind)
- `mono` - Monochromacy (grayscale)

---

## Verification Checklist

After installation, verify:

- [ ] Fonts installed: `fc-list | grep "Spline Sans"`
- [ ] LaTeX styles installed: `kpsewhich minix-colors.sty`
- [ ] Can compile CPU paper: `cd modules/cpu-interface && make quick`
- [ ] Can compile Boot paper: `cd modules/boot-sequence && make quick`
- [ ] MCP tests pass: `cd minix-mcp-servers && pytest -v`
- [ ] PDFs generated correctly (check file sizes > 100 KB)

---

## Support

**Issues**: https://github.com/oaich/minix-analysis/issues
**Documentation**: See `README.md` and module-specific `README.md` files
**ArXiv Standards**: See `ARXIV-STANDARDS.md`

---

**Copyright © 2025 Oaich (eirikr)**
Licensed under MIT License
