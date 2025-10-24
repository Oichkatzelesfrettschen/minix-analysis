# Agent Integration Guide: Math & Science Research Hub

This guide provides comprehensive instructions for LLM agents (such as Claude and Gemini) to effectively assist with research, auditing, and code tasks within this repository. It consolidates general guidelines, project conventions, and agent-specific notes to ensure safe, efficient, and consistent contributions across diverse operating environments, including **Windows**, **Linux** (e.g., CachyOS), **WSL (Windows Subsystem for Linux)**, and **Illumos (e.g., LX Zones)**.

## 1. General Agent Guidelines

### 1.1 Project Structure & Module Organization

*   **`scripts/`**: Automation utilities.
*   **`synthesis/`**: LaTeX assembly for the main monograph.
*   **`modules/equations/`**: Reusable LaTeX equation snippets.
*   **`notes/`**: Research notes, drafts, and synthesis summaries.
*   **`source_materials/`**: Raw references (PDFs, text).
*   **`data/`**: Staging area for catalogs, fixtures, generated outputs.
*   **`extracted_data/`**: Reports and longer-form analyses.
*   **`output/`**: Rendered PDFs and reports.
*   **`docs/`**: Guides, roadmaps, and repository documentation.
*   **`tests/`**: Unit and integration tests.

### 1.2 Build, Test, and Development Commands

Utilize the `Makefile` for common tasks in Unix-like environments (Linux, WSL, macOS, LX Zones). For native Windows, PowerShell scripts (`.ps1`) are often available, or direct Python script execution is possible. Note that `make` commands on Windows typically require a `bash` environment (e.g., Git Bash, WSL).

*   **`make pipeline`**: Rebuilds the catalog from `notes/` and `synthesis/`.
*   **`make audit` / `make parity` / `make gaps`**: Structural, coverage, and TODO diagnostics.
*   **`make smoke`**: Fast regression pass; run before sharing branches.
*   **`make test`**: Executes `pytest -q` across `tests/`.
*   **`make latex` / `make latex_strict`**: Standard and strict LaTeX compiles.
*   **`make reports`**: Generates `DEPS_REPORT.md`, `TODO_TRACKER.md`, `REPO_AUDIT.md`.
*   **`make ascii_guard`**: Enforces ASCII-only policy on code and docs.
*   **`make ascii_normalize`**: Normalize Unicode in docs/summaries to ASCII.

### 1.3 Coding Style & Naming Conventions

*   **Python**: 3.10+, four-space indents, type-hinted helpers, `if __name__ == "__main__"` entry points. Snake_case filenames. Prefer pure functions. Use `scripts/common.py` for path resolution.
*   **LaTeX**: Modules follow `eq_<domain>_<topic>.tex`, use `\label{eq:aether:energy-band}`, and apply framework macros from `synthesis/preamble.tex`.
*   **Markdown**: Files start with a level-one title, mirroring `docs/` and `notes/` structure.
*   **ASCII-only Policy**: Strict ASCII-only for code and documentation (`.py`, `.md`, `.tex`, `.yml`, `.ps1`, `.sh`). Use LaTeX macros or ASCII transliterations for special characters. Run `make ascii_guard` locally. This policy applies consistently across all environments. Data dumps in `data/`, `extracted_data/`, `source_materials/` are exceptions.

### 1.4 Testing Guidelines

*   Tests live in `tests/test_*.py` and run via `pytest`.
*   Pair pipeline work with `make smoke`, `make test`, and `make pipeline`; add `make latex_strict` for TeX-heavy changes.
*   Treat warnings as failures.
*   `scripts/equation_extractor.py` supports `--parallel-workers` for deterministic parallel results.
*   Default excludes apply when scanning the repo root (`data/`, `extracted_data/`, `source_materials/`, `output/`, `.git`, `.pytest_cache`, `__pycache__`).

### 1.5 Commit & Pull Request Guidelines

*   Use scoped commit subjects (e.g., `scripts: message`). Keep changes domain-focused.
*   Before opening a PR, rerun relevant Make or validation commands, list them in the description, and highlight regenerated assets or screenshots.
*   **Pre-commit hooks**: Install locally (`pip install pre-commit`, `pre-commit install`) to enforce ASCII and quick tests. This setup is generally cross-platform compatible.

### 1.6 Data Stewardship & Configuration

*   Regenerate catalog CSVs via scripts instead of manual editing.
*   Log optional dependencies in `requirements-optional.txt`.
*   Mirror environment notes in `INSTALLATION_REQUIREMENTS.md` and `docs/`.
*   Ensure appropriate script execution policies are set for your environment (e.g., `RemoteSigned` for PowerShell on Windows, executable permissions for shell scripts on Linux/WSL/Illumos).

### 1.7 Workflow for Adding Content

#### Adding a New Equation Module
1.  Create `synthesis/modules/equations/eq_[framework]_[descriptor].tex` with full provenance header.
2.  Run `python scripts/equation_extractor.py` or manually update `equation_catalog.csv`.
3.  Add `\input{modules/equations/eq_...}` in the appropriate chapter.
4.  Test compile (`cd synthesis && pdflatex test_chNN.tex`).
5.  Verify `\label{}` and `\ref{}` resolve correctly.
6.  Run `python scripts/link_modules.py` to update related equations.

#### Transforming a Chapter to Whitepaper Style
*   **Target**: 50-65% narrative, 35-50% equations.
*   **Process**: Add opening story, worked examples, physical interpretations, framework attribution (`\aetherattr{}`, etc.), modularize equations, test compile, and **CRITICALLY verify agent output with system commands**.
    *   **Unix-like (Linux, WSL, Illumos):** `wc -l [file]`, `ls -lh [file]`, `grep "keyword" [file]`, `head [file]`.
    *   **Windows (PowerShell):** `(Get-Content [file]).Count`, `Get-Item [file] | Format-List Length, LastWriteTime`, `Select-String -Path [file] -Pattern "keyword"`, `Get-Content [file] -First 10`.

### 1.8 Running Agents in Parallel

*   **Recommended**: Use 2-3 agents maximum for parallel work.
*   **Verification Protocol (CRITICAL)**: NEVER trust agent claims without verification. Use appropriate system commands to verify files changed (line counts, timestamps, content spot-checks). Previous sessions showed agents claiming success but files unchanged; strict verification prevents this.

### 1.9 Key Principles

*   **Quality Standards**: Zero warnings policy, full implementations only, documented provenance, reproducible builds, ALWAYS verify agent output.
*   **Modularity**: Equations in `modules/equations/`, figures generated by scripts, derivations/tables/narrative snippets modularized for reuse.
*   **Validation**: Individual chapter compilation, cross-reference resolution, bibliography citation resolution, catalog-module parity (`catalog_parity.py`), test suite pass (`test_compilation.ps1` for Windows, `make test` for Unix-like).
*   **Collaboration**: Use TodoWrite tool for granular task management, mark tasks `in_progress` then `completed` immediately, deploy 2-3 agents max, verify ALL agent outputs.

## 2. Agent-Specific Notes

### 2.1 Claude-Specific Notes

*   **Primary Development Environment**: Windows 11, PowerShell native environment. Claude's instructions and examples are often Windows/PowerShell-centric. Users on other platforms should adapt commands to their environment (e.g., `make` for LaTeX compilation instead of PowerShell scripts).
*   **LaTeX Distribution**: MiKTeX (primarily Windows).
*   **Python**: 3.10+ (standard library only for current tools).
*   **MiKTeX Repair**: If compilation fails with "memory dump file not found", use MiKTeX Console GUI to update formats (see Troubleshooting section).
*   **UTF-8 vs ASCII**: LaTeX mathematical content MUST use UTF-8. Python/PowerShell code MUST use ASCII identifiers and comments.
*   **Cross-platform notes**: Scripts designed for Windows PowerShell but work in WSL/Linux via Makefile. Use forward slashes in paths for portability.

### 2.2 Gemini-Specific Notes

*   **Cross-Platform Compatibility**: Gemini actively ensures and documents cross-platform compatibility, including Windows, Linux (e.g., CachyOS), WSL, and Illumos (LX Zones). Instructions aim to be generalized or provide specific alternatives where necessary.
*   **Error Handling in `Makefile`**: `|| true` has been removed from critical `Makefile` targets (`validate`, `test`, `latex`, `latex_strict`, `ascii_guard`) to ensure explicit failure on error, promoting stricter CI across all environments.
*   **CI Implementation**: Basic GitHub Actions workflow (`.github/workflows/main.yml`) implemented to run `make ci` on pull requests and `make latex_strict` on `main` branch pushes. Linting (`flake8`) and type checking (`mypy`) steps added, ensuring quality across platforms.
*   **`data/README.md` Update Process**: `scripts/update_data_readme.py` created and integrated into `make reports` to automatically generate or update sections of `data/README.md`.
*   **Ollama CLI Installation**: Direct link to the official Ollama installation guide added to `INSTALLATION_REQUIREMENTS.md` and `GEMINI.md`.
*   **`docs/README` Reference**: `docs/README.md` created with guidelines for the `docs/` directory, and `AGENTS.md` updated to explicitly refer to it.

## 3. Troubleshooting (Consolidated)

### 3.1 LaTeX Compilation Errors

*   **"Memory dump file not found" / "pdflatex.fmt not found"**: (MiKTeX, Windows) MiKTeX format files corrupted. Fix by updating formats in MiKTeX Console or via `initexmf` commands.
*   **"Undefined control sequence"**: Missing custom macro definition from `preamble.tex` or incorrect spelling.
*   **"Missing \begin{document}"**: `preamble.tex` not included or stray text before `\begin{document}`.
*   **"Undefined references" / "Citation ... undefined"**: Run `pdflatex`, `bibtex`, then `pdflatex` twice. Check `\label{}` and `\cite{}` keys.

### 3.2 Python Script Errors

*   **"Module not found"**: Verify Python 3.10+ installed. Ensure `--base-dir` points to repository root. Use absolute paths or correct working directory. Check `PYTHONPATH` environment variable if necessary.
*   **Script runs but no output files**: Check exit code (non-zero indicates errors). Verify write permissions in the target directory.

### 3.3 Verification Failures

*   **Agent claimed to modify file but line count unchanged**: CRITICAL: Verify with appropriate system commands (e.g., `wc -l` or `(Get-Content).Count`) and check file timestamps.

## 4. Additional Resources

*   **Official Documentation**: MiKTeX, TeX Live, Python, LaTeX Project, CTAN.
*   **Community Support**: TeX Stack Exchange, MiKTeX Issues, TeX Live Issues, Python Community.
*   **LaTeX Packages Documentation**: `amsmath`, `physics`, `tikz/pgf`, `hyperref`, `cleveref`.

---

**Last Updated:** 2025-10-24
**Based on:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`