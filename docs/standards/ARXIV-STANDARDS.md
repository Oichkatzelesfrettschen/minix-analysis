# ArXiv Submission Standards for MINIX Analysis Papers

**Version**: 1.0.0
**Date**: 2025-10-30
**Based on**: ArXiv Guidelines (2024), TeX Live 2023
**Source**: Copied from /home/eirikr/Playground/minix-analysis/ARXIV-STANDARDS.md (2025-11-01)

---

## Executive Summary

This document provides **comprehensive ArXiv submission standards** for all MINIX analysis papers, ensuring compliance with ArXiv technical requirements and best practices.

**Sources**:
- ArXiv Submission Guidelines: https://info.arxiv.org/help/submit/index.html
- TeX/LaTeX Submissions: https://info.arxiv.org/help/submit_tex.html
- Overleaf ArXiv Checklist: https://www.overleaf.com/learn/how-to/LaTeX_checklist_for_arXiv_submissions

---

## ArXiv Technical Requirements

### Compiler Version

**TeX Live 2023** (modified version)

- ArXiv uses TeX Live 2023 with custom modifications
- Submit projects should be tested with TeX Live 2023 locally
- Avoid packages or features introduced after TeX Live 2023

**Verification**:
```bash
pdflatex --version
# Should show: TeX Live 2023 or compatible
```

### Accepted Formats

✅ **Preferred**: TeX/LaTeX source files
❌ **Not Accepted**: DVI, PS, or PDF created from TeX/LaTeX

**Rationale**: ArXiv recompiles all submissions for consistency and long-term archival.

---

## File Organization Requirements

### 1. Main .tex File Location

**Requirement**: Main `.tex` file must be at **root level** of submission

**Problem**: Submissions may fail if `.tex` is in a subfolder

**Solution**:
```
# GOOD ✅
my-paper/
├── main.tex              # Root level
├── main.bbl
├── mystyle.sty
└── figures/
    └── diagram.pdf

# BAD ❌
my-paper/
└── latex/
    ├── main.tex          # In subfolder
    └── ...
```

### 2. File Naming Conventions

**Requirements**:
- NO spaces in filenames
- NO question marks (`?`), asterisks (`*`), or special characters
- Case-sensitive filenames and extensions
- Use lowercase for consistency

**Examples**:
```
# GOOD ✅
figure-01.pdf
my_diagram.pdf
minix-boot-arxiv.tex

# BAD ❌
Figure 01.pdf            # Space
my-diagram?.pdf          # Special char
MINIX-Boot-ArXiv.TEX     # Inconsistent case
```

### 3. Directory Structure

**Recommended**:
```
paper-YYYY-MM/                    # Date-stamped submission folder
├── main.tex                      # Main document (root level)
├── main.bbl                      # Bibliography (generated from .bib)
├── shared-style.sty              # Shared style packages
├── module-colors.sty             # Color definitions
├── figures/                      # All figures in subfolder
│   ├── diagram-01.pdf
│   ├── diagram-02.pdf
│   └── chart-performance.pdf
├── sections/                     # Optional: section files
│   ├── introduction.tex
│   └── methodology.tex
└── README.txt                    # Optional: submission notes
```

---

## LaTeX Source Requirements

### 1. Bibliography Files

**Requirement**: Include `.bbl` file, NOT `.bib`

**Reason**: ArXiv does not run BibTeX

**Workflow**:
```bash
# 1. Compile locally with BibTeX
pdflatex main.tex
bibtex main            # Generates main.bbl
pdflatex main.tex
pdflatex main.tex

# 2. Include main.bbl in submission
# 3. Do NOT include main.bib

# 4. Verify .bbl exists
ls -lh main.bbl
```

**Check**: `.bbl` filename must match main `.tex` filename

### 2. Figure Formats

**Supported**:
- ✅ PDF (preferred for vector graphics)
- ✅ PNG (for raster images)
- ✅ JPEG (for photos)

**NOT Supported by pdflatex**:
- ❌ .eps (Encapsulated PostScript)

**Conversion**:
```bash
# Convert .eps to .pdf
epstopdf diagram.eps
# Generates diagram.pdf

# Bulk conversion
for file in *.eps; do epstopdf "$file"; done
```

**In LaTeX**:
```latex
% Use graphics/graphicx package
\usepackage{graphicx}

% Include without extension (LaTeX finds .pdf automatically)
\includegraphics{figures/diagram-01}

% Or explicitly
\includegraphics{figures/diagram-01.pdf}
```

### 3. Hyperref Package

**Requirement**: Must use `colorlinks=true`

**Reason**: ArXiv auto-loads hyperref with specific options

**Correct Usage**:
```latex
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,        % REQUIRED
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}
```

**Common Error**:
```
Option clash for package hyperref
```

**Solution**: Set options only in `\hypersetup{}`, not in `\usepackage[options]{hyperref}`

### 4. Input/Include Paths

**Requirement**: All paths must be **relative**, not absolute

**Good**:
```latex
\input{sections/introduction}
\includegraphics{figures/diagram}
\include{sections/methodology}
```

**Bad**:
```latex
\input{/home/user/paper/sections/introduction}        % Absolute
\includegraphics{C:/Users/Documents/figures/diagram}  % Windows absolute
```

### 5. Custom Packages (.sty files)

**Requirement**: Include ALL custom `.sty` files in submission

**Workflow**:
```
paper/
├── main.tex
├── minix-styles.sty       # Custom style
├── minix-colors.sty       # Color definitions
└── minix-arxiv.sty        # ArXiv formatting
```

**In main.tex**:
```latex
\usepackage{minix-styles}   % No path needed, same directory
\usepackage{minix-colors}
```

**Do NOT**:
- Use absolute paths to `.sty` files
- Assume ArXiv has your custom packages installed

---

## Package and Class File Standards

### Common Safe Packages (TeX Live 2023)

These packages are **guaranteed available** on ArXiv:

```latex
% Formatting
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}

% Graphics
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pgfplots}

% Tables
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}

% Math
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}

% Code listings
\usepackage{listings}
\usepackage{xcolor}

% Algorithms
\usepackage{algorithm}
\usepackage{algpseudocode}

% References
\usepackage{hyperref}
\usepackage{cleveref}   % Load AFTER hyperref

% Misc
\usepackage{float}
\usepackage{enumitem}
```

### Package Compatibility

**PGFPlots compat**:
```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}   % TeX Live 2023 max
```

**Do NOT use**:
```latex
\pgfplotsset{compat=newest}  % May break on ArXiv
```

---

## Submission Package Creation

### Step-by-Step Workflow

#### 1. Organize Files

```bash
# Create submission directory
mkdir paper-YYYY-MM
cd paper-YYYY-MM

# Copy main .tex to root
cp ../latex/main.tex ./

# Copy .bbl (NOT .bib)
cp ../latex/main.bbl ./

# Copy custom .sty files
cp ../shared/styles/*.sty ./

# Copy figures (convert .eps to .pdf first)
cp -r ../latex/figures ./
```

#### 2. Update File Paths

Edit `main.tex`:

```latex
% OLD (local development)
\usepackage{../shared/styles/minix-styles}
\includegraphics{../latex/figures/diagram}

% NEW (ArXiv submission)
\usepackage{minix-styles}
\includegraphics{figures/diagram}
```

#### 3. Test Compilation

```bash
# Clean build
rm -f *.aux *.log *.out

# Compile (should succeed in 1-2 runs)
pdflatex main.tex
pdflatex main.tex

# Check for errors
echo $?  # Should be 0

# Verify PDF generated
ls -lh main.pdf
```

#### 4. Create Tarball

```bash
# From submission directory
tar czf ../paper-YYYY-MM.tar.gz *

# Verify contents
tar tzf ../paper-YYYY-MM.tar.gz | head -20
```

#### 5. Validate Package

**Checklist**:
- [ ] Main `.tex` at root level
- [ ] `.bbl` included (same basename as `.tex`)
- [ ] All `.sty` files included
- [ ] Figures are PDF/PNG/JPEG (no .eps)
- [ ] No absolute paths in `.tex`
- [ ] Compiles cleanly with `pdflatex main.tex`
- [ ] Package size < 50 MB
- [ ] No spaces or special chars in filenames

#### 6. Upload to ArXiv

1. Login to arXiv.org
2. Start new submission
3. Select category (cs.OS for operating systems)
4. Upload `.tar.gz` or `.zip` file
5. ArXiv will compile and show preview
6. Review metadata (title, authors, abstract)
7. Submit

---

## Metadata Requirements

### Title

**Format**: Title Case, no ALL CAPS

**Good**:
```latex
\title{Exhaustive Analysis of the MINIX-3 Kernel Boot Sequence}
```

**Bad**:
```latex
\title{EXHAUSTIVE ANALYSIS OF THE MINIX-3 KERNEL BOOT SEQUENCE}  % All caps
```

### Authors

**Format**:
```latex
\author{
    Author Name\\
    \textit{Affiliation}\\
    \texttt{email@example.com}
}
```

**Multiple Authors**:
```latex
\author{
    Author One\thanks{Institution 1, email1@example.com} \and
    Author Two\thanks{Institution 2, email2@example.com}
}
```

### Abstract

**Length**: 100-250 words recommended

**Structure**:
1. Problem statement
2. Methodology
3. Key findings
4. Significance

**Example**:
```latex
\begin{abstract}
This paper presents an exhaustive analysis of the MINIX-3 microkernel boot sequence. We employ static code analysis and graph theory to decompose the \texttt{kmain()} function (523 lines) into five distinct initialization phases. Our analysis reveals a hub-and-spoke topology with \texttt{kmain()} as central orchestrator (degree centrality = 34). We demonstrate that no infinite loop exists in \texttt{kmain()}; instead, the system performs a unidirectional transition via \texttt{switch\_to\_user()}, which never returns. Performance analysis estimates the critical path at 85--100ms on modern hardware.
\end{abstract}
```

### Keywords

**Format**: Comma-separated, lowercase

```latex
% In document metadata
\hypersetup{
    pdfkeywords={MINIX, microkernel, boot sequence, operating systems, i386}
}

% Or in abstract section
\textbf{Keywords:} MINIX, microkernel, boot sequence, operating systems, i386
```

---

## Common Errors and Fixes

### 1. Compilation Timeout

**Error**: ArXiv compilation times out (5 minute limit)

**Causes**:
- Too many TikZ diagrams (slow compilation)
- Infinite loops in macros
- Excessive package loading

**Fixes**:
- Externalize TikZ graphics:
```latex
\usetikzlibrary{external}
\tikzexternalize
```
- Simplify complex diagrams
- Remove unused packages

### 2. Missing Figure

**Error**: `File 'figure.pdf' not found`

**Causes**:
- Figure not included in upload
- Wrong path in `\includegraphics{}`
- Case mismatch (`Figure.pdf` vs `figure.pdf`)

**Fixes**:
- Verify figure in tarball: `tar tzf paper.tar.gz | grep figure`
- Use relative paths: `figures/diagram.pdf`
- Match case exactly

### 3. Bibliography Empty

**Error**: References section is empty

**Causes**:
- `.bbl` file not included
- `.bbl` filename doesn't match `.tex` filename

**Fixes**:
- Include `main.bbl` if `main.tex`
- Regenerate `.bbl` locally with BibTeX

### 4. Hyperref Option Clash

**Error**: `Option clash for package hyperref`

**Cause**: ArXiv auto-loads hyperref with options

**Fix**: Only use `\hypersetup{}`, not `\usepackage[options]{hyperref}`

```latex
% BAD
\usepackage[colorlinks=true]{hyperref}

% GOOD
\usepackage{hyperref}
\hypersetup{colorlinks=true}
```

---

## Best Practices for MINIX Papers

### 1. Use Shared Style Package

**Advantage**: Single `.sty` file simplifies submissions

**Structure**:
```latex
% minix-styles.sty (include in submission)
\ProvidesPackage{minix-styles}
\RequirePackage{minix-colors}
\RequirePackage{minix-arxiv}
\RequirePackage{tikz}
% ... all common packages
```

**In main.tex**:
```latex
\documentclass{article}
\usepackage{minix-styles}  % One-line import
```

### 2. Modular Sections

**Advantage**: Easier to manage long papers

**Structure**:
```
paper/
├── main.tex
├── sections/
│   ├── introduction.tex
│   ├── methodology.tex
│   ├── results.tex
│   └── conclusion.tex
```

**In main.tex**:
```latex
\section{Introduction}
\input{sections/introduction}

\section{Methodology}
\input{sections/methodology}
```

### 3. Consistent Naming

**Files**:
- `minix-cpu-analysis.tex` (CPU paper)
- `minix-boot-arxiv.tex` (Boot paper)
- `minix-*.sty` (Style files)

**Figures**:
- `cpu-syscall-int-flow.pdf`
- `cpu-syscall-sysenter-flow.pdf`
- `boot-topology-hub-spoke.pdf`

### 4. Version Control for Submissions

**Strategy**: Tag each ArXiv submission

```bash
# Create submission package
./scripts/create-arxiv-package.sh cpu-interface

# Tag in git
git tag -a arxiv-cpu-v1.0 -m "ArXiv submission CPU interface v1.0"
git push origin arxiv-cpu-v1.0
```

**Directory**:
```
arxiv-submissions/
├── cpu-interface-2025-10/
│   ├── minix-cpu-analysis.tex
│   ├── minix-cpu-analysis.bbl
│   └── ...
└── boot-sequence-2025-10/
    ├── minix-boot-arxiv.tex
    └── ...
```

---

## Automation Scripts

### create-arxiv-package.sh

Located at `/home/eirikr/Playground/minix-analysis/scripts/create-arxiv-package.sh`:

```bash
#!/bin/bash
# Create ArXiv submission package for a module
# Usage: ./create-arxiv-package.sh <module-name>

set -e

MODULE=$1
DATE=$(date +%Y-%m)
PACKAGE_DIR="arxiv-submissions/${MODULE}-${DATE}"
MODULE_DIR="modules/${MODULE}"

if [[ -z "$MODULE" ]]; then
    echo "Usage: $0 <module-name>"
    echo "Example: $0 cpu-interface"
    exit 1
fi

if [[ ! -d "$MODULE_DIR" ]]; then
    echo "Error: Module $MODULE not found"
    exit 1
fi

echo "Creating ArXiv package for $MODULE..."

# Create package directory
mkdir -p "$PACKAGE_DIR"

# Find main .tex file
MAIN_TEX=$(find "$MODULE_DIR/latex" -maxdepth 1 -name "*arxiv.tex" -o -name "*-analysis.tex" | head -1)
if [[ -z "$MAIN_TEX" ]]; then
    echo "Error: No main .tex file found in $MODULE_DIR/latex"
    exit 1
fi

BASENAME=$(basename "$MAIN_TEX" .tex)
echo "Main file: $BASENAME.tex"

# Copy main .tex
cp "$MAIN_TEX" "$PACKAGE_DIR/$BASENAME.tex"

# Generate .bbl if .bib exists
if [[ -f "$MODULE_DIR/latex/$BASENAME.bib" ]]; then
    echo "Generating .bbl from .bib..."
    cd "$MODULE_DIR/latex"
    pdflatex "$BASENAME.tex"
    bibtex "$BASENAME"
    pdflatex "$BASENAME.tex"
    cp "$BASENAME.bbl" "../../$PACKAGE_DIR/"
    cd ../../
elif [[ -f "$MODULE_DIR/latex/$BASENAME.bbl" ]]; then
    # Copy existing .bbl
    cp "$MODULE_DIR/latex/$BASENAME.bbl" "$PACKAGE_DIR/"
else
    echo "Warning: No .bbl or .bib file found"
fi

# Copy shared style files
echo "Copying shared style files..."
cp shared/styles/*.sty "$PACKAGE_DIR/"

# Copy figures (convert .eps to .pdf if needed)
echo "Copying figures..."
mkdir -p "$PACKAGE_DIR/figures"
if [[ -d "$MODULE_DIR/latex/figures" ]]; then
    for file in "$MODULE_DIR/latex/figures"/*; do
        if [[ "$file" == *.eps ]]; then
            epstopdf "$file" --outfile="$PACKAGE_DIR/figures/$(basename "$file" .eps).pdf"
        elif [[ "$file" == *.pdf ]] || [[ "$file" == *.png ]] || [[ "$file" == *.jpg ]]; then
            cp "$file" "$PACKAGE_DIR/figures/"
        fi
    done
fi

# Create tarball
echo "Creating tarball..."
cd "$PACKAGE_DIR"
tar czf "../${MODULE}-${DATE}.tar.gz" *
cd ../../

# Verify package
echo ""
echo "=========================================="
echo "ArXiv package created:"
echo "  Directory: $PACKAGE_DIR"
echo "  Tarball:   arxiv-submissions/${MODULE}-${DATE}.tar.gz"
echo "=========================================="
echo ""
echo "Contents:"
tar tzf "arxiv-submissions/${MODULE}-${DATE}.tar.gz" | head -20
echo ""
echo "Next steps:"
echo "1. Verify package compiles: cd $PACKAGE_DIR && pdflatex $BASENAME.tex"
echo "2. Upload to ArXiv: https://arxiv.org/submit"
echo "3. Select category: cs.OS (Operating Systems)"
echo ""
```

**Make executable**:
```bash
chmod +x scripts/create-arxiv-package.sh
```

---

## Testing Before Submission

### Local Compilation Test

```bash
cd arxiv-submissions/module-YYYY-MM

# Clean environment
rm -f *.aux *.log *.out *.toc

# Test compilation (fresh)
pdflatex main.tex
pdflatex main.tex

# Check output
if [[ $? -eq 0 ]]; then
    echo "✅ Compilation successful"
    ls -lh main.pdf
else
    echo "❌ Compilation failed"
    tail -50 main.log
fi
```

### Package Integrity Test

```bash
# Extract tarball to temp directory
mkdir /tmp/arxiv-test
cd /tmp/arxiv-test
tar xzf /path/to/paper-YYYY-MM.tar.gz

# Verify structure
tree -L 2

# Test compilation from extracted package
pdflatex main.tex
pdflatex main.tex
```

---

## Quick Reference Checklist

Before uploading to ArXiv:

- [ ] Main `.tex` at root level
- [ ] `.bbl` included (matches `.tex` basename)
- [ ] All `.sty` files included
- [ ] Figures are PDF/PNG/JPEG (no .eps)
- [ ] No absolute paths
- [ ] No spaces in filenames
- [ ] `hyperref` uses `colorlinks=true`
- [ ] Compiles with `pdflatex` (TeX Live 2023)
- [ ] Package size < 50 MB
- [ ] Title, author, abstract properly formatted
- [ ] Keywords specified
- [ ] Test compilation from extracted tarball

---

## References

1. **ArXiv Help**: https://info.arxiv.org/help/
2. **Submit Guidelines**: https://info.arxiv.org/help/submit/index.html
3. **TeX/LaTeX Submissions**: https://info.arxiv.org/help/submit_tex.html
4. **Overleaf Checklist**: https://www.overleaf.com/learn/how-to/LaTeX_checklist_for_arXiv_submissions
5. **TeX Live**: https://tug.org/texlive/

---

*Next: Implement automation scripts for ArXiv package creation*
