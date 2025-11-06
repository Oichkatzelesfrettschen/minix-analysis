# Pre-commit Hooks - Quality Automation

**Last Updated:** 2025-11-04  
**Status:** Production Ready

---

## Overview

Pre-commit hooks automatically check code quality before each commit, preventing common issues from entering the codebase.

---

## Quick Start

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

That's it! Hooks will now run automatically on `git commit`.

---

## Configuration

**File:** `.pre-commit-config.yaml`

### Hooks Configured

1. **General File Checks**
   - Trailing whitespace removal
   - End-of-file fixer
   - Large file detection
   - Merge conflict detection

2. **Python Quality**
   - Black formatting
   - Flake8 linting
   - isort import sorting
   - MyPy type checking
   - Pydocstyle docstring validation

3. **Shell Scripts**
   - Shellcheck linting
   - Shebang validation

4. **YAML/JSON**
   - Syntax validation
   - YAML linting

5. **Markdown**
   - Markdown linting (markdownlint)

6. **Security**
   - Bandit security checks
   - Secret detection

---

## Usage

### Automatic

Hooks run automatically on `git commit`:

```bash
git add myfile.py
git commit -m "Add feature"
# Hooks run here automatically
```

### Manual

Run hooks manually:

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run on staged files only
pre-commit run
```

### Skip Hooks

**Emergency only!** Skip hooks when necessary:

```bash
git commit -m "Fix critical bug" --no-verify
```

**Note:** This should be rare. Fix issues instead.

---

## Hook Details

### Black (Python Formatting)

**What it does:** Formats Python code to Black style

**Config:**
```yaml
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      args: ['--line-length=88']
```

**Fix manually:**
```bash
black src/ tests/ tools/
```

### Flake8 (Python Linting)

**What it does:** Checks Python code style

**Config:**
```yaml
- repo: https://github.com/pf/flake8
  rev: 7.0.0
  hooks:
    - id: flake8
      args:
        - '--max-line-length=88'
        - '--extend-ignore=E203,W503'
```

**Fix manually:**
- Review flake8 output
- Fix issues one by one
- Some issues auto-fixable with `autopep8`

### isort (Import Sorting)

**What it does:** Sorts Python imports

**Config:**
```yaml
- repo: https://github.com/PyCQA/isort
  rev: 5.13.2
  hooks:
    - id: isort
      args: ['--profile=black']
```

**Fix manually:**
```bash
isort src/ tests/ tools/
```

### MyPy (Type Checking)

**What it does:** Checks Python type hints

**Config:**
```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.8.0
  hooks:
    - id: mypy
      args: ['--ignore-missing-imports']
```

**Fix manually:**
- Add type hints where missing
- Fix type errors
- Use `# type: ignore` sparingly

### Shellcheck (Shell Linting)

**What it does:** Lints shell scripts

**Config:**
```yaml
- repo: https://github.com/shellcheck-py/shellcheck-py
  rev: v0.9.0.6
  hooks:
    - id: shellcheck
```

**Fix manually:**
- Review shellcheck suggestions
- Apply recommended fixes
- Add `# shellcheck disable=SCXXXX` if needed

### Bandit (Security)

**What it does:** Finds security issues

**Config:**
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.6
  hooks:
    - id: bandit
      args: ['-c', '.bandit']
```

**Fix manually:**
- Review security warnings
- Fix actual vulnerabilities
- Skip false positives in `.bandit` config

---

## Troubleshooting

### Hook Fails

**Problem:** Black reformats code

**Solution:** Accept reformatting, add to commit:
```bash
git add -u
git commit
```

**Problem:** MyPy type errors

**Solution:** Fix type hints or add ignore:
```python
result = some_function()  # type: ignore
```

**Problem:** Shellcheck warnings

**Solution:** Fix script or disable specific check:
```bash
# shellcheck disable=SC2086
```

### Slow Hooks

**Problem:** Hooks take too long

**Solution:** 
1. Update hook versions
2. Use `--no-verify` (emergency only)
3. Configure file exclusions

### Update Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Re-install
pre-commit install
```

---

## Configuration Files

### .bandit

Security check configuration:

```yaml
[bandit]
exclude_dirs:
  - /tests/
  - /venv/
skips:
  - B101  # assert_used
```

### .secrets.baseline

Secrets detection baseline:

```json
{
  "version": "1.4.0",
  "plugins_used": [],
  "results": {}
}
```

---

## Best Practices

### DO:

✅ Run hooks before committing  
✅ Fix issues instead of skipping  
✅ Update hooks regularly  
✅ Keep configuration simple  
✅ Add project-specific hooks  

### DON'T:

❌ Use `--no-verify` routinely  
❌ Disable all hooks  
❌ Ignore security warnings  
❌ Commit generated files  
❌ Skip hook updates  

---

## CI Integration

Pre-commit hooks also run in CI:

```yaml
# .github/workflows/ci.yml
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

This ensures code quality even if local hooks are skipped.

---

## Customization

### Add Custom Hook

Edit `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: custom-check
      name: Custom Check
      entry: python scripts/custom_check.py
      language: system
      files: \.py$
```

### Exclude Files

```yaml
exclude: '^(archive|build|dist)/'
```

### Skip Specific Hooks

```yaml
# In .pre-commit-config.yaml, remove the hook
# Or set skip in git config:
git config --global pre-commit.skip "mypy,flake8"
```

---

## Resources

- [Pre-commit documentation](https://pre-commit.com/)
- [Hook repository](https://github.com/pre-commit/pre-commit-hooks)
- [Configuration reference](https://pre-commit.com/#plugins)

---

**Maintained By:** Quality Assurance Team  
**Contact:** See CONTRIBUTING.md

---

*Automate quality. Enforce standards. Build excellence.*
