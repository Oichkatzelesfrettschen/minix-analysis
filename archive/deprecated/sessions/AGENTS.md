# Repository Guidelines

## Project Structure & Module Organization
- Primary Python package lives in `src/os_analysis_toolkit`, grouping analyzers, generators, dashboards, utilities, and the CLI entry point (`cli.py`).
- Domain-specific LaTeX and figure builds sit under `modules/cpu-interface` and `modules/boot-sequence`; reusable styles live in `shared/`.
- Generated data, diagrams, and coverage artifacts collect in `diagrams/`, `analysis-results/`, `htmlcov/`, and `logs/`.
- Python tests reside in `tests/`, diagram validation in `test_diagrams/`, while long-form documentation is maintained in `docs/` and `documentation/`.

## Build, Test, and Development Commands
- `make help` lists the curated automation entry points; prefer these over ad-hoc scripts.
- `make pipeline` executes the end-to-end MINIX analysis (extraction → TikZ generation → PDF/PNG conversion); it expects the MINIX checkout at `/home/eirikr/Playground/minix`.
- `pytest` runs the Python suite with coverage, benchmark autosave, and fail-fast settings; append `-m "not slow"` for rapid iterations.
- `python -m os_analysis_toolkit.cli --source <path> --output <dir>` performs targeted analyses; add `--parallel --workers 8` to fan out across CPU cores.
- `make cpu` or `make boot` rebuild the LaTeX deliverables for their respective modules before publishing artifacts.

## Coding Style & Naming Conventions
- Use 4-space indentation, PEP 484 type hints, and concise docstrings that state analyzer responsibilities and assumptions.
- Format with `black`, lint via `flake8`, and type-check with `mypy src` prior to review.
- Keep package and file names snake_case; CLI switches remain long-form (e.g., `--dashboard`); generated assets follow the `_report` / `_diagram` suffix pattern.
- Install the hook suite (`pre-commit install`) to enforce formatting, import hygiene, and static checks consistently.

## Testing Guidelines
- Mirror the production package layout inside `tests/` (e.g., `tests/analyzers/test_scheduler.py`).
- Apply the pytest markers declared in `pytest.ini` (`unit`, `integration`, `benchmark`, `requires_minix`) so automation can target or skip suites reliably.
- Preserve coverage thresholds by running `pytest --cov-report=html`; deposit the refreshed HTML output in `htmlcov/` for reviewer access.
- Performance-sensitive work should run `pytest -m benchmark` and archive the generated JSON under `analysis-results/benchmarks/`.

## Commit & Pull Request Guidelines
- Commit messages follow `<type>: <imperative summary>` (`docs: Execute Notes Modularization Phase 6`); reference issue IDs or roadmap items in the body when relevant.
- Pull requests include: scope summary, impacted modules list, the exact test command(s) executed with results, and updated diagrams/screenshots when visuals change.
- Prefer rebasing to keep history linear; squash local fixups before requesting review to maintain a clean audit trail.

## Environment & Configuration
- Keep `MINIX_ROOT` references accurate; adjust path overrides locally rather than committing workstation-specific settings.
- Document new Python or system dependencies in `requirements.txt` and mirror installation notes in `INSTALLATION.md` to keep onboarding crisp.
