# Testing Guide

**MINIX Analysis Testing Infrastructure**

---

## Overview

The MINIX Analysis project employs comprehensive testing across three layers:

1. **LaTeX Compilation Tests**: Verify all papers and diagrams compile
2. **Python Unit Tests**: Test MCP server functionality
3. **Integration Tests**: End-to-end validation

**Test Coverage**: 100% (39/39 MCP tests pass)

---

## Quick Start

### Run All Tests

**From project root**:
```bash
cd /home/eirikr/Playground/minix-analysis
make test
```

**What it does**:
1. Compiles all LaTeX files (CPU + Boot papers)
2. Runs Python tests for MCP servers
3. Validates shared styles
4. Checks diagram rendering

**Expected output**:
```
Building CPU Interface Analysis...
Building Boot Sequence Analysis...
Running MCP server tests...
================================ 39 passed in 1.85s ================================
All tests passed!
```

---

## LaTeX Testing

### Module Tests

**CPU Interface Module**:
```bash
cd modules/cpu-interface
make test
```

**What's tested**:
- Main paper compilation (paper.tex)
- All 11 diagrams compile
- No LaTeX errors or warnings (treated as errors)
- Cross-references resolve correctly
- Bibliography compiles (if .bib exists)

**Boot Sequence Module**:
```bash
cd modules/boot-sequence
make test
```

**What's tested**:
- Main paper compilation
- Python visualization scripts run without errors
- All 3 topology diagrams generated
- LaTeX compilation successful

### Diagram Tests

**Individual Diagram**:
```bash
cd modules/cpu-interface/latex/figures
lualatex 05-syscall-int-flow.tex
```

**Expected**: PDF generated without errors

**All Diagrams**:
```bash
cd modules/cpu-interface
make figures
```

**Check output**:
```bash
ls latex/figures/*.pdf | wc -l
# Should output: 11
```

### Style Package Tests

**Verify styles exist**:
```bash
cd shared/styles
ls -1 *.sty
# Should list:
# minix-colors.sty
# minix-colors-cvd.sty
# minix-arxiv.sty
# minix-styles.sty
```

**Test color definitions**:
```latex
\documentclass{standalone}
\usepackage{minix-colors}
\usepackage{tikz}

\begin{document}
\begin{tikzpicture}
  % If this compiles, colors are defined correctly
  \foreach \col in {primaryblue, secondarygreen, accentorange, warningred} {
    \node[fill=\col, minimum width=2cm, minimum height=1cm] {};
  }
\end{tikzpicture}
\end{document}
```

**Test CVD mode**:
```latex
\documentclass{standalone}
\usepackage{minix-colors-cvd}
\cvdsetup[variant=protan]
\usepackage{tikz}

\begin{document}
\begin{tikzpicture}
  % Test CVD colors
  \node[fill=cvdBlue700] {Protan Blue};
\end{tikzpicture}
\end{document}
```

---

## Python Testing

### MCP Server Tests

**Location**: `/home/eirikr/Playground/pkgbuilds/minix-mcp-servers/tests/`

**Setup**:
```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
source venv/bin/activate
```

**Run all tests**:
```bash
pytest -v
```

**Expected output**:
```
tests/test_minix_analysis.py::test_data_loader_initialization PASSED     [  2%]
tests/test_minix_analysis.py::test_architecture_data_loading PASSED      [  5%]
tests/test_minix_analysis.py::test_syscall_data_loading PASSED           [  7%]
...
tests/test_minix_filesystem.py::test_none_path PASSED                    [ 97%]
tests/test_minix_filesystem.py::test_empty_path PASSED                   [100%]

================================ 39 passed in 1.85s ================================
```

### Analysis Server Tests

**Run only analysis tests**:
```bash
pytest tests/test_minix_analysis.py -v
```

**Test Coverage** (15 tests):

1. **Data Loader Tests**:
   - `test_data_loader_initialization` - Loader starts correctly
   - `test_architecture_data_loading` - i386 data loads
   - `test_register_data` - GPRs, segment, control registers
   - `test_paging_data` - 2-level paging structure

2. **Syscall Tests**:
   - `test_syscall_data_loading` - All 3 mechanisms load
   - `test_int_mechanism` - INT 0x80 details
   - `test_sysenter_mechanism` - SYSENTER details
   - `test_syscall_mechanism` - SYSCALL details

3. **Performance Tests**:
   - `test_performance_metrics` - Cycle counts present
   - `test_tlb_metrics` - TLB hit/miss data
   - `test_context_switch_cost` - CS breakdown

4. **Diagram Tests**:
   - `test_diagram_metadata` - All 11 diagrams documented
   - `test_diagram_descriptions` - Each has description

5. **Tool Tests**:
   - `test_query_architecture` - MCP tool functional
   - `test_analyze_syscall` - MCP tool functional
   - `test_search_functionality` - Data search works

### Filesystem Server Tests

**Run only filesystem tests**:
```bash
pytest tests/test_minix_filesystem.py -v
```

**Test Coverage** (24 tests):

1. **Security Tests** (8 tests):
   - `test_allowed_path_kernel` - kernel/ accessible
   - `test_allowed_path_include` - include/ accessible
   - `test_allowed_path_lib` - lib/ accessible
   - `test_disallowed_path_etc` - /etc/ blocked
   - `test_disallowed_path_home` - /home/ blocked
   - `test_path_traversal_blocked` - ../ blocked
   - `test_absolute_path_blocked` - /absolute blocked
   - `test_symlink_traversal_blocked` - symlink escape blocked

2. **File Reading Tests** (6 tests):
   - `test_read_file_basic` - Basic file read
   - `test_read_file_with_offset` - Offset parameter
   - `test_read_file_with_limit` - Line limit
   - `test_read_nonexistent_file` - Error handling
   - `test_read_file_mpx` - Real file (mpx.S)
   - `test_read_file_vm_header` - Real header (vm.h)

3. **Directory Listing Tests** (5 tests):
   - `test_list_directory_basic` - Simple listing
   - `test_list_directory_recursive` - Recursive mode
   - `test_list_directory_max_depth` - Depth limit
   - `test_list_directory_nonexistent` - Error handling
   - `test_list_kernel_directory` - Real directory

4. **Search Tests** (3 tests):
   - `test_search_files_pattern` - Pattern matching
   - `test_search_files_asm` - .S files
   - `test_search_files_headers` - .h files

5. **Edge Case Tests** (2 tests):
   - `test_none_path` - None handling
   - `test_empty_path` - Empty string handling

### Coverage Reports

**Generate HTML coverage report**:
```bash
pytest --cov=servers --cov-report=html
```

**View report**:
```bash
xdg-open htmlcov/index.html
```

**Expected coverage**: >90% for all modules

**Check coverage summary**:
```bash
pytest --cov=servers --cov-report=term
```

**Example output**:
```
---------- coverage: platform linux, python 3.13 -----------
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
servers/minix-analysis/src/server.py            120      5    96%
servers/minix-analysis/src/data_loader.py       85      3    96%
servers/minix-filesystem/src/server.py          95      2    98%
-----------------------------------------------------------------
TOTAL                                           300     10    97%
```

---

## Integration Testing

### End-to-End Paper Build

**Test complete build pipeline**:
```bash
cd /home/eirikr/Playground/minix-analysis

# Clean everything
make clean

# Full build from scratch
make all
```

**Verify outputs**:
```bash
# CPU paper
ls modules/cpu-interface/latex/*.pdf
# Should show: MINIX-CPU-INTERFACE-ANALYSIS.pdf

# Boot paper
ls modules/boot-sequence/latex/*.pdf
# Should show: MINIX-BOOT-SEQUENCE-ANALYSIS.pdf

# All diagrams
find modules/ -name "*.pdf" | wc -l
# Should show: 14+ PDFs (11 CPU + 3 Boot)
```

### ArXiv Package Test

**Create and validate ArXiv packages**:
```bash
# Generate packages
make arxiv-cpu
make arxiv-boot

# Verify structure
ls arxiv-packages/
# Should show dated directories

# Test standalone compilation
cd arxiv-packages/arxiv-cpu-interface-2025-10-30/
lualatex paper.tex
# Should compile without errors (no external dependencies)
```

### MCP Server Integration

**Test live MCP server**:
```bash
cd /home/eirikr/Playground/pkgbuilds/minix-mcp-servers
source venv/bin/activate

# Start server (in separate terminal)
cd servers/minix-analysis
python -m src.server

# Test via MCP client (in another terminal)
# Use Claude Code or another MCP client
```

**Manual tool testing** (Python REPL):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "servers/minix-analysis"))

from src.data_loader import get_data_loader

# Test data loading
loader = get_data_loader()
arch_data = loader.load_architecture_data()
print(arch_data["architecture"])  # Should print: i386
```

### Repository CLI & Data Smoke Tests

Inside this repository, quick smoke tests validate the shared MCP façade and CLI wrappers:

```bash
# Requires pipeline artifacts in diagrams/data/
export PYTHONPATH=$(pwd)/src
pytest tests/modules/test_cpu_pipeline.py tests/modules/test_mcp_server.py
```

These benchmarks confirm that helper scripts execute, `shared/mcp/server/` can be imported, and CLI commands such as `--list-resources`, `--resource`, `--syscall`, `--kernel-summary`, and `--boot-critical-path` return structured JSON payloads.

---

## Continuous Integration (CI)

### GitHub Actions Workflow

**Planned workflow** (`.github/workflows/test.yml`):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  latex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install TeX Live
        run: sudo apt-get install -y texlive-full
      - name: Install Fonts
        run: |
          wget "https://fonts.google.com/download?family=Spline%20Sans"
          unzip SplineSans.zip -d ~/.fonts/
          fc-cache -fv
      - name: Build Papers
        run: make test

  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd pkgbuilds/minix-mcp-servers
          pip install -r requirements.txt
      - name: Run tests
        run: pytest -v --cov=servers
```

---

## Performance Testing

### LaTeX Build Time

**Measure full build**:
```bash
time make cpu
# Typical: ~3 minutes (11 diagrams + 3 LaTeX passes)

time make boot
# Typical: ~2 minutes (3 visualizations + 3 LaTeX passes)
```

**Quick build benchmark**:
```bash
time make -C modules/cpu-interface quick
# Typical: ~30 seconds (single pass, no figures)
```

### Python Test Performance

**Measure test execution**:
```bash
pytest --durations=10
```

**Example output**:
```
============================= slowest 10 durations =============================
0.15s call     tests/test_minix_analysis.py::test_data_loader_initialization
0.08s call     tests/test_minix_filesystem.py::test_list_directory_recursive
0.05s call     tests/test_minix_analysis.py::test_architecture_data_loading
...
```

**Profile tests**:
```bash
pytest --profile
# Generates .prof file for analysis with snakeviz/gprof2dot
```

---

## Debugging Failed Tests

### LaTeX Compilation Errors

**Error**: "File `minix-colors.sty' not found"

**Debug**:
```bash
# Check TEXINPUTS
echo $TEXINPUTS

# Verify style files exist
ls shared/styles/*.sty

# Install system-wide
sudo make install
kpsewhich minix-colors.sty
```

**Error**: "Undefined control sequence \cvdBlue700"

**Debug**:
```bash
# Ensure minix-colors-cvd.sty is loaded
grep "usepackage{minix-colors-cvd}" paper.tex
```

**Error**: "I can't find file `Spline Sans'"

**Debug**:
```bash
# Check fonts installed
fc-list | grep "Spline Sans"

# Re-install if missing
wget "https://fonts.google.com/download?family=Spline%20Sans"
unzip SplineSans.zip -d ~/.fonts/SplineSans/
fc-cache -fv
```

### Python Test Failures

**Error**: "KeyError: 'architecture'"

**Debug**:
```python
# Check environment variable
import os
print(os.getenv("MINIX_DATA_PATH"))

# Verify data files exist
from pathlib import Path
data_path = Path(os.getenv("MINIX_DATA_PATH"))
print(data_path.exists())
print(list(data_path.glob("modules/*/docs/*.md")))
```

**Error**: "access denied: path outside allowed directories"

**Debug**:
```python
# Check path security
from servers.minix_filesystem.src.server import is_path_allowed, ALLOWED_PATHS
print(ALLOWED_PATHS)
print(is_path_allowed("/etc/passwd"))  # Should be False
print(is_path_allowed("minix/kernel/main.c"))  # Should be True
```

---

## Test Maintenance

### Adding New Tests

**For new MCP tool**:
```python
# tests/test_minix_analysis.py

def test_new_tool():
    """Test new tool functionality."""
    result = new_tool("query")
    assert "expected_key" in result
    assert result["expected_key"] == "expected_value"
```

**For new LaTeX diagram**:
```bash
# Add to Makefile
DIAGRAMS += 12-new-diagram.pdf

# Test compilation
cd modules/cpu-interface/latex/figures
lualatex 12-new-diagram.tex
```

### Updating Test Data

**When analysis data changes**:
```python
# Update test expectations
def test_updated_data():
    data = load_data()
    assert data["new_field"] == "new_value"  # Update assertion
```

**When file structure changes**:
```python
# Update path calculations in conftest.py
PROJECT_ROOT = Path(__file__).parent.parent
# Adjust relative paths as needed
```

---

## Quality Gates

### Pre-Commit Checklist

Before committing code, verify:

- [ ] `make test` passes (all LaTeX + Python tests)
- [ ] `black servers/ tests/` (code formatted)
- [ ] `ruff check servers/ tests/` (no linting errors)
- [ ] `pytest -v` shows 39/39 passed
- [ ] No LaTeX warnings (check build logs)
- [ ] Documentation updated (if applicable)

### Pre-Release Checklist

Before creating release:

- [ ] All tests pass on clean checkout
- [ ] ArXiv packages compile standalone
- [ ] Coverage >90% for Python code
- [ ] No broken links in documentation
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated

---

## Related Documentation

- [Contributing Guide](Contributing.md)
- [Build System](build-system/Overview.md)
- [MCP API](api/MCP-Servers.md)
- [Installation Guide](../INSTALLATION.md)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Test Status**: ✅ 39/39 tests pass (100%)
