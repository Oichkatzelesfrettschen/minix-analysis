# Contributing Guidelines

**MINIX Analysis Project - Contribution Guide**

---

## Welcome

Thank you for your interest in contributing to the MINIX Analysis project! This document provides guidelines for contributing code, documentation, diagrams, and research content.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Documentation Standards](#documentation-standards)
6. [Testing Requirements](#testing-requirements)
7. [Pull Request Process](#pull-request-process)
8. [LaTeX Guidelines](#latex-guidelines)
9. [Diagram Guidelines](#diagram-guidelines)

---

## Code of Conduct

### Our Standards

- **Respectful**: Treat all contributors with respect
- **Constructive**: Provide constructive feedback
- **Collaborative**: Work together toward common goals
- **Academic Rigor**: Maintain high standards for research quality

### Academic Integrity

- Cite all sources appropriately
- Credit original authors for code/ideas
- Do not plagiarize or misrepresent work
- Follow academic citation standards (APA, IEEE, etc.)

---

## Getting Started

### Prerequisites

**Required**:
- Python 3.10+
- LaTeX (TeX Live 2023+)
- LuaLaTeX (for Spline Sans fonts)
- GNU Make 4.0+
- Git

**Optional**:
- Spline Sans fonts (for typography)
- pytest (for testing)
- Black (for Python formatting)
- Ruff (for Python linting)

### Fork and Clone

**1. Fork the repository**:
```bash
# Via GitHub web interface
# https://github.com/oaich/minix-analysis/fork
```

**2. Clone your fork**:
```bash
git clone https://github.com/YOUR_USERNAME/minix-analysis.git
cd minix-analysis
```

**3. Add upstream remote**:
```bash
git remote add upstream https://github.com/oaich/minix-analysis.git
git fetch upstream
```

### Install Dependencies

**LaTeX**:
```bash
# Arch Linux
sudo pacman -S texlive-most texlive-luatex

# Ubuntu/Debian
sudo apt install texlive-full texlive-luatex
```

**Python**:
```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Fonts**:
```bash
wget "https://fonts.google.com/download?family=Spline%20Sans"
unzip SplineSans.zip -d ~/.fonts/SplineSans/
fc-cache -fv
```

---

## Development Workflow

### Branch Naming

**Feature branches**:
```bash
git checkout -b feature/add-memory-analysis
git checkout -b feature/syscall-benchmarks
```

**Bug fix branches**:
```bash
git checkout -b fix/tikz-compile-error
git checkout -b fix/mcp-server-path
```

**Documentation branches**:
```bash
git checkout -b docs/update-installation
git checkout -b docs/add-api-examples
```

### Commit Messages

**Format**: `type: subject` (imperative mood)

**Types**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code formatting (no logic change)
- `refactor:` Code restructure (no behavior change)
- `test:` Add or modify tests
- `chore:` Build system, dependencies

**Examples**:
```bash
git commit -m "feat: add TLB miss cost analysis"
git commit -m "fix: correct SYSENTER cycle count"
git commit -m "docs: update installation guide for Arch Linux"
git commit -m "test: add syscall mechanism comparison tests"
```

**Body** (optional):
```bash
git commit -m "feat: add memory layout diagrams

- Create page table hierarchy diagram
- Add TLB architecture visualization
- Document CR3 register structure

Closes #42"
```

### Keep Updated

**Sync with upstream**:
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Rebase feature branch**:
```bash
git checkout feature/my-feature
git rebase main
```

---

## Code Standards

### Python Code

**Style**: PEP 8 (enforced by Black and Ruff)

**Formatting**:
```bash
# Format with Black
black servers/ tests/

# Lint with Ruff
ruff check servers/ tests/
```

**Type Hints**:
```python
def analyze_syscall(mechanism: str) -> dict[str, Any]:
    """Analyze system call mechanism.

    Args:
        mechanism: "INT" | "SYSENTER" | "SYSCALL"

    Returns:
        Dictionary with analysis results
    """
    return {"mechanism": mechanism, "cycles": 1305}
```

**Docstrings**: Google style
```python
def query_architecture(query: str) -> dict:
    """Get i386 architecture details.

    Args:
        query: Search query (e.g., "registers", "paging")

    Returns:
        Dictionary containing architecture data

    Raises:
        KeyError: If query not found in data
    """
    pass
```

### LaTeX Code

**Line Length**: ≤100 characters

**Indentation**: 2 spaces (not tabs)

**Formatting**:
```latex
% Good
\begin{tikzpicture}[cpu flow]
  \node[box] (user) {User Space};
  \node[hw, below=of user] (cpu) {CPU};
  \draw[arrow] (user) -- (cpu);
\end{tikzpicture}

% Bad (inconsistent indentation, long lines)
\begin{tikzpicture}[cpu flow]
\node[box] (user) {User Space (Ring 3) with very long text that exceeds 100 characters};
    \node[hw,below=of user] (cpu) {CPU};
  \draw[arrow] (user) -- (cpu);
\end{tikzpicture}
```

**Comments**:
```latex
% Clear section headers
% ====================
% System Call Entry Points
% ====================

% Explain non-obvious choices
\cvdsetup[variant=protan]  % Protanopia variant for accessibility
```

---

## Documentation Standards

### Markdown Files

**Formatting**:
- Use `#` for headers (not underlines)
- Blank line before/after code blocks
- Consistent list markers (`-` for unordered, `1.` for ordered)
- 80-100 character line length (soft limit)

**Code Blocks**:
````markdown
```bash
# Always specify language
make cpu
```

```python
# Include comments for clarity
def main():
    pass  # Implementation here
```
````

**Links**:
```markdown
<!-- Use relative links for internal docs -->
See [Installation Guide](../INSTALLATION.md)

<!-- Use descriptive text, not "click here" -->
Good: [Build system documentation](build-system/Overview.md)
Bad: [Click here](build-system/Overview.md)
```

### API Documentation

**MCP Tools**: Document all parameters and return types
```python
@server.call_tool()
async def new_tool(param: str) -> list[TextContent]:
    """Brief one-line description.

    Detailed explanation of what this tool does,
    when to use it, and any important notes.

    Args:
        param: Description of parameter

    Returns:
        TextContent with JSON-encoded result

    Example:
        >>> new_tool("query")
        [TextContent(text='{"result": "data"}')]
    """
    pass
```

---

## Testing Requirements

### Coverage Targets

**Backend**: >90% coverage
**Integration**: All critical paths tested
**MCP Servers**: 100% tool coverage

### Python Tests

**Structure**:
```python
# tests/test_new_feature.py

def test_basic_functionality():
    """Test the basic happy path."""
    result = my_function("input")
    assert result == "expected"

def test_error_handling():
    """Test error cases."""
    with pytest.raises(ValueError):
        my_function(None)

def test_edge_cases():
    """Test boundary conditions."""
    assert my_function("") == ""
    assert my_function("x" * 1000) is not None
```

**Run tests**:
```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
source venv/bin/activate
pytest -v
pytest --cov=servers --cov-report=html
```

### LaTeX Tests

**Compilation Test**:
```bash
cd modules/cpu-interface
make test
# Should compile without errors
```

**Diagram Test**:
```bash
cd modules/cpu-interface/latex/figures
lualatex syscall-int-flow.tex
# Should produce PDF without errors
```

---

## Pull Request Process

### Before Submitting

**Checklist**:
- [ ] Code follows style guidelines (Black, Ruff)
- [ ] All tests pass (`pytest -v`)
- [ ] LaTeX compiles without errors (`make test`)
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with main

### Submit PR

**1. Push to your fork**:
```bash
git push origin feature/my-feature
```

**2. Create PR on GitHub**:
- Title: Clear, concise description
- Description: Explain what and why (not just how)
- Link related issues: `Closes #42`

**3. PR Template**:
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Added unit tests
- [ ] LaTeX compiles
- [ ] All existing tests pass

## Screenshots (if applicable)
Attach diagram PDFs or visualizations
```

### Review Process

**Timeline**: 2-7 days for initial review

**Expectations**:
- Address reviewer feedback promptly
- Keep discussion professional and constructive
- Be open to suggestions and changes

**Approval**: 1 maintainer approval required

---

## LaTeX Guidelines

### Shared Styles

**Always use shared styles**:
```latex
\documentclass{article}
\usepackage{minix-arxiv}     % ArXiv compliance + Spline Sans
\usepackage{minix-styles}    % TikZ/PGFPlots styles
```

**Never hardcode colors**:
```latex
% Bad
\node[fill=blue!10] {Box};

% Good
\node[fill=flowbox, draw=primaryblue] {Box};
```

### New Diagrams

**Standalone Format**:
```latex
\documentclass{standalone}
\usepackage{minix-colors}
\usepackage{tikz}
\usepackage{minix-styles}

\begin{document}
\begin{tikzpicture}[cpu flow]
  % Diagram content
\end{tikzpicture}
\end{document}
```

**File Naming**: `##-descriptive-name.tex`
- `##`: Two-digit sequence number
- Lowercase, hyphen-separated
- Descriptive, not generic

**Examples**:
- `05-syscall-int-flow.tex` ✓
- `06-syscall-sysenter-flow.tex` ✓
- `diagram.tex` ✗ (too generic)
- `my_diagram.tex` ✗ (underscores)

### Accessibility

**Use CVD mode for new diagrams**:
```latex
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]
\cvdapplyplotstyles

% Use cvd* colors instead of raw colors
\node[fill=cvdBlue700!15, draw=cvdBlue700] {Box};
```

---

## Diagram Guidelines

### TikZ Best Practices

**Use positioning library**:
```latex
\usetikzlibrary{positioning}

% Good
\node[box] (A) {Box A};
\node[box, below=of A] (B) {Box B};

% Bad
\node[box] (A) at (0,0) {Box A};
\node[box] (B) at (0,-2) {Box B};
```

**Clear node names**:
```latex
% Good
\node[box] (user_space) {User Space};
\node[hw] (cpu_interrupt) {CPU INT};

% Bad
\node[box] (n1) {User Space};
\node[hw] (n2) {CPU INT};
```

### PGFPlots Charts

**Always label axes**:
```latex
\begin{axis}[
    minix axis,
    xlabel={Syscall Mechanism},
    ylabel={Cycles},
    ymin=0,
    legend pos=north west
]
  \addplot[minix bar] coordinates {...};
  \legend{INT, SYSENTER, SYSCALL}
\end{axis}
```

**Use semantic styles**:
```latex
% Good
\addplot[minix line, color=primaryblue] {...};

% Bad
\addplot[line width=1pt, color={rgb,255:red,0;green,102;blue,204}] {...};
```

---

## Research Contributions

### Adding Analysis Modules

**New module structure**:
```
modules/my-analysis/
├── docs/
│   ├── ANALYSIS.md          # Main documentation
│   └── DETAILED-NOTES.md    # Supplementary notes
├── latex/
│   ├── paper.tex            # Main paper
│   ├── figures/             # Standalone diagrams
│   └── plots/               # Performance charts
├── Makefile                 # Build system
└── README.md                # Module overview
```

**Integration checklist**:
- [ ] Add to root Makefile
- [ ] Update wiki Home.md
- [ ] Create module overview page
- [ ] Add to INSTALLATION.md
- [ ] Test build: `make my-analysis`

### Citing Sources

**LaTeX citations**:
```latex
According to Tanenbaum~\cite{tanenbaum2014operating},
MINIX uses a microkernel architecture.

% In .bib file:
@book{tanenbaum2014operating,
  title={Operating Systems: Design and Implementation},
  author={Tanenbaum, Andrew S and Woodhull, Albert S},
  year={2014},
  publisher={Pearson}
}
```

**Markdown citations**:
```markdown
> MINIX 3 is a free, open-source, operating system designed to be
> highly reliable, flexible, and secure. [^1]

[^1]: Tanenbaum, A. S., & Woodhull, A. S. (2014).
      *Operating Systems: Design and Implementation*. Pearson.
```

---

## Questions and Support

### Getting Help

**Documentation**:
- [Installation Guide](../INSTALLATION.md)
- [Build System](build-system/Overview.md)
- [Style Guide](style-guide/Overview.md)
- [MCP API](api/MCP-Servers.md)

**Community**:
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and general discussion
- Email: eirikr@oaich.dev

### Reporting Issues

**Bug Report Template**:
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Run `make cpu`
2. Observe error in file X
3. See compilation failure

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Arch Linux / CachyOS
- LaTeX: TeX Live 2023
- Python: 3.13

## Additional Context
Any other relevant information
```

---

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Maintainer**: Oaich (eirikr@oaich.dev)
