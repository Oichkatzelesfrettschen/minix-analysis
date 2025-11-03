# MINIX Analysis TikZ Style Guide

**Version:** 1.0.0
**Date:** 2025-10-30
**Package:** `minix-styles.sty`

---

## Overview

The `minix-styles.sty` package provides unified TikZ/PGFPlots styles for all MINIX CPU and Boot Analysis diagrams. It harmonizes the visual language across:

- **CPU Analysis Diagrams** (05-11): Syscall flows, paging, TLB, performance
- **Boot Analysis Diagrams**: Boot sequence topology, call graphs, metrics

---

## Usage

### In Standalone Diagrams (CPU Analysis)

```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{minix-styles}

\begin{document}
\begin{tikzpicture}[cpu flow]
    \node[box] {User: Setup registers};
    \node[hw] {CPU: Hardware action};
    \node[kernelbox] {Kernel: Handler};
\end{tikzpicture}
\end{document}
```

### In Multi-Figure Documents (Boot Analysis)

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{minix-styles}

\begin{document}
\begin{tikzpicture}[boot topology]
    \node[process] {kmain()};
    \node[phase] {Phase 1: Early Init};
    \node[critical] {switch\_to\_user()};
\end{tikzpicture}
\end{document}
```

---

## Color Palette

### Primary Colors

| Color Name | RGB | Hex | Usage |
|------------|-----|-----|-------|
| `primaryblue` | 0,102,204 | #0066CC | Main elements, flow boxes |
| `secondarygreen` | 46,204,113 | #2ECC71 | Success, phases, positive |
| `accentorange` | 255,127,0 | #FF7F00 | Highlights, warnings |
| `warningred` | 231,76,60 | #E74C3C | Critical, errors, hardware |

### Supporting Colors

| Color Name | RGB | Hex | Usage |
|------------|-----|-----|-------|
| `lightgray` | 236,240,241 | #ECF0F1 | Backgrounds, fills |
| `darkgray` | 52,73,94 | #34495E | Text, borders |
| `mediumgray` | 149,165,166 | #95A5A6 | Muted elements |

### Semantic Aliases

| Alias | Definition | Usage Example |
|-------|------------|---------------|
| `flowbox` | `primaryblue!15` | CPU flow diagram boxes |
| `hardware` | `warningred!20` | Hardware operations |
| `kernel` | `secondarygreen!15` | Kernel operations |
| `critical` | `accentorange!25` | Critical paths |
| `background` | `lightgray!50` | Diagram backgrounds |

### Legacy Compatibility (CPU Diagrams)

| Legacy Name | Maps To | Original |
|-------------|---------|----------|
| `cpubox` | RGB 204,229,255 | `blue!10` |
| `hwbox` | RGB 255,204,204 | `red!20` |
| `annotation` | RGB 255,255,204 | `yellow!30` |

---

## Node Styles

### Basic Boxes (CPU Flow Diagrams)

#### `box` - Standard Flow Box
```latex
\node[box] {User: Setup registers};
```
- **Fill:** `flowbox` (light blue)
- **Border:** `primaryblue`
- **Size:** 5.5cm width, 0.7cm min height
- **Corners:** Rounded (2pt)

#### `hw` - Hardware Action
```latex
\node[hw] {CPU: Push EFLAGS};
```
- **Fill:** `hardware` (light red)
- **Border:** `warningred`
- **Style:** Same as `box` but red-themed

#### `kernelbox` - Kernel Operation
```latex
\node[kernelbox] {Kernel: Save context};
```
- **Fill:** `kernel` (light green)
- **Border:** `secondarygreen`
- **Style:** Same as `box` but green-themed

### Boot Analysis Styles

#### `process` - Process/Function Node
```latex
\node[process] {proc\_init()};
```
- **Fill:** `primaryblue!20`
- **Border:** `primaryblue`
- **Size:** 3cm width, 1cm min height
- **Shadow:** Drop shadow (0.5pt offset, 0.3 opacity)
- **Corners:** Rounded (3pt)

#### `phase` - Boot Phase Indicator
```latex
\node[phase] {Phase 1: Early Init};
```
- **Fill:** `secondarygreen!20`
- **Border:** `secondarygreen`
- **Size:** 4cm width, 0.8cm min height
- **Shadow:** Drop shadow

#### `critical` - Critical Path Node
```latex
\node[critical] {switch\_to\_user()};
```
- **Fill:** `accentorange!20`
- **Border:** `warningred` (2pt line)
- **Shadow:** Enhanced (0.4 opacity)
- **Usage:** Entry points, never-return functions

### Call Graph Styles

#### `func` - Internal Function
```latex
\node[func] {kmain()};
```
- **Fill:** `primaryblue!15`
- **Border:** `primaryblue`
- **Size:** 2.5cm × 0.7cm
- **Font:** `\footnotesize`

#### `extfunc` - External/Library Function
```latex
\node[extfunc] {memset()};
```
- **Fill:** `lightgray`
- **Border:** `mediumgray` (dashed)
- **Usage:** stdlib, macros, external dependencies

### Special Purpose

#### `decision` - Decision Diamond
```latex
\node[decision] {Branch?};
```
- **Shape:** Diamond
- **Fill:** `accentorange!20`
- **Border:** `accentorange`

#### `terminate` - Terminal Node
```latex
\node[terminate] {NEVER RETURNS};
```
- **Fill:** `warningred!20`
- **Border:** `warningred` (2pt line)
- **Usage:** End states, unreachable code

#### `infobox` - Information Callout
```latex
\node[infobox] at (x,y) {Metric: Value};
```
- **Fill:** `lightgray`
- **Border:** `darkgray`
- **Width:** 3cm
- **Corners:** Rounded (3pt)

---

## Arrow Styles

### `arrow` - Standard Arrow
```latex
\draw[arrow] (a) -- (b);
```
- **Tip:** Stealth
- **Width:** Thick
- **Color:** `primaryblue`

### `critarrow` - Critical Path Arrow
```latex
\draw[critarrow] (a) -- (b);
```
- **Width:** 2pt (extra thick)
- **Color:** `warningred`

### `dasharrow` - Dashed Connection
```latex
\draw[dasharrow] (a) -- (b);
```
- **Style:** Dashed
- **Color:** `mediumgray`

---

## PGFPlots Styles

### `minix axis` - Standard Axis
```latex
\begin{axis}[minix axis]
    ...
\end{axis}
```
- **Grid:** Major lines, light gray
- **Axis:** 0.5pt, dark gray
- **Labels:** Small font

### `minix bar` - Bar Chart
```latex
\begin{axis}[minix axis]
    \addplot[minix bar] coordinates {...};
\end{axis}
```
- **Width:** 0.8cm bars
- **Fill:** `primaryblue!70`
- **Labels:** Values above bars

### `minix line` - Line Plot
```latex
\addplot[minix line] coordinates {...};
```
- **Width:** Thick
- **Markers:** Filled circles (2pt)

---

## Custom Commands

### `\cyclecost{position}{cycles}`
Annotation for cycle costs (CPU diagrams).

```latex
\cyclecost{at (4.5,-10)}{~1772 cycles}
```
- **Background:** `annotation` (yellow)
- **Border:** `accentorange`
- **Width:** 3cm

### `\phaseheader{position}{text}`
Phase title header (Boot diagrams).

```latex
\phaseheader{at (0,8)}{Boot Sequence Topology}
```
- **Font:** Large, bold
- **Color:** `primaryblue`

### `\metricbox{position}{width}{content}`
Metric display box.

```latex
\metricbox{at (7,4)}{4cm}{Functions: 34\\Depth: 3}
```
- **Background:** `lightgray`
- **Border:** `darkgray`

---

## Diagram Presets

### `cpu flow` - CPU Flow Diagram
```latex
\begin{tikzpicture}[cpu flow]
    % Optimized for vertical flow diagrams
    % Node distance: 0.8cm
    % Font: \small
\end{tikzpicture}
```

### `boot topology` - Boot Topology
```latex
\begin{tikzpicture}[boot topology]
    % Optimized for hub-spoke, topology diagrams
    % Node distance: 2cm
    % Font: \small
\end{tikzpicture}
```

### `call graph` - Call Graph/Tree
```latex
\begin{tikzpicture}[call graph]
    % Optimized for hierarchical trees
    % Level 1: 4cm sibling distance
    % Level 2: 2cm sibling distance
\end{tikzpicture}
```

---

## Migration Guide

### Updating CPU Diagrams (05-11)

**Before:**
```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,calc,fit}

\begin{tikzpicture}[
    box/.style={rectangle, draw, fill=blue!10, ...},
    hw/.style={rectangle, draw, fill=red!20, ...}
]
```

**After:**
```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{minix-styles}

\begin{tikzpicture}[cpu flow]
    % box and hw styles already defined!
```

**Changes:**
1. Replace `\usepackage{tikz}` with `\usepackage{minix-styles}`
2. Remove `\usetikzlibrary` (included in package)
3. Remove inline style definitions
4. Add `cpu flow` preset to tikzpicture options

### Updating Boot Diagrams

**Before:**
```latex
\definecolor{primaryblue}{RGB}{0,102,204}
...
process/.style={rectangle, draw, fill=primaryblue!20, ...}
```

**After:**
```latex
\usepackage{minix-styles}
% All colors and styles pre-defined!
```

---

## Examples

### CPU Syscall Flow (Diagram 05)

```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{minix-styles}

\begin{document}
\begin{tikzpicture}[cpu flow]
    \phaseheader{at (0,0)}{INT Syscall Path}

    \node[box] (user1) at (0,-1.2) {User: Setup registers};
    \node[box] (user2) [below=of user1] {Execute INT 0x21};
    \node[hw] (hw1) [below=of user2] {CPU: Push context};
    \node[kernelbox] (kern1) [below=of hw1] {Kernel: IPC handler};

    \draw[arrow] (user1) -- (user2);
    \draw[arrow] (user2) -- (hw1);
    \draw[arrow] (hw1) -- (kern1);

    \cyclecost{at (4.5,-8)}{~1772 cycles}
\end{tikzpicture}
\end{document}
```

### Boot Topology (Hub-Spoke)

```latex
\documentclass{article}
\usepackage{minix-styles}

\begin{document}
\begin{tikzpicture}[boot topology]
    \phaseheader{at (0,8)}{Boot Sequence Topology}

    \node[critical] (kmain) at (0,5) {kmain()\\Degree: 34};
    \node[phase] (phase1) [left of=kmain, xshift=-4cm] {Phase 1};
    \node[process] (cstart) [below of=phase1] {cstart()};

    \draw[critarrow] (kmain) -- (cstart);

    \metricbox{at (8,5)}{3cm}{Functions: 34\\Files: 8}
\end{tikzpicture}
\end{document}
```

---

## Best Practices

### Color Usage

1. **Consistency:** Use semantic aliases (`flowbox`, `hardware`, `kernel`) instead of direct colors
2. **Accessibility:** Primary palette provides good contrast
3. **Hierarchy:** Use `critical` style sparingly for emphasis

### Node Sizing

1. **Text Width:** Keep consistent within diagram type
   - CPU flow: 5.5cm
   - Boot process: 3-4cm
   - Call graphs: 2.5cm
2. **Height:** Use `minimum height` instead of fixed height for flexibility

### Shadows

1. **CPU Diagrams:** No shadows (clean, minimal)
2. **Boot Diagrams:** Drop shadows for depth (process, phase, critical)

### Arrows

1. **Standard:** Use `arrow` for most connections
2. **Critical Path:** Use `critarrow` for main flow
3. **Optional/Dashed:** Use `dasharrow` for interrupts, callbacks

---

## Troubleshooting

### Undefined Color Error

```
! Package xcolor Error: Undefined color `primaryblue'.
```

**Solution:** Ensure `\usepackage{minix-styles}` is **after** `\documentclass`

### Style Not Applied

**Problem:** Custom styles not working

**Solution:** Check tikzpicture options include appropriate preset:
```latex
\begin{tikzpicture}[cpu flow]  % or [boot topology] or [call graph]
```

### Shadow Not Rendering

**Problem:** Drop shadows not visible in PDF

**Solution:** Ensure `\usetikzlibrary{shadows}` is loaded (included in package)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-30 | Initial release - unified CPU + Boot styles |

---

## References

- **Package File:** `latex/minix-styles.sty`
- **CPU Diagrams:** `latex/figures/05-syscall-int-flow.tex` through `11-context-switch-cost.tex`
- **Boot Diagrams:** `/home/eirikr/Playground/minix-boot-analyzer/visualizations/minix_boot_comprehensive.tex`

---

## License

Part of the MINIX CPU Analysis project.
