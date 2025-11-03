# Style Guide Overview

**MINIX Analysis Unified LaTeX Style System v2.1.0**

---

## Introduction

The MINIX Analysis project uses a unified, modular LaTeX style system featuring professional typography (Spline Sans fonts), scientifically-validated colorblind-safe palettes, and publication-ready TikZ/PGFPlots styles. All styles are shared across modules for consistency.

---

## Style Packages

### Package Architecture

```
minix-colors.sty          # Base color definitions
minix-colors-cvd.sty      # Colorblind-safe variants (NEW in v2.1.0)
minix-arxiv.sty           # ArXiv compliance + Spline Sans fonts (v2.1.0)
minix-styles.sty          # TikZ/PGFPlots diagram styles
```

**Dependencies**:
- minix-styles.sty → minix-colors.sty (automatic)
- minix-colors-cvd.sty → standalone (opt-in for accessibility)
- minix-arxiv.sty → minix-colors.sty (automatic)

---

## Typography (Spline Sans)

### Font Configuration

**Main Text**: Spline Sans Regular/Bold/Italic
- OldStyle numerals for body text
- TeX ligatures enabled (fi, fl, ff, ffi, ffl)

**Headings**: Spline Sans (same as main)
- Lining numerals (upright digits)
- Consistent with body font for modern appearance

**Code Listings**: Spline Sans Mono Regular/Bold
- Scale 0.95 for optimal readability
- No ligatures (preserve code structure)

**Mathematics**: Latin Modern Math
- Best compatibility with Spline Sans
- Comprehensive Unicode math symbols

### Requirements

**LaTeX Engine**: LuaLaTeX or XeLaTeX (for fontspec)
- **NOT compatible with pdfLaTeX** (use LuaLaTeX instead)

**Font Installation**:
```bash
# Download from Google Fonts
wget "https://fonts.google.com/download?family=Spline%20Sans"
wget "https://fonts.google.com/download?family=Spline%20Sans%20Mono"

# Install system-wide
sudo unzip Spline_Sans.zip -d /usr/share/fonts/SplineSans
sudo unzip Spline_Sans_Mono.zip -d /usr/share/fonts/SplineSansMono
fc-cache -fv
```

**Verification**:
```bash
fc-list | grep "Spline Sans"
# Should show: Spline Sans, Spline Sans Mono
```

### Usage

**Standard Paper**:
```latex
\documentclass{article}
\usepackage{minix-arxiv}    % Automatically configures Spline Sans

\begin{document}
This text uses Spline Sans Regular.
\textbf{This is bold.}
\textit{This is italic.}
\texttt{This is mono.}  % Spline Sans Mono
\end{document}
```

**Compile**:
```bash
lualatex paper.tex    # REQUIRED (not pdflatex)
```

---

## Color Palette

### Base Colors

| Color Name | RGB | Hex | Usage |
|------------|-----|-----|-------|
| `primaryblue` | 0, 102, 204 | #0066CC | Software/flow boxes |
| `secondarygreen` | 46, 204, 113 | #2ECC71 | Success/completion |
| `accentorange` | 255, 127, 0 | #FF7F00 | Warnings/highlights |
| `warningred` | 231, 76, 60 | #E74C3C | Errors/critical ops |

### Boot Phase Colors

| Phase | Color | Hex | Usage |
|-------|-------|-----|-------|
| 1 | `phase1` | #3498DB | Early C initialization |
| 2 | `phase2` | #2ECC71 | Process table setup |
| 3 | `phase3` | #9B59B6 | Memory management |
| 4 | `phase4` | #E67E22 | System services |
| 5 | `phase5` | #E74C3C | Usermode transition |

### Semantic Aliases

**Use these instead of raw colors**:

| Alias | Definition | Usage |
|-------|-----------|-------|
| `flowbox` | `primaryblue!15` | Software operation background |
| `hardware` | `warningred!20` | Hardware operation background |
| `kernel` | `secondarygreen!15` | Kernel operation background |
| `critical` | `accentorange!25` | Critical path highlights |

**Example**:
```latex
\usepackage{minix-colors}

\begin{tikzpicture}
  \node[draw=primaryblue, fill=flowbox] {User Space};
  \node[draw=warningred, fill=hardware] {CPU};
  \node[draw=secondarygreen, fill=kernel] {Kernel};
\end{tikzpicture}
```

---

## Colorblind-Safe (CVD) Mode

### Overview

**NEW in v2.1.0**: Scientific colorblind-safe palettes for accessibility

**Supported Variants**:
1. **Protanopia** (protan) - Red-blind (1% males, 0.01% females)
2. **Deuteranopia** (deutan) - Green-blind (1% males, 0.01% females)
3. **Tritanopia** (tritan) - Blue-blind (0.001% population)
4. **Monochromacy** (mono) - Grayscale (0.00003% population)

**Research Basis**:
- Okabe & Ito (2008): "Color Universal Design"
- Wong (2011): "Points of view: Color blindness"
- ColorBrewer 2.0 (Cynthia Brewer, Penn State)

### Usage

**Basic Setup**:
```latex
\documentclass{article}
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]  % or deutan|tritan|mono|default
\cvdapplyplotstyles        % Apply to PGFPlots

\begin{document}
\begin{tikzpicture}
\begin{axis}[cvdaxis]
  \addplot[color=cvdBlue700, mark=*] coordinates {(0,0) (1,1) (2,4)};
  \addplot[color=cvdMagenta600, mark=triangle*] coordinates {(0,1) (1,2) (2,3)};
\end{axis}
\end{tikzpicture}
\end{document}
```

### CVD Color Palette

**Protanopia Palette** (darker indigos + warm magentas):
- `cvdBlue700`: #2E2AA1 (dark indigo)
- `cvdMagenta600`: #B12179 (warm magenta)
- `cvdOrange`: #FF9500 (preserved)
- `cvdGreen`: #34C759 (preserved)

**Deuteranopia Palette** (similar to protan):
- `cvdBlue700`: #2E2AA1
- `cvdMagenta600`: #A81E7B
- `cvdOrange`: #FF9500
- `cvdGreen`: #34C759

**Tritanopia Palette** (violet-blue shifts):
- `cvdBlue700`: #3A2A91 (violet-blue)
- `cvdMagenta600`: #B12179
- `cvdOrange`: #E67E22
- `cvdGreen`: #27AE60

**Monochromacy Palette** (grayscale):
- `cvdBlue700`: #333333 (dark gray)
- `cvdMagenta600`: #666666 (medium gray)
- `cvdOrange`: #999999 (light gray)
- `cvdGreen`: #AAAAAA (lighter gray)

### PGFPlots Cycle List

**Features**:
- 6 distinct colors
- Unique markers (*, triangle*, square*, diamond*, pentagon*, x)
- Different line styles (solid, dashed, dotted, dashdotted, densely dashed, loosely dotted)
- Grayscale-printable patterns

**Example**:
```latex
\begin{axis}[cvdaxis]
  \addplot {x};       % cvdBlue700, solid, mark=*
  \addplot {x^2};     % cvdMagenta600, dashed, mark=triangle*
  \addplot {x^3};     % cvdOrange, dotted, mark=square*
\end{axis}
```

### Switching Variants

**Runtime Variant Switch**:
```latex
\cvdsetup[variant=protan]
\input{diagram-syscalls.tex}

\cvdsetup[variant=deutan]
\input{diagram-memory.tex}

\cvdsetup[variant=default]  % Return to standard colors
\input{diagram-boot.tex}
```

---

## TikZ Diagram Styles

### CPU Interface Diagrams

**Node Styles**:
```latex
\begin{tikzpicture}[cpu flow]
  \node[box] {Software};           % Blue rectangle
  \node[hw] {Hardware};             % Red rectangle
  \node[kernelbox] {Kernel};        % Green rectangle
  \node[decision] {Branch?};        % Orange diamond
\end{tikzpicture}
```

**Arrow Styles**:
- `arrow`: Standard flow (black, thick)
- `critarrow`: Critical path (red, very thick)
- `dataflow`: Data transfer (blue, dashed)

**Full Example**:
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

**Node Styles**:
```latex
\begin{tikzpicture}[boot topology]
  \node[process] {kmain()};           % Blue rounded box with shadow
  \node[phase] {Phase 1};              % Green label box
  \node[critical] {switch_to_user()};  % Red thick-border box
  \node[terminate] {[NEVER RETURNS]};  % Red termination marker
\end{tikzpicture}
```

**Tree Layout**:
```latex
\begin{tikzpicture}[call graph]
  \node[func] {kmain()}
    child { node[func] {proc_init()} }
    child { node[func] {memory_init()} }
    child { node[extfunc] {printf()} };  % Gray dashed = external
\end{tikzpicture}
```

---

## PGFPlots Performance Charts

### Bar Charts

**Syscall Comparison**:
```latex
\begin{tikzpicture}
\begin{axis}[
    minix axis,
    ybar,
    xlabel={Syscall Mechanism},
    ylabel={Cycles},
    symbolic x coords={INT, SYSENTER, SYSCALL},
    xtick=data,
]
\addplot[minix bar, fill=primaryblue] coordinates {
    (INT, 1772)
    (SYSENTER, 1305)
    (SYSCALL, 1439)
};
\end{axis}
\end{tikzpicture}
```

### Line Plots

**Time Series**:
```latex
\begin{tikzpicture}
\begin{axis}[
    minix axis,
    xlabel={Time (ms)},
    ylabel={CPU Usage (\%)},
]
\addplot[minix line, color=primaryblue] table {data.dat};
\end{axis}
\end{tikzpicture}
```

### Scatter Plots

**Performance Distribution**:
```latex
\begin{axis}[minix axis, scatter]
  \addplot[only marks, mark=*, color=primaryblue] table {results.csv};
\end{axis}
```

---

## Code Listings

### C Code Style

```latex
\begin{lstlisting}[style=minixcode, caption={System Call Entry}]
void kmain(kinfo_t *cbi) {
    cstart(cbi);          // Early C initialization
    proc_init();          // Process table setup
    memory_init();        // Virtual memory
    switch_to_user();     // Never returns
}
\end{lstlisting}
```

**Features**:
- Spline Sans Mono font
- C syntax highlighting
- Line numbers (optional)
- Frame around code

### Assembly Code Style

```latex
\begin{lstlisting}[style=minixasm, caption={SYSENTER Entry Point}]
ipc_entry_sysenter:
    movl    %esp, %eax       ; Save user ESP
    movl    TSS_ESP0, %esp   ; Load kernel stack
    sti                      ; Enable interrupts
    push    %eax             ; Save user context
    call    do_ipc           ; C handler
    sysexit                  ; Return to usermode
\end{lstlisting}
```

**Features**:
- x86 assembly syntax highlighting
- Comment alignment
- Instruction/operand coloring

---

## ArXiv Compliance

### Required Settings

**Enforced by minix-arxiv.sty**:
1. ✅ `colorlinks=true` (REQUIRED by ArXiv)
2. ✅ UTF-8 input encoding
3. ✅ T1 font encoding
4. ✅ PDF metadata (author, title, subject, keywords)
5. ✅ Hyperref configuration

### PDF Metadata

**Setup**:
```latex
\documentclass{article}
\usepackage{minix-arxiv}

\setpdfmetadata{
    MINIX CPU Interface Analysis  % Title
}{
    Oaich                         % Author
}{
    Operating Systems             % Subject
}{
    MINIX, i386, system calls     % Keywords
}
```

### Bibliography

**ArXiv requires .bbl (not .bib)**:
```bash
lualatex paper.tex
bibtex paper
lualatex paper.tex
lualatex paper.tex
# Include paper.bbl in ArXiv submission
```

---

## Installation

### System-wide Installation

**From project root**:
```bash
cd /home/eirikr/Playground/minix-analysis
sudo make install
```

**What gets installed**:
```
/usr/share/texmf/tex/latex/minix/
├── minix-colors.sty
├── minix-colors-cvd.sty
├── minix-arxiv.sty
└── minix-styles.sty
```

**Verification**:
```bash
kpsewhich minix-colors.sty
# Should output: /usr/share/texmf/tex/latex/minix/minix-colors.sty
```

### Per-Project Usage

**Without system install**:
```latex
\makeatletter
\def\input@path{{../../shared/styles/}}
\makeatother

\usepackage{minix-arxiv}
\usepackage{minix-styles}
```

**Or set TEXINPUTS**:
```bash
export TEXINPUTS=../../shared/styles//:
lualatex paper.tex
```

---

## Migration Guide

### From pdfLaTeX to LuaLaTeX

**Old**:
```bash
pdflatex paper.tex
```

**New**:
```bash
lualatex paper.tex
```

**Breaking Change**: Spline Sans fonts require LuaLaTeX/XeLaTeX

### From Raw Colors to Semantic Names

**Old**:
```latex
\node[fill=blue!10, draw=blue] {Box};
```

**New**:
```latex
\node[fill=flowbox, draw=primaryblue] {Box};
```

**Benefit**: Consistent colors across all diagrams

### Enabling CVD Mode

**Add to existing diagram**:
```latex
% Before:
\usepackage{minix-colors}
\usepackage{minix-styles}

% After:
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]
\cvdapplyplotstyles
\usepackage{minix-styles}
```

---

## Troubleshooting

### "I can't find file `Spline Sans'"

**Cause**: Fonts not installed

**Solution**: See Typography section above

### "Undefined control sequence \setmainfont"

**Cause**: Using pdflatex instead of lualatex

**Solution**: Use `lualatex paper.tex`

### "Package xcolor Error: Undefined color `cvdBlue700'"

**Cause**: minix-colors-cvd.sty not loaded

**Solution**: Add `\usepackage{minix-colors-cvd}` before usage

---

## Related Documentation

- [Shared Styles README](../../shared/styles/README.md)
- [Build System](../build-system/Overview.md)
- [ArXiv Standards](../../ARXIV-STANDARDS.md)

---

**Last Updated**: 2025-10-30
**Version**: 2.1.0
**License**: MIT
