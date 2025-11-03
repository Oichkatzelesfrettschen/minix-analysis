# MINIX Analysis Unified Style System

**Version**: 2.1.0 (Modular Architecture + CVD + Spline Sans)
**Last Updated**: 2025-10-30

## Overview

This directory contains the unified LaTeX style system for all MINIX analysis modules. The style system is modular, with five primary packages:

1. **minix-colors.sty** - Unified color palette
2. **minix-colors-cvd.sty** - **NEW**: Colorblind-safe (CVD) variants
3. **minix-arxiv.sty** - ArXiv submission compliance + **Spline Sans fonts**
4. **minix-styles.sty** - TikZ/PGFPlots diagram styles

## Package Structure

```
shared/styles/
├── minix-colors.sty          # Base color definitions (primary, boot phases, CPU)
├── minix-colors-cvd.sty      # NEW: CVD-safe color variants (protan/deutan/tritan/mono)
├── minix-arxiv.sty           # ArXiv compliance + Spline Sans font configuration
├── minix-styles.sty          # TikZ/PGFPlots styles (imports minix-colors)
└── README.md                 # This file
```

## What's New in v2.1.0

### ✨ Spline Sans Fonts

All papers now use **Spline Sans** (Google Fonts) for clean, modern typography:

- **Main text**: Spline Sans Regular/Bold/Italic
- **Headings**: Spline Sans (same as main for consistency)
- **Code listings**: Spline Sans Mono Regular/Bold/Italic
- **Math**: Latin Modern Math (best compatibility)

**Requirements**:
- LuaLaTeX or XeLaTeX (for fontspec)
- Spline Sans and Spline Sans Mono fonts installed system-wide

**Installation**:
```bash
# Download from Google Fonts
wget https://fonts.google.com/download?family=Spline%20Sans
wget https://fonts.google.com/download?family=Spline%20Sans%20Mono

# Install to ~/.fonts or /usr/share/fonts
unzip Spline_Sans.zip -d ~/.fonts/SplineSans
unzip Spline_Sans_Mono.zip -d ~/.fonts/SplineSansMono
fc-cache -fv
```

### 🎨 Colorblind-Safe (CVD) Palettes

New `minix-colors-cvd.sty` provides scientifically-validated color variants for:

- **Protanopia** (red-blind): 1% males, 0.01% females
- **Deuteranopia** (green-blind): 1% males, 0.01% females
- **Tritanopia** (blue-blind): 0.001% population
- **Monochromacy** (grayscale): 0.00003% population

**Features**:
- ✅ Research-based (Okabe & Ito 2008, Wong 2011, ColorBrewer 2.0)
- ✅ Works with existing MINIX diagrams (just add variant switch)
- ✅ Includes patterns/markers for grayscale printing
- ✅ PGFPlots cycle list with distinct line styles

**Usage**:
```latex
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]  % or deutan|tritan|mono|default
\cvdapplyplotstyles

\begin{tikzpicture}
\begin{axis}[cvdaxis]
  \addplot[color=cvdBlue700, mark=*] {data};
\end{axis}
\end{tikzpicture}
```

## Usage

### For Standalone Diagrams

If you're creating individual diagram PDFs (e.g., `syscall-flow.pdf`):

```latex
\documentclass{standalone}
\usepackage{minix-colors}    % Color palette
\usepackage{tikz}
\usepackage{minix-styles}    % Diagram styles

\begin{document}
\begin{tikzpicture}[cpu flow]
  \node[box] (A) {User Space};
  \node[hw, below=of A] (B) {INT 0x33};
  \draw[arrow] (A) -- (B);
\end{tikzpicture}
\end{document}
```

**Compile**:
```bash
pdflatex diagram.tex
```

### For Complete Papers

If you're writing a full paper for ArXiv submission:

```latex
\documentclass[11pt,a4paper]{article}
\usepackage{minix-arxiv}     % ArXiv compliance (includes colors, hyperref, etc.)
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{minix-styles}    % Diagram styles

\setpdfmetadata{Your Title}{Your Name}{Subject}{Keywords}

\begin{document}
...
\end{document}
```

**Compile**:
```bash
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Color Palette

### Primary Colors

| Color Name | RGB | Usage |
|------------|-----|-------|
| `primaryblue` | 0,102,204 | Professional blue for software/flow boxes |
| `secondarygreen` | 46,204,113 | Success/completion indicators |
| `accentorange` | 255,127,0 | Warnings/highlights |
| `warningred` | 231,76,60 | Errors/critical operations |

### Boot Phase Colors

| Phase | Color Name | RGB | Usage |
|-------|-----------|-----|-------|
| 1 | `phase1` | 52,152,219 | Early C initialization |
| 2 | `phase2` | 46,204,113 | Process table setup |
| 3 | `phase3` | 155,89,182 | Memory management |
| 4 | `phase4` | 230,126,34 | System services |
| 5 | `phase5` | 231,76,60 | Usermode transition |

### Semantic Aliases

Use these semantic names instead of raw colors:

| Alias | Definition | Usage |
|-------|-----------|-------|
| `flowbox` | `primaryblue!15` | Software operation boxes |
| `hardware` | `warningred!20` | Hardware operation boxes |
| `kernel` | `secondarygreen!15` | Kernel operation boxes |
| `critical` | `accentorange!25` | Critical path highlights |

**Example**:
```latex
\node[draw=primaryblue, fill=flowbox] {Process A};
```

## TikZ Node Styles

### CPU Interface Diagrams

| Style | Appearance | Usage |
|-------|-----------|-------|
| `box` | Blue rectangle | Software operations |
| `hw` | Red rectangle | Hardware operations |
| `kernelbox` | Green rectangle | Kernel operations |
| `decision` | Orange diamond | Conditional branches |

**Example**:
```latex
\begin{tikzpicture}[cpu flow]
  \node[box] (user) {User Space (Ring 3)};
  \node[hw, below=of user] (cpu) {CPU (INT 0x33)};
  \node[kernelbox, below=of cpu] (kernel) {Kernel (Ring 0)};
  \draw[arrow] (user) -- (cpu);
  \draw[arrow] (cpu) -- (kernel);
\end{tikzpicture}
```

### Boot Sequence Diagrams

| Style | Appearance | Usage |
|-------|-----------|-------|
| `process` | Blue rounded box with shadow | Process/function nodes |
| `phase` | Green label box | Phase headers |
| `critical` | Red thick-border box | Critical path nodes |
| `terminate` | Red termination box | Never-return functions |

**Example**:
```latex
\begin{tikzpicture}[boot topology]
  \node[process] (kmain) {kmain()};
  \node[process, below=of kmain] (init) {arch\_init()};
  \node[critical, below=of init] (user) {switch\_to\_user()};
  \draw[arrow] (kmain) -- (init);
  \draw[critarrow] (init) -- (user);
\end{tikzpicture}
```

### Call Graph Diagrams

| Style | Appearance | Usage |
|-------|-----------|-------|
| `func` | Blue small box | Internal functions |
| `extfunc` | Gray dashed box | External functions |

**Example**:
```latex
\begin{tikzpicture}[call graph]
  \node[func] {kmain()}
    child { node[func] {proc\_init()} }
    child { node[extfunc] {printf()} };
\end{tikzpicture}
```

## PGFPlots Styles

### Performance Charts

| Style | Usage | Example |
|-------|-------|---------|
| `minix axis` | Standard axis with grid | Timing charts |
| `minix bar` | Bar chart | Syscall comparison |
| `minix line` | Line plot | Time series |

**Example**:
```latex
\begin{tikzpicture}
\begin{axis}[
    minix axis,
    xlabel={Syscall Mechanism},
    ylabel={Cycles},
    ymin=0
]
\addplot[minix bar] coordinates {
    (INT, 1772)
    (SYSENTER, 1305)
    (SYSCALL, 1439)
};
\end{axis}
\end{tikzpicture}
```

## ArXiv Compliance

### Required Settings (Enforced by minix-arxiv.sty)

1. **Hyperlinks**: `colorlinks=true` (REQUIRED by ArXiv)
2. **Fonts**: Latin Modern (lmodern) for high quality
3. **Encoding**: UTF-8 input, T1 font encoding
4. **Figures**: PDF only (no .eps files)
5. **Bibliography**: Include .bbl file (not .bib)

### Code Listings

Two predefined styles:

**C Code**:
```latex
\begin{lstlisting}[style=minixcode]
void kmain(void) {
    proc_init();  // Initialize process table
    mem_init();   // Setup memory management
}
\end{lstlisting}
```

**Assembly Code**:
```latex
\begin{lstlisting}[style=minixasm]
ipc_entry_sysenter:
    movl %esp, %eax
    sysenter
\end{lstlisting}
```

### PDF Metadata

Set metadata for your paper:

```latex
\setpdfmetadata{MINIX CPU Interface Analysis}{Oaich}{Operating Systems}{MINIX, i386, syscalls}
```

## Migration Guide

### From Old CPU Diagrams

Old CPU diagrams using raw colors can continue to work with the compatibility layer:

**Old Code** (still works):
```latex
\node[fill=blue!10, draw=blue] {Box};
```

**New Code** (preferred):
```latex
\node[box] {Box};
% or
\node[fill=flowbox, draw=primaryblue] {Box};
```

### From Boot Analyzer

Boot analyzer diagrams using `phase1-phase5` colors are fully supported:

**Old Code** (boot analyzer):
```latex
\definecolor{phase1}{RGB}{52,152,219}
\node[fill=phase1] {Phase 1};
```

**New Code** (automatically available):
```latex
\node[fill=phase1] {Phase 1};
% phase1-phase5 defined in minix-colors.sty
```

## Directory Integration

This shared style directory is used by all analysis modules:

```
minix-analysis/
├── shared/
│   └── styles/                    # ← This directory
│       ├── minix-colors.sty
│       ├── minix-arxiv.sty
│       └── minix-styles.sty
├── modules/
│   ├── cpu-interface/
│   │   └── latex/
│   │       └── paper.tex          # \usepackage{minix-styles}
│   └── boot-sequence/
│       └── latex/
│           └── paper.tex          # \usepackage{minix-styles}
```

### LaTeX Search Path

To use shared styles from module directories, add to your `.tex` file:

```latex
\makeatletter
\def\input@path{{../../shared/styles/}}
\makeatother

\usepackage{minix-arxiv}
\usepackage{minix-styles}
```

Or set `TEXINPUTS` environment variable:

```bash
export TEXINPUTS=../../shared/styles//:
pdflatex paper.tex
```

Or use `-output-directory` flag:

```bash
pdflatex -output-directory=build paper.tex
```

## Testing

### Verify Colors

Create test diagram:

```latex
\documentclass{standalone}
\usepackage{minix-colors}
\usepackage{tikz}

\begin{document}
\begin{tikzpicture}
  \foreach \col/\name in {
    primaryblue/Primary Blue,
    secondarygreen/Secondary Green,
    accentorange/Accent Orange,
    warningred/Warning Red
  } {
    \node[fill=\col, text=white, minimum width=3cm] {\name};
  }
\end{tikzpicture}
\end{document}
```

### Verify ArXiv Compliance

Check hyperref settings:

```latex
\documentclass{article}
\usepackage{minix-arxiv}

\begin{document}
\hypersetup{pdfinfo}  % Should show colorlinks=true
\end{document}
```

## Troubleshooting

### Error: "File `minix-colors.sty' not found"

**Solution**: Add `shared/styles/` to LaTeX search path or use absolute path:

```latex
\usepackage{../../shared/styles/minix-colors}
```

### Error: "Package xcolor Error: Undefined color `phase1'"

**Solution**: Ensure `minix-colors.sty` is loaded before using phase colors:

```latex
\usepackage{minix-colors}  % Load first
\usepackage{tikz}
```

### Warning: "colorlinks=false in hyperref"

**Solution**: This is impossible with `minix-arxiv.sty`. If you see this warning, you're loading hyperref manually before minix-arxiv. Remove your manual hyperref load.

## Version History

**2.0.0** (2025-10-30) - Modular architecture
- Split into minix-colors.sty, minix-arxiv.sty, minix-styles.sty
- Unified CPU and Boot color palettes
- ArXiv compliance package
- Shared infrastructure for all modules

**1.0.0** (2025-10-30) - Initial monolithic version
- Single minix-styles.sty file
- CPU-focused colors
- Basic TikZ styles

## License

Copyright © 2025 Oaich (eirikr)
Licensed under MIT License

---

For complete usage examples, see:
- `modules/cpu-interface/latex/` - CPU analysis paper
- `modules/boot-sequence/latex/` - Boot analysis paper
- `ARXIV-STANDARDS.md` - ArXiv submission guide
